"""Configuration settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/finance_bot"

    # API Keys
    GROQ_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env
    )


# Loaded from env at runtime; mypy does not understand pydantic-settings injection
settings: Settings = Settings()  # type: ignore[call-arg]
