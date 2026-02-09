---
name: pr-workflow
description: Executa commit e abertura de PR seguindo o template do repositório e docs/PROGRESS.md. Use quando o usuário pedir para commitar, abrir PR, criar pull request, ou "fazer o commit e abrir o PR".
---

# PR Workflow — Commit e Pull Request

Fluxo para commitar alterações de uma task e abrir o PR usando o template do projeto.

---

## Quando usar

| Pedido do usuário | Ação |
|-------------------|------|
| "Fazer o commit e abrir o PR" | Commit + push + criar PR com template |
| "Abrir o PR", "Criar o PR" | Assumir que commit já existe; push (se necessário) + criar PR |
| "Só commitar" | Apenas stage + commit (mensagem convencional) |

---

## Fluxo completo (commit + PR)

1. **Contexto**
   - Ler `docs/PROGRESS.md` e identificar a task pela **branch atual** (coluna Branch).
   - Se não houver branch de task (ex.: está em `main`), avisar e não commitar.

2. **Arquivos**
   - Incluir no commit apenas arquivos da task: código, testes, `docs/PROGRESS.md` se foi atualizado.
   - Não incluir: `.env`, arquivos de regras/IDE não relacionados à task.

3. **Commit**
   - Mensagem no padrão convencional:
     - `feat(TASK-ID): descrição curta` (ex: `feat(AUTH-002): handler /start com ConversationHandler para criação de PIN`)
     - `fix(TASK-ID): ...` para correções
     - `chore: ...` para infra/docs sem task ID
   - Segundo parágrafo (opcional): bullets com detalhes.

4. **Push**
   - `git push -u origin <branch>` (branch atual).

5. **Criar PR**
   - **Título:** igual ao início da mensagem de commit (ex: `feat(AUTH-002): Handler /start com ConversationHandler para criação de PIN`).
   - **Base:** `main` (ou o default do repo).
   - **Body:** preencher usando o conteúdo de [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md):
     - **Contexto:** Task, Branch, Sprint; frase "Implementação da task TASK-ID — [descrição]".
     - **Alterações:** lista objetiva do que foi feito.
     - **DOD:** marcar checkboxes que foram cumpridos (branch, ruff, mypy, pytest, commits).

---

## Template de PR (referência)

O repositório tem template em `.github/PULL_REQUEST_TEMPLATE.md`. Ao criar o PR, preencher:

- **Task:** ID da task (ex: AUTH-002).
- **Branch:** nome da branch (ex: feat/FEAT-001-start-handler).
- **Sprint:** nome do Sprint (ex: Sprint 1: Autenticação).
- **Alterações:** resumo das mudanças.
- **DOD:** marcar itens atendidos.

Se o GitHub já injetar o template no body, apenas preencher os campos e checkboxes.

---

## Regras

- Nunca commitar em `main`/`master`/`develop`; avisar se a branch atual for uma delas.
- Mensagem de commit sempre com prefixo `feat:`, `fix:`, `chore:` (e TASK-ID quando fizer sentido).
- PR deve referenciar a task e a branch conforme `docs/PROGRESS.md`.

---

## Integração

- Antes de **Finish Task** no Progress Tracker, o DOD (lint, test, branch) deve estar ok; este fluxo assume que já foi validado.
- Para **iniciar** uma task (branch + PROGRESS), usar a skill [progress-tracker](../progress-tracker/SKILL.md) (Start Task).
