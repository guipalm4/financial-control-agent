"""Handler for /start command."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    message = update.message
    if not user or not message:
        return
    logger.info("User %s (%s) sent /start", user.id, user.username)
    await message.reply_text(
        f"Olá {user.first_name}! 👋\n\nBem-vindo ao Finance Bot!\nEste bot está em desenvolvimento."
    )
