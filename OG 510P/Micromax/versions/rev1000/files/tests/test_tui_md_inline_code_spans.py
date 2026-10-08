from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, md_inline_code_delimiter_spans, md_inline_code_spans


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


def test_md_inline_code_spans_basic_multiple() -> None:
    s = "alpha `code` beta `more`"
    spans = md_inline_code_spans(s)
    # inside spans (excluding backticks)
    assert spans == [(7, 11), (19, 23)]


def test_md_inline_code_spans_ignores_fences_and_escapes() -> None:
    assert md_inline_code_spans("```python") == []
    assert md_inline_code_spans("\\`notcode`") == []


def test_md_inline_code_spans_support_equal_length_backtick_runs() -> None:
    s = 'alpha ``code `with tick` `` omega'
    spans = md_inline_code_spans(s)
    assert spans == [(8, 25)]


def test_md_inline_code_spans_can_skip_unmatched_run_and_find_later_match() -> None:
    s = 'alpha ``oops and then `ok` omega'
    spans = md_inline_code_spans(s)
    assert spans == [(23, 25)]


def test_md_inline_code_delimiter_spans_cover_simple_and_multi_backtick_tokens() -> None:
    s = 'alpha `code` and ``more `ticks` here`` omega'
    parts = [s[a:b] for a, b in md_inline_code_delimiter_spans(s)]
    assert parts == ['`', '`', '``', '``']


def test_md_inline_code_delimiter_spans_ignore_escaped_and_unmatched_runs() -> None:
    s = r'alpha \`ghost` and ``oops and then `ok` omega'
    parts = [s[a:b] for a, b in md_inline_code_delimiter_spans(s)]
    assert parts == ['`', '`']


def test_help_render_bolds_and_dims_inline_code_delimiters(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    eb = ed.cur()

    def _render_line(needle: str) -> _CaptureStdScr:
        eb.cursors[eb.primary].line = _line_index_of(ed, needle)
        eb.cursors[eb.primary].col = 0
        fake = _CaptureStdScr(h=4, w=120)
        _render(fake, ed)
        return fake

    simple_fake = _render_line('`simple code`')
    simple_delims = [attr for _y, _x, s, attr in simple_fake.calls if s == '`']
    simple_body = [attr for _y, _x, s, attr in simple_fake.calls if s == 'simple code']
    assert simple_delims and all((attr & curses.A_DIM) and (attr & curses.A_BOLD) for attr in simple_delims)
    assert simple_body and all((attr & curses.A_DIM) and not (attr & curses.A_BOLD) for attr in simple_body)

    multi_fake = _render_line('``code with `literal backticks` inside``')
    multi_delims = [attr for _y, _x, s, attr in multi_fake.calls if s == '``']
    multi_body = [attr for _y, _x, s, attr in multi_fake.calls if s == 'code with `literal backticks` inside']
    assert multi_delims and all((attr & curses.A_DIM) and (attr & curses.A_BOLD) for attr in multi_delims)
    assert multi_body and all((attr & curses.A_DIM) and not (attr & curses.A_BOLD) for attr in multi_body)
