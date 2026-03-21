# Implantação — economia de API (Cabeção)

Plano operacional para **Haiku como padrão**, **Sonnet sob demanda**, **Khoj mais barato**, **crons enxutos** — sem trocar Khoj, OpenClaw nem arquitetura.

**Onde aplicar:** na VPS (Khoj + OpenClaw). **Repo:** `git pull` em `/opt/cabecao` depois de merge deste guia no GitHub.

---

## 1. Atualizar o vault na VPS

```bash
cd /opt/cabecao && git pull
```

Confirme que `vault/PERSONALITY.md` e `vault/HEARTBEAT.md` trazem as regras de eficiência. Reinicie o gateway OpenClaw para recarregar skills se necessário:

```bash
systemctl --user restart openclaw-gateway.service
```

---

## 2. Khoj — modelo de chat: Haiku

1. Túnel SSH se o Khoj só escuta em localhost:  
   `ssh -p 22022 -L 42110:localhost:42110 root@SEU_IP`
2. Abra `http://localhost:42110` → login admin.
3. **Settings → AI / Models** (ou equivalente na sua versão).
4. Defina o modelo de **chat / resposta** para **Claude Haiku** (família 4.5 ou a versão listada como Haiku na Anthropic).
5. **IDs de referência (Anthropic):** use o ID exibido no console Anthropic ou no seletor do Khoj — em geral algo como `claude-haiku-4-5-20251001` ou alias `claude-haiku-4-5`. O Sonnet pode continuar cadastrado como opção secundária na UI, se existir.

**Objetivo:** o RAG continua igual; só a **síntese** passa a custar menos.

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

## 6. Duplicação de persona (workspace OpenClaw)

Se existir **o mesmo perfil** em `~/.openclaw/workspace/SOUL.md` / `USER.md` **e** em `vault/PERSONALITY.md`, o contexto pode duplicar. Escolha **uma** fonte canônica para biografia longa (recomendado: **só o vault**) e deixe o workspace só com remissões curtas ou links.

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
