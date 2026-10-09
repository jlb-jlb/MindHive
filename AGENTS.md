---
type: System
title: Agent Session Instructions
description: First-read instructions for any agent starting a new session in MindHive, covering the orientation reading order, the standing capture rule, the folder meaning table for every top-level directory, the editing rules, and the frontmatter contract.
tags: [system, agents, startup, instructions]
timestamp: 2026-08-12T00:00:00Z
---

# Agent Session Instructions

You are in `MindHive`, an Obsidian workspace and OKF knowledge bundle for shared human and agent knowledge work.

Read this file first at the start of a new session.

`AGENTS.md` and `CLAUDE.md` are two copies of this same file, because Claude Code reads only
`CLAUDE.md` while other agent tools read only `AGENTS.md`. Any edit to one has to be made to the
other in the same change. The vault checks do not catch the drift, so nothing else will remind you.

# Immediate Orientation

1. Open [index.md](/index.md) for the bundle entrypoint.
2. Open [MindHive MOC](/5-MOCs/second-brain-moc.md) for top-level navigation.
3. Open [Agent-Human Collaboration MOC](/5-MOCs/agent-human-collaboration-moc.md) when the task involves handoff, decisions, context, or shared work.
4. Open [Agent Operating Protocol](/6-System/agent-operating-protocol.md) before editing the vault.
5. Open [OKF Bundle Practice](/6-System/okf-bundle-practice.md) before changing structure.

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

The numbered folders hold notes and are where your work goes. The rest is infrastructure, and a
task should only touch it when the task is explicitly about tooling or workspace setup.
A leading `_` marks infrastructure: the vault checks skip those folders and the Obsidian
explorer hides them. See [Naming and Linking Rules](/6-System/naming-and-linking-rules.md).

| Folder | Meaning |
|---|---|
| `0-Inbox/` | Unprocessed captures awaiting review. |
| `1-Projects/` | Active outcomes with a finish line. |
| `2-Areas/` | Ongoing responsibilities and standards. |
| `3-Resources/` | Reusable knowledge, templates, methods, and references. |
| `4-Archive/` | Inactive or completed material kept for history. |
| `5-MOCs/` | Maps of Content for navigation and sensemaking. |
| `6-System/` | Operating rules for humans, agents, and the vault itself. |
| `7-Journal/` | Dated daily notes for logs, reflections, and running thoughts. |
| `_attachments/` | Images, PDFs, and other binaries referenced by notes. Never put Markdown here. |
| `_templates/` | Raw note skeletons the Obsidian Templates plugin inserts with Ctrl+P. Skipped by the checks. The agent-facing template docs stay in `3-Resources/Templates/`. See [Obsidian Insertable Templates](/3-Resources/wiki/obsidian-insertable-templates.md). |
| `_tools/` | The PowerShell check scripts and the `automation/` Python project behind the Stop-hook linter. See [Vault Automation](/6-System/vault-automation.md). |
| `.githooks/` | The versioned pre-commit hook, installed with `_tools/Install-GitHooks.ps1`. |
| `.github/` | CI workflow running the same checks as the local hook. |
| `.obsidian/` | Obsidian workspace settings, the local theme, and the two local plugins. |
| `.claude/`, `.agents/`, `.codex/` | Per-tool agent configuration. `.claude/settings.json` is committed and carries the Stop hook. `settings.local.json` is personal and ignored. |

# Editing Rules

* Every normal Markdown concept must have YAML frontmatter with a non-empty `type`.
* `index.md` files are directory maps and carry frontmatter with a `description` like every other file. See [Frontmatter Contract](#frontmatter-contract).
* `log.md` files record directory update history.
* Use bundle-relative links such as `[Linked Thinking](/6-System/linked-thinking.md)`.
* Update the relevant `index.md`, MOC, and `log.md` when adding or materially changing a concept.
* Preserve [OKF Specification](/6-System/okf-specification.md) as the baseline reference; do not rewrite the copied spec text.

# Frontmatter Contract

**Every file you create gets YAML frontmatter, and its `description` is written for an agent that will read only the frontmatter.** Frontmatter is the routing layer of this vault. Agents scan descriptions to work out where to go and which files to open in full, so a vague description costs every later session real work.

Use this field order:

```yaml
---
type: <value from Concept Types>   # required, non-empty
title: <display name>
description: <one or two sentences: what is in this file, and when to read it in full>
tags: [<tag>, <tag>]
timestamp: <ISO 8601, e.g. 2026-08-12T00:00:00Z>
---
```

A good `description`:

* Names the concrete contents, such as the actual steps, decisions, values, or sources the file holds.
* Says when a reader should open the file, so it answers "is this the file I need?"
* Stays at one or two sentences and stands on its own, without leaning on the file name or on chat context.
* Avoids filler such as "notes about X" or "various information".

This covers `index.md` and `log.md` as well, which take `type: Index` and `type: Log`. Files that cannot carry YAML frontmatter, such as `.ps1`, `.js`, `.css`, and `.html`, get the same one-line description in their entry in the directory's `index.md`.

Worked examples and how the checks and the index generator consume these fields: [Frontmatter Contract](/6-System/frontmatter-contract.md).

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
