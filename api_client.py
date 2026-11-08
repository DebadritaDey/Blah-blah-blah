
import requests

# FastAPI backend URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1/datasets"


# 1. GET ALL DATASETS
def get_datasets():
    response = requests.get(f"{API_BASE_URL}/")
    response.raise_for_status()
    return response.json()


# 2. UPLOAD DATASET
def upload_dataset(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/upload",
        files=files
    )

    response.raise_for_status()
    return response.json()


# 3. PREVIEW DATASET
def get_preview(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/preview"
    )

    response.raise_for_status()
    return response.json()


# 4. DATASET INFORMATION
def get_dataset_info(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/info"
    )

    response.raise_for_status()
    return response.json()


# 5. CLEAN DATASET
def clean_dataset(dataset_id, remove_missing_rows, remove_duplicates):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/clean",
        json={
            "remove_missing_rows": remove_missing_rows,
            "remove_duplicates": remove_duplicates
        }
    )

    response.raise_for_status()
    return response.json()


# 6. RENAME COLUMNS
def rename_columns(dataset_id, column_mapping):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/rename-columns",
        json={
            "column_mapping": column_mapping
        }
    )

    response.raise_for_status()
    return response.json()


# 7. DROP COLUMNS
def drop_columns(dataset_id, columns):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/drop-columns",
        json={
            "columns": columns
        }
    )

    response.raise_for_status()
    return response.json()


# 8. CONVERT DATA TYPE
def convert_datatype(dataset_id, column_name, new_type):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/convert-datatype",
        json={
            "column_name": column_name,
            "new_type": new_type
        }
    )

    response.raise_for_status()
    return response.json()


# 9. DESCRIPTIVE STATISTICS
def get_statistics(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/statistics"
    )

    response.raise_for_status()
    return response.json()


# 10. CORRELATION MATRIX
def get_correlation(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/correlation"
    )

    response.raise_for_status()
    return response.json()


# 11. HISTOGRAM
def get_histogram(dataset_id, column_name):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/histogram/{column_name}"
    )

    response.raise_for_status()
    return response.json()


# 12. BAR CHART
def get_bar_chart(dataset_id, column_name):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/bar-chart/{column_name}"
    )

    response.raise_for_status()
    return response.json()


# 13. SCATTER PLOT
def get_scatter_plot(dataset_id, x_column, y_column):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/scatter-plot",
        params={
            "x_column": x_column,
            "y_column": y_column
        }
    )

    response.raise_for_status()
    return response.json()


# 14. DOWNLOAD DATASET
def download_dataset(dataset_id, file_format="csv"):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/download",
        params={
            "file_format": file_format
        }
    )

    response.raise_for_status()
    return response.content
