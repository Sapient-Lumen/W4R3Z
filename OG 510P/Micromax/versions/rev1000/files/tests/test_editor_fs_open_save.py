from __future__ import annotations

import errno
import multiprocessing
import os
import shlex
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from micromax import MicromaxError
from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.file_recovery import read_file_for_editor
from micromax_editor.file_write import (
    FileContainmentError,
    FileFreshnessConflict,
    FileFreshnessTimeoutError,
    FileMkparentsTimeoutError,
    FileWriteTimeoutError,
    capture_file_freshness,
    capture_file_freshness_bounded,
    ensure_parent_directory_bounded,
    write_file_bytes,
)
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


def _symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")


def test_open_file_uses_vm_read_timeout_boundary(tmp_path, monkeypatch) -> None:
    import micromax_editor.editor as editor_mod

    p = tmp_path / "bounded.txt"
    p.write_text("disk\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 0.125
    calls: list[float | None] = []

    def fake_read(path, *, encoding, containment_root=None, max_bytes=None, timeout_seconds=None):  # type: ignore[no-untyped-def]
        calls.append(timeout_seconds)
        return SimpleNamespace(text="bounded\n", fileformat="unix")

    monkeypatch.setattr(editor_mod, "read_file_for_editor", fake_read)

    assert ed.open_file(str(p)) is True

    assert calls == [0.125]
    assert ed.cur().buf.get_text() == "bounded\n"


def test_open_file_large_result_is_drained_before_worker_join(tmp_path, monkeypatch) -> None:
    """The ordinary editor-open loop must survive a pipe-sized read result."""

    from micromax_editor import file_access

    payload = "open-result\n" * 75_000
    p = tmp_path / "large-open.txt"
    p.write_text(payload, encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 3.0  # type: ignore[attr-defined]

    context = multiprocessing.get_context("spawn")
    monkeypatch.setattr(file_access, "_fs_worker_context", lambda: context)

    assert ed.open_file(str(p)) is True
    assert ed.cur().buf.get_text() == payload


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


def test_save_command_reports_saved_path(tmp_path) -> None:
    p = tmp_path / "save-msg.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha\n", path=str(p))
    ed.cur().buf.dirty = True

    assert ed.exec_command_line("save") is True

    assert ed.messages[-1] == f"saved: {p}"


def test_save_command_reports_normalization_steps(tmp_path) -> None:
    p = tmp_path / "save-normalize-msg.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="alpha   ", path=str(p))
    ed.cur().buf.dirty = True

    assert ed.exec_command_line("set rmtrailingws true")
    assert ed.exec_command_line("set eofnewline true")
    assert ed.exec_command_line("save") is True

    assert ed.messages[-1] == f"saved: {p} (normalized: trim trailing whitespace, add eof newline)"


def test_saveas_refuses_open_target_without_saving_wrong_buffer(tmp_path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("A", encoding="utf-8")
    b.write_text("B", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line(f"open {shlex.quote(str(a))}") is True
    ed.cur().buf.set_text("A*")
    ed.cur().buf.dirty = True
    assert ed.exec_command_line(f"open {shlex.quote(str(b))}") is True
    assert ed.switch_buffer(str(a)) is True

    assert ed.exec_command_line(f"saveas {shlex.quote(str(b))}") is False

    assert ed.active == str(a)
    assert ed.cur().name == str(a)
    assert ed.cur().buf.path == str(a)
    assert ed.cur().buf.get_text() == "A*"
    assert ed.buffers[str(b)].buf.get_text() == "B"
    assert a.read_text(encoding="utf-8") == "A"
    assert b.read_text(encoding="utf-8") == "B"
    assert ed.messages[-1] == f"save: target already open: {b}"


def test_saveas_failed_write_restores_pathless_buffer_identity(tmp_path) -> None:
    target_dir = tmp_path / "already-a-dir"
    target_dir.mkdir()

    ed = Editor()
    ed.new_buffer(name="draft", text="draft text", path=None)
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target_dir))}") is False

    assert ed.active == "draft"
    assert "draft" in ed.buffers
    assert str(target_dir) not in ed.buffers
    assert eb.name == "draft"
    assert eb.buf.path is None
    assert eb.buf.get_text() == "draft text"
    assert eb.buf.dirty is True
    assert "Is a directory" in ed.messages[-1] or "is a directory" in ed.messages[-1]


def test_saveas_failed_write_restores_marks_and_mru(tmp_path) -> None:
    target_dir = tmp_path / "dir-target"
    target_dir.mkdir()

    ed = Editor()
    ed.new_buffer(name="draft", text="one", path=None)
    ed.mark_set("a")
    ed.new_buffer(name="other", text="two", path=None)
    assert ed.switch_buffer("draft") is True
    before_mru = list(ed._buffer_mru)

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target_dir))}") is False

    assert ed.active == "draft"
    assert ed._buffer_mru == before_mru
    assert ed.marks["a"][0] == "draft"
    assert str(target_dir) not in ed.buffers


