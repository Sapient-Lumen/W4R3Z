#!/usr/bin/env python3
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-send-proof-record-{REV}-no-transport-proof.json"
SCHEMA_REL = "schemas/external-contact-send-proof-record.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-send-proof-record-draft-eml-as-sent.json"

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
        raise SystemExit(f"{label} fails external-contact-send-proof-record.schema.json: {errors[0].message}")


def parse_draft(text):
    headers, body = text.split("\n\n", 1)
    parsed = {}
    for line in headers.splitlines():
        if ":" not in line:
            raise SystemExit(f"mail-ready draft has malformed header line: {line}")
        k, v = line.split(":", 1)
        parsed[k.strip().lower()] = v.strip()
    return parsed, body.rstrip("\n")


schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("send-proof record revision mismatch")
if record.get("schema_version") != "external-contact-send-proof-record-v0.2":
    raise SystemExit("send-proof record schema version mismatch")
if record.get("send_proof_state") != "not-sent-no-proof":
    raise SystemExit("current send-proof record must stay not-sent-no-proof")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("send-proof record must have no live-floor effect")

packet = load(record["source_request_packet_ref"])
card = load(record["source_dispatch_authorization_card_ref"])
dossier = load(record["source_counterparty_selection_dossier_ref"])
execution = load(record["source_execution_record_ref"])
send_trace = load(record["source_send_trace_shell_ref"])
for label, obj in [("packet", packet), ("card", card), ("dossier", dossier), ("execution", execution), ("send-trace", send_trace)]:
    if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"send-proof {label} source is not current/no-floor")
if card.get("source_send_proof_record_ref") != RECORD_REL:
    raise SystemExit("dispatch authorization card is not bound to current send-proof record")
if execution.get("send_proof_record_ref") != RECORD_REL:
    raise SystemExit("execution record is not bound to current send-proof record")
if execution.get("mail_ready_draft_ref") != record.get("source_mail_ready_draft_ref"):
    raise SystemExit("execution record and send-proof record disagree on mail-ready draft ref")
if record.get("source_send_trace_shell_ref") != f"examples/external-contact-send-trace-shell-{REV}-no-transport.json":
    raise SystemExit("send-proof record is not bound to current send-trace shell")
if card.get("source_send_trace_shell_ref") != record.get("source_send_trace_shell_ref"):
    raise SystemExit("dispatch authorization card and send-proof disagree on send-trace shell")
if execution.get("send_trace_shell_ref") != record.get("source_send_trace_shell_ref"):
    raise SystemExit("execution record and send-proof disagree on send-trace shell")
if send_trace.get("send_trace_state") != "pre-dispatch-no-transport":
    raise SystemExit("send-proof must bind pre-dispatch/no-transport send-trace shell")
if send_trace.get("response_clock_guard", {}).get("clock_may_start_now") is not False:
    raise SystemExit("send-trace shell must not start response clock")

selected = record.get("selected_recipient", {})
card_selected = card.get("selected_candidate", {})
for key in ["candidate_id", "organization_name", "public_channel_locator", "channel_type", "public_source_url"]:
    if selected.get(key) != card_selected.get(key):
        raise SystemExit(f"send-proof selected recipient does not match authorization card: {key}")
for key in ["recipient_is_public_locator_only", "recipient_is_not_consent", "recipient_is_not_authority"]:
    if selected.get(key) is not True:
        raise SystemExit(f"send-proof recipient guard missing: {key}")

body = packet.get("outgoing_request", {}).get("body", "").strip()
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
draft_rel = record["source_mail_ready_draft_ref"]
draft_path = ROOT / draft_rel
if not draft_path.exists():
    raise SystemExit(f"send-proof mail-ready draft missing: {draft_rel}")
draft_bytes = draft_path.read_bytes()
draft_hash = hashlib.sha256(draft_bytes).hexdigest()
draft_text = draft_bytes.decode("utf-8")
headers, draft_body = parse_draft(draft_text)

binding = record.get("message_binding", {})
if binding.get("body_sha256") != body_hash:
    raise SystemExit("send-proof body hash does not match request packet")
if binding.get("mail_ready_draft_sha256") != draft_hash:
    raise SystemExit("send-proof mail-ready draft hash mismatch")
if card.get("message_binding", {}).get("mail_ready_draft_sha256") != draft_hash:
    raise SystemExit("authorization card mail-ready draft hash mismatch")
if card.get("message_binding", {}).get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("authorization card body hash mismatch")
if headers.get("to") != selected.get("public_channel_locator"):
    raise SystemExit("mail-ready draft To header does not match selected public channel")
