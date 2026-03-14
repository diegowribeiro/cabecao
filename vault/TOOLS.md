# TOOLS — Cabeção (OpenClaw)

Instruções para o agente sobre onde e como gravar conteúdo no vault.

---

## Vault

**Path na VPS:** `/opt/cabecao/vault`

### Estrutura

| Pasta / arquivo | Uso |
|-----------------|-----|
| `0-Inbox/Inbox.md` | Pensamentos rápidos, áudios inbox, tasks rápidas. **Sempre append com timestamp.** |
| `1-Projects/` | Projetos ativos. |
| `2-Areas/Saude/` | Saúde, treinos, alimentação, exames. |
| `2-Areas/Financas/` | Finanças, investimentos, metas financeiras. |
| `2-Areas/Carreira/` | Carreira, trabalho, liderança, desenvolvimento profissional. |
| `2-Areas/Relacionamentos/` | Família, amizades, relacionamento com a esposa, filhos. |
| `3-Resources/ideas/` | Ideias elaboradas: `YYYY-MM-DD-titulo.md`. |
| `4-Archive/` | Projetos concluídos ou pausados. |
| `Meetings/` | Reuniões: `YYYY-MM-DD-titulo.md`. |
| `Journal/` | Diário: `YYYY-MM-DD.md`. Criar ou fazer append. |
| `Journal/weekly/` | Revisões semanais: `YYYY-Www.md`. |
| `People/` | Notas sobre pessoas. |

---

## Como salvar — use o script

**Script:** `/opt/cabecao/scripts/save-note.sh`
**Assinatura:** `bash /opt/cabecao/scripts/save-note.sh <tipo> <caminho-relativo> "<conteudo>"`

O script faz append (inbox/journal/task) ou cria arquivo (meeting/idea) + git commit + push automático.

### Inbox (append)
```bash
bash /opt/cabecao/scripts/save-note.sh inbox "0-Inbox/Inbox.md" \
  "## $(date '+%Y-%m-%d %H:%M')\n<texto>\n#tag1 #tag2"
```

### Journal (criar ou append no dia)
```bash
bash /opt/cabecao/scripts/save-note.sh journal "Journal/$(date '+%Y-%m-%d').md" \
  "---\ndate: $(date '+%Y-%m-%d')\ntags: [journal]\nsource: telegram\n---\n\n## $(date '+%H:%M')\n\n<texto>"
```

### Meeting (novo arquivo por reunião)
```bash
bash /opt/cabecao/scripts/save-note.sh meeting "Meetings/$(date '+%Y-%m-%d')-<titulo>.md" \
  "---\ndate: $(date '+%Y-%m-%d')\ntype: meeting\nparticipants: [<nomes>]\ntags: [meeting]\nsource: telegram\n---\n\n## Resumo\n\n<texto>\n\n## Decisões\n\n## Action Items\n"
```

### Idea (novo arquivo)
```bash
bash /opt/cabecao/scripts/save-note.sh idea "3-Resources/ideas/$(date '+%Y-%m-%d')-<titulo>.md" \
  "---\ndate: $(date '+%Y-%m-%d')\ntype: idea\ntags: [idea]\nsource: telegram\n---\n\n<texto>"
```

### Task (append no Inbox)
```bash
bash /opt/cabecao/scripts/save-note.sh task "0-Inbox/Inbox.md" \
  "## $(date '+%Y-%m-%d %H:%M')\n- [ ] <tarefa>\n#task"
```

---

## Regras gerais

1. **Frontmatter:** sempre YAML com `date`, `tags`, `type` quando aplicável, `source: telegram` para conteúdo do Telegram.
2. **Wikilinks:** usar `[[nome]]` para pessoas e projetos quando identificáveis no texto.
3. **Inbox append:** cada entrada com `## YYYY-MM-DD HH:mm` + texto + tags na última linha.
4. **Confirmar:** após salvar, responder ao Diego informando onde foi salvo.
