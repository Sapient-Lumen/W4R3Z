from __future__ import annotations

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.line_edits import (
    DeleteLinesPlan,
    DuplicateLineBlockPlan,
    MoveLineBlockPlan,
)


def _editor(text: str) -> tuple[Editor, object]:
    ed = Editor()
    ed.new_buffer("*lines*", text)
    return ed, ed.cur()


def _set_cursor_state(
    eb: object,
    *,
    cursors: list[Cursor],
    anchors: list[Cursor | None],
    primary: int = 0,
) -> None:
    eb.cursors[:] = cursors
    eb.sel_anchors[:] = anchors
    eb.cursor_ids[:] = list(range(1, len(cursors) + 1))
    eb.primary = primary


def _state(eb: object) -> tuple[str, list[Cursor], list[Cursor | None], list[int], int]:
    return (
        eb.buf.get_text(),
        list(eb.cursors),
        list(eb.sel_anchors),
        list(eb.cursor_ids),
        int(eb.primary),
    )


def test_move_lines_down_preserves_forward_whole_line_selection_and_undo_redo() -> None:
    ed, eb = _editor("A\nB\nC\nD\nE")
    _set_cursor_state(
        eb,
        cursors=[Cursor(3, 0)],
        anchors=[Cursor(1, 0)],
    )
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.selection_text() == "B\nC\n"
    assert ed.run_action("MoveLinesDown") is True
    assert eb.buf.get_text() == "A\nD\nB\nC\nE"
    assert eb.cursors == [Cursor(4, 0)]
    assert eb.sel_anchors == [Cursor(2, 0)]
    assert ed.selection_text() == "B\nC\n"
    assert eb.buf.version == before_version + 1

    moved = _state(eb)
    assert ed.run_action("Undo") is True
    assert _state(eb) == before
    assert ed.run_action("Redo") is True
    assert _state(eb) == moved
    assert ed.selection_text() == "B\nC\n"


def test_move_lines_up_preserves_reverse_whole_line_selection_and_undo_redo() -> None:
    ed, eb = _editor("A\nB\nC\nD\nE")
    _set_cursor_state(
        eb,
        cursors=[Cursor(1, 0)],
        anchors=[Cursor(3, 0)],
    )
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.selection_text() == "B\nC\n"
    assert ed.run_action("MoveLinesUp") is True
    assert eb.buf.get_text() == "B\nC\nA\nD\nE"
    assert eb.cursors == [Cursor(0, 0)]
    assert eb.sel_anchors == [Cursor(2, 0)]
    assert ed.selection_text() == "B\nC\n"
    assert eb.buf.version == before_version + 1

    moved = _state(eb)
    assert ed.run_action("Undo") is True
    assert _state(eb) == before
    assert ed.run_action("Redo") is True
    assert _state(eb) == moved
    assert ed.selection_text() == "B\nC\n"


def test_move_lines_projects_unselected_cursors_with_the_same_line_permutation() -> None:
    ed, eb = _editor("A0\nB1\nC2\nD3\nE4")
    _set_cursor_state(
        eb,
        cursors=[Cursor(0, 1), Cursor(2, 1), Cursor(3, 1), Cursor(4, 1)],
        anchors=[None, Cursor(1, 0), None, None],
        primary=1,
    )

    assert ed.run_action("MoveLinesDown") is True
    assert eb.buf.get_text() == "A0\nD3\nB1\nC2\nE4"
    # A0 and E4 stay put; selected B1/C2 follow the block; D3 follows its
    # displaced source line to the block's old start.
    assert eb.cursors == [
        Cursor(0, 1),
        Cursor(1, 1),
        Cursor(3, 1),
        Cursor(4, 1),
    ]
    assert eb.sel_anchors == [None, None, Cursor(2, 0), None]
    assert eb.primary == 2
    assert ed.selection_text(2) == "B1\nC"


def test_duplicate_line_keeps_columns_and_secondary_cursor_source_identity() -> None:
    ed, eb = _editor("zero\none\ntwo\nthree")
    _set_cursor_state(
        eb,
        cursors=[Cursor(0, 2), Cursor(2, 1)],
        anchors=[None, None],
        primary=0,
    )
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.run_action("DuplicateLine") is True
    assert eb.buf.get_text() == "zero\nzero\none\ntwo\nthree"
    assert eb.cursors == [Cursor(1, 2), Cursor(3, 1)]
    assert eb.sel_anchors == [None, None]
    assert eb.primary == 0
    assert eb.buf.version == before_version + 1

    duplicated = _state(eb)
    assert ed.run_action("Undo") is True
    assert _state(eb) == before
    assert ed.run_action("Redo") is True
    assert _state(eb) == duplicated