if headers.get("subject") != packet.get("outgoing_request", {}).get("subject"):
    raise SystemExit("mail-ready draft Subject does not match request packet")
if draft_body.strip() != body:
    raise SystemExit("mail-ready draft body does not match request packet body")
if headers.get("x-ai-personhood-draft-state") != "NOT-SENT":
    raise SystemExit("mail-ready draft must be marked NOT-SENT")
if headers.get("x-ai-personhood-body-sha256") != body_hash:
    raise SystemExit("mail-ready draft body hash header mismatch")
for term in ["human_signature_missing", "sender_authority_missing", "raw_reply_vault_root_missing", "transport_proof_missing"]:
    if term not in headers.get("x-ai-personhood-send-blockers", ""):
        raise SystemExit(f"mail-ready draft missing send blocker: {term}")
if "draft_may_not_start_response_clock" not in headers.get("x-ai-personhood-clock-guard", ""):
    raise SystemExit("mail-ready draft missing response clock guard")

for key in [
    "request_packet_body_hash_matches",
    "authorization_card_body_hash_matches",
    "draft_to_header_matches_selected_public_channel",
    "draft_subject_matches_request_packet",
    "draft_body_matches_request_packet",
    "draft_headers_mark_not_sent",
    "draft_is_not_transport_proof",
]:
    if binding.get(key) is not True:
        raise SystemExit(f"send-proof message binding missing true guard: {key}")

draft_guard = record.get("draft_guard", {})
for key in ["mail_ready_draft_present", "mail_ready_draft_may_be_imported_by_human"]:
    if draft_guard.get(key) is not True:
        raise SystemExit(f"send-proof draft guard must be true: {key}")
for key in ["mail_ready_draft_may_be_treated_as_sent", "mail_ready_draft_may_start_response_clock", "mail_ready_draft_may_create_failed_gate_shell", "mail_ready_draft_may_create_custody_or_intake"]:
    if draft_guard.get(key) is not False:
        raise SystemExit(f"send-proof draft guard must be false: {key}")

send_event = record.get("send_event", {})
for key in ["sent_at", "sent_by_role", "transport_channel", "transport_proof_ref", "message_id_or_header_source_ref", "send_trace_public_shell_ref", "private_transport_trace_locator", "deadline_at"]:
    if send_event.get(key) is not None:
        raise SystemExit(f"not-sent send-proof record must keep {key}=null")
if send_event.get("transport_proof_present") is not False:
    raise SystemExit("not-sent send-proof record must keep transport_proof_present=false")
for key in ["send_event_may_create_receipt", "send_event_may_create_custody"]:
    if send_event.get(key) is not False:
        raise SystemExit(f"send event guard must be false: {key}")

required = " ".join(record.get("required_when_sent", [])).lower()
for term in ["authorization", "sender", "sent_at", "transport", "message", "private", "deadline", "acknowledgement", "send-trace", "message-id"]:
    if term not in required:
        raise SystemExit(f"send-proof required_when_sent missing term: {term}")

clock = record.get("response_clock_guard", {})
if clock.get("clock_may_start_now") is not False:
    raise SystemExit("send-proof record must not start clock now")
for key in ["clock_starts_only_after_sent_at_and_transport_proof", "deadline_must_be_computed_from_actual_sent_at", "auto_ack_routes_to_triage_not_response", "silence_is_not_waiver", "decline_is_not_adverse_inference"]:
    if clock.get(key) is not True:
        raise SystemExit(f"send-proof response clock guard missing: {key}")

for key, val in record.get("downstream_locks", {}).items():
    if val is not False:
        raise SystemExit(f"send-proof downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"send-proof record references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"send-proof record references missing surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-send-proof-record" not in fx.get("target_filings", []):
    raise SystemExit("send-proof fixture does not target send-proof record")
if fx.get("severity") != "critical":
    raise SystemExit("send-proof fixture must be critical")

subprocess.run([sys.executable, str(ROOT / "tools" / "render_external_contact_mail_ready_draft.py"), "--check-output"], check=True)

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["draft_guard"]["mail_ready_draft_may_be_treated_as_sent"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("send-proof schema failed to reject draft-as-sent")
    mut2 = copy.deepcopy(record)
    mut2["response_clock_guard"]["clock_may_start_now"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("send-proof schema failed to reject response clock start")
    mut3 = copy.deepcopy(record)
    mut3["send_event"]["transport_proof_present"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("send-proof schema failed to reject not-sent transport proof flag")
    mut4 = copy.deepcopy(record)
    mut4["downstream_locks"]["may_create_failed_gate_shell_now"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("send-proof schema failed to reject failed-gate shell from draft")

print("audit_external_contact_send_proof_record: OK")
