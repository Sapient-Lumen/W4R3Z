#!/usr/bin/env python3
"""Measure first-write ``ed.with-undo`` capture against the eager reference.

Both cases use the current Micromax runtime and the same aggregate transaction
semantics:

* ``eager_snapshot_reference`` reproduces the pre-rev0986 all-open-buffer text
  capture used by ``ed.with-undo``.
* ``first_write_product`` uses the rev0992 journal that shallow-copies the
  canonical line vector immediately before a buffer's first mutation.

The success case preserves the same aggregate transaction semantics while the
product retains shared line vectors instead of complete before/after document
strings.  The failure case rolls back the same edit and records no history.

Measurements use CPython ``tracemalloc``.  They are not RSS, allocator-arena,
native-memory, latency, durability, or cross-platform bounds.

Examples:
  PYTHONPATH=src python tools/measure_first_write_transactions.py
  PYTHONPATH=src python tools/measure_first_write_transactions.py \\
      --chars 250000 --buffers 4 --samples 1 --output /tmp/witness.json
"""

from __future__ import annotations

import argparse
import gc
import json
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path
from typing import Any

from micromax_editor.buffer import Buffer, Cursor, normalize_buffer_text
from micromax_editor.editor import Editor, FirstWriteTransactionJournal

SCHEMA = "micromax.first-write-transaction-witness.v2"


class _ExpectedRollback(RuntimeError):
    pass


class _PermanentObservedLineList(list[str]):
    """Rejected always-present line-list dispatch used only as a timing control."""

    def __setitem__(self, index: Any, value: Any) -> None:
        super().__setitem__(index, value)


class _Rev0985MutationBuffer(Buffer):
    """Single-line mutation control without rev0986's cold observer branch."""

    def insert(self, cur: Cursor, s: str) -> Cursor:
        cur = self.clamp(cur)
        replacement = normalize_buffer_text(s)
        if "\n" in replacement:
            raise RuntimeError("mutation control accepts single-line text only")
        line = self._lines[cur.line]
        self._lines[cur.line] = line[: cur.col] + replacement + line[cur.col :]
        self._touch(start_line=cur.line, old_line_count=1, new_line_count=1)
        return Cursor(cur.line, cur.col + len(replacement))

    def delete_range(self, start: Cursor, end: Cursor) -> Cursor:
        start = self.clamp(start)
        end = self.clamp(end)
        if (end.line, end.col) < (start.line, start.col):
            start, end = end, start
        if start.line != end.line:
            raise RuntimeError("mutation control accepts one line only")
        line = self._lines[start.line]
        self._lines[start.line] = line[: start.col] + line[end.col :]
        self._touch(start_line=start.line, old_line_count=1, new_line_count=1)
        return Cursor(start.line, start.col)


class _PermanentObservedMutationBuffer(_Rev0985MutationBuffer):
    """Rejected design control with Python dispatch on every line assignment."""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self._lines = _PermanentObservedLineList(self._lines)


