from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\nbravo\ncharlie\n")
    return ed


def _set_cursor(ed: Editor, line: int, col: int) -> None:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = int(line)
    eb.cursors[eb.primary].col = int(col)


def _hostcall(ed: Editor, name: str, *args: object) -> None:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<mark-access-test>")


def test_script_cannot_read_trusted_mark_without_capability_and_hostcall_preserves_operand() -> None:
    ed = _editor()
    _set_cursor(ed, 1, 2)
    assert ed.mark_set("trusted") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.mark_rows() == []
        assert ed.mark_inventory_rows() == []
        assert ed.mark_detail_row("trusted") is None
        ed.vm.stack[:] = ["trusted"]
        with pytest.raises(Exception, match="script context cannot read mark: trusted"):
            ed.vm.stack.append("ed.mark-detail-row")
            ed.vm.eval("hostcall", filename="<mark-access-test>")

    assert ed.vm.stack == ["trusted", "ed.mark-detail-row"] or ed.vm.stack == ["trusted"]
    # The important evidence is the operation argument, not the transient hostcall word.
    assert "trusted" in ed.vm.stack


def test_script_can_read_trusted_mark_with_explicit_capability() -> None:
    ed = _editor()
    _set_cursor(ed, 1, 2)
    assert ed.mark_set("trusted") is True
    assert ed.exec_command_line("set cap.mark-read true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.mark_rows() == [["trusted", "main", 1, 2]]
        assert ed.mark_detail_row("trusted") == ["trusted", "main", "2:2", "bravo", 1, 1]
        assert ed.mark_inventory_rows() == [["trusted", "main", "2:2", "bravo", 1, 1]]


def test_script_cannot_jump_to_trusted_mark_without_capability_and_preserves_operand() -> None:
    ed = _editor()
    _set_cursor(ed, 2, 1)
    assert ed.mark_set("trusted") is True
    _set_cursor(ed, 0, 0)

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["trusted"]
        with pytest.raises(Exception, match="script context cannot jump mark: trusted"):
            ed.vm.stack.append("ed.mark-jump")
            ed.vm.eval("hostcall", filename="<mark-access-test>")

    assert "trusted" in ed.vm.stack
    c = ed.primary_cursor()
    assert (c.line, c.col) == (0, 0)


def test_script_can_jump_to_trusted_mark_with_explicit_capability() -> None:
    ed = _editor()
    _set_cursor(ed, 2, 1)
    assert ed.mark_set("trusted") is True
    _set_cursor(ed, 0, 0)
    assert ed.exec_command_line("set cap.mark-jump true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.mark_jump("trusted") is True

    c = ed.primary_cursor()
    assert (c.line, c.col) == (2, 1)
    # Jump permission does not also grant mark inventory/read permission.
    with ed.script_context(origin_id="script-a"):
        assert ed.mark_detail_row("trusted") is None


def test_script_can_read_and_jump_own_mark_without_broad_capability() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        _set_cursor(ed, 1, 0)
        assert ed.mark_set("own") is True
        _set_cursor(ed, 0, 0)
        assert ed.mark_detail_row("own") == ["own", "main", "2:0", "bravo", 1, 0]
        assert ed.mark_jump("own") is True

    c = ed.primary_cursor()
    assert (c.line, c.col) == (1, 0)


def test_independent_scripts_cannot_read_or_jump_each_others_marks() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        _set_cursor(ed, 1, 1)
        assert ed.mark_set("owned") is True

    with ed.script_context(origin_id="script-b"):
        assert ed.mark_detail_row("owned") is None
        with pytest.raises(PermissionError, match="different script origin"):
            ed.mark_jump("owned")

    c = ed.primary_cursor()
    assert (c.line, c.col) == (1, 1)


def test_script_mark_completion_and_picker_rows_hide_trusted_marks() -> None:
    ed = _editor()
    _set_cursor(ed, 2, 0)
    assert ed.mark_set("trusted") is True

    with ed.script_context(origin_id="script-a"):
        _set_cursor(ed, 1, 0)
        assert ed.mark_set("own") is True
        assert [row[0] for row in ed.mark_prompt_rows()] == ["own"]
        ed.enter_prompt("command", prefill="markjump ")
        assert ed.prompt is not None
        assert ed.prompt_complete(direction=1) is True
        completed = str(ed.prompt.text)

    assert completed == "markjump own "
    assert "trusted" not in completed


def test_script_cannot_close_clean_buffer_if_that_would_erase_trusted_mark() -> None:
    ed = _editor()
    ed.new_buffer("other", "one\n")
    _set_cursor(ed, 0, 0)
    assert ed.mark_set("trusted") is True
    assert "other" in ed.buffers

    with ed.script_context(origin_id="script-a"):
        assert ed.close_buffer("other") is False

    assert "other" in ed.buffers
    assert "trusted" in ed.marks
    assert "script context cannot modify mark: trusted:close-buffer" in ed.messages[-1]


def test_script_can_close_buffer_and_drop_own_mark() -> None:
    ed = _editor()
    ed.new_buffer("other", "one\n")

    with ed.script_context(origin_id="script-a"):
        _set_cursor(ed, 0, 0)
        assert ed.mark_set("own") is True
        assert ed.close_buffer("other") is True

    assert "other" not in ed.buffers
    assert "own" not in ed.marks


def test_script_cannot_rename_buffer_if_that_would_retarget_trusted_mark() -> None:
    ed = _editor()
    assert ed.mark_set("trusted") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.rename_buffer("main", "renamed") is False

    assert "main" in ed.buffers
    assert "renamed" not in ed.buffers
    assert ed.marks["trusted"][0] == "main"
    assert "script context cannot modify mark: trusted:rename-buffer" in ed.messages[-1]
