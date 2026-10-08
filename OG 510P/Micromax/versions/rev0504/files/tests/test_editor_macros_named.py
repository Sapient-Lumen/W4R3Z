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


def test_macro_play_reports_success_feedback() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line("macro record a")
    ed.input["text"] = "z"
    assert ed.run_action("InsertText")
    assert ed.exec_command_line("macro stop")

    ed.cur().buf.set_text("")
    ed.cur().cursors[0].line = 0
    ed.cur().cursors[0].col = 0
    assert ed.exec_command_line("macro play a 2")
    assert ed.cur().buf.get_text() == "zz"
    assert ed.status_model()["last_message"] == "macro: played a x2 (1 step)"




def test_macro_list_reports_none_before_any_recording() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line("macro list")
    assert ed.status_model()["last_message"] == "macros: 0 macro(s)"


def test_macro_list_reports_step_counts_for_named_macros() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line("macro record a")
    ed.input["text"] = "z"
    assert ed.run_action("InsertText")
    assert ed.exec_command_line("macro stop")

    assert ed.exec_command_line("macro list")
    assert ed.status_model()["last_message"] == "macros: 2 macro(s), a (1 step), last (1 step)"


def test_macro_inventory_rows_match_macro_list_policy() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.macro_inventory_rows() == []

    assert ed.exec_command_line("macro record a")
    ed.input["text"] = "z"
    assert ed.run_action("InsertText")
    assert ed.exec_command_line("macro stop")

    assert ed.macro_inventory_rows() == [["a", 1], ["last", 1]]
    assert ed.macro_list_entries() == ["a (1 step)", "last (1 step)"]


def test_macro_reports_unknown_subcommand_plainly() -> None:
    ed = Editor()

    assert ed.exec_command_line("macro nope") is False
    assert ed.messages[-1] == "macro: no such subcommand: nope"




def test_macro_status_reports_idle_and_recording_snapshot() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.macro_status_rows() == [["status", "idle", "", 0, 0]]
    assert ed.exec_command_line("macro status")
    assert ed.status_model()["last_message"] == "macro status: idle, 0 macro(s)"

    assert ed.exec_command_line("macro record demo")
    ed.input["text"] = "z"
    assert ed.run_action("InsertText")

    assert ed.macro_status_rows() == [["status", "recording", "demo", 1, 0]]
    assert ed.exec_command_line("macro status")
    assert ed.status_model()["last_message"] == "macro status: recording demo (1 step), 0 macro(s)"

    assert ed.exec_command_line("macro stop")
    assert ed.macro_status_rows() == [
        ["status", "idle", "", 0, 2],
        ["saved", "demo", 1],
        ["saved", "last", 1],
    ]
    assert ed.exec_command_line("macro status")
    assert ed.status_model()["last_message"] == "macro status: idle, 2 macro(s), demo (1 step), last (1 step)"


def test_macro_play_reports_missing_macro() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line("macro play missing") is False
    assert ed.status_model()["last_message"] == "macro play: no such macro: missing"


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


def test_macro_hostcall_inventory_rows_match_list_surface() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    install_editor_hostcalls(ed)

    ed.vm.eval('"ed.macro-inventory-rows" hostcall')
    assert ed.vm.pop_list() == []

    ed.vm.eval('"m" "ed.macro-record" hostcall')
    assert ed.vm.pop_int() == 1
    ed.vm.eval('"text" "yo" "ed.input-set" hostcall  "InsertText" "ed.run" hostcall')
    assert ed.vm.pop_int() == 1
    ed.vm.eval('"ed.macro-stop" hostcall')
    assert ed.vm.pop_int() == 1

    ed.vm.eval('"ed.macro-inventory-rows" hostcall')
    assert ed.vm.pop_list() == [["last", 1], ["m", 1]]




def test_macro_status_rows_hostcall_matches_command_surface() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    install_editor_hostcalls(ed)

    ed.vm.eval('"ed.macro-status-rows" hostcall')
    assert ed.vm.pop_list() == [["status", "idle", "", 0, 0]]

    ed.vm.eval('"m" "ed.macro-record" hostcall')
    assert ed.vm.pop_int() == 1
    ed.vm.eval('"text" "yo" "ed.input-set" hostcall  "InsertText" "ed.run" hostcall')
    assert ed.vm.pop_int() == 1

    ed.vm.eval('"ed.macro-status-rows" hostcall')
    assert ed.vm.pop_list() == [["status", "recording", "m", 1, 0]]

    ed.vm.eval('"ed.macro-stop" hostcall')
    assert ed.vm.pop_int() == 1
    ed.vm.eval('"ed.macro-status-rows" hostcall')
    assert ed.vm.pop_list() == [
        ["status", "idle", "", 0, 2],
        ["saved", "last", 1],
        ["saved", "m", 1],
    ]



def test_macro_status_rows_report_playing_state_during_playback() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    seen: list[list[list[object]]] = []

    def capture_macro_status(editor: Editor) -> bool:
        seen.append(editor.macro_status_rows())
        return True

    ed.actions.register("CaptureMacroStatus", capture_macro_status)

    assert ed.exec_command_line("macro record demo")
    assert ed.run_action("CaptureMacroStatus")
    assert ed.exec_command_line("macro stop")
    seen.clear()

    assert ed.play_macro("demo") is True
    assert seen == [[
        ["status", "playing", "demo", 1, 2],
        ["saved", "demo", 1],
        ["saved", "last", 1],
    ]]
    assert ed.macro_status_rows() == [
        ["status", "idle", "", 0, 2],
        ["saved", "demo", 1],
        ["saved", "last", 1],
    ]


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
