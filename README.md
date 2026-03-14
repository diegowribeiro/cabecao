# Cabeção — Assistente Pessoal do Diego

Segundo cérebro rodando 24/7 em VPS. Captura texto e áudio pelo Telegram, classifica, salva no vault Obsidian e responde com base no que você já viveu e registrou.

---

## O que é o Cabeção

Um assistente pessoal que age como mentor, confidente e segundo cérebro. Não é um chatbot genérico — ele conhece sua história, seus padrões, seus objetivos. Quanto mais você usa, mais ele sabe sobre você.

**Canal principal:** Telegram → @AssistenteCabecaoBot
**Dono:** @diegowribeiro (user ID 156600487)

---

## Stack completa

```
[Você no Telegram]
       │
       ▼
  [OpenClaw] ──── agente principal rodando 24/7 na VPS
       │                │
       │        [Groq Whisper] ──── transcrição de áudios
       │                │
       ▼                ▼
   [Vault] ◄──── arquivos .md salvos pelo agente
       │
       ▼
   [Khoj RAG] ──── indexa o vault, responde com contexto do que está lá
       │
       ▼
  [Claude API] ──── raciocínio, geração, respostas
       │
       ▼
[Git → GitHub] ──── sync automático a cada 15 min
```

### Componentes e por que cada um

| Componente | O que faz | Por que esse |
|------------|-----------|--------------|
| **OpenClaw** | Gateway do agente: recebe Telegram, processa, executa, responde | Integra tudo nativamente: Telegram, áudio, shell, crons — sem código custom |
| **Claude Sonnet 4.6** | LLM para raciocínio e geração | Melhor custo-benefício em qualidade de resposta e contexto longo |
| **Groq + Whisper** | Transcrição de áudios do Telegram | Rápido, barato (~US$0,04/h), suporta português, sem GPU na VPS |
| **Khoj** | RAG sobre o vault — busca semântica nas suas notas | Open source, roda local/Docker, integra com Anthropic |
| **Vault Obsidian** | Base de conhecimento pessoal em Markdown | Arquivos simples, versionáveis com Git, abrem em qualquer editor |
| **Git + GitHub** | Sync e versionamento do vault | Histórico completo, acesso de qualquer lugar, backup automático |
| **VPS HostGator** | Tudo roda aqui — OpenClaw, Khoj, vault | Controle total, custo fixo, sem dependência de serviço de terceiros |

---

## Infraestrutura (VPS)

**IP:** 129.121.36.52
**SSH:** `ssh cabecao` (alias em `~/.ssh/config` no Mac, porta 22022, chave `~/.ssh/id_ed25519`)
**OS:** Ubuntu 22.04 | 3.8GB RAM | 99GB disco

### Serviços rodando

| Serviço | Como gerenciar |
|---------|---------------|
| OpenClaw Gateway | `systemctl --user status openclaw-gateway.service` |
| Khoj (Docker) | `cd /root/khoj && docker compose ps` |
| Cron vault sync | `crontab -l` (a cada 15 min faz git push do vault) |

### Paths importantes na VPS

```
/opt/cabecao/               ← repo clonado (vault + scripts)
/opt/cabecao/vault/         ← vault Obsidian
/opt/cabecao/scripts/       ← scripts de automação
/root/.openclaw/            ← config do OpenClaw
/root/.openclaw/openclaw.json                              ← config principal
/root/.openclaw/agents/main/agent/auth-profiles.json      ← API keys
/root/.config/systemd/user/openclaw-gateway.service.d/env.conf  ← env vars
/root/.telegram-bot-token   ← token do bot Telegram
/root/khoj/                 ← docker-compose do Khoj
/root/khoj/.env             ← secrets do Khoj (Anthropic key, postgres)
/root/cabecao-sync.log      ← log do cron de sync do vault
```

---

## Vault — estrutura de pastas

```
vault/
├── 0-Inbox/
│   └── Inbox.md            ← append de pensamentos rápidos, ideias soltas, tasks
├── 1-Projects/             ← projetos ativos com tasks e notas
├── 2-Areas/
│   ├── Saude/
│   ├── Financas/
│   ├── Carreira/
│   └── Relacionamentos/
├── 3-Resources/
│   └── ideas/              ← ideias elaboradas (YYYY-MM-DD-titulo.md)
├── 4-Archive/              ← projetos concluídos ou pausados
├── Meetings/               ← reuniões (YYYY-MM-DD-titulo.md)
├── Journal/
│   ├── YYYY-MM-DD.md       ← diário diário
│   └── weekly/
│       └── YYYY-Www.md     ← revisão semanal
├── People/                 ← notas sobre pessoas importantes
├── _config/                ← configs e specs internas
├── _templates/             ← templates de notas
├── PERSONALITY.md          ← quem é o Cabeção, quem é o Diego, como se comportar
├── TOOLS.md                ← como e onde salvar conteúdo no vault
└── HEARTBEAT.md            ← automações periódicas
```

---

## Como o Cabeção salva notas

Usa o script `/opt/cabecao/scripts/save-note.sh` que:
1. Cria ou faz append no arquivo correto
2. Faz `git commit + push` automaticamente

**Gatilhos naturais** — você fala normalmente, ele classifica:

| O que você diz | Onde vai |
|----------------|----------|
| *"tive uma ideia sobre X"* | `3-Resources/ideas/` |
| *"call com João hoje, decidimos Y"* | `Meetings/` |
| *"hoje foi um dia pesado"* | `Journal/` |
| *"preciso fazer X"* | `0-Inbox/Inbox.md` com `- [ ]` |
| Qualquer coisa solta | `0-Inbox/Inbox.md` |

