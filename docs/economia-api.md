# Implantação — economia de API (Cabeção)

Plano operacional para **Haiku como padrão**, **Sonnet sob demanda**, **Khoj mais barato**, **crons enxutos** — sem trocar Khoj, OpenClaw nem arquitetura.

**Onde aplicar:** na VPS (Khoj + OpenClaw). **Repo:** `git pull` em `/opt/cabecao` depois de merge deste guia no GitHub.

---

## 1. Atualizar o vault na VPS

```bash
cd /opt/cabecao && git pull
```

Confirme que `vault/PERSONALITY.md` e `vault/HEARTBEAT.md` trazem as regras de eficiência.

**`save-note.sh` e Khoj:** na VPS, defina **`KHOJ_UPDATE_TOKEN`** (mesmo valor do token de API do Khoj) no ambiente do processo que executa o agente — ex. em `/root/.config/systemd/user/openclaw-gateway.service.d/env.conf`:

```ini
Environment="KHOJ_UPDATE_TOKEN=o_token_gerado_no_khoj"
```

Depois: `systemctl --user daemon-reload && systemctl --user restart openclaw-gateway.service`.

Reinicie o gateway OpenClaw após mudanças no vault se necessário:

```bash
systemctl --user restart openclaw-gateway.service
```

---

## 2. Khoj — modelo de chat: Haiku (**opcional / pausado**)

Pode manter **Sonnet no Khoj** por enquanto; Haiku aqui é só economia na síntese do RAG, não muda arquitetura.

Quando quiser ativar:

1. Túnel SSH se o Khoj só escuta em localhost:  
   `ssh -p 22022 -L 42110:localhost:42110 root@SEU_IP`
2. Abra `http://localhost:42110` → login admin.
3. **Settings → AI / Models** (ou equivalente na sua versão).
4. Defina o modelo de **chat / resposta** para **Claude Haiku**.
5. **IDs de referência (Anthropic):** use o ID do seletor do Khoj — em geral `claude-haiku-4-5` ou sufixo datado.

**Objetivo:** RAG igual; só a **síntese** mais barata.

---

## 3. OpenClaw — modelo principal Haiku, Sonnet no `/model`

### 3.1 Via CLI (recomendado)

Na VPS, com o mesmo usuário que roda o gateway:

```bash
openclaw models list --all --provider anthropic
openclaw models set anthropic/claude-haiku-4-5
```

Se o ID exato for outro (ex. sufixo de data), use o ref que aparecer em `models list`.

Garanta que **Sonnet** continue **allowlist** para o Diego poder alternar:

```bash
openclaw models status
```

Se Sonnet sumir da lista, adicione no catálogo editando `~/.openclaw/openclaw.json` (ou o path que `openclaw doctor` indicar), conforme [Models CLI](https://docs.openclaw.ai/concepts/models):

- `agents.defaults.model.primary` → `anthropic/claude-haiku-4-5` (ou ID listado pelo CLI).
- `agents.defaults.models` → incluir entradas para Haiku **e** Sonnet (ex. `anthropic/claude-sonnet-4-5` ou `anthropic/claude-sonnet-4-6`, alinhado ao que `openclaw models list` mostrar), cada uma com `alias` curto.

**Uso no Telegram:** Diego envia `/model` → escolhe **Sonnet** para tarefa pesada → volta com `/model` para **Haiku**.

### 3.2 Fallbacks

Para **economia**, não coloque Sonnet como fallback automático do Haiku (fallbacks são para falha de API/latência). Deixe fallbacks vazios ou só outro modelo barato, se um dia configurar.

---

## 4. Crons — mensagens curtas (recriar se já existirem)

Menos tokens na instrução = menos custo por disparo. Remova crons antigos e recrie com texto mínimo:

```bash
openclaw cron list
# openclaw cron remove --name "Briefing 8h"   # se os nomes baterem

openclaw cron add --name "Briefing 8h" --cron "0 8 * * *" --session isolated \
  --message "Briefing: clima SP, tarefas abertas no vault (Inbox), uma pergunta de intenção do dia. Curto."

openclaw cron add --name "Check-in 21h" --cron "0 21 * * *" --session isolated \
  --message "Check-in: como foi o dia? Um highlight e humor. Se responder, atualizar Journal/ hoje."

openclaw cron add --name "Revisão semanal" --cron "0 10 * * 0" --session isolated \
  --message "Revisão semanal: resumir Journal + Meetings da semana, criar Journal/weekly/YYYY-Www.md se faltar, Telegram só com bullets."
```

Ajuste timezone (`timedatectl` / variáveis do OpenClaw) se precisar de BRT.

---

## 5. Heartbeat

- Se o heartbeat de **30 min** estiver gerando muitas chamadas ao modelo, aumente o intervalo na configuração do gateway (ou reduza trabalho no prompt) — prioridade: **sem RAG** e **sem texto longo** quando só houver `HEARTBEAT_OK`.
- Ver `vault/HEARTBEAT.md` no repo.

---

## 6. Persona — uma fonte (`PERSONALITY.md`) + workspace mínimo

**Problema:** `SOUL.md` e `USER.md` grandes no `~/.openclaw/workspace/` repetem o que já está em `vault/PERSONALITY.md` → mais tokens sem ganho.

**Solução no repo:** versões **enxutas** em `config/openclaw-workspace/SOUL.md` e `USER.md` (apontam para o vault). O conteúdo que estava só no SOUL antigo (**modo crise**, **inglês integrado**) foi incorporado em `vault/PERSONALITY.md`.

**Na VPS (depois de `git pull`):**

```bash
cd /opt/cabecao && git pull
TS=$(date +%Y%m%d%H%M%S)
cp -a ~/.openclaw/workspace/SOUL.md ~/.openclaw/workspace/SOUL.md.bak.$TS
cp -a ~/.openclaw/workspace/USER.md ~/.openclaw/workspace/USER.md.bak.$TS
cp /opt/cabecao/config/openclaw-workspace/SOUL.md ~/.openclaw/workspace/SOUL.md
cp /opt/cabecao/config/openclaw-workspace/USER.md ~/.openclaw/workspace/USER.md
systemctl --user restart openclaw-gateway.service
```

Recuperar backup se precisar: `cp ~/.openclaw/workspace/SOUL.md.bak.XXXX SOUL.md`.

---

## 7. Checklist final

- [ ] `git pull` em `/opt/cabecao`; vault atualizado.
- [ ] Khoj: chat model = **Haiku**.
- [ ] OpenClaw: primary = **Haiku**; Sonnet acessível via `/model`.
- [ ] Crons recriados com mensagens curtas.
- [ ] Heartbeat revisado (frequência / custo).
- [ ] Opcional: console Anthropic → uso por modelo (Haiku ↑, Sonnet só quando necessário).

---

## Referências

- OpenClaw — [Models CLI](https://docs.openclaw.ai/concepts/models), [Configuration](https://docs.openclaw.ai/configuration)
- Anthropic — IDs atuais no [docs de modelos](https://docs.anthropic.com/en/docs/about-claude/models)
