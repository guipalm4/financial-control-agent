# Security Implementation — Finance Bot Telegram

> **Resumo executivo:** Implementação de segurança simplificada para perfil PESSOAL. Foco em proteção de dados financeiros pessoais com PIN hasheado, sessões com expiração, e boas práticas de desenvolvimento. Sem exposição externa (ambiente local).

---

## 1. Threat Model (Simplificado)

### Ativos

| Ativo | Classificação | Impacto se comprometido |
|-------|---------------|-------------------------|
| Dados financeiros (valores, categorias) | PII | Exposição de hábitos de consumo |
| Credenciais (PIN hash) | Sensível | Acesso não autorizado ao bot |
| Áudios temporários | Temporário | Exposição de voz do usuário |
| API Keys (Groq, Gemini) | Segredo | Uso indevido e custos |

### Vetores de Ataque (Contexto Local)

| Vetor | Risco | Mitigação |
|-------|-------|-----------|
| Acesso físico ao dispositivo | Médio | PIN + sessão com expiração |
| Comprometimento de .env | Alto | Não versionar, permissões restritas |
| Telegram Bot Token exposto | Alto | .env, rotação manual |
| SQL Injection | Baixo | SQLModel (ORM com queries parametrizadas) |

---

## 2. Classificação de Dados

| Dado | Classificação | Retenção | Criptografia |
|------|---------------|----------|--------------|
| telegram_id | PII | Indefinida | Em repouso (DB) |
| PIN | Sensível | Indefinida | Hash bcrypt |
| Valores financeiros | PII | Indefinida | Em repouso (DB) |
| Áudios | Temporário | 7 dias | Não (local) |
| API Keys | Segredo | N/A | .env (não versionado) |

---

## 3. AuthN (Autenticação)

### Configurações

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| PIN formato | 4-6 dígitos | Balança segurança/usabilidade |
| Hash algorithm | bcrypt | OWASP recomendado |
| Hash cost | 12 | Seguro e performático |
| Sessão duração | 24h inatividade | UX para uso pessoal |
| Tentativas antes bloqueio | 3 | Proteção brute-force |
| Tempo de bloqueio | 15 minutos | Razoável para uso pessoal |

### Implementação PIN

```python
import bcrypt

def hash_pin(pin: str) -> str:
    """Hash PIN com bcrypt cost=12"""
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt(12)).decode()

def verify_pin(pin_hash: str, pin: str) -> bool:
    """Verificar PIN contra hash"""
    return bcrypt.checkpw(pin.encode(), pin_hash.encode())
```

### Fluxo de Autenticação

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated: /start
    Unauthenticated --> CreatingPIN: Novo usuário
    Unauthenticated --> ValidatingPIN: Usuário existente
    CreatingPIN --> Authenticated: PIN válido
    ValidatingPIN --> Authenticated: PIN correto
    ValidatingPIN --> Locked: 3 tentativas
    Locked --> ValidatingPIN: 15min
    Authenticated --> Unauthenticated: 24h inatividade
    Authenticated --> [*]: Uso normal
