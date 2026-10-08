from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    vm.stack.clear()
    for arg in args:
        vm.stack.append(arg)
    vm.stack.append(name)
    vm.eval("hostcall", filename="<hostcall>")
    return list(vm.stack)


def test_script_keymode_inventory_hides_trusted_active_and_known_modes() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")

    ed.bind_key_checked("F40", "command:showstatus", mode="secret")
    ed.push_key_mode("trusted")

    with ed.script_context():
        rows = _hostcall(ed, "ed.keymode-inventory-rows")[-1]
        modes = _hostcall(ed, "ed.keymodes")
        status = _hostcall(ed, "ed.status")[-1]

    assert ["active", "trusted", 0] not in rows
    assert ["known", "secret", 0] not in rows
    assert rows == [["active", "global", 0], ["known", "global", 0]]
    assert "trusted" not in modes[-2]
    assert "secret" not in modes[-1]
    assert status["keymode"] == ""


def test_script_keymode_detail_denial_preserves_operand() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.bind_key_checked("F41", "command:showstatus", mode="secret")

    with ed.script_context():
        with pytest.raises(Exception) as excinfo:
            _hostcall(ed, "ed.keymode-detail-row", "secret")
        stack = list(ed.vm.stack)

    assert "script context cannot read keymode: secret" in str(excinfo.value)
    assert stack == ["secret"]


def test_script_can_read_same_origin_keymode_but_not_binding_spec_without_binding_cap() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")

    with ed.script_context():
        _hostcall(ed, "ed.bind-mode", "mine", "F42", "command:showstatus")
        _hostcall(ed, "ed.keymode-push", "mine")
        rows = _hostcall(ed, "ed.keymode-inventory-rows")[-1]
        detail = _hostcall(ed, "ed.keymode-detail-row", "mine")[-1]

    assert ["active", "mine", 0] in rows
    assert ["known", "mine", 0] in rows
    assert detail[:5] == ["mine", 1, 1, 0, 1]
    assert detail[5] == "F42"
    assert detail[6] == "command:showstatus"


def test_keymode_read_cap_reveals_mode_name_without_granting_binding_read() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.bind_key_checked("F43", "command:showstatus", mode="secret")
    assert ed.exec_command_line("set cap.keymode-read true") is True

    with ed.script_context():
        rows = _hostcall(ed, "ed.keymode-inventory-rows")[-1]
        detail = _hostcall(ed, "ed.keymode-detail-row", "secret")[-1]

    assert ["known", "secret", 0] in rows
    assert detail[:4] == ["secret", 0, 1, 0]
    # The mode itself is visible, but protected key/action specs still require
    # cap.keybinding-read and are not leaked by cap.keymode-read alone.
    assert detail[4:] == [0, 0, 0, 0]


def test_keymode_read_cap_plus_keybinding_read_reveals_sample_binding() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.bind_key_checked("F44", "command:showstatus", mode="secret")
    assert ed.exec_command_line("set cap.keymode-read true") is True
    assert ed.exec_command_line("set cap.keybinding-read true") is True

    with ed.script_context():
        detail = _hostcall(ed, "ed.keymode-detail-row", "secret")[-1]

    assert detail[:7] == ["secret", 0, 1, 0, 1, "F44", "command:showstatus"]
