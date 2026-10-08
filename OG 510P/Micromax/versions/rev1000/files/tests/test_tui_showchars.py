from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, parse_showchars_option, render_showchars_fragment


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


def test_parse_showchars_option_keeps_supported_keys_only() -> None:
    got = parse_showchars_option('tab=>,space=.,itab=|>,ispace=|,bogus=x,noeq')
    assert got == {
        'tab': '>',
        'space': '.',
        'itab': '|>',
        'ispace': '|',
    }


def test_render_showchars_fragment_uses_indent_overrides_and_keeps_softwrap_prefix_plain() -> None:
    shown, spans = render_showchars_fragment(
        '\t a\tb',
        frag_start=0,
        frag_text='\t a\tb',
        spec={'tab': '>', 'space': '.', 'itab': '|>', 'ispace': ':'},
    )
    assert shown == '|:a>b'
    assert spans == [(0, 1), (1, 2), (3, 4)]

    shown2, spans2 = render_showchars_fragment(
        'abcdefghij',
        frag_start=6,
        frag_text='  ghij',
        spec={'space': '.'},
    )
    assert shown2 == '  ghij'
    assert spans2 == []


def test_render_showchars_replaces_visible_spaces_and_tabs_in_editor_rows(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'a b\tc\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('showchars', 'space=.,tab=>', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    assert fake.lines[0].startswith('a.b>c')
    showchar_calls = [attr for y, x, s, attr in fake.calls if y == 0 and s in {'.', '>'}]
    assert showchar_calls and all(attr & curses.A_DIM for attr in showchar_calls)



def test_render_showchars_matches_shared_showchars_rows_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', '\t a\tb\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('showchars', 'tab=>,space=.,itab=|>,ispace=:', local=eb.local_options)

    screen = ed.screen_model(8, 20)
    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    row0 = screen['showchars_rows']['rows'][0]
    assert row0['display_text'] == '|:a>b'
    assert fake.lines[0].startswith(str(row0['display_text']))


def test_render_showchars_also_applies_in_help_buffers(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('guide.md', 'a b\n')
    eb = ed.cur()
    eb.local_options['readonly'] = True
    eb.local_options['help_doc'] = 'guide'
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('showchars', 'space=.', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    assert fake.lines[0].startswith('a.b')
