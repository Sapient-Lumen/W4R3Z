from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*palette*", "")
    return ed


def _recent_names(ed: Editor) -> list[str]:
    return [str(row[0]) for row in ed.command_palette_recent_rows()]


def test_script_cannot_read_trusted_palette_recent_rows() -> None:
    ed = _editor()
    assert ed._record_palette_recent("command", "help") is True

    assert _recent_names(ed) == ["help"]
    with ed.script_context(origin_id="script-a"):
        assert ed.command_palette_recent_rows() == []
        sections = ed.command_palette_section_rows("")

    assert not any(str(label) == "Recent" for label, _items in sections)



def test_history_clear_capability_does_not_grant_palette_recent_read() -> None:
    ed = _editor()
    assert ed._record_palette_recent("command", "help") is True
    assert ed.exec_command_line("set cap.history-clear true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.command_palette_recent_rows() == []


def test_script_can_read_own_palette_recent_rows() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        assert ed._record_palette_recent("command", "help") is True
        assert _recent_names(ed) == ["help"]

    with ed.script_context(origin_id="script-b"):
        assert ed.command_palette_recent_rows() == []



def test_script_palette_recent_update_does_not_evict_trusted_full_mru() -> None:
    ed = _editor()
    ed._palette_recent_limit = 1
    assert ed._record_palette_recent("command", "help") is True

    with ed.script_context(origin_id="script-a"):
        assert ed._record_palette_recent("command", "quit") is False
        assert ed.command_palette_recent_rows() == []

    assert ed._palette_recent == [("command", "help")]
    assert len(ed._palette_recent_authority) == 1
    assert ed._palette_recent_authority[0].script_context is False



def test_script_cannot_reorder_trusted_palette_recent_entry() -> None:
    ed = _editor()
    assert ed._record_palette_recent("command", "help") is True

    with ed.script_context(origin_id="script-a"):
        assert ed._record_palette_recent("command", "help") is False

    assert ed._palette_recent == [("command", "help")]
    assert ed._palette_recent_authority[0].script_context is False



def test_plugin_callback_snapshot_restores_palette_recent_authority() -> None:
    ed = _editor()
    assert ed._record_palette_recent("command", "help") is True
    snap = snapshot_plugin_callback_state(ed.vm)

    with ed.script_context(origin_id="script-a"):
        assert ed._record_palette_recent("command", "quit") is True

    assert ed._palette_recent[0] == ("command", "quit")
    restore_plugin_callback_state(ed.vm, snap)

    assert ed._palette_recent == [("command", "help")]
    assert len(ed._palette_recent_authority) == 1
    assert ed._palette_recent_authority[0].script_context is False
