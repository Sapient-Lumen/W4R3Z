#!/usr/bin/env python3
"""Prepare an external receipt response verification gate.

This gate sits after response-only custody and before an external receipt response
record. It verifies that an actual counterparty reply is present and scoped, but
it still cannot create intake, import, or live-floor effects. Response record
preparation is the maximum unlock.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T06:39:00Z"

REQUIRED_TRUE = [
    "counterparty_reply_received",
    "counterparty_confirmed",
    "signature_or_equivalent_verified",
    "timestamp_independent",
    "request_trace_matches",
    "nonhost_retention_verified",
    "dependency_checked",
    "receipt_class_matches",
    "scoped_acceptance_present",
    "not_stale_or_superseded",
    "manual_review_completed",
    "private_material_not_in_public_release",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    return "".join(out).strip(".-_:") or "response-gate"


def descriptor_defaults() -> dict[str, Any]:
    return {
        "counterparty_reply_received": False,
        "counterparty_identity_ref": "counterparty:pending",
        "response_channel": "unknown",
        "received_at": None,
        "dry_run": False,
        "artifacts": [
            {
                "artifact_id": "ERVG-A-001",
                "artifact_type": "sealed-descriptor",
                "locator_or_hash": "pending:counterparty-response",
                "generated_by": "host",
                "retained_by": "none-yet",
                "sealed": False,
                "dry_run": False,
            }
        ],
        "counterparty_confirmed": False,
        "signature_or_equivalent_verified": False,
        "timestamp_independent": False,
        "request_trace_matches": False,
        "nonhost_retention_verified": False,
        "dependency_checked": False,
        "receipt_class_matches": False,
        "scoped_acceptance_present": False,
        "not_stale_or_superseded": False,
        "manual_review_completed": False,
        "private_material_not_in_public_release": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--custody-record", required=True)
    parser.add_argument("--response-descriptor", help="JSON descriptor for the actual response; omitted means no response yet.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--gate-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--linked-request-packet", default="ERRP-2026-cross-critical-rep-rerb-result-return")
    parser.add_argument("--linked-live-evidence-acquisition-packet", default=f"LEAP-2026-{REV}-first-live-evidence-acquisition-pending")
    args = parser.parse_args()

    custody_path = Path(args.custody_record).expanduser().resolve()
    custody = load_json(custody_path)
    desc = descriptor_defaults()
    if args.response_descriptor:
        supplied = load_json(Path(args.response_descriptor).expanduser().resolve())
        desc.update(supplied)

    readiness = custody.get("import_readiness", {})
    authority = custody.get("counterparty_authority", {})
    custody_ok = (
        custody.get("artifact_state") == "live-candidate-artifact"
        and readiness.get("may_create_response_record") is True
        and readiness.get("may_create_intake_record") is False
        and readiness.get("may_run_import_gate") is False
        and readiness.get("live_import_floor_delta") == 0
        and bool(custody.get("linked_custody_gate_ref"))
        and authority.get("authority_verified") is True
        and custody.get("decision", {}).get("live_reliance_effect") == "stayed"
    )

    failed = []
    if not custody_ok:
        failed.append("custody record is not live-candidate response-only authority")
    for key in REQUIRED_TRUE:
        if desc.get(key) is not True:
            failed.append(key)

    if desc.get("counterparty_reply_received") is not True:
        gate_state = "blocked-no-response"
    elif desc.get("scoped_acceptance_present") is not True or desc.get("receipt_class_matches") is not True:
        gate_state = "blocked-unscoped-acceptance"
    elif failed:
        gate_state = "blocked-unverified"
    else:
        gate_state = "eligible-for-response-record"

    eligible = gate_state == "eligible-for-response-record"
    receipt_class = custody.get("receipt_class", "result-return")
    gate = {
        "response_gate_id": f"ERVG-2026-{safe_slug(args.gate_id)}",
        "schema_version": "external-receipt-response-verification-gate-v0.1",
        "created_at": args.created_at,
        "linked_custody_record_ref": custody.get("custody_record_id", str(custody_path)),
        "linked_live_evidence_acquisition_packet_ref": args.linked_live_evidence_acquisition_packet,
        "linked_request_packet": args.linked_request_packet,
        "requested_receipt_class": receipt_class,
        "gate_state": gate_state,
        "input_response_descriptor": {
            "counterparty_reply_received": desc.get("counterparty_reply_received") is True,
            "counterparty_identity_ref": desc.get("counterparty_identity_ref", authority.get("identity_ref", "counterparty:unknown")),
            "response_channel": desc.get("response_channel", "unknown"),
            "received_at": desc.get("received_at"),
            "dry_run": desc.get("dry_run") is True,
            "artifacts": desc.get("artifacts", descriptor_defaults()["artifacts"]),
        },
        "verification_controls": {
            "custody_record_response_only_authority": custody_ok,
            "counterparty_confirmed": desc.get("counterparty_confirmed") is True,
            "signature_or_equivalent_verified": desc.get("signature_or_equivalent_verified") is True,
            "timestamp_independent": desc.get("timestamp_independent") is True,
            "request_trace_matches": desc.get("request_trace_matches") is True,
            "nonhost_retention_verified": desc.get("nonhost_retention_verified") is True,
            "dependency_checked": desc.get("dependency_checked") is True,
            "receipt_class_matches": desc.get("receipt_class_matches") is True,
            "scoped_acceptance_present": desc.get("scoped_acceptance_present") is True,
            "not_stale_or_superseded": desc.get("not_stale_or_superseded") is True,
            "manual_review_completed": desc.get("manual_review_completed") is True,
            "private_material_not_in_public_release": desc.get("private_material_not_in_public_release") is True,
        },
        "downstream_locks": {
            "may_prepare_external_receipt_response_record": eligible,
            "may_create_intake_record": False,
            "may_run_import_gate": False,
            "live_floor_delta_allowed": False,
        },
        "decision": {
            "response_record_may_be_prepared": eligible,
            "can_generate_actual_intake": False,
            "live_reliance_effect": "stayed" if eligible else "blocked",
            "reason": "All response verification controls passed; only external receipt response record preparation is allowed." if eligible else "Response gate blocked: " + ", ".join(failed[:8]),
            "blocked_actions": [
                "intake record from response gate",
                "actual receipt import gate from response gate",
                "live-floor delta from response gate",
                "treating scoped acceptance as subject-status proof",
            ],
            "next_actions": [
                "prepare external receipt response record only" if eligible else "cure missing response verification controls",
                "run response-to-intake conversion gate separately after response record exists",
                "keep computed live floor at zero until import and recomputation pass",
            ],
        },
        "no_live_floor_effect": True,
    }
    out = Path(args.output_dir) / f"external-receipt-response-verification-gate-{safe_slug(args.gate_id)}.json"
    write_json(out, gate)
    print(out)


if __name__ == "__main__":
    main()
