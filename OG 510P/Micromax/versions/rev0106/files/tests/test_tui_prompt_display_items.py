from __future__ import annotations

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.tui import _prompt_display_items, _prompt_display_lines


def test_tui_prompt_display_items_preserves_row_kinds_and_text() -> None:
    ed = Editor()

    p = Prompt(kind="palette")
    rows: list[list[str]] = [
        ["./foo.txt", "openpath", "file", "/tmp"],
        ["/tmp/bar.txt", "recentfile", "bar.txt", "/tmp"],
        ["DoThing", "action", "do a thing", ""],
        ["save", "command", "save file", ""],
    ]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    ed.prompt = p

    items = _prompt_display_items(ed, max_lines=12, width=80)
    lines = _prompt_display_lines(ed, max_lines=12, width=80)

    assert lines == [it.text for it in items]

    row_items = [it for it in items if (not it.is_header and not it.is_more)]
    assert any(it.row_kind == "openpath" for it in row_items)
    assert any(it.row_kind == "recentfile" for it in row_items)
    assert any(it.row_kind == "action" for it in row_items)
    assert any(it.row_kind == "command" for it in row_items)
