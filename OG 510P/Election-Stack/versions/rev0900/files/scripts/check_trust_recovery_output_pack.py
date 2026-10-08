#!/usr/bin/env python3
"""Verify the synthetic Example County trust-recovery output pack is fresh."""

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
PLAYBOOK = ROOT / "artifacts/registries/trust-recovery-playbook.csv"
TOOL = ROOT / "tools/trust_recovery_output_pack.py"
REQUIRED = {"trust-recovery-matrix.json", "failure-handoff-index.csv", "public-failure-bulletin.md"}
NON_CLAIM_PHRASES = [
    "not live election evidence",
    "does not prove that an election outcome is correct",
    "does not turn failure evidence into proof of intent or fraud",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def run_tool_to_compare() -> dict[str, bytes]:
    before = {name: (OUTDIR / name).read_bytes() if (OUTDIR / name).exists() else b"" for name in REQUIRED}
    proc = subprocess.run([sys.executable, str(TOOL), "--write"], cwd=ROOT, stdin=subprocess.DEVNULL, text=True, capture_output=True, timeout=120)
    after = {name: (OUTDIR / name).read_bytes() if (OUTDIR / name).exists() else b"" for name in REQUIRED}
    for name, data in before.items():
        (OUTDIR / name).write_bytes(data)
    if proc.returncode != 0:
        raise RuntimeError(f"trust-recovery tool failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
    return after


def main() -> int:
    errors: list[str] = []
    for path in [SCENARIO, PLAYBOOK, TOOL]:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    for name in REQUIRED:
        if not (OUTDIR / name).exists():
            errors.append(f"missing trust-recovery output file: {name}")
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
            errors.append(f"trust-recovery output drift: {name}; run `python3 tools/trust_recovery_output_pack.py --write`")

    scenario = load_json(SCENARIO)
    matrix = load_json(OUTDIR / "trust-recovery-matrix.json")
    playbook_rows = read_csv(PLAYBOOK)
    handoff_rows = read_csv(OUTDIR / "failure-handoff-index.csv")
    if scenario.get("archive_version") != VERSION:
        errors.append("scenario archive_version does not match VERSION")
    if matrix.get("archive_version") != VERSION:
        errors.append("trust-recovery matrix archive_version does not match VERSION")
    if matrix.get("scenario_id") != scenario.get("scenario_id"):
        errors.append("trust-recovery matrix scenario_id does not match scenario")
    if matrix.get("synthetic_only") is not True or matrix.get("no_live_deployment_claim") is not True:
        errors.append("trust-recovery matrix must be synthetic-only and no-live-deployment-claim")
    if matrix.get("row_count") != len(playbook_rows):
        errors.append("trust-recovery matrix row_count does not match playbook")
    if len(handoff_rows) != len(playbook_rows):
        errors.append("failure-handoff-index row count does not match playbook")
    ids_matrix = {str(x.get("recovery_id")) for x in matrix.get("failure_modes") or [] if isinstance(x, dict)}
    ids_playbook = {r.get("recovery_id") for r in playbook_rows}
    ids_handoff = {r.get("recovery_id") for r in handoff_rows}
    if ids_matrix != ids_playbook:
        errors.append("trust-recovery matrix ids do not match playbook")
    if ids_handoff != ids_playbook:
        errors.append("failure-handoff-index ids do not match playbook")
    bulletin = (OUTDIR / "public-failure-bulletin.md").read_text(encoding="utf-8").lower()
    for phrase in NON_CLAIM_PHRASES:
        if phrase not in bulletin:
            errors.append(f"public-failure-bulletin missing non-claim phrase: {phrase}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: Example County trust-recovery output pack ({VERSION}, {len(playbook_rows)} mode(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
