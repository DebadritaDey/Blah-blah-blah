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