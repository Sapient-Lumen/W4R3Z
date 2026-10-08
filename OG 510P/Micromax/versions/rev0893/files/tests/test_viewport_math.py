from __future__ import annotations

from micromax_editor.viewport_math import (
    VisualPoint,
    ViewportTop,
    contindent_for_line,
    cursor_visual_yx,
    doc_pos_for_visual_row,
    leading_ws_cols,
    total_visual_rows,
    viewport_top_for_visual_start,
    viewport_visual_start,
    wrap_row_starts_for_line,
)


def test_leading_ws_cols_counts_tabs_as_indentation_columns() -> None:
    assert leading_ws_cols("\t\t  body") == 4
    assert contindent_for_line("\t\tbody", width=8, setting=-1) == 2


def test_wrap_row_starts_and_cursor_mapping_are_pure_and_reversible() -> None:
    lines = ["  alpha beta gamma", "tail"]
    starts = wrap_row_starts_for_line(lines[0], width=8, contindent=2, wordwrap=True)
    assert starts == [0, 8, 13]

    point = cursor_visual_yx(lines, line=0, col=13, width=8, contindent_setting=2, wordwrap=True)
    assert point == VisualPoint(2, 2)

    assert doc_pos_for_visual_row(lines, target_y=2, goal_x=2, width=8, contindent_setting=2, wordwrap=True) == (0, 13)
    assert total_visual_rows(lines, width=8, contindent_setting=2, wordwrap=True) == 4


def test_viewport_visual_start_round_trips_to_top_line_and_subline() -> None:
    lines = ["abcdefghi", "jklmnop"]
    start = viewport_visual_start(
        lines,
        top_line=0,
        top_subline=1,
        width=4,
        contindent_setting=0,
        wordwrap=False,
    )
    assert start == 1
    assert viewport_top_for_visual_start(
        lines,
        start_y=start,
        width=4,
        contindent_setting=0,
        wordwrap=False,
    ) == ViewportTop(0, 1)

    assert viewport_top_for_visual_start(
        lines,
        start_y=99,
        width=4,
        contindent_setting=0,
        wordwrap=False,
    ) == ViewportTop(1, 0)
