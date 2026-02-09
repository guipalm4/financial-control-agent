# Finance Bot Telegram

Bot Telegram para registro de despesas pessoais via áudio com transcrição automática (Groq Whisper) e categorização inteligente por IA (Gemini Flash).

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Python 3.13+ (para desenvolvimento local)
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

```
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
└── requirements.txt
```

## 🛠️ Desenvolvimento

### Executar localmente (sem Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

### Comandos úteis

```bash
# Ver logs do bot
docker compose logs -f bot

# Parar serviços
docker compose down

# Rebuild após mudanças
docker compose up -d --build
```

## 📝 Status do Projeto

Consulte `docs/PROGRESS.md` para acompanhar o progresso das features.

## 🔒 Segurança

- Nunca commite o arquivo `.env`
- Mantenha suas API keys seguras
- Consulte `docs/SECURITY_IMPLEMENTATION.md` para mais detalhes
