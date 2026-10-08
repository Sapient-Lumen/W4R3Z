from __future__ import annotations

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "abcdef")
    return ed


def test_script_cannot_pop_trusted_selection_recovery_stack() -> None:
    ed = _editor()
    ed.cur().cursors[:] = [ed.cur().buf.clamp(Cursor(0, 0))]
    ed.push_selections()
    ed.cur().cursors[:] = [ed.cur().buf.clamp(Cursor(0, 3))]

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="selection recovery stack"):
            ed.pop_selections()

    assert len(ed.cur().sel_stack) == 1
    assert ed.cur().cursors[0].col == 3


def test_script_can_pop_own_selection_recovery_stack() -> None:
    ed = _editor()
    ed.cur().cursors[0].col = 1
    with ed.script_context(origin_id="script-a"):
        ed.push_selections()
        ed.cur().cursors[0].col = 4
        assert ed.pop_selections() is True

    assert ed.cur().cursors[0].col == 1
    assert ed.cur().sel_stack == []
    assert ed.cur().sel_stack_authority == []


def test_independent_script_cannot_clear_other_script_selection_stack() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.push_selections()

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_saved_selections()

    assert len(ed.cur().sel_stack) == 1


def test_set_selections_denial_preserves_cursor_state_stack_and_operand() -> None:
    ed = _editor()
    ed.push_selections()
    original_col = ed.cur().cursors[0].col
    ed.vm.stack[:] = [[[0, 0, 0, 4]]]

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="selection recovery stack"):
            ed.vm.host_fns["ed.set-selections"](ed.vm)

    assert ed.vm.stack == [[[0, 0, 0, 4]]]
    assert ed.cur().cursors[0].col == original_col
    assert len(ed.cur().sel_stack) == 1


def test_with_undo_failure_restores_selection_stack_authority() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed.push_selections()
    assert ed.cur().sel_stack_authority[-1].script_origin_id == "script-a"

    snapshot = ed._buffer_transaction_snapshot()
    with ed.script_context(origin_id="script-a"):
        ed.clear_saved_selections()
    assert ed.cur().sel_stack == []

    ed._restore_buffer_transaction_snapshot(snapshot)
    assert len(ed.cur().sel_stack) == 1
    assert ed.cur().sel_stack_authority[-1].script_origin_id == "script-a"

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.pop_selections()
