"""Category model for expense categorization."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    """Category model: user category (default or custom), soft delete."""

    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=50)
    is_default: bool = Field(default=False, description="True for seed/default categories")
    is_essential: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
