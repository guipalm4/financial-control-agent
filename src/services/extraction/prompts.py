"""Prompts para extração de entidades de despesa via Gemini Flash."""

from __future__ import annotations

from datetime import date, timedelta


def build_extraction_prompt(transcription: str, today: date) -> str:
    """Constrói o prompt de extração baseado no texto transcrito e data atual.

    Parameters
    ----------
    transcription:
        Texto transcrito do áudio.
    today:
        Data atual para referência de datas relativas.

    Returns
    -------
    str
        Prompt formatado para o Gemini.
    """
    yesterday = today - timedelta(days=1)

    intro = (
        "Você é um extrator de despesas financeiras. Sua tarefa: analisar o texto e "
        "retornar EXCLUSIVAMENTE um único JSON válido, sem markdown, sem explicações."
    )
    multi_rule = (
        'Para múltiplas despesas: preencha "expenses" com array de objetos no mesmo '
        "formato. Deixe description/amount/date/category_suggestion vazios ou null."
    )
    essential_rule = (
        "is_essential: Alimentação básica/transporte trabalho/moradia = true. "
        "Restaurante/delivery/lazer/assinaturas = false"
    )

    prompt = f"""{intro}

TEXTO DO USUÁRIO: "{transcription}"
DATA DE REFERÊNCIA: {today.strftime("%Y-%m-%d")}

OBRIGATÓRIO - Formato de saída (um dos dois):

1) Despesa identificada (única ou múltiplas):
{{
  "description": "descrição curta e objetiva",
  "amount": 0.00,
  "date": "YYYY-MM-DD",
  "category_suggestion": "categoria",
  "is_essential": true ou false,
  "confidence": 0.0 a 1.0,
  "expenses": []
}}
{multi_rule}

2) Nenhuma despesa identificada (saudações, perguntas, piadas, áudio irrelevante):
{{"error": "NOT_DETECTED"}}

REGRAS FIXAS - Siga SEMPRE:
- "ontem" = {yesterday.strftime("%Y-%m-%d")}
- "hoje" = {today.strftime("%Y-%m-%d")}
- Valores SEMPRE em R$ (BRL), número decimal
- Datas futuras: INVÁLIDAS. Use a data de referência.
- Se o texto NÃO menciona gasto/compras/despesa/pagamento: retorne {{"error": "NOT_DETECTED"}}
- description: máximo 3-5 palavras, sem valor (ex: "Uber", "Supermercado", "Almoço")
- confidence: 0.0 = incerto, 1.0 = certeza total
- {essential_rule}"""
    return prompt.strip()
