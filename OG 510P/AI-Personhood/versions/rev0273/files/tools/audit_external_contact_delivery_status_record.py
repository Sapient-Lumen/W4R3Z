#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-delivery-status-record-{REV}-pre-dispatch-no-status.json"
SCHEMA_REL = "schemas/external-contact-delivery-status-record.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-delivery-status-dsn-as-response.json"

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
        raise SystemExit(f"{label} fails external-contact-delivery-status-record.schema.json: {errors[0].message}")


schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("delivery-status record revision mismatch")
if record.get("schema_version") != "external-contact-delivery-status-record-v0.1":
    raise SystemExit("delivery-status schema version mismatch")
if record.get("delivery_status_state") != "pre-dispatch-no-delivery-status":
    raise SystemExit("current delivery-status record must stay pre-dispatch/no-status")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("delivery-status record must have no live-floor effect")

sources = {
    "execution": record.get("source_execution_record_ref"),
    "send-proof": record.get("source_send_proof_record_ref"),
    "send-trace": record.get("source_send_trace_shell_ref"),
    "dispatch-card": record.get("source_dispatch_authorization_card_ref"),
    "response-triage": record.get("source_response_triage_record_ref"),
}
for label, rel in sources.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"delivery-status missing source: {label}={rel}")
    src = load(rel)
    if src.get("revision") != REV or src.get("no_live_floor_effect") is not True:
        raise SystemExit(f"delivery-status source is not current/no-floor: {label}")

execution = load(sources["execution"])
send_proof = load(sources["send-proof"])
send_trace = load(sources["send-trace"])
triage = load(sources["response-triage"])
if execution.get("delivery_status_record_ref") != RECORD_REL:
    raise SystemExit("execution record is not bound to delivery-status record")
for label, obj in [("send-proof", send_proof), ("send-trace", send_trace), ("response-triage", triage)]:
    if RECORD_REL not in obj.get("related_surfaces", []):
        raise SystemExit(f"{label} is not related-surface bound to delivery-status record")
if send_proof.get("send_proof_state") != "not-sent-no-proof" or send_trace.get("send_trace_state") != "pre-dispatch-no-transport":
    raise SystemExit("delivery-status current state must bind unsent/no-transport sources")

cap_tool = record.get("status_capture_tool", {})
if cap_tool.get("tool_path") != "tools/stage_external_contact_delivery_status.py" or not (ROOT / cap_tool.get("tool_path", "")).exists():
    raise SystemExit("delivery-status stage tool missing")
for key in ["raw_input_required_outside_release_tree", "copy_to_private_vault_only", "public_shell_only", "check_output_supported", "tool_is_not_delivery_or_response"]:
    if cap_tool.get(key) is not True:
        raise SystemExit(f"delivery-status tool guard missing: {key}")

candidate = record.get("candidate_delivery_status", {})
expected_candidate = {
    "raw_status_present_now": False,
    "source_locator": None,
    "private_status_locator": None,
    "raw_status_sha256": None,
    "size_bytes": None,
    "mime_type": None,
    "status_format": None,
    "dsn_action": None,
    "status_code": None,
    "diagnostic_code_present": False,
    "final_recipient_matches_selected_candidate": False,
    "original_message_id_or_envid_matches_sent_trace": False,
    "raw_status_publicly_embedded": False,
    "screenshot_only": False,
    "provider_ui_only": False,
    "counterparty_human_reply_present": False,
    "delivery_status_proof_present_now": False,
}
for key, expected in expected_candidate.items():
    if candidate.get(key) is not expected:
        raise SystemExit(f"delivery-status current candidate guard unsafe: {key}")

classification = record.get("dsn_classification_rules", {})
for key in ["rfc3461_dsn_extension_is_transport_only", "rfc3464_message_delivery_status_is_transport_only", "failed_dsn_is_not_counterparty_decline", "delayed_dsn_is_not_no_response", "delivered_or_relayed_dsn_is_not_counterparty_response"]:
    if classification.get(key) is not True:
        raise SystemExit(f"delivery-status classification rule missing: {key}")
