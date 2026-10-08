from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from micromax_editor import file_write
from micromax_editor.file_write import (
    FileFreshnessConflict,
    FileWritePlanTimeoutError,
    plan_atomic_write,
    plan_atomic_write_bounded,
    write_file_bytes,
)

pytestmark = pytest.mark.skipif(
    os.name == "nt",
    reason="the pinned parent/mode transaction is a POSIX descriptor contract",
)


def _private_temps(parent: Path) -> list[Path]:
    return list(parent.glob(".*.micromax-v*-*.tmp"))


def test_atomic_write_plan_pins_existing_mode_and_writer_reports_it(
    tmp_path: Path,
) -> None:
    target = tmp_path / "planned.txt"
    target.write_bytes(b"old")
    target.chmod(0o640)

    plan = plan_atomic_write(target, preserve_mode=True)
    result = write_file_bytes(
        target,
        b"new",
        write_plan=plan,
        temp_lease_id="1" * 32,
        fsync=True,
    )

    parent_st = tmp_path.stat()
    assert plan.write_path == str(target)
    assert plan.preserved_existing_mode is True
    assert plan.final_mode == 0o640
    assert (plan.parent_dev, plan.parent_ino) == (
        int(parent_st.st_dev),
        int(parent_st.st_ino),
    )
    assert result.final_mode == 0o640
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert target.read_bytes() == b"new"
    assert _private_temps(tmp_path) == []


def test_atomic_write_plan_refuses_replaced_parent_before_temp_creation(
    tmp_path: Path,
) -> None:
    parent = tmp_path / "documents"
    parent.mkdir()
    target = parent / "note.txt"
    target.write_bytes(b"original authority")
    target.chmod(0o640)
    plan = plan_atomic_write(target, preserve_mode=True)

    original_parent = tmp_path / "documents-original"
    parent.rename(original_parent)
    parent.mkdir()
    replacement = parent / target.name
    replacement.write_bytes(b"replacement authority")
    replacement.chmod(0o644)

    with pytest.raises(FileFreshnessConflict, match="parent authority changed"):
        write_file_bytes(
            target,
            b"must not commit",
            write_plan=plan,
            temp_lease_id="2" * 32,
            fsync=True,
        )

    assert (original_parent / target.name).read_bytes() == b"original authority"
    assert replacement.read_bytes() == b"replacement authority"
    assert _private_temps(original_parent) == []
    assert _private_temps(parent) == []


def test_atomic_write_plan_refuses_retargeted_nominal_symlink(tmp_path: Path) -> None:
    if not hasattr(os, "symlink"):
        pytest.skip("symbolic links unavailable")
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    link = tmp_path / "note.txt"
    try:
        link.symlink_to(first.name)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symbolic links unavailable: {exc}")

    plan = plan_atomic_write(link, preserve_mode=True)
    link.unlink()
    link.symlink_to(second.name)

    with pytest.raises(FileFreshnessConflict, match="target authority changed"):
        write_file_bytes(
            link,
            b"must not commit",
            write_plan=plan,
            temp_lease_id="3" * 32,
            fsync=True,
        )

    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"
    assert link.is_symlink()
    assert _private_temps(tmp_path) == []


def test_atomic_write_plan_refuses_permission_policy_drift(tmp_path: Path) -> None:
    target = tmp_path / "policy.txt"
    target.write_bytes(b"old")
    plan = plan_atomic_write(target, preserve_mode=True)

    with pytest.raises(FileFreshnessConflict, match="permission policy changed"):
        write_file_bytes(
            target,
            b"must not commit",
            preserve_mode=False,
            write_plan=plan,
            temp_lease_id="4" * 32,
        )

    assert target.read_bytes() == b"old"
    assert _private_temps(tmp_path) == []


