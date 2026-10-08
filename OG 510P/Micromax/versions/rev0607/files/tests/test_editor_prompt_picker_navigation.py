from __future__ import annotations


from micromax_editor.editor import Editor


def test_prompt_picker_up_down_moves_selection_without_mutating_query() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    q = str(ed.prompt.text)
    n = len(ed.prompt.suggestion_rows)
    i0 = int(ed.prompt.suggest_index)

    assert ed.dispatch_key("DownArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == (i0 + 1) % n
    assert str(ed.prompt.text) == q

    assert ed.dispatch_key("UpArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == i0
    assert str(ed.prompt.text) == q


def test_prompt_picker_ctrl_y_copies_link_target() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    # Select a known link row.
    idx = None
    tgt = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Softwrap":
            idx = i
            tgt = str(row[2])
            break
    assert idx is not None
    assert tgt
    ed.prompt.suggest_index = int(idx)

    assert ed.dispatch_key("Ctrl-y") is True
    assert ed.clipboard_items == [tgt]
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
