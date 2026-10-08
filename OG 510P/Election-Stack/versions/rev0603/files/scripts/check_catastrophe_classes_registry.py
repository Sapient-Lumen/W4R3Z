#!/usr/bin/env python3
"""Drift firewall for artifacts/registries/catastrophe-classes.csv.

This registry is intentionally tiny and stable. It defines the archive's
catastrophe ordering vocabulary (C1..C5) so hazards and claims can reference it
without duplicating prose.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "catastrophe-classes.csv"

REQUIRED_HEADERS = [
    "catastrophe_class_id",
    "rank",
    "name",
    "description",
    "notes",
]

EXPECTED_IDS = ["C1", "C2", "C3", "C4", "C5"]


def main() -> int:
    if not REG.exists():
        print(f"Missing registry: {REG}", file=sys.stderr)
        return 2

    with REG.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if headers != REQUIRED_HEADERS:
            print(
                "Registry header drift in catastrophe-classes.csv:\n"
                f"  expected: {REQUIRED_HEADERS}\n"
                f"  found:    {headers}",
                file=sys.stderr,
            )
            return 2
        rows = list(reader)

    errs: list[str] = []
    ids: list[str] = []

    for i, r in enumerate(rows, start=2):
        cid = (r.get("catastrophe_class_id") or "").strip()
        if not cid:
            errs.append(f"Line {i}: empty catastrophe_class_id")
        ids.append(cid)

        try:
            rank = int((r.get("rank") or "").strip())
        except Exception:
            errs.append(f"Line {i}: rank is not an integer")
            continue

        # Basic non-empty text fields.
        for k in ("name", "description"):
            if not (r.get(k) or "").strip():
                errs.append(f"Line {i}: empty {k}")

        # Rank must be 1..5.
        if rank < 1 or rank > 5:
            errs.append(f"Line {i}: rank must be 1..5 (found {rank})")

    if len(set(ids)) != len(ids):
        errs.append("Duplicate catastrophe_class_id values")

    missing = [x for x in EXPECTED_IDS if x not in set(ids)]
    extra = sorted({x for x in ids if x not in set(EXPECTED_IDS)})
    if missing:
        errs.append(f"Missing required IDs: {', '.join(missing)}")
    if extra:
        errs.append(f"Unexpected IDs (only C1..C5 allowed): {', '.join(extra)}")

    by_id = {r["catastrophe_class_id"].strip(): r for r in rows if (r.get("catastrophe_class_id") or "").strip()}
    for idx, expected_id in enumerate(EXPECTED_IDS, start=1):
        r = by_id.get(expected_id)
        if not r:
            continue
        try:
            rr = int((r.get("rank") or "").strip())
        except Exception:
            continue
        if rr != idx:
            errs.append(f"{expected_id} must have rank {idx} (found {rr})")

    # Encourage stable ordering: rows should be sorted by rank ascending.
    try:
        parsed_ranks = [int((r.get("rank") or "").strip()) for r in rows]
        if parsed_ranks != sorted(parsed_ranks):
            errs.append("Rows must be sorted by rank ascending")
    except Exception:
        pass

    if errs:
        print("Catastrophe classes registry errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
