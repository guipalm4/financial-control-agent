# Retomar trabalho (Progress Tracker)

Recupere o contexto atual do projeto para continuar de onde parou. Use ao abrir uma nova sessão ou quando precisar relembrar o estado do desenvolvimento.

## O que fazer

1. **Ler** `docs/PROGRESS.md`.
2. **Identificar tasks em progresso:** Localizar todas as linhas com status `🔄` (IN_PROGRESS) nas tabelas de tarefas de cada Sprint.
3. **Montar resumo para o usuário:**
   - Se houver task(s) 🔄: listar **ID**, **Sprint**, **Descrição** (coluna Task), **Branch** sugerida. Dizer: "Você está trabalhando em: [lista]. Branch esperada: `nome-da-branch`. Próximo passo: [resumo do Detalhamento da task]."
   - Se **não** houver nenhuma task 🔄: informar "Nenhuma task em progresso." e indicar a **próxima task disponível** (primeira task com status ⏳ cujas dependências estão todas ✅). Sugerir: "Para iniciar, use o command `/progress-start-task` com o ID [ex: INFRA-003]."
4. **Opcional:** Mostrar resumo do "Resumo de Progresso" (Por Sprint): total de tasks, Done, Progress %.
5. **Confirmar** em português, de forma objetiva.

## Regra

Use apenas IDs e dados que existem em `docs/PROGRESS.md`. Não invente tasks ou branches.
