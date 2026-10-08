#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKET_REL = f"examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json"
SCHEMA_REL = "schemas/live-evidence-acquisition-packet.schema.json"
CONTROL_REL = "examples/live-receipt-floor-control-case-positive-controls.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

packet = load(PACKET_REL)
if Draft202012Validator is not None:
    schema = load(SCHEMA_REL)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(packet), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{PACKET_REL} fails live-evidence-acquisition-packet.schema.json: {errors[0].message}")

if packet.get("revision") != REV:
    raise SystemExit("live evidence acquisition packet revision mismatch")
if packet.get("state") != "ready-no-live-artifact":
    raise SystemExit("LEAP must be ready-no-live-artifact until a genuine artifact exists")
if packet.get("no_live_floor_effect") is not True:
    raise SystemExit("LEAP must have no live-floor effect")
locks = packet.get("downstream_locks", {})
for key in ["response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed"]:
    if locks.get(key) is not False:
        raise SystemExit(f"LEAP must keep {key}=false before raw artifact admission")
if locks.get("failed_gate_public_summary_required") is not True:
    raise SystemExit("LEAP must require failed-gate public summary on rejection")
raw = packet.get("raw_payload_control", {})
if raw.get("raw_payload_present") is not False or raw.get("raw_payload_missing_blocks_response_creation") is not True:
    raise SystemExit("LEAP must block response creation while raw payload is absent")
crypto = packet.get("cryptographic_binding", {})
for key in ["cryptographic_verifier_adapter_required", "independent_timestamp_required", "issuer_key_id_required", "transparency_or_timestamp_log_required", "signature_boolean_zero_weight_without_adapter"]:
    if crypto.get(key) is not True:
        raise SystemExit(f"LEAP cryptographic binding missing required true flag: {key}")
ind = packet.get("independence_controls", {})
for key in [
    "counterparty_org_id_required",
    "dependency_group_id_required",
    "issuer_distinct_from_subject_host_required",
    "counterparty_distinct_from_subject_host_required",
    "correlation_discount_blocks_independence",
]:
    if ind.get(key) is not True:
        raise SystemExit(f"LEAP independence controls missing required true flag: {key}")
proto = packet.get("protocol_boundary", {})
for key in ["mcp_tool_output_is_not_authority", "a2a_task_state_is_not_authority", "federated_relay_is_not_nonhost_retention", "provenance_label_is_not_class_proof"]:
    if proto.get(key) is not True:
        raise SystemExit(f"LEAP protocol boundary missing required true flag: {key}")


# Candidate/admitted LEAP states must now descend from a staged evidence-drop ledger.
schema = load(SCHEMA_REL)
if "source_evidence_drop_ledger_ref" not in schema.get("properties", {}):
    raise SystemExit("LEAP schema lacks source_evidence_drop_ledger_ref")
if not (ROOT / f"examples/live-evidence-drop-ledger-{REV}-quarantine-control.json").exists():
    raise SystemExit("current evidence-drop quarantine ledger missing before LEAP")
if "raw payload has first been staged in a live evidence drop ledger" not in " ".join(locks.get("locks_release_only_after", [])):
    raise SystemExit("LEAP locks do not mention evidence-drop staging before release")

# Negative fixtures must be present and registered in fixture suite/report.
required_fixtures = {
    "NF-PROTOCOL-PIVOT-2026-0002": "fixtures/negative-tests/live-evidence-acquisition-packet-protocol-output-without-raw-custody.json",
    "NF-CRYPTO-2026-0002": "fixtures/negative-tests/live-evidence-acquisition-packet-correlated-counterparty-discount-bypassed.json",
}
for fid, rel in required_fixtures.items():
    if not (ROOT / rel).exists():
        raise SystemExit(f"LEAP required fixture missing: {rel}")
    if load(rel).get("fixture_id") != fid:
        raise SystemExit(f"LEAP fixture id mismatch in {rel}")
suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required_fixtures) <= suite_ids:
    raise SystemExit(f"fixture suite missing LEAP fixtures: {sorted(set(required_fixtures) - suite_ids)}")
if not set(required_fixtures) <= report_ids:
    raise SystemExit(f"fixture report missing LEAP fixtures: {sorted(set(required_fixtures) - report_ids)}")

# The control harness must now include and pass a correlation-discount case.
proc = subprocess.run(
    [sys.executable, str(ROOT / "tools/compute_live_receipt_floor.py"), "--control-case", str(ROOT / CONTROL_REL)],
    check=True,
    capture_output=True,
    text=True,
)
results = {row["case_id"]: row for row in json.loads(proc.stdout).get("results", [])}
case = results.get("correlated-positive-duplicate-dependency-discount")
if not case or not case.get("ok"):
    raise SystemExit("control harness missing or failing correlated-positive-duplicate-dependency-discount")
observed = case.get("observed", {})
if observed.get("independent_receipts_present") != 1:
    raise SystemExit("correlated control case must count exactly one independent receipt")
if not any(row.get("status") == "discounted" for row in observed.get("independence_discount_register", [])):
    raise SystemExit("correlated control case must expose discounted candidate in independence_discount_register")

queue = load("FOLLOWTHROUGH-QUEUE.json")
entries = {e.get("id"): e for e in queue.get("entries", [])}
if entries.get("FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", {}).get("state") != "advanced_not_closed":
    raise SystemExit("FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION should be advanced_not_closed after LEAP creation, not closed")

graph_rel = f"examples/live-artifact-admission-graph-{REV}.json"
if not (ROOT / graph_rel).exists():
    raise SystemExit("current live artifact admission graph missing")
graph = load(graph_rel)
if graph.get("live_path_state", {}).get("downstream_creation_blocked") is not True:
    raise SystemExit("admission graph must keep downstream creation blocked while LEAP has no artifact")

print("audit_live_evidence_acquisition_packet: OK")
