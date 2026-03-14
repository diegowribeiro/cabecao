# SPEC DE IMPLEMENTAÇÃO — Personal AI Stack v2.1

## Assistente Pessoal com RAG sobre o "Eu" · 100% em VPS (HostGator)

**Versão:** 2.1  
**Data:** 2026-02-16  
**Mudanças vs v2.0:** (1) Toda a stack em VPS HostGator — nada local no Mac. (2) Transcrição de áudio via **Groq** (custo-benefício). (3) Pipeline de áudio completo: Telegram → transcrição → classificação pela IA → categorização e armazenamento no vault.

---

## 1. DECISÕES ARQUITETURAIS

### 1.1 Hosting: tudo na VPS HostGator

- **OpenClaw**, **Khoj** (Docker) e **vault Obsidian** rodam na VPS.
- Nada de agentes ou serviços da stack rodando no Mac (apenas uso de cliente: Telegram, Obsidian opcional no Mac via sync).
- **Requisitos VPS:** root SSH, Node.js 22+, Docker, ~2 GB RAM mínimo, 20 GB disco. Preferir VPS com Ubuntu para instalação simples do Docker.

### 1.2 LLM: Claude API para raciocínio e RAG

- **OpenClaw** e **Khoj** usam **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) via API Anthropic.
- Uma API key Anthropic para toda a stack (exceto transcrição de áudio; ver abaixo).

### 1.3 Transcrição de áudio: Groq (melhor custo-benefício)

- A **API Claude não aceita áudio**; transcrição é feita por outro serviço.
- **Escolha:** **Groq** (Whisper Large v3 Turbo).
  - **Custo:** free tier generoso; pago ~US$ 0,04 por hora transcrita.
  - **Uso típico:** vários áudios curtos no Telegram por dia (ex.: 5–15 min/dia) = centavos por mês.
  - **Vantagens:** rápido, multilíngue (PT/EN), sem GPU na VPS, uma conta só para áudio.
- **Configuração:** OpenClaw na VPS com `tools.media.audio` usando `provider: "groq"`. Sem Whisper local.

### 1.4 Componentes e custos (mensal)

| Componente | Onde roda | Custo/mês |
|------------|-----------|-----------|
| VPS HostGator | HostGator | ~US$ 20–40 (conforme plano) |
| Reuniões online | Granola no Mac → envio para VPS (sync ou Telegram) | US$ 18 |
| Áudio (Telegram, etc.) | OpenClaw na VPS → Groq | ~US$ 0–2 (free tier / pouco uso) |
| RAG / segundo cérebro | Khoj (Docker na VPS) | US$ 0 |
| Agente executor | OpenClaw (VPS) | US$ 0 |
| LLM (raciocínio + RAG) | Claude API | ~US$ 15–25 |
| **TOTAL** | | **~US$ 53–85** |

---

## 2. FLUXO DE DADOS GERAL

```
[Telegram: áudio/texto] ──────────────┐
[Granola: MD export → sync para VPS] ─┤
[Voice Memos: enviar áudio no Telegram] ─┼──→ [VAULT na VPS] ←→ [Khoj RAG]
                                         │           ↑
                                         └──→ [OpenClaw] ←──┘
                                              · Transcreve (Groq)
                                              · Classifica (Claude)
                                              · Salva no vault
                                              · Responde no Telegram
```

- **Vault:** diretório na VPS (ex.: `/var/lib/openclaw/vault` ou `/home/user/ObsidianVault`). Pode ser versionado com Git (repo privado) e, opcionalmente, sincronizado para o Mac para edição no Obsidian.
- **Entrada principal de áudio:** Telegram (ideias, reuniões presenciais gravadas no celular, check-in diário). Granola continua no Mac; o resultado (MD) chega à VPS por sync (Syncthing/rclone) ou por upload/cópia.

---

## 3. PIPELINE DE ÁUDIO: TELEGRAM → SISTEMA

### 3.1 Visão do fluxo

