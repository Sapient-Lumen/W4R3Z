#!/usr/bin/env python3
"""Measure sparse query-replace history against the rev0988 broad shape.

Planning is deliberately excluded.  Each case begins with the first immutable
planned match already selected, then measures answer/finalization work with
``fastdirty`` enabled so exact dirty hashing does not obscure the delayed-
interaction path under study.

``rev0988_broad_reference`` is an evidence-only reproduction using the current
buffer primitive plus rev0988's two cursor-to-offset scans, whole-buffer
validation/owned-generation materializations, whole-buffer index-to-cursor
conversions, and broad before/after undo snapshots.  It is not a product mode.

Examples:
  PYTHONPATH=src python tools/measure_qreplace_history.py
  PYTHONPATH=src python tools/measure_qreplace_history.py --chars 1100000 --matches 128 --samples 1
  PYTHONPATH=src python tools/measure_qreplace_history.py --json-out report.json
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from collections.abc import Iterator
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

from micromax_editor.buffer import Cursor, normalize_buffer_text
from micromax_editor.editor import BufferSidecarSnapshot, Editor, QueryReplaceSession
from micromax_editor.query_replace import QueryReplaceSourceSnapshot
from micromax_editor.simultaneous_edits import (
    SimultaneousEditWitness,
    SimultaneousTextEdit,
)
from micromax_editor.textpos import cursor_to_index, index_to_cursor

SCHEMA = "micromax.qreplace-history-measurement.v1"
TOKEN = "needle"
REPLACEMENT = "X\nY"


def _gap(length: int) -> str:
    """Return deterministic multiline filler containing no search token."""

    count = max(0, int(length))
    line = "a" * 79 + "\n"
    whole, tail = divmod(count, len(line))
    return line * whole + "a" * tail


def _source(*, chars: int, matches: int) -> str:
    """Build approximately ``chars`` characters with exactly ``matches`` hits."""

    match_count = max(1, int(matches))
    target = max(match_count * len(TOKEN), int(chars))
    filler = max(0, target - match_count * len(TOKEN))
    base, remainder = divmod(filler, match_count + 1)
    parts: list[str] = []
    for index in range(match_count):
        parts.append(_gap(base + (1 if index < remainder else 0)))
        parts.append(TOKEN)
    parts.append(_gap(base + (1 if match_count < remainder else 0)))
    result = "".join(parts)
    if result.count(TOKEN) != match_count:
        raise RuntimeError("measurement source contains an unexpected match count")
    return result


def _clone_sidecars(snapshot: BufferSidecarSnapshot) -> BufferSidecarSnapshot:
    cursors, anchors, cursor_ids, primary = snapshot
    return (
        [Cursor(int(cursor.line), int(cursor.col)) for cursor in cursors],
        [
            Cursor(int(anchor.line), int(anchor.col)) if anchor is not None else None
            for anchor in anchors
        ],
        [int(value) for value in cursor_ids],
        int(primary),
    )


def _snapshot_from_sidecars(
    text: str,
    sidecars: BufferSidecarSnapshot,
) -> tuple[str, list[Cursor], list[Cursor | None], list[int], int]:
    cursors, anchors, cursor_ids, primary = _clone_sidecars(sidecars)
    return str(text), cursors, anchors, cursor_ids, primary


def _build_editor(*, chars: int, matches: int) -> tuple[Editor, str]:
    source = _source(chars=chars, matches=matches)
    editor = Editor()
    editor.new_buffer("*qreplace-history*", source)
    editor.set_option_value("undobytes", "0", local=True)
    eb = editor.cur()
    # Isolate query-replace from exact dirty hashing. Saved buffers at or above
    # Micromax's large-buffer threshold select this visible mode automatically.
    eb.buf.fastdirty = True
    if not editor.begin_query_replace(TOKEN, REPLACEMENT, literal=True):
        raise RuntimeError("query-replace planning unexpectedly failed")
    if editor.qreplace is None or editor.qreplace.match_start is None:
        raise RuntimeError("query-replace did not select its first planned match")
    return editor, source


def _walk_values(value: object, *, seen: set[int]) -> Iterator[object]:
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
    elif is_dataclass(value) and value.__class__.__module__.endswith(
        "simultaneous_edits"
    ):
        for field in fields(value):
            yield from _walk_values(getattr(value, field.name), seen=seen)


def _history_payload(editor: Editor, *, document_chars: int) -> dict[str, int]:
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
    threshold = max(1, int(document_chars * 0.9))
    return {
        "unique_callback_string_objects": len(strings),
        "unique_callback_string_chars": sum(len(value) for value in strings.values()),
        "max_callback_string_chars": max((len(value) for value in strings.values()), default=0),
        "full_document_callback_generations": sum(
            1 for value in strings.values() if len(value) >= threshold
        ),
        "simultaneous_witnesses": len(witnesses),
        "simultaneous_witness_splices": sum(
            len(value.splices) for value in witnesses.values()
        ),
        "simultaneous_witness_text_chars": sum(
            len(text)
            for witness in witnesses.values()
            for row in witness.splices
            for text in (row.old_text, row.new_text)
        ),
    }


def _select_next_like_rev0988(
    editor: Editor,
    sess: QueryReplaceSession,
) -> None:
    """Install one next match with rev0988's broad conversion shape."""

    eb = editor.cur()
    planned = sess.planned_matches[sess.planned_index]
    start_index = int(planned.start) + int(sess.coordinate_delta)
    end_index = int(planned.end) + int(sess.coordinate_delta)
    text = eb.buf.get_text()
    source_snapshot = sess.source_snapshot
    if not isinstance(source_snapshot, QueryReplaceSourceSnapshot):
        raise RuntimeError("rev0988 reference has no source generation")
    planned_start = int(planned.start)
    planned_end = int(planned.end)
    planned_old = source_snapshot.range_text_offsets(planned_start, planned_end)
    if not (
        0 <= planned_start < planned_end <= source_snapshot.length
        and 0 <= start_index < end_index <= len(text)
        and text[start_index:end_index] == planned_old
    ):
        raise RuntimeError("rev0988 reference match coordinates drifted")

    match_start = index_to_cursor(eb.buf, start_index)
    match_end = index_to_cursor(eb.buf, end_index)
    sess.planned_index += 1
    sess.match_start = match_start
    sess.match_end = match_end
    sess.match_repl = str(planned.new)
    sess.match_old = planned_old
    sess.match_source_start = planned_start
    sess.match_source_end = planned_end
    sess.match_current_start = start_index
    sess.match_source_length = planned_end - planned_start
    sess.next_start = Cursor(match_end.line, match_end.col)
    sess.examined += 1

    editor._normalize_cursor_lists(eb)
    primary = int(eb.primary)
    eb.sel_anchors[primary] = Cursor(match_start.line, match_start.col)
    eb.cursors[primary] = Cursor(match_end.line, match_end.col)


