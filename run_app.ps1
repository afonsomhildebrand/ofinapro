$env:DATABASE_URL = "sqlite:///oficinapro_dev.db"
$env:FLASK_DEBUG = "0"
Set-Location $PSScriptRoot
.\.venv\Scripts\python.exe -m flask --app app run --host 0.0.0.0 --port 5000 --no-reload *> server.log
