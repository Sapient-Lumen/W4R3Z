from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render


class _CaptureStdScr:
    def __init__(self, *, h: int = 14, w: int = 120) -> None:
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


def test_md_heading_line_roles_cover_atx_and_setext_lines() -> None:
    ed = Editor()
    roles = ed._md_heading_line_roles([
        '# Atx heading',
        'Multi-line',
        'setext heading',
        '---------------',
        'Single-line setext',
        '==================',
        'plain text',
    ])

    assert roles[0] == ('title', 1)
    assert roles[1] == ('title', 2)
    assert roles[2] == ('title', 2)
    assert roles[3] == ('underline', 2)
    assert roles[4] == ('title', 1)
    assert roles[5] == ('underline', 1)
    assert 6 not in roles


def test_help_render_styles_setext_title_lines_and_underline(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('multiline-setext-headings') is True

    fake = _CaptureStdScr(h=18, w=120)
    _render(fake, ed)

    title_calls = [attr for y, _x, s, attr in fake.calls if y == 0 and 'Multi-line' in s]
    cont_calls = [attr for y, _x, s, attr in fake.calls if y == 1 and 'setext headings demo' in s]
    underline_calls = [attr for y, _x, s, attr in fake.calls if y == 2 and '=' in s]

    assert title_calls and any(attr & curses.A_BOLD for attr in title_calls)
    assert cont_calls and any(attr & curses.A_BOLD for attr in cont_calls)
    assert underline_calls and any(attr & curses.A_DIM for attr in underline_calls)
