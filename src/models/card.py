"""Card model for user credit/debit cards."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Card(SQLModel, table=True):
    """Card model: user card with closing and due dates (soft delete)."""

    __tablename__ = "cards"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=50)
    last_digits: str = Field(max_length=4, min_length=4, description="Last 4 digits of the card")
    closing_day: int = Field(ge=1, le=31, description="Invoice closing day (1-31)")
    due_day: int = Field(ge=1, le=31, description="Invoice due day (1-31)")
    is_debit: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
