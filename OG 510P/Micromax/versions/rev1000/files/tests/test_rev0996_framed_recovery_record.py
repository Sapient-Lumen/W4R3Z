from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest

import micromax_editor.recovery_journal as recovery_module
from micromax_editor.recovery_journal import (
    PAYLOAD_KIND_BYTES,
    Fingerprint,
    RecoveryConflictError,
    RecoveryCorruptError,
    RecoveryJournal,
    RecoveryStatus,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_measurement_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_framed_recovery.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_framed_recovery",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _legacy_record(
    journal: RecoveryJournal,
    target: Path,
    payload: bytes,
    *,
    buffer_id: str = "legacy-buffer",
) -> tuple[str, bytes]:
    canonical = recovery_module._canonical_target(target)
    entry_id = journal._id(canonical, buffer_id)
    body: dict[str, object] = {
        "schema": recovery_module.SCHEMA,
        "entry_id": entry_id,
        "buffer_id": buffer_id,
        "target": str(canonical),
        "created_ns": 1,
        "base": Fingerprint(False).to_json(),
        # Deliberately omit the separate commit field to exercise rev0959
        # compatibility, where recovery payload and intended bytes were one.
        "payload_kind": PAYLOAD_KIND_BYTES,
        "metadata": {"encoding": "utf-8"},
        "payload": {
            "encoding": "base64",
            "size": len(payload),
            "sha256": recovery_module._sha256(payload),
            "data": base64.b64encode(payload).decode("ascii"),
        },
    }
    record = dict(body)
    record["record_sha256"] = recovery_module._sha256(
        recovery_module._canonical_json(body)
    )
    return entry_id, recovery_module._canonical_json(record) + b"\n"


def _framed_payload_offset(raw: bytes) -> int:
    magic = recovery_module._FRAMED_RECORD_MAGIC
    assert raw.startswith(magic)
    length_at = len(magic)
    length_to = length_at + recovery_module._FRAMED_HEADER_LENGTH.size
    (header_size,) = recovery_module._FRAMED_HEADER_LENGTH.unpack(
        raw[length_at:length_to]
    )
    return length_to + header_size


def test_checkpoint_writes_one_raw_tail_without_base64_copy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = bytes(range(256)) * 4096
    journal = RecoveryJournal(
        tmp_path / "recovery",
        max_payload_bytes=len(payload),
    )

    def forbidden(*_args: object, **_kwargs: object) -> bytes:
        raise AssertionError("v2 checkpoint must not base64-encode its payload")

    monkeypatch.setattr(recovery_module.base64, "b64encode", forbidden)
    entry_id = journal.checkpoint(
        tmp_path / "document.bin",
        payload,
        buffer_id="binary",
        metadata={"encoding": "binary"},
    )

    raw = journal._entry_path(entry_id).read_bytes()
    payload_at = _framed_payload_offset(raw)
    assert raw[payload_at:] == payload
    assert len(raw) - len(payload) < 4096
    assert journal.payload(entry_id) == payload
    candidate = journal.inspect(entry_id)
    assert candidate.payload_size == len(payload)
    assert candidate.payload_sha256 == recovery_module._sha256(payload)
    assert candidate.metadata["encoding"] == "binary"
    assert candidate.status is RecoveryStatus.RECOVERABLE


def test_legacy_json_base64_record_remains_loadable(tmp_path: Path) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    payload = b"legacy\x00payload\xff"
    entry_id, data = _legacy_record(journal, tmp_path / "legacy.bin", payload)
    journal.root.mkdir(parents=True)
    journal._entry_path(entry_id).write_bytes(data)

    snapshot = journal.load(entry_id)

    assert snapshot.payload == payload
    assert snapshot.candidate.commit == Fingerprint.for_bytes(payload)
    assert snapshot.candidate.payload_kind == PAYLOAD_KIND_BYTES
    assert snapshot.candidate.metadata == {"encoding": "utf-8"}


