#!/usr/bin/env python3
"""Measure retained query-replace source shape for a many-line literal plan.

The evidence-only reference retains the complete LF-joined source string used by
rev0996. The product case enters an ordinary literal query-replace session and
retains its shallow immutable line tuple plus compact coordinate bytes. Source
construction and Editor initialization occur before tracing; figures therefore
compare allocations created by planning/retention rather than the live buffer.

Examples:
  PYTHONPATH=src python tools/measure_qreplace_source.py
  PYTHONPATH=src python tools/measure_qreplace_source.py --chars 16777216 --samples 3
  PYTHONPATH=src python tools/measure_qreplace_source.py --json-out report.json
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

from micromax_editor.editor import Editor
from micromax_editor.query_replace import QueryReplaceSourceSnapshot
from micromax_editor.replace_plan import scan_replacement_edits

SCHEMA = "micromax.qreplace-source-measurement.v1"
TOKEN = "needle"
REPLACEMENT = "X"


def _source(*, chars: int, line_chars: int) -> str:
    width = max(len(TOKEN) + 2, int(line_chars))
    target = max(width, int(chars))
    line_count = max(1, (target + width) // (width + 1))
    lines = ["a" * width for _ in range(line_count)]
    middle = line_count // 2
    token_at = max(0, (width - len(TOKEN)) // 2)
    lines[middle] = (
        "a" * token_at
        + TOKEN
        + "a" * (width - token_at - len(TOKEN))
    )
    return "\n".join(lines)


def _editor(*, chars: int, line_chars: int) -> tuple[Editor, int, int]:
    source = _source(chars=chars, line_chars=line_chars)
    document_chars = len(source)
    line_count = source.count("\n") + 1
    editor = Editor()
    editor.new_buffer("*qreplace-source*", source)
    editor.cur().buf.fastdirty = True
    del source
    return editor, document_chars, line_count


def _measure_reference(*, chars: int, line_chars: int) -> dict[str, Any]:
    editor, document_chars, line_count = _editor(chars=chars, line_chars=line_chars)
    eb = editor.cur()
    get_text_calls = 0
    original_get_text = eb.buf.get_text

    def counted_get_text() -> str:
        nonlocal get_text_calls
        get_text_calls += 1
        return original_get_text()

    eb.buf.get_text = counted_get_text  # type: ignore[method-assign]
    gc.collect()
    tracemalloc.start()
    started = time.perf_counter()
    source_text = eb.buf.get_text()
    scan = scan_replacement_edits(
        source_text,
        TOKEN,
        REPLACEMENT,
        literal=True,
        replace_all=True,
    )
    elapsed = time.perf_counter() - started
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    eb.buf.get_text = original_get_text  # type: ignore[method-assign]

    if not scan.ok or len(scan.edits) != 1:
        raise RuntimeError("reference literal plan did not produce one match")
    return {
        "document_chars": document_chars,
        "line_count": line_count,
        "elapsed_seconds": float(elapsed),
        "traced_current_bytes": int(current),
        "traced_peak_bytes": int(peak),
        "buffer_get_text_calls": int(get_text_calls),
        "retained_complete_source_chars": len(source_text),
        "edit_rows": [
            [int(edit.start), int(edit.end), str(edit.new)]
            for edit in scan.edits
        ],
        # Keep both values live through the traced-current read above.
        "retained_objects": 2 if source_text and scan.edits else 0,
    }


def _measure_product(*, chars: int, line_chars: int) -> dict[str, Any]:
    editor, document_chars, line_count = _editor(chars=chars, line_chars=line_chars)
    eb = editor.cur()
    get_text_calls = 0
    original_get_text = eb.buf.get_text

    def counted_get_text() -> str:
        nonlocal get_text_calls
        get_text_calls += 1
        return original_get_text()

    eb.buf.get_text = counted_get_text  # type: ignore[method-assign]
    gc.collect()
    tracemalloc.start()
    started = time.perf_counter()
    ok = editor.begin_query_replace(TOKEN, REPLACEMENT, literal=True)
    elapsed = time.perf_counter() - started
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    eb.buf.get_text = original_get_text  # type: ignore[method-assign]

    sess = editor.qreplace
    if not ok or sess is None or len(sess.planned_matches) != 1:
        raise RuntimeError("product literal query-replace did not produce one match")
    snapshot = sess.source_snapshot
    if not isinstance(snapshot, QueryReplaceSourceSnapshot):
        raise RuntimeError("product did not retain a shallow source snapshot")
    shared = sum(
        1
        for index, line in enumerate(snapshot.lines)
        if line is eb.buf.lines[index]
    )
    return {
        "document_chars": document_chars,
        "line_count": line_count,
        "elapsed_seconds": float(elapsed),
        "traced_current_bytes": int(current),
        "traced_peak_bytes": int(peak),
        "buffer_get_text_calls": int(get_text_calls),
        "retained_complete_source_chars": 0,
        "source_tuple_shallow_bytes": int(sys.getsizeof(snapshot.lines)),
        "source_coordinate_bytes": int(snapshot.coordinate_bytes),
        "shared_source_line_objects": int(shared),
        "edit_rows": [
            [int(edit.start), int(edit.end), str(edit.new)]
            for edit in sess.planned_matches
        ],
    }


def _median_case(
    measure: Any,
    *,
    chars: int,
    line_chars: int,
    samples: int,
) -> dict[str, Any]:
    rows = [
        measure(chars=chars, line_chars=line_chars)
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    dynamic = {"elapsed_seconds", "traced_current_bytes", "traced_peak_bytes"}
    for row in rows[1:]:
        if any(row[key] != first[key] for key in first if key not in dynamic):
            raise RuntimeError("query-replace source shape changed between samples")
    return {
        **{key: value for key, value in first.items() if key not in dynamic},
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
    }


def _reduction_percent(*, reference: int, product: int) -> float | None:
    if reference <= 0:
        return None
    return round((reference - product) * 100.0 / reference, 3)


def build_report(
    *,
    chars: int,
    line_chars: int = 64,
    samples: int = 1,
) -> dict[str, Any]:
    reference = _median_case(
        _measure_reference,
        chars=chars,
        line_chars=line_chars,
        samples=samples,
    )
    product = _median_case(
        _measure_product,
        chars=chars,
        line_chars=line_chars,
        samples=samples,
    )
    return {
        "schema": SCHEMA,
        "method": {
            "source": "many-line canonical buffer with exactly one literal match",
            "reference": "retain one complete LF-joined source plus compact edit plan",
            "product": "retain shared line tuple, packed 64-bit starts, and compact edit plan",
            "memory": "Python allocations traced by tracemalloc; not RSS/native heap",
            "timing": "local elapsed context only; not a portable benchmark bound",
        },
        "rev0996_complete_string_reference": reference,
        "shallow_line_source_product": product,
        "comparison": {
            "plans_exactly_equal": reference["edit_rows"] == product["edit_rows"],
            "product_avoids_buffer_get_text": product["buffer_get_text_calls"] == 0,
            "all_source_line_objects_shared": (
                product["shared_source_line_objects"] == product["line_count"]
            ),
            "retained_complete_source_reduction_percent": _reduction_percent(
                reference=int(reference["retained_complete_source_chars"]),
                product=int(product["retained_complete_source_chars"]),
            ),
            "traced_current_reduction_percent": _reduction_percent(
                reference=int(reference["traced_current_bytes_median"]),
                product=int(product["traced_current_bytes_median"]),
            ),
            "traced_peak_reduction_percent": _reduction_percent(
                reference=int(reference["traced_peak_bytes_median"]),
                product=int(product["traced_peak_bytes_median"]),
            ),
        },
        "residuals": [
            "the shallow tuple and packed coordinate vector remain O(lines)",
            "a huge single logical line remains one shared immutable string",
            "rev0999 regex query-replace stages a private exact-text file; this literal-source witness does not measure the child string or file/page-cache charge",
            "elapsed and tracemalloc figures are machine- and interpreter-specific",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--line-chars", type=int, default=64)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = build_report(
        chars=max(1, int(args.chars)),
        line_chars=max(1, int(args.line_chars)),
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
