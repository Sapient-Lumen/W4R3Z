from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    install_editor_hostcalls(ed)
    for arg in args:
        ed.vm.stack.append(arg)
    ed.vm.eval(f'"{name}" hostcall', filename='<test>')
    out = ed.vm.stack.pop()
    assert isinstance(out, list)
    return out


def _line_index_of(ed: Editor, needle: str) -> int:
    eb = ed.cur()
    for i, ln in enumerate(eb.buf.lines):
        if needle in str(ln):
            return i
    raise AssertionError(f"needle not found: {needle!r}")


def test_helpjump_without_args_opens_outline_prompt() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    assert ed.exec_command_line("helpjump") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpoutline"


def test_helpjump_jumps_to_best_matching_heading() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = _line_index_of(ed, "## Links")

    assert ed.exec_command_line("helpjump Links") is True

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == want_line
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"helpjump: {target} @ {want_line + 1}:{c.col}"


def test_helpjump_can_match_parent_breadcrumb_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("helpoutline-section-groups") is True

    want_line = _line_index_of(ed, "### Links")

    assert ed.exec_command_line("helpjump Guide Links") is True

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == want_line


def test_helpjump_can_match_explicit_heading_fragment_ids() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = _line_index_of(ed, "## Explicit fragment target {#custom-frag}")

    assert ed.exec_command_line("helpjump custom-frag") is True

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == want_line


def test_helpjump_requires_docs_buffer() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hi")
    assert ed.exec_command_line("helpjump Links") is False
    assert "not in a docs buffer" in (ed.messages[-1] if ed.messages else "")


def test_help_heading_detail_row_hostcall_matches_helpjump_surface() -> None:
    ed = Editor()
    assert ed.open_help_doc("helpoutline-section-groups") is True

    row = _hostcall(ed, 'ed.help-heading-detail-row', 'Guide Links')
    assert row[:4] == ['helpoutline-section-groups', 'Links', 'links', 3]
    assert row[4] == _line_index_of(ed, '### Links') + 1
    assert row[5] == 5
    assert row[6] == 'Help outline section groups › Guide'

    ed_frag = Editor()
    assert ed_frag.open_help_doc('help-browser') is True
    frag_row = _hostcall(ed_frag, 'ed.help-heading-detail-row', 'custom-frag')
    assert frag_row[:4] == ['help-browser', 'Explicit fragment target', 'custom-frag', 2]
    assert frag_row[4] == _line_index_of(ed_frag, '## Explicit fragment target {#custom-frag}') + 1
    assert frag_row[5] == 4
    assert frag_row[6] == 'Help browser'

    ed2 = Editor()
    install_editor_hostcalls(ed2)
    ed2.vm.stack.append('Links')
    ed2.vm.eval('"ed.help-heading-detail-row" hostcall', filename='<test>')
    assert int(ed2.vm.stack.pop()) == 0

    assert ed.exec_command_line('helpjump Guide Links') is True
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert (c.line + 1, c.col + 1) == (row[4], row[5])


def test_current_help_heading_detail_row_and_showhelpheading_are_explicit() -> None:
    ed = Editor()
    assert ed.open_help_doc('helpoutline-section-groups') is True

    want_line = _line_index_of(ed, 'inside one generic `Headings` bucket.')
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = want_line
    eb.cursors[eb.primary].col = 2

    row = _hostcall(ed, 'ed.help-current-heading-detail-row')
    assert row[:4] == ['helpoutline-section-groups', 'Links', 'links', 3]
    assert row[4] == _line_index_of(ed, '### Links') + 1
    assert row[5] == 5
    assert row[6] == 'Help outline section groups › Guide'

    ed.messages.clear()
    assert ed.exec_command_line('showhelpheading') is True
    assert ed.messages[-1] == f'helpheading Links @helpoutline-section-groups [h3] [section Help outline section groups › Guide] [#links] @ {row[4]}:{row[5]}'

    ed2 = Editor()
    install_editor_hostcalls(ed2)
    ed2.vm.eval('"ed.help-current-heading-detail-row" hostcall', filename='<test>')
    assert int(ed2.vm.stack.pop()) == 0


def test_showhelpheading_failures_are_typed() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', '')
    assert ed.exec_command_line('showhelpheading') is False
    assert ed.messages[-1] == 'showhelpheading: not in a docs buffer'

    ed2 = Editor()
    assert ed2.open_help_doc('help-browser') is True
    ed2.cur().buf.lines[:] = ['plain prose only', '', 'still no heading']
    ed2.cur().cursors[0].line = 0
    ed2.cur().cursors[0].col = 0
    ed2.cur().primary = 0
    assert ed2.exec_command_line('showhelpheading') is False
    assert ed2.messages[-1] == 'showhelpheading: no heading under cursor'
