from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import (
    cleanup_runtime_group,
    restore_runtime_registrations,
    retag_runtime_group,
    snapshot_runtime_registrations,
)


def _hostcall(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<test>")


def _mark_target(ed: Editor, name: str) -> tuple[str, int, int]:
    buf, cur = ed.marks[name]
    return (buf, int(cur.line), int(cur.col))


def test_script_mark_set_cannot_overwrite_trusted_mark_and_preserves_operand() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\nbravo\n")
    ed.cur().cursors[0].line = 0
    ed.cur().cursors[0].col = 1
    assert ed.mark_set("home")
    assert _mark_target(ed, "home") == ("main", 0, 1)

    ed.cur().cursors[0].line = 1
    ed.cur().cursors[0].col = 2
    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["home"]
        with pytest.raises(Exception, match="script context cannot modify mark: home"):
            _hostcall(ed, "ed.mark-set")

    assert ed.vm.stack == ["home"]
    assert _mark_target(ed, "home") == ("main", 0, 1)


def test_script_mark_set_idempotent_trusted_repeat_is_noop_not_ownership_change() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\n")
    ed.cur().cursors[0].line = 0
    ed.cur().cursors[0].col = 3
    assert ed.mark_set("same")
    trusted_authority = ed._mark_authority["same"]

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["same"]
        _hostcall(ed, "ed.mark-set")

    assert ed.vm.stack == [1]
    assert _mark_target(ed, "same") == ("main", 0, 3)
    assert ed._mark_authority["same"] is trusted_authority
    assert ed._mark_authority["same"].script_context is False


def test_independent_scripts_cannot_retarget_each_others_marks() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\nbravo\n")

    with ed.script_context(origin_id="script-a"):
        ed.cur().cursors[0].line = 0
        ed.cur().cursors[0].col = 0
        ed.vm.stack[:] = ["mine"]
        _hostcall(ed, "ed.mark-set")
    assert ed.vm.stack == [1]
    assert _mark_target(ed, "mine") == ("main", 0, 0)

    with ed.script_context(origin_id="script-b"):
        ed.cur().cursors[0].line = 1
        ed.cur().cursors[0].col = 1
        ed.vm.stack[:] = ["mine"]
        with pytest.raises(Exception, match="different script origin"):
            _hostcall(ed, "ed.mark-set")

    assert ed.vm.stack == ["mine"]
    assert _mark_target(ed, "mine") == ("main", 0, 0)

    with ed.script_context(origin_id="script-a"):
        ed.cur().cursors[0].line = 1
        ed.cur().cursors[0].col = 1
        ed.vm.stack[:] = ["mine"]
        _hostcall(ed, "ed.mark-set")
    assert ed.vm.stack == [1]
    assert _mark_target(ed, "mine") == ("main", 1, 1)


def test_with_undo_failure_restores_mark_authority_sidecar() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\n")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(Exception, match="Unknown word"):
            ed.vm.eval(
                '"group" [ "temp" "ed.mark-set" hostcall drop missing-word ] "ed.with-undo" hostcall',
                filename="<test>",
            )

    assert "temp" not in ed.marks
    assert "temp" not in ed._mark_authority


def test_runtime_registration_snapshot_restores_marks_after_failed_plugin_callback() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\nbravo\n")
    ed.cur().cursors[0].line = 0
    ed.cur().cursors[0].col = 0
    assert ed.mark_set("keep")
    snap = snapshot_runtime_registrations(ed.vm)

    ed.vm.current_editor_group = "plugin:demo"
    ed.vm.current_plugin_load_root = "/tmp/demo"
    ed.vm.current_plugin_generation = 7
    with ed.script_context(origin_id="plugin:demo"):
        ed.cur().cursors[0].line = 1
        ed.cur().cursors[0].col = 1
        assert ed.mark_set("plugin-mark")
    ed.vm.current_editor_group = None
    ed.vm.current_plugin_load_root = None
    ed.vm.current_plugin_generation = None
    assert "plugin-mark" in ed.marks

    restore_runtime_registrations(ed.vm, snap)

    assert sorted(ed.marks) == ["keep"]
    assert sorted(ed._mark_authority) == ["keep"]
    assert _mark_target(ed, "keep") == ("main", 0, 0)


def test_plugin_runtime_group_cleanup_and_retag_cover_marks() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\n")

    ed.vm.current_editor_group = "plugin:demo#reload1"
    ed.vm.current_plugin_load_root = "/tmp/demo"
    ed.vm.current_plugin_generation = 2
    with ed.script_context(origin_id="plugin:demo"):
        assert ed.mark_set("owned")
    assert ed._mark_authority["owned"].group == "plugin:demo#reload1"

    retag_runtime_group(ed.vm, "plugin:demo#reload1", "plugin:demo")
    assert ed._mark_authority["owned"].group == "plugin:demo"

    cleanup_runtime_group(ed.vm, "plugin:demo")
    assert "owned" not in ed.marks
    assert "owned" not in ed._mark_authority
