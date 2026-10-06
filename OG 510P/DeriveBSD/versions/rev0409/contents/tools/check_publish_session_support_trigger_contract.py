#!/usr/bin/env python3
"""Guardrail for publish-session support-session trigger shape coherence."""
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

    support_ok = deepcopy(example)
    support_ok["session_id"] = "publish-support-7c3f"
    support_ok["published_endpoint"]["exposure_scope"] = "support-peer"
    support_ok["published_endpoint"]["access_model"] = "peer-relay"
    support_ok["published_endpoint"]["audience"]["class"] = "support-session-peer"
    support_ok["published_endpoint"]["audience"]["authn_mode"] = "support-session"
    support_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    support_ok["published_endpoint"].pop("secret_handoff", None)
    for key in ["hostname", "port", "url_hint", "path_prefix"]:
        support_ok["published_endpoint"].pop(key, None)
    support_ok["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/7c3f"}
    support_ok["relay"]["destination_hint"] = "support-session/7c3f"
    support_ok["authority"]["trigger"] = "support-session"
    support_ok["authority"].pop("consent_receipt_digest", None)
    support_ok["authority"]["support_session_digest"] = "sha256:" + "90" * 32
    ends = set(support_ok["lifecycle"]["end_conditions"])
    ends.discard("initiating-user-session-end")
    ends.add("support-session-end")
    support_ok["lifecycle"]["end_conditions"] = sorted(ends)
    if validate(validator, support_ok):
        errors.append("support-session publish session with full support-peer shape should validate")

    public_drift = deepcopy(support_ok)
    public_drift["published_endpoint"]["exposure_scope"] = "internet"
    public_drift["published_endpoint"]["access_model"] = "relay-url"
    public_drift["published_endpoint"]["audience"]["class"] = "public-webhook"
    public_drift["published_endpoint"]["audience"]["authn_mode"] = "shared-secret"
    public_drift["published_endpoint"]["hostname"] = "preview-7c3f.relay.example.invalid"
    public_drift["published_endpoint"]["port"] = 443
    public_drift["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks/demo"
    public_drift["published_endpoint"]["path_prefix"] = "/hooks/demo"
    public_drift["published_endpoint"]["secret_handoff"] = {
        "delivery": "separate-secret-receipt",
        "secret_receipt_digest": "sha256:" + "a0" * 32,
        "lifetime_binding": "session-authority-bounded",
        "expires_at": "2026-03-19T03:18:00Z",
        "consumption_posture": "reusable-until-expiry",
    }
    public_drift["published_endpoint"]["audience"]["validation_hint"] = "x-signature-hmac-sha256"
    public_drift["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "relay://preview-7c3f"}
    public_drift["relay"]["destination_hint"] = "relay://preview-7c3f"
    if not validate(validator, public_drift):
        errors.append("support-session trigger on a relay-url public-webhook share must fail validation")

    org_drift = deepcopy(support_ok)
    org_drift["published_endpoint"]["exposure_scope"] = "organization"
    org_drift["published_endpoint"]["access_model"] = "relay-url"
    org_drift["published_endpoint"]["audience"]["class"] = "organization-users"
    org_drift["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    org_drift["published_endpoint"]["audience"]["identity_provider_hint"] = "oidc:corp-sso"
    org_drift["published_endpoint"]["hostname"] = "preview-7c3f.relay.example.invalid"
    org_drift["published_endpoint"]["port"] = 443
    org_drift["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/review"
    org_drift["published_endpoint"]["path_prefix"] = "/review"
    org_drift["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "relay://preview-7c3f"}
    org_drift["relay"]["destination_hint"] = "relay://preview-7c3f"
    if not validate(validator, org_drift):
        errors.append("support-session trigger on an organization-users relay-url share must fail validation")

    authn_drift = deepcopy(support_ok)
    authn_drift["published_endpoint"]["audience"]["authn_mode"] = "provider-identity"
    if not validate(validator, authn_drift):
        errors.append("support-session trigger without support-session audience authn_mode must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["support-session trigger itself now also stays support-peer shaped", "docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md"],
        "docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md": ["non-support share shape", "support-peer shaped all the way down"],
        "docs/570-publish-session-access-model-posture-boundary.md": ["support-peer lane instead of justifying a non-support `relay-url` share", "docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["support-session trigger itself now also stays support-peer shaped", "docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["fully support-peer shaped", "docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_support_trigger_contract.py", "support-session trigger itself now also stays support-peer shaped"],
        "docs/99-llm-runbook.md": ["docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md", "tools/check_publish_session_support_trigger_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing support-session triggers should stay support-peer-shaped", "docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0178", "support-session proof justify a non-support share shape"],
        "README.md": ["docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md", "support authority coherent", "justifying public callback/demo"],
        "docs/00-index.md": ["docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md", "support-session-trigger posture"],
        "CHANGELOG.md": ["ADR-0178", "docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session support-trigger token: {needle}")

    if errors:
        print("Publish-session support-trigger contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session support-trigger contract check OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
