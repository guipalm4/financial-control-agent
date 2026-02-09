"""Example unit tests."""


def test_example_unit():
    """Example unit test."""
    assert True


def test_db_session_fixture(db_session):
    """Test that db_session fixture works."""
    assert db_session is not None


def test_bot_app_fixture(bot_app):
    """Test that bot_app fixture works."""
    assert bot_app is not None
