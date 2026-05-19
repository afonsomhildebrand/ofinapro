$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$baseUrl = "http://127.0.0.1:5000"

Write-Host "Testando containers..."
$psText = docker compose ps | Out-String
if ($psText -notmatch "oficinapro_standalone_app" -or $psText -notmatch "oficinapro_standalone_mysql") {
  throw "Containers standalone nao encontrados."
}
if ($psText -notmatch "3307->3306") {
  throw "MySQL nao esta publicado na porta 3307."
}

Write-Host "Testando HTTP..."
$login = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -TimeoutSec 10
if ($login.StatusCode -ne 200) {
  throw "Tela de login retornou status $($login.StatusCode)."
}

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -WebSession $session -TimeoutSec 10 | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -Method Post -Body @{username='admin'; password='admin123'} -WebSession $session -MaximumRedirection 0 -ErrorAction SilentlyContinue | Out-Null
$users = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/usuarios" -WebSession $session -TimeoutSec 10
if ($users.StatusCode -ne 200 -or -not $users.Content.Contains("Permissoes por menu")) {
  throw "Tela de usuarios nao respondeu como esperado."
}

Write-Host "Testando MySQL..."
$tables = docker exec oficinapro_standalone_mysql mysql -uoficinapro -poficinapro123 -e "SHOW TABLES;" oficina_pro | Out-String
foreach ($table in @("users", "user_permissions", "user_sessions", "activity_logs", "clients", "cars", "car_models", "employees", "manufacturers", "parts", "services", "service_orders", "order_parts")) {
  if ($tables -notmatch $table) {
    throw "Tabela ausente: $table"
  }
}

Write-Host "Teste standalone concluido com sucesso."
