"""Unit tests for User model."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.models import User


def test_user_create_and_read(db_session: Session) -> None:
    """User can be created and read from DB."""
    user = User(
        telegram_id=12345,
        pin_hash="$2b$12$dummy.hash.value.here",
        failed_attempts=0,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.telegram_id == 12345
    assert user.pin_hash == "$2b$12$dummy.hash.value.here"
    assert user.failed_attempts == 0
    assert user.locked_until is None
    assert user.last_login is None


def test_user_optional_fields(db_session: Session) -> None:
    """User locked_until and last_login are optional."""
    now = datetime.now(UTC)
    user = User(
        telegram_id=999,
        pin_hash="hash",
        failed_attempts=2,
        locked_until=now,
        last_login=now,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.locked_until is not None
    assert user.last_login is not None


def test_user_telegram_id_unique(db_session: Session) -> None:
    """telegram_id must be unique."""
    user1 = User(telegram_id=111, pin_hash="h1")
    db_session.add(user1)
    db_session.commit()

    user2 = User(telegram_id=111, pin_hash="h2")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_find_by_telegram_id(db_session: Session) -> None:
    """User can be found by telegram_id."""
    user = User(telegram_id=777, pin_hash="x")
    db_session.add(user)
    db_session.commit()

    stmt = select(User).where(User.telegram_id == 777)
    found = db_session.exec(stmt).first()
    assert found is not None
    assert found.telegram_id == 777
