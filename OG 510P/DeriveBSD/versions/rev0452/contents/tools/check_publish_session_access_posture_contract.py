#!/usr/bin/env python3
"""Guardrail for publish-session audience/publicness posture.

Keeps relay-backed temporary sharing from collapsing into anonymous-public-by-default behavior:
- `net.publish.session` must require `published_endpoint.audience`
- canonical example must keep an explicit audience class + authn mode
- public-link / public-webhook / support-peer / tailnet combinations must stay typed
- discovery docs must keep the audience/publicness boundary wired
"""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    schema = load_json("spec/net.publish.session.schema.json")
    example = load_json("spec/examples/net.publish.session.json")
    errs = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.absolute_path))
    for e in errs[:20]:
        path = "/".join(str(x) for x in e.absolute_path) or "<root>"
        errors.append(f"spec/examples/net.publish.session.json invalid at {path}: {e.message}")
    if len(errs) > 20:
        errors.append(f"spec/examples/net.publish.session.json invalid with {len(errs) - 20} additional errors")

    published = (schema.get("properties", {}).get("published_endpoint") or {})
    props = published.get("properties") or {}
    audience = props.get("audience") or {}
    if "audience" not in (published.get("required") or []):
        errors.append("spec/net.publish.session.schema.json must require published_endpoint.audience")
    if audience.get("type") != "object":
        errors.append("spec/net.publish.session.schema.json must define published_endpoint.audience as an object")

    aud_props = audience.get("properties") or {}
    classes = set((aud_props.get("class") or {}).get("enum") or [])
    authn_modes = set((aud_props.get("authn_mode") or {}).get("enum") or [])
    required_classes = {
        "tailnet-users",
        "organization-users",
        "named-recipients",
        "support-session-peer",
        "public-webhook",
        "public-link",
    }
    required_authn = {
        "tailnet-identity",
        "provider-identity",
        "support-session",
        "single-use-secret",
        "shared-secret",
        "none",
    }
    missing_classes = sorted(required_classes - classes)
    missing_authn = sorted(required_authn - authn_modes)
    if missing_classes:
        errors.append(f"spec/net.publish.session.schema.json audience.class missing: {', '.join(missing_classes)}")
    if missing_authn:
        errors.append(f"spec/net.publish.session.schema.json audience.authn_mode missing: {', '.join(missing_authn)}")

    endpoint = example.get("published_endpoint") or {}
    audience_ex = endpoint.get("audience") or {}
    if audience_ex.get("class") not in required_classes:
        errors.append("publish-session example must carry a recognized published_endpoint.audience.class")
    if audience_ex.get("authn_mode") not in required_authn:
        errors.append("publish-session example must carry a recognized published_endpoint.audience.authn_mode")
    if audience_ex.get("class") == "public-link" and audience_ex.get("authn_mode") != "none":
        errors.append("public-link publish-session example must stay explicitly unauthenticated")
    if audience_ex.get("class") == "public-webhook" and audience_ex.get("authn_mode") not in {"shared-secret", "provider-identity"}:
        errors.append("public-webhook publish-session example must stay on shared-secret or provider-identity auth")
    if endpoint.get("exposure_scope") == "support-peer" and audience_ex.get("class") != "support-session-peer":
        errors.append("support-peer publish-session example must stay support-session-peer scoped")
    if endpoint.get("exposure_scope") == "tailnet" and audience_ex.get("class") != "tailnet-users":
        errors.append("tailnet publish-session example must stay tailnet-users scoped")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["audience", "public-link", "public-webhook"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["`net.publish.session.published_endpoint.audience`", "public-link", "public-webhook"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["audience-bound", "public-link"],
        "docs/460-inbound-listen-posture-by-profile.md": ["organization-users", "public-link"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_access_posture_contract.py", "public-link"],
        "docs/99-llm-runbook.md": ["docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md", "tools/check_publish_session_access_posture_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should be audience-bound by default", "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0153", "public-webhook"],
        "README.md": ["docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md", "public-link"],
        "docs/00-index.md": ["docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md", "public-link"],
        "CHANGELOG.md": ["ADR-0153", "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print("Publish-session access-posture contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
