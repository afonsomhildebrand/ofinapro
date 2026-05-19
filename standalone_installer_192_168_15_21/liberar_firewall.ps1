$ErrorActionPreference = "Stop"

$ruleName = "OficinaPro Web 5000"
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
  Write-Host "Regra de firewall ja existe: $ruleName"
} else {
  New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow | Out-Null
  Write-Host "Regra de firewall criada: $ruleName"
}

Write-Host "Porta 5000 liberada para acesso ao OficinaPro."
