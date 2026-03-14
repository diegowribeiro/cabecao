# TOOLS — Cabeção (OpenClaw)

Instruções para o agente sobre onde e como gravar conteúdo no vault.

---

## Obsidian Vault

Vault em: na VPS com repo cabecao clonado em `/opt/cabecao` use **`/opt/cabecao/vault`**. Se usou bootstrap em pasta separada: **`/var/lib/obsidian-vault`**. No Mac/local: path da pasta `vault/` do clone do repo.

### Estrutura

| Pasta / arquivo | Uso |
|-----------------|-----|
| `0-Inbox/Inbox.md` | Pensamentos rápidos e áudios classificados como **inbox**. Append com timestamp. |
| `1-Projects/` | Projetos ativos. Tasks podem ficar aqui ou no Inbox com `- [ ]`. |
| `2-Areas/` | Saúde, Finanças, Carreira, Relacionamentos. |
| `Meetings/` | Reuniões: `YYYY-MM-DD-titulo.md`. Template: Contexto, Resumo, Decisões, Action Items. |
| `Journal/` | Diário: `YYYY-MM-DD.md`. Seção "Áudio Telegram" ou "Voice" quando for áudio. |
| `Journal/weekly/` | Revisões semanais: `YYYY-Www.md`. |
| `People/` | Notas sobre pessoas. |
| `3-Resources/ideas/` | Ideias para projeto/área: `YYYY-MM-DD-descricao.md`. |

### Regras de gravação

1. **Áudios do Telegram:** classificar em `inbox` | `meeting` | `journal` | `task` | `idea` e salvar no destino correto (ver PERSONALITY.md e stack-spec em `_config/`).
2. **Frontmatter:** sempre YAML com `date`, `tags`, `type` quando aplicável, `source: telegram` para conteúdo vindo do Telegram.
3. **Wikilinks:** usar `[[nome]]` para pessoas e projetos quando identificáveis.
4. **Inbox (append):** cada entrada com `## YYYY-MM-DD HH:mm` e o texto; no final, linha com `#tag1 #tag2` quando aplicável.
5. **Meetings:** um arquivo por reunião; frontmatter com `date`, `type: meeting`, `participants`, `tags`.
6. **Journal:** um arquivo por dia; criar ou fazer append na seção apropriada; opcionalmente `mood` e `energy` no frontmatter.
7. **Tasks:** em arquivos de projeto/área ou em Inbox com `- [ ]` e tags.
