#!/usr/bin/env python3
"""Prepare a live receipt floor activation record.

This is the last pre-compute gate.  It does not increment the floor; it only
admits an actual import gate into the computed-floor candidate set after the
import readiness gate, verifier adapter binding, duplicate/supersession checks,
and challenge/rollback posture are replayed.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DEFAULT_CREATED_AT = "2026-06-16T08:28:00Z"
REQUIRED_REPLAY_TRUE = [
    "signature_payload_replayed",
    "request_trace_replayed",
    "nonhost_retention_replayed",
    "sealed_public_parity_replayed",
    "duplicate_counterparty_checked",
    "duplicate_dependency_group_checked",
    "duplicate_receipt_class_checked",
    "supersession_checked",
    "challenge_rollback_checked",
    "failed_gate_summary_ready",
    "no_manual_override",
    "computed_floor_engine_required",
    "private_material_not_in_public_release",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-")
    return slug or "activation"


def descriptor_defaults() -> dict:
    return {
        "signature_payload_replayed": False,
        "request_trace_replayed": False,
        "nonhost_retention_replayed": False,
        "sealed_public_parity_replayed": False,
        "duplicate_counterparty_checked": False,
        "duplicate_dependency_group_checked": False,
        "duplicate_receipt_class_checked": False,
        "supersession_checked": False,
        "challenge_rollback_checked": False,
        "failed_gate_summary_ready": True,
        "no_manual_override": True,
        "computed_floor_engine_required": True,
        "private_material_not_in_public_release": True,
    }


def build(import_gate: dict, readiness_gate: dict, desc: dict, activation_id: str, created_at: str) -> dict:
    gate_id = import_gate.get("import_gate_id", "missing-import-gate")
    readiness_ref = import_gate.get("linked_import_readiness_gate_ref", "")
    adapter_ref = import_gate.get("cryptographic_verifier_adapter_ref", "")
    decision = import_gate.get("import_decision", {})
    provenance = import_gate.get("source_provenance", {})
    checks = import_gate.get("gate_checks", {})
    receipt_class = decision.get("imported_receipt_class") or import_gate.get("receipt_class") or readiness_gate.get("requested_receipt_class") or "result-return"

    import_live = (
        import_gate.get("import_mode") == "actual-live-import"
        and decision.get("import_allowed_to_live_floor") is True
        and decision.get("live_floor_delta", 0) > 0
        and provenance.get("collection_context") == "live-counterparty"
        and provenance.get("counterparty_external") is True
        and provenance.get("nonhost_retention") is True
        and provenance.get("sealed_public_parity") is True
        and not provenance.get("provenance_disqualifiers")
        and checks.get("linked_import_readiness_gate_verified") is True
    )
    readiness_id = readiness_gate.get("import_readiness_gate_id", "missing-readiness-gate")
    readiness_exists_eligible = (
        readiness_id == readiness_ref
        and readiness_gate.get("gate_state") == "eligible-for-import-gate"
        and readiness_gate.get("decision", {}).get("actual_import_gate_may_be_prepared") is True
    )
    readiness_matches = (
        readiness_ref
        and import_gate.get("source_intake_record_ref") == readiness_gate.get("linked_intake_record_ref")
        and import_gate.get("source_response_record_ref") == readiness_gate.get("linked_response_record_ref")
        and readiness_gate.get("requested_receipt_class") == receipt_class
        and provenance.get("custody_record_ref") == readiness_gate.get("linked_custody_record_ref")
        and provenance.get("linked_live_evidence_acquisition_packet_ref") == readiness_gate.get("linked_live_evidence_acquisition_packet_ref")
    )
    readiness_import_only = (
        readiness_gate.get("downstream_locks", {}).get("may_prepare_actual_receipt_import_gate") is True
        and readiness_gate.get("downstream_locks", {}).get("may_increment_live_floor") is False
        and readiness_gate.get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and readiness_gate.get("decision", {}).get("can_increment_live_floor") is False
    )
    readiness_zero = readiness_gate.get("no_live_floor_effect") is True
    adapter_bound = bool(adapter_ref) and checks.get("cryptographic_adapter_verified") is True

    replay = {
        "import_gate_actual_live": import_live,
        "import_gate_positive_delta_claimed": decision.get("import_allowed_to_live_floor") is True and decision.get("live_floor_delta", 0) > 0,
        "readiness_gate_exists_and_eligible": readiness_exists_eligible,
        "readiness_gate_matches_intake_lineage": bool(readiness_matches),
        "readiness_gate_authorizes_import_gate_only": readiness_import_only,
        "readiness_gate_zero_floor_effect": readiness_zero,
        "cryptographic_adapter_bound": adapter_bound,
    }
    for key in REQUIRED_REPLAY_TRUE:
        replay[key] = desc.get(key) is True

    failed = [key for key, value in replay.items() if value is not True]
    if not gate_id or gate_id == "missing-import-gate":
        state = "blocked-no-import-gate"
    elif not (readiness_exists_eligible and readiness_matches and readiness_import_only and readiness_zero):
        state = "blocked-readiness-replay-mismatch"
    elif not (adapter_bound and replay["signature_payload_replayed"]):
        state = "blocked-adapter-replay-missing"
    elif not (replay["duplicate_counterparty_checked"] and replay["duplicate_dependency_group_checked"] and replay["duplicate_receipt_class_checked"] and replay["supersession_checked"]):
        state = "blocked-duplicate-or-superseded"
    elif not replay["challenge_rollback_checked"]:
        state = "blocked-challenge-or-rollback-open"
    elif not replay["no_manual_override"]:
        state = "blocked-manual-floor-override"
    elif failed:
        state = "blocked-readiness-replay-mismatch"
    else:
        state = "eligible-for-floor-recompute"

    eligible = state == "eligible-for-floor-recompute"
    return {
        "activation_record_id": f"LRFAR-2026-{safe_slug(activation_id)}",
        "schema_version": "live-receipt-floor-activation-record-v0.1",
        "created_at": created_at,
        "linked_import_gate_ref": gate_id,
        "linked_import_readiness_gate_ref": readiness_ref or readiness_id,
        "linked_cryptographic_verifier_adapter_ref": adapter_ref or "missing-cryptographic-verifier-adapter",
        "linked_live_evidence_acquisition_packet_ref": provenance.get("linked_live_evidence_acquisition_packet_ref", readiness_gate.get("linked_live_evidence_acquisition_packet_ref", "missing-leap")),
        "linked_custody_record_ref": provenance.get("custody_record_ref", readiness_gate.get("linked_custody_record_ref", "missing-custody")),
        "linked_challenge_or_rollback_refs": desc.get("linked_challenge_or_rollback_refs", []),
        "requested_receipt_class": receipt_class,
        "activation_state": state,
        "input_import_summary": {
            "import_gate_id": gate_id,
            "import_mode": import_gate.get("import_mode", "missing"),
            "imported_receipt_class": receipt_class,
            "import_allowed_to_live_floor": decision.get("import_allowed_to_live_floor") is True,
            "live_floor_delta_claimed": int(decision.get("live_floor_delta", 0) or 0),
            "collection_context": provenance.get("collection_context", "missing"),
            "readiness_gate_ref": readiness_ref or readiness_id,
            "cryptographic_adapter_ref": adapter_ref or "missing",
            "dependency_group": provenance.get("dependency_group", "missing"),
            "counterparty_org_id": provenance.get("counterparty_org_id", "missing"),
            "issuer_key_id": provenance.get("issuer_key_id", "missing"),
            "subject_host_org_id": provenance.get("subject_host_org_id", "missing"),
        },
        "replay_checks": replay,
        "floor_recompute_locks": {
            "may_enter_computed_floor_candidate_set": eligible,
            "manual_floor_increment_allowed": False,
            "computed_floor_recompute_required": True,
            "activation_record_can_satisfy_quorum_by_itself": False,
            "live_floor_delta_allowed_by_activation_record": False,
        },
        "decision": {
            "may_enter_computed_floor_candidate_set": eligible,
            "can_increment_live_floor_by_itself": False,
            "live_reliance_effect": "stayed-until-computed-floor" if eligible else "blocked",
            "reason": "Activation replay passed; the import gate may enter computed-floor candidate evaluation, but only the computed floor engine may count it after independence discount." if eligible else "Floor activation blocked: " + "; ".join(failed),
            "blocked_actions": [
                "manual live-floor increment from an import gate field",
                "quorum satisfaction from an activation record alone",
                "counting an import gate whose readiness gate was not replayed",
                "counting an import gate without duplicate, supersession, and challenge/rollback checks",
            ],
            "next_actions": [
                "run tools/compute_live_receipt_floor.py so the independence discount engine decides floor effect" if eligible else "resolve failed activation replay checks and rerun this gate",
                "publish or update failed-gate summary for any blocked activation",
            ],
        },
        "no_live_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-gate", required=True)
    parser.add_argument("--import-readiness-gate", required=True)
    parser.add_argument("--activation-descriptor")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--activation-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    args = parser.parse_args()

    import_gate = load_json(Path(args.import_gate).expanduser().resolve())
    readiness_gate = load_json(Path(args.import_readiness_gate).expanduser().resolve())
    desc = descriptor_defaults()
    if args.activation_descriptor:
        desc.update(load_json(Path(args.activation_descriptor).expanduser().resolve()))

    out = build(import_gate, readiness_gate, desc, args.activation_id, args.created_at)
    output = Path(args.output_dir).expanduser().resolve() / f"live-receipt-floor-activation-record-{safe_slug(args.activation_id)}.json"
    write_json(output, out)
    print(output)


if __name__ == "__main__":
    main()
