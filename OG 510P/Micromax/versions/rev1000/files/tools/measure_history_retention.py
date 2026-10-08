#!/usr/bin/env python3
"""Measure aggregate-transaction retention and the soft undo byte budget.

The aggregate comparison uses two shapes inside the current runtime:

* ``changed_buffers_only`` is Micromax's product path.
* ``broad_snapshot_reference`` reproduces the rev0983 compound-row retention
  shape by retaining full before/after snapshots for every open buffer.

Aggregate measurements are Python allocations observed by ``tracemalloc`` after
temporary snapshot owners are released and GC runs.  They are not RSS, allocator,
native memory, latency, or a hard cross-platform process-memory bound.  A separate
synthetic-charge probe counts historical accounting reads exactly, without a
wall-clock complexity claim.

Examples:
  PYTHONPATH=src python tools/measure_history_retention.py
  PYTHONPATH=src python tools/measure_history_retention.py --chars 400000 --samples 1
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from dataclasses import replace
from typing import Any, Callable

from micromax_editor.editor import Editor, MacroReplaySnapshot
from micromax_editor.undo import Edit, UndoManager, UndoSnapshot, logical_text_bytes

SCHEMA = "micromax.history-retention-witness.v1"


def _state_only(snapshot: MacroReplaySnapshot) -> MacroReplaySnapshot:
    """Reproduce the rev0983 broad compound-row retained shape."""

    return replace(
        snapshot,
        input={},
        undo=UndoSnapshot(undo=(), redo=(), suppress=0),
    )


def _callback_snapshot(callback: Callable[[], None]) -> MacroReplaySnapshot:
    rows = [
        cell.cell_contents
        for cell in (callback.__closure__ or ())
        if isinstance(cell.cell_contents, MacroReplaySnapshot)
    ]
    if len(rows) != 1:
        raise RuntimeError(f"expected one retained transaction snapshot, got {len(rows)}")
    return rows[0]


def _history_snapshot_text_bytes(edit: Edit) -> int:
    total = 0
    for callback in (edit.undo, edit.redo):
        snapshot = _callback_snapshot(callback)
        total += sum(logical_text_bytes(row.text) for row in snapshot.buffers)
    return int(total)


def _history_full_text_buffer_rows(edit: Edit) -> int:
    rows = 0
    for callback in (edit.undo, edit.redo):
        snapshot = _callback_snapshot(callback)
        rows += sum(bool(row.text) for row in snapshot.buffers)
    return int(rows)


def _buffer_signatures(editor: Editor) -> tuple[tuple[int, str], ...]:
    return tuple(
        eb.buf._text_signature(eb.buf.get_text())
        for eb in editor.buffers.values()
    )


def _build_editor(*, chars: int, buffer_count: int) -> Editor:
    rows = max(1, int(chars) // 80)
    editor = Editor()
    editor.options.set("undobytes", "0")
    for index in range(max(1, int(buffer_count))):
        marker = chr(ord("a") + (index % 26))
        text = ((marker * 79) + "\n") * rows
        editor.new_buffer(f"buffer-{index + 1}", text)
    editor.exec_command_line("buffer buffer-1")
    return editor


def _measure_aggregate_once(
    *,
    chars: int,
    buffer_count: int,
    broad_reference: bool,
) -> dict[str, Any]:
    editor = _build_editor(chars=chars, buffer_count=buffer_count)
    before_signatures = _buffer_signatures(editor)
    gc.collect()

    tracemalloc.start()
    start = time.perf_counter()
    before = editor._buffer_transaction_snapshot()
    with editor.undo.suppress_recording():
        editor.input["text"] = "X"
        if not editor.run_action("InsertText"):
            raise RuntimeError("aggregate witness edit failed")
    after = editor._buffer_transaction_snapshot(
        reuse_unchanged_text_from=None if broad_reference else before,
    )
    after_signatures = _buffer_signatures(editor)

    if broad_reference:
        retained_before = _state_only(before)
        retained_after = _state_only(after)

        def _undo() -> None:
            editor._restore_buffer_transaction_snapshot(retained_before)

        def _redo() -> None:
            editor._restore_buffer_transaction_snapshot(retained_after)

        editor.undo.record(Edit(undo=_undo, redo=_redo, description="broad reference"))
    else:
        editor._record_buffer_transaction_snapshot(before, after, "changed buffers only")

    del before, after
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    elapsed = time.perf_counter() - start
    tracemalloc.stop()

    edit = editor.undo.peek_undo()
    if edit is None:
        raise RuntimeError("aggregate witness produced no undo row")
    snapshot_text_bytes = _history_snapshot_text_bytes(edit)
    full_text_buffer_rows = _history_full_text_buffer_rows(edit)
    accounted_text_bytes = sum(charge.byte_count for charge in edit.retained_text)

    if not editor.undo_feedback():
        raise RuntimeError("aggregate undo failed")
    undo_exact = _buffer_signatures(editor) == before_signatures
    if not editor.redo_feedback():
        raise RuntimeError("aggregate redo failed")
    redo_exact = _buffer_signatures(editor) == after_signatures

    return {
        "document_chars_per_buffer": int(before_signatures[0][0]),
        "open_buffers": int(buffer_count),
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": int(current),
        "traced_peak_bytes": int(peak),
        "retained_snapshot_text_bytes": int(snapshot_text_bytes),
        "accounted_retained_text_bytes": int(accounted_text_bytes),
        "full_text_buffer_snapshot_rows": int(full_text_buffer_rows),
        "undo_exact": bool(undo_exact),
        "redo_exact": bool(redo_exact),
    }


def _median_aggregate(
    *,
    chars: int,
    buffer_count: int,
    samples: int,
    broad_reference: bool,
) -> dict[str, Any]:
    rows = [
        _measure_aggregate_once(
            chars=chars,
            buffer_count=buffer_count,
            broad_reference=broad_reference,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    return {
        "document_chars_per_buffer": int(first["document_chars_per_buffer"]),
        "open_buffers": int(first["open_buffers"]),
        "samples": len(rows),
        "elapsed_seconds_median": round(
            float(statistics.median(row["elapsed_seconds"] for row in rows)),
            6,
        ),
        "traced_current_bytes_median": int(
            statistics.median(row["traced_current_bytes"] for row in rows)
        ),
        "traced_peak_bytes_median": int(
            statistics.median(row["traced_peak_bytes"] for row in rows)
        ),
        "retained_snapshot_text_bytes": int(first["retained_snapshot_text_bytes"]),
        "accounted_retained_text_bytes": int(first["accounted_retained_text_bytes"]),
        "full_text_buffer_snapshot_rows": int(first["full_text_buffer_snapshot_rows"]),
        "undo_exact": all(bool(row["undo_exact"]) for row in rows),
        "redo_exact": all(bool(row["redo_exact"]) for row in rows),
    }


def _budget_journey(*, budget_bytes: int, edits: int, chunk_chars: int) -> dict[str, Any]:
    editor = Editor()
    editor.new_buffer("budget", "")
    eb = editor.cur()
    editor.set_option_value("undobytes", str(max(0, int(budget_bytes))), local=True)
    chunk = "z" * max(1, int(chunk_chars))
    count = max(1, int(edits))

    for _ in range(count):
        editor.input["text"] = chunk
        if not editor.run_action("InsertText"):
            raise RuntimeError("budget witness edit failed")

    expected = chunk * count
    if eb.buf.get_text() != expected:
        raise RuntimeError("budget witness forward text mismatch")
    retained_before_undo = editor.undo.retained_text_bytes(eb)
    depth = editor.undo.depth()
    undo_count = 0
    while editor.undo_feedback():
        undo_count += 1
    expected_prefix = chunk * (count - undo_count)
    undo_exact = eb.buf.get_text() == expected_prefix
    redo_count = 0
    while editor.redo_feedback():
        redo_count += 1
    redo_exact = eb.buf.get_text() == expected

    trim_notices = [
        str(message)
        for message in editor.messages
        if "undo: trimmed" in str(message)
    ]
    return {
        "budget_bytes": max(0, int(budget_bytes)),
        "edits_attempted": int(count),
        "chunk_chars": len(chunk),
        "retained_text_bytes": int(retained_before_undo),
        "retained_undo_rows": int(depth),
        "trimmed_undo_rows": int(count - depth),
        "trim_messages": len(trim_notices),
        "trim_notices": trim_notices,
        "undo_rows_replayed": int(undo_count),
        "redo_rows_replayed": int(redo_count),
        "undo_exact": bool(undo_exact),
        "redo_exact": bool(redo_exact),
    }


class _CountingCharge:
    """Runtime probe that counts accesses to a historical charge."""

    def __init__(self, owner: object, byte_count: int, reads: list[int]) -> None:
        self.owner = owner
        self.label = "accounting probe"
        self._byte_count = int(byte_count)
        self._reads = reads

    @property
    def byte_count(self) -> int:
        self._reads[0] += 1
        return self._byte_count


def _accounting_hotpath(*, rows: int) -> dict[str, Any]:
    """Witness cached queries and O(1) oldest-row retirement without timing."""

    count = max(2, int(rows))
    owner = object()
    reads = [0]
    undo = UndoManager()

    def _noop() -> None:
        return None

    for index in range(count):
        charge = _CountingCharge(owner, 1, reads)
        undo.record(
            Edit(
                undo=_noop,
                redo=_noop,
                description=f"probe {index}",
                retained_text=(charge,),  # type: ignore[arg-type]
            )
        )

    record_reads = int(reads[0])
    reads[0] = 0
    total = undo.retained_text_bytes()
    owner_total = undo.retained_text_bytes(owner)
    noop_report = undo.trim_undo_to_budgets(((owner, "probe", count),))
    cached_query_reads = int(reads[0])

    reads[0] = 0
    trim_report = undo.trim_undo_to_budgets(((owner, "probe", count - 1),))
    one_row_trim_reads = int(reads[0])

    return {
        "history_rows": int(count),
        "charge_reads_while_recording": record_reads,
        "charge_reads_for_two_queries_and_noop_budget_check": cached_query_reads,
        "linear_rescan_reference_reads_for_same_operations": int(count * 3),
        "charge_reads_to_retire_one_oldest_row": one_row_trim_reads,
        "retained_text_bytes_before_trim": int(total),
        "owner_retained_text_bytes_before_trim": int(owner_total),
        "noop_budget_dropped_rows": int(noop_report.dropped_edits),
        "single_budget_dropped_rows": int(trim_report.dropped_edits),
        "retained_rows_after_trim": int(undo.depth()),
        "retained_text_bytes_after_trim": int(undo.retained_text_bytes(owner)),
    }


def _reduction_percent(reference: int, current: int) -> float:
    if reference <= 0:
        return 0.0
    return round((1.0 - (current / reference)) * 100.0, 3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chars", type=int, default=4_000_000)
    parser.add_argument("--buffers", type=int, default=3)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--budget-bytes", type=int, default=4096)
    parser.add_argument("--budget-edits", type=int, default=80)
    parser.add_argument("--chunk-chars", type=int, default=128)
    parser.add_argument("--accounting-rows", type=int, default=20_000)
    args = parser.parse_args()

    current = _median_aggregate(
        chars=max(80, args.chars),
        buffer_count=max(1, args.buffers),
        samples=max(1, args.samples),
        broad_reference=False,
    )
    reference = _median_aggregate(
        chars=max(80, args.chars),
        buffer_count=max(1, args.buffers),
        samples=max(1, args.samples),
        broad_reference=True,
    )
    budget = _budget_journey(
        budget_bytes=max(0, args.budget_bytes),
        edits=max(1, args.budget_edits),
        chunk_chars=max(1, args.chunk_chars),
    )
    accounting = _accounting_hotpath(rows=max(2, args.accounting_rows))

    payload = {
        "schema": SCHEMA,
        "measurement_scope": (
            "Aggregate rows use Python tracemalloc after temporary snapshots are "
            "released (not RSS/native memory or a hard portable bound); the "
            "accounting probe counts synthetic charge-field reads exactly"
        ),
        "changed_buffers_only": current,
        "broad_snapshot_reference": reference,
        "comparison": {
            "traced_current_reduction_percent": _reduction_percent(
                reference["traced_current_bytes_median"],
                current["traced_current_bytes_median"],
            ),
            "traced_peak_reduction_percent": _reduction_percent(
                reference["traced_peak_bytes_median"],
                current["traced_peak_bytes_median"],
            ),
            "retained_snapshot_text_reduction_percent": _reduction_percent(
                reference["retained_snapshot_text_bytes"],
                current["retained_snapshot_text_bytes"],
            ),
        },
        "budget_journey": budget,
        "accounting_hotpath": accounting,
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
