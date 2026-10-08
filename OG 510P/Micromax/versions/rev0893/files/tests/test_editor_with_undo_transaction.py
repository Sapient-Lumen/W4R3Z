from __future__ import annotations

import pytest

from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    return ed


def test_with_undo_failure_rolls_back_other_buffer_and_history() -> None:
    ed = _editor()
    ed.new_buffer("a", "alpha")
    ed.new_buffer("b", "beta")
    ed.switch_buffer("a")
    before_b_version = ed.buffers["b"].buf.version

    with pytest.raises(MicromaxError):
        ed.vm.eval(
            '"group" [ "b" [ "X" "ed.insert" hostcall nope ] "ed.with-buffer" hostcall ] "ed.with-undo" hostcall',
            filename="<test>",
        )

    assert ed.active == "a"
    assert ed.buffers["a"].buf.get_text() == "alpha"
    assert ed.buffers["b"].buf.get_text() == "beta"
    assert not ed.buffers["a"].buf.dirty
    assert not ed.buffers["b"].buf.dirty
    assert ed.buffers["b"].buf.version == before_b_version
    assert ed.undo.depth() == 0
    assert ed.vm.stack == []


def test_with_undo_success_records_one_cross_buffer_undo_step() -> None:
    ed = _editor()
    ed.new_buffer("a", "alpha")
    ed.new_buffer("b", "beta")
    ed.switch_buffer("a")

    ed.vm.eval(
        '"group" [ "A" "ed.insert" hostcall "b" [ "B" "ed.insert" hostcall ] "ed.with-buffer" hostcall ] "ed.with-undo" hostcall',
        filename="<test>",
    )

    assert ed.buffers["a"].buf.get_text() == "Aalpha"
    assert ed.buffers["b"].buf.get_text() == "Bbeta"
    assert ed.undo.depth() == 1

    assert ed.undo.undo() is True
    assert ed.buffers["a"].buf.get_text() == "alpha"
    assert ed.buffers["b"].buf.get_text() == "beta"

    assert ed.undo.redo() is True
    assert ed.buffers["a"].buf.get_text() == "Aalpha"
    assert ed.buffers["b"].buf.get_text() == "Bbeta"


def test_with_undo_bad_arguments_preserve_stack() -> None:
    ed = _editor()
    ed.vm.stack[:] = ["group", "not-a-quotation"]

    with pytest.raises(MicromaxError, match="ed.with-undo: expected quotation"):
        ed.vm.eval('"ed.with-undo" hostcall', filename="<test>")

    assert ed.vm.stack == ["group", "not-a-quotation"]


def _mark_tuple(ed: Editor, name: str) -> tuple[str, int, int]:
    buf_name, cur = ed.marks[name]
    return (buf_name, int(cur.line), int(cur.col))


def test_with_undo_failure_rolls_back_global_marks() -> None:
    ed = _editor()
    ed.new_buffer("a", "abcdef")
    assert ed.mark_set("keep") is True

    with pytest.raises(MicromaxError):
        ed.vm.eval(
            '"marks" [ 0 2 "ed.set-cursor" hostcall "keep" "ed.mark-set" hostcall drop '
            '"new" "ed.mark-set" hostcall drop nope ] "ed.with-undo" hostcall',
            filename="<test>",
        )

    assert sorted(ed.marks) == ["keep"]
    assert _mark_tuple(ed, "keep") == ("a", 0, 0)
    assert ed.undo.depth() == 0


def test_with_undo_success_records_marks_in_undo_redo_step() -> None:
    ed = _editor()
    ed.new_buffer("a", "abcdef")
    assert ed.mark_set("keep") is True

    ed.vm.eval(
        '"marks" [ 0 2 "ed.set-cursor" hostcall "keep" "ed.mark-set" hostcall drop '
        '"new" "ed.mark-set" hostcall drop ] "ed.with-undo" hostcall',
        filename="<test>",
    )

    assert sorted(ed.marks) == ["keep", "new"]
    assert _mark_tuple(ed, "keep") == ("a", 0, 2)
    assert _mark_tuple(ed, "new") == ("a", 0, 2)

    assert ed.undo.undo() is True
    assert sorted(ed.marks) == ["keep"]
    assert _mark_tuple(ed, "keep") == ("a", 0, 0)

    assert ed.undo.redo() is True
    assert sorted(ed.marks) == ["keep", "new"]
    assert _mark_tuple(ed, "keep") == ("a", 0, 2)
    assert _mark_tuple(ed, "new") == ("a", 0, 2)


def test_with_undo_success_records_mark_only_change() -> None:
    ed = _editor()
    ed.new_buffer("a", "alpha")
    assert ed.mark_set("keep") is True

    ed.vm.eval(
        '"mark-only" [ "new" "ed.mark-set" hostcall drop ] "ed.with-undo" hostcall',
        filename="<test>",
    )

    assert sorted(ed.marks) == ["keep", "new"]
    assert ed.undo.depth() == 1

    assert ed.undo.undo() is True
    assert sorted(ed.marks) == ["keep"]

    assert ed.undo.redo() is True
    assert sorted(ed.marks) == ["keep", "new"]


def test_buffer_transaction_records_saved_cursor_only_change(tmp_path) -> None:
    ed = _editor()
    ed.new_buffer("a", "alpha")
    norm = ed._normalize_path(str(tmp_path / "cursor.txt"))

    before = ed._buffer_transaction_snapshot()
    ed._saved_cursors[norm] = {"line": 3, "col": 2}
    ed._saved_cursors_authority[norm] = ed._current_runtime_authority(kind="editor")
    after = ed._buffer_transaction_snapshot()

    assert ed._buffer_transaction_changed(before, after) is True
    ed._record_buffer_transaction_snapshot(before, after, "savecursor")
    assert ed.undo.depth() == 1

    assert ed.undo.undo() is True
    assert norm not in ed._saved_cursors

    assert ed.undo.redo() is True
    assert ed._saved_cursors[norm] == {"line": 3, "col": 2}
    assert ed._saved_cursor_entry_authority(norm).script_context is False


def test_buffer_transaction_records_saved_cursor_authority_only_change(tmp_path) -> None:
    ed = _editor()
    ed.new_buffer("a", "alpha")
    norm = ed._normalize_path(str(tmp_path / "cursor.txt"))
    ed._saved_cursors[norm] = {"line": 3, "col": 2}
    ed._normalize_saved_cursor_authority()

    before = ed._buffer_transaction_snapshot()
    with ed.script_context(origin_id="script:a"):
        ed._saved_cursors_authority[norm] = ed._current_runtime_authority(kind="editor")
    after = ed._buffer_transaction_snapshot()

    assert ed._buffer_transaction_changed(before, after) is True
    ed._record_buffer_transaction_snapshot(before, after, "savecursor-authority")

    assert ed.undo.undo() is True
    assert ed._saved_cursors[norm] == {"line": 3, "col": 2}
    assert ed._saved_cursor_entry_authority(norm).script_context is False

    assert ed.undo.redo() is True
    assert ed._saved_cursors[norm] == {"line": 3, "col": 2}
    assert ed._saved_cursor_entry_authority(norm).script_origin_id == "script:a"
