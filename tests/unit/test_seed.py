"""Unit tests for db seed (default categories)."""

from sqlmodel import Session, select

from src.db.seed import DEFAULT_CATEGORY_NAMES, seed_default_categories
from src.models import Category, User


def test_seed_default_categories_creates_seven(db_session: Session) -> None:
    """Seed creates exactly the 7 default categories for the user."""
    user = User(telegram_id=12345, pin_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None

    seed_default_categories(db_session, user.id)

    stmt = select(Category).where(Category.user_id == user.id)
    categories = list(db_session.exec(stmt).all())
    assert len(categories) == 7
    names = {c.name for c in categories}
    assert names == set(DEFAULT_CATEGORY_NAMES)
    assert all(c.is_default for c in categories)


def test_seed_default_categories_idempotent(db_session: Session) -> None:
    """Calling seed twice does not duplicate categories."""
    user = User(telegram_id=67890, pin_hash="hash2")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None

    seed_default_categories(db_session, user.id)
    seed_default_categories(db_session, user.id)

    stmt = select(Category).where(Category.user_id == user.id)
    categories = list(db_session.exec(stmt).all())
    assert len(categories) == 7
