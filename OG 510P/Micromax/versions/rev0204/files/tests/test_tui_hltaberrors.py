from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, tab_error_spans


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


def test_tab_error_spans_follow_tabstospaces_policy_and_fragment_intersection() -> None:
    assert tab_error_spans('\talpha', tabstospaces=True) == [(0, 1)]
    assert tab_error_spans('ab\tcd', tabstospaces=True, frag_start=2, frag_text='\t') == [(0, 1)]
    assert tab_error_spans('  \talpha', tabstospaces=False) == [(0, 2)]
    assert tab_error_spans('\t  alpha', tabstospaces=False, frag_start=1, frag_text='  ') == [(0, 2)]
    assert tab_error_spans('alpha  beta', tabstospaces=False) == []



def test_render_hltaberrors_marks_tabs_when_tabstospaces_is_true(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', '\talpha\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('hltaberrors', 'true', local=eb.local_options)
    ed.options.set('tabstospaces', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    tab_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == '\t']
    alpha_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 1 and s == 'alpha']

    assert tab_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in tab_calls)
    assert alpha_calls and all(not (attr & curses.A_REVERSE) for attr in alpha_calls)



def test_render_hltaberrors_marks_indent_spaces_when_tabs_are_expected(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', '  \talpha\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('hltaberrors', 'true', local=eb.local_options)
    ed.options.set('tabstospaces', 'false', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    space_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == '  ']
    tab_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 2 and s == '\talpha']

    assert space_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in space_calls)
    assert tab_calls and all(not (attr & curses.A_REVERSE) for attr in tab_calls)


def test_render_hltaberrors_also_marks_help_buffer_fragments(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('guide.md', '  \talpha\n')
    eb = ed.cur()
    eb.local_options['readonly'] = True
    eb.local_options['help_doc'] = 'guide'
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('hltaberrors', 'true', local=eb.local_options)
    ed.options.set('tabstospaces', 'false', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    space_calls = [attr for y, x, s, attr in fake.calls if y == 0 and x == 0 and s == '  ']
    assert space_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in space_calls)
