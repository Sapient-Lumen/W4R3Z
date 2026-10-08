#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CARD_REL = f"examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json"
SCHEMA_REL = "schemas/external-contact-dispatch-authorization-card.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-dispatch-authorization-card-unsigned-as-sent.json"

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
        raise SystemExit(f"{label} fails external-contact-dispatch-authorization-card.schema.json: {errors[0].message}")


schema = load(SCHEMA_REL)
card = load(CARD_REL)
validate(schema, card, CARD_REL)

if card.get("revision") != REV:
    raise SystemExit("dispatch authorization card revision mismatch")
if card.get("no_live_floor_effect") is not True:
    raise SystemExit("dispatch authorization card must have no live-floor effect")
if card.get("schema_version") != "external-contact-dispatch-authorization-card-v0.3":
    raise SystemExit("dispatch authorization card schema version mismatch")
if card.get("authorization_state") != "blocked-missing-signature-and-vault":
    raise SystemExit("current dispatch authorization card must remain blocked until signed and vault-selected")

packet_rel = card.get("source_request_packet_ref")
dossier_rel = card.get("source_counterparty_selection_dossier_ref")
execution_rel = card.get("source_execution_record_ref")
render_rel = card.get("source_rendered_message_ref")
mail_ready_rel = card.get("source_mail_ready_draft_ref")
send_proof_rel = card.get("source_send_proof_record_ref")
send_trace_rel = card.get("source_send_trace_shell_ref")
for rel in [packet_rel, dossier_rel, execution_rel, render_rel, mail_ready_rel, send_proof_rel, send_trace_rel]:
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"dispatch authorization card references missing surface: {rel}")

packet = load(packet_rel)
dossier = load(dossier_rel)
execution = load(execution_rel)
send_trace = load(send_trace_rel)
if packet.get("revision") != REV or dossier.get("revision") != REV or execution.get("revision") != REV or send_trace.get("revision") != REV:
    raise SystemExit("dispatch authorization card is not bound to current revision surfaces")
if packet.get("no_live_floor_effect") is not True or dossier.get("no_live_floor_effect") is not True or execution.get("no_live_floor_effect") is not True or send_trace.get("no_live_floor_effect") is not True:
    raise SystemExit("dispatch authorization card source surfaces must be no-floor")

body = packet.get("outgoing_request", {}).get("body", "").strip()
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
render_hash = hashlib.sha256((ROOT / render_rel).read_bytes()).hexdigest()
mail_ready_bytes = (ROOT / mail_ready_rel).read_bytes()
mail_ready_hash = hashlib.sha256(mail_ready_bytes).hexdigest()
binding = card.get("message_binding", {})
if binding.get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("dispatch authorization card body hash does not match request packet")
if binding.get("rendered_message_sha256") != render_hash:
    raise SystemExit("dispatch authorization card rendered message hash is stale")
if binding.get("mail_ready_draft_sha256") != mail_ready_hash:
    raise SystemExit("dispatch authorization card mail-ready draft hash is stale")
if binding.get("response_deadline_days") != packet.get("outgoing_request", {}).get("response_deadline_days"):
    raise SystemExit("dispatch authorization card deadline does not match request packet")
for key in ["body_hash_matches_request_packet", "deadline_matches_request_packet", "draft_is_not_sent", "mail_ready_draft_matches_body_and_recipient", "mail_ready_draft_is_not_transport_proof"]:
    if binding.get(key) is not True:
        raise SystemExit(f"dispatch authorization message binding missing true guard: {key}")
if binding.get("message_may_be_edited_after_authorization") is not False:
    raise SystemExit("dispatch authorization card must freeze message edits after authorization")

selected = card.get("selected_candidate", {})
rec_id = dossier.get("recommendation", {}).get("recommended_candidate_id")
if selected.get("candidate_id") != rec_id:
    raise SystemExit("dispatch authorization selected candidate is not dossier recommendation")
rec_cand = next((c for c in dossier.get("candidates", []) if c.get("candidate_id") == selected.get("candidate_id")), None)
if rec_cand is None or rec_cand.get("rank") != 1:
    raise SystemExit("dispatch authorization selected candidate is not rank-1 dossier candidate")
if selected.get("public_channel_locator") not in rec_cand.get("public_contact_locator", "") and selected.get("public_channel_locator") != rec_cand.get("public_contact_locator"):
    raise SystemExit("dispatch authorization public channel locator not bound to dossier candidate")
for key in ["selection_is_not_contact", "selection_is_not_consent", "selection_is_not_authority"]:
    if selected.get(key) is not True:
        raise SystemExit(f"dispatch authorization selected-candidate lock missing: {key}")
mail_text = mail_ready_bytes.decode("utf-8")
if f"To: {selected.get('public_channel_locator')}" not in mail_text:
    raise SystemExit("dispatch authorization mail-ready draft To header mismatch")
if f"Subject: {packet.get('outgoing_request', {}).get('subject')}" not in mail_text:
    raise SystemExit("dispatch authorization mail-ready draft Subject mismatch")
if "X-AI-Personhood-Draft-State: NOT-SENT" not in mail_text:
    raise SystemExit("dispatch authorization mail-ready draft lacks NOT-SENT header")
if "transport_proof_missing" not in mail_text or "draft_may_not_start_response_clock" not in mail_text:
    raise SystemExit("dispatch authorization mail-ready draft lacks transport/clock guard headers")
