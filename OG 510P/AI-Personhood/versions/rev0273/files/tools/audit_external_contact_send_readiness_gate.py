#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
GATE_REL = f"examples/external-contact-send-readiness-gate-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-send-readiness-gate.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-send-readiness-unsigned-as-sendable.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_bytes(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-send-readiness-gate.schema.json: {errors[0].message}")


schema = load_json(SCHEMA_REL)
gate = load_json(GATE_REL)
validate(schema, gate, GATE_REL)

if gate.get("revision") != REV:
    raise SystemExit("send-readiness gate revision mismatch")
if gate.get("no_live_floor_effect") is not True:
    raise SystemExit("send-readiness gate must have no live-floor effect")
if gate.get("gate_state") != "blocked-no-human-send":
    raise SystemExit("current send-readiness gate must remain blocked-no-human-send")

refs = gate.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"send-readiness source missing: {name}={rel}")

request = load_json(refs["request_packet"])
handoff = load_json(refs["send_branch_handoff"])
payload_manifest = load_json(refs["public_payload_manifest"])
card = load_json(refs["dispatch_authorization_card"])
send_proof = load_json(refs["send_proof_record"])
send_trace = load_json(refs["send_trace_shell"])
delivery = load_json(refs["delivery_status_record"])
precommit = load_json(refs["inbound_vault_precommit"])
capture = load_json(refs["inbound_capture_shell"])
triage = load_json(refs["response_triage_record"])
board = load_json(refs["operating_board"])
route_fit = load_json(refs["route_fit_review"])
transport_plan = load_json(refs["transport_capture_plan"])
conflict_review = load_json(refs["conflict_coercion_review"])
hash_dry_run = load_json(refs["hash_recompute_dry_run"])

for label, obj in [
    ("request", request),
    ("handoff", handoff),
    ("payload_manifest", payload_manifest),
    ("dispatch_card", card),
    ("send_proof", send_proof),
    ("send_trace", send_trace),
    ("delivery_status", delivery),
    ("inbound_precommit", precommit),
    ("inbound_capture", capture),
    ("response_triage", triage),
    ("operating_board", board),
    ("route_fit_review", route_fit),
    ("transport_capture_plan", transport_plan),
    ("conflict_coercion_review", conflict_review),
    ("hash_recompute_dry_run", hash_dry_run),
]:
    if obj.get("revision") != REV:
        raise SystemExit(f"send-readiness source revision mismatch: {label}")
    if obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"send-readiness source must be no-floor: {label}")

body = request.get("outgoing_request", {}).get("body", "").strip()
body_hash = sha_text(body)
mail_hash = sha_bytes(refs["mail_ready_draft"])
payload_hash = sha_bytes(refs["public_payload_manifest"])
mb = gate.get("message_binding", {})
if mb.get("body_sha256") != body_hash:
    raise SystemExit("send-readiness body hash mismatch")
if mb.get("body_word_count") != len(body.split()):
    raise SystemExit("send-readiness body word count mismatch")
if len(body.split()) > 260:
    raise SystemExit("send-readiness body exceeds first-contact word budget")
if mb.get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("send-readiness mail-ready hash mismatch")
if mb.get("public_payload_manifest_sha256") != payload_hash:
    raise SystemExit("send-readiness payload manifest hash mismatch")
if mb.get("public_payload_item_count") != len(payload_manifest.get("public_payload_items", [])):
    raise SystemExit("send-readiness payload item count mismatch")
if mb.get("subject") != request.get("outgoing_request", {}).get("subject"):
    raise SystemExit("send-readiness subject mismatch")
mail_text = (ROOT / refs["mail_ready_draft"]).read_text(encoding="utf-8")
if f"X-AI-Personhood-Body-SHA256: {body_hash}" not in mail_text:
    raise SystemExit("send-readiness mail-ready draft lacks current body hash header")
if body not in mail_text:
    raise SystemExit("send-readiness mail-ready draft body mismatch")
if "collaboration/routing inquiry" not in body or "not as an incident submission" not in body:
    raise SystemExit("send-readiness body must clarify RAIC/AIID route fit and non-incident-submission posture")

if route_fit.get("review_state") != "completed-limited-route-fit-no-authorization":
    raise SystemExit("send-readiness route-fit review is not completed/limited")
if route_fit.get("source_request_packet_ref") != refs["request_packet"]:
    raise SystemExit("send-readiness route-fit review not bound to request packet")
if route_fit.get("route_fit_findings", {}).get("fit_satisfied_for_current_draft") is not True:
    raise SystemExit("send-readiness route fit is not satisfied for current draft")
if route_fit.get("route_fit_findings", {}).get("route_fit_may_authorize_send") is not False:
    raise SystemExit("route-fit review must not authorize send")
