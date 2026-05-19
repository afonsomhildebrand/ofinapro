#!/bin/sh
set -e

echo "Aguardando MySQL em ${MYSQL_HOST}:${MYSQL_PORT}..."

python - <<'PY'
import os
import time

import pymysql

host = os.getenv("MYSQL_HOST", "mysql")
port = int(os.getenv("MYSQL_PORT", "3306"))
user = os.getenv("MYSQL_USER", "oficinapro")
password = os.getenv("MYSQL_PASSWORD", "oficinapro123")
database = os.getenv("MYSQL_DATABASE", "oficina_pro")

last_error = None
for attempt in range(1, 61):
    try:
        connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        connection.close()
        print("MySQL pronto.")
        break
    except Exception as exc:
        last_error = exc
        print(f"Tentativa {attempt}/60: MySQL ainda indisponivel.")
        time.sleep(2)
else:
    raise SystemExit(f"Nao foi possivel conectar ao MySQL: {last_error}")
PY

echo "Inicializando banco de dados..."
flask --app app init-db

echo "Iniciando OficinaPro..."
exec "$@"
