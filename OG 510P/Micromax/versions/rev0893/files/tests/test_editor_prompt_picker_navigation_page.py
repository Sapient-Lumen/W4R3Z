from __future__ import annotations


from micromax_editor.editor import Editor


def test_prompt_picker_pageup_pagedown_jumps_selection_without_mutating_query() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    # Make the jump size deterministic for the test.
    ed.options.set("prompt.page", "3")

    q = str(ed.prompt.text)
    n = len(ed.prompt.suggestion_rows)
    assert n >= 4
    i0 = int(ed.prompt.suggest_index)

    assert ed.dispatch_key("PageDown") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == (i0 + 3) % n
    assert str(ed.prompt.text) == q

    assert ed.dispatch_key("PageUp") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == i0
    assert str(ed.prompt.text) == q