if transport_plan.get("plan_state") != "ready-template-no-send-no-private-root":
    raise SystemExit("send-readiness transport capture plan must be ready template/no-send/no-private-root")
if transport_plan.get("source_refs", {}).get("request_packet") != refs["request_packet"]:
    raise SystemExit("transport capture plan not bound to request packet")
if transport_plan.get("source_refs", {}).get("send_trace_shell") != refs["send_trace_shell"]:
    raise SystemExit("transport capture plan not bound to send trace shell")
if transport_plan.get("public_release_policy", {}).get("plan_may_substitute_for_send_proof") is not False:
    raise SystemExit("transport capture plan must not substitute for send proof")
if conflict_review.get("review_state") != "completed-public-language-conflict-coercion-review-no-authorization":
    raise SystemExit("send-readiness conflict/coercion review is not completed/public-language/no-authorization")
if conflict_review.get("source_refs", {}).get("request_packet") != refs["request_packet"]:
    raise SystemExit("send-readiness conflict/coercion review not bound to request packet")
if conflict_review.get("review_scope", {}).get("may_authorize_send") is not False:
    raise SystemExit("conflict/coercion review must not authorize send")
if conflict_review.get("residual_blockers", {}).get("sender_authority_still_required") is not True:
    raise SystemExit("conflict/coercion review must leave sender authority required")
if hash_dry_run.get("dry_run_state") != "current-public-tree-hashes-recomputed-no-send":
    raise SystemExit("hash recompute dry-run is not current/no-send")
if hash_dry_run.get("send_time_policy", {}).get("dry_run_may_satisfy_send_time_recompute") is not False:
    raise SystemExit("hash recompute dry-run must not satisfy send-time recompute")
if hash_dry_run.get("computed_bindings", {}).get("body_sha256") != body_hash:
    raise SystemExit("hash recompute dry-run body hash mismatch")
if hash_dry_run.get("computed_bindings", {}).get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("hash recompute dry-run mail hash mismatch")
if hash_dry_run.get("computed_bindings", {}).get("public_payload_manifest_sha256") != payload_hash:
    raise SystemExit("hash recompute dry-run payload manifest hash mismatch")

# Cross-surface bindings already checked by their own audits, but keep the single-command operator guard direct.
if handoff.get("message_binding", {}).get("outgoing_body_sha256") != body_hash:
    raise SystemExit("send-readiness handoff body hash mismatch")
if handoff.get("message_binding", {}).get("public_payload_manifest_ref") != refs["public_payload_manifest"]:
    raise SystemExit("send-readiness handoff not bound to public payload manifest")
if payload_manifest.get("message_binding", {}).get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("send-readiness payload manifest body hash mismatch")
if payload_manifest.get("message_binding", {}).get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("send-readiness payload manifest mail hash mismatch")
if card.get("message_binding", {}).get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("send-readiness dispatch card body hash mismatch")
if card.get("message_binding", {}).get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("send-readiness dispatch card mail hash mismatch")
if send_proof.get("message_binding", {}).get("body_sha256") != body_hash:
    raise SystemExit("send-readiness send-proof body hash mismatch")
if send_proof.get("message_binding", {}).get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("send-readiness send-proof mail hash mismatch")
if send_trace.get("send_trace_state") != "pre-dispatch-no-transport":
    raise SystemExit("send-readiness requires pre-dispatch/no-transport send trace")
if delivery.get("delivery_status_state") != "pre-dispatch-no-delivery-status":
    raise SystemExit("send-readiness requires pre-dispatch/no-delivery-status delivery record")
if precommit.get("precommit_state") != "pre-dispatch-no-inbound":
    raise SystemExit("send-readiness requires pre-dispatch/no-inbound vault precommit state")
if capture.get("capture_state") != "pre-dispatch-no-inbound":
    raise SystemExit("send-readiness requires pre-dispatch/no-inbound capture shell")
if triage.get("triage_state") != "pre-dispatch-no-inbound":
    raise SystemExit("send-readiness requires pre-dispatch/no-inbound response triage")

required_blockers = {
    "human-signature",
    "sender-authority",
    "conflict-review",
    "public-locator-recheck",
    "route-fit-review",
    "private-vault-roots",
    "transport-proof-capture-plan",
    "payload-and-body-hash-recompute",
}
observed = {item.get("precondition_id") for item in gate.get("blocking_preconditions", [])}
missing = required_blockers - observed
if missing:
    raise SystemExit(f"send-readiness gate missing blockers: {sorted(missing)}")
for item in gate.get("blocking_preconditions", []):
    if item.get("required_before_send") is not True:
        raise SystemExit(f"send-readiness precondition must be required: {item.get('precondition_id')}")
    if item.get("satisfied_now") is True and not item.get("satisfied_by_ref"):
        raise SystemExit(f"satisfied send-readiness precondition lacks evidence ref: {item.get('precondition_id')}")

