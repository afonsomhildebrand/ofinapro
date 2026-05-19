#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

APP_PORT="5000"
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
  APP_PORT="${APP_HOST_PORT:-5000}"
fi

echo "Testando containers..."
docker compose ps | grep -q "oficinapro_linux_app"
docker compose ps | grep -q "oficinapro_linux_mysql"

echo "Testando HTTP..."
curl -fsS "http://127.0.0.1:${APP_PORT}/login" >/dev/null

echo "Testando MySQL..."
TABLES="$(docker exec oficinapro_linux_mysql mysql -u"${MYSQL_USER:-oficinapro}" -p"${MYSQL_PASSWORD:-oficinapro123}" -e "SHOW TABLES;" "${MYSQL_DATABASE:-oficina_pro}")"
for table in users user_permissions user_sessions activity_logs clients cars car_models employees manufacturers parts services service_orders order_parts invoices payments; do
  echo "$TABLES" | grep -q "$table"
done

echo "Teste standalone Linux concluido com sucesso."
