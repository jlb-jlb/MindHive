---
type: MOC
title: Decisions and Context MOC
description: Map of decision records, governing rules, and context packets for continuity. Read it to find why the vault is structured as it is, or to register a new decision or handoff.
tags: [moc, decisions, context, continuity]
timestamp: 2026-10-09T00:00:00Z
---

# Purpose

This map keeps reasoning visible. Humans and agents should be able to reconstruct why a structure, rule, project, or implementation exists.

# Decision Records

* [Why OKF + PARA + MOCs](/6-System/decision-okf-para-mocs.md) - The vault combines OKF, PARA, and MOCs to serve both humans and agents.

Add every new decision note here, made from the [Decision Note Template](/3-Resources/Templates/decision-note-template.md).

# Governing Rules

* [Vault Charter](/6-System/vault-charter.md) - MindHive is a shared OKF PARA second brain for humans and agents.
* [Agent Session Startup](/6-System/agent-session-startup.md) - New sessions should begin from [Agent Session Instructions](/AGENTS.md).
* [Vault Automation](/6-System/vault-automation.md) - Rules are enforced through generated indexes, linting, hooks, and CI.
* [Concept Types and Status Vocabulary](/6-System/concept-types.md) - Frontmatter and lifecycle vocabulary is controlled.
* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md) - File names use lowercase kebab-case, and links are bundle-relative where possible.
* [OKF Bundle Practice](/6-System/okf-bundle-practice.md) - OKF rules are applied through frontmatter, reserved files, indexes, and cross-links.

# Context Packets

* [Context Packet](/3-Resources/agent-resources/context-packet.md) - Definition of a portable task state snapshot.
* [Agent Handoff Template](/3-Resources/Templates/agent-handoff-template.md) - Template for the next agent.

Link every filled-in handoff here.

# Decision Hygiene

Record a decision when:

* A rule changes how future notes are written.
* A project changes direction.
* A tradeoff affects future agents or humans.
* A rejected option may look attractive later.
