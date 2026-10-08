from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render


class _CaptureStdScr:
    def __init__(self, *, h: int = 16, w: int = 120) -> None:
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


def test_md_fenced_code_line_roles_distinguish_fence_and_body_lines() -> None:
    ed = Editor()
    roles = ed._md_fenced_code_line_roles([
        'plain text',
        '```text',
        'set cap.open-url true',
        '```',
        'after',
        '~~~json',
        '{"ok": true}',
        '~~~',
    ])

    assert roles == {
        1: 'fence',
        2: 'body',
        3: 'fence',
        5: 'fence',
        6: 'body',
        7: 'fence',
    }


def test_help_render_dims_fenced_code_bodies_and_bolds_fence_lines(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    fake = _CaptureStdScr(h=40, w=120)
    _render(fake, ed)

    fence_row = next(y for y, line in fake.lines.items() if '```text' in line)
    body_row = next(y for y, line in fake.lines.items() if 'set cap.open-url true' in line)
    close_row = next(y for y, line in fake.lines.items() if y > fence_row and line.strip() == '```')

    fence_calls = [attr for y, _x, s, attr in fake.calls if y == fence_row and '```text' in s]
    body_calls = [attr for y, _x, s, attr in fake.calls if y == body_row and 'set cap.open-url true' in s]
    close_calls = [attr for y, _x, s, attr in fake.calls if y == close_row and '```' in s]

    assert fence_calls and any((attr & curses.A_BOLD) and (attr & curses.A_DIM) for attr in fence_calls)
    assert body_calls and any(attr & curses.A_DIM for attr in body_calls)
    assert close_calls and any((attr & curses.A_BOLD) and (attr & curses.A_DIM) for attr in close_calls)
