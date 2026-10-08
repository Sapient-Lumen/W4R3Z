#!/usr/bin/env python3
"""Build the synthetic Example County trust-recovery output pack.

This deterministic helper turns the trust-recovery playbook into a public,
verifier, and preservation handoff bundle for the synthetic Example County
scenario. It is not live deployment evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SCENARIO = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "scenario.json"
OUTDIR = SCENARIO.parent
PLAYBOOK = ROOT / "artifacts" / "registries" / "trust-recovery-playbook.csv"
NON_CLAIM_PHRASES = [
    "not live election evidence",
    "does not prove that an election outcome is correct",
    "does not turn failure evidence into proof of intent or fraud",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_matrix(scenario: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "archive_version": VERSION,
        "scenario_id": scenario.get("scenario_id"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "row_count": len(rows),
        "failure_modes": [
            {
                "recovery_id": row["recovery_id"],
                "trigger": row["trigger"],
                "public_status": row["public_status"],
                "public_sentence": row["public_sentence"],
                "decision_owner": row["decision_owner"],
                "minimum_evidence": row["minimum_evidence"],
                "operator_action": row["operator_action"],
                "non_claims": row["non_claims"],
                "handoff_refs": [x.strip() for x in row["handoff_refs"].split(";") if x.strip()],
            }
            for row in rows
        ],
        "boundary": "Synthetic trust-recovery rehearsal only; not live election evidence and not outcome certification.",
    }


def handoff_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        out.append({
            "recovery_id": row["recovery_id"],
            "trigger": row["trigger"],
            "public_status": row["public_status"],
            "decision_owner": row["decision_owner"],
            "minimum_evidence": row["minimum_evidence"],
            "operator_action": row["operator_action"],
            "public_sentence": row["public_sentence"],
            "non_claims": row["non_claims"],
        })
    return out


def bulletin_text(scenario: dict[str, Any], matrix: dict[str, Any]) -> str:
    scenario_id = scenario.get("scenario_id")
    lines = [
        "# Example County trust-recovery bulletin",
        "",
        "**Synthetic example only. This is not live election evidence.**",
        "",
        f"Scenario: `{scenario_id}`  ",
        f"Archive version: `{VERSION}`  ",
        f"Failure modes covered: `{matrix['row_count']}`",
        "",
        "## Boundary",
        "",
        "This bulletin describes what the synthetic verifier/public handoff should say when evidence is missing, divergent, stale, compromised, or unverifiable. It does not prove that an election outcome is correct, does not replace canvass, audit, certification, recount, or court procedure, and does not turn failure evidence into proof of intent or fraud.",
        "",
        "## Public failure language",
        "",
    ]
    for mode in matrix["failure_modes"]:
        lines.append(f"- `{mode['recovery_id']}` / `{mode['public_status']}`: {mode['public_sentence']}")
    lines.extend([
        "",
        "## Operator command",
        "",
        "```bash",
        "python3 tools/trust_recovery_output_pack.py --json",
        "```",
        "",
    ])
    return "\n".join(lines)


def build_output() -> dict[str, Any]:
    scenario = load_json(SCENARIO)
    rows = read_csv(PLAYBOOK)
    matrix = build_matrix(scenario, rows)
    return {"matrix": matrix, "handoff_rows": handoff_rows(rows), "bulletin": bulletin_text(scenario, matrix)}


def write_output_pack() -> dict[str, Any]:
    out = build_output()
    (OUTDIR / "trust-recovery-matrix.json").write_text(json.dumps(out["matrix"], sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    fields = ["recovery_id", "trigger", "public_status", "decision_owner", "minimum_evidence", "operator_action", "public_sentence", "non_claims"]
    with (OUTDIR / "failure-handoff-index.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(out["handoff_rows"])
    (OUTDIR / "public-failure-bulletin.md").write_text(out["bulletin"], encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic trust-recovery output files")
    ap.add_argument("--json", action="store_true", help="Print trust-recovery matrix JSON")
    args = ap.parse_args()
    if args.write:
        out = write_output_pack()
    else:
        out = build_output()
    if args.json:
        print(json.dumps(out["matrix"], sort_keys=True, separators=(",", ":")))
    else:
        print(f"PASS: trust-recovery output pack ({out['matrix']['row_count']} failure mode(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
