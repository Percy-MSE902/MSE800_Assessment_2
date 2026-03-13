# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
import os

# Declarative base class
class Base(DeclarativeBase):
    pass

# Database configuration using environment variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "housekeeping")

class DatabaseManager:
    """
    Manager class to create SQLAlchemy engine and session.
    Uses MySQL as the only supported database.
    """

    @staticmethod
    def create_engine_and_session():
        url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

        engine = create_engine(
            url,
            echo=True
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal

# Create engine and session
engine, SessionLocal = DatabaseManager.create_engine_and_session()

# Dependency for FastAPI
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
