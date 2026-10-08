from __future__ import annotations

from pathlib import Path

import pytest

from micromax import MicromaxError
from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_ed_open(ed: Editor, path: str):
    vm = ed.vm
    vm.stack.append(str(path))
    vm.stack.append("ed.open")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    ok = int(vm.stack.pop())
    return ok, err


def _call_ed_save(ed: Editor):
    vm = ed.vm
    vm.stack.append("ed.save")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    ok = int(vm.stack.pop())
    return ok, err


def test_ed_open_and_save_are_capability_gated(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    # Disabled by default.
    vm = ed.vm
    vm.stack.append(str(p))
    vm.stack.append("ed.open")
    with pytest.raises(MicromaxError):
        vm.eval("hostcall")

    vm.stack.append("ed.save")
    with pytest.raises(MicromaxError):
        vm.eval("hostcall")

    # Enable open/save.
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line("set cap.fs-save true")

    ed.vm.eval('"ed.open" host.feature?')
    assert int(ed.vm.stack.pop()) == 1
    ed.vm.eval('"ed.save" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ok, err = _call_ed_open(ed, str(p))
    assert ok == 1
    assert err == ""
    assert ed.cur().buf.path and Path(ed.cur().buf.path).resolve() == p.resolve()

    # Modify and save.
    ed.cur().buf.set_text("changed")
    ed.cur().buf.dirty = True
    ok, err = _call_ed_save(ed)
    assert ok == 1
    assert err == ""
    assert p.read_text(encoding="utf-8") == "changed"


def test_ed_open_and_save_respect_cap_fs_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "in.txt"
    inside.write_text("in", encoding="utf-8")

    outside = tmp_path / "out.txt"
    outside.write_text("out", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    ok, err = _call_ed_open(ed, "in.txt")
    assert ok == 1
    assert err == ""

    ok, err = _call_ed_open(ed, str(outside))
    assert ok == 0
    assert "cap.fs-root" in err

    # Saving to an outside path is denied.
    ed.new_buffer("*tmp*", "x", path=str(outside))
    ok, err = _call_ed_save(ed)
    assert ok == 0
    assert "cap.fs-root" in err



def test_save_trims_trailing_whitespace_when_rmtrailingws_is_enabled(tmp_path) -> None:
    p = tmp_path / "trim.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha   \nbeta\t\t\n", path=str(p))
    eb = ed.cur()
    eb.cursors[0].line = 0
    eb.cursors[0].col = len("alpha   ")
    eb.buf.dirty = True

    assert ed.exec_command_line("set rmtrailingws true")
    ed.save()

    assert p.read_text(encoding="utf-8") == "alpha\nbeta\n"
    assert eb.buf.get_text() == "alpha\nbeta\n"
    assert eb.buf.dirty is False
    assert eb.cursors[0].line == 0
    assert eb.cursors[0].col == len("alpha")



def test_save_adds_eof_newline_when_enabled(tmp_path) -> None:
    p = tmp_path / "eof.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha", path=str(p))
    eb = ed.cur()
    eb.cursors[0].line = 0
    eb.cursors[0].col = len("alpha")
    eb.buf.dirty = True

    assert ed.exec_command_line("set eofnewline true")
    ed.save()

    assert p.read_text(encoding="utf-8") == "alpha\n"
    assert eb.buf.get_text() == "alpha\n"
    assert eb.buf.dirty is False
    assert eb.cursors[0].line == 0
    assert eb.cursors[0].col == len("alpha")


def test_save_eofnewline_cleanup_is_undoable(tmp_path) -> None:
    p = tmp_path / "undo-eof.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="x", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("set eofnewline true")
    ed.save()
    assert eb.buf.get_text() == "x\n"
    assert eb.buf.dirty is False

    assert ed.undo.undo() is True
    assert eb.buf.get_text() == "x"
    assert eb.buf.dirty is True


def test_save_combines_rmtrailingws_and_eofnewline_into_saved_text(tmp_path) -> None:
    p = tmp_path / "normalize-save.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha   ", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("set rmtrailingws true")
    assert ed.exec_command_line("set eofnewline true")
    ed.save()

    assert p.read_text(encoding="utf-8") == "alpha\n"
    assert eb.buf.get_text() == "alpha\n"

    assert ed.undo.undo() is True
    assert eb.buf.get_text() == "alpha   "


def test_save_eofnewline_does_not_force_newline_for_empty_buffer(tmp_path) -> None:
    p = tmp_path / "empty.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("set eofnewline true")
    ed.save()

    assert p.read_text(encoding="utf-8") == ""
    assert eb.buf.get_text() == ""

def test_save_rmtrailingws_cleanup_is_undoable(tmp_path) -> None:
    p = tmp_path / "undo-trim.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="x   \ny\n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("set rmtrailingws true")
    ed.save()
    assert eb.buf.get_text() == "x\ny\n"
    assert eb.buf.dirty is False

    assert ed.undo.undo() is True
    assert eb.buf.get_text() == "x   \ny\n"
    assert eb.buf.dirty is True


def test_save_preserves_trailing_whitespace_when_rmtrailingws_is_disabled(tmp_path) -> None:
    p = tmp_path / "keep-trim.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha   \n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    ed.save()

    assert p.read_text(encoding="utf-8") == "alpha   \n"
    assert eb.buf.get_text() == "alpha   \n"


def test_save_creates_missing_parent_directories_when_mkparents_is_enabled(tmp_path) -> None:
    p = tmp_path / "new" / "deep" / "file.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha\n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert not p.parent.exists()
    assert ed.exec_command_line("set mkparents true")
    ed.save()

    assert p.parent.is_dir()
    assert p.read_text(encoding="utf-8") == "alpha\n"
    assert eb.buf.dirty is False


def test_save_without_mkparents_keeps_missing_parent_error(tmp_path) -> None:
    p = tmp_path / "new" / "deep" / "file.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha\n", path=str(p))
    ed.cur().buf.dirty = True

    with pytest.raises(FileNotFoundError):
        ed.save()


