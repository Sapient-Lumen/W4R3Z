#!/usr/bin/env python3
"""Validate scenario -> recovery -> human-review crosswalk coverage."""
from __future__ import annotations
import csv, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts/registries"
CROSSWALK = REG / "scenario-recovery-crosswalk.csv"
EVALS = REG / "evaluation-scenarios.csv"
TRP = REG / "trust-recovery-playbook.csv"
HRH = REG / "human-review-handoff-playbook.csv"
SCENARIO = ROOT / "artifacts/examples/example_county_2026_municipal_pilot/scenario.json"
REQUIRED_HEADER = ["scenario_id","track","recovery_ids","human_review_ids","required_outputs","public_boundary_sentence","non_claims"]
ALLOWED_TRACKS = {"A", "Shared"}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k:(v or "").strip() for k,v in r.items()} for r in csv.DictReader(f)]

def split_ids(cell: str) -> list[str]:
    return [x.strip() for x in (cell or "").split(";") if x.strip()]

def main() -> int:
    errors: list[str] = []
    for p in [CROSSWALK, EVALS, TRP, HRH, SCENARIO]:
        if not p.exists(): errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        for e in errors: print("ERROR:", e, file=sys.stderr)
        return 2
    with CROSSWALK.open("r", encoding="utf-8", newline="") as f:
        raw = list(csv.reader(f))
    if not raw:
        print("ERROR: scenario-recovery-crosswalk.csv is empty", file=sys.stderr); return 2
    header = [h.strip() for h in raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    rows = read_csv(CROSSWALK)
    eval_rows = read_csv(EVALS)
    eval_ids = {r["scenario_id"] for r in eval_rows if r.get("scenario_id")}
    trp_ids = {r["recovery_id"] for r in read_csv(TRP) if r.get("recovery_id")}
    hrh_ids = {r["review_id"] for r in read_csv(HRH) if r.get("review_id")}
    seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        sid = row.get("scenario_id", "")
        label = f"L{idx} {sid or '?'}"
        if sid in seen: errors.append(f"{label}: duplicate scenario_id")
        seen.add(sid)
        if sid not in eval_ids: errors.append(f"{label}: scenario_id not in evaluation-scenarios.csv")
        if row.get("track") not in ALLOWED_TRACKS: errors.append(f"{label}: invalid track {row.get('track')!r}")
        rec = split_ids(row.get("recovery_ids", ""))
        hrs = split_ids(row.get("human_review_ids", ""))
        if not rec: errors.append(f"{label}: missing recovery_ids")
        if not hrs: errors.append(f"{label}: missing human_review_ids")
        for rid in rec:
            if rid not in trp_ids: errors.append(f"{label}: unknown recovery_id {rid}")
        for hid in hrs:
            if hid not in hrh_ids: errors.append(f"{label}: unknown human_review_id {hid}")
        if not row.get("required_outputs"): errors.append(f"{label}: missing required_outputs")
        if not row.get("public_boundary_sentence", "").endswith("."):
            errors.append(f"{label}: public_boundary_sentence must end with a period")
        if "not" not in row.get("non_claims", "").lower():
            errors.append(f"{label}: non_claims must include not-language")
    missing = sorted(eval_ids - seen)
    extra = sorted(seen - eval_ids)
    if missing: errors.append("crosswalk missing evaluation scenarios: " + ", ".join(missing))
    if extra: errors.append("crosswalk has extra scenario ids: " + ", ".join(extra))
    try:
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        scen_evals = {str(x).strip() for x in (scenario.get("evaluation_scenarios") or [])}
        if scen_evals != eval_ids:
            errors.append("scenario.json evaluation_scenarios must equal evaluation-scenarios.csv ids")
    except Exception as exc:
        errors.append(f"scenario.json parse failed: {exc}")
    if errors:
        for e in errors: print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: scenario recovery crosswalk ({len(rows)} scenario(s))")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
