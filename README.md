# Finance Bot Telegram

Bot Telegram para registro de despesas pessoais via áudio com transcrição automática (Groq Whisper) e categorização inteligente por IA (Gemini Flash).

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Python 3.13+ (para desenvolvimento local)
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes Python)
- Token do Telegram Bot (obtenha em [@BotFather](https://t.me/botfather))

### Configuração

1. Clone o repositório:
```bash
git clone <repo-url>
cd financial-control-agent
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env e adicione seu TELEGRAM_BOT_TOKEN
```

3. Inicie os serviços:
```bash
docker compose up -d
```

4. Verifique os logs:
```bash
docker compose logs -f bot
```

## 📁 Estrutura do Projeto

````
finance-bot/
├── src/
│   ├── api/             # Endpoints FastAPI (health, webhooks)
│   ├── bot/             # Handlers do Telegram
│   │   ├── handlers/    # Handlers por feature
│   │   └── keyboards/   # Inline keyboards
│   ├── services/        # Lógica de negócio
│   ├── models/          # SQLModel entities
│   ├── db/              # Configuração do banco
│   └── core/            # Config, settings, utils
├── tests/               # Testes
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

## 🛠️ Desenvolvimento

### Executar localmente (sem Docker)

```bash
# Criar ambiente virtual e instalar dependências
uv venv
uv sync

# Executar o bot
uv run python -m src.main
```

**Nota:** O projeto usa [uv](https://github.com/astral-sh/uv) como gerenciador de pacotes. As dependências estão definidas em `pyproject.toml` e o lockfile `uv.lock` garante builds reproduzíveis.

### Comandos úteis

```bash
# Usando Makefile (recomendado)
make up          # Subir containers
make down        # Parar containers
make logs        # Ver logs do bot
make test        # Executar testes
make migrate     # Aplicar migrations
make shell       # Abrir shell no container

# Ou usando docker compose diretamente
docker compose logs -f bot
docker compose down
docker compose up -d --build
```

## 📝 Status do Projeto

Consulte `docs/PROGRESS.md` para acompanhar o progresso das features.

## 🔒 Segurança

- Nunca commite o arquivo `.env`
- Mantenha suas API keys seguras
- Consulte `docs/SECURITY_IMPLEMENTATION.md` para mais detalhes
