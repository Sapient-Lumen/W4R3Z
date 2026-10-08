from __future__ import annotations

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.tui import _prompt_display_lines


def test_tui_prompt_display_lines_includes_section_counts_and_more_counts() -> None:
    ed = Editor()

    p = Prompt(kind="helplink")
    rows: list[list[str]] = []

    # Small leading sections
    rows.append(["Docs link 1", "link", "help:vision", ""])
    rows.append(["File link 1", "link", "docs/00-vision.md", ""])

    # Large external section so we force windowing + more markers.
    for i in range(30):
        rows.append([f"External {i}", "link", f"https://example.com/{i}", ""])

    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 2 + 15  # mid External section
    ed.prompt = p

    lines = _prompt_display_lines(ed, max_lines=6, width=80)

    # Section headers include counts.
    assert any("External" in ln and "(" in ln and ")" in ln for ln in lines)

    # When windowed, the TUI shows a more-marker with a count of hidden rows.
    assert any(ln.startswith("↑") and "+" in ln for ln in lines) or any(ln.startswith("↓") and "+" in ln for ln in lines)
