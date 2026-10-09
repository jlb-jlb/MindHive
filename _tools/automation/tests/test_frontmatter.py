from __future__ import annotations

from mindhive_automation import frontmatter


def test_valid_block_parses() -> None:
    result = frontmatter.parse("---\ntype: Resource\ntitle: A\n---\n\n# Body\n")
    assert result.ok
    assert result.data["type"] == "Resource"


def test_missing_block() -> None:
    result = frontmatter.parse("# Body only\n")
    assert not result.present
    assert result.error is None


def test_unterminated_block() -> None:
    result = frontmatter.parse("---\ntype: Resource\n")
    assert result.present
    assert result.error is not None
    assert "never closed" in result.error


def test_unquoted_colon_is_rejected_with_a_hint() -> None:
    """The failure this vault actually hits: a description containing a colon and a space."""
    text = "---\ntype: System\ndescription: Instructions for MindHive: reading order and rules.\n---\n"
    result = frontmatter.parse(text)
    assert result.error is not None
    assert "must be quoted" in result.error


def test_quoting_the_colon_value_fixes_it() -> None:
    text = '---\ntype: System\ndescription: "Instructions for MindHive: reading order."\n---\n'
    result = frontmatter.parse(text)
    assert result.ok
    assert result.data["description"].endswith("reading order.")


def test_byte_order_mark_before_the_fence() -> None:
    result = frontmatter.parse("﻿---\ntype: Log\n---\n")
    assert result.ok


def test_empty_block() -> None:
    result = frontmatter.parse("---\n---\n")
    assert result.error == "frontmatter block is empty"


def test_non_mapping_block() -> None:
    result = frontmatter.parse("---\n- a\n- b\n---\n")
    assert result.error is not None
    assert "expected a mapping" in result.error


def test_missing_or_blank() -> None:
    data = {"a": "x", "b": "  ", "c": None}
    assert not frontmatter.missing_or_blank(data, "a")
    assert frontmatter.missing_or_blank(data, "b")
    assert frontmatter.missing_or_blank(data, "c")
    assert frontmatter.missing_or_blank(data, "missing")
