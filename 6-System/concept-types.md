---
type: System
title: Concept Types and Status Vocabulary
description: Controlled vocabulary for concept types, statuses, and lifecycle transitions in the vault.
tags: [system, vocabulary, lifecycle, okf]
timestamp: 2026-07-06T00:00:00Z
---

# Purpose

This note defines the shared vocabulary that humans and agents should use in frontmatter.

# Concept Types

| Type | Use |
|---|---|
| `Area` | Ongoing responsibility or standard. |
| `Capture` | Unprocessed inbox item awaiting review. |
| `Decision` | Recorded choice, tradeoff, and consequence. |
| `Handoff` | Context packet for resuming unfinished work. |
| `MOC` | Map of Content for navigation and linked thinking. |
| `Project` | Active outcome with a finish line. |
| `Reference` | External or preserved source material. |
| `Resource` | Reusable knowledge, method, or local reference. |
| `System` | Operating rule, protocol, or vault infrastructure note. |
| `Template` | Reusable note pattern. |

# Status Values

| Status | Use |
|---|---|
| `active` | Current and intentionally being worked or maintained. |
| `paused` | Valid but intentionally not moving right now. |
| `done` | Completed and ready to archive when no longer active context. |
| `archived` | Inactive and retained only for history. |
| `unprocessed` | Captured but not yet routed. |

# Decision Status Values

| Decision Status | Use |
|---|---|
| `accepted` | Current decision. |
| `superseded` | Replaced by a later decision. |
| `rejected` | Deliberately not chosen. |

# Lifecycle Rules

Projects start as `active` when they have an outcome, next action, and done condition.

A project may move to `paused` when it remains valid but should not compete for current attention.

A project moves to `done` when its done conditions are met and the result has been linked from the relevant MOCs, areas, or resources.

A `done` project moves to [Archive](/4-Archive/) when it is no longer needed as active context. Set `status: archived` after moving it.

Inbox captures start as `unprocessed`. Captures older than 7 days must be routed into PARA, converted into a decision or handoff, or archived.

# Related

* [Human Operating Protocol](/6-System/human-operating-protocol.md)
* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
* [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md)
* [Vault Automation](/6-System/vault-automation.md)
