# Marcar task como iniciada (Progress Tracker)

Execute o fluxo **Start Task** do Progress Tracker.

## O que fazer

1. Ler `docs/PROGRESS.md`.
2. Se eu não informei o ID da task, perguntar: "Qual o ID da task que você está iniciando? (ex: INFRA-001, AUTH-003)"
3. Localizar a task na tabela do Sprint correspondente.
4. Verificar se todas as dependências da task estão com status ✅. Se alguma não estiver, avisar que a task está bloqueada e não atualizar.
5. Atualizar a linha da task: Status de `⏳` para `🔄`.
6. Adicionar entrada no "Histórico de Atualizações" (nova linha no topo da tabela):
   - Data: hoje (YYYY-MM-DD)
   - Sprint: nome do sprint (ex: Sprint 1: Autenticação)
   - Task: ID da task
   - De: ⏳ | Para: 🔄
   - Notas: "Iniciando: [descrição curta da task]"
7. Responder confirmando a branch sugerida (coluna Branch do PROGRESS.md) para eu criar: `git checkout -b <branch>`.

## Regra

Siga exatamente o fluxo descrito em `.cursor/skills/progress-tracker/SKILL.md` (seção "Fluxo: Start Task"). Não pule a verificação de dependências.
