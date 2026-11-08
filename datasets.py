import os
import uuid

import pandas as pd

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetResponse


router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["Datasets"]
)


# Get project root directory
BASE_DIR = Path(__file__).resolve().parents[3]

# Folder to store uploaded files
UPLOAD_DIR = BASE_DIR / "storage" / "raw"

# Create folder if it does not exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Check file extension
    extension = Path(file.filename).suffix.lower()

    if extension not in [".csv", ".xlsx"]:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are allowed."
        )

    # Generate unique dataset ID
    dataset_id = str(uuid.uuid4())

    # Create file path
    file_path = UPLOAD_DIR / f"{dataset_id}{extension}"

    try:

        # Read uploaded file
        contents = await file.read()

        # Save file locally
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # Read data using Pandas
        if extension == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Create database record
        new_dataset = Dataset(
            dataset_id=dataset_id,
            filename=file.filename,
            file_path=str(file_path),
            row_count=len(df),
            column_count=len(df.columns)
        )

        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)

        # Return response
        return {
            "dataset_id": new_dataset.dataset_id,
            "filename": new_dataset.filename,
            "row_count": new_dataset.row_count,
            "column_count": new_dataset.column_count,
            "message": "Dataset uploaded successfully"
        }

    except Exception as e:

        # Delete saved file if upload processing fails
        if os.path.exists(file_path):
            os.remove(file_path)

        db.rollback()

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Error processing dataset: {str(e)}"
        )

@router.get("/", response_model=list[DatasetListResponse])
def get_all_datasets(db: Session = Depends(get_db)):

    # Fetch all datasets from database
    datasets = db.query(Dataset).all()

    return datasets    


@router.get("/{dataset_id}/preview")
def preview_dataset(
    dataset_id: str,
    db: Session = Depends(get_db)
):

    # Find dataset in database
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    # Check if dataset exists
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:

        # Read dataset
        if dataset.filename.endswith(".csv"):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Get first 10 rows
        preview = df.head(10).fillna("").to_dict(
            orient="records"
        )

        return {
            "dataset_id": dataset.dataset_id,
            "filename": dataset.filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "preview": preview
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to preview dataset: {str(e)}"
        )

@router.get("/{dataset_id}/info")
def get_dataset_info(
    dataset_id: str,
    db: Session = Depends(get_db)
):

    # Find dataset in database
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:

        # Read dataset
        if dataset.filename.endswith(".csv"):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Get column information
        column_info = []

        for column in df.columns:

            column_info.append({
                "column_name": str(column),
                "data_type": str(df[column].dtype),
                "missing_values": int(df[column].isnull().sum())
            })

        # Count duplicate rows
        duplicate_count = int(df.duplicated().sum())

        return {
            "dataset_id": dataset.dataset_id,
            "filename": dataset.filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "duplicate_rows": duplicate_count,
            "columns": column_info
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to analyze dataset: {str(e)}"
        )

