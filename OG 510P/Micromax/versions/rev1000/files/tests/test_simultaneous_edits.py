from __future__ import annotations

import random

import pytest

from micromax import MicromaxError
from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.simultaneous_edits import (
    SimultaneousEditError,
    SimultaneousTextEdit,
    line_start_offsets,
    map_cursor_through_replacement,
    offset_to_cursor,
    plan_simultaneous_edits,
)


def _set_cursors(
    ed: Editor,
    cursors: list[Cursor],
    anchors: list[Cursor | None],
    *,
    primary: int = 0,
) -> None:
    eb = ed.cur()
    eb.cursors[:] = cursors
    eb.sel_anchors[:] = anchors
    eb.cursor_ids[:] = list(range(1, len(cursors) + 1))
    eb.primary = int(primary)
    ed._normalize_cursor_lists(eb)


def _cursor_rows(ed: Editor) -> list[tuple[int, int]]:
    return [(int(cursor.line), int(cursor.col)) for cursor in ed.cur().cursors]


def _anchor_rows(ed: Editor) -> list[tuple[int, int] | None]:
    return [
        (int(anchor.line), int(anchor.col)) if anchor is not None else None
        for anchor in ed.cur().sel_anchors
    ]


def test_multiline_plan_uses_one_original_coordinate_space() -> None:
    source = "alpha\nbeta\ngamma"
    plan = plan_simultaneous_edits(
        source,
        [
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 5), "X", owner=0),
            SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 4), "YY", owner=1),
            SimultaneousTextEdit(Cursor(2, 5), Cursor(2, 5), "!", owner=2),
        ],
    )

    assert plan.new_text == "aX\nYY\ngamma!"
    starts = line_start_offsets(plan.new_text)
    assert offset_to_cursor(plan.new_text, starts, plan.owner_offset(0) or 0) == Cursor(0, 2)
    assert offset_to_cursor(plan.new_text, starts, plan.owner_offset(1) or 0) == Cursor(1, 2)
    assert offset_to_cursor(plan.new_text, starts, plan.owner_offset(2) or 0) == Cursor(2, 6)


def test_local_single_replacement_cursor_mapping_matches_full_planner() -> None:
    rng = random.Random(989)
    for _case in range(1000):
        source = "".join(rng.choice("ab \n") for _ in range(rng.randrange(0, 40)))
        source_starts = line_start_offsets(source)
        start_offset = rng.randrange(0, len(source) + 1)
        end_offset = rng.randrange(start_offset, len(source) + 1)
        replacement = "".join(
            rng.choice("XY\n") for _ in range(rng.randrange(0, 8))
        )
        start = offset_to_cursor(source, source_starts, start_offset)
        old_end = offset_to_cursor(source, source_starts, end_offset)
        plan = plan_simultaneous_edits(
            source,
            [SimultaneousTextEdit(start, old_end, replacement, owner=0)],
            source_starts=source_starts,
        )
        new_starts = line_start_offsets(plan.new_text)
        owner_offset = plan.owner_offset(0)
        assert owner_offset is not None
        new_end = offset_to_cursor(plan.new_text, new_starts, owner_offset)

        for affinity in ("left", "right"):
            for point_offset in {
                0,
                len(source),
                start_offset,
                end_offset,
                rng.randrange(0, len(source) + 1),
            }:
                point = offset_to_cursor(source, source_starts, point_offset)
                expected_offset = plan.map_offset(point_offset, affinity=affinity)
                expected = offset_to_cursor(
                    plan.new_text,
                    new_starts,
                    expected_offset,
                )
                assert map_cursor_through_replacement(
                    point,
                    start=start,
                    old_end=old_end,
                    new_end=new_end,
                    affinity=affinity,
                ) == expected


def test_exact_duplicate_edits_coalesce_for_multiple_cursor_owners() -> None:
    plan = plan_simultaneous_edits(
        "foo",
        [
            SimultaneousTextEdit(Cursor(0, 0), Cursor(0, 3), "x", owner=0),
            SimultaneousTextEdit(Cursor(0, 0), Cursor(0, 3), "x", owner=1),
        ],
    )

    assert plan.new_text == "x"
    assert plan.edit_count == 1
    assert plan.owner_offsets == ((0, 1), (1, 1))


@pytest.mark.parametrize(
    "edits",
    [
        [
            SimultaneousTextEdit(Cursor(0, 0), Cursor(0, 3), "A", owner=0),
            SimultaneousTextEdit(Cursor(0, 2), Cursor(0, 5), "B", owner=1),
        ],
        [
            SimultaneousTextEdit(Cursor(0, 2), Cursor(0, 2), "A", owner=0),
            SimultaneousTextEdit(Cursor(0, 2), Cursor(0, 2), "B", owner=1),
        ],
        [
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 4), "A", owner=0),
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 3), "A", owner=1),
        ],
    ],
)
def test_ambiguous_overlap_or_same_start_fails_closed(
    edits: list[SimultaneousTextEdit],
) -> None:
    with pytest.raises(SimultaneousEditError):
        plan_simultaneous_edits("abcdef", edits)


