#!/usr/bin/env python3
"""Prepare an external receipt intake conversion gate.

This gate sits after a response verification gate and a response record. It may
allow intake-record preparation only. It never authorizes import or live-floor
credit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T07:10:00Z"

REQUIRED_RESPONSE_TRUE = [
    "counterparty_confirmed",
    "signature_or_equivalent_verified",
    "timestamp_independent",
    "request_trace_matches",
    "nonhost_retention_verified",
    "dependency_checked",
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
    return "".join(out).strip(".-_:") or "intake-conversion-gate"


def descriptor_defaults() -> dict[str, Any]:
    return {
        "manual_conversion_review_completed": False,
        "public_failed_gate_summary_ready_for_blocks": True,
        "private_material_not_in_public_release": True,
    }


def looks_fixture_or_dryrun(response: dict[str, Any], response_gate: dict[str, Any]) -> bool:
    text_bits = [
        response.get("response_record_id", ""),
        response.get("linked_response_verification_gate_ref", ""),
        response.get("public_summary_ref", ""),
        response_gate.get("response_gate_id", ""),
    ]
    text = " ".join(str(x).lower() for x in text_bits)
    artifact_dry = any(a.get("dry_run") is True or a.get("generated_by") == "synthetic" for a in response.get("response_artifacts", []))
    gate_dry = response_gate.get("input_response_descriptor", {}).get("dry_run") is True
    return artifact_dry or gate_dry or "fixture" in text or "synthetic" in text or response.get("quorum_effect", {}).get("dry_run_weight", 0) > 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-record", required=True)
    parser.add_argument("--response-gate", required=True)
    parser.add_argument("--conversion-descriptor")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--gate-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    args = parser.parse_args()

    response = load_json(Path(args.response_record).expanduser().resolve())
    response_gate = load_json(Path(args.response_gate).expanduser().resolve())
    desc = descriptor_defaults()
    if args.conversion_descriptor:
        desc.update(load_json(Path(args.conversion_descriptor).expanduser().resolve()))

    gate_id = response_gate.get("response_gate_id", "")
    gate_locks = response_gate.get("downstream_locks", {})
    response_locks_ok = (
        response_gate.get("gate_state") == "eligible-for-response-record"
        and gate_locks.get("may_prepare_external_receipt_response_record") is True
        and gate_locks.get("may_create_intake_record") is False
        and gate_locks.get("may_run_import_gate") is False
        and gate_locks.get("live_floor_delta_allowed") is False
        and response_gate.get("no_live_floor_effect") is True
    )
    verification = response.get("verification_result", {})
    response_actual = response.get("response_state") == "actual-response-received"
    response_gate_ref = response.get("linked_response_verification_gate_ref", "")
    matches_gate = bool(response_gate_ref == gate_id and gate_id.startswith("ERVG-"))
    class_matches = response.get("requested_receipt_class") == response_gate.get("requested_receipt_class")
    custody_leap_match = (
        response.get("linked_custody_record_ref") == response_gate.get("linked_custody_record_ref")
        and response.get("linked_live_evidence_acquisition_packet_ref") == response_gate.get("linked_live_evidence_acquisition_packet_ref")
    )
    stale_ok = verification.get("stale_or_superseded") is False
    response_true_ok = all(verification.get(k) is True for k in REQUIRED_RESPONSE_TRUE)
    external_ok = response.get("source_external_to_host") is True
    can_generate = verification.get("can_generate_actual_intake") is True
    not_fixture = not looks_fixture_or_dryrun(response, response_gate)
    manual_ok = desc.get("manual_conversion_review_completed") is True
    public_failed_ready = desc.get("public_failed_gate_summary_ready_for_blocks") is True
    private_ok = desc.get("private_material_not_in_public_release") is True

    failed = []
    if not response_locks_ok:
        failed.append("response gate is not eligible response-only authority")
    if not response_actual:
        failed.append("response record is not actual-response-received")
    if not matches_gate:
        failed.append("response record does not bind the supplied response gate")
    if not class_matches:
        failed.append("requested receipt class does not match response gate")
    if not custody_leap_match:
        failed.append("custody/LEAP refs do not match response gate")
    for key in REQUIRED_RESPONSE_TRUE:
        if verification.get(key) is not True:
            failed.append(key)
    if not stale_ok:
        failed.append("response stale or superseded")
    if not external_ok:
        failed.append("source is not external to host")
    if not can_generate:
        failed.append("response verification does not allow intake preparation")
    if not not_fixture:
        failed.append("fixture or dry-run response cannot become live intake")
    if not manual_ok:
        failed.append("manual conversion review missing")
    if not public_failed_ready:
        failed.append("public failed-gate summary readiness missing")
    if not private_ok:
        failed.append("private material boundary unsafe")

    if not response_actual:
        state = "blocked-no-response-record"
    elif not response_locks_ok:
        state = "blocked-response-gate-not-eligible"
    elif not not_fixture:
        state = "blocked-fixture-or-dryrun"
    elif failed:
        state = "blocked-response-record-unverified"
    else:
        state = "eligible-for-intake-record"

    eligible = state == "eligible-for-intake-record"
    out = {
        "intake_conversion_gate_id": f"ERICG-2026-{safe_slug(args.gate_id)}",
        "schema_version": "external-receipt-intake-conversion-gate-v0.1",
        "created_at": args.created_at,
        "linked_response_record_ref": response.get("response_record_id", str(args.response_record)),
        "linked_response_verification_gate_ref": gate_id or response_gate_ref,
        "linked_custody_record_ref": response.get("linked_custody_record_ref", response_gate.get("linked_custody_record_ref", "missing")),
        "linked_live_evidence_acquisition_packet_ref": response.get("linked_live_evidence_acquisition_packet_ref", response_gate.get("linked_live_evidence_acquisition_packet_ref", "missing")),
        "linked_request_packet": response.get("linked_request_packet", response_gate.get("linked_request_packet", "missing")),
        "requested_receipt_class": response.get("requested_receipt_class", response_gate.get("requested_receipt_class", "result-return")),
        "gate_state": state,
        "input_response_summary": {
            "response_record_id": response.get("response_record_id", "missing"),
            "response_state": response.get("response_state", "missing"),
            "resulting_intake_record_ref": response.get("resulting_intake_record_ref"),
            "source_external_to_host": external_ok,
            "dependency_group": response.get("dependency_group", "unknown"),
            "response_gate_ref": response_gate_ref,
            "response_gate_state": response_gate.get("gate_state", "missing"),
            "dry_run_or_fixture_detected": not not_fixture,
        },
        "conversion_controls": {
            "response_gate_eligible": response_locks_ok,
            "response_record_actual": response_actual,
            "response_record_matches_gate": matches_gate,
            "response_class_matches_gate": class_matches,
            "custody_and_leap_refs_match": custody_leap_match,
            "counterparty_confirmed": verification.get("counterparty_confirmed") is True,
            "signature_or_equivalent_verified": verification.get("signature_or_equivalent_verified") is True,
            "timestamp_independent": verification.get("timestamp_independent") is True,
            "request_trace_matches": verification.get("request_trace_matches") is True,
            "nonhost_retention_verified": verification.get("nonhost_retention_verified") is True,
            "dependency_checked": verification.get("dependency_checked") is True,
            "not_stale_or_superseded": stale_ok,
            "source_external_to_host": external_ok,
            "not_dry_run_or_fixture": not_fixture,
            "manual_conversion_review_completed": manual_ok,
            "public_failed_gate_summary_ready_for_blocks": public_failed_ready,
            "private_material_not_in_public_release": private_ok,
        },
        "downstream_locks": {
            "may_prepare_external_receipt_intake_record": eligible,
            "may_run_import_gate": False,
            "live_floor_delta_allowed": False,
        },
        "decision": {
            "intake_record_may_be_prepared": eligible,
            "can_run_import_gate": False,
            "live_reliance_effect": "stayed" if eligible else "blocked",
            "reason": "All response-to-intake conversion controls passed; intake-record preparation only is allowed." if eligible else "Intake conversion blocked: " + ", ".join(failed[:8]),
            "blocked_actions": [
                "import gate from intake conversion gate",
                "live-floor delta from intake conversion gate",
                "cross-critical quorum from one response/intake class",
                "intake from fixture, dry-run, stale, or unverified response",
            ],
            "next_actions": [
                "prepare an external receipt intake record only" if eligible else "cure missing response-to-intake conversion controls",
                "run actual receipt import gate separately after intake exists",
                "recompute live floor only after import gate passes",
            ],
        },
        "no_live_floor_effect": True,
    }
    out_path = Path(args.output_dir) / f"external-receipt-intake-conversion-gate-{safe_slug(args.gate_id)}.json"
    write_json(out_path, out)
    print(out_path)


if __name__ == "__main__":
    main()
