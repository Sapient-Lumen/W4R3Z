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

    ed.vm.eval('"ed.plugin-inventory-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.plugin-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.plugin-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.command-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.binding-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.action-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.available-binding-inventory-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.binding-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.keymode-inventory-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.keymode-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.option-inventory-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.option-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.option-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.buffer-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.buffer-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.jump-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.jump-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.mark-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.mark-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-clear-count" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-slot-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-dir-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-slot-dir-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-dir-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-prompt-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.recent-dir-prompt-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.hook-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.hook-inventory-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.hook-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.command-palette-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.word-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.doc-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.topic-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.topic-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.apropos-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.doc-section-summary-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.help-current-heading-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.help-heading-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.help-link-detail-row" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.vm.eval('"ed.helpnav-section-summary-rows" host.feature?')
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
