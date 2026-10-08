from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest

import micromax_editor.editor as editor_module
from micromax_editor.editor import Editor
from micromax_editor.recovery_journal import (
    MODE_REPAIR_CONTRACT_V1,
    PAYLOAD_KIND_EDITOR_TEXT,
    PRIVATE_ATOMIC_COMMIT_MODE,
    RecoveryError,
    RecoveryJournal,
    RecoveryStatus,
)
from micromax_editor.startup import create_editor_runtime, open_initial_buffer
from micromax_editor.save_residue import (
    ProcessIdentity,
    build_private_temp_name,
    current_process_identity,
)


def _runtime(tmp_path: Path):
    plugins = tmp_path / "plugins"
    plugins.mkdir(exist_ok=True)
    return create_editor_runtime(
        plugins_root=plugins,
        workspace_trust="trusted",
        recovery_root=tmp_path / "recovery",
    )


def test_explicit_save_failure_survives_restart_and_opens_dirty_buffer_without_writing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    target = tmp_path / "journey.txt"
    target.write_text("disk", encoding="utf-8")

    ed = _runtime(tmp_path).editor
    assert open_initial_buffer(ed, path=str(target)).ok is True
    ed.cur().buf.set_text("unsaved")
    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("simulated disk full"),
    ):
        assert ed.exec_command_line("save") is False

    assert target.read_text(encoding="utf-8") == "disk"
    assert ed.status_model()["recovery_record_count"] == 1
    assert "[recovery:1]" in ed.statusline_text(40)
    [candidate] = ed.recovery_journal.discover()
    assert candidate.status is RecoveryStatus.RECOVERABLE
    assert candidate.metadata["encoding"] == "utf-8"
    assert candidate.metadata["requested_path"] == str(target)

    restarted = _runtime(tmp_path).editor
    assert any("1 interrupted-save record present" in row for row in restarted.messages)
    assert restarted.exec_command_line("recoveries") is True
    assert "[recoverable]" in restarted.messages[-1]
    assert restarted.exec_command_line("recover #1") is True
    assert "disk unchanged" in restarted.messages[-1]
    assert restarted.cur().buf.get_text() == "unsaved"
    assert restarted.cur().buf.dirty is True
    assert target.read_text(encoding="utf-8") == "disk"

    assert restarted.exec_command_line("save") is True
    assert target.read_text(encoding="utf-8") == "unsaved"
    assert restarted.recovery_journal.discover() == []
    assert restarted.status_model()["recovery_record_count"] == 0
    assert "[recovery:" not in restarted.statusline_text(80)


