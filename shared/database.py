"""
Database configuration and session management.

Uses SQLAlchemy with SQLite for simplicity.
All three APIs share the same database.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# SQLite database URL - use parent directory to share across APIs
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "task_management.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.

    Used by FastAPI's Depends() in all three APIs.
    Ensures proper session lifecycle management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.

    Should be called once at application startup.
    """
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)