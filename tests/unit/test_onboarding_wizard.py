"""Unit tests for onboarding wizard message after PIN creation."""

from src.bot.handlers.start import build_onboarding_message


def test_build_onboarding_message_includes_core_commands_and_skip_hint() -> None:
    text = build_onboarding_message("Gui")

    assert "PIN criado" in text
    assert "/add_cartao" in text
    assert "/list_cartoes" in text
    assert "/add_categoria" in text
    # User must clearly know they can skip onboarding for later
    assert "pular esta etapa" in text or "pular" in text.lower()


def test_build_onboarding_message_handles_missing_name() -> None:
    text = build_onboarding_message(None)

    assert "PIN criado" in text
    # Should not render the Python None literal
    assert "None" not in text