def test_recovery_open_undo_redo_keeps_text_and_journal_authority_atomic(
    tmp_path: Path,
) -> None:
    target = tmp_path / "atomic-recovery.txt"
    target.write_text("disk generation", encoding="utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"recovered generation",
        buffer_id="crashed-buffer-id",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "dos"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(
        str(target),
        "disk generation",
        path=str(target),
    )
    eb = ed.buffers[name]
    original_recovery_id = eb.save_recovery_id
    eb.local_options["encoding"] = "ascii"
    eb.local_options["fileformat"] = "unix"
    eb.local_options["filetype"] = "before-recovery"

    assert ed.exec_command_line("recover #1") is True
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is True
    assert eb.save_recovery_id == "crashed-buffer-id"
    assert eb.interrupted_save_entry_id == entry_id
    assert eb.interrupted_save_target == str(target.resolve())
    assert eb.local_options["encoding"] == "utf-8"
    assert eb.local_options["fileformat"] == "dos"
    assert journal.presence().count == 1

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "disk generation"
    assert eb.buf.dirty is False
    assert eb.save_recovery_id == original_recovery_id
    assert eb.interrupted_save_entry_id is None
    assert eb.interrupted_save_target is None
    assert eb.interrupted_save_requires_force is False
    assert eb.local_options["encoding"] == "ascii"
    assert eb.local_options["fileformat"] == "unix"
    assert eb.local_options["filetype"] == "before-recovery"

    # Saving the clean, undone generation must not acknowledge or delete the
    # still-unreviewed recovery payload.
    assert ed.exec_command_line("save") is True
    assert target.read_text(encoding="utf-8") == "disk generation"
    assert journal.presence().count == 1
    assert journal._entry_path(entry_id).exists()

    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is True
    assert eb.save_recovery_id == "crashed-buffer-id"
    assert eb.interrupted_save_entry_id == entry_id
    assert eb.interrupted_save_target == str(target.resolve())
    assert eb.local_options["encoding"] == "utf-8"
    assert eb.local_options["fileformat"] == "dos"
    assert journal.presence().count == 1

    # Only a successful save of the redone recovered generation retires the
    # record that protected it.
    assert ed.exec_command_line("save") is True
    assert target.read_text(encoding="utf-8") == "recovered generation"
    assert journal.presence().count == 0


def test_saved_recovery_undo_redo_never_resurrects_retired_journal_authority(
    tmp_path: Path,
) -> None:
    target = tmp_path / "saved-recovery-history.txt"
    target.write_text("disk generation", encoding="utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"recovered generation",
        buffer_id="crashed-buffer-id",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(
        str(target),
        "disk generation",
        path=str(target),
    )
    eb = ed.buffers[name]
    original_recovery_id = eb.save_recovery_id

    assert ed.exec_command_line("recover #1") is True
    assert eb.interrupted_save_entry_id == entry_id
    assert ed.exec_command_line("save") is True
    assert journal.entry_present(entry_id) is False
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is False

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "disk generation"
    assert eb.buf.dirty is True
    assert eb.save_recovery_id == original_recovery_id
    assert eb.interrupted_save_entry_id is None
    assert eb.interrupted_save_target is None
    assert eb.interrupted_save_requires_force is False
    assert journal.presence().count == 0

    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is False
    assert eb.save_recovery_id == "crashed-buffer-id"
    assert eb.interrupted_save_entry_id is None
    assert eb.interrupted_save_target is None
    assert eb.interrupted_save_requires_force is False
    assert journal.presence().count == 0


def test_dismissed_recovery_history_never_revives_deleted_authority(
    tmp_path: Path,
) -> None:
    target = tmp_path / "dismissed-recovery-history.txt"
    target.write_text("disk generation", encoding="utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"recovered generation",
        buffer_id="dismissed-crash",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(str(target), "disk generation", path=str(target))
    eb = ed.buffers[name]

    assert ed.exec_command_line("recover #1") is True
    assert eb.interrupted_save_entry_id == entry_id
    assert ed.exec_command_line("recoverdismiss #1") is True
    assert journal.entry_present(entry_id) is False
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id is None

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "disk generation"
    assert eb.buf.dirty is False
    assert eb.interrupted_save_entry_id is None

    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id is None
    assert eb.interrupted_save_target is None
    assert eb.interrupted_save_requires_force is False


def test_recovery_history_drops_known_unusable_record_replacement(
    tmp_path: Path,
) -> None:
    target = tmp_path / "corrupt-recovery-history.txt"
    target.write_text("disk generation", encoding="utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"recovered generation",
        buffer_id="corrupt-crash",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(str(target), "disk generation", path=str(target))
    eb = ed.buffers[name]

    assert ed.exec_command_line("recover #1") is True
    assert ed.undo_feedback() is True
    entry_path = journal._entry_path(entry_id)
    entry_path.unlink()
    entry_path.mkdir()

    with pytest.raises(RecoveryError, match="trusted regular file"):
        journal.entry_present(entry_id)

    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "recovered generation"
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id is None
    assert eb.interrupted_save_target is None
    assert eb.interrupted_save_requires_force is False


def test_metadata_only_recovery_open_is_still_one_reversible_dirty_decision(
    tmp_path: Path,
) -> None:
    target = tmp_path / "missing-empty.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"",
        buffer_id="empty-crash",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(str(target), "", path=str(target))
    eb = ed.buffers[name]
    before_version = eb.buf.version
    before_lines = eb.buf.snapshot_lines()

    assert ed.exec_command_line("recover #1") is True
    assert eb.buf.snapshot_lines() == before_lines
    assert eb.buf.version == before_version
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id == entry_id
    assert ed.undo.depth() == 1

    assert ed.undo_feedback() is True
    assert eb.buf.snapshot_lines() == before_lines
    assert eb.buf.version == before_version
    assert eb.buf.dirty is False
    assert eb.interrupted_save_entry_id is None
    assert journal.presence().count == 1

    assert ed.redo_feedback() is True
    assert eb.buf.snapshot_lines() == before_lines
    assert eb.buf.version == before_version
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id == entry_id
    assert journal.presence().count == 1

    # Once saved, this metadata-only history row remains reversible without
    # inventing a text version or reviving the retired journal filename.
    assert ed.exec_command_line("save") is True
    assert journal.entry_present(entry_id) is False
    assert eb.buf.dirty is False
    saved_version = eb.buf.version

    assert ed.undo_feedback() is True
    assert eb.buf.version == saved_version
    assert eb.buf.dirty is False
    assert eb.interrupted_save_entry_id is None

    assert ed.redo_feedback() is True
    assert eb.buf.version == saved_version
    assert eb.buf.dirty is False
    assert eb.interrupted_save_entry_id is None


def test_changed_target_requires_force_and_recovery_buffer_never_autosaves(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    target = tmp_path / "conflict.txt"
    target.write_text("base", encoding="utf-8")

    ed = _runtime(tmp_path).editor
    assert open_initial_buffer(ed, path=str(target)).ok is True
    ed.cur().buf.set_text("recovered edit")
    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("interrupted"),
    ):
        assert ed.exec_command_line("save") is False
    target.write_text("external edit", encoding="utf-8")

    restarted = _runtime(tmp_path).editor
    [candidate] = restarted.interrupted_save_candidates()
    assert candidate.status is RecoveryStatus.TARGET_CHANGED
    assert restarted.exec_command_line("recover") is True
    assert "target changed" in restarted.messages[-1]
    assert restarted.cur().interrupted_save_requires_force is True

    restarted.cur().local_options["autosave"] = 1
    assert restarted.autosave_dirty_buffers(immediate=True) == []
    assert target.read_text(encoding="utf-8") == "external edit"
    assert restarted.exec_command_line("save") is False
    assert "use `save!`" in restarted.messages[-1]
    assert target.read_text(encoding="utf-8") == "external edit"
    assert restarted.exec_command_line("diff") is True
    assert any("-external edit" in row for row in restarted.messages[-8:])
    assert restarted.exec_command_line("save!") is True
    assert target.read_text(encoding="utf-8") == "recovered edit"
    assert restarted.recovery_journal.discover() == []


def test_recovery_checkpoint_preserves_symlink_and_forces_durable_write(
    tmp_path: Path,
    monkeypatch,
) -> None:
    if not hasattr(os, "symlink"):
        return
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    real = tmp_path / "real.txt"
    link = tmp_path / "link.txt"
    real.write_text("base", encoding="utf-8")
    try:
        link.symlink_to(real)
    except (OSError, NotImplementedError):
        return

    ed = _runtime(tmp_path).editor
    assert open_initial_buffer(ed, path=str(link)).ok is True
    ed.cur().buf.set_text("committed")
    calls: list[dict[str, object]] = []
    actual_writer = editor_module.write_file_bytes

    def witness(*args, **kwargs):
        calls.append(dict(kwargs))
        return actual_writer(*args, **kwargs)

    with mock.patch("micromax_editor.editor.write_file_bytes", side_effect=witness):
        info = ed.save()

    assert calls and calls[0]["fsync"] is True
    assert info["recovery_checkpointed"] is True
    assert info["recovery_retired"] is True
    assert info["file_synced"] is True
    assert isinstance(info["directory_synced"], bool)
    assert info["recovery_checkpoint_file_synced"] is True
    assert isinstance(info["recovery_checkpoint_directory_synced"], bool)
    assert isinstance(info["recovery_retire_directory_synced"], bool)
    assert info["write_path"] == str(real)
    assert info["followed_symlink"] is True
    assert link.is_symlink()
    assert real.read_text(encoding="utf-8") == "committed"
    assert ed.recovery_journal.discover() == []


def test_recovery_checkpoint_failure_warns_but_does_not_block_document_save(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    target = tmp_path / "large.txt"
    target.write_text("old", encoding="utf-8")
    ed = _runtime(tmp_path).editor
    ed.configure_recovery_journal(
        RecoveryJournal(tmp_path / "tiny-recovery", max_payload_bytes=4)
    )
    assert open_initial_buffer(ed, path=str(target)).ok is True
    ed.cur().buf.set_text("payload larger than four bytes")

    assert ed.exec_command_line("save") is True
    assert target.read_text(encoding="utf-8") == "payload larger than four bytes"
    assert "recovery unavailable" in ed.messages[-1]
    assert ed.recovery_journal.discover() == []


def test_scripts_cannot_enumerate_open_or_dismiss_private_recovery(
    tmp_path: Path,
) -> None:
    target = tmp_path / "private.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(target, b"private unsaved text", buffer_id="private-buffer")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    with ed.script_context("plugin:test"):
        assert ed.exec_command_line("recoveries") is False
        assert "disabled for scripts" in ed.messages[-1]
        assert ed.exec_command_line("recover") is False
        assert "disabled for scripts" in ed.messages[-1]
        assert ed.exec_command_line("recovermode") is False
        assert "disabled for scripts" in ed.messages[-1]
        assert ed.exec_command_line("recovertemps") is False
        assert "disabled for scripts" in ed.messages[-1]
        assert ed.exec_command_line("recoverclean") is False
        assert "disabled for scripts" in ed.messages[-1]
        assert ed.exec_command_line("recoverdismiss") is False
        assert "disabled for scripts" in ed.messages[-1]

    assert len(journal.discover()) == 1


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative temp cleanup")
def test_recovertemps_and_recoverclean_require_explicit_interactive_action(
    tmp_path: Path,
) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    journal.root.mkdir(parents=True, mode=0o700)
    name = build_private_temp_name(
        journal.root,
        "orphan.recovery.json",
        lease_id="9" * 32,
        owner=ProcessIdentity(
            "0000000000000000",
            999999,
            1,
            current_process_identity().pid_namespace_token,
        ),
        random_token="8" * 16,
    )
    temp = journal.root / name
    temp.write_bytes(b"private checkpoint")
    temp.chmod(0o600)

    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    assert ed.exec_command_line("recovertemps") is True
    assert "1 private save temp, 1 cleanup eligible" in ed.messages[-2]
    assert "[stale; cleanup eligible] checkpoint" in ed.messages[-1]
    assert temp.exists()

    assert ed.exec_command_line("recoverclean #1") is True
    assert "recoverclean: removed" in ed.messages[-1]
    assert not temp.exists()


@pytest.mark.skipif(
    os.name != "posix" or not hasattr(os, "fchmod"),
    reason="permission repair is a POSIX fd-bound contract",
)
def test_recover_retains_private_commit_until_explicit_recovermode(
    tmp_path: Path,
) -> None:
    target = tmp_path / "mode-repair.txt"
    target.write_bytes(b"base")
    target.chmod(0o640)
    journal = RecoveryJournal(tmp_path / "recovery")
    parent_st = target.parent.stat()
    entry_id = journal.checkpoint(
        target,
        b"saved editor text",
        commit_content=b"saved bytes",
        metadata={
            "requested_path": str(target),
            "mode_repair_contract": MODE_REPAIR_CONTRACT_V1,
            "private_commit_mode": format(PRIVATE_ATOMIC_COMMIT_MODE, "04o"),
            "intended_mode": "0640",
            "target_parent_dev": str(int(parent_st.st_dev)),
            "target_parent_ino": str(int(parent_st.st_ino)),
        },
    )
    target.write_bytes(b"saved bytes")
    target.chmod(0o600)

    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    assert ed.exec_command_line("recoveries") is True
    assert "[permission repair required]" in ed.messages[-1]
    assert "mode 0600->0640" in ed.messages[-1]
    assert ed.exec_command_line("recover #1") is True
    assert "journal retained" in ed.messages[-1]
    assert "recovermode" in ed.messages[-1]
    assert journal._entry_path(entry_id).exists()
    assert (target.stat().st_mode & 0o7777) == 0o600

    assert ed.exec_command_line("recovermode #1") is True
    assert "restored 0600->0640" in ed.messages[-1]
    assert (target.stat().st_mode & 0o7777) == 0o640
    assert target.read_bytes() == b"saved bytes"
    assert journal.discover() == []


def test_retargeted_nominal_symlink_recovers_against_original_authority(
    tmp_path: Path,
    monkeypatch,
) -> None:
    if not hasattr(os, "symlink"):
        return
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    original = tmp_path / "original.txt"
    redirected = tmp_path / "redirected.txt"
    link = tmp_path / "document-link.txt"
    original.write_text("original base", encoding="utf-8")
    redirected.write_text("redirected base", encoding="utf-8")
    try:
        link.symlink_to(original)
    except (OSError, NotImplementedError):
        return

    ed = _runtime(tmp_path).editor
    assert open_initial_buffer(ed, path=str(link)).ok is True
    ed.cur().buf.set_text("recovered through link")
    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("interrupted"),
    ):
        assert ed.exec_command_line("save") is False

    link.unlink()
    link.symlink_to(redirected)
    restarted = _runtime(tmp_path).editor
    [candidate] = restarted.interrupted_save_candidates()
    assert candidate.target == original
    assert candidate.status is RecoveryStatus.RECOVERABLE

    assert restarted.exec_command_line("recover") is True
    assert "original path moved" in restarted.messages[-1]
    assert restarted.cur().buf.path == str(original)
    assert restarted.exec_command_line("save") is True
    assert original.read_text(encoding="utf-8") == "recovered through link"
    assert redirected.read_text(encoding="utf-8") == "redirected base"
    assert link.resolve() == redirected


def test_failed_normalizing_save_recovers_exact_pre_normalization_text(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    target = tmp_path / "normalize.txt"
    target.write_text("disk\n", encoding="utf-8")

    ed = _runtime(tmp_path).editor
    assert open_initial_buffer(ed, path=str(target)).ok is True
    ed.cur().buf.set_text("alpha   ")
    assert ed.exec_command_line("set rmtrailingws true") is True
    assert ed.exec_command_line("set eofnewline true") is True

    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("simulated disk full"),
    ):
        assert ed.exec_command_line("save") is False

    [candidate] = ed.recovery_journal.discover()
    snapshot = ed.recovery_journal.load(candidate.entry_id)
    assert snapshot.editor_text() == "alpha   "
    assert candidate.commit.sha256 is not None
    assert target.read_bytes() == b"disk\n"

    restarted = _runtime(tmp_path).editor
    assert restarted.exec_command_line("recover #1") is True
    assert restarted.cur().buf.get_text() == "alpha   "
    assert restarted.exec_command_line("set rmtrailingws true") is True
    assert restarted.exec_command_line("set eofnewline true") is True
    assert restarted.exec_command_line("save") is True
    assert target.read_bytes() == b"alpha\n"


def test_clean_existing_save_avoids_recovery_journal_and_forced_fsync(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    target = tmp_path / "clean.txt"
    target.write_text("clean", encoding="utf-8")

    ed = _runtime(tmp_path).editor
    assert open_initial_buffer(ed, path=str(target)).ok is True
    assert ed.cur().buf.dirty is False
    calls: list[dict[str, object]] = []
    actual_writer = editor_module.write_file_bytes

    def witness(*args, **kwargs):
        calls.append(dict(kwargs))
        return actual_writer(*args, **kwargs)

    with mock.patch("micromax_editor.editor.write_file_bytes", side_effect=witness):
        info = ed.save()

    assert calls and calls[0]["fsync"] is False
    assert info["recovery_checkpointed"] is False
    assert ed.recovery_journal.discover() == []
    assert ed.recovery_journal.root.exists() is False


def test_failed_save_as_of_clean_pathless_text_is_still_recoverable(
    tmp_path: Path,
) -> None:
    target = tmp_path / "new-name.txt"
    ed = Editor()
    ed.configure_recovery_journal(RecoveryJournal(tmp_path / "recovery"))
    ed.new_buffer("notes", "draft")
    assert ed.cur().buf.dirty is False

    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("simulated disk full"),
    ):
        with pytest.raises(OSError, match="simulated disk full"):
            ed.save_as(str(target))

    assert ed.active == "notes"
    assert ed.cur().buf.path is None
    [candidate] = ed.recovery_journal.discover()
    assert candidate.target == target
    assert ed.recovery_journal.load(candidate.entry_id).editor_text() == "draft"


def test_configured_unscanned_recovery_store_is_visible_as_unknown(
    tmp_path: Path,
) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    status = ed.status_model()
    assert status["recovery_record_known"] == 0
    assert status["recovery_record_count"] == 0
    assert status["recovery_summary"] == "recovery:?"
    assert "[recovery:?]" in ed.statusline_text(40)


def test_startup_announcement_uses_filename_presence_without_target_scan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target = tmp_path / "presence.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(target, b"unsaved")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("startup must not validate recovery targets")

    monkeypatch.setattr(journal, "scan", forbidden)

    assert ed.announce_interrupted_saves() == 1
    assert "1 interrupted-save record present" in ed.messages[-1]
    status = ed.status_model()
    assert status["recovery_record_count"] == 1
    assert status["recovery_record_known"] == 1
    assert status["recovery_summary"] == "recovery:1"

    monkeypatch.setattr(journal, "presence", forbidden)
    ed.message("opened: ordinary.txt")
    assert "[recovery:1]" in ed.statusline_text(40)


def test_recovery_status_clears_after_explicit_dismissal(tmp_path: Path) -> None:
    target = tmp_path / "dismiss.txt"
    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(target, b"unsaved")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    assert ed.announce_interrupted_saves() == 1
    assert "[recovery:1]" in ed.statusline_text(40)
    assert ed.exec_command_line("recoverdismiss") is True
    assert ed.status_model()["recovery_record_count"] == 0
    assert "[recovery:" not in ed.statusline_text(80)


def test_recovery_status_exposes_bounded_lower_bound_without_repaint_scan(
    tmp_path: Path,
) -> None:
    journal = RecoveryJournal(tmp_path / "recovery", max_scan_records=1)
    journal.checkpoint(tmp_path / "one.txt", b"one", buffer_id="one")
    journal.checkpoint(tmp_path / "two.txt", b"two", buffer_id="two")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")

    assert ed.announce_interrupted_saves() == 1
    status = ed.status_model()
    assert status["recovery_record_count"] == 1
    assert status["recovery_record_truncated"] == 1
    assert status["recovery_summary"] == "recovery:1+"
    assert "[recovery:1+]" in ed.statusline_text(40)


def test_recovery_status_drops_stale_count_when_refresh_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(tmp_path / "one.txt", b"one")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer("*scratch*", "")
    assert ed.announce_interrupted_saves() == 1

    def failed_presence():
        raise RecoveryError("inventory unavailable")

    monkeypatch.setattr(journal, "presence", failed_presence)
    assert ed._refresh_recovery_presence_best_effort() == "inventory unavailable"
    status = ed.status_model()
    assert status["recovery_record_count"] == 0
    assert status["recovery_record_truncated"] == 0
    assert status["recovery_record_known"] == 0
    assert status["recovery_summary"] == "recovery:?"
    assert "[recovery:?]" in ed.statusline_text(40)


def test_recoveries_reports_target_unreadable_and_aggregate_limit(
    tmp_path: Path,
) -> None:
    target = tmp_path / "budgeted.txt"
    target.write_bytes(b"base")
    root = tmp_path / "recovery"
    RecoveryJournal(root).checkpoint(target, b"unsaved")

    ed = Editor()
    ed.configure_recovery_journal(
        RecoveryJournal(root, max_scan_comparison_bytes=1)
    )
    ed.new_buffer("*scratch*", "")

    assert ed.exec_command_line("recoveries") is True
    assert "comparison-limited=1" in ed.messages[-2]
    assert "[target unreadable]" in ed.messages[-1]


def test_successful_save_as_retires_stale_checkpoint_from_prior_failed_path(
    tmp_path: Path,
) -> None:
    first_target = tmp_path / "abandoned-name.txt"
    final_target = tmp_path / "final-name.txt"
    ed = Editor()
    ed.configure_recovery_journal(RecoveryJournal(tmp_path / "recovery"))
    ed.new_buffer("notes", "draft")

    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("simulated interrupted save-as"),
    ):
        with pytest.raises(OSError, match="interrupted save-as"):
            ed.save_as(str(first_target))

    [stale] = ed.recovery_journal.discover()
    assert stale.target == first_target
    assert ed.cur().buf.path is None

    info = ed.save_as(str(final_target))

    assert info["recovery_retired"] is True
    assert first_target.exists() is False
    assert final_target.read_text(encoding="utf-8") == "draft"
    assert ed.recovery_journal.entry_ids_for_buffer(ed.cur().save_recovery_id) == []
    assert ed.recovery_journal.discover() == []
