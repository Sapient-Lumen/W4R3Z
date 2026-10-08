#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-inbound-capture-shell-{REV}-no-inbound.json"
SCHEMA_REL = "schemas/external-contact-inbound-capture-shell.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-inbound-capture-shell-public-raw-leak.json"

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
        raise SystemExit(f"{label} fails external-contact-inbound-capture-shell.schema.json: {errors[0].message}")

schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("inbound-capture shell revision mismatch")
if record.get("schema_version") != "external-contact-inbound-capture-shell-v0.1":
    raise SystemExit("inbound-capture shell schema version mismatch")
if record.get("capture_state") != "pre-dispatch-no-inbound":
    raise SystemExit("current inbound-capture shell must stay pre-dispatch/no-inbound")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("inbound-capture shell must have no live-floor effect")

sources = {
    "precommit": record.get("source_inbound_vault_precommit_ref"),
    "send-proof": record.get("source_send_proof_record_ref"),
    "response-triage": record.get("source_response_triage_record_ref"),
    "execution": record.get("source_execution_record_ref"),
}
for label, rel in sources.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"inbound-capture shell missing source: {label}={rel}")
    src = load(rel)
    if src.get("revision") != REV or src.get("no_live_floor_effect") is not True:
        raise SystemExit(f"inbound-capture shell source is not current/no-floor: {label}")

precommit = load(sources["precommit"])
send_proof = load(sources["send-proof"])
execution = load(sources["execution"])
triage = load(sources["response-triage"])
if precommit.get("source_inbound_capture_shell_ref") != RECORD_REL:
    raise SystemExit("inbound-vault precommit is not bound to current inbound-capture shell")
if send_proof.get("send_proof_state") != "not-sent-no-proof":
    raise SystemExit("current inbound-capture shell must bind not-sent send-proof")
if execution.get("execution_state") != "no-send-recorded":
    raise SystemExit("current inbound-capture shell must bind no-send execution record")
if triage.get("triage_state") != "pre-dispatch-no-inbound":
    raise SystemExit("current inbound-capture shell must bind pre-dispatch triage")

cap_tool = record.get("capture_tool", {})
if cap_tool.get("tool_path") != "tools/stage_external_contact_inbound_capture.py" or not (ROOT / cap_tool.get("tool_path", "")).exists():
    raise SystemExit("inbound-capture shell stage tool missing")
for key in ["raw_input_required_outside_release_tree", "copy_to_private_vault_only", "public_shell_only", "check_output_supported", "tool_is_not_dispatch_or_response"]:
    if cap_tool.get(key) is not True:
        raise SystemExit(f"inbound-capture shell tool guard missing: {key}")

payload = record.get("candidate_payload", {})
expected_payload = {
    "raw_payload_present_now": False,
    "source_locator": None,
    "private_vault_locator": None,
    "raw_sha256": None,
    "size_bytes": None,
    "mime_type": None,
    "message_format": None,
    "raw_payload_publicly_embedded": False,
    "screenshot_or_redacted_only": False,
    "protocol_output_only": False,
    "retention_permission_present_now": False,
    "nonhost_retention_present_now": False,
}
for key, expected in expected_payload.items():
    if payload.get(key) is not expected:
        raise SystemExit(f"inbound-capture payload current-state guard unsafe: {key}")

parse = record.get("transport_parse", {})
for key in ["rfc5322_parse_attempted", "message_id_present", "date_header_present", "from_header_present", "to_or_delivered_to_present", "received_or_provider_trace_present", "authentication_results_summary_present", "arc_summary_present"]:
    if parse.get(key) is not False:
        raise SystemExit(f"inbound-capture parse guard must be false pre-dispatch: {key}")
if parse.get("in_reply_to_or_references_binding_state") != "not-applicable-no-sent-message":
    raise SystemExit("inbound-capture binding state must reflect no sent message")
for key in ["parse_or_authentication_may_create_authority", "parse_or_authentication_may_start_clock"]:
    if parse.get(key) is not False:
        raise SystemExit(f"inbound-capture parse/auth overclaim: {key}")

shell = record.get("public_shell", {})
if shell.get("shell_created_now") is not False:
    raise SystemExit("pre-dispatch inbound-capture shell must not claim a future shell already exists")
for key in ["shell_may_satisfy_raw_custody", "shell_may_satisfy_counterparty_authority", "shell_may_start_response_clock", "shell_may_publish_raw_bytes"]:
    if shell.get(key) is not False:
        raise SystemExit(f"inbound-capture public shell overclaims: {key}")
for term in ["raw reply bytes", "full headers", "private vault", "personal", "trade secrets", "retention", "waiver", "adverse", "status", "live-floor"]:
    if term not in " ".join(shell.get("forbidden_public_fields", [])).lower():
        raise SystemExit(f"inbound-capture forbidden public fields missing term: {term}")

routes = record.get("routing_constraints", {})
route_text = "\n".join(str(v).lower() for v in routes.values())
for term in ["automated", "decline", "human", "malformed", "silence", "waiver", "adverse", "custody", "floor"]:
    if term not in route_text:
        raise SystemExit(f"inbound-capture routing constraints missing term: {term}")
if routes.get("routes_may_create_response_record_directly") is not False:
    raise SystemExit("inbound-capture routes must not create response record directly")

for key, val in record.get("downstream_locks", {}).items():
    if val is not False:
        raise SystemExit(f"inbound-capture downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"inbound-capture shell references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"inbound-capture shell references missing surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-inbound-capture-shell" not in fx.get("target_filings", []):
    raise SystemExit("inbound-capture fixture does not target capture shell")
if fx.get("severity") != "critical":
    raise SystemExit("inbound-capture fixture must be critical")

subprocess.run([sys.executable, str(ROOT / "tools" / "stage_external_contact_inbound_capture.py"), "--check-output"], check=True)

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["candidate_payload"]["raw_payload_publicly_embedded"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("inbound-capture schema failed to reject public raw-byte leak")
    mut2 = copy.deepcopy(record)
    mut2["public_shell"]["shell_may_start_response_clock"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("inbound-capture schema failed to reject public shell clock start")
    mut3 = copy.deepcopy(record)
    mut3["transport_parse"]["parse_or_authentication_may_create_authority"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("inbound-capture schema failed to reject auth-as-authority")
    mut4 = copy.deepcopy(record)
    mut4["downstream_locks"]["may_create_custody_record"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("inbound-capture schema failed to reject custody from capture shell")

print("audit_external_contact_inbound_capture_shell: OK")
