from __future__ import annotations

from pathlib import Path

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor


def test_delete_forward_deletes_chars_and_joins_lines() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.run_action("Delete") is True
    assert ed.cur().buf.get_text() == "bc"
    assert (ed.cur().cursors[0].line, ed.cur().cursors[0].col) == (0, 0)

    ed.new_buffer("*t2*", "a\nb")
    ed.cur().cursors[0] = Cursor(0, 1)  # end of 'a'
    assert ed.run_action("Delete") is True
    assert ed.cur().buf.get_text() == "ab"


def test_word_movement_and_selection() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two")

    assert ed.run_action("WordRight") is True
    assert ed.cur().cursors[0].col == 4  # start of 'two'

    assert ed.run_action("WordLeft") is True
    assert ed.cur().cursors[0].col == 0

    # Selection variant
    assert ed.run_action("SelectWordRight") is True
    assert ed.selection_text() == "one "


def test_doc_top_bottom_and_page_moves() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "0\n1\n2\n3\n4")

    # PageDown uses page.height (default 30), so set it to 2 for deterministic test.
    assert ed.exec_command_line("set page.height 2") is True

    assert ed.run_action("PageDown") is True
    assert ed.cur().cursors[0].line == 2

    assert ed.run_action("PageUp") is True
    assert ed.cur().cursors[0].line == 0

    ed.cur().cursors[0] = Cursor(2, 0)
    assert ed.run_action("DocBottom") is True
    assert ed.cur().cursors[0].line == 4

    assert ed.run_action("DocTop") is True
    assert ed.cur().cursors[0].line == 0


def test_open_and_save_round_trip(tmp_path: Path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello", encoding="utf-8")

    ed = Editor()
    ed.exec_command_line(f"open {p}")
    assert ed.cur().buf.get_text() == "hello"

    ed.input["text"] = "!"
    ed.run_action("EndOfLine")
    ed.run_action("InsertText")
    assert ed.cur().buf.dirty is True

    ed.exec_command_line("save")
    assert p.read_text(encoding="utf-8") == "hello!"
    assert ed.cur().buf.dirty is False


def test_quit_warns_on_dirty_buffers_and_can_force() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hello")
    ed.cur().buf.dirty = True

    assert ed.exec_command_line("quit") is False
    assert ed.should_quit is False
    assert ed._quit_armed is True
    assert ed.messages and "unsaved changes" in ed.messages[-1]

    # any other command disarms
    assert ed.exec_command_line("pwd") is True
    assert ed._quit_armed is False

    assert ed.exec_command_line("quit") is False
    assert ed._quit_armed is True

    # second quit actually exits
    assert ed.exec_command_line("quit") is True
    assert ed.should_quit is True

    ed2 = Editor()
    ed2.new_buffer("*t*", "hello")
    ed2.cur().buf.dirty = True
    assert ed2.exec_command_line("quit -f") is True
    assert ed2.should_quit is True
