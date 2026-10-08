#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACK_REL = f"examples/external-contact-route-first-operator-execution-pack-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-first-operator-execution-pack.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-operator-pack-signature-placeholder-as-authority.json"

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
        raise SystemExit(f"{label} fails external-contact-route-first-operator-execution-pack.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
pack = load_json(PACK_REL)
validate(schema, pack, PACK_REL)

if pack.get("revision") != REV:
    raise SystemExit("operator execution pack revision mismatch")
if pack.get("pack_state") != "prepared-not-authorized-not-sent":
    raise SystemExit("operator execution pack must remain prepared/not-authorized/not-sent")
if pack.get("no_live_floor_effect") is not True:
    raise SystemExit("operator execution pack must have no live-floor effect")

refs = pack.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"operator execution pack source missing: {name}={rel}")

preflight = load_json(refs["route_first_preflight"])
send_gate = load_json(refs["route_first_send_capture_gate"])
reply = load_json(refs["route_first_reply_disposition"])
stage_two = load_json(refs["stage_two_authorization_gate"])
hold = load_json(refs["route_first_branch_hold"])
route_first_authority = load_json(refs["route_first_human_sender_authority_precommit"])
board = load_json(refs["operating_board"])

if preflight.get("revision") != REV or send_gate.get("revision") != REV or hold.get("revision") != REV or route_first_authority.get("revision") != REV:
    raise SystemExit("operator execution pack must bind current route-first surfaces")
if route_first_authority.get("precommit_state") != "unsigned-route-first-human-sender-authority-precommit-no-send":
    raise SystemExit("operator execution pack must bind unsigned route-first authority precommit")
if route_first_authority.get("scope_controls", {}).get("full_payload_precommit_may_substitute_for_route_first_signature") is not False:
    raise SystemExit("operator execution pack cannot allow full-payload precommit to substitute for route-first signature")
if route_first_authority.get("scope_controls", {}).get("route_first_precommit_may_authorize_stage_two_payload") is not False:
    raise SystemExit("operator execution pack cannot bind a route-first precommit that authorizes stage two")
if send_gate.get("gate_state") != "blocked-route-first-no-human-send-no-transport":
    raise SystemExit("operator execution pack cannot bind an unblocked send gate")
if hold.get("decision", {}).get("route_first_send_permitted_now") is not False:
    raise SystemExit("operator execution pack cannot bind a hold permitting send")
if reply.get("disposition_state") != "pre-send-no-inbound":
    raise SystemExit("operator execution pack must bind pre-send/no-inbound reply shell")
if stage_two.get("blocker_resolution_summary", {}).get("gate_remains_blocked") is not True:
    raise SystemExit("operator execution pack must bind blocked stage-two gate")
if board.get("queue_counts", {}).get("active_entries") != 7:
    raise SystemExit("operator execution pack must bind seven-item operating board")

msg = pack.get("exact_route_first_message", {})
body_rel = msg.get("body_ref")
eml_rel = msg.get("mail_ready_draft_ref")
for rel in [body_rel, eml_rel, pack.get("stage_two_boundary", {}).get("stage_two_payload_manifest_ref")]:
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"operator execution pack referenced surface missing: {rel}")
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
eml = (ROOT / eml_rel).read_text(encoding="utf-8")
body_hash = sha_text(body)
eml_hash = sha_bytes(eml_rel)
if msg.get("body_sha256") != body_hash or msg.get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("operator execution pack route-first body/.eml hashes stale")
if msg.get("body_word_count") != len(body.split()):
    raise SystemExit("operator execution pack route-first word count stale")
if preflight.get("route_first_message", {}).get("body_sha256") != body_hash:
    raise SystemExit("operator execution pack body hash disagrees with preflight")
if send_gate.get("message_binding", {}).get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("operator execution pack .eml hash disagrees with send gate")
if route_first_authority.get("exact_route_first_binding", {}).get("body_sha256") != body_hash:
    raise SystemExit("operator execution pack body hash disagrees with route-first authority precommit")
