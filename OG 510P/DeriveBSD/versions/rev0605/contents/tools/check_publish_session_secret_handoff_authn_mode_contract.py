#!/usr/bin/env python3
"""Guardrail for publish-session secret_handoff/authn_mode coherence."""
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

    handoff = ((example.get("published_endpoint") or {}).get("secret_handoff") or {})
    audience = ((example.get("published_endpoint") or {}).get("audience") or {})
    if audience.get("authn_mode") not in {"single-use-secret", "shared-secret"}:
        errors.append("publish-session example must keep secret_handoff on a secret-gated authn_mode lane")
    if not handoff.get("secret_receipt_digest"):
        errors.append("publish-session example must keep secret_handoff.secret_receipt_digest")

    public_link_bad = deepcopy(example)
    public_link_bad["session_id"] = "publish-public-link-7c3f"
    public_link_bad["published_endpoint"]["audience"] = {"class": "public-link", "authn_mode": "none"}
    public_link_bad["published_endpoint"].pop("path_prefix", None)
    public_link_bad["published_endpoint"]["path_prefix"] = "/share/demo"
    public_link_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/share/demo"
    if not validate(validator, public_link_bad):
        errors.append("public-link publish session carrying secret_handoff must fail validation")

    provider_bad = deepcopy(example)
    provider_bad["session_id"] = "publish-provider-7c3f"
    provider_bad["published_endpoint"]["audience"] = {
        "class": "organization-users",
        "authn_mode": "provider-identity",
        "identity_provider_hint": "derive-sso"
    }
    if not validate(validator, provider_bad):
        errors.append("provider-identity publish session carrying secret_handoff must fail validation")

    support_bad = deepcopy(example)
    support_bad["session_id"] = "publish-support-7c3f"
    support_bad["published_endpoint"].pop("hostname", None)
    support_bad["published_endpoint"].pop("port", None)
    support_bad["published_endpoint"].pop("url_hint", None)
    support_bad["published_endpoint"].pop("path_prefix", None)
    support_bad["published_endpoint"]["exposure_scope"] = "support-peer"
    support_bad["published_endpoint"]["access_model"] = "peer-relay"
    support_bad["published_endpoint"]["audience"] = {
        "class": "support-session-peer",
        "authn_mode": "support-session"
    }
    support_bad["authority"]["trigger"] = "support-session"
    support_bad["authority"].pop("consent_receipt_digest", None)
    support_bad["authority"]["support_session_digest"] = "sha256:" + "99" * 32
    ends = set(support_bad["lifecycle"]["end_conditions"])
    ends.discard("initiating-user-session-end")
    ends.add("support-session-end")
    support_bad["lifecycle"]["end_conditions"] = sorted(ends)
    support_bad["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/publish-7c3f"}
    support_bad["relay"]["destination_hint"] = "support-session/publish-7c3f"
    if not validate(validator, support_bad):
        errors.append("support-session publish session carrying secret_handoff must fail validation")

    single_use_ok = deepcopy(example)
    single_use_ok["session_id"] = "publish-single-use-7c3f"
    single_use_ok["published_endpoint"]["audience"] = {
        "class": "named-recipients",
        "authn_mode": "single-use-secret",
        "recipient_hint": "support+alice@example.invalid"
    }
    single_use_ok["published_endpoint"]["secret_handoff"]["consumption_posture"] = "single-successful-admission"
    if validate(validator, single_use_ok):
        errors.append("single-use-secret publish session with secret_handoff should validate")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["`secret_handoff` now also follows `audience.authn_mode` exactly", "docs/589-publish-session-secret-handoffs-follow-authn-mode.md"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["Non-secret authn modes must not carry `secret_handoff`", "docs/589-publish-session-secret-handoffs-follow-authn-mode.md"],
        "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md": ["`secret_handoff` now also follows `audience.authn_mode` exactly", "provider-identity"],
        "docs/568-publish-session-secret-consumption-semantics-boundary.md": ["`secret_handoff` is now reserved to secret authn modes only", "docs/589-publish-session-secret-handoffs-follow-authn-mode.md"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["`secret_handoff` now also follows `audience.authn_mode` exactly", "provider-identity"],
        "docs/460-inbound-listen-posture-by-profile.md": ["non-secret authn modes now keep `secret_handoff` absent", "docs/589-publish-session-secret-handoffs-follow-authn-mode.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_secret_handoff_authn_mode_contract.py", "`authn_mode` stays singular"],
        "docs/99-llm-runbook.md": ["docs/589-publish-session-secret-handoffs-follow-authn-mode.md", "tools/check_publish_session_secret_handoff_authn_mode_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing secret handoffs should follow authn_mode exactly", "docs/589-publish-session-secret-handoffs-follow-authn-mode.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0179", "second hidden secret lane"],
        "README.md": ["docs/589-publish-session-secret-handoffs-follow-authn-mode.md", "`authn_mode` singular"],
        "docs/00-index.md": ["docs/589-publish-session-secret-handoffs-follow-authn-mode.md", "secret-handoff/authn-mode posture"],
        "CHANGELOG.md": ["ADR-0179", "docs/589-publish-session-secret-handoffs-follow-authn-mode.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session secret-handoff/authn token: {needle}")

    if errors:
        print("Publish-session secret-handoff/authn-mode contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session secret-handoff/authn-mode contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
