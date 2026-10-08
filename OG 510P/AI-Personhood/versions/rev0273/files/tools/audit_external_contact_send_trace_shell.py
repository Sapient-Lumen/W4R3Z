#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-send-trace-shell-{REV}-no-transport.json"
SCHEMA_REL = "schemas/external-contact-send-trace-shell.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-send-trace-shell-message-id-as-clock.json"

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
        raise SystemExit(f"{label} fails external-contact-send-trace-shell.schema.json: {errors[0].message}")

schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("send-trace shell revision mismatch")
if record.get("schema_version") != "external-contact-send-trace-shell-v0.1":
    raise SystemExit("send-trace shell schema version mismatch")
if record.get("send_trace_state") != "pre-dispatch-no-transport":
    raise SystemExit("current send-trace shell must stay pre-dispatch/no-transport")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("send-trace shell must have no live-floor effect")

sources = {
    "send-proof": record.get("source_send_proof_record_ref"),
    "execution": record.get("source_execution_record_ref"),
    "dispatch-card": record.get("source_dispatch_authorization_card_ref"),
}
for label, rel in sources.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"send-trace shell missing source: {label}={rel}")
    src = load(rel)
    if src.get("revision") != REV or src.get("no_live_floor_effect") is not True:
        raise SystemExit(f"send-trace source is not current/no-floor: {label}")

send_proof = load(sources["send-proof"])
execution = load(sources["execution"])
card = load(sources["dispatch-card"])
if send_proof.get("send_proof_state") != "not-sent-no-proof":
    raise SystemExit("pre-dispatch send-trace shell must bind not-sent send-proof")
if send_proof.get("source_send_trace_shell_ref") != RECORD_REL:
    raise SystemExit("send-proof record is not bound to current send-trace shell")
if execution.get("send_trace_shell_ref") != RECORD_REL:
    raise SystemExit("execution record is not bound to current send-trace shell")
if card.get("source_send_trace_shell_ref") != RECORD_REL:
    raise SystemExit("dispatch card is not bound to current send-trace shell")
if record.get("source_mail_ready_draft_ref") != send_proof.get("source_mail_ready_draft_ref"):
    raise SystemExit("send-trace shell and send-proof disagree on mail-ready draft")

cap_tool = record.get("trace_capture_tool", {})
if cap_tool.get("tool_path") != "tools/stage_external_contact_send_trace.py" or not (ROOT / cap_tool.get("tool_path", "")).exists():
    raise SystemExit("send-trace stage tool missing")
for key in ["raw_input_required_outside_release_tree", "copy_to_private_vault_only", "public_shell_only", "check_output_supported", "tool_is_not_dispatch_or_response"]:
    if cap_tool.get(key) is not True:
        raise SystemExit(f"send-trace tool guard missing: {key}")

candidate = record.get("candidate_trace", {})
expected_candidate = {
    "raw_trace_present_now": False,
    "source_locator": None,
    "private_trace_locator": None,
    "raw_trace_sha256": None,
    "size_bytes": None,
    "mime_type": None,
    "trace_format": None,
    "raw_trace_publicly_embedded": False,
    "screenshot_only": False,
    "provider_ui_only": False,
    "message_id_observed": None,
    "transport_proof_present_now": False,
}
for key, expected in expected_candidate.items():
    if candidate.get(key) is not expected:
        raise SystemExit(f"send-trace current candidate guard unsafe: {key}")

headers = record.get("message_header_checks", {})
for key in ["rfc5322_parse_attempted", "message_id_present", "date_header_present", "from_header_present", "to_header_present", "subject_present", "received_or_provider_trace_present", "authentication_results_present", "dkim_or_dmarc_result_present"]:
    if headers.get(key) is not False:
        raise SystemExit(f"send-trace header parse guard must be false pre-dispatch: {key}")
for key in ["message_id_may_start_response_clock", "headers_may_create_custody", "auth_results_may_create_authority"]:
    if headers.get(key) is not False:
        raise SystemExit(f"send-trace header overclaim: {key}")

deadline = record.get("deadline_binding", {})
if deadline.get("response_deadline_days") != card.get("message_binding", {}).get("response_deadline_days"):
    raise SystemExit("send-trace deadline days do not match dispatch card")
for key in ["sent_at_present_now", "deadline_may_start_now", "deadline_may_be_computed_from_draft_date", "silence_may_be_recorded_now"]:
    if deadline.get(key) is not False:
        raise SystemExit(f"send-trace deadline guard must be false: {key}")
if deadline.get("sent_at_utc") is not None or deadline.get("deadline_at") is not None:
    raise SystemExit("pre-dispatch send-trace shell must not claim sent_at/deadline")
if deadline.get("deadline_requires_actual_sent_at_and_transport_proof") is not True:
    raise SystemExit("send-trace deadline must require actual sent_at and transport proof")

policy = record.get("public_shell_policy", {})
if policy.get("shell_created_now") is not False:
    raise SystemExit("pre-dispatch send-trace shell must not claim a shell created from raw trace")
for key in ["public_shell_may_satisfy_transport_proof", "public_shell_may_publish_raw_headers", "public_shell_may_start_response_clock"]:
    if policy.get(key) is not False:
        raise SystemExit(f"send-trace public shell overclaim: {key}")
if policy.get("private_raw_trace_required_for_sent_state") is not True:
    raise SystemExit("send-trace public shell must require private raw trace for sent state")
for term in ["raw", "headers", "private vault", "provider", "personal", "counterparty", "internal"]:
    if term not in " ".join(policy.get("forbidden_public_fields", [])).lower():
        raise SystemExit(f"send-trace forbidden public fields missing term: {term}")

clock = record.get("response_clock_guard", {})
if clock.get("clock_may_start_now") is not False:
    raise SystemExit("send-trace shell must not start clock now")
for key in ["requires_signed_authorization", "requires_sent_at", "requires_private_transport_trace", "requires_public_trace_shell", "requires_send_proof_record_update", "auto_ack_routes_to_triage_not_response", "silence_is_not_waiver"]:
    if clock.get(key) is not True:
        raise SystemExit(f"send-trace response-clock guard missing: {key}")

for key, val in record.get("downstream_locks", {}).items():
    if val is not False:
        raise SystemExit(f"send-trace downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"send-trace shell references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"send-trace shell references missing surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-send-trace-shell" not in fx.get("target_filings", []):
    raise SystemExit("send-trace fixture does not target send-trace shell")
if fx.get("severity") != "critical":
    raise SystemExit("send-trace fixture must be critical")

subprocess.run([sys.executable, str(ROOT / "tools" / "stage_external_contact_send_trace.py"), "--check-output"], check=True)

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["message_header_checks"]["message_id_may_start_response_clock"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("send-trace schema failed to reject Message-ID-as-clock")
    mut2 = copy.deepcopy(record)
    mut2["public_shell_policy"]["public_shell_may_satisfy_transport_proof"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("send-trace schema failed to reject public-shell-as-transport-proof")
    mut3 = copy.deepcopy(record)
    mut3["candidate_trace"]["raw_trace_publicly_embedded"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("send-trace schema failed to reject raw trace public leak")
    mut4 = copy.deepcopy(record)
    mut4["downstream_locks"]["may_create_failed_gate_shell_now"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("send-trace schema failed to reject failed-gate shell now")

print("audit_external_contact_send_trace_shell: OK")
