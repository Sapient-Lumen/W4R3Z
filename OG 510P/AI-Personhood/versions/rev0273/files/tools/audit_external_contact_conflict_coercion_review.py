#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REVIEW_REL = f"examples/external-contact-conflict-coercion-review-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-conflict-coercion-review.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-conflict-coercion-review-pressure-overclaim.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-conflict-coercion-review.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
review = load_json(REVIEW_REL)
validate(schema, review, REVIEW_REL)

if review.get("revision") != REV:
    raise SystemExit("conflict/coercion review revision mismatch")
if review.get("no_live_floor_effect") is not True:
    raise SystemExit("conflict/coercion review must be no-floor")
if review.get("review_state") != "completed-public-language-conflict-coercion-review-no-authorization":
    raise SystemExit("conflict/coercion review state must be completed/public-language/no-authorization")

refs = review.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"conflict/coercion review missing source: {name}={rel}")
request = load_json(refs["request_packet"])
route_fit = load_json(refs["route_fit_review"])
payload_manifest = load_json(refs["public_payload_manifest"])
mail_text = (ROOT / refs["mail_ready_draft"]).read_text(encoding="utf-8")
for label, obj in [("request", request), ("route_fit", route_fit), ("payload_manifest", payload_manifest)]:
    if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"conflict/coercion source not current no-floor: {label}")

body = request.get("outgoing_request", {}).get("body", "").strip()
lower = body.lower()
if body not in mail_text:
    raise SystemExit("conflict/coercion mail-ready draft does not contain exact body")
if len(body.split()) > 220:
    raise SystemExit("conflict/coercion review requires a shorter, routable body <=220 words")

required_present = [
    "not asking you to endorse ai personhood",
    "legal status",
    "raw/private evidence",
    "collaboration/routing inquiry",
    "not as an incident submission",
    "receive/route/decline",
    "failed-gate/public-shell summary",
    "not be treated as waiver",
    "not custody, intake, import, live-floor credit",
]
for phrase in required_present:
    if phrase not in lower:
        raise SystemExit(f"conflict/coercion body missing guard phrase: {phrase}")

for forbidden in [
    "your silence will be treated",
    "we will count your silence",
    "adverse inference will be drawn",
    "you must endorse",
    "you recognize ai personhood",
    "you consent to custody",
    "this creates intake",
    "this creates live-floor credit",
    "you must publish raw evidence",
    "you must disclose trade secrets",
]:
    if forbidden in lower:
        raise SystemExit(f"conflict/coercion body contains coercive or overclaim phrase: {forbidden}")

scope = review.get("review_scope", {})
if scope.get("public_text_and_route_only") is not True:
    raise SystemExit("conflict/coercion scope must be public text/route only")
for key in ["human_legal_conflict_review", "sender_account_authority_review", "private_interest_check", "may_authorize_send"]:
    if scope.get(key) is not False:
        raise SystemExit(f"conflict/coercion scope overclaims: {key}")

for key, val in review.get("message_checks", {}).items():
    if val is not True:
        raise SystemExit(f"conflict/coercion message check must be true: {key}")
for key, val in review.get("residual_blockers", {}).items():
    if val is not True:
        raise SystemExit(f"conflict/coercion residual blocker must remain true: {key}")
for key, val in review.get("downstream_locks", {}).items():
    if val is not False:
        raise SystemExit(f"conflict/coercion downstream lock must be false: {key}")
for rel in review.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"conflict/coercion related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-conflict-coercion-review" not in fixture.get("target_filings", []):
    raise SystemExit("conflict/coercion fixture does not target review")
if fixture.get("severity") != "critical":
    raise SystemExit("conflict/coercion fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(review)
    mut["review_scope"]["may_authorize_send"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject conflict review as send authorization")
    mut2 = copy.deepcopy(review)
    mut2["message_checks"]["does_not_threaten_retaliation_or_adverse_inference"] = False
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject adverse-inference pressure")

print("audit_external_contact_conflict_coercion_review: OK")
