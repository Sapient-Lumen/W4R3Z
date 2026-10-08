from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_macro_command_named_record_play() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    # record into named slot
    assert ed.exec_command_line("macro record a")
    assert ed.macro_recording is True

    ed.input["text"] = "hi"
    assert ed.run_action("InsertText")
    assert ed.exec_command_line("macro stop")
    assert ed.macro_recording is False

    assert "a" in ed.macros
    assert len(ed.macros["a"]) >= 1
    assert len(ed.macros["last"]) >= 1

    # clear buffer and play named macro
    ed.cur().buf.set_text("")
    ed.cur().cursors[0].line = 0
    ed.cur().cursors[0].col = 0
    assert ed.play_macro("a")
    assert ed.cur().buf.get_text() == "hi"


def test_cancel_macro_restores_previous_last() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    ed.input["text"] = "one"
    ed.run_action("InsertText")
    # record a baseline last macro
    ed.start_macro("last")
    ed.run_action("CursorLeft")
    ed.stop_macro()
    baseline = list(ed.macro)

    # start recording then cancel; baseline should remain
    assert ed.start_macro("last")
    ed.run_action("CursorRight")
    assert ed.cancel_macro()
    assert ed.macro == baseline


def test_macro_hostcalls_portable_roundtrip() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    install_editor_hostcalls(ed)

    # record macro via hostcall into 'm'
    ed.vm.eval('"m" "ed.macro-record" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 1

    # insert via action chain
    ed.vm.eval('"text" "yo" "ed.input-set" hostcall  "InsertText" "ed.run" hostcall')
    ok2 = ed.vm.pop_int()
    assert ok2 == 1

    ed.vm.eval('"ed.macro-stop" hostcall')
    ok3 = ed.vm.pop_int()
    assert ok3 == 1

    # fetch macro steps
    ed.vm.eval('"m" "ed.macro-get" hostcall')
    steps = ed.vm.pop_list()
    assert steps and steps[0][0] in ("a", "c")

    # store under a new name and play twice
    ed.vm.stack.append(steps)
    ed.vm.stack.append("n")
    ed.vm.eval('"ed.macro-set" hostcall')
    ed.cur().buf.set_text("")
    ed.vm.eval('"n" 2 "ed.macro-play" hostcall')
    ok4 = ed.vm.pop_int()
    assert ok4 == 1
    assert ed.cur().buf.get_text() == "yoyo"
