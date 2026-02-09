# Próxima task (Progress Tracker)

Encontra a próxima task que pode ser iniciada (dependências satisfeitas) e sugere começar por ela.

## O que fazer

1. **Ler** `docs/PROGRESS.md`.
2. **Percorrer as tabelas de tarefas** por Sprint (Sprint 0, 1, 2, …), na ordem.
3. **Para cada task com status ⏳ (PENDING):**
   - Ler a coluna "Dependência" da mesma linha.
   - Se "Dependência" estiver vazia ou listar apenas IDs que aparecem em outras linhas com status ✅, considerar a task **desbloqueada**.
   - A **primeira** task desbloqueada encontrada é a **próxima sugerida**.
4. **Responder ao usuário:**
   - ID da task (ex: INFRA-003, AUTH-001).
   - Nome do Sprint.
   - Descrição curta (coluna Task).
   - Branch sugerida (coluna Branch).
   - Instrução: "Para iniciar, use o command **/progress-start-task** e informe o ID: [ID]."
5. Se **todas** as tasks estiverem ✅ ou 🔄, informar: "Todas as tasks do tracker estão concluídas ou em progresso. Verifique se há novas tasks em docs/PROGRESS.md ou se o projeto está completo."

## Regra

Usar apenas IDs e dados presentes em `docs/PROGRESS.md`. A ordem de análise é a ordem dos Sprints e das linhas nas tabelas.
