from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_fs_list(ed: Editor, path: str):
    vm = ed.vm
    vm.stack.append(str(path))
    vm.stack.append("ed.fs-list")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    rows = vm.stack.pop()
    ok = int(vm.stack.pop())
    return ok, rows, err


def test_fs_list_is_capability_gated(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("hello\n", encoding="utf-8")
    (tmp_path / "d").mkdir()

    ed = Editor()
    install_editor_hostcalls(ed)

    # Disabled by default.
    vm = ed.vm
    vm.stack.append(str(tmp_path))
    vm.stack.append("ed.fs-list")
    with pytest.raises(MicromaxError):
        vm.eval("hostcall")

    # Enable capability via option; should refresh host.feature? advertisement too.
    assert ed.exec_command_line("set cap.fs-list true")
    ed.vm.eval('"ed.fs-list" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ok, rows, err = _call_fs_list(ed, str(tmp_path))
    assert ok == 1
    assert err == ""
    assert isinstance(rows, list)

    # Rows are: [name kind path]
    names = {str(r[0]) for r in rows}
    assert "a.txt" in names
    assert "d/" in names


def test_fs_list_reports_missing_and_limits(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    missing = tmp_path / "missing"
    ok, rows, err = _call_fs_list(ed, str(missing))
    assert ok == 0
    assert rows == []
    assert "not a directory" in err

    # Best-effort limit: ensure it doesn't explode on large dirs.
    big = tmp_path / "big"
    big.mkdir()
    for i in range(700):
        (big / f"f{i}.txt").write_text("x", encoding="utf-8")

    ok, rows, err = _call_fs_list(ed, str(big))
    assert ok == 1
    assert err == ""
    assert len(rows) <= 500


def test_fs_list_respects_cap_fs_root_sandbox(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "d").mkdir()
    (root / "d" / "a.txt").write_text("x", encoding="utf-8")

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("nope", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    # Relative paths resolve under cap.fs-root.
    ok, rows, err = _call_fs_list(ed, "d")
    assert ok == 1
    assert err == ""
    names = {str(r[0]) for r in rows}
    assert "a.txt" in names

    # Absolute targets outside the sandbox are denied.
    ok, rows, err = _call_fs_list(ed, str(outside))
    assert ok == 0
    assert rows == []
    assert "cap.fs-root" in err
