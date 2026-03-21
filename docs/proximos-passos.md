# Próximos passos — Cabeção (tudo no repo cabecao)

Tudo fica no repositório **cabecao**: código, scripts e a pasta **vault/**. Você sincroniza o mesmo repo no VPS, Mac e iPhone.

**Arquitetura e estado atual:** leia primeiro **[AGENTS.md](../AGENTS.md)** e o **[índice de docs](INDICE-DOCUMENTACAO.md)**.

> **VPS já criada?** Siga o guia passo a passo: **[implementacao-vps.md](implementacao-vps.md)** (Fases 1–3: vault + Git, Khoj, OpenClaw).

---

## Spec histórica

O arquivo **`stack-spec.md`** na raiz é a especificação v2.1 (histórico). Não substitui **`AGENTS.md`** para decisões atuais.

---

## Visão rápida

| Onde     | O que fazer |
|----------|-------------|
| **VPS**  | Clonar cabecao → OpenClaw/Khoj apontam para `.../cabecao/vault` → cron faz push da pasta `vault/` |
| **Mac**  | Clonar cabecao → Obsidian abre a pasta **vault/** → pull antes de editar, push depois |
| **iPhone** | Clonar cabecao (Obsidian Git ou Working Copy) → Obsidian abre a subpasta **vault/** → pull/push pelo plugin |

---

## 1. Repo cabecao

- Repositório **privado** (GitHub ou GitLab).
- Já contém: `vault/`, `scripts/`, `docs/`, `AGENTS.md`, `stack-spec.md` (histórico), etc.
- Garanta que o primeiro push já foi feito (para o VPS e os dispositivos clonarem depois).

---

## 2. VPS

### 2.1 Acesso e preparação

- Contratar VPS (ex.: HostGator, Hetzner, DigitalOcean) — Ubuntu, ~2 GB RAM, 20 GB disco.
- Acesso SSH (root ou usuário com sudo).
- Instalar: Node.js 22+, Docker (para o Khoj depois).

### 2.2 Clonar o repo e usar o vault

```bash
# Exemplo: repo em /opt/cabecao
sudo mkdir -p /opt/cabecao
sudo chown "$(whoami):$(whoami)" /opt/cabecao
git clone git@github.com:SEU_USUARIO/cabecao.git /opt/cabecao
```

- **Path do vault na VPS:** `/opt/cabecao/vault` (ou o path onde você clonou + `/vault`).
- **OpenClaw** e **Khoj** devem usar esse path (ex.: `/opt/cabecao/vault`).

### 2.3 Git: push a partir da VPS

Para o VPS conseguir dar push no repo:

1. **Git config** (uma vez):
   ```bash
   cd /opt/cabecao
   git config user.email "voce@email.com"
   git config user.name "Cabeção VPS"
   ```

2. **Chave SSH** na VPS e adicionar como **deploy key** no GitHub/GitLab (com permissão de escrita).

3. **Cron** — commit e push só da pasta `vault/` a cada 15 min:
   ```bash
   crontab -e
   # Adicionar:
   */15 * * * * REPO_DIR=/opt/cabecao /opt/cabecao/scripts/vps-cabecao-git-push.sh >> /var/log/cabecao-sync.log 2>&1
   ```

Script usado: `scripts/vps-cabecao-git-push.sh` (só commita mudanças em `vault/`).

### 2.4 Fases seguintes na VPS

- **Fase 2:** Instalar Docker, subir Khoj, apontar o content para `/opt/cabecao/vault`. Ver **[implementacao-vps.md](implementacao-vps.md)** (Fase 2) e **[AGENTS.md](../AGENTS.md)**.
- **Fase 3:** Instalar OpenClaw, Groq, Telegram, vault em `/opt/cabecao/vault`, crons. Ver **[implementacao-vps.md](implementacao-vps.md)** (Fase 3). Detalhe de token Khoj: **[khoj-token-passo-a-passo.md](khoj-token-passo-a-passo.md)**.
- **Histórico de desenho:** [stack-spec.md](../stack-spec.md) (v2.1, não substitui `AGENTS.md`).

---

## 3. Mac

1. **Clonar o repo** (se ainda não tiver):
   ```bash
   git clone git@github.com:SEU_USUARIO/cabecao.git ~/Documents/cabecao
   ```

2. **Obsidian:** File → Open folder as vault → escolher a pasta **`vault`** (ou seja, `~/Documents/cabecao/vault`). Não abra a pasta `cabecao`, e sim **cabecao/vault**.

3. **Sync:**  
   - Antes de editar: `cd ~/Documents/cabecao && git pull`  
   - Depois de editar: `git add vault/ && git commit -m "vault: ..." && git push`  
   Ou use o plugin **Obsidian Git** apontando para o repo `cabecao` (e configure para pull ao abrir e push ao fechar/intervalo). No plugin, o “vault path” do Obsidian é a pasta `vault/`; o repo continua sendo o cabecao (raiz).

---

## 4. iPhone

1. **Obsidian** instalado + plugin **Obsidian Git** (Community plugins).

2. **Clonar o repo cabecao** no iPhone:
   - Opção A: **Working Copy** (ou outro app Git) — clone o repo cabecao, depois no Obsidian “Open folder as vault” e escolha a pasta **vault** dentro do clone.
   - Opção B: Se o Obsidian Git permitir “clone repo”, clone o cabecao e depois abra como vault a subpasta **vault**.

3. **Obsidian Git:** configurar para o repositório raiz (cabecao). **Pull** ao abrir o vault, **Push** ao sair ou em intervalo. O vault no Obsidian é a pasta `vault/` dentro do repo.

---

## 5. Ordem sugerida

1. Criar/garantir o repo **cabecao** (privado) e fazer o primeiro push.
2. **VPS:** seguir **[implementacao-vps.md](implementacao-vps.md)** — Fase 1 (clonar cabecao, Git, cron), Fase 2 (Khoj), Fase 3 (OpenClaw + Groq + Telegram). Path do vault = `/opt/cabecao/vault`.
3. **Mac:** clonar cabecao, abrir `vault/` no Obsidian, usar pull/push (ou Obsidian Git).
4. **iPhone:** clonar cabecao, abrir a pasta `vault/` no Obsidian, configurar Obsidian Git para pull/push no repo cabecao.

Assim o vault fica sincronizado entre VPS, Mac e iPhone usando só o repositório cabecao.