def test_mode_probe_is_unlinked_before_its_mode_is_inspected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "new.txt"
    real_fstat = file_write.os.fstat
    observed = {"regular_probe": False}
    monkeypatch.setattr(
        file_write,
        "_open_unnamed_mode_probe",
        lambda _parent, *, dir_fd=None: None,
    )

    def fail_when_probe_is_inspected(fd: int):  # type: ignore[no-untyped-def]
        st = real_fstat(fd)
        if stat.S_ISREG(st.st_mode):
            observed["regular_probe"] = True
            assert _private_temps(tmp_path) == []
            raise RuntimeError("stop after anonymous probe inspection")
        return st

    monkeypatch.setattr(file_write.os, "fstat", fail_when_probe_is_inspected)

    with pytest.raises(RuntimeError, match="anonymous probe inspection"):
        plan_atomic_write(target, preserve_mode=True)

    assert observed["regular_probe"] is True
    assert not target.exists()
    assert _private_temps(tmp_path) == []


def test_mode_probe_prefers_an_unnamed_inode_without_opening_a_named_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closed: list[int] = []
    monkeypatch.setattr(
        file_write,
        "_open_unnamed_mode_probe",
        lambda _parent, *, dir_fd=None: 91,
    )
    monkeypatch.setattr(
        file_write.os,
        "fstat",
        lambda fd: SimpleNamespace(st_mode=stat.S_IFREG | 0o642)
        if fd == 91
        else (_ for _ in ()).throw(AssertionError(f"unexpected fd {fd}")),
    )
    monkeypatch.setattr(file_write, "_close_fd", closed.append)

    def named_probe_must_not_open(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("named probe opened despite unnamed support")

    monkeypatch.setattr(file_write, "_open_temp_file", named_probe_must_not_open)

    assert file_write._probe_default_create_mode(tmp_path, "note.txt") == 0o642
    assert closed == [91]


@pytest.mark.skipif(
    os.name == "nt" or not hasattr(os, "O_TMPFILE"),
    reason="O_TMPFILE capability classification is Linux-specific",
)
def test_unnamed_mode_probe_falls_back_only_for_capability_absence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unsupported(*_args: object, **_kwargs: object) -> int:
        raise OSError(errno.EOPNOTSUPP, "unsupported")

    monkeypatch.setattr(file_write.os, "open", unsupported)
    assert file_write._open_unnamed_mode_probe(tmp_path) is None

    def denied(*_args: object, **_kwargs: object) -> int:
        raise PermissionError(errno.EACCES, "denied")

    monkeypatch.setattr(file_write.os, "open", denied)
    with pytest.raises(PermissionError):
        file_write._open_unnamed_mode_probe(tmp_path)



def test_atomic_write_plan_timeout_wires_exact_probe_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "plan-timeout.txt"
    target.write_bytes(b"old")
    cleanup_calls: list[tuple[str, int | None, str | None]] = []

    def fake_create(*_args: object, **kwargs: object) -> tuple[object, object]:
        assert kwargs.get("target") is file_write._plan_atomic_write_worker
        return object(), object()

    def fake_cleanup(
        path: str | Path,
        worker_pid: int | None,
        *,
        lease_id: str | None,
        containment_root: str | Path | None,
    ) -> None:
        assert containment_root is None
        cleanup_calls.append((str(path), worker_pid, lease_id))

    def fake_collect(_proc: object, _channel: object, **kwargs: object) -> object:
        cleanup = kwargs.get("abnormal_cleanup")
        assert callable(cleanup)
        cleanup(5150)
        timeout_error = kwargs.get("timeout_error")
        assert callable(timeout_error)
        raise timeout_error()

    monkeypatch.setattr(file_write, "create_one_shot_worker", fake_create)
    monkeypatch.setattr(file_write, "_cleanup_atomic_write_temps_bounded", fake_cleanup)
    monkeypatch.setattr(file_write, "_collect_write_worker_result", fake_collect)

    with pytest.raises(FileWritePlanTimeoutError, match="planning timed out"):
        plan_atomic_write_bounded(
            target,
            temp_lease_id="a" * 32,
            timeout_seconds=0.05,
        )

    assert target.read_bytes() == b"old"
    assert cleanup_calls == [(str(target), 5150, "a" * 32)]
    assert _private_temps(tmp_path) == []

