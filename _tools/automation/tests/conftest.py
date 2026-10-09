from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """A minimal vault carrying the two root markers and the type vocabulary."""
    (tmp_path / "AGENTS.md").write_text("# Agent Session Instructions\n", encoding="utf-8")
    system = tmp_path / "6-System"
    system.mkdir()
    (system / "concept-types.md").write_text(
        "# Concept Types\n\n"
        "| Type | Use |\n|---|---|\n"
        "| `Resource` | Reusable knowledge. |\n"
        "| `System` | Operating rule. |\n"
        "| `Project` | Active outcome. |\n"
        "| `Reference` | Source material. |\n"
        "| `MOC` | Map of Content. |\n\n"
        "# Reserved File Types\n\n"
        "| Type | Use |\n|---|---|\n"
        "| `Index` | Directory map. |\n"
        "| `Log` | Update history. |\n",
        encoding="utf-8",
    )
    return tmp_path


def write_note(path: Path, *, type_: str = "Resource", description: str = "A real description.") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntype: {type_}\ntitle: {path.stem}\ndescription: {description}\ntags: [demo]\n---\n\n# Body\n",
        encoding="utf-8",
    )
    return path


def write_transcript(path: Path, edited: list[Path], *, timestamp: str = "2026-08-12T10:00:00.000Z") -> Path:
    """Write a JSONL transcript in the shape Claude Code produces."""
    records = [
        {
            "type": "assistant",
            "timestamp": timestamp,
            "cwd": str(path.parent),
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": f"toolu_{index}",
                        "name": "Write",
                        "input": {"file_path": str(target), "content": "x"},
                    }
                ],
            },
        }
        for index, target in enumerate(edited)
    ]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return path
