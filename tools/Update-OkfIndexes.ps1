[CmdletBinding()]
param(
  [switch]$Check
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$GeneratedStart = "<!-- BEGIN GENERATED INDEX -->"
$GeneratedEnd = "<!-- END GENERATED INDEX -->"

function Get-RelativePath {
  param([string]$Path)

  $relative = [System.IO.Path]::GetRelativePath($Root, $Path)
  return ($relative -replace "\\", "/")
}

function Convert-ToMarkdownUrl {
  param([string]$Path)

  return (($Path -replace "\\", "/") -replace " ", "%20")
}

function Test-IsRawSkillFile {
  param([string]$RelativePath)

  return $RelativePath -match "^3-Resources/agent-skills/[^/]+/SKILL\.md$"
}

function Test-IsSkillArtifactDirectory {
  param([string]$RelativePath)

  return $RelativePath -match "^3-Resources/agent-skills/[^/]+$"
}

function Get-MarkdownFiles {
  Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.md" |
    Where-Object {
      $relative = Get-RelativePath $_.FullName
      $relative -notmatch "^(?:\.git|\.obsidian|\.github|\.githooks|\.agents|\.codex)/" -and
        -not (Test-IsRawSkillFile $relative)
    }
}

function Get-ContentRaw {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return ""
  }

  return Get-Content -LiteralPath $Path -Raw
}

