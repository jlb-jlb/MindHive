---
type: Resource
title: Obsidian Ruby Second Brain Theme
description: Local Obsidian theme that renders MindHive notes as designed documentation pages, with ruby as the accent color.
tags: [resource, obsidian, theme, ruby, design]
timestamp: 2026-07-06T00:00:00Z
resource: /.obsidian/themes/Ruby%20Second%20Brain/theme.css
---

# Summary

MindHive ships a local Obsidian theme named `Ruby Second Brain`. Version 2 rebuilds it around one goal: a note should read like a documentation page somebody designed, so the shape of a page is visible before a word of it is read. Ruby stays the single accent, used only to mark structure and interaction.

# Files

* [Theme CSS](/.obsidian/themes/Ruby%20Second%20Brain/theme.css)
* [Theme Manifest](/.obsidian/themes/Ruby%20Second%20Brain/manifest.json)
* [Appearance Configuration](/.obsidian/appearance.json)
* `/.obsidian/themes/Ruby Second Brain/preview/` holds the browser harness described in [Previewing Changes](#previewing-changes).

# The Heading System

The design was fitted to how this vault actually writes. A count across the 172 notes found 662 `#`, 574 `##`, 46 `###`, 4 `#####`, and no `####` at all. Two levels carry nearly all the structure, so those two get the strongest and most distinct treatment:

| Element | Role | Treatment |
|---|---|---|
| Inline title | The page title | 2.5em, weight 800, tight tracking, a vertical sheen poured through the glyphs, opened by a lit ruby kicker |
| `#` | Chapter | 1.75em, underlined by a lit ruby cap that runs out into a hairline fading to the right |
| `##` | Section | 1.32em, marked by a cut ruby facet trailing a line of light |
| `###` | Lead-in | 1.1em in ruby, with a faint bloom on the dark scheme |
| `####` and below | Micro label | Uppercase, letterspaced, muted |

The inline title carries the page title because notes here keep their title in frontmatter and use `#` for sections. Turning off "Show inline title" in Obsidian removes the masthead, so leave it on.

Frontmatter renders as an editorial meta strip with hairlines above and below, labels as uppercase micro type, and the `type` value in ruby, since `type` is the fastest orientation cue in an OKF bundle.

# Design Decisions

* **Variables first.** Obsidian binds both Reading view and Live Preview to the same documented CSS variables (`--h1-size`, `--file-line-width`, `--table-header-background`, and the rest). Setting those keeps the two views in step for free, and hand-written selectors are reserved for decoration Obsidian has no variable for.
* **A private token layer.** Palette, fonts, geometry, and motion live in `--mh-*` tokens, and the Obsidian variables read from them. Retuning the theme means editing the token block, leaving the 160 or so component rules untouched.
* **Section markers sit above their heading.** An earlier draft put the `##` accent bar in the left gutter, which clips on narrow panes and risks horizontal scroll inside CodeMirror. Placing the bar above the text reads the same and cannot clip.
* **One accent.** Ruby marks headings, links, list markers, active navigation, and interactive states. Highlights use amber, so `==marked text==` never reads as a link or a tag.
* **Measure over max-width.** Version 1 forced `max-width: 900px` onto the preview element, which overrode Obsidian's own layout. Version 2 sets `--file-line-width: 46rem` (about 72 characters), so the "Readable line length" toggle keeps working.
* **Code blocks announce their language.** A badge in the top left is generated with `pre:has(> code.language-*)`, which reads the class Obsidian puts on the `code` element. Languages without a mapping fall back to a plain `code` badge.

# The Facet Language

The theme is named for a gemstone, so the heading decoration follows a cut-and-light motif that descends in weight from the title down to `###`. Ruby facets are rotated squares with a gradient across the cut and a soft glow, and every one of them sits above or beside the text without touching the reading column.

* **The title sheen runs top to bottom.** A horizontal gradient was tried first and rejected: the inline title is a block spanning the full measure, so a two word title would land entirely in the first colour stop while a ten word title showed the whole ramp. Running the gradient vertically through the glyph height gives every title the same treatment. Light warms neutral ink into burgundy at the baseline, and dark opens on white and closes on ruby.
* **Editing a title restores solid ink.** Glyphs filled by `background-clip: text` have no colour of their own, so a selection highlight would swallow them while renaming a note. A `:focus` and `:focus-within` rule drops the clip for the duration of the edit.
* **The two `##` markers share one axis.** The facet and its trailing bar are separate pseudo-elements, aligned through `--mh-mark-top`: the bar centre sits 1px below that value, and the 7px facet centre 3.5px below its own top, which is why the facet is offset by 2.5px. Change the token and both move together.
* **Glow is heavier on dark.** Bloom only registers against a dark surface, so `--mh-glow` carries more spread and opacity there. The same token drives the kicker, the `#` cap, and the `##` facet, so brightness is tuned in one place.
* **Headings answer the pointer.** Hovering a `#` widens and brightens its cap, and hovering a `##` brightens the facet and extends its trail.
* **The kicker catches the light once.** A sheen sweeps across the title bar as a note is drawn, on a single 1500ms pass. Deleting the `animation` line in the `.inline-title::before` rule leaves the bar still, and the theme already drops it under `prefers-reduced-motion`.

# Previewing Changes

Obsidian caches theme CSS, and reloading the app for every tweak is slow. The `preview/` folder next to `theme.css` renders the theme in a normal browser:

* `preview/index.html` reproduces Reading view: masthead, headings, table, code blocks with badges, callout, quote, task list, tags, and the sidebar.
* `preview/lp.html` reproduces Live Preview, so the CodeMirror rules can be checked as well.
* `preview/obsidian-shim.css` supplies the small set of Obsidian base rules that bind the theme's variables to real properties. It exists only for the preview and is never loaded by Obsidian.

Both pages link `../theme.css` directly, so what the browser shows is the live file. Open either one from disk, or serve the vault root and browse to it. Append `?dark` to the URL for the dark scheme, or use the toggle button in the corner. Obsidian ignores everything in a theme folder other than `manifest.json` and `theme.css`, so the folder is inert in the app.

# Related

* [MindHive MOC](/5-MOCs/second-brain-moc.md)
* [Knowledge Operations](/2-Areas/knowledge-operations.md)
* [Linked Thinking](/6-System/linked-thinking.md)
* [MindHive HTML View Plugin](/3-Resources/obsidian-html-view-plugin.md)
