from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, cursorline_row_attr


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


def test_cursorline_row_attr_only_marks_current_row_when_enabled() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\nbeta\n')
    eb = ed.cur()

    assert cursorline_row_attr(ed, row=1, current_row=1, local_options=eb.local_options) & curses.A_UNDERLINE
    assert cursorline_row_attr(ed, row=0, current_row=1, local_options=eb.local_options) == 0

    ed.options.set('cursorline', 'false', local=eb.local_options)
    assert cursorline_row_attr(ed, row=1, current_row=1, local_options=eb.local_options) == 0


def test_render_cursorline_marks_only_current_plain_row(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\nbeta\ngamma\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 1
    eb.cursors[eb.primary].col = 1
    ed.options.set('cursorline', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    current_calls = [attr for y, x, s, attr in fake.calls if y == 1 and x == 0 and s == 'beta']
    other_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == 'alpha']

    assert current_calls and any(attr & curses.A_UNDERLINE for attr in current_calls)
    assert other_calls and all(not (attr & curses.A_UNDERLINE) for attr in other_calls)


def test_render_cursorline_marks_only_current_visual_row_under_softwrap(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghijklm\nshort\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 0
    eb.cursors[eb.primary].col = 10  # wrapped continuation row
    ed.options.set('cursorline', 'true', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=10)
    _render(fake, ed)

    first_row_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == 'abcdefghij']
    wrapped_row_calls = [attr for y, x, s, attr in fake.calls if y == 1 and x == 0 and s == 'klm']

    assert first_row_calls and all(not (attr & curses.A_UNDERLINE) for attr in first_row_calls)
    assert wrapped_row_calls and any(attr & curses.A_UNDERLINE for attr in wrapped_row_calls)
