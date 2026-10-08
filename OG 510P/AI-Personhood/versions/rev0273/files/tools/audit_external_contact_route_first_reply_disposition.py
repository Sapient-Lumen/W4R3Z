#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DISPOSITION_REL = f"examples/external-contact-route-first-reply-disposition-{REV}-aiid-no-inbound.json"
SCHEMA_REL = "schemas/external-contact-route-first-reply-disposition.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-reply-disposition-willingness-as-custody.json"

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
        raise SystemExit(f"{label} fails external-contact-route-first-reply-disposition.schema.json: {errors[0].message}")


schema = load_json(SCHEMA_REL)
disp = load_json(DISPOSITION_REL)
validate(schema, disp, DISPOSITION_REL)

if disp.get("revision") != REV:
    raise SystemExit("route-first reply disposition revision mismatch")
if disp.get("disposition_state") != "pre-send-no-inbound":
    raise SystemExit("route-first reply disposition must remain pre-send/no-inbound")
if disp.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first reply disposition must be no-floor")

refs = disp.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"route-first reply disposition source missing: {name}={rel}")

gate = load_json(refs["route_first_send_capture_gate"])
preflight = load_json(refs["route_first_preflight"])
stage_gate = load_json(refs["stage_two_authorization_gate"])
for label, obj in [("gate", gate), ("preflight", preflight), ("stage_gate", stage_gate)]:
    if obj.get("revision") != REV:
        raise SystemExit(f"route-first reply disposition source revision mismatch: {label}")
    if obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"route-first reply disposition source must be no-floor: {label}")

body_rel = refs["route_first_body"]
eml_rel = refs["route_first_mail_ready_draft"]
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
eml = (ROOT / eml_rel).read_text(encoding="utf-8")
body_hash = sha_text(body)
eml_hash = sha_bytes(eml_rel)
binding = disp.get("route_first_binding", {})
if binding.get("body_sha256") != body_hash:
    raise SystemExit("route-first reply disposition body hash stale")
if binding.get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("route-first reply disposition .eml hash stale")
if binding.get("body_word_count") != len(body.split()):
    raise SystemExit("route-first reply disposition body word count stale")
if gate.get("message_binding", {}).get("body_sha256") != body_hash:
    raise SystemExit("route-first reply disposition not bound to send/capture gate body")
if preflight.get("route_first_message", {}).get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("route-first reply disposition not bound to preflight .eml")
if body not in eml:
    raise SystemExit("route-first reply disposition .eml does not contain exact body")
if binding.get("transport_proof_required_before_any_reply_disposition") is not True:
    raise SystemExit("route-first reply disposition must require transport proof before reply disposition")
if binding.get("response_clock_started") is not False:
    raise SystemExit("route-first reply disposition must not start response clock")

inbound = disp.get("inbound_state", {})
for key, value in inbound.items():
    if key in {"raw_reply_private_vault_ref", "classification_selected"}:
        if value is not None:
            raise SystemExit(f"route-first reply disposition inbound field must be null: {key}")
    elif value is not False:
        raise SystemExit(f"route-first reply disposition inbound field must be false: {key}")

classes = {item.get("class_id"): item for item in disp.get("classification_ladder", [])}
needed = {
    "no-inbound",
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
if not needed.issubset(classes):
    raise SystemExit(f"route-first reply disposition missing classes: {sorted(needed - set(classes))}")
for cid, item in classes.items():
    if item.get("may_send_stage_two_without_new_authorization") is not False:
        raise SystemExit(f"route-first reply class allows unauthorized stage two: {cid}")
    if item.get("may_create_custody_intake_import_or_floor") is not False:
        raise SystemExit(f"route-first reply class overclaims custody/intake/import/floor: {cid}")
true_candidates = {cid for cid, item in classes.items() if item.get("may_trigger_stage_two_authorization_candidate") is True}
if true_candidates != {"substantive-willingness-to-receive-stage-two"}:
    raise SystemExit(f"only substantive willingness may trigger stage-two authorization candidate, got {sorted(true_candidates)}")

controls = disp.get("stage_two_controls", {})
if controls.get("stage_two_payload_manifest_sha256") != sha_bytes(controls.get("stage_two_payload_manifest_ref")):
    raise SystemExit("route-first reply disposition stage-two manifest hash stale")
for key in ["stage_two_may_be_sent_now", "willing_reply_may_substitute_for_human_signature"]:
    if controls.get(key) is not False:
        raise SystemExit(f"route-first reply disposition must keep stage-two control false: {key}")
for key in ["fresh_stage_two_authorization_gate_required", "fresh_payload_hash_recompute_required", "stage_two_transport_proof_required_if_sent"]:
    if controls.get(key) is not True:
        raise SystemExit(f"route-first reply disposition must keep stage-two control true: {key}")

refactor = disp.get("refactor_audit", {})
if refactor.get("route_first_reply_disposition_added") is not True:
    raise SystemExit("route-first reply disposition refactor flag missing")
if refactor.get("old_full_payload_response_triage_demoted_to_legacy_context") is not True:
    raise SystemExit("route-first reply disposition must demote old full-payload triage context")
if refactor.get("active_queue_count_observed") != 7 or refactor.get("active_queue_count_required") != 7:
    raise SystemExit("route-first reply disposition active queue count must stay seven")

for key, value in disp.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"route-first reply disposition downstream lock must be false: {key}")
for rel in disp.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"route-first reply disposition related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-reply-disposition" not in fixture.get("target_filings", []):
    raise SystemExit("route-first reply disposition fixture does not target disposition")
if fixture.get("severity") != "critical":
    raise SystemExit("route-first reply disposition fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(disp)
    mut["inbound_state"]["inbound_artifact_present"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject inbound artifact in no-inbound shell")
    mut2 = copy.deepcopy(disp)
    mut2["classification_ladder"][0]["may_create_custody_intake_import_or_floor"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject reply custody/intake/import/floor overclaim")
    mut3 = copy.deepcopy(disp)
    mut3["stage_two_controls"]["stage_two_may_be_sent_now"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject immediate stage-two send")

print("audit_external_contact_route_first_reply_disposition: OK")
