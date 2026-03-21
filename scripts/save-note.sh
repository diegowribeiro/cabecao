#!/usr/bin/env bash
# save-note.sh — Salva uma nota no vault e faz git push
# Uso: /opt/cabecao/scripts/save-note.sh <tipo> <caminho-relativo> <conteudo>
# Tipos: inbox | meeting | journal | task | idea

set -euo pipefail

VAULT="/opt/cabecao/vault"
# Token de API do Khoj (Settings → API). Nunca commitar: use env na VPS, ex.:
#   export KHOJ_UPDATE_TOKEN="..." em ~/.bashrc ou no mesmo unit que roda o agente.
KHOJ_TOKEN="${KHOJ_UPDATE_TOKEN:-}"
TYPE="${1:-inbox}"
REL_PATH="${2}"
CONTENT="${3}"

if [[ -z "$REL_PATH" || -z "$CONTENT" ]]; then
  echo "Uso: save-note.sh <tipo> <caminho-relativo> <conteudo>" >&2
  exit 1
fi

# Proteção contra path traversal
if [[ "$REL_PATH" == *".."* ]] || [[ "$REL_PATH" == /* ]]; then
  echo "ERRO: path inválido bloqueado: $REL_PATH" >&2
  exit 1
fi

FULL_PATH="$VAULT/$REL_PATH"
DIR=$(dirname "$FULL_PATH")

mkdir -p "$DIR"

if [[ "$TYPE" == "inbox" || "$TYPE" == "task" || "$TYPE" == "journal" ]]; then
  # Append com nova linha
  printf "\n%b" "$CONTENT" >> "$FULL_PATH"
else
  # meeting/idea: cria novo arquivo (falha se já existir para evitar corrupção)
  if [[ -f "$FULL_PATH" ]]; then
    printf "\n%b" "$CONTENT" >> "$FULL_PATH"
  else
    printf "%b" "$CONTENT" > "$FULL_PATH"
  fi
fi

# Git commit e push
cd "$VAULT"
git add "$REL_PATH"
git commit -m "vault: add $TYPE — $(basename "$REL_PATH" .md)" --quiet
git push --quiet

# Reindexar Khoj para RAG ficar atualizado imediatamente (se token configurado)
if [[ -n "$KHOJ_TOKEN" ]]; then
  curl -s -H "Authorization: Bearer $KHOJ_TOKEN" \
    "http://localhost:42110/api/update?force=true&t=markdown" > /dev/null 2>&1 || true
fi

echo "OK: salvo em $REL_PATH e sincronizado"