def test_framed_header_and_raw_payload_have_independent_integrity_checks(
    tmp_path: Path,
) -> None:
    header_journal = RecoveryJournal(tmp_path / "header-recovery")
    header_id = header_journal.checkpoint(tmp_path / "header.txt", b"header")
    header_path = header_journal._entry_path(header_id)
    header_raw = bytearray(header_path.read_bytes())
    marker = b'"payload":{"encoding":"raw-tail","sha256":"'
    digest_at = header_raw.index(marker) + len(marker)
    header_raw[digest_at] = (
        ord("0") if header_raw[digest_at] != ord("0") else ord("1")
    )
    header_path.write_bytes(header_raw)
    with pytest.raises(RecoveryCorruptError, match="checksum mismatch"):
        header_journal.payload(header_id)

    payload_journal = RecoveryJournal(tmp_path / "payload-recovery")
    payload_id = payload_journal.checkpoint(tmp_path / "payload.txt", b"payload")
    payload_path = payload_journal._entry_path(payload_id)
    payload_raw = bytearray(payload_path.read_bytes())
    payload_raw[-1] ^= 1
    payload_path.write_bytes(payload_raw)
    with pytest.raises(RecoveryCorruptError, match="payload integrity"):
        payload_journal.payload(payload_id)


def test_immediate_commit_reuses_small_inode_bound_checkpoint_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"x" * (2 * 1024 * 1024)
    target = tmp_path / "document.bin"
    journal = RecoveryJournal(
        tmp_path / "recovery",
        max_payload_bytes=len(payload),
    )
    entry_id = journal.checkpoint(target, payload, buffer_id="save")
    witness = journal._checkpoint_witnesses[entry_id]
    assert not hasattr(witness.authority, "payload")

    def forbidden(_entry_id: str) -> object:
        raise AssertionError("unchanged immediate commit must not reread the payload")

    monkeypatch.setattr(journal, "_read", forbidden)
    outcome = journal.commit_checkpoint(
        entry_id,
        payload,
        lambda path, data: Path(path).write_bytes(data),
    )

    assert outcome.committed is True
    assert target.read_bytes() == payload
    assert entry_id not in journal._checkpoint_witnesses


def test_restart_authority_paths_stream_v2_payload_without_materializing_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"streamed authority" * (256 * 1024)
    root = tmp_path / "recovery"
    target = tmp_path / "document.bin"
    entry_id = RecoveryJournal(
        root,
        max_payload_bytes=len(payload),
    ).checkpoint(target, payload, buffer_id="restart")
    restarted = RecoveryJournal(root, max_payload_bytes=len(payload))
    exact_labels: list[str] = []
    real_read_exact = recovery_module._read_exact

    def guarded_read_exact(
        stream: object,
        size: int,
        *,
        label: str,
    ) -> bytes:
        exact_labels.append(label)
        if label == "recovery payload":
            raise AssertionError("authority-only v2 path materialized the payload")
        return real_read_exact(stream, size, label=label)  # type: ignore[arg-type]

    def forbidden_full_read(_entry_id: str) -> object:
        raise AssertionError("authority-only operation called the payload reader")

    monkeypatch.setattr(recovery_module, "_read_exact", guarded_read_exact)
    monkeypatch.setattr(restarted, "_read", forbidden_full_read)

    candidate = restarted.inspect(entry_id)
    outcome = restarted.commit_checkpoint(
        entry_id,
        payload,
        lambda path, data: Path(path).write_bytes(data),
    )

    assert candidate.payload_size == len(payload)
    assert candidate.payload_sha256 == recovery_module._sha256(payload)
    assert outcome.committed is True
    assert target.read_bytes() == payload
    assert "recovery header" in exact_labels
    assert "recovery payload" not in exact_labels


def test_changed_checkpoint_inode_or_bytes_invalidates_fast_commit(
    tmp_path: Path,
) -> None:
    payload = b"trusted payload"
    target = tmp_path / "document.bin"
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(target, payload, buffer_id="save")
    record = journal._entry_path(entry_id)
    raw = bytearray(record.read_bytes())
    raw[-1] ^= 1
    replacement = record.with_suffix(".replacement")
    replacement.write_bytes(raw)
    replacement.replace(record)
    writes: list[bytes] = []

    with pytest.raises(RecoveryCorruptError, match="payload integrity"):
        journal.commit_checkpoint(
            entry_id,
            payload,
            lambda _path, data: writes.append(data),
        )

    assert writes == []
    assert target.exists() is False
    assert entry_id not in journal._checkpoint_witnesses


