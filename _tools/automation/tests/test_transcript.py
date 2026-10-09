from __future__ import annotations

import json
from pathlib import Path

from conftest import write_transcript
from mindhive_automation.transcript import read_transcript
from mindhive_automation.vault import norm_key


def test_collects_edit_tool_paths(tmp_path: Path) -> None:
    targets = [tmp_path / "a.md", tmp_path / "b.md"]
    transcript = write_transcript(tmp_path / "s.jsonl", targets)
    edits = read_transcript(transcript)
    assert set(edits.edited) == {norm_key(p) for p in targets}


def test_records_session_start(tmp_path: Path) -> None:
    transcript = write_transcript(tmp_path / "s.jsonl", [tmp_path / "a.md"])
    edits = read_transcript(transcript)
    assert edits.started_at is not None
    assert edits.started_at.year == 2026


def test_read_tools_are_not_edits(tmp_path: Path) -> None:
    record = {
        "type": "assistant",
        "timestamp": "2026-08-12T10:00:00.000Z",
        "message": {
            "content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": str(tmp_path / "a.md")}},
                {"type": "tool_use", "name": "Glob", "input": {"pattern": "**/*.md"}},
            ]
        },
    }
    transcript = tmp_path / "s.jsonl"
    transcript.write_text(json.dumps(record) + "\n", encoding="utf-8")
    assert read_transcript(transcript).edited == {}


def test_notebook_edit_path_key(tmp_path: Path) -> None:
    record = {
        "type": "assistant",
        "timestamp": "2026-08-12T10:00:00.000Z",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "name": "NotebookEdit",
                    "input": {"notebook_path": str(tmp_path / "n.ipynb")},
                }
            ]
        },
    }
    transcript = tmp_path / "s.jsonl"
    transcript.write_text(json.dumps(record) + "\n", encoding="utf-8")
    assert set(read_transcript(transcript).edited) == {norm_key(tmp_path / "n.ipynb")}


def test_torn_final_line_is_skipped(tmp_path: Path) -> None:
    """A transcript is appended to while the session runs, so the last line can be partial."""
    transcript = write_transcript(tmp_path / "s.jsonl", [tmp_path / "a.md"])
    with transcript.open("a", encoding="utf-8") as handle:
        handle.write('{"type": "assistant", "mess')
    assert set(read_transcript(transcript).edited) == {norm_key(tmp_path / "a.md")}


def test_missing_transcript_is_empty(tmp_path: Path) -> None:
    edits = read_transcript(tmp_path / "nope.jsonl")
    assert edits.edited == {}
    assert edits.started_at is None