function Parse-Frontmatter {
  param([string]$Text)

  $result = [ordered]@{}
  $match = [regex]::Match($Text, "(?s)^---\s*\r?\n(?<frontmatter>.*?)\r?\n---")
  if (-not $match.Success) {
    return $result
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

function Get-ConceptTitle {
  param(
    [System.IO.FileInfo]$File,
    [hashtable]$Frontmatter
  )

  if ($Frontmatter.Contains("title") -and -not [string]::IsNullOrWhiteSpace($Frontmatter["title"])) {
    return $Frontmatter["title"]
  }

  return [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
}

function Get-ConceptDescription {
  param([hashtable]$Frontmatter)

  if ($Frontmatter.Contains("description") -and -not [string]::IsNullOrWhiteSpace($Frontmatter["description"])) {
    return $Frontmatter["description"]
  }

  return "No description."
}

function Get-Tags {
  param([hashtable]$Frontmatter)

  if (-not $Frontmatter.Contains("tags")) {
    return @()
  }

  $raw = $Frontmatter["tags"].Trim()
  if ($raw.StartsWith("[") -and $raw.EndsWith("]")) {
    $raw = $raw.Substring(1, $raw.Length - 2)
  }

  return @(
    $raw -split "," |
      ForEach-Object { $_.Trim().Trim('"').Trim("'") } |
      Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
  )
}

function Set-GeneratedBlock {
  param(
    [string]$Existing,
    [string]$Generated
  )

  $block = "$GeneratedStart`n$Generated`n$GeneratedEnd"
  $pattern = "(?s)" + [regex]::Escape($GeneratedStart) + ".*?" + [regex]::Escape($GeneratedEnd)

  if ($Existing -match $pattern) {
    return [regex]::Replace($Existing, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block })
  }

  $trimmed = $Existing.TrimEnd()
  if ([string]::IsNullOrWhiteSpace($trimmed)) {
    return "$block`n"
  }

  return "$trimmed`n`n$block`n"
}

function Get-IndexGeneratedContent {
  param([System.IO.DirectoryInfo]$Directory)

  $relativeDir = Get-RelativePath $Directory.FullName
  if ($relativeDir -eq ".") {
    $heading = "Generated Bundle Contents"
  } else {
    $heading = "Generated Directory Contents"
  }

  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add("# $heading")
  $lines.Add("")

  $subdirectories = Get-ChildItem -LiteralPath $Directory.FullName -Directory |
    Where-Object { $_.Name -notin @(".git", ".obsidian", ".github", ".githooks", ".agents", ".codex") } |
    Sort-Object Name

  $conceptFiles = Get-ChildItem -LiteralPath $Directory.FullName -File -Filter "*.md" |
    Where-Object {
      $relative = Get-RelativePath $_.FullName
      $_.Name -notin @("index.md", "log.md") -and -not (Test-IsRawSkillFile $relative)
    } |
    Sort-Object Name

  if ($subdirectories.Count -eq 0 -and $conceptFiles.Count -eq 0) {
    $lines.Add("No concepts or subdirectories currently live in this directory.")
    return ($lines -join "`n")
  }

  if ($subdirectories.Count -gt 0) {
    $lines.Add("## Subdirectories")
    $lines.Add("")
    foreach ($subdirectory in $subdirectories) {
      $url = Convert-ToMarkdownUrl "$($subdirectory.Name)/"
      $lines.Add("* [$($subdirectory.Name)]($url)")
    }
    $lines.Add("")
  }

  if ($conceptFiles.Count -gt 0) {
    $lines.Add("## Concepts")
    $lines.Add("")
    foreach ($file in $conceptFiles) {
      $frontmatter = Parse-Frontmatter (Get-ContentRaw $file.FullName)
      $title = Get-ConceptTitle $file $frontmatter
      $description = Get-ConceptDescription $frontmatter
      $url = Convert-ToMarkdownUrl $file.Name
      $lines.Add("* [$title]($url) - $description")
    }
  }

  return ($lines -join "`n")
}

function Get-TagIndexContent {
  $concepts = New-Object System.Collections.Generic.List[object]

  foreach ($file in (Get-MarkdownFiles | Sort-Object FullName)) {
    if ($file.Name -in @("index.md", "log.md")) {
      continue
    }

    if ((Get-RelativePath $file.FullName) -eq "3-Resources/tag-index.md") {
      continue
    }

    $frontmatter = Parse-Frontmatter (Get-ContentRaw $file.FullName)
    $tags = Get-Tags $frontmatter
    if ($tags.Count -eq 0) {
      continue
    }

    $concepts.Add([pscustomobject]@{
      File = $file
      RelativePath = Get-RelativePath $file.FullName
      Title = Get-ConceptTitle $file $frontmatter
      Type = if ($frontmatter.Contains("type")) { $frontmatter["type"] } else { "Unknown" }
      Tags = $tags
    })
  }

  $tagMap = [ordered]@{}
  foreach ($concept in $concepts) {
    foreach ($tag in $concept.Tags) {
      if (-not $tagMap.Contains($tag)) {
        $tagMap[$tag] = New-Object System.Collections.Generic.List[object]
      }
      $tagMap[$tag].Add($concept)
    }
  }

  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add("---")
  $lines.Add("type: Resource")
  $lines.Add("title: Tag Index")
  $lines.Add("description: Generated index of tags used across the vault.")
  $lines.Add("tags: [resource, tags, index, generated]")
  $lines.Add("---")
  $lines.Add("")
  $lines.Add("# Tag Index")
  $lines.Add("")
  $lines.Add("This file is generated by [Update-OkfIndexes.ps1](/tools/Update-OkfIndexes.ps1).")
  $lines.Add("")

  foreach ($tag in ($tagMap.Keys | Sort-Object)) {
    $lines.Add("## $tag")
    $lines.Add("")

    foreach ($concept in ($tagMap[$tag] | Sort-Object RelativePath)) {
      $url = "/" + (Convert-ToMarkdownUrl $concept.RelativePath)
      $lines.Add("* [$($concept.Title)]($url) - $($concept.Type)")
    }
    $lines.Add("")
  }

  return (($lines -join "`n").TrimEnd() + "`n")
}

$plannedWrites = New-Object System.Collections.Generic.List[object]

$directories = Get-ChildItem -LiteralPath $Root -Recurse -Directory |
  Where-Object {
    $relative = Get-RelativePath $_.FullName
    $relative -notmatch "^(?:\.git|\.obsidian|\.github|\.githooks|\.agents|\.codex)(?:/|$)" -and
      -not (Test-IsSkillArtifactDirectory $relative)
  }

$allDirectories = @((Get-Item -LiteralPath $Root)) + @($directories)

foreach ($directory in $allDirectories) {
  $hasMarkdown = (Get-ChildItem -LiteralPath $directory.FullName -File -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0
  $hasChildDirectory = (Get-ChildItem -LiteralPath $directory.FullName -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notin @(".git", ".obsidian", ".github", ".githooks", ".agents", ".codex") } |
    Measure-Object).Count -gt 0

  if (-not $hasMarkdown -and -not $hasChildDirectory) {
    continue
  }

  $indexPath = Join-Path $directory.FullName "index.md"
  $existing = Get-ContentRaw $indexPath
  $generated = Get-IndexGeneratedContent $directory
  $updated = Set-GeneratedBlock $existing $generated

  $plannedWrites.Add([pscustomobject]@{
    Path = $indexPath
    Content = $updated
  })
}

$tagIndexPath = Join-Path $Root "3-Resources/tag-index.md"
$plannedWrites.Add([pscustomobject]@{
  Path = $tagIndexPath
  Content = Get-TagIndexContent
})

$differences = New-Object System.Collections.Generic.List[string]

foreach ($write in $plannedWrites) {
  $current = Get-ContentRaw $write.Path
  if ($current -ne $write.Content) {
    $differences.Add((Get-RelativePath $write.Path))
    if (-not $Check) {
      $parent = Split-Path -Parent $write.Path
      if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
      }
      Set-Content -LiteralPath $write.Path -Value $write.Content -NoNewline -Encoding utf8
    }
  }
}

if ($Check) {
  if ($differences.Count -gt 0) {
    Write-Error ("Generated indexes are stale. Run: pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1 -FixIndexes`nStale files:`n" + (($differences | ForEach-Object { " - $_" }) -join "`n"))
  }

  Write-Host "Generated index check passed"
  exit 0
}

if ($differences.Count -eq 0) {
  Write-Host "Generated indexes already up to date"
} else {
  Write-Host "Updated generated indexes:"
  $differences | ForEach-Object { Write-Host " - $_" }
}
