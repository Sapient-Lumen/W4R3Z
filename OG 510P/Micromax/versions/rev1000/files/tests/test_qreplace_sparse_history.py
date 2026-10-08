from __future__ import annotations

import random

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.simultaneous_edits import SimultaneousEditWitness
from micromax_editor.textpos import index_to_cursor


def test_answers_do_not_materialize_live_document_after_planning(monkeypatch) -> None:
    source = "head needle\n" + ("middle line\n" * 2000) + "needle tail needle"
    ed = Editor()
    ed.new_buffer("large-qreplace", source)
    eb = ed.cur()
    # Isolate the delayed-interaction hot path from exact dirty hashing, which
    # intentionally materializes small buffers after any mutation. Large files
    # use this sticky mode automatically.
    eb.buf.fastdirty = True

    assert ed.begin_query_replace("needle", "X\nY", literal=True) is True
    original_get_text = eb.buf.get_text
    live_materializations = 0

    def unexpected_get_text() -> str:
        nonlocal live_materializations
        live_materializations += 1
        raise AssertionError("qreplace answer materialized the complete live buffer")

    monkeypatch.setattr(eb.buf, "get_text", unexpected_get_text)
    assert ed.qreplace_all() is True

    assert live_materializations == 0
    assert ed.qreplace is None
    assert original_get_text() == source.replace("needle", "X\nY")


def test_finished_qreplace_history_retains_only_changed_slices() -> None:
    block = ("a" * 120 + "\n") * 3000
    source = f"{block}needle\n{block}needle\n{block}needle\n"
    ed = Editor()
    ed.new_buffer("large-qreplace", source)
    eb = ed.cur()

    assert ed.begin_query_replace("needle", "X", literal=True) is True
    assert ed.qreplace_all() is True

    expected = source.replace("needle", "X")
    assert eb.buf.get_text() == expected
    assert ed.qreplace is None
    assert ed.undo.depth() == 1

    edit = ed.undo.snapshot().undo[-1]
    closure = dict(
        zip(
            edit.undo.__code__.co_freevars,
            (cell.cell_contents for cell in (edit.undo.__closure__ or ())),
            strict=True,
        )
    )
    witness = closure.get("witness")
    assert isinstance(witness, SimultaneousEditWitness)
    assert witness.retained_texts() == ("needle", "X") * 3
    assert "source_text" not in closure
    retained = ed.undo.retained_text_bytes(eb)
    unique_texts = {id(text): text for text in witness.retained_texts()}
    assert retained == sum(len(text) for text in unique_texts.values())
    assert retained <= 3 * (len("needle") + len("X"))
    assert retained < len(source) // 10_000

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == source
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == expected


def test_sparse_qreplace_undo_preserves_unrelated_equal_length_text() -> None:
    ed = Editor()
    ed.new_buffer("qreplace", "one gap one tail one")
    eb = ed.cur()

    assert ed.begin_query_replace("one", "X", literal=True) is True
    assert ed.qreplace_all() is True
    assert eb.buf.get_text() == "X gap X tail X"

    # Simulate another owner changing an unrelated same-width gap without
    # entering Micromax's undo boundary. Sparse replay should preserve it.
    eb.buf.replace_range(Cursor(0, 2), Cursor(0, 5), "GAP")
    assert eb.buf.get_text() == "X GAP X tail X"

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "one GAP one tail one"
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "X GAP X tail X"


def test_sparse_qreplace_undo_validates_every_slice_before_mutating() -> None:
    ed = Editor()
    ed.new_buffer("qreplace", "one gap one")
    eb = ed.cur()

    assert ed.begin_query_replace("one", "X", literal=True) is True
    assert ed.qreplace_all() is True
    assert eb.buf.get_text() == "X gap X"

    # Corrupt only the later addressed slice. The inverse must validate the
    # complete sparse row before changing the earlier, still-valid slice.
    eb.buf.replace_range(Cursor(0, 6), Cursor(0, 7), "Z")
    assert ed.undo_feedback() is False
    assert eb.buf.get_text() == "X gap Z"
    assert ed.undo.depth() == 1
    assert "undo: refused stale edit" in ed.messages[-1]


@pytest.mark.parametrize(
    ("source", "replacement", "accept"),
    [
        ("NN\nxN\nN", "", (True, True, False, True)),
        ("N a\nb N c N", "X\nY", (True, False, True)),
        ("N\nN\nN", "N", (True, True, True)),
        ("αNβ N\nNγ", "LONG", (False, True, True)),
    ],
)
def test_sparse_qreplace_roundtrips_multiline_skip_and_adjacent_geometry(
    source: str,
    replacement: str,
    accept: tuple[bool, ...],
) -> None:
    positions: list[int] = []
    at = 0
    while True:
        found = source.find("N", at)
        if found < 0:
            break
        positions.append(found)
        at = found + 1
    assert len(positions) == len(accept)

    parts: list[str] = []
    source_at = 0
    for index, position in enumerate(positions):
        parts.append(source[source_at:position])
        parts.append(replacement if accept[index] else "N")
        source_at = position + 1
    parts.append(source[source_at:])
    expected = "".join(parts)

    ed = Editor()
    ed.new_buffer("qreplace", source)
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 0), eb.buf.clamp(Cursor(999, 999))]
    eb.sel_anchors[:] = [None, Cursor(0, 0)]
    eb.cursor_ids[:] = [11, 22]
    eb.primary = 0
    ed._normalize_cursor_lists(eb)
    before = ed._snapshot_buffer_state(eb)

    assert ed.begin_query_replace("N", replacement, literal=True) is True
    for decision in accept:
        if decision:
            assert ed.qreplace_yes() is True
        else:
            assert ed.qreplace_no() is True

    assert ed.qreplace is None
    assert eb.buf.get_text() == expected
    after = ed._snapshot_buffer_state(eb)
    if any(accept):
        assert ed.undo.depth() == 1
        assert ed.undo_feedback() is True
        assert ed._snapshot_buffer_state(eb) == before
        assert ed.redo_feedback() is True
        assert ed._snapshot_buffer_state(eb) == after
    else:
        assert ed.undo.depth() == 0


