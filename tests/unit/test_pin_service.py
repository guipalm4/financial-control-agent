"""Unit tests for PIN hash and verify service."""

from src.services.auth import hash_pin, verify_pin


def test_hash_pin_returns_str() -> None:
    """hash_pin returns a non-empty string."""
    result = hash_pin("1234")
    assert isinstance(result, str)
    assert len(result) > 0
    assert result.startswith("$2b$")


def test_verify_pin_matches() -> None:
    """verify_pin returns True when PIN matches hash."""
    pin = "5678"
    hashed = hash_pin(pin)
    assert verify_pin(pin, hashed) is True


def test_verify_pin_wrong_pin() -> None:
    """verify_pin returns False when PIN does not match."""
    hashed = hash_pin("1234")
    assert verify_pin("0000", hashed) is False


def test_verify_pin_different_hashes() -> None:
    """Same PIN hashed twice produces different salts, both verify."""
    pin = "9999"
    h1 = hash_pin(pin)
    h2 = hash_pin(pin)
    assert h1 != h2
    assert verify_pin(pin, h1) is True
    assert verify_pin(pin, h2) is True