**Áudio:** manda o áudio no Telegram → Cabeção transcreve (Groq) → classifica → salva → confirma onde foi.

---

## Crons configurados

| Horário | O que faz |
|---------|-----------|
| **8h (BRT)** | Briefing matinal: clima, tarefas do vault, intenção do dia |
| **21h (BRT)** | Check-in noturno: como foi o dia, cria/atualiza `Journal/YYYY-MM-DD.md` |
| **Domingo 10h (BRT)** | Revisão semanal: compila journal + meetings, gera `Journal/weekly/` |
| **A cada 15 min** | `git push` do vault para GitHub (cron do sistema) |

---

## Khoj (RAG)

**O que é:** indexa todos os `.md` do vault e permite ao Cabeção buscar contexto antes de responder. Quanto mais notas no vault, mais útil.

**Config:**
- URL interna: `http://localhost:42110` (só acessível na VPS)
- Admin: `admin@cabecao.local` / `cabecao2026`
- API token: `9993a591-3d74-4ae0-9c70-afc4c1df5a17`
- Modelo: `claude-sonnet-4-5-20250929` (Anthropic)
- Data source: `/vault/**/*.md` (reindexação automática)

**Acessar a UI (quando precisar):**
```bash
ssh -p 22022 -L 42110:localhost:42110 root@129.121.36.52
# Depois abre http://localhost:42110 no navegador
```

---

## Obsidian no Mac

1. Abrir o Obsidian → **Open folder as vault** → selecionar `~/Documents/cabecao/vault`
2. Instalar plugin **Obsidian Git**: faz pull/push automático do repo
3. Vault fica sincronizado com a VPS via GitHub (cron pusha a cada 15min, Mac faz pull/push pelo plugin)

---

## Segurança

- SSH: só chave Ed25519, sem senha, porta 22022
- `ufw`: default deny, só porta 22022 aberta externamente
- Docker: `iptables: false` (não burla ufw)
- Khoj: bind em `127.0.0.1:42110` (invisível externamente)
- Fail2ban: 3 tentativas → ban 1h
- Telegram: `dmPolicy: pairing`, só user ID `156600487` permitido
- Secrets: arquivos `chmod 600`, fora do vault, fora do repo

---

## Custos mensais

| Item | Custo |
|------|-------|
| VPS HostGator | ~US$ 20–40 |
| Claude API (OpenClaw + Khoj) | ~US$ 15–25 |
| Groq (transcrição de áudio) | ~US$ 0–2 |
| **Total** | **~US$ 35–67** |

---

## Estrutura do repositório

```
cabecao/
├── README.md                        ← este arquivo (visão geral + referência rápida)
├── stack-spec.md                    ← spec técnica original completa (v2.1)
├── vault/                           ← vault Obsidian (sincronizado com VPS via Git)
│   ├── PERSONALITY.md               ← perfil do Diego + como o Cabeção se comporta
│   ├── TOOLS.md                     ← instruções de onde/como salvar no vault
│   ├── HEARTBEAT.md                 ← automações periódicas do agente
│   └── ...                          ← notas, journal, meetings, etc.
├── config/
│   └── openclaw-vault.example.yaml  ← exemplo de config OpenClaw
├── docs/
│   ├── status-deploy.md             ← histórico do deploy
│   ├── implementacao-vps.md
│   ├── proximos-passos.md
│   └── sync-vault.md
└── scripts/
    ├── save-note.sh                 ← salva nota no vault + git push (usado pelo agente)
    ├── bootstrap-vault.sh           ← cria estrutura inicial do vault na VPS
    ├── vps-cabecao-git-push.sh      ← cron: commit + push do repo completo
    └── vps-vault-git-push.sh        ← cron: commit + push só do vault
```

---

## Comandos úteis

```bash
# Acessar a VPS
ssh cabecao

# Status dos serviços
systemctl --user status openclaw-gateway.service
cd /root/khoj && docker compose ps

# Reiniciar OpenClaw (após mudanças no vault)
systemctl --user restart openclaw-gateway.service

# Forçar reindexação do Khoj
curl -H "Authorization: Bearer 9993a591-3d74-4ae0-9c70-afc4c1df5a17" \
  "http://localhost:42110/api/update?force=true&t=markdown"

# Ver logs do OpenClaw
journalctl --user -u openclaw-gateway.service -f

# Ver logs do Khoj
cd /root/khoj && docker compose logs -f khoj

# Salvar nota manualmente (teste)
bash /opt/cabecao/scripts/save-note.sh inbox "0-Inbox/Inbox.md" \
  "## $(date '+%Y-%m-%d %H:%M')\nTeste manual\n#teste"
```

---

## Troubleshooting

| Problema | O que verificar / fazer |
|----------|------------------------|
| Bot não responde | `systemctl --user status openclaw-gateway.service` → reiniciar se parado |
| Khoj não acha notas | `cd /root/khoj && docker compose ps` → se parado, `docker compose up -d` |
| Vault não sincroniza | `cat /root/cabecao-sync.log` → ver erros do cron |
| Nota não foi salva | `chmod +x /opt/cabecao/scripts/save-note.sh` → testar manualmente |
| API key expirou | Atualizar em `auth-profiles.json` e `env.conf` (ver paths acima) → reiniciar OpenClaw |
| Khoj sem modelo | Acessar UI via SSH tunnel → Settings → AI Models → verificar Anthropic |
