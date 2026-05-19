$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $PSScriptRoot "backups\oficina_pro_$timestamp.sql"

docker exec oficinapro_standalone_mysql mysqldump -uoficinapro -poficinapro123 oficina_pro | Out-File -Encoding UTF8 $backupFile
Write-Host "Backup gerado: $backupFile"
