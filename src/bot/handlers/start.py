"""Handler for /start command."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) sent /start")
    await update.message.reply_text(
        f"Olá {user.first_name}! 👋\n\n"
        "Bem-vindo ao Finance Bot!\n"
        "Este bot está em desenvolvimento."
    )
