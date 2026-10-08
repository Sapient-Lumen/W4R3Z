#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path: Path | str):
    return json.loads((ROOT / path if isinstance(path, str) else path).read_text(encoding="utf-8"))


def write(path: Path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def base_conversion_gate():
    return {
        "intake_conversion_gate_id": "ERICG-2026-probe-eligible",
        "schema_version": "external-receipt-intake-conversion-gate-v0.1",
        "created_at": "2026-06-16T07:43:00Z",
        "linked_response_record_ref": "ERRR-2026-probe-eligible",
        "linked_response_verification_gate_ref": "ERVG-2026-probe-eligible",
        "linked_custody_record_ref": "CPACR-2026-probe-eligible",
        "linked_live_evidence_acquisition_packet_ref": "LEAP-2026-probe-eligible",
        "linked_request_packet": "ERRP-2026-probe-eligible",
        "requested_receipt_class": "result-return",
        "gate_state": "eligible-for-intake-record",
        "input_response_summary": {
            "response_record_id": "ERRR-2026-probe-eligible",
            "response_state": "actual-response-received",
            "resulting_intake_record_ref": "ERIR-2026-probe-eligible",
            "source_external_to_host": True,
            "dependency_group": "independent-probe-steward",
            "response_gate_ref": "ERVG-2026-probe-eligible",
            "response_gate_state": "eligible-for-response-record",
            "dry_run_or_fixture_detected": False,
        },
        "conversion_controls": {
            "response_gate_eligible": True,
            "response_record_actual": True,
            "response_record_matches_gate": True,
            "response_class_matches_gate": True,
            "custody_and_leap_refs_match": True,
            "counterparty_confirmed": True,
            "signature_or_equivalent_verified": True,
            "timestamp_independent": True,
            "request_trace_matches": True,
            "nonhost_retention_verified": True,
            "dependency_checked": True,
            "not_stale_or_superseded": True,
            "source_external_to_host": True,
            "not_dry_run_or_fixture": True,
            "manual_conversion_review_completed": True,
            "public_failed_gate_summary_ready_for_blocks": True,
            "private_material_not_in_public_release": True,
        },
        "downstream_locks": {
            "may_prepare_external_receipt_intake_record": True,
            "may_run_import_gate": False,
            "live_floor_delta_allowed": False,
        },
        "decision": {
            "intake_record_may_be_prepared": True,
            "can_run_import_gate": False,
            "live_reliance_effect": "stayed",
            "reason": "probe conversion gate allows intake preparation only",
            "blocked_actions": ["import from conversion gate"],
            "next_actions": ["prepare intake record then import readiness gate"],
        },
        "no_live_floor_effect": True,
    }


def base_intake_record():
    return {
        "receipt_record_id": "ERIR-2026-probe-eligible",
        "schema_version": "external-receipt-intake-record-v0.1",
        "created_at": "2026-06-16T07:43:00Z",
        "linked_simulation_bundle": "ERSB-2026-probe-not-simulation-source",
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "receipt_state": "actual-external",
        "receipt_class": "result-return",
        "source_role": "probe external result-return steward",
        "source_identity_ref": "counterparty:probe-result-return-steward",
        "source_external_to_host": True,
        "dependency_group": "independent-probe-steward",
        "dependency_disclosures": [
            {"dependency_type": "none", "disclosed": True, "recusal_required": False}
        ],
        "evidence_artifacts": [
            {
                "artifact_id": "ERIR-PROBE-A1",
                "artifact_type": "signature",
                "hash_or_locator": "sha256:probe-live-shaped-signature",
                "generated_by": "external-counterparty",
                "retained_by": "external-neutral-vault",
                "sealed": False,
            },
            {
                "artifact_id": "ERIR-PROBE-A2",
                "artifact_type": "timestamp",
                "hash_or_locator": "clock:neutral-notary-2026-06-16T07:43:00Z",
                "generated_by": "neutral-infrastructure",
                "retained_by": "external-neutral-vault",
                "sealed": False,
            },
            {
                "artifact_id": "ERIR-PROBE-A3",
                "artifact_type": "sealed-index",
                "hash_or_locator": "sealed-index:probe-live-shaped",
                "generated_by": "external-counterparty",
                "retained_by": "external-sealed-custodian",
                "sealed": True,
            },
        ],
        "verification_checks": {
            "counterparty_confirmed": True,
            "signature_or_equivalent_verified": True,
            "timestamp_independent": True,
            "hash_matches": True,
            "dependency_group_checked": True,
            "sealed_public_parity_checked": True,
            "host_generated_excluded_from_quorum": True,
        },
        "defect_flags": {
            "host_generated": False,
            "simulated": False,
            "stale": False,
            "unsigned": False,
            "correlated_dependency": False,
            "missing_public_failed_gate": False,
            "sealed_descriptor_missing": False,
            "contact_unreachable": False,
        },
        "reliance_decision": {
            "can_satisfy_quorum": False,
            "reliance_effect": "stayed",
            "reason": "Intake record is pre-import evidence only; import gate and computed floor remain separate.",
            "public_shell_disclosure_required": True,
        },
        "public_summary_ref": "Probe intake is eligible for import-readiness review only and has no live-floor effect.",
        "linked_live_evidence_acquisition_packet_ref": "LEAP-2026-probe-eligible",
        "linked_custody_record_ref": "CPACR-2026-probe-eligible",
        "linked_intake_conversion_gate_ref": "ERICG-2026-probe-eligible",
    }


if Draft202012Validator is not None:
    schema = load("schemas/external-receipt-import-readiness-gate.schema.json")
    Draft202012Validator.check_schema(schema)
    example = load("examples/external-receipt-import-readiness-gate-rev0219-blocked-no-intake-record.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"readiness gate example fails schema: {errors[0].message}")

# Schema/tool coupling: actual-live-import gates must carry readiness evidence.
actual_import_schema = load("schemas/actual-receipt-import-gate.schema.json")
actual_live_condition_found = False
for block in actual_import_schema.get("allOf", []):
    if block.get("if", {}).get("properties", {}).get("import_mode", {}).get("const") == "actual-live-import":
        required = set(block.get("then", {}).get("required", []))
        gate_required = set(block.get("then", {}).get("properties", {}).get("gate_checks", {}).get("required", []))
        if "linked_import_readiness_gate_ref" in required and "linked_import_readiness_gate_verified" in gate_required:
            actual_live_condition_found = True
if not actual_live_condition_found:
    raise SystemExit("actual-live-import schema does not require import readiness gate binding")

with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    intake_path = d / "intake.json"
    conv_path = d / "conversion.json"
    desc_path = d / "descriptor.json"
    write(intake_path, base_intake_record())
    write(conv_path, base_conversion_gate())
    write(desc_path, {
        "manual_import_readiness_review_completed": True,
        "public_failed_gate_summary_ready_for_blocks": True,
        "cryptographic_adapter_required_next": True,
        "private_material_not_in_public_release": True,
    })

    subprocess.run([sys.executable, str(ROOT / "tools/prepare_external_receipt_import_readiness_gate.py"), "--intake-record", str(intake_path), "--intake-conversion-gate", str(conv_path), "--readiness-descriptor", str(desc_path), "--output-dir", str(d), "--gate-id", "probe-eligible"], check=True)
    out = json.loads((d / "external-receipt-import-readiness-gate-probe-eligible.json").read_text(encoding="utf-8"))
    if out.get("gate_state") != "eligible-for-import-gate":
        raise SystemExit("eligible probe did not pass import readiness gate: " + out.get("gate_state", "missing"))
    if out.get("downstream_locks", {}).get("may_prepare_actual_receipt_import_gate") is not True:
        raise SystemExit("eligible readiness gate did not allow import-gate preparation")
    if out.get("downstream_locks", {}).get("may_increment_live_floor") is not False or out.get("downstream_locks", {}).get("live_floor_delta_allowed") is not False:
        raise SystemExit("import readiness gate unlocked live floor")

    bad_conv = base_conversion_gate()
    bad_conv["gate_state"] = "blocked-response-record-unverified"
    bad_conv["downstream_locks"]["may_prepare_external_receipt_intake_record"] = False
    write(conv_path, bad_conv)
    subprocess.run([sys.executable, str(ROOT / "tools/prepare_external_receipt_import_readiness_gate.py"), "--intake-record", str(intake_path), "--intake-conversion-gate", str(conv_path), "--readiness-descriptor", str(desc_path), "--output-dir", str(d), "--gate-id", "probe-blocked-conversion"], check=True)
    blocked = json.loads((d / "external-receipt-import-readiness-gate-probe-blocked-conversion.json").read_text(encoding="utf-8"))
    if blocked.get("gate_state") != "blocked-intake-conversion-not-eligible":
        raise SystemExit("blocked conversion probe did not fail closed")

    fixture_conv = base_conversion_gate()
    fixture_conv["intake_conversion_gate_id"] = "ERICG-2026-fixture-probe"
    fixture_conv["input_response_summary"]["dry_run_or_fixture_detected"] = True
    fixture_intake = base_intake_record()
    fixture_intake["receipt_record_id"] = "ERIR-2026-fixture-probe"
    fixture_intake["linked_intake_conversion_gate_ref"] = "ERICG-2026-fixture-probe"
    fixture_intake["reliance_decision"]["reason"] = "controlled fixture shape only"
    fixture_intake["evidence_artifacts"][0]["retained_by"] = "nonhost-fixture-vault"
    fixture_conv["input_response_summary"]["resulting_intake_record_ref"] = "ERIR-2026-fixture-probe"
    write(conv_path, fixture_conv)
    write(intake_path, fixture_intake)
    subprocess.run([sys.executable, str(ROOT / "tools/prepare_external_receipt_import_readiness_gate.py"), "--intake-record", str(intake_path), "--intake-conversion-gate", str(conv_path), "--readiness-descriptor", str(desc_path), "--output-dir", str(d), "--gate-id", "probe-fixture"], check=True)
    fx = json.loads((d / "external-receipt-import-readiness-gate-probe-fixture.json").read_text(encoding="utf-8"))
    if fx.get("gate_state") != "blocked-fixture-or-dryrun":
        raise SystemExit("fixture/dry-run intake did not block")

# Archived readiness gates must never unlock live floor.
for path in (ROOT / "examples").glob("external-receipt-import-readiness-gate*.json"):
    data = load(path)
    if data.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{path.relative_to(ROOT)} has live floor effect")
    locks = data.get("downstream_locks", {})
    if locks.get("may_increment_live_floor") is not False or locks.get("live_floor_delta_allowed") is not False:
        raise SystemExit(f"{path.relative_to(ROOT)} unlocks live floor")

# Floor engine must remain generated and zero after adding readiness gates.
subprocess.run([sys.executable, str(ROOT / "tools/compute_live_receipt_floor.py"), "--check"], check=True)

print("audit_external_receipt_import_readiness_gate: OK")
