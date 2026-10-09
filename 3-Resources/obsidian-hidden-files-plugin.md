---
type: Resource
title: MindHive Hidden Files Plugin
description: Local Obsidian plugin that hides chosen files and folders from the explorer behind an eye toggle in the ribbon, matching by name prefix, ending, or exact name. Covers the settings, the CSS scoping, and the selector traps found while building it.
tags: [obsidian, plugin, file-explorer, css, workspace]
timestamp: 2026-08-12T00:00:00Z
---

# What It Is

A local, unpublished Obsidian plugin in `.obsidian/plugins/mindhive-hidden-files/` (a `manifest.json` and a plain-JavaScript `main.js`, no build step, matching the [MindHive HTML View Plugin](/3-Resources/obsidian-html-view-plugin.md)). It keeps the file explorer showing knowledge content by hiding everything else behind one button.

# What It Hides

Three matchers, all editable under Settings > MindHive Hidden Files, one entry per line:

| Matcher | Matches | Default |
|---|---|---|
| Name prefixes | Name starts with the entry, at any depth | `_` |
| Name endings | Name ends with the entry, so compound extensions such as `.excalidraw.md` work | none |
| Exact names | Whole name matches, in every folder | `index.md`, `log.md`, `CLAUDE.md`, `AGENTS.md`, `README.md` |

The defaults clear the two kinds of clutter this vault produces. `_` is the vault's [infrastructure prefix](/6-System/naming-and-linking-rules.md), carried by `_attachments/` and `_tools/`. The named files are OKF scaffolding: an `index.md` and a `log.md` sit in every directory, and the agent instructions live at the root in two identical copies.

Matching ignores case, so a hand-typed `readme.md` still matches `README.md`, the way the Windows filesystem would.

# The Button

An eye in the left ribbon, beside "Open quick switcher" and the other ribbon actions. The icon is `eye-off`, the struck-through eye, while entries are hidden, and `eye` while they are shown, so the button states the current condition rather than the pending action. The command "Toggle hidden files" does the same and can take a hotkey. State and settings live in `data.json` and survive a restart, hidden being the default on first load.

# What It Deliberately Does Not Do

Nothing is renamed, moved, or deleted, and no index is rewritten. Links still resolve, embedded attachments still render, search still returns these files, and the quick switcher still opens them. Only the explorer drawing changes, which is what keeps `_attachments` working normally while out of sight.

# How It Works

A single `<style>` element in `document.head` holds two rules, rebuilt from the settings on every edit. The file explorer tags every row with `data-path`, so each matcher becomes an attribute selector on that path:

| Setting | Selectors |
|---|---|
| prefix `P` | `[data-path^="P" i]` at the root, `[data-path*="/P" i]` nested |
| ending `E` | `[data-path$="E" i]` at any depth |
| name `N` | `[data-path="N" i]` at the root, `[data-path$="/N" i]` nested |

The slash in the nested forms is load-bearing: without it, a name entry for `index.md` would also swallow `my-index.md`. Children of a hidden folder inherit a path that starts with the prefix, so they match the root form and never outlive their parent.

Three details are deliberate:

* **The primary rule hides the enclosing `.tree-item`**, reached with `:has(> .tree-item-self[...])`. Hiding the row alone would leave a folder's children container behind as an empty indent. The `>` combinator matters: without it, `:has()` would also match every ancestor folder of a hidden note and hide half the tree.
* **The fallback is a separate rule.** An unsupported selector invalidates the entire rule it appears in, so the `:has()` selectors cannot share a rule with the plain ones that must survive without it.
* **Both rules are scoped twice**, to `.workspace-leaf-content[data-type="file-explorer"]` and to `.nav-files-container`, so hiding does not hinge on one attribute surviving an Obsidian update. Both scopes are explorer-only, which is what keeps search results and bookmarks complete.

Attribute values are quoted in the generated CSS, so a quote or backslash typed into a settings box is escaped before it can close the string early and break every rule after it. Toggling flips `styleEl.disabled` instead of rebuilding, which stays instant on a large vault, and typing in a settings box repaints on every keystroke while writing to disk only once the typing stops.

# Verifying a Change Without Obsidian

Obsidian cannot be scripted from outside, so the selectors are checked against a replica of the explorer markup: extract the generated CSS by evaluating everything in `main.js` above `module.exports`, render one row per interesting path, serve them over the local static server, and read back `getClientRects().length` per row. Extracting the CSS rather than retyping it is the point of the exercise, because a typo in the real file then has to fail the test.

The case set, confirmed on 2026-08-13:

| Path | Expected | What it pins down |
|---|---|---|
| `_attachments` and its child | hidden | A prefixed folder takes its contents with it |
| `3-Resources/_draft.md` | hidden | Prefix at depth |
| `3-Resources/note_two.md` | visible | An underscore mid-name is not a prefix |
| `index.md`, `CLAUDE.md` at the root | hidden | Exact name at the root |
| `3-Resources/log.md` | hidden | Exact name at depth |
| `3-Resources/Log.md` | hidden | Matching ignores case |
| `3-Resources/my-index.md` | visible | The slash guard on nested exact names |
| `3-Resources/readme-notes.md` | visible | A name that merely starts the same way |
| `3-Resources` itself | visible | An ancestor of hidden children stays put |
| `drawing.excalidraw.md`, ending set | hidden | Compound extensions |
| `drawing.md`, ending set | visible | The ending is not the extension |
| The same path in a search pane | visible | The explorer scoping holds |

Flipping `styleEl.disabled` on the same page restores every row, which covers the button.

The DOM assumptions are checkable inside the vault too. `.obsidian/themes/Ruby Second Brain/theme.css` styles `.tree-item > .tree-item-self`, `.nav-file-title`, and `.nav-folder-title`, and uses `:has()` in 27 places, which confirms both the structure and the engine support for the Obsidian version in use here.

# Enabling It

`.obsidian/community-plugins.json` lists `mindhive-hidden-files` alongside `mindhive-html-view`. Obsidian reads that file at startup, so restart Obsidian, or enable it once under Settings > Community plugins.

**Obsidian caches plugin code.** After editing `main.js` you must toggle the plugin off and on under Settings > Community plugins, or restart Obsidian.

# Related

* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md)
* [MindHive HTML View Plugin](/3-Resources/obsidian-html-view-plugin.md)
* [Obsidian Ruby Second Brain Theme](/3-Resources/obsidian-ruby-second-brain-theme.md)
