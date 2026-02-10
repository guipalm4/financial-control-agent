"""Unit tests for card CRUD handlers (FEAT-010): add_cartao, list_cartoes, delete_cartao."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session, select

from src.bot.handlers.auth_helpers import get_authenticated_user
from src.models import Card, User
from src.services.auth import hash_pin


@pytest.mark.asyncio
async def test_get_authenticated_user_no_user_replies_start() -> None:
    """When telegram user is not in DB, reply to use /start."""
    from sqlmodel import SQLModel, create_engine

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    update = MagicMock()
    update.effective_user = MagicMock(id=99999)
    update.message = MagicMock(reply_text=AsyncMock())

    with patch("src.bot.handlers.auth_helpers.engine", test_engine):
        result = await get_authenticated_user(update)
    assert result is None
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "/start" in text


@pytest.mark.asyncio
async def test_get_authenticated_user_session_expired_replies_code() -> None:
    """When last_login is older than 24h, reply AUTH.SESSION_EXPIRED."""
    from sqlmodel import SQLModel, create_engine

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        user = User(
            telegram_id=11111,
            pin_hash=hash_pin("1234"),
            last_login=datetime.now(UTC) - timedelta(hours=25),
        )
        session.add(user)
        session.commit()

    update = MagicMock()
    update.effective_user = MagicMock(id=11111)
    update.message = MagicMock(reply_text=AsyncMock())

    with patch("src.bot.handlers.auth_helpers.engine", test_engine):
        result = await get_authenticated_user(update)
    assert result is None
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "AUTH.SESSION_EXPIRED" in text
    assert "/login" in text


@pytest.mark.asyncio
async def test_add_cartao_name_rejects_empty() -> None:
    """add_cartao_name: empty name -> CARD.NAME_REQUIRED."""
    from src.bot.handlers.cards import add_cartao_name

    update = MagicMock()
    update.message = MagicMock(text="   ")
    update.message.reply_text = AsyncMock()
    context = MagicMock(user_data={})

    result = await add_cartao_name(update, context)
    assert result == 0  # CARD_NAME state
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "CARD.NAME_REQUIRED" in text or "nome" in text.lower()


@pytest.mark.asyncio
async def test_add_cartao_last_digits_rejects_invalid() -> None:
    """TEST-011: last_digits '12AB' -> CARD.INVALID_DIGITS."""
    from src.bot.handlers.cards import add_cartao_last_digits

    update = MagicMock()
    update.message = MagicMock(text="12AB")
    update.message.reply_text = AsyncMock()
    context = MagicMock(user_data={"card_name": "Nubank"})

    result = await add_cartao_last_digits(update, context)
    assert result == 1  # CARD_LAST_DIGITS state
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "CARD.INVALID_DIGITS" in text
    assert "4 dígitos" in text or "dígitos" in text


@pytest.mark.asyncio
async def test_add_cartao_closing_day_rejects_invalid() -> None:
    """TEST-012: closing_day '35' -> CARD.INVALID_CLOSING_DAY."""
    from src.bot.handlers.cards import add_cartao_closing_day

    update = MagicMock()
    update.message = MagicMock(text="35")
    update.message.reply_text = AsyncMock()
    context = MagicMock(user_data={"card_name": "Nubank", "card_last_digits": "1234"})

    result = await add_cartao_closing_day(update, context)
    assert result == 2  # CARD_CLOSING_DAY state
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "CARD.INVALID_CLOSING_DAY" in text or "fechamento inválido" in text.lower()


@pytest.mark.asyncio
async def test_add_cartao_start_requires_auth() -> None:
    """add_cartao_start: when not authenticated, replies and END."""
    from sqlmodel import SQLModel, create_engine

    from src.bot.handlers.cards import add_cartao_start

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    update = MagicMock()
    update.effective_user = MagicMock(id=99999)
    update.message = MagicMock(reply_text=AsyncMock())
    context = MagicMock(user_data={})

    with patch("src.bot.handlers.auth_helpers.engine", test_engine):
        result = await add_cartao_start(update, context)
    assert result == -1  # ConversationHandler.END
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_add_cartao_full_flow_saves_card() -> None:
    """TEST-010 (happy path): add_cartao flow creates card and replies with summary."""
    from sqlmodel import SQLModel, create_engine

    from src.bot.handlers.cards import (
        add_cartao_closing_day,
        add_cartao_due_day,
        add_cartao_last_digits,
        add_cartao_name,
        add_cartao_start,
    )

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        user = User(
            telegram_id=55555,
            pin_hash=hash_pin("1234"),
            last_login=datetime.now(UTC),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        assert user_id is not None

    update = MagicMock()
    update.effective_user = MagicMock(id=55555)
    update.message = MagicMock(reply_text=AsyncMock())
    context = MagicMock(user_data={})

    with (
        patch("src.bot.handlers.auth_helpers.engine", test_engine),
        patch("src.bot.handlers.cards.engine", test_engine),
    ):
        res = await add_cartao_start(update, context)
        assert res == 0
        update.message.reply_text.reset_mock()

        update.message.text = "Nubank"
        res = await add_cartao_name(update, context)
        assert res == 1
        update.message.reply_text.reset_mock()

        update.message.text = "1234"
        res = await add_cartao_last_digits(update, context)
        assert res == 2
        update.message.reply_text.reset_mock()

        update.message.text = "10"
        res = await add_cartao_closing_day(update, context)
        assert res == 3
        update.message.reply_text.reset_mock()

        update.message.text = "18"
        res = await add_cartao_due_day(update, context)
        assert res == -1  # END

    # Check DB
    with Session(test_engine) as session:
        stmt = select(Card).where(Card.user_id == user_id).where(Card.deleted_at.is_(None))
        cards = list(session.exec(stmt).all())
    assert len(cards) == 1
    assert cards[0].name == "Nubank"
    assert cards[0].last_digits == "1234"
    assert cards[0].closing_day == 10
    assert cards[0].due_day == 18

    text = update.message.reply_text.call_args[0][0]
    assert "✅ Cartão cadastrado!" in text
    assert "Nubank" in text and "1234" in text
    assert "Fechamento: dia 10" in text and "Vencimento: dia 18" in text
