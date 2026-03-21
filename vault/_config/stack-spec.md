# SPEC DE IMPLEMENTAÇÃO — Personal AI Stack v2.1

> **Histórico v2.1.** Estado atual da stack: ver **`AGENTS.md`** na raiz do repo cabeção e **`docs/INDICE-DOCUMENTACAO.md`**.

---

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

1. **Usuário envia áudio no Telegram** (ou áudio + legenda, ex.: "reunião com João").
2. **OpenClaw (VPS)** recebe o áudio.
3. **Transcrição:** OpenClaw envia o áudio para **Groq** (Whisper Large v3 Turbo); recebe texto.
4. **Classificação:** o agente (Claude) analisa o texto (e a legenda, se houver) e decide: **tipo** (inbox, meeting, journal, task, idea) e **metadados** (tags, data, pessoas).
5. **Armazenamento:** o agente grava no vault no caminho e formato corretos (frontmatter + corpo).
6. **Resposta:** OpenClaw confirma no Telegram (ex.: "Anotado em Meetings/ como reunião com João").

### 3.2 Tipos de conteúdo e onde salvar

| Tipo | Descrição | Destino no vault | Frontmatter mínimo |
|------|-----------|------------------|---------------------|
| **inbox** | Pensamento rápido, ideia solta, lembrete | `0-Inbox/Inbox.md` (append com timestamp) | — |
| **idea** | Ideia para projeto/área | `0-Inbox/Inbox.md` ou `3-Resources/ideas/YYYY-MM-DD-descricao.md` | `type: idea`, `tags` |
| **meeting** | Reunião (presencial ou resumo) | `Meetings/YYYY-MM-DD-titulo.md` | `date`, `type: meeting`, `participants`, `tags` |
| **journal** | Reflexão, humor, como estou | `Journal/YYYY-MM-DD.md` (append ou criar) | `date`, `mood`, `energy`, `tags` |
| **task** | Tarefa ou action item | `1-Projects/` ou `2-Areas/` + arquivo apropriado; ou append em `0-Inbox/Inbox.md` com `- [ ]` | `type: task`, `date` |

### 3.3 Regras de classificação (para o agente)

- **Legenda do áudio:** se o usuário mandar texto junto (ex.: "reunião com João", "ideia projeto X"), usar como sinal forte para `type` e título.
- **Palavras-chave no texto transcrito:** "reunião", "reunião com", "reunião com [nome]" → `meeting`. "Tarefa", "preciso", "action" → `task`. "Como estou", "hoje me senti", "reflexão" → `journal`. Caso contrário → `inbox` ou `idea`.
- **Horário:** áudios em horário típico de check-in (ex.: noite) podem ser sugeridos como `journal` se o conteúdo for reflexivo.
- **Sempre:** adicionar `source: telegram` e `date` (e hora quando fizer sentido) no frontmatter; usar `[[wikilinks]]` para pessoas/projetos quando identificáveis.

### 3.4 Formato de armazenamento

- **Inbox (append):** cada entrada com `## YYYY-MM-DD HH:mm` e o texto; no final, linha com `#tag1 #tag2` quando aplicável.
- **Meetings/:** um arquivo por reunião, template com Contexto, Resumo (transcrição ou resumo), Decisões, Action Items.
- **Journal:** um arquivo por dia; seção "Áudio Telegram" ou "Voice" com o texto e opcionalmente `mood`/`energy` no frontmatter.
- **Tasks:** em arquivos de projeto/área ou em Inbox com `- [ ]` e tags.

---

*Spec oficial v2.1. Cópia no vault. Ver arquivo raiz do repo para versão completa com Fases 4–9 e checklist.*
