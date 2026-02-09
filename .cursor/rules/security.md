---
description: Regras de segurança para Finance Bot Telegram
alwaysApply: true
---

# Security Rules — Finance Bot Telegram

## Perfil de Segurança

- **Classificação:** PESSOAL (single-user, local)
- **Exposição:** Docker Compose + ngrok (local)
- **Dados:** Financeiros pessoais (não-PII crítico, mas sensível)

## Dados Sensíveis

| Dado | Classificação | Onde armazenar | Criptografia |
|------|---------------|----------------|--------------|
| PIN do usuário | Sensível | DB (hash bcrypt) | bcrypt cost=12 |
| Telegram User ID | Identificador | DB | - |
| Dados financeiros | Pessoal | DB | - |
| API Keys (Groq, Gemini) | Segredo | .env (nunca no repo) | - |
| Bot Token | Segredo | .env (nunca no repo) | - |

## Regras Obrigatórias

### Autenticação

- **DEVE** usar PIN de 4-6 dígitos para ativar o bot
- **DEVE** hashear PIN com bcrypt (cost=12)
- **DEVE** bloquear conta após 3 tentativas erradas (15 min)
- **DEVE** expirar sessão após 24h de inatividade
- **NÃO DEVE** armazenar PIN em texto plano

### Segredos

- **DEVE** usar variáveis de ambiente para segredos
- **DEVE** ter `.env.example` sem valores reais
- **NÃO DEVE** commitar `.env` no repositório
- **NÃO DEVE** logar API keys ou tokens

### Validação de Input

- **DEVE** validar todo input do usuário (Pydantic)
- **DEVE** sanitizar input antes de processar
- **DEVE** rejeitar payloads muito grandes (áudio > 60s)
- **NÃO DEVE** concatenar strings em queries SQL

### Telegram

- **DEVE** validar que mensagens vêm do usuário autorizado
- **DEVE** usar apenas o Telegram User ID cadastrado
- **NÃO DEVE** responder a usuários não autorizados

### Áudio

- **DEVE** deletar arquivos de áudio após 7 dias
- **DEVE** validar formato de áudio antes de processar
- **NÃO DEVE** armazenar áudio indefinidamente

## Ações Proibidas (Anti-patterns)

- ❌ Armazenar segredos no código
- ❌ Logar dados financeiros completos
- ❌ Aceitar input sem validação
- ❌ Usar SQL concatenado
- ❌ Responder a qualquer usuário do Telegram
- ❌ Expor endpoints sem autenticação

## Checkpoints com Aprovação Humana

| Operação | Requer aprovação | Motivo |
|----------|------------------|--------|
| Deletar despesas em massa | Sim | Irreversível |
| Resetar PIN | Sim | Segurança |
| Exportar dados | Não | Dados pessoais |
| Backup do banco | Não | Automático |

## Logging Seguro

| Evento | Logar | NUNCA logar |
|--------|-------|-------------|
| Login/PIN check | user_id, success, timestamp | PIN |
| Despesa criada | expense_id, user_id | Valores financeiros |
| Erro de transcrição | error_code, audio_duration | Conteúdo do áudio |
| Chamada API externa | service, latency, status | API keys |

## Gestão de Segredos

| Segredo | Variável de ambiente | Obrigatório |
|---------|---------------------|-------------|
| Bot Token | `TELEGRAM_BOT_TOKEN` | Sim |
| Groq API Key | `GROQ_API_KEY` | Sim |
| Gemini API Key | `GEMINI_API_KEY` | Sim |
| Database URL | `DATABASE_URL` | Sim |
| PIN Salt (opcional) | `PIN_SALT` | Não (bcrypt gera) |

## Recuperação de Acesso

**Perfil PESSOAL:** Reset manual no banco de dados

```sql
-- Reset PIN (gerar novo hash via Python)
UPDATE users SET pin_hash = '<novo_hash>' WHERE telegram_id = <seu_id>;

-- Desbloquear conta
UPDATE users SET locked_until = NULL, failed_attempts = 0 WHERE telegram_id = <seu_id>;
```
