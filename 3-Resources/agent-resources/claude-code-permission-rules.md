---
type: Resource
title: Claude Code Permission Rules
description: How to widen or narrow Claude Code tool permissions in settings.json, including the Bash prefix-rule syntax (Bash(grep:*)), which of the four settings files to edit for which scope, and why the Grep tool is not covered by Bash rules.
tags: [resource, agents, claude-code, configuration, permissions]
timestamp: 2026-08-21T00:00:00Z
---

# Problem

When you approve a shell command in Claude Code with "always allow", it writes a rule that
matches only the exact command it just ran, arguments and all:

```json
"Bash(grep -n \"phase4_umap_verdicts\\|Figure source\" chapters/experiments/phase4-llm-features.tex)"
```

That rule fires once and never again. The next `grep` with a different pattern prompts anew.

# Fix

Replace the exact-match rule with a prefix rule. The prefix ends in `:*`, which matches the
command name plus anything after it:

```json
"Bash(grep:*)"
```

Rules live in the `permissions.allow` array. Merge into the array, never replace it.

# Rule Syntax

| Form | Matches |
|---|---|
| `Bash(npm run test)` | that exact command only |
| `Bash(grep:*)` | `grep` with any arguments |
| `Bash(git status:*)` | `git status` with any arguments, not other git subcommands |
| `Read` | every use of the tool, no argument filter |

The same three arrays exist under `permissions`: `allow`, `deny`, and `ask`. `deny` wins over
`allow`.

# Which File To Edit

Settings load in order and later files override earlier ones.

| File | Scope | Commit it? |
|---|---|---|
| `~/.claude/settings.json` | every project on this machine | n/a, outside any repo |
| `.claude/settings.json` | this project, shared with collaborators | yes |
| `.claude/settings.local.json` | this project, personal only | no, gitignored |

A universally read-only command such as `grep`, `find`, or `ls` belongs in the global file, so
it does not have to be re-approved per project. A project-specific toolchain command such as
`uv run:*` belongs in the project file, where collaborators inherit it.

# Caveats

* **The `Grep` tool is separate from `Bash(grep:*)`.** Claude Code's built-in `Grep` tool is its
  own tool name and is not covered by any `Bash(...)` rule. Ripgrep run through Bash needs its
  own `Bash(rg:*)` entry.
* **Compound commands are matched as a whole.** `grep foo file | head -5` is not simply a `grep`
  invocation, so a bare `Bash(grep:*)` rule may not clear it.
* **Broken JSON silently disables the entire file.** A stray comma in `settings.json` drops every
  setting in it, hooks included, with no error. Validate after editing.
* **`/permissions` is the interactive way to do the same thing**, but it needs an interactive
  terminal session and is not available in every Claude Code surface.

# Related

* [Agent Collaboration Patterns](/3-Resources/agent-resources/agent-collaboration-patterns.md)
* [Vault Automation](/6-System/vault-automation.md) for the hook configured in this vault's own `.claude/settings.json`.
