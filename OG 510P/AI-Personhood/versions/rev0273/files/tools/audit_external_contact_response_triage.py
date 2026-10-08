#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-response-triage-record-{REV}-pre-dispatch.json"
SCHEMA_REL = "schemas/external-contact-response-triage-record.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/external-contact-response-triage-auto-ack-as-response.json",
    "fixtures/negative-tests/external-contact-response-triage-protocol-output-as-authority.json",
    "fixtures/negative-tests/external-contact-response-triage-redacted-copy-as-raw.json",
]

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-response-triage-record.schema.json: {errors[0].message}")

schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("external-contact response triage revision mismatch")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("external-contact response triage must have no live-floor effect")

for rel_key in ["source_request_packet_ref", "source_execution_record_ref"]:
    rel = record.get(rel_key)
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"response triage missing source surface: {rel_key}={rel}")
    src = load(rel)
    if src.get("revision") != REV or src.get("no_live_floor_effect") is not True:
        raise SystemExit(f"response triage source is not current/no-floor: {rel}")

execution = load(record["source_execution_record_ref"])
if execution.get("source_packet_ref") != record.get("source_request_packet_ref"):
    raise SystemExit("response triage execution record is not bound to the same request packet")

inbound = record.get("inbound_state", {})
if record.get("triage_state") == "pre-dispatch-no-inbound":
    if inbound.get("inbound_artifact_present") is not False or inbound.get("inbound_source_kind") != "none":
        raise SystemExit("pre-dispatch response triage must not claim an inbound artifact")
    if inbound.get("raw_payload_retained") is not False or inbound.get("formal_response_record_exists") is not False:
        raise SystemExit("pre-dispatch response triage must not retain raw payload or formal response")

case_text = "\n".join(" ".join(str(v) for v in row.values()) for row in record.get("decision_matrix", [])).lower()
for term in ["not-sent", "silence", "decline", "automated", "raw", "redacted", "protocol", "tool"]:
    if term not in case_text:
        raise SystemExit(f"response triage decision matrix missing case term: {term}")
for term in ["waiver", "adverse", "custody", "response", "intake", "import", "live-floor"]:
    if term not in case_text:
        raise SystemExit(f"response triage decision matrix missing blocked interpretation term: {term}")

capture = record.get("capture_requirements", {})
for key in [
    "transport_trace_required",
    "raw_headers_or_equivalent_required",
    "final_outgoing_body_hash_required",
    "counterparty_role_or_org_required",
    "retention_permission_required",
    "public_shell_permission_or_condition_required",
    "confidentiality_conditions_required",
    "authority_not_inferred_from_reply",
]:
    if capture.get(key) is not True:
        raise SystemExit(f"response triage capture requirement missing: {key}")

shell = record.get("public_shell_policy", {})
for key in ["shell_required_for_decline_or_silence", "hash_shell_only_before_admission", "shell_is_not_waiver_or_adverse_inference"]:
    if shell.get(key) is not True:
        raise SystemExit(f"response triage public shell policy missing: {key}")
joined_forbidden = " ".join(shell.get("forbidden_public_fields", [])).lower()
for term in ["raw", "trade secret", "personal", "waiver", "adverse", "status", "live-floor"]:
    if term not in joined_forbidden:
        raise SystemExit(f"response triage public forbidden fields missing term: {term}")

vault = record.get("private_vault_route", {})
if vault.get("stage_tool") != "tools/stage_live_evidence_drop.py" or not (ROOT / vault.get("stage_tool", "")).exists():
    raise SystemExit("response triage must route raw payloads through stage_live_evidence_drop.py")
for key, expected in [
    ("raw_payload_must_stay_outside_release", True),
    ("public_release_may_include_raw_bytes", False),
    ("redacted_copy_may_satisfy_raw_custody", False),
    ("protocol_output_may_satisfy_authority", False),
]:
    if vault.get(key) is not expected:
        raise SystemExit(f"response triage vault route unsafe: {key}")
for rel in vault.get("allowed_next_surfaces", []):
    # Future first-artifact/custody schema references are allowed by schema path.
    if not (ROOT / rel).exists():
        raise SystemExit(f"response triage allowed next surface missing: {rel}")

locks = record.get("downstream_locks", {})
for key, value in locks.items():
    if value is not False:
        raise SystemExit(f"response triage downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"response triage references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"response triage references missing related surface: {rel}")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["downstream_locks"]["may_treat_auto_ack_as_counterparty_response"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("response triage schema failed to reject auto ack as counterparty response")
    mut2 = copy.deepcopy(record)
    mut2["private_vault_route"]["redacted_copy_may_satisfy_raw_custody"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("response triage schema failed to reject redacted copy as raw custody")
    mut3 = copy.deepcopy(record)
    mut3["downstream_locks"]["may_create_formal_response_record"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("response triage schema failed to reject formal response creation")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "external-contact-response-triage-record" not in fx.get("target_filings", []):
        raise SystemExit(f"response triage fixture does not target record: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"response triage fixture must be critical: {rel}")

print("audit_external_contact_response_triage: OK")
