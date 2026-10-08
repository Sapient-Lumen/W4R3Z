#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"timing-regression: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: scripts/test/check_timing_regression.py <quick|full>", file=sys.stderr)
        return 2

    mode = sys.argv[1]
    if mode not in {"quick", "full"}:
        return 2

    root = Path(__file__).resolve().parents[2]
    baseline_path = root / "goldens" / "timing_baseline.json"
    timing_path = root / "artifacts" / "timing" / f"timing_{mode}.tsv"

    if not baseline_path.exists():
        fail(f"missing baseline: {baseline_path}")
    if not timing_path.exists():
        fail(f"missing timing file: {timing_path}")

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    metric = baseline.get("metrics", {}).get(mode, {})
    p95 = float(metric.get("p95_seconds", 0))
    allow = float(metric.get("allowed_regression_percent", 0))
    if p95 <= 0:
        fail(f"invalid baseline p95 for mode={mode}")

    measured = 0.0
    rows = timing_path.read_text(encoding="utf-8").splitlines()[1:]
    for r in rows:
        parts = r.split("\t")
        if len(parts) < 2:
            continue
        try:
            measured += float(parts[1])
        except ValueError:
            continue

    threshold = p95 * (1.0 + allow / 100.0)
    if measured > threshold:
        fail(f"mode={mode} measured={measured:.2f}s threshold={threshold:.2f}s baseline_p95={p95:.2f}s")

    print(f"timing-regression: ok mode={mode} measured={measured:.2f}s threshold={threshold:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
