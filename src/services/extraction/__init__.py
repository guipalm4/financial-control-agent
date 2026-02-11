"""Extraction service module.

Centraliza a interface pública para serviços de extração de entidades.
"""

from .gemini_extraction import ExtractionError, extract_expense
from .models import (
    ExpenseExtraction,
    ExtractionResponse,
    MultipleExpensesExtraction,
)

__all__ = [
    "ExtractionError",
    "ExpenseExtraction",
    "ExtractionResponse",
    "MultipleExpensesExtraction",
    "extract_expense",
]
