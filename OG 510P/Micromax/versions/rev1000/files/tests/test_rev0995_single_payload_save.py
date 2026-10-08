from __future__ import annotations

import random
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import micromax_editor.editor as editor_module
import micromax_editor.recovery_journal as recovery_module
from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor
from micromax_editor.file_access import ContainedStatResult
from micromax_editor.recovery_journal import (
    PAYLOAD_KIND_EDITOR_TEXT,
    RecoveryJournal,
)


def _save_editor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    text: str,
    *,
    filename: str = "save.txt",
) -> tuple[Editor, Path, list[bytes]]:
    path = tmp_path / filename
    path.write_bytes(text.encode("utf-8", errors="surrogatepass"))
    editor = Editor()
    editor.new_buffer(str(path), text, path=str(path))
    eb = editor.cur()
    eb.local_options.update(
        {
            "eofnewline": False,
            "rmtrailingws": False,
            "fileformat": "unix",
            "encoding": "utf-8",
            "save.atomic": False,
            "save.preserveperm": False,
            "save.checkexternal": False,
            "mkparents": False,
        }
    )
    monkeypatch.setattr(
        editor,
        "_bounded_fs_stat",
        lambda *_args, **_kwargs: ContainedStatResult(
            path=str(path),
            exists=True,
            kind="file",
            size=path.stat().st_size,
            mtime=0,
        ),
    )
    monkeypatch.setattr(
        editor,
        "_check_save_disk_fresh",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(editor, "_refresh_buffer_disk_signature", lambda *_args: None)
    monkeypatch.setattr(editor, "_push_recent_file", lambda *_args: None)
    monkeypatch.setattr(editor, "_remember_cursor_for_buffer", lambda *_args: None)
    monkeypatch.setattr(editor, "_emit_mx_hook", lambda *_args: None)

    writes: list[bytes] = []

    def write_file_bytes(target: Path, content: bytes, **_kwargs: object) -> object:
        payload = content if isinstance(content, bytes) else bytes(content)
        writes.append(payload)
        Path(target).write_bytes(payload)
        return SimpleNamespace(
            atomic=False,
            fsync=False,
            file_synced=False,
            directory_synced=False,
            write_path=Path(target),
            followed_symlink=False,
            final_mode=None,
        )

    monkeypatch.setattr(editor_module, "write_file_bytes", write_file_bytes)
    return editor, path, writes


class _JournalWitness:
    last_checkpoint_file_synced = False
    last_checkpoint_directory_synced = False
    last_dismiss_directory_synced = False

    def __init__(self) -> None:
        self.checkpoint_target: Path | None = None
        self.checkpoint_content: bytes | None = None
        self.checkpoint_commit_content: bytes | None | object = object()
        self.checkpoint_payload_kind = ""
        self.commit_content: bytes | None = None

    def checkpoint(
        self,
        target: Path,
        content: bytes,
        *,
        buffer_id: str,
        commit_content: bytes | None,
        payload_kind: str,
        metadata: dict[str, str],
    ) -> str:
        assert buffer_id
        assert metadata["encoding"]
        self.checkpoint_target = Path(target)
        self.checkpoint_content = content
        self.checkpoint_commit_content = commit_content
        self.checkpoint_payload_kind = payload_kind
        return "checkpoint-id"

    def commit_checkpoint(
        self,
        entry_id: str,
        content: bytes,
        writer: Any,
    ) -> object:
        assert entry_id == "checkpoint-id"
        assert self.checkpoint_target is not None
        self.commit_content = content
        writer(self.checkpoint_target, content)
        return SimpleNamespace(
            entry_id=entry_id,
            recovery_retired=True,
            cleanup_error=None,
        )

    def entry_ids_for_buffer(self, _buffer_id: str) -> list[str]:
        return []

    def dismiss(self, _entry_id: str) -> bool:
        return True


def test_no_cleanup_utf8_save_uses_one_text_materialization_and_no_undo_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Multiple rows force every get_text() call to allocate a joined document;
    # this catches the old second full join hidden inside the state snapshot.
    text = ("alpha🙂\n" * 150_000) + "omega"
    editor, path, writes = _save_editor(tmp_path, monkeypatch, text)
    eb = editor.cur()
    # A globally enabled cleanup option with nothing to remove must not create
    # a second full document merely to prove that it is a no-op.
    eb.local_options["rmtrailingws"] = True
    eb.buf.set_fastdirty(True)
    eb.buf.insert(Cursor(0, 0), "X")
    expected = ("X" + text).encode("utf-8")
    assert eb.buf.current_signature is None

    get_text_calls = 0
    original_get_text = eb.buf.get_text

    def counted_get_text() -> str:
        nonlocal get_text_calls
        get_text_calls += 1
        return original_get_text()

    def forbidden(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("ordinary save must not snapshot undo or document state")

    monkeypatch.setattr(eb.buf, "get_text", counted_get_text)
    monkeypatch.setattr(
        eb.buf,
        "_current_signature",
        lambda: (_ for _ in ()).throw(
            AssertionError("save must hash the already-owned UTF-8 payload")
        ),
    )
    monkeypatch.setattr(editor.undo, "snapshot", forbidden)
    monkeypatch.setattr(editor, "_snapshot_buffer_state", forbidden)

    info = editor._save_buffer(eb, recovery_checkpoint=False)

    assert info["cleanup_parts"] == []
    assert get_text_calls == 1
    assert writes == [expected]
    assert path.read_bytes() == expected
    assert eb.buf.dirty is False
    assert eb.buf.current_signature == Buffer.canonical_utf8_signature(expected)
    assert eb.buf._saved_sig == eb.buf.current_signature


def test_utf8_recovery_checkpoint_aliases_the_commit_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor, path, writes = _save_editor(tmp_path, monkeypatch, "alpha\nbeta")
    eb = editor.cur()
    eb.local_options["encoding"] = "UTF8"
    eb.buf.set_fastdirty(True)
    eb.buf.insert(Cursor(1, 4), "!")
    journal = _JournalWitness()
    editor.recovery_journal = journal  # type: ignore[assignment]
    monkeypatch.setattr(editor, "_refresh_recovery_presence_best_effort", lambda: "")

    info = editor.save()

    assert info["recovery_checkpointed"] is True
    assert journal.checkpoint_target == path.resolve()
    assert journal.checkpoint_payload_kind == PAYLOAD_KIND_EDITOR_TEXT
    assert journal.checkpoint_commit_content is None
    assert journal.checkpoint_content is journal.commit_content
    assert journal.checkpoint_content is writes[0]
    assert writes == [b"alpha\nbeta!"]
    assert eb.buf.dirty is False


def test_normalizing_save_keeps_exact_recovery_text_and_reuses_before_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor, _path, writes = _save_editor(tmp_path, monkeypatch, "alpha   ")
    eb = editor.cur()
    eb.local_options["rmtrailingws"] = True
    eb.local_options["eofnewline"] = True
    eb.buf.set_fastdirty(True)
    eb.buf.insert(Cursor(0, len("alpha   ")), "beta  ")
    original = "alpha   beta  "
    journal = _JournalWitness()
    editor.recovery_journal = journal  # type: ignore[assignment]
    monkeypatch.setattr(editor, "_refresh_recovery_presence_best_effort", lambda: "")

    get_text_calls = 0
    original_get_text = eb.buf.get_text

    def counted_get_text() -> str:
        nonlocal get_text_calls
        get_text_calls += 1
        return original_get_text()

    snapshot_text_arguments: list[str | None] = []
    original_snapshot = editor._snapshot_buffer_state

    def counted_snapshot(
        current: Any,
        *,
        text: str | None = None,
    ) -> tuple[str, list[Any], list[Any], list[int], int]:
        snapshot_text_arguments.append(text)
        return original_snapshot(current, text=text)

    monkeypatch.setattr(eb.buf, "get_text", counted_get_text)
    monkeypatch.setattr(editor, "_snapshot_buffer_state", counted_snapshot)

    info = editor.save()

    assert info["cleanup_parts"] == ["trim trailing whitespace", "add eof newline"]
    assert get_text_calls == 1
    assert snapshot_text_arguments == [original, "alpha   beta\n"]
    assert journal.checkpoint_content == original.encode("utf-8")
    assert journal.checkpoint_commit_content == b"alpha   beta\n"
    assert journal.checkpoint_content is not journal.checkpoint_commit_content
    assert writes == [b"alpha   beta\n"]
    assert eb.buf.get_text() == "alpha   beta\n"
    assert eb.buf.dirty is False

    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == original
    assert eb.buf.dirty is True


def test_cleanup_failure_during_first_mutation_restores_exact_pre_save_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor, path, writes = _save_editor(tmp_path, monkeypatch, "alpha   ")
    eb = editor.cur()
    eb.local_options["rmtrailingws"] = True
    eb.buf.set_fastdirty(True)
    eb.buf.insert(Cursor(0, len("alpha   ")), "beta  ")
    before_text = eb.buf.get_text()
    before_dirty = eb.buf.dirty
    before_fastdirty = eb.buf.fastdirty
    before_version = eb.buf.version
    before_saved = eb.buf._saved_sig
    before_current = eb.buf.current_signature
    before_undo = editor.undo.snapshot()

    original_set_text = eb.buf.set_text
    calls = 0

    def fail_after_first_mutation(value: str) -> None:
        nonlocal calls
        calls += 1
        original_set_text(value)
        if calls == 1:
            raise RuntimeError("simulated cleanup mutation failure")

    monkeypatch.setattr(eb.buf, "set_text", fail_after_first_mutation)

    with pytest.raises(RuntimeError, match="cleanup mutation failure"):
        editor._save_buffer(eb, recovery_checkpoint=False)

    assert calls == 2  # attempted cleanup, then exact rollback
    assert writes == []
    assert path.read_text(encoding="utf-8") == "alpha   "
    assert eb.buf.get_text() == before_text
    assert eb.buf.dirty is before_dirty
    assert eb.buf.fastdirty is before_fastdirty
    assert eb.buf.version == before_version
    assert eb.buf._saved_sig == before_saved
    assert eb.buf.current_signature == before_current
    assert editor.undo.snapshot() == before_undo


def test_dos_save_does_not_adopt_disk_bytes_as_the_lf_buffer_signature(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor, path, writes = _save_editor(tmp_path, monkeypatch, "alpha\nbeta")
    eb = editor.cur()
    eb.local_options["fileformat"] = "dos"
    eb.buf.set_fastdirty(True)
    eb.buf.insert(Cursor(1, 4), "!")
    expected_text = "alpha\nbeta!"
    disk_payload = b"alpha\r\nbeta!"
    signature_calls = 0
    original_signature = eb.buf._current_signature

    def counted_signature() -> tuple[int, str]:
        nonlocal signature_calls
        signature_calls += 1
        return original_signature()

    monkeypatch.setattr(eb.buf, "_current_signature", counted_signature)

    editor._save_buffer(eb, recovery_checkpoint=False)

    assert writes == [disk_payload]
    assert path.read_bytes() == disk_payload
    assert signature_calls == 1
    assert eb.buf._saved_sig == Buffer(expected_text)._current_signature()
    assert eb.buf._saved_sig != Buffer.canonical_utf8_signature(disk_payload)
    assert eb.buf.dirty is False


def test_canonical_utf8_signature_matches_text_signature_randomly() -> None:
    rng = random.Random(995)
    alphabet = "abαβ🙂\n\t \u0000"
    for _ in range(400):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randrange(256)))
        buffer = Buffer(text)
        payload = buffer.get_text().encode("utf-8")
        assert Buffer.canonical_utf8_signature(payload) == buffer._current_signature()


def test_recovery_checkpoint_hashes_identical_payload_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = (b"abcdef" * 200_000) + b"!"
    hashed: list[bytes] = []
    original_sha256 = recovery_module._sha256

    def counted_sha256(data: bytes) -> str:
        hashed.append(data)
        return original_sha256(data)

    written: list[bytes] = []
    journal = RecoveryJournal(
        tmp_path / "recovery",
        journal_writer=lambda _path, data: written.append(data),
    )
    monkeypatch.setattr(recovery_module, "_sha256", counted_sha256)

    journal.checkpoint(tmp_path / "target.txt", payload, commit_content=None)

    assert sum(item is payload for item in hashed) == 1
    assert len(written) == 1
