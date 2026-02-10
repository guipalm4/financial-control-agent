"""Unit tests for card validation (RULE-001) — TEST-011, TEST-012."""

from src.services.cards.validation import (
    CARD_INVALID_CLOSING_DAY,
    CARD_INVALID_DIGITS,
    CARD_INVALID_DUE_DAY,
    CARD_NAME_REQUIRED,
    validate_closing_day,
    validate_due_day,
    validate_last_digits,
    validate_name,
)


# ---- name ----
def test_validate_name_accepts_non_empty_trimmed() -> None:
    ok, err = validate_name("Nubank")
    assert ok is True
    assert err is None


def test_validate_name_rejects_empty() -> None:
    ok, err = validate_name("")
    assert ok is False
    assert err == CARD_NAME_REQUIRED


def test_validate_name_rejects_whitespace_only() -> None:
    ok, err = validate_name("   ")
    assert ok is False
    assert err == CARD_NAME_REQUIRED


def test_validate_name_trims_input() -> None:
    ok, err = validate_name("  Nubank  ")
    assert ok is True
    assert err is None


# ---- last_digits (TEST-011: 4 dígitos numéricos) ----
def test_validate_last_digits_accepts_four_digits() -> None:
    ok, err = validate_last_digits("1234")
    assert ok is True
    assert err is None


def test_validate_last_digits_rejects_non_numeric() -> None:
    """TEST-011: Dígitos inválidos (12AB) -> CARD.INVALID_DIGITS."""
    ok, err = validate_last_digits("12AB")
    assert ok is False
    assert err == CARD_INVALID_DIGITS


def test_validate_last_digits_rejects_three_digits() -> None:
    ok, err = validate_last_digits("123")
    assert ok is False
    assert err == CARD_INVALID_DIGITS


def test_validate_last_digits_rejects_five_digits() -> None:
    ok, err = validate_last_digits("12345")
    assert ok is False
    assert err == CARD_INVALID_DIGITS


# ---- closing_day (TEST-012: 1-31) ----
def test_validate_closing_day_accepts_1_to_31() -> None:
    ok, day, err = validate_closing_day("10")
    assert ok is True
    assert day == 10
    assert err is None

    ok, day, err = validate_closing_day("1")
    assert ok is True
    assert day == 1

    ok, day, err = validate_closing_day("31")
    assert ok is True
    assert day == 31


def test_validate_closing_day_rejects_out_of_range() -> None:
    """TEST-012: Dia de fechamento inválido (35) -> CARD.INVALID_CLOSING_DAY."""
    ok, day, err = validate_closing_day("35")
    assert ok is False
    assert day is None
    assert err == CARD_INVALID_CLOSING_DAY


def test_validate_closing_day_rejects_zero_and_negative() -> None:
    ok, day, err = validate_closing_day("0")
    assert ok is False
    assert err == CARD_INVALID_CLOSING_DAY

    ok, day, err = validate_closing_day("-1")
    assert ok is False  # -1 after strip is still "-1", isdigit() is False for "-1"
    assert err == CARD_INVALID_CLOSING_DAY


# ---- due_day ----
def test_validate_due_day_accepts_1_to_31() -> None:
    ok, day, err = validate_due_day("18")
    assert ok is True
    assert day == 18
    assert err is None


def test_validate_due_day_rejects_out_of_range() -> None:
    ok, day, err = validate_due_day("32")
    assert ok is False
    assert day is None
    assert err == CARD_INVALID_DUE_DAY
