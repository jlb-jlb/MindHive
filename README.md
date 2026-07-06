---
type: System
title: MindHive README
description: GitHub-facing entrypoint for the MindHive vault.
tags: [system, readme, second-brain]
timestamp: 2026-07-06T00:00:00Z
---

# MindHive

MindHive is an Obsidian workspace and OKF knowledge bundle for shared human and agent knowledge work.

This public branch is a publishable version of the vault scaffold: it includes the
structure, operating rules, templates, example resources, automation, and public
Obsidian settings, but not private workspace state or personal project history.

Start with:

* [Vault Index](index.md) - Main bundle entrypoint.
* [Agent Session Instructions](AGENTS.md) - First-read instructions for new agent sessions.
* [MindHive MOC](5-MOCs/second-brain-moc.md) - Top-level navigation map.
* [Current Focus](5-MOCs/current-focus.md) - Active priorities and next useful moves.
* [Agent-Human Collaboration MOC](5-MOCs/agent-human-collaboration-moc.md) - Shared work, handoff, and context map.

# Structure

| Folder                      | Purpose                                                 |
| --------------------------- | ------------------------------------------------------- |
| [0-Inbox](0-Inbox/)         | Unprocessed captures.                                   |
| [1-Projects](1-Projects/)   | Active outcomes with a finish line.                     |
| [2-Areas](2-Areas/)         | Ongoing responsibilities and standards.                 |
| [3-Resources](3-Resources/) | Reusable knowledge, references, methods, and templates. |
| [4-Archive](4-Archive/)     | Inactive material retained for history.                 |
| [5-MOCs](5-MOCs/)           | Maps of Content for navigation and linked thinking.     |
| [6-System](6-System/)       | Operating rules for the vault, humans, and agents.      |

# Validation

Run the local checks before committing structural changes:

```powershell
pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1
```

After adding, moving, or renaming notes, regenerate generated indexes as part of the same portable check sequence:

```powershell
pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1 -FixIndexes
```

The pre-commit hook and GitHub Actions workflow use the same PowerShell 7+ runner on Windows, macOS, and Linux.
