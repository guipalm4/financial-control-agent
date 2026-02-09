"""Handler for /login command (existing user PIN authentication)."""

import logging
from datetime import UTC, datetime

from sqlmodel import Session, select
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.db.engine import engine
from src.models import User
from src.services.auth import verify_pin
from src.services.auth.session import is_locked, lock_duration

logger = logging.getLogger(__name__)

ASK_LOGIN_PIN = 0


def is_valid_pin(pin: str) -> bool:
    """Validate PIN format: 4-6 numeric digits."""
    return pin.isdigit() and 4 <= len(pin) <= 6


async def login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for /login.

    - No user in DB: tell to use /start.
    - User locked: AUTH.ACCOUNT_LOCKED.
    - Otherwise: ask for PIN and go to ASK_LOGIN_PIN.
    """
    user = update.effective_user
    message = update.message
    if not user or not message:
        return ConversationHandler.END

    with Session(engine) as session:
        stmt = select(User).where(User.telegram_id == user.id)
        db_user = session.exec(stmt).first()

    if db_user is None:
        await message.reply_text("Você ainda não tem um PIN. Use /start para ativar seu acesso.")
        return ConversationHandler.END

    if is_locked(db_user):
        await message.reply_text(
            "🔒 Conta bloqueada por muitas tentativas.\n"
            "Tente novamente em 15 minutos.\n"
            "code: AUTH.ACCOUNT_LOCKED"
        )
        return ConversationHandler.END

    logger.info("User %s (%s) started login", user.id, user.username)
    await message.reply_text("Olá! 🔐 Digite seu PIN para continuar:")
    return ASK_LOGIN_PIN


async def login_ask_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive PIN, verify, update failed_attempts/locked_until/last_login."""
    user = update.effective_user
    message = update.message
    if not user or not message or not message.text:
        return ASK_LOGIN_PIN

    pin = message.text.strip()
    if not is_valid_pin(pin):
        await message.reply_text(
            "❌ PIN inválido. Digite apenas 4-6 números.\ncode: AUTH.INVALID_PIN"
        )
        return ASK_LOGIN_PIN

    with Session(engine) as session:
        stmt = select(User).where(User.telegram_id == user.id)
        db_user = session.exec(stmt).first()
        if db_user is None:
            await message.reply_text("Erro: usuário não encontrado. Use /start.")
            return ConversationHandler.END

        if is_locked(db_user):
            await message.reply_text(
                "🔒 Conta bloqueada por muitas tentativas.\n"
                "Tente novamente em 15 minutos.\n"
                "code: AUTH.ACCOUNT_LOCKED"
            )
            return ConversationHandler.END

        if verify_pin(pin, db_user.pin_hash):
            # Success: reset lock, set last_login
            db_user.failed_attempts = 0
            db_user.locked_until = None
            db_user.last_login = datetime.now(UTC)
            session.add(db_user)
            session.commit()
            logger.info("User %s login success", user.id)
            await message.reply_text("✅ Login realizado! Você pode usar o bot.")
            return ConversationHandler.END

        # Wrong PIN: increment failed_attempts
        db_user.failed_attempts = (db_user.failed_attempts or 0) + 1
        if db_user.failed_attempts >= 3:
            db_user.locked_until = datetime.now(UTC) + lock_duration()
            session.add(db_user)
            session.commit()
            logger.warning("User %s account locked after 3 failed attempts", user.id)
            await message.reply_text(
                "🔒 Conta bloqueada por muitas tentativas.\n"
                "Tente novamente em 15 minutos.\n"
                "code: AUTH.ACCOUNT_LOCKED"
            )
            return ConversationHandler.END

        session.add(db_user)
        session.commit()
        remaining = 3 - db_user.failed_attempts
        await message.reply_text(
            f"❌ PIN incorreto. Tentativas restantes: {remaining}.\nDigite seu PIN novamente:"
        )
        return ASK_LOGIN_PIN


async def login_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel login conversation."""
    if update.message:
        await update.message.reply_text("Login cancelado. Use /login quando quiser.")
    return ConversationHandler.END
