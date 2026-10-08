#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_REL = f"examples/external-contact-current-public-locator-recheck-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-current-public-locator-recheck.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-public-locator-recheck-treated-as-consent.json"
CARD_REL = f"examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json"

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
        raise SystemExit(f"{label} fails external-contact-current-public-locator-recheck.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
report = load_json(REPORT_REL)
validate(schema, report, REPORT_REL)

if report.get("revision") != REV:
    raise SystemExit("public locator recheck revision mismatch")
if report.get("no_live_floor_effect") is not True:
    raise SystemExit("public locator recheck must be no-floor")
if report.get("recheck_state") != "current-public-locator-rechecked-no-send":
    raise SystemExit("public locator recheck must remain no-send")

card = load_json(CARD_REL)
if card.get("revision") != REV or card.get("no_live_floor_effect") is not True:
    raise SystemExit("public locator recheck card must be current/no-floor")

finding = report.get("current_locator_finding", {})
if finding.get("public_channel_locator") != "info@raicollab.org":
    raise SystemExit("public locator recheck must bind info@raicollab.org")
if finding.get("public_source_url") != "https://incidentdatabase.ai/contact/":
    raise SystemExit("public locator recheck must bind AIID contact page")
if finding.get("locator_matches_dispatch_card_now") is not True:
    raise SystemExit("public locator recheck must match dispatch card now")
if card.get("selected_candidate", {}).get("public_channel_locator") != finding.get("public_channel_locator"):
    raise SystemExit("public locator recheck does not match dispatch card locator")

sources = report.get("public_sources_checked", [])
source_text = " ".join([s.get("source_url", "") + " " + s.get("observed_claim", "") + " " + s.get("observed_contact_or_route", "") + " " + s.get("route_use", "") for s in sources]).lower()
for term in ["incidentdatabase.ai/contact", "info@raicollab.org", "steward", "collaboration", "incidentdatabase.ai", "harms", "near harms"]:
    if term not in source_text:
        raise SystemExit(f"public locator recheck missing source term: {term}")

limits = report.get("recheck_limits", {})
if limits.get("must_recheck_again_immediately_before_later_send") is not True:
    raise SystemExit("public locator recheck must require later send-time recheck")
for key in ["recheck_may_authorize_send", "recheck_is_consent_or_authority", "recheck_satisfies_send_time_recheck_if_send_delayed"]:
    if limits.get(key) is not False:
        raise SystemExit(f"public locator recheck overclaims limit: {key}")
if limits.get("locator_is_not_custody_intake_import_or_recognition") is not True:
    raise SystemExit("public locator recheck must reject custody/intake/import/recognition")

for section in ["operational_state", "downstream_locks"]:
    for key, value in report.get(section, {}).items():
        if value is not False:
            raise SystemExit(f"public locator recheck {section} lock must be false: {key}")
for rel in report.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"public locator recheck related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-current-public-locator-recheck" not in fixture.get("target_filings", []):
    raise SystemExit("public locator recheck fixture does not target report")
if fixture.get("severity") != "critical":
    raise SystemExit("public locator recheck fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(report)
    mut["recheck_limits"]["recheck_is_consent_or_authority"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject locator as consent/authority")
    mut2 = copy.deepcopy(report)
    mut2["recheck_limits"]["recheck_satisfies_send_time_recheck_if_send_delayed"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject stale recheck as later send-time recheck")
    mut3 = copy.deepcopy(report)
    mut3["downstream_locks"]["may_treat_locator_as_contact"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject locator as contact")

print("audit_external_contact_current_public_locator_recheck: OK")
