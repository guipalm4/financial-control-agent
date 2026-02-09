# Validar Definition of Done (DOD)

Execute as verificações do DOD antes de marcar uma task como concluída. Garante que branch, lint, tipos e testes estão ok.

## O que fazer

1. **Verificar branch atual:**
   - Rodar `git branch --show-current`.
   - Se for `main`, `master` ou `develop`: avisar "❌ Você está na branch principal. Crie uma branch de feature (ex: `feat/FEAT-xxx-descricao`) antes de validar o DOD." e parar.
2. **Rodar verificações (na raiz do projeto):**
   - Lint: `ruff check .`
   - Formatação: `ruff format . --check`
   - Tipos: `mypy .` (ou `uv run mypy .` se usar uv)
   - Testes: `pytest tests/ -v` (ou `uv run pytest tests/ -v` / `make test`)
3. **Resumir resultado:**
   - Para cada comando: ✅ passou ou ❌ falhou (e mostrar saída relevante em caso de falha).
   - No final: "DOD aprovado" se tudo passou, ou "DOD não aprovado — corrigir [lista de falhas] antes de usar /progress-finish-task."
4. **Lembrar:** Só marcar task como ✅ DONE (via `/progress-finish-task`) após DOD aprovado, conforme `.cursor/rules/implementation.md`.

## Regra

Use os comandos do projeto: preferir `make test` se existir, senão `uv run pytest tests/ -v` ou `pytest tests/ -v`. Idem para mypy/ruff conforme `Makefile` ou `pyproject.toml`.
