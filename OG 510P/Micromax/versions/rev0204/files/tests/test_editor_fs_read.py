from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_fs_read(ed: Editor, path: str):
    vm = ed.vm
    vm.stack.append(str(path))
    vm.stack.append("ed.fs-read")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    text = str(vm.stack.pop())
    ok = int(vm.stack.pop())
    return ok, text, err


def test_fs_read_is_capability_gated(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    # Disabled by default.
    vm = ed.vm
    vm.stack.append(str(p))
    vm.stack.append("ed.fs-read")
    with pytest.raises(MicromaxError):
        vm.eval("hostcall")

    # Enable capability via option; should refresh host.feature? advertisement too.
    assert ed.exec_command_line("set cap.fs-read true")
    ed.vm.eval('"ed.fs-read" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ok, text, err = _call_fs_read(ed, str(p))
    assert ok == 1
    assert text == "hello\n"
    assert err == ""


def test_fs_read_reports_missing_and_size_limits(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")

    missing = tmp_path / "missing.txt"
    ok, text, err = _call_fs_read(ed, str(missing))
    assert ok == 0
    assert text == ""
    assert "not a file" in err

    big = tmp_path / "big.txt"
    big.write_bytes(b"x" * (1_000_000 + 10))
    ok, text, err = _call_fs_read(ed, str(big))
    assert ok == 0
    assert text == ""
    assert "too large" in err


def test_fs_read_respects_cap_fs_root_sandbox(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    p = root / "a.txt"
    p.write_text("ok", encoding="utf-8")

    outside = tmp_path / "outside.txt"
    outside.write_text("nope", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    ok, text, err = _call_fs_read(ed, "a.txt")
    assert ok == 1
    assert text == "ok"
    assert err == ""

    ok, text, err = _call_fs_read(ed, str(outside))
    assert ok == 0
    assert text == ""
    assert "cap.fs-root" in err
