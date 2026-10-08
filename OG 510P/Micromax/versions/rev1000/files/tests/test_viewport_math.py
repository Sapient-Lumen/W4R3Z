from __future__ import annotations

from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.viewport_math import (
    VisualPoint,
    VisualRowIndex,
    ViewportTop,
    WordWrapLayout,
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


def test_visual_row_index_matches_pure_reference_geometry() -> None:
    lines = ["", "alpha beta gamma", "  indented tail", "z"]
    index = VisualRowIndex(
        lines,
        version=7,
        width=7,
        contindent_setting=2,
        wordwrap=True,
    )

    assert index.total_rows == total_visual_rows(
        lines,
        width=7,
        contindent_setting=2,
        wordwrap=True,
    )
    assert index.storage_bytes == len(lines) * 16
    for line in range(len(lines)):
        for subline in range(index.row_count(line)):
            expected = viewport_visual_start(
                lines,
                top_line=line,
                top_subline=subline,
                width=7,
                contindent_setting=2,
                wordwrap=True,
            )
            assert index.visual_row(line, subline) == expected
            assert index.line_subline_for_visual(expected) == ViewportTop(line, subline)

    assert index.line_subline_for_visual(10_000) == ViewportTop(len(lines) - 1, 0)


def test_visual_row_index_reuses_unchanged_geometry_and_updates_one_line(
    monkeypatch,
) -> None:
    import micromax_editor.viewport_math as viewport_module

    buf = Buffer("\n".join("abcdefgh" for _ in range(32)))
    buf.set_fastdirty(True)
    real_wraps = viewport_module.wraps_for_line
    calls = 0

    def counted_wraps(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_wraps(*args, **kwargs)

    monkeypatch.setattr(viewport_module, "wraps_for_line", counted_wraps)
    index = VisualRowIndex(
        buf.lines,
        version=buf.version,
        width=4,
        contindent_setting=0,
        wordwrap=False,
    )
    assert calls == len(buf.lines)
    baseline_total = index.total_rows

    index.sync(
        buf.lines,
        version=buf.version,
        change=buf.last_change,
        width=4,
        contindent_setting=0,
        wordwrap=False,
    )
    assert calls == len(buf.lines)

    buf.insert(Cursor(17, 0), "xxxx")
    assert buf.last_change is not None
    assert (
        buf.last_change.start_line,
        buf.last_change.old_line_count,
        buf.last_change.new_line_count,
    ) == (17, 1, 1)
    index.sync(
        buf.lines,
        version=buf.version,
        change=buf.last_change,
        width=4,
        contindent_setting=0,
        wordwrap=False,
    )
    assert calls == len(buf.lines) + 1
    assert index.total_rows == baseline_total + 1


def test_visual_row_index_rebuilds_after_line_splice_or_unknown_touch(monkeypatch) -> None:
    import micromax_editor.viewport_math as viewport_module

    buf = Buffer("alpha\nbeta\ngamma")
    buf.set_fastdirty(True)
    index = VisualRowIndex(
        buf.lines,
        version=buf.version,
        width=4,
        contindent_setting=0,
    )
    real_wraps = viewport_module.wraps_for_line
    calls = 0

    def counted_wraps(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_wraps(*args, **kwargs)

    monkeypatch.setattr(viewport_module, "wraps_for_line", counted_wraps)
    buf.insert(Cursor(1, 2), "X\nY")
    assert buf.last_change is not None
    assert (buf.last_change.old_line_count, buf.last_change.new_line_count) == (1, 2)
    index.sync(
        buf.lines,
        version=buf.version,
        change=buf.last_change,
        width=4,
        contindent_setting=0,
    )
    assert calls == len(buf.lines)
    assert index.line_count == len(buf.lines)
    assert index.total_rows == total_visual_rows(
        buf.lines,
        width=4,
        contindent_setting=0,
    )

    calls = 0
    buf.lines[0] = "externally changed"
    buf.touch_external()
    assert buf.last_change is None
    index.sync(
        buf.lines,
        version=buf.version,
        change=buf.last_change,
        width=4,
        contindent_setting=0,
    )
    assert calls == len(buf.lines)


def test_fixed_wrap_geometry_uses_arithmetic_not_a_boundary_vector(monkeypatch) -> None:
    import micromax_editor.viewport_math as viewport_module

    text = "x" * 1_000_003

    def forbidden_starts(*_args, **_kwargs):
        raise AssertionError("fixed wrapping must not materialize every row start")

    monkeypatch.setattr(viewport_module, "wrap_row_starts_for_line", forbidden_starts)
    count = viewport_module.wraps_for_line(
        text,
        width=80,
        contindent=2,
        wordwrap=False,
    )
    assert count == 1 + ((len(text) - 80 + 77) // 78)
    assert viewport_module.wrap_start_for_row_in_line(
        text,
        width=80,
        row=10_000,
        contindent=2,
        wordwrap=False,
    ) == 80 + (9_999 * 78)
    assert viewport_module.wrap_end_for_row_in_line(
        text,
        width=80,
        row=count - 1,
        contindent=2,
        wordwrap=False,
    ) == len(text)
    assert viewport_module.wrap_row_for_col(
        text,
        len(text),
        width=80,
        contindent=2,
        wordwrap=False,
    ) == count - 1

def test_sparse_wordwrap_layout_matches_reference_boundaries_and_inverse_lookup() -> None:
    text = "  alpha beta gamma delta epsilon"
    starts = wrap_row_starts_for_line(
        text,
        width=8,
        contindent=2,
        wordwrap=True,
    )
    layout = WordWrapLayout(text, width=8, contindent=2)

    assert layout.row_count == len(starts)
    assert [layout.start_for_row(row) for row in range(layout.row_count)] == starts
    assert list(layout.iter_bounds(0, layout.row_count)) == [
        (start, starts[row + 1] if row + 1 < len(starts) else len(text))
        for row, start in enumerate(starts)
    ]
    for col in range(len(text) + 1):
        expected = max(row for row, start in enumerate(starts) if start <= col)
        assert layout.row_for_col(col) == expected


def test_sparse_wordwrap_layout_caps_checkpoint_payload_on_huge_narrow_line() -> None:
    text = "x" * 1_000_000
    layout = WordWrapLayout(text, width=1, contindent=0)

    assert layout.row_count == len(text)
    assert layout.storage_bytes <= WordWrapLayout._MAX_CHECKPOINT_BYTES
    assert layout.start_for_row(999_999) == 999_999
    assert layout.bounds_for_row(999_999) == (999_999, 1_000_000)
    assert layout.row_for_col(999_999) == 999_999


def test_visual_row_index_wordwrap_cache_reuses_then_evicts_changed_line() -> None:
    buf = Buffer(("alpha beta " * 8_000) + "\ntail")
    buf.set_fastdirty(True)
    index = VisualRowIndex(
        buf.lines,
        version=buf.version,
        width=10,
        contindent_setting=0,
        wordwrap=True,
    )

    first = index.wordwrap_line_index(0, buf.lines[0])
    assert index.wordwrap_line_index(0, buf.lines[0]) is first
    assert index.wordwrap_cache_size == 1

    buf.insert(Cursor(0, 0), "prefix ")
    index.sync(
        buf.lines,
        version=buf.version,
        change=buf.last_change,
        width=10,
        contindent_setting=0,
        wordwrap=True,
    )
    second = index.wordwrap_line_index(0, buf.lines[0])
    assert second is not first
    assert second.text is buf.lines[0]
    assert index.wordwrap_cache_size == 1

