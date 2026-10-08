#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
GATE_REL = f"examples/external-contact-stage-two-authorization-gate-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-stage-two-authorization-gate.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-stage-two-willing-reply-as-automatic-send.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_bytes(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-stage-two-authorization-gate.schema.json: {errors[0].message}")


schema = load_json(SCHEMA_REL)
gate = load_json(GATE_REL)
validate(schema, gate, GATE_REL)

if gate.get("revision") != REV:
    raise SystemExit("stage-two authorization gate revision mismatch")
if gate.get("gate_state") != "blocked-stage-two-no-willing-reply-no-human-authorization":
    raise SystemExit("stage-two gate must remain blocked/no-willing-reply/no-human-authorization")
if gate.get("no_live_floor_effect") is not True:
    raise SystemExit("stage-two authorization gate must be no-floor")

refs = gate.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"stage-two authorization source missing: {name}={rel}")

manifest = load_json(refs["public_payload_manifest"])
reply = load_json(refs["route_first_reply_disposition"])
route_gate = load_json(refs["route_first_send_capture_gate"])
hash_dry_run = load_json(refs["hash_recompute_dry_run"])
for label, obj in [("manifest", manifest), ("reply", reply), ("route_gate", route_gate), ("hash_dry_run", hash_dry_run)]:
    if obj.get("revision") != REV:
        raise SystemExit(f"stage-two source revision mismatch: {label}")
    if obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"stage-two source must be no-floor: {label}")

binding = gate.get("payload_binding", {})
if binding.get("payload_manifest_ref") != refs["public_payload_manifest"]:
    raise SystemExit("stage-two gate payload manifest ref mismatch")
if binding.get("payload_manifest_sha256") != sha_bytes(refs["public_payload_manifest"]):
    raise SystemExit("stage-two gate payload manifest sha stale")
items = manifest.get("public_payload_items", [])
if binding.get("public_payload_item_count") != len(items) or len(items) != 2:
    raise SystemExit("stage-two gate must bind exactly two public payload items")
if binding.get("one_page_sha256") != sha_bytes(refs["one_page_note"]):
    raise SystemExit("stage-two gate one-page sha stale")
if binding.get("request_packet_sha256") != sha_bytes(refs["machine_checkable_request_packet"]):
    raise SystemExit("stage-two gate request packet sha stale")
for key in ["raw_private_evidence_included", "payload_manifest_may_substitute_for_authorization_or_transport_proof"]:
    if binding.get(key) is not False:
        raise SystemExit(f"stage-two payload binding overclaim: {key}")

required_unsatisfied = {
    "route-first-transport-proof",
    "route-first-willing-reply-or-separate-authorization",
    "fresh-human-signature",
    "fresh-sender-authority",
    "send-time-locator-recheck",
    "private-vault-roots",
    "final-payload-hash-recompute",
    "actual-stage-two-transport-proof",
}
preconditions = gate.get("preconditions", [])
unsatisfied = {p.get("precondition_id") for p in preconditions if p.get("satisfied_now") is False}
satisfied = {p.get("precondition_id") for p in preconditions if p.get("satisfied_now") is True}
if satisfied:
    raise SystemExit(f"stage-two gate should have no satisfied preconditions yet: {sorted(satisfied)}")
if unsatisfied != required_unsatisfied:
    raise SystemExit(f"stage-two unsatisfied blockers mismatch: {sorted(unsatisfied)}")
for p in preconditions:
    if p.get("required_before_stage_two_send") is not True:
        raise SystemExit(f"stage-two precondition must be required: {p.get('precondition_id')}")
    if p.get("satisfied_by_ref") is not None:
        raise SystemExit(f"stage-two precondition must not claim evidence yet: {p.get('precondition_id')}")
summary = gate.get("blocker_resolution_summary", {})
if summary.get("total_preconditions") != len(preconditions):
    raise SystemExit("stage-two blocker total stale")
if summary.get("satisfied_now_count") != 0 or summary.get("unsatisfied_now_count") != len(required_unsatisfied):
    raise SystemExit("stage-two blocker counts stale")
if set(summary.get("unsatisfied_precondition_ids", [])) != required_unsatisfied:
    raise SystemExit("stage-two unsatisfied summary stale")
if summary.get("gate_remains_blocked") is not True:
    raise SystemExit("stage-two gate must remain blocked")

controls = gate.get("send_controls", {})
for key in ["stage_two_send_permitted_now", "automatic_send_after_willing_reply", "stage_two_response_clock_may_start_from_payload_manifest"]:
    if controls.get(key) is not False:
        raise SystemExit(f"stage-two send control must be false: {key}")
for key in ["willing_reply_is_only_authorization_candidate", "fresh_human_signature_required", "fresh_sender_authority_required", "fresh_payload_hash_recompute_required", "stage_two_transport_proof_required"]:
    if controls.get(key) is not True:
        raise SystemExit(f"stage-two send control must be true: {key}")
if reply.get("stage_two_controls", {}).get("stage_two_may_be_sent_now") is not False:
    raise SystemExit("stage-two gate requires reply disposition to block stage-two send")
if route_gate.get("blocker_resolution_summary", {}).get("gate_remains_blocked") is not True:
    raise SystemExit("stage-two gate must be downstream of a blocked route-first gate")
if hash_dry_run.get("send_time_policy", {}).get("dry_run_may_satisfy_send_time_recompute") is not False:
    raise SystemExit("stage-two gate must not accept dry-run as send-time recompute")

for key, value in gate.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"stage-two downstream lock must be false: {key}")
for rel in gate.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"stage-two related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-stage-two-authorization-gate" not in fixture.get("target_filings", []):
    raise SystemExit("stage-two fixture does not target authorization gate")
if fixture.get("severity") != "critical":
    raise SystemExit("stage-two fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(gate)
    mut["send_controls"]["automatic_send_after_willing_reply"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject willing reply as automatic send")
    mut2 = copy.deepcopy(gate)
    mut2["blocker_resolution_summary"]["gate_remains_blocked"] = False
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject unblocked stage-two gate")
    mut3 = copy.deepcopy(gate)
    mut3["payload_binding"]["payload_manifest_may_substitute_for_authorization_or_transport_proof"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject payload manifest as authorization/transport proof")

print("audit_external_contact_stage_two_authorization_gate: OK")
