from __future__ import annotations

from micromax_editor.editor import Editor


def test_prompt_picker_ctrl_home_end_jumps_selection_without_mutating_query() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    q = str(ed.prompt.text)
    n = len(ed.prompt.suggestion_rows)
    assert n >= 4

    ed.prompt.suggest_index = 2
    assert ed.dispatch_key("Ctrl-End") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == n - 1
    assert str(ed.prompt.text) == q

    assert ed.dispatch_key("Ctrl-Home") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == 0
    assert str(ed.prompt.text) == q
