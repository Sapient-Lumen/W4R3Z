from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _new_editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    return ed


def _call_host(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<test>")


def test_qreplace_yes_no_and_undo_single_step() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two one two")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None
    st = ed.status_model()
    assert st["mode"] == "qreplace"
    assert st["keymode"] == "qreplace"
    assert st["keymode_capture"] == 1
    assert st["capture_kind"] == "qreplace"
    assert st["capture_progress"] == "1/2"
    assert st["interaction_kind"] == "qreplace"
    assert st["interaction_position"] == "1/2"
    assert st["interaction_line"].startswith("?replace [1/2]")
    assert st["capture_search"] == "one"
    assert st["capture_replace"] == "X"
    assert st["capture_detail"] == "one -> X"
    assert st["capture_summary"].startswith("?replace [1/2]")
    assert ed.selection_text() == "one"

    # Skip the first match.
    assert ed.dispatch_key("n") is True
    assert ed.qreplace is not None
    assert ed.cur().buf.get_text() == "one two one two"
    assert ed.selection_text() == "one"

    # Replace the second match.
    assert ed.dispatch_key("y") is True
    assert ed.qreplace is None
    assert ed.cur().buf.get_text() == "one two X two"

    # Query-replace records one undo entry.
    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "one two one two"


def test_qreplace_all_replaces_remaining() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a1 a2 a3")

    assert ed.exec_command_line("qreplace 'a([0-9])' 'b$1'") is True
    assert ed.qreplace is not None
    assert ed.selection_text() == "a1"

    assert ed.dispatch_key("a") is True
    assert ed.qreplace is None
    assert ed.cur().buf.get_text() == "b1 b2 b3"

    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "a1 a2 a3"


def test_qreplace_capture_mode_blocks_global_bindings() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None

    # Ctrl-q is globally bound to command:quit in the core plugin.
    # In qreplace capture mode, it should not fall through.
    assert ed.dispatch_key("Ctrl-q") is False
    assert ed.qreplace is not None
    assert ed.cur().buf.get_text() == "one two"

    # Quit out normally.
    assert ed.dispatch_key("q") is True
    assert ed.qreplace is None



def test_qreplace_respects_ignorecase_option() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "One one")

    # ignorecase is enabled by default; query-replace should match "One" first.
    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None
    assert ed.selection_text() == "One"

    # Replace the first match; the session should continue to the next match.
    assert ed.dispatch_key("y") is True
    assert ed.qreplace is not None
    assert ed.selection_text() == "one"

    # Replace the last match and quit.
    assert ed.dispatch_key("l") is True
    assert ed.qreplace is None
    assert ed.cur().buf.get_text() == "X X"



def test_qreplace_rejects_unknown_flags_before_capture_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one")

    assert ed.exec_command_line("qreplace one X --all") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "one one"
    assert ed.status_model()["last_message"] == "qreplace: unknown flag: --all"

def test_qreplace_rejects_empty_search_before_capture() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("qreplace '' X -l") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "qreplace: empty search"


def test_qreplace_rejects_zero_width_regex_before_capture() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("qreplace '$' X") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "qreplace: zero-width matches are not supported"


def test_qreplace_rejects_regex_that_eventually_matches_zero_width() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("qreplace 'abc|$' X") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "qreplace: zero-width matches are not supported"


def test_qreplace_keeps_python_backslash_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a1 a2")

    assert ed.exec_command_line(r"qreplace 'a([0-9])' '\1'") is True
    assert ed.qreplace is not None
    assert ed.qreplace_yes() is True
    assert ed.cur().buf.get_text() == r"\1 a2"
    assert ed.status_model()["last_message"].startswith("qreplace: y/Enter replace")





def test_qreplace_keeps_leading_zero_numeric_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "ab ab")

    assert ed.exec_command_line("qreplace '(a)(b)' '$01'") is True
    assert ed.qreplace is not None
    assert ed.qreplace_yes() is True

    assert ed.cur().buf.get_text() == "$01 ab"
    assert ed.status_model()["last_message"].startswith("qreplace: y/Enter replace")


def test_qreplace_keeps_malformed_braced_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a a")

    assert ed.exec_command_line("qreplace '(?P<x>a)' '${x>lit}'") is True
    assert ed.qreplace is not None
    assert ed.qreplace_yes() is True

    assert ed.cur().buf.get_text() == "${x>lit} a"
    assert ed.status_model()["last_message"].startswith("qreplace: y/Enter replace")


def test_qreplace_keeps_unterminated_braced_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a a")

    assert ed.exec_command_line("qreplace '(?P<x>a)' '${$1'") is True
    assert ed.qreplace is not None
    assert ed.qreplace_yes() is True

    assert ed.cur().buf.get_text() == "${$1 a"
    assert ed.status_model()["last_message"].startswith("qreplace: y/Enter replace")




def test_qreplace_reports_invalid_replacement_even_when_not_found() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("qreplace 'z([0-9])' '$2'") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"].startswith("qreplace: invalid replacement: ")
    assert "invalid group reference 2" in ed.status_model()["last_message"]

    # Valid replacement templates that simply have no target remain not-found.
    assert ed.exec_command_line("qreplace 'z([0-9])' '$1'") is False
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "qreplace: not found"


def test_qreplace_rejects_invalid_replacement_before_capture() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a1 a2")

    assert ed.exec_command_line("qreplace 'a([0-9])' '$2'") is False

    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.cur().buf.get_text() == "a1 a2"
    assert ed.status_model()["last_message"].startswith("qreplace: invalid replacement: ")
    assert "invalid group reference 2" in ed.status_model()["last_message"]


