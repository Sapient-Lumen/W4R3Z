from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from micromax_editor.recovery_journal import (
    RecoveryJournal,
    RecoveryResidueKind,
    RecoveryStatus,
)
from micromax_editor.save_residue import TempOwnerState

CRASH_EXIT = 86
OLD_BYTES = b"old payload\n"
NEW_BYTES = b"new payload\n"
CHILD = Path(__file__).with_name("save_crash_child.py")


def _crash_at(tmp_path: Path, stage: str, *, mode: str = "atomic") -> Path:
    target = tmp_path / "document.txt"
    target.write_bytes(OLD_BYTES)
    target.chmod(0o640)
    env = dict(os.environ)
    src = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    completed = subprocess.run(
        [sys.executable, str(CHILD), str(tmp_path), stage, mode],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == CRASH_EXIT, (
        stage,
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )
    assert (tmp_path / "crash-stage.txt").read_text(encoding="utf-8") == stage
    return target


@pytest.mark.skipif(
    os.name == "nt" or not hasattr(os, "O_DIRECTORY"),
    reason="declared Linux/POSIX local-filesystem process-crash matrix",
)
@pytest.mark.parametrize(
    ("stage", "target_bytes", "status"),
    [
        ("checkpoint_temp_synced", OLD_BYTES, None),
        ("after_checkpoint_replace", OLD_BYTES, RecoveryStatus.RECOVERABLE),
        (
            "after_checkpoint_directory_sync",
            OLD_BYTES,
            RecoveryStatus.RECOVERABLE,
        ),
        ("document_temp_synced", OLD_BYTES, RecoveryStatus.RECOVERABLE),
        ("after_document_replace", NEW_BYTES, RecoveryStatus.ALREADY_PERSISTED),
        (
            "after_document_mode_restore",
            NEW_BYTES,
            RecoveryStatus.ALREADY_PERSISTED,
        ),
        (
            "after_document_metadata_sync",
            NEW_BYTES,
            RecoveryStatus.ALREADY_PERSISTED,
        ),
        (
            "after_document_directory_sync",
            NEW_BYTES,
            RecoveryStatus.ALREADY_PERSISTED,
        ),
        ("before_dismiss", NEW_BYTES, RecoveryStatus.ALREADY_PERSISTED),
        ("after_dismiss_unlink", NEW_BYTES, None),
        ("after_dismiss", NEW_BYTES, None),
    ],
)
def test_atomic_save_survives_real_process_death_at_transaction_stages(
    tmp_path: Path,
    stage: str,
    target_bytes: bytes,
    status: RecoveryStatus | None,
) -> None:
    target = _crash_at(tmp_path, stage)

    assert target.read_bytes() == target_bytes
    expected_mode = 0o600 if stage == "after_document_replace" else 0o640
    assert (target.stat().st_mode & 0o7777) == expected_mode

    document_temps = list(tmp_path.glob(".document.txt.micromax-*.tmp"))
    recovery_temps = list((tmp_path / "recovery").glob("*.tmp"))
    if stage == "document_temp_synced":
        assert len(document_temps) == 1
        assert document_temps[0].read_bytes() == NEW_BYTES
        assert (document_temps[0].stat().st_mode & 0o7777) == 0o600
    else:
        assert document_temps == []
    if stage == "checkpoint_temp_synced":
        assert len(recovery_temps) == 1
        assert (recovery_temps[0].stat().st_mode & 0o7777) == 0o600
    else:
        assert recovery_temps == []

    restarted = RecoveryJournal(tmp_path / "recovery")
    residue_scan = restarted.scan_residue()
    if stage in {"checkpoint_temp_synced", "document_temp_synced"}:
        assert len(residue_scan.residues) == 1
        residue = residue_scan.residues[0]
        assert residue.kind is (
            RecoveryResidueKind.CHECKPOINT_TEMP
            if stage == "checkpoint_temp_synced"
            else RecoveryResidueKind.DOCUMENT_TEMP
        )
        assert residue.owner_state is TempOwnerState.STALE
        assert residue.cleanup_eligible is True
        assert restarted.cleanup_residue(residue).removed is True
        assert not residue.path.exists()
    else:
        assert residue_scan.residues == ()
    candidates = restarted.discover()
    if status is None:
        assert candidates == []
        return
    assert len(candidates) == 1
    assert candidates[0].status is status
    if status is RecoveryStatus.ALREADY_PERSISTED:
        assert candidates[0].intended_mode == 0o640
        assert candidates[0].current_mode == expected_mode
        assert candidates[0].mode_repair_available is True
        assert candidates[0].mode_repair_required is (
            stage == "after_document_replace"
        )
    assert restarted.load(candidates[0].entry_id).payload == NEW_BYTES


@pytest.mark.skipif(
    os.name == "nt" or not hasattr(os, "O_DIRECTORY"),
    reason="declared Linux/POSIX local-filesystem process-crash matrix",
)
@pytest.mark.parametrize(
    ("stage", "changed"),
    [
        ("after_document_replace", True),
        ("after_document_mode_restore", False),
    ],
)
def test_restart_finishes_private_mode_or_pending_metadata_sync(
    tmp_path: Path,
    stage: str,
    changed: bool,
) -> None:
    target = _crash_at(tmp_path, stage)
    restarted = RecoveryJournal(tmp_path / "recovery")
    [candidate] = restarted.discover()

    outcome = restarted.repair_mode(candidate.entry_id)

    assert outcome.changed is changed
    assert outcome.file_synced is True
    assert isinstance(outcome.directory_synced, bool)
    assert outcome.recovery_retired is True
    assert target.read_bytes() == NEW_BYTES
    assert (target.stat().st_mode & 0o7777) == 0o640
    assert restarted.discover() == []


@pytest.mark.skipif(
    os.name == "nt" or not hasattr(os, "O_DIRECTORY"),
    reason="declared Linux/POSIX local-filesystem process-crash matrix",
)
def test_direct_save_process_death_after_truncate_preserves_recovery_but_not_target(
    tmp_path: Path,
) -> None:
    target = _crash_at(tmp_path, "after_document_truncate", mode="direct")

    assert target.read_bytes() == b""
    restarted = RecoveryJournal(tmp_path / "recovery")
    [candidate] = restarted.discover()
    assert candidate.status is RecoveryStatus.TARGET_CHANGED
    assert restarted.load(candidate.entry_id).payload == NEW_BYTES


@pytest.mark.skipif(
    os.name == "nt" or not hasattr(os, "O_DIRECTORY"),
    reason="declared Linux/POSIX local-filesystem process-crash matrix",
)
def test_direct_save_process_death_after_file_sync_is_classified_as_persisted(
    tmp_path: Path,
) -> None:
    target = _crash_at(tmp_path, "after_document_file_sync", mode="direct")

    assert target.read_bytes() == NEW_BYTES
    restarted = RecoveryJournal(tmp_path / "recovery")
    [candidate] = restarted.discover()
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED
