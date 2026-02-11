"""Gemini Flash extraction service.

Responsável por integrar com a API do Google Generative AI (Gemini Flash)
para extrair entidades de despesa (valor, descrição, data, categoria) de
textos transcritos.

Este módulo NÃO deve ser responsável por lógica de Telegram ou de
persistência, apenas por transformar texto transcrito em dados estruturados.
"""

from __future__ import annotations

from datetime import date

from google import genai
from google.genai import errors, types

from src.core.config import settings
from src.services.extraction.models import ExtractionResponse
from src.services.extraction.prompts import build_extraction_prompt

# Cliente global para reutilização
_async_client: genai.Client | None = None


class ExtractionError(Exception):
    """Erro de alto nível ao extrair entidades via Gemini."""


def _get_async_client() -> genai.Client:
    """Return a cached Gemini client configured with the API key.

    Levanta ExtractionError se a API key não estiver configurada,
    para falhar de forma explícita no ambiente de desenvolvimento.
    """
    global _async_client

    if _async_client is not None:
        return _async_client

    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        raise ExtractionError(
            "GOOGLE_API_KEY não configurada. Defina a variável de ambiente para usar o "
            "serviço de extração."
        )

    _async_client = genai.Client(api_key=api_key)
    return _async_client


async def extract_expense(transcription: str, today: date | None = None) -> ExtractionResponse:
    """Extrai entidades de despesa de um texto transcrito usando Gemini Flash.

    Parameters
    ----------
    transcription:
        Texto transcrito do áudio de despesa.
    today:
        Data atual para referência de datas relativas. Se None, usa date.today().

    Returns
    -------
    ExtractionResponse
        Resposta estruturada com despesa(s) extraída(s) ou erro.

    Raises
    ------
    ExtractionError
        Em falhas de configuração, comunicação com a API ou resposta inválida.
    """
    if today is None:
        today = date.today()

    client = _get_async_client()
    prompt = build_extraction_prompt(transcription, today)

    try:
        # Usa o cliente async via .aio
        response = await client.aio.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResponse,
            ),
        )
    except errors.APIError as exc:
        # APIError cobre erros de conexão, timeouts, rate limit e respostas 4xx/5xx
        raise ExtractionError(f"Falha ao extrair entidades via Gemini: {exc.message}") from exc
    except Exception as exc:
        # Outros erros inesperados
        raise ExtractionError("Erro inesperado ao extrair entidades via Gemini.") from exc

    # Tenta obter o objeto parseado (Pydantic)
    if hasattr(response, "parsed") and response.parsed is not None:
        parsed = response.parsed
        if isinstance(parsed, ExtractionResponse):
            return parsed

    # Fallback: tenta parsear o texto manualmente
    if hasattr(response, "text") and response.text:
        import json

        try:
            data = json.loads(response.text)
            return ExtractionResponse(**data)
        except (json.JSONDecodeError, ValueError) as exc:
            error_msg = f"Resposta inválida do Gemini (não é JSON válido): {response.text}"
            raise ExtractionError(error_msg) from exc

    raise ExtractionError("Resposta vazia da API de extração.")
