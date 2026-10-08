from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, scrollbar_gutter_width, scrollbar_thumb_char, scrollbar_thumb_span


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


def test_scrollbar_helpers_cover_disabled_fit_and_mid_document_cases() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\n')
    eb = ed.cur()
    assert scrollbar_gutter_width(ed) == 0
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    assert scrollbar_gutter_width(ed) == 1
    assert scrollbar_thumb_char(ed) == '|'
    ed.options.set('scrollbarchar', '#', local=eb.local_options)
    assert scrollbar_thumb_char(ed) == '#'
    ed.options.set('scrollbarchar', '', local=eb.local_options)
    assert scrollbar_thumb_char(ed) == '|'
    ed.options.set('scrollbarchar', '[]', local=eb.local_options)
    assert scrollbar_thumb_char(ed) == '['

    assert scrollbar_thumb_span(total_rows=4, start_row=0, window_rows=6) is None
    assert scrollbar_thumb_span(total_rows=12, start_row=0, window_rows=6) == (0, 3)
    assert scrollbar_thumb_span(total_rows=12, start_row=3, window_rows=6) == (2, 3)
    assert scrollbar_thumb_span(total_rows=12, start_row=6, window_rows=6) == (3, 3)



def test_render_scrollbar_marks_plain_viewport_thumb(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', ''.join(f'line {i:02d}\n' for i in range(12)))
    eb = ed.cur()
    eb.cursors[eb.primary].line = 8
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    thumb_rows = {
        y
        for y, x, s, attr in fake.calls
        if x == 19 and s == '|' and (attr & curses.A_REVERSE) and (attr & curses.A_DIM)
    }
    thumb = scrollbar_thumb_span(total_rows=len(eb.buf.lines), start_row=ed.viewport_model()['top_line'], window_rows=6)
    assert thumb is not None
    thumb_top, thumb_size = thumb
    assert thumb_rows == set(range(thumb_top, thumb_top + thumb_size))
    assert fake.cursor == (5, 0)


def test_render_scrollbar_uses_configured_thumb_char(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', ''.join(f'line {i:02d}\n' for i in range(12)))
    eb = ed.cur()
    eb.cursors[eb.primary].line = 8
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.options.set('scrollbarchar', '#', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    thumb_rows = {
        y
        for y, x, s, attr in fake.calls
        if x == 19 and s == '#' and (attr & curses.A_REVERSE) and (attr & curses.A_DIM)
    }
    thumb = scrollbar_thumb_span(total_rows=len(eb.buf.lines), start_row=ed.viewport_model()['top_line'], window_rows=6)
    assert thumb is not None
    thumb_top, thumb_size = thumb
    assert thumb_rows == set(range(thumb_top, thumb_top + thumb_size))



def test_render_scrollbar_tracks_softwrapped_visual_rows(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghijklmnopqrstuvwxyz' * 3 + '\n')
    eb = ed.cur()
    eb.cursors[eb.primary].col = 60
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=10)
    _render(fake, ed)

    total = ed._total_visual_rows(eb, w=9)
    start = ed._viewport_visual_start(eb, w=9)
    thumb = scrollbar_thumb_span(total_rows=total, start_row=start, window_rows=6)
    assert thumb is not None
    thumb_top, thumb_size = thumb
    thumb_rows = {
        y
        for y, x, s, attr in fake.calls
        if x == 9 and s == '|' and (attr & curses.A_REVERSE) and (attr & curses.A_DIM)
    }
    assert thumb_rows == set(range(thumb_top, thumb_top + thumb_size))



def test_render_scrollbar_also_marks_help_buffers(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('guide.md', ''.join(f'row {i:02d}\n' for i in range(20)))
    eb = ed.cur()
    eb.local_options['readonly'] = True
    eb.local_options['help_doc'] = 'guide'
    eb.cursors[eb.primary].line = 12
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    thumb_calls = [
        attr
        for y, x, s, attr in fake.calls
        if x == 19 and s == '|' and (attr & curses.A_REVERSE) and (attr & curses.A_DIM)
    ]
    assert thumb_calls
