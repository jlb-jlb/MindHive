---
type: System
title: Agent Operating Protocol
description: How agents should read, update, verify, and hand off work in this vault.
tags: [system, agents, protocol, handoff]
timestamp: 2026-07-06T00:00:00Z
---

# Read Order

When a task affects this vault, agents should read:

1. [Agent Session Instructions](/AGENTS.md)
2. [Vault Charter](/6-System/vault-charter.md)
3. [Concept Types and Status Vocabulary](/6-System/concept-types.md) when creating or changing frontmatter.
4. The relevant MOC from [MOCs](/5-MOCs/)
5. The specific project, area, or resource notes being changed
6. [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md) when changing structure

# Edit Rules

* Keep concept frontmatter valid.
* Add or update links when relationships change.
* Update the relevant `index.md` when adding a concept to a directory.
* Update the relevant `log.md` when the directory meaningfully changes.
* Prefer small, scoped edits over broad rewrites.
* Preserve user-authored content unless asked to change it.

# Handoff Rules

Create or update a handoff when:

* The work is unfinished.
* The reasoning is not obvious from changed files.
* A future agent needs assumptions, verification, or next actions.

Use [Agent Handoff Template](/3-Resources/Templates/agent-handoff-template.md) and link the handoff from [Decisions and Context MOC](/5-MOCs/decisions-and-context-moc.md).

# Verification

Before finishing structural work, check:

* Run `pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1 -FixIndexes` after adding, moving, or renaming notes.
* Run `pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1` before handing work back when generated indexes should already be current.
* Confirm generated index changes are intentional.
* Confirm important concepts are linked from at least one MOC or generated index.
* Confirm new `type` and `status` values match [Concept Types and Status Vocabulary](/6-System/concept-types.md).

# Related

* [Agent Collaboration Patterns](/3-Resources/agent-collaboration-patterns.md)
* [Context Packet](/3-Resources/context-packet.md)
* [Agent-Human Collaboration](/2-Areas/agent-human-collaboration.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
