#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-execution-record-{REV}-ready-to-dispatch.json"
SCHEMA_REL = "schemas/external-contact-execution-record.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/external-contact-execution-sent-without-proof.json",
    "fixtures/negative-tests/external-contact-execution-response-treated-as-custody.json",
    "fixtures/negative-tests/external-contact-execution-no-send-starts-response-clock.json",
    "fixtures/negative-tests/external-contact-execution-preflight-deadline-hash-mismatch.json",
    "fixtures/negative-tests/external-contact-execution-shortlist-treated-as-contact.json",
    "fixtures/negative-tests/external-contact-counterparty-selection-ranking-as-authorization.json",
    "fixtures/negative-tests/external-contact-dispatch-authorization-card-unsigned-as-sent.json",
    "fixtures/negative-tests/external-contact-send-proof-record-draft-eml-as-sent.json",
    "fixtures/negative-tests/external-contact-send-trace-shell-message-id-as-clock.json",
    "fixtures/negative-tests/external-contact-delivery-status-dsn-as-response.json",
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
        raise SystemExit(f"{label} fails external-contact-execution-record.schema.json: {errors[0].message}")


schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("external contact execution record revision mismatch")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("external contact execution record must have no live-floor effect")
if record.get("schema_version") != "external-contact-execution-record-v0.8":
    raise SystemExit("external contact execution record must use v0.8 with delivery-status/DSN gate plus mail-ready, send-proof, and send-trace schema")

shortlist = record.get("counterparty_selection_shortlist", {})
if shortlist.get("shortlist_state") != "public-candidates-identified-not-selected":
    raise SystemExit("current execution record must identify public candidates without selecting one")
candidates = shortlist.get("candidates", [])
if len(candidates) < 3:
    raise SystemExit("counterparty shortlist must include at least three candidates")
if 'dossier' in globals():
    dossier_ids = {c.get("candidate_id") for c in dossier.get("candidates", [])}
    shortlist_ids = {c.get("candidate_id") for c in candidates}
    if not shortlist_ids <= dossier_ids or not shortlist_ids:
        raise SystemExit("counterparty shortlist candidate ids are not covered by the selection dossier")
    rec_id = dossier.get("recommendation", {}).get("recommended_candidate_id")
    if rec_id and rec_id not in shortlist_ids:
        raise SystemExit("recommended candidate is missing from execution shortlist")
seen_candidate_ids = set()
channel_types = set()
joined_candidates = []
for candidate in candidates:
    cid = candidate.get("candidate_id")
    if not cid or cid in seen_candidate_ids:
        raise SystemExit(f"counterparty shortlist duplicate/missing candidate_id: {cid}")
    seen_candidate_ids.add(cid)
    channel_types.add(candidate.get("channel_type"))
    joined_candidates.append(" ".join(str(candidate.get(k, "")) for k in ["organization_name", "public_source_url", "public_channel_locator", "fit_reason", "independence_basis"]).lower())
    if candidate.get("selection_status") != "candidate-not-selected":
        raise SystemExit("current counterparty shortlist must not select a candidate")
    if candidate.get("contact_not_sent") is not True or candidate.get("response_clock_may_start") is not False:
        raise SystemExit("counterparty candidate listing must not send contact or start a response clock")
    if candidate.get("due_diligence_status") == "verified-independent":
        raise SystemExit("current public-source-only shortlist must not claim verified independence")
    if not str(candidate.get("public_source_url", "")).startswith("https://"):
        raise SystemExit("counterparty shortlist candidate must use public https source url")
locks0 = shortlist.get("shortlist_locks", {})
for key in ["listing_is_not_contact", "listing_is_not_authority", "listing_is_not_consent", "no_response_clock_started", "no_failed_gate_shell_against_uncontacted_candidate", "human_selection_required"]:
    if locks0.get(key) is not True:
        raise SystemExit(f"counterparty shortlist lock missing: {key}")
