#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ "${1:-}" = "--remove-data" ]; then
  docker compose down -v
  echo "Containers e dados removidos."
else
  docker compose down
  echo "Containers removidos. Dados preservados no volume Docker."
fi