def _apply_current_like_rev0988(
    editor: Editor,
    sess: QueryReplaceSession,
) -> str:
    """Apply the selected row and return rev0988's owned full generation."""

    eb = editor.cur()
    if sess.match_start is None or sess.match_end is None:
        raise RuntimeError("rev0988 reference has no selected match")
    start_index = cursor_to_index(eb.buf, sess.match_start)
    end_index = cursor_to_index(eb.buf, sess.match_end)
    if eb.buf.get_text()[start_index:end_index] != sess.match_old:
        raise RuntimeError("rev0988 reference current match drifted")

    replacement = normalize_buffer_text(sess.match_repl)
    editor._normalize_cursor_lists(eb)
    primary = int(eb.primary)
    result = editor._apply_simultaneous_buffer_edits(
        eb,
        [
            SimultaneousTextEdit(
                start=sess.match_start,
                end=sess.match_end,
                text=replacement,
                owner=primary,
            )
        ],
        clear_selection_indices=[primary],
    )
    cursor = eb.cursors[eb.primary]
    sess.coordinate_delta += len(replacement) - int(sess.match_source_length)
    sess.replaced += 1
    sess.next_start = Cursor(cursor.line, cursor.col)
    editor._qreplace_refresh_generation(sess, eb)
    owned_text = eb.buf.get_text()
    if result.text_changed:
        editor._note_buffer_changed(eb, script_context=False)
    return owned_text


