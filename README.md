# Cabeção

Assistente pessoal com RAG sobre o "eu": captura áudio e texto (Telegram), classifica, grava no vault e responde com base na sua base de conhecimento.

## Stack

- **Vault:** Obsidian-style markdown (este repo).
- **VPS:** OpenClaw (agente + Telegram) + Khoj (RAG) + vault. Spec: [stack-spec.md](./stack-spec.md).
- **Áudio:** Groq (Whisper). **LLM:** Claude Sonnet 4.5 (Anthropic).

## Estrutura do repositório

```
cabecao/
├── stack-spec.md          # Especificação da stack (Fases 1–3, custos, checklist)
├── vault/                 # Vault Obsidian (sync para VPS ou usar na VPS)
│   ├── 0-Inbox/
│   ├── 1-Projects/
│   ├── 2-Areas/
│   ├── 3-Resources/
│   ├── 4-Archive/
│   ├── Meetings/
│   ├── Journal/
│   ├── People/
│   ├── _config/            # stack-spec e configs
│   ├── _templates/
│   ├── TOOLS.md            # Instruções para OpenClaw (onde gravar)
│   ├── PERSONALITY.md      # Quem é o Cabeção e regras de áudio
│   └── HEARTBEAT.md        # Automações a cada 30 min
├── config/
│   └── openclaw-vault.example.yaml  # Exemplo de config OpenClaw (Groq + Telegram)
├── docs/
│   ├── sync-vault.md                # Sincronizar vault: VPS ↔ Mac ↔ iPhone (Git ou Syncthing+iCloud)
│   └── proximos-passos.md           # Próximos passos (tudo no repo cabecao): VPS, Mac, iPhone
└── scripts/
    ├── bootstrap-vault.sh           # Cria vault na VPS (vault em pasta separada)
    ├── vps-cabecao-git-push.sh      # Cron na VPS: commit + push só de vault/ (repo cabecao)
    └── vps-vault-git-push.sh        # Cron na VPS: commit + push (vault = repo separado)
```

## Como começar

### 1. Local (desenvolvimento / Obsidian no Mac)

- Abra a pasta `vault/` no Obsidian (File → Open folder as vault).
- Edite notas, templates e `TOOLS.md` / `PERSONALITY.md` à vontade.

### 2. VPS (produção)

1. **Fase 1 — Vault na VPS**  
   Na VPS, clone este repo (ou copie só a pasta `vault`) e rode o bootstrap, ou copie `vault/` para o path desejado (ex.: `/var/lib/obsidian-vault`):

   ```bash
   git clone --depth 1 https://github.com/SEU_USUARIO/cabecao.git
   ./cabecao/scripts/bootstrap-vault.sh /var/lib/obsidian-vault
   ```

   Para manter o vault sincronizado com Mac e iPhone: **[docs/sync-vault.md](./docs/sync-vault.md)** (Git em todos ou Syncthing + iCloud).

2. **Fase 2 — Khoj**  
   Instale Docker na VPS, suba o Khoj e aponte o content para o path do vault. Detalhes em [stack-spec.md](./stack-spec.md) § 5.

3. **Fase 3 — OpenClaw**  
   Instale OpenClaw na VPS, configure Claude + Groq, Telegram, e aponte o skill/vault para o mesmo path. Use os crons e HEARTBEAT da spec (§ 6).

## Custos estimados (mensal)

| Item        | Custo     |
|------------|-----------|
| VPS        | ~US$ 20–40 |
| Claude API | ~US$ 15–25 |
| Groq       | ~US$ 0–2   |
| Granola (opcional) | US$ 18 |
| **Total**  | **~US$ 35–85** |

## Segurança

- Repo do vault: **privado**.
- API keys só em variáveis de ambiente na VPS, nunca no vault.
- Telegram: 2FA + bot com `dmPolicy: pairing` (ou equivalente).

---

*Spec completa e checklist em [stack-spec.md](./stack-spec.md). Cópia no vault: `vault/_config/stack-spec.md`.*
