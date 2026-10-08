#!/usr/bin/env python3
"""Measure bounded typing-history groups against rev0987 independent rows.

The reference path disables only the rev0988 grouping witness and otherwise
uses the current editor, buffer, action, compact-splice, accounting, and replay
code.  ``tracemalloc`` reports Python allocations, not RSS or native heap.
Elapsed time is included as local context, not as a portable benchmark claim.

Examples:
  PYTHONPATH=src python tools/measure_typing_history.py
  PYTHONPATH=src python tools/measure_typing_history.py --chars 10000 --samples 1
  PYTHONPATH=src python tools/measure_typing_history.py --json-out report.json
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any

from micromax_editor.buffer import Cursor
from micromax_editor.editor import (
    Editor,
    TYPING_HISTORY_GROUP_MAX_CHARS,
    TypingHistorySpan,
)

SCHEMA = "micromax.typing-history-measurement.v1"


class _IndependentTypingRowsEditor(Editor):
    """Current runtime with only automatic typing grouping disabled."""

    def _typing_history_span_for_splice(self, *args: Any, **kwargs: Any) -> None:
        return None


def _history_shape(editor: Editor) -> dict[str, Any]:
    rows = editor.undo.snapshot().undo
    sidecars: set[int] = set()
    callback_closure_cells = 0
    group_sizes: list[int] = []

    for row in rows:
        for callback in (row.undo, row.redo):
            callback_closure_cells += len(callback.__closure__ or ())
        span = row.history_group
        if isinstance(span, TypingHistorySpan):
            sidecars.add(id(span.before_sidecars))
            sidecars.add(id(span.after_sidecars))
            group_sizes.append(len(span.old_text) + len(span.new_text))
            continue
        for callback in (row.undo, row.redo):
            for cell in callback.__closure__ or ():
                value = cell.cell_contents
                if (
                    isinstance(value, tuple)
                    and len(value) == 4
                    and isinstance(value[0], list)
                    and isinstance(value[1], list)
                    and isinstance(value[2], list)
                ):
                    sidecars.add(id(value))

    return {
        "undo_rows": len(rows),
        "retained_sidecar_snapshots": len(sidecars),
        "undo_redo_callback_closure_cells": int(callback_closure_cells),
        "typing_group_rows": len(group_sizes),
        "max_typing_group_chars": max(group_sizes, default=0),
        "min_typing_group_chars": min(group_sizes, default=0),
    }


def _measure_once(*, chars: int, grouped: bool) -> dict[str, Any]:
    count = max(1, int(chars))
    editor: Editor = Editor() if grouped else _IndependentTypingRowsEditor()
    editor.new_buffer("*typing-history*", "")
    editor._now_fn = lambda: 0.0
    buffer = editor.cur()

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    for _ in range(count):
        editor.input["text"] = "x"
        if not editor.run_action("InsertText"):
            raise RuntimeError("InsertText unexpectedly failed")
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    expected_depth = (
        (count + TYPING_HISTORY_GROUP_MAX_CHARS - 1)
        // TYPING_HISTORY_GROUP_MAX_CHARS
        if grouped
        else count
    )
    if buffer.buf.get_text() != "x" * count:
        raise RuntimeError("typed text differs from the expected witness")
    if editor.undo.depth() != expected_depth:
        raise RuntimeError(
            f"unexpected undo depth: {editor.undo.depth()} != {expected_depth}"
        )
    if editor.undo.retained_text_bytes(buffer) != count:
        raise RuntimeError("logical retained-text accounting is not exact")

    shape = _history_shape(editor)
    for _ in range(expected_depth):
        if not editor.undo.undo():
            raise RuntimeError("undo replay unexpectedly failed")
    if buffer.buf.get_text() != "" or editor.primary_cursor() != Cursor(0, 0):
        raise RuntimeError("undo did not restore the exact initial state")
    for _ in range(expected_depth):
        if not editor.undo.redo():
            raise RuntimeError("redo replay unexpectedly failed")
    if buffer.buf.get_text() != "x" * count or editor.primary_cursor() != Cursor(0, count):
        raise RuntimeError("redo did not restore the exact typed state")

    return {
        "typed_chars": count,
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "logical_retained_text_bytes": int(editor.undo.retained_text_bytes(buffer)),
        "roundtrip_exact": True,
        **shape,
    }


def _median_measurement(*, chars: int, grouped: bool, samples: int) -> dict[str, Any]:
    rows = [
        _measure_once(chars=chars, grouped=grouped)
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    stable_keys = {
        "typed_chars",
        "logical_retained_text_bytes",
        "undo_rows",
        "retained_sidecar_snapshots",
        "undo_redo_callback_closure_cells",
        "typing_group_rows",
        "max_typing_group_chars",
        "min_typing_group_chars",
        "roundtrip_exact",
    }
    for row in rows[1:]:
        if any(row[key] != first[key] for key in stable_keys):
            raise RuntimeError("measurement shape changed between samples")
    return {
        **{key: first[key] for key in stable_keys},
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
    }


def _reduction_percent(*, reference: int, product: int) -> float | None:
    if reference <= 0:
        return None
    return round((reference - product) * 100.0 / reference, 3)


def build_report(*, chars: int, samples: int = 1) -> dict[str, Any]:
    independent = _median_measurement(
        chars=chars,
        grouped=False,
        samples=samples,
    )
    grouped = _median_measurement(
        chars=chars,
        grouped=True,
        samples=samples,
    )
    return {
        "schema": SCHEMA,
        "method": {
            "clock": "constant monotonic timestamp; every keystroke is adjacent in time",
            "reference": "current compact-splice path with only rev0988 grouping disabled",
            "memory": "Python allocations traced after editor/buffer construction; not RSS",
            "timing": "local elapsed context only; not a portable benchmark claim",
            "group_max_chars": TYPING_HISTORY_GROUP_MAX_CHARS,
        },
        "independent_rows_reference": independent,
        "bounded_typing_groups": grouped,
        "comparison": {
            "undo_row_reduction_percent": _reduction_percent(
                reference=int(independent["undo_rows"]),
                product=int(grouped["undo_rows"]),
            ),
            "sidecar_snapshot_reduction_percent": _reduction_percent(
                reference=int(independent["retained_sidecar_snapshots"]),
                product=int(grouped["retained_sidecar_snapshots"]),
            ),
            "callback_closure_cell_reduction_percent": _reduction_percent(
                reference=int(independent["undo_redo_callback_closure_cells"]),
                product=int(grouped["undo_redo_callback_closure_cells"]),
            ),
            "traced_current_reduction_percent": _reduction_percent(
                reference=int(independent["traced_current_bytes_median"]),
                product=int(grouped["traced_current_bytes_median"]),
            ),
            "traced_peak_reduction_percent": _reduction_percent(
                reference=int(independent["traced_peak_bytes_median"]),
                product=int(grouped["traced_peak_bytes_median"]),
            ),
            "logical_retained_text_bytes_equal": (
                independent["logical_retained_text_bytes"]
                == grouped["logical_retained_text_bytes"]
            ),
            "both_roundtrip_exact": bool(
                independent["roundtrip_exact"] and grouped["roundtrip_exact"]
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=10_000)
    parser.add_argument("--samples", type=int, default=1)
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
