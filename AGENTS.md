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

# Grow This Workspace Organically (Explicit Standing Instruction)

**Whenever you generate, synthesize, or discover knowledge in the course of a task, capture it as a durable note in this vault before ending the turn.** This workspace is meant to grow organically as a living second brain, not to stay static between explicit "write a note" requests.

This applies to knowledge produced as a *byproduct* of any work, not only when the user says "save this." Concretely, capture:

* **Synthesized understanding** — conclusions, models, or explanations you worked out that took real effort to reach and would cost effort to re-derive.
* **How-tos and procedures** — repeatable steps you figured out (a setup, a workflow, a fix, a command sequence).
* **Decisions and their rationale** — what was chosen, what was rejected, and why (so future humans and agents understand the "why").
* **References discovered** — useful external sources, tools, or resources encountered while working.
* **Reusable methods and patterns** — anything general enough to help on future tasks.

Rules for organic growth:

1. **Default to capture.** When in doubt about whether something is worth keeping, write a short note rather than letting it evaporate. A small linked note is better than lost knowledge.
2. **Place it correctly** using PARA and the [Folder Meaning](#folder-meaning) table: how-tos, methods, and references → `3-Resources/`; project-specific outcomes → `1-Projects/`; standing responsibilities → `2-Areas/`; operating rules → `6-System/`; raw unprocessed captures → `0-Inbox/`.
3. **Never orphan a note.** Give it OKF frontmatter with a non-empty `type`, link it from at least one MOC, and link it to related concepts. Follow the [Editing Rules](#editing-rules) and [Naming and Linking Rules](/6-System/naming-and-linking-rules.md).
4. **Update the surrounding structure** — the relevant `index.md`, MOC, and `log.md` — so the new knowledge is discoverable, exactly as you would for a requested note.
5. **Prefer growing an existing note** over creating a near-duplicate. If a note already covers the topic, extend or refine it and record the update in `log.md`.
6. **Keep it self-contained.** Do not rely on hidden chat context; write down what a future reader would need.

Do this proactively and briefly tell the user what you captured and where. If a capture would be large or ambiguous in placement, drop a quick note in `0-Inbox/` and flag it for review rather than skipping it.

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
