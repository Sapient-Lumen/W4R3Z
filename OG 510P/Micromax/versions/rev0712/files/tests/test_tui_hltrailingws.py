from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, trailing_whitespace_spans


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


def test_trailing_whitespace_spans_intersects_visible_fragment() -> None:
    assert trailing_whitespace_spans('alpha  ') == [(5, 7)]
    assert trailing_whitespace_spans('alpha  ', frag_start=0, frag_text='alpha') == []
    assert trailing_whitespace_spans('alpha  ', frag_start=5, frag_text='  ') == [(0, 2)]
    assert trailing_whitespace_spans('alpha\t\t', frag_start=6, frag_text='\t') == [(0, 1)]



def test_render_hltrailingws_marks_visible_trailing_whitespace(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha  \nbeta\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('hltrailingws', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    plain_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == 'alpha']
    trail_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 5 and s == '  ']

    assert plain_calls and all(not (attr & curses.A_REVERSE) for attr in plain_calls)
    assert trail_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in trail_calls)



def test_render_hltrailingws_marks_only_final_softwrapped_fragment(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghij  \n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)
    ed.options.set('hltrailingws', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=10)
    _render(fake, ed)

    first_row_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == 'abcdefghij']
    wrapped_trail_calls = [attr for y, x, s, attr in fake.calls if y == 1 and x == 0 and s == '  ']

    assert first_row_calls and all(not (attr & curses.A_REVERSE) for attr in first_row_calls)
    assert wrapped_trail_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in wrapped_trail_calls)
