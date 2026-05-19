$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$launcherDir = Join-Path $PSScriptRoot "launcher"
$pythonLauncher = Join-Path $launcherDir "OficinaProNuitkaLauncher.py"
$csharpLauncher = Join-Path $launcherDir "OficinaProLauncher.cs"
$outputExe = Join-Path $PSScriptRoot "OficinaPro.exe"
$buildDir = Join-Path $PSScriptRoot "build"
$pyarmorDir = Join-Path $buildDir "pyarmor"
$nuitkaSource = $pythonLauncher

Write-Host "OficinaPro - Build de executavel standalone"
Write-Host "==========================================="

function Test-Command($name) {
  $command = Get-Command $name -ErrorAction SilentlyContinue
  return $null -ne $command
}

function Get-CscPath {
  $candidates = @(
    "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
  )

  foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
      return $candidate
    }
  }

  return $null
}

$builtWith = $null
$protectionSteps = @()

if (Test-Command "nuitka") {
  if (Test-Command "pyarmor") {
    Write-Host "PyArmor encontrado. Ofuscando launcher Python antes do Nuitka..."
    if (Test-Path $pyarmorDir) {
      Remove-Item $pyarmorDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $pyarmorDir -Force | Out-Null
    pyarmor gen --output "$pyarmorDir" "$pythonLauncher"
    $nuitkaSource = Join-Path $pyarmorDir "OficinaProNuitkaLauncher.py"
    $protectionSteps += "PyArmor"
  } else {
    Write-Host "PyArmor nao encontrado. Build Nuitka seguira sem ofuscacao PyArmor."
  }

  Write-Host "Nuitka encontrado. Compilando launcher Python..."
  $nuitkaArgs = @(
    "--standalone",
    "--onefile",
    "--assume-yes-for-downloads",
    "--output-filename=OficinaPro.exe",
    "--output-dir=$PSScriptRoot"
  )

  $nuitkaArgs += "$nuitkaSource"
  nuitka @nuitkaArgs
  $builtWith = "Nuitka"
} else {
  Write-Host "Nuitka nao encontrado. Usando fallback C# com .NET Framework."
  $csc = Get-CscPath
  if (-not $csc) {
    throw "Nao foi encontrado Nuitka nem compilador C# do .NET Framework."
  }

  & $csc /nologo /target:exe /out:"$outputExe" "$csharpLauncher"
  $builtWith = "C#/.NET Framework"
}

if (-not (Test-Path $outputExe)) {
  throw "Falha no build: $outputExe nao foi gerado."
}

Write-Host "Executavel gerado: $outputExe"
Write-Host "Metodo de build: $builtWith"
if ($protectionSteps.Count -gt 0) {
  Write-Host "Etapas adicionais: $($protectionSteps -join ', ')"
} else {
  Write-Host "Etapas adicionais de protecao nao aplicadas."
  Write-Host "Instale PyArmor e Nuitka para ofuscacao/compilacao, e UPX para compactacao opcional."
}

if ((Test-Command "upx") -and (Test-Path $outputExe)) {
  Write-Host "UPX encontrado. Compactando executavel..."
  upx --best --lzma "$outputExe"
  $protectionSteps += "UPX"
}

Write-Host "Build concluido."
