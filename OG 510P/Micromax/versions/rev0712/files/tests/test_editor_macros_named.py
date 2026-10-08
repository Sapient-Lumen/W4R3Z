from __future__ import annotations

import pytest
from pathlib import Path

from micromax import MicromaxError
from micromax_editor.editor import Editor, MacroStep
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




def test_macro_root_reports_runtime_summary_then_usage_when_idle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line('macro') is False
    assert ed.messages == [
        'macro: idle · default=last (0 steps) · 0 macros',
        'usage: macro record|rec|start|stop|end|cancel|abort|play|run|list|ls|status|st ...',
    ]



def test_macro_root_reports_runtime_summary_then_usage_while_recording_and_after_save() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    ed.messages.clear()
    assert ed.exec_command_line('macro') is False
    assert ed.messages == [
        'macro: recording · demo (1 step) · stop to save, cancel to discard · 0 macros',
        'usage: macro record|rec|start|stop|end|cancel|abort|play|run|list|ls|status|st ...',
    ]

    assert ed.exec_command_line('macro stop')
    ed.messages.clear()
    assert ed.exec_command_line('macro') is False
    assert ed.messages == [
        'macro: idle · default=last (1 step) · 2 macros · e.g. demo (1 step)',
        'usage: macro record|rec|start|stop|end|cancel|abort|play|run|list|ls|status|st ...',
    ]

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    ed.messages.clear()
    assert ed.exec_command_line('macro') is False
    assert ed.messages == [
        'macro: playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]',
        'usage: macro record|rec|start|stop|end|cancel|abort|play|run|list|ls|status|st ...',
    ]



def test_macro_stop_cancel_aliases_report_runtime_state_when_idle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    cases = [
        ('macro stop', 'macro stop: idle · not recording'),
        ('macro end', 'macro end: idle · not recording'),
        ('macro cancel', 'macro cancel: idle · not recording'),
        ('macro abort', 'macro abort: idle · not recording'),
    ]
    for cmd, want in cases:
        ed.messages.clear()
        assert ed.exec_command_line(cmd) is False
        assert ed.messages == [want]



def test_macro_record_aliases_report_runtime_state_when_already_recording() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    cases = [
        ('macro record other', 'macro record: recording · demo (1 step) · stop or cancel first'),
        ('macro rec other', 'macro rec: recording · demo (1 step) · stop or cancel first'),
        ('macro start other', 'macro start: recording · demo (1 step) · stop or cancel first'),
    ]
    for cmd, want in cases:
        ed.messages.clear()
        assert ed.exec_command_line(cmd) is False
        assert ed.messages == [want]


def test_macro_play_aliases_report_recording_blockers_consistently() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    for cmd, want in (
        ('macro play demo', 'macro play: recording · demo (1 step) · stop or cancel first'),
        ('macro run demo', 'macro run: recording · demo (1 step) · stop or cancel first'),
    ):
        ed.messages.clear()
        assert ed.exec_command_line(cmd) is False
        assert ed.messages == [want]


