"""Handler for audio/voice messages (FEAT-003, AUDIO-001).

Neste estágio, o handler:
1. Garante que o usuário está autenticado (sessão válida).
2. Valida a duração máxima do áudio (60 segundos).
3. Faz o download temporário do arquivo de áudio do Telegram.
4. Usa o serviço de transcrição Groq Whisper para obter o texto.
5. Retorna uma mensagem de prévia da transcrição ou erros AUDIO.* adequados.

A extração de entidades, categorização e fluxo de confirmação serão
implementados em tasks futuras (AUDIO-002+).
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from src.bot.handlers.auth_helpers import get_authenticated_user
from src.core.config import settings
from src.services.transcription import TranscriptionError, transcribe_audio

logger = logging.getLogger(__name__)

MAX_AUDIO_DURATION_SECONDS = settings.AUDIO_MAX_DURATION_SECONDS


async def audio_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice messages from authenticated users.

    Regras principais:
    - Rejeita áudios com duração > 60s (AUDIO.TOO_LONG).
    - Em falhas de transcrição ou download, responde com AUDIO.TRANSCRIPTION_FAILED.
    - Em sucesso, envia apenas uma prévia da transcrição (sem integração ainda
      com Gemini/fluxo de confirmação).
    """
    message = update.message
    if not message:
        return

    # Garante sessão/autenticação antes de qualquer processamento pesado.
    db_user = await get_authenticated_user(update)
    if db_user is None:
        return

    voice = message.voice
    if voice is None:
        await message.reply_text(
            "❌ Formato de áudio não suportado.\ncode: AUDIO.FORMAT_NOT_SUPPORTED"
        )
        return

    duration_seconds = int(getattr(voice, "duration", 0) or 0)
    if duration_seconds > MAX_AUDIO_DURATION_SECONDS:
        await message.reply_text(
            "❌ Áudio muito longo. Máximo permitido: "
            f"{MAX_AUDIO_DURATION_SECONDS} segundos.\ncode: AUDIO.TOO_LONG"
        )
        return

    try:
        tg_file = await context.bot.get_file(voice.file_id)
    except TelegramError:
        logger.exception("Erro ao obter arquivo de áudio do Telegram para user_id=%s", db_user.id)
        await message.reply_text(
            "❌ Erro ao processar o áudio. Tente novamente.\ncode: AUDIO.TRANSCRIPTION_FAILED"
        )
        return

    tmp_path = Path(tempfile.gettempdir()) / f"voice_{voice.file_unique_id}.ogg"

    try:
        await tg_file.download_to_drive(custom_path=str(tmp_path))
    except (TelegramError, OSError):
        logger.exception("Erro ao baixar arquivo de áudio para user_id=%s", db_user.id)
        await message.reply_text(
            "❌ Erro ao processar o áudio. Tente novamente.\ncode: AUDIO.TRANSCRIPTION_FAILED"
        )
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        return

    try:
        transcription = await transcribe_audio(tmp_path)
    except TranscriptionError:
        logger.exception("Falha na transcrição do áudio para user_id=%s", db_user.id)
        await message.reply_text(
            "❌ Erro ao transcrever o áudio. Tente novamente.\ncode: AUDIO.TRANSCRIPTION_FAILED"
        )
        return
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    preview = transcription.strip()
    if len(preview) > 400:
        preview = f"{preview[:397]}..."

    await message.reply_text(
        "📝 Prévia da transcrição do seu áudio:\n\n"
        f'"{preview}"\n\n'
        "Obs.: o fluxo completo de extração de dados e confirmação ainda está em desenvolvimento."
    )
