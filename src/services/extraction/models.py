"""Pydantic models for expense extraction from transcribed audio."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ExpenseExtraction(BaseModel):
    """Modelo para extração de despesa única do texto transcrito."""

    description: str = Field(..., description="Descrição curta da despesa")
    amount: float = Field(..., ge=0, description="Valor da despesa em R$ (BRL)")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data no formato YYYY-MM-DD")
    category_suggestion: str = Field(..., description="Categoria sugerida")
    is_essential: bool = Field(..., description="Se a despesa é essencial ou não")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da extração (0.0-1.0)")


class MultipleExpensesExtraction(BaseModel):
    """Modelo para múltiplas despesas extraídas do mesmo texto."""

    expenses: list[ExpenseExtraction] = Field(
        ..., min_length=1, description="Lista de despesas extraídas"
    )


class ExtractionError(BaseModel):
    """Modelo para erro quando não há despesa detectada."""

    error: Literal["NOT_DETECTED"] = Field(..., description="Código de erro")


class ExtractionResponse(BaseModel):
    """Resposta da extração - pode ser despesa única, múltiplas ou erro."""

    # Campos opcionais para despesa única
    description: str | None = None
    amount: float | None = Field(None, ge=0)
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    category_suggestion: str | None = None
    is_essential: bool | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)

    # Campo para múltiplas despesas
    expenses: list[ExpenseExtraction] | None = None

    # Campo para erro
    error: Literal["NOT_DETECTED"] | None = None

    def is_error(self) -> bool:
        """Verifica se a resposta indica erro (não detectou despesa)."""
        return self.error == "NOT_DETECTED"

    def is_multiple(self) -> bool:
        """Verifica se há múltiplas despesas."""
        return self.expenses is not None and len(self.expenses) > 0

    def get_single_expense(self) -> ExpenseExtraction | None:
        """Retorna a despesa única se existir, None caso contrário."""
        if self.is_error() or self.is_multiple():
            return None
        if (
            self.description
            and self.amount is not None
            and self.date
            and self.category_suggestion
            and self.is_essential is not None
            and self.confidence is not None
        ):
            return ExpenseExtraction(
                description=self.description,
                amount=self.amount,
                date=self.date,
                category_suggestion=self.category_suggestion,
                is_essential=self.is_essential,
                confidence=self.confidence,
            )
        return None
