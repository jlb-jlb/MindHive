"""Rendering findings.

From the Stop hook this goes to stderr, where Claude reads it as the reason it may not stop
yet, so it ends with an instruction. Run by hand it is read by a human, who does not need to be
told to finish their own task.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .checks import Finding, Severity

AGENT_DIRECTIVE = "Fix the errors above, then finish. Do not report the task as done while any remain."


def render(
    findings: list[Finding],
    root: Path,
    *,
    scope: str,
    directive: bool = False,
    skipped: tuple[str, ...] = (),
) -> str:
    """Format findings grouped by file, errors first.

    ``scope`` names what was examined, for example "files touched this session".
    ``skipped`` names checks that could not run, so their silence is not read as a pass.
    """
    if not findings and not skipped:
        return ""

    errors = [f for f in findings if f.severity is Severity.ERROR]
    warnings = [f for f in findings if f.severity is Severity.WARNING]

    lines: list[str] = [_headline(scope, len(errors), len(warnings)), ""]

    for severity, group in ((Severity.ERROR, errors), (Severity.WARNING, warnings)):
        if not group:
            continue
        lines.append(f"{severity.value.upper()}S")
        lines.extend(_render_group(group, root))
        lines.append("")

    if skipped:
        lines.append(f"Not checked: {', '.join(skipped)} (needs a full session, not a file list).")
        lines.append("")

    if errors and directive:
        lines.append(AGENT_DIRECTIVE)

    return "\n".join(lines).rstrip() + "\n"


def _headline(scope: str, errors: int, warnings: int) -> str:
    if not errors and not warnings:
        return f"Vault lint on {scope}: no issues."
    parts = []
    if errors:
        parts.append(f"{errors} error{'s' if errors != 1 else ''}")
    if warnings:
        parts.append(f"{warnings} warning{'s' if warnings != 1 else ''}")
    return f"Vault lint on {scope}: " + ", ".join(parts) + "."


def _render_group(findings: list[Finding], root: Path) -> list[str]:
    by_path: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        by_path[_display(finding.path, root)].append(finding)

    lines: list[str] = []
    for path in sorted(by_path):
        lines.append(f"  {path}")
        for finding in by_path[path]:
            lines.append(f"    [{finding.check}] {finding.message}")
            if finding.fix:
                lines.append(f"      -> {finding.fix}")
    return lines


def _display(path: Path, root: Path) -> str:
    """Vault-relative POSIX path, falling back to the absolute path when outside the vault."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)
