---
type: Resource
title: Obsidian Insertable Templates
description: How to insert a ready-to-fill note skeleton in Obsidian from the vault-root _templates folder (Ctrl+P, Templates Insert template), which placeholders Obsidian expands, how the folder differs from the agent-facing template docs in 3-Resources/Templates, and the settings that wire it up. Read before adding or editing a template.
tags: [wiki, howto, obsidian, templates]
timestamp: 2026-09-05T00:00:00Z
---

# Summary

Obsidian's core Templates plugin reads from `_templates/` at the vault root. Open a new note, press Ctrl+P, run **Templates: Insert template**, and pick one. The file's full text lands at the cursor with `{{title}}` and `{{date}}` already expanded, so the note starts with valid OKF frontmatter and the section skeleton for its type.

# Context

The vault has two kinds of template, and they serve different readers.

* **Agent-facing template docs** in [3-Resources/Templates](/3-Resources/Templates/index.md). Each is a normal concept with `type: Template` that describes a note type: the frontmatter fields and the body sections, wrapped in code fences with explanatory headings. An agent reads one and writes the note by hand. Inserting one of these through Obsidian would paste the code fences and the doc's own frontmatter, which is not a usable note.
* **Insertable templates** in `_templates/`. Each is the raw skeleton of a note with Obsidian placeholders in the frontmatter and no wrapper. This is what the Templates plugin pastes.

The two sets are kept in step by hand. When a field or section changes in one, change the other. Set 2026-09-05.

Why the folder sits at the vault root with a leading underscore: the [naming rules](/6-System/naming-and-linking-rules.md) make a top-level `_` folder infrastructure. The vault checks skip it, so placeholder frontmatter such as `title: {{title}}` and an unfilled `description` never fail the linter, no `index.md` is generated inside it, and the placeholder tags stay out of the [Tag Index](/3-Resources/tag-index.md). The [Hidden Files plugin](/3-Resources/obsidian-hidden-files-plugin.md) hides it in the explorer, which does not matter for the Templates plugin, because the picker lists files from the vault index rather than from the explorer. Click the eye icon in the ribbon to see and edit the files.

# Templates

| File | Creates | Lands in |
|---|---|---|
| `project.md` | `type: Project` with status and area | `1-Projects/` |
| `area.md` | `type: Area` with a standard | `2-Areas/` |
| `resource.md` | `type: Resource` | `3-Resources/` |
| `wiki-article.md` | `type: Resource` with the summary-first wiki layout | `3-Resources/wiki/` |
| `decision.md` | `type: Decision` with `decision_status` | `1-Projects/` or `6-System/` |
| `agent-handoff.md` | `type: Handoff` | wherever the handed-off work lives |
| `daily-capture.md` | `type: Capture`, `status: unprocessed` | `0-Inbox/` |
| `daily-note.md` | `type: Journal` titled with today's date | `7-Journal/` |

# Steps

1. Create the note in its target folder and give it the final file name first. `{{title}}` expands to the file name at insert time, so a note still called `Untitled` gets `title: Untitled`.
2. Press Ctrl+P, type `insert template`, run **Templates: Insert template**, and pick the file. To skip the palette, bind a hotkey to that command under Settings, Hotkeys.
3. Replace every `<angle bracket>` placeholder. The `description` matters most, because agents route on it. See the [Frontmatter Contract](/6-System/frontmatter-contract.md).
4. Link the note from its `index.md` and a MOC, and add a `log.md` entry, as for any concept.

Daily Notes is wired separately in `.obsidian/daily-notes.json`. It creates today's note in `0-Inbox/` from `_templates/daily-capture`, so the ribbon's calendar icon and **Daily notes: Open today's daily note** produce an inbox capture rather than a journal entry. For a journal entry, create the note in `7-Journal/` and insert `daily-note` by hand.

# Placeholders Obsidian Expands

The core plugin knows only three, and nothing else. Any other `{{...}}` stays literal.

* `{{title}}`: the note's file name without extension.
* `{{date}}` and `{{time}}`: formatted with the patterns in `.obsidian/templates.json`, set here to `YYYY-MM-DD` and `HH:mm`.
* `{{date:FORMAT}}` and `{{time:FORMAT}}`: any moment.js pattern. The templates use `{{date:YYYY-MM-DD[T]HH:mm:ssZ}}` for `timestamp`, which yields a full ISO 8601 stamp with the local offset, such as `2026-09-05T14:03:00+02:00`. The square brackets keep the `T` literal, since bare letters are moment tokens. The vault's staleness check parses this form.

# Pitfalls

* **Templates folder unset.** If the picker is empty, check Settings, Templates, Template folder location. It must read `_templates`. The setting lives in `.obsidian/templates.json`, which is committed.
* **Inserted into a note that already has frontmatter.** Obsidian pastes at the cursor, so a second frontmatter block appears mid-file and the properties panel shows only the first. Insert into an empty note.
* **Placeholder tags leaking.** `wiki-article` carries `tags: [wiki, <topic>]`. Replace `<topic>` before saving, or the tag index picks up a literal `<topic>` tag the next time the indexes regenerate.
* **Editing a template while the Hidden Files toggle is on.** The file is invisible in the explorer but still opens through the quick switcher (Ctrl+O) by name.

# Sources and Related

* Obsidian help, Templates core plugin: https://help.obsidian.md/plugins/templates
* [Templates](/3-Resources/Templates/index.md), the agent-facing template docs these mirror
* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md), the underscore-prefix rule
* [MindHive Hidden Files Plugin](/3-Resources/obsidian-hidden-files-plugin.md)
* [Vault Automation](/6-System/vault-automation.md), the checks that skip `_` folders