for key in ["auto_generated_dsn_may_create_response_record", "dsn_may_create_custody", "dsn_may_create_authority", "dsn_may_increment_live_floor"]:
    if classification.get(key) is not False:
        raise SystemExit(f"delivery-status classification overclaims: {key}")

clock = record.get("response_clock_policy", {})
if clock.get("clock_may_start_now") is not False:
    raise SystemExit("delivery-status record must not start clock now")
for key in ["start_requires_signed_authorization", "start_requires_sent_at_utc", "start_requires_send_trace_transport_proof", "start_requires_send_proof_record_sent_state", "start_requires_no_failed_or_delayed_delivery_status", "bounce_or_delay_suspends_no_response_claim"]:
    if clock.get(key) is not True:
        raise SystemExit(f"delivery-status clock policy missing: {key}")
for key in ["start_may_use_delivery_status_timestamp_alone", "no_response_may_be_recorded_now", "delivery_status_may_substitute_for_counterparty_reply"]:
    if clock.get(key) is not False:
        raise SystemExit(f"delivery-status clock policy overclaims: {key}")

decision = record.get("delivery_outcome_decision", {})
if decision.get("current_outcome") != "not-applicable-pre-dispatch" or decision.get("delivery_status_processed_now") is not False:
    raise SystemExit("delivery-status outcome must remain pre-dispatch/not processed")
for key in ["hard_bounce_requires_counterparty_or_channel_reselection", "delayed_status_requires_watch_not_no_response", "successful_delivery_is_not_human_response", "public_status_shell_allowed"]:
    if decision.get(key) is not True:
        raise SystemExit(f"delivery-status outcome decision missing: {key}")
if decision.get("retry_or_reselection_may_create_failed_gate") is not False:
    raise SystemExit("delivery-status outcome must not permit failed-gate from retry/reselection")

policy = record.get("public_shell_policy", {})
for key in ["public_shell_may_publish_raw_dsn", "public_shell_may_publish_personal_headers", "public_shell_may_satisfy_delivery_proof", "public_shell_may_start_response_clock"]:
    if policy.get(key) is not False:
        raise SystemExit(f"delivery-status public-shell overclaim: {key}")
if policy.get("private_raw_status_required_for_delivery_outcome") is not True:
    raise SystemExit("delivery-status shell must require private raw status for delivery outcome")
for term in ["raw", "headers", "personal", "provider", "private vault", "tokens", "smtp"]:
    if term not in " ".join(policy.get("forbidden_public_fields", [])).lower():
        raise SystemExit(f"delivery-status forbidden public fields missing term: {term}")

for key, val in record.get("downstream_locks", {}).items():
    if val is not False:
        raise SystemExit(f"delivery-status downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"delivery-status record references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"delivery-status record references missing surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-delivery-status-record" not in fx.get("target_filings", []):
    raise SystemExit("delivery-status fixture does not target delivery-status record")
if fx.get("severity") != "critical":
    raise SystemExit("delivery-status fixture must be critical")

subprocess.run([sys.executable, str(ROOT / "tools" / "stage_external_contact_delivery_status.py"), "--check-output"], check=True)

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["downstream_locks"]["may_treat_dsn_as_counterparty_response"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("delivery-status schema failed to reject DSN-as-response")
    mut2 = copy.deepcopy(record)
    mut2["response_clock_policy"]["start_may_use_delivery_status_timestamp_alone"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("delivery-status schema failed to reject delivery-status timestamp as clock")
    mut3 = copy.deepcopy(record)
    mut3["public_shell_policy"]["public_shell_may_satisfy_delivery_proof"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("delivery-status schema failed to reject public-shell-as-delivery-proof")
    mut4 = copy.deepcopy(record)
    mut4["candidate_delivery_status"]["raw_status_publicly_embedded"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("delivery-status schema failed to reject raw DSN leak")

print("audit_external_contact_delivery_status_record: OK")
