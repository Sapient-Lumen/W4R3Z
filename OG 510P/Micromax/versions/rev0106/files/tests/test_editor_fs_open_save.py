from __future__ import annotations

from pathlib import Path

import pytest

from micromax import MicromaxError
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
