# Sincronizar o vault: VPS, Mac e iPhone

O vault precisa estar em três lugares: **VPS** (onde o Cabeção escreve e o Khoj indexa), **Mac** (Obsidian) e **iPhone** (Obsidian mobile). Duas formas de manter tudo alinhado.

---

## Visão geral

| Onde   | Quem escreve        | Como sincroniza      |
|--------|---------------------|----------------------|
| **VPS**  | OpenClaw + você (via sync) | Push para o Git ou recebe do Syncthing |
| **Mac**  | Você (Obsidian)     | Git pull/push ou Syncthing + iCloud    |
| **iPhone** | Você (Obsidian)  | Git pull/push (plugin) ou iCloud       |

---

## Opção 1: Git em todos (recomendado)

Um **repositório Git privado** é a fonte da verdade. VPS faz push depois que o OpenClaw grava; Mac e iPhone fazem pull antes de editar e push depois.

```
                    ┌─────────────┐
                    │ GitHub /    │
                    │ GitLab      │
                    │ (repo       │
                    │  privado)   │
                    └──────┬──────┘
           push            │            pull
    ┌───────┴───────┐       │       ┌────┴────┐
    │               │   pull│push   │         │
    ▼               ▼       │       ▼         ▼
┌───────┐     ┌─────────┐  │  ┌───────┐ ┌────────┐
│  VPS  │     │  Mac    │  │  │ iPhone│ │  Mac   │
│OpenClaw│     │ Obsidian│◄─┴──►│Obsidian│ │Obsidian│
│ Khoj  │     │ (clone) │       │ + Git │ │ (clone)│
└───────┘     └─────────┘       │plugin │ └────────┘
                                └────────┘
```

### VPS

1. **Se tudo está no repo cabecao:** clone cabecao na VPS; OpenClaw e Khoj usam o path `.../cabecao/vault`. **Cron:** use `scripts/vps-cabecao-git-push.sh` (commit só `vault/`, push). Ver [proximos-passos.md](proximos-passos.md).
2. **Se o vault é um repo separado:** vault = clone do repo do vault; OpenClaw/Khoj apontam para essa pasta. **Cron:** use `scripts/vps-vault-git-push.sh`.

### Mac

1. Clone o repo **cabecao** (ex.: `~/Documents/cabecao`).
2. No Obsidian, abra a pasta **vault** como vault (ou seja, `~/Documents/cabecao/vault`), não a raiz do repo.
3. **Antes de editar:** na raiz do repo, `git pull`. **Depois:** `git add vault/ && git commit -m "..." && git push`. Ou use o plugin “Obsidian Git” no repo cabecao (vault = subpasta `vault/`).

### iPhone

1. Instale **Obsidian** e o plugin **Obsidian Git**.
2. Clone o repo **cabecao** (por Working Copy ou pelo próprio Obsidian Git, se suportar). Abra como vault a **subpasta vault/** (não a raiz do repo).
3. No Obsidian Git: repo = cabecao (raiz). **Pull** ao abrir, **Push** ao sair ou em intervalo.

### Repo: vault sozinho ou vault dentro do cabecao?

- **Tudo no repo cabecao (recomendado aqui):** Um único repo com pasta `vault/`. VPS clona cabecao; OpenClaw/Khoj apontam para `.../cabecao/vault`. Cron na VPS usa o script **`scripts/vps-cabecao-git-push.sh`** (commit só de `vault/`, depois push). Mac/iPhone clonam cabecao e abrem a pasta **vault/** no Obsidian. Ver **[proximos-passos.md](proximos-passos.md)**.
- **Vault como repo separado:** Repo privado só para o vault. Na VPS o vault é esse repo; use **`scripts/vps-vault-git-push.sh`** (o vault é a raiz do repo). No Mac/iPhone, clone só esse repo e abra como vault.

---

## Opção 2: Syncthing (Mac ↔ VPS) + iCloud (Mac ↔ iPhone)

Sem Git no vault: arquivos replicados por Syncthing e iCloud.

```
  iPhone  ◄──── iCloud ────►  Mac  ◄──── Syncthing ─────►  VPS
  Obsidian     (vault)         Obsidian    (vault)         OpenClaw
  (iCloud)                     (pasta                     Khoj
                                iCloud +
                                Syncthing)
```

- **Mac:** Uma pasta que é ao mesmo tempo:
  - pasta do vault no **Obsidian**, e
  - pasta sincronizada com a **iCloud** (para o iPhone), e
  - pasta em **Syncthing** compartilhada com a VPS.
- **VPS:** Mesma pasta do vault que o OpenClaw/Khoj usam, sincronizada com o Mac via Syncthing.
- **iPhone:** Obsidian abrindo o vault pela **iCloud** (mesma pasta que o Mac).

Vantagem: não precisa pensar em pull/push. Desvantagem: conflitos de arquivo (editar o mesmo note no Mac e no iPhone ao mesmo tempo) podem gerar duplicados; Syncthing e iCloud precisam estar sempre ativos no Mac.

### Passos resumidos

1. **Mac:** Criar pasta do vault em **iCloud Drive** (ex.: `iCloud Drive/Obsidian/Cabeção`). Abrir no Obsidian. Instalar Syncthing e adicionar essa pasta como “Folder” para compartilhar.
2. **VPS:** Instalar Syncthing, adicionar o “device” do Mac e a pasta remota; pasta local na VPS = path do vault (ex.: `/var/lib/obsidian-vault`). OpenClaw e Khoj apontam para essa pasta.
3. **iPhone:** No Obsidian, “Open folder as vault” e escolher a mesma pasta do vault na iCloud.

---

## Recomendações práticas

| Se você… | Use |
|----------|-----|
| Quer controle de versão e histórico | **Opção 1 (Git)** |
| Quer o mínimo de configuração e não liga a Git | **Opção 2 (Syncthing + iCloud)** |
| Edita muito no iPhone | **Opção 1** costuma dar menos conflito (pull/push explícito). |

Para **Cabeção**, a **Opção 1 (Git)** é a mais alinhada com a stack: VPS já vai ter o vault; basta um cron para commit/push e Mac/iPhone usarem o mesmo repo.

---

## Scripts: VPS commit + push (Opção 1)

- **Tudo no repo cabecao:** use **`scripts/vps-cabecao-git-push.sh`**. Define `REPO_DIR=/opt/cabecao` (ou onde está o clone). O script faz commit só da pasta `vault/` e push. Ver [proximos-passos.md](proximos-passos.md) para Git config, SSH e exemplo de cron.
- **Vault em repo separado:** use **`scripts/vps-vault-git-push.sh`**. Define `VAULT_DIR` como a pasta do vault (que é a raiz do repo). O script faz commit de todo o vault e push.

Em ambos: lock para não sobrepor execuções; commit só se houver mudanças.
