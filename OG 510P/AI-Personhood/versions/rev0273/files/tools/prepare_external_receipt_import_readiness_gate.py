#!/usr/bin/env python3
"""Prepare an external receipt import readiness gate.

This gate sits after an intake conversion gate and an intake record. It may
allow preparation of an actual receipt import gate only. It never grants live
floor credit; the later actual import gate, verifier adapter, class-local replay,
challenge/rollback, and computed-floor engine remain separate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T07:43:00Z"

REQUIRED_INTAKE_TRUE = [
    "counterparty_confirmed",
    "signature_or_equivalent_verified",
    "timestamp_independent",
    "hash_matches",
    "dependency_group_checked",
    "sealed_public_parity_checked",
    "host_generated_excluded_from_quorum",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    out: list[str] = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    return "".join(out).strip(".-_:") or "import-readiness-gate"


def descriptor_defaults() -> dict[str, Any]:
    return {
        "manual_import_readiness_review_completed": False,
        "public_failed_gate_summary_ready_for_blocks": True,
        "cryptographic_adapter_required_next": True,
        "private_material_not_in_public_release": True,
    }


def looks_fixture_or_dryrun(intake: dict[str, Any], gate: dict[str, Any]) -> bool:
    text_bits = [
        intake.get("receipt_record_id", ""),
        intake.get("linked_intake_conversion_gate_ref", ""),
        intake.get("public_summary_ref", ""),
        gate.get("intake_conversion_gate_id", ""),
    ]
    text = " ".join(str(x).lower() for x in text_bits)
    artifact_dry = any(
        a.get("generated_by") == "synthetic" or "fixture" in str(a.get("retained_by", "")).lower()
        for a in intake.get("evidence_artifacts", [])
    )
    decision = intake.get("reliance_decision", {})
    return (
        artifact_dry
        or "fixture" in text
        or "synthetic" in text
        or "dryrun" in text
        or "dry-run" in text
        or "controlled-fixture:" in text
        or decision.get("reason", "").lower().find("fixture") >= 0
    )


def has_nonhost_retention_artifact(intake: dict[str, Any]) -> bool:
    for artifact in intake.get("evidence_artifacts", []):
        retained_by = str(artifact.get("retained_by", "")).lower()
        generated_by = artifact.get("generated_by")
        if generated_by in {"external-counterparty", "neutral-infrastructure"} and "host" not in retained_by:
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake-record", required=True)
    parser.add_argument("--intake-conversion-gate", required=True)
    parser.add_argument("--readiness-descriptor")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--gate-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    args = parser.parse_args()

    intake = load_json(Path(args.intake_record).expanduser().resolve())
    conversion_gate = load_json(Path(args.intake_conversion_gate).expanduser().resolve())
    desc = descriptor_defaults()
    if args.readiness_descriptor:
        desc.update(load_json(Path(args.readiness_descriptor).expanduser().resolve()))

    conversion_id = conversion_gate.get("intake_conversion_gate_id", "")
    conversion_locks = conversion_gate.get("downstream_locks", {})
    conversion_ok = (
        conversion_gate.get("gate_state") == "eligible-for-intake-record"
        and conversion_locks.get("may_prepare_external_receipt_intake_record") is True
        and conversion_locks.get("may_run_import_gate") is False
        and conversion_locks.get("live_floor_delta_allowed") is False
        and conversion_gate.get("no_live_floor_effect") is True
    )

    verification = intake.get("verification_checks", {})
    decision = intake.get("reliance_decision", {})
    intake_actual = intake.get("receipt_state") == "actual-external"
    intake_gate_ref = intake.get("linked_intake_conversion_gate_ref", "")
    matches_conversion = bool(intake_gate_ref == conversion_id and conversion_id.startswith("ERICG-"))
    response_matches = intake.get("receipt_record_id") == conversion_gate.get("input_response_summary", {}).get("resulting_intake_record_ref")
    class_matches = intake.get("receipt_class") == conversion_gate.get("requested_receipt_class")
    custody_leap_match = (
        intake.get("linked_custody_record_ref") == conversion_gate.get("linked_custody_record_ref")
        and intake.get("linked_live_evidence_acquisition_packet_ref") == conversion_gate.get("linked_live_evidence_acquisition_packet_ref")
    )
    external_ok = intake.get("source_external_to_host") is True
    intake_true_ok = all(verification.get(k) is True for k in REQUIRED_INTAKE_TRUE)
    nonhost_retention_artifact = has_nonhost_retention_artifact(intake)
    not_fixture = not looks_fixture_or_dryrun(intake, conversion_gate)
    intake_non_quorum = decision.get("can_satisfy_quorum") is False and decision.get("reliance_effect") in {"conditional", "stayed", "blocked", "none"}
    manual_ok = desc.get("manual_import_readiness_review_completed") is True
    public_failed_ready = desc.get("public_failed_gate_summary_ready_for_blocks") is True
    crypto_next = desc.get("cryptographic_adapter_required_next") is True
    private_ok = desc.get("private_material_not_in_public_release") is True

    failed: list[str] = []
    if not conversion_ok:
        failed.append("intake conversion gate is not eligible or unlocks import/floor")
    if not intake_actual:
        failed.append("intake record is not actual-external")
    if not matches_conversion:
        failed.append("intake record does not bind supplied intake conversion gate")
    if not response_matches:
        failed.append("intake record does not match conversion gate resulting_intake_record_ref")
    if not class_matches:
        failed.append("receipt class does not match conversion gate")
    if not custody_leap_match:
        failed.append("custody/LEAP refs do not match conversion gate")
    for key in REQUIRED_INTAKE_TRUE:
        if verification.get(key) is not True:
            failed.append(key)
    if not external_ok:
        failed.append("intake source is not external to host")
    if not nonhost_retention_artifact:
        failed.append("no non-host retained external/neutral artifact present")
    if not not_fixture:
        failed.append("fixture or dry-run intake cannot become live import readiness")
    if not intake_non_quorum:
        failed.append("intake record attempts to satisfy quorum before import gate")
    if not manual_ok:
        failed.append("manual import readiness review missing")
    if not public_failed_ready:
        failed.append("public failed-gate summary readiness missing")
    if not crypto_next:
        failed.append("cryptographic adapter requirement not carried forward")
    if not private_ok:
        failed.append("private material boundary unsafe")

    if not intake_actual:
        state = "blocked-no-intake-record"
    elif not conversion_ok:
        state = "blocked-intake-conversion-not-eligible"
    elif not not_fixture:
        state = "blocked-fixture-or-dryrun"
    elif failed:
        state = "blocked-intake-record-unverified"
    else:
        state = "eligible-for-import-gate"

    eligible = state == "eligible-for-import-gate"
    out = {
        "import_readiness_gate_id": f"ERIRG-2026-{safe_slug(args.gate_id)}",
        "schema_version": "external-receipt-import-readiness-gate-v0.1",
        "created_at": args.created_at,
        "linked_intake_record_ref": intake.get("receipt_record_id", str(args.intake_record)),
        "linked_intake_conversion_gate_ref": conversion_id or intake_gate_ref,
        "linked_response_record_ref": conversion_gate.get("linked_response_record_ref", "missing"),
        "linked_response_verification_gate_ref": conversion_gate.get("linked_response_verification_gate_ref", "missing"),
        "linked_custody_record_ref": intake.get("linked_custody_record_ref", conversion_gate.get("linked_custody_record_ref", "missing")),
        "linked_live_evidence_acquisition_packet_ref": intake.get("linked_live_evidence_acquisition_packet_ref", conversion_gate.get("linked_live_evidence_acquisition_packet_ref", "missing")),
        "linked_request_packet": conversion_gate.get("linked_request_packet", intake.get("linked_simulation_bundle", "missing")),
        "requested_receipt_class": intake.get("receipt_class", conversion_gate.get("requested_receipt_class", "result-return")),
        "gate_state": state,
        "input_intake_summary": {
            "receipt_record_id": intake.get("receipt_record_id", "missing"),
            "receipt_state": intake.get("receipt_state", "missing"),
            "receipt_class": intake.get("receipt_class", "missing"),
            "source_external_to_host": external_ok,
            "dependency_group": intake.get("dependency_group", "unknown"),
            "conversion_gate_ref": intake_gate_ref,
            "conversion_gate_state": conversion_gate.get("gate_state", "missing"),
            "dry_run_or_fixture_detected": not not_fixture,
            "intake_can_satisfy_quorum_by_itself": decision.get("can_satisfy_quorum") is True,
        },
        "readiness_controls": {
            "intake_conversion_gate_eligible": conversion_ok,
            "intake_record_actual_external": intake_actual,
            "intake_record_matches_conversion_gate": matches_conversion,
            "response_record_matches_conversion_gate": response_matches,
            "response_verification_gate_matches_conversion_gate": bool(conversion_gate.get("linked_response_verification_gate_ref")),
            "receipt_class_matches_conversion_gate": class_matches,
            "custody_and_leap_refs_match": custody_leap_match,
            "counterparty_confirmed": verification.get("counterparty_confirmed") is True,
            "signature_or_equivalent_verified": verification.get("signature_or_equivalent_verified") is True,
            "timestamp_independent": verification.get("timestamp_independent") is True,
            "hash_matches": verification.get("hash_matches") is True,
            "dependency_group_checked": verification.get("dependency_group_checked") is True,
            "sealed_public_parity_checked": verification.get("sealed_public_parity_checked") is True,
            "host_generated_excluded_from_quorum": verification.get("host_generated_excluded_from_quorum") is True,
            "source_external_to_host": external_ok,
            "nonhost_retention_artifact_present": nonhost_retention_artifact,
            "public_failed_gate_summary_ready_for_blocks": public_failed_ready,
            "cryptographic_adapter_required_next": crypto_next,
            "not_dry_run_or_fixture": not_fixture,
            "intake_record_does_not_itself_satisfy_quorum": intake_non_quorum,
            "manual_import_readiness_review_completed": manual_ok,
            "private_material_not_in_public_release": private_ok,
        },
        "downstream_locks": {
            "may_prepare_actual_receipt_import_gate": eligible,
            "may_increment_live_floor": False,
            "live_floor_delta_allowed": False,
        },
        "decision": {
            "actual_import_gate_may_be_prepared": eligible,
            "can_increment_live_floor": False,
            "live_reliance_effect": "stayed" if eligible else "blocked",
            "reason": "All intake-to-import readiness controls passed; actual import-gate preparation only is allowed." if eligible else "Import readiness blocked: " + "; ".join(failed),
            "blocked_actions": [
                "live-floor increment from an import readiness gate",
                "ordinary reliance from an intake record alone",
                "actual-live-import without a later cryptographic verifier adapter",
                "cross-critical quorum from one class-local intake",
            ],
            "next_actions": [
                "prepare an actual receipt import gate only after verifier-adapter evidence is available" if eligible else "resolve failed readiness controls and rerun this gate",
                "run challenge/rollback and computed-floor recomputation after any future import gate",
            ],
        },
        "no_live_floor_effect": True,
    }

    output = Path(args.output_dir).expanduser().resolve() / f"external-receipt-import-readiness-gate-{safe_slug(args.gate_id)}.json"
    write_json(output, out)
    print(output)


if __name__ == "__main__":
    main()
