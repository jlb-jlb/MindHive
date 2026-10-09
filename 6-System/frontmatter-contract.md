---
type: System
title: Frontmatter Contract
description: The required frontmatter fields for every file in this vault and how to write a description that lets an agent route from frontmatter alone, with good and bad examples and the tooling that consumes these fields.
tags: [system, frontmatter, okf, metadata, routing]
timestamp: 2026-08-12T00:00:00Z
---

# Purpose

Frontmatter is the routing layer of this vault. A human opens files through the Obsidian
explorer, an agent opens them through `index.md` listings and frontmatter scans. Reading a
file costs an agent context it cannot get back, so the `description` field has one job: let a
reader decide whether to open the file without opening it.

This note is the detail behind the Frontmatter Contract section in [Agent Session Instructions](/AGENTS.md).

# Required Fields

| Field | Required | Purpose |
|---|---|---|
| `type` | Yes | Routing and filtering. Must be a value from [Concept Types and Status Vocabulary](/6-System/concept-types.md). |
| `title` | Yes in practice | Display name used in generated index entries. Falls back to the file name when missing. |
| `description` | Yes in practice | One or two sentences that let a reader skip or open the file. |
| `tags` | Recommended | Feeds the generated [Tag Index](/3-Resources/tag-index.md). A file with no tags never appears there. |
| `timestamp` | Recommended | ISO 8601 last-touched time. Required on Inbox captures, where the staleness check reads it. |

Local extensions such as `status`, `area`, `decision_status`, `review_cycle`, `verdict`, and
`rating` are listed in [OKF Bundle Practice](/6-System/okf-bundle-practice.md).

# Writing the Description

Write for a reader who sees only this line and has to decide where to go next.

* **Name the concrete contents.** State the actual steps, decisions, values, or sources inside.
* **Say when to open it.** The line should answer "is this the file I need right now?"
* **Stand alone.** Do not lean on the file name, the folder, or anything said in a chat thread.
* **Stay at one or two sentences.** Longer than that and it stops being scannable.
* **Skip filler.** "Notes about X" and "various information" tell a reader nothing.

| Weak | Strong |
|---|---|
| `description: Notes on the vault checks.` | `description: The five vault check scripts, what each one blocks, and the pre-commit hook behavior on whole-tree versus partial commits.` |
| `description: Obsidian setup.` | `description: Why .html files stay hidden in the Obsidian explorer, and five ways to open one in a tab. Read before wiring a new HTML dashboard into the vault.` |
| `description: Job application stuff.` | `description: Per-company application status, submission dates, and the tailored letter for each open application. Start here before drafting a new one.` |

# Reserved Files

`index.md` and `log.md` carry frontmatter as well, using the reserved types `Index` and `Log`.
Their descriptions are the highest-value ones in the vault, because a directory index is what
an agent reads when it is deciding which branch of the tree to walk into.

```yaml
---
type: Index
title: Setup Guides
description: Directory map for machine and tool setup procedures, covering remote desktop, Apptainer sandboxes, and viewing HTML in Obsidian.
---
```

The vault checks skip both filenames entirely, so this is a convention the checks do not
enforce. Write it anyway.

# Files Without Frontmatter

`.ps1`, `.js`, `.css`, `.html`, PDFs, and images cannot carry YAML frontmatter. Give them the
same one-line description in the entry for that file in the directory's `index.md`, the way
[Vault Automation](/6-System/vault-automation.md) describes each script in `_tools/`.

# How the Tooling Consumes These Fields

Two scripts read frontmatter, which is why a thin description degrades more than style.

* [Test-OkfVault.ps1](/_tools/Test-OkfVault.ps1) reports a missing frontmatter block, a missing
  or unknown `type`, and a missing or empty `description` as issues. It skips `index.md` and
  `log.md` before parsing, so those two files are never checked.
* [Update-OkfIndexes.ps1](/_tools/Update-OkfIndexes.ps1) copies `title` and `description`
  verbatim into the generated block of every `index.md`, and copies `title`, `type`, and
  `tags` into the tag index. A file with no description is listed in its directory map as
  `No description.`, which makes it invisible to anyone routing by index. The script only
  rewrites the region between its generated markers, so frontmatter in an `index.md` survives
  regeneration.

# Scope

The contract applies to every file created from now on, and to any file being materially
rewritten. Backfilling untouched older files is optional cleanup rather than a blocking task.

# Related

* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
* [OKF Bundle Practice](/6-System/okf-bundle-practice.md)
* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md)
* [Vault Automation](/6-System/vault-automation.md)
