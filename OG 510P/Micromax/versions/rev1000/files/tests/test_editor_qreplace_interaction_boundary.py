from __future__ import annotations

from micromax_editor.editor import Editor


def test_qreplace_direct_accept_refuses_after_buffer_becomes_readonly() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None
    ed.cur().local_options["readonly"] = True

    assert ed.qreplace_yes() is False
    assert ed.cur().buf.get_text() == "one one"
    assert ed.qreplace is not None
    assert ed.current_capture_key_mode() == "qreplace"
    assert ed.status_model()["last_message"] == "qreplace: read-only buffer"

    assert ed.qreplace_quit() is True
    assert ed.qreplace is None


def test_qreplace_buffer_switch_finalizes_original_buffer_undo() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one one")
    main = ed.cur()

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert main.buf.get_text() == "X one one"
    assert main.sel_anchors[main.primary] is not None

    ed.new_buffer("other", "untouched")

    assert ed.active == "other"
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert main.sel_anchors[main.primary] is None
    assert ed.undo.can_undo() is True
    assert ed.run_action("Undo") is True
    assert main.buf.get_text() == "one one one"
    assert ed.cur().buf.get_text() == "untouched"


def test_qreplace_survives_target_rename_by_object_identity() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")
    target = ed.cur()

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert ed.rename_buffer("main", "renamed") is True

    assert ed.qreplace is not None
    assert ed.qreplace.buffer_name == "renamed"
    assert ed._qreplace_target_buffer() is target
    assert ed.selection_text() == "one"
    assert ed.qreplace_last() is True
    assert target.buf.get_text() == "X X"

    assert ed.run_action("Undo") is True
    assert target.buf.get_text() == "one one"
    assert ed.active == "renamed"


def test_qreplace_runtime_cleanup_clears_only_target_and_keeps_undo() -> None:
    from micromax_editor.buffer import Cursor

    ed = Editor()
    ed.new_buffer("main", "one one")
    main = ed.cur()
    ed.new_buffer("other", "safe")
    other = ed.cur()
    assert ed.switch_buffer("main") is True

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert main.buf.get_text() == "X one"
    assert main.sel_anchors[main.primary] is not None

    # Simulate a runtime owner restoring/removing interaction state while another
    # buffer is current. The owner must not clear the unrelated active selection.
    other.sel_anchors[0] = Cursor(0, 0)
    other.cursors[0] = Cursor(0, 2)
    ed.active = "other"
    ed._clear_qreplace_runtime_row()

    assert ed.qreplace is None
    assert main.sel_anchors[main.primary] is None
    assert other.sel_anchors[0] == Cursor(0, 0)
    assert other.cursors[0] == Cursor(0, 2)
    assert ed.undo.can_undo() is True
    assert ed.undo.undo() is True
    assert main.buf.get_text() == "one one"


def test_qreplace_close_drops_identity_without_retargeting_reused_name() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")
    old = ed.cur()
    ed.new_buffer("other", "safe")
    assert ed.switch_buffer("main") is True

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert old.buf.get_text() == "X one"

    ed.close_buffers(["main"], keep="other")
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.undo.can_undo() is False

    ed.new_buffer("main", "fresh")
    fresh = ed.cur()
    assert fresh is not old
    assert fresh.buf.get_text() == "fresh"
    assert fresh.sel_anchors[fresh.primary] is None


def test_replacing_live_qreplace_finalizes_accepted_edits_before_new_error() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")
    target = ed.cur()

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert target.buf.get_text() == "X one"

    assert ed.begin_query_replace("", "Y", literal=True) is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.status_model()["last_message"] == "qreplace: empty search"
    assert ed.undo.can_undo() is True
    assert ed.undo.undo() is True
    assert target.buf.get_text() == "one one"


def test_external_insert_action_closes_qreplace_before_using_its_selection() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.selection_text() == "one"

    ed.input["text"] = "ZZ"
    assert ed.run_action("InsertText") is True

    # The insert starts after qreplace has cleared its transient selection.  It
    # must not replace the old match, and a delayed qreplace answer is inert.
    assert ed.cur().buf.get_text() == "oneZZ one"
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.status_model()["last_message"] == "qreplace: canceled (0 replaced)"
    assert ed.qreplace_yes() is False
    assert ed.cur().buf.get_text() == "oneZZ one"

    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "one one"


def test_external_action_preserves_qreplace_then_action_undo_order() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert ed.cur().buf.get_text() == "X one"

    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "X one!"
    assert ed.qreplace is None

    # The later insert is undone first; the accepted qreplace transaction is
    # still available as the next independent undo row.
    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "X one"
    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "one one"


def test_direct_recorded_edit_splits_from_live_qreplace_undo_transaction() -> None:
    from micromax_editor.edit_boundary import set_buffer_text_undoably

    ed = Editor()
    ed.new_buffer("main", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert ed.cur().buf.get_text() == "X one"

    # Direct host-style edits record after mutation.  The central undo recorder
    # uses their before snapshot to close qreplace at the correct boundary.
    set_buffer_text_undoably(ed, "tracked outside edit", description="SetText")

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "tracked outside edit"

    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "X one"
    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "one one"


def test_qreplace_refuses_stale_coordinates_after_untracked_buffer_change() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    witness_version = ed.qreplace.buffer_witness.version if ed.qreplace else None
    ed.cur().buf.set_text("ZZ one")
    assert ed.cur().buf.version != witness_version

    assert ed.qreplace_yes() is False
    assert ed.cur().buf.get_text() == "ZZ one"
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert (
        ed.status_model()["last_message"]
        == "qreplace: canceled (buffer changed outside session)"
    )


def test_stale_abort_never_clobbers_untracked_change_with_grouped_undo() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_yes() is True
    assert ed.cur().buf.get_text() == "X one"

    # This bypasses the editor's undo boundary but still advances Buffer.version.
    # A broad qreplace snapshot undo would erase this outside text, so fail
    # closed and keep the accepted replacement without manufacturing unsafe undo.
    ed.cur().buf.set_text("outside owner text")

    assert ed.qreplace_yes() is False
    assert ed.cur().buf.get_text() == "outside owner text"
    assert ed.qreplace is None
    assert ed.undo.can_undo() is False
    assert (
        ed.status_model()["last_message"]
        == "qreplace: canceled (buffer changed outside session; "
        "1 accepted; grouped undo unavailable)"
    )


def test_every_qreplace_response_fails_closed_after_generation_drift() -> None:
    for response_name in (
        "qreplace_yes",
        "qreplace_no",
        "qreplace_all",
        "qreplace_last",
        "qreplace_quit",
    ):
        ed = Editor()
        ed.new_buffer("main", "one one")
        assert ed.exec_command_line("qreplace one X -l") is True
        ed.cur().buf.set_text("outside one")

        response = getattr(ed, response_name)
        assert response() is False, response_name
        assert ed.cur().buf.get_text() == "outside one", response_name
        assert ed.qreplace is None, response_name
        assert ed.current_capture_key_mode() is None, response_name


def test_restored_qreplace_snapshot_keeps_original_generation_witness() -> None:
    ed = Editor()
    ed.new_buffer("main", "one one")
    assert ed.exec_command_line("qreplace one X -l") is True

    snap = ed._qreplace_state(captured=True)
    ed._qreplace_dispose(record_undo=False, clear_selection=True)
    ed._drop_qreplace_capture_modes()
    ed.cur().buf.set_text("new owner one")

    ed.restore_qreplace_group_state(snap)
    assert ed.qreplace is not None
    assert ed.qreplace_yes() is False
    assert ed.cur().buf.get_text() == "new owner one"
    assert ed.qreplace is None
