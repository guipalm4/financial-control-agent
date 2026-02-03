# ADR — Finance Bot Telegram

> **Resumo:** Registro das decisões arquiteturais do projeto com contexto, alternativas e consequências.

---

## ADR-001: Banco de Dados — PostgreSQL

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Arquiteto + Desenvolvedor

### Contexto
O projeto precisa de um banco de dados para armazenar usuários, cartões, despesas e lançamentos. O perfil é PESSOAL com possível evolução para multi-user no futuro.

### Decisão
Usar **PostgreSQL 16+** como banco de dados principal.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **PostgreSQL** ✅ | JSONB, robusto, evolução fácil | Mais pesado que SQLite |
| SQLite | Zero config, leve | Sem suporte a JSONB, difícil escalar |
| MongoDB | Flexível, schemaless | Eventual consistency, overhead operacional |

### Consequências

**Ganhos:**
- Suporte a JSONB para dados semi-estruturados (extracted_data)
- Índices parciais para soft delete
- Caminho claro para escalar se necessário
- Ecossistema maduro de ferramentas

**Perdas:**
- Requer container Docker adicional
- Mais complexo que SQLite para MVP

**Riscos:**
- Overhead para projeto single-user (mitigado por ser local)

---

## ADR-002: Task Queue — FastAPI Background Tasks

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Arquiteto + Desenvolvedor

### Contexto
O processamento de áudio (transcrição + categorização) leva ~3s e não deve bloquear o bot. Precisa de processamento assíncrono.

### Decisão
Usar **FastAPI BackgroundTasks** nativo ao invés de Celery + Redis.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **FastAPI BackgroundTasks** ✅ | Simples, nativo, sem deps extras | Não escala horizontalmente |
| Celery + Redis | Robusto, escalável | 2 containers extras, complexo |
| ARQ + Redis | Async-native, leve | Requer Redis |

### Consequências

**Ganhos:**
- Menos containers (apenas API + DB)
- Configuração simples
- Suficiente para single-user

**Perdas:**
- Não escala horizontalmente
- Sem retry automático sofisticado

**Riscos:**
- Se migrar para multi-user, precisará reescrever para Celery (aceitável)

---

## ADR-003: ORM — SQLModel

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Arquiteto + Desenvolvedor

### Contexto
Precisamos de um ORM para interagir com PostgreSQL. A aplicação usa FastAPI com Pydantic para validação.

### Decisão
Usar **SQLModel 0.0.14+** que integra Pydantic + SQLAlchemy.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **SQLModel** ✅ | Pydantic integrado, menos boilerplate | Menos maduro |
| SQLAlchemy puro | Maduro, completo | Boilerplate, Pydantic separado |
| Tortoise ORM | Async-first | Menos documentação |

### Consequências

**Ganhos:**
- Modelos servem como schemas Pydantic automaticamente
- Menos código duplicado
- Validações integradas

**Perdas:**
- SQLModel ainda em evolução (v0.x)
- Algumas features avançadas do SQLAlchemy menos acessíveis

**Riscos:**
- Breaking changes em versões futuras (mitigado por pinning de versão)

---

## ADR-004: Estrutura de Projeto — Monolito Modular

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Arquiteto + Desenvolvedor

### Contexto
Precisamos organizar o código de forma que seja fácil de manter e testar, mas sem over-engineering para um MVP.

### Decisão
Usar **Monolito Modular** com separação por features.

### Estrutura
```
src/features/
├── auth/          # FEAT-001
├── expenses/      # FEAT-003 a FEAT-009
├── reports/       # FEAT-012, FEAT-013
└── learning/      # FEAT-004
```

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Monolito Modular** ✅ | Separação clara, testável | Pode crescer demais |
| Flat Structure | Simples para MVP | Difícil escalar |
| DDD Lite | Bem organizado | Over-engineering para MVP |

### Consequências

**Ganhos:**
- Cada feature é isolada e testável
- Fácil de entender a responsabilidade de cada módulo
- Caminho claro para extrair microserviços se necessário

**Perdas:**
- Mais diretórios que flat structure

**Riscos:**
- Nenhum significativo

---

## ADR-005: Fallback de Transcrição — Apenas em Erro

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Usuário + Desenvolvedor

