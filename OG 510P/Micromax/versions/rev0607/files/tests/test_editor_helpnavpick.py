from __future__ import annotations


from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    install_editor_hostcalls(ed)
    ed.vm.stack.clear()
    for arg in args:
        ed.vm.stack.append(arg)
    ed.vm.eval(f'"{name}" hostcall', filename='<test>')
    assert ed.vm.stack
    return ed.vm.stack.pop()


def _line_index_of(ed: Editor, needle: str) -> int:
    eb = ed.cur()
    for i, ln in enumerate(eb.buf.lines):
        if needle in str(ln):
            return i
    raise AssertionError(f"needle not found: {needle!r}")


def test_helpnavpick_query_can_match_heading_breadcrumb_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("helpoutline-section-groups") is True

    assert ed.exec_command_line("helpnavpick Guide Links") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Links"
    assert ed.prompt.suggestion_rows[0][1] == "heading"


def test_helpnavpick_query_can_match_link_heading_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick Reference Vision ref") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Vision ref"
    assert ed.prompt.suggestion_rows[0][1] == "link"


def test_helpnavpick_query_can_match_link_target_doc_title_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick image metadata") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Metadata note"
    assert ed.prompt.suggestion_rows[0][1] == "link"


def test_helpnavpick_query_can_match_link_target_heading_title_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick hidden image metadata anchor") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Image anchor note"
    assert ed.prompt.suggestion_rows[0][1] == "link"


def test_helpnavpick_query_can_match_heading_fragment_ids() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    assert ed.exec_command_line("helpnavpick custom-frag") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][0] == "Explicit fragment target"
    assert ed.prompt.suggestion_rows[0][1] == "heading"


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
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"helpjump: {target} @ {want_line + 1}:{c.col}"


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


def test_helpnavpick_section_name_for_headings_uses_outline_breadcrumb() -> None:
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
    assert ed.prompt_current_section() == "Help browser"


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

    assert "Top" in labels
    assert "Help browser" in labels
    assert "Links" in labels
    assert "External links" in labels
    assert "Headings" not in labels
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




def test_helpnavpick_section_name_for_nested_headings_uses_full_outline_breadcrumb() -> None:
    ed = Editor()
    assert ed.open_help_doc("helpoutline-section-groups") is True

    assert ed.exec_command_line("helpnavpick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpnav"
    assert ed.prompt.suggestion_rows

    idx = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        if str(row[0]) == "Deep dive" and str(row[1]) == "heading":
            idx = i
            break
    assert idx is not None
    ed.prompt.suggest_index = int(idx)
    assert ed.prompt_current_section() == "Help outline section groups › Guide › Links"

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
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == want_line
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"helpjump: {target} @ {want_line + 1}:{c.col}"


def test_helpnav_section_summary_rows_and_showhelpnav_are_count_aware() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    rows = _hostcall(ed, 'ed.helpnav-section-summary-rows', '')
    assert isinstance(rows, list)
    assert rows
    assert rows[0][:2] == ['Top', 1]
    assert rows[0][3] == 'h1 · 1:3'
    labels = [str(r[0]) for r in rows if isinstance(r, list) and r]
    assert 'Files' in labels
    assert 'External' in labels
    file_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Files')
    assert '00-vision.md · ' in str(file_row[3])

    ed.messages.clear()
    assert ed.exec_command_line('showhelpnav') is True
    assert ed.messages[0].startswith('showhelpnav: ')
    assert any(msg.startswith('Top: 1 (e.g. Help browser') for msg in ed.messages[1:])
    assert any(msg.startswith('Files: ') for msg in ed.messages[1:])

    ed.messages.clear()
    assert ed.exec_command_line('showhelpnav image metadata') is True
    assert ed.messages[0] == 'showhelpnav image metadata: 1 section(s), 3 target(s)'
    assert ed.messages[1].startswith('Files: 3 (e.g. Metadata note')


def test_showhelpnav_requires_docs_buffer() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', '')
    assert ed.exec_command_line('showhelpnav') is False
    assert ed.messages[-1] == 'showhelpnav: not in a docs buffer'
