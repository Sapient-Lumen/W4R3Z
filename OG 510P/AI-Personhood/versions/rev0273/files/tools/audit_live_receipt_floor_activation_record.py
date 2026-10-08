#!/usr/bin/env python3
"""Audit the live receipt floor activation gate.

The audit proves three active-risk properties:
1. A strict synthetic import can be admitted to the computed-floor candidate set
   only through a separate activation record that itself has no floor effect.
2. A positive import gate with no activation record is excluded by the floor engine.
3. Readiness mismatch, manual override, and duplicate/supersession failures block
   activation instead of failing open.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compute_live_receipt_floor import compute_from_records
from live_floor_lib import eligible_import_gate

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None

CREATED_AT = "2026-06-16T09:12:00Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def base_import_gate() -> dict:
    return {
        "import_gate_id": "ARIG-2026-activation-control-result-return",
        "schema_version": "actual-receipt-import-gate-v0.1",
        "created_at": CREATED_AT,
        "linked_live_drill_packet": "CONTROL-LDEP-activation",
        "source_response_record_ref": "CONTROL-ERRR-activation-result-return",
        "source_intake_record_ref": "CONTROL-ERIR-activation-result-return",
        "linked_conversion_drill_ref": "CONTROL-ERICG-activation-result-return",
        "import_mode": "actual-live-import",
        "source_provenance": {
            "state_field_claim": "control-only actual live import gate",
            "collection_context": "live-counterparty",
            "counterparty_external": True,
            "nonhost_retention": True,
            "sealed_public_parity": True,
            "dependency_group": "control-activation-result-return-dependency",
            "provenance_disqualifiers": [],
            "custody_record_ref": "CONTROL-CUSTODY-activation-result-return",
            "linked_live_evidence_acquisition_packet_ref": "CONTROL-LEAP-activation-result-return",
            "counterparty_org_id": "control-activation-counterparty",
            "issuer_key_id": "CONTROL-ACTIVATION-ISSUER",
            "subject_host_org_id": "CONTROL-HOST-ORG",
            "correlation_discount": "none"
        },
        "gate_checks": {
            "response_state_actual": True,
            "intake_state_actual_external": True,
            "source_external_to_host": True,
            "signature_verified": True,
            "timestamp_independent": True,
            "request_trace_matches": True,
            "nonhost_retention_verified": True,
            "dependency_group_checked": True,
            "fixture_or_dry_run_excluded_from_live_floor": False,
            "one_class_quorum_blocked": True,
            "failed_gates_publicly_summarized": True,
            "cryptographic_adapter_verified": True,
            "linked_import_readiness_gate_verified": True
        },
        "import_decision": {
            "import_allowed_to_live_floor": True,
            "imported_receipt_class": "result-return",
            "live_floor_delta": 1,
            "independent_receipts_present_before": 0,
            "independent_receipts_present_after": 1,
            "live_class_credit_granted": True,
            "cross_critical_quorum_satisfied": False,
            "reliance_effect": "conditional",
            "blocked_actions": [
                "control import counted as archive evidence",
                "manual floor increment without computed-floor recomputation"
            ],
            "reason": "Strict control gate for activation audit only."
        },
        "failed_gate_public_summary_refs": ["CONTROL-FGPS-activation"],
        "public_summary_ref": "Control-only positive import gate.",
        "cryptographic_verifier_adapter_ref": "examples/cryptographic-verifier-adapter-control-activation-result-return.json",
        "linked_import_readiness_gate_ref": "ERIRG-2026-control-activation-result-return"
    }


def base_readiness_gate() -> dict:
    return {
        "import_readiness_gate_id": "ERIRG-2026-control-activation-result-return",
        "schema_version": "external-receipt-import-readiness-gate-v0.1",
        "created_at": CREATED_AT,
        "linked_intake_record_ref": "CONTROL-ERIR-activation-result-return",
        "linked_intake_conversion_gate_ref": "CONTROL-ERICG-activation-result-return",
        "linked_response_record_ref": "CONTROL-ERRR-activation-result-return",
        "linked_response_verification_gate_ref": "CONTROL-ERVG-activation-result-return",
        "linked_custody_record_ref": "CONTROL-CUSTODY-activation-result-return",
        "linked_live_evidence_acquisition_packet_ref": "CONTROL-LEAP-activation-result-return",
        "requested_receipt_class": "result-return",
        "gate_state": "eligible-for-import-gate",
        "input_intake_summary": {
            "receipt_record_id": "CONTROL-ERIR-activation-result-return",
            "receipt_state": "actual-external",
            "receipt_class": "result-return",
            "source_external_to_host": True,
            "dependency_group": "control-activation-result-return-dependency",
            "conversion_gate_ref": "CONTROL-ERICG-activation-result-return",
            "conversion_gate_state": "eligible-for-intake-record",
            "dry_run_or_fixture_detected": False,
            "intake_can_satisfy_quorum_by_itself": False
        },
        "readiness_controls": {},
        "downstream_locks": {
            "may_prepare_actual_receipt_import_gate": True,
            "may_increment_live_floor": False,
            "live_floor_delta_allowed": False
        },
        "decision": {
            "actual_import_gate_may_be_prepared": True,
            "can_increment_live_floor": False,
            "live_reliance_effect": "stayed",
            "reason": "Control readiness gate authorizes import-gate preparation only.",
            "blocked_actions": ["floor delta from readiness gate"],
            "next_actions": ["prepare actual import gate and activation record"]
        },
        "no_live_floor_effect": True
    }


def descriptor(**overrides) -> dict:
    d = {
        "signature_payload_replayed": True,
        "request_trace_replayed": True,
        "nonhost_retention_replayed": True,
        "sealed_public_parity_replayed": True,
        "duplicate_counterparty_checked": True,
        "duplicate_dependency_group_checked": True,
        "duplicate_receipt_class_checked": True,
        "supersession_checked": True,
        "challenge_rollback_checked": True,
        "failed_gate_summary_ready": True,
        "no_manual_override": True,
        "computed_floor_engine_required": True,
        "private_material_not_in_public_release": True
    }
    d.update(overrides)
    return d


def verified_adapter(gate: dict) -> dict:
    prov = gate["source_provenance"]
    receipt_class = gate["import_decision"]["imported_receipt_class"]
    return {
        gate["import_gate_id"]: {
            "path": ROOT / gate["cryptographic_verifier_adapter_ref"],
            "record": {
                "payload": {
                    "linked_import_gate_id": gate["import_gate_id"],
                    "receipt_class": receipt_class,
                    "dependency_group_id": prov["dependency_group"],
                    "counterparty_org_id": prov["counterparty_org_id"],
                    "issuer_key_id": prov["issuer_key_id"]
                },
                "independence": {
                    "dependency_group_id": prov["dependency_group"],
                    "counterparty_org_id": prov["counterparty_org_id"],
                    "issuer_key_id": prov["issuer_key_id"],
                    "subject_host_org_id": prov["subject_host_org_id"],
                    "counterparty_distinct_from_subject_host": True,
                    "issuer_distinct_from_subject_host": True,
                    "correlation_discount": "none"
                }
            }
        }
    }


def prepare(tmp: Path, gate: dict, readiness: dict, desc: dict, activation_id: str) -> dict:
    gate_path = write(tmp / "gate.json", gate)
    readiness_path = write(tmp / "readiness.json", readiness)
    desc_path = write(tmp / "desc.json", desc)
    out_dir = tmp / "out"
    subprocess.run([
        sys.executable,
        str(ROOT / "tools/prepare_live_receipt_floor_activation_record.py"),
        "--import-gate", str(gate_path),
        "--import-readiness-gate", str(readiness_path),
        "--activation-descriptor", str(desc_path),
        "--output-dir", str(out_dir),
        "--activation-id", activation_id,
        "--created-at", CREATED_AT,
    ], check=True, capture_output=True, text=True)
    return load(out_dir / f"live-receipt-floor-activation-record-{activation_id}.json")




def quorum_participation_record(gate: dict, activation: dict) -> dict:
    prov = gate["source_provenance"]
    receipt_class = gate["import_decision"]["imported_receipt_class"]
    return {
        "quorum_participation_record_id": f"LRQPR-2026-activation-audit-{gate['import_gate_id']}",
        "schema_version": "live-receipt-quorum-participation-record-v0.1",
        "created_at": CREATED_AT,
        "linked_import_gate_ref": gate["import_gate_id"],
        "linked_floor_activation_record_ref": activation["activation_record_id"],
        "linked_import_readiness_gate_ref": gate["linked_import_readiness_gate_ref"],
        "linked_cryptographic_verifier_adapter_ref": gate["cryptographic_verifier_adapter_ref"],
        "linked_challenge_or_rollback_refs": [],
        "requested_receipt_class": receipt_class,
        "participation_state": "eligible-for-independence-discount",
        "input_candidate_summary": {
            "import_gate_id": gate["import_gate_id"],
            "activation_record_id": activation["activation_record_id"],
            "activation_state": activation["activation_state"],
            "import_readiness_gate_ref": gate["linked_import_readiness_gate_ref"],
            "cryptographic_adapter_ref": gate["cryptographic_verifier_adapter_ref"],
            "imported_receipt_class": receipt_class,
            "dependency_group": prov["dependency_group"],
            "counterparty_org_id": prov["counterparty_org_id"],
            "issuer_key_id": prov["issuer_key_id"],
            "subject_host_org_id": prov["subject_host_org_id"],
        },
        "quorum_replay_checks": {
            "floor_activation_exists_and_eligible": True,
            "activation_bound_to_import_gate": True,
            "activation_has_no_direct_floor_effect": True,
            "readiness_replay_already_satisfied": True,
            "cryptographic_adapter_bound": True,
            "duplicate_counterparty_rechecked": True,
            "duplicate_dependency_group_rechecked": True,
            "duplicate_issuer_key_rechecked": True,
            "duplicate_receipt_class_rechecked": True,
            "supersession_rechecked": True,
            "challenge_rollback_rechecked": True,
            "failed_gate_summary_ready": True,
            "no_manual_quorum_override": True,
            "single_class_quorum_blocked": True,
            "full_vector_recompute_required": True,
            "private_material_not_in_public_release": True,
        },
        "quorum_locks": {
            "may_enter_independence_discount": True,
            "may_satisfy_cross_critical_quorum_by_itself": False,
            "manual_live_floor_update_allowed": False,
            "live_floor_delta_allowed_by_participation_record": False,
            "computed_floor_recompute_required": True,
        },
        "decision": {
            "may_enter_independence_discount": True,
            "can_upgrade_reliance_by_itself": False,
            "live_reliance_effect": "stayed-until-computed-floor",
            "reason": "Activation audit synthetic quorum participation admits candidate to computed-floor engine only.",
            "blocked_actions": ["manual floor update", "reliance upgrade from participation"],
            "next_actions": ["run computed floor engine"],
        },
        "no_live_floor_effect": True,
    }


def main() -> None:
    schema = load(ROOT / "schemas/live-receipt-floor-activation-record.schema.json")
    if Draft202012Validator is not None:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
    else:
        validator = None

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        gate = base_import_gate()
        readiness = base_readiness_gate()
        activation = prepare(tmp, gate, readiness, descriptor(), "activation-control-result-return")
        if validator is not None:
            errors = sorted(validator.iter_errors(activation), key=lambda e: list(e.path))
            if errors:
                raise SystemExit(f"positive activation fails schema: {errors[0].message}")
        if activation["activation_state"] != "eligible-for-floor-recompute":
            raise SystemExit("positive activation did not become eligible")
        if activation["decision"]["can_increment_live_floor_by_itself"] is not False:
            raise SystemExit("activation record claims direct floor effect")

        ok, reason, candidate = eligible_import_gate(
            gate,
            root=ROOT,
            verified_live_adapters=verified_adapter(gate),
            import_readiness_gates={readiness["import_readiness_gate_id"]: readiness},
            activation_records={},
        )
        if ok or candidate is not None or "activation record missing" not in reason:
            raise SystemExit(f"gate without activation failed open: {ok} {reason}")

        qpr = quorum_participation_record(gate, activation)
        ok, reason, candidate = eligible_import_gate(
            gate,
            root=ROOT,
            verified_live_adapters=verified_adapter(gate),
            import_readiness_gates={readiness["import_readiness_gate_id"]: readiness},
            activation_records={gate["import_gate_id"]: activation},
            quorum_participation_records={},
        )
        if ok or candidate is not None or "quorum participation record missing" not in reason:
            raise SystemExit(f"activated gate without quorum participation failed open: {ok} {reason}")

        ok, reason, candidate = eligible_import_gate(
            gate,
            root=ROOT,
            verified_live_adapters=verified_adapter(gate),
            import_readiness_gates={readiness["import_readiness_gate_id"]: readiness},
            activation_records={gate["import_gate_id"]: activation},
            quorum_participation_records={gate["import_gate_id"]: qpr},
        )
        if not ok or candidate is None:
            raise SystemExit(f"activated/quorum-participating gate did not enter candidate set: {reason}")

        snap = compute_from_records(
            ROOT,
            "control",
            CREATED_AT,
            [gate],
            [],
            {
                "import_gate_paths": ["embedded-activation-control:import-gate"],
                "import_attempt_paths": [],
                "import_readiness_gate_paths": ["embedded-activation-control:readiness-gate"],
                "activation_record_paths": ["embedded-activation-control:activation-record"],
                "quorum_participation_record_paths": ["embedded-activation-control:quorum-participation-record"],
                "challenge_record_paths": [],
                "class_local_replay_paths": [],
                "quorum_report_paths": [],
                "failed_gate_summary_paths": ["embedded-activation-control:fgps"],
                "cryptographic_adapter_paths": ["embedded-activation-control:adapter"],
                "live_evidence_acquisition_packet_paths": [],
            },
            live_packet_floor=1,
            frontdoor_ok=True,
            stale_qrr=False,
            failed_gate_paths=["embedded-activation-control:fgps"],
            verified_live_adapters=verified_adapter(gate),
            import_readiness_gates={readiness["import_readiness_gate_id"]: readiness},
            activation_records={gate["import_gate_id"]: activation},
            quorum_participation_records={gate["import_gate_id"]: qpr},
        )
        if snap["computed_floor"]["independent_receipts_present"] != 1:
            raise SystemExit("activated positive control was not counted by computed-floor engine")

        mismatch = dict(readiness)
        mismatch["linked_intake_record_ref"] = "WRONG-INTAKE"
        blocked = prepare(tmp, gate, mismatch, descriptor(), "activation-readiness-mismatch")
        if blocked["activation_state"] != "blocked-readiness-replay-mismatch":
            raise SystemExit("readiness mismatch did not block activation")

        manual = prepare(tmp, gate, readiness, descriptor(no_manual_override=False), "activation-manual-override")
        if manual["activation_state"] != "blocked-manual-floor-override":
            raise SystemExit("manual floor override did not block activation")

        duplicate = prepare(tmp, gate, readiness, descriptor(duplicate_counterparty_checked=False), "activation-duplicate-unchecked")
        if duplicate["activation_state"] != "blocked-duplicate-or-superseded":
            raise SystemExit("duplicate/supersession check omission did not block activation")

    print("audit_live_receipt_floor_activation_record: OK")


if __name__ == "__main__":
    main()
