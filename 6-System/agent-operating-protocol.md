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

# Organic Growth (Capture Byproduct Knowledge)

Grow this vault as a living second brain. When a task produces durable knowledge as a byproduct — synthesized understanding, a how-to or procedure, a decision and its rationale, a discovered reference, or a reusable method — capture it as a linked note before ending the turn, not only when the user explicitly asks. Default to capture when unsure; a small linked note beats lost knowledge.

* Place it by PARA: how-tos, methods, references → `3-Resources/`; project outcomes → `1-Projects/`; standing responsibilities → `2-Areas/`; operating rules → `6-System/`; ambiguous or raw captures → `0-Inbox/` flagged for review.
* Never orphan it: valid frontmatter, at least one MOC link, links to related concepts, and updated `index.md` / MOC / `log.md`.
* Prefer extending an existing note over creating a near-duplicate.
* Briefly tell the user what you captured and where.

This is the operating-level restatement of the standing instruction in [Agent Session Instructions](/AGENTS.md#grow-this-workspace-organically-explicit-standing-instruction).

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

* [Agent Collaboration Patterns](/3-Resources/agent-resources/agent-collaboration-patterns.md)
* [Context Packet](/3-Resources/agent-resources/context-packet.md)
* [Agent-Human Collaboration](/2-Areas/agent-human-collaboration.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
