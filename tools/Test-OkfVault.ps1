[CmdletBinding()]
param(
  [int]$InboxMaxAgeDays = 7
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Issues = New-Object System.Collections.Generic.List[string]
$AllowedTypes = @(
  "Area",
  "Capture",
  "Decision",
  "Handoff",
  "MOC",
  "Project",
  "Reference",
  "Resource",
  "System",
  "Template"
)
$AllowedStatuses = @(
  "active",
  "paused",
  "done",
  "archived",
  "unprocessed"
)
$AllowedDecisionStatuses = @(
  "accepted",
  "superseded",
  "rejected"
)

function Get-RelativePath {
  param([string]$Path)

  $relative = [System.IO.Path]::GetRelativePath($Root, $Path)
  return ($relative -replace "\\", "/")
}

function Get-ContentRaw {
  param([string]$Path)

  return Get-Content -LiteralPath $Path -Raw
}

function Test-IsRawSkillFile {
  param([string]$RelativePath)

  return $RelativePath -match "^3-Resources/agent-resources/agent-skills/[^/]+/SKILL\.md$"
}

function Get-MarkdownFiles {
  Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.md" |
    Where-Object {
      $relative = Get-RelativePath $_.FullName
      $relative -notmatch "^(?:\.git|\.obsidian|\.github|\.githooks|\.agents|\.codex)/" -and
        -not (Test-IsRawSkillFile $relative)
    }
}

function Parse-Frontmatter {
  param([string]$Text)

  $result = [ordered]@{}
  $match = [regex]::Match($Text, "(?s)^---\s*\r?\n(?<frontmatter>.*?)\r?\n---")
  if (-not $match.Success) {
    return $null
  }

  $frontmatter = $match.Groups["frontmatter"].Value
  foreach ($line in ($frontmatter -split "\r?\n")) {
    if ($line -match "^\s*#" -or $line -notmatch "^\s*([^:]+):\s*(.*)\s*$") {
      continue
    }

    $key = $Matches[1].Trim()
    $value = $Matches[2].Trim()
    $result[$key] = $value.Trim('"').Trim("'")
  }

  return $result
}

function Remove-CodeBlocks {
  param([string]$Text)

  return [regex]::Replace($Text, '(?s)```.*?```', "")
}

function Resolve-MarkdownLink {
  param(
    [System.IO.FileInfo]$SourceFile,
    [string]$Target
  )

  if ($Target -match '^(https?|mailto|obsidian):' -or $Target -match '^#') {
    return $null
  }

  $targetParts = $Target -split '#'
  $targetNoAnchor = $targetParts[0]
  if ([string]::IsNullOrWhiteSpace($targetNoAnchor)) {
    return $null
  }

  $targetNoAnchor = [Uri]::UnescapeDataString($targetNoAnchor)
  if ($targetNoAnchor.StartsWith('/')) {
    return Join-Path $Root ($targetNoAnchor.TrimStart('/'))
  }

  return Join-Path $SourceFile.DirectoryName $targetNoAnchor
}

function Add-Issue {
  param([string]$Message)

  $Issues.Add($Message) | Out-Null
}

$markdownFiles = @(Get-MarkdownFiles | Sort-Object FullName)
$conceptFiles = @()

foreach ($file in $markdownFiles) {
  $relative = Get-RelativePath $file.FullName
  if ($file.Name -in @("index.md", "log.md")) {
    continue
  }

  $conceptFiles += $file
  $text = Get-ContentRaw $file.FullName
  $frontmatter = Parse-Frontmatter $text

  if ($null -eq $frontmatter) {
    Add-Issue "Missing YAML frontmatter: $relative"
    continue
  }

  if (-not $frontmatter.Contains("type") -or [string]::IsNullOrWhiteSpace($frontmatter["type"])) {
    Add-Issue "Missing required frontmatter field 'type': $relative"
  } elseif ($AllowedTypes -notcontains $frontmatter["type"]) {
    Add-Issue "Unknown frontmatter type '$($frontmatter["type"])': $relative"
  }

  if (-not $frontmatter.Contains("description") -or [string]::IsNullOrWhiteSpace($frontmatter["description"])) {
    Add-Issue "Missing recommended frontmatter field 'description': $relative"
  }

  if ($frontmatter.Contains("status") -and $AllowedStatuses -notcontains $frontmatter["status"]) {
    Add-Issue "Unknown frontmatter status '$($frontmatter["status"])': $relative"
  }

  if ($frontmatter.Contains("decision_status") -and $AllowedDecisionStatuses -notcontains $frontmatter["decision_status"]) {
    Add-Issue "Unknown frontmatter decision_status '$($frontmatter["decision_status"])': $relative"
  }
}

$linkedTargets = New-Object "System.Collections.Generic.HashSet[string]"

foreach ($file in $markdownFiles) {
  $text = Remove-CodeBlocks (Get-ContentRaw $file.FullName)
  $matches = [regex]::Matches($text, "\[[^\]]+\]\(([^)]+)\)")

  foreach ($match in $matches) {
    $target = $match.Groups[1].Value.Trim()
    $resolved = Resolve-MarkdownLink $file $target
    if ($null -eq $resolved) {
      continue
    }

    if (-not (Test-Path -LiteralPath $resolved)) {
      Add-Issue "Broken link in $(Get-RelativePath $file.FullName): $target"
      continue
    }

    try {
      $item = Get-Item -LiteralPath $resolved
      if (-not $item.PSIsContainer -and $item.Extension -eq ".md") {
        $linkedTargets.Add((Get-RelativePath $item.FullName)) | Out-Null
      }
    } catch {
      Add-Issue "Could not resolve link in $(Get-RelativePath $file.FullName): $target"
    }
  }
}

$mocAndIndexFiles = @(
  $markdownFiles |
    Where-Object {
      $_.Name -eq "index.md" -or (Get-RelativePath $_.FullName).StartsWith("5-MOCs/")
    }
)

$navigationTargets = New-Object "System.Collections.Generic.HashSet[string]"
foreach ($file in $mocAndIndexFiles) {
  $text = Remove-CodeBlocks (Get-ContentRaw $file.FullName)
  $matches = [regex]::Matches($text, "\[[^\]]+\]\(([^)]+)\)")

  foreach ($match in $matches) {
    $target = $match.Groups[1].Value.Trim()
    $resolved = Resolve-MarkdownLink $file $target
    if ($null -eq $resolved -or -not (Test-Path -LiteralPath $resolved)) {
      continue
    }

    $item = Get-Item -LiteralPath $resolved
    if (-not $item.PSIsContainer -and $item.Extension -eq ".md") {
      $navigationTargets.Add((Get-RelativePath $item.FullName)) | Out-Null
    }
  }
}

foreach ($file in $conceptFiles) {
  $relative = Get-RelativePath $file.FullName
  if ($relative -in @("AGENTS.md")) {
    continue
  }

  if ($relative.StartsWith("5-MOCs/")) {
    continue
  }

  if (-not $navigationTargets.Contains($relative)) {
    Add-Issue "Orphan concept not linked from any MOC or index: $relative"
  }
}

$inboxCutoff = (Get-Date).AddDays(-1 * $InboxMaxAgeDays)
foreach ($file in ($conceptFiles | Where-Object { (Get-RelativePath $_.FullName).StartsWith("0-Inbox/") })) {
  $relative = Get-RelativePath $file.FullName
  $frontmatter = Parse-Frontmatter (Get-ContentRaw $file.FullName)
  if ($null -eq $frontmatter) {
    continue
  }

  $status = if ($frontmatter.Contains("status")) { $frontmatter["status"] } else { "unprocessed" }
  if ($status -ne "unprocessed") {
    continue
  }

  if (-not $frontmatter.Contains("timestamp")) {
    Add-Issue "Inbox item has no timestamp for stale check: $relative"
    continue
  }

  $timestamp = [datetimeoffset]::MinValue
  if (-not [datetimeoffset]::TryParse($frontmatter["timestamp"], [ref]$timestamp)) {
    Add-Issue "Inbox item has invalid timestamp: $relative"
    continue
  }

  if ($timestamp.DateTime -lt $inboxCutoff) {
    Add-Issue "Stale Inbox item older than $InboxMaxAgeDays days: $relative"
  }
}

if ($Issues.Count -gt 0) {
  Write-Error ("OKF vault checks failed:`n" + (($Issues | ForEach-Object { " - $_" }) -join "`n"))
}

Write-Host "OKF vault checks passed"
