from __future__ import annotations

import os
from pathlib import Path

import pytest

from micromax_editor.recovery_journal import (
    RecoveryConflictError,
    RecoveryJournal,
    RecoveryResidueKind,
)
from micromax_editor.save_residue import (
    ProcessIdentity,
    TempOwnerState,
    build_private_temp_name,
    current_process_identity,
)


CURRENT_OWNER = current_process_identity()
STALE_OWNER = ProcessIdentity(
    "0000000000000000",
    999999,
    123,
    CURRENT_OWNER.pid_namespace_token,
)
UNKNOWN_OWNER = ProcessIdentity("x", os.getpid(), 0)


def _private_temp(
    parent: Path,
    basename: str,
    *,
    lease: str,
    owner: ProcessIdentity = STALE_OWNER,
    token: str = "1" * 16,
    payload: bytes = b"private draft",
) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    name = build_private_temp_name(
        parent,
        basename,
        lease_id=lease,
        owner=owner,
        random_token=token,
    )
    path = parent / name
    path.write_bytes(payload)
    path.chmod(0o600)
    return path


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative cleanup contract")
def test_orphan_checkpoint_temp_is_inventoried_and_explicitly_cleaned(
    tmp_path: Path,
) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    temp = _private_temp(journal.root, "record.recovery.json", lease="a" * 32)

    scan = journal.scan_residue()

    assert len(scan.residues) == 1
    residue = scan.residues[0]
    assert residue.path == temp
    assert residue.kind is RecoveryResidueKind.CHECKPOINT_TEMP
    assert residue.owner_state is TempOwnerState.STALE
    assert residue.cleanup_eligible is True
    assert residue.reason == ""

    outcome = journal.cleanup_residue(residue)
    assert outcome.removed is True
    assert not temp.exists()


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative cleanup contract")
def test_document_temp_requires_verified_record_lease_and_parent_identity(
    tmp_path: Path,
) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    target = documents / "note.txt"
    target.write_bytes(b"base")
    journal = RecoveryJournal(tmp_path / "recovery")
    lease = "b" * 32
    entry_id = journal.checkpoint(
        target,
        b"draft",
        buffer_id="note",
        metadata={"save_lease_id": lease},
    )
    matching = _private_temp(documents, target.name, lease=lease, token="2" * 16)
    unrelated = _private_temp(
        documents,
        target.name,
        lease="c" * 32,
        token="3" * 16,
    )

    scan = journal.scan_residue()

    assert len(scan.residues) == 1
    residue = scan.residues[0]
    assert residue.path == matching
    assert residue.kind is RecoveryResidueKind.DOCUMENT_TEMP
    assert residue.entry_id == entry_id
    assert residue.cleanup_eligible is True
    assert unrelated.exists()

    journal.cleanup_residue(residue)
    assert not matching.exists()
    assert unrelated.exists()
    assert journal._entry_path(entry_id).exists()


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative cleanup contract")
def test_active_and_unprovable_creators_are_never_cleanup_eligible(
    tmp_path: Path,
) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    active = current_process_identity()
    if not active.reliable:
        pytest.skip("host process identity is not reliable")
    active_path = _private_temp(
        journal.root,
        "active",
        lease="d" * 32,
        owner=active,
        token="4" * 16,
    )
    unknown_path = _private_temp(
        journal.root,
        "unknown",
        lease="e" * 32,
        owner=UNKNOWN_OWNER,
        token="5" * 16,
    )

    rows = {row.path: row for row in journal.scan_residue().residues}

    assert rows[active_path].owner_state is TempOwnerState.ACTIVE
    assert rows[active_path].cleanup_eligible is False
    assert "still active" in rows[active_path].reason
    assert rows[unknown_path].owner_state is TempOwnerState.UNKNOWN
    assert rows[unknown_path].cleanup_eligible is False
    assert "cannot be disproved" in rows[unknown_path].reason
    with pytest.raises(RecoveryConflictError):
        journal.cleanup_residue(rows[active_path])
    with pytest.raises(RecoveryConflictError):
        journal.cleanup_residue(rows[unknown_path])
    assert active_path.exists() and unknown_path.exists()


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative cleanup contract")
def test_cleanup_revalidates_exact_inode_after_inventory(tmp_path: Path) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    temp = _private_temp(journal.root, "replace", lease="f" * 32)
    [residue] = journal.scan_residue().residues

    temp.unlink()
    temp.write_bytes(b"replacement")
    temp.chmod(0o600)

    with pytest.raises(RecoveryConflictError, match="metadata changed"):
        journal.cleanup_residue(residue)
    assert temp.read_bytes() == b"replacement"


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative cleanup contract")
def test_replaced_document_parent_is_not_scanned(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    target = documents / "note.txt"
    target.write_bytes(b"base")
    journal = RecoveryJournal(tmp_path / "recovery")
    lease = "1" * 32
    journal.checkpoint(target, b"draft", metadata={"save_lease_id": lease})

    old_documents = tmp_path / "documents-old"
    documents.rename(old_documents)
    documents.mkdir()
    replacement_temp = _private_temp(
        documents,
        target.name,
        lease=lease,
        token="6" * 16,
    )

    scan = journal.scan_residue()

    assert scan.residues == ()
    assert scan.unreadable_directories == 1
    assert replacement_temp.exists()


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative cleanup contract")
def test_residue_inventory_caps_rows_and_directory_work(tmp_path: Path) -> None:
    journal = RecoveryJournal(
        tmp_path / "recovery",
        max_residue_files=2,
        max_residue_directory_entries=3,
    )
    for index in range(5):
        _private_temp(
            journal.root,
            f"temp-{index}",
            lease=f"{index + 2:032x}",
            token=f"{index + 7:016x}",
        )

    scan = journal.scan_residue()

    assert len(scan.residues) == 2
    assert scan.directory_entries_visited == 3
    assert scan.truncated is True
    assert scan.omitted == 1