satisfied_ids = {item.get("precondition_id") for item in gate.get("blocking_preconditions", []) if item.get("satisfied_now") is True}
unsatisfied_ids = {item.get("precondition_id") for item in gate.get("blocking_preconditions", []) if item.get("satisfied_now") is False}
expected_satisfied = {"route-fit-review", "transport-proof-capture-plan", "conflict-review"}
expected_unsatisfied = required_blockers - expected_satisfied
if satisfied_ids != expected_satisfied:
    raise SystemExit(f"send-readiness satisfied blockers should be only {sorted(expected_satisfied)}, got {sorted(satisfied_ids)}")
if unsatisfied_ids != expected_unsatisfied:
    raise SystemExit(f"send-readiness unsatisfied blockers mismatch: {sorted(unsatisfied_ids)}")
summary = gate.get("blocker_resolution_summary", {})
if summary.get("satisfied_now_count") != len(satisfied_ids) or summary.get("unsatisfied_now_count") != len(unsatisfied_ids):
    raise SystemExit("send-readiness blocker resolution counts are stale")
if set(summary.get("satisfied_precondition_ids", [])) != satisfied_ids:
    raise SystemExit("send-readiness satisfied precondition summary mismatch")
if set(summary.get("unsatisfied_precondition_ids", [])) != unsatisfied_ids:
    raise SystemExit("send-readiness unsatisfied precondition summary mismatch")
if summary.get("gate_remains_blocked") is not True:
    raise SystemExit("send-readiness summary must keep gate blocked")

if gate.get("operator_next_step") != "human-send-with-proof-or-explicit-no-send-decision":
    raise SystemExit("send-readiness operator next step must be the branch decision")

capture_plan = gate.get("if_send_capture_plan", {})
for text in [" ".join(capture_plan.get(k, [])) for k in ["capture_before_clicking_send", "capture_immediately_after_send", "capture_before_reading_reply"]]:
    lower = text.lower()
    for term in ["hash", "vault", "transport"]:
        if term not in lower:
            raise SystemExit(f"send-readiness capture plan missing {term}: {text}")
if capture_plan.get("raw_locations_stay_outside_release_tree") is not True:
    raise SystemExit("send-readiness raw locations must stay outside release tree")
if capture_plan.get("public_release_may_publish_raw_transport_or_reply_bytes") is not False:
    raise SystemExit("send-readiness must forbid raw transport/reply publication")

classes = {item.get("class_id") for item in gate.get("if_reply_classification_order", [])}
needed_classes = {"dsn-or-bounce", "auto-ack-or-ticket", "human-decline-or-out-of-scope", "routing-referral", "conditional-retention", "substantive-review-willingness", "redacted-only", "protocol-or-tool-output"}
if not needed_classes.issubset(classes):
    raise SystemExit(f"send-readiness reply classification missing classes: {sorted(needed_classes - classes)}")
for item in gate.get("if_reply_classification_order", []):
    if item.get("may_create_custody_intake_import_or_floor") is not False:
        raise SystemExit(f"send-readiness reply class overclaims: {item.get('class_id')}")

active_entries = [entry for entry in load_json("FOLLOWTHROUGH-QUEUE.json").get("entries", []) if entry.get("state") in {"open", "advanced_not_closed"}]
if len(active_entries) != 7:
    raise SystemExit(f"send-readiness queue active count must remain 7, got {len(active_entries)}")
q = gate.get("queue_refactor_audit", {})
if q.get("active_queue_count_observed") != 7 or q.get("active_queue_count_required") != 7:
    raise SystemExit("send-readiness queue count fields must be 7")
if q.get("backlog_may_close_first_artifact_by_narrative") is not False:
    raise SystemExit("send-readiness must reject backlog closure by narrative")

for key, value in gate.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"send-readiness downstream lock must be false: {key}")
for rel in gate.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"send-readiness related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-send-readiness-gate" not in fixture.get("target_filings", []):
    raise SystemExit("send-readiness fixture does not target gate")
if fixture.get("severity") != "critical":
    raise SystemExit("send-readiness fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(gate)
    mut["blocker_resolution_summary"]["gate_remains_blocked"] = False
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject unblocked summary in blocked gate")
    mut2 = copy.deepcopy(gate)
    mut2["downstream_locks"]["may_start_response_clock"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject response-clock overclaim")
    mut3 = copy.deepcopy(gate)
    mut3["if_reply_classification_order"][0]["may_create_custody_intake_import_or_floor"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject reply class creating custody/intake/import/floor")

print("audit_external_contact_send_readiness_gate: OK")