def test_sparse_qreplace_long_mixed_session_keeps_monotonic_geometry() -> None:
    fragments: list[str] = []
    decisions: list[bool] = []
    for index in range(257):
        if index % 5 == 0:
            fragments.append(f"row-{index}\nα")
        elif index % 7 == 0:
            fragments.append("wide-ββ-")
        else:
            fragments.append(f"g{index}-")
        fragments.append("N")
        decisions.append(index % 3 != 1 and index % 11 != 0)
    fragments.append("-tail\n")
    source = "".join(fragments)
    replacement = "X\nYZ"

    expected_parts: list[str] = []
    source_at = 0
    match_index = 0
    while True:
        found = source.find("N", source_at)
        if found < 0:
            expected_parts.append(source[source_at:])
            break
        expected_parts.append(source[source_at:found])
        expected_parts.append(replacement if decisions[match_index] else "N")
        source_at = found + 1
        match_index += 1
    expected = "".join(expected_parts)

    ed = Editor()
    ed.new_buffer("long-qreplace", source)
    eb = ed.cur()
    eb.buf.fastdirty = True
    eb.cursors[:] = [Cursor(0, 0), eb.buf.clamp(Cursor(99999, 99999))]
    eb.sel_anchors[:] = [None, Cursor(0, 0)]
    eb.cursor_ids[:] = [31, 47]
    eb.primary = 0
    ed._normalize_cursor_lists(eb)
    before = ed._snapshot_buffer_state(eb)

    assert ed.begin_query_replace("N", replacement, literal=True) is True
    for decision in decisions:
        assert (ed.qreplace_yes() if decision else ed.qreplace_no()) is True

    assert ed.qreplace is None
    assert eb.buf.get_text() == expected
    after = ed._snapshot_buffer_state(eb)
    edit = ed.undo.snapshot().undo[-1]
    closure = dict(
        zip(
            edit.undo.__code__.co_freevars,
            (cell.cell_contents for cell in (edit.undo.__closure__ or ())),
            strict=True,
        )
    )
    witness = closure.get("witness")
    assert isinstance(witness, SimultaneousEditWitness)
    assert len(witness.splices) == sum(decisions)
    assert all(
        left.old_end <= right.old_start and left.new_end <= right.new_start
        for left, right in zip(witness.splices, witness.splices[1:])
    )

    assert ed.undo_feedback() is True
    assert ed._snapshot_buffer_state(eb) == before
    assert ed.redo_feedback() is True
    assert ed._snapshot_buffer_state(eb) == after


def test_sparse_qreplace_random_nonzero_origins_match_source_coordinates() -> None:
    rng = random.Random(989)
    replacements = ("", "X", "X\nY", "αβ")
    alphabet = "ab αβ\n"

    for case in range(160):
        fragments: list[str] = []
        match_count = rng.randrange(1, 18)
        for _match in range(match_count):
            fragments.append(
                "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 12)))
            )
            fragments.append("N")
        fragments.append(
            "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 12)))
        )
        source = "".join(fragments)
        all_positions = [
            index for index, character in enumerate(source) if character == "N"
        ]
        start = rng.randrange(0, all_positions[-1] + 1)
        positions = [position for position in all_positions if position >= start]
        decisions = [bool(rng.randrange(0, 2)) for _ in positions]
        replacement = rng.choice(replacements)

        expected_parts = [source[:start]]
        source_at = start
        for position, decision in zip(positions, decisions, strict=True):
            expected_parts.append(source[source_at:position])
            expected_parts.append(replacement if decision else "N")
            source_at = position + 1
        expected_parts.append(source[source_at:])
        expected = "".join(expected_parts)

        ed = Editor()
        ed.new_buffer(f"random-qreplace-{case}", source)
        eb = ed.cur()
        eb.cursors[:] = [
            index_to_cursor(eb.buf, start),
            index_to_cursor(eb.buf, rng.randrange(0, len(source) + 1)),
        ]
        eb.sel_anchors[:] = [
            None,
            index_to_cursor(eb.buf, rng.randrange(0, len(source) + 1)),
        ]
        eb.cursor_ids[:] = [101, 202]
        eb.primary = 0
        ed._normalize_cursor_lists(eb)
        before = ed._snapshot_buffer_state(eb)

        assert ed.begin_query_replace("N", replacement, literal=True) is True
        for decision in decisions:
            assert (ed.qreplace_yes() if decision else ed.qreplace_no()) is True

        assert ed.qreplace is None
        assert eb.buf.get_text() == expected
        if any(decisions):
            after = ed._snapshot_buffer_state(eb)
            assert ed.undo.depth() == 1
            assert ed.undo_feedback() is True
            assert ed._snapshot_buffer_state(eb) == before
            assert ed.redo_feedback() is True
            assert ed._snapshot_buffer_state(eb) == after
        else:
            assert ed.undo.depth() == 0
