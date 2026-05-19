param(
  [switch]$RemoveData
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($RemoveData) {
  docker compose down -v
  Write-Host "Containers removidos e dados apagados."
} else {
  docker compose down
  Write-Host "Containers removidos. Dados preservados no volume Docker."
}
