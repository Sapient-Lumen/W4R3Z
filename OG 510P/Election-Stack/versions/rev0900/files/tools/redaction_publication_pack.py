#!/usr/bin/env python3
"""Build the redaction/public-publication no-go pack.

The stack now has a live-pilot intake gate, but public release of evidence-derived
artifacts needs its own privacy/data-minimization gate. This tool turns the
redaction policy registry into deterministic reports for maintainers and local
reviewers. In this archive every row remains synthetic until a local jurisdiction
adds reviewer approval or a documented exception.
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
REG = ROOT / "artifacts" / "registries" / "redaction-publication-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"

BOUNDARY = (
    "Redaction and public-publication support only; not live election evidence, not public-release authorization, "
    "not certification, not current voter instruction, not an outcome proof, not proof of intent or fraud, "
    "not a public-records ruling, and not legal advice."
)
DECISION = "NO_GO_PUBLIC_RELEASE_REDACTION_REVIEW_INCOMPLETE"
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
    family = row.get("evidence_family", "")
    actions = {
        "official_channel_directory": "Confirm which contacts are official public channels and remove private staff contact details.",
        "public_notice_feed": "Publish digest and notice timing only after draft metadata and private correction notes are removed.",
        "public_surface_parity_snapshot": "Generalize probe vantage data and remove device, account, and network identifiers before public release.",
        "missingness_record": "Preserve expected artifact and deadline while redacting witness contacts and internal speculation.",
        "witness_set": "Separate public witness roles from private safety/contact details before publishing witness evidence.",
        "key_compromise_event": "Publish trust-status facts while withholding exploit details and active containment data until reviewed.",
        "intimidation_or_safety_report": "Route help and preserve evidence without publishing names, precise personal locations, or unreviewed allegations.",
        "official_ai_use_review_log": "Publish human approval and AI-use boundary while removing prompts, PII, drafts, and unapproved outputs.",
        "human_review_worksheet": "Publish decision class and next action only after private deliberation and legal notes are removed.",
        "court_packet_index": "Publish digest index and sealed/private flags only after legal and records review.",
        "source_review_reports": "Publish source-review queue status without implying current voter instruction or source correctness.",
        "negative_control_report": "Publish expected-failure status without turning fixtures into exploit recipes.",
        "local_pilot_intake": "Publish missing-evidence categories and no-go state while withholding draft local contacts and exceptions.",
        "redaction_publication_gate": "Keep all public-release promotion blocked until every applicable policy row has approval or local exception.",
    }
    return actions.get(family, "Apply the registry redaction floor and record local reviewer approval before publication.")


def build_matrix() -> dict[str, Any]:
    policies = read_csv(REG)
    rows: list[dict[str, Any]] = []
    missing_refs: list[str] = []
    for r in policies:
        template_refs = tokens(r.get("template_refs", ""))
        support_refs = tokens(r.get("support_refs", ""))
        template_status = [ref_status(x) for x in template_refs]
        support_status = [ref_status(x) for x in support_refs]
        for rs in template_status + support_status:
            if not rs.get("exists"):
                missing_refs.append(str(rs.get("ref") or ""))
        rows.append({
            "policy_id": r.get("policy_id"),
            "evidence_family": r.get("evidence_family"),
            "status": "MISSING_LOCAL_REDACTION_APPROVAL",
            "private_data_risk": r.get("private_data_risk"),
            "public_release_floor": r.get("public_release_floor"),
            "required_redactions": r.get("required_redactions"),
            "reviewer_role": r.get("reviewer_role"),
            "release_gate": r.get("release_gate"),
            "template_refs": template_refs,
            "support_refs": support_refs,
            "template_ref_status": template_status,
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
        "decision_id": f"RPP-{VERSION}",
        "decision": DECISION,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_public_release_authorization": True,
        "policy_count": len(rows),
        "blocking_policy_count": len(blocking),
        "missing_local_approval_count": len(rows),
        "missing_support_ref_count": len([x for x in missing_refs if x]),
        "rows": rows,
        "boundary": BOUNDARY,
        "non_claims": [
            "This pack does not authorize public release of local private evidence.",
            "This pack does not decide public-records disclosure obligations.",
            "This pack does not certify any election system or election outcome.",
            "This pack does not determine current voter instructions or legal rights.",
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
            "missing_local_approval_count": sum(1 for r in vals if r.get("status") == "MISSING_LOCAL_REDACTION_APPROVAL"),
            "evidence_families": "; ".join(str(r.get("evidence_family") or "") for r in vals),
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
    out: list[dict[str, str]] = []
    for row in matrix.get("rows") or []:
        out.append({
            "policy_id": str(row.get("policy_id") or ""),
            "evidence_family": str(row.get("evidence_family") or ""),
            "publishable_after_review": str(row.get("public_release_floor") or ""),
            "must_not_publish_without_review": str(row.get("required_redactions") or ""),
            "public_boundary": str(row.get("public_boundary") or ""),
            "non_claims": str(row.get("non_claims") or ""),
        })
    return out


def notice_md(matrix: dict[str, Any], burndown: dict[str, Any]) -> str:
    lines = [
        "# Redaction/public-publication no-go notice",
        "",
        f"Archive version: `{matrix['archive_version']}`  ",
        f"Release date: `{matrix['release_date']}`  ",
        "",
        "**No-go for public release of local/private evidence until redaction review is complete. Synthetic-only. This is not live election evidence, not public-release authorization, not certification, not current voter instruction, not a public-records ruling, and not legal advice.**",
        "",
        "## Decision",
        "",
        f"`{matrix['decision']}`",
        "",
        "The synthetic archive can publish example outputs, but live or local evidence-derived public artifacts need a separate reviewer-approved redaction path. This gate prevents digest evidence from accidentally carrying voter, witness, staff, device, network, safety, or legal-review data into public release.",
        "",
        "## Current redaction state",
        "",
        f"- Policies: `{matrix['policy_count']}`.",
        f"- Blocking policies: `{matrix['blocking_policy_count']}`.",
        f"- Missing local approval rows: `{matrix['missing_local_approval_count']}`.",
        f"- Release-gate families: `{burndown['gate_count']}`.",
        "",
        "## Promotion condition",
        "",
        "Regenerate this pack with local reviewer approvals, public/private field decisions, and documented exceptions. Public release remains no-go until every applicable policy row is closed or an accountable local exception is recorded.",
        "",
        "## First actions",
        "",
    ]
    for r in matrix.get("rows") or []:
        lines.append(f"- `{r['policy_id']}` / `{r['evidence_family']}` — {r['next_action']}")
    lines += ["", "## Boundary", "", BOUNDARY, ""]
    return "\n".join(lines)


def write_outputs() -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    burndown = build_burndown(matrix)
    preview = build_preview_index(matrix)
    (REPORTS / "redaction-publication-matrix.json").write_text(json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "redaction-publication-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "evidence_family", "status", "reviewer_role", "release_gate", "public_release_floor", "required_redactions", "next_action", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in matrix["rows"]:
            w.writerow({k: r.get(k, "") for k in fields})
    (REPORTS / "redaction-publication-burndown.json").write_text(json.dumps(burndown, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "redaction-publication-burndown.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["release_gate", "policy_count", "missing_local_approval_count", "evidence_families", "first_next_action", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(burndown["rows"])
    with (REPORTS / "public-release-preview-index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "evidence_family", "publishable_after_review", "must_not_publish_without_review", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(preview)
    (REPORTS / "redaction-publication-no-go-notice.md").write_text(notice_md(matrix, burndown), encoding="utf-8")
    return {"redaction_matrix": matrix, "redaction_burndown": burndown, "preview_index": preview}


def build_output() -> dict[str, Any]:
    matrix = build_matrix()
    return {"redaction_matrix": matrix, "redaction_burndown": build_burndown(matrix), "preview_index": build_preview_index(matrix)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic redaction/publication reports")
    ap.add_argument("--json", action="store_true", help="Print generated JSON")
    args = ap.parse_args()
    out = write_outputs() if args.write else build_output()
    if args.json:
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        m = out["redaction_matrix"]
        print(f"decision={m['decision']} version={m['archive_version']} policies={m['policy_count']} missing={m['missing_local_approval_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
