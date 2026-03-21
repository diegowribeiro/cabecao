# Implementação na VPS — Cabeção

Guia passo a passo para subir o sistema na VPS **já criada**. Stack: vault (repo cabecao) + Khoj (RAG) + OpenClaw (agente + Telegram + Groq).

---

## Pré-requisitos (VPS)

- Acesso SSH (root ou usuário com sudo).
- Ubuntu (recomendado) ou Debian.
- Mínimo: ~2 GB RAM, 20 GB disco.
- Repo **cabecao** no GitHub/GitLab (privado), com primeiro push feito.

---

## Visão das fases

| Fase | O que fazer | Tempo estimado |
|------|-------------|-----------------|
| **1** | Clonar repo, configurar Git + cron (sync vault) | ~30 min |
| **2** | Docker + Khoj, indexar vault, agente Mentor | ~1–2 h |
| **3** | OpenClaw, Groq, Telegram, crons 8h/21h/domingo, HEARTBEAT | ~1–2 h |

---

## Fase 1 — Vault e Git na VPS

### 1.1 Clonar o repo cabecao

Escolha um diretório (ex.: `/opt/cabecao`). O **vault** será `.../cabecao/vault`.

```bash
# Na VPS, via SSH
sudo mkdir -p /opt/cabecao
sudo chown "$(whoami):$(whoami)" /opt/cabecao
git clone git@github.com:SEU_USUARIO/cabecao.git /opt/cabecao
# ou: git clone https://github.com/SEU_USUARIO/cabecao.git /opt/cabecao
```

**Path do vault na VPS:** `/opt/cabecao/vault`. OpenClaw e Khoj usarão esse path.

### 1.2 Git na VPS (para o cron poder dar push)

1. **Configurar identidade (uma vez):**
   ```bash
   cd /opt/cabecao
   git config user.email "voce@email.com"
   git config user.name "Cabeção VPS"
   ```

2. **Chave SSH:** gere uma chave na VPS (se ainda não tiver) e adicione como **Deploy Key** no GitHub/GitLab com permissão de **escrita**:
   ```bash
   ssh-keygen -t ed25519 -C "vps-cabecao" -f ~/.ssh/cabecao_deploy -N ""
   cat ~/.ssh/cabecao_deploy.pub
   ```
   No GitHub: repo → Settings → Deploy keys → Add deploy key → colar o `.pub`, marcar "Allow write access".

3. **Usar essa chave para o clone** (se clonou com HTTPS, troque o remote):
   ```bash
   cd /opt/cabecao
   git remote set-url origin git@github.com:SEU_USUARIO/cabecao.git
   # Garanta que o SSH usa a chave certa, ex. em ~/.ssh/config:
   # Host github.com
   #   IdentityFile ~/.ssh/cabecao_deploy
   ```

### 1.3 Cron: commit + push da pasta vault/ a cada 15 min

```bash
crontab -e
```

Adicione (ajuste o path se não for `/opt/cabecao`):

```
*/15 * * * * REPO_DIR=/opt/cabecao /opt/cabecao/scripts/vps-cabecao-git-push.sh >> /var/log/cabecao-sync.log 2>&1
```

Se `/var/log/cabecao-sync.log` der permissão negada, use um path em sua home, ex.: `~/cabecao-sync.log`.

**Checklist Fase 1**

- [ ] Repo clonado em `/opt/cabecao`, pasta `vault/` existe.
- [ ] `git config` e deploy key com write access configurados.
- [ ] Cron instalado; após 15 min, verificar se há commit no GitHub (ou `tail -f ~/cabecao-sync.log`).

---

## Fase 2 — Khoj (RAG) na VPS

### 2.1 Instalar Docker

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker && sudo systemctl start docker
sudo usermod -aG docker "$USER"
# Fazer logout/login para o grupo docker valer
```

### 2.2 Subir o Khoj com o vault montado

```bash
mkdir -p ~/khoj && cd ~/khoj
curl -sSL -o docker-compose.yml https://raw.githubusercontent.com/khoj-ai/khoj/master/docker-compose.yml
```

Edite `docker-compose.yml` e monte o vault. Exemplo (ajuste o path do vault):

```yaml
# No serviço do Khoj, em volumes, adicione algo como:
volumes:
  - /opt/cabecao/vault:/vault
```

Ou use variável de ambiente para o content path, conforme documentação do Khoj. Em seguida:

```bash
docker compose up -d
curl -s http://localhost:42110/ | head -20
```

### 2.3 Configurar Khoj (UI)

1. Acesse `http://IP_DA_VPS:42110` (ou configure um domínio com proxy reverso e HTTPS).
2. Crie conta de admin.
3. **Content:** adicione fonte de arquivos apontando para o path do vault dentro do container (ex.: `/vault`). Tipos: Markdown. Reindexação automática (ex.: a cada 30 min).
4. **Model:** Anthropic, API key (a mesma que usará no OpenClaw). Para **custo no dia a dia**, use **Claude Haiku** como modelo de chat/resposta do Khoj (RAG continua igual; só a síntese fica mais barata). IDs típicos: `claude-haiku-4-5` / `claude-haiku-4-5-20251001` — confira no seletor do Khoj ou no console Anthropic.
5. **Agente "Mentor Pessoal":** crie um agente com system prompt de conselheiro pessoal, baseado no vault, em português; knowledge base = conteúdo indexado; tools = web search + file access (se disponível).

**Checklist Fase 2**

- [ ] Docker rodando; `docker ps` mostra o container do Khoj.
- [ ] Khoj responde em `http://localhost:42110`.
- [ ] Vault indexado; busca retorna notas do vault.
- [ ] Agente Mentor criado e testado (pergunta sobre algo que está no vault).

