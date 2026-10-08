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


def test_fs_read_rechecks_cap_root_after_late_symlink_parent_swap(tmp_path, monkeypatch) -> None:
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
    assert ed.exec_command_line("set cap.fs-read true")
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

    ok, text, err = _call_fs_read(ed, "link/secret.txt")

    assert ok == 0
    assert text == ""
    assert swapped["done"] is True
    assert "outside containment root" in err
    assert "outside" not in text


def test_fs_read_refuses_symlink_swap_at_final_open(tmp_path, monkeypatch) -> None:
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
    assert ed.exec_command_line("set cap.fs-read true")
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

    ok, text, err = _call_fs_read(ed, "link/secret.txt")

    assert ok == 0
    assert text == ""
    assert swapped["done"] is True
    assert "outside containment root" in err


def test_fs_read_cap_root_uses_descriptor_backend_not_path_read_text(tmp_path, monkeypatch) -> None:
    from pathlib import Path

    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("descriptor", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    def forbidden_read_text(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError(f"ambient Path.read_text used for {self}")

    monkeypatch.setattr(Path, "read_text", forbidden_read_text)

    ok, text, err = _call_fs_read(ed, "a.txt")

    assert ok == 1
    assert text == "descriptor"
    assert err == ""
