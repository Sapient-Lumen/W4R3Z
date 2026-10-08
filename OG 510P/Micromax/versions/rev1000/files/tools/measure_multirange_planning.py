#!/usr/bin/env python3
"""Measure genuine multi-range planning before and after line-vector application.

This is a local allocation-shape witness, not a portable latency benchmark. It
compares the exact rev0990 flat-document planning/publication shape with the
rev0991 product line-vector path over one immutable source generation.

Examples:
  PYTHONPATH=src python tools/measure_multirange_planning.py
  PYTHONPATH=src python tools/measure_multirange_planning.py --samples 3
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import statistics
import time
import tracemalloc
from collections.abc import Iterable, Sequence
from typing import Any

from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.simultaneous_edits import (
    SimultaneousEditWitness,
    SimultaneousTextEdit,
    cursor_to_offset,
    cursor_to_offset_lines,
    line_start_offsets,
    line_start_offsets_for_lines,
    offset_to_cursor,
    offset_to_cursor_lines,
    plan_simultaneous_edits,
    plan_simultaneous_edits_lines,
    replay_simultaneous_edit_witness_lines,
)

SCHEMA = "micromax.line-vector-multirange-planning-measurement.v1"


class _CountingBuffer(Buffer):
    """Count complete-text and line-vector publication calls."""

    def __init__(self, text: str) -> None:
        self.full_text_reads = 0
        self.full_text_read_chars = 0
        self.full_text_writes = 0
        self.full_text_write_chars = 0
        self.line_vector_writes = 0
        super().__init__(text)
        self.set_fastdirty(True)
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
        value = str(text)
        self.full_text_writes += 1
        self.full_text_write_chars += len(value)
        super().set_text(value)

    def replace_lines(self, lines: Iterable[str]) -> None:
        self.line_vector_writes += 1
        super().replace_lines(lines)


def _fixture(
    *,
    line_count: int,
    line_width: int,
    edit_count: int,
) -> tuple[
    tuple[str, ...],
    tuple[SimultaneousTextEdit, ...],
    tuple[Cursor, ...],
    tuple[Cursor | None, ...],
]:
    width = max(24, int(line_width))
    lines = tuple(
        f"{index:08d}:" + ("a" * max(1, width - 9))
        for index in range(max(2, int(line_count)))
    )
    count = max(2, min(int(edit_count), len(lines) - 1))
    requests: list[SimultaneousTextEdit] = []
    cursors: list[Cursor] = []
    anchors: list[Cursor | None] = []
    for index in range(count):
        line = max(
            0,
            min(
                len(lines) - 1,
                round((index + 1) * (len(lines) - 1) / (count + 1)),
            ),
        )
        col = min(12, len(lines[line]) - 2)
        requests.append(
            SimultaneousTextEdit(
                Cursor(line, col),
                Cursor(line, col + 1),
                f"<{index:03x}>",
                owner=index,
            )
        )
        cursors.append(Cursor(line, col + 1))
        anchors.append(Cursor(line, max(0, col - 2)))

    # Passive sidecars exercise ordinary position mapping in addition to owner
    # placement. They have no corresponding requested edit.
    cursors.extend(
        (
            Cursor(0, 0),
            Cursor(len(lines) // 2, len(lines[len(lines) // 2]) // 2),
            Cursor(len(lines) - 1, len(lines[-1])),
        )
    )
    anchors.extend((None, Cursor(0, 1), Cursor(len(lines) - 1, 0)))
    return lines, tuple(requests), tuple(cursors), tuple(anchors)


def _mapped_sidecars_flat(
    *,
    source_text: str,
    requests: Sequence[SimultaneousTextEdit],
    cursors: Sequence[Cursor],
    anchors: Sequence[Cursor | None],
    buffer: _CountingBuffer,
) -> tuple[SimultaneousEditWitness, tuple[Cursor, ...], tuple[Cursor | None, ...]]:
    source_starts = line_start_offsets(source_text)
    cursor_offsets = tuple(
        cursor_to_offset(source_text, source_starts, cursor) for cursor in cursors
    )
    anchor_offsets = tuple(
        cursor_to_offset(source_text, source_starts, anchor)
        if anchor is not None
        else None
        for anchor in anchors
    )
    plan = plan_simultaneous_edits(
        source_text,
        requests,
        source_starts=source_starts,
    )
    witness = plan.compact_history_witness()
    if plan.text_changed:
        buffer.set_text(plan.new_text)

    result_starts = line_start_offsets(plan.new_text)
    owner_offsets = dict(plan.owner_offsets)
    mapped_cursor_rows: list[Cursor] = []
    for index, source_offset in enumerate(cursor_offsets):
        result_offset = owner_offsets.get(index)
        if result_offset is None:
            result_offset = plan.map_offset(source_offset)
        mapped_cursor_rows.append(
            offset_to_cursor(plan.new_text, result_starts, result_offset)
        )
    mapped_cursors = tuple(mapped_cursor_rows)
    mapped_anchors = tuple(
        offset_to_cursor(
            plan.new_text,
            result_starts,
            plan.map_offset(offset),
        )
        if offset is not None
        else None
        for offset in anchor_offsets
    )
    return witness, mapped_cursors, mapped_anchors


def _mapped_sidecars_lines(
    *,
    source_lines: Sequence[str],
    requests: Sequence[SimultaneousTextEdit],
    cursors: Sequence[Cursor],
    anchors: Sequence[Cursor | None],
    buffer: _CountingBuffer,
) -> tuple[SimultaneousEditWitness, tuple[Cursor, ...], tuple[Cursor | None, ...]]:
    snapshot = tuple(str(line) for line in source_lines) or ("",)
    source_starts = line_start_offsets_for_lines(snapshot)
    cursor_offsets = tuple(
        cursor_to_offset_lines(snapshot, source_starts, cursor) for cursor in cursors
    )
    anchor_offsets = tuple(
        cursor_to_offset_lines(snapshot, source_starts, anchor)
        if anchor is not None
        else None
        for anchor in anchors
    )
    plan = plan_simultaneous_edits_lines(
        snapshot,
        requests,
        source_starts=source_starts,
        capture_history_witness=True,
    )
    witness = plan.compact_history_witness()
    if plan.text_changed:
        buffer.replace_lines(plan.new_lines)

    owner_offsets = dict(plan.owner_offsets)
    mapped_cursor_rows: list[Cursor] = []
    for index, source_offset in enumerate(cursor_offsets):
        result_offset = owner_offsets.get(index)
        if result_offset is None:
            result_offset = plan.map_offset(source_offset)
        mapped_cursor_rows.append(
            offset_to_cursor_lines(
                plan.new_lines,
                plan.result_starts,
                result_offset,
                source_length=plan.result_length,
            )
        )
    mapped_cursors = tuple(mapped_cursor_rows)
    mapped_anchors = tuple(
        offset_to_cursor_lines(
            plan.new_lines,
            plan.result_starts,
            plan.map_offset(offset),
            source_length=plan.result_length,
        )
        if offset is not None
        else None
        for offset in anchor_offsets
    )
    return witness, mapped_cursors, mapped_anchors


def _measure_once(
    *,
    mode: str,
    source_lines: tuple[str, ...],
    requests: tuple[SimultaneousTextEdit, ...],
    cursors: tuple[Cursor, ...],
    anchors: tuple[Cursor | None, ...],
    expected_text: str,
) -> dict[str, Any]:
    source_text = "\n".join(source_lines)
    buffer = _CountingBuffer(source_text)
    # Retain the exact pre-edit objects so allocator address reuse cannot be
    # mistaken for structural sharing after the reference rebuilds the buffer.
    source_line_objects = tuple(buffer.lines)

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    if mode == "rev0990-flat-reference":
        source_generation = buffer.get_text()
        witness, mapped_cursors, mapped_anchors = _mapped_sidecars_flat(
            source_text=source_generation,
            requests=requests,
            cursors=cursors,
            anchors=anchors,
            buffer=buffer,
        )
        complete_result_strings = 1
    elif mode == "rev0991-line-vector-product":
        witness, mapped_cursors, mapped_anchors = _mapped_sidecars_lines(
            source_lines=buffer.lines,
            requests=requests,
            cursors=cursors,
            anchors=anchors,
            buffer=buffer,
        )
        complete_result_strings = 0
    else:
        raise ValueError(f"unknown planning mode: {mode}")
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    counts = {
        "full_document_get_text_calls": int(buffer.full_text_reads),
        "full_document_get_text_chars": int(buffer.full_text_read_chars),
        "full_document_set_text_calls": int(buffer.full_text_writes),
        "full_document_set_text_chars": int(buffer.full_text_write_chars),
        "complete_result_strings": int(complete_result_strings),
        "complete_document_string_generations": int(
            buffer.full_text_reads + complete_result_strings
        ),
        "line_vector_commits": int(buffer.line_vector_writes),
    }
    result_lines = tuple(buffer.lines)
    result_text = "\n".join(result_lines)
    reused = sum(
        1
        for index, line in enumerate(result_lines)
        if index < len(source_line_objects)
        and line is source_line_objects[index]
    )
    restored = replay_simultaneous_edit_witness_lines(
        result_lines,
        witness,
        undo=True,
    )
    redone = replay_simultaneous_edit_witness_lines(
        restored,
        witness,
        undo=False,
    )
    mapped_payload = json.dumps(
        {
            "cursors": [[row.line, row.col] for row in mapped_cursors],
            "anchors": [
                [row.line, row.col] if row is not None else None
                for row in mapped_anchors
            ],
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return {
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "result_exact": result_text == expected_text,
        "undo_exact": tuple(restored) == source_lines,
        "redo_exact": tuple(redone) == result_lines,
        "mapped_sidecars_sha256": hashlib.sha256(mapped_payload).hexdigest(),
        "mapped_cursor_count": len(mapped_cursors),
        "mapped_anchor_count": len(mapped_anchors),
        "history_splices": len(witness.splices),
        "history_retained_text_chars": sum(
            len(text) for text in witness.retained_texts()
        ),
        "result_lines": len(result_lines),
        "reused_source_line_objects": int(reused),
        "reused_source_line_percent": round(
            100.0 * reused / max(1, len(result_lines)),
            3,
        ),
        **counts,
    }


def _median_int(rows: list[dict[str, Any]], key: str) -> int:
    return int(statistics.median(int(row[key]) for row in rows))


def _median_float(rows: list[dict[str, Any]], key: str) -> float:
    return round(float(statistics.median(float(row[key]) for row in rows)), 6)


def _median_case(
    *,
    mode: str,
    source_lines: tuple[str, ...],
    requests: tuple[SimultaneousTextEdit, ...],
    cursors: tuple[Cursor, ...],
    anchors: tuple[Cursor | None, ...],
    expected_text: str,
    samples: int,
) -> dict[str, Any]:
    rows = [
        _measure_once(
            mode=mode,
            source_lines=source_lines,
            requests=requests,
            cursors=cursors,
            anchors=anchors,
            expected_text=expected_text,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    return {
        "samples": len(rows),
        "elapsed_seconds_median": _median_float(rows, "elapsed_seconds"),
        "traced_current_bytes_median": _median_int(rows, "traced_current_bytes"),
        "traced_peak_bytes_median": _median_int(rows, "traced_peak_bytes"),
        "result_exact": all(bool(row["result_exact"]) for row in rows),
        "undo_exact": all(bool(row["undo_exact"]) for row in rows),
        "redo_exact": all(bool(row["redo_exact"]) for row in rows),
        "mapped_sidecars_sha256": str(first["mapped_sidecars_sha256"]),
        "mapped_cursor_count": int(first["mapped_cursor_count"]),
        "mapped_anchor_count": int(first["mapped_anchor_count"]),
        "history_splices": int(first["history_splices"]),
        "history_retained_text_chars": int(first["history_retained_text_chars"]),
        "result_lines": int(first["result_lines"]),
        "reused_source_line_objects": int(first["reused_source_line_objects"]),
        "reused_source_line_percent": float(first["reused_source_line_percent"]),
        "full_document_get_text_calls": int(first["full_document_get_text_calls"]),
        "full_document_get_text_chars": int(first["full_document_get_text_chars"]),
        "full_document_set_text_calls": int(first["full_document_set_text_calls"]),
        "full_document_set_text_chars": int(first["full_document_set_text_chars"]),
        "complete_result_strings": int(first["complete_result_strings"]),
        "complete_document_string_generations": int(
            first["complete_document_string_generations"]
        ),
        "line_vector_commits": int(first["line_vector_commits"]),
    }


def _percent_reduction(product: int, reference: int) -> float | None:
    if int(reference) <= 0:
        return None
    return round(100.0 * (int(reference) - int(product)) / int(reference), 3)


def build_report(
    *,
    line_count: int,
    line_width: int,
    edit_count: int,
    samples: int,
) -> dict[str, Any]:
    source_lines, requests, cursors, anchors = _fixture(
        line_count=line_count,
        line_width=line_width,
        edit_count=edit_count,
    )
    source_text = "\n".join(source_lines)
    oracle = plan_simultaneous_edits(source_text, requests)
    expected_text = oracle.new_text

    reference = _median_case(
        mode="rev0990-flat-reference",
        source_lines=source_lines,
        requests=requests,
        cursors=cursors,
        anchors=anchors,
        expected_text=expected_text,
        samples=samples,
    )
    product = _median_case(
        mode="rev0991-line-vector-product",
        source_lines=source_lines,
        requests=requests,
        cursors=cursors,
        anchors=anchors,
        expected_text=expected_text,
        samples=samples,
    )
    reference_current = int(reference["traced_current_bytes_median"])
    product_current = int(product["traced_current_bytes_median"])
    reference_peak = int(reference["traced_peak_bytes_median"])
    product_peak = int(product["traced_peak_bytes_median"])
    return {
        "schema": SCHEMA,
        "measurement_scope": (
            "local CPython allocations traced around one complete planning, sidecar "
            "mapping, witness capture, and publication action; not RSS/native heap "
            "or a portable latency guarantee"
        ),
        "reference_scope": (
            "exact rev0990 genuine multi-range shape: Buffer.get_text, flat immutable "
            "source/result plan, Buffer.set_text, and result-text sidecar mapping; "
            "evidence only"
        ),
        "fixture": {
            "source_characters": len(source_text),
            "source_lines": len(source_lines),
            "requested_edits": len(requests),
            "cursor_sidecars": len(cursors),
            "anchor_sidecars": len(anchors),
        },
        "rev0990_flat_reference": reference,
        "rev0991_line_vector_product": product,
        "comparison": {
            "sidecars_exact": (
                reference["mapped_sidecars_sha256"]
                == product["mapped_sidecars_sha256"]
                and reference["mapped_cursor_count"]
                == product["mapped_cursor_count"]
                and reference["mapped_anchor_count"]
                == product["mapped_anchor_count"]
            ),
            "history_shape_exact": (
                reference["history_splices"] == product["history_splices"]
                and reference["history_retained_text_chars"]
                == product["history_retained_text_chars"]
            ),
            "complete_document_string_generation_reduction_percent": _percent_reduction(
                int(product["complete_document_string_generations"]),
                int(reference["complete_document_string_generations"]),
            ),
            "traced_current_reduction_bytes": reference_current - product_current,
            "traced_current_reduction_percent": _percent_reduction(
                product_current,
                reference_current,
            ),
            "traced_peak_reduction_bytes": reference_peak - product_peak,
            "traced_peak_reduction_percent": _percent_reduction(
                product_peak,
                reference_peak,
            ),
            "reused_source_line_object_gain": (
                int(product["reused_source_line_objects"])
                - int(reference["reused_source_line_objects"])
            ),
            "local_elapsed_ratio_product_over_reference": round(
                float(product["elapsed_seconds_median"])
                / max(0.000001, float(reference["elapsed_seconds_median"])),
                3,
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=11_000)
    parser.add_argument("--line-width", type=int, default=99)
    parser.add_argument("--edits", type=int, default=128)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    report = build_report(
        line_count=max(2, int(args.lines)),
        line_width=max(24, int(args.line_width)),
        edit_count=max(2, int(args.edits)),
        samples=max(1, int(args.samples)),
    )
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if str(args.output):
        with open(str(args.output), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
