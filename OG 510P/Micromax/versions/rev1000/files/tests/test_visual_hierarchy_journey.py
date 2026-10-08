from __future__ import annotations

from pathlib import Path

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.screen_consumer import validate_screen_contract_v1


def _cue_kinds(contract: dict[str, object]) -> set[str]:
    return {
        str(cue["kind"])
        for cue in contract["cues"]  # type: ignore[index]
        if isinstance(cue, dict)
    }


def test_80x24_edit_help_prompt_journey_has_visible_hierarchy(
    tmp_path: Path,
    monkeypatch,
) -> None:
    doc = tmp_path / "10-visual-hierarchy.md"
    doc.write_text(
        "# Visual hierarchy\n\n"
        "Use [selection help](#selection-help).\n\n"
        "## Selection help\n\n"
        "Keep the active range visible.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("MICROMAX_DOCS", str(tmp_path))

    ed = Editor()
    ed.new_buffer(
        "demo.mx",
        ": square dup * ;\n5 square\n",
        path="demo.mx",
    )
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 8), Cursor(1, 8)]
    eb.sel_anchors[:] = [Cursor(0, 2), Cursor(1, 2)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    edit = ed.screen_contract(24, 80)
    assert validate_screen_contract_v1(edit) == edit
    assert len(edit["rows"]) == 24
    assert edit["rows"][23]["kind"] == "statusline"
    assert {
        "syntax-def",
        "selection-primary",
        "selection-secondary",
    } <= _cue_kinds(edit)
    assert edit["cursor"] == {
        "visible": True,
        "mode": "edit",
        "y": 0,
        "x": 8,
    }

    assert ed.open_help_doc(str(doc), allow_outside_root=True) is True
    help_screen = ed.screen_contract(24, 80)
    assert validate_screen_contract_v1(help_screen) == help_screen
    assert help_screen["rows"][23]["kind"] == "statusline"
    assert any(
        "docs-heading-title" in row.get("tags", [])
        for row in help_screen["rows"]
    )
    assert "docs-link" in _cue_kinds(help_screen)

    ed.enter_command_palette("help")
    prompt = ed.screen_contract(24, 80)
    assert validate_screen_contract_v1(prompt) == prompt
    prompt_rows = [row for row in prompt["rows"] if row["kind"] == "prompt-panel"]
    assert any("prompt-header" in row.get("tags", []) for row in prompt_rows)
    assert any("prompt-selected" in row.get("tags", []) for row in prompt_rows)
    assert prompt["rows"][22]["kind"] == "interaction"
    assert prompt["rows"][23]["kind"] == "statusline"
    assert prompt["cursor"]["mode"] == "prompt"
    assert prompt["cursor"]["y"] == 22
