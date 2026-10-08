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
    assert any(r[2] == "h2" and r[0] == "Links" for r in rows)


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
