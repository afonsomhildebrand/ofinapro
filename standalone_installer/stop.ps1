$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
docker compose down
Write-Host "OficinaPro parado. Os dados foram preservados no volume Docker."
