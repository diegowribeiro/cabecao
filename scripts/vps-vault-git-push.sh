#!/usr/bin/env bash
# Cron: commit e push do vault na VPS (para sync com Mac/iPhone)
# Uso: VAULT_DIR=/var/lib/obsidian-vault ./vps-vault-git-push.sh
# Cron (a cada 15 min): */15 * * * * VAULT_DIR=/var/lib/obsidian-vault /path/to/vps-vault-git-push.sh

set -e

VAULT_DIR="${VAULT_DIR:-/var/lib/obsidian-vault}"
LOCK_FILE="${VAULT_DIR}/.git-sync.lock"

if [ ! -d "$VAULT_DIR" ]; then
  echo "Erro: vault não encontrado em ${VAULT_DIR}" >&2
  exit 1
fi

if [ ! -d "$VAULT_DIR/.git" ]; then
  echo "Vault em ${VAULT_DIR} não é um repo Git. Ignorando." >&2
  exit 0
fi

# Evitar duas execuções ao mesmo tempo
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Outro sync em andamento. Saindo." >&2
  exit 0
fi

cd "$VAULT_DIR"

# Só commita se houver mudanças
if git status --porcelain | grep -q .; then
  git add -A
  git commit -m "vault: sync automático $(date -Iseconds)" || true
  git push origin HEAD || true
fi
