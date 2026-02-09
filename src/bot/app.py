"""Main Telegram bot application."""

import logging

from telegram.ext import Application, CommandHandler

from src.bot.handlers.start import start_handler
from src.core.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def create_app() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_handler))

    return application


def main() -> None:
    """Run the bot."""
    app = create_app()
    logger.info("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
