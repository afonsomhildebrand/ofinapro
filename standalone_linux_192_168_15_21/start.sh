#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
docker compose up -d

APP_PORT="5000"
PUBLIC_HOST="192.168.15.21"
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
  APP_PORT="${APP_HOST_PORT:-5000}"
  PUBLIC_HOST="${APP_PUBLIC_HOST:-192.168.15.21}"
fi

echo "OficinaPro iniciado."
echo "Acesso local: http://127.0.0.1:${APP_PORT}"
echo "Acesso na rede: http://${PUBLIC_HOST}:${APP_PORT}"
