# ADR — Telegram Finance Bot

> Architectural Decision Records — Decisões arquiteturais do projeto.

---

## ADR-001: Usar APIs de IA na Nuvem (Groq + Gemini)

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

Precisamos de:
1. Transcrição de áudio (Speech-to-Text)
2. Extração de dados estruturados de texto natural (LLM)

### Decisão

Usar **APIs de IA na nuvem** com providers especializados:
- **Groq Whisper Large v3 Turbo** para transcrição (STT)
- **Gemini 2.0 Flash** para extração de dados (LLM)

### Alternativas Consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Groq Whisper + Gemini Flash** ✅ | Latência muito baixa, tiers free generosos, modelos especializados | Duas API keys, requer internet |
| Groq para ambos (Whisper + Llama) | Uma única API key | Llama inferior ao Gemini para extração estruturada |
| Whisper local | Offline, privacidade total | Requer GPU, mais lento |
| OpenAI API | Alta qualidade | Mais caro, latência maior |
| Ollama/Llama local | Offline, gratuito | Requer RAM/GPU, qualidade inferior |

### Consequências

**Ganhos:**
- Latência muito baixa (~1-2s para áudio + extração)
- Tiers free generosos (Groq: ~14K req/dia, Gemini: 15 RPM / 1M tokens/dia)
- Sem necessidade de hardware especializado
- Gemini Flash excelente para extração de JSON estruturado

**Perdas:**
- Requer conexão com internet
- Duas API keys para gerenciar
- Dados passam por servidores externos (aceitável para uso pessoal)

**Riscos:**
- Providers podem mudar política de preços (mitigação: monitorar uso)

---

## ADR-002: SQLite como Banco de Dados

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

Precisamos persistir dados financeiros (gastos, cartões, faturas).

### Decisão

Usar **SQLite** com **SQLAlchemy 2.x**.

### Alternativas Consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **SQLite** ✅ | Zero config, arquivo único, backup fácil, ACID | Não escala horizontalmente |
| PostgreSQL | Robusto, escala | Overkill para 1 usuário, requer setup |
| JSON files | Simples | Sem queries, sem ACID |

### Consequências

**Ganhos:**
- Zero configuração
- Backup = copiar um arquivo
- Suficiente para milhares de registros
- Portável (levar banco para outro PC)

**Perdas:**
- Não escala para múltiplos usuários (não aplicável)

---

## ADR-003: Confirmação Obrigatória Antes de Salvar

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

LLM pode extrair dados incorretos do áudio transcrito.

### Decisão

Sempre mostrar **preview** e pedir **confirmação** antes de salvar.

```
[Áudio] → [Transcrição] → [Extração] → [PREVIEW] → [Confirmação] → [Salva]
                                         ↑
                                    Usuário valida
```

### Alternativas Consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Confirmação obrigatória** ✅ | Evita erros, transparência | Um clique extra |
| Salvar direto | Mais rápido | Registros incorretos |
| Confirmação opcional | Flexível | Inconsistência |

### Consequências

**Ganhos:**
- Usuário sempre valida antes de salvar
- Permite correção imediata
- Maior confiança nos dados

**Perdas:**
- Um passo extra no fluxo

---

## ADR-004: Classificação de Itens (ESSENCIAL vs NÃO ESSENCIAL)

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

Usuário quer diferenciar gastos essenciais de não essenciais, inclusive dentro da mesma categoria (ex: carne vs cerveja, ambos no mercado).

### Decisão

- Categoria tem um **tipo padrão** (ESSENCIAL ou NÃO ESSENCIAL)
- **Item específico** pode **sobrescrever** o tipo da categoria
- LLM infere o tipo baseado no item mencionado

### Lógica

```
Mercado (categoria) → default ESSENCIAL
  ├── carne → ESSENCIAL (mantém)
  ├── arroz → ESSENCIAL (mantém)
  ├── cerveja → NÃO ESSENCIAL (sobrescreve)
  └── refrigerante → NÃO ESSENCIAL (sobrescreve)
```