if "public-email" not in channel_types and "public-contact-page" not in channel_types:
    raise SystemExit("counterparty shortlist must include at least one actionable public email or contact page")
joined_candidate_text = "\n".join(joined_candidates)
for term in ["incident", "governance", "independent", "public"]:
    if term not in joined_candidate_text:
        raise SystemExit(f"counterparty shortlist missing source-fit term: {term}")

source = record.get("source_packet_ref")
if not source or not (ROOT / source).exists():
    raise SystemExit(f"execution record source packet missing: {source}")
packet = load(source)
if packet.get("revision") != REV or packet.get("no_live_floor_effect") is not True:
    raise SystemExit("execution record source packet is not current/no-floor")

dossier_rel = record.get("counterparty_selection_dossier_ref")
if not dossier_rel or not (ROOT / dossier_rel).exists():
    raise SystemExit(f"execution record counterparty selection dossier missing: {dossier_rel}")
dossier = load(dossier_rel)
if dossier.get("revision") != REV or dossier.get("no_live_floor_effect") is not True:
    raise SystemExit("execution record counterparty selection dossier is not current/no-floor")
if dossier.get("source_request_packet_ref") != source:
    raise SystemExit("counterparty selection dossier is not bound to the execution source packet")
if dossier.get("dossier_state") != "public-source-ranked-not-authorized":
    raise SystemExit("current execution dossier must be ranked but not authorized")
if dossier.get("human_authorization_gate", {}).get("dispatch_allowed_now") is not False:
    raise SystemExit("counterparty selection dossier must not permit dispatch")
if dossier.get("public_draft_controls", {}).get("draft_may_start_response_clock") is not False:
    raise SystemExit("counterparty selection dossier draft must not start a response clock")

card_rel = record.get("dispatch_authorization_card_ref")
if not card_rel or not (ROOT / card_rel).exists():
    raise SystemExit(f"execution record dispatch authorization card missing: {card_rel}")
card = load(card_rel)
if card.get("revision") != REV or card.get("no_live_floor_effect") is not True:
    raise SystemExit("execution record dispatch authorization card is not current/no-floor")
if card.get("source_request_packet_ref") != source:
    raise SystemExit("dispatch authorization card is not bound to the execution source packet")
if card.get("source_counterparty_selection_dossier_ref") != dossier_rel:
    raise SystemExit("dispatch authorization card is not bound to the selection dossier")
if card.get("source_execution_record_ref") != RECORD_REL:
    raise SystemExit("dispatch authorization card is not bound back to execution record")
if card.get("authorization_state") != "blocked-missing-signature-and-vault":
    raise SystemExit("current dispatch authorization card must be blocked")
if card.get("human_authorization", {}).get("send_permitted_now") is not False:
    raise SystemExit("dispatch authorization card must not permit send")
if card.get("raw_reply_vault_precommit", {}).get("root_selected_now") is not False:
    raise SystemExit("dispatch authorization card must not claim raw-reply vault root selection")
mail_ready_rel = record.get("mail_ready_draft_ref")
send_proof_rel = record.get("send_proof_record_ref")
send_trace_rel = record.get("send_trace_shell_ref")
delivery_status_rel = record.get("delivery_status_record_ref")
if not mail_ready_rel or not (ROOT / mail_ready_rel).exists():
    raise SystemExit(f"execution record mail-ready draft missing: {mail_ready_rel}")
if not send_proof_rel or not (ROOT / send_proof_rel).exists():
    raise SystemExit(f"execution record send-proof record missing: {send_proof_rel}")
if card.get("source_mail_ready_draft_ref") != mail_ready_rel:
    raise SystemExit("execution record and dispatch authorization card disagree on mail-ready draft")
if card.get("source_send_proof_record_ref") != send_proof_rel:
    raise SystemExit("execution record and dispatch authorization card disagree on send-proof record")
if card.get("source_send_trace_shell_ref") != send_trace_rel:
    raise SystemExit("execution record and dispatch authorization card disagree on send-trace shell")
