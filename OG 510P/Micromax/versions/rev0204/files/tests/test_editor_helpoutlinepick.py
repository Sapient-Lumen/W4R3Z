from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.buffer import Cursor


def _line_index_of(ed: Editor, needle: str) -> int:
    eb = ed.cur()
    for i, ln in enumerate(eb.buf.lines):
        if needle in str(ln):
            return i
    raise AssertionError(f"needle not found: {needle!r}")


def test_help_outline_rows_lists_headings() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    rows = ed.help_outline_rows()
    # Should include the top-level title and a few subheadings.
    titles = {r[0] for r in rows}
    assert "Help browser" in titles
    assert "Links" in titles
    assert "Explicit fragment target" in titles
    assert "Explicit fragment target {#custom-frag}" not in titles
    assert any(r[2] == "h2" and r[0] == "Links" for r in rows)


def test_help_outline_rows_include_setext_headings() -> None:
    ed = Editor()
    assert ed.open_help_doc("setext-headings") is True
    rows = ed.help_outline_rows()
    titles = {r[0] for r in rows}
    assert "Setext headings demo" in titles
    assert "Outline section" in titles
    assert "Explicit setext target" in titles
    assert "Explicit setext target {#custom-setext-frag}" not in titles
    assert any(r[2] == "h1" and r[0] == "Setext headings demo" for r in rows)
    assert any(r[2] == "h2" and r[0] == "Outline section" for r in rows)


def test_help_outline_rows_include_multiline_setext_headings() -> None:
    ed = Editor()
    assert ed.open_help_doc("multiline-setext-headings") is True
    rows = ed.help_outline_rows()
    titles = {r[0] for r in rows}
    assert "Multi-line setext headings demo" in titles
    assert "Outline section for multi-line setext" in titles
    assert "Explicit multi-line setext target" in titles
    assert "setext target {#multi-setext-frag}" not in titles
    assert any(r[2] == "h1" and r[0] == "Multi-line setext headings demo" for r in rows)
    assert any(r[2] == "h2" and r[0] == "Outline section for multi-line setext" for r in rows)


def test_help_outline_rows_ignore_code_indented_heading_lookalikes() -> None:
    ed = Editor()
    assert ed.open_help_doc("indented-codeish-markdown") is True
    rows = ed.help_outline_rows()
    titles = {r[0] for r in rows}
    assert "Indented code-ish markdown" in titles
    assert "Links and refs" in titles
    assert "Indented heading lookalikes" in titles
    assert "Real setext heading" in titles
    assert "Four-space ATX heading stays prose" not in titles


def test_help_outline_rows_ignore_headings_inside_html_comments() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True
    rows = ed.help_outline_rows()
    titles = {r[0] for r in rows}
    assert "Hidden heading inside comment" not in titles


def test_helpoutlinepick_jumps_to_selected_heading() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    want_line = _line_index_of(ed, "## Links")

    assert ed.exec_command_line("helpoutlinepick Links") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpoutline"

    # Submit should jump to the best matching heading.
    assert ed.submit_prompt() is True

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == want_line


def test_helpoutlinepick_requires_docs_buffer() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hi")
    assert ed.exec_command_line("helpoutlinepick") is False
    assert "not in a docs buffer" in (ed.messages[-1] if ed.messages else "")


def test_hostcall_help_outline_rows() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc("help-browser") is True

    vm = ed.vm
    vm.stack.append("Links")
    vm.stack.append("ed.help-outline-rows")
    vm.eval("hostcall")
    rows = vm.pop_list()

    assert any(r[0] == "Links" for r in rows)
