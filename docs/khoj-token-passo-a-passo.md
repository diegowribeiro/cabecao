# Khoj — token de API e `KHOJ_UPDATE_TOKEN` (passo a passo)

O script `scripts/save-note.sh`, depois de salvar uma nota no vault, pode chamar a API do Khoj para **forçar reindexação** do conteúdo. Isso exige um **token de API** válido, passado por variável de ambiente — **nunca** commitado no Git.

---

## Preciso gerar um token novo?

- **Se nunca expôs o token em lugar público nem no histórico do Git:** pode usar o **mesmo** token que o Khoj já mostra na interface (e só configurar `KHOJ_UPDATE_TOKEN` na VPS).
- **Se o token já apareceu em README, script com valor fixo ou issue pública:** **sim** — gere um **novo** token no Khoj e **revogue** o antigo (o antigo pode existir no histórico do `git`).

Na dúvida, **rotacione**: gere um novo, atualize a VPS, revogue o anterior.

---

## Passo 1 — Abrir a UI do Khoj na VPS

O Khoj escuta em `localhost` na VPS. No seu **Mac**:

```bash
ssh -p 22022 -L 42110:localhost:42110 root@SEU_IP_DA_VPS
```

No navegador: **http://localhost:42110**

Faça login com o **usuário admin** que você criou na instalação do Khoj (email/senha **não** estão neste repo — são os da sua instalação).

---

## Passo 2 — Criar ou copiar o token de API

A interface do Khoj varia por versão; em geral:

1. Entre em **Settings** (ou **Configuração** / ícone de engrenagem).
2. Procure seções como **API**, **API Keys**, **Developer**, **Authentication** ou **Personal Access Tokens**.
3. **Crie um novo token** (nome sugerido: `cabecao-reindex`) ou copie um token existente que tenha permissão para **acessar a API** / **reindex**.

Se não achar: consulte a documentação da sua versão em [https://docs.khoj.dev](https://docs.khoj.dev) ou a ajuda dentro da UI.

Guarde o token em um **gerenciador de senhas** até colá-lo na VPS (um único lugar seguro).

---

## Passo 3 — Colocar o token na VPS (`KHOJ_UPDATE_TOKEN`)

O processo que executa o **OpenClaw Gateway** (e portanto o `save-note.sh` quando o agente grava notas) precisa ver a variável.

Arquivo típico (usuário `root`, systemd user):

**`/root/.config/systemd/user/openclaw-gateway.service.d/env.conf`**

Edite ( `nano` / `vim` ) e adicione **uma** linha (substitua pelo token real):

```ini
Environment="KHOJ_UPDATE_TOKEN=cole_aqui_o_token_do_khoj"
```

Se já existir `[Service]` ou outras linhas `Environment=`, pode adicionar outra linha `Environment=` ou combinar conforme a documentação do systemd.

**Permissões:** restrinja leitura (`chmod 600` nesse arquivo se fizer sentido no seu ambiente).

---

## Passo 4 — Recarregar e reiniciar o gateway

```bash
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
systemctl --user status openclaw-gateway.service
```

---

## Passo 5 — Testar

Na VPS:

```bash
export KHOJ_UPDATE_TOKEN="mesmo_valor_que_colocou_no_env.conf"
curl -s -H "Authorization: Bearer $KHOJ_UPDATE_TOKEN" \
  "http://localhost:42110/api/update?force=true&t=markdown"
```

Se retornar erro HTTP ou “unauthorized”, o token ou a URL da API está incorreta para a sua versão do Khoj — verifique na documentação do Khoj o endpoint exato de atualização.

Teste também salvar uma linha via:

```bash
/opt/cabecao/scripts/save-note.sh inbox "0-Inbox/Inbox.md" "## teste token $(date -Iseconds)\n"
```

(Depois pode reverter o commit no vault se for só teste.)

---

## Passo 6 — Revogar token antigo (se rotacionou)

Na UI do Khoj, na mesma área de API Keys, **revogue** o token comprometido.

---

## Resumo

| O quê | Onde |
|--------|------|
| Gerar/copiar token | UI Khoj → Settings → API (ou equivalente) |
| Variável | `KHOJ_UPDATE_TOKEN` |
| Arquivo na VPS | `~/.config/systemd/user/openclaw-gateway.service.d/env.conf` (ajuste usuário se não for root) |
| Script que usa | `/opt/cabecao/scripts/save-note.sh` |

Mais contexto: `AGENTS.md` (raiz do repo) e `docs/economia-api.md`.
