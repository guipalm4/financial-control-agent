---
description: Contexto do projeto Finance Bot Telegram
alwaysApply: true
---

# Project Context — Finance Bot Telegram

## Resumo
Bot Telegram para registro de despesas pessoais via áudio com transcrição e categorização automática por IA.

## Classificação
- **Perfil:** PESSOAL
- **Usuários:** Single-user (uso próprio)
- **Exposição:** Local (Docker Compose)
- **PII:** Dados financeiros básicos (valores, cartões, categorias)

## Stack
| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Runtime | Python | 3.11+ |
| Framework | FastAPI | 0.109+ |
| Bot | python-telegram-bot | 21+ |
| Database | PostgreSQL | 16+ |
| ORM | SQLModel | 0.0.14+ |
| Migrations | Alembic | 1.13+ |
| Transcrição | Groq Whisper Large | API |
| LLM | Gemini Flash 2.0 | API |

## Estrutura de Diretórios
```
src/
├── main.py                    # FastAPI app entry
├── config.py                  # Settings (pydantic-settings)
├── database.py                # SQLModel engine/session
├── features/
│   ├── auth/                  # Autenticação (PIN, sessões)
│   ├── expenses/              # Despesas e lançamentos
│   ├── reports/               # Relatórios e resumos
│   └── learning/              # Aprendizado de categorização
├── integrations/
│   ├── telegram/              # Bot handlers
│   ├── groq.py                # Whisper client
│   └── gemini.py              # Gemini client
└── shared/                    # Utilitários compartilhados
```

## Decisões Arquiteturais (ADRs)
- **ADR-001:** PostgreSQL (não SQLite) para evolução futura
- **ADR-002:** FastAPI Background Tasks (não Celery) por simplicidade
- **ADR-003:** SQLModel para integração Pydantic + SQLAlchemy
- **ADR-004:** Monolito Modular para separação de concerns

## IDs Rastreáveis
| Prefixo | Significado |
|---------|-------------|
| FEAT-xxx | Feature/User Story |
| RULE-xxx | Regra de negócio |
| API-xxx | Comando/Handler |
| TEST-xxx | Cenário de teste |
| ADR-xxx | Decisão arquitetural |

## Documentação Relacionada
- `PRD_v2.md` — Requisitos e user stories
- `TECH_SPECS.md` — Especificação técnica
- `ADR.md` — Decisões arquiteturais
- `SECURITY_IMPLEMENTATION.md` — Segurança
