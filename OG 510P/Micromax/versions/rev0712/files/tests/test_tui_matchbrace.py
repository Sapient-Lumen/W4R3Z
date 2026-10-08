from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, brace_match_attr, brace_match_spans, matching_brace_positions


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


def test_matching_brace_positions_support_direct_and_left_of_cursor_matching() -> None:
    lines = ['a(b[c]d)e']
    assert matching_brace_positions(lines, line=0, col=3, match_left=True) == [(0, 3), (0, 5)]
    assert matching_brace_positions(['(abc)'], line=0, col=1, match_left=False) == []
    assert matching_brace_positions(['(abc)'], line=0, col=1, match_left=True) == [(0, 0), (0, 4)]


def test_brace_match_spans_intersects_visible_fragment() -> None:
    spans = brace_match_spans(
        line_index=0,
        frag_start=4,
        frag_text='cd)e',
        brace_positions=[(0, 0), (0, 6)],
    )
    assert spans == [(2, 3)]


def test_render_matchbrace_marks_visible_pair_in_plain_buffer(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'a(b[c]d)e\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 0
    eb.cursors[eb.primary].col = 3
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('matchbrace', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    open_calls = [attr for y, x, s, attr in fake.calls if y == 0 and s == '[']
    close_calls = [attr for y, x, s, attr in fake.calls if y == 0 and s == ']']
    assert open_calls and any((attr & curses.A_UNDERLINE) and (attr & curses.A_BOLD) for attr in open_calls)
    assert close_calls and any((attr & curses.A_UNDERLINE) and (attr & curses.A_BOLD) for attr in close_calls)


def test_render_matchbrace_also_marks_help_buffers(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('guide.md', 'Call `demo(x)` here.\n')
    eb = ed.cur()
    eb.local_options['readonly'] = True
    eb.local_options['help_doc'] = 'guide'
    eb.cursors[eb.primary].line = 0
    eb.cursors[eb.primary].col = 10
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('matchbrace', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=30)
    _render(fake, ed)

    paren_calls = [attr for y, x, s, attr in fake.calls if y == 0 and s in {'(', ')'}]
    assert paren_calls and any((attr & curses.A_UNDERLINE) and (attr & curses.A_BOLD) for attr in paren_calls)


def test_brace_match_attr_honors_matchbracestyle(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', '()\n')
    eb = ed.cur()
    ed.options.set('matchbracestyle', 'underline', local=eb.local_options)
    assert brace_match_attr(ed, local_options=eb.local_options) == int(curses.A_BOLD | curses.A_UNDERLINE)
    ed.options.set('matchbracestyle', 'highlight', local=eb.local_options)
    assert brace_match_attr(ed, local_options=eb.local_options) == int(curses.A_BOLD | curses.A_REVERSE)


def test_render_matchbrace_highlight_style_uses_reverse_not_underline(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'a(b[c]d)e\n')
    eb = ed.cur()
    eb.cursors[eb.primary].line = 0
    eb.cursors[eb.primary].col = 3
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('matchbrace', 'true', local=eb.local_options)
    ed.options.set('matchbracestyle', 'highlight', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    open_calls = [attr for y, x, s, attr in fake.calls if y == 0 and s == '[']
    close_calls = [attr for y, x, s, attr in fake.calls if y == 0 and s == ']']
    assert open_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_BOLD) and not (attr & curses.A_UNDERLINE) for attr in open_calls)
    assert close_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_BOLD) and not (attr & curses.A_UNDERLINE) for attr in close_calls)