### Alternativas Consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Item sobrescreve categoria** ✅ | Granular, preciso | LLM precisa inferir |
| Apenas categoria | Simples | Impreciso (cerveja = essencial?) |
| Subcategorias fixas | Estruturado | Muitas categorias |

### Consequências

**Ganhos:**
- Classificação precisa por item
- Resumo financeiro mais útil (% essencial vs não essencial)

**Perdas:**
- Depende da qualidade da extração do LLM

---

## ADR-005: Múltiplos Itens na Mesma Transcrição

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

Usuário pode dizer: "comprei 20 reais de cerveja e 15 de carne no mercado".

### Decisão

LLM retorna **array de itens** quando detecta múltiplos valores. Cada item vira um registro separado no banco.

### Estrutura

```json
// Input: "20 de cerveja e 15 de carne"
// Output:
{
  "items": [
    {"amount": 20, "item": "cerveja", "category_type": "NAO_ESSENCIAL"},
    {"amount": 15, "item": "carne", "category_type": "ESSENCIAL"}
  ]
}
```

### Consequências

**Ganhos:**
- Rastreabilidade por item
- Classificação correta por item
- Resumos mais precisos

**Perdas:**
- Lógica de preview mais complexa (múltiplos itens)

---

## ADR-006: Detecção de Datas Relativas

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

Usuário pode dizer: "gastei 50 reais ontem" ou "comprei na segunda-feira".

### Decisão

LLM recebe a **data atual** no prompt e converte expressões relativas para datas absolutas.

### Mapeamento

| Expressão | Cálculo |
|-----------|---------|
| "hoje" | data atual |
| "ontem" | data atual - 1 |
| "anteontem" | data atual - 2 |
| "segunda/terça/..." | último dia da semana |
| (sem data) | data atual |

### Prompt

```
Data de hoje: 2026-01-29
Dia da semana: quarta-feira

Regras de data:
- "ontem" = 2026-01-28
- "anteontem" = 2026-01-27
- "segunda" = 2026-01-27 (última segunda)
```

### Consequências

**Ganhos:**
- Registro na data correta do gasto (não da transcrição)
- Fatura calculada corretamente

**Perdas:**
- Depende da interpretação do LLM

---

## ADR-007: Lógica de Parcelas por Fechamento

**Status:** ✅ Aceito  
**Data:** 2026-01-29  
**Decisores:** Owner

### Contexto

Compras parceladas no cartão precisam ser distribuídas nas faturas corretas.

### Decisão

- **Parcela 1** entra na fatura atual (se compra ≤ fechamento) ou próxima (se compra > fechamento)
- **Parcelas 2, 3, 4...** entram nos meses seguintes à parcela 1

### Exemplo

```
Cartão: fecha dia 20, vence dia 28
Compra: R$300 em 3x no dia 25/01 (> fechamento)

Parcela 1 → FEV/2026 (R$100)
Parcela 2 → MAR/2026 (R$100)
Parcela 3 → ABR/2026 (R$100)
```

### Consequências

**Ganhos:**
- Faturas refletem a realidade dos cartões
- Alertas de vencimento precisos

---

## Índice de ADRs

| ID | Decisão | Status |
|----|---------|--------|
| ADR-001 | APIs de IA na nuvem (Groq + Gemini) | ✅ Aceito |
| ADR-002 | SQLite como banco | ✅ Aceito |
| ADR-003 | Confirmação obrigatória | ✅ Aceito |
| ADR-004 | Item sobrescreve categoria | ✅ Aceito |
| ADR-005 | Múltiplos itens por transcrição | ✅ Aceito |
| ADR-006 | Datas relativas | ✅ Aceito |
| ADR-007 | Parcelas por fechamento | ✅ Aceito |
