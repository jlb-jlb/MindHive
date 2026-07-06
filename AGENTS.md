---
type: System
title: Agent Session Instructions
description: First-read instructions for any agent starting a new session in MindHive.
tags: [system, agents, startup, instructions]
timestamp: 2026-07-06T00:00:00Z
---

# Agent Session Instructions

You are in `MindHive`, an Obsidian workspace and OKF knowledge bundle for shared human and agent knowledge work.

Read this file first at the start of a new session.

# Immediate Orientation

1. Open [index.md](/index.md) for the bundle entrypoint.
2. Open [MindHive MOC](/5-MOCs/second-brain-moc.md) for top-level navigation.
3. Open [Agent-Human Collaboration MOC](/5-MOCs/agent-human-collaboration-moc.md) when the task involves handoff, decisions, context, or shared work.
4. Open [Agent Operating Protocol](/6-System/agent-operating-protocol.md) before editing the vault.
5. Open [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md) before changing structure.

# What This Vault Is

This vault uses:

* **OKF** for portable Markdown concepts with YAML frontmatter.
* **PARA** for organization: [Projects](/1-Projects/), [Areas](/2-Areas/), [Resources](/3-Resources/), [Archive](/4-Archive/).
* **MOCs** for navigation and linked thinking: [MOCs](/5-MOCs/).
* **Obsidian** as the human workspace.

# Folder Meaning

| Folder | Meaning |
|---|---|
| `1-Projects/` | Active outcomes with a finish line. |
| `2-Areas/` | Ongoing responsibilities and standards. |
| `3-Resources/` | Reusable knowledge, templates, methods, and references. |
| `4-Archive/` | Inactive or completed material kept for history. |
| `0-Inbox/` | Unprocessed captures awaiting review. |
| `5-MOCs/` | Maps of Content for navigation and sensemaking. |
| `6-System/` | Operating rules for humans, agents, and the vault itself. |
| `.obsidian/` | Obsidian workspace settings and the local theme. |

# Editing Rules

* Every normal Markdown concept must have YAML frontmatter with a non-empty `type`.
* `index.md` files are directory maps and normally do not need frontmatter except the root bundle index.
* `log.md` files record directory update history.
* Use bundle-relative links such as `[Linked Thinking](/3-Resources/linked-thinking.md)`.
* Update the relevant `index.md`, MOC, and `log.md` when adding or materially changing a concept.
* Preserve [OKF Specification](/3-Resources/okf-specification.md) as the baseline reference; do not rewrite the copied spec text.

# How To Handle Work

When the user asks for a change:

1. Identify whether it is a project, area, resource, system rule, capture, or archive item.
2. Read the relevant MOC before editing.
3. Make the smallest coherent change that keeps the vault navigable.
4. Link the new or changed concept from at least one MOC.
5. Record decisions when future humans or agents would need to understand why.
6. Run a quick conformance check when structure changes.

# Handoff

If work remains unfinished or context may be lost, create or update a handoff using [Agent Handoff Template](/3-Resources/Templates/agent-handoff-template.md), then link it from [Decisions and Context MOC](/5-MOCs/decisions-and-context-moc.md).

# Key Rules To Remember

* Do not rely on hidden chat context when a note should preserve it.
* Do not create isolated notes without links.
* Do not move material into PARA folders without clarifying why it belongs there.
* Do not treat MOCs as simple file lists; they should explain relationships.
* Keep this file short enough that a fresh agent can read it immediately.
