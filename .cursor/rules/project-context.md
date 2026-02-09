---
description: Contexto do projeto Finance Bot Telegram
alwaysApply: true
---

# Project Context — Finance Bot Telegram

## Resumo

Bot Telegram para registro de despesas pessoais via áudio com transcrição automática (Groq Whisper) e categorização inteligente por IA (Gemini Flash). Objetivo: reduzir tempo de registro de 2 minutos para 10 segundos.

## Perfil

- **Tipo:** PESSOAL (single-user, local)
- **Meta de qualidade:** 95%+ de precisão em decisões
- **Exposição:** Local (Docker Compose + ngrok)

## Stack (VERSÕES FIXADAS - OBRIGATÓRIO SEGUIR)

**ATENÇÃO:** As versões abaixo são OBRIGATÓRIAS. Antes de usar qualquer lib:
1. Verificar se está listada aqui
2. Se não estiver, consultar Context7 para versão compatível
3. Registrar em learnings.md antes de usar

| Componente | Tecnologia | Versão EXATA | Validação Context7 |
|------------|------------|--------------|-------------------|
| Runtime | Python | 3.13.x | ✅ Atualizado (LTS até 2029) |
| Framework | FastAPI | 0.128.x | ✅ Consultado |
| ORM | SQLModel | 0.0.24 | ✅ Consultado |
| Banco | PostgreSQL | 16.x | ✅ Consultado |
| Telegram | python-telegram-bot | 22.5 | ✅ Consultado |
| Transcrição | Groq Python | latest | ✅ Consultado |
| LLM | Google Generative AI | latest | - |
| Validação | Pydantic | 2.7.x | (via FastAPI) |
| Server | Uvicorn | 0.30.x | (via FastAPI) |
| Migrations | Alembic | 1.13.x | - |

**Anti-pattern:** NÃO usar versões diferentes sem atualizar esta tabela e registrar em ADR.

### Verificação de compatibilidade

Antes de adicionar uma dependência (`uv add` ou `pip install`):
1. Verificar se lib existe na tabela acima
2. Se não existir, usar Context7 para verificar compatibilidade
3. Adicionar à tabela após validação
4. Usar `uv add <pacote>` para adicionar ao projeto (atualiza `pyproject.toml` e `uv.lock`)

## Estrutura de diretórios

```
finance-bot/
├── .cursor/
│   └── rules/           # Regras do Cursor
├── src/
│   ├── api/             # Endpoints FastAPI (health, webhooks)
│   ├── bot/             # Handlers do Telegram
│   │   ├── handlers/    # Handlers por feature
│   │   └── keyboards/   # Inline keyboards
│   ├── services/        # Lógica de negócio
│   │   ├── transcription/  # Groq Whisper
│   │   ├── extraction/     # Gemini Flash
│   │   └── learning/       # Aprendizado de padrões
│   ├── models/          # SQLModel entities
│   ├── db/              # Configuração do banco
│   │   └── migrations/  # Alembic migrations
│   └── core/            # Config, settings, utils
├── tests/               # Testes
│   ├── unit/
│   └── integration/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

## Workflow de Implementação (OBRIGATÓRIO)

### Progress Tracker (FONTE DE VERDADE)

**SEMPRE** consultar `docs/PROGRESS.md` antes de iniciar qualquer task:
1. Verificar dependências (não iniciar se dependência não está ✅ DONE)
2. Usar branch name conforme definido no tracker
3. Atualizar status: ⏳ → 🔄 → ✅

### Git (NUNCA codar em main)

1. Verificar PROGRESS.md para branch name correto
2. Criar branch: `git checkout -b <branch-do-progress>`
3. Commits convencionais: `feat:`, `fix:`, `chore:`
4. Push e PR após DOD completo
5. Atualizar PROGRESS.md para ✅ DONE

### Antes de implementar QUALQUER task:

1. **PROGRESS.md obrigatório:**
   - Localizar task no Sprint correto
   - Verificar dependências
   - Atualizar para 🔄 IN_PROGRESS

2. **PLAN mode obrigatório:**
   - Usar Cursor Plan mode
   - Listar arquivos que serão criados/modificados
   - Identificar dependências
   - Estimar complexidade

3. **Clarification Questions se:**
   - Contrato de API ambíguo
   - Múltiplas formas de implementar
   - Lib/versão não especificada
   - Comportamento de erro não definido

4. **Consultar Context7 ANTES de codar:**
   - Para cada lib usada
   - Validar sintaxe atual
   - Registrar em learnings.md

### Anti-patterns (PROIBIDO)

- ❌ Pular direto para implementação sem Plan
- ❌ Codar na branch main/master/develop
- ❌ Assumir versão de lib sem consultar Context7
- ❌ Marcar task como DONE sem executar DOD
- ❌ Ignorar testes definidos no PRD
- ❌ Iniciar task sem verificar PROGRESS.md
- ❌ Iniciar task com dependência não concluída

## Integrações Externas

| Serviço | Uso | Timeout | Retries |
|---------|-----|---------|---------|
| Telegram Bot API | Webhook/Polling | 30s | 3 |
| Groq Whisper | Transcrição de áudio | 60s | 2 |
| Gemini Flash | Extração e categorização | 30s | 2 |

## Referências

- **PROGRESS.md** — Progress Tracker (fonte de verdade para tasks) — **CONSULTAR PRIMEIRO**
- PRD.md — Requisitos e user stories
- TECH_SPECS.md — Especificação técnica
- SECURITY_IMPLEMENTATION.md — Segurança
- ADR.md — Decisões arquiteturais
