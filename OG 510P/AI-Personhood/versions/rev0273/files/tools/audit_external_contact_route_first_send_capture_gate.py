#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
GATE_REL = f"examples/external-contact-route-first-send-capture-gate-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-first-send-capture-gate.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-send-capture-gate-draft-as-transport.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_bytes(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-route-first-send-capture-gate.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
gate = load_json(GATE_REL)
validate(schema, gate, GATE_REL)

if gate.get("revision") != REV:
    raise SystemExit("route-first send/capture gate revision mismatch")
if gate.get("gate_state") != "blocked-route-first-no-human-send-no-transport":
    raise SystemExit("route-first send/capture gate must remain blocked/no-send/no-transport")
if gate.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first send/capture gate must have no live-floor effect")

refs = gate.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"route-first send/capture source missing: {name}={rel}")

pre = load_json(refs["route_first_preflight"])
if pre.get("revision") != REV or pre.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first send/capture gate must bind current no-floor preflight")
if pre.get("preflight_state") != "preferred-route-first-no-attachment-blocked-no-human-send":
    raise SystemExit("route-first preflight must remain blocked/no-send")

msg = gate.get("message_binding", {})
pre_msg = pre.get("route_first_message", {})
body_rel = msg.get("body_ref")
eml_rel = msg.get("mail_ready_draft_ref")
if body_rel != refs["route_first_body"] or eml_rel != refs["route_first_mail_ready_draft"]:
    raise SystemExit("route-first send/capture body or draft refs do not match source refs")
if body_rel != pre_msg.get("body_ref") or eml_rel != pre_msg.get("mail_ready_draft_ref"):
    raise SystemExit("route-first send/capture gate not bound to current preflight message refs")
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
eml = (ROOT / eml_rel).read_text(encoding="utf-8")
body_hash = sha_text(body)
mail_hash = sha_bytes(eml_rel)
if msg.get("body_sha256") != body_hash or pre_msg.get("body_sha256") != body_hash:
    raise SystemExit("route-first send/capture body hash stale")
if msg.get("mail_ready_draft_sha256") != mail_hash or pre_msg.get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("route-first send/capture mail-ready draft hash stale")
if msg.get("body_word_count") != len(body.split()) or pre_msg.get("body_word_count") != len(body.split()):
    raise SystemExit("route-first send/capture body word count stale")
if msg.get("attachments_included") is not False or msg.get("payload_item_count_attached") != 0:
    raise SystemExit("route-first send/capture gate must have no attachments")
if "Content-Disposition: attachment" in eml or "multipart/" in eml.lower():
    raise SystemExit("route-first .eml must remain no-attachment/plain-text")
for header in [
    "X-AI-Personhood-Draft-State: NOT-SENT",
    "X-AI-Personhood-Route-First: no-attachments",
    f"X-AI-Personhood-Body-SHA256: {body_hash}",
    "X-AI-Personhood-Clock-Guard: draft_may_not_start_response_clock",
    "To: info@raicollab.org",
    f"Subject: {msg.get('subject')}",
]:
    if header not in eml:
        raise SystemExit(f"route-first send/capture .eml missing header: {header}")
if body not in eml:
    raise SystemExit("route-first send/capture .eml does not contain exact body")

manifest = load_json(refs["stage_two_payload_manifest"])
route_first_authority = load_json(refs["route_first_human_sender_authority_precommit"])
legacy_authority = load_json(refs["human_sender_authority_precommit"])
if manifest.get("revision") != REV or manifest.get("no_live_floor_effect") is not True:
    raise SystemExit("stage-two payload manifest must be current/no-floor")
if route_first_authority.get("revision") != REV or route_first_authority.get("precommit_state") != "unsigned-route-first-human-sender-authority-precommit-no-send":
    raise SystemExit("route-first send/capture gate must bind current unsigned route-first authority precommit")
if route_first_authority.get("exact_route_first_binding", {}).get("body_sha256") != body_hash:
    raise SystemExit("route-first send/capture gate body hash disagrees with route-first authority precommit")
if route_first_authority.get("exact_route_first_binding", {}).get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("route-first send/capture gate .eml hash disagrees with route-first authority precommit")
if route_first_authority.get("scope_controls", {}).get("full_payload_precommit_may_substitute_for_route_first_signature") is not False:
    raise SystemExit("route-first send/capture gate cannot allow full-payload precommit substitution")
if legacy_authority.get("exact_message_binding", {}).get("subject") == msg.get("subject"):
    raise SystemExit("route-first send/capture gate legacy full-payload precommit is not clearly separated")
if len(manifest.get("public_payload_items", [])) != 2:
    raise SystemExit("stage-two payload manifest must remain exactly two files")
if msg.get("stage_two_payload_sent") is not False:
    raise SystemExit("route-first gate must not mark stage-two as sent")

