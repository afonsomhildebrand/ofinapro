#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
echo "Status dos containers:"
docker compose ps
echo
echo "Ultimos logs do app:"
docker compose logs --tail 80 app
