#!/usr/bin/env python3
"""Verify the synthetic Example County human-review output pack is fresh."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SCENARIO = ROOT / "artifacts/examples/example_county_2026_municipal_pilot/scenario.json"
OUTDIR = SCENARIO.parent
TOOL = ROOT / "tools/human_review_handoff_pack.py"
REQUIRED = {
    "human-review-matrix.json",
    "reviewer-worksheet-index.csv",
    "scenario-recovery-crosswalk.json",
    "human-review-quickstart.md",
}
NON_CLAIM_PHRASES = [
    "not live election evidence",
    "not outcome certification",
    "not proof of intent or fraud",
    "not legal advice",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def run_tool_to_compare() -> dict[str, bytes]:
    before = {name: (OUTDIR / name).read_bytes() if (OUTDIR / name).exists() else b"" for name in REQUIRED}
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--write"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        text=True,
        capture_output=True,
        timeout=120,
    )
    after = {name: (OUTDIR / name).read_bytes() if (OUTDIR / name).exists() else b"" for name in REQUIRED}
    for name, data in before.items():
        (OUTDIR / name).write_bytes(data)
    if proc.returncode != 0:
        raise RuntimeError(f"human-review tool failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
    return after


def main() -> int:
    errors: list[str] = []
    for path in [SCENARIO, TOOL]:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    for name in REQUIRED:
        if not (OUTDIR / name).exists():
            errors.append(f"missing human-review output file: {name}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    try:
        generated = run_tool_to_compare()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    for name, got in generated.items():
        have = (OUTDIR / name).read_bytes()
        if got != have:
            errors.append(f"human-review output drift: {name}; run `python3 tools/human_review_handoff_pack.py --write`")
    scenario = load_json(SCENARIO)
    matrix = load_json(OUTDIR / "human-review-matrix.json")
    crosswalk_json = load_json(OUTDIR / "scenario-recovery-crosswalk.json")
    rows = read_csv(OUTDIR / "reviewer-worksheet-index.csv")
    if scenario.get("archive_version") != VERSION:
        errors.append("scenario archive_version does not match VERSION")
    if matrix.get("archive_version") != VERSION:
        errors.append("human-review matrix archive_version does not match VERSION")
    if matrix.get("scenario_id") != scenario.get("scenario_id"):
        errors.append("human-review matrix scenario_id does not match scenario")
    if matrix.get("synthetic_only") is not True or matrix.get("no_live_deployment_claim") is not True:
        errors.append("matrix must be synthetic-only and no-live-deployment-claim")
    if int(matrix.get("scenario_count") or 0) < 10:
        errors.append("matrix must cover at least 10 scenarios")
    if int(matrix.get("human_review_count") or 0) < 10:
        errors.append("matrix must cover at least 10 human review modes")
    if int(matrix.get("retention_count") or 0) < 8:
        errors.append("matrix must cover at least 8 retention dispositions")
    if crosswalk_json.get("archive_version") != VERSION:
        errors.append("scenario-recovery-crosswalk.json archive_version mismatch")
    if len(rows) < int(matrix.get("scenario_count") or 0):
        errors.append("reviewer-worksheet-index has too few rows")
    quickstart = (OUTDIR / "human-review-quickstart.md").read_text(encoding="utf-8").lower()
    boundary = str(matrix.get("boundary") or "").lower() + "\n" + quickstart
    for phrase in NON_CLAIM_PHRASES:
        if phrase not in boundary:
            errors.append(f"human-review output missing non-claim phrase: {phrase}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: Example County human-review output pack ({VERSION}, {matrix.get('scenario_count')} scenario(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
