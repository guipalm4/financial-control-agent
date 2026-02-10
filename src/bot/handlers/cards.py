"""Handlers for card CRUD: /add_cartao, /list_cartoes, /delete_cartao (FEAT-010, RULE-001)."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Session, select
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.handlers.auth_helpers import get_authenticated_user
from src.db.engine import engine
from src.models import Card
from src.services.cards.validation import (
    CARD_INVALID_CLOSING_DAY,
    CARD_INVALID_DUE_DAY,
    CARD_NAME_REQUIRED,
    validate_closing_day,
    validate_due_day,
    validate_last_digits,
    validate_name,
)

logger = logging.getLogger(__name__)

# ConversationHandler states for /add_cartao
CARD_NAME, CARD_LAST_DIGITS, CARD_CLOSING_DAY, CARD_DUE_DAY = range(4)

# User data keys
KEY_CARD_NAME = "card_name"
KEY_CARD_LAST_DIGITS = "card_last_digits"
KEY_CARD_CLOSING_DAY = "card_closing_day"
KEY_CARD_DUE_DAY = "card_due_day"


# ---- /add_cartao ----
async def add_cartao_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry: require auth, then ask for card name."""
    user = update.effective_user
    message = update.message
    if not user or not message:
        return ConversationHandler.END

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return ConversationHandler.END

    if context.user_data:
        context.user_data.pop(KEY_CARD_NAME, None)
        context.user_data.pop(KEY_CARD_LAST_DIGITS, None)
        context.user_data.pop(KEY_CARD_CLOSING_DAY, None)
        context.user_data.pop(KEY_CARD_DUE_DAY, None)

    await message.reply_text("💳 Nome do cartão (ex: Nubank):")
    return CARD_NAME


async def add_cartao_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive name, validate, ask last 4 digits."""
    message = update.message
    if not message or not message.text:
        return CARD_NAME

    ok, err = validate_name(message.text)
    if not ok:
        await message.reply_text(
            "❌ Informe o nome do cartão.\ncode: " + (err or CARD_NAME_REQUIRED)
        )
        return CARD_NAME

    name = message.text.strip()[:50]
    if context.user_data is not None:
        context.user_data[KEY_CARD_NAME] = name

    await message.reply_text("Digite os últimos 4 dígitos do cartão (ex: 1234):")
    return CARD_LAST_DIGITS


async def add_cartao_last_digits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive last digits, validate, ask closing day."""
    message = update.message
    if not message or not message.text:
        return CARD_LAST_DIGITS

    ok, err = validate_last_digits(message.text)
    if not ok:
        code = err or "CARD.INVALID_DIGITS"
        await message.reply_text(f"❌ Digite apenas 4 dígitos numéricos (ex: 1234).\ncode: {code}")
        return CARD_LAST_DIGITS

    digits = message.text.strip()
    if context.user_data is not None:
        context.user_data[KEY_CARD_LAST_DIGITS] = digits

    await message.reply_text("📅 Dia de fechamento da fatura (1 a 31):")
    return CARD_CLOSING_DAY


