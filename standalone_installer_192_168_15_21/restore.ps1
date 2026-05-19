param(
  [Parameter(Mandatory=$true)]
  [string]$BackupFile
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path $BackupFile)) {
  throw "Arquivo de backup nao encontrado: $BackupFile"
}

Get-Content $BackupFile | docker exec -i oficinapro_standalone_mysql mysql -uoficinapro -poficinapro123 oficina_pro
Write-Host "Backup restaurado: $BackupFile"
