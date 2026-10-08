from __future__ import annotations

from pathlib import Path

import pytest

from micromax_editor.buffer import Buffer
from micromax_editor.editor import Editor
from micromax_editor.recovery_journal import (
    PAYLOAD_KIND_EDITOR_TEXT,
    RecoveryJournal,
)


@pytest.mark.parametrize(
    "text",
    (
        "",
        "one line",
        "trailing newline\n",
        "alpha\r\nbeta\rgamma",
        "snowman: ☃\nsurrogate: \udcff",
        "x" * (1024 * 1024 + 17),
    ),
)
def test_line_vector_signature_matches_canonical_document_signature(text: str) -> None:
    buffer = Buffer(text)

    assert buffer.line_vector_signature(buffer.snapshot_lines()) == buffer._saved_sig


def test_recovery_open_history_reuses_unchanged_line_objects_without_full_join(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "large-recovery.txt"
    source_lines = tuple(
        f"row-{index:05d}-" + (chr(97 + index % 26) * 96)
        for index in range(4096)
    )
    changed_index = len(source_lines) // 2
    recovered_lines = list(source_lines)
    recovered_lines[changed_index] = "RECOVERED-" + recovered_lines[changed_index]
    source = "\n".join(source_lines)
    recovered = "\n".join(recovered_lines)
    target.write_text(source, encoding="utf-8")

    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(
        target,
        recovered.encode("utf-8"),
        buffer_id="large-crash",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(str(target), source, path=str(target))
    eb = ed.buffers[name]
    # Keep dirty tracking on the O(1) large-buffer policy so a forbidden
    # get_text witness specifically covers recovery history construction.
    eb.buf.fastdirty = True
    eb.buf.dirty = False
    before = eb.buf.snapshot_lines()

    original_get_text = eb.buf.get_text

    def forbidden_join() -> str:
        raise AssertionError("recovery history joined a complete live document")

    monkeypatch.setattr(eb.buf, "get_text", forbidden_join)

    info = ed.open_interrupted_save("#1")

    assert info["buffer"] == name
    after = eb.buf.snapshot_lines()
    assert after[changed_index] == recovered_lines[changed_index]
    assert after[changed_index] is not before[changed_index]
    assert all(
        after[index] is before[index]
        for index in range(len(before))
        if index != changed_index
    )

    row = ed.undo.peek_undo()
    assert row is not None
    assert row.description == "open interrupted save"
    expected_charge = (
        sum(len(line) for line in before)
        + (len(before) - 1)
        + (len(after) - 1)
        + len(after[changed_index])
    )
    assert row.retained_text[0].byte_count == expected_charge
    assert expected_charge < len(source) + len(recovered)

    assert ed.undo.undo() is True
    assert eb.buf.snapshot_lines() == before
    assert eb.buf.dirty is False
    assert eb.interrupted_save_entry_id is None
    assert ed.undo.redo() is True
    assert eb.buf.snapshot_lines() == tuple(recovered_lines)
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id == info["entry_id"]

    # Saving establishes a new baseline.  Recovery history must compare its
    # retained generation signature with that current baseline, even while the
    # buffer stays in fastdirty mode, and replay must still avoid ``get_text``.
    monkeypatch.setattr(eb.buf, "get_text", original_get_text)
    assert ed.exec_command_line("save") is True
    assert eb.buf.dirty is False
    monkeypatch.setattr(eb.buf, "get_text", forbidden_join)

    assert ed.undo.undo() is True
    assert eb.buf.snapshot_lines() == before
    assert eb.buf.dirty is True
    assert ed.undo.redo() is True
    assert eb.buf.snapshot_lines() == tuple(recovered_lines)
    assert eb.buf.dirty is False


def test_aggregate_transactions_restore_recovery_authority_sidecars() -> None:
    ed = Editor()
    ed.new_buffer("main", "stable text")
    eb = ed.cur()
    original = (
        eb.save_recovery_id,
        eb.interrupted_save_entry_id,
        eb.interrupted_save_target,
        eb.interrupted_save_requires_force,
    )

    with ed._first_write_buffer_transaction() as journal:
        eb.save_recovery_id = "crashed-buffer"
        eb.interrupted_save_entry_id = "a" * 64
        eb.interrupted_save_target = "/tmp/recovered-target"
        eb.interrupted_save_requires_force = True

    before, after = ed._finish_first_write_buffer_transaction(journal)
    assert ed._macro_replay_has_undoable_change(before, after) is True
    before_row = before.buffers[0]
    after_row = after.buffers[0]
    assert before_row.line_vector is after_row.line_vector
    assert before_row.line_vector == ("stable text",)

    ed._record_buffer_transaction_snapshot(
        before,
        after,
        "recovery sidecar transaction",
    )
    assert ed.undo.depth() == 1

    assert ed.undo.undo() is True
    assert (
        eb.save_recovery_id,
        eb.interrupted_save_entry_id,
        eb.interrupted_save_target,
        eb.interrupted_save_requires_force,
    ) == original

    assert ed.undo.redo() is True
    assert eb.save_recovery_id == "crashed-buffer"
    assert eb.interrupted_save_entry_id == "a" * 64
    assert eb.interrupted_save_target == "/tmp/recovered-target"
    assert eb.interrupted_save_requires_force is True



@pytest.mark.parametrize(
    "name",
    (
        "recoveries",
        "recover",
        "recovermode",
        "recovertemps",
        "recoverclean",
        "recoverdismiss",
    ),
)
def test_recovery_disposition_commands_are_macro_recording_boundaries(
    name: str,
) -> None:
    ed = Editor()

    assert ed._macro_command_recordability_kind(name) == "exact"
    assert ed._macro_should_record_command_name(name) is False


def test_successful_recovery_open_is_not_absorbed_into_aggregate_macro_history(
    tmp_path: Path,
) -> None:
    target = tmp_path / "macro-recovery.txt"
    target.write_text("disk", encoding="utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(
        target,
        b"recovered",
        buffer_id="macro-recovery",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer(str(target), "disk", path=str(target))

    assert ed.exec_command_line("macro record recovery-review") is True
    assert ed.exec_command_line("recover #1") is True
    assert ed._macro_buffer == []
    assert ed.undo.peek_undo() is not None
    assert ed.undo.peek_undo().description == "open interrupted save"
    assert ed.exec_command_line("macro stop") is True
    assert "recovery-review" not in ed.macros

def test_recovery_history_treats_transient_and_known_unusable_entry_checks_differently(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "entry-check.txt"
    target.write_text("disk", encoding="utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(
        target,
        b"recovered",
        buffer_id="entry-check",
        payload_kind=PAYLOAD_KIND_EDITOR_TEXT,
        metadata={"encoding": "utf-8", "fileformat": "unix"},
    )

    ed = Editor()
    ed.configure_recovery_journal(journal)
    name = ed.new_buffer(str(target), "disk", path=str(target))
    eb = ed.buffers[name]
    assert ed.open_interrupted_save("#1")["entry_id"] == entry_id
    assert ed.undo.undo() is True

    original_entry_present = journal.entry_present

    def transient_failure(_entry_id: str) -> bool:
        from micromax_editor.recovery_journal import RecoveryError

        raise RecoveryError("temporary inventory failure")

    monkeypatch.setattr(journal, "entry_present", transient_failure)
    assert ed.undo.redo() is True
    assert eb.buf.get_text() == "recovered"
    assert eb.interrupted_save_entry_id == entry_id

    assert ed.undo.undo() is True
    monkeypatch.setattr(journal, "entry_present", original_entry_present)
    record = journal._entry_path(entry_id)
    record.unlink()
    try:
        record.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are unavailable on this platform")

    assert ed.undo.redo() is True
    assert eb.buf.get_text() == "recovered"
    assert eb.buf.dirty is True
    assert eb.interrupted_save_entry_id is None
    assert eb.interrupted_save_target is None
    assert eb.interrupted_save_requires_force is False
