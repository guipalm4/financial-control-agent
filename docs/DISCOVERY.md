# FASE 1 — Discovery: Telegram Finance Bot

> **Status:** 🟡 Em andamento
> **Perfil:** PESSOAL | **Exposição:** LOCAL | **PII:** Sim

---

## 1. Resumo do Produto

**Bot de Telegram para gestão financeira pessoal** que permite registrar gastos via mensagem de áudio, categorizando automaticamente e persistindo em banco de dados.

### Exemplo concreto
> "Gastei 150 reais no mercado no cartão de crédito, parcela única"
> → Bot transcreve, extrai: valor=150, categoria=mercado, método=crédito, parcelas=1
> → Persiste no banco
> → Confirma: "✅ Registrado: R$150 | Mercado | Crédito | 1x"

---

## 2. Problema que resolve

- Dificuldade de manter controle financeiro manual
- Atrito de abrir apps para registrar cada gasto
- Esquecimento de registrar gastos pequenos
- Falta de visibilidade sobre vencimentos de faturas

---

## 3. Usuários e Papéis

| Papel | Descrição | Permissões |
|-------|-----------|------------|
| `OWNER` | Único usuário (você) | Todas as operações |

**Nota:** Por ser PESSOAL, o bot deve aceitar apenas mensagens do seu Telegram ID.

---

## 4. Dados e PII

### Dados manipulados

| Dado | Tipo | PII? | Sensibilidade |
|------|------|------|---------------|
| Telegram ID | string | Sim | Média |
| Valor do gasto | decimal | Não | Baixa |
| Descrição/categoria | string | Não | Baixa |
| Método de pagamento | enum | Não | Baixa |
| Data do gasto | datetime | Não | Baixa |
| Parcelas | integer | Não | Baixa |
| Vencimento fatura | date | Não | Baixa |
| Áudios (temporário) | blob | Sim | Alta |

### Tratamento de PII
- Telegram ID: armazenado para validação de acesso
- Áudios: processados e **deletados** após transcrição (não persistir)
- Banco local: sem exposição externa

---

## 5. Features (Escopo MVP)

### ✅ MVP (v1)

| ID | Feature | Prioridade |
|----|---------|------------|
| FEAT-001 | Receber mensagem de áudio | Alta |
| FEAT-002 | Transcrever áudio para texto | Alta |
| FEAT-003 | Extrair dados estruturados do texto (NLP/LLM) | Alta |
| FEAT-004 | Persistir gasto no banco de dados | Alta |
| FEAT-005 | Confirmar registro via mensagem | Alta |
| FEAT-006 | Categorizar gasto automaticamente | Alta |
| FEAT-007 | Registrar método de pagamento (PIX/débito/crédito) | Alta |
| FEAT-008 | Registrar parcelas | Média |
| FEAT-009 | Configurar vencimento de faturas por cartão | Média |
| FEAT-010 | Alertar vencimentos próximos | Média |

### ❌ Fora do MVP (v2+)

| Feature | Motivo |
|---------|--------|
| Frontend web/mobile | Fase 2 |
| Relatórios e gráficos | Fase 2 |
| Múltiplos usuários | Não aplicável (PESSOAL) |
| Integração com bancos (Open Finance) | Complexidade |
| Exportação para Excel/CSV | Nice to have |

---

## 6. Integrações

| Sistema | Tipo | Obrigatório? | Observação |
|---------|------|--------------|------------|
| Telegram Bot API | API externa | Sim | Receber/enviar mensagens |
| Groq Whisper Large v3 Turbo | API externa | Sim | Transcrição de áudio (STT) |
| Gemini 2.0 Flash | API externa | Sim | Extração de dados (LLM) |
| SQLite | Local | Sim | Persistência |

---

## 7. Restrições e Preferências

### Stack Definida

| Camada | Tecnologia | Tipo |
|--------|------------|------|
| Linguagem | Python 3.14 | Local |
| Bot Framework | python-telegram-bot 22.x | Local |
| Speech-to-Text | Groq Whisper Large v3 Turbo | API |
| LLM | Gemini 2.0 Flash | API |
| Banco | SQLite + SQLAlchemy | Local |

