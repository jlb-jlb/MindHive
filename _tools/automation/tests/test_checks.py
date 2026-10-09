from __future__ import annotations

from datetime import date
from pathlib import Path

from conftest import write_note
from mindhive_automation.checks import Severity, build_context, run_all
from mindhive_automation.transcript import SessionEdits
from mindhive_automation.vault import norm_key

TODAY = date(2026, 8, 12)

LOG_FRONTMATTER = "---\ntype: Log\ntitle: Log\ndescription: History.\ntags: [log]\n---\n"


def edits_for(*paths: Path) -> SessionEdits:
    edits = SessionEdits()
    for path in paths:
        edits.edited[norm_key(path)] = path
    return edits


def touched_on_disk(edits: SessionEdits, *paths: Path) -> SessionEdits:
    for path in paths:
        edits.also_changed[norm_key(path)] = path
    return edits


def write_log(vault: Path, folder: str, day: date = TODAY) -> Path:
    log = vault / folder / "log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    body = f"\n# Log\n\n## {day.isoformat()}\n* **Update**: x\n"
    log.write_text(LOG_FRONTMATTER + body, encoding="utf-8")
    return log


def run(vault: Path, edits: SessionEdits) -> list:
    return run_all(build_context(vault, edits, today=TODAY))


def test_clean_note_with_log_passes(vault: Path) -> None:
    note = write_note(vault / "3-Resources" / "a.md")
    log = write_log(vault, "3-Resources")
    assert run(vault, edits_for(note, log)) == []


def test_note_without_log_update_is_an_error(vault: Path) -> None:
    note = write_note(vault / "3-Resources" / "a.md")
    write_log(vault, "3-Resources")
    findings = run(vault, edits_for(note))
    log_findings = [f for f in findings if f.check == "log"]
    assert len(log_findings) == 1
    assert log_findings[0].severity is Severity.ERROR
    assert "3-Resources/log.md" in (log_findings[0].fix or "")


def test_ancestor_log_satisfies_the_rule(vault: Path) -> None:
    """The pre-commit hook accepts any ancestor log, so this must too."""
    note = write_note(vault / "3-Resources" / "wiki" / "a.md")
    parent_log = write_log(vault, "3-Resources")
    assert [f for f in run(vault, edits_for(note, parent_log)) if f.check == "log"] == []


def test_missing_log_anywhere_is_only_a_warning(vault: Path) -> None:
    note = write_note(vault / "3-Resources" / "a.md")
    findings = [f for f in run(vault, edits_for(note)) if f.check == "log"]
    assert len(findings) == 1
    assert findings[0].severity is Severity.WARNING
    assert "no log.md exists" in findings[0].message


def test_log_without_todays_heading_warns(vault: Path) -> None:
    note = write_note(vault / "3-Resources" / "a.md")
    log = write_log(vault, "3-Resources", day=date(2026, 1, 1))
    findings = [f for f in run(vault, edits_for(note, log)) if f.check == "log"]
    assert len(findings) == 1
    assert findings[0].severity is Severity.WARNING
    assert "2026-08-12" in findings[0].message


def test_missing_frontmatter_is_an_error(vault: Path) -> None:
    note = vault / "3-Resources" / "a.md"
    note.parent.mkdir(parents=True)
    note.write_text("# No frontmatter\n", encoding="utf-8")
    write_log(vault, "3-Resources")
    findings = [f for f in run(vault, edits_for(note)) if f.check == "frontmatter"]
    assert any(f.severity is Severity.ERROR and "no frontmatter" in f.message for f in findings)


def test_unknown_type_is_rejected(vault: Path) -> None:
    note = write_note(vault / "3-Resources" / "a.md", type_="Invented")
    log = write_log(vault, "3-Resources")
    findings = [f for f in run(vault, edits_for(note, log)) if f.check == "frontmatter"]
    assert any("not in the controlled vocabulary" in f.message for f in findings)


def test_unparseable_description_is_reported(vault: Path) -> None:
    note = write_note(vault / "3-Resources" / "a.md", description="Covers MindHive: the reading order.")
    log = write_log(vault, "3-Resources")
    findings = [f for f in run(vault, edits_for(note, log)) if f.check == "frontmatter"]
    assert any("does not parse" in f.message for f in findings)


def test_reserved_filenames_only_warn(vault: Path) -> None:
    """index.md and log.md are skipped by the PowerShell checks, so a miss here is not fatal."""
    index = vault / "3-Resources" / "index.md"
    index.parent.mkdir(parents=True)
    index.write_text("# Resources\n", encoding="utf-8")
    findings = run(vault, edits_for(index))
    assert findings
    assert all(f.severity is Severity.WARNING for f in findings)


def test_infrastructure_directories_are_skipped(vault: Path) -> None:
    readme = vault / "_tools" / "automation" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("# Tooling\n", encoding="utf-8")
    assert run(vault, edits_for(readme)) == []


def test_disk_only_changes_downgrade_to_warnings(vault: Path) -> None:
    """A file recovered by the mtime scan may have been changed by the human, so it warns."""
    note = write_note(vault / "3-Resources" / "a.md")
    write_log(vault, "3-Resources")
    findings = [f for f in run(vault, touched_on_disk(SessionEdits(), note)) if f.check == "log"]
    assert len(findings) == 1
    assert findings[0].severity is Severity.WARNING


def test_deleted_file_is_ignored(vault: Path) -> None:
    assert run(vault, edits_for(vault / "3-Resources" / "gone.md")) == []


def test_file_outside_the_vault_is_ignored(vault: Path, tmp_path: Path) -> None:
    outside = tmp_path.parent / "elsewhere.md"
    outside.write_text("# Nothing\n", encoding="utf-8")
    assert run(vault, edits_for(outside)) == []
