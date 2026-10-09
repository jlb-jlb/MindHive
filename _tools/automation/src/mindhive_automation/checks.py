"""The checks themselves.

A check is a function over a :class:`Context` returning findings. Register it in :data:`CHECKS`.

Some checks only mean something for a whole session. "Was the log updated alongside this note"
cannot be answered from a list of files handed over on the command line, because the answer
depends on what else the session did. Those carry ``needs_session`` and are skipped when the
context was not built from a session, rather than reporting a failure they cannot judge.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from pathlib import Path

from . import frontmatter
from .transcript import SessionEdits
from .vault import ancestor_logs, classify, load_concept_types

DATE_HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Finding:
    severity: Severity
    path: Path
    check: str
    message: str
    fix: str | None = None


@dataclass(frozen=True, slots=True)
class Context:
    """Everything a check needs to run."""

    root: Path
    edits: SessionEdits
    concept_types: frozenset[str]
    today: date
    session_scoped: bool = True
    """False when the file set came from the command line rather than from a session."""


def build_context(
    root: Path,
    edits: SessionEdits,
    today: date | None = None,
    *,
    session_scoped: bool = True,
) -> Context:
    return Context(
        root=root,
        edits=edits,
        concept_types=load_concept_types(root),
        today=today or date.today(),
        session_scoped=session_scoped,
    )


def _severity_for(is_reserved: bool, was_edited: bool) -> Severity:
    """Reserved filenames warn where a concept note errors.

    A file recovered from the disk scan rather than an edit-tool record also only warns,
    because the session may not be what changed it.
    """
    if is_reserved or not was_edited:
        return Severity.WARNING
    return Severity.ERROR


def check_frontmatter(ctx: Context) -> list[Finding]:
    """Every touched Markdown file parses as frontmatter and carries type and description."""
    findings: list[Finding] = []

    for path in ctx.edits.all_paths().values():
        info = classify(path, ctx.root)
        if info is None or not info.is_markdown or info.in_infra:
            continue
        if not path.exists():
            continue

        severity = _severity_for(info.is_reserved, ctx.edits.was_edited(path))
        block = frontmatter.read(path)

        if not block.present:
            findings.append(
                Finding(
                    severity,
                    path,
                    "frontmatter",
                    "no frontmatter block",
                    "add a --- fenced YAML block with type, title, description, tags, timestamp",
                )
            )
            continue

        if block.error is not None:
            findings.append(
                Finding(
                    severity,
                    path,
                    "frontmatter",
                    f"frontmatter does not parse: {block.error}",
                    "Obsidian uses the same parser, so these properties are invisible to it",
                )
            )
            continue

        data = block.data

        if frontmatter.missing_or_blank(data, "type"):
            findings.append(
                Finding(
                    severity,
                    path,
                    "frontmatter",
                    "type is missing or empty",
                    "required by the frontmatter contract",
                )
            )
        else:
            declared = str(data["type"]).strip()
            if declared not in ctx.concept_types:
                findings.append(
                    Finding(
                        severity,
                        path,
                        "frontmatter",
                        f"type {declared!r} is not in the controlled vocabulary",
                        "allowed: " + ", ".join(sorted(ctx.concept_types)),
                    )
                )

        if frontmatter.missing_or_blank(data, "description"):
            findings.append(
                Finding(
                    severity,
                    path,
                    "frontmatter",
                    "description is missing or empty",
                    "one or two sentences naming the contents and when to open the file",
                )
            )

        for optional in ("title", "tags"):
            if frontmatter.missing_or_blank(data, optional):
                findings.append(
                    Finding(Severity.WARNING, path, "frontmatter", f"{optional} is missing or empty")
                )

    return findings


def check_log_updated(ctx: Context) -> list[Finding]:
    """A touched concept note has a log.md updated in the same session.

    The log may sit in the note's own directory or in any ancestor up to the vault root, which
    matches the rule the pre-commit hook already enforces on staged files.
    """
    findings: list[Finding] = []

    for path in ctx.edits.all_paths().values():
        info = classify(path, ctx.root)
        if info is None or not info.is_concept:
            continue
        if not path.exists():
            continue

        candidates = ancestor_logs(path, ctx.root)
        satisfied = next((log for log in candidates if ctx.edits.was_touched(log)), None)

        if satisfied is not None:
            findings.extend(_check_log_has_todays_entry(ctx, satisfied))
            continue

        existing = [log for log in candidates if log.exists()]
        if not existing:
            findings.append(
                Finding(
                    Severity.WARNING,
                    path,
                    "log",
                    "no log.md exists in this directory or any ancestor",
                    f"create {candidates[0].relative_to(ctx.root).as_posix()}",
                )
            )
            continue

        nearest = existing[0].relative_to(ctx.root).as_posix()
        findings.append(
            Finding(
                _severity_for(info.is_reserved, ctx.edits.was_edited(path)),
                path,
                "log",
                "changed without a log update",
                f"add a dated entry to {nearest}",
            )
        )

    return findings


def _check_log_has_todays_entry(ctx: Context, log: Path) -> list[Finding]:
    """The touched log carries a heading for today, so the entry is findable by date."""
    try:
        text = log.read_text(encoding="utf-8")
    except OSError:
        return []

    headings = set(DATE_HEADING.findall(text))
    accepted = {ctx.today.isoformat(), (ctx.today - timedelta(days=1)).isoformat()}
    if headings & accepted:
        return []

    return [
        Finding(
            Severity.WARNING,
            log,
            "log",
            f"was updated but has no '## {ctx.today.isoformat()}' heading",
            "date the entry so it can be found later",
        )
    ]


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    run: Callable[[Context], list[Finding]]
    needs_session: bool
    """True when the check compares files against each other within one session."""


CHECKS: tuple[Check, ...] = (
    Check("frontmatter", check_frontmatter, needs_session=False),
    Check("log", check_log_updated, needs_session=True),
)

CHECK_NAMES: tuple[str, ...] = tuple(check.name for check in CHECKS)


def selected(ctx: Context, only: set[str] | None = None) -> tuple[Check, ...]:
    """The checks that can run against ``ctx``, optionally narrowed by name."""
    return tuple(
        check
        for check in CHECKS
        if (only is None or check.name in only) and (ctx.session_scoped or not check.needs_session)
    )


def run_all(ctx: Context, only: set[str] | None = None) -> list[Finding]:
    """Run the applicable checks and return findings, errors first, then grouped by path."""
    findings = [finding for check in selected(ctx, only) for finding in check.run(ctx)]
    findings.sort(key=lambda f: (f.severity is Severity.WARNING, str(f.path), f.check))
    # A single check can report the same problem twice when a path arrives from both signals.
    seen: set[tuple[Severity, str, str, str]] = set()
    unique: list[Finding] = []
    for finding in findings:
        key = (finding.severity, str(finding.path), finding.check, finding.message)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique
