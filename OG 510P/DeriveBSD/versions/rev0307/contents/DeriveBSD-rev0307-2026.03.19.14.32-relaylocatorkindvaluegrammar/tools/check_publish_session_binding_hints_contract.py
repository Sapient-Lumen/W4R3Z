#!/usr/bin/env python3
"""Guardrail for publish-session audience-binding hints posture."""
from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


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

    org_ok = deepcopy(example)
    org_ok["session_id"] = "publish-org-binding-hint-7c3f"
    org_ok["published_endpoint"]["exposure_scope"] = "organization"
    org_ok["published_endpoint"]["access_model"] = "relay-url"
    org_ok["published_endpoint"]["audience"]["class"] = "organization-users"
    org_ok["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    org_ok["published_endpoint"]["audience"]["identity_provider_hint"] = "okta-example-com"
    org_ok["published_endpoint"]["audience"]["validation_hint"] = "group=design-reviewers"
    org_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, org_ok):
        errors.append("organization-users publish session with identity_provider_hint should validate")

    org_missing = deepcopy(org_ok)
    org_missing["published_endpoint"]["audience"].pop("identity_provider_hint", None)
    if not validate(validator, org_missing):
        errors.append("organization-users publish session without identity_provider_hint must fail validation")

    named_secret_ok = deepcopy(example)
    named_secret_ok["session_id"] = "publish-named-recipient-hint-7c3f"
    named_secret_ok["published_endpoint"]["exposure_scope"] = "internet"
    named_secret_ok["published_endpoint"]["access_model"] = "relay-url"
    named_secret_ok["published_endpoint"]["audience"]["class"] = "named-recipients"
    named_secret_ok["published_endpoint"]["audience"]["authn_mode"] = "single-use-secret"
    named_secret_ok["published_endpoint"]["audience"]["recipient_hint"] = "external-reviewer@example.invalid"
    named_secret_ok["published_endpoint"]["audience"]["validation_hint"] = "single-use secret delivered out-of-band"
    named_secret_ok["published_endpoint"]["secret_handoff"]["consumption_posture"] = "single-successful-admission"
    if validate(validator, named_secret_ok):
        errors.append("named-recipients publish session with recipient_hint should validate")

    named_missing = deepcopy(named_secret_ok)
    named_missing["published_endpoint"]["audience"].pop("recipient_hint", None)
    if not validate(validator, named_missing):
        errors.append("named-recipients publish session without recipient_hint must fail validation")

    webhook_idp_ok = deepcopy(example)
    webhook_idp_ok["session_id"] = "publish-webhook-provider-id-7c3f"
    webhook_idp_ok["published_endpoint"]["audience"]["class"] = "public-webhook"
    webhook_idp_ok["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    webhook_idp_ok["published_endpoint"]["audience"]["identity_provider_hint"] = "google-workspace-example"
    webhook_idp_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, webhook_idp_ok):
        errors.append("provider-identity publish session with identity_provider_hint should validate")

    webhook_idp_missing = deepcopy(webhook_idp_ok)
    webhook_idp_missing["published_endpoint"]["audience"].pop("identity_provider_hint", None)
    if not validate(validator, webhook_idp_missing):
        errors.append("provider-identity publish session without identity_provider_hint must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["identity_provider_hint", "recipient_hint"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["identity_provider_hint", "recipient_hint", "docs/573-publish-session-audience-bound-shares-require-binding-hints.md"],
        "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md": ["identity_provider_hint", "recipient_hint", "docs/573-publish-session-audience-bound-shares-require-binding-hints.md"],
        "docs/573-publish-session-audience-bound-shares-require-binding-hints.md": ["identity_provider_hint", "recipient_hint", "provider-identity"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["identity_provider_hint", "recipient_hint"],
        "docs/460-inbound-listen-posture-by-profile.md": ["identity_provider_hint", "recipient_hint"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_binding_hints_contract.py", "identity_provider_hint"],
        "docs/99-llm-runbook.md": ["docs/573-publish-session-audience-bound-shares-require-binding-hints.md", "tools/check_publish_session_binding_hints_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing audience-bound shares should carry binding hints", "docs/573-publish-session-audience-bound-shares-require-binding-hints.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0163", "identity_provider_hint", "recipient_hint"],
        "docs/32-curated-references.md": ["ngrok secure your applications with OAuth 2.0"],
        "README.md": ["docs/573-publish-session-audience-bound-shares-require-binding-hints.md", "identity_provider_hint"],
        "docs/00-index.md": ["docs/573-publish-session-audience-bound-shares-require-binding-hints.md", "identity_provider_hint"],
        "CHANGELOG.md": ["ADR-0163", "docs/573-publish-session-audience-bound-shares-require-binding-hints.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session binding-hints token: {needle}")

    if errors:
        print("Publish-session audience-binding hints contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session audience-binding hints contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
