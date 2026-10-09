[CmdletBinding()]
param(
  [switch]$FixIndexes,
  [switch]$SkipCommitCheck
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$indexScript = Join-Path $PSScriptRoot "Update-OkfIndexes.ps1"
$vaultScript = Join-Path $PSScriptRoot "Test-OkfVault.ps1"
$commitScript = Join-Path $PSScriptRoot "Test-OkfCommit.ps1"

Push-Location $Root
try {
  if ($FixIndexes) {
    & $indexScript
  } else {
    & $indexScript -Check
  }

  & $vaultScript

  if (-not $SkipCommitCheck) {
    & $commitScript
  }
} finally {
  Pop-Location
}

