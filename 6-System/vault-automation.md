---
type: System
title: Vault Automation
description: The five PowerShell check scripts and the Python session linter, what each one blocks, the skip rule for dot-folders and underscore directories, the pre-commit hook behaviour on whole-tree versus partial commits, and the Stop hook exit-code contract.
tags: [system, automation, okf, linting, hooks, python]
timestamp: 2026-08-13T00:00:00Z
---

# Purpose

The vault has executable checks so its conventions do not depend only on memory.

# Tools

* [Update OKF Indexes](/_tools/Update-OkfIndexes.ps1) - Regenerates marked sections in `index.md` files and rewrites the generated [Tag Index](/3-Resources/tag-index.md).
* [Test OKF Vault](/_tools/Test-OkfVault.ps1) - Checks frontmatter, controlled `type` and `status` values, `description`, links, orphan concepts, and stale Inbox items.
* [Test OKF Commit](/_tools/Test-OkfCommit.ps1) - Checks staged changes and blocks new or moved concept files unless a nearby `log.md` update is staged too.
* [Invoke OKF Checks](/_tools/Invoke-OkfChecks.ps1) - Runs the canonical check sequence through PowerShell 7+ on Windows, macOS, and Linux.
* [Install Git Hooks](/_tools/Install-GitHooks.ps1) - Configures Git to use the versioned hook in `.githooks`.
* [Session Linter](/_tools/automation/README.md) - Python `uv` project that lints the files a Claude Code session touched, wired to the `Stop` hook. See [Session Linter](#session-linter).

# What The Checks Skip

Both scanning scripts ignore the same set of paths: the dot-folders (`.git`, `.obsidian`,
`.github`, `.githooks`, `.agents`, `.codex`) and any **top-level directory starting with
`_`**, which is why `_tools/` and `_attachments/` are exempt. Skipped means no frontmatter
is demanded, no `index.md` is generated inside, and the folder is left out of the generated
bundle contents.

The `_` rule was added on 2026-08-13 with the `tools/` to `_tools/` rename, and it closed a
live trap. `_tools/automation/` is a Python project, and its `.venv` is not marked hidden on
Windows, so the directory walk descended into `site-packages`. Before the rule,
`Update-OkfIndexes.ps1` wanted to create about 75 `index.md` files inside the virtualenv and
`.pytest_cache`, and the linter reported third-party `README.md` files as concepts missing
frontmatter. Since the pre-commit hook runs `-FixIndexes` by itself on a whole-tree commit,
that would have landed without anyone asking for it. See
[Naming and Linking Rules](/6-System/naming-and-linking-rules.md) for the convention.

# Runtime Contract

Vault automation is operating-system agnostic through PowerShell 7+ (`pwsh`). Do not rely on Windows PowerShell, shell-specific path separators, or hidden editor behavior for canonical checks.

Run the canonical check sequence with:

```powershell
pwsh -NoProfile -File _tools/Invoke-OkfChecks.ps1
```

After adding, moving, or renaming notes, regenerate generated indexes first:

```powershell
pwsh -NoProfile -File _tools/Invoke-OkfChecks.ps1 -FixIndexes
```

For a normal whole-tree commit the pre-commit hook now runs this step for you and stages the result (see [Git Hook](#git-hook) below), so this command is mainly for working outside a commit or for partial commits.

# Git Hook

The versioned pre-commit hook lives at `/.githooks/pre-commit`.

The hook blocks commits when a staged new or moved concept file does not have a staged `log.md` update in the same directory or an ancestor directory. The failure message names the concept file, suggests the nearest log file, and gives a copyable example entry so a human or agent can repair the commit without hidden context.

## Indexes regenerate automatically

On a **whole-tree commit** (no unstaged changes to tracked files) the hook runs `Invoke-OkfChecks.ps1 -FixIndexes`, then stages the regenerated `index.md` files and `tag-index.md` into the same commit. A stale generated index no longer aborts the commit, so the manual `-FixIndexes` step is only needed when working outside a commit.

This is guarded rather than unconditional for a specific reason: `Update-OkfIndexes.ps1` reads the **working tree**, not the staged snapshot. On a **partial commit** (some notes staged, others left unstaged) regenerating would bake the unstaged notes into the generated index and stage that, committing references to content that is not in the commit. So when `git diff --quiet` reports unstaged tracked changes, the hook falls back to the earlier check-only behavior and leaves regeneration to a deliberate `-FixIndexes` run. Untracked new notes that are never staged are outside this guard, so a generated index can still list them; stage or stash such notes before committing something unrelated.

Install it with:

```powershell
pwsh -NoProfile -File _tools/Install-GitHooks.ps1
```

# Session Linter

The commit hook catches a problem when work is already finished. The session linter catches the
same class of problem at the moment the agent tries to stop, while the context to fix it is
still loaded. Both exist because they fail at different times, not because one replaces the
other.

It lives in [_tools/automation](/_tools/automation/README.md) as a `uv` project on Python 3.13,
and it is Python rather than PowerShell so it runs unchanged on Windows, macOS, and Linux.

## Wiring

Declared as a `Stop` hook in `/.claude/settings.json`:

```json
{ "type": "command", "command": "uv run --project \"$CLAUDE_PROJECT_DIR/_tools/automation\" mindhive-automation lint-session", "timeout": 60 }
```

`uv run` resolves the environment from `uv.lock` before running, so a fresh clone needs no setup
step beyond having `uv` installed.

### The `--project` path must be absolute

It was originally the relative `_tools/automation`, on the stated assumption that hooks always
run with the vault root as the working directory. **That assumption is wrong.** The hook inherits
the working directory of the agent's shell, and an agent that has `cd`-ed into a subdirectory
during the session leaves it there. Observed on 2026-08-13, after a session spent editing under
`3-Resources/wiki/`, the Stop hook failed with:

```
warning: Project directory `_tools/automation` does not exist.
error: Failed to spawn: `mindhive-automation`
  Caused by: program not found
```

The second line is the misleading one. It reads like a broken install, so the instinct is to
reinstall the environment or hunt for a missing entry point. Nothing was missing: `src/`,
`uv.lock`, and `.venv/Scripts/mindhive-automation.exe` were all present. `uv` simply could not
find the project, fell back to the ambient environment, and reported the absent console script.
The cheap diagnostic is to run the command from the vault root and then from a subdirectory. It
succeeds from the root and fails from anywhere else, which isolates it to path resolution.

`$CLAUDE_PROJECT_DIR` is set by Claude Code for every hook and always points at the vault root,
so the absolute form works from any working directory.

The linter's own vault-root detection was never involved. `_resolve_root` in `cli.py` tries the
explicit `--root`, then the hook payload's `cwd`, then `Path.cwd()`, walking up from each, so it
locates the vault from anywhere inside it. Only `uv`'s `--project` argument was position
dependent, which is why the failure looked like a packaging problem rather than a path one.

## What It Checks

Only files the session touched, never the whole vault.

* **frontmatter** - the block parses as YAML, `type` is present and in the
  [controlled vocabulary](/6-System/concept-types.md), `description` is non-empty. The vocabulary
  is parsed out of that note at runtime rather than duplicated in code, so adding a type in one
  place is enough. Missing `title` or `tags` warn.
* **log** - a touched concept note has a `log.md` updated in the same session, in its own
  directory or any ancestor up to the bundle root. This is the commit hook's rule applied
  earlier. It is deliberately stricter in one way: the commit hook fires only on added and
  renamed files, while this fires on any edit.

`index.md` and `log.md` warn where a concept note errors, matching the fact that
[Test-OkfVault.ps1](/_tools/Test-OkfVault.ps1) skips both filenames entirely.

## A Check Only Runs Where It Can Be Judged

`lint-session` reads a whole session, so it can answer both questions. `lint-files` takes a list
of paths and can answer only the first, because "did the log change alongside this note" depends
on what else the session did. A file list carries no such history.

The first version ran both regardless, so every manual `lint-files` call reported a log failure
for a note whose log was perfectly fine. A check that fires on missing evidence rather than on
evidence of a problem trains the reader to ignore it, which costs more than the check was worth.

Checks now declare `needs_session`, and the ones that cannot be judged are skipped and named in
the output:

```text
Not checked: log (needs a full session, not a file list).
```

Printing the skip is the part that matters. A silently omitted check reads as a passing check.

## Exit Codes

The Claude Code hook contract, which is what makes this useful rather than decorative:

| Code | Effect |
|---|---|
| 0 | Clean, or nothing to check. The session stops. |
| 2 | Errors found. The session does not stop, and stderr is fed back to Claude as the reason. |
| 1 | The hook itself failed. Non-blocking, surfaced to the human so the bug stays visible. |

The payload carries `stop_hook_active`, which is true when the session is already continuing
because of a Stop hook. The linter returns 0 immediately in that case. Without that guard a
blocking hook never terminates.

## Finding the Touched Files

Two signals, kept apart because they carry different confidence.

* **The transcript** at `transcript_path` records every `Write`, `Edit`, and `NotebookEdit` call
  with an absolute `file_path`. This is exact, so its findings are errors.
* **A disk scan** covers the gap: an edit made through the Bash tool (`sed -i`, a heredoc, a
  redirect) leaves no tool record at all. Git's changed-file list is intersected with
  modification times inside the session window to recover those. The same net catches a file the
  human edited in Obsidian while the session ran, so its findings are warnings rather than
  errors. `--no-disk-scan` turns it off.

Reading the whole vault was rejected. The point is to report on this session's work, and a
linter that also reports the vault's pre-existing backlog gets ignored within a week.

## What Strict YAML Parsing Found

The linter uses a real YAML parser, which turned out to matter more than expected. On
2026-08-12 it flagged six files whose frontmatter does not parse at all, every one of them for
the same reason: a `description` containing a colon followed by a space, which YAML reads as the
start of a nested mapping.

```yaml
description: Instructions for MindHive: reading order and rules.   # breaks
description: Instructions for MindHive, covering reading order.    # fine
```

These files pass [Test-OkfVault.ps1](/_tools/Test-OkfVault.ps1), which reads frontmatter line by
line and is therefore blind to the failure. Obsidian is not: it uses a real parser, so for those
six files it shows no properties at all. Quoting the value also works, and rewriting the
sentence is preferred because a quoted description is easy to break again later.

The lesson generalizes past this vault. A lenient checker that agrees with nothing else in the
toolchain is worse than no checker, because it converts an unnoticed problem into a confident
green light.

# Committing a Backlog in Topical Slices

Splitting a large uncommitted backlog into several meaningful commits has to account for the two different scopes the hook checks. Worked out while committing the July 2026 backlog:

* **Index and vault checks look at the whole worktree, not the staged set.** Every commit in the series fails until the *last* file in the backlog is conformant. Fix the whole tree first (run `-FixIndexes`, add missing frontmatter, repair broken links), then slice.
* **The log guard looks only at the staged set**, and it fires on added, copied, or renamed `*.md` concept files. Modified concepts, `index.md`, `log.md`, and non-Markdown files (PDF, images, `.js`, `.css`, `.ps1`) never trigger it.
* **Each slice needs its own staged `log.md` change.** A `log.md` committed in slice one is unchanged by slice two, so slice two counts as having no log. Either give the later slice a genuinely new dated entry, or arrange the slices so that only one of them adds concept files and the rest carry binaries and index files.
* **Any ancestor `log.md` is accepted**, up to the bundle root. A directory without its own log can borrow its parent's, which is the escape hatch when a slice would otherwise need an artificial log file.
* **A stale Inbox capture blocks every commit** once it passes seven days, even when the commit has nothing to do with the Inbox. Either process the capture or refresh its `timestamp` and record what has been routed so far; do not bypass the hook to get around it.

# CI

GitHub Actions runs the same portable check runner through [OKF Vault workflow](/.github/workflows/okf-vault.yml). The staged-change log guard is meaningful in the local pre-commit hook because CI does not have the developer's staged index.

# Related

* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
* [OKF Bundle Practice](/6-System/okf-bundle-practice.md)
* [Naming and Linking Rules](/6-System/naming-and-linking-rules.md)
* [Concept Types and Status Vocabulary](/6-System/concept-types.md)
