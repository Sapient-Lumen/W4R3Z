#!/usr/bin/env python3
"""Measure sparse history replay and sustained very-long-line editing.

This is a local attribution witness, not a portable latency benchmark.  It
compares rev0990's product line-vector Undo/Redo replay with the exact rev0989
flat-string replay shape, then runs insertion, Backspace, Delete, and replacement
journeys in one long logical line under exact-dirty and fast-dirty policy.

Examples:
  PYTHONPATH=src python tools/measure_line_vector_replay.py
  PYTHONPATH=src python tools/measure_line_vector_replay.py --samples 3
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from collections.abc import Callable, Iterable
from typing import Any

from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor
from micromax_editor.simultaneous_edits import (
    SimultaneousEditWitness,
    SimultaneousTextEdit,
    plan_simultaneous_edits,
    replay_simultaneous_edit_witness,
    replay_simultaneous_edit_witness_lines,
)

SCHEMA = "micromax.line-vector-replay-long-line-measurement.v1"


class _CountingBuffer(Buffer):
    """Count explicit complete-text and line-vector publication calls."""

    def __init__(self, text: str) -> None:
        self.full_text_reads = 0
        self.full_text_read_chars = 0
        self.full_text_writes = 0
        self.full_text_write_chars = 0
        self.line_vector_writes = 0
        super().__init__(text)
        self.reset_counts()

    def reset_counts(self) -> None:
        self.full_text_reads = 0
        self.full_text_read_chars = 0
        self.full_text_writes = 0
        self.full_text_write_chars = 0
        self.line_vector_writes = 0

    def get_text(self) -> str:
        value = super().get_text()
        self.full_text_reads += 1
        self.full_text_read_chars += len(value)
        return value

    def set_text(self, text: str) -> None:
        self.full_text_writes += 1
        self.full_text_write_chars += len(str(text))
        super().set_text(text)

    def replace_lines(self, lines: Iterable[str]) -> None:
        self.line_vector_writes += 1
        super().replace_lines(lines)


def _median_int(rows: list[dict[str, Any]], key: str) -> int:
    return int(statistics.median(int(row[key]) for row in rows))


def _median_float(rows: list[dict[str, Any]], key: str) -> float:
    return round(float(statistics.median(float(row[key]) for row in rows)), 6)


def _percent_reduction(product: int, reference: int) -> float | None:
    if int(reference) <= 0:
        return None
    return round(100.0 * (int(reference) - int(product)) / int(reference), 3)


def _sparse_plan(
    *,
    line_count: int,
    line_width: int,
    splice_count: int,
) -> tuple[str, object, SimultaneousEditWitness]:
    lines = [
        f"{index:08d}" + ("a" * max(1, int(line_width) - 8))
        for index in range(max(2, int(line_count)))
    ]
    source = "\n".join(lines)
    count = max(2, min(int(splice_count), len(lines) - 1))
    requests: list[SimultaneousTextEdit] = []
    for index in range(count):
        line = max(0, min(len(lines) - 1, round((index + 1) * (len(lines) - 1) / (count + 1))))
        col = min(10, len(lines[line]) - 1)
        requests.append(
            SimultaneousTextEdit(
                Cursor(line, col),
                Cursor(line, col + 1),
                f"<{index:03x}>",
                owner=index,
            )
        )
    plan = plan_simultaneous_edits(source, requests)
    return source, plan, plan.compact_history_witness()


def _measure_replay_once(
    *,
    mode: str,
    source: str,
    plan: Any,
    witness: SimultaneousEditWitness,
) -> dict[str, Any]:
    buffer = _CountingBuffer(plan.new_text)
    buffer.set_fastdirty(True)

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    if mode == "flat-reference":
        current = buffer.get_text()
        restored = replay_simultaneous_edit_witness(current, witness, undo=True)
        buffer.set_text(restored)
        current = buffer.get_text()
        restored = replay_simultaneous_edit_witness(current, witness, undo=False)
        buffer.set_text(restored)
        complete_result_strings = 2
    elif mode == "line-vector-product":
        restored_lines = replay_simultaneous_edit_witness_lines(
            buffer.lines,
            witness,
            undo=True,
        )
        buffer.replace_lines(restored_lines)
        restored_lines = replay_simultaneous_edit_witness_lines(
            buffer.lines,
            witness,
            undo=False,
        )
        buffer.replace_lines(restored_lines)
        complete_result_strings = 0
    else:
        raise ValueError(f"unknown replay mode: {mode}")
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    counts = {
        "full_document_get_text_calls": int(buffer.full_text_reads),
        "full_document_get_text_chars": int(buffer.full_text_read_chars),
        "full_document_set_text_calls": int(buffer.full_text_writes),
        "full_document_set_text_chars": int(buffer.full_text_write_chars),
        "complete_result_strings": int(complete_result_strings),
        "line_vector_commits": int(buffer.line_vector_writes),
    }
    exact = buffer.get_text() == plan.new_text
    return {
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "roundtrip_exact": bool(exact and source != plan.new_text),
        **counts,
    }


def _measure_replay(
    *,
    mode: str,
    source: str,
    plan: Any,
    witness: SimultaneousEditWitness,
    samples: int,
) -> dict[str, Any]:
    rows = [
        _measure_replay_once(
            mode=mode,
            source=source,
            plan=plan,
            witness=witness,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    return {
        "samples": len(rows),
        "elapsed_seconds_median": _median_float(rows, "elapsed_seconds"),
        "traced_current_bytes_median": _median_int(rows, "traced_current_bytes"),
        "traced_peak_bytes_median": _median_int(rows, "traced_peak_bytes"),
        "roundtrip_exact": all(bool(row["roundtrip_exact"]) for row in rows),
        "full_document_get_text_calls": int(first["full_document_get_text_calls"]),
        "full_document_get_text_chars": int(first["full_document_get_text_chars"]),
        "full_document_set_text_calls": int(first["full_document_set_text_calls"]),
        "full_document_set_text_chars": int(first["full_document_set_text_chars"]),
        "complete_result_strings": int(first["complete_result_strings"]),
        "line_vector_commits": int(first["line_vector_commits"]),
    }


def _line_reuse_probe(plan: Any, witness: SimultaneousEditWitness) -> dict[str, Any]:
    current_lines = plan.new_text.split("\n")
    source_ids = {id(line) for line in current_lines}
    restored = replay_simultaneous_edit_witness_lines(
        current_lines,
        witness,
        undo=True,
    )
    reused = sum(1 for line in restored if id(line) in source_ids)
    return {
        "result_lines": len(restored),
        "reused_source_line_objects": int(reused),
        "reused_source_line_percent": round(100.0 * reused / max(1, len(restored)), 3),
    }


def _install_one_cursor(editor: Editor, cursor: Cursor) -> None:
    eb = editor.cur()
    eb.cursors[:] = [Cursor(int(cursor.line), int(cursor.col))]
    eb.sel_anchors[:] = [None]
    eb.cursor_ids[:] = [1]
    eb.primary = 0
    editor._normalize_cursor_lists(eb)


def _long_line_once(
    *,
    chars: int,
    edits: int,
    operation: str,
    fastdirty: bool,
) -> dict[str, Any]:
    size = max(64, int(chars))
    count = max(1, min(int(edits), size // 4))
    source = "a" * size
    middle = size // 2
    editor = Editor()
    editor.new_buffer(f"*long-line-{operation}*", source)
    editor._now_fn = lambda: 1.0
    eb = editor.cur()
    eb.buf.set_fastdirty(bool(fastdirty))

    if operation == "insert":
        _install_one_cursor(editor, Cursor(0, middle))
        expected = source[:middle] + ("x" * count) + source[middle:]
    elif operation == "backspace":
        _install_one_cursor(editor, Cursor(0, middle))
        expected = source[: middle - count] + source[middle:]
    elif operation == "delete":
        _install_one_cursor(editor, Cursor(0, middle))
        expected = source[:middle] + source[middle + count :]
    elif operation == "replace":
        _install_one_cursor(editor, Cursor(0, middle + 1))
        expected_char = "a" if count % 2 == 0 else "b"
        expected = source[:middle] + expected_char + source[middle + 1 :]
    else:
        raise ValueError(f"unknown long-line operation: {operation}")

    signature_calls = 0
    original_signature: Callable[[], tuple[int, str]] = eb.buf._current_signature

    def counted_signature() -> tuple[int, str]:
        nonlocal signature_calls
        signature_calls += 1
        return original_signature()

    eb.buf._current_signature = counted_signature  # type: ignore[method-assign]

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    for index in range(count):
        if operation == "insert":
            editor.input["text"] = "x"
            changed = editor.run_action("InsertText")
        elif operation == "backspace":
            changed = editor.run_action("Backspace")
        elif operation == "delete":
            changed = editor.run_action("Delete")
        else:
            eb.cursors[0] = Cursor(0, middle + 1)
            eb.sel_anchors[0] = Cursor(0, middle)
            editor.input["text"] = "b" if index % 2 == 0 else "a"
            changed = editor.run_action("InsertText")
        if not changed:
            raise RuntimeError(f"long-line {operation} action made no change")
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    action_signature_calls = int(signature_calls)
    action_text_exact = eb.buf.get_text() == expected
    action_cursor = Cursor(int(eb.cursors[0].line), int(eb.cursors[0].col))
    action_dirty = bool(eb.buf.dirty)
    history_depth = int(editor.undo.depth())

    while editor.undo.depth():
        if not editor.undo_feedback():
            raise RuntimeError(f"long-line {operation} undo failed")
    undo_text_exact = eb.buf.get_text() == source
    undo_cursor = Cursor(int(eb.cursors[0].line), int(eb.cursors[0].col))
    undo_dirty = bool(eb.buf.dirty)
    while editor.undo.redo_depth():
        if not editor.redo_feedback():
            raise RuntimeError(f"long-line {operation} redo failed")
    redo_text_exact = eb.buf.get_text() == expected
    redo_cursor = Cursor(int(eb.cursors[0].line), int(eb.cursors[0].col))

    return {
        "document_chars": len(source),
        "edits": int(count),
        "operation": operation,
        "fastdirty": bool(fastdirty),
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "action_signature_calls": action_signature_calls,
        "history_depth": history_depth,
        "action_text_exact": bool(action_text_exact),
        "undo_text_exact": bool(undo_text_exact),
        "redo_text_exact": bool(redo_text_exact),
        "action_cursor": [int(action_cursor.line), int(action_cursor.col)],
        "undo_cursor": [int(undo_cursor.line), int(undo_cursor.col)],
        "redo_cursor": [int(redo_cursor.line), int(redo_cursor.col)],
        "action_dirty": action_dirty,
        "undo_dirty": undo_dirty,
    }


def _long_line_case(
    *,
    chars: int,
    edits: int,
    operation: str,
    fastdirty: bool,
    samples: int,
) -> dict[str, Any]:
    rows = [
        _long_line_once(
            chars=chars,
            edits=edits,
            operation=operation,
            fastdirty=fastdirty,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    return {
        "document_chars": int(first["document_chars"]),
        "edits": int(first["edits"]),
        "operation": str(first["operation"]),
        "fastdirty": bool(first["fastdirty"]),
        "samples": len(rows),
        "elapsed_seconds_median": _median_float(rows, "elapsed_seconds"),
        "traced_current_bytes_median": _median_int(rows, "traced_current_bytes"),
        "traced_peak_bytes_median": _median_int(rows, "traced_peak_bytes"),
        "action_signature_calls": int(first["action_signature_calls"]),
        "history_depth": int(first["history_depth"]),
        "action_text_exact": all(bool(row["action_text_exact"]) for row in rows),
        "undo_text_exact": all(bool(row["undo_text_exact"]) for row in rows),
        "redo_text_exact": all(bool(row["redo_text_exact"]) for row in rows),
        "action_cursor": list(first["action_cursor"]),
        "undo_cursor": list(first["undo_cursor"]),
        "redo_cursor": list(first["redo_cursor"]),
        "action_dirty": bool(first["action_dirty"]),
        "undo_dirty": bool(first["undo_dirty"]),
    }


def build_report(
    *,
    line_count: int = 11_000,
    line_width: int = 99,
    splices: int = 128,
    long_line_chars: int = 1_100_000,
    long_line_edits: int = 64,
    samples: int = 3,
) -> dict[str, Any]:
    source, plan, witness = _sparse_plan(
        line_count=line_count,
        line_width=line_width,
        splice_count=splices,
    )
    product = _measure_replay(
        mode="line-vector-product",
        source=source,
        plan=plan,
        witness=witness,
        samples=samples,
    )
    reference = _measure_replay(
        mode="flat-reference",
        source=source,
        plan=plan,
        witness=witness,
        samples=samples,
    )

    long_line: dict[str, Any] = {}
    for operation in ("insert", "backspace", "delete", "replace"):
        operation_edits = (
            min(int(long_line_edits), 32)
            if operation == "replace"
            else int(long_line_edits)
        )
        fast = _long_line_case(
            chars=long_line_chars,
            edits=operation_edits,
            operation=operation,
            fastdirty=True,
            samples=samples,
        )
        exact = _long_line_case(
            chars=long_line_chars,
            edits=operation_edits,
            operation=operation,
            fastdirty=False,
            samples=samples,
        )
        long_line[operation] = {
            "fastdirty_product_policy": fast,
            "exact_dirty_reference_policy": exact,
            "comparison": {
                "signature_pass_reduction_percent": _percent_reduction(
                    int(fast["action_signature_calls"]),
                    int(exact["action_signature_calls"]),
                ),
                "elapsed_reduction_percent_local_context": _percent_reduction(
                    round(float(fast["elapsed_seconds_median"]) * 1_000_000),
                    round(float(exact["elapsed_seconds_median"]) * 1_000_000),
                ),
                "both_roundtrip_exact": bool(
                    fast["undo_text_exact"]
                    and fast["redo_text_exact"]
                    and exact["undo_text_exact"]
                    and exact["redo_text_exact"]
                ),
            },
        }

    return {
        "schema": SCHEMA,
        "scope": {
            "timing": "local context only; not a portable latency bound",
            "memory": "Python tracemalloc only; not RSS, allocator arenas, or native memory",
            "reference": "rev0989 flat current/result replay shape, evidence only",
        },
        "sparse_replay": {
            "document_chars": len(source),
            "document_lines": len(plan.new_text.split("\n")),
            "splices": len(witness.splices),
            "line_vector_product": product,
            "rev0989_flat_reference": reference,
            "line_identity_reuse": _line_reuse_probe(plan, witness),
            "comparison": {
                "complete_document_string_reduction_percent": _percent_reduction(
                    int(product["complete_result_strings"])
                    + int(product["full_document_get_text_calls"]),
                    int(reference["complete_result_strings"])
                    + int(reference["full_document_get_text_calls"]),
                ),
                "traced_peak_reduction_percent": _percent_reduction(
                    int(product["traced_peak_bytes_median"]),
                    int(reference["traced_peak_bytes_median"]),
                ),
                "both_roundtrip_exact": bool(
                    product["roundtrip_exact"] and reference["roundtrip_exact"]
                ),
            },
        },
        "long_logical_line": long_line,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--line-count", type=int, default=11_000)
    parser.add_argument("--line-width", type=int, default=99)
    parser.add_argument("--splices", type=int, default=128)
    parser.add_argument("--long-line-chars", type=int, default=1_100_000)
    parser.add_argument("--long-line-edits", type=int, default=64)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    report = build_report(
        line_count=args.line_count,
        line_width=args.line_width,
        splices=args.splices,
        long_line_chars=args.long_line_chars,
        long_line_edits=args.long_line_edits,
        samples=args.samples,
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload)
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