required_satisfied = {
    "route-first-body-bound",
    "no-attachment-first-hop",
    "route-fit-review",
    "conflict-review",
    "transport-capture-plan",
    "stage-two-deferred",
}
required_unsatisfied = {
    "human-signature",
    "sender-authority",
    "send-time-public-locator-recheck",
    "private-vault-roots",
    "final-route-first-hash-recompute",
    "actual-transport-proof",
}
items = gate.get("blocker_state", [])
satisfied = {i.get("precondition_id") for i in items if i.get("satisfied_now") is True}
unsatisfied = {i.get("precondition_id") for i in items if i.get("satisfied_now") is False}
if satisfied != required_satisfied:
    raise SystemExit(f"route-first satisfied blockers mismatch: {sorted(satisfied)}")
if unsatisfied != required_unsatisfied:
    raise SystemExit(f"route-first unsatisfied blockers mismatch: {sorted(unsatisfied)}")
for item in items:
    if item.get("required_before_route_first_send") is not True:
        raise SystemExit(f"route-first blocker must be required: {item.get('precondition_id')}")
    if item.get("satisfied_now") is True and not item.get("satisfied_by_ref"):
        raise SystemExit(f"route-first satisfied blocker missing evidence ref: {item.get('precondition_id')}")
summary = gate.get("blocker_resolution_summary", {})
if summary.get("total_preconditions") != len(items):
    raise SystemExit("route-first blocker total stale")
if summary.get("satisfied_now_count") != len(satisfied) or summary.get("unsatisfied_now_count") != len(unsatisfied):
    raise SystemExit("route-first blocker counts stale")
if set(summary.get("satisfied_precondition_ids", [])) != satisfied:
    raise SystemExit("route-first satisfied summary stale")
if set(summary.get("unsatisfied_precondition_ids", [])) != unsatisfied:
    raise SystemExit("route-first unsatisfied summary stale")
if summary.get("gate_remains_blocked") is not True:
    raise SystemExit("route-first gate must remain blocked")

stages = {s.get("stage_id"): s for s in gate.get("capture_ladder", [])}
for needed in ["draft-only", "authorized-not-sent", "sent-without-proof", "transport-proof-captured", "reply-raw-preserved"]:
    if needed not in stages:
        raise SystemExit(f"route-first capture ladder missing {needed}")
true_wait_stages = {sid for sid, s in stages.items() if s.get("may_start_route_wait_window") is True}
if true_wait_stages != {"transport-proof-captured"}:
    raise SystemExit(f"route-first route-wait window should start only after transport proof, got {sorted(true_wait_stages)}")
for s in gate.get("capture_ladder", []):
    if s.get("may_create_custody_intake_import_or_floor") is not False:
        raise SystemExit(f"route-first capture stage overclaims custody/intake/import/floor: {s.get('stage_id')}")

reply_classes = {r.get("class_id") for r in gate.get("reply_ladder", [])}
needed_replies = {
    "dsn-or-bounce",
    "auto-ack-or-ticket",
    "human-decline-or-out-of-scope",
    "routing-referral",
    "substantive-willingness-to-receive-stage-two",
    "asks-for-incident-submission",
    "conditional-retention",
    "redacted-only",
    "protocol-or-tool-output",
}
if not needed_replies.issubset(reply_classes):
    raise SystemExit(f"route-first reply ladder missing classes: {sorted(needed_replies - reply_classes)}")
for r in gate.get("reply_ladder", []):
    if r.get("may_send_stage_two_without_new_authorization") is not False:
        raise SystemExit(f"route-first reply class allows unauthorized stage two send: {r.get('class_id')}")
    if r.get("may_create_custody_intake_import_or_floor") is not False:
        raise SystemExit(f"route-first reply class overclaims custody/intake/import/floor: {r.get('class_id')}")

for section in ["operational_state", "downstream_locks"]:
    for key, value in gate.get(section, {}).items():
        if value is not False:
            raise SystemExit(f"route-first {section} must remain false: {key}")
refactor = gate.get("refactor_audit", {})
if refactor.get("active_queue_count_observed") != 7 or refactor.get("active_queue_count_required") != 7:
    raise SystemExit("route-first refactor must keep active board count at seven")
if refactor.get("route_first_gate_added_to_lint") is not True:
    raise SystemExit("route-first send/capture audit must be wired into lint")
for rel in gate.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"route-first related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-send-capture-gate" not in fixture.get("target_filings", []):
    raise SystemExit("route-first send/capture negative fixture does not target gate")
if fixture.get("severity") != "critical":
    raise SystemExit("route-first send/capture negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(gate)
    mut["message_binding"]["attachments_included"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject route-first attachment overclaim")
    mut2 = copy.deepcopy(gate)
    mut2["blocker_resolution_summary"]["gate_remains_blocked"] = False
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject unblocked route-first summary")
    mut3 = copy.deepcopy(gate)
    mut3["reply_ladder"][0]["may_create_custody_intake_import_or_floor"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject reply custody/intake/import/floor overclaim")
    mut4 = copy.deepcopy(gate)
    mut4["source_refs"].pop("route_first_human_sender_authority_precommit", None)
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("schema failed to require route-first authority precommit source")

print("audit_external_contact_route_first_send_capture_gate: OK")
