"""Database session management."""

from collections.abc import Iterator

from sqlmodel import Session

from src.db.engine import engine


def get_session() -> Iterator[Session]:
    """Get a database session.

    Yields:
        Session: SQLModel database session

    Example:
        ```python
        with get_session() as session:
            user = User(name="John")
            session.add(user)
            session.commit()
        ```
    """
    with Session(engine) as session:
        yield session
