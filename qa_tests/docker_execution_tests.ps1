$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)
$reportsDir = Join-Path $PSScriptRoot "reports"
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
$startedAt = Get-Date
$steps = New-Object System.Collections.Generic.List[object]
$status = "PASS"
$errorMessage = ""
$envPath = Join-Path (Get-Location) ".env"
$appHostPort = "5000"
$mysqlHostPort = "3307"
if (Test-Path $envPath) {
  foreach ($line in Get-Content $envPath) {
    if ($line -match "^APP_HOST_PORT=(.+)$") {
      $appHostPort = $Matches[1].Trim()
    }
    if ($line -match "^MYSQL_HOST_PORT=(.+)$") {
      $mysqlHostPort = $Matches[1].Trim()
    }
  }
}

function Add-Step {
  param(
    [string]$Name,
    [string]$Status,
    [string]$Details
  )
  $script:steps.Add([pscustomobject]@{
    Name = $Name
    Status = $Status
    Details = $Details
    Time = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  })
}

try {
Write-Host "Validating docker compose config"
$composeConfig = docker compose config | Out-String
Add-Step "docker compose config" "PASS" "Configuracao Docker Compose validada."

Write-Host "Building and starting containers"
$composeUp = docker compose up -d --build | Out-String
Add-Step "docker compose up" "PASS" "Containers construidos/iniciados."

Write-Host "Checking container status"
$psText = docker compose ps | Out-String
if ($psText -notmatch "oficinapro_app" -or $psText -notmatch "oficinapro_mysql") {
  throw "Expected containers were not found"
}
if ($psText -notmatch "$mysqlHostPort->3306") {
  throw "MySQL is not exposed on host port $mysqlHostPort"
}
Add-Step "container status" "PASS" $psText.Trim()

Write-Host "Testing HTTP endpoints"
$baseUrl = "http://127.0.0.1:$appHostPort"
for ($attempt = 1; $attempt -le 30; $attempt++) {
  try {
    $loginPage = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -TimeoutSec 5
    break
  } catch {
    if ($attempt -eq 30) {
      throw
    }
    Start-Sleep -Seconds 2
  }
}
if ($loginPage.StatusCode -ne 200) {
  throw "Login page returned $($loginPage.StatusCode)"
}
Add-Step "GET /login" "PASS" "Status HTTP: $($loginPage.StatusCode)"

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -WebSession $session -TimeoutSec 10 | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -Method Post -Body @{username='admin'; password='admin123'} -WebSession $session -MaximumRedirection 0 -ErrorAction SilentlyContinue | Out-Null
Add-Step "POST /login" "PASS" "Login admin executado."

$charts = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/graficos" -WebSession $session -TimeoutSec 20
if ($charts.StatusCode -ne 200 -or -not $charts.Content.Contains("Servicos por mes")) {
  throw "Charts page did not render correctly"
}
Add-Step "GET /graficos" "PASS" "Status HTTP: $($charts.StatusCode); conteudo esperado encontrado."

$usersPage = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/usuarios" -WebSession $session -TimeoutSec 20
if ($usersPage.StatusCode -ne 200 -or -not $usersPage.Content.Contains("Permissoes por menu")) {
  throw "Users page did not render correctly"
}
Add-Step "GET /usuarios" "PASS" "Status HTTP: $($usersPage.StatusCode); permissoes renderizadas."

$billingPage = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/financeiro" -WebSession $session -TimeoutSec 20
if ($billingPage.StatusCode -ne 200 -or -not $billingPage.Content.Contains("Notas fiscais")) {
  throw "Billing page did not render correctly"
}
Add-Step "GET /financeiro" "PASS" "Status HTTP: $($billingPage.StatusCode); financeiro renderizado."

Write-Host "Testing MySQL tables"
$tables = docker exec oficinapro_mysql mysql -uoficinapro -poficinapro123 -e "SHOW TABLES;" oficina_pro | Out-String
foreach ($table in @("users", "user_permissions", "user_sessions", "activity_logs", "clients", "cars", "car_models", "employees", "manufacturers", "parts", "services", "service_orders", "order_parts", "invoices", "payments")) {
  if ($tables -notmatch $table) {
    throw "Missing table: $table"
  }
}
Add-Step "mysql tables" "PASS" $tables.Trim()

$auditCounts = docker exec oficinapro_mysql mysql -uoficinapro -poficinapro123 -N -e "SELECT (SELECT COUNT(*) FROM user_sessions), (SELECT COUNT(*) FROM activity_logs), (SELECT COUNT(*) FROM user_permissions);" oficina_pro | Out-String
$parts = $auditCounts.Trim() -split "\s+"
if ([int]$parts[0] -lt 1 -or [int]$parts[1] -lt 1 -or [int]$parts[2] -lt 1) {
  throw "Audit tables did not receive expected records: $auditCounts"
}
Add-Step "audit records" "PASS" "user_sessions=$($parts[0]); activity_logs=$($parts[1]); user_permissions=$($parts[2])"

Write-Host "Docker execution tests passed"
} catch {
  $status = "FAIL"
  $errorMessage = $_.Exception.Message
  Add-Step "failure" "FAIL" $errorMessage
  throw
} finally {
  $finishedAt = Get-Date
  $reportPath = Join-Path $reportsDir ("docker_execution_tests_{0}.md" -f $finishedAt.ToString("yyyyMMdd_HHmmss"))
  $content = New-Object System.Collections.Generic.List[string]
  $content.Add("# Relatorio de Testes Docker - OficinaPro")
  $content.Add("")
  $content.Add("- Status: $status")
  $content.Add("- Inicio: $($startedAt.ToString("yyyy-MM-dd HH:mm:ss"))")
  $content.Add("- Fim: $($finishedAt.ToString("yyyy-MM-dd HH:mm:ss"))")
  $content.Add("- Duracao: $([math]::Round(($finishedAt - $startedAt).TotalSeconds, 2))s")
  if ($errorMessage) {
    $content.Add("- Erro: $errorMessage")
  }
  $content.Add("")
  $content.Add("## Etapas")
  foreach ($step in $steps) {
    $content.Add("")
    $content.Add("### $($step.Name)")
    $content.Add("")
    $content.Add("- Status: $($step.Status)")
    $content.Add("- Hora: $($step.Time)")
    $content.Add("")
    $content.Add('```text')
    $content.Add($step.Details)
    $content.Add('```')
  }
  Set-Content -Path $reportPath -Value $content -Encoding UTF8
  Write-Host "Relatorio gerado: $reportPath"
}
