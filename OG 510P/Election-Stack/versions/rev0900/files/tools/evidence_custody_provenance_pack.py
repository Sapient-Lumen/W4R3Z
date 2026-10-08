#!/usr/bin/env python3
"""Build the evidence custody/provenance no-go pack.

Byte verification is necessary but not sufficient for live use. This tool turns
custody policy rows into deterministic reports that block promotion until local
capture, transfer, access, sealing, derivative, and disposition records exist.
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
REG = ROOT / "artifacts" / "registries" / "evidence-custody-provenance-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"

BOUNDARY = (
    "Evidence custody/provenance support only; not live election evidence, not live-pilot authorization, "
    "not chain-of-custody certification, not public-records authorization, not admissibility opinion, "
    "not outcome proof, not proof of intent or fraud, and not legal advice."
)
DECISION = "NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE_INCOMPLETE"
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
        "capture_scope_authorization": "Record who authorized collection, what surfaces are in scope, and what data is excluded before capture.",
        "collector_identity_and_role": "Bind each collector to a role, affiliation/COI note, training status, and equipment-owner record.",
        "capture_environment_and_tooling": "Record tool/archive version, time source, vantage point, and capture limitations while minimizing private identifiers.",
        "digest_manifest_and_payload_lineage": "Preserve payload, manifest, report, and command lineage for every packet or derivative.",
        "custody_transfer_handoff": "Record from/to custodian, timestamp, storage medium, and pre/post transfer digests for every handoff.",
        "access_log_and_review_window": "Record who accessed evidence, why, when, and whether private fields were visible.",
        "sealed_or_sensitive_material": "Separate sealed/private fields from public derivatives and document withholding reasons.",
        "public_derivative_lineage": "Link public summaries, quickstarts, screenshots, and bulletins to source evidence, redaction rule, and correction pointer.",
        "incident_evidence_freeze": "Freeze incident evidence before interpretation and attach a safe public sentence plus non-claims.",
        "offline_drill_transcript_custody": "Preserve offline drill transcript digest, ZIP digest, verifier role, machine description, and manifest result.",
        "source_review_and_pin_custody": "Record source-review reviewer, date, pin/demotion reason, and affected artifacts.",
        "chain_gap_exception_and_dissent": "Make chain gaps, exceptions, reviewer dissent, owners, and expiry dates visible before relying on evidence.",
        "retention_disposition_and_destruction": "Record disposition action, retention rule, digest, owner, legal hold, and date.",
        "custody_provenance_gate": "Keep live promotion no-go until every applicable custody row has local records or documented exceptions.",
    }
    return actions.get(family, "Record local custody evidence and reviewer approval before live use.")


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
            "evidence_family": r.get("evidence_family"),
            "status": "MISSING_LOCAL_CUSTODY_RECORD",
            "custody_risk": r.get("custody_risk"),
            "custody_floor": r.get("custody_floor"),
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
        "decision_id": f"ECP-{VERSION}",
        "decision": DECISION,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_live_pilot_authorization": True,
        "no_chain_of_custody_certification": True,
        "no_public_records_authorization": True,
        "no_admissibility_opinion": True,
        "policy_count": len(rows),
        "blocking_policy_count": len(blocking),
        "missing_local_custody_record_count": len(rows),
        "missing_support_ref_count": len([x for x in missing_refs if x]),
        "rows": rows,
        "boundary": BOUNDARY,
        "non_claims": [
            "This pack does not authorize a live pilot or public release of local evidence.",
            "This pack does not certify chain of custody or court admissibility.",
            "This pack does not prove election outcome correctness, intent, fraud, or misconduct.",
            "This pack does not replace local counsel, public-records, retention, or election-office procedure.",
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
            "missing_local_custody_record_count": sum(1 for r in vals if r.get("status") == "MISSING_LOCAL_CUSTODY_RECORD"),
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
    return [{
        "policy_id": str(row.get("policy_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "required_records": str(row.get("required_records") or ""),
        "reviewer_role": str(row.get("reviewer_role") or ""),
        "public_boundary": str(row.get("public_boundary") or ""),
        "non_claims": str(row.get("non_claims") or ""),
    } for row in matrix.get("rows") or []]


def notice_md(matrix: dict[str, Any], burndown: dict[str, Any]) -> str:
    lines = [
        "# Evidence custody/provenance no-go notice",
        "",
        f"Archive version: `{matrix['archive_version']}`  ",
        f"Release date: `{matrix['release_date']}`  ",
        "",
        "**No-go for live pilot use or public release of local evidence until custody/provenance records exist. Synthetic-only. This is not live election evidence, not authorization, not chain-of-custody certification, not an admissibility opinion, and not legal advice.**",
        "",
        "## Decision",
        "",
        f"`{matrix['decision']}`",
        "",
        "The archive can verify synthetic packet bytes, but live evidence handling also needs capture authorization, collector attribution, tool/version/time-source records, transfer digests, access logs, public/private separation, incident freeze records, source-review custody, chain-gap exceptions, and retention/disposition records.",
        "",
        "## Current custody state",
        "",
        f"- Policies: `{matrix['policy_count']}`.",
        f"- Blocking policies: `{matrix['blocking_policy_count']}`.",
        f"- Missing local custody records: `{matrix['missing_local_custody_record_count']}`.",
        f"- Release-gate families: `{burndown['gate_count']}`.",
        "",
        "## Promotion condition",
        "",
        "Regenerate this pack with jurisdiction-specific custody records, named owners, transfer/access logs, reviewer approvals, and documented exceptions. Live promotion remains no-go until every applicable row is closed or an accountable local exception is recorded.",
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
    (REPORTS / "evidence-custody-provenance-matrix.json").write_text(json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "evidence-custody-provenance-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "evidence_family", "reviewer_role", "status", "release_gate", "required_records", "next_action", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in matrix["rows"]:
            w.writerow({k: r.get(k, "") for k in fields})
    (REPORTS / "evidence-custody-burndown.json").write_text(json.dumps(burndown, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "evidence-custody-burndown.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["release_gate", "policy_count", "missing_local_custody_record_count", "evidence_families", "first_next_action", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(burndown["rows"])
    with (REPORTS / "custody-transfer-preview-index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "evidence_family", "required_records", "reviewer_role", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(preview)
    (REPORTS / "evidence-custody-no-go-notice.md").write_text(notice_md(matrix, burndown), encoding="utf-8")
    return {"custody_matrix": matrix, "custody_burndown": burndown, "custody_transfer_preview_index": preview}


def build_output() -> dict[str, Any]:
    matrix = build_matrix()
    return {"custody_matrix": matrix, "custody_burndown": build_burndown(matrix), "custody_transfer_preview_index": build_preview_index(matrix)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic custody/provenance no-go reports")
    ap.add_argument("--json", action="store_true", help="Print custody/provenance matrix JSON wrapper")
    args = ap.parse_args()
    out = write_outputs() if args.write else build_output()
    if args.json:
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        m = out["custody_matrix"]
        print(f"PASS: evidence custody/provenance pack ({m['archive_version']}, policies={m['policy_count']}, decision={m['decision']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
