from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, md_escaped_markdown_token_spans


class _CaptureStdScr:
    def __init__(self, *, h: int = 120, w: int = 120) -> None:
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


def _line_index_of(ed: Editor, needle: str) -> int:
    for i, ln in enumerate(ed.cur().buf.lines):
        if needle in str(ln):
            return i
    raise AssertionError(f"needle not found: {needle}")


def test_md_escaped_markdown_token_spans_cover_literal_markdown_escape_pairs() -> None:
    s = r'literal \[link](doc.md) and \<https://example.invalid/> and \*stars\* and `\\[code]`'
    parts = [s[a:b] for a, b in md_escaped_markdown_token_spans(s)]
    assert parts == [r'\[', r'\<', r'\*', r'\*']


def test_md_escaped_markdown_token_spans_ignore_double_backslashes_and_non_markdown_escapes() -> None:
    s = r'literal \\[not-cued] and \\. and \ n'
    parts = [s[a:b] for a, b in md_escaped_markdown_token_spans(s)]
    assert parts == []


def test_help_render_dims_escaped_markdown_pairs(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    eb = ed.cur()

    ed.options.set('cursorline', 'false')

    def _render_line(needle: str) -> _CaptureStdScr:
        eb.cursors[eb.primary].line = _line_index_of(ed, needle)
        eb.cursors[eb.primary].col = 0
        fake = _CaptureStdScr(h=220, w=120)
        _render(fake, ed)
        return fake

    fake = _render_line(r'\[Literal inline link](00-vision.md)')
    escaped_link_openers = [
        attr
        for _y, _x, s, attr in fake.calls
        if s == r'\['
    ]
    assert escaped_link_openers and all((attr & curses.A_DIM) and not (attr & curses.A_BOLD) for attr in escaped_link_openers)
    assert not any(attr & curses.A_UNDERLINE for _y, _x, s, attr in fake.calls if 'Literal inline link' in s)

    auto_fake = _render_line(r'\<https://example.invalid/escaped-help-autolink>')
    escaped_autolink_openers = [
        attr
        for _y, _x, s, attr in auto_fake.calls
        if s == r'\<'
    ]
    assert escaped_autolink_openers and all((attr & curses.A_DIM) and not (attr & curses.A_BOLD) for attr in escaped_autolink_openers)
