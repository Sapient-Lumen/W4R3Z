from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "")
    return ed


def _insert_text(ed: Editor, text: str) -> None:
    ed.input["text"] = text
    assert ed.run_action("InsertText") is True


def test_script_cannot_undo_trusted_user_edit() -> None:
    ed = _editor()
    _insert_text(ed, "trusted")

    with ed.script_context(origin_id="script-a"):
        assert ed.exec_command_line("undo") is False

    assert ed.cur().buf.get_text() == "trusted"
    assert ed.undo.depth() == 1
    assert "cannot replay undo history" in ed.messages[-1]
    assert "trusted" in ed.messages[-1]


def test_script_cannot_redo_trusted_user_edit() -> None:
    ed = _editor()
    _insert_text(ed, "trusted")
    assert ed.exec_command_line("undo") is True
    assert ed.cur().buf.get_text() == ""

    with ed.script_context(origin_id="script-a"):
        assert ed.exec_command_line("redo") is False

    assert ed.cur().buf.get_text() == ""
    assert ed.undo.redo_depth() == 1
    assert "cannot replay undo history" in ed.messages[-1]
    assert "trusted" in ed.messages[-1]


def test_script_can_undo_and_redo_own_edit() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        _insert_text(ed, "own")
        assert ed.exec_command_line("undo") is True
        assert ed.cur().buf.get_text() == ""
        assert ed.exec_command_line("redo") is True

    assert ed.cur().buf.get_text() == "own"
    assert ed.undo.depth() == 1


def test_independent_script_cannot_undo_other_script_edit() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        _insert_text(ed, "a")

    with ed.script_context(origin_id="script-b"):
        assert ed.exec_command_line("undo") is False

    assert ed.cur().buf.get_text() == "a"
    assert ed.undo.depth() == 1
    assert "different script origin" in ed.messages[-1]


def test_cap_undo_redo_allows_trusted_replay_from_script() -> None:
    ed = _editor()
    _insert_text(ed, "trusted")
    assert ed.exec_command_line("set cap.undo-redo true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.exec_command_line("undo") is True

    assert ed.cur().buf.get_text() == ""
    assert ed.undo.redo_depth() == 1