def test_duplicate_line_clears_zero_width_primary_anchor() -> None:
    ed, eb = _editor("abc\ndef")
    _set_cursor_state(
        eb,
        cursors=[Cursor(0, 2)],
        anchors=[Cursor(0, 2)],
    )

    assert ed.run_action("DuplicateLine") is True
    assert eb.buf.get_text() == "abc\nabc\ndef"
    assert eb.cursors == [Cursor(1, 2)]
    assert eb.sel_anchors == [None]
    assert ed.has_selection() is False


def test_duplicate_line_preserves_directed_whole_line_selection_on_original() -> None:
    ed, eb = _editor("A\nB\nC\nD")
    _set_cursor_state(
        eb,
        cursors=[Cursor(1, 0)],
        anchors=[Cursor(3, 0)],
    )
    before_version = eb.buf.version

    assert ed.selection_text() == "B\nC\n"
    assert ed.run_action("DuplicateLine") is True
    assert eb.buf.get_text() == "A\nB\nC\nB\nC\nD"
    # Micro-compatible selection duplication keeps the original block selected;
    # the half-open boundary must not be mistaken for the following source line.
    assert eb.cursors == [Cursor(1, 0)]
    assert eb.sel_anchors == [Cursor(3, 0)]
    assert ed.selection_text() == "B\nC\n"
    assert eb.buf.version == before_version + 1


def test_cut_line_uses_one_mutation_for_multiple_cursor_lines() -> None:
    ed, eb = _editor("A0\nB1\nC2\nD3")
    _set_cursor_state(
        eb,
        cursors=[Cursor(0, 1), Cursor(2, 1)],
        anchors=[None, None],
        primary=1,
    )
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.run_action("CutLine") is True
    assert eb.buf.get_text() == "B1\nD3"
    assert ed.clipboard_text() == "A0\nC2\n"
    assert eb.cursors == [Cursor(0, 0), Cursor(1, 0)]
    assert eb.primary == 1
    assert eb.buf.version == before_version + 1

    cut = _state(eb)
    assert ed.run_action("Undo") is True
    assert _state(eb) == before
    assert ed.run_action("Redo") is True
    assert _state(eb) == cut


def test_cut_line_selection_uses_fully_or_partially_selected_source_rows() -> None:
    ed, eb = _editor("A0\nB1\nC2\nD3\nE4")
    _set_cursor_state(
        eb,
        cursors=[Cursor(3, 1)],
        anchors=[Cursor(1, 1)],
    )
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.run_action("CutLine") is True
    assert eb.buf.get_text() == "A0\nE4"
    assert ed.clipboard_text() == "B1\nC2\nD3\n"
    assert eb.cursors == [Cursor(1, 0)]
    assert eb.sel_anchors == [None]
    assert eb.buf.version == before_version + 1

    cut = _state(eb)
    assert ed.run_action("Undo") is True
    assert _state(eb) == before
    assert ed.run_action("Redo") is True
    assert _state(eb) == cut


def test_cut_line_whole_line_boundary_does_not_consume_adjacent_source_line() -> None:
    for cursor, anchor in (
        (Cursor(3, 0), Cursor(1, 0)),
        (Cursor(1, 0), Cursor(3, 0)),
    ):
        ed, eb = _editor("A\nB\nC\nD\nE")
        _set_cursor_state(eb, cursors=[cursor], anchors=[anchor])

        assert ed.selection_text() == "B\nC\n"
        assert ed.run_action("CutLine") is True
        assert eb.buf.get_text() == "A\nD\nE"
        assert ed.clipboard_text() == "B\nC\n"
        assert eb.cursors == [Cursor(1, 0)]
        assert eb.sel_anchors == [None]


def test_cut_line_unions_selected_rows_and_unselected_cursor_rows() -> None:
    ed, eb = _editor("a\nb\nc\nd\ne\nf")
    _set_cursor_state(
        eb,
        cursors=[Cursor(3, 0), Cursor(5, 0)],
        anchors=[Cursor(1, 1), None],
        primary=0,
    )
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.selection_text(0) == "\nc\n"
    assert ed.run_action("CutLine") is True
    assert eb.buf.get_text() == "a\nd\ne"
    assert ed.clipboard_items == ["b", "c", "f"]
    assert ed.clipboard_text() == "b\nc\nf\n"
    assert eb.cursors == [Cursor(1, 0), Cursor(2, 0)]
    assert eb.sel_anchors == [None, None]
    assert eb.buf.version == before_version + 1

    cut = _state(eb)
    assert ed.run_action("Undo") is True
    assert _state(eb) == before
    assert ed.run_action("Redo") is True
    assert _state(eb) == cut


