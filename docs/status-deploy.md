# Status do Deploy — Cabeção

**Última atualização:** 2026-03-21 (alinhamento com `AGENTS.md` + docs)

**Status geral:** operacional — conferir serviços na VPS se algo mudar.

**Fonte de verdade:** [**AGENTS.md**](../AGENTS.md) (raiz). Este arquivo é **snapshot**; atualize após mudanças de deploy.

---

## VPS

| Item | Valor |
|------|-------|
| IP | `129.121.36.52` |
| Porta SSH | `22022` |
| Usuário | `root` |
| Acesso Mac | `ssh cabecao` (alias em `~/.ssh/config`) |
| OS | Ubuntu 22.04 LTS |
| RAM | 3.8 GB |
| Disco | 99 GB |
| Repo | `/opt/cabecao` |
| Vault | `/opt/cabecao/vault` |

---

## Serviços rodando

| Serviço | Status | Como verificar |
|---------|--------|----------------|
| OpenClaw Gateway | ✅ ativo (systemd) | `systemctl --user status openclaw-gateway.service` |
| Khoj (Docker) | ✅ ativo | `cd /root/khoj && docker compose ps` |
| Cron vault sync | ✅ a cada 30min | `crontab -l` |
| Cron Garmin sync | ✅ todo dia 7h | `crontab -l` |

---

## Crons configurados

### OpenClaw (lista real — **verificar na VPS**)

```bash
openclaw cron list
```

A tabela abaixo é **referência**; nomes/horários podem incluir extras (suplementos, negócio, etc.).

| Nome (exemplos) | Horário (BRT) | Notas |
|-----------------|---------------|--------|
| Briefing 8h | 8h | Mensagem curta (economia de tokens); ver `docs/economia-api.md` |
| Check-in 21h | 21h | Idem |
| Revisão semanal | Domingo 10h | Idem |
| Outros | variável | Loop quarta, suplementos, sessão negócio, análise mensal — conforme `cron list` |

### Sistema (crontab)

| Schedule | Script | O que faz |
|----------|--------|-----------|
| `*/30 * * * *` | `vps-cabecao-git-push.sh` | Git commit+push do vault → GitHub |
| `0 7 * * *` | `garmin-sync.py` | Busca dados Garmin do dia anterior → vault |

---

## Configurações aplicadas

### OpenClaw
- Modelo padrão: **Haiku** (`anthropic/claude-haiku-4-5`); Sonnet via `/model` (ver `openclaw models status`)
- Telegram: `@AssistenteCabecaoBot`, pareado com `@diegowribeiro` (ID 156600487)
- Áudio: Groq `whisper-large-v3-turbo` (transcrição)
- Exec allowlist: somente `/opt/cabecao/scripts/save-note.sh`
- Workspace: `SOUL.md` / `USER.md` **mínimos** (repo: `config/openclaw-workspace/`); persona longa em **`vault/PERSONALITY.md`**. Demais: `IDENTITY.md`, `AGENTS.md`, `TOOLS.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`

### Khoj (RAG)
- Modelo de chat: conforme UI (Haiku opcional para custo)
- Data source: `/vault/**/*.md` (reindexação automática)
- API token: **não** versionar; definir `KHOJ_UPDATE_TOKEN` na VPS para `save-note.sh` reindexar após cada nota
- Acesso UI (via tunnel): `ssh -p 22022 -L 42110:localhost:42110 root@129.121.36.52` → `http://localhost:42110`
- Admin: credenciais da **sua** instalação (Khoj UI / `.env`)

### Garmin
- Credenciais: `/root/.garmin-credentials` (chmod 600)
- Display name: `_diegoribeiro_`
- Dados salvos em: `vault/2-Areas/Saude/garmin/YYYY-MM-DD.md`
- Log: `/root/garmin-sync.log`

---

## Arquivos importantes na VPS

| Arquivo | Conteúdo |
|---------|----------|
| `/root/.openclaw/openclaw.json` | Config principal do OpenClaw |
| `/root/.openclaw/exec-approvals.json` | Allowlist de execução (só save-note.sh) |
| `/root/.openclaw/workspace/SOUL.md` | Núcleo; persona longa em `vault/PERSONALITY.md` |
| `/root/.openclaw/workspace/USER.md` | Identidade mínima; perfil completo no vault |
| `/root/.openclaw/workspace/IDENTITY.md` | Identidade do Cabeção |
| `/root/.openclaw/agents/main/agent/auth-profiles.json` | API keys Anthropic e Groq |
| `/root/.config/systemd/user/openclaw-gateway.service.d/env.conf` | Env vars do gateway |
| `/root/.telegram-bot-token` | Token do bot Telegram |
| `/root/khoj/docker-compose.yml` | Config do Khoj |
| `/root/khoj/.env` | Secrets do Khoj (chmod 600) |
| `/root/.garmin-credentials` | Credenciais Garmin Connect (chmod 600) |
| `/root/cabecao-sync.log` | Log do cron de sync do vault |
| `/root/garmin-sync.log` | Log do sync Garmin |
| `/opt/cabecao/scripts/save-note.sh` | Salva nota no vault + git push + reindex Khoj |
| `/opt/cabecao/scripts/garmin-sync.py` | Sync dados Garmin para vault |
| `/opt/cabecao/vault/` | Vault Obsidian completo |

---

## Segurança

- SSH: só chave Ed25519, sem senha, porta 22022
- `ufw`: default deny, só porta 22022 aberta
- Docker: `iptables: false` (não burla ufw)
- Khoj: bind em `127.0.0.1:42110`
- Fail2ban: 3 tentativas → ban 1h
- Telegram: `dmPolicy: pairing`, só ID 156600487
- Exec allowlist: somente `/opt/cabecao/scripts/save-note.sh`
- `save-note.sh`: proteção contra path traversal (`../`)
- Secrets: todos `chmod 600`, fora do vault e do repo

---

## Comandos úteis

```bash
# Acessar VPS
ssh cabecao

# Status serviços
systemctl --user status openclaw-gateway.service
cd /root/khoj && docker compose ps

# Reiniciar OpenClaw
systemctl --user restart openclaw-gateway.service

# Forçar reindex Khoj (token = mesmo valor que KHOJ_UPDATE_TOKEN)
curl -H "Authorization: Bearer $KHOJ_UPDATE_TOKEN" \
  "http://localhost:42110/api/update?force=true&t=markdown"

# Testar Garmin sync
python3 /opt/cabecao/scripts/garmin-sync.py

# Ver logs
journalctl --user -u openclaw-gateway.service -f
tail -f /root/garmin-sync.log
tail -f /root/cabecao-sync.log

# Vault: último git log
cd /opt/cabecao/vault && git log --oneline -10
```

---

## Troubleshooting

| Problema | O que fazer |
|----------|-------------|
| Bot não responde | `systemctl --user restart openclaw-gateway.service` |
| Khoj parado | `cd /root/khoj && docker compose up -d` |
| Vault não sincroniza | `cat /root/cabecao-sync.log` |
| Garmin sem dados | `python3 /opt/cabecao/scripts/garmin-sync.py` manualmente; checar `/root/garmin-sync.log` |
| API key expirou | Atualizar em `auth-profiles.json` + `env.conf` → reiniciar OpenClaw |
| Reindex Khoj não roda após nota | Definir `KHOJ_UPDATE_TOKEN` no `env.conf` do gateway; ver [khoj-token-passo-a-passo.md](khoj-token-passo-a-passo.md) |
