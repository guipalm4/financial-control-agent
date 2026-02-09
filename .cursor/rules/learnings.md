---
description: Lições aprendidas, métricas e erros a evitar
alwaysApply: true
---

# Learnings — Finance Bot Telegram

## Métricas de Qualidade (Meta: 95%+ precisão)

### Métricas Gerais

| Métrica | Valor | Meta |
|---------|-------|------|
| Total de Clarification Questions | 0 | - |
| Precisão média | -% | 95%+ |
| Tasks sem retrabalho | -% | 90%+ |

### Por FEAT

| FEAT | Questions | Retrabalhos | Precisão | Data |
|------|-----------|-------------|----------|------|
| FEAT-001 | - | - | -% | - |
| FEAT-002 | - | - | -% | - |
| FEAT-003 | - | - | -% | - |

### Template para registrar métricas por FEAT

```markdown
## Métricas FEAT-xxx (YYYY-MM-DD)

| Métrica | Valor |
|---------|-------|
| Clarification Questions feitas | X |
| Decisões que precisaram retrabalho | Y |
| Precisão | (X-Y)/X * 100% |
| Causa dos retrabalhos | [lista] |
```

---

## Erros Conhecidos

| Data | Erro | Solução | Contexto | FEAT/API |
|------|------|---------|----------|----------|
| - | - | - | - | - |

---

## Padrões que Funcionam

### Padrão: Handler Telegram Assíncrono

**Quando usar:** Qualquer handler do bot Telegram

**Como:**

```python
from telegram import Update
from telegram.ext import ContextTypes

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sempre usar async/await
    await update.message.reply_text("Resposta")
```

**Funciona bem para:** Todos os handlers do bot

### Padrão: Sessão SQLModel com Context Manager

**Quando usar:** Qualquer operação no banco

**Como:**

```python
from sqlmodel import Session
from src.db.engine import engine

with Session(engine) as session:
    # Operações
    session.add(entity)
    session.commit()
    session.refresh(entity)
```

**Funciona bem para:** CRUD operations

---

## Libs Consultadas (Cache)

| Lib | Versão | Doc URL | Última Consulta | Notas |
|-----|--------|---------|-----------------|-------|
| FastAPI | 0.128.x | fastapi.tiangolo.com | 2026-02-03 | Async, Pydantic v2 |
| SQLModel | 0.0.24 | sqlmodel.tiangolo.com | 2026-02-03 | SQLAlchemy + Pydantic |
| python-telegram-bot | 22.5 | python-telegram-bot.org | 2026-02-03 | Async handlers |
| Groq Python | latest | console.groq.com | 2026-02-03 | Whisper API |

**Regra:** Consultar Context7 ANTES de usar lib. Registrar aqui APÓS consulta.

---

## Decisões de Design

| Data | Decisão | Justificativa | ADR |
|------|---------|---------------|-----|
| 2026-02-03 | Usar FastAPI | Performance, async, validação automática | ADR-001 |
| 2026-02-03 | Usar SQLModel | Combina SQLAlchemy + Pydantic | ADR-002 |
| 2026-02-03 | Usar python-telegram-bot | Biblioteca oficial, bem documentada | ADR-003 |
| 2026-02-03 | Separar Expense/Entry | Flexibilidade para parcelas e faturas | ADR-004 |

---

## Comandos Úteis

| Comando | Quando usar | Resultado |
|---------|-------------|-----------|
| `git branch --show-current` | Verificar branch atual | Nome da branch |
| `ruff check . && ruff format .` | Validar código | Lint + format |
| `mypy .` | Verificar tipos | Type check |
| `pytest tests/ -v` | Rodar testes | Resultados |
| `docker compose up -d` | Subir ambiente | Bot + DB rodando |
| `docker compose logs -f bot` | Ver logs do bot | Output em tempo real |

---

## Notas de Debug

| Data | Problema | Solução | Ferramenta |
|------|----------|---------|------------|
| - | - | - | - |

---

## Relatório de Qualidade (preencher ao final do projeto)

### Lições Aprendidas

- [A preencher durante o desenvolvimento]

### Recomendações para próximo projeto

- [A preencher ao final]
