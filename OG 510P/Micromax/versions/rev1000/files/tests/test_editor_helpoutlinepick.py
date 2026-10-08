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




def test_help_outline_section_rows_group_by_parent_heading_path() -> None:
    ed = Editor()
    assert ed.open_help_doc("helpoutline-section-groups") is True

    sections = ed.help_outline_section_rows()

    assert [sec[0] for sec in sections] == [
        "Top",
        "Help outline section groups",
        "Help outline section groups › Guide",
        "Help outline section groups › Guide › Links",
    ]

    assert [row[0] for row in sections[0][1]] == ["Help outline section groups"]
    assert [row[0] for row in sections[1][1]][:2] == ["Guide", "Appendix"]
    assert any(row[0] == "Why this stays honest" for row in sections[1][1])
    assert [row[0] for row in sections[2][1]] == ["Links", "Other"]
    assert [row[0] for row in sections[3][1]] == ["Deep dive"]


def test_help_outline_rows_query_can_match_parent_breadcrumb_terms() -> None:
    ed = Editor()
    assert ed.open_help_doc("helpoutline-section-groups") is True

    rows = ed.help_outline_rows("Guide Links", limit=3)
    assert rows
    assert rows[0][0] == "Links"

    rows2 = ed.help_outline_rows("Guide Deep dive", limit=3)
    assert rows2
    assert rows2[0][0] == "Deep dive"


def test_help_outline_rows_query_can_match_explicit_heading_fragment_ids() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    rows = ed.help_outline_rows("custom-frag", limit=3)
    assert rows
    assert rows[0][0] == "Explicit fragment target"


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
    target = str(eb.buf.path or eb.name)
    assert ed.status_model()["last_message"] == f"helpjump: {target} @ {want_line + 1}:{c.col}"


def test_helpoutlinepick_requires_docs_buffer() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hi")
    assert ed.exec_command_line("helpoutlinepick") is False
    assert "not in a docs buffer" in (ed.messages[-1] if ed.messages else "")


def test_hostcall_help_outline_rows_and_sections() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc("helpoutline-section-groups") is True

    vm = ed.vm
    vm.stack.append("Links")
    vm.stack.append("ed.help-outline-rows")
    vm.eval("hostcall")
    rows = vm.pop_list()
    assert any(r[0] == "Links" for r in rows)

    vm.stack.append("")
    vm.stack.append("ed.help-outline-section-rows")
    vm.eval("hostcall")
    sections = vm.pop_list()

    assert [sec[0] for sec in sections] == [
        "Top",
        "Help outline section groups",
        "Help outline section groups › Guide",
        "Help outline section groups › Guide › Links",
    ]


def test_helpoutlinepick_submit_reresolves_after_typed_text_changes() -> None:
    ed = Editor()
    assert ed.open_help_doc("help-browser") is True

    links_line = _line_index_of(ed, "## Links")
    external_line = _line_index_of(ed, "## External links")

    assert ed.exec_command_line("helpoutlinepick Links") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "helpoutline"
    assert ed.prompt.suggestion_rows
    assert str(ed.prompt.suggestion_rows[0][0]) == "Links"

    assert ed.set_prompt_text("External links") is True
    assert ed.submit_prompt() is True

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    c = eb.cursors[eb.primary]
    assert c.line == external_line
    assert c.line != links_line
