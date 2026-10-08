#!/usr/bin/env python3
"""Ensure every registered EvidenceEnvelope kind has at least one example packet.

This is a coverage gate, not a quality judgment. Example payload validation and
packet verification are handled by neighboring release-gate checks.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIND_REGISTRY = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
EXAMPLES = ROOT / "artifacts" / "examples"


def main() -> int:
    wanted: set[str] = set()
    with KIND_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            kind = (row.get("kind") or "").strip()
            if kind:
                wanted.add(kind)

    found: dict[str, list[str]] = {}
    if EXAMPLES.exists():
        for env_path in sorted(EXAMPLES.glob("evidence_packet_*/envelopes/*.json")):
            try:
                obj = json.loads(env_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"ERROR: cannot parse {env_path.relative_to(ROOT)}: {e}", file=sys.stderr)
                return 2
            kind = obj.get("kind")
            if isinstance(kind, str) and kind:
                found.setdefault(kind, []).append(str(env_path.relative_to(ROOT)))

    missing = sorted(wanted - set(found))
    if missing:
        for kind in missing:
            print(f"ERROR: no example packet envelope for registered kind {kind}", file=sys.stderr)
        return 2
    print(f"PASS: registered envelope kind example coverage ({len(wanted)} kind(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
