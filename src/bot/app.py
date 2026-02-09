"""Main Telegram bot application."""

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.handlers.login import (
    ASK_LOGIN_PIN,
    login_ask_pin,
    login_cancel,
    login_handler,
)
from src.bot.handlers.start import (
    ASK_PIN,
    CONFIRM_PIN,
    ask_pin,
    cancel,
    confirm_pin,
    start_handler,
)
from src.core.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def create_app() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # /start: new user -> PIN creation (ConversationHandler)
    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            ASK_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_pin)],
            CONFIRM_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_pin)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(start_conv)

    login_conv = ConversationHandler(
        entry_points=[CommandHandler("login", login_handler)],
        states={
            ASK_LOGIN_PIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, login_ask_pin),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", login_cancel),
            CommandHandler("login", login_handler),
        ],
    )
    application.add_handler(login_conv)

    return application


def main() -> None:
    """Run the bot."""
    app = create_app()
    logger.info("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
