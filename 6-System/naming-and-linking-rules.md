---
type: System
title: Naming and Linking Rules
description: Stable rules for file names, concept IDs, links, and tags.
tags: [system, naming, links, okf]
timestamp: 2026-07-06T00:00:00Z
---

# File Names

New concept files should use lowercase kebab-case:

```text
example-note-title.md
```

Existing files may keep their current names when renaming would create churn.

HTML dashboards are the exception to kebab-case: they are user entry points, so their
file names are ALL CAPS, like `MY DASHBOARD.html`, to stand out in the file explorer
and the tab bar.

# The Underscore Prefix Means Infrastructure

A top-level directory whose name starts with `_` holds support material rather than
knowledge. Three exist: `_attachments/` for images and PDFs referenced by notes,
`_tools/` for the check and index-generation scripts, and `_templates/` for the raw note
skeletons the Obsidian Templates plugin inserts (see [Obsidian Insertable Templates](/3-Resources/wiki/obsidian-insertable-templates.md)).
Set 2026-08-13, when `tools/` was renamed to `_tools/`, and extended 2026-09-05 with `_templates/`.

The prefix is load-bearing in two places, so a new `_` folder inherits both behaviors
without any further wiring:

* **The vault checks skip it.** [Test-OkfVault.ps1](/_tools/Test-OkfVault.ps1) and
  [Update-OkfIndexes.ps1](/_tools/Update-OkfIndexes.ps1) treat a leading `_` on a
  top-level directory exactly like `.github/` or `.githooks/`: no frontmatter is
  demanded, no `index.md` is generated inside it, and it is left out of the generated
  bundle contents. This is what keeps a Python virtualenv or a build artifact from
  being scanned as a concept.
* **The explorer hides it.** The [MindHive Hidden Files plugin](/3-Resources/obsidian-hidden-files-plugin.md)
  hides `_`-prefixed entries at any depth behind its ribbon toggle.

The two scopes differ on purpose. The checks only skip the prefix at the top level, so
a `_drafts/` folder inside `3-Resources/` stays hidden in the explorer while still being
held to the frontmatter rules.

# Concept IDs

The concept ID is the bundle-relative path without `.md`, following the OKF baseline.

Example:

```text
6-System/linked-thinking.md -> 6-System/linked-thinking
```

# Links

Prefer bundle-relative links beginning with `/` inside concept bodies:

```markdown
[Linked Thinking](/6-System/linked-thinking.md)
```

Use relative links in `index.md` files when listing local directory contents.

# Moving a Note in Obsidian Breaks Links Elsewhere

This vault runs with `alwaysUpdateLinks` on. When a note is moved in Obsidian, Obsidian
rewrites every link pointing at it, but writes them relative to the note's *new* folder,
which turns a bundle-relative link like `/3-Resources/wiki/topic/x.md` into a
bare `x.md`. That resolves only for files sitting in the same folder, so links from MOCs,
logs, and other directories silently break.

After moving notes, run the vault checks and repair what they flag back to bundle-relative
form:

```bash
pwsh -NoProfile -File _tools/Invoke-OkfChecks.ps1 -FixIndexes
```

The checks catch this reliably, so the move itself is safe; it just is not finished until
they pass.

# Tags

Tags should be short, lowercase, and reusable:

```yaml
tags: [agents, handoff, para]
```

# Related

* [OKF Bundle Practice](/6-System/okf-bundle-practice.md)
* [Linked Thinking](/6-System/linked-thinking.md)
* [Maps of Content](/6-System/maps-of-content.md)

