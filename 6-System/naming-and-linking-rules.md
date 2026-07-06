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

# Concept IDs

The concept ID is the bundle-relative path without `.md`, following the OKF baseline.

Example:

```text
3-Resources/linked-thinking.md -> 3-Resources/linked-thinking
```

# Links

Prefer bundle-relative links beginning with `/` inside concept bodies:

```markdown
[Linked Thinking](/3-Resources/linked-thinking.md)
```

Use relative links in `index.md` files when listing local directory contents.

# Tags

Tags should be short, lowercase, and reusable:

```yaml
tags: [agents, handoff, para]
```

# Related

* [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md)
* [Linked Thinking](/3-Resources/linked-thinking.md)
* [Maps of Content](/3-Resources/maps-of-content.md)

