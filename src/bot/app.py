"""Main Telegram bot application."""

import logging

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters

from src.bot.handlers.audio import audio_message_handler
from src.bot.handlers.cards import (
    CARD_CLOSING_DAY,
    CARD_DUE_DAY,
    CARD_LAST_DIGITS,
    CARD_NAME,
    add_cartao_cancel,
    add_cartao_closing_day,
    add_cartao_due_day,
    add_cartao_last_digits,
    add_cartao_name,
    add_cartao_start,
    delete_cartao_handler,
    list_cartoes_handler,
)
from src.bot.handlers.categories import (
    add_categoria_handler,
    delete_categoria_handler,
    list_categorias_handler,
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

    # FEAT-010: CRUD cartões
    add_cartao_conv = ConversationHandler(
        entry_points=[CommandHandler("add_cartao", add_cartao_start)],
        states={
            CARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_cartao_name)],
            CARD_LAST_DIGITS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cartao_last_digits),
            ],
            CARD_CLOSING_DAY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cartao_closing_day),
            ],
            CARD_DUE_DAY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cartao_due_day),
            ],
        },
        fallbacks=[CommandHandler("cancel", add_cartao_cancel)],
    )
    application.add_handler(add_cartao_conv)
    application.add_handler(CommandHandler("list_cartoes", list_cartoes_handler))
    application.add_handler(CommandHandler("delete_cartao", delete_cartao_handler))

    # FEAT-011: CRUD categorias
    application.add_handler(CommandHandler("add_categoria", add_categoria_handler))
    application.add_handler(CommandHandler("list_categorias", list_categorias_handler))
    application.add_handler(CommandHandler("delete_categoria", delete_categoria_handler))

    # FEAT-003: mensagens de voz → transcrição (AUDIO-001)
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, audio_message_handler))

    return application


def main() -> None:
    """Run the bot."""
    app = create_app()
    logger.info("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
