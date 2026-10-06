#!/usr/bin/env python3
"""Guardrail for publish-session public-webhook validation-hint posture."""
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

    webhook_ok = deepcopy(example)
    webhook_ok["session_id"] = "publish-webhook-validate-hint-7c3f"
    webhook_ok["published_endpoint"]["audience"]["class"] = "public-webhook"
    webhook_ok["published_endpoint"]["audience"]["authn_mode"] = "shared-secret"
    webhook_ok["published_endpoint"]["audience"]["validation_hint"] = "x-hub-signature-256"
    if validate(validator, webhook_ok):
        errors.append("public-webhook publish session with validation_hint should validate")

    webhook_missing = deepcopy(webhook_ok)
    webhook_missing["published_endpoint"]["audience"].pop("validation_hint", None)
    if not validate(validator, webhook_missing):
        errors.append("public-webhook publish session without validation_hint must fail validation")

    webhook_provider_ok = deepcopy(example)
    webhook_provider_ok["session_id"] = "publish-webhook-provider-validation-7c3f"
    webhook_provider_ok["published_endpoint"]["audience"]["class"] = "public-webhook"
    webhook_provider_ok["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    webhook_provider_ok["published_endpoint"]["audience"]["identity_provider_hint"] = "cloudflare-access"
    webhook_provider_ok["published_endpoint"]["audience"]["validation_hint"] = "cf-access-jwt-assertion"
    webhook_provider_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, webhook_provider_ok):
        errors.append("provider-identity public-webhook publish session with validation_hint should validate")

    public_link_ok = deepcopy(example)
    public_link_ok["session_id"] = "publish-public-link-no-validation-7c3f"
    public_link_ok["published_endpoint"]["audience"] = {"class": "public-link", "authn_mode": "none"}
    public_link_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, public_link_ok):
        errors.append("public-link publish session without validation_hint should still validate")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["validation_hint", "public-webhook"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["validation_hint", "docs/574-publish-session-public-webhook-shares-require-validation-hints.md"],
        "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md": ["published_endpoint.audience.validation_hint", "not bearer material"],
        "docs/574-publish-session-public-webhook-shares-require-validation-hints.md": ["validation_hint", "public-webhook"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["validation_hint", "public-webhook"],
        "docs/460-inbound-listen-posture-by-profile.md": ["validation_hint", "public-webhook"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_webhook_validation_contract.py", "validation_hint"],
        "docs/99-llm-runbook.md": ["docs/574-publish-session-public-webhook-shares-require-validation-hints.md", "tools/check_publish_session_webhook_validation_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing public-webhook shares should carry validation hints", "docs/574-publish-session-public-webhook-shares-require-validation-hints.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0164", "validation_hint"],
        "docs/32-curated-references.md": ["GitHub validating webhook deliveries", "Stripe webhook signature verification", "Cloudflare Access JWT validation"],
        "README.md": ["docs/574-publish-session-public-webhook-shares-require-validation-hints.md", "validation_hint"],
        "docs/00-index.md": ["docs/574-publish-session-public-webhook-shares-require-validation-hints.md", "validation_hint"],
        "CHANGELOG.md": ["ADR-0164", "docs/574-publish-session-public-webhook-shares-require-validation-hints.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session webhook-validation token: {needle}")

    if errors:
        print("Publish-session public-webhook validation-hint contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session public-webhook validation-hint contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
