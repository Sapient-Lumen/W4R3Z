from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.hostcall_transactions import capture_messages, restore_messages
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state
from micromax_editor.runtime_policy import RuntimeRegistrationAuthority


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*messages*", "")
    return ed


def test_script_cannot_pop_or_clear_trusted_messages() -> None:
    ed = _editor()
    ed.message("trusted")
    ed.message("also trusted")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="messages"):
            ed.pop_message()
        with pytest.raises(PermissionError, match="messages"):
            ed.clear_messages()

    assert ed.messages == ["trusted", "also trusted"]
    assert [auth.script_context for auth in ed.message_authority] == [False, False]


def test_script_can_pop_and_clear_own_messages() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.message("first")
        ed.message("second")
        assert ed.pop_message() == "first"
        assert ed.clear_messages() == 1

    assert ed.messages == []
    assert ed.message_authority == []


def test_independent_script_cannot_clear_other_script_messages() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.message("owned by a")

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_messages()

    assert ed.messages == ["owned by a"]
    assert ed.message_authority[0].script_origin_id == "script-a"


def test_history_clear_capability_allows_script_to_clear_trusted_message_log() -> None:
    ed = _editor()
    ed.message("trusted")
    assert ed.exec_command_line("set cap.history-clear true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.clear_messages() >= 1

    assert ed.messages == []
    assert ed.message_authority == []


def test_capture_restore_preserves_message_authority() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.message("script-owned")
    saved = capture_messages(ed)

    ed.messages[:] = []
    ed.message_authority[:] = []
    restore_messages(ed, saved)

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_messages()

    assert ed.messages == ["script-owned"]
    assert ed.message_authority[0].script_origin_id == "script-a"


def test_ed_capture_messages_restores_message_authority_sidecar() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.message("script-owned")

    ed.vm.eval('[ "temporary" "ed.msg" hostcall ] "ed.capture-messages" hostcall')
    ok = ed.vm.pop_int()
    captured = ed.vm.pop_list()

    assert ok == 1
    assert captured == ["temporary"]
    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_messages()
    assert ed.messages == ["script-owned"]
    assert ed.message_authority[0].script_origin_id == "script-a"


def test_with_messages_restores_message_authority_after_failure() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.message("script-owned")

    with pytest.raises(Exception):
        ed.vm.eval('[ "temp" "ed.msg" hostcall bogus-message-word ] "ed.with-messages" hostcall')

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_messages()
    assert ed.messages == ["script-owned"]
    assert ed.message_authority[0].script_origin_id == "script-a"


def test_plugin_callback_snapshot_restores_message_log_authority() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.message("script-owned")
    snap = snapshot_plugin_callback_state(ed.vm)

    ed.messages[:] = []
    ed.message_authority[:] = []
    with ed.script_context(origin_id="script-b"):
        ed.message("script-b")

    restore_plugin_callback_state(ed.vm, snap)

    with ed.script_context(origin_id="script-c"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_messages()
    assert ed.messages == ["script-owned", "script-b"]
    assert ed.message_authority[0].script_origin_id == "script-a"
    assert ed.message_authority[1].script_origin_id == "script-b"


def test_script_message_reads_hide_trusted_and_other_origin_rows() -> None:
    ed = _editor()
    ed.message("trusted secret path /tmp/private")
    with ed.script_context(origin_id="script-a"):
        ed.message("owned by a")
    with ed.script_context(origin_id="script-b"):
        ed.message("owned by b")

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval('"ed.messages" hostcall')
        assert ed.vm.pop_list() == ["owned by a"]
        ed.vm.eval('"ed.last-message" hostcall')
        assert ed.vm.pop_str() == "owned by a"
        assert ed.status_model()["last_message"] == "owned by a"

    with ed.script_context(origin_id="script-b"):
        ed.vm.eval('"ed.messages" hostcall')
        assert ed.vm.pop_list() == ["owned by b"]
        ed.vm.eval('"ed.last-message" hostcall')
        assert ed.vm.pop_str() == "owned by b"


def test_message_read_capability_allows_script_to_read_protected_rows() -> None:
    ed = _editor()
    ed.message("trusted")
    with ed.script_context(origin_id="script-a"):
        ed.message("owned")

    with ed.script_context(origin_id="script-b"):
        ed.vm.eval('"ed.messages" hostcall')
        assert ed.vm.pop_list() == []

    assert ed.exec_command_line("set cap.message-read true") is True
    with ed.script_context(origin_id="script-b"):
        ed.vm.eval('"ed.messages" hostcall')
        rows = ed.vm.pop_list()
        assert rows[:2] == ["trusted", "owned"]
        assert rows[-1] == "set: cap.message-read=True"
        ed.vm.eval('"ed.last-message" hostcall')
        assert ed.vm.pop_str() == "set: cap.message-read=True"


def test_capture_messages_returns_only_visible_rows_for_script_origin() -> None:
    ed = _editor()

    def trusted_emit(vm):
        ed.messages.append("trusted-inside-capture")
        ed.message_authority.append(RuntimeRegistrationAuthority(script_context=False))

    ed.vm.register_host("test.trusted-emit", trusted_emit)
    with ed.script_context(origin_id="script-a"):
        ed.vm.eval('[ "script-owned" "ed.msg" hostcall "test.trusted-emit" hostcall ] "ed.capture-messages" hostcall')
        ok = ed.vm.pop_int()
        captured = ed.vm.pop_list()

    assert ok == 1
    assert captured == ["script-owned"]
    assert ed.messages == []


def test_status_model_hides_trusted_last_message_in_script_context() -> None:
    ed = _editor()
    ed.message("trusted")
    with ed.script_context(origin_id="script-a"):
        assert ed.status_model()["last_message"] == ""
        ed.message("script-owned")
        assert ed.status_model()["last_message"] == "script-owned"


def test_message_read_capability_is_advertised_when_enabled() -> None:
    ed = _editor()
    ed.vm.eval('"ed.message-read" host.feature?', filename="<message-read-capability>")
    assert ed.vm.stack.pop() == 0
    assert ed.exec_command_line("set cap.message-read true") is True
    ed.vm.eval('"ed.message-read" host.feature?', filename="<message-read-capability>")
    assert ed.vm.stack.pop() == 1
