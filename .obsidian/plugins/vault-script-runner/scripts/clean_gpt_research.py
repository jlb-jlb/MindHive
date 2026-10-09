#!/usr/bin/env python3
"""
Clean a ChatGPT "deep research" Markdown report so it renders correctly in
Obsidian.

Two classes of artifact are fixed:

1. Math delimiters. ChatGPT emits LaTeX with ``\\(`` ... ``\\)`` for inline math
   and ``\\[`` ... ``\\]`` for display math. Obsidian expects ``$`` ... ``$`` and
   ``$$`` ... ``$$``. They are converted here.

2. Citation artifacts. ChatGPT wraps citations in Private Use Area control
   characters, for example ``citeturn20search16``. These are
   invisible junk once pasted, so the whole run is removed.

Sandbox download links such as ``[Download](sandbox:/mnt/data/x.md)`` are also
flattened to plain text, and excessive blank lines are collapsed.

Code blocks (fenced ``` blocks and inline ``code`` spans) are protected, so a
``\\(`` that appears inside a code sample is never rewritten as math.

The script uses only the Python standard library.

Example:
    python clean_gpt_research.py ^
        --vault "C:\\Users\\me\\Documents\\MyVault" ^
        --in-place ^
        "10_Research/Source_Documents/Report.md"
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from pathlib import Path


# Private Use Area characters ChatGPT uses to delimit citation runs.
CITE_OPEN = ""
CITE_CLOSE = ""

# A whole citation run: open marker, anything (often spanning lines), close marker.
CITATION_RUN = re.compile(r".*?", re.DOTALL)
# Any stray Private Use Area control char left behind.
STRAY_PUA = re.compile(r"[-]")

# Fenced code blocks: opening fence (3+ backticks or tildes) ... matching fence.
FENCED_CODE = re.compile(
    r"(?ms)^(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^(?P=fence)[ \t]*$"
)
# Inline code spans of one or two backticks, not crossing line boundaries.
INLINE_CODE = re.compile(r"(?P<tick>`{1,2})(?:(?!(?P=tick)).)+?(?P=tick)")

# Display math: \[ ... \]  (content may span lines).
DISPLAY_MATH = re.compile(r"\\\[\s*(.*?)\s*\\\]", re.DOTALL)
# Inline math: \( ... \)
INLINE_MATH = re.compile(r"\\\((.*?)\\\)", re.DOTALL)

# Markdown link whose target is a ChatGPT sandbox path.
SANDBOX_LINK = re.compile(r"\[([^\]]*)\]\(sandbox:[^)]*\)")


def protect(text: str, pattern: re.Pattern, store: list[str], tag: str) -> str:
    """Replace every ``pattern`` match with a placeholder, saving the original."""

    def _stash(match: re.Match) -> str:
        token = f"\x00{tag}{len(store)}\x00"
        store.append(match.group(0))
        return token

    return pattern.sub(_stash, text)


def restore(text: str, store: list[str], tag: str) -> str:
    """Swap placeholders back for their original text."""
    for index, original in enumerate(store):
        text = text.replace(f"\x00{tag}{index}\x00", original)
    return text


def convert_math(text: str) -> str:
    text = DISPLAY_MATH.sub(lambda m: f"$$\n{m.group(1).strip()}\n$$", text)
    text = INLINE_MATH.sub(lambda m: f"${m.group(1).strip()}$", text)
    return text


def remove_citations(text: str) -> str:
    text = CITATION_RUN.sub("", text)
    text = STRAY_PUA.sub("", text)
    return text


def flatten_sandbox_links(text: str) -> str:
    return SANDBOX_LINK.sub(lambda m: m.group(1), text)


def tidy_whitespace(text: str) -> str:
    # Drop trailing spaces left where a citation used to be.
    text = re.sub(r"[ \t]+(\r?\n)", r"\1", text)
    # Collapse 3+ blank lines into a single blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def clean_report(
    text: str,
    *,
    convert_formulas: bool = True,
    strip_citations: bool = True,
    flatten_sandbox: bool = True,
) -> str:
    """Run the full cleaning pipeline on a Markdown string."""
    # Protect code first so math/citation rules never touch code samples.
    fenced: list[str] = []
    inline: list[str] = []
    text = protect(text, FENCED_CODE, fenced, "FENCE")
    text = protect(text, INLINE_CODE, inline, "CODE")

    if strip_citations:
        text = remove_citations(text)
    if convert_formulas:
        text = convert_math(text)
    if flatten_sandbox:
        text = flatten_sandbox_links(text)

    # Restore inline code before fenced so nested placeholders resolve cleanly.
    text = restore(text, inline, "CODE")
    text = restore(text, fenced, "FENCE")

    text = tidy_whitespace(text)
    return text


def resolve_inside_vault(vault: Path, value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = vault / path

    resolved = path.resolve()
    try:
        resolved.relative_to(vault)
    except ValueError:
        raise SystemExit(f"{label} must be inside the Obsidian vault: {resolved}")

    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Clean a ChatGPT deep-research Markdown report for Obsidian: "
            "convert LaTeX math delimiters and strip citation artifacts."
        )
    )
    parser.add_argument(
        "input",
        help="Markdown report to clean. Relative paths resolve from --vault.",
    )
    parser.add_argument(
        "--vault",
        required=True,
        help="Path to the Obsidian vault root.",
    )
    parser.add_argument(
        "--output",
        help=(
            "Where to write the cleaned note. Relative paths resolve from the "
            "vault. Defaults to '<name> (cleaned).md' next to the input, unless "
            "--in-place is given."
        ),
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input file with the cleaned content.",
    )
    parser.add_argument(
        "--keep-citations",
        action="store_true",
        help="Do not remove ChatGPT citation artifacts.",
    )
    parser.add_argument(
        "--keep-formulas",
        action="store_true",
        help="Do not convert \\( \\) and \\[ \\] math delimiters.",
    )
    parser.add_argument(
        "--keep-sandbox-links",
        action="store_true",
        help="Do not flatten [text](sandbox:...) links to plain text.",
    )
    return parser.parse_args()


def write_output(output_md: Path, content: str) -> None:
    """Write the cleaned note, clearing a read-only attribute if one blocks it."""
    try:
        output_md.write_text(content, encoding="utf-8")
        return
    except PermissionError:
        # On Windows an existing file with the read-only attribute (or a 0o444
        # mode on POSIX) raises PermissionError. Clear it and retry once.
        if not output_md.exists():
            raise
    try:
        os.chmod(output_md, stat.S_IWRITE | stat.S_IREAD)
        output_md.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"Permission denied writing {output_md}. The file may be read-only, "
            "open with an exclusive lock in another program, or held by a cloud "
            f"sync client. Close it or clear its read-only flag, then retry. ({exc})"
        )


def main() -> int:
    args = parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if not vault.exists() or not vault.is_dir():
        print(f"Vault does not exist or is not a directory: {vault}", file=sys.stderr)
        return 1

    if not args.input.strip():
        print(
            "No input file given. Open the report in Obsidian (so {{activeFile}} "
            "resolves) or pass a Markdown path explicitly.",
            file=sys.stderr,
        )
        return 1

    input_md = resolve_inside_vault(vault, args.input, "input")
    if not input_md.exists() or not input_md.is_file():
        print(f"Input is not a file: {input_md}", file=sys.stderr)
        return 1

    if args.output:
        output_md = resolve_inside_vault(vault, args.output, "--output")
    elif args.in_place:
        output_md = input_md
    else:
        output_md = input_md.with_name(f"{input_md.stem} (cleaned){input_md.suffix}")

    original = input_md.read_text(encoding="utf-8")
    cleaned = clean_report(
        original,
        convert_formulas=not args.keep_formulas,
        strip_citations=not args.keep_citations,
        flatten_sandbox=not args.keep_sandbox_links,
    )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    write_output(output_md, cleaned)

    citations_removed = len(CITATION_RUN.findall(original))
    display_converted = len(DISPLAY_MATH.findall(original))
    inline_converted = len(INLINE_MATH.findall(original))
    print(f"Removed {citations_removed} citation run(s)")
    print(f"Converted {display_converted} display and {inline_converted} inline formula(s)")
    print(f"Wrote cleaned note to: {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
