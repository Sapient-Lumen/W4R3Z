from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, search_match_spans


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


def test_search_match_spans_cover_literal_and_regex_cases() -> None:
    assert search_match_spans('Alpha beta ALPHA', 'alpha', literal=True, case_sensitive=False) == [(0, 5), (11, 16)]
    assert search_match_spans('a1 b22 c333', r'\d+', literal=False, case_sensitive=True) == [(1, 2), (4, 6), (8, 11)]
    assert search_match_spans('abc', '(', literal=False) == []



def test_render_hlsearch_marks_visible_matches_and_current_match(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha beta alpha\nsecond alpha\n')
    eb = ed.cur()
    ed.options.set('hlsearch', 'true', local=eb.local_options)

    assert ed.find('ALPHA') is True
    fake = _CaptureStdScr(h=8, w=30)
    _render(fake, ed)

    assert fake.lines[0].startswith('alpha beta alpha')
    current_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == 'alpha']
    later_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 11 and s == 'alpha']
    second_row_calls = [attr for y, x, s, attr in fake.calls if y == 1 and x == 7 and s == 'alpha']

    assert current_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_BOLD) for attr in current_calls)
    assert later_calls and any((attr & curses.A_REVERSE) and not (attr & curses.A_BOLD) for attr in later_calls)
    assert second_row_calls and any((attr & curses.A_REVERSE) and not (attr & curses.A_BOLD) for attr in second_row_calls)


def test_render_find_prompt_shows_search_position_summary(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha beta alpha\nsecond alpha\n')

    ed.enter_prompt('find')
    assert ed.set_prompt_text('alpha') is True

    fake = _CaptureStdScr(h=8, w=40)
    _render(fake, ed)

    assert '[1/3]' in fake.lines[6]


def test_render_statusline_shows_search_position_summary_when_search_is_active(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha beta alpha\nsecond alpha\n')
    assert ed.find('alpha') is True

    fake = _CaptureStdScr(h=8, w=80)
    _render(fake, ed)

    assert '[1/3]' in fake.lines[7]
