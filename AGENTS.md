# Cabeção — guia do repositório (humanos e IAs)

Leia este arquivo **antes** de alterar arquitetura, deploy ou comportamento do agente. Mantém o estado **atual** da stack; especificações antigas estão em `stack-spec.md` (histórico).

---

## 1. O que é este projeto

**Cabeção** é um assistente pessoal (OpenClaw + Telegram + vault Obsidian + Khoj RAG + Groq para áudio). O repositório **cabecao** contém o **vault** versionado, scripts da VPS e documentação.

- **Nome do projeto / bot:** contexto em `vault/PERSONALITY.md` e `README.md`.
- **Idioma do agente com o usuário:** português (ver `vault/PERSONALITY.md`).

---

## 2. Fonte da verdade (ordem de leitura)

| Prioridade | Arquivo | Conteúdo |
|------------|---------|----------|
| 1 | **Este `AGENTS.md`** | Arquitetura atual, paths, segredos, como evoluir. |
| 2 | `README.md` | Visão geral, tabela da stack, comandos rápidos. |
| 3 | `vault/PERSONALITY.md` | Persona longa do Cabeção; modo crise; inglês integrado; regras de eficiência. |
| 4 | `vault/TOOLS.md` | Onde salvar notas; uso de `save-note.sh`. |
| 5 | `vault/HEARTBEAT.md` | Automações periódicas esperadas. |
| 6 | `docs/implementacao-vps.md` | Instalação passo a passo na VPS. |
| 7 | `docs/economia-api.md` | Modelos (Haiku/Sonnet), custos, `KHOJ_UPDATE_TOKEN`, crons. |
| 8 | `docs/khoj-token-passo-a-passo.md` | Token Khoj + variável de ambiente na VPS. |
| 9 | `docs/status-deploy.md` | Snapshot do que foi deployado (atualizar quando mudar produção). |
| Histórico | `stack-spec.md`, `vault/_config/stack-spec.md` | Spec v2.1 (2026-02); **não** refletem todas as decisões atuais — ver § 12 abaixo. |

---

## 3. Arquitetura atual (resumo)

```
Telegram → OpenClaw (gateway systemd) → Claude (Haiku padrão; Sonnet via /model)
              ↓                              ↑
         Groq (Whisper) — áudio              Khoj RAG (localhost:42110)
              ↓
         /opt/cabecao/vault/*.md → git push → GitHub
              ↓
         save-note.sh → (opcional) POST Khoj reindex com KHOJ_UPDATE_TOKEN
```

- **Mac/iPhone:** clone do mesmo repo; Obsidian abre só `vault/` se desejado.
- **Khoj:** Docker na VPS; indexa markdown do vault; **não** substitui o OpenClaw — é segundo cérebro / busca.

---

## 4. Onde cada coisa roda

| Componente | Onde | Observação |
|------------|------|------------|
| OpenClaw Gateway | VPS, `systemctl --user` | Config: `~/.openclaw/openclaw.json` (usuário que roda o serviço). |
| Vault | `/opt/cabecao/vault` na VPS | Repo: pasta `vault/` neste git. |
| Khoj | Docker, ex. `/root/khoj` | API HTTP `127.0.0.1:42110` (não expor público). |
| Transcrição de áudio | Groq API | Chave em perfil de auth OpenClaw / env. |
| LLM (chat) | Anthropic API | Haiku padrão no agente; Sonnet no catálogo para `/model`. |

---

## 5. Modelos de IA (estado alinhado a março/2026)

- **OpenClaw:** primário **`anthropic/claude-haiku-4-5`**; **`anthropic/claude-sonnet-4-6`** (ou versão equivalente no `openclaw models list`) para tarefas pesadas via `/model`. Conferir na VPS: `openclaw models status`.
- **Khoj (chat/RAG):** configurável na UI do Khoj; **Haiku é opcional** para economia (ver `docs/economia-api.md`).
- **Áudio:** Groq — modelo Whisper compatível configurado no OpenClaw (`whisper-large-v3-turbo` típico).

Se a documentação antiga disser “só Sonnet em tudo”, está **desatualizada**.

---

## 6. Segredos (nunca commitar)

