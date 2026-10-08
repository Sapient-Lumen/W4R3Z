from __future__ import annotations

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor


def test_view_rows_hscroll_when_softwrap_off() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdef\nXYZ")
    ed.set_viewport(top_line=0, left_col=2, height=2, width=3, follow_cursor=False)

    rows = ed.view_rows(height=2, width=3)
    assert rows == [
        (0, 2, "cde"),
        (1, 2, "Z"),
    ]


def test_view_rows_wrap_when_softwrap_on() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdefghi\nXYZ")
    ed.options.set("softwrap", "true")
    # Try to set a left_col; it should be forced to 0.
    ed.set_viewport(top_line=0, left_col=99, height=4, width=4, follow_cursor=False)
    assert ed.viewport_model()["left_col"] == 0

    rows = ed.view_rows(height=4, width=4)
    assert rows == [
        (0, 0, "abcd"),
        (0, 4, "efgh"),
        (0, 8, "i"),
        (1, 0, "XYZ"),
    ]


def test_cursor_view_pos_wrap_mapping() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdefgh\n")
    ed.options.set("softwrap", "true")
    ed.set_viewport(top_line=0, height=5, width=4, follow_cursor=False)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 5)
    y, x = ed.cursor_view_pos(height=5, width=4)
    assert (y, x) == (1, 1)

    # EOL on a wrap boundary should stay on the last visual row.
    eb.cursors[eb.primary] = Cursor(0, 8)
    y2, x2 = ed.cursor_view_pos(height=5, width=4)
    assert (y2, x2) == (1, 4)


def test_softwrap_visual_up_down_moves_within_wrapped_line() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdefghij\nXYZ")
    ed.options.set("softwrap", "true")
    ed.set_viewport(top_line=0, height=4, width=4, follow_cursor=False)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 0)

    assert ed.run_action("CursorDown")
    assert eb.cursors[eb.primary] == Cursor(0, 4)

    assert ed.run_action("CursorDown")
    assert eb.cursors[eb.primary] == Cursor(0, 8)

    # Next visual row steps into the next logical line.
    assert ed.run_action("CursorDown")
    assert eb.cursors[eb.primary] == Cursor(1, 0)

    # And moving back up walks visual rows.
    assert ed.run_action("CursorUp")
    assert eb.cursors[eb.primary] == Cursor(0, 8)


def test_softwrap_scrolls_by_visual_rows_using_top_subline() -> None:
    ed = Editor()
    # A single long line that wraps into 4 visual rows at width=4.
    ed.new_buffer("*t*", "abcdefghijklmnop\n")
    ed.options.set("softwrap", "true")
    ed.set_viewport(top_line=0, height=2, width=4, follow_cursor=True)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 0)
    ed.ensure_cursor_visible()

    # Walk down three visual rows; viewport should start partway through the same line.
    assert ed.run_action("CursorDown")
    assert ed.run_action("CursorDown")
    assert ed.run_action("CursorDown")

    vp = ed.viewport_model()
    assert vp["top_line"] == 0
    assert vp["top_subline"] >= 1

    rows = ed.view_rows(height=2, width=4)
    # First visible fragment should match the viewport's top_subline.
    start0 = vp["top_subline"] * vp["width"]
    assert rows[0] == (0, start0, "abcdefghijklmnop"[start0 : start0 + 4])


def test_softwrap_scrollmargin_keeps_visual_context_rows() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdefghijklmnop\n")
    ed.options.set("softwrap", "true")
    ed.options.set("scrollmargin", "1")
    ed.set_viewport(top_line=0, height=3, width=4, follow_cursor=True)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 0)
    ed.ensure_cursor_visible()

    assert ed.run_action("CursorDown")
    assert ed.viewport_model()["top_subline"] == 0

    # Moving into the last visible visual row should now scroll one wrapped row
    # earlier, keeping one line of context above when possible.
    assert ed.run_action("CursorDown")
    vp = ed.viewport_model()
    assert vp["top_line"] == 0
    assert vp["top_subline"] == 1


