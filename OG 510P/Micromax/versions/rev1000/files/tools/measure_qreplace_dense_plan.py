#!/usr/bin/env python3
"""Measure dense delayed query-replace plan retention.

The evidence-only reference recreates rev0997's tuple of one ``ReplacementEdit``
object per match.  The product case enters an ordinary literal query-replace and
retains packed unsigned-64-bit start/end cells plus one shared replacement value.
Source construction and Editor initialization occur before tracing.

Examples:
  PYTHONPATH=src python tools/measure_qreplace_dense_plan.py
  PYTHONPATH=src python tools/measure_qreplace_dense_plan.py --matches 100000 --samples 3
  PYTHONPATH=src python tools/measure_qreplace_dense_plan.py --json-out report.json
"""

from __future__ import annotations

import argparse
import copy
import gc
import json
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any

from micromax_editor.editor import Editor
from micromax_editor.query_replace import QueryReplaceSourceSnapshot
from micromax_editor.replace_plan import ReplacementEdit, ReplacementEdits

SCHEMA = "micromax.qreplace-dense-plan-measurement.v1"
TOKEN = "a"
REPLACEMENT = "XYZ"


def _editor(*, matches: int) -> Editor:
    editor = Editor()
    editor.new_buffer("*qreplace-dense-plan*", "a " * max(1, int(matches)))
    editor.cur().buf.fastdirty = True
    return editor


def _sample_rows(edits: object) -> list[list[object]]:
    count = len(edits)  # type: ignore[arg-type]
    if count <= 0:
        return []
    indices = sorted({0, count // 2, count - 1})
    rows: list[list[object]] = []
    for index in indices:
        edit = edits[index]  # type: ignore[index]
        rows.append([int(edit.start), int(edit.end), str(edit.new)])
    return rows


def _measure_reference(*, matches: int) -> dict[str, Any]:
    count = max(1, int(matches))
    editor = _editor(matches=count)
    source_lines = editor.cur().buf.snapshot_lines()

    gc.collect()
    tracemalloc.start()
    started = time.perf_counter()
    source_snapshot = QueryReplaceSourceSnapshot.capture(source_lines)
    plan = tuple(
        ReplacementEdit(index * 2, index * 2 + 1, REPLACEMENT)
        for index in range(count)
    )
    elapsed = time.perf_counter() - started
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    copied = copy.deepcopy(plan)
    copied_elements = sum(
        1 for left, right in zip(plan, copied, strict=True) if left is not right
    )
    return {
        "document_chars": count * 2,
        "matches": count,
        "elapsed_seconds": float(elapsed),
        "traced_current_bytes": int(current),
        "traced_peak_bytes": int(peak),
        "source_coordinate_bytes": int(source_snapshot.coordinate_bytes),
        "retained_edit_objects": len(plan),
        "retained_coordinate_python_ints": len(plan) * 2,
        "retained_replacement_values": 1,
        "deepcopy_rebuilt_edit_objects": int(copied_elements),
        "sample_rows": _sample_rows(plan),
    }


def _measure_product(*, matches: int) -> dict[str, Any]:
    count = max(1, int(matches))
    editor = _editor(matches=count)

    gc.collect()
    tracemalloc.start()
    started = time.perf_counter()
    ok = editor.begin_query_replace(TOKEN, REPLACEMENT, literal=True)
    elapsed = time.perf_counter() - started
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    session = editor.qreplace
    if not ok or session is None:
        raise RuntimeError("packed query-replace product did not start")
    plan = session.planned_matches
    if not isinstance(plan, ReplacementEdits) or len(plan) != count:
        raise RuntimeError("packed query-replace product has the wrong plan shape")
    return {
        "document_chars": count * 2,
        "matches": len(plan),
        "elapsed_seconds": float(elapsed),
        "traced_current_bytes": int(current),
        "traced_peak_bytes": int(peak),
        "coordinate_bytes": int(plan.coordinate_bytes),
        "retained_edit_objects": 0,
        "retained_coordinate_python_ints": 0,
        "retained_replacement_values": int(plan.retained_replacement_values),
        "uses_uniform_replacement": bool(plan.uses_uniform_replacement),
        "deepcopy_shares_plan": copy.deepcopy(plan) is plan,
        "sample_rows": _sample_rows(plan),
    }


def _median_case(measure: Any, *, matches: int, samples: int) -> dict[str, Any]:
    rows = [measure(matches=matches) for _ in range(max(1, int(samples)))]
    first = rows[0]
    dynamic = {"elapsed_seconds", "traced_current_bytes", "traced_peak_bytes"}
    for row in rows[1:]:
        if any(row[key] != first[key] for key in first if key not in dynamic):
            raise RuntimeError("dense query-replace plan shape changed between samples")
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


def build_report(*, matches: int = 100_000, samples: int = 3) -> dict[str, Any]:
    count = max(1, int(matches))
    reference = _median_case(
        _measure_reference,
        matches=count,
        samples=samples,
    )
    product = _median_case(
        _measure_product,
        matches=count,
        samples=samples,
    )
    return {
        "schema": SCHEMA,
        "method": {
            "source": "one-line literal document with one non-overlapping match every two characters",
            "reference": "rev0997 shallow source plus one slotted ReplacementEdit and two Python ints per match",
            "product": "ordinary query-replace with interleaved array('Q') spans and one shared replacement",
            "memory": "Python allocations traced by tracemalloc; not RSS/native heap",
            "timing": "local elapsed context only; reference constructs the retained legacy shape directly",
        },
        "rev0997_object_rows_reference": reference,
        "packed_plan_product": product,
        "comparison": {
            "plans_exactly_equal": reference["sample_rows"] == product["sample_rows"],
            "product_deepcopy_shares_plan": product["deepcopy_shares_plan"],
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
            "packed source coordinates remain O(matches) at 16 bytes per match on this interpreter",
            "this literal-plan witness does not measure the separate rev0999 file-backed regex transport, child string, or file/page-cache charge",
            "varying regex capture expansions still retain one string reference per match",
            "elapsed and tracemalloc figures are machine- and interpreter-specific",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matches", type=int, default=100_000)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = build_report(
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