def _run_rev0988_broad_reference(editor: Editor) -> None:
    """Finish the active interaction with rev0988's retained/history shape."""

    eb = editor.cur()
    sess = editor.qreplace
    if sess is None or sess.before_sidecars is None:
        raise RuntimeError("rev0988 reference has no active session boundary")
    source_snapshot = sess.source_snapshot
    if not isinstance(source_snapshot, QueryReplaceSourceSnapshot):
        raise RuntimeError("rev0988 reference has no source generation")
    before = _snapshot_from_sidecars(
        source_snapshot.materialize_text(),
        sess.before_sidecars,
    )
    owned_text: str | None = None

    while True:
        owned_text = _apply_current_like_rev0988(editor, sess)
        if sess.planned_index >= len(sess.planned_matches):
            editor._normalize_cursor_lists(eb)
            eb.sel_anchors[eb.primary] = None
            after = editor._snapshot_buffer_state(eb)
            editor.qreplace = None
            editor._drop_qreplace_capture_modes()
            editor._record_undo_snapshot(
                eb,
                before,
                after,
                "rev0988 qreplace broad snapshot reference",
                finalize_qreplace=False,
            )
            owned_text = None
            return
        _select_next_like_rev0988(editor, sess)


def _measure_once(*, chars: int, matches: int, broad_reference: bool) -> dict[str, Any]:
    editor, source = _build_editor(chars=chars, matches=matches)
    eb = editor.cur()
    expected = source.replace(TOKEN, REPLACEMENT)
    original_get_text = eb.buf.get_text

    # Move the session's shallow line/coordinate witness into the traced
    # allocation domain. The first selected match remains valid because this is
    # an equal immutable source generation.
    gc.collect()
    tracemalloc.start()
    sess = editor.qreplace
    if sess is None:
        raise RuntimeError("query-replace session disappeared before measurement")
    sess.source_snapshot = QueryReplaceSourceSnapshot.capture(
        eb.buf.snapshot_lines()
    )
    del sess
    gc.collect()
    tracemalloc.reset_peak()

    materializations = 0
    materialized_chars = 0
    longest_materialization = 0

    def _counted_get_text() -> str:
        nonlocal materializations, materialized_chars, longest_materialization
        value = original_get_text()
        materializations += 1
        materialized_chars += len(value)
        longest_materialization = max(longest_materialization, len(value))
        return value

    eb.buf.get_text = _counted_get_text  # type: ignore[method-assign]
    started = time.perf_counter()
    if broad_reference:
        _run_rev0988_broad_reference(editor)
    elif not editor.qreplace_all():
        raise RuntimeError("sparse query-replace unexpectedly failed")
    elapsed = time.perf_counter() - started
    eb.buf.get_text = original_get_text  # type: ignore[method-assign]

    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    edited = original_get_text()
    payload = _history_payload(editor, document_chars=max(len(source), len(edited)))
    retained = editor.undo.retained_text_bytes(eb)
    if editor.qreplace is not None:
        raise RuntimeError("query-replace session remained active")
    if editor.undo.depth() != 1:
        raise RuntimeError("query-replace did not produce exactly one undo row")
    if edited != expected:
        raise RuntimeError("query-replace produced unexpected text")

    if not editor.undo_feedback():
        raise RuntimeError("query-replace undo unexpectedly failed")
    undo_exact = original_get_text() == source
    if not editor.redo_feedback():
        raise RuntimeError("query-replace redo unexpectedly failed")
    redo_exact = original_get_text() == expected

    return {
        "document_chars": len(source),
        "matches": max(1, int(matches)),
        "replacement_chars": len(REPLACEMENT),
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": int(current),
        "traced_peak_bytes": int(peak),
        "answer_full_document_materializations": int(materializations),
        "answer_full_document_materialized_chars": int(materialized_chars),
        "longest_answer_materialization_chars": int(longest_materialization),
        "accounted_retained_text_bytes": int(retained),
        "undo_depth": int(editor.undo.depth()),
        "undo_exact": bool(undo_exact),
        "redo_exact": bool(redo_exact),
        **payload,
    }