def test_softwrap_contindent_auto_adds_prefix_and_visual_home_end() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "    abcdefghij\n")
    ed.options.set("softwrap", "true")
    ed.options.set("softwrap.contindent", "-1")  # auto: uses leading indent
    ed.set_viewport(top_line=0, height=6, width=6, follow_cursor=False)

    rows = ed.view_rows(height=6, width=6)
    assert rows[:4] == [
        (0, 0, "    ab"),
        (0, 6, "    cd"),
        (0, 8, "    ef"),
        (0, 10, "    gh"),
    ]

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 7)  # in the "cd" fragment
    y, x = ed.cursor_view_pos(height=6, width=6)
    assert (y, x) == (1, 5)  # includes continuation indent prefix

    assert ed.run_action("StartOfLine")
    assert eb.cursors[eb.primary] == Cursor(0, 6)

    assert ed.run_action("EndOfLine")
    assert eb.cursors[eb.primary] == Cursor(0, 8)


def test_softwrap_page_moves_respect_pageoverlap_by_visual_row() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdefghijklmnopqrstuvwxyzab\n")
    ed.options.set("softwrap", "true")
    ed.options.set("pageoverlap", "1")
    ed.set_viewport(top_line=0, top_subline=0, height=4, width=4, follow_cursor=False)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 0)

    assert ed.run_action("PageDown") is True
    vp = ed.viewport_model()
    assert vp["top_line"] == 0
    assert vp["top_subline"] == 3
    assert eb.cursors[eb.primary] == Cursor(0, 12)

    y, x = ed.cursor_view_pos(height=4, width=4)
    assert (y, x) == (0, 0)

    assert ed.run_action("PageUp") is True
    vp2 = ed.viewport_model()
    assert vp2["top_line"] == 0
    assert vp2["top_subline"] == 0
    assert eb.cursors[eb.primary] == Cursor(0, 0)


def test_view_rows_wordwrap_prefers_spaces_when_softwrap_is_on() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "alpha beta gamma\n")
    ed.options.set("softwrap", "true")
    ed.options.set("wordwrap", "true")
    ed.set_viewport(top_line=0, left_col=0, height=4, width=10, follow_cursor=False)

    rows = ed.view_rows(height=4, width=10)
    assert rows[:2] == [
        (0, 0, "alpha "),
        (0, 6, "beta gamma"),
    ]


def test_cursor_view_pos_tracks_wordwrapped_row_starts() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "alpha beta gamma\n")
    ed.options.set("softwrap", "true")
    ed.options.set("wordwrap", "true")
    ed.set_viewport(top_line=0, height=4, width=10, follow_cursor=False)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 8)
    y, x = ed.cursor_view_pos(height=4, width=10)
    assert (y, x) == (1, 2)


def test_softwrap_visual_up_down_follow_wordwrap_boundaries() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "alpha beta gamma\nXYZ")
    ed.options.set("softwrap", "true")
    ed.options.set("wordwrap", "true")
    ed.set_viewport(top_line=0, height=4, width=10, follow_cursor=False)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 0)

    assert ed.run_action("CursorDown")
    assert eb.cursors[eb.primary] == Cursor(0, 6)

    assert ed.run_action("CursorDown")
    assert eb.cursors[eb.primary] == Cursor(1, 0)

    assert ed.run_action("CursorUp")
    assert eb.cursors[eb.primary] == Cursor(0, 6)


def test_softwrap_auto_contindent_counts_leading_tabs() -> None:
    ed = Editor()
    ed.new_buffer("*tabs*", "\t\tabcdef\n")
    ed.options.set("softwrap", "true")
    ed.options.set("softwrap.contindent", "-1")
    ed.set_viewport(top_line=0, height=4, width=5, follow_cursor=False)

    assert ed.view_rows(height=4, width=5)[:2] == [
        (0, 0, "\t\tabc"),
        (0, 5, "  def"),
    ]

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 6)
    assert ed.cursor_view_pos(height=4, width=5) == (1, 3)


