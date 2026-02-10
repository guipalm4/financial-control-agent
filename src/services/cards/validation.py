"""Card validation (RULE-001): name, last_digits, closing_day, due_day."""

# Error codes per TECH_SPECS (map to consolidated error codes)
CARD_NAME_REQUIRED = "CARD.NAME_REQUIRED"
CARD_INVALID_DIGITS = "CARD.INVALID_DIGITS"
CARD_INVALID_CLOSING_DAY = "CARD.INVALID_CLOSING_DAY"
CARD_INVALID_DUE_DAY = "CARD.INVALID_DUE_DAY"


def validate_name(name: str) -> tuple[bool, str | None]:
    """Validate card name: non-empty, trimmed, max 50 chars.

    Returns:
        (True, None) if valid, (False, error_code) otherwise.
    """
    trimmed = (name or "").strip()
    if not trimmed:
        return False, CARD_NAME_REQUIRED
    if len(trimmed) > 50:
        return False, CARD_NAME_REQUIRED
    return True, None


def validate_last_digits(digits: str) -> tuple[bool, str | None]:
    """Validate last 4 digits: exactly 4 numeric characters (RULE-001).

    Returns:
        (True, None) if valid, (False, error_code) otherwise.
    """
    s = (digits or "").strip()
    if len(s) != 4 or not s.isdigit():
        return False, CARD_INVALID_DIGITS
    return True, None


def validate_closing_day(value: str) -> tuple[bool, int | None, str | None]:
    """Parse and validate closing day (1-31). RULE-001.

    Returns:
        (True, day_int, None) if valid, (False, None, error_code) otherwise.
    """
    s = (value or "").strip()
    if not s.isdigit():
        return False, None, CARD_INVALID_CLOSING_DAY
    day = int(s)
    if day < 1 or day > 31:
        return False, None, CARD_INVALID_CLOSING_DAY
    return True, day, None


def validate_due_day(value: str) -> tuple[bool, int | None, str | None]:
    """Parse and validate due day (1-31). RULE-001.

    Returns:
        (True, day_int, None) if valid, (False, None, error_code) otherwise.
    """
    s = (value or "").strip()
    if not s.isdigit():
        return False, None, CARD_INVALID_DUE_DAY
    day = int(s)
    if day < 1 or day > 31:
        return False, None, CARD_INVALID_DUE_DAY
    return True, day, None
