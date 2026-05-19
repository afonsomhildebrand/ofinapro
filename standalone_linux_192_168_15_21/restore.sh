#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ "$#" -ne 1 ]; then
  echo "Uso: ./restore.sh backups/arquivo.sql"
  exit 1
fi

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

docker exec -i oficinapro_linux_mysql mysql -u"${MYSQL_USER:-oficinapro}" -p"${MYSQL_PASSWORD:-oficinapro123}" "${MYSQL_DATABASE:-oficina_pro}" < "$1"
echo "Backup restaurado: $1"
