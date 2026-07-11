---
type: Resource
title: Agent Skills Library
description: Catalog of reusable agent skills maintained alongside MindHive.
tags: [resource, agents, skills, library]
timestamp: 2026-07-06T00:00:00Z
---

# Purpose

This library tracks reusable agent skills that are useful enough to maintain deliberately. It stores actual copy-pasteable skill folders under [agent-skills](/3-Resources/agent-resources/agent-skills/) and records what each skill does, when it should trigger, and what quality rules it enforces.

# Skills

| Skill | Purpose | Canonical Source |
|---|---|---|
| [General Academic Writing](/3-Resources/agent-resources/agent-skill-general-academic-writing.md) | Discipline-neutral academic writing and revision with evidence, style, and structure rules. | [SKILL.md](/3-Resources/agent-resources/agent-skills/general-academic-writing/SKILL.md) |

# Library Rules

* Record each skill as a resource note before relying on it for recurring work.
* Store the actual skill in `3-Resources/agent-skills/<skill-name>/SKILL.md`.
* Do not add vault `index.md` files inside individual skill folders; the skill folder should stay copy-pasteable.
* Keep the skill's trigger description explicit enough that a fresh agent knows when to use it.
* Keep skill bodies procedural and concise. Put broad background in resource notes, not in the skill itself.
* Validate skills after meaningful edits.
* Link each skill to the projects, areas, and resources it supports.

# Related

* [Agent Collaboration Patterns](/3-Resources/agent-resources/agent-collaboration-patterns.md)
* [Context Packet](/3-Resources/agent-resources/context-packet.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
