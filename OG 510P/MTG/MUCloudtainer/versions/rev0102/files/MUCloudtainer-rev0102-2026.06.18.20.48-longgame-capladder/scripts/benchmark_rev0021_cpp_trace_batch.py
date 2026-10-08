from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.cpp_transition import build_transition_binary, cpp_transition_signatures
from src.muc5.replay import read_trace_jsonl

REV = "rev0021"
DATA = ROOT / "data"


def main() -> None:
    trace_path = DATA / "rev0020_public_traces.jsonl"
    if not trace_path.exists():
        raise SystemExit(f"missing trace source: {trace_path}")
    traces = read_trace_jsonl(trace_path)
    build_transition_binary()

    t0 = time.perf_counter()
    prepared = prepare_public_traces_for_cpp(traces, revision=REV)
    t1 = time.perf_counter()
    expected = list(prepared.expected_signatures)

    t2 = time.perf_counter()
    actual = cpp_transition_signatures(prepared.records)
    t3 = time.perf_counter()
    mismatches = sum(1 for got, want in zip(actual, expected) if got != want)

    # Include a small one-process-per-record sample to quantify subprocess overhead.
    sample_n = min(100, len(prepared.records))
    one_by_one_times: list[float] = []
    one_by_one_mismatches = 0
    for i in range(sample_n):
        s0 = time.perf_counter()
        got = cpp_transition_signatures([prepared.records[i]])[0]
        s1 = time.perf_counter()
        one_by_one_times.append(s1 - s0)
        one_by_one_mismatches += 1 if got != expected[i] else 0

    # Also run the normal finalizer once to prove the refactored path still
    # produces the canonical summary/row payload used by audits.
    summary, rows = finalize_cpp_trace_batch(prepared)
    row_dicts = [r.as_dict() for r in rows]
    import pandas as pd
    pd.DataFrame(row_dicts).to_csv(DATA / f"{REV}_cpp_batch_trace_rows.csv", index=False)

    batch_seconds = t3 - t2
    prepare_seconds = t1 - t0
    batch_rps = len(prepared.records) / batch_seconds if batch_seconds > 0 else 0.0
    one_mean = statistics.mean(one_by_one_times) if one_by_one_times else 0.0
    one_rps = 1.0 / one_mean if one_mean > 0 else 0.0
    ratio = (one_mean / (batch_seconds / max(1, len(prepared.records)))) if batch_seconds > 0 and prepared.records else 0.0

    payload = {
        "revision": REV,
        "trace_source": str(trace_path.relative_to(ROOT)),
        "traces": len(traces),
        "events": prepared.events,
        "records": len(prepared.records),
        "python_prepare_seconds": prepare_seconds,
        "python_prepare_records_per_second": len(prepared.records) / prepare_seconds if prepare_seconds > 0 else 0.0,
        "cpp_batch_seconds": batch_seconds,
        "cpp_batch_records_per_second": batch_rps,
        "cpp_batch_mismatches": mismatches,
        "cpp_finalize_summary": summary.as_dict(),
        "one_by_one_sample_n": sample_n,
        "one_by_one_mean_seconds_per_record": one_mean,
        "one_by_one_records_per_second": one_rps,
        "one_by_one_mismatches": one_by_one_mismatches,
        "estimated_subprocess_overhead_ratio_vs_batch_per_record": ratio,
    }
    (DATA / f"{REV}_cpp_batch_benchmark.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if mismatches or one_by_one_mismatches or summary.mismatches or summary.python_replay_errors or summary.skipped_events:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
