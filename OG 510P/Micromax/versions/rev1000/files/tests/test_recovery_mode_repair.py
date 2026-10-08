from __future__ import annotations

import os
from pathlib import Path

import pytest

import micromax_editor.recovery_journal as recovery_module
from micromax_editor.recovery_journal import (
    MODE_REPAIR_CONTRACT_V1,
    PRIVATE_ATOMIC_COMMIT_MODE,
    RecoveryConflictError,
    RecoveryError,
    RecoveryJournal,
    RecoveryStatus,
)


def stat_mode(path: Path) -> int:
    return int(path.stat().st_mode & 0o7777)


pytestmark = pytest.mark.skipif(
    os.name != "posix" or not hasattr(os, "fchmod"),
    reason="permission repair is a POSIX fd-bound contract",
)


def _private_commit(
    journal: RecoveryJournal,
    target: Path,
    *,
    commit: bytes = b"committed bytes",
    intended_mode: int = 0o640,
) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"base")
    target.chmod(intended_mode)
    parent_st = target.parent.stat()
    entry_id = journal.checkpoint(
        target,
        b"exact editor text",
        buffer_id="mode-repair",
        commit_content=commit,
        metadata={
            "mode_repair_contract": MODE_REPAIR_CONTRACT_V1,
            "private_commit_mode": format(PRIVATE_ATOMIC_COMMIT_MODE, "04o"),
            "intended_mode": format(intended_mode, "04o"),
            "target_parent_dev": str(int(parent_st.st_dev)),
            "target_parent_ino": str(int(parent_st.st_ino)),
        },
    )
    target.write_bytes(commit)
    target.chmod(PRIVATE_ATOMIC_COMMIT_MODE)
    return entry_id


def test_mode_repair_is_resumable_after_death_between_chmod_and_fsync(
    tmp_path: Path,
) -> None:
    target = tmp_path / "resume.txt"

    def fault(stage: str) -> None:
        if stage == "after_mode_repair_chmod":
            raise OSError("simulated death after chmod")

    journal = RecoveryJournal(tmp_path / "recovery", fault=fault)
    entry_id = _private_commit(journal, target)

    with pytest.raises(OSError, match="after chmod"):
        journal.repair_mode(entry_id)

    assert target.read_bytes() == b"committed bytes"
    assert (target.stat().st_mode & 0o7777) == 0o640
    assert journal._entry_path(entry_id).exists()

    restarted = RecoveryJournal(journal.root)
    candidate = restarted.inspect(entry_id)
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED
    assert candidate.mode_repair_available is True
    assert candidate.mode_repair_required is False

    outcome = restarted.repair_mode(entry_id)
    assert outcome.changed is False
    assert outcome.file_synced is True
    assert outcome.recovery_retired is True
    assert restarted.discover() == []


def test_private_intended_mode_still_requires_commit_sync_before_retire(
    tmp_path: Path,
) -> None:
    target = tmp_path / "private.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = _private_commit(journal, target, intended_mode=0o600)

    candidate = journal.inspect(entry_id)
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED
    assert candidate.current_mode == 0o600
    assert candidate.intended_mode == 0o600
    assert candidate.mode_repair_available is True
    assert candidate.mode_repair_required is False
    assert candidate.mode_repair_conflict is False

    outcome = journal.repair_mode(entry_id)

    assert outcome.changed is False
    assert outcome.file_synced is True
    assert outcome.directory_synced is True
    assert outcome.recovery_retired is True
    assert not journal._entry_path(entry_id).exists()


def test_commit_checkpoint_checks_private_intended_mode_too(tmp_path: Path) -> None:
    target = tmp_path / "wrong-private-mode.txt"
    target.write_bytes(b"base")
    target.chmod(0o600)
    journal = RecoveryJournal(tmp_path / "recovery")
    parent_st = target.parent.stat()
    entry_id = journal.checkpoint(
        target,
        b"exact editor text",
        buffer_id="private-mode-commit",
        commit_content=b"committed bytes",
        metadata={
            "mode_repair_contract": MODE_REPAIR_CONTRACT_V1,
            "private_commit_mode": "0600",
            "intended_mode": "0600",
            "target_parent_dev": str(int(parent_st.st_dev)),
            "target_parent_ino": str(int(parent_st.st_ino)),
        },
    )

    def wrong_mode_writer(path: Path, payload: bytes) -> None:
        path.write_bytes(payload)
        path.chmod(0o644)

    with pytest.raises(RecoveryError, match="permission transaction"):
        journal.commit_checkpoint(entry_id, b"committed bytes", wrong_mode_writer)

    assert target.read_bytes() == b"committed bytes"
    assert (target.stat().st_mode & 0o7777) == 0o644
    assert journal._entry_path(entry_id).exists()
    candidate = journal.inspect(entry_id)
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED
    assert candidate.mode_repair_available is False
    assert candidate.mode_repair_conflict is True


def test_mode_repair_retains_witness_when_directory_sync_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "unsynced-directory.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = _private_commit(journal, target, intended_mode=0o640)
    monkeypatch.setattr(recovery_module, "_fsync_dir_fd", lambda _fd: False)

    with pytest.raises(RecoveryError, match="directory sync is unavailable"):
        journal.repair_mode(entry_id)

    # The inode transition is idempotently complete, but the recovery witness
    # stays until a later run can positively synchronize the namespace.
    assert (target.stat().st_mode & 0o7777) == 0o640
    assert journal._entry_path(entry_id).exists()
    candidate = journal.inspect(entry_id)
    assert candidate.mode_repair_available is True
    assert candidate.mode_repair_required is False


