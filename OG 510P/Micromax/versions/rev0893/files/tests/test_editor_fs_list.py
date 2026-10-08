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


def test_fs_list_rechecks_cap_root_after_late_symlink_parent_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import fs_hostcalls as fs_hostcalls_mod

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "inside.txt").write_text("inside", encoding="utf-8")
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
    assert ed.exec_command_line("set cap.fs-list true")
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

    ok, rows, err = _call_fs_list(ed, "link")

    assert ok == 0
    assert rows == []
    assert swapped["done"] is True
    assert "outside containment root" in err


def test_fs_list_does_not_follow_child_symlink_for_kind(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret", encoding="utf-8")
    link = root / "outside-link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    ok, rows, err = _call_fs_list(ed, ".")

    assert ok == 1
    assert err == ""
    row = next(r for r in rows if str(r[0]).startswith("outside-link"))
    assert row[0] == "outside-link"
    assert row[1] == "other"
    assert str(row[2]).endswith("outside-link")


def test_fs_list_refuses_symlink_swap_at_final_open(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_access

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "inside.txt").write_text("inside", encoding="utf-8")
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
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    original_open = file_access.os.open
    swapped = {"done": False}

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):  # type: ignore[no-untyped-def]
        if dir_fd is None and str(path).endswith("link") and not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        if dir_fd is None:
            return original_open(path, flags, mode)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(file_access.os, "open", swap_before_open)

    ok, rows, err = _call_fs_list(ed, "link")

    assert ok == 0
    assert rows == []
    assert swapped["done"] is True
    assert "outside containment root" in err


def test_fs_list_cap_root_uses_descriptor_backend_not_path_iterdir(tmp_path, monkeypatch) -> None:
    from pathlib import Path

    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("a", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    def forbidden_iterdir(self):  # type: ignore[no-untyped-def]
        raise AssertionError(f"ambient Path.iterdir used for {self}")

    monkeypatch.setattr(Path, "iterdir", forbidden_iterdir)

    ok, rows, err = _call_fs_list(ed, ".")

    assert ok == 1
    assert err == ""
    assert any(str(row[0]) == "a.txt" for row in rows)
