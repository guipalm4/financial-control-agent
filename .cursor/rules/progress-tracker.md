---
description: Garante atualização do Progress Tracker ao iniciar e ao concluir tasks (como taskmaster)
alwaysApply: true
---

# Progress Tracker — Regra Obrigatória

O arquivo `docs/PROGRESS.md` é a **fonte de verdade** do projeto. O agente **DEVE** atualizá-lo em dois momentos.

## Ao INICIAR uma task

Antes de implementar qualquer task listada no PROGRESS.md (INFRA-xxx, AUTH-xxx, ONBOARD-xxx, etc.):

1. **Executar o fluxo Start Task:** ler a skill `.cursor/skills/progress-tracker/SKILL.md` (seção "Fluxo: Start Task") e aplicar no `docs/PROGRESS.md`.
2. Ou o usuário pode rodar o comando: `/progress-start-task` e informar o ID da task.
3. **Não iniciar** se as dependências da task não estiverem ✅. Avisar o usuário que a task está bloqueada.

Resumo: verificar dependências → atualizar Status para 🔄 → adicionar linha no Histórico.

## Ao CONCLUIR uma task

Quando uma task for considerada pronta (DOD cumprido):

1. **Executar o fluxo Finish Task:** ler a skill `.cursor/skills/progress-tracker/SKILL.md` (seção "Fluxo: Finish Task") e aplicar no `docs/PROGRESS.md`.
2. Ou o usuário pode rodar o comando: `/progress-finish-task` e informar o ID da task.
3. Só marcar ✅ após lint/test/branch validados (DOD em implementation.md).

Resumo: Status 🔄 → ✅, DOD [x], atualizar Resumo de Progresso e Histórico.

## Onde estão os fluxos

- **Skill (passo a passo):** `.cursor/skills/progress-tracker/SKILL.md`
- **Comandos no chat:** digite `/` e escolha:
  - `progress-start-task` — marcar task como iniciada
  - `progress-finish-task` — marcar task como concluída
  - `resume-work` — retomar contexto (tasks em progresso, próxima task)
  - `next-task` — sugerir próxima task a iniciar
  - `validate-dod` — validar DOD antes de marcar DONE

## Anti-pattern (PROIBIDO)

- ❌ Implementar task do PROGRESS sem antes ter executado Start Task (ou comando equivalente).
- ❌ Dar por concluída uma task sem executar Finish Task e atualizar PROGRESS.md.
