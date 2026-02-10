"""Unit tests for the audio/voice handler (AUDIO-001)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.handlers.audio import audio_message_handler
from src.services.transcription import TranscriptionError


@pytest.mark.asyncio
async def test_audio_handler_rejects_audio_too_long() -> None:
    """TEST-023: áudio > 60s deve responder com AUDIO.TOO_LONG e não transcrever."""
    update = MagicMock()
    message = MagicMock()
    message.reply_text = AsyncMock()
    voice = MagicMock()
    voice.duration = 61
    voice.file_unique_id = "unique"
    message.voice = voice
    update.message = message

    context = MagicMock()

    with (
        patch(
            "src.bot.handlers.audio.get_authenticated_user",
            new=AsyncMock(return_value=MagicMock(id=1)),
        ),
        patch(
            "src.bot.handlers.audio.transcribe_audio",
            new=AsyncMock(),
        ) as transcribe_mock,
    ):
        await audio_message_handler(update, context)

    message.reply_text.assert_awaited()
    text = message.reply_text.await_args.args[0]
    assert "AUDIO.TOO_LONG" in text
    transcribe_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_audio_handler_success_calls_transcription_and_replies_preview() -> None:
    """Happy path: áudio dentro do limite → transcrição chamada e preview enviado."""
    update = MagicMock()
    message = MagicMock()
    message.reply_text = AsyncMock()
    voice = MagicMock()
    voice.duration = 10
    voice.file_unique_id = "unique2"
    voice.file_id = "file-id"
    message.voice = voice
    update.message = message

    context = MagicMock()
    fake_file = MagicMock()
    fake_file.download_to_drive = AsyncMock()
    context.bot.get_file = AsyncMock(return_value=fake_file)

    with (
        patch(
            "src.bot.handlers.audio.MAX_AUDIO_DURATION_SECONDS",
            120,
        ),
        patch(
            "src.bot.handlers.audio.get_authenticated_user",
            new=AsyncMock(return_value=MagicMock(id=1)),
        ),
        patch(
            "src.bot.handlers.audio.transcribe_audio",
            new=AsyncMock(return_value="gastei trinta reais no uber hoje"),
        ) as transcribe_mock,
    ):
        await audio_message_handler(update, context)

    context.bot.get_file.assert_awaited_once_with("file-id")
    fake_file.download_to_drive.assert_awaited()
    transcribe_mock.assert_awaited()
    message.reply_text.assert_awaited()
    text = message.reply_text.await_args.args[0]
    assert "Prévia da transcrição" in text


@pytest.mark.asyncio
async def test_audio_handler_transcription_error_returns_audio_transcription_failed() -> None:
    """Quando o serviço de transcrição falha, deve responder AUDIO.TRANSCRIPTION_FAILED."""
    update = MagicMock()
    message = MagicMock()
    message.reply_text = AsyncMock()
    voice = MagicMock()
    voice.duration = 10
    voice.file_unique_id = "unique3"
    voice.file_id = "file-id-3"
    message.voice = voice
    update.message = message

    context = MagicMock()
    fake_file = MagicMock()
    fake_file.download_to_drive = AsyncMock()
    context.bot.get_file = AsyncMock(return_value=fake_file)

    with (
        patch(
            "src.bot.handlers.audio.MAX_AUDIO_DURATION_SECONDS",
            120,
        ),
        patch(
            "src.bot.handlers.audio.get_authenticated_user",
            new=AsyncMock(return_value=MagicMock(id=1)),
        ),
        patch(
            "src.bot.handlers.audio.transcribe_audio",
            new=AsyncMock(side_effect=TranscriptionError("boom")),
        ),
    ):
        await audio_message_handler(update, context)

    message.reply_text.assert_awaited()
    text = message.reply_text.await_args.args[0]
    assert "AUDIO.TRANSCRIPTION_FAILED" in text
