from __future__ import annotations

import random

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.query_replace import (
    QueryReplaceBufferWitness,
    advance_cursor_by_text,
    advance_cursor_through_text_span,
)


def test_bounded_cursor_advance_matches_slice_reference() -> None:
    rng = random.Random(989)
    for _case in range(1000):
        text = "".join(rng.choice("ab α\n") for _ in range(rng.randrange(0, 120)))
        left = rng.randrange(0, len(text) + 1)
        right = rng.randrange(left, len(text) + 1)
        origin = Cursor(rng.randrange(0, 20), rng.randrange(0, 40))

        assert advance_cursor_through_text_span(
            origin,
            text,
            left,
            right,
        ) == advance_cursor_by_text(origin, text[left:right])


def test_bounded_cursor_advance_clamps_span_without_gap_copy() -> None:
    assert advance_cursor_through_text_span(
        Cursor(3, 4),
        "zero\none\ntwo",
        -20,
        10_000,
    ) == Cursor(5, 3)


def test_query_replace_witness_tracks_identity_and_exact_buffer_version() -> None:
    ed = Editor()
    ed.new_buffer("main", "one")
    target = ed.cur()

    witness = QueryReplaceBufferWitness.capture(target.name, target)
    assert witness.resolve() is target
    assert witness.version == target.buf.version
    assert witness.is_current(target) is True

    target.buf.insert(Cursor(0, 0), "x")
    assert witness.is_current(target) is False

    refreshed = witness.refresh(target.name, target)
    assert refreshed.resolve() is target
    assert refreshed.version == target.buf.version
    assert refreshed.is_current(target) is True


def test_query_replace_witness_rejects_same_name_different_identity() -> None:
    ed = Editor()
    ed.new_buffer("main", "one")
    original = ed.cur()
    witness = QueryReplaceBufferWitness.capture(original.name, original)

    ed.new_buffer("other", "safe")
    ed.close_buffers(["main"], keep="other")
    replacement = ed.new_buffer("main", "fresh")

    assert replacement is not original
    assert witness.is_current(replacement) is False


class _MutableVersionBuffer:
    def __init__(self, version: int) -> None:
        self.version = version


class _MutableVersionEditorBuffer:
    def __init__(self, version: int) -> None:
        self.buf = _MutableVersionBuffer(version)


def test_versioned_witness_fails_closed_if_counter_becomes_unreadable() -> None:
    target = _MutableVersionEditorBuffer(7)
    witness = QueryReplaceBufferWitness.capture("main", target)
    assert witness.version == 7

    del target.buf.version

    assert witness.is_current(target) is False
