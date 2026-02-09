# Marcar task como concluída (Progress Tracker)

Execute o fluxo **Finish Task** do Progress Tracker.

## O que fazer

1. Ler `docs/PROGRESS.md`.
2. Se eu não informei o ID da task, perguntar: "Qual o ID da task que você concluiu? (ex: AUTH-001, INFRA-002)"
3. Localizar a task (deve estar com status 🔄).
4. Atualizar a linha da task:
   - Status: `🔄` → `✅`
   - DOD: `[ ]` → `[x]`
5. Na seção "Resumo de Progresso" → "Por Sprint":
   - Na linha do Sprint dessa task: incrementar "Done" em 1 e recalcular "Progress" (%).
   - Na linha **TOTAL**: somar todos os Done dos sprints, recalcular Progress.
6. Adicionar entrada no "Histórico de Atualizações" (nova linha no topo da tabela):
   - Data: hoje (YYYY-MM-DD)
   - Sprint: nome do sprint
   - Task: ID da task
   - De: 🔄 | Para: ✅
   - Notas: "DOD completo"
7. Responder confirmando: "Task [ID] marcada como ✅ DONE. Resumo atualizado."

## Antes de marcar DONE

Lembre-se: só marque como concluída se o DOD foi cumprido (branch dedicada, lint/test passando, conforme `.cursor/rules/implementation.md`). Se não tiver certeza, pergunte.

## Regra

Siga exatamente o fluxo em `.cursor/skills/progress-tracker/SKILL.md` (seção "Fluxo: Finish Task").
