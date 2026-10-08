from __future__ import annotations

import pytest
from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*recent*", "abcdef\n")
    return ed


def test_script_cannot_clear_trusted_recent_files() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="recent-file MRU"):
            ed.clear_recent_files()

    assert ed.recent_files == ["trusted.txt"]
    assert ed.recent_files_authority[0].script_context is False


def test_recent_clear_hostcall_does_not_bypass_authority_guard() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="recent-file MRU"):
            ed.vm.host_fns["ed.recent-clear-count"](ed.vm)

    assert ed.recent_files == ["trusted.txt"]
    assert ed.vm.stack == []


def test_script_recent_update_skips_instead_of_dropping_trusted_full_mru() -> None:
    ed = _editor()
    ed._recent_limit = 1
    assert ed._push_recent_file("trusted.txt") is True

    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script.txt") is False

    assert ed.recent_files == ["trusted.txt"]
    assert len(ed.recent_files_authority) == 1
    assert ed.recent_files_authority[0].script_context is False


def test_script_can_clear_own_recent_entries() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script.txt") is True
        assert ed.clear_recent_files() == 1

    assert ed.recent_files == []
    assert ed.recent_files_authority == []


def test_independent_script_cannot_clear_other_script_recent_entry() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script-a.txt") is True

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_recent_files()

    assert ed.recent_files == ["script-a.txt"]
    assert ed.recent_files_authority[0].script_origin_id == "script-a"


def test_buffer_transaction_snapshot_restores_recent_authority() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True
    snap = ed._buffer_transaction_snapshot()

    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script.txt") is True

    assert ed.recent_files[0] == "script.txt"
    ed._restore_buffer_transaction_snapshot(snap)

    assert ed.recent_files == ["trusted.txt"]
    assert ed.recent_files_authority[0].script_context is False


def test_plugin_callback_snapshot_restores_recent_register() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True
    snap = snapshot_plugin_callback_state(ed.vm)

    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script.txt") is True

    assert ed.recent_files[0] == "script.txt"
    restore_plugin_callback_state(ed.vm, snap)

    assert ed.recent_files == ["trusted.txt"]
    assert len(ed.recent_files_authority) == 1
    assert ed.recent_files_authority[0].script_context is False


def _call_host(ed: Editor, name: str, *args: object) -> object:
    ed.vm.stack.clear()
    for arg in args:
        ed.vm.stack.append(arg)
    ed.vm.host_fns[name](ed.vm)
    if not ed.vm.stack:
        return None
    return ed.vm.stack.pop()


def test_script_cannot_read_trusted_recent_file_paths() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.visible_recent_files() == []
        assert _call_host(ed, "ed.recent") == []
        assert ed.recent_inventory_rows() == []
        assert ed.recent_prompt_rows() == []
        assert ed.command_palette_recent_file_rows() == []
        assert ed.recent_detail_row("trusted.txt") is None
        assert ed.recent_detail_row_by_index(1) is None

    assert ed.visible_recent_files() == ["trusted.txt"]


def test_history_clear_capability_does_not_grant_recent_read() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True
    ed.exec_command_line("set cap.history-clear true")

    with ed.script_context(origin_id="script-a"):
        assert ed.visible_recent_files() == []
        assert _call_host(ed, "ed.recent") == []


def test_recent_read_capability_reveals_trusted_recent_rows() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True
    ed.exec_command_line("set cap.recent-read true")

    with ed.script_context(origin_id="script-a"):
        assert ed.visible_recent_files() == ["trusted.txt"]
        assert _call_host(ed, "ed.recent") == ["trusted.txt"]
        assert ed.recent_inventory_rows()[0][1] == "trusted.txt"
        assert ed.recent_detail_row_by_index(1)[1] == "trusted.txt"  # type: ignore[index]


def test_script_can_read_own_recent_but_not_other_script_recent() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script-a.txt") is True
        assert ed.visible_recent_files() == ["script-a.txt"]

    with ed.script_context(origin_id="script-b"):
        assert ed.visible_recent_files() == []
        assert ed.recent_detail_row("script-a.txt") is None


def test_command_palette_and_path_completion_hide_trusted_recent_paths() -> None:
    ed = _editor()
    assert ed._push_recent_file("/tmp/trusted-recent-secret.txt") is True

    with ed.script_context(origin_id="script-a"):
        rows = ed.command_palette_apropos_rows("")
        assert all("trusted-recent-secret" not in str(row) for row in rows)
        candidates = ed._known_path_completion_candidates(Path("/tmp"), "trusted-recent")
        assert candidates == []



def test_recent_command_opens_visible_slot_not_hidden_raw_slot(tmp_path: Path) -> None:
    ed = _editor()
    install_editor_hostcalls(ed)
    trusted = tmp_path / "trusted-secret.txt"
    script_owned = tmp_path / "script-owned.txt"
    trusted.write_text("trusted\n", encoding="utf-8")
    script_owned.write_text("script\n", encoding="utf-8")

    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file(str(script_owned)) is True
    # Put a trusted row before the script row in raw MRU order.  Script-visible
    # slot #1 must still refer to the script-owned row, not raw MRU index 0.
    assert ed._push_recent_file(str(trusted)) is True
    ed.exec_command_line("set cap.fs-open true")

    with ed.script_context(origin_id="script-a"):
        assert ed.visible_recent_files() == [str(script_owned)]
        assert ed.exec_command_line("recent 1") is True

    assert ed.cur().buf.path == str(script_owned)
    assert ed.cur().buf.get_text() == "script\n"
    assert ed.active != str(trusted)


def test_script_recent_slots_are_visible_slots_not_raw_slots() -> None:
    ed = _editor()
    assert ed._push_recent_file("trusted.txt") is True
    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("script.txt") is True
        assert ed.recent_inventory_rows()[0][0] == 1
        assert ed.recent_inventory_rows()[0][1] == "script.txt"
        assert ed.recent_detail_row_by_index(1)[1] == "script.txt"  # type: ignore[index]
        assert ed.recent_detail_row_by_index(2) is None
