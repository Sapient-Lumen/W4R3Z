#!/usr/bin/env python3
"""Guardrail for publish-session audience-bound human-share access-model posture."""
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

    org_ok = deepcopy(example)
    org_ok["session_id"] = "publish-org-preview-7c3f"
    org_ok["published_endpoint"]["exposure_scope"] = "organization"
    org_ok["published_endpoint"]["access_model"] = "relay-url"
    org_ok["published_endpoint"]["audience"]["class"] = "organization-users"
    org_ok["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    org_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    org_ok["published_endpoint"]["audience"]["identity_provider_hint"] = "corp-oidc"
    org_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, org_ok):
        errors.append("organization-users publish session with access_model=relay-url should validate")

    org_bad = deepcopy(org_ok)
    org_bad["published_endpoint"]["access_model"] = "peer-relay"
    if not validate(validator, org_bad):
        errors.append("organization-users publish session with access_model=peer-relay must fail validation")

    named_ok = deepcopy(example)
    named_ok["session_id"] = "publish-named-recipient-7c3f"
    named_ok["published_endpoint"]["exposure_scope"] = "internet"
    named_ok["published_endpoint"]["access_model"] = "relay-url"
    named_ok["published_endpoint"]["audience"]["class"] = "named-recipients"
    named_ok["published_endpoint"]["audience"]["authn_mode"] = "single-use-secret"
    named_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    named_ok["published_endpoint"]["audience"]["recipient_hint"] = "external-reviewer@example.invalid"
    named_ok["published_endpoint"]["secret_handoff"]["consumption_posture"] = "single-successful-admission"
    if validate(validator, named_ok):
        errors.append("named-recipients publish session with access_model=relay-url should validate")

    named_bad = deepcopy(named_ok)
    named_bad["published_endpoint"]["access_model"] = "reverse-forward"
    if not validate(validator, named_bad):
        errors.append("named-recipients publish session with access_model=reverse-forward must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["organization-users", "named-recipients", "relay-url"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["organization-users", "named-recipients", "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md"],
        "docs/570-publish-session-access-model-posture-boundary.md": ["organization-users", "named-recipients", "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md"],
        "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md": ["organization-users", "named-recipients", "relay-url"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["organization-users", "named-recipients", "relay-url"],
        "docs/460-inbound-listen-posture-by-profile.md": ["organization-users", "named-recipients", "relay-url"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_human_share_access_model_contract.py", "organization-users"],
        "docs/99-llm-runbook.md": ["docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md", "tools/check_publish_session_human_share_access_model_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should keep ordinary audience-bound human shares relay-url-shaped", "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0162", "organization-users", "named-recipients"],
        "README.md": ["docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md", "relay-url"],
        "docs/00-index.md": ["docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md", "named-recipients"],
        "CHANGELOG.md": ["ADR-0162", "docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session human-share token: {needle}")

    if errors:
        print("Publish-session audience-bound human-share access-model contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session audience-bound human-share access-model contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
