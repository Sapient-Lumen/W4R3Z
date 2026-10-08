from __future__ import annotations

"""Measure rev0996 recovery framing against the retired JSON/base64 path."""

import argparse
import base64
import gc
import json
from pathlib import Path
import statistics
import tempfile
import time
import tracemalloc
from typing import Callable, TypeVar

from micromax_editor.recovery_journal import (
    FRAMED_SCHEMA,
    PAYLOAD_KIND_BYTES,
    Fingerprint,
    RecoveryJournal,
)
import micromax_editor.recovery_journal as recovery_module

SCHEMA = "micromax.framed-recovery-measurement.v1"
T = TypeVar("T")


def _measure(call: Callable[[], T]) -> tuple[T, float, int, int]:
    gc.collect()
    tracemalloc.start()
    started = time.perf_counter()
    try:
        result = call()
        elapsed = time.perf_counter() - started
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, elapsed, int(current), int(peak)


def _summary(rows: list[tuple[float, int, int]]) -> dict[str, object]:
    return {
        "samples": len(rows),
        "elapsed_seconds_median": statistics.median(row[0] for row in rows),
        "traced_current_bytes_median": int(
            statistics.median(row[1] for row in rows)
        ),
        "traced_peak_bytes_median": int(
            statistics.median(row[2] for row in rows)
        ),
    }


def _legacy_record_bytes(
    target: Path,
    payload: bytes,
    *,
    buffer_id: str = "measurement",
) -> tuple[str, bytes]:
    canonical = recovery_module._canonical_target(target)
    material = (str(canonical) + "\0" + buffer_id).encode(
        "utf-8",
        "surrogatepass",
    )
    entry_id = recovery_module.hashlib.sha256(material).hexdigest()
    payload_sha256 = recovery_module._sha256(payload)
    body: dict[str, object] = {
        "schema": recovery_module.SCHEMA,
        "entry_id": entry_id,
        "buffer_id": buffer_id,
        "target": str(canonical),
        "created_ns": 1,
        "base": Fingerprint(False).to_json(),
        "commit": Fingerprint(True, len(payload), payload_sha256).to_json(),
        "payload_kind": PAYLOAD_KIND_BYTES,
        "metadata": {"encoding": "utf-8"},
        "payload": {
            "encoding": "base64",
            "size": len(payload),
            "sha256": payload_sha256,
            "data": base64.b64encode(payload).decode("ascii"),
        },
    }
    record = dict(body)
    record["record_sha256"] = recovery_module._sha256(
        recovery_module._canonical_json(body)
    )
    return entry_id, recovery_module._canonical_json(record) + b"\n"


def _legacy_checkpoint(path: Path, target: Path, payload: bytes) -> int:
    _entry_id, data = _legacy_record_bytes(target, payload)
    recovery_module._private_atomic_write(path, data)
    return len(data)


def _legacy_load(path: Path, payload_bytes: int) -> bytes:
    raw = path.read_bytes()
    value = recovery_module._strict_json(raw)
    checksum = value.pop("record_sha256")
    if checksum != recovery_module._sha256(recovery_module._canonical_json(value)):
        raise AssertionError("legacy checksum mismatch")
    envelope = value["payload"]
    if not isinstance(envelope, dict):
        raise AssertionError("legacy payload envelope missing")
    encoded = envelope["data"]
    if not isinstance(encoded, str):
        raise AssertionError("legacy payload text missing")
    decoded = base64.b64decode(encoded, validate=True)
    if len(decoded) != payload_bytes:
        raise AssertionError("legacy payload size mismatch")
    if recovery_module._sha256(decoded) != envelope["sha256"]:
        raise AssertionError("legacy payload digest mismatch")
    return decoded


def _percent_reduction(old: int | float, new: int | float) -> float:
    if old <= 0:
        return 0.0
    return round((1.0 - (float(new) / float(old))) * 100.0, 3)