### Contexto
O sistema usa Groq Whisper Large para transcrição. Existe a opção de fallback para OpenAI Whisper se a confiança for baixa ou se houver erro.

### Decisão
Usar fallback para OpenAI Whisper **apenas em caso de erro ou timeout** do Groq, não por confiança baixa.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Fallback em erro** ✅ | Mais barato, Groq suficiente | Sem segunda chance em baixa confiança |
| Fallback se confiança < 0.7 | Mais preciso | Custo dobrado em alguns casos |
| Sem fallback | Mais simples | Menos resiliente |

### Consequências

**Ganhos:**
- Custo previsível
- Groq Whisper Large é suficiente para PT-BR

**Perdas:**
- Não há "segunda opinião" em transcrições duvidosas

**Riscos:**
- Se Groq degradar qualidade, não há proteção (mitigado por confirmação manual)

---

## ADR-006: Retenção de Áudios — 7 Dias

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Usuário + Desenvolvedor

### Contexto
Áudios são enviados para transcrição. Precisamos decidir se mantemos os arquivos originais e por quanto tempo.

### Decisão
Manter áudios por **7 dias** após transcrição para debug, depois deletar automaticamente.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Manter 7 dias** ✅ | Permite debug | Uso de disco |
| Deletar imediato | Privacidade máxima | Sem debug possível |
| Manter sempre | Histórico completo | Disco infinito |

### Consequências

**Ganhos:**
- Permite investigar erros de transcrição
- Não acumula dados infinitamente

**Perdas:**
- Uso de disco por 7 dias

**Riscos:**
- Nenhum significativo (dados locais)

---

## ADR-007: Sessão de Autenticação — 24h Inatividade

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Arquiteto + Desenvolvedor

### Contexto
O bot requer PIN para autenticação. Precisamos definir quando solicitar PIN novamente.

### Decisão
Sessão expira após **24 horas de inatividade**. Cada interação renova o timer.

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **24h inatividade** ✅ | UX balanceada | Sessão longa se ativo |
| 1h fixo | Mais seguro | UX ruim, pede PIN frequente |
| Nunca expira | UX máxima | Inseguro |

### Consequências

**Ganhos:**
- Usuário não precisa digitar PIN a cada uso
- Segurança razoável para perfil PESSOAL

**Perdas:**
- Se dispositivo for comprometido, sessão ativa por até 24h

**Riscos:**
- Aceitável para perfil PESSOAL

---

## ADR-008: Modelo de Dados — Despesa vs Lançamento

**Status:** Aceito  
**Data:** 2026-02-01  
**Decisores:** Arquiteto + Desenvolvedor

### Contexto
Despesas podem ser à vista (1 pagamento) ou parceladas (N pagamentos). Precisamos modelar isso corretamente.

### Decisão
Separar em duas tabelas: **`expenses`** (registro único) e **`entries`** (parcelas/lançamentos).

### Modelo
```
expenses (1) ──────< entries (N)
   │                    │
   └─ valor_total       └─ valor_parcela
   └─ num_parcelas      └─ data_vencimento
                        └─ status (pending/paid)
```

### Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Despesa + Lançamentos** ✅ | Modelo correto, flexível | Mais tabelas |
| Apenas Despesas | Simples | Não suporta parcelas bem |
| Array de parcelas em JSON | Menos tabelas | Difícil consultar |

### Consequências

**Ganhos:**
- Modelo correto para parcelamento
- Fácil consultar "quanto devo em março"
- Suporta faturas por cartão

**Perdas:**
- Mais complexidade de código

**Riscos:**
- Nenhum significativo

---

## Matriz de ADRs por Feature

| ADR | Features Impactadas | Status |
|-----|---------------------|--------|
| ADR-001 | Todas | Aceito |
| ADR-002 | FEAT-003 | Aceito |
| ADR-003 | Todas | Aceito |
| ADR-004 | Todas | Aceito |
| ADR-005 | FEAT-003 | Aceito |
| ADR-006 | FEAT-003 | Aceito |
| ADR-007 | FEAT-001 | Aceito |
| ADR-008 | FEAT-008, FEAT-009 | Aceito |
