"""Groq Whisper transcription service.

Responsável por integrar com a API da Groq usando o cliente AsyncGroq
para transcrever áudios utilizando o modelo Whisper.

Este módulo NÃO deve ser responsável por lógica de Telegram ou de
persistência, apenas por transformar um arquivo de áudio em texto.
"""

from __future__ import annotations

from pathlib import Path

import groq
from groq import AsyncGroq

from src.core.config import settings


class TranscriptionError(Exception):
    """Erro de alto nível ao transcrever áudio via Groq."""


_async_client: AsyncGroq | None = None


def _get_async_client() -> AsyncGroq:
    """Return a cached AsyncGroq client configured with the API key.

    Levanta TranscriptionError se a API key não estiver configurada,
    para falhar de forma explícita no ambiente de desenvolvimento.
    """
    global _async_client

    if _async_client is not None:
        return _async_client

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise TranscriptionError(
            "GROQ_API_KEY não configurada. Defina a variável de ambiente para usar o "
            "serviço de transcrição."
        )

    _async_client = AsyncGroq(api_key=api_key)
    return _async_client


async def transcribe_audio(path: Path, language: str = "pt") -> str:
    """Transcribe an audio file into text using Groq Whisper.

    Parameters
    ----------
    path:
        Caminho para o arquivo de áudio já salvo em disco.
    language:
        Código da língua em ISO-639-1. Default: \"pt\".

    Returns
    -------
    str
        Texto transcrito.

    Raises
    ------
    TranscriptionError
        Em falhas de configuração, comunicação com a API ou resposta vazia.
    """
    client = _get_async_client()

    try:
        # Quando response_format=\"text\", a API retorna uma string simples.
        result = await client.audio.transcriptions.create(
            file=path,
            model="whisper-large-v3-turbo",
            language=language,
            response_format="text",
        )
    except (groq.APIError, OSError) as exc:
        # APIError cobre erros de conexão, timeouts, rate limit e respostas 4xx/5xx.
        # OSError cobre problemas locais de arquivo (ex.: permissão ou inexistente).
        raise TranscriptionError("Falha ao transcrever áudio via Groq.") from exc

    if isinstance(result, str):
        text = result.strip()
    else:
        # fallback defensivo caso a biblioteca mude a forma de retorno
        text = getattr(result, "text", "").strip()

    if not text:
        raise TranscriptionError("Resposta vazia da API de transcrição.")

    return text
