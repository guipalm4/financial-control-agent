---
description: Workflow de implementação — Git, DOD, Clarification, Progress Tracker, Métricas (95%+ precisão). Aplica ao editar código ou testes.
alwaysApply: false
globs: ["src/**", "tests/**"]
---

# Workflow de Implementação — Finance Bot Telegram

**Meta de qualidade:** 95%+ de precisão em decisões (sem retrabalho).

---

## 0. Progress Tracker (FONTE DE VERDADE)

**OBRIGATÓRIO:** O arquivo `docs/PROGRESS.md` é a fonte de verdade para acompanhamento do projeto.

### Antes de iniciar QUALQUER task

1. Abrir `docs/PROGRESS.md`
2. Localizar a task no Sprint correspondente
3. Verificar dependências (coluna "Dependência")
4. **Se dependência não está ✅ DONE → NÃO INICIAR**
5. Atualizar status para 🔄 IN_PROGRESS
6. Registrar na tabela "Histórico de Atualizações"
7. **CRIAR BRANCH (obrigatório antes de qualquer edição):** `git checkout -b <branch>` usando a coluna **Branch** da task. Se já estiver em main/master/develop, NUNCA editar código antes de criar e trocar para a branch.

### Após concluir QUALQUER task

1. Verificar DOD completo (seção abaixo)
2. Atualizar status para ✅ DONE
3. Marcar checkbox na coluna DOD: `[x]`
4. Atualizar contadores em "Resumo de Progresso"
5. Registrar no "Histórico de Atualizações"

### Fluxo visual

```
PROGRESS.md → Verificar dependências → Branch (git checkout -b) → Implementar → DOD → PROGRESS.md (DONE)
```

**Regra crítica:** Nenhuma edição de arquivo (código, testes, config) pode acontecer antes de `git checkout -b <branch>`. A branch é o primeiro passo após marcar a task como IN_PROGRESS.

### Comandos de atualização

```markdown
# Antes de começar
| TASK-001 | Descrição | ⏳ → 🔄 | branch | ... |

# Após concluir
| TASK-001 | Descrição | 🔄 → ✅ | branch | ... | [x] |

# No histórico
| 2026-02-03 | Sprint 1 | AUTH-001 | ⏳ | 🔄 | Iniciando modelo User |
| 2026-02-03 | Sprint 1 | AUTH-001 | 🔄 | ✅ | Concluído com DOD |
```

---

## 1. Git Workflow (OBRIGATÓRIO)

**NUNCA codar diretamente na branch principal (main/master/develop).**

### Antes de implementar QUALQUER task (executar antes da primeira edição de código)

1. Verificar branch: `git branch --show-current`
2. Se estiver em main/master/develop: **criar e trocar para a branch da task** (nome em `docs/PROGRESS.md`, coluna Branch). Ex.: `git checkout -b feat/FEAT-001-user-model`
3. Só então iniciar implementação (editar arquivos).
4. Validar branch antes de commitar: `git status`

### Padrão de nomenclatura

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Feature | feat/FEAT-xxx-descricao | feat/FEAT-001-ativacao-pin |
| Bug fix | fix/BUG-xxx-descricao | fix/BUG-042-parcelas-incorretas |
| Refactor | refactor/descricao | refactor/extrair-servico-audio |
| Infra/Setup | chore/descricao | chore/docker-compose-setup |
| Docs | docs/descricao | docs/atualizar-readme |

### Workflow completo

```bash
git checkout main && git pull origin main
git checkout -b feat/FEAT-xxx-descricao
# Implementar (commits frequentes: feat:, fix:, chore:)
make lint && make test && docker compose up -d
git push -u origin feat/FEAT-xxx-descricao
```

### Anti-patterns (PROIBIDO)

- ❌ Codar na branch main/master/develop
- ❌ Branch sem prefixo (feat/, fix/, etc.) ou sem referência à task
- ❌ Commitar código que não passa no lint
- ❌ Push sem executar testes

---

## 2. Definition of Done (DOD) — Obrigatório

Uma task SÓ pode ser marcada como DONE quando TODOS os itens forem verificados.

### DOD Git (PRIMEIRO)

- [ ] Branch dedicada criada
- [ ] NÃO está em main/master/develop
- [ ] Commits seguem padrão convencional

### DOD Básico (todas as tasks)

- [ ] Código compila sem erros
- [ ] Lint passa sem erros críticos (`ruff check .`)
- [ ] Formatação aplicada (`ruff format .`)
- [ ] Tipos verificados (`mypy .`)

### DOD Funcional (features)

- [ ] Teste unitário existe e passa (mínimo happy path)
- [ ] Teste de integração existe (se API)
- [ ] Versões das libs conferem com project-context.md
- [ ] Bot funciona localmente (docker compose up -d)

### DOD Infra (setup/deploy)

- [ ] Container builda e inicia sem erro
- [ ] Health check responde
- [ ] Logs sem erros

### DOD Métricas

- [ ] Clarification Questions feitas quando necessário
- [ ] Precisão registrada em learnings.md
- [ ] Retrabalhos e causa registrados

