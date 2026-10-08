#!/usr/bin/env python3
"""Compare sparse simultaneous undo with Micromax rev0984's snapshot fallback.

The product case applies one atomic non-overlapping insertion group through the
current editor seam.  ``snapshot_reference`` applies the same planned edits but
records the broad before/after buffer snapshots used by rev0984.  It is an
evidence-only reference, not a second product mode.

Measurements report Python allocations traced by ``tracemalloc`` after each
history is built.  They are not RSS, allocator arenas, native memory, latency
bounds, or a portable process-memory guarantee.  Retained-text accounting is
Micromax's explicit logical UTF-8 charge.

Examples:
  PYTHONPATH=src python tools/measure_simultaneous_history.py
  PYTHONPATH=src python tools/measure_simultaneous_history.py --chars 1100000 --cursors 8 --edits 10 --samples 3
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from collections.abc import Callable, Iterator
from dataclasses import fields, is_dataclass
from typing import Any

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.simultaneous_edits import (
    SimultaneousEditWitness,
    SimultaneousTextEdit,
)

SCHEMA = "micromax.simultaneous-history-retention-witness.v1"


def _walk_values(value: object, *, seen: set[int]) -> Iterator[object]:
    """Walk plain immutable history containers without following editor owners."""

    ident = id(value)
    if ident in seen:
        return
    seen.add(ident)
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_values(key, seen=seen)
            yield from _walk_values(item, seen=seen)
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from _walk_values(item, seen=seen)
    elif isinstance(value, SimultaneousEditWitness):
        for row in value.splices:
            yield from _walk_values(row, seen=seen)
    elif is_dataclass(value) and value.__class__.__module__.endswith("simultaneous_edits"):
        for field in fields(value):
            yield from _walk_values(getattr(value, field.name), seen=seen)


def _history_payload(editor: Editor) -> dict[str, int]:
    strings: dict[int, str] = {}
    witnesses: dict[int, SimultaneousEditWitness] = {}
    for edit in editor.undo.snapshot().undo:
        for callback in (edit.undo, edit.redo):
            for cell in callback.__closure__ or ():
                for value in _walk_values(cell.cell_contents, seen=set()):
                    if isinstance(value, str):
                        strings.setdefault(id(value), value)
                    elif isinstance(value, SimultaneousEditWitness):
                        witnesses.setdefault(id(value), value)
    witness_splices = sum(len(value.splices) for value in witnesses.values())
    witness_text_chars = sum(
        len(text)
        for witness in witnesses.values()
        for row in witness.splices
        for text in (row.old_text, row.new_text)
    )
    return {
        "unique_callback_string_objects": len(strings),
        "unique_callback_string_chars": sum(len(value) for value in strings.values()),
        "max_callback_string_chars": max((len(value) for value in strings.values()), default=0),
        "simultaneous_witnesses": len(witnesses),
        "simultaneous_witness_splices": int(witness_splices),
        "simultaneous_witness_text_chars": int(witness_text_chars),
    }


def _build_editor(*, chars: int, cursor_count: int) -> tuple[Editor, str]:
    count = max(2, int(chars))
    cursors = max(2, int(cursor_count))
    source = "a" * count
    editor = Editor()
    editor.new_buffer("*simultaneous-history*", source)
    editor.set_option_value("undobytes", "0", local=True)
    eb = editor.cur()
    offsets = [
        max(0, min(count, round((index + 1) * count / (cursors + 1))))
        for index in range(cursors)
    ]
    eb.cursors[:] = [Cursor(0, offset) for offset in offsets]
    eb.sel_anchors[:] = [None] * cursors
    eb.cursor_ids[:] = list(range(1, cursors + 1))
    eb.primary = 0
    editor._normalize_cursor_lists(eb)
    return editor, source


def _requests(editor: Editor, edit_index: int) -> list[SimultaneousTextEdit]:
    eb = editor.cur()
    editor._normalize_cursor_lists(eb)
    return [
        SimultaneousTextEdit(
            start=cursor,
            end=cursor,
            text=f"<{int(edit_index):02x}:{int(index):02x}>",
            owner=index,
        )
        for index, cursor in enumerate(eb.cursors)
    ]


def _apply_sparse(editor: Editor, edit_index: int) -> None:
    eb = editor.cur()
    requests = _requests(editor, edit_index)
    result = editor._apply_undoable_simultaneous_buffer_edits(
        eb,
        requests,
        clear_selection_indices=range(len(eb.cursors)),
        description="simultaneous retention witness",
    )
    if not result.changed:
        raise RuntimeError("sparse simultaneous witness made no change")


def _apply_snapshot_reference(editor: Editor, edit_index: int) -> None:
    """Reproduce rev0984's broad immediate multi-cursor history shape."""

    eb = editor.cur()
    requests = _requests(editor, edit_index)
    before = editor._snapshot_undo_buffer_state(eb)
    result = editor._apply_simultaneous_buffer_edits(
        eb,
        requests,
        clear_selection_indices=range(len(eb.cursors)),
    )
    if not result.changed:
        raise RuntimeError("snapshot simultaneous witness made no change")
    after = editor._snapshot_undo_buffer_state(eb)
    editor._record_undo_snapshot(
        eb,
        before,
        after,
        "rev0984 simultaneous snapshot reference",
    )


