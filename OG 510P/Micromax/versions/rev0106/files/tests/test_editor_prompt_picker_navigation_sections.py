from __future__ import annotations


from micromax_editor.editor import Editor


def _section_starts(ed: Editor) -> list[int]:
    assert ed.prompt is not None
    kind = str(ed.prompt.kind)
    starts: list[int] = []
    last = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        lbl = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind=kind)
        if lbl != last:
            starts.append(i)
            last = lbl
    return starts


def test_prompt_picker_alt_up_down_jumps_between_sections() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helplink"
    assert ed.prompt.suggestion_rows

    starts = _section_starts(ed)
    assert len(starts) >= 2

    # If the first section has multiple rows, start inside it so Alt-Up jumps
    # to the section start.
    i0 = starts[0]
    i1 = starts[1]
    inside0 = i0 + 1 if (i0 + 1) < i1 else i0
    ed.prompt.suggest_index = inside0

    assert ed.dispatch_key("Alt-UpArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == i0

    assert ed.dispatch_key("Alt-DownArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == i1

    # From a section start, Alt-Up goes to the previous section start.
    assert ed.dispatch_key("Alt-UpArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == i0


def test_prompt_picker_section_jump_respects_prompt_wrap_option() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    assert ed.exec_command_line("helplinkpick") is True
    assert ed.prompt is not None
    assert ed.prompt.suggestion_rows

    starts = _section_starts(ed)
    assert len(starts) >= 2

    # Disable wrap: jumping past the last section should clamp.
    ed.options.set("prompt.wrap", "false")
    ed.prompt.suggest_index = int(starts[-1])
    assert ed.dispatch_key("Alt-DownArrow") is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[-1])
