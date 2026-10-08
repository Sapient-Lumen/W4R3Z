#!/usr/bin/env python3
"""Validate that the Example County evaluator scorecard is current and bounded."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OUTDIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
TOOL = ROOT / "tools" / "example_county_evaluator_scorecard.py"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k:(v or "").strip() for k,v in r.items()} for r in csv.DictReader(f)]


def main() -> int:
    errors: list[str] = []
    expected_files = ["evaluator-scorecard.json", "evaluator-scorecard.csv", "public-evaluator-scorecard.md"]
    for name in expected_files:
        if not (OUTDIR / name).exists():
            errors.append(f"missing {OUTDIR.relative_to(ROOT) / name}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    proc = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        print("ERROR: tool/example_county_evaluator_scorecard.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    try:
        generated = json.loads(proc.stdout)
    except Exception as e:
        print(f"ERROR: generated scorecard JSON parse failed: {e}", file=sys.stderr)
        return 2

    shipped = load_json(OUTDIR / "evaluator-scorecard.json")
    if shipped != generated:
        errors.append("evaluator-scorecard.json is stale; run tools/example_county_evaluator_scorecard.py --write")
    if shipped.get("archive_version") != VERSION:
        errors.append(f"scorecard archive_version {shipped.get('archive_version')!r} != VERSION {VERSION!r}")
    if shipped.get("scenario_id") != f"EXAMPLE-COUNTY-2026-MUNI-{VERSION}":
        errors.append("scorecard scenario_id is stale or malformed")
    if shipped.get("synthetic_only") is not True or shipped.get("no_live_deployment_claim") is not True:
        errors.append("scorecard missing synthetic/live-evidence JSON boundary flags")
    if shipped.get("status") != "PASS" or int(shipped.get("total_points") or 0) != int(shipped.get("max_points") or -1):
        errors.append("scorecard must pass with full synthetic rehearsal points")
    metrics = shipped.get("metrics") if isinstance(shipped, dict) else None
    if not isinstance(metrics, list) or len(metrics) != 11:
        errors.append("scorecard must contain 11 metrics")
    else:
        for m in metrics:
            if not isinstance(m, dict):
                errors.append("scorecard metric is not an object")
                continue
            if m.get("status") != "PASS":
                errors.append(f"metric {m.get('metric_id')} is not PASS")
            if "not" not in str(m.get("non_claims") or "").lower():
                errors.append(f"metric {m.get('metric_id')} missing explicit non_claims")

    rows = read_csv(OUTDIR / "evaluator-scorecard.csv")
    if len(rows) != 11:
        errors.append("evaluator-scorecard.csv must contain 11 metric rows")
    if not all(r.get("status") == "PASS" and r.get("non_claims") for r in rows):
        errors.append("evaluator-scorecard.csv rows must all PASS and carry non_claims")

    public = (OUTDIR / "public-evaluator-scorecard.md").read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["synthetic example only", "not live election evidence", "not certification", "not proof of intent or fraud", "not legal advice"]:
        if phrase not in public:
            errors.append(f"public-evaluator-scorecard.md missing boundary phrase {phrase!r}")
    if "certifies" in public or "proves fraud" in public:
        errors.append("public-evaluator-scorecard.md contains prohibited certification/fraud inference language")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: Example County evaluator scorecard ({shipped['total_points']}/{shipped['max_points']}, {VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
