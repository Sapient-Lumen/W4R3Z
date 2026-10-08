#!/usr/bin/env python3
from __future__ import annotations

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


def load(rel_or_path):
    p = Path(rel_or_path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def validate(schema_rel, data_rel):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_rel)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")


def write(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def base_response_gate():
    return {
        "response_gate_id": "ERVG-2026-probe-response-gate",
        "schema_version": "external-receipt-response-verification-gate-v0.1",
        "created_at": "2026-06-16T07:10:00Z",
        "linked_custody_record_ref": "CACR-2026-probe-live-custody",
        "linked_live_evidence_acquisition_packet_ref": f"LEAP-2026-{REV}-probe-live-evidence-acquisition",
        "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
        "requested_receipt_class": "result-return",
        "gate_state": "eligible-for-response-record",
        "input_response_descriptor": {
            "counterparty_reply_received": True,
            "counterparty_identity_ref": "org:probe-counterparty",
            "response_channel": "non-host-email",
            "received_at": "2026-06-16T07:10:00Z",
            "dry_run": False,
            "artifacts": [{"artifact_id":"ERVG-PROBE-A1","artifact_type":"signed-response","locator_or_hash":"sha256:" + "1"*64,"generated_by":"external-counterparty","retained_by":"non-host-vault","sealed":True,"dry_run":False}],
        },
        "verification_controls": {
            "custody_record_response_only_authority": True,
            "counterparty_confirmed": True,
            "signature_or_equivalent_verified": True,
            "timestamp_independent": True,
            "request_trace_matches": True,
            "nonhost_retention_verified": True,
            "dependency_checked": True,
            "receipt_class_matches": True,
            "scoped_acceptance_present": True,
            "not_stale_or_superseded": True,
            "manual_review_completed": True,
            "private_material_not_in_public_release": True,
        },
        "downstream_locks": {
            "may_prepare_external_receipt_response_record": True,
            "may_create_intake_record": False,
            "may_run_import_gate": False,
            "live_floor_delta_allowed": False,
        },
        "decision": {
            "response_record_may_be_prepared": True,
            "can_generate_actual_intake": False,
            "live_reliance_effect": "stayed",
            "reason": "probe",
            "blocked_actions": ["intake from response gate"],
            "next_actions": ["prepare response record only"],
        },
        "no_live_floor_effect": True,
    }


def base_response_record():
    return {
        "response_record_id": "ERRR-2026-probe-live-response",
        "schema_version": "external-receipt-response-record-v0.1",
        "created_at": "2026-06-16T07:10:00Z",
        "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "requested_receipt_class": "result-return",
        "response_state": "actual-response-received",
        "counterparty_role": "probe result-return steward",
        "counterparty_identity_ref": "org:probe-counterparty",
        "source_external_to_host": True,
        "dependency_group": "probe-independent-group",
        "response_channel": "non-host-email",
        "received_at": "2026-06-16T07:10:00Z",
        "response_artifacts": [{"artifact_id":"ERRR-PROBE-A1","artifact_type":"signed-response","locator_or_hash":"sha256:" + "2"*64,"generated_by":"external-counterparty","retained_by":"non-host-vault","sealed":True,"dry_run":False}],
        "verification_result": {"counterparty_confirmed":True,"signature_or_equivalent_verified":True,"timestamp_independent":True,"request_trace_matches":True,"nonhost_retention_verified":True,"dependency_checked":True,"stale_or_superseded":False,"can_generate_actual_intake":True},
        "resulting_intake_record_ref": None,
        "quorum_effect": {"can_create_live_intake":True,"can_satisfy_quorum_by_itself":False,"can_increment_independent_receipts_present":False,"live_weight":0,"dry_run_weight":0,"reliance_effect":"stayed","limit_reasons":["probe no quorum by itself"],"public_failed_gate_summary_required":True},
        "public_summary_ref": "public-shell:probe-response",
        "linked_live_evidence_acquisition_packet_ref": f"LEAP-2026-{REV}-probe-live-evidence-acquisition",
        "linked_custody_record_ref": "CACR-2026-probe-live-custody",
        "linked_response_verification_gate_ref": "ERVG-2026-probe-response-gate",
    }


# Static examples/schema validation.
validate("schemas/external-receipt-intake-conversion-gate.schema.json", f"examples/external-receipt-intake-conversion-gate-{REV}-blocked-no-response-record.json")
validate("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/intake-conversion-gate-skipped-response-gate.json")
validate("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/intake-conversion-gate-import-unlocked.json")
validate("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json")
validate("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json")

# Schema regression: response naming an intake must bind the conversion gate.
if Draft202012Validator is not None:
    schema = load("schemas/external-receipt-response-record.schema.json")
    resp = base_response_record()
    resp["resulting_intake_record_ref"] = "ERIR-2026-probe-live-intake"
    errors = list(Draft202012Validator(schema).iter_errors(resp))
    if not errors:
        raise SystemExit("response record with resulting intake but no intake conversion gate unexpectedly validates")
    resp["linked_intake_conversion_gate_ref"] = "ERICG-2026-probe-intake-conversion"
    errors = sorted(Draft202012Validator(schema).iter_errors(resp), key=lambda e: list(e.path))
    if errors:
        raise SystemExit("response record with intake conversion gate failed schema probe: " + errors[0].message)

    intake_schema = load("schemas/external-receipt-intake-record.schema.json")
    intake = load("examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json")
    live_intake = dict(intake)
    live_intake["receipt_record_id"] = "ERIR-2026-probe-live-intake"
    live_intake["linked_live_evidence_acquisition_packet_ref"] = f"LEAP-2026-{REV}-probe-live-evidence-acquisition"
    live_intake["linked_custody_record_ref"] = "CACR-2026-probe-live-custody"
    errors = list(Draft202012Validator(intake_schema).iter_errors(live_intake))
    if not errors:
        raise SystemExit("lineaged actual intake without conversion gate unexpectedly validates")
    live_intake["linked_intake_conversion_gate_ref"] = "ERICG-2026-probe-intake-conversion"
    errors = sorted(Draft202012Validator(intake_schema).iter_errors(live_intake), key=lambda e: list(e.path))
    if errors:
        raise SystemExit("lineaged actual intake with conversion gate failed schema probe: " + errors[0].message)

with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    gate_path = d / "gate.json"
    resp_path = d / "response.json"
    desc_path = d / "desc.json"
    write(gate_path, base_response_gate())
    write(resp_path, base_response_record())
    write(desc_path, {"manual_conversion_review_completed": True, "public_failed_gate_summary_ready_for_blocks": True, "private_material_not_in_public_release": True})
    subprocess.run([sys.executable, str(ROOT / "tools" / "prepare_external_receipt_intake_conversion_gate.py"), "--response-record", str(resp_path), "--response-gate", str(gate_path), "--conversion-descriptor", str(desc_path), "--output-dir", str(d), "--gate-id", "probe-eligible"], check=True)
    out = load(d / "external-receipt-intake-conversion-gate-probe-eligible.json")
    if out.get("gate_state") != "eligible-for-intake-record":
        raise SystemExit("eligible probe did not pass intake conversion gate: " + out.get("gate_state", "missing"))
    if out.get("downstream_locks", {}).get("may_prepare_external_receipt_intake_record") is not True:
        raise SystemExit("eligible intake conversion gate did not allow intake preparation")
    if out.get("downstream_locks", {}).get("may_run_import_gate") is not False or out.get("downstream_locks", {}).get("live_floor_delta_allowed") is not False:
        raise SystemExit("intake conversion gate unlocked import/floor")

    bad_gate = base_response_gate()
    bad_gate["gate_state"] = "blocked-unverified"
    bad_gate["downstream_locks"]["may_prepare_external_receipt_response_record"] = False
    write(gate_path, bad_gate)
    subprocess.run([sys.executable, str(ROOT / "tools" / "prepare_external_receipt_intake_conversion_gate.py"), "--response-record", str(resp_path), "--response-gate", str(gate_path), "--conversion-descriptor", str(desc_path), "--output-dir", str(d), "--gate-id", "probe-blocked-gate"], check=True)
    blocked = load(d / "external-receipt-intake-conversion-gate-probe-blocked-gate.json")
    if blocked.get("gate_state") != "blocked-response-gate-not-eligible":
        raise SystemExit("blocked response gate probe failed closed incorrectly")

    fixture_gate = base_response_gate()
    fixture_gate["response_gate_id"] = "ERVG-2026-fixture-probe"
    fixture_gate["input_response_descriptor"]["dry_run"] = True
    fixture_resp = base_response_record()
    fixture_resp["response_record_id"] = "ERRR-2026-fixture-probe"
    fixture_resp["linked_response_verification_gate_ref"] = "ERVG-2026-fixture-probe"
    fixture_resp["quorum_effect"]["dry_run_weight"] = 1
    write(gate_path, fixture_gate)
    write(resp_path, fixture_resp)
    subprocess.run([sys.executable, str(ROOT / "tools" / "prepare_external_receipt_intake_conversion_gate.py"), "--response-record", str(resp_path), "--response-gate", str(gate_path), "--conversion-descriptor", str(desc_path), "--output-dir", str(d), "--gate-id", "probe-fixture"], check=True)
    fx = load(d / "external-receipt-intake-conversion-gate-probe-fixture.json")
    if fx.get("gate_state") != "blocked-fixture-or-dryrun":
        raise SystemExit("fixture/dry-run probe did not block")

# Archived gates must never unlock import/floor.
for path in (ROOT / "examples").glob("external-receipt-intake-conversion-gate*.json"):
    data = load(path)
    if data.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{path.relative_to(ROOT)} has live floor effect")
    locks = data.get("downstream_locks", {})
    if locks.get("may_run_import_gate") is not False or locks.get("live_floor_delta_allowed") is not False:
        raise SystemExit(f"{path.relative_to(ROOT)} unlocks import or floor")

print("audit_external_receipt_intake_conversion_gate: OK")
