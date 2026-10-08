from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*keys*", "")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<keybinding-authority-test>")
    return list(ed.vm.stack)


def test_script_press_key_cannot_replay_trusted_binding_as_user_authority() -> None:
    ed = _editor()
    ed.bind_key_checked("F12", "command:set cap.fs-save true")

    assert _hostcall(ed, "ed.press-key", "F12")[-1] == 0

    assert bool(ed.options.get("cap.fs-save")) is False
    assert "script context cannot press keybinding: F12" in ed.messages[-1]
    assert "cap.keybinding-press" in ed.messages[-1]


def test_keybinding_press_capability_replays_spec_under_script_authority_not_trusted_authority() -> None:
    ed = _editor()
    ed.bind_key_checked("F12", "command:set cap.fs-save true")
    assert ed.exec_command_line("set cap.keybinding-press true") is True

    assert _hostcall(ed, "ed.press-key", "F12")[-1] == 0

    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)


def test_keybinding_press_capability_can_replay_safe_trusted_binding_under_script_context() -> None:
    ed = _editor()
    ed.bind_key_checked("F11", "command:set showchars true")
    assert bool(ed.options.get("showchars")) is False
    assert ed.exec_command_line("set cap.keybinding-press true") is True

    assert _hostcall(ed, "ed.press-key", "F11")[-1] == 1

    assert bool(ed.options.get("showchars")) is True


def test_independent_script_cannot_synthetic_press_other_script_binding() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.bind_key_checked("F10", "command:set showchars true")

    with ed.script_context(origin_id="script-b"):
        assert ed.dispatch_key("F10") is False

    assert bool(ed.options.get("showchars")) is False
    assert "different script origin" in ed.messages[-1]

    with ed.script_context(origin_id="script-a"):
        assert ed.dispatch_key("F10") is True

    assert bool(ed.options.get("showchars")) is True


def test_script_binding_inventory_hides_trusted_specs_but_keeps_same_origin_specs() -> None:
    ed = _editor()
    ed.bind_key_checked("F1", "command:trusted-secret")
    with ed.script_context(origin_id="script-a"):
        ed.bind_key_checked("F2", "command:own-public")
        rows = ed.available_binding_inventory_rows()
        keys = {str(row[1]): row for row in rows}
        assert "F2" in keys
        assert "F1" not in keys
        assert ed.binding_detail_row("F1") == 0
        assert ed.binding_detail_row("F2") != 0

    with ed.script_context(origin_id="script-b"):
        rows = ed.available_binding_inventory_rows()
        keys = {str(row[1]): row for row in rows}
        assert "F1" not in keys
        assert "F2" not in keys


def test_keybinding_read_capability_reveals_protected_binding_specs() -> None:
    ed = _editor()
    ed.bind_key_checked("F1", "command:trusted-secret")
    assert ed.exec_command_line("set cap.keybinding-read true") is True

    with ed.script_context(origin_id="script-a"):
        row = ed.binding_detail_row("F1")

    assert row != 0
    assert row[1] == "F1"
    assert row[2] == "command:trusted-secret"


def test_resolve_key_hostcall_denial_preserves_key_operand() -> None:
    ed = _editor()
    ed.bind_key_checked("F1", "command:trusted-secret")

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["F1"]
        with pytest.raises(MicromaxError, match="cannot resolve keybinding: F1"):
            ed.vm.stack.append("ed.resolve-key")
            ed.vm.eval("hostcall", filename="<keybinding-authority-test>")

    assert ed.vm.stack == ["F1"]


def test_keybinding_press_capability_is_advertised() -> None:
    ed = _editor()
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.keybinding-press"][1] == "cap.keybinding-press"
    assert rows["ed.keybinding-press"][3] == 0

    assert ed.exec_command_line("set cap.keybinding-press true") is True
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.keybinding-press"][3] == 1


def test_binding_inventory_hostcalls_use_read_authority_filters() -> None:
    ed = _editor()
    ed.bind_key_checked("F1", "command:trusted-secret", desc="trusted opener")

    with ed.script_context(origin_id="script-a"):
        ed.bind_key_checked("F2", "command:own-public", desc="own opener")
        assert _hostcall(ed, "ed.bindings")[-1] == [["F2", "command:own-public", 0]]
        assert _hostcall(ed, "ed.binding-detail")[-1] == [["F2", "command:own-public", 0, 0]]
        assert _hostcall(ed, "ed.available-binding-inventory-rows")[-1] == [
            ["global", "F2", "command:own-public", "own opener", 0]
        ]
        assert _hostcall(ed, "ed.binding-rows-for", 0)[-1] == [["F2", "command:own-public", 0, 0]]
        assert _hostcall(ed, "ed.binding-info-for", 0)[-1] == [["F2", "command:own-public", "own opener", 0, 0]]

    assert ed.exec_command_line("set cap.keybinding-read true") is True
    with ed.script_context(origin_id="script-b"):
        keys = {str(row[0]) for row in _hostcall(ed, "ed.bindings")[-1]}
        assert {"F1", "F2"}.issubset(keys)


def test_binding_detail_hostcall_denial_preserves_key_operand() -> None:
    ed = _editor()
    ed.bind_key_checked("F1", "command:trusted-secret")

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["F1"]
        with pytest.raises(MicromaxError, match="cannot read keybinding: F1"):
            ed.vm.stack.append("ed.binding-detail-row")
            ed.vm.eval("hostcall", filename="<keybinding-authority-test>")

    assert ed.vm.stack == ["F1"]