def test_adjacent_edits_and_right_affinity_have_explicit_boundaries() -> None:
    plan = plan_simultaneous_edits(
        "abcdef",
        [
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 3), "X", owner=0),
            SimultaneousTextEdit(Cursor(0, 3), Cursor(0, 5), "YY", owner=1),
            SimultaneousTextEdit(Cursor(0, 6), Cursor(0, 6), "!", owner=2),
        ],
    )

    assert plan.new_text == "aXYYf!"
    # A cursor at a replacement start/inside lands at that replacement's end;
    # a cursor at its original end sees the completed edit delta.
    assert plan.map_offset(1) == 2
    assert plan.map_offset(2) == 2
    assert plan.map_offset(3) == 4
    assert plan.map_offset(5) == 4
    assert plan.map_offset(6) == 6


def test_multicursor_insert_has_one_buffer_mutation_witness() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcd")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 0), Cursor(0, 2), Cursor(0, 4)]
    eb.sel_anchors[:] = [None, None, None]
    eb.cursor_ids[:] = [1, 2, 3]
    eb.primary = 0
    version_before = int(eb.buf.version)

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True

    assert eb.buf.get_text() == "XabXcdX"
    assert int(eb.buf.version) == version_before + 1
    assert eb.cursors == [Cursor(0, 1), Cursor(0, 4), Cursor(0, 7)]


def _install_overlapping_selections(ed: Editor) -> None:
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 3), Cursor(0, 5)]
    eb.sel_anchors[:] = [Cursor(0, 0), Cursor(0, 2)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0


def test_action_overlap_rejection_is_atomic_and_not_undoable() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdef")
    _install_overlapping_selections(ed)
    before = ed._snapshot_buffer_state(ed.cur())
    undo_depth = ed.undo.depth()
    ed.input["text"] = "X"

    assert ed.run_action("InsertText") is False

    assert ed._snapshot_buffer_state(ed.cur()) == before
    assert ed.undo.depth() == undo_depth
    assert "overlapping edit ranges" in ed.messages[-1]


def test_hostcall_overlap_rejection_preserves_argument_and_editor_state() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdef")
    install_editor_hostcalls(ed)
    _install_overlapping_selections(ed)
    before = ed._snapshot_buffer_state(ed.cur())
    ed.vm.stack.append(["X", "Y"])
    ed.vm.stack.append("ed.replace-selections")

    with pytest.raises(MicromaxError, match="overlapping edit ranges"):
        ed.vm.eval("hostcall")

    assert ed.vm.stack == [["X", "Y"]]
    assert ed._snapshot_buffer_state(ed.cur()) == before
    assert ed.undo.depth() == 0


def test_planner_matches_reference_application_for_seeded_edit_sets() -> None:
    rng = random.Random(968)
    for _case in range(500):
        source = "".join(rng.choice("ab \n") for _ in range(rng.randrange(0, 25)))
        starts = line_start_offsets(source)
        flat_edits: list[tuple[int, int, str]] = []
        cursor = 0
        while cursor <= len(source) and len(flat_edits) < 6:
            cursor += rng.randrange(0, 4)
            if cursor > len(source):
                break
            end = min(len(source), cursor + rng.randrange(0, 4))
            replacement = "".join(rng.choice("XY\n") for _ in range(rng.randrange(0, 4)))
            flat_edits.append((cursor, end, replacement))
            cursor = max(cursor + 1, end)

        requests = [
            SimultaneousTextEdit(
                offset_to_cursor(source, starts, start),
                offset_to_cursor(source, starts, end),
                replacement,
                owner=index,
            )
            for index, (start, end, replacement) in enumerate(flat_edits)
        ]
        plan = plan_simultaneous_edits(source, requests)
        reference = source
        for start, end, replacement in reversed(flat_edits):
            reference = reference[:start] + replacement + reference[end:]
        assert plan.new_text == reference


def test_indent_and_unindent_use_per_line_transaction_geometry() -> None:
    ed = Editor()
    ed.new_buffer("indent", "    alpha\n  beta")
    _set_cursors(
        ed,
        [Cursor(0, 9), Cursor(1, 6)],
        [Cursor(0, 4), Cursor(1, 2)],
    )
    before_version = ed.cur().buf.version

    assert ed.run_action("UnindentSelection") is True
    assert ed.cur().buf.get_text() == "alpha\nbeta"
    assert _cursor_rows(ed) == [(0, 5), (1, 4)]
    assert _anchor_rows(ed) == [(0, 0), (1, 0)]
    assert ed.cur().buf.version == before_version + 1

    assert ed.run_action("IndentSelection") is True
    assert ed.cur().buf.get_text() == "    alpha\n    beta"
    assert _cursor_rows(ed) == [(0, 9), (1, 8)]
    assert _anchor_rows(ed) == [(0, 4), (1, 4)]
    assert ed.cur().buf.version == before_version + 2

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "alpha\nbeta"
    assert _cursor_rows(ed) == [(0, 5), (1, 4)]
    assert _anchor_rows(ed) == [(0, 0), (1, 0)]

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "    alpha\n  beta"
    assert _cursor_rows(ed) == [(0, 9), (1, 6)]
    assert _anchor_rows(ed) == [(0, 4), (1, 2)]



def test_buffer_text_boundary_normalizes_only_crlf_and_cr() -> None:
    separator = "\u2028"
    buf = Buffer(f"a\r\nb\rc{separator}d\r\n")

    assert buf.lines == ["a", "b", f"c{separator}d", ""]
    assert buf.get_text() == f"a\nb\nc{separator}d\n"

    cursor = buf.insert(Cursor(1, 1), "X\r\nY\rZ")
    assert cursor == Cursor(3, 1)
    assert buf.get_text() == f"a\nbX\nY\nZ\nc{separator}d\n"

    cursor = buf.replace_range(Cursor(0, 0), Cursor(0, 1), "Q\r\nR")
    assert cursor == Cursor(1, 1)
    assert buf.get_text() == f"Q\nR\nbX\nY\nZ\nc{separator}d\n"


def test_planner_discards_pre_normalization_line_index() -> None:
    raw = "a\r\nb"
    stale_starts = line_start_offsets(raw)
    plan = plan_simultaneous_edits(
        raw,
        [SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 1), "B", owner=0)],
        source_starts=stale_starts,
    )

    assert plan.original_text == "a\nb"
    assert plan.new_text == "a\nB"
    assert plan.owner_offset(0) == 3