```

### Recuperação de Acesso (PESSOAL)

| Método | Procedimento |
|--------|--------------|
| Reset manual | `UPDATE users SET pin_hash = NULL, pin_attempts = 0, locked_until = NULL WHERE telegram_id = XXX` |

---

## 4. AuthZ (Autorização)

### Matriz de Permissões

| Ação | Requer Auth | Verificações |
|------|-------------|--------------|
| /start | Não | - |
| /add_cartao | Sim | Session válida |
| Enviar áudio | Sim | Session válida |
| /resumo | Sim | Session válida |
| /despesas | Sim | Session válida |
| /fatura | Sim | Session válida |

### Verificação de Sessão

```python
async def require_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Decorator para verificar autenticação"""
    user_id = update.effective_user.id
    session = await get_session(user_id)
    
    if not session or not session.is_authenticated:
        await update.message.reply_text("❌ Faça login primeiro com /start")
        return False
    
    if session.expires_at < datetime.utcnow():
        await update.message.reply_text("⚠️ Sessão expirada. Digite seu PIN:")
        session.is_authenticated = False
        return False
    
    # Renovar sessão
    session.last_activity_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(hours=24)
    return True
```

---

## 5. OWASP Top 10 (Aplicável)

| # | Vulnerabilidade | Aplica? | Mitigação | Status |
|---|-----------------|---------|-----------|--------|
| A01 | Broken Access Control | ✅ | Verificar telegram_id em cada request | ✅ |
| A02 | Cryptographic Failures | ✅ | bcrypt para PIN, HTTPS para webhook | ✅ |
| A03 | Injection | ✅ | SQLModel ORM (queries parametrizadas) | ✅ |
| A04 | Insecure Design | ⚠️ | Seguir princípios de mínimo privilégio | ✅ |
| A05 | Security Misconfiguration | ✅ | .env não versionado, permissões restritas | ✅ |
| A06 | Vulnerable Components | ⚠️ | Manter deps atualizadas | Manual |
| A07 | Auth Failures | ✅ | PIN hasheado, bloqueio após tentativas | ✅ |
| A08 | Data Integrity Failures | ⚠️ | N/A (ambiente local) | N/A |
| A09 | Logging Failures | ✅ | Não logar PII/secrets | ✅ |
| A10 | SSRF | ❌ | N/A | N/A |

---

## 6. Rate Limiting (Básico)

| Contexto | Limite | Janela | Ação se exceder |
|----------|--------|--------|-----------------|
| Tentativas PIN | 3 | Por sessão | Bloquear 15min |
| Mensagens/min | 30 | 1 minuto | Ignorar silenciosamente |
| Áudios/dia | Sem limite | - | - |

### Implementação

```python
from datetime import datetime, timedelta
from collections import defaultdict

# Rate limiter simples em memória
rate_limits = defaultdict(list)

def check_rate_limit(user_id: int, limit: int = 30, window_seconds: int = 60) -> bool:
    """Verifica rate limit básico"""
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)
    
    # Limpar entradas antigas
    rate_limits[user_id] = [t for t in rate_limits[user_id] if t > cutoff]
    
    if len(rate_limits[user_id]) >= limit:
        return False
    
    rate_limits[user_id].append(now)
    return True
```

---

## 7. Logging Seguro

### O que logar

| Evento | Dados logados | Nível |
|--------|---------------|-------|
| Comando recebido | Comando, user_hash, timestamp | INFO |
| Erro de autenticação | user_hash, tentativas, timestamp | WARNING |
| Erro de transcrição | trace_id, erro genérico | ERROR |
| Despesa criada | expense_id, categoria (não valor) | INFO |

### O que NUNCA logar

| Dado | Motivo |
|------|--------|
| telegram_id | PII |
| PIN (mesmo hash) | Segurança |
| Valores financeiros | PII |
| Transcrições completas | Privacidade |
| API Keys | Segredo |

### Implementação

```python
import structlog
from hashlib import sha256

logger = structlog.get_logger()

def hash_user_id(telegram_id: int) -> str:
    """Hash do telegram_id para logs"""
    return sha256(str(telegram_id).encode()).hexdigest()[:16]

# Uso
logger.info(
    "expense_created",
    user_hash=hash_user_id(user_id),
    expense_id=str(expense.id),
    category=expense.category.name,  # OK: não é PII
    # amount=expense.total_amount,   # NUNCA: é PII
    trace_id=trace_id,
)
```

---

## 8. Gestão de Segredos

| Segredo | Onde armazenar | Rotação | Acesso |
|---------|----------------|---------|--------|
| TELEGRAM_BOT_TOKEN | .env | Manual (se comprometido) | App |
| GROQ_API_KEY | .env | Manual | App |
| GEMINI_API_KEY | .env | Manual | App |
| DATABASE_URL | .env | N/A | App |

### .env.example

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# APIs
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/finance_bot

# App
APP_ENV=development
DEBUG=false
```

### .gitignore

```
.env
.env.local
*.pem
*.key
```

---

## 9. Checklist de Segurança (PESSOAL)

### Antes do Deploy

- [ ] .env não está versionado
- [ ] .gitignore inclui .env e secrets
- [ ] PIN usa bcrypt cost=12
- [ ] Sessão expira após 24h
- [ ] Rate limiting básico implementado
- [ ] Logs não contêm PII
- [ ] SQLModel usado para queries (não SQL raw)

### Manutenção

- [ ] Rodar `pip audit` periodicamente
- [ ] Atualizar dependências com vulnerabilidades
- [ ] Rotacionar API keys se comprometidas

---

## 10. Resposta a Incidentes (Simplificado)

| Incidente | Ação |
|-----------|------|
| API Key exposta | Rotacionar imediatamente no provider |
| Bot Token exposto | Revogar via @BotFather, criar novo |
| Banco comprometido | Restaurar backup, resetar PINs |
| Brute force detectado | Verificar logs, aumentar bloqueio |
