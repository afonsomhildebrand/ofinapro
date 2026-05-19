$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)
$reportsDir = Join-Path $PSScriptRoot "reports"
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
$startedAt = Get-Date
$steps = New-Object System.Collections.Generic.List[object]
$status = "PASS"
$errorMessage = ""

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

$baseUrl = "http://127.0.0.1:5000"

try {
Write-Host "Testing local app at $baseUrl"

$login = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -TimeoutSec 10
if ($login.StatusCode -ne 200) {
  throw "Login page returned $($login.StatusCode)"
}
Add-Step "GET /login" "PASS" "Status HTTP: $($login.StatusCode)"

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -WebSession $session -TimeoutSec 10 | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -Method Post -Body @{username='admin'; password='admin123'} -WebSession $session -MaximumRedirection 0 -ErrorAction SilentlyContinue | Out-Null
Add-Step "POST /login" "PASS" "Login admin executado."

$charts = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/graficos" -WebSession $session -TimeoutSec 10
if ($charts.StatusCode -ne 200 -or -not $charts.Content.Contains("Servicos por mes")) {
  throw "Charts page did not render correctly"
}
Add-Step "GET /graficos" "PASS" "Status HTTP: $($charts.StatusCode); conteudo esperado encontrado."

Write-Host "Local execution tests passed"
} catch {
  $status = "FAIL"
  $errorMessage = $_.Exception.Message
  Add-Step "failure" "FAIL" $errorMessage
  throw
} finally {
  $finishedAt = Get-Date
  $reportPath = Join-Path $reportsDir ("local_execution_tests_{0}.md" -f $finishedAt.ToString("yyyyMMdd_HHmmss"))
  $content = New-Object System.Collections.Generic.List[string]
  $content.Add("# Relatorio de Testes Locais - OficinaPro")
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
