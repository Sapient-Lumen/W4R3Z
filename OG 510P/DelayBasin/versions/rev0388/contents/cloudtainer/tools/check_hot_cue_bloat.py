#!/usr/bin/env python3
"""Fast cloudtainer check for DelayBasin landing hot-cue bloat.

This is a working-overlay diagnostic, not a canonical DelayBasin validator.
Run from anywhere inside the extracted tree:

    python cloudtainer/tools/check_hot_cue_bloat.py --threshold 24
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGETS = ["README.md", "START_HERE.md", "AGENTS.md", "docs/README.md"]
GENERATED_OR_COLD_HINTS = {
    "VALIDATION-INDEX.json",
    "LEDGER-AUDIT.json",
    "CANARY-PROTOCOL.json",
    "PACKAGE-IDENTITY-AUDIT.json",
    "SCHEMA-CONFORMANCE-AUDIT.json",
    "ARCHIVE-ECONOMY-AUDIT.json",
}

def extract_current_additions(text: str) -> list[str]:
    match = re.search(r"Current additions: (?P<additions>.*?)(?:\n|$)", text)
    if not match:
        return []
    return [item.strip() for item in match.group("additions").split(";") if item.strip()]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=24)
    args = parser.parse_args()

    receipt_path = ROOT / "REVISION-RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    canon = receipt.get("canon_additions", [])
    touched = receipt.get("touched_surfaces", [])

    problems: list[str] = []
    print(f"source revision: {receipt.get('revision')}")
    print(f"canon_additions: {len(canon)}")
    print(f"touched_surfaces: {len(touched)}")

    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"missing landing surface: {rel}")
            continue
        items = extract_current_additions(path.read_text(encoding="utf-8"))
        print(f"{rel}: current additions = {len(items)}")
        if len(items) > args.threshold:
            problems.append(f"{rel} hot cue has {len(items)} items > threshold {args.threshold}")
        if touched and len(items) == len(touched) and set(items) == set(touched):
            problems.append(f"{rel} hot cue equals touched_surfaces; likely regrown to full trace")
        cold = [item for item in items if pathlib.PurePosixPath(item).name in GENERATED_OR_COLD_HINTS]
        if cold:
            problems.append(f"{rel} hot cue includes generated/cold surfaces: {', '.join(cold)}")

    if problems:
        print("\nHOT-CUE-BLOAT detected:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("\nhot cue looks bounded")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