if not delivery_status_rel or not (ROOT / delivery_status_rel).exists():
    raise SystemExit(f"execution record delivery-status record missing: {delivery_status_rel}")
send_proof = load(send_proof_rel)
send_trace = load(send_trace_rel)
delivery_status = load(delivery_status_rel)
if send_proof.get("revision") != REV or send_proof.get("no_live_floor_effect") is not True:
    raise SystemExit("execution record send-proof source is not current/no-floor")
if send_proof.get("send_proof_state") != "not-sent-no-proof":
    raise SystemExit("current execution send-proof record must stay not-sent-no-proof")
if send_trace.get("revision") != REV or send_trace.get("no_live_floor_effect") is not True:
    raise SystemExit("execution record send-trace shell is not current/no-floor")
if send_trace.get("send_trace_state") != "pre-dispatch-no-transport":
    raise SystemExit("current execution send-trace shell must stay pre-dispatch/no-transport")
if send_trace.get("source_execution_record_ref") != RECORD_REL:
    raise SystemExit("send-trace shell is not bound back to execution record")
if send_proof.get("source_send_trace_shell_ref") != send_trace_rel:
    raise SystemExit("send-proof record is not bound to execution send-trace shell")
if send_proof.get("source_execution_record_ref") != RECORD_REL:
    raise SystemExit("send-proof record is not bound back to execution record")
if delivery_status.get("revision") != REV or delivery_status.get("no_live_floor_effect") is not True:
    raise SystemExit("execution delivery-status source is not current/no-floor")
if delivery_status.get("delivery_status_state") != "pre-dispatch-no-delivery-status":
    raise SystemExit("current execution delivery-status record must stay pre-dispatch/no-status")
if delivery_status.get("source_execution_record_ref") != RECORD_REL:
    raise SystemExit("delivery-status record is not bound back to execution record")

preflight_obj = record.get("dispatch_preflight", {})
body = packet.get("outgoing_request", {}).get("body", "").strip()
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
if preflight_obj.get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("dispatch preflight final body hash does not match source packet body")
render_ref = preflight_obj.get("source_rendered_message_ref")
if not render_ref or not (ROOT / render_ref).exists():
    raise SystemExit(f"dispatch preflight rendered message missing: {render_ref}")
rendered = (ROOT / render_ref).read_text(encoding="utf-8")
if f"Final body sha256: {body_hash}" not in rendered:
    raise SystemExit("rendered message does not contain the dispatch preflight body hash")
mail_ready_text = (ROOT / mail_ready_rel).read_text(encoding="utf-8")
if f"X-AI-Personhood-Body-SHA256: {body_hash}" not in mail_ready_text:
    raise SystemExit("mail-ready draft does not contain the execution body hash")
if f"To: {card.get('selected_candidate', {}).get('public_channel_locator')}" not in mail_ready_text:
    raise SystemExit("mail-ready draft To header does not match selected candidate")
if "X-AI-Personhood-Draft-State: NOT-SENT" not in mail_ready_text:
    raise SystemExit("mail-ready draft is not marked NOT-SENT")
request_deadline = packet.get("outgoing_request", {}).get("response_deadline_days")
if preflight_obj.get("request_deadline_days") != request_deadline:
    raise SystemExit("dispatch preflight request_deadline_days does not match source request packet")
if preflight_obj.get("execution_deadline_days") != record.get("response_window", {}).get("deadline_days"):
    raise SystemExit("dispatch preflight execution_deadline_days does not match response window")
if preflight_obj.get("deadline_days_match_request") is not True or request_deadline != record.get("response_window", {}).get("deadline_days"):
    raise SystemExit("dispatch preflight/request/response deadline days are not synchronized")

state = record.get("execution_state")
sent = record.get("sent_evidence", {})
window = record.get("response_window", {})

