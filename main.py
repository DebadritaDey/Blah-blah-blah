from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.dataset import Dataset
from app.routers.datasets import router as dataset_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI
app = FastAPI(
    title="Prep_AI",
    description="AI-powered Data Preprocessing and Visualization Platform",
    version="1.0.0"
)


# Register dataset router
app.include_router(dataset_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Prep_AI!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

Users often need to switch between different tools and platforms to inspect datasets, clean missing values, transform columns, create visualizations, and export processed data. This makes the workflow less convenient and time-consuming.

2. Manual Effort

Common data preparation tasks, such as handling missing values, removing duplicate records, renaming columns, and changing data types, often require repetitive manual work. Performing these operations individually can increase effort and the chances of errors.

3. Limited Visibility

When data preparation activities are performed across different tools, it becomes difficult to maintain a clear view of the original dataset and its processed versions. Users need an organized way to inspect changes and track their outputs.
