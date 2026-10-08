from __future__ import annotations

import curses

from micromax_editor.editor import Editor
from micromax_editor.tui import _render


class _CaptureStdScr:
    def __init__(self, *, h: int = 80, w: int = 120) -> None:
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


def test_md_definition_line_roles_dim_reference_and_footnote_definitions(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    fake = _CaptureStdScr(h=220, w=120)
    _render(fake, ed)

    ref_marker_calls = [attr for _y, _x, s, attr in fake.calls if s == '[space-path-doc-multiline]:']
    ref_cont_calls = [attr for _y, _x, s, attr in fake.calls if s == '  103-space\\ path.md' and (attr & curses.A_DIM)]

    assert ref_marker_calls and any((attr & curses.A_DIM) and (attr & curses.A_BOLD) for attr in ref_marker_calls)
    assert ref_cont_calls

    eb = ed.cur()
    eb.cursors[eb.primary].line = max(0, len(eb.buf.lines) - 1)
    eb.cursors[eb.primary].col = 0

    fake = _CaptureStdScr(h=220, w=120)
    _render(fake, ed)
    foot_marker_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if s.startswith('[^help-footnote]:') or s.startswith('[^help-footnote-more]:')
    ]
    foot_cont_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if s == '    Indented continuation lines now also read like footnote-body source in the live docs/help TUI.'
    ]

    assert foot_marker_calls and any((attr & curses.A_DIM) and (attr & curses.A_BOLD) for attr in foot_marker_calls)
    assert foot_cont_calls and all(attr & curses.A_DIM for attr in foot_cont_calls)


def test_md_footnote_reference_tokens_render_bold_in_live_help_tui(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    fake = _CaptureStdScr(h=220, w=120)
    _render(fake, ed)

    foot_ref_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if s == '[^help-footnote]' or s == '^help-footnote'
    ]

    assert foot_ref_calls
    assert any(attr & curses.A_BOLD for attr in foot_ref_calls)
    assert any(attr & curses.A_UNDERLINE for attr in foot_ref_calls if attr & curses.A_BOLD)


def test_md_autolink_tokens_render_bold_in_live_help_tui(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    fake = _CaptureStdScr(h=220, w=120)
    _render(fake, ed)

    autolink_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if s == '<https://micro-editor.github.io/>' or s == 'https://micro-editor.github.io/'
    ]

    assert autolink_calls
    assert any(attr & curses.A_BOLD for attr in autolink_calls)
    assert any(attr & curses.A_UNDERLINE for attr in autolink_calls if attr & curses.A_BOLD)


def test_md_image_tokens_render_dim_in_live_help_tui(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    fake = _CaptureStdScr(h=220, w=120)
    _render(fake, ed)

    image_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if s == '![Vision image](00-vision.md)' or s == '![Vision ref image][visionimg]'
    ]

    assert image_calls
    assert all(attr & curses.A_DIM for attr in image_calls)
    assert not any(attr & curses.A_UNDERLINE for attr in image_calls)


def test_md_link_source_tokens_render_dim_while_labels_stay_underlined(monkeypatch) -> None:
    monkeypatch.setattr(curses, "has_colors", lambda: False)
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    fake = _CaptureStdScr(h=220, w=120)
    _render(fake, ed)

    vision_rows = {
        y for y, line in fake.lines.items()
        if '[Vision](00-vision.md)' in line or '[Vision ref][visionref]' in line or '[Vision shortcut]' in line
    }

    link_source_calls = [
        attr
        for y, x, s, attr in fake.calls
        if y in vision_rows and s in ('[', '](00-vision.md)', '][visionref]', ']')
    ]
    link_label_calls = [
        attr
        for _y, _x, s, attr in fake.calls
        if s in ('Vision', 'Vision ref', 'Vision shortcut')
    ]

    assert link_source_calls
    assert all((attr & curses.A_DIM) and not (attr & curses.A_UNDERLINE) for attr in link_source_calls)
    assert link_label_calls
    assert all(attr & curses.A_UNDERLINE for attr in link_label_calls)
