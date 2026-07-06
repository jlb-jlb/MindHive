---
type: System
title: Agent Session Startup
description: Startup flow that tells a fresh agent where it is and how to orient in the vault.
tags: [system, agents, startup, orientation]
timestamp: 2026-07-06T00:00:00Z
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

* The vault structure changes.
* The agent operating protocol changes.
* A new required startup document is added.
* The user changes how agents should collaborate with the vault.

# Related

* [Vault Charter](/6-System/vault-charter.md)
* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
* [Agent-Human Collaboration MOC](/5-MOCs/agent-human-collaboration-moc.md)
* [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md)
