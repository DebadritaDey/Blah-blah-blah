
from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.dataset import Dataset

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Prep_AI",
    description="AI-powered Data Preprocessing and Visualization Platform",
    version="1.0.0"
)


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