def test_play_macro_method_and_hostcall_reject_recording_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    assert ed.play_macro('demo') is False
    assert ed.status_model()['last_message'] == 'macro play: recording · demo (1 step) · stop or cancel first'

    ed.vm.eval('"demo" 2 "ed.macro-play" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro play: recording · demo (1 step) · stop or cancel first'


def test_start_macro_method_and_hostcall_reject_recording_and_playback_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    assert ed.start_macro('other') is False
    assert ed.status_model()['last_message'] == 'macro record: recording · demo (1 step) · stop or cancel first'

    ed.vm.eval('"other" "ed.macro-record" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro record: recording · demo (1 step) · stop or cancel first'

    assert ed.exec_command_line('macro stop')
    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    assert ed.start_macro('other') is False
    assert ed.status_model()['last_message'] == 'macro record: playing · demo (1 step) · wait for playback'

    ed.vm.eval('"other" "ed.macro-record" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro record: playing · demo (1 step) · wait for playback'



def test_stop_cancel_methods_and_hostcalls_report_idle_and_playback_blockers() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.stop_macro() is False
    assert ed.status_model()['last_message'] == 'macro stop: idle · not recording'
    ed.vm.eval('"ed.macro-stop" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro stop: idle · not recording'

    assert ed.cancel_macro() is False
    assert ed.status_model()['last_message'] == 'macro cancel: idle · not recording'
    ed.vm.eval('"ed.macro-cancel" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro cancel: idle · not recording'

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    assert ed.stop_macro() is False
    assert ed.status_model()['last_message'] == 'macro stop: playing · demo (1 step) · wait for playback'
    ed.vm.eval('"ed.macro-stop" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro stop: playing · demo (1 step) · wait for playback'

    assert ed.cancel_macro() is False
    assert ed.status_model()['last_message'] == 'macro cancel: playing · demo (1 step) · wait for playback'
    ed.vm.eval('"ed.macro-cancel" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro cancel: playing · demo (1 step) · wait for playback'


def test_play_macro_method_and_hostcall_reject_playback_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    assert ed.play_macro('demo') is False
    assert ed.status_model()['last_message'] == 'macro play: playing · demo (1 step) · wait for playback'

    ed.vm.eval('"demo" 2 "ed.macro-play" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 0
    assert ed.status_model()['last_message'] == 'macro play: playing · demo (1 step) · wait for playback'


def test_macro_commands_report_playback_blockers_consistently() -> None:
    ed = Editor()
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    for cmd, want in (
        ('macro play demo', 'macro play: playing · demo (1 step) · wait for playback'),
        ('macro run demo', 'macro run: playing · demo (1 step) · wait for playback'),
        ('macro stop', 'macro stop: playing · demo (1 step) · wait for playback'),
        ('macro end', 'macro end: playing · demo (1 step) · wait for playback'),
        ('macro cancel', 'macro cancel: playing · demo (1 step) · wait for playback'),
        ('macro abort', 'macro abort: playing · demo (1 step) · wait for playback'),
    ):
        assert ed.exec_command_line(cmd) is False
        assert ed.status_model()['last_message'] == want

def test_macro_play_count_paths_keep_blockers_ahead_of_missing_slots() -> None:
    ed = Editor()
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    assert ed.exec_command_line('macro record live')
    ed.input['text'] = 'x'
    assert ed.run_action('InsertText')

    assert ed.exec_command_line('macro run ghost 2') is False
    assert ed.status_model()['last_message'] == 'macro run: recording · live (1 step) · stop or cancel first'

    assert ed.exec_command_line('macro cancel')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    assert ed.exec_command_line('macro run ghost 2') is False
    assert ed.status_model()['last_message'] == 'macro run: playing · demo (1 step) · wait for playback'

def test_macro_run_alias_reports_alias_specific_count_and_missing_feedback() -> None:
    ed = Editor()
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro run missing') is False
    assert ed.status_model()['last_message'] == 'macro run: no such macro: missing'

    assert ed.exec_command_line('macro run demo 0') is False
    assert ed.status_model()['last_message'] == 'macro run: count must be > 0'

    assert ed.exec_command_line('macro run demo nope') is False
    assert ed.status_model()['last_message'] == 'macro run: count must be an int'


def test_macro_subcommands_reject_extra_args_without_mutating_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    ed.messages.clear()
    assert ed.exec_command_line('macro stop now') is False
    assert ed.messages == [
        'macro stop: takes no args',
        'usage: macro stop',
    ]
    assert ed.macro_recording is True

    assert ed.exec_command_line('macro stop')
    ed.cur().buf.set_text('')
    ed.cur().cursors[0].line = 0
    ed.cur().cursors[0].col = 0

    ed.messages.clear()
    assert ed.exec_command_line('macro play demo 2 extra') is False
    assert ed.messages == [
        'macro play: takes at most 2 args',
        'usage: macro play [NAME] [COUNT]',
    ]
    assert ed.cur().buf.get_text() == ''

    extra_cases = [
        ('macro end now', ['macro end: takes no args', 'usage: macro end']),
        ('macro cancel now', ['macro cancel: takes no args', 'usage: macro cancel']),
        ('macro abort now', ['macro abort: takes no args', 'usage: macro abort']),
        ('macro list junk', ['macro list: takes no args', 'usage: macro list']),
        ('macro ls junk', ['macro ls: takes no args', 'usage: macro ls']),
        ('macro status junk', ['macro status: takes no args', 'usage: macro status']),
        ('macro st junk', ['macro st: takes no args', 'usage: macro st']),
        ('macro record demo extra', ['macro record: takes at most 1 arg', 'usage: macro record [NAME]']),
        ('macro rec demo extra', ['macro rec: takes at most 1 arg', 'usage: macro rec [NAME]']),
        ('macro start demo extra', ['macro start: takes at most 1 arg', 'usage: macro start [NAME]']),
        ('macro run demo 2 extra', ['macro run: takes at most 2 args', 'usage: macro run [NAME] [COUNT]']),
    ]
    for cmd, want in extra_cases:
        ed.messages.clear()
        assert ed.exec_command_line(cmd) is False
        assert ed.messages == want



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
    assert ed.status_model()["last_message"] == "macros: 2 macro(s), a (1 step), last (1 step) [default]"


def test_macro_inventory_rows_match_macro_list_policy() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.macro_inventory_rows() == []

    assert ed.exec_command_line("macro record a")
    ed.input["text"] = "z"
    assert ed.run_action("InsertText")
    assert ed.exec_command_line("macro stop")

    assert ed.macro_inventory_rows() == [["a", 1], ["last", 1]]
    assert ed.macro_list_entries() == ["a (1 step)", "last (1 step) [default]"]


def test_macro_reports_unknown_subcommand_plainly() -> None:
    ed = Editor()

    assert ed.exec_command_line("macro nope") is False
    assert ed.messages[-1] == "macro: no such subcommand: nope"




def test_macro_inventory_preview_sample_skips_requested_names() -> None:
    ed = Editor()
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'a'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    assert ed._macro_inventory_preview_sample(skip_names={'demo'}) == 'last (1 step) [default]'
    assert ed._macro_inventory_preview_sample(skip_names={'last'}) == 'demo (1 step)'
    assert ed._macro_inventory_preview_sample(skip_names={'demo', 'last'}) == ''


def test_macro_status_reports_idle_and_recording_snapshot() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.macro_status_rows() == [["status", "idle", "", 0, 0]]
    assert ed.exec_command_line("macro status")
    assert ed.status_model()["last_message"] == "macro status: idle, default=last (0 steps), 0 macro(s)"

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
    assert ed.status_model()["last_message"] == "macro status: idle, default=last (1 step), 2 macro(s), demo (1 step), last (1 step) [default]"

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    assert ed.exec_command_line("macro status")
    assert ed.status_model()["last_message"] == "macro status: playing demo (1 step), 2 macro(s), last (1 step) [default]"


def test_macro_play_reports_missing_macro() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line("macro play missing") is False
    assert ed.status_model()["last_message"] == "macro play: no such macro: missing"


def test_macro_play_reports_empty_default_slot() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line("macro play last") is False
    assert ed.status_model()["last_message"] == "macro play: default slot is empty"

    assert ed.exec_command_line("macro run last 2") is False
    assert ed.status_model()["last_message"] == "macro run: default slot is empty"

    assert ed.play_macro("last") is False
    assert ed.status_model()["last_message"] == "macro play: default slot is empty"

    assert ed.play_macro("last", count="oops") is False
    assert ed.status_model()["last_message"] == "macro play: count must be an int"


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


def test_get_macro_and_hostcall_return_empty_for_missing_named_slots() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    assert len(ed.get_macro('last')) == 1
    assert len(ed.get_macro('demo')) == 1
    assert ed.get_macro('ghost') == []

    ed.vm.eval('"ghost" "ed.macro-get" hostcall')
    assert ed.vm.pop_list() == []

    ed.vm.eval('"last" "ed.macro-get" hostcall')
    last_steps = ed.vm.pop_list()
    assert last_steps and last_steps[0][0] in ('a', 'c')


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


def test_zero_step_named_macros_are_omitted_from_saved_inventory_surfaces() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    assert ed.exec_command_line('macro record demo')
    assert ed.exec_command_line('macro stop')
    assert ed.status_model()['last_message'] == 'macro: saved 0 steps (demo omitted)'

    assert ed.macro_names() == []
    assert ed.macro_inventory_rows() == []
    assert ed.macro_status_rows() == [["status", "idle", "", 0, 0]]
    assert ed.macro_list_entries() == []
    assert ed.macro_list_message() == 'macros: 0 macro(s)'
    assert ed.macro_status_message() == 'macro status: idle, default=last (0 steps), 0 macro(s)'

    assert ed.exec_command_line('macro play demo') is False
    assert ed.status_model()['last_message'] == 'macro play: no such macro: demo'


def test_macro_set_empty_steps_prunes_named_slot_from_names_inventory_and_hostcalls() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    install_editor_hostcalls(ed)

    ed.set_macro('blank', [])
    assert ed.macro_names() == []
    assert ed.macro_inventory_rows() == []
    assert ed.macro_status_rows() == [["status", "idle", "", 0, 0]]

    ed.vm.stack.append([])
    ed.vm.stack.append('ghost')
    ed.vm.eval('"ed.macro-set" hostcall')

    ed.vm.eval('"ed.macro-names" hostcall')
    assert ed.vm.pop_list() == []
    ed.vm.eval('"ed.macro-inventory-rows" hostcall')
    assert ed.vm.pop_list() == []
    ed.vm.eval('"ghost" "ed.macro-get" hostcall')
    assert ed.vm.pop_list() == []


def test_set_macro_rejects_recording_owned_slots_but_allows_other_names() -> None:
    from micromax_editor.editor import MacroStep

    ed = Editor()
    ed.new_buffer(text="")

    seed = [MacroStep(kind="command", name="command", payload={"cmdline": "seed"})]
    other = [MacroStep(kind="command", name="command", payload={"cmdline": "other"})]

    ed.set_macro('last', seed)
    assert ed.start_macro('demo')

    with pytest.raises(RuntimeError, match=r'macro set: recording owns last .*stop or cancel first'):
        ed.set_macro('last', other)
    with pytest.raises(RuntimeError, match=r'macro set: recording owns demo .*stop or cancel first'):
        ed.set_macro('demo', other)

    ed.set_macro('sidecar', other)
    assert ed.macro_names() == ['last', 'sidecar']
    assert len(ed.get_macro('last')) == 1
    assert len(ed.get_macro('sidecar')) == 1

    assert ed.cancel_macro()
    assert len(ed.get_macro('last')) == 1
    assert len(ed.get_macro('sidecar')) == 1


def test_macro_set_hostcall_rejects_recording_owned_slots() -> None:
    from micromax_editor.editor import MacroStep

    ed = Editor()
    ed.new_buffer(text="")
    install_editor_hostcalls(ed)

    steps = [["c", "noop"]]
    seed = [MacroStep(kind="command", name="command", payload={"cmdline": "seed"})]
    ed.set_macro('last', seed)
    assert ed.start_macro('demo')

    ed.vm.stack.append(steps)
    ed.vm.stack.append('last')
    with pytest.raises(MicromaxError, match=r'macro set: recording owns last .*stop or cancel first'):
        ed.vm.eval('"ed.macro-set" hostcall')

    ed.vm.stack.append(steps)
    ed.vm.stack.append('demo')
    with pytest.raises(MicromaxError, match=r'macro set: recording owns demo .*stop or cancel first'):
        ed.vm.eval('"ed.macro-set" hostcall')

    ed.vm.stack.append(steps)
    ed.vm.stack.append('sidecar')
    ed.vm.eval('"ed.macro-set" hostcall')
    assert ed.get_macro('sidecar')


def test_macro_detail_row_hostcall_and_showmacro_surface() -> None:
    ed = Editor()
    ed.new_buffer(text='')
    install_editor_hostcalls(ed)

    assert ed.macro_detail_row('last') == ['last', 'last', 'saved', 0, 1, 0]
    ed.vm.eval('"last" "ed.macro-detail-row" hostcall')
    assert ed.vm.pop() == ['last', 'last', 'saved', 0, 1, 0]

    assert ed.exec_command_line('showmacro last') is True
    assert ed.messages[-1] == 'showmacro last [default]: 0 steps · default replay slot'

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    assert ed.macro_detail_row('demo') == ['demo', 'demo', 'recording', 1, 0, 0]
    assert ed.macro_detail_row('last') == ['last', 'last', 'recording', 1, 1, 0]

    ed.vm.eval('"demo" "ed.macro-detail-row" hostcall')
    assert ed.vm.pop() == ['demo', 'demo', 'recording', 1, 0, 0]

    assert ed.exec_command_line('showmacro demo') is True
    assert ed.messages[-1] == 'showmacro demo [recording]: 1 live step · stop to save, cancel to discard'
    assert len(ed._macro_buffer) == 1
    assert ed._macro_buffer[0].name == 'InsertText'

    assert ed.exec_command_line('showmacro last') is True
    assert ed.messages[-1] == 'showmacro last [recording, default]: 1 live step · stop to save, cancel to discard'

    assert ed.exec_command_line('macro stop')

    ed.vm.eval('"demo" "ed.macro-detail-row" hostcall')
    assert ed.vm.pop() == ['demo', 'demo', 'saved', 1, 0, 0]

    assert ed.exec_command_line('showmacro demo') is True
    assert ed.messages[-1] == 'showmacro demo: 1 step'

    assert ed.exec_command_line('showmacro last') is True
    assert ed.messages[-1] == 'showmacro last [default]: 1 step · default replay slot'

    assert ed.exec_command_line('showmacro ghost') is False
    assert ed.messages[-1] == 'showmacro: no such macro: ghost'


def test_macro_recordability_helpers_cover_command_and_action_filters() -> None:
    ed = Editor()

    assert ed._macro_command_recordability_kind('goto') == 'recordable'
    assert ed._macro_should_record_command_name('goto') is True

    assert ed._macro_command_recordability_kind('macro') == 'exact'
    assert ed._macro_should_record_command_name('macro') is False
    assert ed._macro_command_recordability_kind('jumps') == 'exact'
    assert ed._macro_should_record_command_name('jumps') is False
    assert ed._macro_command_recordability_kind('pwd') == 'exact'
    assert ed._macro_should_record_command_name('pwd') is False
    assert ed._macro_command_recordability_kind('apropos') == 'exact'
    assert ed._macro_should_record_command_name('apropos') is False
    assert ed._macro_command_recordability_kind('whichkey') == 'exact'
    assert ed._macro_should_record_command_name('whichkey') is False
    assert ed._macro_command_recordability_kind('prefixmode') == 'exact'
    assert ed._macro_should_record_command_name('prefixmode') is False

    assert ed._macro_command_recordability_kind('showstatus') == 'prefix'
    assert ed._macro_should_record_command_name('showstatus') is False
    assert ed._macro_command_recordability_kind('helphistory') == 'prefix'
    assert ed._macro_should_record_command_name('helphistory') is False
    assert ed._macro_command_recordability_kind('help') == 'prefix'
    assert ed._macro_should_record_command_name('help') is False
    assert ed._macro_command_recordability_kind('helpback') == 'prefix'
    assert ed._macro_should_record_command_name('helpback') is False
    assert ed._macro_command_recordability_kind('helpfollow') == 'prefix'
    assert ed._macro_should_record_command_name('helpfollow') is False

    assert ed._macro_command_recordability_kind('commandpick') == 'suffix'
    assert ed._macro_should_record_command_name('commandpick') is False
    assert ed._macro_command_recordability_kind('helppick') == 'prefix'
    assert ed._macro_should_record_command_name('helppick') is False
    assert ed._macro_command_recordability_kind('jumppick') == 'suffix'
    assert ed._macro_should_record_command_name('jumppick') is False
    assert ed._macro_command_recordability_kind('') == 'empty'
    assert ed._macro_should_record_command_name('') is False

    assert ed._macro_should_record_action_name('InsertText') is True
    assert ed._macro_should_record_action_name('ToggleMacro') is False
    assert ed._macro_should_record_action_name('PlayMacro') is False
    assert ed._macro_should_record_action_name('CancelMacro') is False
    assert ed._macro_should_record_action_name('') is False


def test_command_line_macro_recording_only_keeps_successful_non_show_commands() -> None:
    ed = Editor()
    ed.new_buffer(text='abc')

    assert ed.exec_command_line('macro record demo')
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('nope') is False
    assert ed.messages[-1] == 'command: no such command: nope'
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('showstatus') is True
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('jumps') is True
    assert ed.messages[-1] == 'jumps: 0 jump(s)'
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('pwd') is True
    assert ed.messages[-1] == str(Path.cwd())
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('helphistory') is True
    assert ed.messages[-1] == 'helphistory: 0 help target(s)'
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('help') is True
    assert ed.messages[-1] == 'Use: apropos QUERY, commandpick, topicpick, or helppick'
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('apropos macro') is True
    assert ed.messages[-1].startswith('apropos macro: ')
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('commandpick') is True
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('helppick') is True
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('jumppick') is True
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('goto 1:1') is True
    assert ed.messages[-1] == 'goto: *scratch* @ 1:1'
    assert len(ed._macro_buffer) == 1
    assert ed._macro_buffer[0] == MacroStep(kind='command', name='command', payload={'cmdline': 'goto 1:1'})

    assert ed.exec_command_line('macro stop')
    assert ed.macro_detail_row('demo') == ['demo', 'demo', 'saved', 1, 0, 0]


def test_action_macro_recording_only_keeps_successful_actions() -> None:
    ed = Editor()
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.cur().local_options['readonly'] = True
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText') is False
    assert ed.messages[-1] == 'InsertText: read-only buffer'
    assert len(ed._macro_buffer) == 0

    ed.cur().local_options['readonly'] = False
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText') is True
    assert len(ed._macro_buffer) == 1
    assert ed._macro_buffer[0] == MacroStep(kind='action', name='InsertText', payload={'input': {'text': 'z'}})

    assert ed.exec_command_line('macro stop')
    assert ed.macro_detail_row('demo') == ['demo', 'demo', 'saved', 1, 0, 0]


def test_help_commands_stay_read_only_while_recording() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-browser') is True

    text = ed.cur().buf.get_text()
    needle = 'Space path doc (escaped space)'
    idx = text.index(needle)
    prefix = text[:idx]
    line = prefix.count('\n')
    col = len(prefix.rsplit('\n', 1)[-1])
    ed.cur().cursors[0].line = line
    ed.cur().cursors[0].col = col

    assert ed.exec_command_line('macro record demo')
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('helpfollow') is True
    assert ed.cur().name.startswith('help:space path')
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('helpback') is True
    assert ed.cur().name.startswith('help:help-browser')
    assert len(ed._macro_buffer) == 0


def test_whichkey_stays_read_only_while_recording() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"nav" "ed.keymode-push" hostcall')

    assert ed.exec_command_line('macro record demo')
    assert len(ed._macro_buffer) == 0

    assert ed.exec_command_line('whichkey') is True
    assert ed.messages[-1] == (
        'whichkey: 2 binding(s), '
        'Ctrl-x@nav->request editor quit, '
        'Ctrl-z@global->show help for commands/actions'
    )
    assert len(ed._macro_buffer) == 0

    ed.vm.eval('"g" "tools" "goto menu" "ed.bind-prefix" hostcall', filename='<prefix-bind>')
    assert ed.exec_command_line('prefixmode tools') is True
    assert ed.messages[-1].startswith('whichkey: ')
    assert 'g@global->goto menu' in ed.messages[-1]
    assert len(ed._macro_buffer) == 0


def test_show_commands_stay_read_only_while_recording() -> None:
    ed = Editor()
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert len(ed._macro_buffer) == 1

    assert ed.exec_command_line('showstatus') is True
    assert ed.messages[-1].startswith("mode=normal buffer='*scratch*'")
    assert len(ed._macro_buffer) == 1
    assert ed._macro_buffer[0].name == 'InsertText'

    assert ed.exec_command_line('showmacro demo') is True
    assert ed.messages[-1] == 'showmacro demo [recording]: 1 live step · stop to save, cancel to discard'
    assert len(ed._macro_buffer) == 1

    assert ed.exec_command_line('macro stop')
    assert ed.macro_detail_row('demo') == ['demo', 'demo', 'saved', 1, 0, 0]


def test_showmacro_root_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed._showmacro_root_preview_summary() == 'idle · default=last (0 steps) · 0 macros'

    ed.messages.clear()
    assert ed.exec_command_line('showmacro') is False
    assert ed.messages == [
        'showmacro: idle · default=last (0 steps) · 0 macros',
        'usage: showmacro NAME',
    ]

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed._showmacro_root_preview_summary() == 'recording · demo (1 step) · stop to save, cancel to discard · 0 macros'

    ed.messages.clear()
    assert ed.exec_command_line('showmacro') is False
    assert ed.messages == [
        'showmacro: recording · demo (1 step) · stop to save, cancel to discard · 0 macros',
        'usage: showmacro NAME',
    ]

    assert ed.exec_command_line('macro stop')
    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    assert ed._showmacro_root_preview_summary() == 'playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]'

    ed.messages.clear()
    assert ed.exec_command_line('showmacro') is False
    assert ed.messages == [
        'showmacro: playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]',
        'usage: showmacro NAME',
    ]


def test_showmacro_root_prefers_default_last_while_idle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])
    ed.set_macro('demo', [
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop'}),
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop 2'}),
    ])

    assert ed._showmacro_root_preview_summary() == 'idle · default=last (1 step) · 2 macros · e.g. demo (2 steps)'


def test_macro_idle_default_slot_summary_prefers_default_last_while_idle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_idle_default_slot_summary() == 'idle · default=last (0 steps) · 0 macros'

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])
    ed.set_macro('demo', [
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop'}),
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop 2'}),
    ])

    assert ed._macro_idle_default_slot_summary() == 'idle · default=last (1 step) · 2 macros · e.g. demo (2 steps)'


def test_macro_default_slot_steps_helper_tracks_empty_and_saved_last() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_default_slot_steps() == 0
    assert ed._macro_default_slot_steps_label() == 'default=last (0 steps)'

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])

    assert ed._macro_default_slot_steps() == 1
    assert ed._macro_default_slot_steps_label() == 'default=last (1 step)'


def test_macro_default_slot_action_helpers_track_empty_and_saved_last() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_default_slot_play_detail() == 'default slot empty'
    assert ed._macro_default_slot_play_detail(count=2) == 'default slot empty'
    assert ed._macro_default_slot_record_detail() == 'record default slot'

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])

    assert ed._macro_default_slot_play_detail() == 'play default slot'
    assert ed._macro_default_slot_play_detail(count=2) == 'play default slot 2x'
    assert ed._macro_default_slot_record_detail() == 'overwrite default slot on save'


def test_macro_default_slot_empty_runtime_message_helper_tracks_subcommand() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_default_slot_empty_runtime_message() == 'macro play: default slot is empty'
    assert ed._macro_default_slot_empty_runtime_message('run') == 'macro run: default slot is empty'


def test_macro_missing_runtime_message_helper_tracks_name_and_subcommand() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_missing_runtime_message('ghost') == 'macro play: no such macro: ghost'
    assert ed._macro_missing_runtime_message('ghost', 'run') == 'macro run: no such macro: ghost'


def test_macro_invalid_count_runtime_message_helper_tracks_subcommand() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_invalid_count_runtime_message() == 'macro play: count must be > 0'
    assert ed._macro_invalid_count_runtime_message('run') == 'macro run: count must be > 0'


def test_macro_invalid_count_type_runtime_message_helper_tracks_subcommand() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed._macro_invalid_count_type_runtime_message() == 'macro play: count must be an int'
    assert ed._macro_invalid_count_type_runtime_message('run') == 'macro run: count must be an int'

