from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, md_blockquote_alert_marker, md_blockquote_body_span, md_blockquote_prefix


def test_md_blockquote_prefix_accepts_common_quote_forms() -> None:
    assert md_blockquote_prefix('> quote') == (0, 2, 1)
    assert md_blockquote_prefix('  > > nested') == (2, 6, 2)
    assert md_blockquote_prefix('>> dense') == (0, 3, 2)
    assert md_blockquote_prefix('>') == (0, 1, 1)



def test_md_blockquote_prefix_rejects_non_quote_lines() -> None:
    assert md_blockquote_prefix('plain text') is None
    assert md_blockquote_prefix('>_< smiley') is None
    assert md_blockquote_prefix('    > code-ish indent') is None



def test_md_blockquote_body_span_returns_text_after_prefix() -> None:
    s = '  > quoted text'
    assert md_blockquote_body_span(s) == (4, len(s))
    assert md_blockquote_body_span('>') is None


def test_md_blockquote_alert_marker_accepts_common_github_alert_markers() -> None:
    assert md_blockquote_alert_marker('> [!NOTE]') == (2, 9, 'note')
    assert md_blockquote_alert_marker('> [!TIP] handy hint') == (2, 8, 'tip')
    assert md_blockquote_alert_marker('  > > [!WARNING] careful') == (6, 16, 'warning')


def test_md_blockquote_alert_marker_rejects_plain_quotes_and_unknown_markers() -> None:
    assert md_blockquote_alert_marker('> ordinary quote') is None
    assert md_blockquote_alert_marker('> [!MAYBE] nope') is None
    assert md_blockquote_alert_marker('plain [!NOTE] text') is None


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
    raise AssertionError(f'needle not found: {needle}')


def test_help_render_styles_github_alert_marker_inside_blockquote(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    eb = ed.cur()
    eb.cursors[eb.primary].line = _line_index_of(ed, '[!NOTE]')
    eb.cursors[eb.primary].col = 0

    fake = _CaptureStdScr(h=20, w=120)
    _render(fake, ed)

    alert_row = next(y for y, text in fake.lines.items() if '[!NOTE]' in text)
    quote_prefix_calls = [attr for y, x, s, attr in fake.calls if y == alert_row and x == 0 and s == '> ']
    alert_marker_calls = [attr for y, x, s, attr in fake.calls if y == alert_row and s == '[!NOTE]']

    assert quote_prefix_calls and any(attr & curses.A_BOLD for attr in quote_prefix_calls)
    assert alert_marker_calls and any((attr & curses.A_BOLD) and (attr & curses.A_DIM) for attr in alert_marker_calls)
