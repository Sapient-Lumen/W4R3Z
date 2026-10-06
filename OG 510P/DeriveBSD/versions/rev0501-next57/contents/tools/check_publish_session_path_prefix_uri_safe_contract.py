#!/usr/bin/env python3
"""Guardrail for publish-session URI-path-safe path-prefix posture."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SEGMENT_CHARS = set("-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._~!$&'()*+,;=:@")


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def path_prefix_uri_safe_errors(doc: dict) -> list[str]:
    endpoint = doc.get("published_endpoint") or {}
    path_prefix = endpoint.get("path_prefix")
    if path_prefix is None:
        return []
    path = str(path_prefix)
    errors: list[str] = []
    if "%" in path:
        errors.append("published_endpoint.path_prefix must not carry percent-encoding")
    if " " in path:
        errors.append("published_endpoint.path_prefix must not carry raw spaces")
    if "\\" in path:
        errors.append("published_endpoint.path_prefix must not carry backslashes")
    for segment in path.split("/")[1:]:
        for ch in segment:
            if ch not in ALLOWED_SEGMENT_CHARS:
                errors.append("published_endpoint.path_prefix must use URI-path-safe literal segment characters")
                return errors
    if endpoint.get("access_model") == "relay-url" and endpoint.get("url_hint") and path_prefix:
        parsed = urlsplit(str(endpoint["url_hint"]))
        if parsed.path != path_prefix:
            errors.append("published_endpoint.url_hint path must equal the URI-path-safe published_endpoint.path_prefix")
    return errors


def validate_with_contract(validator: Draft202012Validator, doc: dict) -> list[str]:
    return validate(validator, doc) + path_prefix_uri_safe_errors(doc)


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
    relay_ok["session_id"] = "publish-uri-safe-path-7c3f"
    if validate_with_contract(validator, relay_ok):
        errors.append("relay-url share whose path_prefix is already URI-path-safe should validate")

    pct_bad = deepcopy(example)
    pct_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks/%2E%2E/admin"
    pct_bad["published_endpoint"]["path_prefix"] = "/hooks/%2E%2E/admin"
    if not validate_with_contract(validator, pct_bad):
        errors.append("publish-session example with percent-encoded path_prefix must fail validation")

    space_bad = deepcopy(example)
    space_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks/demo path"
    space_bad["published_endpoint"]["path_prefix"] = "/hooks/demo path"
    if not validate_with_contract(validator, space_bad):
        errors.append("publish-session example with raw-space path_prefix must fail validation")

    backslash_bad = deepcopy(example)
    backslash_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks\\demo"
    backslash_bad["published_endpoint"]["path_prefix"] = "/hooks\\demo"
    if not validate_with_contract(validator, backslash_bad):
        errors.append("publish-session example with backslash path_prefix must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["URI-path-safe", "path_prefix", "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md"],
        "docs/579-publish-session-url-hints-follow-endpoint-tuple.md": ["URI-path-safe", "path_prefix", "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md"],
        "docs/582-publish-session-path-prefixes-stay-normalized.md": ["docs/585-publish-session-path-prefixes-stay-uri-path-safe.md", "percent-encoding", "path_prefix"],
        "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md": ["URI-path-safe", "percent-encoding", "path_prefix"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["URI-path-safe", "path_prefix", "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["URI-path-safe", "path_prefix", "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_path_prefix_uri_safe_contract.py", "URI-path-safe", "path_prefix"],
        "docs/99-llm-runbook.md": ["docs/585-publish-session-path-prefixes-stay-uri-path-safe.md", "tools/check_publish_session_path_prefix_uri_safe_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing path prefixes should stay URI-path-safe", "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0175", "percent-decoding", "path_prefix"],
        "docs/32-curated-references.md": ["RFC 6943", "RFC 3986"],
        "README.md": ["docs/585-publish-session-path-prefixes-stay-uri-path-safe.md", "URI-path-safe", "path_prefix"],
        "docs/00-index.md": ["docs/585-publish-session-path-prefixes-stay-uri-path-safe.md", "URI-path-safe", "path_prefix"],
        "CHANGELOG.md": ["ADR-0175", "docs/585-publish-session-path-prefixes-stay-uri-path-safe.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session URI-path-safe token: {needle}")

    if errors:
        print("Publish-session URI-path-safe path-prefix posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session URI-path-safe path-prefix posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
