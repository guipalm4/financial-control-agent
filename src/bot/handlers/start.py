"""Handler for /start command."""

import logging

from sqlmodel import Session, select
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.db.engine import engine
from src.db.seed import seed_default_categories
from src.models import User
from src.services.auth import hash_pin

logger = logging.getLogger(__name__)

ASK_PIN, CONFIRM_PIN = range(2)


def is_valid_pin(pin: str) -> bool:
    """Validate PIN format: 4-6 numeric digits."""
    return pin.isdigit() and 4 <= len(pin) <= 6


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for /start.

    - New user: start PIN creation conversation.
    - Existing user: just greet (login handled in AUTH-003).
    """
    user = update.effective_user
    message = update.message
    if not user or not message:
        return ConversationHandler.END

    with Session(engine) as session:
        stmt = select(User).where(User.telegram_id == user.id)
        existing = session.exec(stmt).first()

    if existing is not None:
        await message.reply_text(
            f"Olá {user.first_name}! 👋\n\nVocê já tem um PIN configurado.\n"
            "Use /login para autenticar."
        )
        return ConversationHandler.END

    logger.info("User %s (%s) sent /start", user.id, user.username)
    await message.reply_text(
        f"Olá {user.first_name}! 👋\n\nVamos ativar seu acesso.\n\n"
        "Digite um PIN de 4-6 números (ex: 1234)."
    )
    return ASK_PIN


async def ask_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect PIN and ask confirmation."""
    message = update.message
    if not message or not message.text:
        return ASK_PIN

    pin = message.text.strip()
    if not is_valid_pin(pin):
        await message.reply_text(
            "❌ PIN inválido. Digite apenas 4-6 números.\ncode: AUTH.INVALID_PIN"
        )
        return ASK_PIN

    user_data = context.user_data
    if user_data is None:
        return ConversationHandler.END

    user_data["pending_pin"] = pin
    await message.reply_text("Confirme o PIN digitando novamente:")
    return CONFIRM_PIN


async def confirm_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm PIN, create user, and end conversation."""
    user = update.effective_user
    message = update.message
    if not user or not message or not message.text:
        return CONFIRM_PIN

    user_data = context.user_data
    if user_data is None:
        return ConversationHandler.END

    pending_pin = str(user_data.get("pending_pin", "")).strip()
    confirmation = message.text.strip()

    if pending_pin == "" or confirmation != pending_pin:
        user_data.pop("pending_pin", None)
        await message.reply_text(
            "❌ PINs não conferem. Vamos tentar de novo.\n\nDigite um PIN de 4-6 números:"
        )
        return ASK_PIN

    pin_hash = hash_pin(pending_pin)

    with Session(engine) as session:
        # Re-check to avoid duplicates if user restarted conversation
        stmt = select(User).where(User.telegram_id == user.id)
        existing = session.exec(stmt).first()
        if existing is None:
            new_user = User(telegram_id=user.id, pin_hash=pin_hash)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            if new_user.id is not None:
                seed_default_categories(session, new_user.id)

    user_data.pop("pending_pin", None)
    await message.reply_text("✅ PIN criado! Vamos configurar seus cartões.")
    # Onboarding wizard will be implemented in ONBOARD-004
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel PIN creation conversation."""
    user_data = context.user_data
    if user_data is not None:
        user_data.pop("pending_pin", None)
    if update.message:
        await update.message.reply_text("Ok — cancelado. Você pode recomeçar com /start.")
    return ConversationHandler.END
