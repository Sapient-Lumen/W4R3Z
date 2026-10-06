#!/usr/bin/env python3
"""Guardrail for publish-session redacted locator + separate secret handoff posture."""
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
    secret_handoff = props.get("secret_handoff") or {}
    if secret_handoff.get("type") != "object":
        errors.append("spec/net.publish.session.schema.json must define published_endpoint.secret_handoff as an object")
    if ((secret_handoff.get("properties") or {}).get("delivery") or {}).get("const") != "separate-secret-receipt":
        errors.append("spec/net.publish.session.schema.json must keep secret_handoff.delivery fixed to separate-secret-receipt")
    if "secret_receipt_digest" not in (secret_handoff.get("required") or []):
        errors.append("spec/net.publish.session.schema.json must require secret_handoff.secret_receipt_digest")
    endpoint = example.get("published_endpoint") or {}
    if '?' in endpoint.get("url_hint", "") or '#' in endpoint.get("url_hint", ""):
        errors.append("publish-session url_hint must stay free of query/fragment bearer material")
    if '?' in endpoint.get("path_prefix", "") or '#' in endpoint.get("path_prefix", ""):
        errors.append("publish-session path_prefix must stay free of query/fragment bearer material")
    audience = endpoint.get("audience") or {}
    handoff = endpoint.get("secret_handoff") or {}
    if audience.get("authn_mode") in {"single-use-secret", "shared-secret"}:
        if handoff.get("delivery") != "separate-secret-receipt":
            errors.append("secret-gated publish-session example must use secret_handoff.delivery = separate-secret-receipt")
        if not handoff.get("secret_receipt_digest"):
            errors.append("secret-gated publish-session example must carry secret_handoff.secret_receipt_digest")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["secret_handoff", "query token"],
        "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md": ["`published_endpoint.secret_handoff`", "separate-secret-receipt"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["secret.receipt", "bearer URL"],
        "docs/460-inbound-listen-posture-by-profile.md": ["secret.receipt", "share URL"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_secret_handoff_contract.py", "secret_handoff.secret_receipt_digest"],
        "docs/99-llm-runbook.md": ["docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md", "tools/check_publish_session_secret_handoff_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing secrets should travel separately from the locator", "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0156", "query-token URLs"],
        "README.md": ["docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md", "secret.receipt"],
        "docs/00-index.md": ["docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md", "secret-handoff posture"],
        "CHANGELOG.md": ["ADR-0156", "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session secret-handoff token: {needle}")
    if errors:
        print("Publish-session secret-handoff contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session secret-handoff contract check OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
