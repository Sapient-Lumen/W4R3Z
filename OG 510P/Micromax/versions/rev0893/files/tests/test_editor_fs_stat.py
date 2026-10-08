from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_fs_stat(ed: Editor, path: str):
    vm = ed.vm
    vm.stack.append(str(path))
    vm.stack.append("ed.fs-stat")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    info = vm.stack.pop()
    ok = int(vm.stack.pop())
    return ok, info, err


def test_fs_stat_is_capability_gated(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    # Disabled by default.
    vm = ed.vm
    vm.stack.append(str(p))
    vm.stack.append("ed.fs-stat")
    with pytest.raises(MicromaxError):
        vm.eval("hostcall")

    # Enable capability via option; should refresh host.feature? advertisement too.
    assert ed.exec_command_line("set cap.fs-stat true")
    ed.vm.eval('"ed.fs-stat" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    ok, info, err = _call_fs_stat(ed, str(p))
    assert ok == 1
    assert err == ""
    assert isinstance(info, dict)
    assert int(info.get("exists", 0)) == 1
    assert str(info.get("kind")) == "file"
    assert int(info.get("size", 0)) > 0


def test_fs_stat_reports_missing(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")

    missing = tmp_path / "missing"
    ok, info, err = _call_fs_stat(ed, str(missing))
    assert ok == 0
    assert isinstance(info, dict)
    assert int(info.get("exists", 0)) == 0
    assert "not found" in err


def test_fs_stat_respects_cap_fs_root_sandbox(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    p = root / "a.txt"
    p.write_text("hi", encoding="utf-8")

    outside = tmp_path / "outside.txt"
    outside.write_text("nope", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    ok, info, err = _call_fs_stat(ed, "a.txt")
    assert ok == 1
    assert err == ""
    assert int(info.get("exists", 0)) == 1

    ok, info, err = _call_fs_stat(ed, str(outside))
    assert ok == 0
    assert isinstance(info, dict)
    assert int(info.get("exists", 0)) == 0
    assert "cap.fs-root" in err


def test_fs_stat_rechecks_cap_root_after_late_symlink_parent_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import fs_hostcalls as fs_hostcalls_mod

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "secret.txt").write_text("inside", encoding="utf-8")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.txt").write_text("outside", encoding="utf-8")
    link = root / "link"
    try:
        link.symlink_to(inside_dir, target_is_directory=True)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    original = fs_hostcalls_mod.checked_operation_path
    swapped = {"done": False}

    def swap_after_preflight(ed_arg, raw_path):  # type: ignore[no-untyped-def]
        path = original(ed_arg, raw_path)
        if not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        return path

    monkeypatch.setattr(fs_hostcalls_mod, "checked_operation_path", swap_after_preflight)

    ok, info, err = _call_fs_stat(ed, "link/secret.txt")

    assert ok == 0
    assert isinstance(info, dict)
    assert swapped["done"] is True
    assert "outside containment root" in err


def test_fs_stat_refuses_symlink_swap_at_final_open(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_access

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "secret.txt").write_text("inside", encoding="utf-8")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.txt").write_text("outside", encoding="utf-8")
    link = root / "link"
    try:
        link.symlink_to(inside_dir, target_is_directory=True)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    original_open = file_access.os.open
    swapped = {"done": False}

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):  # type: ignore[no-untyped-def]
        if dir_fd is None and "link" in str(path) and not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        if dir_fd is None:
            return original_open(path, flags, mode)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(file_access.os, "open", swap_before_open)

    ok, info, err = _call_fs_stat(ed, "link/secret.txt")

    assert ok == 0
    assert isinstance(info, dict)
    assert swapped["done"] is True
    assert "outside containment root" in err
