---
type: System
title: MindHive README
description: GitHub-facing entrypoint for the MindHive vault.
tags: [system, readme, second-brain]
timestamp: 2026-07-06T00:00:00Z
---

# MindHive

MindHive is an Obsidian workspace and OKF knowledge bundle for shared human and agent knowledge work.

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

# Using This Template

1. Create your own repository from this one (GitHub "Use this template", or clone and replace the remote).
2. Open the folder as an Obsidian vault. The two local plugins and the Ruby Second Brain theme ship in `.obsidian/`.
3. Install the git hook once with `pwsh -NoProfile -File _tools/Install-GitHooks.ps1`.
4. For agent use, install [uv](https://docs.astral.sh/uv/). The Claude Code Stop hook in `.claude/settings.json` runs the session linter in `_tools/automation/`.
5. Start a session with your agent. `CLAUDE.md` and `AGENTS.md` are identical copies, so Claude Code and other agent tools read the same first-read instructions. Edit them together.
6. Replace the placeholder entries in [Current Focus](5-MOCs/current-focus.md) with your own priorities.

# Validation

Run the local checks before committing structural changes:

```powershell
pwsh -NoProfile -File _tools/Invoke-OkfChecks.ps1
```

After adding, moving, or renaming notes, regenerate generated indexes as part of the same portable check sequence:

```powershell
pwsh -NoProfile -File _tools/Invoke-OkfChecks.ps1 -FixIndexes
```

The pre-commit hook and GitHub Actions workflow use the same PowerShell 7+ runner on Windows, macOS, and Linux.
