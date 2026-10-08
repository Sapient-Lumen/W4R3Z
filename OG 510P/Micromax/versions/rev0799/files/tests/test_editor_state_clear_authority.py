from __future__ import annotations

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "0123456789")
    return ed


def _push_jump_at(ed: Editor, col: int) -> None:
    ed.cur().cursors[:] = [Cursor(0, int(col))]
    ed.cur().sel_anchors[:] = [None]
    ed.cur().cursor_ids[:] = [int(col) + 1]
    ed.cur().primary = 0
    assert ed.push_jump() is True


def test_script_cannot_clear_trusted_jumplist() -> None:
    ed = _editor()
    _push_jump_at(ed, 1)
    _push_jump_at(ed, 3)

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="jumplist"):
            ed.clear_jumps()

    assert len(ed.cur().jump_list) == 2
    assert len(ed.cur().jump_list_authority) == 2
    assert ed.cur().jump_index == 1


def test_script_can_clear_own_jumplist_rows() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        _push_jump_at(ed, 2)
        _push_jump_at(ed, 5)
        ed.clear_jumps()

    assert ed.cur().jump_list == []
    assert ed.cur().jump_list_authority == []
    assert ed.cur().jump_index == -1


def test_script_push_jump_cannot_truncate_trusted_forward_tail() -> None:
    ed = _editor()
    _push_jump_at(ed, 1)
    _push_jump_at(ed, 4)
    _push_jump_at(ed, 7)
    assert ed.jump_back() is True
    assert ed.cur().jump_index == 1

    ed.cur().cursors[:] = [Cursor(0, 9)]
    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="truncate"):
            ed.push_jump()

    assert len(ed.cur().jump_list) == 3
    assert ed.cur().jump_index == 1
    assert ed.cur().cursors[0].col == 9


def test_script_push_jump_cannot_drop_oldest_trusted_jumplist_row() -> None:
    ed = _editor()
    eb = ed.cur()
    eb.jump_list[:] = [ed._snapshot_cursor_only(eb) for _ in range(100)]
    eb.jump_list_authority[:] = []  # legacy rows default to trusted/user-owned
    eb.jump_index = 99
    eb.cursors[:] = [Cursor(0, 8)]

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="drop-oldest"):
            ed.push_jump()

    assert len(eb.jump_list) == 100
    assert eb.jump_index == 99


def test_script_cannot_clear_recent_files_via_hostcall_fallback() -> None:
    ed = _editor()
    ed.recent_files[:] = ["a.txt", "b.txt"]

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="recent-file MRU"):
            ed.vm.host_fns["ed.recent-clear-count"](ed.vm)

    assert ed.recent_files == ["a.txt", "b.txt"]
    assert ed.vm.stack == []


def test_interactive_recent_clear_still_works() -> None:
    ed = _editor()
    ed.recent_files[:] = ["a.txt", "b.txt"]

    assert ed.exec_command_line("recent clear") is True

    assert ed.recent_files == []
    assert ed.messages[-1] == "recent cleared: forgot 2 recent files"


def test_script_cannot_clear_or_pop_trusted_messages() -> None:
    ed = _editor()
    ed.messages[:] = ["important", "later"]

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="messages"):
            ed.vm.host_fns["ed.pop-message"](ed.vm)
        with pytest.raises(PermissionError, match="messages"):
            ed.vm.host_fns["ed.clear-messages"](ed.vm)

    assert ed.messages == ["important", "later"]
    assert ed.vm.stack == []


def test_interactive_message_clear_still_works() -> None:
    ed = _editor()
    ed.messages[:] = ["important"]

    ed.vm.host_fns["ed.clear-messages"](ed.vm)

    assert ed.messages == []


def test_script_can_clear_own_recent_files_but_not_mixed_rows() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("own-a.txt") is True
        assert ed.clear_recent_files() == 1

    assert ed.recent_files == []
    ed.recent_files[:] = ["trusted.txt"]
    ed.recent_files_authority[:] = []
    with ed.script_context(origin_id="script-a"):
        assert ed._push_recent_file("own-b.txt") is True
        with pytest.raises(PermissionError, match="recent-file MRU"):
            ed.clear_recent_files()

    assert ed.recent_files == ["own-b.txt", "trusted.txt"]


def test_script_can_clear_own_messages_but_not_mixed_log() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.message("mine")
        assert ed.clear_messages() == 1

    assert ed.messages == []
    ed.message("trusted")
    with ed.script_context(origin_id="script-a"):
        ed.message("mine")
        with pytest.raises(PermissionError, match="messages"):
            ed.clear_messages()

    assert ed.messages == ["trusted", "mine"]
    assert len(ed.message_authority) == 2


def test_history_clear_capability_allows_script_to_clear_trusted_state() -> None:
    ed = _editor()
    ed.messages[:] = ["important"]
    ed.message_authority[:] = []
    ed.recent_files[:] = ["a.txt", "b.txt"]
    ed.recent_files_authority[:] = []
    _push_jump_at(ed, 1)
    _push_jump_at(ed, 3)

    assert ed.exec_command_line("set cap.history-clear true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.clear_messages() >= 1
        assert ed.clear_recent_files() == 2
        ed.clear_jumps()

    assert ed.messages == []
    assert ed.message_authority == []
    assert ed.recent_files == []
    assert ed.recent_files_authority == []
    assert ed.cur().jump_list == []
    assert ed.cur().jump_list_authority == []


def test_script_cannot_replay_trusted_help_history() -> None:
    ed = _editor()
    ed._help_stack[:] = [ed._help_history_entry("vision", line=0, col=0)]
    ed._help_stack_authority[:] = []  # legacy rows default to trusted/user-owned
    active = ed.active

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="help history"):
            ed.help_back()

    assert ed.active == active
    assert len(ed._help_stack) == 1
    assert ed.current_help_doc_topic() is None


def test_script_can_replay_own_help_history() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed._push_help_history("back", ed._help_history_entry("vision", line=0, col=0))
        assert ed.help_back() is True

    assert ed._help_stack == []
    assert ed.current_help_doc_topic() == "vision"


def test_script_cannot_prune_trusted_help_history() -> None:
    ed = _editor()
    ed._help_stack[:] = [ed._help_history_entry("zzz-no-such-doc", line=0, col=0)]
    ed._help_stack_authority[:] = []

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="help history"):
            ed.help_prune()

    assert len(ed._help_stack) == 1
    assert ed._help_history_topic(ed._help_stack[0]) == "zzz-no-such-doc"


def test_history_clear_capability_allows_script_to_prune_trusted_help_history() -> None:
    ed = _editor()
    ed._help_stack[:] = [ed._help_history_entry("zzz-no-such-doc", line=0, col=0)]
    ed._help_stack_authority[:] = []

    assert ed.exec_command_line("set cap.history-clear true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.help_prune() is True

    assert ed._help_stack == []


def test_history_clear_capability_does_not_replay_trusted_help_history() -> None:
    ed = _editor()
    ed._help_stack[:] = [ed._help_history_entry("vision", line=0, col=0)]
    ed._help_stack_authority[:] = []
    assert ed.exec_command_line("set cap.history-clear true") is True

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="help history"):
            ed.help_back()

    assert ed.current_help_doc_topic() is None
    assert len(ed._help_stack) == 1
