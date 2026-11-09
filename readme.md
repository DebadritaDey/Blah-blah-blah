# Prep_AI – Data Preprocessing & Exploratory Data Analysis Platform

## 1. Project Overview

Prep_AI is a web-based data preprocessing and exploratory data analysis platform built using Python, FastAPI, Streamlit, and SQLite.

It helps users upload datasets, inspect data, clean missing values, remove duplicates, transform columns, perform exploratory data analysis, visualize results, and download processed datasets.

The application uses a FastAPI backend for data processing and a Streamlit frontend for user interaction.

## 2. Key Features

- **Dataset Upload:** Upload CSV and Excel files.
- **Dataset Management:** View uploaded datasets, dataset information, and data previews.
- **Data Cleaning:** Remove missing values and duplicate records.
- **Data Transformation:** Rename columns, drop columns, and convert data types.
- **Exploratory Data Analysis:**
  - Descriptive statistics
  - Correlation heatmap
  - Histograms
  - Bar charts
  - Scatter plots
- **Dataset Export:** Download processed datasets in CSV and Excel formats.
- **Database Management:** Store dataset metadata using SQLite.
- **Local Execution:** Run the application locally.

## 3. Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| API Communication | Requests |
| Styling | CSS |

## 4. Project Architecture

The application follows a simple three-layer architecture:

1. **Frontend:** Streamlit provides the user interface.
2. **Backend:** FastAPI handles API requests and dataset processing.
3. **Database and Storage:** SQLite stores dataset metadata, while uploaded and processed files are stored separately.

Frontend → FastAPI → SQLite and File Storage

## 5. Project Structure

```text
Prep_AI/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── database/
│       ├── models/
│       ├── schemas/
│       ├── routers/
│       └── services/
│
├── frontend/
│   ├── streamlit_app.py
│   ├── api_client.py
│   └── assets/
│       ├── style.css
│       └── scripts.js
│
├── storage/
│   ├── raw/
│   └── processed/
│
├── tests/
├── requirements.txt
└── README.md
```

## 6. Installation and Setup

### Prerequisites

- Python installed on your system.
- pip package manager.
- Visual Studio Code (recommended).

### Step 1: Create and activate virtual environment

```bash
py -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Install dependencies

```bash
py -m pip install -r requirements.txt
```

### Step 3: Start FastAPI backend

Open a terminal and navigate to the backend folder:

```powershell
cd backend
```

Run:

```powershell
py -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### Step 4: Start Streamlit frontend

Open another terminal, activate the virtual environment, and navigate to the frontend folder:

```powershell
cd frontend
```

Run:

```powershell
py -m streamlit run streamlit_app.py
```

Frontend URL:

http://localhost:8501

**Important:** Keep both servers running while using the application.

## 7. API Endpoints

Base URL: `/api/v1/datasets`

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/upload` | Upload dataset |
| GET | `/` | List datasets |
| GET | `/{id}/preview` | Preview dataset |
| GET | `/{id}/info` | Dataset information |
| POST | `/{id}/clean` | Clean dataset |
| POST | `/{id}/rename-columns` | Rename columns |
| POST | `/{id}/drop-columns` | Drop columns |
| POST | `/{id}/convert-datatype` | Convert data types |
| GET | `/{id}/statistics` | Descriptive statistics |
| GET | `/{id}/correlation` | Correlation analysis |
| GET | `/{id}/histogram/{column}` | Histogram data |
| GET | `/{id}/bar-chart/{column}` | Bar chart data |
| GET | `/{id}/scatter-plot` | Scatter plot data |
| GET | `/{id}/download` | Download dataset |

## 8. How to Use the Application

1. Start the FastAPI backend and Streamlit frontend.
2. Open the application in your browser.
3. Upload a CSV or Excel dataset.
4. Navigate to Manage Datasets to inspect the uploaded data.
5. Use Clean & Transform to modify the dataset.
6. Open EDA Dashboard to explore statistics and visualizations.
7. Navigate to Download Dataset to export the final dataset.

## 9. Future Enhancements

- Advanced data validation.
- Additional visualization options.
- Automated data quality reports.
- Improved dataset management.
- More data transformation operations.

## 10. Conclusion

Prep_AI provides a simple and interactive platform for dataset preprocessing and exploratory data analysis. It combines FastAPI, Streamlit, Pandas, and SQLite to create a modular application that simplifies common data preparation tasks.