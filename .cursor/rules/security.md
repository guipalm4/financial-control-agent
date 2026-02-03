---
description: Regras de segurança do projeto
alwaysApply: true
---

# Security Rules — Finance Bot Telegram

## Classificação de Dados

| Dado | Classificação | Tratamento |
|------|---------------|------------|
| telegram_id | PII | Não logar |
| PIN | Sensível | Hash bcrypt (cost=12) |
| Valores financeiros | PII | Não logar em texto |
| Áudios | Temporário | Deletar após 7 dias |
| Transcrições | Interno | Não expor ao usuário |

## Regras Inquebráveis

### DEVE
- [ ] Validar e sanitizar TODO input do usuário
- [ ] Usar hash bcrypt (cost=12) para PIN
- [ ] Implementar rate limiting básico (anti-loop)
- [ ] Logar erros sem PII/secrets
- [ ] Usar HTTPS para webhook do Telegram

### NÃO DEVE
- [ ] Logar valores financeiros em texto
- [ ] Armazenar PIN em texto
- [ ] Expor tracebacks ao usuário
- [ ] Concatenar strings em queries SQL
- [ ] Armazenar secrets no código

## Autenticação

### PIN
- **Formato:** 4-6 dígitos numéricos
- **Hash:** bcrypt, cost=12
- **Bloqueio:** 3 tentativas → 15 minutos
- **Sessão:** Expira após 24h de inatividade

### Recuperação
- **Método:** Reset manual no banco (perfil PESSOAL)
- **Procedimento:** `UPDATE users SET pin_hash = NULL WHERE id = 'xxx'`

## Rate Limiting (Básico)

| Contexto | Limite | Ação |
|----------|--------|------|
| Tentativas PIN | 3/15min | Bloquear conta |
| Mensagens/minuto | 30/min | Ignorar excedentes |

## Gestão de Segredos

| Segredo | Onde | Rotação |
|---------|------|---------|
| TELEGRAM_BOT_TOKEN | .env | Manual |
| GROQ_API_KEY | .env | Manual |
| GEMINI_API_KEY | .env | Manual |
| DATABASE_URL | .env | N/A |

## Checkpoints (Aprovação Humana)

| Ação | Checkpoint |
|------|------------|
| Deletar cartão | Confirmação no bot |
| Excluir despesa | Confirmação no bot |
| Reset de PIN | Acesso direto ao banco |

## OWASP Top 10 (Aplicável)

| # | Vulnerabilidade | Mitigação |
|---|-----------------|-----------|
| A01 | Broken Access Control | Validar telegram_id em cada request |
| A03 | Injection | SQLModel ORM (queries parametrizadas) |
| A07 | Auth Failures | PIN com hash, bloqueio após tentativas |
