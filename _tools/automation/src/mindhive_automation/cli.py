"""Command line entry points, including the Claude Code Stop hook.

Exit codes for ``lint-session`` follow the Claude Code hook contract:

* ``0`` clean, or nothing to check. The session stops normally.
* ``2`` errors found. Claude does not stop, and stderr is fed back to it as the reason.
* ``1`` the hook itself failed. Non-blocking, shown to the human so the bug is visible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import report
from .checks import CHECK_NAMES, CHECKS, Severity, build_context, run_all, selected
from .transcript import SessionEdits, collect, read_transcript
from .vault import find_vault_root, norm_key

EXIT_OK = 0
EXIT_INTERNAL_ERROR = 1
EXIT_BLOCK = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mindhive-automation",
        description="Vault automation for the MindHive OKF bundle.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    session = sub.add_parser(
        "lint-session",
        help="Lint the files touched in a Claude Code session. Reads the hook payload on stdin.",
    )
    session.add_argument(
        "--transcript",
        type=Path,
        help="Transcript path to read instead of the stdin payload. For testing.",
    )
    session.add_argument(
        "--root",
        type=Path,
        help="Vault root. Defaults to walking up from the current directory.",
    )
    session.add_argument(
        "--no-disk-scan",
        action="store_true",
        help="Skip the git and mtime scan that recovers edits made through Bash.",
    )
    session.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Block on warnings too.",
    )
    session.add_argument(
        "--dry-run",
        action="store_true",
        help="Always exit 0 and print the report to stdout. For testing.",
    )
    _add_check_flag(session)
    session.set_defaults(func=_lint_session)

    files = sub.add_parser(
        "lint-files",
        help=(
            "Lint explicit paths. Session-scoped checks are skipped, since a file list "
            "cannot say what else a session did."
        ),
    )
    files.add_argument("paths", nargs="+", type=Path)
    files.add_argument("--root", type=Path)
    _add_check_flag(files)
    files.set_defaults(func=_lint_files)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"mindhive-automation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR


def _add_check_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--check",
        action="append",
        choices=CHECK_NAMES,
        dest="checks",
        help="Run only this check. Repeatable. Defaults to every applicable check.",
    )


def _read_payload() -> dict[str, Any]:
    """Read the hook JSON from stdin, tolerating an empty or non-JSON stream."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve_root(explicit: Path | None, payload: dict[str, Any]) -> Path | None:
    for candidate in (explicit, payload.get("cwd"), Path.cwd()):
        if candidate is None:
            continue
        found = find_vault_root(Path(candidate))
        if found is not None:
            return found
    return None


def _lint_session(args: argparse.Namespace) -> int:
    payload = {} if args.transcript else _read_payload()

    # Loop guard. Claude Code sets this when the session is already continuing because of a
    # Stop hook, so blocking again would never terminate.
    if payload.get("stop_hook_active"):
        return EXIT_OK

    root = _resolve_root(args.root, payload)
    if root is None:
        # Not inside the vault. Say nothing rather than nagging in an unrelated project.
        return EXIT_OK

    transcript_path = args.transcript or payload.get("transcript_path")
    if not transcript_path:
        return EXIT_OK
    transcript = Path(transcript_path)
    if not transcript.exists():
        return EXIT_OK

    edits = collect(transcript, root, scan_disk=not args.no_disk_scan)
    if not edits.all_paths():
        return EXIT_OK

    only = set(args.checks) if args.checks else None
    ctx = build_context(root, edits)
    findings = run_all(ctx, only)
    blocking = [
        f
        for f in findings
        if f.severity is Severity.ERROR or (args.warnings_as_errors and f.severity is Severity.WARNING)
    ]

    count = len(edits.all_paths())
    scope = f"{count} file{'s' if count != 1 else ''} touched this session"

    if not findings:
        print(f"Vault lint on {scope}: no issues.")
        return EXIT_OK

    text = report.render(findings, root, scope=scope, directive=not args.dry_run)
    if args.dry_run or not blocking:
        # Warnings alone go to the human on stdout without interrupting the session.
        print(text)
        return EXIT_OK

    print(text, file=sys.stderr)
    return EXIT_BLOCK


def _lint_files(args: argparse.Namespace) -> int:
    root = _resolve_root(args.root, {})
    if root is None:
        print("not inside a MindHive vault", file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    edits = SessionEdits()
    for path in args.paths:
        resolved = path.resolve()
        edits.edited[norm_key(resolved)] = resolved

    only = set(args.checks) if args.checks else None
    # A file list carries no session history, so checks that compare files against each other
    # within a session cannot be judged and are reported as skipped rather than failed.
    ctx = build_context(root, edits, session_scoped=False)
    findings = run_all(ctx, only)

    ran = {check.name for check in selected(ctx, only)}
    skipped = tuple(c.name for c in CHECKS if c.name not in ran and (only is None or c.name in only))

    count = len(args.paths)
    scope = f"{count} file{'s' if count != 1 else ''}"

    if not findings and not skipped:
        print(f"Vault lint on {scope}: no issues.")
        return EXIT_OK

    print(report.render(findings, root, scope=scope, skipped=skipped))
    return EXIT_BLOCK if any(f.severity is Severity.ERROR for f in findings) else EXIT_OK


__all__ = ["main", "read_transcript"]
