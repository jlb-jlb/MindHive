[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Issues = New-Object System.Collections.Generic.List[object]

function Convert-ToSlashPath {
  param([string]$Path)

  return ($Path -replace "\\", "/")
}

function Test-IsIgnoredPath {
  param([string]$RelativePath)

  return $RelativePath -match "^(?:\.git|\.obsidian|\.github|\.githooks|\.agents|\.codex)(?:/|$)"
}

function Test-IsRawSkillFile {
  param([string]$RelativePath)

  return $RelativePath -match "^3-Resources/agent-skills/[^/]+/SKILL\.md$"
}

function Test-IsConceptFile {
  param([string]$RelativePath)

  if (Test-IsIgnoredPath $RelativePath) {
    return $false
  }

  if ($RelativePath -notmatch "\.md$") {
    return $false
  }

  $name = Split-Path -Leaf $RelativePath
  if ($name -in @("index.md", "log.md")) {
    return $false
  }

  if (Test-IsRawSkillFile $RelativePath) {
    return $false
  }

  return $true
}

function Get-LogCandidates {
  param([string]$RelativePath)

  $candidates = New-Object System.Collections.Generic.List[string]
  $directory = Convert-ToSlashPath (Split-Path -Parent $RelativePath)

  while (-not [string]::IsNullOrWhiteSpace($directory)) {
    $candidates.Add("$directory/log.md") | Out-Null
    $parent = Convert-ToSlashPath (Split-Path -Parent $directory)
    if ($parent -eq $directory) {
      break
    }
    $directory = $parent
  }

  $candidates.Add("log.md") | Out-Null
  return $candidates
}

function Parse-StagedNameStatus {
  $lines = & git -C $Root diff --cached --name-status --diff-filter=ACR -- .
  foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
      continue
    }

    $parts = $line -split "`t"
    $status = $parts[0]

    if ($status -match "^[RC]" -and $parts.Count -ge 3) {
      [pscustomobject]@{
        Status = $status
        Path = Convert-ToSlashPath $parts[2]
      }
      continue
    }

    if ($parts.Count -ge 2) {
      [pscustomobject]@{
        Status = $status
        Path = Convert-ToSlashPath $parts[1]
      }
    }
  }
}

$stagedLogs = New-Object "System.Collections.Generic.HashSet[string]"
$stagedChangedFiles = & git -C $Root diff --cached --name-only --diff-filter=ACMR -- .
foreach ($path in $stagedChangedFiles) {
  $relativePath = Convert-ToSlashPath $path
  if ((Split-Path -Leaf $relativePath) -eq "log.md") {
    $stagedLogs.Add($relativePath) | Out-Null
  }
}

foreach ($change in (Parse-StagedNameStatus)) {
  if (-not (Test-IsConceptFile $change.Path)) {
    continue
  }

  $candidates = @(Get-LogCandidates $change.Path)
  $hasNearbyLog = $false
  foreach ($candidate in $candidates) {
    if ($stagedLogs.Contains($candidate)) {
      $hasNearbyLog = $true
      break
    }
  }

  if (-not $hasNearbyLog) {
    $Issues.Add([pscustomobject]@{
      Path = $change.Path
      Status = $change.Status
      SuggestedLog = $candidates[0]
      AcceptedLogs = $candidates
    }) | Out-Null
  }
}

if ($Issues.Count -gt 0) {
  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add("OKF commit checks failed: new or moved concept files need a staged log.md update.")
  $lines.Add("")
  $lines.Add("What to do:")
  $lines.Add("1. Add a short dated entry to the nearest relevant log.md explaining why each file was added or moved.")
  $lines.Add("2. Stage that log.md file with the concept change.")
  $lines.Add("3. Commit again.")
  $lines.Add("")
  $lines.Add("Missing staged log coverage:")

  foreach ($issue in $Issues) {
    $lines.Add(" - $($issue.Path) [$($issue.Status)]")
    $lines.Add("   Suggested log: $($issue.SuggestedLog)")
    $otherLogs = @($issue.AcceptedLogs | Select-Object -Skip 1)
    if ($otherLogs.Count -gt 0) {
      $lines.Add("   Also accepted: $($otherLogs -join ', ')")
    }
  }

  $lines.Add("")
  $lines.Add("Example log entry:")
  $lines.Add("## $(Get-Date -Format 'yyyy-MM-dd')")
  $lines.Add("* **Creation**: Added [Title](/path/to/file.md) to capture the new concept and keep the vault navigable.")

  [Console]::Error.WriteLine(($lines -join [Environment]::NewLine))
  exit 1
}

Write-Host "OKF commit checks passed"
