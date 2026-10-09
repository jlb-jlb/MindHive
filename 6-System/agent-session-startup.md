---
type: System
title: Agent Session Startup
description: Startup flow that tells a fresh agent where it is and how to orient in the vault, the four triggers for updating the instructions file, and the rule that AGENTS.md and CLAUDE.md are copies that must be edited together.
tags: [system, agents, startup, orientation]
timestamp: 2026-08-12T00:00:00Z
resource: /AGENTS.md
---

# Purpose

A fresh agent needs a stable first-read file that explains where it is, what the vault is for, and which notes to open next.

# First-Read File

Use [Agent Session Instructions](/AGENTS.md) as the filesystem-level entrypoint for new agent sessions.

# Startup Flow

1. Read [Agent Session Instructions](/AGENTS.md).
2. Read [MindHive](/index.md).
3. Read [MindHive MOC](/5-MOCs/second-brain-moc.md).
4. Read [Agent-Human Collaboration MOC](/5-MOCs/agent-human-collaboration-moc.md) when shared work is involved.
5. Read [Agent Operating Protocol](/6-System/agent-operating-protocol.md) before editing.

# Maintenance

Update [Agent Session Instructions](/AGENTS.md) whenever:

* The vault structure changes. A new top-level folder belongs in the Folder Meaning table.
* The agent operating protocol changes.
* A new required startup document is added.
* The user changes how agents should collaborate with the vault.

# The Instructions Live in Two Files

`/CLAUDE.md` is a copy of `/AGENTS.md`, kept because Claude Code reads only that name while other
agent tools read only the other. Every edit above goes into both files in the same change.

Nothing compares them, so this drift is silent. [Test-OkfVault.ps1](/_tools/Test-OkfVault.ps1)
checks frontmatter and links inside each file and never checks one file against another, and
Obsidian's table formatter rewrites the copy a human opens, which makes the two differ without
anyone editing content. On 2026-08-12 the Folder Meaning table turned out to be missing five real
folders, `7-Journal/`, `_attachments/`, `_tools/`, `.githooks/`, and `.github/`, with `7-Journal/`
having existed since 2026-07-09. Both files were rewritten and reconciled.

# Related

* [Vault Charter](/6-System/vault-charter.md)
* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
* [Agent-Human Collaboration MOC](/5-MOCs/agent-human-collaboration-moc.md)
* [OKF Bundle Practice](/6-System/okf-bundle-practice.md)
