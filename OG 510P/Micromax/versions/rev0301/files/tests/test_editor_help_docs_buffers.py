from __future__ import annotations


from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    assert vm.stack
    return vm.stack.pop()


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
    assert any(r[0] == "setext-headings" and r[2] == "Setext headings demo" for r in rows)
    assert any(
        r[0] == "multiline-setext-headings"
        and r[2] == "Multi-line setext headings demo"
        and str(r[3]).startswith("This page exists to prove a multi-line setext heading")
        for r in rows
    )

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


def test_docpick_exposes_grouped_sections_and_preview_labels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    sections = _hostcall(ed, 'ed.doc-section-rows', '')
    assert isinstance(sections, list)
    labels = [sec[0] for sec in sections]
    assert labels[:3] == ['00–09 Project', '10–19 Research', '20–29 Language + VM']

    project_rows = next(sec[1] for sec in sections if sec[0] == '00–09 Project')
    vm_rows = next(sec[1] for sec in sections if sec[0] == '20–29 Language + VM')
    assert any(row[0] == 'vision' and row[2] == 'Vision' for row in project_rows)
    assert any(row[0] == 'language-design' and str(row[2]).startswith('Micromax language design') for row in vm_rows)

    assert ed.exec_command_line('helppick vision') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'doc'
    assert ed.prompt_current_section() == '00–09 Project'
    assert ed.prompt_current_preview().startswith('00–09 Project: Vision')
