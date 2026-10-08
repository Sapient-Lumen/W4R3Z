#!/usr/bin/env python3
"""Measure the rev0995 single-payload save path and a complete huge-line loop.

This is a local attribution witness, not a portable latency or total-memory
benchmark.  The legacy reference reproduces the pre-rev0995 sequence of full
text joins/encodes used by one ordinary fast-dirty UTF-8 save.  The product lane
uses the already materialized commit payload for recovery identity and the clean
baseline.  The journey then exercises viewport, literal search, cursor motion,
edit, Undo/Redo, and save on one very long logical line.

Examples:
  PYTHONPATH=src python tools/measure_single_payload_save.py
  PYTHONPATH=src python tools/measure_single_payload_save.py \
    --chars 8000000 --samples 3 \
    --json-out .artifacts/rev0995-single-payload-save.json
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import micromax_editor.editor as editor_module
import micromax_editor.recovery_journal as recovery_module
from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor
from micromax_editor.file_access import ContainedStatResult
from micromax_editor.recovery_journal import PAYLOAD_KIND_EDITOR_TEXT, RecoveryJournal

SCHEMA = "micromax.single-payload-save-measurement.v1"


def _measure_preparation_once(mode: str, text: str) -> dict[str, Any]:
    buffer = Buffer(text)
    buffer.set_fastdirty(True)
    buffer.touch_external()
    calls = 0
    original_get_text = buffer.get_text

    def counted_get_text() -> str:
        nonlocal calls
        calls += 1
        return original_get_text()

    buffer.get_text = counted_get_text  # type: ignore[method-assign]
    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()

    if mode == "legacy-reference":
        before_text = buffer.get_text()
        payload = before_text.encode("utf-8")
        recovery_payload = before_text.encode("utf-8", errors="surrogatepass")
        rollback_snapshot = buffer.get_text()
        signature = buffer._current_signature()
    elif mode == "single-payload-product":
        before_text = buffer.get_text()
        payload = before_text.encode("utf-8")
        recovery_payload = payload
        rollback_snapshot = None
        signature = Buffer.canonical_utf8_signature(payload)
    else:
        raise ValueError(f"unknown preparation mode: {mode}")

    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    expected_signature = Buffer.canonical_utf8_signature(payload)
    return {
        "elapsed_seconds": round(float(elapsed), 9),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "get_text_calls": int(calls),
        "payload_bytes": len(payload),
        "payload_exact": bool(payload.decode("utf-8") == before_text),
        "recovery_exact": bool(recovery_payload.decode("utf-8") == before_text),
        "recovery_aliases_payload": recovery_payload is payload,
        "rollback_snapshot_present": rollback_snapshot is not None,
        "rollback_snapshot_exact": bool(
            rollback_snapshot is None or rollback_snapshot == before_text
        ),
        "signature_exact": signature == expected_signature,
    }


def _median_preparation(mode: str, text: str, samples: int) -> dict[str, Any]:
    rows = [
        _measure_preparation_once(mode, text)
        for _ in range(max(1, int(samples)))
    ]
    return {
        "samples": len(rows),
        "elapsed_seconds_median": round(
            float(statistics.median(float(row["elapsed_seconds"]) for row in rows)),
            9,
        ),
        "traced_current_bytes_median": int(
            statistics.median(int(row["traced_current_bytes"]) for row in rows)
        ),
        "traced_peak_bytes_median": int(
            statistics.median(int(row["traced_peak_bytes"]) for row in rows)
        ),
        "get_text_calls": int(rows[0]["get_text_calls"]),
        "payload_bytes": int(rows[0]["payload_bytes"]),
        "payload_exact": all(bool(row["payload_exact"]) for row in rows),
        "recovery_exact": all(bool(row["recovery_exact"]) for row in rows),
        "recovery_aliases_payload": all(
            bool(row["recovery_aliases_payload"]) for row in rows
        ),
        "rollback_snapshot_present": all(
            bool(row["rollback_snapshot_present"]) for row in rows
        ),
        "rollback_snapshot_exact": all(
            bool(row["rollback_snapshot_exact"]) for row in rows
        ),
        "signature_exact": all(bool(row["signature_exact"]) for row in rows),
    }


def _percent_reduction(product: float, reference: float) -> float | None:
    if reference <= 0:
        return None
    return round(100.0 * (reference - product) / reference, 3)


class _JournalWitness:
    last_checkpoint_file_synced = False
    last_checkpoint_directory_synced = False
    last_dismiss_directory_synced = False

    def __init__(self) -> None:
        self.target: Path | None = None
        self.recovery_payload: bytes | None = None
        self.commit_argument: bytes | None | object = object()
        self.writer_payload: bytes | None = None
        self.payload_kind = ""

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
        if not buffer_id or not metadata.get("encoding"):
            raise AssertionError("missing save recovery authority")
        self.target = Path(target)
        self.recovery_payload = content
        self.commit_argument = commit_content
        self.payload_kind = payload_kind
        return "measurement-checkpoint"

    def commit_checkpoint(
        self,
        entry_id: str,
        content: bytes,
        writer: Callable[[Path, bytes], None],
    ) -> object:
        if entry_id != "measurement-checkpoint" or self.target is None:
            raise AssertionError("invalid checkpoint handoff")
        self.writer_payload = content
        writer(self.target, content)
        return SimpleNamespace(
            entry_id=entry_id,
            recovery_retired=True,
            cleanup_error=None,
        )

    def entry_ids_for_buffer(self, _buffer_id: str) -> list[str]:
        return []

    def dismiss(self, _entry_id: str) -> bool:
        return True


def _complete_huge_line_journey(chars: int) -> dict[str, Any]:
    line_chars = max(10_000, int(chars))
    needle = "NEEDLE"
    needle_at = max(1, (line_chars * 3) // 4)
    suffix_chars = max(0, line_chars - needle_at - len(needle))
    huge_line = ("a" * needle_at) + needle + ("b" * suffix_chars)
    source = huge_line + "\nfooter"
    timings: dict[str, float] = {}

    with tempfile.TemporaryDirectory(prefix="micromax-rev0995-") as tmp:
        path = Path(tmp) / "huge-line.txt"
        path.write_bytes(b"baseline")
        started = time.perf_counter()
        editor = Editor()
        editor.new_buffer(str(path), source, path=str(path))
        timings["open"] = time.perf_counter() - started
        eb = editor.cur()
        eb.local_options.update(
            {
                "softwrap": True,
                "wordwrap": False,
                "eofnewline": False,
                "rmtrailingws": True,
                "fileformat": "unix",
                "encoding": "UTF8",
                "save.atomic": False,
                "save.preserveperm": False,
                "save.checkexternal": False,
                "mkparents": False,
            }
        )

        width = 80
        top_subline = max(0, needle_at // width - 1)
        started = time.perf_counter()
        editor.set_viewport(
            top_line=0,
            top_subline=top_subline,
            left_col=0,
            height=3,
            width=width,
            follow_cursor=False,
        )
        rows = editor.view_rows(height=3, width=width)
        timings["viewport"] = time.perf_counter() - started
        viewport_found = any(needle in row[2] for row in rows)

        started = time.perf_counter()
        search_found = editor.find(needle, literal=True)
        timings["literal_search"] = time.perf_counter() - started
        search_cursor = eb.cursors[eb.primary]

        started = time.perf_counter()
        moved_right = editor.run_action("CursorRight")
        moved_left = editor.run_action("CursorLeft")
        timings["cursor_roundtrip"] = time.perf_counter() - started

        started = time.perf_counter()
        editor.input["text"] = "!"
        inserted = editor.run_action("InsertText")
        timings["edit"] = time.perf_counter() - started
        edited_fragment = eb.buf.lines[0][needle_at : needle_at + len(needle) + 1]

        started = time.perf_counter()
        undone = editor.undo_feedback()
        undo_fragment = eb.buf.lines[0][needle_at : needle_at + len(needle)]
        timings["undo"] = time.perf_counter() - started

        started = time.perf_counter()
        redone = editor.redo_feedback()
        redo_fragment = eb.buf.lines[0][needle_at : needle_at + len(needle) + 1]
        timings["redo"] = time.perf_counter() - started

        journal = _JournalWitness()
        editor.recovery_journal = journal  # type: ignore[assignment]
        editor._bounded_fs_stat = lambda *_args, **_kwargs: ContainedStatResult(  # type: ignore[method-assign]
            path=str(path),
            exists=True,
            kind="file",
            size=8,
            mtime=0,
        )
        editor._check_save_disk_fresh = lambda *_args, **_kwargs: None  # type: ignore[method-assign]
        editor._refresh_buffer_disk_signature = lambda *_args: None  # type: ignore[method-assign]
        editor._push_recent_file = lambda *_args: None  # type: ignore[method-assign]
        editor._remember_cursor_for_buffer = lambda *_args: None  # type: ignore[method-assign]
        editor._emit_mx_hook = lambda *_args: None  # type: ignore[method-assign]
        editor._refresh_recovery_presence_best_effort = lambda: ""  # type: ignore[method-assign]

        save_get_text_calls = 0
        save_signature_calls = 0
        save_undo_snapshot_calls = 0
        save_state_snapshot_calls = 0
        original_get_text = eb.buf.get_text
        original_signature = eb.buf._current_signature
        original_undo_snapshot = editor.undo.snapshot
        original_state_snapshot = editor._snapshot_buffer_state

        def counted_get_text() -> str:
            nonlocal save_get_text_calls
            save_get_text_calls += 1
            return original_get_text()

        def counted_signature() -> tuple[int, str]:
            nonlocal save_signature_calls
            save_signature_calls += 1
            return original_signature()

        def counted_undo_snapshot() -> Any:
            nonlocal save_undo_snapshot_calls
            save_undo_snapshot_calls += 1
            return original_undo_snapshot()

        def counted_state_snapshot(*args: Any, **kwargs: Any) -> Any:
            nonlocal save_state_snapshot_calls
            save_state_snapshot_calls += 1
            return original_state_snapshot(*args, **kwargs)

        eb.buf.get_text = counted_get_text  # type: ignore[method-assign]
        eb.buf._current_signature = counted_signature  # type: ignore[method-assign]
        editor.undo.snapshot = counted_undo_snapshot  # type: ignore[method-assign]
        editor._snapshot_buffer_state = counted_state_snapshot  # type: ignore[method-assign]

        writer_payload: bytes | None = None
        original_writer = editor_module.write_file_bytes

        def witness_writer(target: Path, content: bytes, **_kwargs: object) -> object:
            nonlocal writer_payload
            writer_payload = content
            return SimpleNamespace(
                atomic=False,
                fsync=False,
                file_synced=False,
                directory_synced=False,
                write_path=Path(target),
                followed_symlink=False,
                final_mode=None,
            )

        editor_module.write_file_bytes = witness_writer
        try:
            started = time.perf_counter()
            save_info = editor.save()
            timings["save"] = time.perf_counter() - started
        finally:
            editor_module.write_file_bytes = original_writer

        measured_get_text_calls = int(save_get_text_calls)
        measured_signature_calls = int(save_signature_calls)
        payload_exact = bool(
            writer_payload is not None
            and writer_payload.decode("utf-8") == original_get_text()
        )
        payload_signature_exact = bool(
            writer_payload is not None
            and eb.buf.current_signature
            == Buffer.canonical_utf8_signature(writer_payload)
        )

    return {
        "line_chars": line_chars,
        "needle_at": needle_at,
        "timings_seconds": {
            key: round(float(value), 9) for key, value in timings.items()
        },
        "viewport_found_needle": viewport_found,
        "viewport_rows": len(rows),
        "search_found": bool(search_found),
        "search_cursor_exact": bool(
            search_cursor.line == 0 and search_cursor.col == needle_at
        ),
        "cursor_roundtrip": bool(moved_right and moved_left),
        "inserted": bool(inserted),
        "edited_fragment": edited_fragment,
        "undone": bool(undone),
        "undo_fragment": undo_fragment,
        "redone": bool(redone),
        "redo_fragment": redo_fragment,
        "save_get_text_calls": measured_get_text_calls,
        "save_current_signature_calls": measured_signature_calls,
        "save_undo_snapshot_calls": int(save_undo_snapshot_calls),
        "save_state_snapshot_calls": int(save_state_snapshot_calls),
        "save_payload_exact": payload_exact,
        "save_payload_aliases_recovery": bool(
            writer_payload is not None
            and journal.recovery_payload is writer_payload
            and journal.writer_payload is writer_payload
        ),
        "save_checkpoint_commit_argument_is_none": journal.commit_argument is None,
        "save_payload_kind": journal.payload_kind,
        "save_clean_signature_exact": payload_signature_exact,
        "save_buffer_clean": not eb.buf.dirty,
        "save_recovery_checkpointed": bool(save_info["recovery_checkpointed"]),
    }


def _recovery_digest_witness(payload_bytes: int) -> dict[str, Any]:
    size = max(1, int(payload_bytes))
    payload = (b"0123456789abcdef" * ((size + 15) // 16))[:size]
    hashed: list[bytes] = []
    record_sizes: list[int] = []
    original_sha256 = recovery_module._sha256

    def counted_sha256(data: bytes) -> str:
        hashed.append(data)
        return original_sha256(data)

    recovery_module._sha256 = counted_sha256
    try:
        with tempfile.TemporaryDirectory(prefix="micromax-rev0995-journal-") as tmp:
            root = Path(tmp)
            journal = RecoveryJournal(
                root / "recovery",
                max_payload_bytes=max(size, 1024),
                journal_writer=lambda _path, data: record_sizes.append(len(data)),
            )
            journal.checkpoint(root / "target.txt", payload, commit_content=None)
    finally:
        recovery_module._sha256 = original_sha256

    return {
        "payload_bytes": size,
        "payload_identity_sha256_passes": sum(item is payload for item in hashed),
        "total_sha256_calls": len(hashed),
        "record_bytes": int(record_sizes[0]),
        "record_written": len(record_sizes) == 1,
    }


def build_report(*, chars: int, samples: int) -> dict[str, Any]:
    line_chars = max(10_000, int(chars))
    needle_at = max(1, (line_chars * 3) // 4)
    line = (
        ("a" * needle_at)
        + "NEEDLE"
        + ("b" * max(0, line_chars - needle_at - 6))
    )
    text = line + "\nfooter"
    legacy = _median_preparation("legacy-reference", text, samples)
    product = _median_preparation("single-payload-product", text, samples)
    return {
        "schema": SCHEMA,
        "method": {
            "timing": "local elapsed attribution only; not a portable benchmark",
            "memory": "Python allocations traced after source construction; not RSS or total memory",
            "legacy_reference": (
                "pre-rev0995 ordinary fast-dirty save: three text joins, two commit/recovery encodes, "
                "and a clean-baseline rehash"
            ),
            "product": (
                "one text join and encode; the commit payload aliases recovery and supplies the clean signature"
            ),
        },
        "save_preparation": {
            "source_chars": len(text),
            "legacy_reference": legacy,
            "single_payload_product": product,
            "comparison": {
                "get_text_call_reduction_percent": _percent_reduction(
                    float(product["get_text_calls"]),
                    float(legacy["get_text_calls"]),
                ),
                "elapsed_reduction_percent": _percent_reduction(
                    float(product["elapsed_seconds_median"]),
                    float(legacy["elapsed_seconds_median"]),
                ),
                "traced_peak_reduction_percent": _percent_reduction(
                    float(product["traced_peak_bytes_median"]),
                    float(legacy["traced_peak_bytes_median"]),
                ),
                "both_exact": bool(
                    legacy["payload_exact"]
                    and legacy["recovery_exact"]
                    and legacy["signature_exact"]
                    and product["payload_exact"]
                    and product["recovery_exact"]
                    and product["signature_exact"]
                ),
                "product_aliases_recovery": bool(
                    product["recovery_aliases_payload"]
                ),
            },
        },
        "complete_huge_line_journey": _complete_huge_line_journey(line_chars),
        "recovery_checkpoint_digest": _recovery_digest_witness(
            min(line_chars, 2_000_000)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=8_000_000)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = build_report(chars=args.chars, samples=args.samples)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
