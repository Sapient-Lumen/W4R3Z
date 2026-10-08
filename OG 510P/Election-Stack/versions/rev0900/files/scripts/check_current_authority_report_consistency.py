#!/usr/bin/env python3
"""Check that current-authority queue reports agree on row/lane counts.

rev0867 found a risky refactor bug: the queue and burndown-batch reports had
near-duplicate host/state/tag lists and produced different 45-day totals.  This
check keeps future edits from hiding current-authority work in one report while
showing it in another.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from release_context import release_date as archive_release_date
DEFAULT_RELEASE_DATE = archive_release_date(ROOT)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-date", default=os.environ.get("ELECTION_STACK_SOURCE_REVIEW_DATE", DEFAULT_RELEASE_DATE))
    ap.add_argument("--horizon-days", type=int, default=45)
    args = ap.parse_args()
    release_date = dt.date.fromisoformat(args.release_date)

    queue = load_module(ROOT / "scripts" / "report_current_authority_source_queue.py", "queue_report")
    batches = load_module(ROOT / "scripts" / "report_current_authority_burndown_batches.py", "batch_report")
    rows = queue.load_rows()
    _queue_table, queue_summary = queue.summarize(rows, release_date, int(args.horizon_days))
    _batch_table, batch_summary = batches.summarize(rows, release_date, int(args.horizon_days))

    errors: list[str] = []
    for key in ["current_authority_due_count", "lane_counts"]:
        if queue_summary.get(key) != batch_summary.get(key):
            errors.append(
                f"{key} mismatch: source_queue={queue_summary.get(key)!r}; "
                f"burndown_batches={batch_summary.get(key)!r}"
            )

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print(
        "PASS: current-authority reports agree "
        f"(due={queue_summary['current_authority_due_count']}, lanes={len(queue_summary['lane_counts'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
