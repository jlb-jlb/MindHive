# MindHive Automation

Python automation for the vault, run through `uv`. Cross-platform by design, which is why this
exists alongside the PowerShell scripts in `_tools/`.

## Setup

```bash
uv sync --all-groups
```

That is the whole setup. `uv` reads `.python-version` (3.13), creates `.venv/`, and installs
from `uv.lock`. Nothing needs activating, and every command below works the same on Windows,
macOS, and Linux.

## The session linter

Runs from the Claude Code `Stop` hook declared in `/.claude/settings.json`, and checks only the
files that session touched.

| Check | Rule |
|---|---|
| `frontmatter` | Every touched Markdown file parses as YAML and carries a `type` from the vault vocabulary plus a non-empty `description`. |
| `log` | A touched concept note has a `log.md` updated in the same session, in its own directory or any ancestor. |

Errors block the session and are fed back to Claude. Warnings print and let it stop.

### Running it by hand

```bash
uv run mindhive-automation lint-files 3-Resources/wiki/some-note.md
```

`lint-files` runs only the checks a file list can actually answer. The log rule asks whether a
note and its `log.md` changed together in one session, which a list of paths cannot say, so it
is skipped and the skip is printed. Silence would otherwise read as a pass. Narrow the run
further with `--check frontmatter`.

```bash
uv run mindhive-automation lint-session --transcript <path-to.jsonl> --dry-run
```

Useful flags on `lint-session`: `--no-disk-scan`, `--warnings-as-errors`, `--dry-run`, `--root`.

## Development

```bash
uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest
```

All four must pass. Adding a check means writing a function of the same shape in `checks.py`
and listing it in `CHECKS`.

## How touched files are found

Two signals with different confidence, kept apart deliberately:

* **The transcript.** Every `Write`, `Edit`, and `NotebookEdit` call records an absolute
  `file_path`. Exact, so findings against it are errors.
* **The disk scan.** An edit made through the Bash tool leaves no such record, so git's
  changed-file list is intersected with modification times inside the session window. That can
  also catch a file the human changed in Obsidian while the session ran, so findings against it
  are warnings.

Full reasoning: [Vault Automation](../../6-System/vault-automation.md).