1. **Usuário envia áudio no Telegram** (ou áudio + legenda, ex.: “reunião com João”).
2. **OpenClaw (VPS)** recebe o áudio.
3. **Transcrição:** OpenClaw envia o áudio para **Groq** (Whisper Large v3 Turbo); recebe texto.
4. **Classificação:** o agente (Claude) analisa o texto (e a legenda, se houver) e decide: **tipo** (inbox, meeting, journal, task, idea) e **metadados** (tags, data, pessoas).
5. **Armazenamento:** o agente grava no vault no caminho e formato corretos (frontmatter + corpo).
6. **Resposta:** OpenClaw confirma no Telegram (ex.: “Anotado em Meetings/ como reunião com João”).

### 3.2 Tipos de conteúdo e onde salvar

| Tipo | Descrição | Destino no vault | Frontmatter mínimo |
|------|-----------|------------------|---------------------|
| **inbox** | Pensamento rápido, ideia solta, lembrete | `0-Inbox/Inbox.md` (append com timestamp) | — |
| **idea** | Ideia para projeto/área | `0-Inbox/Inbox.md` ou `3-Resources/ideas/YYYY-MM-DD-descricao.md` | `type: idea`, `tags` |
| **meeting** | Reunião (presencial ou resumo) | `Meetings/YYYY-MM-DD-titulo.md` | `date`, `type: meeting`, `participants`, `tags` |
| **journal** | Reflexão, humor, como estou | `Journal/YYYY-MM-DD.md` (append ou criar) | `date`, `mood`, `energy`, `tags` |
| **task** | Tarefa ou action item | `1-Projects/` ou `2-Areas/` + arquivo apropriado; ou append em `0-Inbox/Inbox.md` com `- [ ]` | `type: task`, `date` |

### 3.3 Regras de classificação (para o agente)

- **Legenda do áudio:** se o usuário mandar texto junto (ex.: “reunião com João”, “ideia projeto X”), usar como sinal forte para `type` e título.
- **Palavras-chave no texto transcrito:** “reunião”, “reunião com”, “reunião com [nome]” → `meeting`. “Tarefa”, “preciso”, “action” → `task`. “Como estou”, “hoje me senti”, “reflexão” → `journal`. Caso contrário → `inbox` ou `idea`.
- **Horário:** áudios em horário típico de check-in (ex.: noite) podem ser sugeridos como `journal` se o conteúdo for reflexivo.
- **Sempre:** adicionar `source: telegram` e `date` (e hora quando fizer sentido) no frontmatter; usar `[[wikilinks]]` para pessoas/projetos quando identificáveis.

### 3.4 Formato de armazenamento

- **Inbox (append):** cada entrada com `## YYYY-MM-DD HH:mm` e o texto; no final, linha com `#tag1 #tag2` quando aplicável.
- **Meetings/:** um arquivo por reunião, template com Contexto, Resumo (transcrição ou resumo), Decisões, Action Items.
- **Journal:** um arquivo por dia; seção “Áudio Telegram” ou “Voice” com o texto e opcionalmente `mood`/`energy` no frontmatter.
- **Tasks:** em arquivos de projeto/área ou em Inbox com `- [ ]` e tags.

---

## 4. FASE 1 — VAULT E ESTRUTURA NA VPS (Semana 1–2)

### 4.1 Criar vault na VPS

```bash
# Na VPS (SSH)
sudo mkdir -p /var/lib/obsidian-vault   # ou /home/SEU_USER/ObsidianVault
sudo chown $USER:$USER /var/lib/obsidian-vault
cd /var/lib/obsidian-vault

mkdir -p 0-Inbox 1-Projects 2-Areas 3-Resources 4-Archive
mkdir -p Meetings/templates Journal/weekly People
mkdir -p _config _templates
mkdir -p 2-Areas/Saude 2-Areas/Financas 2-Areas/Carreira 2-Areas/Relacionamentos
```

### 4.2 Templates (opcional; mesmo conteúdo da spec v2.0)

- `_templates/daily-note.md`, `_templates/meeting-note.md`, `_templates/weekly-review.md` — conforme spec original (date, mood, energy, tags, etc.).

### 4.3 Git no vault (recomendado)

```bash
cd /var/lib/obsidian-vault
git init
echo ".obsidian/workspace.json" >> .gitignore
echo ".obsidian/workspace-mobile.json" >> .gitignore
echo ".trash/" >> .gitignore
git add .
git commit -m "Initial vault structure"
git remote add origin git@github.com:SEU_USUARIO/obsidian-vault.git   # REPO PRIVADO
git push -u origin main
```

