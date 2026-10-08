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


def test_fs_read_preflights_vm_tunable_size_before_byte_loader(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_access

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")
    ed.vm.editor_hostcall_fs_read_max_bytes = 5
    # This is a foreground preflight contract, not a process-lifecycle test.
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 0.0

    big = tmp_path / "big.txt"
    big.write_bytes(b"abcdef")

    def forbidden_byte_loader(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("oversized ed.fs-read reached the byte-loading seam")

    monkeypatch.setattr(file_access, "read_file_bytes_contained", forbidden_byte_loader)

    ok, text, err = _call_fs_read(ed, str(big))

    assert ok == 0
    assert text == ""
    assert "too large" in err
    assert "5 bytes" in err


def test_fs_read_rechecks_size_after_preflight_file_growth(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_access

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")
    ed.vm.editor_hostcall_fs_read_max_bytes = 5
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 0.0

    p = tmp_path / "grows.txt"
    p.write_bytes(b"ok")
    original_preflight = file_access.preflight_file_read_size_contained
    grew = {"done": False}

    def grow_after_preflight(*args, **kwargs):  # type: ignore[no-untyped-def]
        result = original_preflight(*args, **kwargs)
        if not grew["done"]:
            grew["done"] = True
            p.write_bytes(b"abcdef")
        return result

    monkeypatch.setattr(file_access, "preflight_file_read_size_contained", grow_after_preflight)

    ok, text, err = _call_fs_read(ed, str(p))

    assert ok == 0
    assert text == ""
    assert p.read_bytes() == b"abcdef"
    assert "too large" in err
    assert "5 bytes" in err


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
    assert link.resolve(strict=True) == outside_dir
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
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 0.0

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
    assert link.resolve(strict=True) == outside_dir
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


def test_fs_read_timeout_preserves_hostcall_tuple(tmp_path, monkeypatch) -> None:
    from micromax_editor import fs_hostcalls as fs_hostcalls_mod
    from micromax_editor.file_access import FilesystemOperationTimeoutError

    p = tmp_path / "slow.txt"
    p.write_text("slow", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 0.05

    def timed_out(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise FilesystemOperationTimeoutError(
            f"filesystem read timed out after 0.05s: {p}"
        )

    # Worker kill/late-cleanup ownership is exercised in test_worker_process;
    # this test owns only the script-visible tuple mapping.
    monkeypatch.setattr(fs_hostcalls_mod, "read_file_bytes_contained_bounded", timed_out)

    ok, text, err = _call_fs_read(ed, str(p))

    assert ok == 0
    assert text == ""
    assert "timed out" in err
    assert str(p) in err

def test_fs_read_large_result_is_drained_before_worker_join(tmp_path, monkeypatch) -> None:
    """A healthy near-limit read must not deadlock behind its result pipe."""

    import multiprocessing

    from micromax_editor import file_access

    payload = "q" * 900_000
    p = tmp_path / "queue-pressure.txt"
    p.write_text(payload, encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")
    ed.vm.editor_hostcall_fs_read_timeout_seconds = 3.0  # type: ignore[attr-defined]

    # Exercise the portable isolated-start path.  The old join-before-receive
    # order timed out even though the file read itself had completed.
    context = multiprocessing.get_context("spawn")
    monkeypatch.setattr(file_access, "_fs_worker_context", lambda: context)

    ok, text, err = _call_fs_read(ed, str(p))

    assert ok == 1
    assert err == ""
    assert text == payload