### Comando de validação (antes de DONE)

```bash
git branch --show-current   # NÃO deve ser main
ruff check . && ruff format . --check && mypy .
pytest tests/ -v
docker compose up -d && docker compose logs
```

**NUNCA marcar DONE sem:** (1) branch dedicada, (2) validação completa, (3) métricas em learnings.md.

---

## 3. Workflow por FEAT

Para cada FEAT-xxx:

1. **PROGRESS:** Verificar `docs/PROGRESS.md`, localizar tasks da FEAT, verificar dependências
2. **PROGRESS:** Atualizar status para 🔄 IN_PROGRESS
3. **GIT:** Criar branch dedicada (nome conforme PROGRESS.md)
4. **PLAN mode:** Ler PRD.md e TECH_SPECS.md da FEAT, listar dependências
5. **Clarification:** Perguntar ANTES de implementar se houver ambiguidade
6. **Context7:** Consultar sintaxe de libs, validar versão, registrar em learnings.md
7. **Implementar** seguindo DOD
8. **Validar** antes de DONE e registrar métricas
9. **PROGRESS:** Atualizar status para ✅ DONE, atualizar contadores e histórico

---

## 4. Clarification Questions para Implementação

### Gatilhos obrigatórios (perguntar ANTES de codar)

| Situação | Pergunta estruturada |
|----------|---------------------|
| Lib não especificada | "Qual lib usar para X?" → [Opção A / Opção B / Sugerir] |
| Versão ambígua | "project-context diz 'X 1.x+', usar qual?" → [versão exata] |
| Múltiplas implementações | "Como implementar X?" → [Opção A / Opção B com prós/cons] |
| Comportamento não definido | "O que fazer quando Y?" → [Erro / Fallback / Ignorar] |
| Estrutura de diretórios | "Onde criar X?" → [caminho A / caminho B] |

### Formato de Clarification

```markdown
**Contexto:** Implementando FEAT-xxx | **Documento:** TECH_SPECS.md
**Pergunta 1:** [clara] — [ ] Opção A  [ ] Opção B  [ ] Outra
**Impacto se não perguntar:** [risco]
```

---

## 5. Checklist por Task

### Antes de começar

- [ ] **PROGRESS:** Verifiquei `docs/PROGRESS.md`
- [ ] **PROGRESS:** Dependências estão ✅ DONE
- [ ] **PROGRESS:** Atualizei status para 🔄 IN_PROGRESS
- [ ] Branch dedicada criada (nome conforme PROGRESS.md)
- [ ] Li FEAT-xxx no PRD.md e API-xxx no TECH_SPECS.md
- [ ] Identifiquei RULE-xxx e TEST-xxx
- [ ] PLAN mode usado
- [ ] Clarification feita se necessário

### Durante implementação

- [ ] Context7 consultado para libs novas
- [ ] Versões conferem com project-context.md
- [ ] Contrato de API seguido
- [ ] Códigos de erro corretos

### Antes de DONE

- [ ] lint, format, type-check passam
- [ ] Testes unitários e integração passam
- [ ] Bot funciona localmente
- [ ] Métricas em learnings.md
- [ ] **PROGRESS:** Atualizei status para ✅ DONE
- [ ] **PROGRESS:** Marquei DOD checkbox `[x]`
- [ ] **PROGRESS:** Atualizei contadores em "Resumo de Progresso"
- [ ] **PROGRESS:** Registrei no "Histórico de Atualizações"

---

## 6. Métricas (Meta: 95%+ precisão)

Precisão = (Decisões corretas na 1ª tentativa) / (Total de decisões). Registrar em learnings.md:

```markdown
## Métricas FEAT-xxx (YYYY-MM-DD)
| Métrica | Valor |
| Clarification Questions feitas | X |
| Decisões que precisaram retrabalho | Y |
| Precisão | (X-Y)/X * 100% |
| Causa dos retrabalhos | [lista] |
```

---

## 7. Consulta de documentação

Para implementar FEAT-xxx:
- **@PROGRESS.md** (verificar dependências, status, branch name) — **SEMPRE PRIMEIRO**
- @PRD.md (FEAT-xxx, regras de negócio)
- @TECH_SPECS.md (API-xxx, modelo de dados)
- @SECURITY_IMPLEMENTATION.md (requisitos de segurança)
- @ADR.md (decisões arquiteturais)

---

## 8. Anti-patterns (PROIBIDO)

- ❌ Codar em main
- ❌ Pular Plan mode
- ❌ Assumir versão sem Context7
- ❌ Marcar DONE sem DOD
- ❌ Ignorar testes do PRD
- ❌ Não registrar métricas
- ❌ Assumir quando há ambiguidade (perguntar!)
- ❌ **Iniciar task sem verificar PROGRESS.md**
- ❌ **Iniciar task com dependência não concluída**
- ❌ **Esquecer de atualizar PROGRESS.md após DONE**
- ❌ **Usar branch name diferente do PROGRESS.md**