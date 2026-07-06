---
type: Decision
title: Why OKF + PARA + MOCs
description: Decision record explaining why this vault combines OKF, PARA, and Maps of Content.
tags: [decision, okf, para, moc, second-brain]
timestamp: 2026-07-06T00:00:00Z
decision_status: accepted
status: active
---

# Context

The vault needs to serve both humans and agents. Humans need a low-friction Obsidian workspace. Agents need stable structure, parseable metadata, clear links, and explicit operating rules.

# Decision

Use OKF as the file and metadata baseline, PARA as the top-level organization model, and MOCs as the navigation and linked-thinking layer.

# Alternatives

* Pure PARA without OKF: easier for humans, weaker for agents and automation.
* Pure OKF hierarchy without PARA: portable and parseable, but less aligned with day-to-day personal knowledge workflows.
* Tag-only organization: flexible, but too weak as the main navigation and lifecycle model.
* One large wiki hierarchy: familiar, but tends to bury actionable work and stale material together.

# Consequences

* Every concept has enough frontmatter to be checked by tooling.
* Top-level folders communicate actionability and lifecycle.
* MOCs provide curated navigation across PARA boundaries.
* Links and decision notes preserve reasoning for future humans and agents.
* The system requires automation because manual index, link, and lifecycle hygiene will decay.

# Links

* [Decisions and Context MOC](/5-MOCs/decisions-and-context-moc.md)
* [PARA Method](/3-Resources/para-method.md)
* [Maps of Content](/3-Resources/maps-of-content.md)
* [OKF Bundle Practice](/3-Resources/okf-bundle-practice.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