- Cron na VPS para commit/push periódico (ex.: a cada 1h) ou uso de Obsidian Git no Mac se sincronizar o vault para lá.

### 4.4 Granola (Mac) → VPS

- **Opção A — Syncthing:** no Mac, pasta de export do Granola = uma pasta sincronizada com a VPS (ex.: `Meetings/` na VPS). Granola exporta para essa pasta no Mac; Syncthing replica para a VPS.
- **Opção B — Manual/script:** export do Granola para uma pasta; script na VPS que baixa de um cloud (ex.: Dropbox/Google Drive via rclone) para `Meetings/`.
- **Opção C — Só Telegram:** para reuniões online, enviar áudio ou resumo por Telegram; OpenClaw classifica como `meeting` e salva (menos automático que Granola).

---

## 5. FASE 2 — KHOJ NA VPS (Semana 3–4)

### 5.1 Docker + Khoj na VPS

```bash
# VPS: instalar Docker (Ubuntu)
sudo apt update && sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker && sudo systemctl start docker

# Khoj
mkdir -p ~/khoj && cd ~/khoj
curl -sSL -o docker-compose.yml https://raw.githubusercontent.com/khoj-ai/khoj/master/docker-compose.yml
# Ajustar no docker-compose: volume para o vault da VPS, ex.:
# volumes: - /var/lib/obsidian-vault:/path/inside/container
docker compose up -d
curl http://localhost:42110/
```

### 5.2 Configurar Khoj

- Admin: criar conta, em **Content** apontar para o path do vault na VPS; tipos Markdown; reindexação automática (ex.: 30 min).
- **Model:** Anthropic, API key, modelo `claude-sonnet-4-5-20250929`.
- Plugin Obsidian (no Mac, se usar sync do vault): URL do Khoj = `http://IP_DA_VPS:42110` ou domínio reverso (ex.: `khoj.seudominio.com`) com proxy reverso.

### 5.3 Agente “Mentor Pessoal”

- Criar agente no Khoj com system prompt (conselheiro, padrões, citações do vault, português). Knowledge base = vault; tools = web search + file access.

---

## 6. FASE 3 — OPENCLAW NA VPS (Semana 5–6)

### 6.1 Instalar OpenClaw na VPS

```bash
# VPS
curl -fsSL https://openclaw.ai/install.sh | bash
# No wizard: modelo Claude Sonnet 4.5, ANTHROPIC_API_KEY, canal Telegram, skill obsidian
```

### 6.2 Variáveis de ambiente (transcrição + LLM)

```bash
# /etc/environment ou ~/.bashrc / systemd service
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk_..."   # https://console.groq.com
```

### 6.3 Configuração de áudio (Groq) e gateway

No config do OpenClaw (ex.: `~/.openclaw/config.yaml` ou JSON equivalente):

```yaml
# Transcrição: Groq (melhor custo-benefício, sem GPU)
tools:
  media:
    audio:
      enabled: true
      maxBytes: 20971520   # 20 MB
      timeoutSeconds: 120
      models:
        - provider: groq
          model: whisper-large-v3-turbo   # multilíngue, ~US$ 0,04/h
```

Telegram (exemplo):

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

### 6.4 TOOLS.md (vault na VPS)

Caminho do vault deve ser o path **na VPS**, ex.:

```markdown
## Obsidian Vault

Vault em: /var/lib/obsidian-vault

Estrutura:
- 0-Inbox/Inbox.md — pensamentos rápidos e áudios classificados como inbox
- 1-Projects/ — projetos ativos
- 2-Areas/ — Saúde, Finanças, Carreira, Relacionamentos
- Meetings/ — reuniões (YYYY-MM-DD-titulo.md)
- Journal/ — diário (YYYY-MM-DD.md)
- Journal/weekly/ — revisões semanais
- People/ — notas sobre pessoas

Regras:
- Áudios do Telegram: classificar em inbox | meeting | journal | task | idea e salvar no destino correto.
- Sempre frontmatter YAML com date, tags, type, source: telegram quando aplicável.
- Usar [[wikilinks]] para pessoas e projetos.
- Reuniões: Meetings/YYYY-MM-DD-titulo.md. Pensamentos rápidos: append em 0-Inbox/Inbox.md com ## YYYY-MM-DD HH:mm.
```