def test_view_rows_reuses_sparse_wordwrap_layout_without_full_boundary_vector(
    monkeypatch,
) -> None:
    import micromax_editor.editor as editor_module

    ed = Editor()
    ed.new_buffer("*t*", ("alpha beta gamma delta " * 20) + "\nshort")
    ed.options.set("softwrap", "true")
    ed.options.set("wordwrap", "true")
    ed.set_viewport(top_line=0, left_col=0, height=12, width=10, follow_cursor=False)

    def forbidden_starts(*_args, **_kwargs):
        raise AssertionError("wordwrap rendering must not retain every row boundary")

    monkeypatch.setattr(
        editor_module.viewport_math,
        "wrap_row_starts_for_line",
        forbidden_starts,
    )
    first = ed.view_rows(height=12, width=10)
    index = ed._visual_row_index_for(ed.cur(), w=10)
    cached = index.wordwrap_line_index(0, ed.cur().buf.lines[0])
    second = ed.view_rows(height=12, width=10)

    assert first == second
    assert len(first) == 12
    assert {line for line, _start, _text in first} == {0}
    assert index.wordwrap_cache_size == 1
    assert index.wordwrap_line_index(0, ed.cur().buf.lines[0]) is cached


def test_editor_softwrap_prefix_index_refreshes_only_the_changed_line(monkeypatch) -> None:
    import micromax_editor.viewport_math as viewport_module

    ed = Editor()
    ed.new_buffer("*t*", "\n".join("abcdefgh" for _ in range(64)))
    eb = ed.cur()
    eb.buf.set_fastdirty(True)
    ed.options.set("softwrap", "true", local=eb.local_options)

    real_wraps = viewport_module.wraps_for_line
    calls = 0

    def counted_wraps(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_wraps(*args, **kwargs)

    monkeypatch.setattr(viewport_module, "wraps_for_line", counted_wraps)
    assert ed._total_visual_rows(eb, w=4) == 128
    assert calls == 64

    # Unchanged prefix, total, and inverse queries reuse the same compact index.
    assert ed._visual_row_index(eb, 32, 0, w=4) == 64
    assert ed._doc_pos_for_visual_row(eb, 64, 0, w=4) == Cursor(32, 0)
    assert ed._total_visual_rows(eb, w=4) == 128
    assert calls == 64

    eb.buf.insert(Cursor(32, 0), "xxxx")
    assert ed._total_visual_rows(eb, w=4) == 129
    assert calls == 65

    # Wrap configuration is part of the lease, so width changes rebuild safely.
    assert ed._total_visual_rows(eb, w=5) > 0
    assert calls == 65 + len(eb.buf.lines)


def test_fixed_wrap_renderer_materializes_only_visible_fragments(monkeypatch) -> None:
    import micromax_editor.viewport_math as viewport_module

    ed = Editor()
    ed.new_buffer("*long*", "x" * 2_000_000)
    eb = ed.cur()
    eb.buf.set_fastdirty(True)
    ed.options.set("softwrap", "true", local=eb.local_options)
    ed.options.set("wordwrap", "false", local=eb.local_options)
    ed.set_viewport(top_line=0, left_col=0, height=3, width=80, follow_cursor=False)
    ed.viewport_top_subline = 10_000

    def forbidden_starts(*_args, **_kwargs):
        raise AssertionError("fixed rendering must not build all wrap boundaries")

    monkeypatch.setattr(viewport_module, "wrap_row_starts_for_line", forbidden_starts)
    rows = ed.view_rows(height=3, width=80)

    assert [start for _line, start, _text in rows] == [800_000, 800_080, 800_160]
    assert all(len(fragment) == 80 for _line, _start, fragment in rows)
