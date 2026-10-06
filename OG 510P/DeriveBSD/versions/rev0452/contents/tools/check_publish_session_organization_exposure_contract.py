#!/usr/bin/env python3
"""Guardrail for publish-session organization-user exposure posture."""
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
    org_ok["session_id"] = "publish-org-users-organization-scope-7c3f"
    org_ok["published_endpoint"]["exposure_scope"] = "organization"
    org_ok["published_endpoint"]["audience"] = {
        "class": "organization-users",
        "authn_mode": "provider-identity",
        "identity_provider_hint": "corp-oidc",
    }
    org_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, org_ok):
        errors.append("organization-users publish session with exposure_scope=organization should validate")

    org_bad = deepcopy(org_ok)
    org_bad["session_id"] = "publish-org-users-internet-scope-7c3f"
    org_bad["published_endpoint"]["exposure_scope"] = "internet"
    if not validate(validator, org_bad):
        errors.append("organization-users publish session with exposure_scope=internet must fail validation")

    named_org_ok = deepcopy(example)
    named_org_ok["session_id"] = "publish-named-org-scope-7c3f"
    named_org_ok["published_endpoint"]["exposure_scope"] = "organization"
    named_org_ok["published_endpoint"]["audience"] = {
        "class": "named-recipients",
        "authn_mode": "provider-identity",
        "recipient_hint": "reviewer@example.invalid",
        "identity_provider_hint": "corp-oidc",
    }
    named_org_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, named_org_ok):
        errors.append("named-recipients publish session with exposure_scope=organization should remain valid")

    named_inet_ok = deepcopy(example)
    named_inet_ok["session_id"] = "publish-named-internet-scope-7c3f"
    named_inet_ok["published_endpoint"]["exposure_scope"] = "internet"
    named_inet_ok["published_endpoint"]["audience"] = {
        "class": "named-recipients",
        "authn_mode": "single-use-secret",
        "recipient_hint": "reviewer@example.invalid",
    }
    named_inet_ok["published_endpoint"]["secret_handoff"]["consumption_posture"] = "single-successful-admission"
    if validate(validator, named_inet_ok):
        errors.append("named-recipients publish session with exposure_scope=internet should remain valid")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["`organization-users` now also stays organization-scoped", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["`organization-users` now also requires `published_endpoint.exposure_scope = organization`", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
        "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md": ["`organization-users` now also stays `organization` scoped", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
        "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md": ["must be `organization`", "tools/check_publish_session_organization_exposure_contract.py"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["`organization-users` now also stays organization-scoped", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["`organization-users` now also stays organization-scoped", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_organization_exposure_contract.py", "organization-user exposure exactness"],
        "docs/99-llm-runbook.md": ["docs/593-publish-session-organization-user-shares-stay-organization-scoped.md", "tools/check_publish_session_organization_exposure_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing organization-user shares should stay organization-scoped", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0183", "`organization-users` can no longer say \"coworkers only\" while still claiming generic internet exposure"],
        "README.md": ["docs/593-publish-session-organization-user-shares-stay-organization-scoped.md", "organization-scoped"],
        "docs/00-index.md": ["docs/593-publish-session-organization-user-shares-stay-organization-scoped.md", "organization-user exposure posture"],
        "CHANGELOG.md": ["ADR-0183", "docs/593-publish-session-organization-user-shares-stay-organization-scoped.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required organization-user exposure token: {needle}")

    if errors:
        print("Publish-session organization-user exposure contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session organization-user exposure contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
