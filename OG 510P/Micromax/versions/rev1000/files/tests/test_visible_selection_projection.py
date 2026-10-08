from __future__ import annotations

from micromax_editor.buffer import Cursor
import micromax_editor.editor as editor_module
from micromax_editor.editor import Editor
from micromax_editor.highlight import project_highlight_spans
from micromax_editor.selection import Selection, visible_selection_fragment


def test_visible_selection_fragment_clips_to_horizontal_fragment() -> None:
    fragment = visible_selection_fragment(
        Selection(Cursor(0, 2), Cursor(0, 9)),
        line_index=0,
        line_length=12,
        fragment_start=5,
        fragment_length=4,
    )

    assert fragment is not None
    assert (fragment.start, fragment.end, fragment.eol_x) == (0, 4, None)


def test_visible_selection_fragment_exposes_selected_newline_cell() -> None:
    start_row = visible_selection_fragment(
        Selection(Cursor(0, 3), Cursor(2, 0)),
        line_index=0,
        line_length=5,
        fragment_start=0,
        fragment_length=5,
    )
    empty_middle_row = visible_selection_fragment(
        Selection(Cursor(0, 3), Cursor(2, 0)),
        line_index=1,
        line_length=0,
        fragment_start=0,
        fragment_length=0,
    )
    end_row = visible_selection_fragment(
        Selection(Cursor(0, 3), Cursor(2, 0)),
        line_index=2,
        line_length=7,
        fragment_start=0,
        fragment_length=7,
    )

    assert start_row is not None
    assert (start_row.start, start_row.end, start_row.eol_x) == (3, 5, 5)
    assert empty_middle_row is not None
    assert (empty_middle_row.start, empty_middle_row.end, empty_middle_row.eol_x) == (
        0,
        0,
        0,
    )
    assert end_row is None


def test_project_highlight_spans_clips_and_rejects_malformed_tags() -> None:
    spans = [
        [0, 3, "kw"],
        [4, 10, "comment"],
        [3, 8, "unknown"],
        ["bad", 8, "str"],
        [7, 7, "num"],
    ]

    assert project_highlight_spans(
        spans,
        fragment_start=2,
        fragment_length=5,
    ) == [
        [0, 1, "kw"],
        [2, 5, "comment"],
    ]


def test_selection_heavy_reads_normalize_cursor_sidecars_once(monkeypatch) -> None:
    ed = Editor()
    ed.new_buffer("multi", "alpha\nbeta\n")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 2), Cursor(1, 2)]
    eb.sel_anchors[:] = [Cursor(0, 0), Cursor(1, 0)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    original = ed._normalize_cursor_lists
    calls = 0

    def counted(target) -> None:  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        original(target)

    monkeypatch.setattr(ed, "_normalize_cursor_lists", counted)

    assert ed.has_selection() is True
    assert calls == 1

    calls = 0
    ranges = ed._all_selection_ranges()
    assert [(i, s.line, s.col, e.line, e.col) for i, s, e in ranges] == [
        (0, 0, 0, 0, 2),
        (1, 1, 0, 1, 2),
    ]
    assert calls == 1

    calls = 0
    status = ed.status_model()
    assert status["selection_count"] == 2
    assert status["primary_selection_chars"] == 2
    assert calls == 1

    calls = 0
    screen = ed.screen_model(8, 40)
    assert screen["viewport_cues"]["selection_ranges_visible"] == 2
    assert calls == 1


def test_screen_window_reuses_one_status_snapshot(monkeypatch) -> None:
    ed = Editor()
    ed.new_buffer("status", "alpha\n")

    original = ed._status_model_from_normalized_buffer
    calls = 0

    def counted_status(target):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        return original(target)

    monkeypatch.setattr(ed, "_status_model_from_normalized_buffer", counted_status)

    parts = ed._screen_window_parts(8, 40)

    assert parts["bottom_rows_text"]
    assert calls == 1


def test_viewport_syntax_filetype_match_is_case_and_space_normalized() -> None:
    ed = Editor()
    ed.new_buffer("case.mx", ": word ;", path="case.mx")
    eb = ed.cur()
    eb.local_options["filetype"] = "  MicroMax  "
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)

    model = ed.viewport_cues_model(1, 20)

    assert model["filetype"] == "micromax"
    assert model["syntax_enabled"] == 1
    assert model["rows"][0]["syntax_spans"][:2] == [
        [0, 1, "kw"],
        [2, 6, "def"],
    ]


def test_viewport_syntax_scan_stops_at_explicit_long_line_budget(monkeypatch) -> None:
    ed = Editor()
    ed.new_buffer("long.mx", "\\" + ("x" * 5000), path="long.mx")
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("softwrap", "false", local=eb.local_options)
    eb.cursors[eb.primary] = Cursor(0, 4150)
    ed.set_viewport(left_col=4080, follow_cursor=False)

    original_highlight_line = editor_module.highlight_line
    scanned_lengths: list[int] = []

    def counted_highlight_line(filetype: str, text: str) -> list[list[object]]:
        scanned_lengths.append(len(text))
        return original_highlight_line(filetype, text)

    monkeypatch.setattr(editor_module, "highlight_line", counted_highlight_line)
    model = ed.viewport_cues_model(2, 80)

    assert scanned_lengths == [4096]
    assert model["syntax_scan_max_chars"] == 4096
    assert model["syntax_truncated_rows"] == 1
    assert model["rows"][0]["syntax_spans"] == [[0, 16, "comment"]]


