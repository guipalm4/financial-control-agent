# Guia de Teste - INFRA-001

Este guia explica como testar a implementação do bot antes de validar o DOD.

## 📋 Pré-requisitos

- ✅ Docker e Docker Compose instalados
- ✅ Arquivo `.env` configurado com `TELEGRAM_BOT_TOKEN`
- ✅ Token do bot válido do [@BotFather](https://t.me/botfather)

## 🐳 Opção 1: Testar com Docker Compose (Recomendado)

### Passo 1: Verificar se o .env está configurado

```bash
# Verificar se o token está presente
grep TELEGRAM_BOT_TOKEN .env
```

Deve mostrar algo como:
```
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

### Passo 2: Build e iniciar os serviços

```bash
# Build da imagem e iniciar serviços
docker compose up -d --build
```

Isso vai:
- Construir a imagem do bot
- Iniciar o PostgreSQL
- Iniciar o bot (aguardando o PostgreSQL ficar saudável)

### Passo 3: Verificar se os serviços estão rodando

```bash
# Ver status dos containers
docker compose ps
```

Você deve ver algo como:
```
NAME                    STATUS          PORTS
finance_bot_bot         Up X seconds    
finance_bot_postgres    Up X seconds   0.0.0.0:5432->5432/tcp
```

### Passo 4: Verificar logs do bot

```bash
# Ver logs em tempo real
docker compose logs -f bot
```

Você deve ver algo como:
```
bot  | 2026-02-09 08:20:00,000 - src.bot.app - INFO - Starting bot...
bot  | 2026-02-09 08:20:01,000 - telegram.ext.Application - INFO - Application started
```

**⚠️ Se houver erros:**
- Token inválido: `Unauthorized` ou `Invalid token`
- Problema de conexão: verifique sua internet
- Erro de importação: verifique os logs completos

### Passo 5: Testar no Telegram

1. Abra o Telegram
2. Procure pelo seu bot (nome que você configurou no @BotFather)
3. Envie o comando `/start`

**Resposta esperada:**
```
Olá [Seu Nome]! 👋

Bem-vindo ao Finance Bot!
Este bot está em desenvolvimento.
```

### Passo 6: Verificar logs após teste

```bash
# Ver logs do bot após enviar /start
docker compose logs bot | tail -20
```

Você deve ver algo como:
```
bot  | INFO:src.bot.handlers.start:User 123456789 (@seu_usuario) sent /start
```

## 💻 Opção 2: Testar Localmente (Sem Docker)

### Passo 1: Criar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### Passo 2: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 3: Verificar se o PostgreSQL está rodando

Se você já iniciou com Docker Compose, o PostgreSQL já está disponível em `localhost:5432`.

Se não, você pode iniciar apenas o PostgreSQL:
```bash
docker compose up -d postgres
```

### Passo 4: Executar o bot localmente

```bash
# Certifique-se de que o .env está na raiz do projeto
python -m src.main
```

Você deve ver:
```
2026-02-09 08:20:00,000 - src.bot.app - INFO - Starting bot...
2026-02-09 08:20:01,000 - telegram.ext.Application - INFO - Application started
```

### Passo 5: Testar no Telegram

Mesmo processo da Opção 1, Passo 5.

## 🔍 Troubleshooting

### Problema: Bot não responde

**Verificar:**
1. Logs do bot: `docker compose logs bot`
2. Token está correto: `grep TELEGRAM_BOT_TOKEN .env`
3. Bot está rodando: `docker compose ps`

**Soluções:**
- Se token inválido: Obtenha um novo token no @BotFather
- Se bot não inicia: Verifique os logs para erros de sintaxe ou importação

### Problema: Erro ao iniciar container

**Verificar:**
```bash
# Ver logs completos
docker compose logs bot

# Rebuild forçado
docker compose build --no-cache bot
docker compose up -d bot
```

### Problema: PostgreSQL não inicia

**Verificar:**
```bash
# Ver logs do PostgreSQL
docker compose logs postgres

# Verificar se a porta 5432 está livre
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows
```

### Problema: Erro de importação

**Verificar:**
```bash
# Testar importação manualmente
docker compose exec bot python -c "from src.bot.app import create_app; print('OK')"
```

## ✅ Checklist de Validação

Antes de marcar como DONE, verifique:

- [ ] `docker compose up -d` inicia sem erros
- [ ] Bot responde ao comando `/start` no Telegram
- [ ] Logs mostram mensagem de boas-vindas
- [ ] PostgreSQL está saudável (`docker compose ps`)
- [ ] Nenhum erro crítico nos logs

## 📝 Comandos Úteis

```bash
# Parar serviços
docker compose down

# Parar e remover volumes (limpar dados)
docker compose down -v

# Rebuild após mudanças no código
docker compose up -d --build

# Ver logs em tempo real
docker compose logs -f bot

# Entrar no container do bot
docker compose exec bot bash

# Executar comando Python no container
docker compose exec bot python -m src.main
```

## 🎯 Próximos Passos

Após validar que tudo funciona:
1. Marcar INFRA-001 como ✅ DONE no PROGRESS.md
2. Prosseguir para INFRA-002 (SQLModel + Alembic + pytest)
