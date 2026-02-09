# Security Implementation — Finance Bot Telegram

> **Resumo executivo:** Especificação de segurança simplificada para perfil PESSOAL. Foco em proteção básica de dados financeiros pessoais, autenticação via PIN e gestão segura de segredos.

---

## 1. Threat Model (Simplificado)

### Ativos

| Ativo | Classificação | Impacto se comprometido |
|-------|---------------|-------------------------|
| Dados financeiros | Pessoal/Sensível | Exposição de hábitos de gastos |
| PIN do usuário | Sensível | Acesso não autorizado |
| API Keys (Groq, Gemini) | Segredo | Uso indevido, custos |
| Bot Token | Segredo | Controle do bot |

### Vetores de Ataque (Contexto Local)

| Vetor | Ativo alvo | Probabilidade | Mitigação |
|-------|------------|---------------|-----------|
| Acesso físico ao servidor | Todos | Baixa (localhost) | Senha no host |
| Telegram ID spoofing | Dados | Média | Validar telegram_id único |
| Brute force PIN | PIN | Média | Bloqueio após 3 tentativas |
| Exposição de .env | API Keys | Baixa | .gitignore, permissões |
| Logs com dados sensíveis | Dados | Média | Logging seguro |

---

## 2. Classificação de Dados

| Dado | Classificação | Retenção | Minimização | Criptografia |
|------|---------------|----------|-------------|--------------|
| telegram_id | Identificador | Permanente | Não | - |
| PIN | Sensível | Permanente | Hash only | bcrypt (cost=12) |
| Despesas (valores) | Pessoal | Permanente | Não | - |
| Descrições | Pessoal | Permanente | Não | - |
| Áudio | Temporário | 7 dias | Deletar após transcrição | - |
| API Keys | Segredo | - | .env only | - |

---

## 3. Autenticação (AuthN)

### Configurações

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| PIN length | 4-6 dígitos | Balance segurança/usabilidade |
| Hash algorithm | bcrypt | OWASP recomendado |
| bcrypt cost | 12 | ~250ms por hash |
| Sessão expiry | 24h | Conveniência (uso pessoal) |
| Lock after | 3 tentativas | Proteção brute force |
| Lock duration | 15 minutos | Dissuasão sem bloquear permanente |

### Fluxo de Autenticação

```mermaid
flowchart TD
    A[Usuário envia /start] --> B{Usuário existe?}
    B -->|Não| C[Criar PIN]
    B -->|Sim| D{Conta bloqueada?}
    D -->|Sim| E[Mostrar tempo restante]
    D -->|Não| F[Pedir PIN]
    F --> G{PIN correto?}
    G -->|Sim| H[Criar sessão 24h]
    G -->|Não| I[Incrementar tentativas]
    I --> J{3 tentativas?}
    J -->|Sim| K[Bloquear 15min]
    J -->|Não| F
```

### Implementação

```python
from passlib.hash import bcrypt

# Criar hash
pin_hash = bcrypt.using(rounds=12).hash(pin)

# Verificar PIN
is_valid = bcrypt.verify(pin_input, user.pin_hash)
```

---

## 4. Autorização (AuthZ)

### Modelo Simplificado (Single-User)

| Operação | Quem pode | Validação |
|----------|-----------|-----------|
| Todas as operações | Usuário único | telegram_id == user.telegram_id |

### Validação de Telegram ID

```python
async def validate_user(update: Update) -> User | None:
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    
    if not user:
        return None  # Não autorizado
    
    if user.locked_until and user.locked_until > datetime.utcnow():
        return None  # Conta bloqueada
    
    if user.session_expires_at and user.session_expires_at < datetime.utcnow():
        return None  # Sessão expirada
    
    return user
```

---

## 5. OWASP Top 10 (Contexto Bot Telegram)

| # | Vulnerabilidade | Aplica? | Mitigação |
|---|-----------------|---------|-----------|
| A01 | Broken Access Control | Parcial | Validar telegram_id em toda operação |
| A02 | Cryptographic Failures | Sim | bcrypt para PIN, HTTPS para APIs |
| A03 | Injection | Sim | SQLModel (parameterized), validação Pydantic |
| A04 | Insecure Design | Não | Design simples, single-user |
| A05 | Security Misconfiguration | Sim | .env para segredos, Docker isolado |
| A06 | Vulnerable Components | Parcial | Fixar versões no pyproject.toml e uv.lock |
| A07 | Auth Failures | Sim | Bloqueio após tentativas, sessão expira |
| A08 | Software/Data Integrity | Não | Ambiente local, não há CI/CD |
| A09 | Logging Failures | Sim | Não logar PIN, valores completos |
| A10 | SSRF | Não | Não há requests dinâmicos |

