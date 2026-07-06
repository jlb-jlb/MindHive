---
type: System
title: Vault Automation
description: Enforcement and generation tooling for the MindHive OKF bundle.
tags: [system, automation, okf, linting]
timestamp: 2026-07-06T00:00:00Z
---

# Purpose

The vault has executable checks so its conventions do not depend only on memory.

# Tools

* [Update OKF Indexes](/tools/Update-OkfIndexes.ps1) - Regenerates marked sections in `index.md` files and rewrites the generated [Tag Index](/3-Resources/tag-index.md).
* [Test OKF Vault](/tools/Test-OkfVault.ps1) - Checks frontmatter, controlled `type` and `status` values, `description`, links, orphan concepts, and stale Inbox items.
* [Test OKF Commit](/tools/Test-OkfCommit.ps1) - Checks staged changes and blocks new or moved concept files unless a nearby `log.md` update is staged too.
* [Invoke OKF Checks](/tools/Invoke-OkfChecks.ps1) - Runs the canonical check sequence through PowerShell 7+ on Windows, macOS, and Linux.
* [Install Git Hooks](/tools/Install-GitHooks.ps1) - Configures Git to use the versioned hook in `.githooks`.

# Runtime Contract

Vault automation is operating-system agnostic through PowerShell 7+ (`pwsh`). Do not rely on Windows PowerShell, shell-specific path separators, or hidden editor behavior for canonical checks.

Run the canonical check sequence with:

```powershell
pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1
```

After adding, moving, or renaming notes, regenerate generated indexes first:

```powershell
pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1 -FixIndexes
```

# Git Hook

The versioned pre-commit hook lives at `/.githooks/pre-commit`.

The hook blocks commits when a staged new or moved concept file does not have a staged `log.md` update in the same directory or an ancestor directory. The failure message names the concept file, suggests the nearest log file, and gives a copyable example entry so a human or agent can repair the commit without hidden context.

Install it with:

```powershell
pwsh -NoProfile -File tools/Install-GitHooks.ps1
```

# CI

GitHub Actions runs the same portable check runner through [OKF Vault workflow](/.github/workflows/okf-vault.yml). The staged-change log guard is meaningful in the local pre-commit hook because CI does not have the developer's staged index.

# Related

* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
* [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md)
* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
