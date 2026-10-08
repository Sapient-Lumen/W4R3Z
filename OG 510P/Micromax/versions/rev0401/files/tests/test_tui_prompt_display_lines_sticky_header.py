from __future__ import annotations

from pathlib import Path

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.tui import _prompt_display_lines, _render


def test_tui_prompt_display_lines_repeats_section_header_when_window_starts_mid_section() -> None:
    ed = Editor()

    # Build a synthetic helplink prompt with enough rows that the centered
    # suggestion window will start *after* the External header.
    p = Prompt(kind="helplink")
    rows: list[list[str]] = []

    # Docs section
    rows.append(["Docs link 1", "link", "help:vision", ""])
    rows.append(["Docs link 2", "link", "help:help-browser", ""])

    # Files section
    rows.append(["File link 1", "link", "docs/00-vision.md", ""])
    rows.append(["File link 2", "link", "docs/98-help-browser.md", ""])

    # External section (many)
    for i in range(20):
        rows.append([f"External {i}", "link", f"https://example.com/{i}", ""])

    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 4 + 10  # 10 deep into External section
    ed.prompt = p

    lines = _prompt_display_lines(ed, max_lines=5, width=80)
    # Newer TUI polish includes section counts in headers.
    assert any(line.strip().startswith("-- External") for line in lines)
    assert any("(20)" in line for line in lines)


def test_recentpick_display_lines_show_project_section_headers(tmp_path: Path) -> None:
    p1 = tmp_path / 'proj1'
    p2 = tmp_path / 'proj2'
    p1.mkdir()
    p2.mkdir()
    (p1 / '.git').mkdir()
    (p2 / '.git').mkdir()
    a = p1 / 'a.txt'
    b = p2 / 'b.txt'
    a.write_text('A', encoding='utf-8')
    b.write_text('B', encoding='utf-8')

    ed = Editor()
    ed.open_file(str(a))
    ed.open_file(str(b))
    assert ed.exec_command_line('recentpick') is True

    lines = _prompt_display_lines(ed, max_lines=8, width=120)
    assert any(str(p2) in ln and ln.startswith('-- ') for ln in lines)
    assert any(str(p1) in ln and ln.startswith('-- ') for ln in lines)


class _FakeStdScr:
    def __init__(self, *, h: int = 14, w: int = 120) -> None:
        self.h = h
        self.w = w
        self.lines: dict[int, str] = {}
        self.cursor = (0, 0)

    def erase(self) -> None:
        self.lines = {}

    def getmaxyx(self) -> tuple[int, int]:
        return (self.h, self.w)

    def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
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


def test_recentpick_render_shows_prompt_position_summary(tmp_path: Path) -> None:
    proj = tmp_path / 'proj'
    (proj / '.git').mkdir(parents=True)
    a = proj / 'src' / 'a.py'
    b = proj / 'tests' / 'b.py'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text('print(1)\n', encoding='utf-8')
    b.write_text('print(2)\n', encoding='utf-8')

    ed = Editor()
    ed.open_file(str(a))
    ed.open_file(str(b))
    assert ed.exec_command_line('recentpick') is True

    fake = _FakeStdScr(h=16, w=260)
    _render(fake, ed)
    prompt_line = fake.lines.get(14, '')
    assert '[1/2 • ' in prompt_line
    assert str(proj) in prompt_line
    assert 'tests/test_main.py' not in prompt_line
    assert 'tests/b.py' in prompt_line


def test_topicpick_display_lines_show_section_headers() -> None:
    ed = Editor()
    assert ed.exec_command_line('topicpick') is True
    assert ed.prompt is not None
    assert ed.prompt.suggestion_rows

    starts: list[tuple[int, str]] = []
    last = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind='topic')
        if label != last:
            starts.append((i, label))
            last = label

    assert [label for _i, label in starts][:3] == ['Commands', 'Actions', 'Words']

    for i, label in starts[:3]:
        ed.prompt.suggest_index = int(i)
        lines = _prompt_display_lines(ed, max_lines=10, width=120)
        assert any(line.strip().startswith(f'-- {label}') for line in lines)


def test_palettepick_display_lines_show_section_headers() -> None:
    ed = Editor()
    assert ed.exec_command_line('commandpick') is True
    assert ed.prompt is not None
    assert ed.prompt.suggestion_rows

    starts: list[tuple[int, str]] = []
    last = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind='palette')
        if label != last:
            starts.append((i, label))
            last = label

    assert [label for _i, label in starts][:2] == ['Commands', 'Actions']

    for i, label in starts[:2]:
        ed.prompt.suggest_index = int(i)
        lines = _prompt_display_lines(ed, max_lines=10, width=120)
        assert any(line.strip().startswith(f'-- {label}') for line in lines)