def test_failed_save_does_not_apply_cleanup_or_record_undo(tmp_path) -> None:
    p = tmp_path / "encoding-fail.txt"
    p.write_text("old", encoding="utf-8")

    ed = Editor()
    ed.new_buffer(name=str(p), text="café   ", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    assert ed.exec_command_line("set rmtrailingws true")
    assert ed.exec_command_line("setlocal encoding ascii")
    before_depth = ed.undo.depth()

    assert ed.exec_command_line("save") is False

    assert eb.buf.get_text() == "café   "
    assert eb.buf.dirty is True
    assert ed.undo.depth() == before_depth
    assert p.read_text(encoding="utf-8") == "old"
    assert "codec" in ed.messages[-1]


def test_failed_save_cleanup_rollback_preserves_fastdirty_clean_state(tmp_path) -> None:
    p = tmp_path / "fastdirty-encoding-fail.txt"
    p.write_text("café   ", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    eb = ed.cur()
    assert eb.buf.dirty is False

    assert ed.exec_command_line("set fastdirty true")
    assert ed.exec_command_line("set rmtrailingws true")
    assert ed.exec_command_line("setlocal encoding ascii")
    before_depth = ed.undo.depth()
    before_version = eb.buf.version

    assert ed.exec_command_line("save") is False

    assert eb.buf.get_text() == "café   "
    assert eb.buf.dirty is False
    assert eb.buf.fastdirty is True
    assert eb.buf.version == before_version
    assert ed.undo.depth() == before_depth
    assert p.read_text(encoding="utf-8") == "café   "


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


def test_parsecursor_existing_literal_path_uses_bounded_stat(tmp_path, monkeypatch) -> None:
    p = tmp_path / "literal:colon"
    p.write_text("alpha\n", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set parsecursor true")
    calls: list[tuple[str, object]] = []

    def fake_bounded_stat(path, *, containment_root=None):  # type: ignore[no-untyped-def]
        calls.append((str(path), containment_root))
        return SimpleNamespace(exists=True, kind="file", size=6, mtime=0)

    monkeypatch.setattr(ed, "_bounded_fs_stat", fake_bounded_stat)

    parsed, cursor = ed._parse_open_target(str(p))

    assert parsed == str(p)
    assert cursor is None
    assert calls
    assert calls[0][0].endswith("literal:colon")


def test_parsecursor_palette_literal_check_uses_preseeded_stat_cache(tmp_path, monkeypatch) -> None:
    p = tmp_path / "literal:palette"
    p.write_text("alpha\n", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set parsecursor true")
    assert ed.exec_command_line("set cap.fs-list true")
    ed._seed_palette_fs_stat_cache([str(p)])

    def fail_bounded_stat(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("palette parsecursor should use the preseeded stat cache")

    monkeypatch.setattr(ed, "_bounded_fs_stat", fail_bounded_stat)

    parsed, cursor = ed._parse_open_target(str(p), use_palette_stat_cache=True)

    assert parsed == str(p)
    assert cursor is None


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



def test_open_command_reports_target_path_and_landed_cursor(tmp_path) -> None:
    p = tmp_path / 'nav.txt'
    p.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    assert ed.exec_command_line('set parsecursor true')
    assert ed.exec_command_line(f'open {p}:2:3') is True
    assert ed.primary_cursor() == Cursor(1, 3)
    assert ed.status_model()['last_message'] == f'opened: {p} @ 2:3'



def test_open_command_reports_restored_saved_cursor_position(tmp_path) -> None:
    p = tmp_path / 'saved-cursor.txt'
    p.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    assert ed.exec_command_line('set savecursor true')
    norm = ed._normalize_path(str(p))
    assert norm
    ed._saved_cursors[str(norm)] = {'line': 2, 'col': 1}
    assert ed.exec_command_line(f'open {p}') is True
    assert ed.primary_cursor() == Cursor(2, 1)
    assert ed.status_model()['last_message'] == f'opened: {p} @ 3:1'



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


def test_atomic_save_replace_failure_keeps_disk_and_buffer_state(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    p = tmp_path / "atomic-fail.txt"
    p.write_text("old\n", encoding="utf-8")

    ed = Editor()
    ed.new_buffer(name=str(p), text="new   ", path=str(p))
    eb = ed.cur()
    eb.buf.dirty = True
    assert ed.exec_command_line("set rmtrailingws true")

    def fail_replace(src, dst, **kwargs):
        raise OSError("replace failed intentionally")

    monkeypatch.setattr(file_write.os, "replace", fail_replace)
    before_depth = ed.undo.depth()
    before_version = eb.buf.version

    assert ed.exec_command_line("save") is False

    assert p.read_text(encoding="utf-8") == "old\n"
    assert eb.buf.get_text() == "new   "
    assert eb.buf.dirty is True
    assert eb.buf.version == before_version
    assert ed.undo.depth() == before_depth
    assert not list(tmp_path.glob(".atomic-fail.txt.micromax-*.tmp"))
    assert "replace failed intentionally" in ed.messages[-1]


def test_atomic_save_preserves_existing_permission_bits(tmp_path) -> None:
    import os
    import stat

    if os.name == "nt":
        pytest.skip("POSIX permission-bit preservation is not stable on Windows")

    p = tmp_path / "mode.txt"
    p.write_text("old", encoding="utf-8")
    p.chmod(0o640)

    ed = Editor()
    ed.new_buffer(name=str(p), text="new", path=str(p))
    ed.cur().buf.dirty = True
    info = ed.save()

    assert p.read_text(encoding="utf-8") == "new"
    assert stat.S_IMODE(p.stat().st_mode) == 0o640
    assert info["atomic"] is True


def test_atomic_save_preserves_symlink_and_updates_link_target(tmp_path) -> None:
    import os

    if not hasattr(os, "symlink"):
        pytest.skip("symlink support not available")

    target = tmp_path / "real.txt"
    target.write_text("old", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    ed.new_buffer(name=str(link), text="new", path=str(link))
    ed.cur().buf.dirty = True
    info = ed.save()

    assert link.is_symlink()
    assert target.read_text(encoding="utf-8") == "new"
    assert link.read_text(encoding="utf-8") == "new"
    assert info["atomic"] is True
    assert info["followed_symlink"] is True


def test_file_writer_refuses_symlink_escape_from_containment_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / "link.txt"
    _symlink_or_skip(link, outside)

    with pytest.raises(FileContainmentError, match="outside containment root"):
        write_file_bytes(link, b"changed", containment_root=root)

    assert link.is_symlink()
    assert outside.read_text(encoding="utf-8") == "outside"
    assert not list(root.glob(".link.txt.micromax-*.tmp"))


def test_atomic_file_writer_refuses_parent_directory_swap_and_cleans_temp(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    if not file_write._dir_fd_io_available():
        pytest.skip("dir-fd writer path not available on this host")

    root = tmp_path / "root"
    work = root / "work"
    work.mkdir(parents=True)
    p = work / "note.txt"
    p.write_text("old", encoding="utf-8")
    parked = root / "work-parked"
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_note = outside / "note.txt"
    outside_note.write_text("outside", encoding="utf-8")

    original_open_temp = file_write._open_temp_file
    swapped = {"done": False}

    def swap_parent_after_temp(parent, basename, **kwargs):
        fd, tmp = original_open_temp(parent, basename, **kwargs)
        if kwargs.get("dir_fd") is not None and not swapped["done"]:
            swapped["done"] = True
            work.rename(parked)
            work.symlink_to(outside, target_is_directory=True)
        return fd, tmp

    monkeypatch.setattr(file_write, "_open_temp_file", swap_parent_after_temp)

    with pytest.raises(FileContainmentError, match="outside containment root"):
        write_file_bytes(p, b"new", containment_root=root)

    assert swapped["done"] is True
    assert work.is_symlink()
    assert outside_note.read_text(encoding="utf-8") == "outside"
    assert (parked / "note.txt").read_text(encoding="utf-8") == "old"
    assert not list(parked.glob(".note.txt.micromax-*.tmp"))



def test_atomic_file_writer_detects_in_root_parent_replacement_without_proc_fd_path(
    tmp_path, monkeypatch
) -> None:
    """A pinned dir fd, not /proc path text, owns the commit authority."""

    from micromax_editor import file_write

    if not file_write._dir_fd_io_available():
        pytest.skip("dir-fd writer path not available on this host")

    root = tmp_path / "root"
    work = root / "work"
    work.mkdir(parents=True)
    target = work / "note.txt"
    target.write_text("old", encoding="utf-8")
    parked = root / "work-parked"

    original_open_temp = file_write._open_temp_file
    swapped = {"done": False}

    def replace_parent_after_temp(parent, basename, **kwargs):
        fd, temp = original_open_temp(parent, basename, **kwargs)
        if kwargs.get("dir_fd") is not None and not swapped["done"]:
            swapped["done"] = True
            work.rename(parked)
            work.mkdir()
            (work / "note.txt").write_text("decoy", encoding="utf-8")
        return fd, temp

    monkeypatch.setattr(file_write, "_open_temp_file", replace_parent_after_temp)
    monkeypatch.setattr(file_write, "_resolve_dir_fd", lambda _fd: None)

    with pytest.raises(FileContainmentError, match="parent directory changed"):
        write_file_bytes(target, b"new", containment_root=root)

    assert swapped["done"] is True
    assert (parked / "note.txt").read_text(encoding="utf-8") == "old"
    assert (work / "note.txt").read_text(encoding="utf-8") == "decoy"
    assert not list(parked.glob(".note.txt.micromax-*.tmp"))
    assert not list(work.glob(".note.txt.micromax-*.tmp"))



def test_direct_file_writer_refuses_symlink_escape_from_containment_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside-direct.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / "direct-link.txt"
    _symlink_or_skip(link, outside)

    with pytest.raises(FileContainmentError, match="outside containment root"):
        write_file_bytes(link, b"changed", atomic=False, containment_root=root)

    assert link.is_symlink()
    assert outside.read_text(encoding="utf-8") == "outside"


def test_direct_file_writer_path_fallback_rechecks_opened_fd_content_hash(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    p = tmp_path / "direct-path-same-stat-race.txt"
    p.write_text("base", encoding="utf-8")
    st = p.stat()
    expected = capture_file_freshness(p, max_hash_bytes=1024)

    monkeypatch.setattr(file_write, "_dir_fd_io_available", lambda: False)
    original_assert = file_write.assert_file_freshness
    raced = {"done": False}

    def race_after_path_freshness(path, expected_state, **kwargs):
        original_assert(path, expected_state, **kwargs)
        if not raced["done"]:
            raced["done"] = True
            p.write_text("evil", encoding="utf-8")
            p.chmod(st.st_mode & 0o7777)
            import os

            os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))

    monkeypatch.setattr(file_write, "assert_file_freshness", race_after_path_freshness)

    with pytest.raises(FileFreshnessConflict, match="file changed on disk"):
        write_file_bytes(
            p,
            b"ours",
            atomic=False,
            expected_state=expected,
            expected_hash_max=1024,
        )

    assert raced["done"] is True
    assert p.read_text(encoding="utf-8") == "evil"


def test_direct_file_writer_rechecks_opened_fd_content_hash_before_truncate(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    if not file_write._dir_fd_io_available():
        pytest.skip("dir-fd direct writer path not available on this host")

    p = tmp_path / "direct-same-stat-race.txt"
    p.write_text("base", encoding="utf-8")
    st = p.stat()
    expected = capture_file_freshness(p, max_hash_bytes=1024)

    original_assert = file_write._assert_file_freshness_at
    raced = {"done": False}

    def race_after_path_freshness(dir_fd, name, expected_state, **kwargs):
        original_assert(dir_fd, name, expected_state, **kwargs)
        if not raced["done"]:
            raced["done"] = True
            p.write_text("evil", encoding="utf-8")
            p.chmod(st.st_mode & 0o7777)
            import os

            os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))

    monkeypatch.setattr(file_write, "_assert_file_freshness_at", race_after_path_freshness)

    with pytest.raises(FileFreshnessConflict, match="file changed on disk"):
        write_file_bytes(
            p,
            b"ours",
            atomic=False,
            expected_state=expected,
            expected_hash_max=1024,
        )

    assert raced["done"] is True
    assert p.read_text(encoding="utf-8") == "evil"


def test_direct_file_writer_rechecks_opened_fd_before_truncate(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    if not file_write._dir_fd_io_available():
        pytest.skip("dir-fd direct writer path not available on this host")

    p = tmp_path / "direct-race.txt"
    p.write_text("base", encoding="utf-8")
    expected = capture_file_freshness(p, max_hash_bytes=1024)

    original_assert = file_write._assert_file_freshness_at
    raced = {"done": False}

    def race_after_path_freshness(dir_fd, name, expected_state, **kwargs):
        original_assert(dir_fd, name, expected_state, **kwargs)
        if not raced["done"]:
            raced["done"] = True
            p.write_text("theirs", encoding="utf-8")

    monkeypatch.setattr(file_write, "_assert_file_freshness_at", race_after_path_freshness)

    with pytest.raises(FileFreshnessConflict, match="file changed on disk"):
        write_file_bytes(
            p,
            b"ours",
            atomic=False,
            expected_state=expected,
            expected_hash_max=1024,
        )

    assert raced["done"] is True
    assert p.read_text(encoding="utf-8") == "theirs"


def test_file_recovery_read_refuses_symlink_escape_from_containment_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside-read.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / "read-link.txt"
    _symlink_or_skip(link, outside)

    with pytest.raises(FileContainmentError, match="outside containment root"):
        read_file_for_editor(link, encoding="utf-8", containment_root=root)


def test_atomic_save_rechecks_external_change_immediately_before_replace(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    p = tmp_path / "precommit-race.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True

    original_open_temp = file_write._open_temp_file
    raced = {"done": False}

    def racing_open_temp(parent, basename, **kwargs):
        fd, tmp = original_open_temp(parent, basename, **kwargs)
        if not raced["done"]:
            raced["done"] = True
            p.write_text("theirs", encoding="utf-8")
        return fd, tmp

    monkeypatch.setattr(file_write, "_open_temp_file", racing_open_temp)

    assert ed.exec_command_line("save") is False

    assert raced["done"] is True
    assert p.read_text(encoding="utf-8") == "theirs"
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True
    assert not list(tmp_path.glob(".precommit-race.txt.micromax-*.tmp"))
    assert "before save commit" in ed.messages[-1]


def test_saveas_missing_target_rechecks_create_race_immediately_before_replace(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    source = tmp_path / "precommit-saveas-source.txt"
    target = tmp_path / "precommit-saveas-target.txt"
    source.write_text("source", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(source)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True

    original_open_temp = file_write._open_temp_file
    raced = {"done": False}

    def racing_open_temp(parent, basename, **kwargs):
        fd, tmp = original_open_temp(parent, basename, **kwargs)
        if Path(parent) == target.parent and basename == target.name and not raced["done"]:
            raced["done"] = True
            target.write_text("theirs", encoding="utf-8")
        return fd, tmp

    monkeypatch.setattr(file_write, "_open_temp_file", racing_open_temp)

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target))}") is False

    assert raced["done"] is True
    assert target.read_text(encoding="utf-8") == "theirs"
    assert source.read_text(encoding="utf-8") == "source"
    assert ed.cur().buf.path == str(source)
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True
    assert not list(tmp_path.glob(".precommit-saveas-target.txt.micromax-*.tmp"))
    assert "before save commit" in ed.messages[-1]


def test_save_refuses_external_permission_change_since_open(tmp_path) -> None:
    import os
    import stat

    if os.name == "nt":
        pytest.skip("POSIX chmod freshness is not stable on Windows")

    p = tmp_path / "chmod-stale.txt"
    p.write_text("base", encoding="utf-8")
    p.chmod(0o640)

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.chmod(0o600)

    assert ed.exec_command_line("save") is False

    assert p.read_text(encoding="utf-8") == "base"
    assert stat.S_IMODE(p.stat().st_mode) == 0o600
    assert ed.cur().buf.get_text() == "ours"
    assert "file changed on disk" in ed.messages[-1]




def test_save_freshness_timeout_maps_at_worker_boundary(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    target = tmp_path / "freshness-timeout.txt"
    target.write_text("old", encoding="utf-8")
    created: list[object] = []

    def fake_create(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        created.append(_kwargs.get("target"))
        return object(), object()

    def fake_collect(_proc, _channel, **kwargs):  # type: ignore[no-untyped-def]
        raise kwargs["timeout_error"]()

    monkeypatch.setattr(file_write, "create_one_shot_worker", fake_create)
    monkeypatch.setattr(file_write, "_collect_write_worker_result", fake_collect)

    with pytest.raises(FileFreshnessTimeoutError) as excinfo:
        capture_file_freshness_bounded(
            target,
            max_hash_bytes=1024,
            timeout_seconds=0.05,
        )

    assert created == [file_write._capture_file_freshness_worker]
    assert "filesystem freshness check timed out" in str(excinfo.value)

def test_save_passes_vm_tunable_freshness_timeout_for_checkexternal(tmp_path, monkeypatch) -> None:
    import micromax_editor.editor as editor_mod

    p = tmp_path / "freshness-boundary.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    ed.new_buffer(name=str(p), text="ours", path=str(p))
    # This test verifies save-time option plumbing, not whether a fresh worker
    # can start within 125 ms on every CI/cloudtainer scheduler.  Keep buffer
    # construction on the normal budget and install the narrow budget only for
    # the instrumented save below.
    ed.vm.editor_file_freshness_timeout_seconds = 0.125
    ed.cur().disk_signature = capture_file_freshness(p).signature
    ed.cur().buf.dirty = True

    calls: list[float | None] = []

    def spy(path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(kwargs.get("timeout_seconds"))
        return capture_file_freshness(path, max_hash_bytes=kwargs.get("max_hash_bytes", 0))

    monkeypatch.setattr(editor_mod, "capture_file_freshness_bounded", spy)

    assert ed.save()["path"] == str(p)

    assert 0.125 in calls
    assert p.read_text(encoding="utf-8") == "ours"


def test_save_directory_preflight_uses_bounded_stat(tmp_path, monkeypatch) -> None:
    import micromax_editor.editor as editor_mod

    p = tmp_path / "dir-target"
    p.mkdir()

    ed = Editor()
    ed.vm.editor_hostcall_fs_stat_timeout_seconds = 0.125
    ed.new_buffer(name=str(p), text="payload", path=str(p))
    ed.cur().buf.dirty = True

    calls: list[float | None] = []

    def fake_stat(path, *, containment_root=None, timeout_seconds=None):  # type: ignore[no-untyped-def]
        calls.append(timeout_seconds)
        return SimpleNamespace(exists=True, kind="dir", size=0, mtime=0)

    monkeypatch.setattr(editor_mod, "stat_path_contained_bounded", fake_stat)

    with pytest.raises(IsADirectoryError):
        ed.save()

    assert calls == [0.125]



def test_mkparents_timeout_maps_before_target_write(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    parent = tmp_path / "slow-parent"
    created: list[object] = []

    def fake_create(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        created.append(_kwargs.get("target"))
        return object(), object()

    def fake_collect(_proc, _channel, **kwargs):  # type: ignore[no-untyped-def]
        raise kwargs["timeout_error"]()

    monkeypatch.setattr(file_write, "create_one_shot_worker", fake_create)
    monkeypatch.setattr(file_write, "_collect_write_worker_result", fake_collect)

    with pytest.raises(FileMkparentsTimeoutError) as excinfo:
        ensure_parent_directory_bounded(parent, timeout_seconds=0.05)

    assert created == [file_write._ensure_parent_directory_worker]
    assert "filesystem parent creation timed out" in str(excinfo.value)
    assert not parent.exists()

def test_save_passes_vm_tunable_mkparents_timeout(tmp_path, monkeypatch) -> None:
    import micromax_editor.editor as editor_mod

    p = tmp_path / "a" / "b" / "file.txt"
    ed = Editor()
    ed.vm.editor_file_mkparents_timeout_seconds = 0.125
    ed.new_buffer(name=str(p), text="nested", path=str(p))
    ed.cur().buf.dirty = True
    assert ed.exec_command_line("setlocal mkparents true")

    calls: list[float | None] = []

    def spy(path, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(kwargs.get("timeout_seconds"))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(editor_mod, "ensure_parent_directory_bounded", spy)

    assert ed.save()["path"] == str(p)

    assert calls == [0.125]
    assert p.read_text(encoding="utf-8") == "nested"


def test_atomic_file_writer_timeout_preserves_target_and_wires_exact_cleanup(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "atomic-timeout.txt"
    target.write_bytes(b"old")
    cleanup_calls: list[tuple[str, int | None, str | None]] = []

    def fake_create(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        assert _kwargs.get("target") is file_write._write_file_bytes_worker
        return object(), object()

    def fake_cleanup(path, worker_pid, *, lease_id, containment_root):  # type: ignore[no-untyped-def]
        assert containment_root is None
        cleanup_calls.append((str(path), worker_pid, lease_id))

    def fake_collect(_proc, _channel, **kwargs):  # type: ignore[no-untyped-def]
        cleanup = kwargs.get("abnormal_cleanup")
        assert cleanup is not None
        cleanup(4242)
        raise kwargs["timeout_error"]()

    monkeypatch.setattr(file_write, "create_one_shot_worker", fake_create)
    monkeypatch.setattr(file_write, "_cleanup_atomic_write_temps_bounded", fake_cleanup)
    monkeypatch.setattr(file_write, "_collect_write_worker_result", fake_collect)

    with pytest.raises(FileWriteTimeoutError) as excinfo:
        write_file_bytes(target, b"new", atomic=True, timeout_seconds=0.05)

    assert "filesystem write timed out" in str(excinfo.value)
    assert target.read_bytes() == b"old"
    assert len(cleanup_calls) == 1
    cleanup_path, cleanup_pid, cleanup_lease = cleanup_calls[0]
    assert cleanup_path == str(target)
    assert cleanup_pid == 4242
    assert isinstance(cleanup_lease, str) and len(cleanup_lease) == 32

def test_direct_file_writer_timeout_stays_in_process_to_avoid_partial_kill(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    target = tmp_path / "direct-timeout.txt"
    target.write_bytes(b"old")

    def fail_if_called(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("direct writes must not use the killable atomic worker")

    monkeypatch.setattr(file_write, "_write_file_bytes_bounded", fail_if_called)

    result = file_write.write_file_bytes(
        target,
        b"new",
        atomic=False,
        timeout_seconds=0.01,
    )

    assert target.read_bytes() == b"new"
    assert result.atomic is False


def test_save_atomic_option_can_use_legacy_direct_write_path(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    p = tmp_path / "direct.txt"
    ed = Editor()
    ed.new_buffer(name=str(p), text="direct", path=str(p))
    ed.cur().buf.dirty = True
    assert ed.exec_command_line("setlocal save.atomic false")

    calls = []
    original = file_write.write_file_bytes

    def spy(path, payload, **kwargs):
        calls.append(dict(kwargs))
        return original(path, payload, **kwargs)

    monkeypatch.setattr("micromax_editor.editor.write_file_bytes", spy)
    info = ed.save()

    assert p.read_text(encoding="utf-8") == "direct"
    assert calls and calls[0]["atomic"] is False
    assert calls[0]["timeout_seconds"] == pytest.approx(0.0)
    assert info["atomic"] is False




def test_save_passes_vm_tunable_atomic_write_timeout(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    p = tmp_path / "vm-timeout.txt"
    ed = Editor()
    ed.vm.editor_file_write_timeout_seconds = 0.125
    ed.new_buffer(name=str(p), text="bounded", path=str(p))
    ed.cur().buf.dirty = True

    calls = []
    original = file_write.write_file_bytes

    def spy(path, payload, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(dict(kwargs))
        # The assertion is about forwarding the configured budget.  Execute the
        # same write in-process so scheduler startup variance cannot turn this
        # plumbing test into a process-launch benchmark.
        return original(path, payload, **{**kwargs, "timeout_seconds": 0.0})

    monkeypatch.setattr("micromax_editor.editor.write_file_bytes", spy)

    info = ed.save()

    assert p.read_text(encoding="utf-8") == "bounded"
    assert calls and calls[0]["atomic"] is True
    assert calls[0]["timeout_seconds"] == pytest.approx(0.125)
    assert info["atomic"] is True


def test_save_refuses_external_file_change_since_open(tmp_path) -> None:
    p = tmp_path / "external.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("save") is False

    assert p.read_text(encoding="utf-8") == "theirs"
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True
    assert "file changed on disk" in ed.messages[-1]


def test_save_checkexternal_can_be_disabled_for_explicit_overwrite(tmp_path) -> None:
    p = tmp_path / "external-overwrite.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("setlocal save.checkexternal false") is True
    assert ed.exec_command_line("save") is True

    assert p.read_text(encoding="utf-8") == "ours"
    assert ed.cur().buf.dirty is False


def test_saveas_failed_write_restores_disk_freshness_witness(tmp_path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("base", encoding="utf-8")
    target_dir = tmp_path / "dir-target"
    target_dir.mkdir()

    ed = Editor()
    assert ed.open_file(str(source)) is True
    before_sig = ed.cur().disk_signature
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target_dir))}") is False

    assert ed.cur().buf.path == str(source)
    assert ed.cur().disk_signature == before_sig
    assert source.read_text(encoding="utf-8") == "base"


def test_saveas_existing_target_uses_new_path_freshness_witness(tmp_path) -> None:
    source = tmp_path / "source-saveas.txt"
    target = tmp_path / "target-saveas.txt"
    source.write_text("source", encoding="utf-8")
    target.write_text("target", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(source)) is True
    old_sig = ed.cur().disk_signature
    assert old_sig is not None
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target))}") is True

    assert source.read_text(encoding="utf-8") == "source"
    assert target.read_text(encoding="utf-8") == "ours"
    assert ed.cur().buf.path == str(target)
    assert ed.cur().disk_signature is not None
    assert ed.cur().disk_signature != old_sig


def test_save_same_path_argument_does_not_bypass_external_change_guard(tmp_path) -> None:
    p = tmp_path / "same-path-stale.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs-later", encoding="utf-8")

    assert ed.exec_command_line(f"save {shlex.quote(str(p))}") is False

    assert p.read_text(encoding="utf-8") == "theirs-later"
    assert ed.cur().buf.get_text() == "ours"
    assert "run `diff`, `revert!`, or `save!`" in ed.messages[-1]


def test_save_bang_forces_external_overwrite_and_refreshes_witness(tmp_path) -> None:
    p = tmp_path / "force-stale.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs-later", encoding="utf-8")

    assert ed.exec_command_line("save!") is True

    assert p.read_text(encoding="utf-8") == "ours"
    assert ed.cur().buf.dirty is False
    assert "forced overwrite" in ed.messages[-1]
    assert ed.status_model()["disk_state"] == "fresh"

    ed.cur().buf.set_text("ours-again")
    ed.cur().buf.dirty = True
    p.write_text("theirs-again", encoding="utf-8")
    assert ed.exec_command_line("save") is False
    assert p.read_text(encoding="utf-8") == "theirs-again"


def test_status_model_disk_state_uses_seeded_cache_and_slow_refresh(tmp_path, monkeypatch) -> None:
    p = tmp_path / "status-cache.txt"
    p.write_text("base", encoding="utf-8")

    now = {"t": 10.0}
    ed = Editor()
    ed._now_fn = lambda: now["t"]
    assert ed.open_file(str(p)) is True

    original = ed._capture_disk_freshness
    calls = {"n": 0}

    def counted_capture(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(ed, "_capture_disk_freshness", counted_capture)

    st = ed.status_model()
    assert st["disk_state"] == "fresh"
    assert st["disk_status_stale"] == 0
    assert calls["n"] == 0

    p.write_text("changed externally", encoding="utf-8")
    assert ed.status_model()["disk_state"] == "fresh"
    assert calls["n"] == 0

    now["t"] += 0.251
    st = ed.status_model()
    assert st["disk_state"] == "fresh"
    assert st["disk_status_stale"] == 1
    assert calls["n"] == 0

    now["t"] += 0.750
    st = ed.status_model()
    assert st["disk_state"] == "changed"
    assert st["disk_status_stale"] == 0
    assert calls["n"] == 1


def test_status_readonly_refresh_uses_bounded_access_probe(tmp_path, monkeypatch) -> None:
    import micromax_editor.editor as editor_mod

    p = tmp_path / "readonly-status.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    calls: list[tuple[str, object, float | None]] = []

    def fake_access(path, *, containment_root=None, timeout_seconds=None):  # type: ignore[no-untyped-def]
        calls.append((str(path), containment_root, timeout_seconds))
        return SimpleNamespace(path=str(path), exists=True, kind="file", writable=False)

    monkeypatch.setattr(editor_mod, "access_path_contained_bounded", fake_access)

    status = ed.status_model()

    assert status["readonly"] == 1
    assert calls
    assert calls[0][2] is not None


def test_disk_state_rows_refreshes_even_when_status_cache_is_warm(tmp_path) -> None:
    p = tmp_path / "diskstate-refresh.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    assert ed.status_model()["disk_state"] == "fresh"

    p.write_text("changed externally", encoding="utf-8")
    rows = ed.disk_state_rows()

    assert rows
    assert str(rows[0][1]) == "changed"


def test_status_model_and_default_statusline_expose_stale_disk_state(tmp_path) -> None:
    p = tmp_path / "status-stale.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set diskstate.cachems 0") is True
    assert ed.open_file(str(p)) is True
    assert ed.exec_command_line("setlocal basename true") is True
    assert ed.status_model()["disk_state"] == "fresh"
    assert "disk:" not in ed.statusline_text(120)

    p.write_text("external-change-has-different-size", encoding="utf-8")
    st = ed.status_model()
    assert st["disk_state"] == "changed"
    assert st["disk_changed"] == 1
    assert st["disk_warning"] == 1
    assert "[disk:changed]" in ed.statusline_text(120)

    p.unlink()
    st = ed.status_model()
    assert st["disk_state"] == "missing"
    assert st["disk_missing"] == 1
    assert "[disk:missing]" in ed.statusline_text(120)


def test_open_missing_path_save_refuses_file_created_after_open(tmp_path) -> None:
    p = tmp_path / "created-after-open.txt"

    ed = Editor()
    assert ed.exec_command_line("set diskstate.cachems 0") is True
    assert ed.open_file(str(p)) is True
    assert ed.status_model()["disk_state"] == "new"
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("save") is False

    assert p.read_text(encoding="utf-8") == "theirs"
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True
    assert ed.status_model()["disk_state"] == "changed"
    assert "run `diff`, `revert!`, or `save!`" in ed.messages[-1]


def test_new_path_buffer_save_refuses_file_created_after_buffer_creation(tmp_path) -> None:
    p = tmp_path / "created-after-new-buffer.txt"

    ed = Editor()
    assert ed.exec_command_line("set diskstate.cachems 0") is True
    ed.new_buffer(name=str(p), text="ours", path=str(p))
    assert ed.status_model()["disk_state"] == "new"
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("save") is False

    assert p.read_text(encoding="utf-8") == "theirs"
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True


def test_save_bang_can_explicitly_overwrite_file_created_after_open(tmp_path) -> None:
    p = tmp_path / "force-created-after-open.txt"

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("save!") is True

    assert p.read_text(encoding="utf-8") == "ours"
    assert ed.cur().buf.dirty is False
    assert ed.status_model()["disk_state"] == "fresh"
    assert "forced overwrite" in ed.messages[-1]


def test_save_checkexternal_hash_catches_same_stat_mutation(tmp_path) -> None:
    import os

    from micromax_editor.file_write import file_state_signature

    p = tmp_path / "same-stat.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    before_sig = file_state_signature(p)
    before_stat = p.stat()
    before_hash = ed.cur().disk_content_hash
    assert before_hash is not None

    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("evil", encoding="utf-8")
    os.utime(p, ns=(before_stat.st_atime_ns, before_stat.st_mtime_ns))
    if file_state_signature(p) != before_sig:
        pytest.skip("filesystem did not preserve enough timestamp precision for same-stat check")

    # The visible status model stays stat-cheap because it may render on every
    # keypress; the stronger content hash check is paid at the save boundary.
    assert ed.status_model()["disk_state"] == "fresh"
    assert ed.exec_command_line("save") is False

    assert p.read_text(encoding="utf-8") == "evil"
    assert ed.cur().buf.get_text() == "ours"
    assert "run `diff`, `revert!`, or `save!`" in ed.messages[-1]


def test_saveas_missing_target_refuses_same_turn_created_file(tmp_path, monkeypatch) -> None:
    source = tmp_path / "saveas-race-source.txt"
    target = tmp_path / "saveas-race-target.txt"
    source.write_text("source", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(source)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True

    original_capture = ed._capture_disk_freshness
    calls = {"target": 0}

    def racing_capture(eb, path):
        if Path(path) == target:
            calls["target"] += 1
            result = original_capture(eb, path)
            if calls["target"] == 1:
                target.write_text("theirs", encoding="utf-8")
            return result
        return original_capture(eb, path)

    monkeypatch.setattr(ed, "_capture_disk_freshness", racing_capture)

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target))}") is False

    assert target.read_text(encoding="utf-8") == "theirs"
    assert ed.cur().buf.path == str(source)
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True
    assert calls["target"] >= 2


def test_revert_reloads_clean_stale_buffer_from_disk(tmp_path) -> None:
    p = tmp_path / "revert-clean.txt"
    p.write_text("one\n", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set diskstate.cachems 0") is True
    assert ed.open_file(str(p)) is True
    p.write_bytes(b"two\r\n")

    assert ed.status_model()["disk_state"] == "changed"
    assert ed.exec_command_line("revert") is True

    assert ed.cur().buf.get_text() == "two\n"
    assert ed.cur().buf.dirty is False
    assert ed.cur().local_options["fileformat"] == "dos"
    assert ed.status_model()["disk_state"] == "fresh"
    assert ed.messages[-1].startswith("reverted: ")


def test_revert_refuses_dirty_buffer_and_revert_bang_is_undoable(tmp_path) -> None:
    p = tmp_path / "revert-dirty.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("revert") is False
    assert ed.cur().buf.get_text() == "ours"
    assert "use revert!" in ed.messages[-1]

    assert ed.exec_command_line("revert!") is True
    assert ed.cur().buf.get_text() == "theirs"
    assert ed.cur().buf.dirty is False
    assert "discarded local edits" in ed.messages[-1]

    assert ed.exec_command_line("undo") is True
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True


def test_diff_reports_disk_vs_buffer_changes_without_mutation(tmp_path) -> None:
    p = tmp_path / "diff-stale.txt"
    p.write_text("one\ntwo\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("one\nours\n")
    ed.cur().buf.dirty = True
    p.write_text("one\ntheirs\n", encoding="utf-8")

    assert ed.exec_command_line("diff") is True

    assert ed.cur().buf.get_text() == "one\nours\n"
    assert ed.cur().buf.dirty is True
    assert ed.messages[-7].startswith("diff: ")
    joined = "\n".join(ed.messages[-6:])
    assert "--- disk:" in joined
    assert "+++ buffer:" in joined
    assert "-theirs" in joined
    assert "+ours" in joined


def test_diff_reports_no_differences_for_fresh_buffer(tmp_path) -> None:
    p = tmp_path / "diff-clean.txt"
    p.write_text("same\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(p)) is True

    assert ed.exec_command_line("diff") is True
    assert ed.messages[-1] == "diff: no differences"


def test_file_state_signature_missing_sentinel_blocks_create_after_open(tmp_path) -> None:
    from micromax_editor.file_write import MISSING_FILE_SIGNATURE

    p = tmp_path / "sentinel-created-after-open.txt"
    ed = Editor()
    assert ed.exec_command_line("set diskstate.cachems 0") is True
    assert ed.open_file(str(p)) is True
    assert ed.cur().disk_signature == MISSING_FILE_SIGNATURE

    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True
    p.write_text("theirs", encoding="utf-8")

    assert ed.exec_command_line("save") is False
    assert p.read_text(encoding="utf-8") == "theirs"
    assert ed.status_model()["disk_state"] == "changed"


def _call_structured_hostcall(ed: Editor, name: str, *args: object):
    vm = ed.vm
    for arg in args:
        vm.stack.append(arg)
    vm.stack.append(name)
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    value = vm.stack.pop()
    ok = int(vm.stack.pop())
    return ok, value, err


def test_structured_file_recovery_hostcalls_diff_revert_and_force_save(tmp_path) -> None:
    p = tmp_path / "structured-recovery.txt"
    p.write_text("base\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.open_file(str(p)) is True

    ed.vm.eval('"ed.diff" host.feature?')
    assert int(ed.vm.stack.pop()) == 1
    ed.vm.eval('"ed.revert" host.feature?')
    assert int(ed.vm.stack.pop()) == 1
    ed.vm.eval('"ed.save-info" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ed.cur().buf.set_text("ours\n")
    ed.cur().buf.dirty = True
    p.write_text("theirs\n", encoding="utf-8")

    ok, lines, err = _call_structured_hostcall(ed, "ed.diff", 80)
    assert ok == 1
    assert err == ""
    assert isinstance(lines, list)
    assert "-theirs" in "\n".join(str(x) for x in lines)
    assert "+ours" in "\n".join(str(x) for x in lines)
    assert ed.cur().buf.get_text() == "ours\n"

    ok, info, err = _call_structured_hostcall(ed, "ed.revert", 0)
    assert ok == 0
    assert info == {}
    assert "dirty" in err
    assert ed.cur().buf.get_text() == "ours\n"

    ok, info, err = _call_structured_hostcall(ed, "ed.revert", 1)
    assert ok == 1
    assert err == ""
    assert isinstance(info, dict)
    assert info["forced"] is True
    assert ed.cur().buf.get_text() == "theirs\n"

    ed.cur().buf.set_text("ours-again\n")
    ed.cur().buf.dirty = True
    p.write_text("theirs-again\n", encoding="utf-8")

    ok, info, err = _call_structured_hostcall(ed, "ed.save-info", 0)
    assert ok == 0
    assert info == {}
    assert "file changed on disk" in err
    assert p.read_text(encoding="utf-8") == "theirs-again\n"

    ok, info, err = _call_structured_hostcall(ed, "ed.save-info", 1)
    assert ok == 0
    assert info == {}
    assert "cap.fs-force-save" in err
    assert p.read_text(encoding="utf-8") == "theirs-again\n"

    assert ed.exec_command_line("set cap.fs-force-save true")
    ok, info, err = _call_structured_hostcall(ed, "ed.save-info", 1)
    assert ok == 1
    assert err == ""
    assert isinstance(info, dict)
    assert info["forced"] is True
    assert p.read_text(encoding="utf-8") == "ours-again\n"


def _call_raw_hostcall(ed: Editor, name: str, *args: object):
    vm = ed.vm
    for arg in args:
        vm.stack.append(arg)
    vm.stack.append(name)
    vm.eval("hostcall")
    return vm.stack.pop()


def test_diskstate_command_lists_multi_buffer_disk_conflicts(tmp_path) -> None:
    changed = tmp_path / "changed.txt"
    missing = tmp_path / "missing.txt"
    changed.write_text("base\n", encoding="utf-8")
    missing.write_text("gone\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(changed)) is True
    assert ed.open_file(str(missing)) is True

    changed.write_text("changed externally\n", encoding="utf-8")
    missing.unlink()

    rows = ed.disk_state_rows()
    states = {str(row[0]): str(row[1]) for row in rows}
    assert states[str(changed)] == "changed"
    assert states[str(missing)] == "missing"

    assert ed.exec_command_line("diskstate") is True
    text = "\n".join(ed.messages[-3:])
    assert "diskstate: 2 warning buffers" in text
    assert str(changed) in text and "changed" in text
    assert str(missing) in text and "missing" in text

    assert ed.exec_command_line("diskstate --all") is True
    assert "(all)" in "\n".join(ed.messages[-3:])


def test_disk_rows_hostcall_exposes_multi_buffer_warning_inventory(tmp_path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("base\n", encoding="utf-8")
    second.write_text("base\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True

    first.write_text("changed externally\n", encoding="utf-8")
    second.unlink()

    ed.vm.eval('"ed.disk-rows" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    rows = _call_raw_hostcall(ed, "ed.disk-rows", 0)
    assert isinstance(rows, list)
    by_name = {str(row[0]): row for row in rows}
    assert str(first) in by_name
    assert str(second) in by_name
    assert by_name[str(first)][1] == "changed"
    assert by_name[str(second)][1] == "missing"

    all_rows = _call_raw_hostcall(ed, "ed.disk-rows", 1)
    assert len(all_rows) >= len(rows)

def test_saveas_missing_target_refuses_create_after_final_freshness_check(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    source = tmp_path / "final-link-race-source.txt"
    target = tmp_path / "final-link-race-target.txt"
    source.write_text("source", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(source)) is True
    ed.cur().buf.set_text("ours")
    ed.cur().buf.dirty = True

    original_assert = file_write._assert_file_freshness_at
    raced = {"done": False}

    def create_after_final_check(dir_fd, name, expected, **kwargs):  # type: ignore[no-untyped-def]
        original_assert(dir_fd, name, expected, **kwargs)
        if name == target.name and not raced["done"]:
            raced["done"] = True
            target.write_text("theirs", encoding="utf-8")

    monkeypatch.setattr(file_write, "_assert_file_freshness_at", create_after_final_check)

    assert ed.exec_command_line(f"saveas {shlex.quote(str(target))}") is False

    assert raced["done"] is True
    assert target.read_text(encoding="utf-8") == "theirs"
    assert ed.cur().buf.path == str(source)
    assert ed.cur().buf.get_text() == "ours"
    assert ed.cur().buf.dirty is True
    assert not list(tmp_path.glob(".final-link-race-target.txt.micromax-*.tmp"))
    assert "before save commit" in ed.messages[-1]


def test_file_recovery_read_refuses_symlink_swap_at_final_open(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_access

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "note.txt").write_text("inside", encoding="utf-8")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "note.txt").write_text("outside", encoding="utf-8")
    link = root / "link"
    _symlink_or_skip(link, inside_dir)

    original_open = file_access.os.open
    swapped = {"done": False}

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):  # type: ignore[no-untyped-def]
        text = str(path)
        if dir_fd is None and "link" in text and not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        if dir_fd is None:
            return original_open(path, flags, mode)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(file_access.os, "open", swap_before_open)

    with pytest.raises(FileContainmentError, match="outside containment root"):
        read_file_for_editor(link / "note.txt", encoding="utf-8", containment_root=root)

    assert swapped["done"] is True



def test_direct_file_writer_honors_fsync_when_atomic_disabled(tmp_path, monkeypatch) -> None:
    target = tmp_path / "direct-fsync.txt"
    calls: list[int] = []

    def fake_fsync(fd: int) -> None:
        calls.append(int(fd))

    monkeypatch.setattr("micromax_editor.file_write.os.fsync", fake_fsync)

    result = write_file_bytes(target, b"durable-ish", atomic=False, fsync=True)

    assert target.read_bytes() == b"durable-ish"
    assert result.atomic is False
    assert result.fsync is True
    assert result.file_synced is True
    assert result.directory_synced is True
    assert calls


def test_file_writer_does_not_claim_directory_sync_when_host_lacks_it(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "no-directory-sync.txt"
    monkeypatch.setattr(file_write, "_dir_fd_io_available", lambda: False)
    monkeypatch.delattr(file_write.os, "O_DIRECTORY", raising=False)

    result = file_write.write_file_bytes(target, b"content", atomic=True, fsync=True)

    assert result.file_synced is True
    assert result.directory_synced is False


def test_file_writer_treats_explicit_unsupported_directory_fsync_as_no_witness(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "unsupported-directory-fsync.txt"
    real_fsync = os.fsync
    monkeypatch.setattr(file_write, "_dir_fd_io_available", lambda: False)

    def selective_fsync(fd: int) -> None:
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError(errno.EINVAL, "directory fsync unsupported")
        real_fsync(fd)

    monkeypatch.setattr(file_write.os, "fsync", selective_fsync)

    result = file_write.write_file_bytes(target, b"content", atomic=True, fsync=True)

    assert target.read_bytes() == b"content"
    assert result.file_synced is True
    assert result.directory_synced is False


def test_file_writer_propagates_real_directory_fsync_failure_after_replace(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "directory-fsync-io-error.txt"
    target.write_bytes(b"old")
    real_fsync = os.fsync
    monkeypatch.setattr(file_write, "_dir_fd_io_available", lambda: False)

    def selective_fsync(fd: int) -> None:
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError(errno.EIO, "directory fsync failed")
        real_fsync(fd)

    monkeypatch.setattr(file_write.os, "fsync", selective_fsync)

    with pytest.raises(OSError) as exc_info:
        file_write.write_file_bytes(target, b"new", atomic=True, fsync=True)

    assert exc_info.value.errno == errno.EIO
    # The namespace replacement happened before the failed durability boundary.
    # Reporting failure is essential because rolling back the visible bytes is
    # neither safe nor possible here.
    assert target.read_bytes() == b"new"
    assert list(tmp_path.glob(".*.micromax-*.tmp")) == []


def test_path_fallback_atomic_fault_after_temp_creation_cleans_temp(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "path-fallback-cleanup.txt"
    target.write_bytes(b"old")
    monkeypatch.setattr(file_write, "_dir_fd_io_available", lambda: False)
    sensitive_fds: list[int] = []
    original_open = file_write._open_temp_file

    def recording_open(parent, basename, *, dir_fd=None, create_mode=0o600):  # type: ignore[no-untyped-def]
        fd, temp = original_open(
            parent,
            basename,
            dir_fd=dir_fd,
            create_mode=create_mode,
        )
        if int(create_mode) == 0o600:
            sensitive_fds.append(fd)
        return fd, temp

    monkeypatch.setattr(file_write, "_open_temp_file", recording_open)

    def fault(stage: str) -> None:
        if stage == "document_temp_created":
            raise OSError("fault after document temp creation")

    with pytest.raises(OSError, match="document temp creation"):
        file_write.write_file_bytes(
            target,
            b"new",
            atomic=True,
            fsync=True,
            _fault=fault,
        )

    assert target.read_bytes() == b"old"
    assert list(tmp_path.glob(".*.micromax-*.tmp")) == []
    assert len(sensitive_fds) == 1
    with pytest.raises(OSError) as exc_info:
        os.fstat(sensitive_fds[0])
    assert exc_info.value.errno == errno.EBADF


@pytest.mark.skipif(
    os.name == "nt",
    reason="descriptor-relative atomic cleanup is POSIX-specific",
)
def test_dirfd_atomic_fault_after_temp_creation_closes_descriptor(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    if not file_write._dir_fd_io_available():
        pytest.skip("descriptor-relative writer unavailable on this host")
    target = tmp_path / "dirfd-cleanup.txt"
    target.write_bytes(b"old")
    sensitive_fds: list[int] = []
    original_open = file_write._open_temp_file

    def recording_open(parent, basename, *, dir_fd=None, create_mode=0o600):  # type: ignore[no-untyped-def]
        fd, temp = original_open(
            parent,
            basename,
            dir_fd=dir_fd,
            create_mode=create_mode,
        )
        if int(create_mode) == 0o600:
            sensitive_fds.append(fd)
        return fd, temp

    monkeypatch.setattr(file_write, "_open_temp_file", recording_open)

    def fault(stage: str) -> None:
        if stage == "document_temp_created":
            raise OSError("fault after dirfd temp creation")

    with pytest.raises(OSError, match="dirfd temp creation"):
        file_write.write_file_bytes(
            target,
            b"new",
            atomic=True,
            fsync=True,
            _fault=fault,
        )

    assert target.read_bytes() == b"old"
    assert list(tmp_path.glob(".*.micromax-*.tmp")) == []
    assert len(sensitive_fds) == 1
    with pytest.raises(OSError) as exc_info:
        os.fstat(sensitive_fds[0])
    assert exc_info.value.errno == errno.EBADF


@pytest.mark.skipif(os.name == "nt", reason="POSIX owner-only temp permission contract")
def test_atomic_save_keeps_precommit_document_temp_owner_only(tmp_path) -> None:
    from micromax_editor import file_write

    target = tmp_path / "private-temp.txt"
    target.write_bytes(b"old")
    target.chmod(0o640)
    observed: dict[str, object] = {}

    def fault(stage: str) -> None:
        if stage != "document_temp_synced":
            return
        [temp] = list(tmp_path.glob(".private-temp.txt.micromax-*.tmp"))
        observed["mode"] = stat.S_IMODE(temp.stat().st_mode)
        observed["payload"] = temp.read_bytes()
        raise OSError("inspect synchronized precommit temp")

    with pytest.raises(OSError, match="precommit temp"):
        file_write.write_file_bytes(
            target,
            b"new secret bytes",
            atomic=True,
            fsync=True,
            _fault=fault,
        )

    assert observed == {"mode": 0o600, "payload": b"new secret bytes"}
    assert target.read_bytes() == b"old"
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert list(tmp_path.glob(".private-temp.txt.micromax-*.tmp")) == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX owner-only temp creation contract")
def test_atomic_sensitive_temp_is_created_private_not_narrowed_after_open(
    tmp_path, monkeypatch
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "private-from-birth.txt"
    requested_modes: list[int] = []
    original = file_write._open_temp_file

    def recording_open(parent, basename, *, dir_fd=None, create_mode=0o600):  # type: ignore[no-untyped-def]
        requested_modes.append(int(create_mode))
        return original(
            parent,
            basename,
            dir_fd=dir_fd,
            create_mode=create_mode,
        )

    monkeypatch.setattr(file_write, "_open_temp_file", recording_open)

    file_write.write_file_bytes(target, b"secret", atomic=True, fsync=True)

    # Linux/filesystems with O_TMPFILE use an unnamed 0666 mode probe, so the
    # instrumented named-temp owner sees only the payload inode.  Portable
    # fallback hosts may first create and immediately unlink one empty 0666
    # probe.  In both lanes the only named inode that receives document bytes
    # is requested as owner-only at creation time.
    assert requested_modes in ([0o600], [0o666, 0o600])
    assert requested_modes[-1] == 0o600
    assert target.read_bytes() == b"secret"


@pytest.mark.skipif(os.name == "nt", reason="POSIX umask-derived new-file mode")
def test_atomic_new_file_restores_ordinary_umask_mode_after_private_temp(tmp_path) -> None:
    from micromax_editor import file_write

    reference = tmp_path / "ordinary-create-mode.txt"
    fd = os.open(reference, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    os.close(fd)
    expected_mode = stat.S_IMODE(reference.stat().st_mode)
    reference.unlink()

    target = tmp_path / "atomic-create-mode.txt"
    result = file_write.write_file_bytes(target, b"new", atomic=True, fsync=True)

    assert target.read_bytes() == b"new"
    assert stat.S_IMODE(target.stat().st_mode) == expected_mode
    assert result.file_synced is True
