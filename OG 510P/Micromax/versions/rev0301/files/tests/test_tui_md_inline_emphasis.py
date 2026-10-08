from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import (
    _render,
    md_emphasis_spans,
    md_inline_markup_delimiter_spans,
    md_inline_markup_matches,
    md_strikethrough_spans,
    md_strong_spans,
)


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


def test_md_strong_spans_accept_common_star_and_underscore_forms() -> None:
    s1 = 'alpha **strong** omega'
    s2 = 'alpha __strong__ omega'
    assert md_strong_spans(s1) == [(8, 14)]
    assert md_strong_spans(s2) == [(8, 14)]



def test_md_emphasis_spans_accept_common_star_and_underscore_forms() -> None:
    s1 = 'alpha *soft* omega'
    s2 = 'alpha _soft_ omega'
    assert md_emphasis_spans(s1) == [(7, 11)]
    assert md_emphasis_spans(s2) == [(7, 11)]



def test_md_strikethrough_spans_accept_common_gfm_form() -> None:
    s = 'alpha ~~gone~~ omega'
    assert md_strikethrough_spans(s) == [(8, 12)]



def test_inline_markup_helpers_ignore_escaped_code_and_word_internal_underscore() -> None:
    assert md_emphasis_spans(r'alpha \*nope* omega') == []
    assert md_emphasis_spans('alpha foo_bar_baz omega') == []
    assert md_strong_spans('alpha `**code**` omega') == []
    assert md_strikethrough_spans('alpha `~~code~~` omega') == []



def test_md_emphasis_spans_do_not_reparse_inside_strong_or_strike() -> None:
    assert md_emphasis_spans('alpha __strong__ omega') == []
    assert md_emphasis_spans('alpha ~~gone~~ omega') == []
    s = 'alpha **strong** and *soft* and ~~gone~~ omega'
    assert md_emphasis_spans(s) == [(22, 26)]


def test_inline_markup_helpers_ignore_multi_backtick_code_spans() -> None:
    assert md_strong_spans('alpha ``**code**`` omega') == []
    assert md_emphasis_spans('alpha ``*code*`` omega') == []
    assert md_strikethrough_spans('alpha ``~~code~~`` omega') == []


def test_md_inline_markup_delimiter_spans_cover_common_visible_tokens() -> None:
    s = 'alpha **strong** and *soft* and _also_ and ~~gone~~ omega'
    parts = [s[a:b] for a, b in md_inline_markup_delimiter_spans(s)]
    assert parts == ['**', '**', '*', '*', '_', '_', '~~', '~~']


def test_md_inline_markup_delimiter_spans_ignore_escaped_and_code_tokens() -> None:
    s = r'alpha \*ghost* and `*code*` and ``~~code~~`` and **strong** omega'
    parts = [s[a:b] for a, b in md_inline_markup_delimiter_spans(s)]
    assert '*' not in parts
    assert '~~' not in parts
    assert parts == ['**', '**']


def test_help_render_dims_inline_markup_delimiters_while_styling_bodies(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    italic_attr = int(getattr(curses, 'A_ITALIC', 0) or curses.A_UNDERLINE)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True
    eb = ed.cur()

    def _render_line(needle: str) -> _CaptureStdScr:
        eb.cursors[eb.primary].line = _line_index_of(ed, needle)
        eb.cursors[eb.primary].col = 0
        fake = _CaptureStdScr(h=220, w=120)
        _render(fake, ed)
        return fake

    strong_fake = _render_line('**strong delimiter cue**')
    strong_delims = [attr for _y, _x, s, attr in strong_fake.calls if s == '**']
    strong_body = [attr for _y, _x, s, attr in strong_fake.calls if s == 'strong delimiter cue']
    assert strong_delims and all(attr & curses.A_DIM for attr in strong_delims)
    assert strong_body and any(attr & curses.A_BOLD for attr in strong_body)

    em_fake = _render_line('*emphasis delimiter cue*')
    em_delims = [attr for _y, _x, s, attr in em_fake.calls if s == '*']
    em_body = [attr for _y, _x, s, attr in em_fake.calls if 'emphasis delimiter cue' in s]
    assert em_delims and all(attr & curses.A_DIM for attr in em_delims)
    assert em_body and any(attr & italic_attr for attr in em_body)

    under_fake = _render_line('_underscore delimiter cue_')
    under_delims = [attr for _y, _x, s, attr in under_fake.calls if s == '_']
    under_body = [attr for _y, _x, s, attr in under_fake.calls if 'underscore delimiter cue' in s]
    assert under_delims and all(attr & curses.A_DIM for attr in under_delims)
    assert under_body and any(attr & italic_attr for attr in under_body)

    strike_fake = _render_line('~~strike delimiter cue~~')
    strike_delims = [attr for _y, _x, s, attr in strike_fake.calls if s == '~~']
    strike_body = [attr for _y, _x, s, attr in strike_fake.calls if 'strike delimiter cue' in s]
    assert strike_delims and all(attr & curses.A_DIM for attr in strike_delims)
    assert strike_body and all(attr & curses.A_DIM for attr in strike_body)



def test_md_inline_markup_matches_surface_kind_delimiter_and_text() -> None:
    s = 'alpha **strong** and *soft* and _also_ and ~~gone~~ omega'
    parts = md_inline_markup_matches(s)
    assert [(m.kind, m.delimiter, m.text) for m in parts] == [
        ('strong', '**', 'strong'),
        ('emphasis', '*', 'soft'),
        ('emphasis', '_', 'also'),
        ('strike', '~~', 'gone'),
    ]
    assert [m.delimiter_length for m in parts] == [2, 1, 1, 2]


def test_md_inline_markup_matches_ignore_code_and_nested_reparse() -> None:
    s = 'alpha `**code**` and **strong** and ~~gone~~ and *soft* omega'
    parts = md_inline_markup_matches(s)
    assert [(m.kind, m.text) for m in parts] == [
        ('strong', 'strong'),
        ('strike', 'gone'),
        ('emphasis', 'soft'),
    ]
