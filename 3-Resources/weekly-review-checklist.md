---
type: Resource
title: Weekly Review Checklist
description: Practical checklist for keeping MindHive current and usable.
tags: [resource, review, second-brain, operations]
timestamp: 2026-07-06T00:00:00Z
---

# Purpose

Use this checklist once per week to keep MindHive from becoming a static scaffold.

# Checklist

* Empty or route [Inbox](/0-Inbox/) captures older than 7 days.
* Review active projects in [Projects](/1-Projects/) for next actions and done conditions.
* Move completed or inactive material toward [Archive](/4-Archive/) when it no longer needs attention.
* Add links from new notes to the relevant MOC.
* Record decisions that explain a lasting rule, structure, or tradeoff.
* Run the vault checks:

```powershell
pwsh -NoProfile -File tools/Invoke-OkfChecks.ps1
```

# Related

* [Human Operating Protocol](/6-System/human-operating-protocol.md)
* [Operationalize MindHive](/1-Projects/operationalize-second-brain.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