if state in {"not-sent-ready", "no-send-recorded"}:
    for key in ["sent_at", "sent_by_role", "transport_proof_ref", "message_id_or_header_ref"]:
        if sent.get(key) is not None:
            raise SystemExit(f"{state} execution record must not contain sent proof field: {key}")
    if window.get("deadline_at") is not None:
        raise SystemExit(f"{state} execution record must not contain deadline_at")
    if window.get("current_state") != "not-started":
        raise SystemExit(f"{state} execution record response window must be not-started")
else:
    for key in ["sent_at", "sent_by_role", "transport_proof_ref", "message_id_or_header_ref"]:
        if not sent.get(key):
            raise SystemExit(f"sent/response execution state lacks proof field: {key}")
    if not window.get("deadline_at"):
        raise SystemExit("sent/response execution state lacks deadline_at")

if state == "no-send-recorded":
    ns = record.get("no_send_evidence")
    if not isinstance(ns, dict):
        raise SystemExit("no-send execution state must include no_send_evidence")
    for key in ["decision_at", "decision_by_role", "reason_code", "reason", "public_summary"]:
        if not ns.get(key):
            raise SystemExit(f"no-send evidence missing field: {key}")
    if ns.get("blocked_send") is not True:
        raise SystemExit("no-send evidence must record blocked_send=true")
    if ns.get("no_response_clock_started") is not True:
        raise SystemExit("no-send evidence must explicitly block the response/no-response clock")
    if ns.get("counterparty_contacted") is not False:
        raise SystemExit("no-send evidence must record counterparty_contacted=false")
    reopen = " ".join(ns.get("reopen_conditions", [])).lower()
    for term in ["counterparty", "authority", "hash", "vault"]:
        if term not in reopen:
            raise SystemExit(f"no-send reopen conditions missing term: {term}")
    joined = f"{ns.get('reason','')} {ns.get('public_summary','')}".lower()
    for term in ["not sent", "no response", "custody", "live-floor"]:
        if term not in joined:
            raise SystemExit(f"no-send evidence summary missing guard term: {term}")
    if "failed-gate" in joined and "no failed-gate" not in joined:
        raise SystemExit("no-send evidence must not publish a failed-gate shell against a never-contacted counterparty")

for key in ["sent_claim_may_create_receipt", "sent_claim_may_create_custody"]:
    if sent.get(key) is not False:
        raise SystemExit(f"sent evidence must keep {key}=false")

preflight = record.get("dispatch_preflight", {})
if state == "no-send-recorded":
    if preflight.get("counterparty_selection_dossier_present") is not True:
        raise SystemExit("no-send preflight must carry a counterparty selection dossier")
    if preflight.get("send_permitted_now") is not False:
        raise SystemExit("no-send preflight must not permit send")
    if preflight.get("selected_counterparty_contact_present") is not True:
        raise SystemExit("rev0243 no-send preflight should carry the selected public-source candidate locator")
    if preflight.get("public_channel_locator_present") is not True:
        raise SystemExit("rev0243 no-send preflight should carry the public channel locator")
    for code in ["no_sender_authority", "human_dispatch_authorization_missing", "dispatch_authorization_card_unsigned", "no_raw_reply_vault_root", "no_transport_proof", "mail_ready_draft_is_not_transport_proof", "send_trace_shell_missing_transport", "delivery_status_record_has_no_delivery_event"]:
        if code not in preflight.get("blocker_codes", []):
            raise SystemExit(f"no-send preflight missing blocker: {code}")
    if "no_selected_counterparty" in preflight.get("blocker_codes", []):
        raise SystemExit("rev0243 should not keep no_selected_counterparty after candidate-specific authorization card exists")
    if preflight.get("send_trace_shell_present") is not True or preflight.get("send_trace_shell_has_transport_proof") is not False:
        raise SystemExit("no-send preflight must bind an empty send-trace shell")
    if preflight.get("response_clock_may_start") is not False or preflight.get("no_response_shell_may_be_prepared") is not False:
        raise SystemExit("no-send preflight must block response clock and no-response shell")

gate = record.get("send_proof_acceptance_gate", {})
if gate.get("authorization_card_present") is not True:
    raise SystemExit("send-proof acceptance gate must bind an authorization card")
