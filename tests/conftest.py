"""Pytest configuration and fixtures."""

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.bot.app import create_app
from src.models import Card, Category, User  # noqa: F401 - register models for metadata


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session.

    Creates a temporary in-memory SQLite database for testing.
    Yields a session that is automatically rolled back after each test.

    Yields:
        Session: SQLModel database session for testing
    """
    # Use in-memory SQLite for testing
    test_db_url = "sqlite:///:memory:"
    engine = create_engine(test_db_url, echo=False)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    with Session(engine) as session:
        yield session
        session.rollback()

    # Cleanup
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def bot_app():
    """Create a test Telegram bot application.

    Returns:
        Application: Configured Telegram bot application for testing
    """
    return create_app()


@pytest.fixture(scope="function")
async def bot_app_async():
    """Create and initialize a test Telegram bot application (async).

    Returns:
        Application: Configured and initialized Telegram bot application

    Note:
        Remember to call app.shutdown() after tests if needed.
    """
    app = create_app()
    await app.initialize()
    yield app
    await app.shutdown()