### 6.5 PERSONALITY.md

Incluir instruções para: (1) sempre transcrever áudios (Groq já configurado); (2) classificar conforme as regras da seção 3; (3) salvar no vault com o formato definido; (4) responder em português e confirmar onde foi salvo.

### 6.6 Cron (horários fixos)

```bash
# Briefing 8h (America/Sao_Paulo)
openclaw cron add --name "Briefing 8h" --cron "0 8 * * *" --session isolated --message "Briefing matinal: calendário, tarefas do vault, clima SP."

# Check-in noturno 21h
openclaw cron add --name "Check-in 21h" --cron "0 21 * * *" --session isolated --message "Check-in noturno: como foi o dia? Highlights e como está se sentindo. Se responder, criar/atualizar Journal/YYYY-MM-DD.md."

# Revisão semanal domingo 10h
openclaw cron add --name "Revisão semanal" --cron "0 10 * * 0" --session isolated --message "Revisão semanal: compilar Journal e Meetings da semana, gerar Journal/weekly/YYYY-Www.md, enviar resumo no Telegram."
```

### 6.7 HEARTBEAT.md (tarefas a cada 30 min)

Conteúdo sugerido:

```markdown
## Automações a cada 30 min

1. Verificar se há novos arquivos em Meetings/ (ex.: export do Granola via sync). Se houver, enriquecer com action items se faltando e notificar no Telegram.
2. (Opcional) Verificar outra pasta de sync para Voice Memos se no futuro houver upload automático para a VPS.
3. Responder HEARTBEAT_OK se não houver nada a fazer.
```

---

## 7. SEGURANÇA

- Repositório Git do vault: **privado**.
- API keys (Anthropic, Groq) em variável de ambiente na VPS; nunca no vault.
- Telegram: 2FA ativado; bot com `allowedUsers` ou `dmPolicy: pairing` para evitar uso por terceiros.
- Khoj e OpenClaw: em rede privada ou atrás de firewall; expor Khoj só por HTTPS (proxy reverso) se acessar do Mac.
- Granola: opt-out de model training ativado.

---

## 8. CUSTOS DETALHADOS (v2.1)

| Item | Custo/mês |
|------|-----------|
| VPS HostGator | ~US$ 20–40 |
| Granola Individual | US$ 18 |
| Claude API (OpenClaw + Khoj) | ~US$ 15–25 |
| Groq (transcrição) | ~US$ 0–2 (free tier / pouco uso) |
| **TOTAL** | **~US$ 53–85** |

---

## 9. CHECKLIST DE VALIDAÇÃO

### Fase 1 — Vault na VPS
- [ ] Vault criado na VPS com estrutura de pastas
- [ ] Templates e Git (repo privado) configurados
- [ ] Granola no Mac + fluxo para VPS (Syncthing ou outro) definido e testado

### Fase 2 — Khoj
- [ ] Docker rodando na VPS; Khoj acessível (localhost e/ou domínio)
- [ ] Vault indexado; Claude API configurada no Khoj
- [ ] Agente Mentor criado e testado

### Fase 3 — OpenClaw
- [ ] OpenClaw rodando na VPS; Claude Sonnet 4.5 configurado
- [ ] **Groq** configurado em `tools.media.audio` (transcrição)
- [ ] Telegram bot pareado; TOOLS.md e PERSONALITY.md com regras de classificação
- [ ] Cron: briefing 8h, check-in 21h, revisão domingo
- [ ] HEARTBEAT.md ativo
- [ ] Teste: áudio no Telegram → transcrição Groq → classificação → salvo no vault → resposta no Telegram

### Pipeline de áudio
- [ ] Áudio Telegram → transcrição em PT/EN correta
- [ ] Classificação (inbox/meeting/journal/task/idea) coerente
- [ ] Armazenamento no path e formato corretos (frontmatter, wikilinks)
- [ ] Khoj encontra o conteúdo novo após reindexação

---

*Spec oficial v2.1. Manter cópia em `_config/stack-spec.md` no vault. Última atualização: 2026-02-16.*
