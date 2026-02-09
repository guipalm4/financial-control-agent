"""Unit tests for session and lock helpers (RULE-007, RULE-008)."""

from datetime import UTC, datetime, timedelta

from src.models import User
from src.services.auth import hash_pin
from src.services.auth.session import is_locked, is_session_valid, lock_duration


def test_lock_duration_is_15_minutes() -> None:
    assert lock_duration() == timedelta(minutes=15)


def test_is_locked_none_returns_false() -> None:
    user = User(telegram_id=1, pin_hash=hash_pin("1234"), locked_until=None)
    assert is_locked(user) is False


def test_is_locked_future_returns_true() -> None:
    later = datetime.now(UTC) + timedelta(minutes=5)
    user = User(telegram_id=1, pin_hash=hash_pin("1234"), locked_until=later)
    assert is_locked(user) is True


def test_is_locked_past_returns_false() -> None:
    past = datetime.now(UTC) - timedelta(minutes=5)
    user = User(telegram_id=1, pin_hash=hash_pin("1234"), locked_until=past)
    assert is_locked(user) is False


def test_is_session_valid_none_returns_false() -> None:
    user = User(telegram_id=1, pin_hash=hash_pin("1234"), last_login=None)
    assert is_session_valid(user) is False


def test_is_session_valid_within_24h_returns_true() -> None:
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    user = User(
        telegram_id=1,
        pin_hash=hash_pin("1234"),
        last_login=one_hour_ago,
    )
    assert is_session_valid(user) is True


def test_is_session_valid_over_24h_returns_false() -> None:
    twenty_five_hours_ago = datetime.now(UTC) - timedelta(hours=25)
    user = User(
        telegram_id=1,
        pin_hash=hash_pin("1234"),
        last_login=twenty_five_hours_ago,
    )
    assert is_session_valid(user) is False


def test_is_session_valid_naive_datetime_uses_utc() -> None:
    """last_login without tzinfo is treated as UTC."""
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    user = User(
        telegram_id=1,
        pin_hash=hash_pin("1234"),
        last_login=one_hour_ago,
    )
    assert is_session_valid(user) is True
