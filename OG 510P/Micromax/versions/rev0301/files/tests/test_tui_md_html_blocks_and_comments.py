from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render


class _CaptureStdScr:
    def __init__(self, *, h: int = 40, w: int = 120) -> None:
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


def test_help_render_dims_html_comment_spans(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    eb = ed.cur()
    eb.cursors[eb.primary].line = _line_index_of(ed, "Ghost inline comment link")
    eb.cursors[eb.primary].col = 0

    fake = _CaptureStdScr(h=90)
    _render(fake, ed)

    comment_calls = [attr for _y, _x, s, attr in fake.calls if 'Ghost inline comment link' in s]
    visible_calls = [attr for _y, _x, s, attr in fake.calls if 'Visible link before comment' in s]

    assert comment_calls and any(attr & curses.A_DIM for attr in comment_calls)
    assert visible_calls and any(attr & curses.A_UNDERLINE for attr in visible_calls)


def test_help_render_dims_inline_raw_html_tags(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    eb = ed.cur()

    eb.cursors[eb.primary].line = _line_index_of(ed, 'Press <kbd>Ctrl-b</kbd>')
    eb.cursors[eb.primary].col = 0
    fake = _CaptureStdScr(h=220)
    _render(fake, ed)
    raw_tag_calls = [attr for _y, _x, s, attr in fake.calls if '<kbd>' in s or '</kbd>' in s]
    assert raw_tag_calls and any(attr & curses.A_DIM for attr in raw_tag_calls)

    eb.cursors[eb.primary].line = _line_index_of(ed, '<a name="inline-raw-anchor"></a>')
    eb.cursors[eb.primary].col = 0
    fake = _CaptureStdScr(h=220)
    _render(fake, ed)
    anchor_calls = [attr for _y, _x, s, attr in fake.calls if '<a name="inline-raw-anchor">' in s or '</a>' in s]
    assert anchor_calls and any(attr & curses.A_DIM for attr in anchor_calls)

    eb.cursors[eb.primary].line = _line_index_of(ed, '<https://example.invalid/inline-autolink>')
    eb.cursors[eb.primary].col = 0
    fake = _CaptureStdScr(h=220)
    _render(fake, ed)
    autolink_calls = [attr for _y, _x, s, attr in fake.calls if 'example.invalid/inline-autolink' in s or s == '<']
    assert autolink_calls and any(attr & curses.A_BOLD for attr in autolink_calls)
    assert not any(attr & curses.A_DIM for attr in autolink_calls)

    eb.cursors[eb.primary].line = _line_index_of(ed, 'Visible link after inline raw HTML tags')
    eb.cursors[eb.primary].col = 0
    fake = _CaptureStdScr(h=220)
    _render(fake, ed)
    link_calls = [attr for _y, _x, s, attr in fake.calls if 'Visible link after inline raw HTML tags' in s]
    assert link_calls and any(attr & curses.A_UNDERLINE for attr in link_calls)


def test_help_render_dims_raw_html_block_lines(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    eb = ed.cur()
    eb.cursors[eb.primary].line = _line_index_of(ed, "<div>")
    eb.cursors[eb.primary].col = 0

    fake = _CaptureStdScr(h=220)
    _render(fake, ed)

    tag_calls = [attr for _y, _x, s, attr in fake.calls if s.strip() == '<div>']
    assert tag_calls and any(attr & curses.A_DIM for attr in tag_calls)

    eb.cursors[eb.primary].line = _line_index_of(ed, '[Ghost html block link](94-softwrap.md)')
    fake = _CaptureStdScr(h=220)
    _render(fake, ed)

    link_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if 'Ghost html block link' in s or '94-softwrap.md' in s
    ]
    assert link_calls and any(attr & curses.A_DIM for attr in link_calls)

    eb.cursors[eb.primary].line = _line_index_of(ed, "<widget-box data-kind=\"demo\">")
    eb.cursors[eb.primary].col = 0
    fake = _CaptureStdScr(h=220)
    _render(fake, ed)

    generic_tag_calls = [attr for _y, _x, s, attr in fake.calls if s.strip() == '<widget-box data-kind="demo">']
    assert generic_tag_calls and any(attr & curses.A_DIM for attr in generic_tag_calls)
