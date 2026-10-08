#!/usr/bin/env python3
"""Compare compact splice undo with the prior full-snapshot edit shape.

The witness isolates Micromax's ordinary one-cursor typing path.  It reports
Python allocations traced by ``tracemalloc``; it is not an RSS, native-heap,
allocator, or cross-platform memory bound.  The newly allocated live edited
line is included in ``traced_current_bytes`` because Python strings are
immutable.

``snapshot_reference`` reproduces the rev0982 action shape inside the current
runtime: snapshot full text, apply the same one-cursor splice, snapshot full
text again, then retain both snapshots in one undo row.  It is a reference
measurement, not a second product path.

Examples:
  PYTHONPATH=src python tools/measure_undo_retention.py
  PYTHONPATH=src python tools/measure_undo_retention.py --chars 1100000 --edits 10 --samples 3
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from collections.abc import Callable, Iterator
from typing import Any

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.simultaneous_edits import SimultaneousTextEdit

SCHEMA = "micromax.undo-retention-witness.v1"


def _container_strings(value: object) -> Iterator[str]:
    """Yield strings held through plain callback-closure containers."""

    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _container_strings(key)
            yield from _container_strings(item)
        return
    if isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from _container_strings(item)


def _max_history_closure_string_chars(editor: Editor) -> int:
    longest = 0
    for edit in editor.undo.snapshot().undo:
        for callback in (edit.undo, edit.redo):
            for cell in callback.__closure__ or ():
                for value in _container_strings(cell.cell_contents):
                    longest = max(longest, len(value))
    return int(longest)


def _apply_compact_splice(editor: Editor, _index: int) -> None:
    # This older witness measures one independent compact row per edit.  Keep
    # its comparison stable now that normal sub-500 ms typing intentionally
    # coalesces; the dedicated typing-history witness measures that product path.
    editor._now_fn = lambda: float(_index)
    editor.input["text"] = "x"
    if not editor.run_action("InsertText"):
        raise RuntimeError("InsertText unexpectedly failed")


def _apply_snapshot_reference(editor: Editor, _index: int) -> None:
    """Apply one edit with the full before/after snapshot shape from rev0982."""

    buffer = editor.cur()
    before = editor._snapshot_undo_buffer_state(buffer)
    cursor = buffer.cursors[0]
    result = editor._apply_simultaneous_buffer_edits(
        buffer,
        [
            SimultaneousTextEdit(
                start=cursor,
                end=cursor,
                text="x",
                owner=0,
            )
        ],
        clear_selection_indices=[0],
    )
    if not result.changed:
        raise RuntimeError("snapshot reference edit unexpectedly made no change")
    after = editor._snapshot_undo_buffer_state(buffer)
    editor._record_undo_snapshot(buffer, before, after, "insert 1")


def _measure_case(
    *,
    chars: int,
    edits: int,
    apply_edit: Callable[[Editor, int], None],
) -> dict[str, Any]:
    char_count = max(1, int(chars))
    edit_count = max(1, int(edits))
    source = "a" * char_count
    editor = Editor()
    editor.new_buffer("*undo-retention*", source)
    buffer = editor.cur()
    insertion_col = char_count // 2
    buffer.cursors[0] = Cursor(0, insertion_col)

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    for index in range(edit_count):
        apply_edit(editor, index)
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    expected = source[:insertion_col] + ("x" * edit_count) + source[insertion_col:]
    if buffer.buf.get_text() != expected:
        raise RuntimeError("edited text differs from the expected witness")
    if editor.undo.depth() != edit_count:
        raise RuntimeError("undo depth differs from the edit count")

    max_closure_string_chars = _max_history_closure_string_chars(editor)
    for _ in range(edit_count):
        if not editor.undo_feedback():
            raise RuntimeError("undo replay unexpectedly failed")
    if buffer.buf.get_text() != source:
        raise RuntimeError("undo did not restore the exact source")
    for _ in range(edit_count):
        if not editor.redo_feedback():
            raise RuntimeError("redo replay unexpectedly failed")
    if buffer.buf.get_text() != expected:
        raise RuntimeError("redo did not restore the exact edited text")

    return {
        "document_chars": char_count,
        "edits": edit_count,
        "fastdirty": bool(buffer.buf.fastdirty),
        "elapsed_seconds": round(elapsed, 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "undo_depth": int(editor.undo.depth()),
        "max_history_closure_string_chars": max_closure_string_chars,
        "roundtrip_exact": True,
    }


def _median_case(
    *,
    chars: int,
    edits: int,
    samples: int,
    apply_edit: Callable[[Editor, int], None],
) -> dict[str, Any]:
    rows = [
        _measure_case(chars=chars, edits=edits, apply_edit=apply_edit)
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    return {
        "document_chars": int(first["document_chars"]),
        "edits": int(first["edits"]),
        "samples": len(rows),
        "fastdirty": bool(first["fastdirty"]),
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
        "undo_depth": int(first["undo_depth"]),
        "max_history_closure_string_chars": max(
            int(row["max_history_closure_string_chars"]) for row in rows
        ),
        "roundtrip_exact": all(bool(row["roundtrip_exact"]) for row in rows),
    }


def _strategy_report(
    *,
    chars: int,
    edits: int,
    samples: int,
    apply_edit: Callable[[Editor, int], None],
) -> dict[str, Any]:
    edit_count = max(2, int(edits))
    one = _median_case(
        chars=chars,
        edits=1,
        samples=samples,
        apply_edit=apply_edit,
    )
    many = _median_case(
        chars=chars,
        edits=edit_count,
        samples=samples,
        apply_edit=apply_edit,
    )
    additional = edit_count - 1
    retained_growth = int(many["traced_current_bytes_median"]) - int(
        one["traced_current_bytes_median"]
    )
    return {
        "one_edit": one,
        "many_edits": many,
        "additional_history": {
            "edits": additional,
            "traced_current_growth_bytes": retained_growth,
            "growth_bytes_per_additional_edit": round(
                retained_growth / additional,
                3,
            ),
        },
    }


def _reduction_percent(*, old: int, new: int) -> float | None:
    if old <= 0:
        return None
    return round((old - new) * 100.0 / old, 3)


def build_report(*, chars: int, edits: int, samples: int = 5) -> dict[str, Any]:
    compact = _strategy_report(
        chars=chars,
        edits=edits,
        samples=samples,
        apply_edit=_apply_compact_splice,
    )
    snapshot = _strategy_report(
        chars=chars,
        edits=edits,
        samples=samples,
        apply_edit=_apply_snapshot_reference,
    )

    compact_many = int(compact["many_edits"]["traced_current_bytes_median"])
    snapshot_many = int(snapshot["many_edits"]["traced_current_bytes_median"])
    compact_peak = int(compact["many_edits"]["traced_peak_bytes_median"])
    snapshot_peak = int(snapshot["many_edits"]["traced_peak_bytes_median"])
    compact_history = int(
        compact["additional_history"]["traced_current_growth_bytes"]
    )
    snapshot_history = int(
        snapshot["additional_history"]["traced_current_growth_bytes"]
    )

    return {
        "schema": SCHEMA,
        "measurement_scope": (
            "Python allocations traced by tracemalloc; includes the newly allocated "
            "live document, not RSS or total/native heap"
        ),
        "snapshot_reference_scope": (
            "replays the rev0982 full before/after text snapshot shape using the "
            "current buffer splice primitive; it is evidence only"
        ),
        "compact_splice": compact,
        "snapshot_reference": snapshot,
        "comparison": {
            "many_edit_current_reduction_bytes": snapshot_many - compact_many,
            "many_edit_current_reduction_percent": _reduction_percent(
                old=snapshot_many,
                new=compact_many,
            ),
            "many_edit_peak_reduction_bytes": snapshot_peak - compact_peak,
            "many_edit_peak_reduction_percent": _reduction_percent(
                old=snapshot_peak,
                new=compact_peak,
            ),
            "additional_history_reduction_bytes": snapshot_history - compact_history,
            "additional_history_reduction_percent": _reduction_percent(
                old=snapshot_history,
                new=compact_history,
            ),
        },
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=4_000_000)
    parser.add_argument("--edits", type=int, default=10)
    parser.add_argument("--samples", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    print(
        json.dumps(
            build_report(
                chars=args.chars,
                edits=args.edits,
                samples=args.samples,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
