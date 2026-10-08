#!/usr/bin/env python3
"""Audit the live receipt quorum participation gate.

The audit proves that floor activation is still not enough: an import candidate
must pass a separate quorum participation replay before it can enter the floor
engine's independence discount. The participation record remains zero-effect and
cannot create quorum or reliance by itself.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_live_receipt_floor_activation_record import base_import_gate, base_readiness_gate, descriptor as activation_descriptor, prepare as prepare_activation, verified_adapter
from compute_live_receipt_floor import compute_from_records
from live_floor_lib import eligible_import_gate

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None

CREATED_AT = "2026-06-16T09:47:00Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def participation_descriptor(**overrides) -> dict:
    data = {
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
        "linked_challenge_or_rollback_refs": [],
    }
    data.update(overrides)
    return data


def prepare_participation(tmp: Path, gate: dict, activation: dict, desc: dict, participation_id: str) -> dict:
    gate_path = write(tmp / f"gate-{participation_id}.json", gate)
    activation_path = write(tmp / f"activation-{participation_id}.json", activation)
    desc_path = write(tmp / f"participation-{participation_id}.json", desc)
    out_dir = tmp / "out-qpr"
    subprocess.run([
        sys.executable,
        str(ROOT / "tools/prepare_live_receipt_quorum_participation_record.py"),
        "--import-gate", str(gate_path),
        "--floor-activation-record", str(activation_path),
        "--participation-descriptor", str(desc_path),
        "--output-dir", str(out_dir),
        "--participation-id", participation_id,
        "--created-at", CREATED_AT,
    ], check=True, capture_output=True, text=True)
    return load(out_dir / f"live-receipt-quorum-participation-record-{participation_id}.json")


def main() -> None:
    schema = load(ROOT / "schemas/live-receipt-quorum-participation-record.schema.json")
    if Draft202012Validator is not None:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        example = load(ROOT / "examples/live-receipt-quorum-participation-record-rev0221-blocked-no-activation.json")
        errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"blocked example fails schema: {errors[0].message}")
    else:
        validator = None

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        gate = base_import_gate()
        readiness = base_readiness_gate()
        activation = prepare_activation(tmp, gate, readiness, activation_descriptor(), "quorum-activation-control-result-return")
        if activation.get("activation_state") != "eligible-for-floor-recompute":
            raise SystemExit("precondition failed: activation control is not eligible")

        qpr = prepare_participation(tmp, gate, activation, participation_descriptor(), "quorum-control-result-return")
        if validator is not None:
            errors = sorted(validator.iter_errors(qpr), key=lambda e: list(e.path))
            if errors:
                raise SystemExit(f"positive participation fails schema: {errors[0].message}")
        if qpr.get("participation_state") != "eligible-for-independence-discount":
            raise SystemExit("positive participation did not become eligible")
        if qpr.get("decision", {}).get("can_upgrade_reliance_by_itself") is not False:
            raise SystemExit("participation claims reliance upgrade by itself")

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
            raise SystemExit(f"quorum participation did not admit candidate: {reason}")

        snap = compute_from_records(
            ROOT,
            "control",
            CREATED_AT,
            [gate],
            [],
            {
                "import_gate_paths": ["embedded-quorum-control:import-gate"],
                "import_attempt_paths": [],
                "import_readiness_gate_paths": ["embedded-quorum-control:readiness-gate"],
                "activation_record_paths": ["embedded-quorum-control:activation-record"],
                "quorum_participation_record_paths": ["embedded-quorum-control:quorum-participation-record"],
                "challenge_record_paths": [],
                "class_local_replay_paths": [],
                "quorum_report_paths": [],
                "failed_gate_summary_paths": ["embedded-quorum-control:fgps"],
                "cryptographic_adapter_paths": ["embedded-quorum-control:adapter"],
                "live_evidence_acquisition_packet_paths": [],
            },
            live_packet_floor=1,
            frontdoor_ok=True,
            stale_qrr=False,
            failed_gate_paths=["embedded-quorum-control:fgps"],
            verified_live_adapters=verified_adapter(gate),
            import_readiness_gates={readiness["import_readiness_gate_id"]: readiness},
            activation_records={gate["import_gate_id"]: activation},
            quorum_participation_records={gate["import_gate_id"]: qpr},
        )
        floor = snap["computed_floor"]
        if floor["independent_receipts_present"] != 1 or floor["cross_critical_quorum_satisfied"] is not False:
            raise SystemExit("quorum participation should allow one class-local count but no cross-critical quorum")

        duplicate = prepare_participation(tmp, gate, activation, participation_descriptor(duplicate_counterparty_rechecked=False), "quorum-duplicate-unchecked")
        if duplicate["participation_state"] != "blocked-duplicate-or-superseded":
            raise SystemExit("duplicate recheck omission did not block quorum participation")

        rollback = prepare_participation(tmp, gate, activation, participation_descriptor(challenge_rollback_rechecked=False), "quorum-rollback-open")
        if rollback["participation_state"] != "blocked-challenge-or-rollback-open":
            raise SystemExit("challenge/rollback omission did not block quorum participation")

        single_class = prepare_participation(tmp, gate, activation, participation_descriptor(single_class_quorum_blocked=False), "quorum-single-class-unblocked")
        if single_class["participation_state"] != "blocked-quorum-replay-missing":
            raise SystemExit("single-class quorum bypass did not block participation")

    print("audit_live_receipt_quorum_participation_record: OK")


if __name__ == "__main__":
    main()