def _source_text(chars: int, marker: str) -> str:
    target = max(1, int(chars))
    row = (str(marker) * 79) + "\n"
    repeats = max(1, target // len(row))
    text = row * repeats
    remainder = target - len(text)
    if remainder > 0:
        text += str(marker) * remainder
    return text


def _build_editor(*, chars: int, buffer_count: int) -> tuple[Editor, dict[str, str]]:
    editor = Editor()
    editor.options.set("undobytes", "0")
    sources: dict[str, str] = {}
    for index in range(max(1, int(buffer_count))):
        name = f"buffer-{index + 1}"
        marker = chr(ord("a") + (index % 26))
        source = _source_text(chars, marker)
        sources[name] = source
        editor.new_buffer(name, source)
        # Keep the witness on transaction capture rather than exact dirty hashing.
        editor.buffers[name].buf.fastdirty = True
        editor.buffers[name].buf.dirty = False
    if not editor.switch_buffer("buffer-1"):
        raise RuntimeError("could not select witness buffer")
    editor.input["text"] = "X"
    return editor, sources


def _instrument_text_joins(editor: Editor) -> tuple[dict[str, int], Callable[[], None]]:
    counts = {"calls": 0, "chars": 0}
    instrumented: list[Buffer] = []
    for eb in editor.buffers.values():
        buffer = eb.buf
        original = buffer.get_text

        def counted(*, _original: Callable[[], str] = original) -> str:
            text = _original()
            counts["calls"] += 1
            counts["chars"] += len(text)
            return text

        buffer.get_text = counted  # type: ignore[method-assign]
        instrumented.append(buffer)

    def restore() -> None:
        for buffer in instrumented:
            buffer.__dict__.pop("get_text", None)

    return counts, restore


def _texts_match(editor: Editor, expected: dict[str, str]) -> bool:
    return set(editor.buffers) == set(expected) and all(
        editor.buffers[name].buf.get_text() == text
        for name, text in expected.items()
    )


def _record_eager(editor: Editor) -> None:
    before = editor._buffer_transaction_snapshot()
    with editor.undo.suppress_recording():
        if not editor.run_action("InsertText"):
            raise RuntimeError("eager success edit failed")
    after = editor._buffer_transaction_snapshot(reuse_unchanged_text_from=before)
    if not editor._buffer_transaction_changed(before, after):
        raise RuntimeError("eager success transaction looked unchanged")
    editor._record_buffer_transaction_snapshot(before, after, "eager reference")


def _record_first_write(editor: Editor) -> int:
    journal: FirstWriteTransactionJournal | None = None
    with editor._first_write_buffer_transaction() as journal:
        with editor.undo.suppress_recording():
            if not editor.run_action("InsertText"):
                raise RuntimeError("first-write success edit failed")
    if journal is None:
        raise RuntimeError("first-write journal was not created")
    old_rows = len(journal.old_lines_by_buffer_id)
    before, after = editor._finish_first_write_buffer_transaction(journal)
    if not editor._buffer_transaction_changed(before, after):
        raise RuntimeError("first-write success transaction looked unchanged")
    editor._record_buffer_transaction_snapshot(before, after, "first-write product")
    return int(old_rows)


def _rollback_eager(editor: Editor) -> None:
    before = editor._buffer_transaction_snapshot()
    try:
        with editor.undo.suppress_recording():
            if not editor.run_action("InsertText"):
                raise RuntimeError("eager rollback edit failed")
            raise _ExpectedRollback("rollback witness")
    except _ExpectedRollback:
        editor._restore_macro_replay_snapshot(before)


def _rollback_first_write(editor: Editor) -> int:
    journal: FirstWriteTransactionJournal | None = None
    try:
        with editor._first_write_buffer_transaction() as journal:
            with editor.undo.suppress_recording():
                if not editor.run_action("InsertText"):
                    raise RuntimeError("first-write rollback edit failed")
                raise _ExpectedRollback("rollback witness")
    except _ExpectedRollback:
        if journal is None:
            raise RuntimeError("first-write journal was not created")
        old_rows = len(journal.old_lines_by_buffer_id)
        rollback = editor._first_write_transaction_rollback_snapshot(journal)
        editor._restore_macro_replay_snapshot(rollback)
        return int(old_rows)
    raise RuntimeError("rollback witness unexpectedly committed")


def _measure_transaction_once(
    *,
    chars: int,
    buffer_count: int,
    first_write: bool,
    commit: bool,
) -> dict[str, Any]:
    editor, sources = _build_editor(chars=chars, buffer_count=buffer_count)
    before_expected = dict(sources)
    after_expected = dict(sources)
    after_expected["buffer-1"] = "X" + after_expected["buffer-1"]
    joins, restore_joins = _instrument_text_joins(editor)
    old_rows = 0

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    if commit:
        if first_write:
            old_rows = _record_first_write(editor)
        else:
            _record_eager(editor)
            old_rows = len(before_expected)
    elif first_write:
        old_rows = _rollback_first_write(editor)
    else:
        _rollback_eager(editor)
        old_rows = len(before_expected)
    elapsed = time.perf_counter() - started

    joined_calls = int(joins["calls"])
    joined_chars = int(joins["chars"])
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    restore_joins()

    if commit:
        forward_exact = _texts_match(editor, after_expected)
        edit = editor.undo.peek_undo()
        if edit is None:
            raise RuntimeError("success witness produced no undo row")
        retained_bytes = sum(int(charge.byte_count) for charge in edit.retained_text)
        retained_rows = len(edit.retained_text)
        if not editor.undo.undo():
            raise RuntimeError("success witness undo failed")
        undo_exact = _texts_match(editor, before_expected)
        if not editor.undo.redo():
            raise RuntimeError("success witness redo failed")
        redo_exact = _texts_match(editor, after_expected)
    else:
        forward_exact = _texts_match(editor, before_expected)
        retained_bytes = editor.undo.retained_text_bytes()
        retained_rows = 0
        undo_exact = editor.undo.depth() == 0
        redo_exact = editor.undo.redo_depth() == 0

    return {
        "document_chars_per_buffer": len(next(iter(sources.values()))),
        "open_buffers": len(sources),
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "joined_text_calls": joined_calls,
        "joined_text_chars": joined_chars,
        "old_content_capture_rows": int(old_rows),
        "capture_representation": (
            "line-vector" if first_write else "joined-text"
        ),
        "retained_text_charge_rows": int(retained_rows),
        "accounted_retained_text_bytes": int(retained_bytes),
        "forward_or_rollback_exact": bool(forward_exact),
        "undo_exact": bool(undo_exact),
        "redo_exact": bool(redo_exact),
    }


def _median_transaction_case(
    *,
    chars: int,
    buffer_count: int,
    samples: int,
    first_write: bool,
    commit: bool,
) -> dict[str, Any]:
    rows = [
        _measure_transaction_once(
            chars=chars,
            buffer_count=buffer_count,
            first_write=first_write,
            commit=commit,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    stable_fields = (
        "document_chars_per_buffer",
        "open_buffers",
        "joined_text_calls",
        "joined_text_chars",
        "old_content_capture_rows",
        "capture_representation",
        "retained_text_charge_rows",
        "accounted_retained_text_bytes",
    )
    for field in stable_fields:
        if any(row[field] != first[field] for row in rows[1:]):
            raise RuntimeError(f"transaction witness field was not stable: {field}")
    return {
        **{field: first[field] for field in stable_fields},
        "samples": len(rows),
        "elapsed_seconds_median": round(
            float(statistics.median(float(row["elapsed_seconds"]) for row in rows)),
            6,
        ),
        "traced_current_bytes_median": int(
            statistics.median(int(row["traced_current_bytes"]) for row in rows)
        ),
        "traced_peak_bytes_median": int(
            statistics.median(int(row["traced_peak_bytes"]) for row in rows)
        ),
        "forward_or_rollback_exact": all(
            bool(row["forward_or_rollback_exact"]) for row in rows
        ),
        "undo_exact": all(bool(row["undo_exact"]) for row in rows),
        "redo_exact": all(bool(row["redo_exact"]) for row in rows),
    }


def _mutation_run(buffer_type: type[Buffer], cycles: int) -> float:
    buffer = buffer_type("a" * 80)
    buffer.fastdirty = True
    cursor = Cursor(0, 40)
    started = time.perf_counter()
    for _ in range(max(1, int(cycles))):
        cursor = buffer.insert(cursor, "x")
        cursor = buffer.delete_range(Cursor(cursor.line, cursor.col - 1), cursor)
    elapsed = time.perf_counter() - started
    if buffer.get_text() != "a" * 80 or cursor != Cursor(0, 40):
        raise RuntimeError("ordinary mutation witness lost exact state")
    return float(elapsed)


def _mutation_hotpath(*, cycles: int, samples: int) -> dict[str, Any]:
    count = max(1, int(samples))
    product: list[float] = []
    rejected: list[float] = []
    reference: list[float] = []
    classes = (
        (_Rev0985MutationBuffer, reference),
        (_PermanentObservedMutationBuffer, rejected),
        (Buffer, product),
    )
    # Warm every code path before taking rotating-order samples.
    warm_cycles = min(5_000, max(1, int(cycles)))
    for buffer_type, _rows in classes:
        _mutation_run(buffer_type, warm_cycles)
    for index in range(count):
        offset = index % len(classes)
        order = classes[offset:] + classes[:offset]
        for buffer_type, rows in order:
            rows.append(_mutation_run(buffer_type, cycles))
    reference_median = float(statistics.median(reference))
    rejected_median = float(statistics.median(rejected))
    product_median = float(statistics.median(product))
    product_ratio = product_median / reference_median if reference_median else 0.0
    rejected_ratio = rejected_median / reference_median if reference_median else 0.0
    return {
        "cycles": max(1, int(cycles)),
        "mutations_per_cycle": 2,
        "samples": count,
        "rev0985_branch_free_control_seconds_median": round(reference_median, 6),
        "rejected_permanent_line_wrapper_seconds_median": round(rejected_median, 6),
        "rev0986_product_seconds_median": round(product_median, 6),
        "rejected_wrapper_to_control_ratio": round(rejected_ratio, 6),
        "rejected_wrapper_overhead_percent": round((rejected_ratio - 1.0) * 100.0, 3),
        "product_to_control_ratio": round(product_ratio, 6),
        "product_overhead_percent": round((product_ratio - 1.0) * 100.0, 3),
        "scope": (
            "single-line insert/delete Python microloop with fastdirty enabled; "
            "not end-to-end editor latency"
        ),
    }


def _reduction_percent(reference: int | float, product: int | float) -> float:
    ref = float(reference)
    if ref <= 0:
        return 0.0
    return round((1.0 - (float(product) / ref)) * 100.0, 3)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    common = {
        "chars": int(args.chars),
        "buffer_count": int(args.buffers),
        "samples": int(args.samples),
    }
    success_reference = _median_transaction_case(
        **common,
        first_write=False,
        commit=True,
    )
    success_product = _median_transaction_case(
        **common,
        first_write=True,
        commit=True,
    )
    failure_reference = _median_transaction_case(
        **common,
        first_write=False,
        commit=False,
    )
    failure_product = _median_transaction_case(
        **common,
        first_write=True,
        commit=False,
    )
    return {
        "schema": SCHEMA,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "measurement_scope": (
            "same-runtime eager reference versus rev0992 line-vector product; "
            "Python tracemalloc only, with fastdirty enabled to isolate "
            "transaction capture"
        ),
        "success": {
            "eager_snapshot_reference": success_reference,
            "first_write_product": success_product,
            "reductions_percent": {
                "joined_text_calls": _reduction_percent(
                    success_reference["joined_text_calls"],
                    success_product["joined_text_calls"],
                ),
                "joined_text_chars": _reduction_percent(
                    success_reference["joined_text_chars"],
                    success_product["joined_text_chars"],
                ),
                "accounted_retained_text_bytes": _reduction_percent(
                    success_reference["accounted_retained_text_bytes"],
                    success_product["accounted_retained_text_bytes"],
                ),
                "traced_peak_bytes_median": _reduction_percent(
                    success_reference["traced_peak_bytes_median"],
                    success_product["traced_peak_bytes_median"],
                ),
                "elapsed_seconds_median": _reduction_percent(
                    success_reference["elapsed_seconds_median"],
                    success_product["elapsed_seconds_median"],
                ),
            },
        },
        "failure": {
            "eager_snapshot_reference": failure_reference,
            "first_write_product": failure_product,
            "reductions_percent": {
                "joined_text_calls": _reduction_percent(
                    failure_reference["joined_text_calls"],
                    failure_product["joined_text_calls"],
                ),
                "joined_text_chars": _reduction_percent(
                    failure_reference["joined_text_chars"],
                    failure_product["joined_text_chars"],
                ),
                "traced_peak_bytes_median": _reduction_percent(
                    failure_reference["traced_peak_bytes_median"],
                    failure_product["traced_peak_bytes_median"],
                ),
                "elapsed_seconds_median": _reduction_percent(
                    failure_reference["elapsed_seconds_median"],
                    failure_product["elapsed_seconds_median"],
                ),
            },
        },
        "ordinary_mutation_hotpath": _mutation_hotpath(
            cycles=int(args.mutation_cycles),
            samples=int(args.mutation_samples),
        ),
        "notes": [
            "Both paths preserve exact forward, rollback, Undo, and Redo semantics; rev0992 replaces complete transaction strings with shallow immutable line vectors.",
            "The eager reference is executable historical control flow in the current runtime, not a shipped product mode.",
            "Joined characters count complete strings returned by Buffer.get_text during the measured transaction only.",
            "Logical retained-byte accounting excludes pointer-vector and Python-object overhead and conservatively charges the after vector's changed middle.",
            "The failure case includes exact in-memory rollback but does not model process crash or durable recovery.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=1_000_000)
    parser.add_argument("--buffers", type=int, default=8)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--mutation-cycles", type=int, default=150_000)
    parser.add_argument("--mutation-samples", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(args)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
