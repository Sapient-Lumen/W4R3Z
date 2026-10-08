from __future__ import annotations
import errno
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import pytest

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT / "src", ROOT):
    if str(candidate) not in sys.path: sys.path.insert(0, str(candidate))
from micromax_editor.recovery_journal import (
    MODE_REPAIR_CONTRACT_V1,
    PRIVATE_ATOMIC_COMMIT_MODE,
    RecoveryConflictError,
    RecoveryCorruptError,
    RecoveryJournal,
    RecoveryStatus,
    RecoveryTooLargeError,
)



def atomic_writer(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".test-tmp")
    with temp.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def mode_repair_metadata(
    target: Path,
    intended_mode: int = 0o640,
) -> dict[str, str]:
    parent = target.parent.stat()
    return {
        "mode_repair_contract": MODE_REPAIR_CONTRACT_V1,
        "private_commit_mode": format(PRIVATE_ATOMIC_COMMIT_MODE, "04o"),
        "intended_mode": format(intended_mode, "04o"),
        "target_parent_dev": str(int(parent.st_dev)),
        "target_parent_ino": str(int(parent.st_ino)),
    }


class RecoveryJournalJourneyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.target = root / "document.txt"
        self.journal = RecoveryJournal(root / "recovery")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_constructor_is_lazy_until_first_checkpoint(self) -> None:
        self.assertFalse(self.journal.root.exists())
        self.assertEqual([], self.journal.discover())
        self.assertFalse(self.journal.root.exists())

    def test_default_checkpoint_and_dismiss_report_real_sync_witnesses(self) -> None:
        entry_id = self.journal.checkpoint(self.target, b"content")

        self.assertTrue(self.journal.last_checkpoint_file_synced)
        self.assertIsInstance(self.journal.last_checkpoint_directory_synced, bool)
        self.assertTrue(self.journal.dismiss(entry_id))
        self.assertIsInstance(self.journal.last_dismiss_directory_synced, bool)

    def test_unsupported_directory_fsync_is_an_honest_false_witness(self) -> None:
        real_fsync = os.fsync

        def selective_fsync(fd: int) -> None:
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError(errno.EINVAL, "directory fsync unsupported")
            real_fsync(fd)

        with patch("micromax_editor.recovery_journal.os.fsync", selective_fsync):
            entry_id = self.journal.checkpoint(self.target, b"content")
            self.assertTrue(self.journal.last_checkpoint_file_synced)
            self.assertFalse(self.journal.last_checkpoint_directory_synced)
            self.assertTrue(self.journal.dismiss(entry_id))
            self.assertFalse(self.journal.last_dismiss_directory_synced)

    def test_real_checkpoint_directory_fsync_failure_remains_visible(self) -> None:
        real_fsync = os.fsync

        def selective_fsync(fd: int) -> None:
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError(errno.EIO, "directory fsync failed")
            real_fsync(fd)

        with patch("micromax_editor.recovery_journal.os.fsync", selective_fsync):
            with self.assertRaises(OSError) as caught:
                self.journal.checkpoint(self.target, b"content")

        self.assertEqual(errno.EIO, caught.exception.errno)
        # Replace completed before the directory durability error.  The caller
        # sees failure, while restart can still discover the valid record.
        [candidate] = self.journal.discover()
        self.assertEqual(RecoveryStatus.RECOVERABLE, candidate.status)
        self.assertEqual([], list(self.journal.root.glob("*.tmp")))

    def test_failed_checkpoint_attempt_does_not_reuse_prior_sync_witnesses(self) -> None:
        self.journal.checkpoint(self.target, b"content")
        self.assertTrue(self.journal.last_checkpoint_file_synced)

        with self.assertRaises(ValueError):
            self.journal.checkpoint(self.target, b"content", buffer_id="")

        self.assertFalse(self.journal.last_checkpoint_file_synced)
        self.assertFalse(self.journal.last_checkpoint_directory_synced)

    def test_in_process_checkpoint_fault_cleans_private_temp_file(self) -> None:
        def fault(stage: str) -> None:
            if stage == "checkpoint_temp_created":
                raise OSError("fault after private temp creation")

        journal = RecoveryJournal(self.journal.root, fault=fault)
        with self.assertRaisesRegex(OSError, "private temp creation"):
            journal.checkpoint(self.target, b"content")

        self.assertEqual([], list(self.journal.root.glob("*.recovery.json")))
        self.assertEqual([], list(self.journal.root.glob("*.tmp")))

    def test_metadata_round_trips_through_verified_candidate(self) -> None:
        entry_id = self.journal.checkpoint(
            self.target,
            b"content",
            metadata={"encoding": "utf-8", "requested_path": str(self.target)},
        )
        candidate = self.journal.inspect(entry_id)
        self.assertEqual("utf-8", candidate.metadata["encoding"])
        self.assertEqual(str(self.target), candidate.metadata["requested_path"])

    def test_failed_save_survives_restart_and_restore(self) -> None:
        self.target.write_bytes(b"disk")
        with self.assertRaises(OSError):
            self.journal.save_with_recovery(self.target, b"unsaved", lambda _p, _d: (_ for _ in ()).throw(OSError("disk full")), buffer_id="buffer-1")
        restarted = RecoveryJournal(self.journal.root)
        found = restarted.discover()
        self.assertEqual(1, len(found))
        self.assertEqual(RecoveryStatus.RECOVERABLE, found[0].status)
        restarted.restore(found[0].entry_id, atomic_writer)
        self.assertEqual(b"unsaved", self.target.read_bytes())
        self.assertEqual([], restarted.discover())

    def test_external_mutation_blocks_restore_without_override(self) -> None:
        self.target.write_bytes(b"base")
        entry_id = self.journal.checkpoint(self.target, b"buffer")
        self.target.write_bytes(b"external")
        candidate = self.journal.discover()[0]
        self.assertEqual(RecoveryStatus.TARGET_CHANGED, candidate.status)
        with self.assertRaises(RecoveryConflictError):
            self.journal.restore(entry_id, atomic_writer)
        self.assertEqual(b"external", self.target.read_bytes())
        self.assertEqual(b"buffer", self.journal.payload(entry_id))

    def test_post_commit_cleanup_failure_is_not_a_false_failed_save(self) -> None:
        def fault(stage: str) -> None:
            if stage == "before_dismiss":
                raise OSError("simulated cleanup failure")
        journal = RecoveryJournal(self.journal.root, fault=fault)
        outcome = journal.save_with_recovery(self.target, b"committed", atomic_writer)
        self.assertTrue(outcome.committed)
        self.assertFalse(outcome.recovery_retired)
        restarted = RecoveryJournal(self.journal.root)
        found = restarted.discover()
        self.assertEqual(RecoveryStatus.ALREADY_PERSISTED, found[0].status)
        self.assertTrue(restarted.dismiss(found[0].entry_id))
        self.assertFalse(restarted.dismiss(found[0].entry_id))

    def test_collision_safe_ids_and_repeatable_discovery(self) -> None:
        other = self.target.with_name("other.txt")
        first = self.journal.checkpoint(self.target, b"one", buffer_id="same")
        second = self.journal.checkpoint(other, b"two", buffer_id="same")
        self.assertNotEqual(first, second)
        self.assertEqual([c.entry_id for c in self.journal.discover()], [c.entry_id for c in self.journal.discover()])

    def test_corrupt_or_truncated_record_is_quarantined(self) -> None:
        entry_id = self.journal.checkpoint(self.target, b"content")
        entry = self.journal.root / f"{entry_id}.recovery.json"
        entry.write_bytes(entry.read_bytes()[:20])
        self.assertEqual([], self.journal.discover())
        quarantined = list((self.journal.root / "quarantine").iterdir())
        self.assertEqual(1, len(quarantined))

    def test_oversize_is_rejected_before_journaling(self) -> None:
        journal = RecoveryJournal(self.journal.root, max_payload_bytes=4)
        with self.assertRaises(RecoveryTooLargeError):
            journal.checkpoint(self.target, b"12345")
        self.assertEqual([], list(self.journal.root.glob("*.recovery.json")))

    def test_writer_cannot_retire_journal_without_verified_commit(self) -> None:
        entry_id = self.journal.checkpoint(self.target, b"recovery")
        with self.assertRaises(Exception):
            self.journal.restore(entry_id, lambda _path, _data: None)
        self.assertEqual(b"recovery", self.journal.payload(entry_id))

    def test_missing_original_target_is_recoverable(self) -> None:
        entry_id = self.journal.checkpoint(self.target, b"new document")
        [candidate] = self.journal.discover()
        self.assertEqual(entry_id, candidate.entry_id)
        self.assertEqual(RecoveryStatus.RECOVERABLE, candidate.status)

    def test_same_base_bytes_remain_recoverable_after_metadata_change(self) -> None:
        self.target.write_bytes(b"base")
        entry_id = self.journal.checkpoint(self.target, b"buffer")
        os.utime(self.target, None)
        [candidate] = self.journal.discover()
        self.assertEqual(entry_id, candidate.entry_id)
        self.assertEqual(RecoveryStatus.RECOVERABLE, candidate.status)

    def test_target_symlink_is_not_followed(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symbolic links unavailable")
        real = self.target.with_name("real.txt")
        real.write_bytes(b"authority")
        try:
            self.target.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links unavailable to this account")
        with self.assertRaises(RecoveryConflictError):
            self.journal.checkpoint(self.target, b"buffer")
        self.assertEqual(b"authority", real.read_bytes())

    def test_interrupted_journal_replace_leaves_no_temp_file(self) -> None:
        from unittest import mock
        with mock.patch(f"{RecoveryJournal.__module__}.os.replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(OSError):
                self.journal.checkpoint(self.target, b"content")
        self.assertEqual([], list(self.journal.root.glob("*.tmp")))
        self.assertEqual([], list(self.journal.root.glob("*.recovery.json")))

    def test_journal_permissions_are_private_on_posix(self) -> None:
        if os.name != "posix":
            self.skipTest("POSIX permission bits are not authoritative on this platform")
        entry_id = self.journal.checkpoint(self.target, b"content")
        mode = (self.journal.root / f"{entry_id}.recovery.json").stat().st_mode & 0o777
        self.assertEqual(0o600, mode)

    def test_record_tampering_fails_checksum_and_never_restores(self) -> None:
        entry_id = self.journal.checkpoint(self.target, b"secret")
        entry = self.journal.root / f"{entry_id}.recovery.json"
        raw = bytearray(entry.read_bytes())
        marker = b'"payload":{"encoding":"raw-tail","sha256":"'
        digest_at = raw.index(marker) + len(marker)
        raw[digest_at] = ord("0") if raw[digest_at] != ord("0") else ord("1")
        entry.write_bytes(raw)
        with self.assertRaises(RecoveryCorruptError):
            self.journal.payload(entry_id)


if __name__ == "__main__":
    unittest.main()


def test_recovery_payload_and_commit_identity_are_separate(tmp_path: Path) -> None:
    from micromax_editor.recovery_journal import PAYLOAD_KIND_EDITOR_TEXT

    target = tmp_path / "normalized.txt"
    target.write_bytes(b"disk\n")
    journal = RecoveryJournal(tmp_path / "recovery")
    exact_text = "alpha   ".encode("utf-8", errors="surrogatepass")
    entry_id = journal.checkpoint(
        target,
        exact_text,
        buffer_id="buffer-normalized",
        commit_content=b"alpha\n",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8"},
    )

    snapshot = journal.load(entry_id)
    assert snapshot.editor_text() == "alpha   "
    assert snapshot.candidate.payload_sha256 != snapshot.candidate.commit.sha256

    # A crash after the normalized document commit but before journal cleanup is
    # recognized as completed; the exact pre-normalization payload remains
    # available only until startup retires the stale record.
    target.write_bytes(b"alpha\n")
    [candidate] = journal.discover()
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED


def test_commit_checkpoint_rejects_bytes_not_covered_by_record(tmp_path: Path) -> None:
    target = tmp_path / "mismatch.txt"
    target.write_bytes(b"base")
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"exact editor text",
        commit_content=b"intended bytes",
        buffer_id="buffer-mismatch",
    )

    with pytest.raises(RecoveryConflictError, match="commit bytes"):
        journal.commit_checkpoint(entry_id, b"different bytes", atomic_writer)

    assert target.read_bytes() == b"base"
    assert journal.payload(entry_id) == b"exact editor text"


def test_unreadable_or_over_budget_target_is_reported_not_quarantined(tmp_path: Path) -> None:
    target = tmp_path / "growing.txt"
    target.write_bytes(b"base")
    journal = RecoveryJournal(
        tmp_path / "recovery",
        max_payload_bytes=32,
        max_comparison_bytes=4,
    )
    entry_id = journal.checkpoint(target, b"mine", commit_content=b"mine")
    target.write_bytes(b"larger")

    [candidate] = journal.discover()
    assert candidate.entry_id == entry_id
    assert candidate.status is RecoveryStatus.TARGET_UNREADABLE
    assert candidate.error
    assert journal.payload(entry_id) == b"mine"


def test_selector_requires_unambiguous_human_scale_prefix(tmp_path: Path) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    target = tmp_path / "selector.txt"
    entry_id = journal.checkpoint(target, b"mine")
    [candidate] = journal.discover()

    with pytest.raises(Exception, match="at least 8"):
        journal.resolve_selector(entry_id[:4], candidates=[candidate])
    assert journal.resolve_selector(entry_id[:8], candidates=[candidate]) == candidate
    assert journal.resolve_selector("#1", candidates=[candidate]) == candidate


def test_default_recovery_root_uses_state_directory_and_ignores_relative_xdg(
    tmp_path: Path,
) -> None:
    from micromax_editor.recovery_journal import default_recovery_root

    home = tmp_path / "home"
    state = tmp_path / "state"
    assert default_recovery_root(
        environ={"XDG_STATE_HOME": str(state)}, home=home
    ) == (state / "micromax" / "recovery").resolve()
    assert default_recovery_root(
        environ={"XDG_STATE_HOME": "relative"}, home=home
    ) == (home / ".local" / "state" / "micromax" / "recovery").resolve()


def test_presence_is_filename_only_and_bounded(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "recovery"
    root.mkdir()
    for value in range(1, 4):
        (root / f"{value:064x}.recovery.json").write_text(
            "not decoded during startup\n",
            encoding="utf-8",
        )
    journal = RecoveryJournal(root, max_scan_records=2)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("presence must not decode journal records")

    monkeypatch.setattr(journal, "_read", forbidden)
    presence = journal.presence()

    assert presence.count == 2
    assert presence.truncated is True


def test_exact_entry_presence_is_bounded_no_follow_and_does_not_decode(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "recovery"
    journal = RecoveryJournal(root, max_payload_bytes=4)
    assert journal.entry_present("a" * 64) is False

    entry_id = journal.checkpoint(tmp_path / "target.txt", b"data")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("exact presence must not decode a journal record")

    monkeypatch.setattr(journal, "_read", forbidden)
    assert journal.entry_present(entry_id) is True

    record = journal._entry_path(entry_id)
    record.unlink()
    record.write_bytes(b"x" * (journal._record_limit + 1))
    with pytest.raises(RecoveryTooLargeError, match="bounded read limit"):
        journal.entry_present(entry_id)

    record.unlink()
    record.mkdir()
    with pytest.raises(RecoveryCorruptError, match="trusted regular file"):
        journal.entry_present(entry_id)

    with pytest.raises(RecoveryCorruptError, match="invalid recovery entry id"):
        journal.entry_present("not-an-entry-id")


def test_scan_keeps_newest_records_with_truthful_omission_count(tmp_path: Path) -> None:
    root = tmp_path / "recovery"
    journal = RecoveryJournal(root)
    entry_ids: list[str] = []
    for index in range(3):
        target = tmp_path / f"target-{index}.txt"
        entry_id = journal.checkpoint(target, f"payload-{index}".encode())
        entry_ids.append(entry_id)
        os.utime(
            journal._entry_path(entry_id),
            ns=(1_000_000_000 + index, 1_000_000_000 + index),
        )

    bounded = RecoveryJournal(root, max_scan_records=2)
    scan = bounded.scan()

    assert [row.entry_id for row in scan.candidates] == entry_ids[1:][::-1]
    assert scan.omitted == 1
    assert scan.truncated is False


def test_scan_caps_aggregate_target_comparison_bytes(tmp_path: Path) -> None:
    root = tmp_path / "recovery"
    journal = RecoveryJournal(root)
    for index in range(2):
        target = tmp_path / f"target-{index}.txt"
        target.write_bytes(b"base")
        entry_id = journal.checkpoint(target, f"edit-{index}".encode())
        os.utime(
            journal._entry_path(entry_id),
            ns=(1_000_000_000 + index, 1_000_000_000 + index),
        )

    bounded = RecoveryJournal(root, max_scan_comparison_bytes=4)
    scan = bounded.scan()

    assert len(scan.candidates) == 2
    assert scan.comparison_limited == 1
    limited = [row for row in scan.candidates if row.error]
    assert len(limited) == 1
    assert limited[0].status is RecoveryStatus.TARGET_UNREADABLE
    assert "comparison budget exhausted" in str(limited[0].error)


def test_scan_caps_aggregate_record_bytes_without_quarantining_valid_rows(
    tmp_path: Path,
) -> None:
    root = tmp_path / "recovery"
    journal = RecoveryJournal(root)
    for index in range(2):
        journal.checkpoint(tmp_path / f"target-{index}.txt", b"payload")

    bounded = RecoveryJournal(root, max_scan_record_bytes=1)
    scan = bounded.scan()

    assert scan.candidates == ()
    assert scan.omitted == 2
    assert scan.record_bytes_limited is True
    assert scan.corrupt == 0
    assert len(list(root.glob("*.recovery.json"))) == 2


def test_full_id_can_address_a_record_omitted_from_bounded_inventory(
    tmp_path: Path,
) -> None:
    root = tmp_path / "recovery"
    journal = RecoveryJournal(root)
    old_id = journal.checkpoint(tmp_path / "old.txt", b"old")
    new_id = journal.checkpoint(tmp_path / "new.txt", b"new")
    os.utime(journal._entry_path(old_id), ns=(1, 1))
    os.utime(journal._entry_path(new_id), ns=(2, 2))

    bounded = RecoveryJournal(root, max_scan_records=1)
    scan = bounded.scan()
    assert [row.entry_id for row in scan.candidates] == [new_id]
    assert scan.omitted == 1

    resolved = bounded.resolve_selector(old_id, candidates=list(scan.candidates))
    assert resolved.entry_id == old_id


def test_presence_refuses_a_replaced_symlink_root(tmp_path: Path) -> None:
    if not hasattr(os, "symlink"):
        pytest.skip("symbolic links unavailable")
    root = tmp_path / "recovery"
    journal = RecoveryJournal(root)
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        root.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable to this account")

    with pytest.raises(RecoveryCorruptError, match="not a trusted directory"):
        journal.presence()


def test_scan_quarantines_record_symlink_without_reading_its_target(
    tmp_path: Path,
) -> None:
    if not hasattr(os, "symlink"):
        pytest.skip("symbolic links unavailable")
    root = tmp_path / "recovery"
    root.mkdir()
    outside = tmp_path / "private.txt"
    outside.write_text("must not be decoded", encoding="utf-8")
    entry = root / ("a" * 64 + ".recovery.json")
    try:
        entry.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable to this account")

    journal = RecoveryJournal(root)
    scan = journal.scan()

    assert scan.candidates == ()
    assert scan.corrupt == 1
    assert outside.read_text(encoding="utf-8") == "must not be decoded"
    quarantined = list((root / "quarantine").iterdir())
    assert len(quarantined) == 1
    assert quarantined[0].is_symlink()


@pytest.mark.skipif(
    os.name != "posix" or not hasattr(os, "fchmod"),
    reason="permission repair is a POSIX fd-bound contract",
)
def test_mode_repair_verifies_commit_owner_mode_and_syncs_before_retire(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repair.txt"
    target.write_bytes(b"base")
    target.chmod(0o640)
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"editor text",
        commit_content=b"committed",
        metadata=mode_repair_metadata(target, 0o640),
    )

    # Model process death after private-temp replace but before mode restore.
    target.write_bytes(b"committed")
    target.chmod(PRIVATE_ATOMIC_COMMIT_MODE)
    candidate = journal.inspect(entry_id)
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED
    assert candidate.current_mode == 0o600
    assert candidate.intended_mode == 0o640
    assert candidate.mode_repair_available is True
    assert candidate.mode_repair_required is True
    assert candidate.mode_repair_conflict is False

    outcome = journal.repair_mode(entry_id)

    assert outcome.previous_mode == 0o600
    assert outcome.intended_mode == 0o640
    assert outcome.changed is True
    assert outcome.file_synced is True
    assert isinstance(outcome.directory_synced, bool)
    assert outcome.recovery_retired is True
    assert (target.stat().st_mode & 0o7777) == 0o640
    assert target.read_bytes() == b"committed"
    assert journal.discover() == []


@pytest.mark.skipif(
    os.name != "posix" or not hasattr(os, "fchmod"),
    reason="permission repair is a POSIX fd-bound contract",
)
def test_mode_repair_failure_after_chmod_is_retryable_without_guessing(
    tmp_path: Path,
) -> None:
    target = tmp_path / "retry-repair.txt"
    target.write_bytes(b"base")
    target.chmod(0o640)
    root = tmp_path / "recovery"

    def fault(stage: str) -> None:
        if stage == "after_mode_repair_chmod":
            raise OSError("simulated crash after fchmod")

    journal = RecoveryJournal(root, fault=fault)
    entry_id = journal.checkpoint(
        target,
        b"editor text",
        commit_content=b"committed",
        metadata=mode_repair_metadata(target, 0o640),
    )
    target.write_bytes(b"committed")
    target.chmod(0o600)

    with pytest.raises(OSError, match="after fchmod"):
        journal.repair_mode(entry_id)

    assert (target.stat().st_mode & 0o7777) == 0o640
    assert journal._entry_path(entry_id).exists()

    restarted = RecoveryJournal(root)
    candidate = restarted.inspect(entry_id)
    assert candidate.mode_repair_available is True
    assert candidate.mode_repair_required is False
    outcome = restarted.repair_mode(entry_id)
    assert outcome.changed is False
    assert outcome.file_synced is True
    assert outcome.recovery_retired is True


@pytest.mark.skipif(
    os.name != "posix" or not hasattr(os, "fchmod"),
    reason="permission repair is a POSIX fd-bound contract",
)
def test_mode_repair_refuses_changed_bytes_or_unexpected_mode(tmp_path: Path) -> None:
    target = tmp_path / "refuse-repair.txt"
    target.write_bytes(b"base")
    target.chmod(0o640)
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"editor text",
        commit_content=b"committed",
        metadata=mode_repair_metadata(target, 0o640),
    )

    target.write_bytes(b"different")
    target.chmod(0o600)
    with pytest.raises(RecoveryConflictError, match="bytes no longer match"):
        journal.repair_mode(entry_id)
    assert journal._entry_path(entry_id).exists()

    target.write_bytes(b"committed")
    target.chmod(0o644)
    candidate = journal.inspect(entry_id)
    assert candidate.status is RecoveryStatus.ALREADY_PERSISTED
    assert candidate.mode_repair_available is False
    assert candidate.mode_repair_conflict is True
    with pytest.raises(RecoveryConflictError, match="mode changed outside"):
        journal.repair_mode(entry_id)
    assert (target.stat().st_mode & 0o7777) == 0o644
    assert journal._entry_path(entry_id).exists()
