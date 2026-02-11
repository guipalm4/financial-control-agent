"""Unit tests for extraction service (Gemini Flash)."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.genai import errors

from src.services.extraction import ExtractionError, ExtractionResponse, extract_expense


@pytest.mark.asyncio
async def test_extract_expense_success_returns_extraction_response() -> None:
    """When Gemini returns valid JSON, service should return ExtractionResponse."""
    transcription = "Gastei trinta reais no Uber hoje"

    # Mock da resposta do Gemini
    mock_response = MagicMock()
    mock_response.parsed = ExtractionResponse(
        description="Uber",
        amount=30.0,
        date="2026-02-10",
        category_suggestion="Transporte",
        is_essential=False,
        confidence=0.9,
    )

    mock_client = MagicMock()
    mock_client.aio = MagicMock()
    mock_client.aio.models = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch(
        "src.services.extraction.gemini_extraction._get_async_client",
        return_value=mock_client,
    ):
        result = await extract_expense(transcription)

    assert isinstance(result, ExtractionResponse)
    assert result.description == "Uber"
    assert result.amount == 30.0
    assert result.date == "2026-02-10"
    assert result.category_suggestion == "Transporte"
    assert result.is_essential is False
    assert result.confidence == 0.9
    assert not result.is_error()


@pytest.mark.asyncio
async def test_extract_expense_raises_on_api_error() -> None:
    """When Gemini API raises APIError, service should raise ExtractionError."""
    transcription = "Gastei trinta reais no Uber hoje"

    # Cria um mock de APIError com os parâmetros obrigatórios
    api_error = errors.APIError(code=500, response_json={"error": {"message": "API error"}})

    mock_client = MagicMock()
    mock_client.aio = MagicMock()
    mock_client.aio.models = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_error)

    with patch(
        "src.services.extraction.gemini_extraction._get_async_client",
        return_value=mock_client,
    ):
        with pytest.raises(ExtractionError, match="Falha ao extrair entidades via Gemini"):
            await extract_expense(transcription)


@pytest.mark.asyncio
async def test_extract_expense_handles_not_detected_error() -> None:
    """When Gemini returns NOT_DETECTED error, service should return error response."""
    transcription = "Oi, como você está?"

    mock_response = MagicMock()
    mock_response.parsed = ExtractionResponse.model_validate({"error": "NOT_DETECTED"})

    mock_client = MagicMock()
    mock_client.aio = MagicMock()
    mock_client.aio.models = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch(
        "src.services.extraction.gemini_extraction._get_async_client",
        return_value=mock_client,
    ):
        result = await extract_expense(transcription)

    assert isinstance(result, ExtractionResponse)
    assert result.is_error()
    assert result.error == "NOT_DETECTED"


@pytest.mark.asyncio
async def test_extract_expense_uses_custom_date() -> None:
    """When today is provided, service should use it for date reference."""
    transcription = "Gastei trinta reais no Uber ontem"
    custom_date = date(2026, 2, 15)

    mock_response = MagicMock()
    mock_response.parsed = ExtractionResponse(
        description="Uber",
        amount=30.0,
        date="2026-02-14",  # yesterday relative to custom_date
        category_suggestion="Transporte",
        is_essential=False,
        confidence=0.9,
    )

    mock_client = MagicMock()
    mock_client.aio = MagicMock()
    mock_client.aio.models = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch(
        "src.services.extraction.gemini_extraction._get_async_client",
        return_value=mock_client,
    ):
        result = await extract_expense(transcription, today=custom_date)

    assert result.date == "2026-02-14"
    # Verifica que o prompt foi construído com a data customizada
    call_args = mock_client.aio.models.generate_content.await_args
    assert call_args is not None
    assert "2026-02-15" in str(call_args.kwargs.get("contents", ""))
