#!/usr/bin/env python3
"""Guardrail for publish-session binding-hint exactness posture."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return strict_load_json(ROOT, rel)


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/net.publish.session.schema.json")
    example = load_json("spec/examples/net.publish.session.json")
    validator = Draft202012Validator(schema)

    errs = validate(validator, example)
    for msg in errs[:20]:
        errors.append(f"spec/examples/net.publish.session.json invalid: {msg}")
    if len(errs) > 20:
        errors.append(f"spec/examples/net.publish.session.json invalid with {len(errs) - 20} additional errors")

    webhook_idp_ok = deepcopy(example)
    webhook_idp_ok["session_id"] = "publish-webhook-idp-hint-exact-7c3f"
    webhook_idp_ok["published_endpoint"]["audience"]["class"] = "public-webhook"
    webhook_idp_ok["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    webhook_idp_ok["published_endpoint"]["audience"]["identity_provider_hint"] = "google-workspace-example"
    webhook_idp_ok["published_endpoint"]["audience"]["validation_hint"] = "jwt-assertion-header"
    webhook_idp_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, webhook_idp_ok):
        errors.append("provider-identity webhook publish session with identity_provider_hint should validate")

    public_link_idp_bad = deepcopy(example)
    public_link_idp_bad["session_id"] = "publish-public-link-spare-idp-hint-7c3f"
    public_link_idp_bad["published_endpoint"]["audience"] = {
        "class": "public-link",
        "authn_mode": "none",
        "identity_provider_hint": "okta-example-com",
    }
    public_link_idp_bad["published_endpoint"].pop("secret_handoff", None)
    if not validate(validator, public_link_idp_bad):
        errors.append("public-link publish session carrying identity_provider_hint must fail validation")

    named_secret_idp_bad = deepcopy(example)
    named_secret_idp_bad["session_id"] = "publish-named-secret-spare-idp-hint-7c3f"
    named_secret_idp_bad["published_endpoint"]["audience"]["class"] = "named-recipients"
    named_secret_idp_bad["published_endpoint"]["audience"]["authn_mode"] = "single-use-secret"
    named_secret_idp_bad["published_endpoint"]["audience"]["recipient_hint"] = "external-reviewer@example.invalid"
    named_secret_idp_bad["published_endpoint"]["audience"]["identity_provider_hint"] = "okta-example-com"
    named_secret_idp_bad["published_endpoint"]["secret_handoff"]["consumption_posture"] = "single-successful-admission"
    if not validate(validator, named_secret_idp_bad):
        errors.append("single-use-secret named-recipient publish session carrying identity_provider_hint must fail validation")

    named_idp_ok = deepcopy(example)
    named_idp_ok["session_id"] = "publish-named-idp-hints-exact-7c3f"
    named_idp_ok["published_endpoint"]["audience"]["class"] = "named-recipients"
    named_idp_ok["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    named_idp_ok["published_endpoint"]["audience"]["recipient_hint"] = "external-reviewer@example.invalid"
    named_idp_ok["published_endpoint"]["audience"]["identity_provider_hint"] = "okta-example-com"
    named_idp_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    named_idp_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, named_idp_ok):
        errors.append("provider-identity named-recipient publish session with both binding hints should validate")

    org_recipient_bad = deepcopy(example)
    org_recipient_bad["session_id"] = "publish-org-spare-recipient-hint-7c3f"
    org_recipient_bad["published_endpoint"]["exposure_scope"] = "organization"
    org_recipient_bad["published_endpoint"]["audience"]["class"] = "organization-users"
    org_recipient_bad["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    org_recipient_bad["published_endpoint"]["audience"]["identity_provider_hint"] = "okta-example-com"
    org_recipient_bad["published_endpoint"]["audience"]["recipient_hint"] = "external-reviewer@example.invalid"
    org_recipient_bad["published_endpoint"].pop("secret_handoff", None)
    if not validate(validator, org_recipient_bad):
        errors.append("organization-users publish session carrying recipient_hint must fail validation")

    support_recipient_bad = deepcopy(example)
    support_recipient_bad["session_id"] = "publish-support-spare-recipient-hint-7c3f"
    support_recipient_bad["published_endpoint"]["exposure_scope"] = "support-peer"
    support_recipient_bad["published_endpoint"]["access_model"] = "peer-relay"
    support_recipient_bad["published_endpoint"]["audience"] = {
        "class": "support-session-peer",
        "authn_mode": "support-session",
        "recipient_hint": "analyst@example.invalid",
    }
    support_recipient_bad["published_endpoint"].pop("hostname", None)
    support_recipient_bad["published_endpoint"].pop("port", None)
    support_recipient_bad["published_endpoint"].pop("url_hint", None)
    support_recipient_bad["published_endpoint"].pop("path_prefix", None)
    support_recipient_bad["published_endpoint"].pop("secret_handoff", None)
    support_recipient_bad["authority"]["trigger"] = "support-session"
    support_recipient_bad["authority"].pop("consent_receipt_digest", None)
    support_recipient_bad["authority"]["support_session_digest"] = "sha256:support-session-1234"
    support_recipient_bad["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/7c3f"}
    support_recipient_bad["relay"]["destination_hint"] = "support-session/7c3f"
    support_recipient_bad["lifecycle"]["end_conditions"] = ["support-session-end", "manual-revoke", "system-sleep"]
    if not validate(validator, support_recipient_bad):
        errors.append("support-session-peer publish session carrying recipient_hint must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["binding hints are inverse evidence too", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["inverse evidence too", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md": ["stay lane-exact", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/573-publish-session-audience-bound-shares-require-binding-hints.md": ["inverse evidence too", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/592-publish-session-binding-hints-stay-lane-exact.md": ["now stay **exact with their lanes**", "tools/check_publish_session_binding_hint_exactness_contract.py"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["binding hints are inverse evidence too", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["binding hints are inverse evidence too", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_binding_hint_exactness_contract.py", "binding hints lane-exact"],
        "docs/99-llm-runbook.md": ["docs/592-publish-session-binding-hints-stay-lane-exact.md", "tools/check_publish_session_binding_hint_exactness_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing binding hints should stay lane-exact", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0182", "binding hints inverse evidence"],
        "README.md": ["docs/592-publish-session-binding-hints-stay-lane-exact.md", "binding hints lane-exact"],
        "docs/00-index.md": ["docs/592-publish-session-binding-hints-stay-lane-exact.md", "binding-hint exactness posture"],
        "CHANGELOG.md": ["ADR-0182", "docs/592-publish-session-binding-hints-stay-lane-exact.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session binding-hint exactness token: {needle}")

    if errors:
        print("Publish-session binding-hint exactness contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session binding-hint exactness contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
