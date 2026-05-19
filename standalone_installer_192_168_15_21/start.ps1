$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
docker compose up -d
if ($LASTEXITCODE -ne 0) {
  throw "Docker Compose falhou ao iniciar os containers. Confirme se o Docker Desktop esta aberto e com o daemon Linux ativo."
}
$appPort = "5000"
$publicHost = "127.0.0.1"
if (Test-Path ".env") {
  Get-Content ".env" | ForEach-Object {
    if ($_ -match "^APP_HOST_PORT=(.+)$") { $appPort = $Matches[1].Trim() }
    if ($_ -match "^APP_PUBLIC_HOST=(.+)$") { $publicHost = $Matches[1].Trim() }
  }
}
Write-Host "OficinaPro iniciado."
Write-Host "Acesso local: http://127.0.0.1:$appPort"
Write-Host "Acesso na rede: http://$publicHost`:$appPort"
