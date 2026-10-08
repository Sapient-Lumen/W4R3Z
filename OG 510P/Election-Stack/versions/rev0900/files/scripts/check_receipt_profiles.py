#!/usr/bin/env python3
"""Check receipt profile identifiers used in example packets.

Registry:
- artifacts/registries/receipt-profiles.csv

This is a drift firewall: examples should not silently invent new receipt profile strings.
"""

from __future__ import annotations

from pathlib import Path
import csv, json, sys

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "receipt-profiles.csv"

def load_profiles() -> set[str]:
    profiles=set()
    if not REG.exists():
        return profiles
    with REG.open("r", encoding="utf-8", newline="") as f:
        r=csv.DictReader(f)
        for row in r:
            p=row.get("profile")
            if p:
                profiles.add(p)
    return profiles

def main() -> int:
    profiles = load_profiles()
    if not profiles:
        print("WARN receipt profiles registry missing or empty", file=sys.stderr)
        return 0

    problems=0
    # Scan example packets for receipt objects (attachments with rel=transparency_receipt)
    examples = ROOT / "artifacts" / "examples"
    for env_path in examples.rglob("*.envelope.json"):
        try:
            env=json.loads(env_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for att in env.get("attachments", []) or []:
            if not isinstance(att, dict):
                continue
            if att.get("rel") != "transparency_receipt":
                continue
            uri=att.get("uri","")
            if not uri:
                continue
            obj = env_path.parents[1] / "objects" / uri  # .../evidence_packet_x/envelopes -> parents[1] is packet dir
            if not obj.exists():
                continue
            try:
                robj=json.loads(obj.read_text(encoding="utf-8"))
            except Exception:
                continue
            prof=robj.get("profile")
            if not prof:
                print(f"PROBLEM receipt_profile_missing {env_path}", file=sys.stderr)
                problems += 1
            elif prof not in profiles:
                print(f"PROBLEM receipt_profile_unknown {prof} in {env_path}", file=sys.stderr)
                problems += 1

    return 2 if problems else 0

if __name__ == "__main__":
    raise SystemExit(main())
