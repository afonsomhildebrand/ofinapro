#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

APP_PORT="${APP_HOST_PORT:-5000}"
PUBLIC_HOST="${APP_PUBLIC_HOST:-192.168.15.21}"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
  APP_PORT="${APP_HOST_PORT:-5000}"
  PUBLIC_HOST="${APP_PUBLIC_HOST:-192.168.15.21}"
fi

echo "OficinaPro Linux - Instalador"
echo "Verificando Docker..."
docker --version >/dev/null
docker compose version >/dev/null

echo "Construindo e iniciando app + MySQL..."
docker compose up -d --build

echo "Aguardando aplicacao responder..."
for attempt in $(seq 1 40); do
  if curl -fsS "http://127.0.0.1:${APP_PORT}/login" >/dev/null; then
    echo "Instalacao concluida com sucesso."
    echo "Acesso local: http://127.0.0.1:${APP_PORT}"
    echo "Acesso na rede: http://${PUBLIC_HOST}:${APP_PORT}"
    echo "Login inicial: admin / admin123"
    exit 0
  fi
  sleep 3
done

echo "A aplicacao nao respondeu em http://127.0.0.1:${APP_PORT}/login."
echo "Verifique logs com: ./status.sh"
exit 1
