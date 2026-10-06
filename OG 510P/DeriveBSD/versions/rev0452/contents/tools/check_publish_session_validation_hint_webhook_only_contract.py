#!/usr/bin/env python3
"""Guardrail for publish-session validation_hint webhook-only posture."""
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

    webhook_ok = deepcopy(example)
    webhook_ok["session_id"] = "publish-webhook-only-validation-hint-7c3f"
    webhook_ok["published_endpoint"]["audience"]["class"] = "public-webhook"
    webhook_ok["published_endpoint"]["audience"]["authn_mode"] = "shared-secret"
    webhook_ok["published_endpoint"]["audience"]["validation_hint"] = "x-signature-hmac-sha256"
    if validate(validator, webhook_ok):
        errors.append("public-webhook publish session with validation_hint should validate")

    public_link_bad = deepcopy(example)
    public_link_bad["session_id"] = "publish-public-link-spare-validation-hint-7c3f"
    public_link_bad["published_endpoint"]["audience"] = {
        "class": "public-link",
        "authn_mode": "none",
        "validation_hint": "x-signature-hmac-sha256",
    }
    public_link_bad["published_endpoint"].pop("secret_handoff", None)
    if not validate(validator, public_link_bad):
        errors.append("public-link publish session carrying validation_hint must fail validation")

    org_bad = deepcopy(example)
    org_bad["session_id"] = "publish-org-spare-validation-hint-7c3f"
    org_bad["published_endpoint"]["exposure_scope"] = "organization"
    org_bad["published_endpoint"]["audience"]["class"] = "organization-users"
    org_bad["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    org_bad["published_endpoint"]["audience"]["identity_provider_hint"] = "okta-example-com"
    org_bad["published_endpoint"]["audience"]["validation_hint"] = "group=design-reviewers"
    org_bad["published_endpoint"].pop("secret_handoff", None)
    if not validate(validator, org_bad):
        errors.append("organization-users publish session carrying validation_hint must fail validation")

    named_bad = deepcopy(example)
    named_bad["session_id"] = "publish-named-spare-validation-hint-7c3f"
    named_bad["published_endpoint"]["audience"]["class"] = "named-recipients"
    named_bad["published_endpoint"]["audience"]["authn_mode"] = "single-use-secret"
    named_bad["published_endpoint"]["audience"]["recipient_hint"] = "external-reviewer@example.invalid"
    named_bad["published_endpoint"]["audience"]["validation_hint"] = "single-use secret delivered out-of-band"
    named_bad["published_endpoint"]["secret_handoff"]["consumption_posture"] = "single-successful-admission"
    if not validate(validator, named_bad):
        errors.append("named-recipients publish session carrying validation_hint must fail validation")

    support_bad = deepcopy(example)
    support_bad["session_id"] = "publish-support-spare-validation-hint-7c3f"
    support_bad["published_endpoint"]["exposure_scope"] = "support-peer"
    support_bad["published_endpoint"]["access_model"] = "peer-relay"
    support_bad["published_endpoint"]["audience"] = {
        "class": "support-session-peer",
        "authn_mode": "support-session",
        "validation_hint": "x-signature-hmac-sha256",
    }
    support_bad["published_endpoint"].pop("hostname", None)
    support_bad["published_endpoint"].pop("port", None)
    support_bad["published_endpoint"].pop("url_hint", None)
    support_bad["published_endpoint"].pop("path_prefix", None)
    support_bad["published_endpoint"].pop("secret_handoff", None)
    support_bad["authority"]["trigger"] = "support-session"
    support_bad["authority"].pop("consent_receipt_digest", None)
    support_bad["authority"]["support_session_digest"] = "sha256:support-session-1234"
    support_bad["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/7c3f"}
    support_bad["relay"]["destination_hint"] = "support-session/7c3f"
    support_bad["lifecycle"]["end_conditions"] = ["support-session-end", "manual-revoke", "system-sleep"]
    if not validate(validator, support_bad):
        errors.append("support-session-peer publish session carrying validation_hint must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["stays webhook-only", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["keep `validation_hint` absent", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
        "docs/574-publish-session-public-webhook-shares-require-validation-hints.md": ["validation_hint` is present, the share must therefore also be `public-webhook`", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
        "docs/591-publish-session-validation-hints-stay-webhook-only.md": ["validation_hint` now stays **exact with the webhook lane**", "tools/check_publish_session_validation_hint_webhook_only_contract.py"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["stays webhook-only", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["stays webhook-only", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_validation_hint_webhook_only_contract.py", "`audience.validation_hint` webhook-only"],
        "docs/99-llm-runbook.md": ["docs/591-publish-session-validation-hints-stay-webhook-only.md", "tools/check_publish_session_validation_hint_webhook_only_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing validation hints should stay webhook-only", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0181", "`validation_hint` lane webhook-only"],
        "README.md": ["docs/591-publish-session-validation-hints-stay-webhook-only.md", "validation_hint` to stay webhook-only"],
        "docs/00-index.md": ["docs/591-publish-session-validation-hints-stay-webhook-only.md", "validation-hint exactness posture"],
        "CHANGELOG.md": ["ADR-0181", "docs/591-publish-session-validation-hints-stay-webhook-only.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required validation-hint exactness token: {needle}")

    if errors:
        print("Publish-session validation_hint webhook-only contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session validation_hint webhook-only contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
