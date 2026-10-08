from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, colorcolumn_screen_x


class _CaptureStdScr:
    def __init__(self, *, h: int = 20, w: int = 40) -> None:
        self.h = h
        self.w = w
        self.lines: dict[int, str] = {}
        self.calls: list[tuple[int, int, str, int]] = []
        self.cursor = (0, 0)

    def erase(self) -> None:
        self.lines = {}
        self.calls = []

    def getmaxyx(self) -> tuple[int, int]:
        return (self.h, self.w)

    def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
        attr = int(args[0]) if args else 0
        self.calls.append((int(y), int(x), str(s)[: max(0, int(n))], attr))
        cur = self.lines.get(int(y), '')
        need = max(len(cur), int(x) + max(0, int(n)))
        buf = list(cur.ljust(need))
        txt = str(s)[: max(0, int(n))]
        for i, ch in enumerate(txt):
            pos = int(x) + i
            if pos >= len(buf):
                buf.extend(' ' * (pos - len(buf) + 1))
            buf[pos] = ch
        self.lines[int(y)] = ''.join(buf).rstrip()

    def move(self, y: int, x: int) -> None:
        self.cursor = (int(y), int(x))

    def refresh(self) -> None:
        pass


def test_colorcolumn_screen_x_tracks_scroll_and_softwrap_policy() -> None:
    assert colorcolumn_screen_x(colorcolumn=0, frag_start=0, view_width=10, softwrap=False) is None
    assert colorcolumn_screen_x(colorcolumn=5, frag_start=0, view_width=10, softwrap=False) == 4
    assert colorcolumn_screen_x(colorcolumn=5, frag_start=3, view_width=10, softwrap=False) == 1
    assert colorcolumn_screen_x(colorcolumn=5, frag_start=5, view_width=10, softwrap=False) is None
    assert colorcolumn_screen_x(colorcolumn=5, frag_start=99, view_width=10, softwrap=True) == 4



def test_render_colorcolumn_marks_visible_text_cell(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('colorcolumn', '3', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    mark_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 2 and s == 'p']
    plain_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == 'al']

    assert mark_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in mark_calls)
    assert plain_calls and all(not (attr & curses.A_REVERSE) for attr in plain_calls)



def test_render_colorcolumn_draws_blank_marker_past_short_line_end(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'hi\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('colorcolumn', '5', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    blank_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 4 and s == ' ']
    assert blank_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in blank_calls)



def test_render_colorcolumn_repeats_per_softwrapped_screen_row(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghij\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)
    ed.options.set('colorcolumn', '4', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=5)
    _render(fake, ed)

    first_row_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 3 and s == 'd']
    second_row_calls = [attr for y, x, s, attr in fake.calls if y == 1 and x == 3 and s == 'i']

    assert first_row_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in first_row_calls)
    assert second_row_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in second_row_calls)



def test_render_colorcolumn_also_marks_help_buffer_rows(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('guide.md', 'alpha\n')
    eb = ed.cur()
    eb.local_options['readonly'] = True
    eb.local_options['help_doc'] = 'guide'
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('colorcolumn', '3', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    mark_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 2 and s == 'p']
    assert mark_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in mark_calls)
