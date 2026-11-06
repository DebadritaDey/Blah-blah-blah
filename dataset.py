
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.database import Base


class Dataset(Base):

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    row_count = Column(Integer, nullable=False)

    column_count = Column(Integer, nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
