#!/usr/bin/env python3
"""
tools/coverage_accounting.py

Toy-but-executable coverage accounting for verification ecosystems.

Input: a JSONL file of events with fields:
  - ts (RFC3339)
  - watcher_id
  - target_id
  - kind ("challenge_issued" | "challenge_answered" | "suppression_reported")
  - round_id (string)

Output:
  - JSON report (CoverageReport-like)
  - Markdown summary

This is meant to be a starter: it makes coverage publishable and auditable early.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input JSONL")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    events = []
    with Path(args.inp).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))

    targets = set()
    watchers = set()
    touched = set()
    per_target_rounds = defaultdict(set)
    suppressions = 0
    issued = 0

    for e in events:
        watchers.add(e.get("watcher_id", ""))
        t = e.get("target_id", "")
        r = e.get("round_id", "")
        k = e.get("kind", "")
        if t:
            targets.add(t)
        if k == "challenge_issued":
            issued += 1
            touched.add(t)
            if t and r:
                per_target_rounds[t].add(r)
        if k == "suppression_reported":
            suppressions += 1

    target_coverage = (len(touched) / len(targets)) if targets else 0.0
    suppression_rate = (suppressions / issued) if issued else 0.0
    max_gap_proxy = 0
    if per_target_rounds:
        max_gap_proxy = max(len(rs) for rs in per_target_rounds.values())

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "watchers": sorted([w for w in watchers if w]),
        "targets_total": len(targets),
        "targets_touched": len(touched),
        "target_coverage": round(target_coverage, 4),
        "challenges_issued": issued,
        "suppressions": suppressions,
        "suppression_rate": round(suppression_rate, 4),
        "max_rounds_seen_for_any_target": max_gap_proxy,
        "notes": "Toy coverage accounting; see docs/174."
    }

    Path(args.out_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Coverage report (toy example)",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Watchers: {', '.join(report['watchers']) if report['watchers'] else '(none)'}",
        f"- Targets total: {report['targets_total']}",
        f"- Targets touched: {report['targets_touched']}",
        f"- Target coverage: {report['target_coverage']}",
        f"- Challenges issued: {report['challenges_issued']}",
        f"- Suppressions: {report['suppressions']}",
        f"- Suppression rate: {report['suppression_rate']}",
        "",
        "This is intentionally simple: the point is to make coverage accounting a first-class deliverable.",
    ]
    Path(args.out_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
