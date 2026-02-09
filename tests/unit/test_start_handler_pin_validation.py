"""Unit tests for /start PIN validation helpers."""

from src.bot.handlers.start import is_valid_pin


def test_is_valid_pin_accepts_4_to_6_digits() -> None:
    assert is_valid_pin("1234")
    assert is_valid_pin("12345")
    assert is_valid_pin("123456")


def test_is_valid_pin_rejects_non_digits() -> None:
    assert not is_valid_pin("abc123")
    assert not is_valid_pin("12 34")
    assert not is_valid_pin("12-34")


def test_is_valid_pin_rejects_wrong_length() -> None:
    assert not is_valid_pin("")
    assert not is_valid_pin("123")
    assert not is_valid_pin("1234567")
