from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("trusted", "secret\n", path="/tmp/trusted-secret.txt")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<buffer-authority-test>")
    return list(ed.vm.stack)


def test_script_buffer_inventory_hides_inactive_trusted_open_buffer_metadata() -> None:
    ed = _editor()
    ed.new_buffer("other", "other secret\n", path="/tmp/other-secret.txt")
    ed.switch_buffer("trusted")

    with ed.script_context(origin_id="script-a"):
        # The active buffer remains the ambient object a script was invoked on.
        # Other trusted/user buffers are hidden from list/picker/detail rows.
        assert ed.visible_buffer_names() == ["trusted"]
        assert [row[0] for row in ed.buffer_inventory_rows()] == ["trusted"]
        assert ed.buffer_detail_row("trusted") is not None
        assert ed.buffer_detail_row("other") is None
        assert [row[0] for row in ed.buffer_prompt_rows()] == ["trusted"]
        status = ed.status_model()
        assert status["buffer_name"] == "trusted"
        assert status["path"] == "/tmp/trusted-secret.txt"
        assert _hostcall(ed, "ed.buffers")[-1] == ["trusted"]
        assert _hostcall(ed, "ed.active-buffer")[-1] == "trusted"


def test_script_buffer_read_capability_reveals_buffer_rows_but_not_switch_authority() -> None:
    ed = _editor()
    ed.new_buffer("other", "other\n")
    ed.switch_buffer("trusted")
    assert ed.exec_command_line("set cap.buffer-read true") is True

    with ed.script_context(origin_id="script-a"):
        names = ed.visible_buffer_names()
        assert "trusted" in names and "other" in names
        row = ed.buffer_detail_row("trusted")
        assert row is not None
        assert row[0] == "trusted"
        assert row[6] == "/tmp/trusted-secret.txt"
        with pytest.raises(PermissionError, match="cap.buffer-switch"):
            ed.switch_buffer_checked("other")

    assert ed.active == "trusted"


def test_script_created_inactive_buffer_is_visible_to_same_origin_only() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
        assert ed.visible_buffer_names() == ["own"]
        assert ed.buffer_detail_row("own") is not None

    ed.switch_buffer("trusted")
    with ed.script_context(origin_id="script-b"):
        assert "own" not in ed.visible_buffer_names()
        assert ed.buffer_detail_row("own") is None

    with ed.script_context(origin_id="script-a"):
        assert "own" in ed.visible_buffer_names()
        assert ed.buffer_detail_row("own") is not None


def test_script_cannot_switch_to_trusted_buffer_without_capability_and_operand_survives() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    assert ed.active == "own"

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["trusted"]
        with pytest.raises(Exception, match="script context cannot switch buffer: trusted"):
            ed.vm.stack.append("ed.set-active-buffer")
            ed.vm.eval("hostcall", filename="<buffer-authority-test>")

    assert "trusted" in ed.vm.stack
    assert ed.active == "own"


def test_buffer_switch_capability_is_separate_from_read_capability() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    assert ed.active == "own"
    assert ed.exec_command_line("set cap.buffer-switch true") is True

    ed.new_buffer("other", "other\n")
    ed.switch_buffer("own")

    with ed.script_context(origin_id="script-a"):
        assert ed.switch_buffer_checked("trusted") is True
        # Switch authority makes the target active/ambient, but does not reveal
        # unrelated inactive trusted/user buffers.
        assert "trusted" in ed.visible_buffer_names()
        assert "other" not in ed.visible_buffer_names()
        assert ed.buffer_detail_row("other") is None

    assert ed.active == "trusted"


def test_script_cannot_close_inactive_trusted_clean_buffer_without_discard_capability() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    assert ed.active == "own"

    with ed.script_context(origin_id="script-a"):
        assert ed.close_buffer("trusted") is False

    assert "trusted" in ed.buffers
    assert ed.active == "own"
    assert "script context cannot close buffer: trusted" in ed.messages[-1]
    assert "cap.buffer-discard" in ed.messages[-1]


def test_script_can_close_same_origin_inactive_buffer_without_global_discard_capability() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    ed.switch_buffer("trusted")

    with ed.script_context(origin_id="script-a"):
        assert ed.close_buffer("own") is True

    assert "own" not in ed.buffers
    assert "trusted" in ed.buffers


def test_buffer_discard_capability_allows_closing_inactive_trusted_clean_buffer() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    assert ed.exec_command_line("set cap.buffer-discard true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.close_buffer("trusted") is True

    assert "trusted" not in ed.buffers
    assert ed.active == "own"


def test_script_closeall_refuses_inactive_trusted_clean_buffer_without_discard_capability() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="script context cannot close buffer: trusted"):
            ed.close_buffers(["trusted"], keep="own")

    assert "trusted" in ed.buffers
    assert "own" in ed.buffers
    assert ed.active == "own"


def test_script_with_buffer_denial_preserves_name_and_quotation_operands() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    ed.vm.eval('[ "trusted" "ed.msg" hostcall ]', filename="<buffer-authority-q>")
    q = ed.vm.stack.pop()

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["trusted", q]
        with pytest.raises(Exception, match="script context cannot switch buffer: trusted"):
            ed.vm.stack.append("ed.with-buffer")
            ed.vm.eval("hostcall", filename="<buffer-authority-test>")

    assert ed.vm.stack == ["trusted", q]
    assert ed.active == "own"


def test_script_open_existing_protected_buffer_cannot_launder_through_fs_open(tmp_path) -> None:
    target = tmp_path / "already-open.txt"
    target.write_text("secret\n", encoding="utf-8")
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_file(str(target)) is True
    ed.rename_buffer(str(target), "trusted")

    with ed.script_context(origin_id="script-a"):
        ed.new_buffer("own", "owned\n")
    assert ed.exec_command_line("set cap.fs-open true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.open_file(str(target)) is False

    assert ed.active == "own"
    assert "already open but inaccessible" in ed.messages[-1]
    assert "cap.buffer-switch" in ed.messages[-1]
