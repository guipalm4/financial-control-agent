FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY src/ ./src/

# Copy Alembic config and migrations (for make migrate inside container)
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Use Python from uv's managed environment
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["python", "-m", "src.main"]