def test_script_pushed_keymode_does_not_launder_trusted_binding_authority() -> None:
    ed = _new_editor()

    # The binding itself is trusted/user-originated, but the delayed routing
    # frame that exposes it is installed by a script.  A later user-style key
    # dispatch must therefore keep script authority.
    assert ed.exec_command_line('bindmode nav F6 "command:set cap.fs-open true"') is True
    b = ed.keymap.get_binding_exact('F6', mode='nav')
    assert b is not None
    assert b.script_context is False

    with ed.script_context():
        ed.push_key_mode('nav', once=True)
        origin = ed.current_script_origin_id()

    assert ed.key_mode_stack
    top = ed.key_mode_stack[-1]
    assert top.name == 'nav'
    assert top.once is True
    assert top.script_context is True
    assert top.script_origin_id == origin

    ed.messages.clear()
    assert ed.dispatch_key('F6') is False
    assert bool(ed.options.get('cap.fs-open')) is False
    assert any('script context cannot modify capability option: cap.fs-open' in msg for msg in ed.messages)
    assert ed.key_mode_stack == []


def test_script_set_keymode_does_not_launder_trusted_mode_binding_authority() -> None:
    ed = _new_editor()

    assert ed.exec_command_line('bindmode tools F7 "command:set cap.fs-save true"') is True
    with ed.script_context():
        ed.set_key_mode('tools')
        origin = ed.current_script_origin_id()

    assert ed.key_mode_stack[-1].script_context is True
    assert ed.key_mode_stack[-1].script_origin_id == origin

    ed.messages.clear()
    assert ed.dispatch_key('F7') is False
    assert bool(ed.options.get('cap.fs-save')) is False
    assert any('script context cannot modify capability option: cap.fs-save' in msg for msg in ed.messages)
    assert ed.key_mode_stack and ed.key_mode_stack[-1].name == 'tools'


def test_clipboard_mutation_hostcall_type_errors_preserve_arguments() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    bad_cases = [
        ("ed.set-clipboard", [123], "ed.set-clipboard: expected str"),
        ("ed.set-clipboard-items", ["not-list", "items"], "ed.set-clipboard-items: expected list"),
        ("ed.set-clipboard-items", [["x"], 123], "ed.set-clipboard-items: expected str"),
        ("ed.set-clipboard-items", [["x"], "bad-kind"], "kind must be items\\|lines"),
    ]
    for host, args, match in bad_cases:
        ed.vm.stack.clear()
        ed.vm.stack.extend(args)
        with pytest.raises(MicromaxError, match=match):
            _call_host(ed, host)
        assert ed.vm.stack == args
        assert ed.clipboard_text() == ""


def test_macro_hostcall_type_errors_preserve_arguments() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    bad_cases = [
        ("ed.macro-detail-row", [123], "ed.macro-detail-row: expected str"),
        ("ed.macro-get", [123], "ed.macro-get: expected str"),
        ("ed.macro-record", [123], "ed.macro-record: expected str"),
        ("ed.macro-play", [123, 1], "ed.macro-play: expected str"),
        ("ed.macro-play", ["last", "once"], "ed.macro-play: expected int"),
        ("ed.macro-set", ["not-steps", "owned"], "macro: expected list of steps"),
        ("ed.macro-set", [["c", "noop"], 123], "ed.macro-set: expected str"),
    ]
    for host, args, match in bad_cases:
        ed.vm.stack.clear()
        ed.vm.stack.extend(args)
        with pytest.raises(MicromaxError, match=match):
            _call_host(ed, host)
        assert ed.vm.stack == args


def test_script_macro_set_denial_preserves_delayed_execution_payload() -> None:
    from micromax_editor.editor import MacroStep

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.set_macro("trusted", [MacroStep(kind="command", name="command", payload={"cmdline": "help"})])
    replacement = [["c", "set cap.fs-save true"]]

    with ed.script_context():
        ed.vm.stack.clear()
        ed.vm.stack.extend([replacement, "trusted"])
        with pytest.raises(MicromaxError, match="script context cannot modify macro: trusted"):
            _call_host(ed, "ed.macro-set")

    assert ed.vm.stack == [replacement, "trusted"]
    assert ed.macros["trusted"][0].payload["cmdline"] == "help"


def test_qreplace_all_stops_at_configured_replacement_budget_and_keeps_session_active() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one one")
    ed.options.set("qreplace.max", "2")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None

    assert ed.qreplace_all() is True

    assert ed.cur().buf.get_text() == "X X one"
    assert ed.qreplace is not None
    assert ed.current_capture_key_mode() == "qreplace"
    assert ed.status_model()["last_message"] == (
        "qreplace: stopped at qreplace.max 2 (2 replaced; session active)"
    )

    assert ed.qreplace_all() is True
    assert ed.cur().buf.get_text() == "X X X"
    assert ed.qreplace is None
    assert ed.status_model()["last_message"] == "qreplace: done (3 replaced)"


def test_qreplace_all_zero_budget_preserves_unbounded_explicit_opt_in() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one one")
    ed.options.set("qreplace.max", "0")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace_all() is True

    assert ed.cur().buf.get_text() == "X X X"
    assert ed.qreplace is None
    assert ed.status_model()["last_message"] == "qreplace: done (3 replaced)"
