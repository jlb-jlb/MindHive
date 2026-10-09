"""End-to-end behaviour of the two subcommands.

The log rule asks whether a note and its log changed together in one session. A file list
cannot answer that, so `lint-files` must skip the check rather than report a failure it has no
evidence for. Shipping that false positive is what these tests exist to prevent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import write_note
from mindhive_automation.cli import main


@pytest.fixture
def note_with_log(vault: Path) -> Path:
    note = write_note(vault / "3-Resources" / "wiki" / "a.md")
    log = vault / "3-Resources" / "wiki" / "log.md"
    log.write_text(
        "---\ntype: Log\ntitle: Log\ndescription: History.\ntags: [log]\n---\n\n# Log\n",
        encoding="utf-8",
    )
    return note


def test_lint_files_does_not_run_the_log_check(
    note_with_log: Path, vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["lint-files", str(note_with_log), "--root", str(vault)])
    out = capsys.readouterr().out
    assert "[log]" not in out
    assert code == 0


def test_lint_files_says_which_check_it_skipped(
    note_with_log: Path, vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Silence must not read as a pass."""
    main(["lint-files", str(note_with_log), "--root", str(vault)])
    out = capsys.readouterr().out
    assert "Not checked: log" in out
    assert "needs a full session" in out


def test_lint_files_scope_wording_is_not_session_wording(
    note_with_log: Path, vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main(["lint-files", str(note_with_log), "--root", str(vault)])
    out = capsys.readouterr().out
    assert "touched this session" not in out
    assert "Vault lint on 1 file:" in out


def test_lint_files_omits_the_agent_directive(vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A human running this by hand does not need to be told to finish their task."""
    broken = vault / "3-Resources" / "wiki" / "b.md"
    broken.parent.mkdir(parents=True, exist_ok=True)
    broken.write_text("# No frontmatter\n", encoding="utf-8")
    code = main(["lint-files", str(broken), "--root", str(vault)])
    out = capsys.readouterr().out
    assert "Do not report the task as done" not in out
    assert code == 2


def test_lint_files_still_reports_frontmatter(vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    note = write_note(vault / "3-Resources" / "a.md", description="Covers MindHive: the order.")
    code = main(["lint-files", str(note), "--root", str(vault)])
    out = capsys.readouterr().out
    assert "does not parse" in out
    assert code == 2


def test_check_flag_narrows_the_run(vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    broken = vault / "3-Resources" / "wiki" / "c.md"
    broken.parent.mkdir(parents=True, exist_ok=True)
    broken.write_text("# No frontmatter\n", encoding="utf-8")
    main(["lint-files", str(broken), "--root", str(vault), "--check", "frontmatter"])
    out = capsys.readouterr().out
    assert "[frontmatter]" in out
    assert "Not checked" not in out


def test_lint_session_keeps_the_log_check(
    vault: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same note, through the session path, must still be judged on its log."""
    note = write_note(vault / "3-Resources" / "wiki" / "d.md")
    (vault / "3-Resources" / "wiki" / "log.md").write_text(
        "---\ntype: Log\ntitle: Log\ndescription: History.\ntags: [log]\n---\n\n# Log\n",
        encoding="utf-8",
    )
    transcript = tmp_path / "s.jsonl"
    record = {
        "type": "assistant",
        "timestamp": "2026-08-13T10:00:00.000Z",
        "message": {"content": [{"type": "tool_use", "name": "Write", "input": {"file_path": str(note)}}]},
    }
    transcript.write_text(json.dumps(record) + "\n", encoding="utf-8")

    code = main(
        [
            "lint-session",
            "--transcript",
            str(transcript),
            "--root",
            str(vault),
            "--no-disk-scan",
            "--dry-run",
        ]
    )
    out = capsys.readouterr().out
    assert "[log] changed without a log update" in out
    assert "touched this session" in out
    assert code == 0