def test_viewport_selection_projection_is_bounded_but_keeps_primary(monkeypatch) -> None:
    monkeypatch.setattr(editor_module, "VISIBLE_SELECTION_MAX_RANGES", 3)

    ed = Editor()
    ed.new_buffer("many", "x" * 20)
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, col) for col in (2, 4, 6, 8, 10)]
    eb.sel_anchors[:] = [Cursor(0, col) for col in (1, 3, 5, 7, 9)]
    eb.cursor_ids[:] = [1, 2, 3, 4, 5]
    eb.primary = 4
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)

    model = ed.viewport_cues_model(1, 20)

    assert model["selection_range_limit"] == 3
    assert model["selection_ranges_visible"] == 3
    assert model["selection_projection_truncated"] == 2
    row = model["rows"][0]
    assert row["primary_selection_spans"] == [[9, 10]]
    assert row["secondary_selection_spans"] == [[1, 2], [3, 4]]


def test_selection_ranges_visible_excludes_offscreen_ranges() -> None:
    ed = Editor()
    ed.new_buffer("offscreen", "zero\none\ntwo\nthree\nfour\n")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 2), Cursor(4, 2)]
    eb.sel_anchors[:] = [Cursor(0, 0), Cursor(4, 0)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)

    model = ed.viewport_cues_model(1, 20)

    assert model["selection_ranges_visible"] == 1
    assert model["selection_projection_truncated"] == 0
    assert model["rows"][0]["primary_selection_spans"] == [[0, 2]]
    assert model["rows"][0]["secondary_selection_spans"] == []


def test_projection_helpers_shift_past_display_only_prefix() -> None:
    highlight = project_highlight_spans(
        [[8, 10, "def"]],
        fragment_start=8,
        fragment_length=4,
        display_offset=2,
    )
    selection = visible_selection_fragment(
        Selection(Cursor(0, 8), Cursor(0, 10)),
        line_index=0,
        line_length=12,
        fragment_start=8,
        fragment_length=4,
        display_offset=2,
    )

    assert highlight == [[2, 4, "def"]]
    assert selection is not None
    assert (selection.start, selection.end, selection.eol_x) == (2, 4, None)


def test_softwrap_source_display_seam_aligns_syntax_selection_and_search() -> None:
    ed = Editor()
    ed.new_buffer("wrap.mx", ": abcdefgh  ;", path="wrap.mx")
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("softwrap", "true", local=eb.local_options)
    ed.options.set("softwrap.contindent", "2", local=eb.local_options)
    ed.options.set("hlsearch", "true", local=eb.local_options)
    eb.cursors[eb.primary] = Cursor(0, 10)
    eb.sel_anchors[eb.primary] = Cursor(0, 8)
    ed.search.query = "  "

    window = ed.edit_window_model(4, 8)
    continuation = window["rows"][1]
    assert continuation["text"] == "  gh  ;"
    assert continuation["source_text_x"] == 2
    assert continuation["source_text_length"] == 5

    model = ed.viewport_cues_model(4, 8)
    row = model["rows"][1]
    assert row["source_text_x"] == 2
    assert row["syntax_spans"] == [[2, 4, "def"], [6, 7, "kw"]]
    assert row["primary_selection_spans"] == [[2, 4]]
    assert row["search_spans"] == [[4, 6]]
    assert row["current_search_spans"] == [[4, 6]]
    assert all(
        int(span[0]) >= row["source_text_x"]
        for field in (
            "syntax_spans",
            "primary_selection_spans",
            "search_spans",
            "current_search_spans",
        )
        for span in row[field]
    )


def test_softwrap_source_display_seam_keeps_showchars_and_trailing_cues_off_prefix() -> None:
    ed = Editor()
    ed.new_buffer("wrap.txt", "abcdefgh  ", path="wrap.txt")
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("softwrap", "true", local=eb.local_options)
    ed.options.set("softwrap.contindent", "2", local=eb.local_options)
    ed.options.set("showchars", "space=.", local=eb.local_options)
    ed.options.set("hltrailingws", "true", local=eb.local_options)

    screen = ed.screen_model(4, 8)
    showchars_row = screen["showchars_rows"]["rows"][1]
    cues_row = screen["viewport_cues"]["rows"][1]

    assert showchars_row["text"] == "    "
    assert showchars_row["source_text_x"] == 2
    assert showchars_row["display_text"] == "  .."
    assert showchars_row["spans"] == [[2, 3], [3, 4]]
    assert cues_row["trailing_spans"] == [[2, 4]]


def test_softwrap_source_display_seam_aligns_tab_and_brace_diagnostics() -> None:
    ed = Editor()
    ed.new_buffer("wrap.txt", "abcdefgh\t\nabcdefgh()", path="wrap.txt")
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("softwrap", "true", local=eb.local_options)
    ed.options.set("softwrap.contindent", "2", local=eb.local_options)
    ed.options.set("hltaberrors", "true", local=eb.local_options)
    ed.options.set("tabstospaces", "true", local=eb.local_options)
    ed.options.set("matchbrace", "true", local=eb.local_options)
    eb.cursors[eb.primary] = Cursor(1, 8)

    rows = ed.viewport_cues_model(6, 8)["rows"]
    tab_row = next(row for row in rows if row["line"] == 0 and row["start_col"] == 8)
    brace_row = next(row for row in rows if row["line"] == 1 and row["start_col"] == 8)

    assert tab_row["text"] == "  \t"
    assert tab_row["source_text_x"] == 2
    assert tab_row["tab_error_spans"] == [[2, 3]]
    assert brace_row["text"] == "  ()"
    assert brace_row["source_text_x"] == 2
    assert brace_row["brace_spans"] == [[2, 3], [3, 4]]
