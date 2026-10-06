#!/usr/bin/env python3
"""Guardrail for publish-session relay uri-hint locators staying non-web-shaped."""
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


def uri_hint_shape_errors(doc: dict) -> list[str]:
    relay = doc.get("relay") or {}
    remote = relay.get("remote_locator") or {}
    if remote.get("kind") != "uri-hint":
        return []
    value = remote.get("value")
    if value is None:
        return []
    parsed = urlsplit(str(value))
    errors: list[str] = []
    if parsed.scheme.lower() in {"http", "https"}:
        errors.append("relay.remote_locator.value must not use http/https scheme when kind = uri-hint")
    if parsed.username is not None or parsed.password is not None:
        errors.append("relay.remote_locator.value must not carry userinfo when kind = uri-hint")
    if parsed.query:
        errors.append("relay.remote_locator.value must not carry query material when kind = uri-hint")
    if parsed.fragment:
        errors.append("relay.remote_locator.value must not carry fragment material when kind = uri-hint")
    hint = relay.get("destination_hint")
    if hint is not None and hint != value:
        errors.append("relay.destination_hint must equal relay.remote_locator.value exactly when kind = uri-hint")
    if hint is not None:
        parsed_hint = urlsplit(str(hint))
        if parsed_hint.scheme.lower() in {"http", "https"}:
            errors.append("relay.destination_hint must not use http/https scheme when kind = uri-hint")
        if parsed_hint.username is not None or parsed_hint.password is not None:
            errors.append("relay.destination_hint must not carry userinfo when kind = uri-hint")
        if parsed_hint.query:
            errors.append("relay.destination_hint must not carry query material when kind = uri-hint")
        if parsed_hint.fragment:
            errors.append("relay.destination_hint must not carry fragment material when kind = uri-hint")
    return errors


def validate_with_contract(validator: Draft202012Validator, doc: dict) -> list[str]:
    return validate(validator, doc) + uri_hint_shape_errors(doc)


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
    relay_ok["session_id"] = "publish-relay-uri-nonweb-7c3f"
    relay_ok["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "relay://preview-7c3f"}
    relay_ok["relay"]["destination_hint"] = "relay://preview-7c3f"
    if validate_with_contract(validator, relay_ok):
        errors.append("uri-hint relay locator using a non-web relay scheme should validate")

    https_bad = deepcopy(relay_ok)
    https_bad["relay"]["remote_locator"]["value"] = "https://preview-7c3f.relay.example.invalid:443/hooks/demo"
    https_bad["relay"]["destination_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks/demo"
    if not validate_with_contract(validator, https_bad):
        errors.append("uri-hint relay locator using https scheme must fail validation")

    userinfo_bad = deepcopy(relay_ok)
    userinfo_bad["relay"]["remote_locator"]["value"] = "relay://preview@preview-7c3f"
    userinfo_bad["relay"]["destination_hint"] = "relay://preview@preview-7c3f"
    if not validate_with_contract(validator, userinfo_bad):
        errors.append("uri-hint relay locator carrying userinfo must fail validation")

    query_bad = deepcopy(relay_ok)
    query_bad["relay"]["remote_locator"]["value"] = "relay://preview-7c3f?token=secret"
    query_bad["relay"]["destination_hint"] = "relay://preview-7c3f?token=secret"
    if not validate_with_contract(validator, query_bad):
        errors.append("uri-hint relay locator carrying query material must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["non-web-shaped", "relay.remote_locator.value", "docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md"],
        "docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md": ["docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md", "uri-hint", "http` / `https"],
        "docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md": ["non-web-shaped", "http` / `https`", "docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md"],
        "docs/578-publish-session-destination-hint-follows-remote-locator.md": ["docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md", "non-web-shaped", "destination_hint"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["non-web-shaped", "relay.remote_locator.value", "docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["non-web-shaped", "relay.remote_locator.value", "docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_remote_locator_uri_hint_contract.py", "non-web-shaped", "relay.remote_locator.value"],
        "docs/99-llm-runbook.md": ["docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md", "tools/check_publish_session_remote_locator_uri_hint_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing relay uri-hint locators should stay non-web-shaped", "docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0174", "http` / `https`", "relay.remote_locator.value"],
        "README.md": ["docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md", "non-web-shaped", "relay.remote_locator.value"],
        "docs/00-index.md": ["docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md", "non-web-shaped", "relay.remote_locator.value"],
        "CHANGELOG.md": ["ADR-0174", "docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session relay uri-hint token: {needle}")

    if errors:
        print("Publish-session relay uri-hint non-web-shaped locator contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session relay uri-hint non-web-shaped locator contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