if send_trace.get("send_trace_state") != "pre-dispatch-no-transport":
    raise SystemExit("dispatch authorization card must bind a pre-dispatch/no-transport send-trace shell")
if send_trace.get("source_send_proof_record_ref") != send_proof_rel:
    raise SystemExit("send-trace shell is not bound to dispatch card send-proof record")
if send_trace.get("source_dispatch_authorization_card_ref") != CARD_REL:
    raise SystemExit("send-trace shell is not bound back to dispatch authorization card")
if send_trace.get("response_clock_guard", {}).get("clock_may_start_now") is not False:
    raise SystemExit("send-trace shell must not start response clock")

auth = card.get("human_authorization", {})
if any(auth.get(k) for k in ["human_authorizer_id", "authorizer_role", "signed_at"]):
    raise SystemExit("blocked dispatch authorization card must not contain signature identity or timestamp")
for key in ["exact_recipient_authorized", "sender_authority_attested", "conflict_review_accepted", "send_permitted_now"]:
    if auth.get(key) is not False:
        raise SystemExit(f"blocked dispatch authorization must keep {key}=false")
for code in ["human_signature_missing", "sender_authority_missing", "raw_reply_vault_root_missing"]:
    if code not in auth.get("blocker_codes", []):
        raise SystemExit(f"blocked dispatch authorization missing blocker: {code}")
for term in ["exact", "recipient", "sender", "vault", "transport", "custody", "live-floor"]:
    if term not in auth.get("required_signature_statement", "").lower():
        raise SystemExit(f"signature statement missing guard term: {term}")

vault = card.get("raw_reply_vault_precommit", {})
if vault.get("root_policy") != "outside-release-tree" or vault.get("public_release_may_include_raw_reply_bytes") is not False:
    raise SystemExit("dispatch authorization raw-reply vault policy unsafe")
if vault.get("root_selected_now") is not False:
    raise SystemExit("blocked dispatch authorization must not claim a selected raw-reply vault root")
if not str(vault.get("locator_prefix", "")).startswith("private-vault://"):
    raise SystemExit("dispatch authorization vault locator prefix must use private-vault://")
if vault.get("stage_tool") != "tools/stage_live_evidence_drop.py" or not (ROOT / vault.get("stage_tool", "")).exists():
    raise SystemExit("dispatch authorization card stage tool missing")
if vault.get("precommit_may_satisfy_custody_or_authority") is not False:
    raise SystemExit("dispatch authorization vault precommit must not satisfy custody or authority")

proof = card.get("transport_proof_acceptance_tests", {})
required_text = " ".join(proof.get("required_before_marking_sent", [])).lower()
for term in ["recipient", "sender", "timestamp", "body", "message", "transport", "deadline", "automated acknowledgement", "send-trace", "message-id"]:
    if term not in required_text:
        raise SystemExit(f"send-proof acceptance test missing term: {term}")
for key in ["reject_if_missing_any", "auto_ack_triage_required", "send_proof_is_not_receipt", "send_proof_is_not_custody", "send_trace_shell_required", "message_id_alone_rejected_as_response_clock"]:
    if proof.get(key) is not True:
        raise SystemExit(f"send-proof acceptance missing true guard: {key}")
if proof.get("all_present_now") is not False:
    raise SystemExit("send-proof acceptance test must record all_present_now=false")

clock = card.get("response_clock_guard", {})
if clock.get("clock_may_start_now") is not False or clock.get("no_response_shell_may_be_prepared_now") is not False:
    raise SystemExit("dispatch authorization card must not start clock or prepare no-response shell")
for key in ["clock_starts_only_after_sent_proof", "silence_is_not_waiver", "decline_is_not_adverse_inference"]:
    if clock.get(key) is not True:
        raise SystemExit(f"response clock guard missing true flag: {key}")
if clock.get("draft_or_authorization_card_may_start_clock") is not False:
    raise SystemExit("authorization card must not start response clock")

for key, value in card.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"dispatch authorization downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in card.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"dispatch authorization card references missing queue id: {qid}")
for rel in card.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"dispatch authorization card references missing surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-dispatch-authorization-card" not in fx.get("target_filings", []):
    raise SystemExit("dispatch authorization fixture does not target authorization card")
if fx.get("severity") != "critical":
    raise SystemExit("dispatch authorization fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(card)
    mut["downstream_locks"]["may_treat_card_as_dispatch"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("dispatch authorization schema failed to reject card-as-dispatch")
    mut2 = copy.deepcopy(card)
    mut2["response_clock_guard"]["clock_may_start_now"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("dispatch authorization schema failed to reject clock start")
    mut3 = copy.deepcopy(card)
    mut3["raw_reply_vault_precommit"]["public_release_may_include_raw_reply_bytes"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("dispatch authorization schema failed to reject raw reply publication")
    mut4 = copy.deepcopy(card)
    mut4["human_authorization"]["send_permitted_now"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("dispatch authorization schema failed to reject unsigned send permission")
    mut5 = copy.deepcopy(card)
    mut5["message_binding"]["mail_ready_draft_is_not_transport_proof"] = False
    if not list(validator.iter_errors(mut5)):
        raise SystemExit("dispatch authorization schema failed to reject mail-ready draft as transport proof")

print("audit_external_contact_dispatch_authorization_card: OK")
