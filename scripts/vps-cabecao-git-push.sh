#!/usr/bin/env bash
# Cron: commit e push da pasta vault/ no repo cabecao (VPS → GitHub/GitLab)
# Use este script quando o vault estiver DENTRO do repo cabecao.
# Uso: REPO_DIR=/opt/cabecao ./vps-cabecao-git-push.sh
# Cron: */15 * * * * REPO_DIR=/opt/cabecao /path/to/cabecao/scripts/vps-cabecao-git-push.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$SCRIPT_DIR/..}"
REPO_DIR="$(cd "$REPO_DIR" && pwd)"
LOCK_FILE="${REPO_DIR}/.git-sync.lock"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Não é um repo Git: ${REPO_DIR}" >&2
  exit 1
fi

if [ ! -d "$REPO_DIR/vault" ]; then
  echo "Pasta vault/ não encontrada em ${REPO_DIR}" >&2
  exit 1
fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Outro sync em andamento. Saindo." >&2
  exit 0
fi

cd "$REPO_DIR"

# Só commita mudanças em vault/
if git status --porcelain vault/ | grep -q .; then
  git add vault/
  git commit -m "vault: sync automático $(date -Iseconds)" || true
  git push origin HEAD || true
fi
