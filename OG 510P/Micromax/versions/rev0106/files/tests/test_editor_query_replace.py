from __future__ import annotations


from micromax_editor.editor import Editor


def test_qreplace_yes_no_and_undo_single_step() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two one two")

    assert ed.exec_command_line("qreplace one X -l") is True
    assert ed.qreplace is not None
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