---

## Fase 3 — OpenClaw na VPS

### 3.1 Instalar OpenClaw

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Siga o wizard: informe `ANTHROPIC_API_KEY`, canal Telegram, skill Obsidian (vault). Para **economia**, configure o modelo padrão do agente como **Claude Haiku** e deixe **Sonnet** disponível via `/model` no Telegram (ver [economia-api.md](economia-api.md)).

### 3.2 Variáveis de ambiente

Garanta que o processo do OpenClaw (systemd ou seu shell) tenha:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk_..."
```

Coloque em `~/.bashrc` ou no service file do OpenClaw (ex.: `/etc/systemd/system/openclaw.service` com `Environment=ANTHROPIC_API_KEY=...`).

**Groq:** crie conta em https://console.groq.com e gere uma API key para transcrição (Whisper).

### 3.3 Configuração: áudio (Groq) e Telegram

No config do OpenClaw (ex.: `~/.openclaw/config.yaml` ou o path indicado pela instalação), use o exemplo em `config/openclaw-vault.example.yaml` do repo. Trechos essenciais:

**Transcrição (Groq):**

```yaml
tools:
  media:
    audio:
      enabled: true
      maxBytes: 20971520   # 20 MB
      timeoutSeconds: 120
      models:
        - provider: groq
          model: whisper-large-v3-turbo
```

**Telegram:**

```yaml
channels:
  telegram:
    enabled: true
    botToken: "SEU_TOKEN"
    dmPolicy: pairing
    groups:
      "*":
        requireMention: true
```

### 3.4 Path do vault no OpenClaw

O OpenClaw precisa ler **TOOLS.md**, **PERSONALITY.md** e **HEARTBEAT.md** do vault. Configure o skill Obsidian (ou equivalente) para o path:

- **`/opt/cabecao/vault`**

Assim o agente usa as regras de gravação (TOOLS.md), personalidade (PERSONALITY.md) e automações (HEARTBEAT.md). O `TOOLS.md` no repo já descreve a estrutura; na VPS o path real é `/opt/cabecao/vault`.

### 3.5 Crons do OpenClaw (horários fixos)

```bash
# Briefing 8h (America/Sao_Paulo — ajuste timezone se preciso). Mensagens curtas = menos tokens por sessão isolada.
openclaw cron add --name "Briefing 8h" --cron "0 8 * * *" --session isolated --message "Briefing: clima SP, tarefas abertas no vault (Inbox), uma pergunta de intenção do dia. Curto."

# Check-in noturno 21h
openclaw cron add --name "Check-in 21h" --cron "0 21 * * *" --session isolated --message "Check-in: como foi o dia? Um highlight e humor. Se responder, atualizar Journal/ hoje."

# Revisão semanal domingo 10h
openclaw cron add --name "Revisão semanal" --cron "0 10 * * 0" --session isolated --message "Revisão semanal: resumir Journal + Meetings da semana, criar Journal/weekly/YYYY-Www.md se faltar, Telegram só com bullets."
```

Ajuste a mensagem e o timezone conforme seu uso. Detalhes e checklist: [economia-api.md](economia-api.md).

### 3.6 HEARTBEAT

O arquivo `vault/HEARTBEAT.md` já descreve o que o Cabeção deve fazer a cada ~30 min (verificar Meetings/, etc.). Com o vault em `/opt/cabecao/vault`, o OpenClaw carrega esse arquivo automaticamente se o skill Obsidian estiver apontando para esse path.

**Checklist Fase 3**

- [ ] OpenClaw instalado e rodando.
- [ ] Claude (ANTHROPIC_API_KEY) e Groq (GROQ_API_KEY) configurados.
- [ ] Telegram bot criado, token configurado, bot pareado com você (`dmPolicy: pairing`).
- [ ] Skill/vault apontando para `/opt/cabecao/vault`; TOOLS.md e PERSONALITY.md carregados.
- [ ] Crons 8h, 21h e domingo 10h adicionados.
- [ ] **Teste de ponta a ponta:** envie um áudio no Telegram → deve transcrever (Groq), classificar, salvar no vault e responder em português confirmando onde salvou. Verifique em `/opt/cabecao/vault` se o arquivo foi criado/atualizado (ex.: Inbox, Journal ou Meetings).

---

## Resumo dos paths na VPS

| O quê | Path |
|-------|------|
| Repo cabecao | `/opt/cabecao` |
| Vault (OpenClaw + Khoj) | `/opt/cabecao/vault` |
| Script cron (push vault) | `/opt/cabecao/scripts/vps-cabecao-git-push.sh` |
| Config OpenClaw (exemplo) | `/opt/cabecao/config/openclaw-vault.example.yaml` |

---

## Segurança (lembrete)

- Repo **cabecao**: privado.
- API keys só em variáveis de ambiente na VPS, nunca no vault nem no repo.
- Telegram: 2FA na conta; bot com `dmPolicy: pairing`.
- Khoj/OpenClaw: firewall (só portas necessárias); Khoj atrás de HTTPS se acessar de fora.

---

## Próximo passo após tudo funcionando

- **Mac:** clonar cabecao, abrir a pasta **vault/** no Obsidian, pull/push (ou plugin Obsidian Git). Ver [proximos-passos.md](proximos-passos.md) e [sync-vault.md](sync-vault.md).
- **iPhone:** mesmo repo, pasta **vault/** no Obsidian, Obsidian Git para pull/push.

Assim o vault fica sincronizado entre VPS, Mac e iPhone.
