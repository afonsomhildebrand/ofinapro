$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "Status dos containers:"
docker compose ps
Write-Host ""
Write-Host "Ultimos logs do app:"
docker compose logs --tail 60 app
