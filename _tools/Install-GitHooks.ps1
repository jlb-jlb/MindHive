[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$hookPath = Join-Path $root ".githooks/pre-commit"
Push-Location $root
try {
  $current = git config --get core.hooksPath
  if ($LASTEXITCODE -eq 0 -and $current -eq ".githooks") {
    Write-Host "Git core.hooksPath is already .githooks"
  } else {
    git config --local core.hooksPath .githooks
    if ($LASTEXITCODE -ne 0) {
      throw "Failed to configure git core.hooksPath. If Git reports dubious ownership, add this repository to safe.directory first."
    }

    Write-Host "Configured git core.hooksPath=.githooks"
  }

  $runningOnWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)
  if (-not $runningOnWindows) {
    & chmod +x $hookPath
    if ($LASTEXITCODE -ne 0) {
      throw "Failed to mark .githooks/pre-commit as executable."
    }
  }
} finally {
  Pop-Location
}