async def add_cartao_closing_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive closing day, validate, ask due day."""
    message = update.message
    if not message or not message.text:
        return CARD_CLOSING_DAY

    ok, day, err = validate_closing_day(message.text)
    if not ok:
        await message.reply_text(
            "❌ Dia de fechamento inválido. Digite um número entre 1 e 31.\ncode: "
            + (err or CARD_INVALID_CLOSING_DAY)
        )
        return CARD_CLOSING_DAY

    if context.user_data is not None:
        context.user_data[KEY_CARD_CLOSING_DAY] = day

    await message.reply_text("📅 Dia de vencimento da fatura (1 a 31):")
    return CARD_DUE_DAY


async def add_cartao_due_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive due day, validate, check duplicate, save card."""
    message = update.message
    if not message or not message.text:
        return CARD_DUE_DAY

    ok, day, err = validate_due_day(message.text)
    if not ok:
        await message.reply_text(
            "❌ Dia de vencimento inválido. Digite um número entre 1 e 31.\ncode: "
            + (err or CARD_INVALID_DUE_DAY)
        )
        return CARD_DUE_DAY

    user = update.effective_user
    if not user:
        return ConversationHandler.END

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return ConversationHandler.END

    user_data = context.user_data
    if not user_data:
        await message.reply_text("Erro: sessão perdida. Tente /add_cartao de novo.")
        return ConversationHandler.END

    name = user_data.get(KEY_CARD_NAME) or ""
    last_digits = user_data.get(KEY_CARD_LAST_DIGITS) or ""
    closing_day = user_data.get(KEY_CARD_CLOSING_DAY)
    if closing_day is None:
        await message.reply_text("Erro: dados incompletos. Tente /add_cartao de novo.")
        return ConversationHandler.END

    # Check duplicate: same user, same name (case-insensitive), not deleted
    with Session(engine) as session:
        stmt = (
            select(Card)
            .where(Card.user_id == db_user.id)
            .where(Card.deleted_at == None)  # noqa: E711
            .where(func.lower(Card.name) == name.lower())
        )
        existing = session.exec(stmt).first()
        if existing is not None:
            await message.reply_text("❌ Já existe um cartão com esse nome.\ncode: CARD.DUPLICATE")
            return CARD_DUE_DAY

        card = Card(
            user_id=db_user.id,
            name=name,
            last_digits=last_digits,
            closing_day=closing_day,
            due_day=day,
        )
        session.add(card)
        session.commit()
        session.refresh(card)

    # Clear conversation data
    user_data.pop(KEY_CARD_NAME, None)
    user_data.pop(KEY_CARD_LAST_DIGITS, None)
    user_data.pop(KEY_CARD_CLOSING_DAY, None)
    user_data.pop(KEY_CARD_DUE_DAY, None)

    await message.reply_text(
        "✅ Cartão cadastrado!\n\n"
        f"💳 {card.name} (*{card.last_digits})\n"
        f"📅 Fechamento: dia {card.closing_day}\n"
        f"📅 Vencimento: dia {card.due_day}"
    )
    return ConversationHandler.END


async def add_cartao_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel add card conversation."""
    if context.user_data:
        context.user_data.pop(KEY_CARD_NAME, None)
        context.user_data.pop(KEY_CARD_LAST_DIGITS, None)
        context.user_data.pop(KEY_CARD_CLOSING_DAY, None)
        context.user_data.pop(KEY_CARD_DUE_DAY, None)
    if update.message:
        await update.message.reply_text("Cadastro de cartão cancelado.")
    return ConversationHandler.END


# ---- /list_cartoes ----
async def list_cartoes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List active cards for the authenticated user."""
    message = update.message
    if not message:
        return

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return

    with Session(engine) as session:
        stmt = (
            select(Card)
            .where(Card.user_id == db_user.id)
            .where(Card.deleted_at == None)  # noqa: E711
            .order_by(Card.name)
        )
        cards = list(session.exec(stmt).all())

    if not cards:
        await message.reply_text(
            "📋 Você ainda não tem cartões cadastrados.\nUse /add_cartao para adicionar."
        )
        return

    lines = ["📋 Seus cartões:\n"]
    for c in cards:
        lines.append(
            f"• {c.name} (*{c.last_digits}) — fech. dia {c.closing_day}, "
            f"venc. dia {c.due_day} — ID: {c.id}"
        )
    await message.reply_text("\n".join(lines))


# ---- /delete_cartao ----
async def delete_cartao_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Soft delete card by id. Usage: /delete_cartao <id>."""
    message = update.message
    if not message:
        return

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return

    # Parse command args: /delete_cartao 1 or /delete_cartao 1 2
    text = (message.text or "").strip()
    parts = text.split()
    if len(parts) < 2:
        await message.reply_text(
            "Uso: /delete_cartao <id>\nUse /list_cartoes para ver os IDs dos seus cartões."
        )
        return

    try:
        card_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ ID deve ser um número.\ncode: CARD.NOT_FOUND")
        return

    card_name: str | None = None
    with Session(engine) as session:
        stmt = (
            select(Card)
            .where(Card.id == card_id)
            .where(Card.user_id == db_user.id)
            .where(Card.deleted_at == None)  # noqa: E711
        )
        card = session.exec(stmt).first()

        if card is None:
            await message.reply_text("❌ Cartão não encontrado.\ncode: CARD.NOT_FOUND")
            return

        card_name = card.name
        card.deleted_at = datetime.now(UTC)
        session.add(card)
        session.commit()

    await message.reply_text(f'✅ Cartão "{card_name}" removido.')
