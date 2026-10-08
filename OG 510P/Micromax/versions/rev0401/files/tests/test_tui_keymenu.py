from __future__ import annotations

import curses

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.tui import _render, capture_prompt_text, constantshow_text, infobar_text, keymenu_text


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


def test_keymenu_text_uses_default_editor_shortcuts() -> None:
    ed = Editor()
    got = keymenu_text(ed, width=120)
    assert '^Q Quit' in got
    assert '^S Save' in got
    assert '^G Help' in got




def test_keymenu_text_switches_to_capture_help_for_qreplace() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'one two three\n')

    assert ed.begin_query_replace('one', 'X', literal=True) is True

    got = keymenu_text(ed, width=120)
    assert 'Y/Enter Replace' in got
    assert 'A All' in got
    assert 'Q/Esc Quit' in got


def test_capture_prompt_text_summarizes_qreplace_session() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'one two one\n')

    assert ed.begin_query_replace('one', 'X', literal=True) is True

    got = capture_prompt_text(ed, width=120)
    assert got == ed.interaction_model(120)['text']
    assert got.startswith('?replace [1/2]')
    assert 'one -> X' in got


def test_capture_prompt_text_summarizes_openurl_confirmation() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'look https://example.invalid\n')
    eb = ed.cur()
    ed.options.set('cap.open-url', 'true')

    assert ed.begin_open_url_confirm('https://example.invalid/demo', source='help') is True

    got = capture_prompt_text(ed, width=120)
    assert got == ed.interaction_model(120)['text']
    assert got.startswith('?open external link from help')
    assert 'https://example.invalid/demo' in got

def test_constantshow_text_reports_line_column_and_percentage() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\n')
    eb = ed.cur()
    eb.cursors[0].line = 2
    eb.cursors[0].col = 1

    assert constantshow_text(ed) == 'Ln 3/5, Col 2 (50%)'


def test_infobar_text_can_right_align_constantshow_summary_without_message() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\n')
    eb = ed.cur()
    ed.options.set('constantshow', 'true', local=eb.local_options)

    got = infobar_text(ed, width=32)
    assert got.endswith('Ln 1/4, Col 1 (0%)')
    assert len(got) == 32


def test_keymenu_text_switches_to_prompt_help_for_picker_sessions() -> None:
    ed = Editor()
    p = Prompt(kind='palette')
    rows = [
        ['open README.md', 'openpath', 'README.md', 'Files'],
        ['open TODO.md', 'openpath', 'TODO.md', 'Files'],
    ]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    ed.prompt = p

    got = keymenu_text(ed, width=120)
    assert 'Enter Choose' in got
    assert 'PgUp/PgDn Page' in got
    assert 'Alt-Up/Down Section' in got


def test_render_keymenu_draws_extra_bottom_row_and_shrinks_view(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('keymenu', 'true', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=40)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 5
    assert fake.lines[5].startswith('^Q Quit')
    assert fake.lines[6] == ''


def test_render_infobar_false_reclaims_idle_message_row(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.message('saved')

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 7
    assert fake.lines[6].startswith('seven')
    assert 'saved' not in fake.lines.get(6, '')


def test_render_constantshow_populates_idle_infobar_right_side(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('constantshow', 'true', local=eb.local_options)
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.message('saved')

    fake = _CaptureStdScr(h=8, w=40)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 7
    assert fake.lines[7].startswith('saved')
    assert fake.lines[7].endswith('Ln 1/5, Col 1 (0%)')


def test_render_still_shows_prompt_when_infobar_is_disabled(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    p = Prompt(kind='command')
    p.text = 'open README.md'
    p.cursor = len(p.text)
    ed.prompt = p

    fake = _CaptureStdScr(h=8, w=40)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 6
    assert fake.lines[6].startswith(':open README.md')
    assert fake.lines[6] == ed.status_model()['interaction_line']
    assert fake.cursor == (6, 15)


def test_render_prompt_row_does_not_append_constantshow_when_prompt_active(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('constantshow', 'true', local=eb.local_options)
    p = Prompt(kind='command')
    p.text = 'open README.md'
    p.cursor = len(p.text)
    ed.prompt = p

    fake = _CaptureStdScr(h=8, w=40)
    _render(fake, ed)

    assert fake.lines[6].startswith(':open README.md')
    assert 'Ln ' not in fake.lines[6]




def test_render_capture_mode_shows_qreplace_prompt_even_when_infobar_is_disabled(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one two one\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    assert ed.begin_query_replace('one', 'X', literal=True) is True

    fake = _CaptureStdScr(h=8, w=60)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 6
    assert fake.lines[6].startswith('?replace [1/2]')
    assert fake.lines[6] == ed.status_model()['interaction_line']
    assert 'one -> X' in fake.lines[6]


def test_render_capture_mode_shows_openurl_prompt_and_keymenu(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'look https://example.invalid\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('cap.open-url', 'true')
    ed.options.set('keymenu', 'true', local=eb.local_options)

    assert ed.begin_open_url_confirm('https://example.invalid/demo', source='cursor') is True

    fake = _CaptureStdScr(h=8, w=70)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 5
    assert fake.lines[5].startswith('Y/Enter Open')
    assert fake.lines[6].startswith('?open external link under cursor')
    assert 'https://example.invalid/demo' in fake.lines[6]

def test_render_statusline_false_reclaims_bottom_row_when_no_other_bottom_chrome(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    fake = _CaptureStdScr(h=8, w=20)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 8
    assert fake.lines[7].startswith('eight')


def test_render_statusline_false_still_keeps_prompt_on_bottom_row(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    p = Prompt(kind='command')
    p.text = 'open README.md'
    p.cursor = len(p.text)
    ed.prompt = p

    fake = _CaptureStdScr(h=8, w=40)
    _render(fake, ed)

    assert ed.viewport_model()['height'] == 7
    assert fake.lines[7].startswith(':open README.md')
    assert fake.cursor == (7, 15)
