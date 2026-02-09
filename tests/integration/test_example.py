"""Example integration tests."""
import pytest

from tests.conftest import db_session, bot_app_async


@pytest.mark.integration
def test_example_integration():
    """Example integration test."""
    assert True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bot_app_async_fixture(bot_app_async):
    """Test that bot_app_async fixture works."""
    assert bot_app_async is not None
