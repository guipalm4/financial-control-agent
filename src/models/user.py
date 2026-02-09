"""User model for authentication."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model: Telegram user with PIN and session data."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    pin_hash: str = Field(min_length=1)
    failed_attempts: int = Field(default=0)
    locked_until: datetime | None = Field(default=None)
    last_login: datetime | None = Field(default=None)
