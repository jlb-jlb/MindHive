---
type: Template
title: Wiki Article Template
description: Template for a wiki article, a how-to or topic explainer with sources.
tags: [template, wiki, howto]
timestamp: 2026-08-05T00:00:00Z
---

# Frontmatter

```yaml
---
type: Resource
title: <Article title, named after the task or question>
description: <One sentence naming what the article lets you do or understand>
tags: [wiki, <topic>]
timestamp: <ISO 8601 datetime>
---
```

# Body

```markdown
# Summary

<Two or three sentences a skimmer can act on. The core answer, up front.>

# Context

<When this applies. Prerequisites, versions, assumptions, scope limits.>

# Steps

<Numbered steps for a how-to. For a topic article, replace this with titled sections that explain how the thing works.>

# Pitfalls

* <What goes wrong, how to recognize it, what to do then>

# Sources and Related

* <Where this was learned, plus links to related vault concepts>
```

# Usage

Save the article in the [Wiki](/3-Resources/wiki/), list it in the wiki index, and add a dated entry to the [wiki log](/3-Resources/wiki/log.md).
