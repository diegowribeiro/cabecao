# Status do Deploy — Cabeção

**Última atualização:** 2026-03-14
**Sessão:** Setup inicial VPS

---

## VPS

| Item | Valor |
|------|-------|
| IP | `129.121.36.52` |
| Porta SSH | `22022` |
| Usuário | `root` |
| OS | Ubuntu 22.04 LTS |
| RAM | 3.8 GB |
| Disco | 99 GB (85 GB livres) |
| Repo clonado em | `/opt/cabecao` |
| Vault em | `/opt/cabecao/vault` |
| Khoj docker-compose | `/root/khoj/docker-compose.yml` |

Acesso SSH sem senha configurado (chave `~/.ssh/id_ed25519` do Mac já está em `authorized_keys` da VPS).

---

## O que foi feito

### Fase 1 — CONCLUÍDA ✅

- [x] SSH sem senha do Mac para a VPS
- [x] Deploy key `vps-cabecao` gerada em `~/.ssh/cabecao_deploy` na VPS e adicionada no GitHub com write access
- [x] Node.js 22 instalado
- [x] Primeiro push do repo `cabecao` para `github.com/diegowribeiro/cabecao`
- [x] Repo clonado em `/opt/cabecao`; vault com estrutura completa em `/opt/cabecao/vault`
- [x] Git configurado: `user.email = vps@cabecao`, `user.name = Cabecao VPS`
- [x] Cron a cada 15 min: `vps-cabecao-git-push.sh` → log em `/root/cabecao-sync.log`

### Fase 2 — PARCIALMENTE CONCLUÍDA ⚠️

- [x] Docker CE + docker-compose-plugin instalados
- [x] Khoj rodando via Docker Compose em `/root/khoj/`
  - Imagem DB: `pgvector/pgvector:pg16` (necessário para a extensão vector)
  - Comando override: `--host 0.0.0.0` (sem isso o Khoj só escuta em 127.0.0.1 dentro do container)
  - Vault montado em `/vault` (readonly) dentro do container
  - Admin: `admin@cabecao.local` / `cabecao2026`
- [x] Khoj respondendo em `http://129.121.36.52:42110` — testado e OK
- [ ] **PENDENTE:** Configurar Khoj pela UI (data sources, API key Anthropic, agente Mentor)
- [ ] Serviços **parados intencionalmente** — não expostos

### Fase 3 — NÃO INICIADA ⏳

- [ ] OpenClaw instalado
- [ ] Groq API key configurada
- [ ] Telegram bot criado e pareado
- [ ] Crons: briefing 8h, check-in 21h, revisão domingo 10h
- [ ] HEARTBEAT ativo

---

## Como retomar

### 1. Subir os serviços do Khoj

```bash
ssh -p 22022 root@129.121.36.52
cd /root/khoj && docker compose up -d
# aguardar ~30s e verificar:
docker compose ps
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:42110/api/health
```

### 2. Configurar o Khoj pela UI

Acesse: **http://129.121.36.52:42110**
Login: `admin@cabecao.local` / senha: `cabecao2026`

Passos:
1. **Settings → AI Models** → Add → Anthropic → colar `ANTHROPIC_API_KEY` → modelo `claude-sonnet-4-5-20250929`
2. **Settings → Data Sources** → Add → Files → path `/vault` → tipo Markdown → reindexação 30 min → salvar e aguardar indexação
3. **Agents** → New Agent → nome "Mentor Pessoal" → system prompt abaixo → Knowledge base = vault indexado → tools: web search

System prompt sugerido para o agente Mentor:
```
Você é o Cabeção, assistente pessoal de Diego. Fale sempre em português.
Você tem acesso ao vault pessoal do Diego (notas, projetos, áreas de vida, journal, reuniões).
Aja como um conselheiro pessoal: reflita sobre padrões, conecte informações do vault, faça perguntas que ajudem Diego a pensar com mais clareza.
Seja direto, honesto e sem enrolação. Quando relevante, cite notas do vault usando [[wikilinks]].
```

### 3. Fase 3 — OpenClaw

Após o Khoj configurado, seguir `docs/implementacao-vps.md` Fase 3:
- Instalar OpenClaw
- Configurar `ANTHROPIC_API_KEY` e `GROQ_API_KEY` no ambiente
- Criar Telegram bot via @BotFather → pegar token
- Configurar `config/openclaw-vault.example.yaml` com os tokens
- Adicionar os 3 crons
- Teste de ponta a ponta: áudio no Telegram → transcrição → vault → resposta

---

## Segurança — status (atualizado 2026-03-14)

### Concluído ✅
- [x] Senha root trocada (gerada aleatoriamente, salva em `/root/.root_pass` — só acessível via chave SSH)
- [x] SSH: login por senha desabilitado (`PasswordAuthentication no`)
- [x] SSH: root só por chave (`PermitRootLogin prohibit-password`)
- [x] SSH: máximo 3 tentativas (`MaxAuthTries 3`)
- [x] Firewall ufw ativo: `default deny incoming`, só porta 22022 aberta
- [x] Docker configurado com `"iptables": false` — não burla o ufw
- [x] Khoj bind em `127.0.0.1:42110` — inacessível da internet mesmo quando rodando
- [x] Secrets fora do docker-compose: arquivo `/root/khoj/.env` com `chmod 600`
- [x] Fail2ban: 3 tentativas falhas → ban de 1h na porta 22022
- [x] Unattended-upgrades: patches de segurança automáticos

### Pendente ⚠️
- [ ] **Gerar nova ANTHROPIC_API_KEY** na console Anthropic e invalidar a exposta no chat
  - Atualizar em `/root/khoj/.env` após gerar a nova
- [ ] (Futuro) Se precisar acessar Khoj UI remotamente: usar SSH tunnel
  `ssh -p 22022 -L 42110:localhost:42110 root@129.121.36.52`
  Nunca expor a porta 42110 diretamente

---

## Arquivos importantes na VPS

| Arquivo | Conteúdo |
|---------|----------|
| `/root/khoj/docker-compose.yml` | Config do Khoj (já com fixes: pgvector + --host 0.0.0.0) |
| `/root/.ssh/cabecao_deploy` | Chave SSH da VPS para o GitHub |
| `/root/cabecao-sync.log` | Log do cron de sync do vault |
| `/opt/cabecao/vault/` | Vault Obsidian |
| `/opt/cabecao/scripts/vps-cabecao-git-push.sh` | Script de sync |
