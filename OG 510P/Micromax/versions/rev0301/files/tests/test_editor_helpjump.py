from __future__ import annotations

from micromax_editor.editor import Editor


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
