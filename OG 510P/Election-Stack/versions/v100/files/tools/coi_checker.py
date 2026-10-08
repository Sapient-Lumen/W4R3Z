#!/usr/bin/env python3
"""Reference checker: ensure each witness has a COI disclosure file.

Usage:
  coi_checker.py <witness_set.json> <coi_dir>

Expects witness_set.json to contain `witnesses: [{witness_id: ...}, ...]`.
COI files are expected as <coi_dir>/<witness_id>.json
"""

import json
import os
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage: coi_checker.py <witness_set.json> <coi_dir>")
        sys.exit(2)

    witness_set_path, coi_dir = sys.argv[1:3]

    with open(witness_set_path, "r", encoding="utf-8") as f:
        ws = json.load(f)

    missing = []
    for w in ws.get("witnesses", []):
        wid = w.get("witness_id")
        if not wid:
            continue
        fp = os.path.join(coi_dir, f"{wid}.json")
        if not os.path.exists(fp):
            missing.append(wid)

    if missing:
        print("MISSING_COI:")
        for wid in missing:
            print(f"- {wid}")
        sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
