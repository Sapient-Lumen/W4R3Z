from __future__ import annotations


from micromax_editor.editor import Editor


def _line_index_of(ed: Editor, needle: str) -> int:
    eb = ed.cur()
    for i, ln in enumerate(eb.buf.lines):
        if needle in str(ln):
            return i
    raise AssertionError(f"needle not found: {needle!r}")


def test_helpnavpick_jumps_to_heading_match() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = _line_index_of(ed, "## Links")

    assert ed.exec_command_line("helpnavpick Links") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"

    # Submit should jump to the best matching heading.
    assert ed.submit_prompt() is True

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == want_line


def test_helpnavpick_can_open_link_target_doc() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Softwrap":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "Files"

    assert ed.submit_prompt() is True
    assert ed.cur().name.startswith("help:softwrap")


def test_helpnavpick_section_name_for_headings() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Links" and str(row[1]) == "heading":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "Headings"


def test_helpnavpick_requires_docs_buffer() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hi")
    assert ed.exec_command_line("helpnavpick") is False
    assert "not in a docs buffer" in (ed.messages[-1] if ed.messages else "")


def test_helpnav_section_rows_respects_help_linksections_heading_option() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    ed.options.set("help.linksections", "heading")

    sections = ed.help_nav_section_rows()
    labels = [str(s[0]) for s in sections if isinstance(s, list) and s]

    assert "Headings" in labels
    assert "Links" in labels
    assert "External links" in labels
    assert "Files" not in labels
    assert "External" not in labels


def test_helpnavpick_link_section_name_respects_heading_grouping() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    ed.options.set("help.linksections", "heading")

    assert ed.exec_command_line("helpnavpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Softwrap":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)

    assert ed.prompt_current_section() == "Links"


def test_helpnavpick_includes_footnote_reference() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "[^help-footnote]":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "Docs"

    want_line = _line_index_of(ed, "[^help-footnote]:")
    assert ed.submit_prompt() is True
    assert ed.cur().cursors[ed.cur().primary].line == want_line