def test_open_file_parsecursor_places_cursor_when_enabled(tmp_path) -> None:
    p = tmp_path / 'nav.txt'
    p.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    assert ed.exec_command_line('set parsecursor true')
    assert ed.open_file(f'{p}:2:3') is True
    assert ed.primary_cursor() == Cursor(1, 3)


def test_open_file_parsecursor_line_only_defaults_to_column_zero(tmp_path) -> None:
    p = tmp_path / 'nav.txt'
    p.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    assert ed.exec_command_line('set parsecursor true')
    assert ed.open_file(f'{p}:3') is True
    assert ed.primary_cursor() == Cursor(2, 0)



def test_open_file_detects_dos_fileformat_and_normalizes_buffer_text(tmp_path) -> None:
    p = tmp_path / "dos.txt"
    p.write_bytes(b"alpha\r\nbeta\r\n")

    ed = Editor()
    assert ed.open_file(str(p)) is True

    eb = ed.cur()
    assert eb.buf.get_text() == "alpha\nbeta\n"
    assert ed.options.get("fileformat", local=eb.local_options) == "dos"


def test_open_file_uses_configured_encoding_and_reports_it_in_status(tmp_path) -> None:
    p = tmp_path / "latin1.txt"
    p.write_bytes("café\r\n".encode("latin-1"))

    ed = Editor()
    assert ed.exec_command_line("set encoding latin-1")
    assert ed.open_file(str(p)) is True

    eb = ed.cur()
    assert eb.buf.get_text() == "café\n"
    assert ed.options.get("encoding", local=eb.local_options) == "latin-1"
    assert ed.status_model()["encoding"] == "latin-1"
    assert ed.options.get("fileformat", local=eb.local_options) == "dos"


def test_save_uses_dos_line_endings_when_fileformat_is_dos(tmp_path) -> None:
    p = tmp_path / "dos-save.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha\nbeta\n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("setlocal fileformat dos")
    ed.save()

    assert p.read_bytes() == b"alpha\r\nbeta\r\n"
    assert eb.buf.get_text() == "alpha\nbeta\n"
    assert eb.buf.dirty is False


def test_save_preserves_detected_dos_fileformat_after_edit(tmp_path) -> None:
    p = tmp_path / "detected-dos.txt"
    p.write_bytes(b"alpha\r\nbeta\r\n")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    eb = ed.cur()
    eb.cursors[0] = Cursor(1, len("beta"))
    eb.cursors[0] = eb.buf.insert(eb.cursors[0], "!")

    ed.save()

    assert p.read_bytes() == b"alpha\r\nbeta!\r\n"
    assert ed.options.get("fileformat", local=eb.local_options) == "dos"


def test_save_eofnewline_uses_selected_fileformat(tmp_path) -> None:
    p = tmp_path / "dos-eof.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("setlocal fileformat dos")
    assert ed.exec_command_line("set eofnewline true")
    ed.save()

    assert p.read_bytes() == b"alpha\r\n"
    assert eb.buf.get_text() == "alpha\n"


def test_save_uses_selected_text_encoding(tmp_path) -> None:
    p = tmp_path / "latin1-save.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="café\n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("setlocal encoding latin-1")
    ed.save()

    assert p.read_bytes() == "café\n".encode("latin-1")
    assert eb.buf.get_text() == "café\n"
    assert eb.buf.dirty is False


def test_save_preserves_buffer_local_encoding_after_global_default_changes(tmp_path) -> None:
    p = tmp_path / "buffer-encoding.txt"

    ed = Editor()
    assert ed.exec_command_line("set encoding latin-1")
    ed.new_buffer(name=str(p), text="café\n", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.options.get("encoding", local=eb.local_options) == "latin-1"
    assert ed.exec_command_line("set encoding utf-8")
    ed.save()

    assert p.read_bytes() == "café\n".encode("latin-1")
    assert ed.status_model()["encoding"] == "latin-1"


def test_autosave_saves_dirty_path_buffer_after_interval(tmp_path) -> None:
    p = tmp_path / "auto.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    ed.exec_command_line(f"open {p}")
    assert ed.exec_command_line("set autosave 2") is True

    now = [0.0]
    ed._now_fn = lambda: float(now[0])

    ed.run_action("EndOfLine")
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.dirty is True
    assert p.read_text(encoding="utf-8") == "hello\n"

    now[0] = 1.9
    assert ed.pump_timers() == 0
    assert ed.cur().buf.dirty is True
    assert p.read_text(encoding="utf-8") == "hello\n"

    now[0] = 2.1
    assert ed.pump_timers() == 0
    assert ed.cur().buf.dirty is False
    assert ed.cur().autosave_dirty_since is None
    assert p.read_text(encoding="utf-8") == "hello!\n"


def test_autosave_skips_dirty_buffers_without_paths(tmp_path) -> None:
    ed = Editor()
    ed.new_buffer("*scratch*", "hello")
    assert ed.exec_command_line("set autosave 1") is True

    now = [0.0]
    ed._now_fn = lambda: float(now[0])

    ed.run_action("EndOfLine")
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.dirty is True

    now[0] = 2.0
    assert ed.pump_timers() == 0
    assert ed.cur().buf.dirty is True
    assert ed.cur().buf.get_text() == "hello!"