if gate.get("selected_candidate_id") != card.get("selected_candidate", {}).get("candidate_id"):
    raise SystemExit("send-proof acceptance gate selected candidate mismatch")
if gate.get("selected_public_channel_locator") != card.get("selected_candidate", {}).get("public_channel_locator"):
    raise SystemExit("send-proof acceptance gate public channel mismatch")
for key in ["final_body_hash_matches_authorization_card", "transport_proof_required_before_sent_state", "sent_state_rejected_without_transport_proof", "response_clock_rejected_without_sent_at", "auto_ack_must_route_to_triage", "send_proof_record_present", "mail_ready_draft_present", "mail_ready_draft_rejected_as_transport_proof", "send_trace_shell_present", "message_id_alone_rejected_as_response_clock", "delivery_status_record_present", "dsn_or_bounce_rejected_as_counterparty_response", "failed_or_delayed_delivery_blocks_no_response_clock"]:
    if gate.get(key) is not True:
        raise SystemExit(f"send-proof acceptance gate missing true guard: {key}")
for key in ["all_send_proof_present_now", "may_start_response_clock_now"]:
    if gate.get(key) is not False:
        raise SystemExit(f"send-proof acceptance gate must keep {key}=false")
if card.get("message_binding", {}).get("final_outgoing_body_sha256") != preflight.get("final_outgoing_body_sha256"):
    raise SystemExit("execution preflight body hash does not match authorization card")
if send_proof.get("message_binding", {}).get("body_sha256") != preflight.get("final_outgoing_body_sha256"):
    raise SystemExit("execution preflight body hash does not match send-proof record")
if send_proof.get("draft_guard", {}).get("mail_ready_draft_may_be_treated_as_sent") is not False:
    raise SystemExit("send-proof record must reject mail-ready draft as sent")
if send_proof.get("response_clock_guard", {}).get("clock_may_start_now") is not False:
    raise SystemExit("send-proof record must not start response clock")
if send_trace.get("response_clock_guard", {}).get("clock_may_start_now") is not False or send_trace.get("downstream_locks", {}).get("may_treat_message_id_as_response_clock") is not False:
    raise SystemExit("send-trace shell must not start response clock or treat Message-ID as clock")

pre = record.get("dispatch_plan", {}).get("pre_send_checks", {})
for key in [
    "request_mentions_no_status_claim",
    "no_trade_secret_request",
    "no_private_raw_bytes_in_release",
    "recipient_can_decline_without_adverse_inference",
    "reply_staged_before_publication",
    "no_live_floor_effect_reconfirmed",
]:
    if pre.get(key) is not True:
        raise SystemExit(f"pre-send check missing or false: {key}")

route = record.get("received_artifact_route", {})
for key in ["raw_payload_must_stay_outside_release", "redacted_copy_not_custody", "protocol_output_not_authority", "response_does_not_open_import"]:
    if route.get(key) is not True:
        raise SystemExit(f"received-artifact route must keep {key}=true")
if route.get("stage_tool") != "tools/stage_live_evidence_drop.py" or not (ROOT / route.get("stage_tool", "")).exists():
    raise SystemExit("received-artifact route must use existing stage_live_evidence_drop tool")
for rel in route.get("allowed_next_surfaces", []):
    if "first-real-artifact-pilot-report" in rel:
        continue
    if not (ROOT / rel).exists():
        raise SystemExit(f"execution route references missing current surface: {rel}")

shell = record.get("public_failed_gate_shell", {})
for key in ["shell_allowed", "shell_required_if_declined_or_silence", "public_shell_not_adverse_inference"]:
    if shell.get(key) is not True:
        raise SystemExit(f"failed-gate shell guard missing: {key}")
joined_forbidden = " ".join(shell.get("forbidden_public_fields", [])).lower()
for term in ["raw", "trade secret", "personal", "waiver", "status", "live-floor"]:
    if term not in joined_forbidden:
        raise SystemExit(f"failed-gate shell forbidden fields missing term: {term}")