@router.post("/{dataset_id}/clean")
def clean_dataset(
    dataset_id: str,
    request: CleanDatasetRequest,
    db: Session = Depends(get_db)
):

    # Find the original dataset
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    new_file_path = None

    try:

        # Read the original dataset
        extension = Path(dataset.file_path).suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        original_rows = len(df)

        # Remove rows containing missing values
        missing_rows_removed = 0

        if request.remove_missing_rows:

            df = df.dropna()

            missing_rows_removed = original_rows - len(df)

        # Remove duplicate rows
        duplicate_rows_removed = 0

        if request.remove_duplicates:

            rows_before_duplicates = len(df)

            df = df.drop_duplicates()

            duplicate_rows_removed = (
                rows_before_duplicates - len(df)
            )

        # Generate a new dataset ID
        cleaned_dataset_id = str(uuid.uuid4())

        # Create the cleaned file path
        new_filename = f"cleaned_{dataset.filename}"

        new_file_path = (
            PROCESSED_DIR /
            f"{cleaned_dataset_id}{extension}"
        )

        # Save the cleaned dataset
        if extension == ".csv":
            df.to_csv(new_file_path, index=False)
        else:
            df.to_excel(new_file_path, index=False)

        # Save cleaned dataset information in database
        cleaned_dataset = Dataset(
            dataset_id=cleaned_dataset_id,
            filename=new_filename,
            file_path=str(new_file_path),
            row_count=len(df),
            column_count=len(df.columns)
        )

        db.add(cleaned_dataset)
        db.commit()
        db.refresh(cleaned_dataset)

        return {
            "original_dataset_id": dataset_id,
            "cleaned_dataset_id": cleaned_dataset_id,
            "original_rows": original_rows,
            "cleaned_rows": len(df),
            "removed_missing_rows": missing_rows_removed,
            "removed_duplicate_rows": duplicate_rows_removed,
            "message": "Dataset cleaned successfully"
        }

    except Exception as e:

        db.rollback()

        # Remove the new file if processing fails
        if new_file_path and new_file_path.exists():
            new_file_path.unlink()

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Error cleaning dataset: {str(e)}"
        )

@router.post("/{dataset_id}/rename-columns")
def rename_columns(
    dataset_id: str,
    request: RenameColumnsRequest,
    db: Session = Depends(get_db)
):

    # Find the dataset
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    new_file_path = None

    try:

        # Read the dataset
        extension = Path(dataset.file_path).suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Check whether requested columns exist
        missing_columns = [
            column for column in request.column_mapping
            if column not in df.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Columns not found: {missing_columns}"
            )

        # Rename columns
        df = df.rename(columns=request.column_mapping)

        # Create a new dataset ID
        new_dataset_id = str(uuid.uuid4())

        # Save transformed dataset
        new_filename = f"renamed_{dataset.filename}"

        new_file_path = (
            PROCESSED_DIR /
            f"{new_dataset_id}{extension}"
        )

        if extension == ".csv":
            df.to_csv(new_file_path, index=False)
        else:
            df.to_excel(new_file_path, index=False)

        # Save new dataset information
        new_dataset = Dataset(
            dataset_id=new_dataset_id,
            filename=new_filename,
            file_path=str(new_file_path),
            row_count=len(df),
            column_count=len(df.columns)
        )

        db.add(new_dataset)
        db.commit()

        return {
            "original_dataset_id": dataset_id,
            "new_dataset_id": new_dataset_id,
            "renamed_columns": request.column_mapping,
            "message": "Columns renamed successfully"
        }

    except Exception as e:

        db.rollback()

        if new_file_path and new_file_path.exists():
            new_file_path.unlink()

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Error renaming columns: {str(e)}"
        )  

@router.post("/{dataset_id}/drop-columns")
def drop_columns(
    dataset_id: str,
    request: DropColumnsRequest,
    db: Session = Depends(get_db)
):

    # Find the dataset
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    new_file_path = None

    try:

        # Read the dataset
        extension = Path(dataset.file_path).suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Check whether columns exist
        missing_columns = [
            column for column in request.columns
            if column not in df.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Columns not found: {missing_columns}"
            )

        # Check that at least one column remains
        if len(request.columns) >= len(df.columns):
            raise HTTPException(
                status_code=400,
                detail="Cannot remove all columns from the dataset."
            )

        # Drop selected columns
        df = df.drop(columns=request.columns)

        # Generate new dataset ID
        new_dataset_id = str(uuid.uuid4())

        new_filename = f"modified_{dataset.filename}"

        new_file_path = (
            PROCESSED_DIR /
            f"{new_dataset_id}{extension}"
        )

        # Save modified dataset
        if extension == ".csv":
            df.to_csv(new_file_path, index=False)
        else:
            df.to_excel(new_file_path, index=False)

        # Save dataset information
        new_dataset = Dataset(
            dataset_id=new_dataset_id,
            filename=new_filename,
            file_path=str(new_file_path),
            row_count=len(df),
            column_count=len(df.columns)
        )

        db.add(new_dataset)
        db.commit()

        return {
            "original_dataset_id": dataset_id,
            "new_dataset_id": new_dataset_id,
            "removed_columns": request.columns,
            "remaining_columns": list(df.columns),
            "message": "Columns removed successfully"
        }

    except Exception as e:

        db.rollback()

        if new_file_path and new_file_path.exists():
            new_file_path.unlink()

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Error removing columns: {str(e)}"
        )

