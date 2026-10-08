#!/usr/bin/env python3
import copy
import json
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
GRAPH_REL = f"examples/live-artifact-admission-graph-{REV}.json"
SCHEMA_REL = "schemas/live-artifact-admission-graph.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

# The generated graph must match the builder exactly.
subprocess.run([sys.executable, str(ROOT / "tools" / "build_live_artifact_admission_graph.py"), "--check"], check=True)

graph = load(GRAPH_REL)
if Draft202012Validator is not None:
    schema = load(SCHEMA_REL)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(graph), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{GRAPH_REL} fails live-artifact-admission-graph.schema.json: {errors[0].message}")

if graph.get("revision") != REV:
    raise SystemExit("admission graph revision mismatch")
if graph.get("no_live_floor_effect") is not True:
    raise SystemExit("admission graph must have no live-floor effect")
if graph.get("live_path_state", {}).get("computed_live_floor") != 0:
    raise SystemExit("admission graph observed nonzero live floor")
if graph.get("live_path_state", {}).get("downstream_creation_blocked") is not True:
    raise SystemExit("downstream creation should remain blocked while no actual live artifact exists")

node_ids = {n.get("node_id") for n in graph.get("nodes", [])}
edge_pairs = {(e.get("from"), e.get("to")) for e in graph.get("edges", [])}
for node_id in ["CANDIDATE_CHALLENGE", "CANDIDATE_DISPOSITION", "AUTHORITY_EVIDENCE_BINDER", "CUSTODY_GATE"]:
    if node_id not in node_ids:
        raise SystemExit(f"admission graph missing node {node_id}")
for edge in [("CANDIDATE_CHALLENGE", "CANDIDATE_DISPOSITION"), ("CANDIDATE_DISPOSITION", "AUTHORITY_EVIDENCE_BINDER"), ("AUTHORITY_EVIDENCE_BINDER", "CUSTODY_GATE")]:
    if edge not in edge_pairs:
        raise SystemExit(f"admission graph missing edge {edge}")
if graph.get("live_path_state", {}).get("gate_consumable_candidate_disposition_count", 0) != 0:
    raise SystemExit("current no-artifact graph must not have a gate-consumable challenge disposition")
# Authority evidence binder is represented as a graph node/check rather than a floor input.
if any(n.get("node_id") == "AUTHORITY_EVIDENCE_BINDER" and n.get("actual_live_count", 0) != 0 for n in graph.get("nodes", [])):
    raise SystemExit("current no-artifact graph must not have a gate-consumable authority binder")
failed = [c for c in graph.get("bypass_checks", []) if c.get("passed") is not True]
if failed:
    raise SystemExit("admission graph bypass check failed: " + failed[0].get("check_id", "unknown"))

