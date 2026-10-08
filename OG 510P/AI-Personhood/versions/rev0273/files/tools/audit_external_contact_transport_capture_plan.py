#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLAN_REL = f"examples/external-contact-transport-capture-plan-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-transport-capture-plan.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-transport-capture-plan-public-raw-path.json"

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
        raise SystemExit(f"{label} fails external-contact-transport-capture-plan.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
plan = load_json(PLAN_REL)
validate(schema, plan, PLAN_REL)

if plan.get("revision") != REV:
    raise SystemExit("transport capture plan revision mismatch")
if plan.get("no_live_floor_effect") is not True:
    raise SystemExit("transport capture plan must have no live-floor effect")
if plan.get("plan_state") != "ready-template-no-send-no-private-root":
    raise SystemExit("transport capture plan must be ready template/no-send/no-private-root")

refs = plan.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"transport capture plan missing source: {name}={rel}")
    if rel.endswith(".json"):
        obj = load_json(rel)
        if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
            raise SystemExit(f"transport capture source must be current no-floor: {name}")

request = load_json(refs["request_packet"])
body = request.get("outgoing_request", {}).get("body", "").strip()
body_hash = sha_text(body)
mail_text = (ROOT / refs["mail_ready_draft"]).read_text(encoding="utf-8")
if body not in mail_text or f"X-AI-Personhood-Body-SHA256: {body_hash}" not in mail_text:
    raise SystemExit("transport capture plan mail-ready draft is not bound to exact body")
manifest = load_json(refs["public_payload_manifest"])
if manifest.get("message_binding", {}).get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("transport capture plan payload manifest body hash mismatch")

sequence_text = json.dumps(plan.get("capture_sequence", {})).lower()
for term in ["hash", "vault", "sent", "message-id", "provider", "reply", "transport", "utc"]:
    if term not in sequence_text:
        raise SystemExit(f"transport capture sequence missing term: {term}")

roots = plan.get("required_private_vault_roots", [])
root_ids = {root.get("root_id") for root in roots}
required_roots = {"outbound-sent-copy", "transport-trace", "delivery-status-or-dsn", "inbound-raw-reply"}
if root_ids != required_roots:
    raise SystemExit(f"transport capture plan root ids mismatch: {sorted(root_ids)}")
for root in roots:
    for key in ["root_selected_now", "public_release_may_disclose_root", "raw_bytes_may_enter_release_tree"]:
        if root.get(key) is not False:
            raise SystemExit(f"transport capture root overclaims {key}: {root.get('root_id')}")
    if root.get("selection_required_before_send") is not True:
        raise SystemExit(f"transport capture root must require selection before send: {root.get('root_id')}")

fields = {test.get("required_field") for test in plan.get("send_proof_acceptance_tests", [])}
required_fields = {"sent_at_utc", "sender_account_or_role", "recipient", "subject", "exact_body_sha256", "mail_ready_draft_sha256", "payload_item_hashes", "message_id_or_provider_equivalent", "provider_trace_or_sent_export_hash", "attachment_disposition"}
if not required_fields.issubset(fields):
    raise SystemExit(f"transport capture plan missing send-proof fields: {sorted(required_fields - fields)}")
for test in plan.get("send_proof_acceptance_tests", []):
    if test.get("may_start_response_clock_if_alone") is not False:
        raise SystemExit(f"transport capture proof field alone starts clock: {test.get('test_id')}")

policy = plan.get("public_release_policy", {})
for key in ["may_publish_raw_transport_bytes", "may_publish_raw_reply_bytes", "may_publish_private_vault_paths", "plan_may_substitute_for_send_proof"]:
    if policy.get(key) is not False:
        raise SystemExit(f"transport capture public policy overclaims: {key}")
for forbidden in ["/mnt/", "private-vault://actual", "gmail", "token", "secret"]:
    if forbidden in json.dumps(plan).lower():
        raise SystemExit(f"transport capture plan leaks forbidden private locator/token term: {forbidden}")
for key, value in plan.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"transport capture downstream lock must be false: {key}")
for rel in plan.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"transport capture related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-transport-capture-plan" not in fixture.get("target_filings", []):
    raise SystemExit("transport capture negative fixture does not target plan")
if fixture.get("severity") != "critical":
    raise SystemExit("transport capture negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(plan)
    mut["public_release_policy"]["may_publish_raw_transport_bytes"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject raw transport publication")
    mut2 = copy.deepcopy(plan)
    mut2["required_private_vault_roots"][0]["root_selected_now"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject root_selected_now=true in public template")

print("audit_external_contact_transport_capture_plan: OK")
