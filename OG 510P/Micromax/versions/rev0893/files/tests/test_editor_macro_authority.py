from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*m*", "")
    return ed


def _insert_step(text: str) -> MacroStep:
    return MacroStep(kind="action", name="InsertText", payload={"input": {"text": str(text)}})


def _trusted_macro(ed: Editor, name: str = "trusted", text: str = "T") -> None:
    ed.set_macro(name, [_insert_step(text)])


def _macro_get_hostcall(ed: Editor, name: str) -> None:
    ed.vm.stack.append(str(name))
    ed.vm.stack.append("ed.macro-get")
    ed.vm.eval("hostcall", filename="<macro-auth-test>")


def test_script_cannot_play_trusted_saved_macro_without_capability() -> None:
    ed = _editor()
    _trusted_macro(ed, text="X")

    with ed.script_context(origin_id="script-a"):
        assert ed.play_macro("trusted") is False

    assert ed.cur().buf.get_text() == ""
    assert "macro play: script context cannot play macro: trusted" in ed.messages[-1]
    assert "cap.macro-play" in ed.messages[-1]


def test_script_can_play_own_saved_macro_without_broad_capability() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.set_macro("own", [_insert_step("o")])
        assert ed.play_macro("own") is True

    assert ed.cur().buf.get_text() == "o"


def test_script_can_play_trusted_saved_macro_with_explicit_capability() -> None:
    ed = _editor()
    _trusted_macro(ed, text="Y")
    assert ed.exec_command_line("set cap.macro-play true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.play_macro("trusted") is True

    assert ed.cur().buf.get_text() == "Y"


def test_script_cannot_read_trusted_saved_macro_payload_without_capability() -> None:
    ed = _editor()
    _trusted_macro(ed, text="secret")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(PermissionError):
            ed.get_macro("trusted")
        assert ed.macro_names() == []
        assert ed.macro_inventory_rows() == []
        assert ed.macro_detail_row("trusted") is None


def test_macro_get_hostcall_denial_preserves_macro_argument() -> None:
    ed = _editor()
    _trusted_macro(ed, text="secret")

    with ed.script_context(origin_id="script-a"):
        with pytest.raises(MicromaxError):
            _macro_get_hostcall(ed, "trusted")

    assert ed.vm.stack[-1] == "trusted"


def test_script_can_read_trusted_saved_macro_with_explicit_capability() -> None:
    ed = _editor()
    _trusted_macro(ed, text="visible")
    assert ed.exec_command_line("set cap.macro-read true") is True

    with ed.script_context(origin_id="script-a"):
        steps = ed.get_macro("trusted")
        assert len(steps) == 1
        assert ed.macro_names() == ["trusted"]
        assert ed.macro_inventory_rows() == [["trusted", 1]]
        assert ed.macro_detail_row("trusted") == ["trusted", "trusted", "saved", 1, 0, 0]


def test_independent_scripts_cannot_read_or_play_each_others_macros() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.set_macro("owned", [_insert_step("a")])

    with ed.script_context(origin_id="script-b"):
        assert ed.play_macro("owned") is False
        with pytest.raises(PermissionError):
            ed.get_macro("owned")

    assert ed.cur().buf.get_text() == ""
    assert "different script origin" in ed.messages[-1]