def _median_case(
    *,
    chars: int,
    matches: int,
    samples: int,
    broad_reference: bool,
) -> dict[str, Any]:
    rows = [
        _measure_once(
            chars=chars,
            matches=matches,
            broad_reference=broad_reference,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    stable_keys = {
        "document_chars",
        "matches",
        "replacement_chars",
        "answer_full_document_materializations",
        "answer_full_document_materialized_chars",
        "longest_answer_materialization_chars",
        "accounted_retained_text_bytes",
        "undo_depth",
        "unique_callback_string_objects",
        "unique_callback_string_chars",
        "max_callback_string_chars",
        "full_document_callback_generations",
        "simultaneous_witnesses",
        "simultaneous_witness_splices",
        "simultaneous_witness_text_chars",
        "undo_exact",
        "redo_exact",
    }
    for row in rows[1:]:
        if any(row[key] != first[key] for key in stable_keys):
            raise RuntimeError("query-replace measurement shape changed between samples")
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


def build_report(*, chars: int, matches: int, samples: int = 1) -> dict[str, Any]:
    sparse = _median_case(
        chars=chars,
        matches=matches,
        samples=samples,
        broad_reference=False,
    )
    reference = _median_case(
        chars=chars,
        matches=matches,
        samples=samples,
        broad_reference=True,
    )
    return {
        "schema": SCHEMA,
        "method": {
            "planning": "excluded; first immutable planned match selected before tracing",
            "dirty_tracking": "fastdirty enabled to isolate delayed-interaction work",
            "product": "current sparse accepted-slice journal and local cursor rebasing",
            "reference": (
                "evidence-only reproduction of rev0988 answer materializations, "
                "coordinate conversions, and broad before/after history"
            ),
            "memory": "Python allocations traced by tracemalloc; not RSS/native heap",
            "timing": "local elapsed context only; not a portable benchmark bound",
        },
        "sparse_query_replace": sparse,
        "rev0988_broad_reference": reference,
        "comparison": {
            "answer_materialization_reduction_percent": _reduction_percent(
                reference=int(reference["answer_full_document_materializations"]),
                product=int(sparse["answer_full_document_materializations"]),
            ),
            "materialized_character_reduction_percent": _reduction_percent(
                reference=int(reference["answer_full_document_materialized_chars"]),
                product=int(sparse["answer_full_document_materialized_chars"]),
            ),
            "accounted_retained_text_reduction_percent": _reduction_percent(
                reference=int(reference["accounted_retained_text_bytes"]),
                product=int(sparse["accounted_retained_text_bytes"]),
            ),
            "traced_current_reduction_percent": _reduction_percent(
                reference=int(reference["traced_current_bytes_median"]),
                product=int(sparse["traced_current_bytes_median"]),
            ),
            "traced_peak_reduction_percent": _reduction_percent(
                reference=int(reference["traced_peak_bytes_median"]),
                product=int(sparse["traced_peak_bytes_median"]),
            ),
            "reference_materialization_formula_holds": (
                int(reference["answer_full_document_materializations"])
                == 5 * int(reference["matches"]) - 2
            ),
            "product_has_no_answer_materializations": (
                int(sparse["answer_full_document_materializations"]) == 0
            ),
            "both_roundtrip_exact": bool(
                sparse["undo_exact"]
                and sparse["redo_exact"]
                and reference["undo_exact"]
                and reference["redo_exact"]
            ),
        },
        "residuals": [
            "rev0999 regex planning stages one private exact-text file; this history witness does not measure the child string or file/page-cache charge",
            "the delayed source witness retains O(lines) pointers and compact offsets",
            "exact dirty mode may hash a small buffer after each accepted mutation",
            "elapsed and tracemalloc figures are machine- and interpreter-specific",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=1_100_000)
    parser.add_argument("--matches", type=int, default=128)
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = build_report(
        chars=max(1, int(args.chars)),
        matches=max(1, int(args.matches)),
        samples=max(1, int(args.samples)),
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