# Schema-regression probes: actual downstream records without LEAP/custody refs must fail.
if Draft202012Validator is not None:
    response_schema = load("schemas/external-receipt-response-record.schema.json")
    response = {
        "response_record_id": "ERRR-2026-schema-probe-actual-response",
        "schema_version": "external-receipt-response-record-v0.1",
        "created_at": "2026-06-13T18:46:00Z",
        "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "requested_receipt_class": "result-return",
        "response_state": "actual-response-received",
        "counterparty_role": "probe",
        "counterparty_identity_ref": "org:probe",
        "source_external_to_host": True,
        "dependency_group": "probe-independent",
        "response_channel": "non-host-email",
        "received_at": "2026-06-13T18:46:00Z",
        "response_artifacts": [{"artifact_id":"probe-a","artifact_type":"signed-response","locator_or_hash":"sha256:" + "0"*64,"generated_by":"external-counterparty","retained_by":"non-host","sealed":True,"dry_run":False}],
        "verification_result": {"counterparty_confirmed":True,"signature_or_equivalent_verified":True,"timestamp_independent":True,"request_trace_matches":True,"nonhost_retention_verified":True,"dependency_checked":True,"stale_or_superseded":False,"can_generate_actual_intake":True},
        "resulting_intake_record_ref": None,
        "quorum_effect": {"can_create_live_intake":True,"can_satisfy_quorum_by_itself":False,"can_increment_independent_receipts_present":False,"live_weight":0,"dry_run_weight":0,"reliance_effect":"stayed","limit_reasons":["schema probe"],"public_failed_gate_summary_required":True},
        "public_summary_ref": "public-shell:schema-probe"
    }
    errors = list(Draft202012Validator(response_schema).iter_errors(response))
    if not errors:
        raise SystemExit("actual response without LEAP/custody refs unexpectedly validates")
    response_ok = copy.deepcopy(response)
    response_ok["linked_live_evidence_acquisition_packet_ref"] = f"LEAP-2026-{REV}-first-live-evidence-acquisition"
    response_ok["linked_custody_record_ref"] = "CACR-2026-probe-live-custody"
    response_ok["linked_response_verification_gate_ref"] = "ERVG-2026-probe-live-response-gate"
    errors = sorted(Draft202012Validator(response_schema).iter_errors(response_ok), key=lambda e: list(e.path))
    if errors:
        raise SystemExit("actual response with LEAP/custody refs failed schema probe: " + errors[0].message)


    leap_schema = load("schemas/live-evidence-acquisition-packet.schema.json")
    leap = load(f"examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json")
    leap_probe = copy.deepcopy(leap)
    leap_probe["state"] = "candidate-artifact-received"
    leap_probe["source_request"]["request_trace_present"] = True
    leap_probe["source_request"]["counterparty_contact_present"] = True
    leap_probe["raw_payload_control"]["raw_payload_locator"] = "examples/artifacts/live-evidence-drops/schema-probe.txt"
    leap_probe["raw_payload_control"]["raw_payload_sha256"] = "0" * 64
    leap_probe["raw_payload_control"]["raw_payload_present"] = True
    leap_probe["raw_payload_control"]["nonhost_retention_present"] = True
    leap_probe["raw_payload_control"]["sealed_public_parity_present"] = True
    leap_probe["independence_controls"]["counterparty_org_id_present"] = True
    leap_probe["independence_controls"]["dependency_group_id_present"] = True
    errors = list(Draft202012Validator(leap_schema).iter_errors(leap_probe))
    if not errors:
        raise SystemExit("candidate LEAP without evidence-drop ledger ref unexpectedly validates")
    leap_probe["source_evidence_drop_ledger_ref"] = "LEDL-2026-schema-probe"
    errors = sorted(Draft202012Validator(leap_schema).iter_errors(leap_probe), key=lambda e: list(e.path))
    if errors:
        raise SystemExit("candidate LEAP with evidence-drop ledger ref failed schema probe: " + errors[0].message)

    arig_schema = load("schemas/actual-receipt-import-gate.schema.json")
    arig = {
        "import_gate_id": "ARIG-2026-schema-probe-actual-live-import",
        "schema_version": "actual-receipt-import-gate-v0.1",
        "created_at": "2026-06-13T18:46:00Z",
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "source_response_record_ref": "ERRR-2026-schema-probe-actual-response",
        "source_intake_record_ref": "ERIR-2026-schema-probe-actual-intake",
        "linked_conversion_drill_ref": "RTIC-2026-schema-probe",
        "import_mode": "actual-live-import",
        "source_provenance": {"state_field_claim":"actual","collection_context":"live-counterparty","counterparty_external":True,"nonhost_retention":True,"sealed_public_parity":True,"dependency_group":"probe-independent","provenance_disqualifiers":[]},
        "gate_checks": {"response_state_actual":True,"intake_state_actual_external":True,"source_external_to_host":True,"signature_verified":True,"timestamp_independent":True,"cryptographic_adapter_verified":True,"request_trace_matches":True,"nonhost_retention_verified":True,"dependency_group_checked":True,"fixture_or_dry_run_excluded_from_live_floor":True,"one_class_quorum_blocked":True,"failed_gates_publicly_summarized":True},
        "import_decision": {"import_allowed_to_live_floor":True,"imported_receipt_class":"result-return","live_floor_delta":1,"independent_receipts_present_before":0,"independent_receipts_present_after":1,"live_class_credit_granted":True,"cross_critical_quorum_satisfied":False,"reliance_effect":"stayed","blocked_actions":["schema probe"],"reason":"schema probe"},
        "failed_gate_public_summary_refs": ["FGPS-2026-schema-probe"],
        "public_summary_ref": "public-shell:schema-probe",
        "cryptographic_verifier_adapter_ref": "examples/cryptographic-verifier-adapter-schema-probe.json"
    }
    if not list(Draft202012Validator(arig_schema).iter_errors(arig)):
        raise SystemExit("actual-live import without LEAP/custody provenance unexpectedly validates")

# Negative fixtures must be registered.
required = {
    "NF-CUSTODY-2026-0002": "fixtures/negative-tests/live-artifact-admission-graph-response-before-custody.json",
    "NF-PROTOCOL-PIVOT-2026-0003": "fixtures/negative-tests/live-artifact-admission-graph-import-without-leap.json",
}
for fid, rel in required.items():
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing admission graph fixture: {rel}")
    if load(rel).get("fixture_id") != fid:
        raise SystemExit(f"fixture id mismatch in {rel}")
suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required) <= suite_ids:
    raise SystemExit("fixture suite missing admission graph fixtures")
if not set(required) <= report_ids:
    raise SystemExit("fixture report missing admission graph fixtures")

print("audit_live_artifact_admission_graph: OK")
