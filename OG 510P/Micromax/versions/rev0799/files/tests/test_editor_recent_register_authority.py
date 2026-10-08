from __future__ import annotations

import pytest

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
