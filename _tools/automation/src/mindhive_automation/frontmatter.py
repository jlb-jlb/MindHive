"""Reading YAML frontmatter the way a strict consumer reads it.

Obsidian and any YAML library parse the block strictly. A line-oriented parser is more
forgiving and therefore useless as a check, because it passes files whose properties Obsidian
will silently refuse to display.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

FENCE = "---"


@dataclass(frozen=True, slots=True)
class Frontmatter:
    """Result of parsing the leading YAML block of a Markdown file."""

    present: bool
    data: dict[str, Any]
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.present and self.error is None


def read(path: Path) -> Frontmatter:
    """Parse the frontmatter block of ``path``.

    Returns ``present=False`` when the file does not open with a fence, and a populated
    ``error`` when the block is unterminated or is not a YAML mapping.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Frontmatter(present=False, data={}, error="file is not valid UTF-8")
    except OSError as exc:
        return Frontmatter(present=False, data={}, error=f"could not read file: {exc}")

    return parse(text)


def parse(text: str) -> Frontmatter:
    """Parse frontmatter out of raw Markdown text."""
    # A byte order mark ahead of the fence stops both Obsidian and a naive parser from seeing it.
    stripped = text.lstrip("﻿")
    lines = stripped.splitlines()

    if not lines or lines[0].strip() != FENCE:
        return Frontmatter(present=False, data={})

    closing = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == FENCE), None)
    if closing is None:
        return Frontmatter(present=True, data={}, error="frontmatter block is never closed")

    block = "\n".join(lines[1:closing])
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return Frontmatter(present=True, data={}, error=_explain(exc))

    if loaded is None:
        return Frontmatter(present=True, data={}, error="frontmatter block is empty")
    if not isinstance(loaded, dict):
        return Frontmatter(
            present=True, data={}, error=f"frontmatter is {type(loaded).__name__}, expected a mapping"
        )
    return Frontmatter(present=True, data=loaded)


def _explain(exc: yaml.YAMLError) -> str:
    """Turn a YAML exception into one actionable line.

    The common failure in this vault is an unquoted value containing a colon followed by a
    space, which YAML reads as the start of a nested mapping.
    """
    mark = getattr(exc, "problem_mark", None)
    problem = getattr(exc, "problem", None) or "invalid YAML"
    where = f" at line {mark.line + 1}" if mark is not None else ""
    hint = ""
    if "mapping values are not allowed" in problem:
        hint = ' (a value containing ": " must be quoted, or rewrite the sentence to avoid the colon)'
    return f"{problem}{where}{hint}"


def missing_or_blank(data: dict[str, Any], field: str) -> bool:
    """True when ``field`` is absent, None, or an empty or whitespace-only string."""
    if field not in data:
        return True
    value = data[field]
    if value is None:
        return True
    return isinstance(value, str) and not value.strip()
