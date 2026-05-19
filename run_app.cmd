@echo off
cd /d "%~dp0"
set DATABASE_URL=sqlite:///oficinapro_dev.db
set FLASK_DEBUG=0
.venv\Scripts\python.exe -m flask --app app run --host 0.0.0.0 --port 5000 --no-reload > server.log 2>&1
