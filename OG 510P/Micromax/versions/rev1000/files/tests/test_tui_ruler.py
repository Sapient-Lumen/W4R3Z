from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, line_number_gutter_text, line_number_gutter_width


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


def test_line_number_gutter_helpers_cover_absolute_relative_and_wrapped_rows() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\nbeta\ngamma\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 1
    ed.options.set('ruler', 'true', local=eb.local_options)

    gw = line_number_gutter_width(ed)
    assert gw == 2
    assert line_number_gutter_text(ed, line_index=0, wrap_start_col=0, gutter_width=gw) == '1 '
    assert line_number_gutter_text(ed, line_index=1, wrap_start_col=0, gutter_width=gw) == '2 '
    assert line_number_gutter_text(ed, line_index=1, wrap_start_col=3, gutter_width=gw) == '  '

    ed.options.set('relativeruler', 'true', local=eb.local_options)
    assert line_number_gutter_text(ed, line_index=0, wrap_start_col=0, gutter_width=gw) == '1 '
    assert line_number_gutter_text(ed, line_index=1, wrap_start_col=0, gutter_width=gw) == '2 '
    assert line_number_gutter_text(ed, line_index=2, wrap_start_col=0, gutter_width=gw) == '1 '


def test_render_ruler_shows_numbers_and_offsets_cursor(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\nbeta\ngamma\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 1
    eb.cursors[eb.primary].col = 2
    ed.options.set('ruler', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    assert fake.lines[0].startswith('1 alpha')
    assert fake.lines[1].startswith('2 beta')
    assert fake.lines[2].startswith('3 gamma')
    # gutter width 2 + cursor col 2
    assert fake.cursor == (1, 4)

    cur_num_calls = [attr for y, x, s, attr in fake.calls if y == 1 and x == 0 and s == '2 ']
    other_num_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == '1 ']
    assert cur_num_calls and any(attr & curses.A_BOLD for attr in cur_num_calls)
    assert other_num_calls and any(attr & curses.A_DIM for attr in other_num_calls)


def test_render_relative_ruler_and_blank_softwrap_continuations(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'abcdefghijklm\nsecond\nthird\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 1
    eb.cursors[eb.primary].col = 0
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('relativeruler', 'true', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=10)
    _render(fake, ed)

    assert fake.lines[0].startswith('1 abcdefgh')
    assert fake.lines[1].startswith('  ijklm')
    assert fake.lines[2].startswith('2 second')
    assert fake.lines[3].startswith('1 third')


def test_render_preserves_explicit_zero_screen_cursor(monkeypatch) -> None:
    """Terminal placement must not treat coordinate zero as a missing value."""

    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha\nbeta\n')
    model = ed.screen_model(lines=8, cols=20)
    model['cursor'] = {'mode': 'edit', 'screen_y': 0, 'screen_x': 0, 'visible': 1}
    model['edit_window']['cursor']['view_y'] = 3
    model['edit_window']['cursor']['view_x'] = 4
    monkeypatch.setattr(ed, 'screen_model', lambda *, lines, cols: model)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    assert fake.cursor == (0, 0)
