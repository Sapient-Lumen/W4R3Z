#!/usr/bin/env python3
"""Build the synthetic Example County human-review handoff output pack.

This deterministic helper combines the evaluation-scenario crosswalk, trust
recovery playbook, human-review playbook, and retention registry into a compact
reviewer handoff pack. It is synthetic-only and does not create live deployment
evidence.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SCENARIO = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "scenario.json"
OUTDIR = SCENARIO.parent
REG = ROOT / "artifacts" / "registries"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def split_ids(cell: str) -> list[str]:
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def build_matrix() -> dict[str, Any]:
    scenario = load_json(SCENARIO)
    eval_rows = {r["scenario_id"]: r for r in read_csv(REG / "evaluation-scenarios.csv")}
    crosswalk_rows = read_csv(REG / "scenario-recovery-crosswalk.csv")
    human_rows = {r["review_id"]: r for r in read_csv(REG / "human-review-handoff-playbook.csv")}
    recovery_rows = {r["recovery_id"]: r for r in read_csv(REG / "trust-recovery-playbook.csv")}
    retention_rows = {r["retention_id"]: r for r in read_csv(REG / "evidence-retention-disposition.csv")}

    scenarios: list[dict[str, Any]] = []
    for row in crosswalk_rows:
        sid = row["scenario_id"]
        hr_ids = split_ids(row["human_review_ids"])
        trp_ids = split_ids(row["recovery_ids"])
        scenarios.append({
            "scenario_id": sid,
            "track": row["track"],
            "adversary_or_failure": eval_rows.get(sid, {}).get("adversary_or_failure", ""),
            "recovery_ids": trp_ids,
            "human_review_ids": hr_ids,
            "review_triggers": [human_rows.get(hid, {}).get("review_trigger", "") for hid in hr_ids],
            "public_boundary_sentence": row["public_boundary_sentence"],
            "required_outputs": split_ids(row["required_outputs"]),
            "non_claims": row["non_claims"],
        })

    return {
        "archive_version": VERSION,
        "scenario_id": scenario.get("scenario_id"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "scenario_count": len(scenarios),
        "human_review_count": len(human_rows),
        "recovery_count": len(recovery_rows),
        "retention_count": len(retention_rows),
        "scenarios": scenarios,
        "human_review_playbook": list(human_rows.values()),
        "retention_disposition": list(retention_rows.values()),
        "boundary": "Synthetic human-review rehearsal only; not live election evidence, not outcome certification, not proof of intent or fraud, and not legal advice.",
    }


def worksheet_rows(matrix: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    human_by_id = {r["review_id"]: r for r in matrix.get("human_review_playbook", []) if isinstance(r, dict)}
    for scenario in matrix.get("scenarios", []):
        if not isinstance(scenario, dict):
            continue
        scenario_id = str(scenario.get("scenario_id") or "")
        for hid in scenario.get("human_review_ids") or []:
            review_id = str(hid)
            hr = human_by_id.get(review_id, {})
            rows.append({
                "worksheet_id": f"{scenario_id}-{review_id}",
                "scenario_id": scenario_id,
                "review_id": review_id,
                "review_trigger": str(hr.get("review_trigger") or ""),
                "primary_reviewer": str(hr.get("primary_reviewer") or ""),
                "secondary_reviewer": str(hr.get("secondary_reviewer") or ""),
                "worksheet_ref": str(hr.get("worksheet_ref") or ""),
                "public_boundary_sentence": str(scenario.get("public_boundary_sentence") or ""),
                "non_claims": str(hr.get("non_claims") or ""),
            })
    return rows


def quickstart_text(matrix: dict[str, Any]) -> str:
    return f"""# Example County human-review handoff quickstart

**Synthetic example only. This is not live election evidence.**

Scenario: `{matrix['scenario_id']}`  
Archive version: `{matrix['archive_version']}`  
Scenarios covered: `{matrix['scenario_count']}`  
Human-review modes: `{matrix['human_review_count']}`  
Retention dispositions: `{matrix['retention_count']}`

## Operator command

```bash
python3 tools/human_review_handoff_pack.py --json
```

## What this pack adds

- `human-review-matrix.json` maps each evaluator scenario to recovery IDs, reviewer IDs, public boundary language, and non-claims.
- `reviewer-worksheet-index.csv` lists the reviewer roles and worksheet templates needed for each scenario.
- `scenario-recovery-crosswalk.json` is a JSON copy of the crosswalk for tools that do not want to parse CSV.

## Boundary

This handoff pack helps reviewers preserve evidence, redaction rationale, dissent, and public boundary language. It is not outcome certification, not proof of intent or fraud, not legal advice, and not live deployment evidence.
"""


def build_output() -> dict[str, Any]:
    matrix = build_matrix()
    rows = worksheet_rows(matrix)
    crosswalk_json = {
        "archive_version": VERSION,
        "scenario_id": matrix["scenario_id"],
        "synthetic_only": True,
        "scenarios": matrix["scenarios"],
    }
    return {
        "matrix": matrix,
        "worksheet_rows": rows,
        "crosswalk_json": crosswalk_json,
        "quickstart": quickstart_text(matrix),
    }


def write_output_pack() -> dict[str, Any]:
    out = build_output()
    (OUTDIR / "human-review-matrix.json").write_text(
        json.dumps(out["matrix"], sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    (OUTDIR / "scenario-recovery-crosswalk.json").write_text(
        json.dumps(out["crosswalk_json"], sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    with (OUTDIR / "reviewer-worksheet-index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "worksheet_id",
            "scenario_id",
            "review_id",
            "review_trigger",
            "primary_reviewer",
            "secondary_reviewer",
            "worksheet_ref",
            "public_boundary_sentence",
            "non_claims",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out["worksheet_rows"])
    (OUTDIR / "human-review-quickstart.md").write_text(out["quickstart"], encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic human-review handoff output files")
    ap.add_argument("--json", action="store_true", help="Print human-review matrix JSON")
    args = ap.parse_args()
    out = write_output_pack() if args.write else build_output()
    if args.json:
        print(json.dumps(out["matrix"], sort_keys=True, separators=(",", ":")))
    else:
        print(f"PASS: human-review handoff output pack ({out['matrix']['scenario_count']} scenario(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
