"""Transcription service module.

Centraliza a interface pública para serviços de transcrição.
"""

from pathlib import Path

from .groq_whisper import TranscriptionError, transcribe_audio

__all__ = [
    "TranscriptionError",
    "transcribe_audio",
    "Path",
]
