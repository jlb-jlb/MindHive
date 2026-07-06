---
type: Template
title: Agent Handoff Template
description: Template for a compact task handoff from one human or agent to the next.
tags: [template, agents, handoff, context]
timestamp: 2026-07-06T00:00:00Z
---

# Frontmatter

```yaml
---
type: Handoff
title: <Task handoff title>
description: <One-sentence handoff summary>
tags: [handoff, agents]
timestamp: <ISO 8601 datetime>
status: active
---
```

# Body

```markdown
# Objective

<What outcome is being pursued?>

# Current State

<What has been done?>

# Key Links

* [Project](/1-Projects/<project>.md)
* [Decision](/5-MOCs/decisions-and-context-moc.md)

# Assumptions

* <Assumption>

# Next Actions

* <Concrete next action>

# Verification

* <Check run, result, or not run>

# Risks

* <Known gap>
```

