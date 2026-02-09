"""Database engine configuration for SQLModel."""
from sqlmodel import SQLModel, create_engine

from src.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
)


def create_db_and_tables() -> None:
    """Create all database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)
