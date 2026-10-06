#!/usr/bin/env python3
"""Guardrail for publish-session relay-url URL-hint coherence."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json
from urllib.parse import urlsplit
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return strict_load_json(ROOT, rel)


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def url_hint_contract_errors(doc: dict) -> list[str]:
    endpoint = (doc.get("published_endpoint") or {})
    if endpoint.get("access_model") != "relay-url":
        return []
    url_hint = endpoint.get("url_hint")
    path_prefix = endpoint.get("path_prefix")
    if url_hint is None and path_prefix is None:
        return []
    errors: list[str] = []
    if url_hint is None:
        errors.append("path_prefix requires url_hint for relay-url shares")
        return errors
    if path_prefix is None:
        errors.append("url_hint requires path_prefix for relay-url shares")
        return errors
    parsed = urlsplit(str(url_hint))
    if not parsed.scheme or not parsed.netloc or not parsed.hostname:
        errors.append("url_hint must be an absolute URI-shaped hint with authority")
        return errors
    hostname = endpoint.get("hostname")
    port = endpoint.get("port")
    parsed_port = parsed.port
    if parsed.hostname != hostname:
        errors.append("url_hint host must equal published_endpoint.hostname")
    if parsed_port != port:
        errors.append("url_hint port must equal published_endpoint.port")
    if parsed.path != path_prefix:
        errors.append("url_hint path must equal published_endpoint.path_prefix")
    return errors


def validate_with_contract(validator: Draft202012Validator, doc: dict) -> list[str]:
    return validate(validator, doc) + url_hint_contract_errors(doc)


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
    relay_ok["session_id"] = "publish-url-hint-tuple-7c3f"
    if validate_with_contract(validator, relay_ok):
        errors.append("relay-url share whose url_hint serializes hostname, port, and path_prefix should validate")

    missing_path = deepcopy(relay_ok)
    missing_path["published_endpoint"].pop("path_prefix", None)
    if not validate_with_contract(validator, missing_path):
        errors.append("relay-url share with url_hint but no path_prefix must fail validation")

    missing_url = deepcopy(relay_ok)
    missing_url["published_endpoint"].pop("url_hint", None)
    if not validate_with_contract(validator, missing_url):
        errors.append("relay-url share with path_prefix but no url_hint must fail validation")

    host_bad = deepcopy(relay_ok)
    host_bad["published_endpoint"]["url_hint"] = "https://other-preview.relay.example.invalid/hooks/demo"
    if not validate_with_contract(validator, host_bad):
        errors.append("relay-url share whose url_hint host differs from hostname must fail validation")

    port_bad = deepcopy(relay_ok)
    port_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:8443/hooks/demo"
    if not validate_with_contract(validator, port_bad):
        errors.append("relay-url share whose url_hint port differs from port must fail validation")

    path_bad = deepcopy(relay_ok)
    path_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid/other"
    if not validate_with_contract(validator, path_bad):
        errors.append("relay-url share whose url_hint path differs from path_prefix must fail validation")

    relative_bad = deepcopy(relay_ok)
    relative_bad["published_endpoint"]["url_hint"] = "/hooks/demo"
    if not validate_with_contract(validator, relative_bad):
        errors.append("relay-url share whose url_hint is not absolute must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["url_hint", "path_prefix", "docs/579-publish-session-url-hints-follow-endpoint-tuple.md"],
        "docs/570-publish-session-access-model-posture-boundary.md": ["url_hint", "path_prefix", "docs/579-publish-session-url-hints-follow-endpoint-tuple.md"],
        "docs/575-publish-session-endpoint-hints-follow-access-model.md": ["docs/579-publish-session-url-hints-follow-endpoint-tuple.md", "url_hint", "path_prefix"],
        "docs/578-publish-session-destination-hint-follows-remote-locator.md": ["docs/579-publish-session-url-hints-follow-endpoint-tuple.md", "url_hint"],
        "docs/579-publish-session-url-hints-follow-endpoint-tuple.md": ["url_hint", "path_prefix", "hostname", "port"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["url_hint", "path_prefix", "docs/579-publish-session-url-hints-follow-endpoint-tuple.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["url_hint", "path_prefix", "docs/579-publish-session-url-hints-follow-endpoint-tuple.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_url_hint_contract.py", "url_hint", "path_prefix"],
        "docs/99-llm-runbook.md": ["docs/579-publish-session-url-hints-follow-endpoint-tuple.md", "tools/check_publish_session_url_hint_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing URL hints should follow endpoint tuple", "docs/579-publish-session-url-hints-follow-endpoint-tuple.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0169", "url_hint", "path_prefix"],
        "docs/32-curated-references.md": ["RFC 3986", "WHATWG URL Standard"],
        "README.md": ["docs/579-publish-session-url-hints-follow-endpoint-tuple.md", "url_hint", "path_prefix"],
        "docs/00-index.md": ["docs/579-publish-session-url-hints-follow-endpoint-tuple.md", "url_hint", "path_prefix"],
        "CHANGELOG.md": ["ADR-0169", "docs/579-publish-session-url-hints-follow-endpoint-tuple.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session url-hint token: {needle}")

    if errors:
        print("Publish-session URL-hint posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session URL-hint posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
