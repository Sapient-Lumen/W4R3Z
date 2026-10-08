from __future__ import annotations

import curses

from micromax_editor.editor import Editor, md_indented_code_line_flags
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


def test_md_indented_code_line_flags_mark_blank_separated_runs() -> None:
    flags = md_indented_code_line_flags([
        'paragraph',
        '',
        '    code one',
        '    code two',
        '',
        '\tcode tab',
        'after',
        '- bullet',
        '    wrapped continuation, not a fresh code block',
    ])

    assert flags == [False, False, True, True, True, True, False, False, False]


def test_help_render_dims_indented_codeish_lines(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('indented-codeish-markdown') is True

    fake = _CaptureStdScr(h=40, w=120)
    _render(fake, ed)

    ref_calls = [attr for _y, _x, s, attr in fake.calls if '[ghost-four-space-ref]: 94-softwrap.md' in s]
    inline_calls = [attr for _y, _x, s, attr in fake.calls if '[Ghost indented inline link](94-softwrap.md)' in s]

    assert ref_calls and any(attr & curses.A_DIM for attr in ref_calls)
    assert inline_calls and any(attr & curses.A_DIM for attr in inline_calls)
