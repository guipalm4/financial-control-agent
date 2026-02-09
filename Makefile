.PHONY: help install up down logs test lint typecheck migrate migrate-create shell clean

# Default target
help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instalar dependências Python (uv sync)"
	@echo "  make lock         - Gerar/atualizar uv.lock"
	@echo "  make up           - Subir containers (docker compose up -d)"
	@echo "  make down         - Parar containers (docker compose down)"
	@echo "  make logs         - Ver logs do bot"
	@echo "  make test         - Executar testes"
	@echo "  make lint         - Lint e formatação (ruff check . && ruff format . --check)"
	@echo "  make typecheck    - Verificação de tipos (mypy .)"
	@echo "  make migrate      - Aplicar migrations (alembic upgrade head)"
	@echo "  make migrate-create - Criar nova migration (use: make migrate-create MESSAGE='descrição')"
	@echo "  make shell        - Abrir shell no container do bot"
	@echo "  make clean        - Limpar cache Python e testes"

# Instalar dependências
install:
	uv sync

# Gerar/atualizar lockfile
lock:
	uv lock

# Docker Compose
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f bot

# Testes
test:
	uv run pytest tests/ -v

# Qualidade: lint e tipos (DOD INFRA-003)
lint:
	uv run ruff check . && uv run ruff format . --check

typecheck:
	uv run mypy .

# Migrations
migrate:
	docker compose exec bot alembic upgrade head

migrate-create:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Erro: Use make migrate-create MESSAGE='descrição da migration'"; \
		exit 1; \
	fi
	docker compose exec bot alembic revision --autogenerate -m "$(MESSAGE)"

# Shell no container
shell:
	docker compose exec bot /bin/bash

# Limpeza
clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
