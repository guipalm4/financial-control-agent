"""Shared auth helpers for handlers that require an active session (RULE-008)."""

from sqlmodel import Session, select
from telegram import Update

from src.db.engine import engine
from src.models import User
from src.services.auth.session import is_locked, is_session_valid


async def get_authenticated_user(update: Update) -> User | None:
    """Load user by telegram_id and ensure session is valid.

    If user is missing, locked, or session expired, sends the appropriate
    message and returns None. Otherwise returns the DB User.
    """
    user = update.effective_user
    message = update.message
    if not user or not message:
        return None

    with Session(engine) as session:
        stmt = select(User).where(User.telegram_id == user.id)
        db_user = session.exec(stmt).first()

    if db_user is None:
        await message.reply_text("Você ainda não tem um PIN. Use /start para ativar seu acesso.")
        return None

    if is_locked(db_user):
        await message.reply_text(
            "🔒 Conta bloqueada por muitas tentativas.\n"
            "Tente novamente em 15 minutos.\n"
            "code: AUTH.ACCOUNT_LOCKED"
        )
        return None

    if not is_session_valid(db_user):
        await message.reply_text(
            "⏱️ Sessão expirada. Use /login para continuar.\ncode: AUTH.SESSION_EXPIRED"
        )
        return None

    return db_user
