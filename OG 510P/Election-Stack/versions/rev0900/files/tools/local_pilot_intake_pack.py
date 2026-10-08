#!/usr/bin/env python3
"""Build the local-pilot intake/no-go pack.

This tool turns the live-pilot no-go condition into a concrete, auditable gap
matrix. It is intentionally conservative: in this archive, every row remains a
synthetic placeholder until a jurisdiction supplies local evidence, owners,
source-refresh records, review transcripts, and legal boundaries.
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
REG = ROOT / "artifacts" / "registries" / "local-pilot-intake-requirements.csv"
REPORTS = ROOT / "artifacts" / "reports"

BOUNDARY = (
    "Local-pilot intake support only; not live election evidence, not live-pilot authorization, "
    "not certification, not current voter instruction, not outcome proof, not proof of intent or fraud, "
    "and not legal advice."
)
DECISION = "NO_GO_LIVE_PILOT_LOCAL_INTAKE_INCOMPLETE"

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


def build_matrix() -> dict[str, Any]:
    reqs = read_csv(REG)
    rows: list[dict[str, Any]] = []
    missing_support_refs: list[str] = []
    for r in reqs:
        evidence_refs = tokens(r.get("evidence_template_refs", ""))
        support_refs = tokens(r.get("release_support_refs", ""))
        evidence_ref_status = [ref_status(x) for x in evidence_refs]
        support_ref_status = [ref_status(x) for x in support_refs]
        for rs in evidence_ref_status + support_ref_status:
            if not rs.get("exists"):
                missing_support_refs.append(str(rs.get("ref") or ""))
        live_gate = r.get("live_pilot_gate", "")
        status = "MISSING_LOCAL_EVIDENCE"
        rows.append({
            "requirement_id": r.get("requirement_id"),
            "phase": r.get("phase"),
            "requirement": r.get("requirement"),
            "owner_role": r.get("owner_role"),
            "status": status,
            "required_for_live_pilot": True,
            "live_pilot_gate": live_gate,
            "evidence_template_refs": evidence_refs,
            "release_support_refs": support_refs,
            "evidence_ref_status": evidence_ref_status,
            "support_ref_status": support_ref_status,
            "synthetic_placeholder_status": r.get("synthetic_placeholder_status"),
            "public_boundary": r.get("public_boundary"),
            "non_claims": r.get("non_claims"),
            "next_action": next_action_for(r),
        })
    blocking = [r for r in rows if str(r.get("live_pilot_gate") or "").startswith("blocks")]
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision_id": f"LPI-{VERSION}",
        "decision": DECISION,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "requirement_count": len(rows),
        "blocking_requirement_count": len(blocking),
        "missing_live_evidence_count": len(rows),
        "missing_support_ref_count": len([x for x in missing_support_refs if x]),
        "rows": rows,
        "boundary": BOUNDARY,
        "non_claims": [
            "This intake pack does not authorize any live election pilot.",
            "This intake pack does not certify any election system or election outcome.",
            "This intake pack does not determine current voter instructions or legal rights.",
            "This intake pack does not replace local counsel, public-records review, or statutory election procedure.",
        ],
    }


def next_action_for(row: dict[str, str]) -> str:
    phase = row.get("phase", "")
    actions = {
        "authority_and_scope": "Complete the local configuration worksheet and record the named sponsor, scope, and approval pointer.",
        "official_channels": "Populate the official-channel map and confirm who can correct each surface.",
        "source_freshness": "Refresh, pin, or locally confirm every current-authority source used by the pilot.",
        "data_minimization": "Record prohibited data categories, redaction floor, and private-data handling before capture.",
        "publication_contracts": "Define expected notices, deadlines, and missingness conditions for the local pilot.",
        "witness_set": "Name witness roles, replacement rules, and disagreement handling before relying on witnesses.",
        "offline_verification": "Run the offline drill for the target release ZIP and preserve the transcript.",
        "human_review_escalation": "Assign reviewer roles and escalation routes for each failure mode.",
        "retention_and_disposition": "Map local retention, disposition, sealed-material, and public-records routing.",
        "external_review": "Schedule and log a bounded external review or challenge session.",
        "accessibility_language": "Review public summaries for local accessibility and language-access obligations.",
        "legal_admissibility": "Obtain counsel-reviewed local boundaries before legal, court, or records language.",
        "ai_use_controls": "Record human approval, PII discipline, and prohibited-use boundaries for AI-assisted output.",
        "incident_public_communications": "Name the incident communications owner and safe public bulletin rules.",
        "public_release_redaction": "Record redaction policy, public/private field decisions, reviewer approval, and exception handling before publication.",
        "evidence_custody_provenance": "Record capture authorization, collector role, transfer digests, access logs, chain-gap exceptions, and disposition records before field-evidence reliance.",
        "independent_review_conflict": "Record reviewer independence, conflicts, qualifications, reproducibility transcript, dissent route, public-summary approval, and remediation/retest closure before validation claims.",
    }
    return actions.get(phase, "Add jurisdiction-specific evidence and owner approval before live use.")


def build_burndown(matrix: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in matrix.get("rows") or []:
        if isinstance(row, dict):
            grouped[str(row.get("phase") or "unknown")].append(row)
    rows = []
    for phase in sorted(grouped):
        vals = grouped[phase]
        rows.append({
            "phase": phase,
            "requirement_count": len(vals),
            "missing_live_evidence_count": sum(1 for r in vals if r.get("status") == "MISSING_LOCAL_EVIDENCE"),
            "blocking_gate_count": sum(1 for r in vals if str(r.get("live_pilot_gate") or "").startswith("blocks")),
            "first_next_action": str(vals[0].get("next_action") or "") if vals else "",
            "non_claims": BOUNDARY,
        })
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision": matrix.get("decision"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "phase_count": len(rows),
        "rows": rows,
        "boundary": BOUNDARY,
    }


def notice_md(matrix: dict[str, Any], burndown: dict[str, Any]) -> str:
    lines = [
        "# Local pilot intake no-go notice",
        "",
        f"Archive version: `{matrix['archive_version']}`  ",
        f"Release date: `{matrix['release_date']}`  ",
        "",
        "**No-go for live pilot use. Synthetic-only. This is not live election evidence, not authorization, not certification, not current voter instruction, and not legal advice.**",
        "",
        "## Decision",
        "",
        f"`{matrix['decision']}`",
        "",
        "The archive contains a complete synthetic rehearsal path, but it does not contain jurisdiction-specific authorization, local official-channel confirmation, source refresh or pinning for current public authority, privacy and retention approvals, custody/provenance records, independent-review/conflict evidence, an offline drill transcript, external-review evidence, or counsel-reviewed legal boundaries.",
        "",
        "## Current intake state",
        "",
        f"- Requirements: `{matrix['requirement_count']}`.",
        f"- Blocking requirements: `{matrix['blocking_requirement_count']}`.",
        f"- Missing live-evidence rows: `{matrix['missing_live_evidence_count']}`.",
        f"- Intake phases: `{burndown['phase_count']}`.",
        "",
        "## Promotion condition",
        "",
        "Regenerate this pack with jurisdiction-specific evidence pointers, named owners, review dates, and public-boundary language. Live promotion remains no-go until every blocking row is closed or an accountable local exception is recorded.",
        "",
        "## First actions",
        "",
    ]
    for r in matrix.get("rows") or []:
        lines.append(f"- `{r['requirement_id']}` / `{r['phase']}` — {r['next_action']}")
    lines += ["", "## Boundary", "", BOUNDARY, ""]
    return "\n".join(lines)


def write_outputs() -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    burndown = build_burndown(matrix)
    (REPORTS / "local-pilot-intake-matrix.json").write_text(json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "local-pilot-intake-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["requirement_id", "phase", "owner_role", "status", "live_pilot_gate", "evidence_template_refs", "release_support_refs", "next_action", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in matrix["rows"]:
            w.writerow({
                "requirement_id": r["requirement_id"],
                "phase": r["phase"],
                "owner_role": r["owner_role"],
                "status": r["status"],
                "live_pilot_gate": r["live_pilot_gate"],
                "evidence_template_refs": "; ".join(r["evidence_template_refs"]),
                "release_support_refs": "; ".join(r["release_support_refs"]),
                "next_action": r["next_action"],
                "public_boundary": r["public_boundary"],
                "non_claims": r["non_claims"],
            })
    (REPORTS / "local-pilot-gap-burndown.json").write_text(json.dumps(burndown, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "local-pilot-gap-burndown.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["phase", "requirement_count", "missing_live_evidence_count", "blocking_gate_count", "first_next_action", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(burndown["rows"])
    (REPORTS / "local-pilot-no-go-notice.md").write_text(notice_md(matrix, burndown), encoding="utf-8")
    return {"intake_matrix": matrix, "gap_burndown": burndown}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic local-pilot intake reports")
    ap.add_argument("--json", action="store_true", help="Print generated JSON")
    args = ap.parse_args()
    out = write_outputs() if args.write else {"intake_matrix": build_matrix()}
    if not args.write:
        out["gap_burndown"] = build_burndown(out["intake_matrix"])
    if args.json:
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        m = out["intake_matrix"]
        print(f"decision={m['decision']} version={m['archive_version']} requirements={m['requirement_count']} missing={m['missing_live_evidence_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
