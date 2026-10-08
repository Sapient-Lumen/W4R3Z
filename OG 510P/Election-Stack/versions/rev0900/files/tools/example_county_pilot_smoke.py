#!/usr/bin/env python3
"""Run the synthetic Example County pilot smoke path.

This helper reads artifacts/examples/example_county_2026_municipal_pilot/scenario.json,
verifies every referenced packet, and emits a compact phase summary. It is a
rehearsal helper, not live deployment evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from example_county_common import ROOT, DEFAULT_SCENARIO, load_json, iter_packet_refs, verify_packet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(DEFAULT_SCENARIO), help="Path to scenario.json")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = ap.parse_args()

    scenario_path = Path(args.scenario)
    if not scenario_path.is_absolute():
        scenario_path = ROOT / scenario_path
    scenario = load_json(scenario_path)

    results = []
    for phase_id, _public_sentence, kind, rel in iter_packet_refs(scenario):
        r = verify_packet(rel)
        r["phase_id"] = phase_id
        r["kind"] = kind
        results.append(r)

    fail = [r for r in results if r.get("returncode") != 0 or r.get("status") != "PASS"]
    report = {
        "scenario_id": scenario.get("scenario_id"),
        "archive_version": scenario.get("archive_version"),
        "synthetic_only": scenario.get("synthetic_only") is True,
        "packets_checked": len(results),
        "status": "PASS" if not fail else "FAIL",
        "results": results,
        "non_claim": "Synthetic rehearsal only; not live deployment evidence and not an outcome certification.",
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"scenario={report['scenario_id']} version={report['archive_version']} status={report['status']} packets={len(results)}")
        for r in results:
            print(f"{r['status']:>4} {r['phase_id']} {r['kind']} {r['packet']}")
        print(report["non_claim"])

    return 0 if not fail else 2


if __name__ == "__main__":
    raise SystemExit(main())
