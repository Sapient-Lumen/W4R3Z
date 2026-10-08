#!/usr/bin/env python3
"""Validate hazard register catastrophe classes.

Ensures:
- artifacts/hazards/hazard-register.csv has a CatastropheClass column
- Every row sets CatastropheClass
- Values are limited to the stable vocabulary in artifacts/registries/catastrophe-classes.csv

This is a drift firewall: it keeps the archive's priority ordering explicit.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAZ = ROOT / "artifacts" / "hazards" / "hazard-register.csv"
REG = ROOT / "artifacts" / "registries" / "catastrophe-classes.csv"


def read_ids() -> set[str]:
    with REG.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        ids = set()
        for i, row in enumerate(reader, start=2):
            cid = (row.get("catastrophe_class_id") or "").strip()
            if cid:
                ids.add(cid)
            else:
                print(f"ERROR: {REG}:L{i}: empty catastrophe_class_id", file=sys.stderr)
                raise SystemExit(2)
        return ids


def main() -> int:
    if not HAZ.exists():
        print(f"ERROR: missing hazard register: {HAZ}", file=sys.stderr)
        return 2
    if not REG.exists():
        print(f"ERROR: missing catastrophe class registry: {REG}", file=sys.stderr)
        return 2

    valid = read_ids()

    errors: list[str] = []

    with HAZ.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if "CatastropheClass" not in headers:
            errors.append("hazard-register.csv must include CatastropheClass column")
            # continue scanning for better errors is pointless
            if errors:
                for e in errors:
                    print("ERROR:", e, file=sys.stderr)
                return 2

        for line_no, row in enumerate(reader, start=2):
            hid = (row.get("HazardID") or "").strip() or f"<row {line_no}>"
            cc = (row.get("CatastropheClass") or "").strip()
            if not cc:
                errors.append(f"{HAZ}:L{line_no}: {hid}: missing CatastropheClass")
                continue
            if cc not in valid:
                errors.append(
                    f"{HAZ}:L{line_no}: {hid}: invalid CatastropheClass {cc!r} (expected one of {sorted(valid)})"
                )

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
