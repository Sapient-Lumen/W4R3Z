from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.buffer import Cursor


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
