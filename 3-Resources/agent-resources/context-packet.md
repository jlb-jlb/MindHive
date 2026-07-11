---
type: Resource
title: Context Packet
description: Minimal state snapshot needed for a human or agent to resume work.
tags: [resource, context, handoff, agents]
timestamp: 2026-07-06T00:00:00Z
---

# Definition

A context packet is a compact, durable summary of task state. It should let the next human or agent resume without rereading an entire conversation.

# Fields

| Field | Purpose |
|---|---|
| Objective | What outcome is being pursued. |
| Current state | What has already happened. |
| Key links | Notes, files, decisions, or sources that matter. |
| Assumptions | Claims being treated as true. |
| Decisions | Choices already made. |
| Next actions | Concrete follow-up steps. |
| Verification | Checks already run and their result. |
| Risks | Known gaps, uncertainty, or unresolved questions. |

# Related

* [Agent Handoff Template](/3-Resources/Templates/agent-handoff-template.md)
* [Decision Note Template](/3-Resources/Templates/decision-note-template.md)
* [Agent-Human Collaboration](/2-Areas/agent-human-collaboration.md)

