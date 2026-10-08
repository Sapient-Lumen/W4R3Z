from __future__ import annotations

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.tui import _prompt_display_lines


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
