.PHONY: help install up down logs test migrate migrate-create shell clean

# Default target
help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instalar dependências Python"
	@echo "  make up           - Subir containers (docker compose up -d)"
	@echo "  make down         - Parar containers (docker compose down)"
	@echo "  make logs         - Ver logs do bot"
	@echo "  make test         - Executar testes"
	@echo "  make migrate      - Aplicar migrations (alembic upgrade head)"
	@echo "  make migrate-create - Criar nova migration (use: make migrate-create MESSAGE='descrição')"
	@echo "  make shell        - Abrir shell no container do bot"
	@echo "  make clean        - Limpar cache Python e testes"

# Instalar dependências
install:
	pip install -r requirements.txt

# Docker Compose
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f bot

# Testes
test:
	pytest tests/ -v

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
