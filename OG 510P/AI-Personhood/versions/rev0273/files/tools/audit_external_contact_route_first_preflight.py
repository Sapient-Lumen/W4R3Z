#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PREFLIGHT_REL = f"examples/external-contact-route-first-preflight-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-first-preflight.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-preflight-attachment-overclaim.json"

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
        raise SystemExit(f"{label} fails external-contact-route-first-preflight.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
pre = load_json(PREFLIGHT_REL)
validate(schema, pre, PREFLIGHT_REL)

if pre.get("revision") != REV:
    raise SystemExit("route-first preflight revision mismatch")
if pre.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first preflight must be no-floor")
if pre.get("preflight_state") != "preferred-route-first-no-attachment-blocked-no-human-send":
    raise SystemExit("route-first preflight must remain blocked/no-send")

msg = pre.get("route_first_message", {})
body_rel = msg.get("body_ref")
eml_rel = msg.get("mail_ready_draft_ref")
manifest_rel = pre.get("stage_two_payload", {}).get("public_payload_manifest_ref")
for rel in [body_rel, eml_rel, manifest_rel]:
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"route-first referenced surface missing: {rel}")
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
eml = (ROOT / eml_rel).read_text(encoding="utf-8")
if msg.get("body_sha256") != sha_text(body):
    raise SystemExit("route-first body hash stale")
if msg.get("mail_ready_draft_sha256") != sha_bytes(eml_rel):
    raise SystemExit("route-first .eml hash stale")
if msg.get("body_word_count") != len(body.split()):
    raise SystemExit("route-first body word count stale")
if not (60 <= len(body.split()) <= 180):
    raise SystemExit("route-first body must stay short")
if msg.get("attachments_included") is not False or msg.get("payload_item_count") != 0:
    raise SystemExit("route-first message must include zero attachments")
if "Content-Disposition: attachment" in eml or "multipart/" in eml.lower():
    raise SystemExit("route-first .eml must remain plain-text/no-attachment")
if body not in eml:
    raise SystemExit("route-first .eml does not contain exact body")
for header in [
    "X-AI-Personhood-Draft-State: NOT-SENT",
    "X-AI-Personhood-Route-First: no-attachments",
    f"X-AI-Personhood-Body-SHA256: {msg.get('body_sha256')}",
    "X-AI-Personhood-Clock-Guard: draft_may_not_start_response_clock",
    "To: info@raicollab.org",
    f"Subject: {msg.get('subject')}",
]:
    if header not in eml:
        raise SystemExit(f"route-first .eml missing header: {header}")

lower = body.lower()
required_terms = [
    "before sending any packet or attachments",
    "not an aiid incident submission",
    "not asking you to endorse ai personhood",
    "not be treated as waiver",
    "not custody, intake, import, live-floor credit",
]
for term in required_terms:
    if term not in lower:
        raise SystemExit(f"route-first body missing guard term: {term}")
for forbidden in ["attached", "attachments included", "creates custody", "legal/status recognition", "will be treated as waiver"]:
    if forbidden in lower and forbidden != "attached":
        raise SystemExit(f"route-first body contains forbidden term: {forbidden}")
# Allow "attachments" only in the phrase that says no attachments before routing.
if lower.count("attachments") > 1:
    raise SystemExit("route-first body mentions attachments too often")

manifest = load_json(manifest_rel)
if manifest.get("revision") != REV or manifest.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first stage-two manifest must be current/no-floor")
if len(manifest.get("public_payload_items", [])) != 2:
    raise SystemExit("route-first stage-two manifest must have exactly two public payload items")
if pre.get("stage_two_payload", {}).get("send_only_after_counterparty_willingness_or_separate_human_authorization") is not True:
    raise SystemExit("route-first must defer payload until willingness or separate authorization")
if pre.get("stage_two_payload", {}).get("payload_manifest_may_substitute_for_send_proof_or_custody") is not False:
    raise SystemExit("route-first stage-two manifest must not substitute for proof/custody")

required_blockers = {"human-signature", "sender-authority", "send-time-public-locator-recheck", "private-vault-roots", "final-body-hash-recompute", "transport-proof-capture"}
observed = {b.get("precondition_id") for b in pre.get("blocking_preconditions", [])}
if not required_blockers.issubset(observed):
    raise SystemExit(f"route-first missing blockers: {sorted(required_blockers - observed)}")
for b in pre.get("blocking_preconditions", []):
    if b.get("required_before_send") is not True or b.get("satisfied_now") is not False:
        raise SystemExit(f"route-first blocker overclaimed: {b.get('precondition_id')}")
for section in ["operational_state", "downstream_locks"]:
    for key, val in pre.get(section, {}).items():
        if val is not False:
            raise SystemExit(f"route-first {section} overclaims: {key}")
for rel in pre.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"route-first related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-preflight" not in fixture.get("target_filings", []):
    raise SystemExit("route-first negative fixture does not target preflight")
if fixture.get("severity") != "critical":
    raise SystemExit("route-first negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(pre)
    mut["route_first_message"]["attachments_included"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject route-first attachments")
    mut2 = copy.deepcopy(pre)
    mut2["risk_reduction_rationale"]["route_first_may_authorize_send"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject route-first as authorization")
    mut3 = copy.deepcopy(pre)
    mut3["downstream_locks"]["may_start_response_clock"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject response-clock overclaim")

print("audit_external_contact_route_first_preflight: OK")