def test_move_at_document_edge_is_a_true_noop() -> None:
    ed, eb = _editor("A\nB")
    _set_cursor_state(eb, cursors=[Cursor(0, 1)], anchors=[None])
    before = _state(eb)
    before_version = eb.buf.version

    assert ed.run_action("MoveLinesUp") is False
    assert _state(eb) == before
    assert eb.buf.version == before_version
    assert ed.run_action("Undo") is False


def test_move_plan_is_a_text_identity_bijection_for_every_valid_span() -> None:
    source = tuple(f"line-{index}" for index in range(6))
    for direction in (-1, 1):
        for start in range(len(source)):
            for end in range(start, len(source)):
                if direction < 0 and start == 0:
                    continue
                if direction > 0 and end == len(source) - 1:
                    continue
                plan = MoveLineBlockPlan.build(
                    source,
                    start=start,
                    end=end,
                    direction=direction,
                )
                assert sorted(plan.old_to_new) == list(range(len(source)))
                for old_line, new_line in enumerate(plan.old_to_new):
                    assert plan.lines[new_line] == source[old_line]
                    assert plan.project(Cursor(old_line, 3)) == Cursor(new_line, 3)
                assert plan.project(
                    plan.source_trailing_boundary,
                    trailing_boundary=True,
                ) == plan.target_trailing_boundary


def test_duplicate_plan_distinguishes_source_text_from_half_open_boundary() -> None:
    source = ("A", "B", "C", "D", "E")
    plan = DuplicateLineBlockPlan.build(source, start=1, end=2)

    assert plan.lines == ("A", "B", "C", "B", "C", "D", "E")
    assert plan.project_duplicate(Cursor(1, 1)) == Cursor(3, 1)
    assert plan.project_duplicate(Cursor(2, 1)) == Cursor(4, 1)
    # The same raw coordinate can mean either the original block's trailing
    # boundary or the first character of source line D.
    assert plan.project_original(Cursor(3, 0), keep_boundary=True) == Cursor(3, 0)
    assert plan.project_original(Cursor(3, 0)) == Cursor(5, 0)


def test_delete_plan_preserves_surviving_source_identity_and_lands_deleted_rows() -> None:
    source = ("A", "B", "C", "D", "E")
    plan = DeleteLinesPlan.build(source, deleted=(1, 3))

    assert plan.lines == ("A", "C", "E")
    assert plan.project(Cursor(0, 1)) == Cursor(0, 1)
    assert plan.project(Cursor(2, 1)) == Cursor(1, 1)
    assert plan.project(Cursor(4, 1)) == Cursor(2, 1)
    assert plan.project(Cursor(1, 1)) == Cursor(1, 0)
    assert plan.project(Cursor(3, 1)) == Cursor(2, 0)


def test_duplicate_selected_block_shifts_unselected_cursor_below_insertion() -> None:
    ed, eb = _editor("A\nB\nC\nD\nE")
    _set_cursor_state(
        eb,
        cursors=[Cursor(1, 0), Cursor(4, 1)],
        anchors=[Cursor(3, 0), None],
        primary=0,
    )

    assert ed.run_action("DuplicateLine") is True
    assert eb.buf.get_text() == "A\nB\nC\nB\nC\nD\nE"
    assert eb.cursors == [Cursor(1, 0), Cursor(6, 1)]
    assert eb.sel_anchors == [Cursor(3, 0), None]
    assert ed.selection_text() == "B\nC\n"


def test_cutting_every_line_keeps_one_empty_buffer_line_and_one_cursor() -> None:
    ed, eb = _editor("A\nB")
    _set_cursor_state(
        eb,
        cursors=[Cursor(0, 1), Cursor(1, 1)],
        anchors=[None, None],
        primary=1,
    )
    before_version = eb.buf.version

    assert ed.run_action("CutLine") is True
    assert eb.buf.lines == [""]
    assert eb.cursors == [Cursor(0, 0)]
    assert eb.sel_anchors == [None]
    assert ed.clipboard_text() == "A\nB\n"
    assert eb.buf.version == before_version + 1