def test_selected_and_unselected_cursors_share_one_source_snapshot() -> None:
    ed = Editor()
    ed.new_buffer("mixed", "foo middle end")
    _set_cursors(
        ed,
        [Cursor(0, 3), Cursor(0, 11)],
        [Cursor(0, 0), None],
    )
    before_version = int(ed.cur().buf.version)

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True

    assert ed.cur().buf.get_text() == "X middle Xend"
    assert _cursor_rows(ed) == [(0, 1), (0, 10)]
    assert _anchor_rows(ed) == [None, None]
    assert int(ed.cur().buf.version) == before_version + 1


def test_replace_range_hostcall_remaps_secondary_selection(monkeypatch) -> None:
    import micromax_editor.editor as editor_module

    ed = Editor()
    ed.new_buffer("range", "one two three")
    install_editor_hostcalls(ed)
    _set_cursors(
        ed,
        [Cursor(0, 0), Cursor(0, 13)],
        [None, Cursor(0, 8)],
    )
    ed.vm.stack.extend([0, 0, 0, 3, "ONE-LONG", "ed.replace-range"])

    def unexpected_planner(*_args, **_kwargs):
        raise AssertionError("one-range multi-cursor edit entered full planner")

    monkeypatch.setattr(
        editor_module,
        "plan_simultaneous_edits_lines",
        unexpected_planner,
    )
    ed.vm.eval("hostcall")

    col = ed.vm.pop_int()
    line = ed.vm.pop_int()
    assert (line, col) == (0, 8)
    assert ed.cur().buf.get_text() == "ONE-LONG two three"
    assert _cursor_rows(ed) == [(0, 8), (0, 18)]
    assert _anchor_rows(ed) == [None, (0, 13)]

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "one two three"
    assert _cursor_rows(ed) == [(0, 0), (0, 13)]
    assert _anchor_rows(ed) == [None, (0, 8)]
    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "ONE-LONG two three"
    assert _cursor_rows(ed) == [(0, 8), (0, 18)]
    assert _anchor_rows(ed) == [None, (0, 13)]


def test_query_replace_remaps_secondary_selection_from_original_snapshot() -> None:
    ed = Editor()
    ed.new_buffer("qreplace", "one two three")
    _set_cursors(
        ed,
        [Cursor(0, 0), Cursor(0, 13)],
        [None, Cursor(0, 8)],
    )

    assert ed.begin_query_replace("one", "ONE-LONG", literal=True) is True
    assert ed.qreplace_yes() is True

    assert ed.cur().buf.get_text() == "ONE-LONG two three"
    assert _cursor_rows(ed) == [(0, 8), (0, 18)]
    assert _anchor_rows(ed) == [None, (0, 13)]


def test_line_start_offsets_are_compact_and_preserve_trailing_empty_line() -> None:
    from array import array

    starts = line_start_offsets("a\nb\n")

    assert isinstance(starts, array)
    assert starts.typecode == "Q"
    assert list(starts) == [0, 2, 4]
    assert starts.itemsize * len(starts) == 24


def test_planner_consumes_caller_line_index_without_full_reboxing() -> None:
    class IndexOnlyOffsets:
        def __init__(self, values: list[int]) -> None:
            self.values = values

        def __len__(self) -> int:
            return len(self.values)

        def __getitem__(self, index: int) -> int:
            return self.values[index]

        def __iter__(self):
            raise AssertionError("planner reboxed the complete source index")

    starts = IndexOnlyOffsets([0, 2, 4])
    plan = plan_simultaneous_edits(
        "a\nb\n",
        [SimultaneousTextEdit(Cursor(1, 0), Cursor(1, 1), "B", owner=1)],
        source_starts=starts,
    )

    assert plan.new_text == "a\nB\n"
    assert plan.owner_offset(1) == 3
