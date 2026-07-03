"""Unit tests for the chat parser / chunker.

Run from the backend directory:  python -m pytest
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chat_parser import (
    parse_chat,
    _detect_role_lines,
    _extract_code_blocks,
    _number_code_placeholders,
    CHUNK_CHAR_LIMIT,
)


def test_detect_roles_splits_user_and_assistant():
    text = "User: hello there\nAssistant: hi, how can I help?"
    messages = _detect_role_lines(text)
    roles = [m.role for m in messages]
    assert roles == ["user", "assistant"]
    assert "hello there" in messages[0].content


def test_no_role_markers_returns_single_unknown_message():
    messages = _detect_role_lines("just some freeform notes about a project")
    assert len(messages) == 1
    assert messages[0].role == "unknown"


def test_extract_code_blocks_pulls_out_fences():
    text = "before\n```python\nprint('hi')\n```\nafter"
    cleaned, blocks = _extract_code_blocks(text)
    assert blocks == ["print('hi')"]
    assert "print('hi')" not in cleaned
    assert "before" in cleaned and "after" in cleaned


def test_code_placeholders_numbered_in_order():
    cleaned, blocks = _extract_code_blocks("```\na\n```\nmid\n```\nb\n```")
    assert blocks == ["a", "b"]
    numbered = _number_code_placeholders(cleaned)
    assert "[CODE_BLOCK_1]" in numbered
    assert "[CODE_BLOCK_2]" in numbered
    assert numbered.index("[CODE_BLOCK_1]") < numbered.index("[CODE_BLOCK_2]")


def test_oversized_marker_less_input_is_chunked():
    # A single message with no role markers, far over the char budget,
    # must still be split into multiple chunks.
    big = "x" * (CHUNK_CHAR_LIMIT * 3 + 100)
    chunks = parse_chat(big)
    assert len(chunks) >= 3
    # Every chunk should respect the budget (allowing role-prefix overhead).
    for c in chunks:
        assert len(c.raw_text) <= CHUNK_CHAR_LIMIT + 100


def test_small_input_is_single_chunk():
    chunks = parse_chat("User: quick question\nAssistant: quick answer")
    assert len(chunks) == 1


def test_empty_chat_handled():
    # Whitespace-only / empty input should not raise.
    assert isinstance(parse_chat(""), list)
