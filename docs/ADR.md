# ADR — Finance Bot Telegram

> **Resumo executivo:** Registro das decisões arquiteturais do Finance Bot, incluindo escolha de stack, modelo de dados e estratégias de integração com APIs externas.

---

## ADR-001: Stack Backend Python + FastAPI

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

O projeto precisa de um backend para:
- Servir webhooks do Telegram
- Integrar com APIs de IA (Groq, Gemini)
- Gerenciar dados no PostgreSQL
- Processar áudio de forma assíncrona

### Decisão

Usar **Python 3.13+ com FastAPI 0.128.x** como framework web.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **FastAPI** | Async nativo, validação Pydantic, docs automáticas, ecossistema IA | Curva de aprendizado para async |
| Flask | Simples, maduro | Sync por padrão, sem validação nativa |
| Node.js + Fastify | Muito rápido, bom para I/O | Menos bibliotecas de IA, tipagem opcional |

### Consequências

**Ganhos:**
- Suporte nativo a async/await para I/O (Telegram, Groq, Gemini)
- Validação automática com Pydantic
- Documentação OpenAPI automática
- Excelente integração com bibliotecas de IA Python

**Perdas:**
- Nenhuma significativa para este caso de uso

**Riscos:**
- Complexidade de async pode gerar bugs difíceis de debugar

---

## ADR-002: ORM SQLModel (SQLAlchemy + Pydantic)

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

Precisamos de um ORM para:
- Definir modelos de dados
- Validar dados de entrada/saída
- Integrar com FastAPI de forma natural

### Decisão

Usar **SQLModel 0.0.24** como ORM, que combina SQLAlchemy com Pydantic.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **SQLModel** | Combina ORM + validação, mesma sintaxe do FastAPI | Relativamente novo (0.0.x) |
| SQLAlchemy puro | Maduro, completo | Duplicação: modelos ORM + Pydantic separados |
| Prisma (Python) | Tipagem forte, migrations | Menos maduro em Python |

### Consequências

**Ganhos:**
- Um único modelo para banco e validação
- Integração perfeita com FastAPI
- Menos código duplicado

**Perdas:**
- Documentação menos extensa que SQLAlchemy puro

**Riscos:**
- Versão 0.0.x pode ter breaking changes (mitigado: fixar versão)

---

## ADR-003: Biblioteca python-telegram-bot

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

Precisamos interagir com a API do Telegram para:
- Receber mensagens e áudios
- Enviar respostas com botões inline
- Gerenciar estado de conversação

### Decisão

Usar **python-telegram-bot v22.5** como biblioteca oficial do Telegram.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **python-telegram-bot** | Oficial, bem documentada, async nativo | API verbosa |
| aiogram | Moderno, async first | Menos documentação |
| Telegraf (Node.js) | Muito popular | Mudaria stack para Node.js |

### Consequências

**Ganhos:**
- Biblioteca oficial, mantida ativamente
- Excelente documentação e exemplos
- Suporte completo a todas as features do Telegram

**Perdas:**
- API pode ser verbosa para casos simples

**Riscos:**
- Nenhum significativo (biblioteca estável)

---

## ADR-004: Modelo de Dados Expense/Entry (Despesa/Lançamento)

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

Despesas podem ser:
- À vista (1 lançamento)
- Parceladas (N lançamentos em faturas diferentes)
- No débito (1 lançamento, data = compra)
- No crédito (1+ lançamentos, data = vencimento fatura)

### Decisão

Separar em duas entidades:
- **Expense:** Registro da despesa original (valor total, descrição, categoria)
- **Entry:** Lançamentos individuais (parcela, valor, data de vencimento, status)

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Expense + Entry** | Flexível, rastreia parcelas, calcula faturas | Mais complexo |
| Apenas Expense | Simples | Não suporta parcelamento corretamente |
| Expense com array de parcelas | Menos tabelas | Mais difícil consultar faturas |

### Consequências

**Ganhos:**
- Consultas de fatura por mês são simples (WHERE due_date BETWEEN...)
- Histórico de parcelas preservado
- Status por parcela (pending, paid, cancelled)

**Perdas:**
- Mais JOINs em algumas consultas

**Riscos:**
- Nenhum significativo

---

## ADR-005: Transcrição com Groq Whisper + Fallback

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

Áudios precisam ser transcritos para texto antes da extração de entidades. Groq oferece Whisper com latência muito baixa.

### Decisão

