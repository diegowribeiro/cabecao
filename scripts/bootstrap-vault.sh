#!/usr/bin/env bash
# Bootstrap do vault Cabeção na VPS
# Uso: ./bootstrap-vault.sh [DIR]
# Ex.: ./bootstrap-vault.sh /var/lib/obsidian-vault

set -e

VAULT_DIR="${1:-/var/lib/obsidian-vault}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_VAULT="${SCRIPT_DIR}/../vault"

echo "==> Cabeção: bootstrap do vault em ${VAULT_DIR}"

if [ ! -d "$REPO_VAULT" ]; then
  echo "Erro: pasta vault não encontrada em ${REPO_VAULT}"
  exit 1
fi

sudo mkdir -p "$VAULT_DIR"
sudo chown "$(whoami):$(whoami)" "$VAULT_DIR"

echo "==> Copiando estrutura do vault..."
rsync -a --exclude='.git' "$REPO_VAULT/" "$VAULT_DIR/"

echo "==> Ajustando permissões..."
chmod -R u+rwX "$VAULT_DIR"

echo "==> Git no vault (opcional)..."
if [ ! -d "$VAULT_DIR/.git" ]; then
  cd "$VAULT_DIR"
  git init
  echo ".obsidian/workspace.json" >> .gitignore
  echo ".obsidian/workspace-mobile.json" >> .gitignore
  echo ".trash/" >> .gitignore
  echo "Vault inicializado com Git. Adicione remote e faça o primeiro push manualmente."
  cd - > /dev/null
fi

echo "==> Pronto. Vault em: ${VAULT_DIR}"
echo "    Próximo: configurar OpenClaw/Khoj para apontar para este path."
