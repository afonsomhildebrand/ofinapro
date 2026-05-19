$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "OficinaPro Standalone Installer"
Write-Host "Verificando Docker..."

try {
  docker --version | Out-Null
  docker compose version | Out-Null
} catch {
  throw "Docker Desktop com Docker Compose nao foi encontrado. Instale o Docker Desktop e execute este instalador novamente."
}

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Arquivo .env criado a partir de .env.example."
}

Write-Host "Construindo e iniciando app + MySQL..."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
  throw "Docker Compose falhou ao construir ou iniciar os containers. Confirme se o Docker Desktop esta aberto e com o daemon Linux ativo."
}

Write-Host "Aguardando aplicacao responder..."
$appPort = "5000"
$publicHost = "127.0.0.1"
if (Test-Path ".env") {
  Get-Content ".env" | ForEach-Object {
    if ($_ -match "^APP_HOST_PORT=(.+)$") { $appPort = $Matches[1].Trim() }
    if ($_ -match "^APP_PUBLIC_HOST=(.+)$") { $publicHost = $Matches[1].Trim() }
  }
}
$baseUrl = "http://127.0.0.1:$appPort"
$publicUrl = "http://$publicHost`:$appPort"
for ($attempt = 1; $attempt -le 40; $attempt++) {
  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/login" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
      Write-Host "Instalacao concluida com sucesso."
      Write-Host "Acesso local: $baseUrl"
      Write-Host "Acesso na rede: $publicUrl"
      Write-Host "Login inicial: admin / admin123"
      exit 0
    }
  } catch {
    Start-Sleep -Seconds 3
  }
}

throw "A aplicacao nao respondeu em $baseUrl/login. Verifique os logs com .\status.ps1."
