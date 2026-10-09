"""Locating the vault and reading the conventions the checks enforce.

The vault root is found by walking up from a starting directory, so the automation works
regardless of which directory a hook happens to run in.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

# A directory is the vault root when it holds both of these. AGENTS.md alone is too weak,
# since a nested project could carry one.
ROOT_MARKERS = ("AGENTS.md", "6-System")

# Extra infrastructure names that the leading-character rule below does not already cover.
# The vault convention, documented in 6-System/vault-automation.md, is that the scanning scripts
# skip every dot-folder and every top-level directory starting with an underscore.
INFRA_DIRS = frozenset(
    {
        ".git",
        ".github",
        ".githooks",
        ".obsidian",
        ".claude",
        ".agents",
        ".codex",
        "_attachments",
        "tools",
        "_tools",
        "node_modules",
    }
)

# Filenames the frontmatter checks treat leniently. The vault's PowerShell checks skip these
# two entirely; the Frontmatter Contract asks for frontmatter anyway, so a miss is a warning.
RESERVED_FILENAMES = frozenset({"index.md", "log.md"})

# Used when 6-System/concept-types.md cannot be read or parsed. Keep in step with that note.
FALLBACK_CONCEPT_TYPES = frozenset(
    {
        "Area",
        "Capture",
        "Decision",
        "Handoff",
        "Journal",
        "MOC",
        "Project",
        "Reference",
        "Resource",
        "Skill",
        "System",
        "Template",
        "Index",
        "Log",
    }
)

_TYPE_ROW = re.compile(r"^\|\s*`([A-Za-z][A-Za-z0-9_-]*)`\s*\|")


def find_vault_root(start: Path) -> Path | None:
    """Walk up from ``start`` and return the first directory that looks like the vault."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate
    return None


def load_concept_types(root: Path) -> frozenset[str]:
    """Read the controlled type vocabulary from the vault rather than duplicating it here.

    Parses the Markdown tables in ``6-System/concept-types.md``. Falls back to a baked-in set
    when that note is missing or its tables have been restructured, so a documentation edit can
    never take the hook down.
    """
    note = root / "6-System" / "concept-types.md"
    try:
        text = note.read_text(encoding="utf-8")
    except OSError:
        return FALLBACK_CONCEPT_TYPES

    found = {match.group(1) for line in text.splitlines() if (match := _TYPE_ROW.match(line))}
    # A handful of rows means the tables parsed. Anything less means the format moved.
    return frozenset(found) if len(found) >= 5 else FALLBACK_CONCEPT_TYPES


def norm_key(path: Path) -> str:
    """Comparison key for a path.

    Windows paths differ in case and separator between the transcript, git, and the filesystem,
    so every set membership test in this package goes through this function.
    """
    return os.path.normcase(os.path.normpath(str(path)))


@dataclass(frozen=True, slots=True)
class VaultFile:
    """A path classified against the vault layout."""

    path: Path
    relative: Path
    is_markdown: bool
    is_reserved: bool
    in_infra: bool

    @property
    def is_concept(self) -> bool:
        """True for a Markdown note that both checks apply to."""
        return self.is_markdown and not self.is_reserved and not self.in_infra


def classify(path: Path, root: Path) -> VaultFile | None:
    """Describe ``path`` relative to the vault, or None when it sits outside the vault."""
    try:
        resolved = path.resolve()
        relative = resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return None

    return VaultFile(
        path=resolved,
        relative=relative,
        is_markdown=resolved.suffix.lower() == ".md",
        is_reserved=resolved.name.lower() in RESERVED_FILENAMES,
        in_infra=_is_infra(relative.parts),
    )


def _is_infra(parts: tuple[str, ...]) -> bool:
    """Apply the vault's skip rule to a vault-relative path.

    Skipped: any dot-folder, any top-level directory starting with an underscore, and the
    legacy names in INFRA_DIRS. A file sitting at the bundle root is never infrastructure.
    """
    directories = parts[:-1]
    if not directories:
        return False
    if directories[0].startswith(("_", ".")):
        return True
    return any(part in INFRA_DIRS or part.startswith(".") for part in directories)


def ancestor_logs(concept: Path, root: Path) -> list[Path]:
    """Every ``log.md`` that could satisfy the log rule for ``concept``, nearest first.

    Mirrors the pre-commit hook in .githooks/pre-commit, which accepts a log update in the
    concept's own directory or in any ancestor directory up to the bundle root.
    """
    root = root.resolve()
    logs: list[Path] = []
    current = concept.resolve().parent
    while True:
        logs.append(current / "log.md")
        if current == root or root not in current.parents:
            break
        current = current.parent
    return logs