def _measure_once(
    *,
    chars: int,
    cursor_count: int,
    edits: int,
    apply_edit: Callable[[Editor, int], None],
) -> dict[str, Any]:
    editor, source = _build_editor(chars=chars, cursor_count=cursor_count)
    eb = editor.cur()
    count = max(1, int(edits))

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    for index in range(count):
        apply_edit(editor, index)
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    edited = eb.buf.get_text()
    payload = _history_payload(editor)
    retained = editor.undo.retained_text_bytes(eb)
    if editor.undo.depth() != count:
        raise RuntimeError("history depth differs from requested edit count")

    for _ in range(count):
        if not editor.undo_feedback():
            raise RuntimeError("undo replay unexpectedly failed")
    undo_exact = eb.buf.get_text() == source
    for _ in range(count):
        if not editor.redo_feedback():
            raise RuntimeError("redo replay unexpectedly failed")
    redo_exact = eb.buf.get_text() == edited

    return {
        "document_chars": len(source),
        "cursors": len(eb.cursors),
        "edits": count,
        "elapsed_seconds": round(elapsed, 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "accounted_retained_text_bytes": int(retained),
        "undo_depth": int(editor.undo.depth()),
        "undo_exact": bool(undo_exact),
        "redo_exact": bool(redo_exact),
        **payload,
    }


def _median_case(
    *,
    chars: int,
    cursor_count: int,
    edits: int,
    samples: int,
    apply_edit: Callable[[Editor, int], None],
) -> dict[str, Any]:
    rows = [
        _measure_once(
            chars=chars,
            cursor_count=cursor_count,
            edits=edits,
            apply_edit=apply_edit,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    return {
        "document_chars": int(first["document_chars"]),
        "cursors": int(first["cursors"]),
        "edits": int(first["edits"]),
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
        "accounted_retained_text_bytes": int(first["accounted_retained_text_bytes"]),
        "undo_depth": int(first["undo_depth"]),
        "unique_callback_string_objects": int(first["unique_callback_string_objects"]),
        "unique_callback_string_chars": int(first["unique_callback_string_chars"]),
        "max_callback_string_chars": int(first["max_callback_string_chars"]),
        "simultaneous_witnesses": int(first["simultaneous_witnesses"]),
        "simultaneous_witness_splices": int(first["simultaneous_witness_splices"]),
        "simultaneous_witness_text_chars": int(first["simultaneous_witness_text_chars"]),
        "undo_exact": all(bool(row["undo_exact"]) for row in rows),
        "redo_exact": all(bool(row["redo_exact"]) for row in rows),
    }


def _suppressed_transaction_probe(
    *,
    chars: int,
    cursor_count: int,
    edits: int,
) -> dict[str, Any]:
    """Count redundant local snapshot-helper calls under one aggregate owner.

    Rev0984 already represented suppressed text with a version sentinel, so
    these calls copied cursor/selection/id sidecars but did not retain complete
    document strings when no query-replace session was live.
    """

    editor, source = _build_editor(chars=chars, cursor_count=cursor_count)
    eb = editor.cur()
    snapshot_calls = 0
    original_snapshot = editor._snapshot_undo_buffer_state

    def _counted_snapshot(target):
        nonlocal snapshot_calls
        snapshot_calls += 1
        return original_snapshot(target)

    editor._snapshot_undo_buffer_state = _counted_snapshot  # type: ignore[method-assign]
    count = max(1, int(edits))
    with editor.undo.suppress_recording():
        for index in range(count):
            _apply_sparse(editor, index)

    changed = eb.buf.get_text() != source
    return {
        "document_chars": len(source),
        "cursors": len(eb.cursors),
        "actions": count,
        "local_snapshot_helper_calls": int(snapshot_calls),
        "rev0984_reference_local_snapshot_helper_calls": int(count * 2),
        "rev0984_helper_payload": (
            "version sentinel plus copied cursor/selection/id sidecars; "
            "not full document text when query-replace is absent"
        ),
        "undo_rows_recorded_inside_owner": int(editor.undo.depth()),
        "text_changed": bool(changed),
    }


def _reduction_percent(*, reference: int, current: int) -> float | None:
    if reference <= 0:
        return None
    return round((reference - current) * 100.0 / reference, 3)


def build_report(
    *,
    chars: int,
    cursor_count: int,
    edits: int,
    samples: int,
) -> dict[str, Any]:
    compact = _median_case(
        chars=chars,
        cursor_count=cursor_count,
        edits=edits,
        samples=samples,
        apply_edit=_apply_sparse,
    )
    reference = _median_case(
        chars=chars,
        cursor_count=cursor_count,
        edits=edits,
        samples=samples,
        apply_edit=_apply_snapshot_reference,
    )

    compact_current = int(compact["traced_current_bytes_median"])
    reference_current = int(reference["traced_current_bytes_median"])
    compact_peak = int(compact["traced_peak_bytes_median"])
    reference_peak = int(reference["traced_peak_bytes_median"])
    compact_accounted = int(compact["accounted_retained_text_bytes"])
    reference_accounted = int(reference["accounted_retained_text_bytes"])

    suppressed_probe = _suppressed_transaction_probe(
        chars=min(max(2, int(chars)), 1_100_000),
        cursor_count=cursor_count,
        edits=edits,
    )

    return {
        "schema": SCHEMA,
        "measurement_scope": (
            "Python allocations traced by tracemalloc after history construction; "
            "not RSS/native heap or a hard portable memory bound"
        ),
        "snapshot_reference_scope": (
            "same current simultaneous edit planner with the broad before/after "
            "history snapshots used by Micromax rev0984; evidence only"
        ),
        "sparse_simultaneous_history": compact,
        "rev0984_snapshot_reference": reference,
        "suppressed_aggregate_owner": suppressed_probe,
        "comparison": {
            "traced_current_reduction_bytes": reference_current - compact_current,
            "traced_current_reduction_percent": _reduction_percent(
                reference=reference_current,
                current=compact_current,
            ),
            "traced_peak_reduction_bytes": reference_peak - compact_peak,
            "traced_peak_reduction_percent": _reduction_percent(
                reference=reference_peak,
                current=compact_peak,
            ),
            "accounted_retained_text_reduction_bytes": (
                reference_accounted - compact_accounted
            ),
            "accounted_retained_text_reduction_percent": _reduction_percent(
                reference=reference_accounted,
                current=compact_accounted,
            ),
        },
        "residuals": [
            "planning and replay still materialize complete immutable result text",
            "sidecar and callback object overhead is outside undobytes accounting",
            "query-replace, line-plan, and arbitrary aggregate transactions retain broader snapshots",
        ],
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=4_000_000)
    parser.add_argument("--cursors", type=int, default=8)
    parser.add_argument("--edits", type=int, default=10)
    parser.add_argument("--samples", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    print(
        json.dumps(
            build_report(
                chars=max(2, int(args.chars)),
                cursor_count=max(2, int(args.cursors)),
                edits=max(1, int(args.edits)),
                samples=max(1, int(args.samples)),
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
