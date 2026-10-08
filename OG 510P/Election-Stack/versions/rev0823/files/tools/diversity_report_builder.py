#!/usr/bin/env python3
"""Build a simple StakeholderDiversityReport from a witness set JSON.

This is a reference tool: it computes basic counts and Shannon entropy over categories.
"""

import json
import math
import sys
from datetime import datetime, timezone


def shannon_entropy(counts):
    total = sum(counts)
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        ent -= p * math.log(p, 2)
    return ent


def main():
    if len(sys.argv) < 4:
        print("Usage: diversity_report_builder.py <election_id> <checkpoint_id> <witness_set.json>")
        sys.exit(2)

    election_id, checkpoint_id, path = sys.argv[1:4]

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expect a list of witnesses with `categories`.
    category_counts = {}
    for w in data.get("witnesses", []):
        for cat in w.get("categories", []):
            category_counts[cat] = category_counts.get(cat, 0) + 1

    ent = shannon_entropy(list(category_counts.values()))

    report = {
        "election_id": election_id,
        "checkpoint_id": checkpoint_id,
        "metrics": {
            "category_counts": category_counts,
            "entropy": ent,
        },
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
