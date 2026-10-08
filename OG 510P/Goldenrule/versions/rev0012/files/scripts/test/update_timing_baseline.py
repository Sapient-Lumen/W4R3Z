#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: scripts/test/update_timing_baseline.py <timing_tsv>", file=sys.stderr)
        return 2

    tsv = Path(sys.argv[1])
    if not tsv.exists():
        print(f"missing timing file: {tsv}", file=sys.stderr)
        return 2

    values = []
    for line in tsv.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            values.append(float(parts[1]))
        except ValueError:
            continue

    if not values:
        print("no timing values found", file=sys.stderr)
        return 1

    values.sort()
    idx = int(0.95 * (len(values) - 1))
    p95 = values[idx]

    baseline_path = Path("goldens/timing_baseline.json")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline["metrics"]["quick"]["p95_seconds"] = p95
    baseline["generated_at"] = __import__("datetime").date.today().isoformat()
    baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"updated {baseline_path} quick.p95_seconds={p95}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
