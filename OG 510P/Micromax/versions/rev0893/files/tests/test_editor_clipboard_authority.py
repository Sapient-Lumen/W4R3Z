from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*authority*", "alpha beta\n")
    return ed


def test_script_cannot_read_trusted_clipboard_hostcalls() -> None:
    ed = _editor()
    ed.set_clipboard_items(["secret"], kind="items")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="clipboard"):
            ed.vm.host_fns["ed.clipboard"](ed.vm)
        with pytest.raises(PermissionError, match="clipboard"):
            ed.vm.host_fns["ed.clipboard-items"](ed.vm)

    assert ed.vm.stack == []
    assert ed.clipboard_text() == "secret"


def test_script_cannot_overwrite_trusted_clipboard_without_capability() -> None:
    ed = _editor()
    ed.set_clipboard_items(["trusted"], kind="items")
    ed.vm.stack.append("script-value")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="clipboard"):
            ed.vm.host_fns["ed.set-clipboard"](ed.vm)

    assert ed.vm.stack == ["script-value"]
    assert ed.clipboard_text() == "trusted"
    assert ed.clipboard_authority.script_context is False


def test_script_can_read_and_update_own_clipboard() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack.append("mine")
        ed.vm.host_fns["ed.set-clipboard"](ed.vm)
        assert ed.vm.stack == []
        ed.vm.host_fns["ed.clipboard"](ed.vm)
        assert ed.vm.stack.pop() == "mine"
        ed.vm.stack.extend([["a", "b"], "lines"])
        ed.vm.host_fns["ed.set-clipboard-items"](ed.vm)
        ed.vm.host_fns["ed.clipboard-items"](ed.vm)
        assert ed.vm.stack.pop() == "lines"
        assert ed.vm.stack.pop() == ["a", "b"]

    assert ed.clipboard_text() == "a\nb\n"
    assert ed.clipboard_authority.script_origin_id == "script-a"


def test_clipboard_read_write_capabilities_are_explicit_overrides() -> None:
    ed = _editor()
    ed.set_clipboard_items(["trusted"], kind="items")

    assert ed.exec_command_line("set cap.clipboard-read true") is True
    with ed.script_context(origin_id="script-a"):
        ed.vm.host_fns["ed.clipboard"](ed.vm)
        assert ed.vm.stack.pop() == "trusted"

    assert ed.exec_command_line("set cap.clipboard-write true") is True
    with ed.script_context(origin_id="script-a"):
        ed.vm.stack.append("override")
        ed.vm.host_fns["ed.set-clipboard"](ed.vm)

    assert ed.clipboard_text() == "override"
    assert ed.clipboard_authority.script_origin_id == "script-a"


def test_script_paste_cannot_read_trusted_internal_clipboard() -> None:
    ed = _editor()
    ed.set_clipboard_items(["trusted"], kind="items")
    before = ed.cur().buf.get_text()

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="clipboard"):
            ed.run_action("Paste")

    assert ed.cur().buf.get_text() == before


def test_failed_plugin_callback_rollback_restores_clipboard_register() -> None:
    ed = _editor()
    ed.set_clipboard_items(["trusted"], kind="items")
    snap = snapshot_plugin_callback_state(ed.vm)

    assert ed.exec_command_line("set cap.clipboard-write true") is True
    with ed.script_context(origin_id="script-a"):
        ed.set_clipboard_items(["temporary"], kind="items")
    assert ed.clipboard_text() == "temporary"

    restore_plugin_callback_state(ed.vm, snap)

    assert ed.clipboard_text() == "trusted"
    assert ed.clipboard_authority.script_context is False


def test_script_cut_selection_denied_before_deleting_text() -> None:
    from micromax_editor.textpos import Cursor

    ed = _editor()
    ed.cur().buf.set_text("alpha beta")
    ed.set_clipboard_items(["trusted"], kind="items")
    eb = ed.cur()
    eb.cursors[0] = Cursor(0, 5)
    eb.sel_anchors[0] = Cursor(0, 0)

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="clipboard"):
            ed.run_action("Cut")

    assert ed.cur().buf.get_text() == "alpha beta"
    assert ed.clipboard_text() == "trusted"
    assert ed.cur().sel_anchors[0] == Cursor(0, 0)
    assert ed.cur().cursors[0] == Cursor(0, 5)


def test_script_cutline_denied_before_deleting_or_appending_to_trusted_clipboard() -> None:
    ed = _editor()
    ed.cur().buf.set_text("alpha\nbeta\n")
    ed.set_clipboard_items(["trusted-line"], kind="lines")
    ed._cutline_accum = True

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="clipboard"):
            ed.run_action("CutLine")

    assert ed.cur().buf.get_text() == "alpha\nbeta\n"
    assert ed.clipboard_items == ["trusted-line"]
    assert ed.clipboard_kind == "lines"
    assert ed._cutline_accum is True


def test_script_cutline_can_accumulate_own_clipboard() -> None:
    ed = _editor()
    ed.cur().buf.set_text("alpha\nbeta\ngamma\n")

    with ed.script_context(origin_id="script-a"):
        assert ed.run_action("CutLine") is True
        assert ed.cur().buf.get_text() == "beta\ngamma\n"
        assert ed.clipboard_items == ["alpha"]
        assert ed.run_action("CutLine") is True
        assert ed.cur().buf.get_text() == "gamma\n"
        assert ed.clipboard_items == ["alpha", "beta"]
        assert ed.clipboard_kind == "lines"
        assert ed.clipboard_authority.script_origin_id == "script-a"
