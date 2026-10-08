#!/usr/bin/env python3
"""Build the independent-review/conflict no-go pack.

Self-tests and synthetic evaluator PASS results are useful, but they are not
independent validation.  This tool turns review/conflict policy rows into a
machine-readable no-go matrix that blocks third-party-validation, live-pilot,
public-review, challenge-session, and legal/admissibility-adjacent claims until
local review evidence exists.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
RELEASE_DATE = release_date(ROOT)
REG = ROOT / "artifacts" / "registries" / "independent-review-conflict-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"

BOUNDARY = (
    "Independent-review/conflict support only; not third-party validation, not certification, "
    "not live-pilot authorization, not current voter instruction, not public-release authorization, "
    "not an admissibility opinion, not authorization to test live systems, and not legal advice."
)
DECISION = "NO_GO_INDEPENDENT_REVIEW_CONFLICT_EVIDENCE_INCOMPLETE"
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def tokens(cell: str) -> list[str]:
    return [raw.strip() for raw in (cell or "").split(";") if raw.strip()]


def ref_status(ref: str) -> dict[str, Any]:
    m = TOKEN_RE.match(ref)
    if not m:
        return {"ref": ref, "parseable": False, "exists": False, "path": ""}
    rel = m.group("path")
    return {"ref": ref, "parseable": True, "exists": (ROOT / rel).exists(), "path": rel}


def next_action_for(row: dict[str, str]) -> str:
    family = row.get("review_family", "")
    actions = {
        "reviewer_independence_scope": "Name reviewers, relationship to sponsor/vendor/implementer, scope, exclusions, and approver before saying independent.",
        "conflict_of_interest_disclosure": "Collect COI disclosures, mitigations, recusals, unresolved-conflict notes, and expiry dates.",
        "reviewer_qualification_and_limits": "Record reviewer qualifications, method limits, evidence access limits, and out-of-scope domains.",
        "evidence_selection_and_sampling_plan": "Pre-register artifacts, scenario samples, negative controls, source rows, and exclusions before review.",
        "reproducibility_transcript": "Preserve release ZIP hash, extraction path, commands, environment notes, verifier outputs, failures, and deviations.",
        "dissent_and_minority_report": "Create a dissent/minority-report route and preserve unresolved disagreements with a safe public sentence.",
        "public_summary_approval": "Require reviewer approval of public summary language, non-claims, unresolved issues, and scope limits.",
        "reviewer_privacy_and_safety_constraints": "Record private/sealed access class, minimization rule, safe-contact route, and redaction constraints.",
        "adversarial_challenge_and_red_team_bounds": "Define allowed targets, prohibited targets, authorization, disclosure route, rate limits, and stop conditions.",
        "legal_records_boundary_review": "Route legal, records, court, and admissibility-adjacent language to local counsel/records owners.",
        "reviewer_access_and_chain_records": "Log evidence provided to reviewers, transfer digests, sealed/private fields, and return/disposition rules.",
        "remediation_retest_closure": "For each finding, record remediation owner, changed artifact, retest command, old/new result, and residual risk.",
        "external_review_public_nonclaim": "Attach reviewer-approved non-claims to external-review summaries before public use.",
        "independent_review_gate": "Keep independent-validation and live-pilot claims no-go until every review row is closed or locally excepted.",
    }
    return actions.get(family, "Record local independent-review evidence and reviewer approval before promotion.")


def build_matrix() -> dict[str, Any]:
    policies = read_csv(REG)
    rows: list[dict[str, Any]] = []
    missing_refs: list[str] = []
    for r in policies:
        worksheet_refs = tokens(r.get("worksheet_refs", ""))
        support_refs = tokens(r.get("support_refs", ""))
        worksheet_status = [ref_status(x) for x in worksheet_refs]
        support_status = [ref_status(x) for x in support_refs]
        for rs in worksheet_status + support_status:
            if not rs.get("exists"):
                missing_refs.append(str(rs.get("ref") or ""))
        rows.append({
            "policy_id": r.get("policy_id"),
            "review_family": r.get("review_family"),
            "status": "MISSING_INDEPENDENT_REVIEW_EVIDENCE",
            "review_risk": r.get("review_risk"),
            "review_floor": r.get("review_floor"),
            "required_records": r.get("required_records"),
            "reviewer_role": r.get("reviewer_role"),
            "release_gate": r.get("release_gate"),
            "worksheet_refs": worksheet_refs,
            "support_refs": support_refs,
            "worksheet_ref_status": worksheet_status,
            "support_ref_status": support_status,
            "synthetic_status": r.get("synthetic_status"),
            "public_boundary": r.get("public_boundary"),
            "non_claims": r.get("non_claims"),
            "next_action": next_action_for(r),
        })
    blocking = [r for r in rows if str(r.get("release_gate") or "").startswith("blocks")]
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision_id": f"IRC-{VERSION}",
        "decision": DECISION,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_third_party_validation_claim": True,
        "no_certification_claim": True,
        "no_live_pilot_authorization": True,
        "no_public_release_authorization": True,
        "no_admissibility_opinion": True,
        "no_live_system_testing_authorization": True,
        "policy_count": len(rows),
        "blocking_policy_count": len(blocking),
        "missing_independent_review_evidence_count": len(rows),
        "missing_support_ref_count": len([x for x in missing_refs if x]),
        "rows": rows,
        "boundary": BOUNDARY,
        "non_claims": [
            "This pack does not create or certify independent review.",
            "This pack does not authorize live pilot use, public release, or live-system testing.",
            "This pack does not prove outcome correctness, system security, intent, fraud, or misconduct.",
            "This pack does not replace local counsel, public-records review, ethics review, or election-office procedure.",
        ],
    }


def build_burndown(matrix: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in matrix.get("rows") or []:
        if isinstance(row, dict):
            grouped[str(row.get("release_gate") or "unknown")].append(row)
    rows = []
    for gate in sorted(grouped):
        vals = grouped[gate]
        rows.append({
            "release_gate": gate,
            "policy_count": len(vals),
            "missing_independent_review_evidence_count": sum(1 for r in vals if r.get("status") == "MISSING_INDEPENDENT_REVIEW_EVIDENCE"),
            "review_families": "; ".join(str(r.get("review_family") or "") for r in vals),
            "first_next_action": str(vals[0].get("next_action") or "") if vals else "",
            "non_claims": BOUNDARY,
        })
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision": matrix.get("decision"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "gate_count": len(rows),
        "rows": rows,
        "boundary": BOUNDARY,
    }


def build_preview_index(matrix: dict[str, Any]) -> list[dict[str, str]]:
    return [{
        "policy_id": str(row.get("policy_id") or ""),
        "review_family": str(row.get("review_family") or ""),
        "required_records": str(row.get("required_records") or ""),
        "reviewer_role": str(row.get("reviewer_role") or ""),
        "public_boundary": str(row.get("public_boundary") or ""),
        "non_claims": str(row.get("non_claims") or ""),
    } for row in matrix.get("rows") or []]


def notice_md(matrix: dict[str, Any], burndown: dict[str, Any]) -> str:
    lines = [
        "# Independent review/conflict no-go notice",
        "",
        f"Archive version: `{matrix['archive_version']}`  ",
        f"Release date: `{matrix['release_date']}`  ",
        "",
        "**No-go for independent-validation, live-pilot, public-review, challenge-session, or legal/admissibility-adjacent claims until local independent-review evidence exists. Synthetic-only. This is not third-party validation, not certification, not live authorization, not public-release authorization, not authorization to test live systems, and not legal advice.**",
        "",
        "## Decision",
        "",
        f"`{matrix['decision']}`",
        "",
        "The archive can verify its own synthetic packets and expected-failure fixtures, but independent review needs named reviewers, conflict disclosures, scope limits, reproducibility transcripts, dissent routes, reviewer access/custody records, public-summary approvals, challenge authorization, legal/records routing, and remediation/retest closure.",
        "",
        "## Current review state",
        "",
        f"- Policies: `{matrix['policy_count']}`.",
        f"- Blocking policies: `{matrix['blocking_policy_count']}`.",
        f"- Missing independent-review evidence: `{matrix['missing_independent_review_evidence_count']}`.",
        f"- Release-gate families: `{burndown['gate_count']}`.",
        "",
        "## Promotion condition",
        "",
        "Regenerate this pack with jurisdiction-specific reviewer records, COI disclosures, transcripts, reviewer-approved public language, findings/retest closure, and local exceptions. Independent-validation and live-pilot claims remain no-go until every applicable row is closed or an accountable local exception is recorded.",
        "",
        "## First actions",
        "",
    ]
    for r in matrix.get("rows") or []:
        lines.append(f"- `{r['policy_id']}` / `{r['review_family']}` — {r['next_action']}")
    lines += ["", "## Boundary", "", BOUNDARY, ""]
    return "\n".join(lines)


def write_outputs() -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    burndown = build_burndown(matrix)
    preview = build_preview_index(matrix)
    (REPORTS / "independent-review-matrix.json").write_text(json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "independent-review-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "review_family", "reviewer_role", "status", "release_gate", "worksheet_refs", "support_refs", "next_action", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in matrix["rows"]:
            w.writerow({
                "policy_id": row["policy_id"],
                "review_family": row["review_family"],
                "reviewer_role": row["reviewer_role"],
                "status": row["status"],
                "release_gate": row["release_gate"],
                "worksheet_refs": "; ".join(row["worksheet_refs"]),
                "support_refs": "; ".join(row["support_refs"]),
                "next_action": row["next_action"],
                "public_boundary": row["public_boundary"],
                "non_claims": row["non_claims"],
            })
    (REPORTS / "independent-review-burndown.json").write_text(json.dumps(burndown, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "independent-review-burndown.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["release_gate", "policy_count", "missing_independent_review_evidence_count", "review_families", "first_next_action", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(burndown["rows"])
    with (REPORTS / "reviewer-role-preview-index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "review_family", "required_records", "reviewer_role", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(preview)
    (REPORTS / "independent-review-no-go-notice.md").write_text(notice_md(matrix, burndown), encoding="utf-8")
    return {"review_matrix": matrix, "review_burndown": burndown, "reviewer_role_preview_index": preview}


def build_output() -> dict[str, Any]:
    matrix = build_matrix()
    return {"review_matrix": matrix, "review_burndown": build_burndown(matrix), "reviewer_role_preview_index": build_preview_index(matrix)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic independent-review/conflict no-go reports")
    ap.add_argument("--json", action="store_true", help="Print independent-review/conflict JSON wrapper")
    args = ap.parse_args()
    out = write_outputs() if args.write else build_output()
    if args.json:
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        m = out["review_matrix"]
        print(f"PASS: independent review/conflict pack ({m['archive_version']}, policies={m['policy_count']}, decision={m['decision']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
