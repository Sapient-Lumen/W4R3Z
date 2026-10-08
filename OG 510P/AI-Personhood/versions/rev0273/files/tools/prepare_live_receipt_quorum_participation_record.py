#!/usr/bin/env python3
"""Prepare a live receipt quorum participation record.

This is the final pre-floor participation gate. It consumes an actual import
candidate plus its floor-activation record and decides whether the candidate may
enter the computed floor engine's independence-discount/quorum recomputation set.
It does not increment the floor, satisfy quorum, or upgrade reliance by itself.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DEFAULT_CREATED_AT = "2026-06-16T09:47:00Z"
REQUIRED_DESC_TRUE = [
    "duplicate_counterparty_rechecked",
    "duplicate_dependency_group_rechecked",
    "duplicate_issuer_key_rechecked",
    "duplicate_receipt_class_rechecked",
    "supersession_rechecked",
    "challenge_rollback_rechecked",
    "failed_gate_summary_ready",
    "no_manual_quorum_override",
    "single_class_quorum_blocked",
    "full_vector_recompute_required",
    "private_material_not_in_public_release",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-")
    return slug or "quorum-participation"


def descriptor_defaults() -> dict:
    return {
        "duplicate_counterparty_rechecked": False,
        "duplicate_dependency_group_rechecked": False,
        "duplicate_issuer_key_rechecked": False,
        "duplicate_receipt_class_rechecked": False,
        "supersession_rechecked": False,
        "challenge_rollback_rechecked": False,
        "failed_gate_summary_ready": True,
        "no_manual_quorum_override": True,
        "single_class_quorum_blocked": True,
        "full_vector_recompute_required": True,
        "private_material_not_in_public_release": True,
        "linked_challenge_or_rollback_refs": [],
    }


def build(import_gate: dict, activation: dict, desc: dict, participation_id: str, created_at: str) -> dict:
    gate_id = import_gate.get("import_gate_id", "missing-import-gate")
    decision = import_gate.get("import_decision", {})
    provenance = import_gate.get("source_provenance", {})
    receipt_class = decision.get("imported_receipt_class") or import_gate.get("receipt_class") or activation.get("requested_receipt_class") or "result-return"
    adapter_ref = import_gate.get("cryptographic_verifier_adapter_ref") or activation.get("linked_cryptographic_verifier_adapter_ref") or "missing-cryptographic-verifier-adapter"
    readiness_ref = import_gate.get("linked_import_readiness_gate_ref") or activation.get("linked_import_readiness_gate_ref") or "missing-import-readiness-gate"
    activation_id = activation.get("activation_record_id", "missing-floor-activation-record")

    activation_eligible = activation.get("activation_state") == "eligible-for-floor-recompute"
    activation_bound = activation.get("linked_import_gate_ref") == gate_id and gate_id != "missing-import-gate"
    activation_no_direct_floor = (
        activation.get("no_live_floor_effect") is True
        and activation.get("floor_recompute_locks", {}).get("activation_record_can_satisfy_quorum_by_itself") is False
        and activation.get("floor_recompute_locks", {}).get("live_floor_delta_allowed_by_activation_record") is False
        and activation.get("decision", {}).get("can_increment_live_floor_by_itself") is False
    )
    readiness_replay = (
        activation.get("linked_import_readiness_gate_ref") == readiness_ref
        and activation.get("replay_checks", {}).get("readiness_gate_exists_and_eligible") is True
        and activation.get("replay_checks", {}).get("readiness_gate_matches_intake_lineage") is True
        and activation.get("replay_checks", {}).get("readiness_gate_authorizes_import_gate_only") is True
        and activation.get("replay_checks", {}).get("readiness_gate_zero_floor_effect") is True
    )
    adapter_bound = bool(adapter_ref and adapter_ref != "missing-cryptographic-verifier-adapter") and activation.get("linked_cryptographic_verifier_adapter_ref") == adapter_ref

    checks = {
        "floor_activation_exists_and_eligible": activation_eligible,
        "activation_bound_to_import_gate": activation_bound,
        "activation_has_no_direct_floor_effect": activation_no_direct_floor,
        "readiness_replay_already_satisfied": readiness_replay,
        "cryptographic_adapter_bound": adapter_bound,
    }
    for key in REQUIRED_DESC_TRUE:
        checks[key] = desc.get(key) is True

    failed = [key for key, value in checks.items() if value is not True]
    if gate_id == "missing-import-gate":
        state = "blocked-no-import-gate"
    elif not activation_id or activation_id == "missing-floor-activation-record":
        state = "blocked-no-activation-record"
    elif not (activation_eligible and activation_bound and activation_no_direct_floor and readiness_replay and adapter_bound):
        state = "blocked-activation-not-eligible"
    elif not (checks["duplicate_counterparty_rechecked"] and checks["duplicate_dependency_group_rechecked"] and checks["duplicate_issuer_key_rechecked"] and checks["duplicate_receipt_class_rechecked"] and checks["supersession_rechecked"]):
        state = "blocked-duplicate-or-superseded"
    elif not checks["challenge_rollback_rechecked"]:
        state = "blocked-challenge-or-rollback-open"
    elif failed:
        state = "blocked-quorum-replay-missing"
    else:
        state = "eligible-for-independence-discount"

    eligible = state == "eligible-for-independence-discount"
    return {
        "quorum_participation_record_id": f"LRQPR-2026-{safe_slug(participation_id)}",
        "schema_version": "live-receipt-quorum-participation-record-v0.1",
        "created_at": created_at,
        "linked_import_gate_ref": gate_id,
        "linked_floor_activation_record_ref": activation_id,
        "linked_import_readiness_gate_ref": readiness_ref,
        "linked_cryptographic_verifier_adapter_ref": adapter_ref,
        "linked_challenge_or_rollback_refs": desc.get("linked_challenge_or_rollback_refs", []),
        "requested_receipt_class": receipt_class,
        "participation_state": state,
        "input_candidate_summary": {
            "import_gate_id": gate_id,
            "activation_record_id": activation_id,
            "activation_state": activation.get("activation_state", "missing"),
            "import_readiness_gate_ref": readiness_ref,
            "cryptographic_adapter_ref": adapter_ref,
            "imported_receipt_class": receipt_class,
            "dependency_group": provenance.get("dependency_group", "missing"),
            "counterparty_org_id": provenance.get("counterparty_org_id", "missing"),
            "issuer_key_id": provenance.get("issuer_key_id", "missing"),
            "subject_host_org_id": provenance.get("subject_host_org_id", "missing"),
        },
        "quorum_replay_checks": checks,
        "quorum_locks": {
            "may_enter_independence_discount": eligible,
            "may_satisfy_cross_critical_quorum_by_itself": False,
            "manual_live_floor_update_allowed": False,
            "live_floor_delta_allowed_by_participation_record": False,
            "computed_floor_recompute_required": True,
        },
        "decision": {
            "may_enter_independence_discount": eligible,
            "can_upgrade_reliance_by_itself": False,
            "live_reliance_effect": "stayed-until-computed-floor" if eligible else "blocked",
            "reason": "Quorum participation replay passed; the import gate may enter independence-discount and class-quorum recomputation, but this record carries no direct floor effect." if eligible else "Quorum participation blocked: " + "; ".join(failed),
            "blocked_actions": [
                "manual live-floor update from a participation record",
                "ordinary reliance from one class-local candidate",
                "counting a candidate whose activation, duplicate, supersession, or rollback posture was not replayed",
            ],
            "next_actions": [
                "run tools/compute_live_receipt_floor.py so the engine applies independence discount and required-class quorum" if eligible else "resolve failed quorum participation replay checks and rerun this gate",
                "publish or update failed-gate summary for any blocked participation record",
            ],
        },
        "no_live_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-gate", required=True)
    parser.add_argument("--floor-activation-record", required=True)
    parser.add_argument("--participation-descriptor", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--participation-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    args = parser.parse_args()

    desc = descriptor_defaults()
    desc.update(load_json(Path(args.participation_descriptor)))
    record = build(
        load_json(Path(args.import_gate)),
        load_json(Path(args.floor_activation_record)),
        desc,
        args.participation_id,
        args.created_at,
    )
    out = Path(args.output_dir) / f"live-receipt-quorum-participation-record-{safe_slug(args.participation_id)}.json"
    write_json(out, record)
    print(out)


if __name__ == "__main__":
    main()