if route_first_authority.get("exact_route_first_binding", {}).get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("operator execution pack .eml hash disagrees with route-first authority precommit")
if "Content-Disposition: attachment" in eml or msg.get("attachments_included") is not False or msg.get("stage_two_payload_attached") is not False:
    raise SystemExit("operator execution pack must remain no-attachment/stage-two-deferred")

# Human and private slots must remain empty public placeholders, not authority.
slot_ids = {slot.get("slot_id") for slot in pack.get("human_authority_slots", [])}
required_slots = {"human-signature", "sender-authority", "send-time-locator-recheck", "final-route-first-hash-recompute"}
if not required_slots.issubset(slot_ids):
    raise SystemExit(f"operator execution pack missing human slots: {sorted(required_slots - slot_ids)}")
for slot in pack.get("human_authority_slots", []):
    if slot.get("required_before_send") is not True or slot.get("current_value") is not None:
        raise SystemExit(f"operator execution pack overclaims human slot: {slot.get('slot_id')}")
    if slot.get("may_be_satisfied_inside_public_release") is not False:
        raise SystemExit(f"operator execution pack wrongly treats public release as satisfying authority: {slot.get('slot_id')}")

vault_ids = {slot.get("slot_id") for slot in pack.get("private_vault_slots", [])}
required_vault = {"sent-copy-root", "transport-trace-root", "delivery-status-root", "raw-inbound-root"}
if not required_vault.issubset(vault_ids):
    raise SystemExit(f"operator execution pack missing private vault slots: {sorted(required_vault - vault_ids)}")
for slot in pack.get("private_vault_slots", []):
    if slot.get("public_value") is not None:
        raise SystemExit(f"operator execution pack leaked or invented public vault value: {slot.get('slot_id')}")
    for key in ["raw_private_material_allowed_in_release", "placeholder_may_satisfy_custody"]:
        if slot.get(key) is not False:
            raise SystemExit(f"operator execution pack private slot overclaims {key}: {slot.get('slot_id')}")

for step in pack.get("execution_checklist", []):
    if step.get("may_create_contact_or_floor") is not False:
        raise SystemExit(f"operator execution pack checklist overclaims contact/floor: {step.get('step_id')}")
if not any(step.get("completion_state") == "blocked" for step in pack.get("execution_checklist", [])):
    raise SystemExit("operator execution pack must retain blocked steps")

stage = pack.get("stage_two_boundary", {})
if stage.get("stage_two_send_authorized_now") is not False or stage.get("willing_reply_may_auto_send_stage_two") is not False:
    raise SystemExit("operator execution pack cannot authorize stage two")
for key in ["fresh_authorization_required", "fresh_hashes_required"]:
    if stage.get(key) is not True:
        raise SystemExit(f"operator execution pack stage-two boundary must require {key}")

nonclosure = pack.get("nonclosure_controls", {})
if nonclosure.get("operator_pack_may_close_first_artifact_tasks") is not False:
    raise SystemExit("operator execution pack cannot close first-artifact tasks")
needed = {"FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"}
if not needed.issubset(set(nonclosure.get("do_not_close_by_narrative", []))):
    raise SystemExit("operator execution pack missing nonclosure task controls")
if nonclosure.get("operating_board_active_count_observed") != 7:
    raise SystemExit("operator execution pack must preserve seven active board items")

for section in ["operational_state", "downstream_locks"]:
    for key, value in pack.get(section, {}).items():
        if value is not False:
            raise SystemExit(f"operator execution pack {section} must remain false: {key}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-operator-execution-pack" not in fixture.get("target_filings", []):
    raise SystemExit("operator execution pack negative fixture does not target pack")
if fixture.get("severity") != "critical":
    raise SystemExit("operator execution pack negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(pack)
    mut["human_authority_slots"][0]["current_value"] = "signed"
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject public signature placeholder as authority")
    mut2 = copy.deepcopy(pack)
    mut2["private_vault_slots"][0]["public_value"] = "file:///private/raw.eml"
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject public private-vault value")
    mut3 = copy.deepcopy(pack)
    mut3["downstream_locks"]["may_treat_operator_pack_as_send"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject operator-pack-as-send overclaim")

print("audit_external_contact_route_first_operator_execution_pack: OK")