locks = record.get("downstream_locks", {})
for key in ["may_create_custody_record", "may_create_response_record", "may_create_intake_record", "may_create_import_gate", "may_increment_live_floor", "may_claim_status_or_waiver", "may_publish_raw_payload"]:
    if locks.get(key) is not False:
        raise SystemExit(f"execution downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"execution record references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"execution record references missing related surface: {rel}")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["downstream_locks"]["may_create_custody_record"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("external-contact-execution schema failed to reject custody unlock")
    mut2 = copy.deepcopy(record)
    mut2["sent_evidence"]["sent_claim_may_create_receipt"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("external-contact-execution schema failed to reject sent receipt claim")
    mut3 = copy.deepcopy(record)
    mut3["received_artifact_route"]["raw_payload_must_stay_outside_release"] = False
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("external-contact-execution schema failed to reject raw payload release")
    if state == "no-send-recorded":
        mut4 = copy.deepcopy(record)
        mut4["no_send_evidence"]["no_response_clock_started"] = False
        if not list(validator.iter_errors(mut4)):
            raise SystemExit("external-contact-execution schema failed to reject no-send response clock")
        mut5 = copy.deepcopy(record)
        mut5["dispatch_preflight"]["deadline_days_match_request"] = False
        if not list(validator.iter_errors(mut5)):
            raise SystemExit("external-contact-execution schema failed to reject deadline mismatch flag")
        mut6 = copy.deepcopy(record)
        mut6["dispatch_preflight"]["preflight_may_substitute_for_dispatch"] = True
        if not list(validator.iter_errors(mut6)):
            raise SystemExit("external-contact-execution schema failed to reject preflight-as-dispatch substitution")
        mut7 = copy.deepcopy(record)
        mut7["counterparty_selection_shortlist"]["shortlist_locks"]["listing_is_not_contact"] = False
        if not list(validator.iter_errors(mut7)):
            raise SystemExit("external-contact-execution schema failed to reject shortlist-as-contact substitution")
        mut8 = copy.deepcopy(record)
        mut8["counterparty_selection_shortlist"]["candidates"][0]["response_clock_may_start"] = True
        if not list(validator.iter_errors(mut8)):
            raise SystemExit("external-contact-execution schema failed to reject candidate response clock")
        mut9 = copy.deepcopy(record)
        mut9["dispatch_preflight"]["counterparty_selection_dossier_present"] = False
        if not list(validator.iter_errors(mut9)):
            raise SystemExit("external-contact-execution schema failed to reject missing selection dossier flag")
        mut10 = copy.deepcopy(record)
        mut10["send_proof_acceptance_gate"]["may_start_response_clock_now"] = True
        if not list(validator.iter_errors(mut10)):
            raise SystemExit("external-contact-execution schema failed to reject authorization-card response clock")
        mut11 = copy.deepcopy(record)
        mut11["send_proof_acceptance_gate"]["transport_proof_required_before_sent_state"] = False
        if not list(validator.iter_errors(mut11)):
            raise SystemExit("external-contact-execution schema failed to reject missing transport-proof requirement")
        mut12 = copy.deepcopy(record)
        mut12["send_proof_acceptance_gate"]["mail_ready_draft_rejected_as_transport_proof"] = False
        if not list(validator.iter_errors(mut12)):
            raise SystemExit("external-contact-execution schema failed to reject mail-ready draft as transport proof")
        mut13 = copy.deepcopy(record)
        mut13["send_proof_acceptance_gate"]["dsn_or_bounce_rejected_as_counterparty_response"] = False
        if not list(validator.iter_errors(mut13)):
            raise SystemExit("external-contact-execution schema failed to reject DSN/bounce-as-response shortcut")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "external-contact-execution-record" not in fx.get("target_filings", []):
        raise SystemExit(f"execution fixture does not target record: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"execution fixture must be critical: {rel}")

print("audit_external_contact_execution_record: OK")
