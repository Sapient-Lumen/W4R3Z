from __future__ import annotations


from micromax_editor.editor import Editor


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