Usar **Groq Whisper** como serviço primário de transcrição, sem fallback no MVP (simplicidade).

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Groq Whisper** | Muito rápido (~1s), barato | Menos conhecido |
| OpenAI Whisper | Original, mais recursos | Mais caro, mais lento |
| Whisper local | Sem custo de API | Requer GPU, mais complexo |

### Consequências

**Ganhos:**
- Transcrição em ~1 segundo
- Custo baixo
- API simples

**Perdas:**
- Dependência de serviço externo

**Riscos:**
- Indisponibilidade do Groq (mitigado: retry + mensagem de erro amigável)

---

## ADR-006: Categorização com Gemini Flash + Aprendizado Local

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

Despesas precisam ser categorizadas. O sistema deve aprender padrões do usuário.

### Decisão

Estratégia híbrida:
1. **Primeiro:** Buscar no histórico local (se descrição normalizada já foi categorizada 3+ vezes)
2. **Se não encontrar:** Usar Gemini Flash para categorização por IA

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Híbrido (local + LLM)** | Aprende, reduz custos, rápido para padrões | Mais complexo |
| Só LLM | Simples | Custo maior, não aprende |
| Só regras locais | Zero custo | Não generaliza |

### Consequências

**Ganhos:**
- Redução de chamadas à API ao longo do tempo
- Categorização personalizada
- Fallback para LLM em casos novos

**Perdas:**
- Complexidade de implementação do cache de aprendizado

**Riscos:**
- Aprendizado incorreto se usuário errar categorização (mitigado: mínimo 3 confirmações)

---

## ADR-007: Armazenamento de Áudio Temporário

**Status:** Aceito  
**Data:** 2026-02-03  
**Decisores:** Desenvolvedor

### Contexto

Áudios são recebidos do Telegram, processados e não são mais necessários após a transcrição.

### Decisão

- Armazenar áudio localmente apenas durante processamento
- Deletar após transcrição bem-sucedida
- Cleanup job para áudios não processados após 7 dias (RULE-009)

### Consequências

**Ganhos:**
- Economia de espaço
- Privacidade (dados não persistem)
- Simplicidade

**Perdas:**
- Não é possível re-transcrever (precisa novo áudio)

**Riscos:**
- Perda de contexto em caso de erro (mitigado: log de erro com detalhes)

---

## ADR-008: Gerenciador de Pacotes uv

**Status:** Aceito  
**Data:** 2026-02-09  
**Decisores:** Desenvolvedor

### Contexto

O projeto inicialmente usava `pip` e `requirements.txt` para gerenciar dependências Python. Com o crescimento do projeto e necessidade de builds reproduzíveis, surge a necessidade de um gerenciador de pacotes mais moderno e eficiente.

### Decisão

Migrar para **uv** como gerenciador de pacotes Python, usando `pyproject.toml` como fonte única de verdade para dependências e `uv.lock` para builds reproduzíveis.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **uv** | Extremamente rápido, drop-in replacement para pip, suporta pyproject.toml, lockfile nativo | Relativamente novo (mas estável) |
| Poetry | Maduro, ecossistema grande | Mais lento que uv, overhead maior |
| pip-tools | Compatível com pip | Requer workflow adicional, não integrado |
| pip + requirements.txt | Simples, familiar | Lento, sem lockfile nativo, duplicação com pyproject.toml |

### Consequências

**Ganhos:**
- Instalação de dependências 10-100x mais rápida que pip
- Builds reproduzíveis com `uv.lock`
- Fonte única de verdade: `pyproject.toml` (sem duplicação com requirements.txt)
- Compatível com PEP 621 (pyproject.toml)
- Drop-in replacement: `uv pip install` funciona como `pip install`
- Melhor integração com Docker (menor tempo de build)

**Perdas:**
- Requer instalação do uv (mas é simples: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Equipe precisa aprender comandos do uv (mas são intuitivos)

**Riscos:**
- Ferramenta relativamente nova (mitigado: mantida pela Astral, mesma equipe do ruff, amplamente adotada)
- Migração inicial requer atualização de documentação (mitigado: documentação atualizada)

### Implementação

- Dependências migradas de `requirements.txt` para `pyproject.toml`
- `uv.lock` gerado e commitado no repositório
- Dockerfile atualizado para usar uv
- Makefile atualizado com comandos `uv sync` e `uv run`
- Documentação atualizada (README, TESTING.md, project-context.md)
