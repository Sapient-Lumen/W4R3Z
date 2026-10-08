#!/usr/bin/env python3
"""Measure Python allocation peaks for Micromax's largest editor hot paths.

This is a repeatable engineering witness, not a total-process memory profiler.
``tracemalloc`` observes Python-tracked allocations only; native allocator,
interpreter, subprocess, and operating-system resident memory are outside the
reported figures.

Examples:
  python tools/measure_hotpath_allocations.py --case all
  python tools/measure_hotpath_allocations.py --case wordwrap --wordwrap-chars 1000000
"""

from __future__ import annotations

import argparse
import gc
import json
import time
import tracemalloc
from collections.abc import Callable
from typing import Any

from micromax_editor.buffer import Buffer
from micromax_editor.replace_plan import plan_replace
from micromax_editor.search import SearchState, scan_buffer
from micromax_editor.viewport_math import WordWrapLayout

SCHEMA = "micromax.hotpath-allocation-witness.v1"


def _measure(
    name: str,
    operation: Callable[[], tuple[dict[str, Any], object]],
) -> dict[str, Any]:
    """Return one isolated Python-allocation observation."""

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    details, retained = operation()
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del retained
    return {
        "case": str(name),
        "elapsed_seconds": round(elapsed, 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        **details,
    }


def measure_wordwrap(*, chars: int, width: int) -> dict[str, Any]:
    chars_i = max(0, int(chars))
    width_i = max(1, int(width))
    text = "x" * chars_i

    def operation() -> tuple[dict[str, Any], object]:
        layout = WordWrapLayout(text, width=width_i, contindent=0)
        middle_row = layout.row_count // 2
        middle_bounds = layout.bounds_for_row(middle_row)
        return ({
            "input_chars": chars_i,
            "width": width_i,
            "visual_rows": layout.row_count,
            "checkpoint_stride": layout.checkpoint_stride,
            "retained_coordinate_bytes": layout.storage_bytes,
            "middle_row": middle_row,
            "middle_bounds": list(middle_bounds),
        }, layout)

    return _measure("true-wordwrap", operation)


def measure_search(*, matches: int) -> dict[str, Any]:
    matches_i = max(0, int(matches))
    text = "x" * matches_i
    buffer = Buffer(text)
    state = SearchState(query="x", literal=True, case_sensitive=True)

    def operation() -> tuple[dict[str, Any], object]:
        snapshot = scan_buffer(
            buffer,
            state,
            max_matches=matches_i + 1,
        )
        if snapshot.error:
            raise RuntimeError(snapshot.error)
        return ({
            "input_chars": len(text),
            "matches": len(snapshot.spans),
            "line_starts": len(snapshot.line_starts),
            "retained_coordinate_bytes": snapshot.storage_bytes,
        }, snapshot)

    return _measure("cold-literal-search", operation)


def measure_replace(*, matches: int) -> dict[str, Any]:
    matches_i = max(0, int(matches))
    text = "a " * matches_i

    def operation() -> tuple[dict[str, Any], object]:
        plan = plan_replace(
            text,
            "a",
            "XYZ",
            replace_all=True,
            literal=True,
            sample_limit=3,
            max_matches=matches_i,
        )
        if not plan.ok:
            raise RuntimeError(plan.error)
        return ({
            "input_chars": len(text),
            "matches": plan.count,
            "sample_rows": len(plan.matches),
            "output_chars": len(plan.new_text),
        }, plan)

    return _measure("complete-replace-plan", operation)


def build_report(
    *,
    cases: tuple[str, ...],
    wordwrap_chars: int,
    wordwrap_width: int,
    search_matches: int,
    replace_matches: int,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if "wordwrap" in cases:
        rows.append(measure_wordwrap(chars=wordwrap_chars, width=wordwrap_width))
    if "search" in cases:
        rows.append(measure_search(matches=search_matches))
    if "replace" in cases:
        rows.append(measure_replace(matches=replace_matches))
    return {
        "schema": SCHEMA,
        "measurement_scope": "Python allocations traced by tracemalloc; not RSS or total heap",
        "cases": rows,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        choices=("all", "wordwrap", "search", "replace"),
        default="all",
    )
    parser.add_argument("--wordwrap-chars", type=int, default=1_000_000)
    parser.add_argument("--wordwrap-width", type=int, default=10)
    parser.add_argument("--search-matches", type=int, default=100_000)
    parser.add_argument("--replace-matches", type=int, default=50_000)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    selected = (
        ("wordwrap", "search", "replace")
        if args.case == "all"
        else (str(args.case),)
    )
    report = build_report(
        cases=selected,
        wordwrap_chars=args.wordwrap_chars,
        wordwrap_width=args.wordwrap_width,
        search_matches=args.search_matches,
        replace_matches=args.replace_matches,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
