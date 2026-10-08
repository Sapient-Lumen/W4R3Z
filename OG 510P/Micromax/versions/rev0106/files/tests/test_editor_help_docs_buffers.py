from __future__ import annotations


from micromax_editor.editor import Editor


def test_help_opens_docs_buffer_protected_and_blocks_edits() -> None:
    ed = Editor()

    # Open a known docs page from the repo.
    assert ed.open_help_doc("vision") is True
    eb = ed.cur()

    assert eb.name.startswith("help:")
    assert bool(eb.local_options.get("readonly")) is True

    st = ed.status_model()
    assert int(st.get("protected", 0)) == 1
    assert int(st.get("readonly", 0)) == 1

    # Help/docs buffers should not pollute the recent file MRU.
    assert getattr(ed, "recent_files", []) == []

    # Mutating actions are blocked.
    before = eb.buf.get_text()
    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is False
    assert eb.buf.get_text() == before
    assert "read-only buffer" in (ed.messages[-1] if ed.messages else "")

    # Mutating commands are also blocked.
    assert ed.exec_command_line("replace foo bar") is False
    assert "replace: read-only buffer" in (ed.messages[-1] if ed.messages else "")

    # Save should fail clearly.
    assert ed.exec_command_line("save") is False
    assert "save:" in (ed.messages[-1] if ed.messages else "")


def test_doc_prompt_rows_and_helppick_command() -> None:
    ed = Editor()
    rows = ed.doc_prompt_rows()
    assert rows
    assert any(r[0] == "vision" and r[1] == "doc" for r in rows)

    assert ed.exec_command_line("helppick") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "doc"


def test_command_palette_openpath_row() -> None:
    ed = Editor()
    q = "docs/00-vision.md"
    rows = ed.command_palette_apropos_rows(q, limit=8)
    assert any(r[0] == q and r[1] == "openpath" for r in rows)

    ed.enter_command_palette(q)
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    assert ed.submit_prompt() is True
    assert ed.cur().buf.path and ed.cur().buf.path.endswith("docs/00-vision.md")
