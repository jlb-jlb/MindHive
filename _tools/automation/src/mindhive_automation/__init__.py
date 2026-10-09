"""Vault automation for the MindHive OKF bundle.

Entry point: ``mindhive-automation lint-session``, wired to the Claude Code Stop hook in
``.claude/settings.json``.
"""

from __future__ import annotations

import sys

__version__ = "0.1.0"


def main() -> None:
    """Console script wrapper so the exit code reaches the shell."""
    from .cli import main as run

    sys.exit(run())