---

## 6. Rate Limiting (Básico)

| Operação | Limite | Janela | Ação se exceder |
|----------|--------|--------|-----------------|
| Tentativas de PIN | 3 | Sessão | Bloquear 15min |
| Áudios por minuto | 10 | 1 minuto | Ignorar (Telegram já limita) |
| Comandos por minuto | 30 | 1 minuto | Ignorar |

---

## 7. Logging Seguro

### O que logar

| Evento | Dados logados | Nível |
|--------|---------------|-------|
| Login bem-sucedido | user_id, timestamp | INFO |
| Login falhou | user_id, tentativa # | WARNING |
| Conta bloqueada | user_id | WARNING |
| Despesa criada | expense_id, user_id | INFO |
| Erro de transcrição | error_code, audio_duration | ERROR |
| Erro de API externa | service, status_code, latency | ERROR |

### NUNCA logar

- PIN (em nenhuma forma)
- Valores de despesas
- Conteúdo de transcrições
- API Keys
- Tokens

### Exemplo de Log Seguro

```python
import structlog

logger = structlog.get_logger()

# ✅ Correto
logger.info("expense_created", expense_id=expense.id, user_id=user.id)

# ❌ Errado
logger.info("expense_created", amount=expense.amount, description=expense.description)
```

---

## 8. Gestão de Segredos

### Variáveis de Ambiente

| Variável | Obrigatória | Exemplo | Onde obter |
|----------|-------------|---------|------------|
| `TELEGRAM_BOT_TOKEN` | Sim | `123456:ABC-DEF...` | @BotFather |
| `GROQ_API_KEY` | Sim | `gsk_...` | console.groq.com |
| `GEMINI_API_KEY` | Sim | `AI...` | aistudio.google.com |
| `DATABASE_URL` | Sim | `postgresql://user:pass@localhost/db` | Local |

### .env.example

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# AI APIs
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://finance:finance@localhost:5432/finance_bot

# Optional
LOG_LEVEL=INFO
```

### Regras

- ✅ `.env` no `.gitignore`
- ✅ `.env.example` com placeholders no repo
- ✅ Permissões `600` no arquivo `.env`
- ❌ Nunca commitar `.env` com valores reais
- ❌ Nunca logar valores de variáveis de ambiente

---

## 9. Segurança do Docker

### docker-compose.yml (Boas Práticas)

```yaml
version: "3.8"

services:
  bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - internal
    # Não expor portas desnecessariamente
    
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: finance
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: finance_bot
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - internal
    # Não expor porta 5432 ao host

networks:
  internal:
    driver: bridge

volumes:
  pgdata:
```

### Dockerfile (Boas Práticas)

```dockerfile
FROM python:3.13-slim

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Não rodar como root
RUN useradd -m -s /bin/bash app
USER app

WORKDIR /app

COPY --chown=app:app pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=app:app src/ ./src/

# Usar Python do ambiente gerenciado pelo uv
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "src.main"]
```

---

## 10. Recuperação de Acesso

### Perfil PESSOAL: Reset Manual

Como é single-user e local, reset é feito diretamente no banco:

```bash
# Conectar ao banco
docker compose exec db psql -U finance -d finance_bot

# Ver usuário
SELECT id, telegram_id, locked_until, failed_attempts FROM users;

# Desbloquear conta
UPDATE users 
SET locked_until = NULL, failed_attempts = 0 
WHERE id = 1;

# Resetar PIN (gerar novo hash via Python primeiro)
# python -c "from passlib.hash import bcrypt; print(bcrypt.using(rounds=12).hash('123456'))"
UPDATE users 
SET pin_hash = '<novo_hash>' 
WHERE id = 1;
```

---

## 11. Checklist de Segurança

### Antes do Deploy

- [ ] `.env` não está no git
- [ ] `.env.example` existe com placeholders
- [ ] Permissões do `.env` são `600`
- [ ] Docker não expõe portas desnecessárias
- [ ] Usuário do container não é root
- [ ] Versões das libs estão fixadas

### Durante Desenvolvimento

- [ ] Validar telegram_id em todo handler
- [ ] Usar SQLModel (nunca concatenar SQL)
- [ ] Usar Pydantic para validação de input
- [ ] Não logar dados sensíveis
- [ ] Hash de PIN com bcrypt

### Monitoramento

- [ ] Logs de erro configurados
- [ ] Alertas para falhas de autenticação (opcional)
