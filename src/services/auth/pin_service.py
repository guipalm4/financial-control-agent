"""PIN hashing and verification using bcrypt (cost=12)."""

import bcrypt

# Bcrypt cost factor (rounds). PRD: cost=12.
PIN_BCRYPT_COST = 12


def hash_pin(pin: str) -> str:
    """Hash a PIN with bcrypt.

    Args:
        pin: Plain PIN (4-6 digits). Caller must validate format.

    Returns:
        Bcrypt hash string (ASCII, suitable for storing in DB).
    """
    salt = bcrypt.gensalt(rounds=PIN_BCRYPT_COST)
    hashed = bcrypt.hashpw(pin.encode("utf-8"), salt)
    return hashed.decode("ascii")


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify a PIN against a stored hash.

    Args:
        pin: Plain PIN to check.
        pin_hash: Stored bcrypt hash (from User.pin_hash).

    Returns:
        True if PIN matches, False otherwise.
    """
    return bcrypt.checkpw(
        pin.encode("utf-8"),
        pin_hash.encode("ascii"),
    )
