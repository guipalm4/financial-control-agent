"""Unit tests for the Groq Whisper transcription service (AUDIO-001)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import groq
import pytest

from src.services.transcription import TranscriptionError, transcribe_audio


@pytest.mark.asyncio
async def test_transcribe_audio_success_returns_text(tmp_path: Path) -> None:
    """When Groq returns text successfully, service should return the same text."""
    audio_path = tmp_path / "audio.ogg"
    audio_path.write_bytes(b"dummy")  # conteúdo não é relevante, chamada é mockada

    async_mock = AsyncMock(return_value="texto de teste")
    fake_client = MagicMock()
    fake_client.audio.transcriptions.create = async_mock

    with patch(
        "src.services.transcription.groq_whisper._get_async_client",
        return_value=fake_client,
    ):
        result = await transcribe_audio(audio_path)

    assert result == "texto de teste"
    async_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_transcribe_audio_raises_on_exception(tmp_path: Path) -> None:
    """If the underlying client raises, TranscriptionError should be raised."""
    audio_path = tmp_path / "audio.ogg"
    audio_path.write_bytes(b"dummy")

    async_mock = AsyncMock(
        side_effect=groq.APIError(message="boom", request=MagicMock(), body=None)
    )
    fake_client = MagicMock()
    fake_client.audio.transcriptions.create = async_mock

    with patch(
        "src.services.transcription.groq_whisper._get_async_client",
        return_value=fake_client,
    ):
        with pytest.raises(TranscriptionError):
            await transcribe_audio(audio_path)


@pytest.mark.asyncio
async def test_transcribe_audio_raises_on_empty_response(tmp_path: Path) -> None:
    """Empty or whitespace-only responses are treated as errors."""
    audio_path = tmp_path / "audio.ogg"
    audio_path.write_bytes(b"dummy")

    async_mock = AsyncMock(return_value="   ")
    fake_client = MagicMock()
    fake_client.audio.transcriptions.create = async_mock

    with patch(
        "src.services.transcription.groq_whisper._get_async_client",
        return_value=fake_client,
    ):
        with pytest.raises(TranscriptionError):
            await transcribe_audio(audio_path)
