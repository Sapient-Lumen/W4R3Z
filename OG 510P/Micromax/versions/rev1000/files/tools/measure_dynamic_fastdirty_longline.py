#!/usr/bin/env python3
"""Measure live fast-dirty promotion and one-pass logical-line splicing.

This is a local attribution witness, not a portable latency benchmark.  It
compares the pre-rev0994 chained three-fragment string expression with the
product splice constructor, then records exact-signature calls while a buffer
created below the automatic threshold grows through it.

Examples:
  PYTHONPATH=src python tools/measure_dynamic_fastdirty_longline.py
  PYTHONPATH=src python tools/measure_dynamic_fastdirty_longline.py \
    --chars 32000000 --samples 3 --json-out .artifacts/rev0994.json
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path
from typing import Any

from micromax_editor.buffer import (
    FASTDIRTY_AUTO_BYTES,
    Buffer,
    Cursor,
    _splice_line_text,
)
from micromax_editor.editor import Editor

SCHEMA = "micromax.dynamic-fastdirty-longline-measurement.v1"


def _legacy_chained_splice(
    line: str,
    start: int,
    end: int,
    replacement: str,
) -> str:
    """Reproduce the pre-rev0994 same-line construction expression."""

    return line[:start] + replacement + line[end:]


def _measure_splice_once(
    *,
    mode: str,
    line: str,
    start: int,
    end: int,
    replacement: str,
) -> dict[str, Any]:
    if mode == "legacy-chained-reference":
        splice: Callable[[str, int, int, str], str] = _legacy_chained_splice
    elif mode == "single-join-product":
        splice = _splice_line_text
    else:
        raise ValueError(f"unknown splice mode: {mode}")

    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    result = splice(line, start, end, replacement)
    elapsed = time.perf_counter() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    expected = _legacy_chained_splice(line, start, end, replacement)
    return {
        "elapsed_seconds": round(float(elapsed), 9),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "result_exact": bool(result == expected),
        "result_chars": len(result),
    }


def _median_splice(
    *,
    mode: str,
    line: str,
    start: int,
    end: int,
    replacement: str,
    samples: int,
) -> dict[str, Any]:
    rows = [
        _measure_splice_once(
            mode=mode,
            line=line,
            start=start,
            end=end,
            replacement=replacement,
        )
        for _ in range(max(1, int(samples)))
    ]
    return {
        "samples": len(rows),
        "elapsed_seconds_median": round(
            float(statistics.median(float(row["elapsed_seconds"]) for row in rows)),
            9,
        ),
        "traced_current_bytes_median": int(
            statistics.median(int(row["traced_current_bytes"]) for row in rows)
        ),
        "traced_peak_bytes_median": int(
            statistics.median(int(row["traced_peak_bytes"]) for row in rows)
        ),
        "result_exact": all(bool(row["result_exact"]) for row in rows),
        "result_chars": int(rows[0]["result_chars"]),
    }


def _signature_counter(buffer: Buffer) -> tuple[list[int], Callable[[], tuple[int, str]]]:
    calls = [0]
    original = buffer._current_signature

    def counted() -> tuple[int, str]:
        calls[0] += 1
        return original()

    return calls, counted


def _growth_policy_once(
    *,
    explicit_exact: bool,
    followup_edits: int,
    target_chars: int,
) -> dict[str, Any]:
    baseline = "a" * (FASTDIRTY_AUTO_BYTES - 1)
    target = max(FASTDIRTY_AUTO_BYTES + 1, int(target_chars))
    crossing_text = "X" * (target - len(baseline))
    editor = Editor()
    editor.new_buffer("*growth-policy*", baseline)
    eb = editor.cur()
    if explicit_exact:
        editor.exec_command_line("setlocal fastdirty false")

    calls, counted = _signature_counter(eb.buf)
    eb.buf._current_signature = counted  # type: ignore[method-assign]

    cursor = Cursor(0, len(baseline))
    started = time.perf_counter()
    cursor = eb.buf.insert(cursor, crossing_text)
    crossing_calls = int(calls[0])
    for index in range(max(0, int(followup_edits))):
        cursor = eb.buf.insert(cursor, chr(97 + index % 26))
    elapsed = time.perf_counter() - started

    return {
        "explicit_exact": bool(explicit_exact),
        "followup_edits": max(0, int(followup_edits)),
        "target_chars_at_crossing": target,
        "elapsed_seconds": round(float(elapsed), 9),
        "signature_calls_at_crossing": crossing_calls,
        "signature_calls_total": int(calls[0]),
        "fastdirty_after_crossing": bool(eb.buf.fastdirty),
        "visible_local_fastdirty": eb.local_options.get("fastdirty", "<absent>"),
        "current_signature_cached_after_followups": eb.buf.current_signature is not None,
        "text_chars": len(eb.buf.get_text()),
        "expected_text_chars": target + max(0, int(followup_edits)),
    }


def _mark_clean_signature_reuse() -> dict[str, Any]:
    buffer = Buffer("seed")
    calls, counted = _signature_counter(buffer)
    buffer._current_signature = counted  # type: ignore[method-assign]
    buffer.insert(Cursor(0, 4), "!")
    after_mutation = int(calls[0])
    before_clean_signature = buffer.current_signature
    buffer.mark_clean()
    return {
        "signature_calls_after_exact_mutation": after_mutation,
        "signature_calls_after_mark_clean": int(calls[0]),
        "clean_reused_current_signature": bool(
            before_clean_signature is not None
            and buffer.current_signature == before_clean_signature
            and buffer._saved_sig == before_clean_signature
        ),
    }


def _percent_reduction(product: float, reference: float) -> float | None:
    if reference <= 0:
        return None
    return round(100.0 * (reference - product) / reference, 3)


def build_report(
    *,
    chars: int,
    followup_edits: int,
    samples: int,
) -> dict[str, Any]:
    line_chars = max(64, int(chars))
    line = "a" * line_chars
    start = line_chars // 2
    end = min(line_chars, start + 1)
    replacement = "XYZ"
    legacy = _median_splice(
        mode="legacy-chained-reference",
        line=line,
        start=start,
        end=end,
        replacement=replacement,
        samples=samples,
    )
    product = _median_splice(
        mode="single-join-product",
        line=line,
        start=start,
        end=end,
        replacement=replacement,
        samples=samples,
    )
    automatic = _growth_policy_once(
        explicit_exact=False,
        followup_edits=followup_edits,
        target_chars=line_chars,
    )
    exact = _growth_policy_once(
        explicit_exact=True,
        followup_edits=followup_edits,
        target_chars=line_chars,
    )
    return {
        "schema": SCHEMA,
        "method": {
            "timing": "local elapsed context only; not a portable benchmark claim",
            "memory": "Python allocations traced after source-line construction; not RSS",
            "legacy_reference": "pre-rev0994 line[:start] + replacement + line[end:] expression",
            "product": "shared _splice_line_text constructor using one str.join",
            "growth_baseline_bytes": FASTDIRTY_AUTO_BYTES - 1,
            "automatic_threshold_bytes": FASTDIRTY_AUTO_BYTES,
        },
        "single_line_splice": {
            "source_chars": line_chars,
            "legacy_chained_reference": legacy,
            "single_join_product": product,
            "comparison": {
                "elapsed_reduction_percent": _percent_reduction(
                    float(product["elapsed_seconds_median"]),
                    float(legacy["elapsed_seconds_median"]),
                ),
                "traced_peak_reduction_percent": _percent_reduction(
                    float(product["traced_peak_bytes_median"]),
                    float(legacy["traced_peak_bytes_median"]),
                ),
                "both_exact": bool(legacy["result_exact"] and product["result_exact"]),
            },
        },
        "live_growth_policy": {
            "automatic_product": automatic,
            "explicit_exact_reference": exact,
            "comparison": {
                "automatic_hashes_only_crossing_edit": (
                    automatic["signature_calls_at_crossing"] == 1
                    and automatic["signature_calls_total"] == 1
                ),
                "explicit_exact_hashes_every_edit": (
                    exact["signature_calls_total"]
                    == 1 + max(0, int(followup_edits))
                ),
                "signature_call_reduction_percent": _percent_reduction(
                    float(automatic["signature_calls_total"]),
                    float(exact["signature_calls_total"]),
                ),
                "elapsed_reduction_percent": _percent_reduction(
                    float(automatic["elapsed_seconds"]),
                    float(exact["elapsed_seconds"]),
                ),
                "both_text_lengths_exact": bool(
                    automatic["text_chars"] == automatic["expected_text_chars"]
                    and exact["text_chars"] == exact["expected_text_chars"]
                ),
            },
        },
        "mark_clean_cache": _mark_clean_signature_reuse(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=16_000_000)
    parser.add_argument("--followup-edits", type=int, default=32)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = build_report(
        chars=args.chars,
        followup_edits=args.followup_edits,
        samples=args.samples,
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
