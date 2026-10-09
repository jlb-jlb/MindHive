"""The skip rule must agree with 6-System/vault-automation.md.

The PowerShell scripts and this linter both walk the vault. When their skip rules disagree, one
of them descends into a virtualenv, which is the trap that produced the tools -> _tools rename
on 2026-08-12.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mindhive_automation.vault import (
    FALLBACK_CONCEPT_TYPES,
    ancestor_logs,
    classify,
    find_vault_root,
    load_concept_types,
)


@pytest.mark.parametrize(
    ("relative", "expected"),
    [
        ("3-Resources/wiki/a.md", False),
        ("6-System/a.md", False),
        ("index.md", False),
        ("README.md", False),
        ("_tools/automation/README.md", True),
        ("_tools/automation/.venv/Lib/site-packages/pkg/README.md", True),
        ("_attachments/note.md", True),
        (".github/workflows/readme.md", True),
        (".obsidian/plugins/x/readme.md", True),
        ("3-Resources/.hidden/a.md", True),
    ],
)
def test_skip_rule(vault: Path, relative: str, expected: bool) -> None:
    info = classify(vault / relative, vault)
    assert info is not None
    assert info.in_infra is expected


def test_root_marker_detection(vault: Path) -> None:
    nested = vault / "3-Resources" / "wiki"
    nested.mkdir(parents=True)
    assert find_vault_root(nested) == vault.resolve()


def test_outside_a_vault_returns_none(tmp_path: Path) -> None:
    stray = tmp_path / "not-a-vault"
    stray.mkdir()
    assert find_vault_root(stray) is None


def test_concept_types_come_from_the_vault(vault: Path) -> None:
    types = load_concept_types(vault)
    assert "Resource" in types
    assert "Log" in types
    assert "Invented" not in types


def test_concept_types_fall_back_when_the_note_moves(tmp_path: Path) -> None:
    assert load_concept_types(tmp_path) == FALLBACK_CONCEPT_TYPES


def test_ancestor_logs_walk_up_to_the_root(vault: Path) -> None:
    note = vault / "3-Resources" / "wiki" / "a.md"
    logs = ancestor_logs(note, vault)
    relative = [log.relative_to(vault).as_posix() for log in logs]
    assert relative == ["3-Resources/wiki/log.md", "3-Resources/log.md", "log.md"]