def build_report(
    *,
    payload_bytes: int = 16 * 1024 * 1024,
    samples: int = 3,
) -> dict[str, object]:
    if payload_bytes <= 0:
        raise ValueError("payload_bytes must be positive")
    if samples <= 0:
        raise ValueError("samples must be positive")
    seed = b"0123456789abcdef"
    payload = (seed * ((payload_bytes + len(seed) - 1) // len(seed)))[
        :payload_bytes
    ]

    legacy_checkpoint_rows: list[tuple[float, int, int]] = []
    legacy_load_rows: list[tuple[float, int, int]] = []
    product_checkpoint_rows: list[tuple[float, int, int]] = []
    product_load_rows: list[tuple[float, int, int]] = []
    product_inspect_rows: list[tuple[float, int, int]] = []
    product_restart_commit_rows: list[tuple[float, int, int]] = []
    product_transaction_rows: list[tuple[float, int, int]] = []
    legacy_record_sizes: list[int] = []
    product_record_sizes: list[int] = []

    for _sample in range(samples):
        with tempfile.TemporaryDirectory(prefix="mx-recovery-measure-") as raw:
            base = Path(raw)
            target = base / "document.bin"

            legacy_root = base / "legacy"
            legacy_root.mkdir()
            legacy_path = legacy_root / ("a" * 64 + ".recovery.json")
            legacy_size, elapsed, current, peak = _measure(
                lambda: _legacy_checkpoint(legacy_path, target, payload)
            )
            legacy_record_sizes.append(legacy_size)
            legacy_checkpoint_rows.append((elapsed, current, peak))
            decoded, elapsed, current, peak = _measure(
                lambda: _legacy_load(legacy_path, payload_bytes)
            )
            if decoded != payload:
                raise AssertionError("legacy measurement did not round-trip")
            legacy_load_rows.append((elapsed, current, peak))
            del decoded

            journal = RecoveryJournal(
                base / "product",
                max_payload_bytes=payload_bytes,
            )
            entry_id, elapsed, current, peak = _measure(
                lambda: journal.checkpoint(target, payload)
            )
            product_checkpoint_rows.append((elapsed, current, peak))
            product_record_sizes.append(journal._entry_path(entry_id).stat().st_size)
            loaded, elapsed, current, peak = _measure(lambda: journal.payload(entry_id))
            if loaded != payload:
                raise AssertionError("framed measurement did not round-trip")
            product_load_rows.append((elapsed, current, peak))
            del loaded

            restarted = RecoveryJournal(
                base / "product",
                max_payload_bytes=payload_bytes,
            )
            candidate, elapsed, current, peak = _measure(
                lambda: restarted.inspect(entry_id)
            )
            if candidate.payload_size != payload_bytes:
                raise AssertionError("framed authority inspection lost payload size")
            product_inspect_rows.append((elapsed, current, peak))

            def restart_commit() -> object:
                return restarted.commit_checkpoint(
                    entry_id,
                    payload,
                    lambda path, data: Path(path).write_bytes(data),
                )

            restart_outcome, elapsed, current, peak = _measure(restart_commit)
            if not (
                getattr(restart_outcome, "committed", False)
                and getattr(restart_outcome, "recovery_retired", False)
                and target.read_bytes() == payload
            ):
                raise AssertionError("restart-time framed commit was not exact")
            product_restart_commit_rows.append((elapsed, current, peak))

            transaction_target = base / "transaction.bin"
            transaction_journal = RecoveryJournal(
                base / "transaction-recovery",
                max_payload_bytes=payload_bytes,
            )

            def transaction() -> object:
                return transaction_journal.save_with_recovery(
                    transaction_target,
                    payload,
                    lambda path, data: Path(path).write_bytes(data),
                )

            outcome, elapsed, current, peak = _measure(transaction)
            if not (
                getattr(outcome, "committed", False)
                and getattr(outcome, "recovery_retired", False)
                and transaction_target.read_bytes() == payload
            ):
                raise AssertionError("framed save transaction was not exact")
            product_transaction_rows.append((elapsed, current, peak))

    legacy_checkpoint = _summary(legacy_checkpoint_rows)
    legacy_load = _summary(legacy_load_rows)
    product_checkpoint = _summary(product_checkpoint_rows)
    product_load = _summary(product_load_rows)
    product_inspect = _summary(product_inspect_rows)
    product_restart_commit = _summary(product_restart_commit_rows)
    product_transaction = _summary(product_transaction_rows)
    legacy_record = int(statistics.median(legacy_record_sizes))
    product_record = int(statistics.median(product_record_sizes))

    return {
        "schema": SCHEMA,
        "payload_bytes": payload_bytes,
        "legacy_json_base64": {
            "record_bytes_median": legacy_record,
            "record_expansion_ratio": legacy_record / payload_bytes,
            "checkpoint": legacy_checkpoint,
            "load": legacy_load,
        },
        "framed_raw_tail": {
            "schema": FRAMED_SCHEMA,
            "record_bytes_median": product_record,
            "record_expansion_ratio": product_record / payload_bytes,
            "checkpoint": product_checkpoint,
            "load": product_load,
            "authority_inspect": product_inspect,
            "restart_commit": product_restart_commit,
            "checkpoint_then_commit": product_transaction,
            "legacy_read_compatible": True,
            "authority_paths_materialize_payload": False,
            "immediate_commit_rereads_payload": False,
        },
        "comparison": {
            "record_bytes_reduction_percent": _percent_reduction(
                legacy_record,
                product_record,
            ),
            "checkpoint_peak_reduction_percent": _percent_reduction(
                int(legacy_checkpoint["traced_peak_bytes_median"]),
                int(product_checkpoint["traced_peak_bytes_median"]),
            ),
            "load_peak_reduction_percent": _percent_reduction(
                int(legacy_load["traced_peak_bytes_median"]),
                int(product_load["traced_peak_bytes_median"]),
            ),
            "both_round_trip_exact": True,
        },
        "method": {
            "memory": (
                "CPython tracemalloc starts after the immutable source payload exists; "
                "results are not RSS or total-memory bounds"
            ),
            "legacy": (
                "the retired canonical JSON/base64 construction, private atomic write, "
                "whole-record read, JSON decode, and validated base64 decode"
            ),
            "product": (
                "one compact canonical JSON header plus raw payload tail, private atomic "
                "part writes, bounded authority hashing, exact payload load, and an "
                "inode-bound immediate commit witness"
            ),
            "timing": "local elapsed attribution only; not a portable benchmark",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--payload-bytes",
        type=int,
        default=16 * 1024 * 1024,
    )
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = build_report(payload_bytes=args.payload_bytes, samples=args.samples)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
