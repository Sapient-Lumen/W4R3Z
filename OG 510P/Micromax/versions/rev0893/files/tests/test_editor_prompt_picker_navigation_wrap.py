from __future__ import annotations

from micromax_editor.editor import Editor


def test_prompt_picker_wrap_option_clamps_at_ends_when_disabled() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    n = len(ed.prompt.suggestion_rows)
    assert n >= 3

    # Disable wrap: selection should clamp at ends.
    ed.options.set("prompt.wrap", "false")

    ed.prompt.suggest_index = 0
    assert ed.dispatch_key("UpArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == 0

    ed.prompt.suggest_index = n - 1
    assert ed.dispatch_key("DownArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == n - 1
