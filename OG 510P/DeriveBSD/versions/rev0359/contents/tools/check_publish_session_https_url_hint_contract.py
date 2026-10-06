#!/usr/bin/env python3
"""Guardrail for publish-session relay-url https-shaped URL-hint posture."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def https_url_hint_errors(doc: dict) -> list[str]:
    endpoint = doc.get("published_endpoint") or {}
    if endpoint.get("access_model") != "relay-url":
        return []
    url_hint = endpoint.get("url_hint")
    if url_hint is None:
        return []
    parsed = urlsplit(str(url_hint))
    errors: list[str] = []
    if parsed.scheme != "https":
        errors.append("published_endpoint.url_hint must use https scheme for relay-url shares")
    if not parsed.netloc or not parsed.hostname:
        errors.append("published_endpoint.url_hint must carry an authority host for relay-url shares")
        return errors
    if parsed.username is not None or parsed.password is not None:
        errors.append("published_endpoint.url_hint must not carry userinfo for relay-url shares")
    if parsed.query:
        errors.append("published_endpoint.url_hint must not carry query material for relay-url shares")
    if parsed.fragment:
        errors.append("published_endpoint.url_hint must not carry fragment material for relay-url shares")
    return errors


def validate_with_contract(validator: Draft202012Validator, doc: dict) -> list[str]:
    return validate(validator, doc) + https_url_hint_errors(doc)


def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/net.publish.session.schema.json")
    example = load_json("spec/examples/net.publish.session.json")
    validator = Draft202012Validator(schema)

    errs = validate_with_contract(validator, example)
    for msg in errs[:20]:
        errors.append(f"spec/examples/net.publish.session.json invalid: {msg}")
    if len(errs) > 20:
        errors.append(f"spec/examples/net.publish.session.json invalid with {len(errs) - 20} additional errors")

    relay_ok = deepcopy(example)
    relay_ok["session_id"] = "publish-https-url-hint-7c3f"
    if validate_with_contract(validator, relay_ok):
        errors.append("relay-url share whose url_hint is https-shaped should validate")

    http_bad = deepcopy(relay_ok)
    http_bad["published_endpoint"]["url_hint"] = "http://preview-7c3f.relay.example.invalid:443/hooks/demo"
    if not validate_with_contract(validator, http_bad):
        errors.append("relay-url share whose url_hint uses http must fail validation")

    userinfo_bad = deepcopy(relay_ok)
    userinfo_bad["published_endpoint"]["url_hint"] = "https://preview@preview-7c3f.relay.example.invalid:443/hooks/demo"
    if not validate_with_contract(validator, userinfo_bad):
        errors.append("relay-url share whose url_hint carries userinfo must fail validation")

    fragment_bad = deepcopy(relay_ok)
    fragment_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks/demo#frag"
    if not validate_with_contract(validator, fragment_bad):
        errors.append("relay-url share whose url_hint carries fragment material must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["https-shaped", "url_hint", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
        "docs/575-publish-session-endpoint-hints-follow-access-model.md": ["https-shaped", "relay-url", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
        "docs/579-publish-session-url-hints-follow-endpoint-tuple.md": ["https-shaped", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
        "docs/583-publish-session-relay-url-hints-stay-https-shaped.md": ["https-shaped", "userinfo", "relay-url"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["https-shaped", "url_hint", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["https-shaped", "url_hint", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_https_url_hint_contract.py", "https-shaped", "url_hint"],
        "docs/99-llm-runbook.md": ["docs/583-publish-session-relay-url-hints-stay-https-shaped.md", "tools/check_publish_session_https_url_hint_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing relay-url hints should stay https-shaped", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0173", "userinfo", "relay.remote_locator.value"],
        "docs/32-curated-references.md": ["RFC 9110", "https", "userinfo"],
        "README.md": ["docs/583-publish-session-relay-url-hints-stay-https-shaped.md", "https-shaped", "url_hint"],
        "docs/00-index.md": ["docs/583-publish-session-relay-url-hints-stay-https-shaped.md", "https-shaped", "url_hint"],
        "CHANGELOG.md": ["ADR-0173", "docs/583-publish-session-relay-url-hints-stay-https-shaped.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session https url-hint token: {needle}")

    if errors:
        print("Publish-session relay-url https-shaped URL-hint posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session relay-url https-shaped URL-hint posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
