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