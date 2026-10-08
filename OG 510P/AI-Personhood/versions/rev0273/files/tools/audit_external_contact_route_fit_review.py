#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REVIEW_REL = f"examples/external-contact-route-fit-review-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-fit-review.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-fit-review-treated-as-authorization.json"

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
        raise SystemExit(f"{label} fails external-contact-route-fit-review.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
review = load_json(REVIEW_REL)
validate(schema, review, REVIEW_REL)

if review.get("revision") != REV:
    raise SystemExit("route-fit review revision mismatch")
if review.get("no_live_floor_effect") is not True:
    raise SystemExit("route-fit review must have no live-floor effect")
if review.get("review_state") != "completed-limited-route-fit-no-authorization":
    raise SystemExit("route-fit review must remain completed-limited/no-authorization")

packet_rel = review.get("source_request_packet_ref")
if not packet_rel or not (ROOT / packet_rel).exists():
    raise SystemExit("route-fit review request packet missing")
packet = load_json(packet_rel)
if packet.get("revision") != REV or packet.get("no_live_floor_effect") is not True:
    raise SystemExit("route-fit review request packet must be current no-floor")
body = packet.get("outgoing_request", {}).get("body", "").lower()
for phrase in [
    "collaboration/routing inquiry",
    "not as an incident submission",
    "not asking you to endorse ai personhood",
    "not custody, intake, import, live-floor credit",
    "not be treated as waiver",
]:
    if phrase not in body:
        raise SystemExit(f"route-fit review body missing required phrase: {phrase}")
if len(body.split()) > 260:
    raise SystemExit("route-fit review body exceeds word budget")

counterparty = review.get("target_counterparty", {})
if counterparty.get("public_channel_locator") != "info@raicollab.org":
    raise SystemExit("route-fit review public channel locator changed unexpectedly")
if "incidentdatabase.ai/contact" not in counterparty.get("public_source_url", ""):
    raise SystemExit("route-fit review not bound to AIID contact page")
if counterparty.get("locator_is_not_consent_authority_or_retention_permission") is not True:
    raise SystemExit("route-fit review must keep locator non-authorizing")

urls = {item.get("url", "") for item in review.get("public_sources", [])}
if not any("incidentdatabase.ai/contact" in u for u in urls):
    raise SystemExit("route-fit review missing AIID contact source")
if not any(u.rstrip("/") == "https://incidentdatabase.ai" or "incidentdatabase.ai/" in u for u in urls):
    raise SystemExit("route-fit review missing AIID purpose source")
if not any("raicollab.org" in u for u in urls):
    raise SystemExit("route-fit review missing RAICollab source")
for item in review.get("public_sources", []):
    text = " ".join(str(item.get(k, "")) for k in ["observed_claim", "route_relevance", "evidence_limit"]).lower()
    if "consent" in text and "not" not in text and "does not" not in text:
        raise SystemExit(f"route-fit source may imply consent: {item.get('source_id')}")

findings = review.get("route_fit_findings", {})
if findings.get("best_current_route") != "collaboration/routing inquiry":
    raise SystemExit("route-fit review must choose collaboration/routing inquiry")
if findings.get("fit_satisfied_for_current_draft") is not True:
    raise SystemExit("route-fit review must satisfy route fit for current draft")
for key in ["route_fit_may_authorize_send", "source_listing_may_be_treated_as_consent", "reply_may_be_treated_as_custody_without_separate_gate"]:
    if findings.get(key) is not False:
        raise SystemExit(f"route-fit review overclaims: {key}")
not_fit = " ".join(findings.get("not_fit_for", [])).lower()
for term in ["incident", "status", "custody", "raw"]:
    if term not in not_fit:
        raise SystemExit(f"route-fit not-fit list missing {term}")

checks = review.get("message_fit_checks", {})
for key, value in checks.items():
    if value is not True:
        raise SystemExit(f"route-fit message check must be true: {key}")
limits = review.get("send_limitations", {})
for key, value in limits.items():
    if value is not True:
        raise SystemExit(f"route-fit send limitation must remain true: {key}")
for key, value in review.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"route-fit downstream lock must be false: {key}")
for rel in review.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"route-fit related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-fit-review" not in fixture.get("target_filings", []):
    raise SystemExit("route-fit negative fixture does not target route-fit review")
if fixture.get("severity") != "critical":
    raise SystemExit("route-fit negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(review)
    mut["route_fit_findings"]["route_fit_may_authorize_send"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject route-fit-as-authorization")
    mut2 = copy.deepcopy(review)
    mut2["target_counterparty"]["locator_is_not_consent_authority_or_retention_permission"] = False
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject locator-as-consent")

print("audit_external_contact_route_fit_review: OK")