| Segredo | Onde configurar na VPS |
|---------|-------------------------|
| `ANTHROPIC_API_KEY` | `auth-profiles.json` / env do gateway (ver docs OpenClaw). |
| `GROQ_API_KEY` | Idem. |
| Token do bot Telegram | Arquivo tipo `/root/.telegram-bot-token` ou config OpenClaw (não no vault). |
| **`KHOJ_UPDATE_TOKEN`** | Token de API do Khoj para `scripts/save-note.sh` reindexar após cada nota. Ver **`docs/khoj-token-passo-a-passo.md`**. |
| Khoj DB / admin | `/root/khoj/.env` (chmod 600). |
| Garmin | `/root/.garmin-credentials` (chmod 600). |

O script `scripts/save-note.sh` **não** contém token fixo; usa a variável de ambiente `KHOJ_UPDATE_TOKEN`.

---

## 7. Paths importantes (VPS)

```
/opt/cabecao/                    clone deste repositório
/opt/cabecao/vault/              vault Obsidian
/opt/cabecao/scripts/save-note.sh   usado pelo agente (allowlist)
/root/.openclaw/openclaw.json    config principal OpenClaw
/root/.openclaw/workspace/       SOUL.md, USER.md (cópias mínimas em config/openclaw-workspace/)
/root/.config/systemd/user/openclaw-gateway.service.d/env.conf   env vars do gateway
/root/khoj/                      docker-compose Khoj
```

---

## 8. Arquivos que definem comportamento

| Arquivo | Função |
|---------|--------|
| `vault/PERSONALITY.md` | Persona, tom, modo crise, inglês integrado, áudio, eficiência de tokens. |
| `vault/TOOLS.md` | Contrato de gravação no vault + exemplos `save-note.sh`. |
| `config/openclaw-workspace/SOUL.md` | Núcleo; aponta para o vault (não duplicar biografia). |
| `config/openclaw-workspace/USER.md` | Identidade mínima do usuário. |
| `~/.openclaw/workspace/*` na VPS | Devem estar alinhados aos templates do `config/openclaw-workspace/` após deploy. |

---

## 9. Scripts relevantes

| Script | Uso |
|--------|-----|
| `scripts/save-note.sh` | Append/cria nota, `git commit` + `push` no vault; reindex Khoj se `KHOJ_UPDATE_TOKEN` definido. |
| `scripts/vps-cabecao-git-push.sh` | Cron: push periódico do vault. |
| `scripts/garmin-sync.py` | Sync Garmin → `vault/2-Areas/Saude/garmin/` (credenciais fora do repo). |

---

## 10. O que atualizar quando mudar algo

| Mudança | Atualizar |
|---------|-----------|
| Novo serviço / path | `AGENTS.md`, `README.md`, `docs/status-deploy.md` |
| Novo segredo | `docs/khoj-token-passo-a-passo.md` ou seção 6 deste arquivo; **nunca** o valor em texto puro no git |
| Comportamento do agente | `vault/PERSONALITY.md`, `vault/TOOLS.md` |
| Decisão de modelo/custo | `docs/economia-api.md` |
| Deploy ponta a ponta | `docs/implementacao-vps.md` |

---

## 11. Troubleshooting (IA / dev)

- Bot parado: `systemctl --user status openclaw-gateway.service` na VPS.
- Khoj sem índice novo após nota: checar `KHOJ_UPDATE_TOKEN` no ambiente do **mesmo processo** que executa o agente (gateway).
- RAG desatualizado: curl manual em `docs/economia-api.md` ou reindex na UI Khoj.
- Conflitos git no vault: resolver no clone como qualquer repo; priorizar não perder notas.

---

## 12. Documentação histórica (`stack-spec.md`)

Os arquivos `stack-spec.md` e `vault/_config/stack-spec.md` descrevem a **Personal AI Stack v2.1** (fevereiro/2026): úteis para contexto e decisões originais (Groq, fluxo de áudio, custos aproximados).

**Divergências conhecidas em relação à produção atual:**

- Especificavam **Sonnet** como modelo único para OpenClaw e Khoj; hoje o padrão do OpenClaw é **Haiku** com **Sonnet** opcional.
- Caminhos de exemplo (`/var/lib/...`) podem diferir do padrão real **`/opt/cabecao/vault`**.
- Crons e integrações (Garmin, crons extra) evoluíram após a spec.

**Regra:** para implementar ou corrigir algo hoje, use **`AGENTS.md`** + **`docs/status-deploy.md`**; use **`stack-spec.md`** como referência histórica ou para recuperar intenção de design.

---

## 13. Como manter este guia

Sempre que uma IA ou pessoa alterar modelo, paths, segredos ou fluxos, **atualize `AGENTS.md`** e, se aplicável, **`docs/status-deploy.md`** no mesmo PR/commit. Assim o próximo contexto fica coerente.
