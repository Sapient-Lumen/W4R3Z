#!/usr/bin/env python3
"""Check PublicationContract trigger identifiers used in example packets.

Registry:
- artifacts/registries/publication-triggers.csv

This is a drift firewall: examples should not silently invent new trigger strings.
"""

from __future__ import annotations

from pathlib import Path
import csv, json, sys

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "publication-triggers.csv"
EXAMPLES = ROOT / "artifacts" / "examples"

def load_triggers() -> set[str]:
    if not REG.exists():
        return set()
    out=set()
    with REG.open("r", encoding="utf-8", newline="") as f:
        r=csv.DictReader(f)
        for row in r:
            tid=(row.get("trigger_id") or "").strip()
            if tid:
                out.add(tid)
    return out

TRIGGERS = load_triggers()

def is_allowed(t: str) -> bool:
    if t in TRIGGERS:
        return True
    # allow experimental namespaced triggers
    if t.startswith("x-") and len(t) > 3:
        return True
    return False

def main() -> int:
    problems=[]
    if not EXAMPLES.exists():
        return 0
    # Find envelopes of kind hfv.publication.contract
    for env_path in EXAMPLES.rglob("*.envelope.json"):
        try:
            env=json.loads(env_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if env.get("kind") != "hfv.publication.contract":
            continue
        ptr=env.get("payload_pointer") or {}
        uri=ptr.get("uri","")
        if not uri:
            continue
        obj_path=env_path.parent.parent / "objects" / uri  # envelopes/.. -> packet root
        if not obj_path.exists():
            problems.append(f"missing_payload_object:{env_path}")
            continue
        try:
            pc=json.loads(obj_path.read_text(encoding="utf-8"))
        except Exception:
            problems.append(f"unparseable_contract:{obj_path}")
            continue
        for i, rule in enumerate(pc.get("rules", [])):
            trig=(rule.get("trigger") or "").strip()
            if not trig:
                problems.append(f"missing_trigger:{obj_path}:{i}")
            elif not is_allowed(trig):
                problems.append(f"unknown_trigger:{obj_path}:{i}:{trig}")
    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 2
    print("OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
