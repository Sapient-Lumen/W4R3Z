from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render, md_task_body_span, md_task_checkbox


def test_md_task_checkbox_accepts_common_gfm_task_list_forms() -> None:
    s1 = '- [ ] pending'
    s2 = '* [x] done'
    s3 = '  12. [X] numbered done'
    assert md_task_checkbox(s1) == (2, 5, False)
    assert md_task_checkbox(s2) == (2, 5, True)
    assert md_task_checkbox(s3) == (6, 9, True)



def test_md_task_checkbox_rejects_non_task_list_lines() -> None:
    assert md_task_checkbox('[ ] not a list item') is None
    assert md_task_checkbox('- [no] invalid') is None
    assert md_task_checkbox('- [ ]') == (2, 5, False)
    assert md_task_checkbox('plain text') is None



def test_md_task_body_span_returns_body_after_checkbox() -> None:
    s = '- [x] write docs'
    assert md_task_body_span(s) == (6, len(s))
    assert md_task_body_span('- [ ]') is None


def test_md_task_checkbox_can_opt_into_nested_source_view_mode() -> None:
    s1 = '    - [ ] nested pending'
    s2 = '        3. [x] nested done'
    assert md_task_checkbox(s1, max_leading_spaces=None) == (6, 9, False)
    assert md_task_checkbox(s2, max_leading_spaces=None) == (11, 14, True)
    assert md_task_body_span(s2, max_leading_spaces=None) == (15, len(s2))


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


def test_help_render_styles_nested_list_and_task_markers(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    eb = ed.cur()
    eb.cursors[eb.primary].line = _line_index_of(ed, 'nested bullet item')
    eb.cursors[eb.primary].col = 0

    fake = _CaptureStdScr(h=20, w=120)
    _render(fake, ed)

    bullet_row = next(y for y, text in fake.lines.items() if 'nested bullet item' in text)
    bullet_marker_calls = [attr for y, x, s, attr in fake.calls if y == bullet_row and x == 4 and s == '-']
    assert bullet_marker_calls and any(attr & curses.A_BOLD for attr in bullet_marker_calls)

    eb.cursors[eb.primary].line = _line_index_of(ed, 'nested finished task')
    eb.cursors[eb.primary].col = 0
    fake = _CaptureStdScr(h=20, w=120)
    _render(fake, ed)

    task_row = next(y for y, text in fake.lines.items() if 'nested finished task' in text)
    task_marker_calls = [attr for y, x, s, attr in fake.calls if y == task_row and x == 4 and s == '-']
    task_box_calls = [attr for y, x, s, attr in fake.calls if y == task_row and x == 6 and s == '[x]']

    assert task_marker_calls and any(attr & curses.A_BOLD for attr in task_marker_calls)
    assert task_box_calls and any(attr & curses.A_BOLD for attr in task_box_calls)
    assert any((call[3] & curses.A_DIM) for call in fake.calls if call[0] == task_row and 'nested finished task' in call[2])
