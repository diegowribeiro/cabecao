#!/usr/bin/env bash
# save-note.sh — Salva uma nota no vault e faz git push
# Uso: save-note.sh <tipo> <caminho-relativo> <conteudo>
# Tipos: inbox | meeting | journal | task | idea
#
# Exemplos:
#   save-note.sh inbox "0-Inbox/Inbox.md" "## 2026-03-14 10:30\nIdeia sobre X\n#ideia"    (append)
#   save-note.sh meeting "Meetings/2026-03-14-reuniao-joao.md" "---\ndate: 2026-03-14\n..."  (criar)

set -euo pipefail

VAULT="/opt/cabecao/vault"
TYPE="${1:-inbox}"
REL_PATH="${2}"
CONTENT="${3}"

if [[ -z "$REL_PATH" || -z "$CONTENT" ]]; then
  echo "Uso: save-note.sh <tipo> <caminho-relativo> <conteudo>" >&2
  exit 1
fi

FULL_PATH="$VAULT/$REL_PATH"
DIR=$(dirname "$FULL_PATH")

mkdir -p "$DIR"

if [[ "$TYPE" == "inbox" ]] && [[ -f "$FULL_PATH" ]]; then
  # Inbox: append
  printf "\n%b" "$CONTENT" >> "$FULL_PATH"
else
  # Outros tipos: criar arquivo (sobrescreve se existir)
  printf "%b" "$CONTENT" >> "$FULL_PATH"
fi

# Git commit e push
cd "$VAULT"
git add "$REL_PATH"
git commit -m "vault: add $TYPE — $(basename "$REL_PATH" .md)" --quiet
git push --quiet

echo "OK: salvo em $REL_PATH e sincronizado"
