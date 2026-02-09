"""Unit tests for /login handler (PIN validation and flow)."""

from datetime import UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session, select

from src.bot.handlers.login import is_valid_pin, login_ask_pin, login_handler
from src.models import User
from src.services.auth import hash_pin


def test_login_is_valid_pin_accepts_4_to_6_digits() -> None:
    assert is_valid_pin("1234")
    assert is_valid_pin("12345")
    assert is_valid_pin("123456")


def test_login_is_valid_pin_rejects_non_digits() -> None:
    assert not is_valid_pin("abc123")
    assert not is_valid_pin("12 34")


def test_login_is_valid_pin_rejects_wrong_length() -> None:
    assert not is_valid_pin("123")
    assert not is_valid_pin("1234567")


@pytest.mark.asyncio
async def test_login_handler_no_user_ends_conversation() -> None:
    """When telegram user is not in DB, reply to use /start and END."""
    from sqlmodel import SQLModel, create_engine

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    update = MagicMock()
    update.effective_user = MagicMock(id=99999)
    update.message = MagicMock(reply_text=AsyncMock())
    context = MagicMock()

    with patch("src.bot.handlers.login.engine", test_engine):
        result = await login_handler(update, context)
        assert result == -1  # ConversationHandler.END
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "PIN" in text and "/start" in text


@pytest.mark.asyncio
async def test_login_handler_user_locked_returns_account_locked() -> None:
    """When user is locked, reply AUTH.ACCOUNT_LOCKED and END."""
    from datetime import datetime

    from sqlmodel import SQLModel, create_engine

    from src.services.auth.session import lock_duration

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        locked_until = datetime.now(UTC) + lock_duration()
        user = User(
            telegram_id=88888,
            pin_hash=hash_pin("1234"),
            failed_attempts=3,
            locked_until=locked_until,
        )
        session.add(user)
        session.commit()

    update = MagicMock()
    update.effective_user = MagicMock(id=88888)
    update.message = MagicMock(reply_text=AsyncMock())
    context = MagicMock()

    with patch("src.bot.handlers.login.engine", test_engine):
        result = await login_handler(update, context)
        assert result == -1
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "AUTH.ACCOUNT_LOCKED" in text
        assert "bloqueada" in text


@pytest.mark.asyncio
async def test_login_ask_pin_three_wrong_pins_locks_account() -> None:
    """TEST-003: After 3 wrong PINs, account is locked (AUTH.ACCOUNT_LOCKED)."""
    from sqlmodel import SQLModel, create_engine

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        user = User(
            telegram_id=77777,
            pin_hash=hash_pin("123456"),
            failed_attempts=0,
        )
        session.add(user)
        session.commit()

    update = MagicMock()
    update.effective_user = MagicMock(id=77777)
    update.message = MagicMock(text="000000", reply_text=AsyncMock())
    context = MagicMock()

    with patch("src.bot.handlers.login.engine", test_engine):
        # First wrong PIN
        await login_ask_pin(update, context)
        # Second wrong PIN
        await login_ask_pin(update, context)
        # Third wrong PIN -> lock
        result = await login_ask_pin(update, context)

        assert result == -1
        calls = update.message.reply_text.call_args_list
        last_text = calls[-1][0][0]
        assert "AUTH.ACCOUNT_LOCKED" in last_text
        assert "bloqueada" in last_text

        with Session(test_engine) as session:
            stmt = select(User).where(User.telegram_id == 77777)
            u = session.exec(stmt).first()
            assert u is not None
            assert u.failed_attempts == 3
            assert u.locked_until is not None
