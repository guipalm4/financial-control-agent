"""Session and account lock logic (RULE-007, RULE-008)."""

from datetime import UTC, datetime, timedelta

from src.models import User

# RULE-007: lock duration after 3 failed PIN attempts
LOCK_DURATION_MINUTES = 15
# RULE-008: session valid for 24h after last_login
SESSION_VALID_HOURS = 24


def is_locked(user: User) -> bool:
    """Return True if user account is locked (within lock window)."""
    if user.locked_until is None:
        return False
    now = datetime.now(UTC)
    # Ensure comparison is timezone-aware
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=UTC)
    return now < locked_until


def is_session_valid(user: User) -> bool:
    """Return True if user has a valid session (last_login within 24h)."""
    if user.last_login is None:
        return False
    now = datetime.now(UTC)
    last = user.last_login
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    return (now - last) <= timedelta(hours=SESSION_VALID_HOURS)


def lock_duration() -> timedelta:
    """Return the lock duration (15 minutes)."""
    return timedelta(minutes=LOCK_DURATION_MINUTES)