### Restrições
- Usar apenas APIs (sem IA local)
- Groq API tier free para STT (suficiente para uso pessoal)
- Google AI tier free para Gemini (suficiente para uso pessoal)
- Banco local para dados financeiros

---

## 8. Incertezas (RESOLVIDAS)

| ID | Incerteza | Resolução |
|----|-----------|-----------|
| ~~INC-001~~ | ~~Performance do Whisper local~~ | ✅ Usar **Groq Whisper Large v3 Turbo** (API) |
| ~~INC-002~~ | ~~Qualidade da extração de dados~~ | ✅ Usar **Gemini 2.0 Flash** (API) |
| ~~INC-003~~ | ~~Categorias de gastos~~ | ✅ Lista fixa + ESSENCIAL/NÃO ESSENCIAL |
| ~~INC-004~~ | ~~Múltiplos cartões de crédito~~ | ✅ 4 cartões, vencimentos diferentes |

---

## 9. Matriz de Risco

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Transcrição imprecisa | Média | Alto | Fallback para texto manual |
| Extração incorreta de valores | Média | Alto | Confirmação antes de salvar |
| Categorização errada | Alta | Baixo | Permitir correção manual |
| Banco corrompido | Baixa | Alto | Backup automático |

---

## 10. Métricas de Sucesso

| Métrica | Target | Como medir |
|---------|--------|------------|
| Taxa de transcrição correta | >90% | Amostragem manual |
| Taxa de extração correta | >85% | Validação humana |
| Tempo de resposta | <10s | Log de latência |
| Uso diário | >1 registro/dia | Contagem no banco |

---

## Gate da FASE 1

- [x] Perfil definido: **PESSOAL**
- [x] MVP delimitado: 10 features
- [x] PII classificada: Telegram ID + áudios (temporários)
- [x] Integrações listadas: Telegram, STT, LLM, DB
- [x] Incertezas resolvidas

✅ **FASE 1 COMPLETA** — Pronto para FASE 2

---

## Decisões do Bloco 2 (Resolvidas)

| Pergunta | Decisão |
|----------|---------|
| Speech-to-Text | **Groq Whisper Large v3 Turbo** (API) |
| LLM para extração | **Gemini 2.0 Flash** (API) |
| Cartões de crédito | **4 cartões** com vencimentos diferentes |
| Categorias | **Lista fixa** + subcategoria ESSENCIAL/NÃO ESSENCIAL |
| Confirmação | **Sim**, pedir confirmação antes de salvar |

---

## Categorias Definidas

| Categoria | Tipo | Exemplos |
|-----------|------|----------|
| 🛒 Mercado | ESSENCIAL | Supermercado, feira, açougue |
| 🏠 Moradia | ESSENCIAL | Aluguel, condomínio, IPTU |
| 💡 Contas | ESSENCIAL | Luz, água, gás, internet |
| 🚗 Transporte | ESSENCIAL | Combustível, estacionamento, Uber |
| 🏥 Saúde | ESSENCIAL | Farmácia, consultas, plano de saúde |
| 🍔 Alimentação | NÃO ESSENCIAL | Restaurantes, delivery, lanches |
| 🎮 Lazer | NÃO ESSENCIAL | Streaming, jogos, cinema |
| 👕 Vestuário | NÃO ESSENCIAL | Roupas, calçados, acessórios |
| 🎁 Outros | NÃO ESSENCIAL | Presentes, assinaturas, diversos |

> **Nota:** Categorias podem ser ajustadas na FASE 3.

---

## Fluxo com Confirmação

```
[Áudio] → [Groq Whisper v3 Turbo] → [Texto]
                              ↓
                    [Gemini 2.0 Flash: Extração de dados]
                              ↓
                    [Bot envia preview]
                    "💰 R$ 150,00
                     📁 Mercado (ESSENCIAL)
                     💳 Nubank - Crédito 1x
                     📅 29/01/2026
                     
                     Confirmar? [✅ Sim] [❌ Não] [✏️ Editar]"
                              ↓
              [Usuário confirma] → [Salva no banco]
```
