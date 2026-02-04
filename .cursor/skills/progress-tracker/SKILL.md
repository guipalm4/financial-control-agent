---
name: progress-tracker
description: Atualiza o Progress Tracker (docs/PROGRESS.md) ao iniciar ou concluir uma task. Use quando o usuário for começar uma atividade do projeto, terminar uma atividade, ou quando pedir para marcar task como iniciada/concluída no tracker.
---

# Progress Tracker — Start / Finish Task

Este projeto usa `docs/PROGRESS.md` como fonte de verdade. **SEMPRE** executar o fluxo correspondente ao iniciar ou ao concluir uma task.

---

## Quando usar

| Ação do usuário/agente | Fluxo a executar |
|------------------------|------------------|
| "Vou começar a task X", "Iniciar INFRA-001", "Começar FEAT-001" | **Start Task** |
| "Terminei a task", "Marcar como concluído", "DONE AUTH-001" | **Finish Task** |
| Antes de implementar qualquer task listada no PROGRESS.md | **Start Task** (primeiro passo) |
| Após validar DOD e considerar task pronta | **Finish Task** (último passo) |

---

## Fluxo: Start Task

**Objetivo:** Marcar a task como em progresso e garantir que dependências estão satisfeitas.

1. **Ler** `docs/PROGRESS.md`.
2. **Localizar** a task pelo ID (ex: `INFRA-001`, `AUTH-003`, `ONBOARD-005`). Se o usuário não informou o ID, perguntar qual task ou inferir pelo contexto (branch, FEAT em discussão).
3. **Verificar dependências:** Na coluna "Dependência" da linha da task, conferir se todos os IDs listados estão com status ✅ na tabela de tarefas. Se algum dependente estiver ⏳ ou 🔄, **avisar o usuário** que a task está bloqueada e não atualizar.
4. **Atualizar a linha da task:**
   - Coluna "Status": trocar `⏳` ou `🚫` por `🔄`
   - Manter demais colunas iguais.
5. **Histórico:** Na seção "## Histórico de Atualizações", **adicionar uma nova linha** no topo da tabela (logo abaixo do header):

   | Data | Sprint | Task | De | Para | Notas |
   |------|--------|------|----|------|-------|
   | YYYY-MM-DD | Nome do Sprint (ex: Sprint 1) | TASK-ID | ⏳ | 🔄 | Iniciando: [descrição curta] |

   Usar a data de hoje. "Notas" pode ser algo como "Iniciando modelo User".
6. **Confirmar** ao usuário: "Task TASK-ID marcada como 🔄 IN_PROGRESS. Branch sugerida: \`nome-da-branch\` (conforme PROGRESS.md)."

---

## Fluxo: Finish Task

**Objetivo:** Marcar a task como concluída, atualizar DOD e contadores.

1. **Ler** `docs/PROGRESS.md`.
2. **Localizar** a task pelo ID (deve estar com status 🔄).
3. **Atualizar a linha da task:**
   - Coluna "Status": trocar `🔄` por `✅`
   - Coluna "DOD": trocar `[ ]` por `[x]`
4. **Resumo de Progresso:** Na seção "### Por Sprint", localizar a linha do Sprint dessa task e:
   - Incrementar "Done" em 1
   - Recalcular "Progress" em % (Done / Total Tasks * 100). Atualizar a linha "**TOTAL**" também (somar todos os Done, recalcular %).
5. **Histórico:** Adicionar linha no topo da tabela de Histórico:

   | Data | Sprint | Task | De | Para | Notas |
   |------|--------|------|----|------|-------|
   | YYYY-MM-DD | Nome do Sprint | TASK-ID | 🔄 | ✅ | DOD completo |

6. **Opcional:** Se a task concluída desbloqueia testes (TEST-xxx), na subseção "### Testes (PRD)" do mesmo Sprint, marcar a coluna "Status" desses testes de `⏳` para `✅` apenas se os testes foram de fato implementados e passam. Caso contrário, deixar como está.
7. **Confirmar** ao usuário: "Task TASK-ID marcada como ✅ DONE. Resumo de Progresso atualizado."

---

## IDs de task por Sprint

Para localizar rápido:
- **Sprint 0:** INFRA-001 … INFRA-007
- **Sprint 1:** AUTH-001 … AUTH-009
- **Sprint 2:** ONBOARD-001 … ONBOARD-011
- **Sprint 3:** AUDIO-001 … AUDIO-010
- **Sprint 4:** CAT-001 … CAT-013
- **Sprint 5:** FIN-001 … FIN-010
- **Sprint 6:** REP-001 … REP-008
- **Sprint 7:** OBS-001 … OBS-009

---

## Regras

- **Nunca** inventar IDs; usar apenas os que existem nas tabelas do PROGRESS.md.
- **Sempre** manter o formato das tabelas (pipes, alinhamento).
- Se o usuário disser apenas "comecei" ou "terminei", perguntar o **ID da task** (ex: AUTH-002).
- Ao fazer **Finish Task**, lembrar ao usuário que o DOD (lint, test, branch) deve estar completo conforme `.cursor/rules/implementation.md`.
