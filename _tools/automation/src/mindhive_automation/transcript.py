"""Working out which files a session touched.

Two signals, deliberately kept apart because they carry different confidence:

* The transcript records every ``Write``, ``Edit``, and ``NotebookEdit`` call with an absolute
  ``file_path``. This is exact, and findings against it are errors.
* An edit made through the Bash tool (``sed -i``, a heredoc, a redirect) leaves no such record.
  Those are recovered by intersecting git's changed-file list with modification times inside the
  session window, which can also catch a file the human edited in Obsidian while the session ran.
  That ambiguity is why findings against it are warnings.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .vault import norm_key

# Tools whose input names a file they wrote. Read and Glob are deliberately absent: opening a
# file is not touching it.
EDIT_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})
PATH_KEYS = ("file_path", "notebook_path", "path")


@dataclass(slots=True)
class SessionEdits:
    """Files a session changed, split by how confidently we know it."""

    edited: dict[str, Path] = field(default_factory=dict)
    """Recorded by an edit tool. Keyed by :func:`~mindhive_automation.vault.norm_key`."""

    also_changed: dict[str, Path] = field(default_factory=dict)
    """Changed on disk during the session with no edit-tool record."""

    started_at: datetime | None = None

    def all_paths(self) -> dict[str, Path]:
        return {**self.also_changed, **self.edited}

    def was_edited(self, path: Path) -> bool:
        return norm_key(path) in self.edited

    def was_touched(self, path: Path) -> bool:
        return norm_key(path) in self.edited or norm_key(path) in self.also_changed


def _iter_records(transcript: Path) -> Iterator[dict[str, Any]]:
    """Yield the JSON records of a transcript, skipping anything unparseable.

    A transcript is appended to while the session runs, so the final line can be a partial
    write. Skipping bad lines keeps the hook working rather than crashing on a torn record.
    """
    try:
        handle = transcript.open(encoding="utf-8", errors="replace")
    except OSError:
        return
    with handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def read_transcript(transcript: Path) -> SessionEdits:
    """Collect edit-tool file paths and the session start time from a transcript."""
    edits = SessionEdits()
    earliest: datetime | None = None

    for record in _iter_records(transcript):
        stamp = _parse_timestamp(record.get("timestamp"))
        if stamp is not None and (earliest is None or stamp < earliest):
            earliest = stamp

        message = record.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") not in EDIT_TOOLS:
                continue
            payload = block.get("input")
            if not isinstance(payload, dict):
                continue
            for key in PATH_KEYS:
                raw = payload.get(key)
                if isinstance(raw, str) and raw.strip():
                    path = Path(raw)
                    edits.edited[norm_key(path)] = path
                    break

    edits.started_at = earliest
    return edits


def add_disk_changes(edits: SessionEdits, root: Path) -> None:
    """Add files git reports as changed whose mtime falls inside the session window.

    Only files not already recorded by an edit tool are added. Without a session start time
    nothing is added, since every uncommitted file in the vault would otherwise be reported.
    """
    if edits.started_at is None:
        return

    cutoff = edits.started_at.timestamp()
    for path in _git_changed(root):
        key = norm_key(path)
        if key in edits.edited:
            continue
        try:
            if path.stat().st_mtime >= cutoff:
                edits.also_changed[key] = path
        except OSError:
            continue


def _git_changed(root: Path) -> Iterator[Path]:
    """Yield paths git reports as modified, added, or untracked."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if result.returncode != 0:
        return

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        entry = line[3:]
        # A rename is reported as "old -> new"; only the destination exists on disk.
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        yield root / entry.strip().strip('"')


def collect(transcript: Path, root: Path, *, scan_disk: bool = True) -> SessionEdits:
    """Full touched-file set for a session."""
    edits = read_transcript(transcript)
    if scan_disk:
        add_disk_changes(edits, root)
    return edits