@router.post("/{dataset_id}/convert-datatype")
def convert_datatype(
    dataset_id: str,
    request: ConvertDataTypeRequest,
    db: Session = Depends(get_db)
):

    # Find the dataset
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    new_file_path = None

    try:

        # Read the dataset
        extension = Path(dataset.file_path).suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Check if column exists
        if request.column_name not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Column not found"
            )

        # Convert data type
        if request.new_type == "int":
            df[request.column_name] = pd.to_numeric(
                df[request.column_name],
                errors="raise"
            ).astype("int64")

        elif request.new_type == "float":
            df[request.column_name] = pd.to_numeric(
                df[request.column_name],
                errors="raise"
            ).astype(float)

        elif request.new_type == "str":
            df[request.column_name] = df[
                request.column_name
            ].astype(str)

        else:
            raise HTTPException(
                status_code=400,
                detail="Supported types are int, float and str"
            )

        # Generate new dataset ID
        new_dataset_id = str(uuid.uuid4())

        new_filename = f"converted_{dataset.filename}"

        new_file_path = (
            PROCESSED_DIR /
            f"{new_dataset_id}{extension}"
        )

        # Save converted dataset
        if extension == ".csv":
            df.to_csv(new_file_path, index=False)
        else:
            df.to_excel(new_file_path, index=False)

        # Save dataset information
        new_dataset = Dataset(
            dataset_id=new_dataset_id,
            filename=new_filename,
            file_path=str(new_file_path),
            row_count=len(df),
            column_count=len(df.columns)
        )

        db.add(new_dataset)
        db.commit()

        return {
            "original_dataset_id": dataset_id,
            "new_dataset_id": new_dataset_id,
            "column_name": request.column_name,
            "new_data_type": request.new_type,
            "message": "Data type converted successfully"
        }

    except Exception as e:

        db.rollback()

        if new_file_path and new_file_path.exists():
            new_file_path.unlink()

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Error converting data type: {str(e)}"
        )
@router.get("/{dataset_id}/statistics")
def get_dataset_statistics(
    dataset_id: str,
    db: Session = Depends(get_db)
):

    # Find dataset
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:

        # Read dataset
        extension = Path(dataset.file_path).suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Select numerical columns
        numeric_df = df.select_dtypes(include="number")

        if numeric_df.empty:
            raise HTTPException(
                status_code=400,
                detail="No numerical columns found"
            )

        # Calculate statistical summary
        statistics = numeric_df.describe()

        return {
            "dataset_id": dataset_id,
            "filename": dataset.filename,
            "statistics": statistics.to_dict()
        }

    except Exception as e:

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Unable to calculate statistics: {str(e)}"
        )

@router.get("/{dataset_id}/correlation")
def get_dataset_correlation(
    dataset_id: str,
    db: Session = Depends(get_db)
):

    # Find dataset
    dataset = db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:

        # Read dataset
        extension = Path(dataset.file_path).suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Select numerical columns
        numeric_df = df.select_dtypes(include="number")

        if len(numeric_df.columns) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two numerical columns are required"
            )

        # Calculate correlation
        correlation = numeric_df.corr()

        return {
            "dataset_id": dataset_id,
            "filename": dataset.filename,
            "correlation": correlation.to_dict()
        }

    except Exception as e:

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail=f"Unable to calculate correlation: {str(e)}"
        )
