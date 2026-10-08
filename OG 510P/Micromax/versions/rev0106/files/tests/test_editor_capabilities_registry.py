from __future__ import annotations


from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_host_capabilities_rows_and_feature_advertisement() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    # By default, unsafe caps are disabled and not advertised.
    ed.vm.eval('"ed.shell" host.feature?')
    assert int(ed.vm.stack.pop()) == 0

    # Enabling via option should refresh feature advertisement.
    ed.exec_command_line("set cap.shell true")
    ed.vm.eval('"ed.shell" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    # Clipboard export/import are separate unsafe surfaces (UI backends like OSC 52 / external tools).
    ed.vm.eval('"ed.clipboard-export" host.feature?')
    assert int(ed.vm.stack.pop()) == 0
    ed.exec_command_line("set cap.clipboard-write true")
    ed.vm.eval('"ed.clipboard-export" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.clipboard-import" host.feature?')
    assert int(ed.vm.stack.pop()) == 0
    ed.exec_command_line("set cap.clipboard-read true")
    ed.vm.eval('"ed.clipboard-import" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    # Registry hostcall returns rows.
    ed.vm.eval('"host.capabilities" hostcall')
    rows = ed.vm.stack.pop()
    assert isinstance(rows, list)
    assert any((isinstance(r, list) and r and r[0] == "ed.shell") for r in rows)
    assert any((isinstance(r, list) and r and r[0] == "ed.fs-read") for r in rows)
    assert any((isinstance(r, list) and r and r[0] == "ed.persist") for r in rows)
    assert any((isinstance(r, list) and r and r[0] == "ed.clipboard-export") for r in rows)
    assert any((isinstance(r, list) and r and r[0] == "ed.clipboard-import") for r in rows)
