from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, overflow_marker_cells


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


def test_overflow_marker_cells_cover_right_left_both_softwrap_and_one_cell_cases() -> None:
    assert overflow_marker_cells(line_text='abcdef', frag_start=0, view_width=4, softwrap=False) == [(3, '>')]
    assert overflow_marker_cells(line_text='abcdef', frag_start=2, view_width=4, softwrap=False) == [(0, '<')]
    assert overflow_marker_cells(line_text='abcdefghij', frag_start=2, view_width=4, softwrap=False) == [(0, '<'), (3, '>')]
    assert overflow_marker_cells(line_text='abcdefghij', frag_start=2, view_width=4, softwrap=True) == []
    assert overflow_marker_cells(line_text='abcdefghij', frag_start=2, view_width=1, softwrap=False) == [(0, '>')]



def test_render_overflowmarkers_marks_plain_right_clipping(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghij\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=6)
    _render(fake, ed)

    marker_calls = [
        attr
        for y, x, s, attr in fake.calls
        if y == 0 and x == 5 and s == '>'
    ]
    assert marker_calls and any((attr & curses.A_BOLD) and (attr & curses.A_DIM) for attr in marker_calls)



def test_render_overflowmarkers_match_shared_display_rows_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghijklmno\n')
    eb = ed.cur()
    eb.cursors[eb.primary].col = 6
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)

    screen = ed.screen_model(8, 6)
    row0 = next(row for row in screen['display_rows']['rows'] if row['kind'] == 'viewport')
    fake = _CaptureStdScr(h=8, w=6)
    _render(fake, ed)

    assert row0['text'] == fake.lines[0]
    assert row0['overflow_cells'] == [[0, '<'], [5, '>']]



def test_render_overflowmarkers_marks_horizontal_scroll_both_sides(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghijklmno\n')
    eb = ed.cur()
    eb.cursors[eb.primary].col = 6
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=6)
    _render(fake, ed)

    vp = ed.viewport_model()
    cells = overflow_marker_cells(
        line_text='abcdefghijklmno',
        frag_start=int(vp['left_col']),
        view_width=6,
        softwrap=False,
    )
    seen = {
        (x, s)
        for y, x, s, attr in fake.calls
        if y == 0 and (attr & curses.A_BOLD) and (attr & curses.A_DIM) and s in {'<', '>'}
    }
    assert seen == {(int(x), ch) for x, ch in cells}



def test_render_overflowmarkers_also_marks_help_buffers(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('guide.md', 'abcdefghij\n')
    eb = ed.cur()
    eb.local_options['readonly'] = True
    eb.local_options['help_doc'] = 'guide'
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=6)
    _render(fake, ed)

    marker_calls = [
        attr
        for y, x, s, attr in fake.calls
        if y == 0 and x == 5 and s == '>'
    ]
    assert marker_calls and any((attr & curses.A_BOLD) and (attr & curses.A_DIM) for attr in marker_calls)



def test_render_overflowmarkers_are_suppressed_under_softwrap(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghijklmno\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=6)
    _render(fake, ed)

    marker_calls = [
        (y, x, s)
        for y, x, s, attr in fake.calls
        if (attr & curses.A_BOLD) and (attr & curses.A_DIM) and s in {'<', '>'}
    ]
    assert marker_calls == []