def test_same_inode_checkpoint_mutation_invalidates_fast_commit(
    tmp_path: Path,
) -> None:
    payload = b"same inode mutation"
    target = tmp_path / "document.bin"
    journal = RecoveryJournal(tmp_path / "recovery")
    entry_id = journal.checkpoint(target, payload, buffer_id="save")
    record = journal._entry_path(entry_id)
    inode_before = record.stat().st_ino
    with record.open("r+b") as handle:
        handle.seek(-1, 2)
        final = handle.read(1)
        handle.seek(-1, 2)
        handle.write(bytes([final[0] ^ 1]))
        handle.flush()
        recovery_module.os.fsync(handle.fileno())
    # Force visible metadata drift even on filesystems with coarse timestamps;
    # the inode itself deliberately remains unchanged.
    changed = record.stat()
    recovery_module.os.utime(
        record,
        ns=(changed.st_atime_ns, changed.st_mtime_ns + 1_000_000_000),
    )
    assert record.stat().st_ino == inode_before
    writes: list[bytes] = []

    with pytest.raises(RecoveryCorruptError, match="payload integrity"):
        journal.commit_checkpoint(
            entry_id,
            payload,
            lambda _path, data: writes.append(data),
        )

    assert writes == []
    assert target.exists() is False
    assert entry_id not in journal._checkpoint_witnesses


@pytest.mark.parametrize(
    "stage, message",
    [
        (
            "after_checkpoint_directory_sync",
            "published recovery inode does not match the fsynced temp",
        ),
        (
            "after_checkpoint_write",
            "recovery record changed after checkpoint publication",
        ),
    ],
)
def test_publication_race_never_inherits_fast_commit_authority(
    tmp_path: Path,
    stage: str,
    message: str,
) -> None:
    root = tmp_path / "recovery"
    target = tmp_path / "document.bin"
    payload = b"same bytes, different published inode"
    replaced = False

    def replace_published_record(current_stage: str) -> None:
        nonlocal replaced
        if current_stage != stage or replaced:
            return
        record = next(root.glob("*.recovery.json"))
        replacement = root / "replacement"
        replacement.write_bytes(record.read_bytes())
        replacement.replace(record)
        replaced = True

    journal = RecoveryJournal(root, fault=replace_published_record)
    entry_id = journal._id(
        recovery_module._canonical_target(target),
        "race",
    )

    with pytest.raises(RecoveryConflictError, match=message):
        journal.checkpoint(target, payload, buffer_id="race")

    assert replaced is True
    assert entry_id not in journal._checkpoint_witnesses
    # The byte-identical replacement remains a valid recovery record; only the
    # unearned in-memory shortcut is refused.
    assert RecoveryJournal(root).payload(entry_id) == payload


def test_framed_header_is_small_canonical_json(tmp_path: Path) -> None:
    journal = RecoveryJournal(tmp_path / "recovery")
    payload = b"abc"
    entry_id = journal.checkpoint(tmp_path / "document.txt", payload)
    raw = journal._entry_path(entry_id).read_bytes()
    payload_at = _framed_payload_offset(raw)
    length_at = len(recovery_module._FRAMED_RECORD_MAGIC)
    length_to = length_at + recovery_module._FRAMED_HEADER_LENGTH.size
    header = json.loads(raw[length_to:payload_at])

    assert header["schema"] == recovery_module.FRAMED_SCHEMA
    assert header["payload"] == {
        "encoding": "raw-tail",
        "sha256": recovery_module._sha256(payload),
        "size": len(payload),
    }
    assert "data" not in header["payload"]


def test_framed_recovery_measurement_pins_exact_memory_shape() -> None:
    module = _load_measurement_tool()
    report = module.build_report(payload_bytes=256 * 1024, samples=1)

    assert report["schema"] == module.SCHEMA
    legacy = report["legacy_json_base64"]
    product = report["framed_raw_tail"]
    comparison = report["comparison"]
    assert comparison["both_round_trip_exact"] is True
    assert product["schema"] == recovery_module.FRAMED_SCHEMA
    assert product["legacy_read_compatible"] is True
    assert product["authority_paths_materialize_payload"] is False
    assert product["immediate_commit_rereads_payload"] is False
    assert product["record_bytes_median"] < legacy["record_bytes_median"]
    assert product["record_bytes_median"] < report["payload_bytes"] + 4096
    assert (
        product["checkpoint"]["traced_peak_bytes_median"]
        < legacy["checkpoint"]["traced_peak_bytes_median"]
    )
    assert (
        product["load"]["traced_peak_bytes_median"]
        < legacy["load"]["traced_peak_bytes_median"]
    )
    assert (
        product["authority_inspect"]["traced_peak_bytes_median"]
        < product["load"]["traced_peak_bytes_median"]
    )
