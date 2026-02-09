"""Seed data: default categories per user."""

from sqlmodel import Session, select

from src.models import Category

# Default category names (seed for new users)
DEFAULT_CATEGORY_NAMES: tuple[str, ...] = (
    "Alimentação",
    "Transporte",
    "Lazer",
    "Moradia",
    "Assinaturas",
    "Saúde",
    "Outros",
)


def seed_default_categories(session: Session, user_id: int) -> None:
    """Create default categories for a user. Idempotent if defaults already exist."""
    stmt = select(Category).where(
        Category.user_id == user_id,
        Category.is_default == True,  # noqa: E712
    )
    existing = session.exec(stmt).first()
    if existing is not None:
        return
    for name in DEFAULT_CATEGORY_NAMES:
        session.add(Category(user_id=user_id, name=name, is_default=True, is_essential=False))
    session.commit()
