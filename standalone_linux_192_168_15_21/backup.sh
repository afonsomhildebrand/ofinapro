#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p backups

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="backups/oficina_pro_${STAMP}.sql"
docker exec oficinapro_linux_mysql mysqldump -u"${MYSQL_USER:-oficinapro}" -p"${MYSQL_PASSWORD:-oficinapro123}" "${MYSQL_DATABASE:-oficina_pro}" > "$BACKUP_FILE"
echo "Backup criado: $BACKUP_FILE"
