#!/usr/bin/env python3
"""Generate the mission-kernel live-closeout workqueue.

This is the substance bridge after the v889 closeout gap map: each live blocker
becomes a concrete intake work item with evidence classes, owner roles, closure
tests, and a fail-closed no-go status.  It creates operator-ready artifacts but
never fabricates live evidence and never upgrades the archive beyond synthetic.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from example_county_common import DEFAULT_SCENARIO, ROOT
from mission_kernel_closeout import build_closeout
from mission_kernel_common import WORKQUEUE_BOUNDARY, evidence_classes_for, element_label, standard_alignment_for
from release_context import archive_version, release_date

VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
OUTDIR = DEFAULT_SCENARIO.parent
WORKQUEUE_JSON = OUTDIR / "live-closeout-workqueue.json"
WORKQUEUE_CSV = OUTDIR / "live-closeout-workqueue.csv"
INTAKE_TEMPLATE = OUTDIR / "live-closeout-intake-template.json"
PUBLIC_MD = OUTDIR / "public-live-closeout-workqueue.md"
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-live-workqueue-rev{REV}.json"

BOUNDARY = WORKQUEUE_BOUNDARY

CSV_FIELDS = [
    "work_item_id",
    "blocker_id",
    "priority",
    "kernel_element_ids",
    "owner_role",
    "status",
    "next_artifact",
    "missing_evidence",
    "minimum_evidence_classes",
    "closure_test",
    "first_operator_action",
    "acceptance_gate",
    "non_claims",
]


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out or "item"


def build_workqueue() -> dict[str, Any]:
    closeout = build_closeout()
    blockers = closeout.get("highest_risk_blockers") or []
    elements_by_id = {str(e.get("element_id")): e for e in closeout.get("kernel_elements") or [] if isinstance(e, dict)}

    rows: list[dict[str, Any]] = []
    for idx, blocker in enumerate(blockers, start=1):
        if not isinstance(blocker, dict):
            continue
        bid = str(blocker.get("blocker_id") or f"MKB-{idx:03d}")
        element_ids = [str(x) for x in blocker.get("kernel_element_ids") or []]
        element_labels = [element_label(eid) for eid in element_ids]
        evidence_classes = evidence_classes_for(bid, str(blocker.get("missing_evidence") or "missing live evidence"))
        first_action = (
            "collect and hash the minimum evidence classes, record the local authority that supplied them, "
            "and keep private/source records outside public artifacts until redaction and release approval"
        )
        rows.append({
            "work_item_id": f"LWC-{idx:03d}",
            "blocker_id": bid,
            "priority": str(blocker.get("priority") or "high"),
            "kernel_element_ids": element_ids,
            "kernel_element_labels": element_labels,
            "owner_role": str(blocker.get("owner_role") or "release maintainer"),
            "status": "BLOCKED_PENDING_LIVE_EVIDENCE",
            "next_artifact": str(blocker.get("next_artifact") or "live evidence packet"),
            "missing_evidence": str(blocker.get("missing_evidence") or "live evidence not supplied"),
            "minimum_evidence_classes": evidence_classes,
            "standard_alignment": standard_alignment_for(bid),
            "closure_test": str(blocker.get("closure_test") or "local live evidence must close this work item"),
            "first_operator_action": first_action,
            "acceptance_gate": "closed only when the referenced live evidence object exists, has a sha256 digest, names its approving local authority, and passes redaction/public-boundary review",
            "no_go_reason": "synthetic archive lacks live jurisdiction evidence for this blocker",
            "non_claims": BOUNDARY,
            "source_blocker": blocker,
            "source_kernel_elements": [elements_by_id[eid] for eid in element_ids if eid in elements_by_id],
        })

    critical = [r for r in rows if r.get("priority") == "critical"]
    high = [r for r in rows if r.get("priority") == "high"]
    return {
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "scenario_id": closeout.get("scenario_id"),
        "closeout_id": closeout.get("closeout_id"),
        "workqueue_id": f"MKLQ-EXAMPLE-COUNTY-2026-MUNI-rev{REV}",
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "decision": "NO_GO_LIVE_CLOSEOUT_EVIDENCE_INCOMPLETE",
        "readiness_verdict": closeout.get("readiness_verdict"),
        "work_item_count": len(rows),
        "critical_work_item_count": len(critical),
        "high_work_item_count": len(high),
        "rows": rows,
        "boundary": BOUNDARY,
        "operator_rule": "Do not mark a row closed from narrative, self-attestation, generated synthetic artifacts, or missing private records; close only from digest-bound local evidence plus approval trail.",
        "refactor_audit": {
            "status": "PASS",
            "source": "tools/mission_kernel_closeout.py build_closeout()",
            "duplicated_blocker_list_after_refactor": 0,
            "notes": "The live workqueue is generated from the mission-kernel closeout blocker list so the public gap map and operator queue cannot drift independently.",
        },
    }


def build_intake_template(workqueue: dict[str, Any]) -> dict[str, Any]:
    return {
        "archive_version": VERSION,
        "template_id": f"LIVE-CLOSEOUT-INTAKE-TEMPLATE-rev{REV}",
        "scenario_id": workqueue.get("scenario_id"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "boundary": BOUNDARY,
        "operator_instruction": "Copy this template outside the governed synthetic archive for a real jurisdiction. Fill only with authorized local evidence, file digests, approvals, and public/private boundary decisions.",
        "required_common_fields": [
            "jurisdiction_name",
            "election_id",
            "election_date",
            "local_authority_contact_role",
            "authority_scope_record_sha256",
            "evidence_capture_datetime_utc",
            "redaction_review_status",
            "public_release_approval_status",
            "records_retention_rule_ref",
        ],
        "work_items": [
            {
                "work_item_id": row["work_item_id"],
                "blocker_id": row["blocker_id"],
                "owner_role": row["owner_role"],
                "next_artifact": row["next_artifact"],
                "minimum_evidence_classes": row["minimum_evidence_classes"],
                "evidence_objects_to_record": [
                    {
                        "evidence_class": cls,
                        "local_path_or_record_locator": "",
                        "sha256": "",
                        "approving_role": "",
                        "public_private_boundary": "",
                        "redaction_status": "",
                    }
                    for cls in row["minimum_evidence_classes"]
                ],
                "closure_test": row["closure_test"],
                "acceptance_gate": row["acceptance_gate"],
                "status": "UNFILLED_TEMPLATE_NOT_EVIDENCE",
            }
            for row in workqueue.get("rows") or []
        ],
    }


def build_report(workqueue: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    return {
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "scenario_id": workqueue.get("scenario_id"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "decision": workqueue.get("decision"),
        "workqueue_path": WORKQUEUE_JSON.relative_to(ROOT).as_posix(),
        "workqueue_csv_path": WORKQUEUE_CSV.relative_to(ROOT).as_posix(),
        "intake_template_path": INTAKE_TEMPLATE.relative_to(ROOT).as_posix(),
        "public_summary_path": PUBLIC_MD.relative_to(ROOT).as_posix(),
        "work_item_count": workqueue.get("work_item_count"),
        "critical_work_item_count": workqueue.get("critical_work_item_count"),
        "high_work_item_count": workqueue.get("high_work_item_count"),
        "unfilled_template_work_item_count": len(intake.get("work_items") or []),
        "owner_roles": sorted({str(r.get("owner_role") or "") for r in workqueue.get("rows") or []}),
        "next_artifacts": [r.get("next_artifact") for r in workqueue.get("rows") or []],
        "refactor_audit": workqueue.get("refactor_audit"),
        "boundary": BOUNDARY,
    }


def public_text(workqueue: dict[str, Any]) -> str:
    lines = [
        "# Live-closeout evidence workqueue",
        "",
        "**Synthetic workqueue only. This is not live election evidence and does not authorize a live pilot.**",
        "",
        f"Archive version: `{workqueue['archive_version']}`  ",
        f"Scenario: `{workqueue['scenario_id']}`  ",
        f"Decision: `{workqueue['decision']}`",
        "",
        "The queue converts each mission-kernel live blocker into a concrete intake item. Rows stay no-go until digest-bound local evidence, approving roles, redaction/public-boundary review, and retention/disposition records exist.",
        "",
        "## Blocking work items",
        "",
    ]
    for row in workqueue.get("rows") or []:
        lines.append(
            f"- `{row['work_item_id']}` / `{row['blocker_id']}` ({row['priority']}): "
            f"{row['next_artifact']} — owner role: {row['owner_role']}; "
            f"minimum evidence classes: {len(row['minimum_evidence_classes'])}."
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "This queue is a no-go live-closeout intake surface. It is not current voter instruction, not certification, not outcome proof, not authorization, and not legal advice. Do not close rows from narrative summaries or synthetic artifacts; close only from authorized local evidence and approval records.",
        "",
    ])
    return "\n".join(lines)


def csv_rows(workqueue: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in workqueue.get("rows") or []:
        out.append({
            "work_item_id": str(row.get("work_item_id") or ""),
            "blocker_id": str(row.get("blocker_id") or ""),
            "priority": str(row.get("priority") or ""),
            "kernel_element_ids": "; ".join(row.get("kernel_element_ids") or []),
            "owner_role": str(row.get("owner_role") or ""),
            "status": str(row.get("status") or ""),
            "next_artifact": str(row.get("next_artifact") or ""),
            "missing_evidence": str(row.get("missing_evidence") or ""),
            "minimum_evidence_classes": "; ".join(row.get("minimum_evidence_classes") or []),
            "closure_test": str(row.get("closure_test") or ""),
            "first_operator_action": str(row.get("first_operator_action") or ""),
            "acceptance_gate": str(row.get("acceptance_gate") or ""),
            "non_claims": str(row.get("non_claims") or ""),
        })
    return out


def build_all() -> dict[str, Any]:
    workqueue = build_workqueue()
    intake = build_intake_template(workqueue)
    report = build_report(workqueue, intake)
    return {"workqueue": workqueue, "intake_template": intake, "report": report, "public_markdown": public_text(workqueue)}


def write_all(payload: dict[str, Any]) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    workqueue = payload["workqueue"]
    intake = payload["intake_template"]
    report = payload["report"]
    WORKQUEUE_JSON.write_text(json.dumps(workqueue, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    INTAKE_TEMPLATE.write_text(json.dumps(intake, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    PUBLIC_MD.write_text(str(payload["public_markdown"]), encoding="utf-8")
    with WORKQUEUE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(csv_rows(workqueue))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write live-closeout workqueue artifacts")
    ap.add_argument("--json", action="store_true", help="print generated pack JSON")
    args = ap.parse_args()
    payload = build_all()
    if args.write:
        write_all(payload)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        wq = payload["workqueue"]
        print(f"mission-kernel-live-workqueue version={VERSION} decision={wq['decision']} items={wq['work_item_count']}")
    return 0 if payload["workqueue"].get("decision") == "NO_GO_LIVE_CLOSEOUT_EVIDENCE_INCOMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
