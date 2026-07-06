---
type: Resource
title: OKF Bundle Practice
description: How this vault applies the Open Knowledge Format v0.1 rules.
tags: [resource, okf, conformance, markdown]
timestamp: 2026-07-06T00:00:00Z
resource: /3-Resources/okf-specification.md
---

# Practice

This vault applies the local [OKF Baseline](/3-Resources/okf-specification.md) as follows:

* Every concept document is a Markdown file with YAML frontmatter.
* Every concept document has a non-empty `type`.
* `index.md` files provide directory-level progressive disclosure.
* `log.md` files record chronological changes for their directory scope.
* Links are standard Markdown links.
* MOCs are ordinary concept documents with `type: MOC`.

# Reserved Files

| File | Meaning |
|---|---|
| `index.md` | Directory listing for progressive disclosure. |
| `log.md` | Chronological update history. |

# Local Extensions

The vault uses additional frontmatter fields when useful:

* `status`
* `area`
* `standard`
* `decision_status`
* `review_cycle`

# Related

* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md)
* [Knowledge Operations](/2-Areas/knowledge-operations.md)
* [MindHive MOC](/5-MOCs/second-brain-moc.md)
