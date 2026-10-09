---
type: Resource
title: MindHive HTML View Plugin
description: Local Obsidian plugin that renders vault .html files with their CSS and JavaScript active, and lets embedded pages open vault notes.
tags: [obsidian, plugin, html, dashboard]
timestamp: 2026-08-05T00:00:00Z
---

# What It Is

A local, unpublished Obsidian plugin in `.obsidian/plugins/mindhive-html-view/` (a `manifest.json` and a plain-JavaScript `main.js`, no build step). It makes `.html` and `.htm` files first-class citizens of the vault: they open in a normal tab on click, rendered with their CSS and JavaScript fully active.

# What It Does

* Registers a file view for `.html` and `.htm`, so the files open from the explorer and quick switcher like notes.
* Renders each file in a borderless iframe pointed at the vault-local resource URL (`app://local/...`), so relative references to images, stylesheets, scripts, and fetch/XHR requests to sibling vault files resolve exactly as on a static web server.
* Reloads the frame whenever the open file changes on disk, so editing HTML in a split pane gives live feedback on save.
* Listens for `postMessage` calls of the shape `{ type: 'mindhive-open', path: '<vault path>' }` and routes them through `app.workspace.openLinkText`, which is how plain HTML pages get real vault navigation.
* Answers `mindhive-ping` (plugin version, so a page can detect a stale build), `mindhive-list` (folder contents via `adapter.list`), `mindhive-read` (file text via `vault.adapter.read`), `mindhive-image` (raw bytes via `readBinary`), and `mindhive-resource` (an `img` URL via `getResourcePath`), so embedded pages never have to guess vault URLs. `mindhive-list` lets a page walk the real folder tree instead of trusting generated index files to be current, which is how the dashboard notices a new subfolder the moment it exists.
* Forwards every vault modify, create, delete, and rename into open frames as `{ type: 'mindhive-vault-changed', event, path, oldPath }`, which is how the dashboard refreshes the moment a review note is edited or added.

The mechanics are commented in `main.js` itself.

# Enabling It

`.obsidian/community-plugins.json` already lists `mindhive-html-view`. If Obsidian still shows Restricted mode, turn it off once under Settings > Community plugins, then reload Obsidian.

**Obsidian caches plugin code.** After editing `main.js` you must toggle the plugin off and on under Settings > Community plugins, or restart Obsidian. Reopening the HTML file is not enough, and this is the single most likely reason an embedded page suddenly loses its photos or shows stale data: the page is talking to an old build that does not know the newer messages. `mindhive-ping` exists for exactly this reason, and the dashboard logs the answering version to the console on every load.

# Do Not Build Vault URLs Inside an Embedded Page

Learned the hard way, in this order:

1. Relative paths break because the resource URL can carry Windows backslashes (encoded `%5C`); the browser sees one giant path segment, so `../` walks resolve wrong and every request 404s.
2. Normalizing `location.href` and rebuilding absolute URLs from it fixes `fetch` but still did not make `<img>` load reliably.
3. What works unconditionally: **do not pass a URL at all.** Ask for the bytes over the bridge (`mindhive-image`), wrap them in a `Blob`, and use `URL.createObjectURL`. The resulting `blob:` URL belongs to the page's own document, so no vault URL scheme, host token, or path separator can break it.

Cache the object URL per path: a grid that re-renders on tab or sort changes must not re-read a 2 MB photo every time.

# Related

* [Obsidian Ruby Second Brain Theme](/3-Resources/obsidian-ruby-second-brain-theme.md)
* [Resources MOC](/5-MOCs/resources-moc.md)
