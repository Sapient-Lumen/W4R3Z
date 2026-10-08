from __future__ import annotations

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "zero\none\ntwo\nthree\n")
    return ed


def _set_col(ed: Editor, col: int) -> None:
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, int(col))]
    eb.sel_anchors[:] = [None]
    eb.cursor_ids[:] = [1]
    eb.primary = 0


def _push_at(ed: Editor, col: int) -> None:
    _set_col(ed, col)
    assert ed.push_jump() is True


def test_script_cannot_clear_trusted_jumplist() -> None:
    ed = _editor()
    _push_at(ed, 0)
    _push_at(ed, 2)
    assert len(ed.cur().jump_list) == 2

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="jumplist"):
            ed.clear_jumps()

    assert len(ed.cur().jump_list) == 2
    assert ed.cur().jump_index == 1


def test_script_can_clear_own_jumplist_rows() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        _push_at(ed, 0)
        _push_at(ed, 1)
        ed.clear_jumps()

    assert ed.cur().jump_list == []
    assert ed.cur().jump_list_authority == []
    assert ed.cur().jump_index == -1


def test_independent_script_cannot_clear_other_script_jumplist_rows() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        _push_at(ed, 0)

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_jumps()

    assert len(ed.cur().jump_list) == 1
    assert ed.cur().jump_list_authority[-1].script_origin_id == "script-a"


def test_script_push_jump_cannot_truncate_trusted_forward_tail() -> None:
    ed = _editor()
    _push_at(ed, 0)
    _push_at(ed, 1)
    _push_at(ed, 2)
    assert ed.jump_to_index(1) is True
    before_rows = list(ed.cur().jump_list)
    before_auth = list(ed.cur().jump_list_authority)

    with ed.script_context(origin_id="script-a"):
        _set_col(ed, 3)
        with pytest.raises(PermissionError, match="truncate"):
            ed.push_jump()

    assert ed.cur().jump_list == before_rows
    assert ed.cur().jump_list_authority == before_auth
    assert ed.cur().jump_index == 1


def test_script_cannot_navigate_trusted_jumplist() -> None:
    ed = _editor()
    _push_at(ed, 0)
    _push_at(ed, 2)
    assert ed.cur().jump_index == 1
    _set_col(ed, 4)

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError, match="jumpback"):
            ed.jump_back()

    assert ed.cur().jump_index == 1
    assert ed.cur().cursors[0].col == 4


def test_script_can_navigate_own_jumplist_rows() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        _push_at(ed, 0)
        _push_at(ed, 2)
        _set_col(ed, 4)
        assert ed.jump_back() is True

    assert ed.cur().jump_index == 0
    assert ed.cur().cursors[0].col == 0


def test_transaction_restore_preserves_jumplist_authority() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        _push_at(ed, 0)
    assert ed.cur().jump_list_authority[-1].script_origin_id == "script-a"

    snap = ed._buffer_transaction_snapshot()
    with ed.script_context(origin_id="script-a"):
        ed.clear_jumps()
    assert ed.cur().jump_list == []

    ed._restore_buffer_transaction_snapshot(snap)
    assert len(ed.cur().jump_list) == 1
    assert ed.cur().jump_list_authority[-1].script_origin_id == "script-a"

    with ed.script_context(origin_id="script-b"):
        with pytest.raises(PermissionError, match="different script origin"):
            ed.clear_jumps()

def test_script_push_jump_full_trusted_history_does_not_partially_append() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "".join(f"line {i}\n" for i in range(120)))
    eb = ed.cur()
    for line in range(100):
        eb.cursors[:] = [Cursor(line, 0)]
        eb.sel_anchors[:] = [None]
        eb.cursor_ids[:] = [1]
        eb.primary = 0
        assert ed.push_jump() is True
    before_rows = list(eb.jump_list)
    before_auth = list(eb.jump_list_authority)
    before_index = int(eb.jump_index)

    with ed.script_context(origin_id="script-a"):
        eb.cursors[:] = [Cursor(101, 0)]
        with pytest.raises(PermissionError, match="drop-oldest"):
            ed.push_jump()

    assert eb.jump_list == before_rows
    assert eb.jump_list_authority == before_auth
    assert eb.jump_index == before_index
