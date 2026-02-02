# Security — Telegram Finance Bot

> **Resumo:** Requisitos de segurança simplificados para perfil PESSOAL.
> Bot local, único usuário, sem exposição externa.

## 1. Classificação de Dados

| Dado | Classificação | Armazenamento | Retenção |
|------|---------------|---------------|----------|
| TELEGRAM_BOT_TOKEN | 🔴 SEGREDO | .env (local) | Permanente |
| GROQ_API_KEY | 🔴 SEGREDO | .env (local) | Permanente |
| GOOGLE_API_KEY | 🔴 SEGREDO | .env (local) | Permanente |
| OWNER_TELEGRAM_ID | 🟡 SENSÍVEL | .env (local) | Permanente |
| Arquivos de áudio | 🟡 TEMPORÁRIO | Memória | Deletar após uso |
| Dados financeiros | 🟢 PESSOAL | SQLite local | Permanente |
| Banco SQLite | 🟢 PESSOAL | ./data/ | Backup manual |

## 2. Autenticação

### Validação de Usuário

```python
import os

OWNER_TELEGRAM_ID = int(os.getenv("OWNER_TELEGRAM_ID"))

async def validate_owner(update: Update) -> bool:
    """
    Valida se o usuário é o owner autorizado.
    Retorna False silenciosamente para não autorizar.
    """
    return update.effective_user.id == OWNER_TELEGRAM_ID
```

### Comportamento para Usuários Não Autorizados

| Ação | Comportamento |
|------|---------------|
| Mensagem de texto | Ignorar silenciosamente |
| Mensagem de áudio | Ignorar silenciosamente |
| Comando /start | Ignorar silenciosamente |
| Callback | Ignorar silenciosamente |

**Justificativa:** Não revelar a existência ou funcionalidade do bot para terceiros.

## 3. Gestão de Segredos

### Variáveis de Ambiente

```env
# .env (NUNCA commitar)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
OWNER_TELEGRAM_ID=123456789
DATABASE_URL=sqlite:///./data/finance.db
```

```env
# .env.example (commitar)
TELEGRAM_BOT_TOKEN=your_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OWNER_TELEGRAM_ID=your_telegram_id_here
DATABASE_URL=sqlite:///./data/finance.db
```

### .gitignore

```gitignore
.env
*.db
data/
__pycache__/
```

## 4. Tratamento de Áudio

```python
async def process_audio(voice_file: File) -> str:
    """
    Processa áudio de forma segura:
    1. Baixa para memória (não disco)
    2. Envia para API
    3. Descarta imediatamente
    """
    # Baixar para bytes (memória)
    audio_bytes = await voice_file.download_as_bytearray()
    
    try:
        # Transcrever
        text = await groq_client.transcribe(audio_bytes)
        return text
    finally:
        # Garantir descarte
        del audio_bytes
```

**Regras:**
- ❌ NÃO salvar áudio em disco
- ❌ NÃO persistir áudio no banco
- ❌ NÃO logar conteúdo do áudio
- ✅ Processar apenas em memória
- ✅ Deletar imediatamente após uso

## 5. Logging Seguro

### O que Logar

```python
# ✅ Permitido
logger.info("Bot iniciado")
logger.info(f"Gasto registrado: id={expense.id}")
logger.error(f"Erro na transcrição", extra={"trace_id": trace_id})
logger.warning(f"Timeout de confirmação: expense_id={expense_id}")
```

### O que NÃO Logar

```python
# ❌ Proibido
logger.info(f"Token: {TELEGRAM_BOT_TOKEN}")
logger.info(f"API Key: {GROQ_API_KEY}")
logger.info(f"User ID: {telegram_id}")
logger.info(f"Valor: R$ {amount}")
logger.info(f"Transcrição: {text}")
```

### Formato de Log

```python
import logging
import uuid

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def generate_trace_id() -> str:
    return str(uuid.uuid4())[:8]
```

## 6. Backup do Banco

### Manual (Recomendado)

```bash
# Backup
cp ./data/finance.db ./backups/finance_$(date +%Y%m%d).db

# Restaurar
cp ./backups/finance_20260129.db ./data/finance.db
```

### Automático (Opcional)

```python
# src/utils/backup.py
import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """Backup diário do banco."""
    src = Path("./data/finance.db")
    dst = Path(f"./backups/finance_{datetime.now():%Y%m%d}.db")
    dst.parent.mkdir(exist_ok=True)
    shutil.copy2(src, dst)
```

## 7. Dependências

### Auditoria

```bash
# Verificar vulnerabilidades
pip install safety
safety check

# Atualizar dependências
pip install --upgrade -r requirements.txt
```

### Versões Fixas

```toml
# pyproject.toml - usar versões específicas
dependencies = [
    "python-telegram-bot>=21.0,<22.0",
    "groq>=0.4.0,<1.0",
    "sqlalchemy>=2.0,<3.0",
]
```

## 8. Checklist de Segurança

### Antes do Primeiro Uso

- [ ] `.env` criado com tokens reais
- [ ] `.env` adicionado ao `.gitignore`
- [ ] `OWNER_TELEGRAM_ID` configurado corretamente
- [ ] Diretório `data/` com permissões restritas

### Manutenção

- [ ] Backup do banco feito regularmente
- [ ] Dependências atualizadas mensalmente
- [ ] Logs não contêm dados sensíveis
- [ ] Tokens não commitados no Git

## 9. Resposta a Incidentes

| Incidente | Ação |
|-----------|------|
| Token do bot vazado | Revogar no @BotFather, gerar novo |
| API key Groq vazada | Revogar no console Groq, gerar nova |
| API key Google vazada | Revogar no Google Cloud Console, gerar nova |
| Banco corrompido | Restaurar do último backup |
| Acesso não autorizado | Verificar logs, trocar tokens |

## 10. Não Aplicável (Perfil PESSOAL)

Por ser perfil PESSOAL sem exposição externa, os seguintes itens não se aplicam:

- Rate limiting
- WAF/Firewall
- SSL/TLS (conexão local)
- RBAC (único usuário)
- Audit trail formal
- Compliance (LGPD/GDPR)
- Penetration testing
- SOC2/ISO27001
