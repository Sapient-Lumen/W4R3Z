#!/usr/bin/env python3
"""Small consistency checker for rev0006 coherence families."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cluster_path = ROOT / "data" / "rev0006_cluster_refactor.csv"
map_path = ROOT / "data" / "rev0006_coherence_map.csv"

def main() -> int:
    members = defaultdict(list)
    with cluster_path.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            members[row['canonical_family']].append(row['member'])

    map_families = set()
    with map_path.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            map_families.add(row['family'])

    errors = []
    for family, ids in members.items():
        short = family.split()[0]
        if short not in map_families:
            errors.append(f"family {family!r} missing from coherence_map")
        if len(ids) != len(set(ids)):
            errors.append(f"family {family!r} has duplicate members: {ids}")

    print("Coherence families:")
    for family, ids in sorted(members.items()):
        print(f"- {family}: {', '.join(ids)}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nNo structural coherence-map errors detected.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