def test_mode_repair_refuses_content_or_mode_outside_transaction(
    tmp_path: Path,
) -> None:
    content_target = tmp_path / "content.txt"
    content_journal = RecoveryJournal(tmp_path / "content-recovery")
    content_id = _private_commit(content_journal, content_target)
    content_target.write_bytes(b"external replacement")
    content_target.chmod(0o600)

    with pytest.raises(RecoveryConflictError, match="bytes no longer match"):
        content_journal.repair_mode(content_id)
    assert (content_target.stat().st_mode & 0o7777) == 0o600
    assert content_journal._entry_path(content_id).exists()

    mode_target = tmp_path / "mode.txt"
    mode_journal = RecoveryJournal(tmp_path / "mode-recovery")
    mode_id = _private_commit(mode_journal, mode_target)
    mode_target.chmod(0o666)

    candidate = mode_journal.inspect(mode_id)
    assert candidate.mode_repair_conflict is True
    with pytest.raises(RecoveryConflictError, match="mode changed outside"):
        mode_journal.repair_mode(mode_id)
    assert (mode_target.stat().st_mode & 0o7777) == 0o666
    assert mode_journal._entry_path(mode_id).exists()


def test_mode_repair_revalidates_mode_immediately_before_fchmod(
    tmp_path: Path,
) -> None:
    target = tmp_path / "concurrent-mode.txt"

    def fault(stage: str) -> None:
        if stage == "before_mode_repair":
            target.chmod(0o666)

    journal = RecoveryJournal(tmp_path / "recovery", fault=fault)
    entry_id = _private_commit(journal, target, intended_mode=0o640)

    with pytest.raises(RecoveryConflictError, match="mode changed during"):
        journal.repair_mode(entry_id)

    assert (target.stat().st_mode & 0o7777) == 0o666
    assert journal._entry_path(entry_id).exists()


def test_mode_repair_refuses_hardlink_created_at_prechmod_boundary(
    tmp_path: Path,
) -> None:
    target = tmp_path / "hardlink-race.txt"
    alias = tmp_path / "hardlink-race-alias.txt"

    def fault(stage: str) -> None:
        if stage == "before_mode_repair":
            os.link(target, alias)

    journal = RecoveryJournal(tmp_path / "recovery", fault=fault)
    entry_id = _private_commit(journal, target, intended_mode=0o640)

    with pytest.raises(RecoveryConflictError, match="authority changed"):
        journal.repair_mode(entry_id)

    assert stat_mode(target) == 0o600
    assert stat_mode(alias) == 0o600
    assert journal._entry_path(entry_id).exists()


def test_mode_repair_refuses_hardlinked_or_symlinked_authority(
    tmp_path: Path,
) -> None:
    hard_target = tmp_path / "hard.txt"
    hard_journal = RecoveryJournal(tmp_path / "hard-recovery")
    hard_id = _private_commit(hard_journal, hard_target)
    alias = tmp_path / "hard-alias.txt"
    os.link(hard_target, alias)

    with pytest.raises(RecoveryConflictError, match="multiple hard links"):
        hard_journal.repair_mode(hard_id)
    assert hard_journal._entry_path(hard_id).exists()

    if not hasattr(os, "symlink"):
        return
    link_target = tmp_path / "link.txt"
    link_journal = RecoveryJournal(tmp_path / "link-recovery")
    link_id = _private_commit(link_journal, link_target)
    other = tmp_path / "other.txt"
    other.write_bytes(b"committed bytes")
    other.chmod(0o600)
    link_target.unlink()
    try:
        link_target.symlink_to(other)
    except (OSError, NotImplementedError):
        return

    with pytest.raises(RecoveryConflictError, match="symbolic link"):
        link_journal.repair_mode(link_id)
    assert (other.stat().st_mode & 0o7777) == 0o600
    assert link_journal._entry_path(link_id).exists()


def test_mode_repair_refuses_replaced_parent_directory_authority(
    tmp_path: Path,
) -> None:
    parent = tmp_path / "documents"
    target = parent / "note.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = _private_commit(journal, target)

    original_parent = tmp_path / "documents-original"
    parent.rename(original_parent)
    parent.mkdir()
    replacement = parent / target.name
    replacement.write_bytes(b"committed bytes")
    replacement.chmod(0o600)

    candidate = journal.inspect(entry_id)
    assert candidate.status is RecoveryStatus.TARGET_CHANGED
    assert "parent authority changed" in str(candidate.error)
    with pytest.raises(RecoveryConflictError, match="parent authority changed"):
        journal.repair_mode(entry_id)

    original = original_parent / target.name
    assert (original.stat().st_mode & 0o7777) == 0o600
    assert (replacement.stat().st_mode & 0o7777) == 0o600
    assert journal._entry_path(entry_id).exists()

def test_checkpoint_refuses_changed_caller_pinned_parent_before_publication(
    tmp_path: Path,
) -> None:
    parent = tmp_path / "live"
    parent.mkdir()
    target = parent / "document.txt"
    target.write_bytes(b"base")
    parent_st = parent.stat()

    parked = tmp_path / "parked"
    parent.rename(parked)
    parent.mkdir()
    target.write_bytes(b"decoy")

    journal = RecoveryJournal(tmp_path / "recovery")
    with pytest.raises(
        RecoveryConflictError,
        match="target parent authority changed before recovery checkpoint",
    ):
        journal.checkpoint(
            target,
            b"exact editor text",
            commit_content=b"commit",
            metadata={
                "mode_repair_contract": MODE_REPAIR_CONTRACT_V1,
                "private_commit_mode": format(PRIVATE_ATOMIC_COMMIT_MODE, "04o"),
                "intended_mode": format(0o640, "04o"),
                "target_parent_dev": str(int(parent_st.st_dev)),
                "target_parent_ino": str(int(parent_st.st_ino)),
            },
        )

    assert journal.discover() == []
    assert not journal.root.exists()

