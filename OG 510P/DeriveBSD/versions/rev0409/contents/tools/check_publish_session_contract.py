#!/usr/bin/env python3
"""Guardrail for the relay-backed publish-session boundary.

Keeps temporary service sharing distinct from durable host ingress:
- `net.publish.session` must exist and validate
- canonical example must stay local-first + leased + transport-joined
- discovery docs must keep the boundary wired
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

    if example.get("kind") != "net.publish.session":
        errors.append("spec/examples/net.publish.session.json kind must stay net.publish.session")
    local = example.get("local_service") or {}
    if local.get("bind_scope") not in {"loopback-only", "broker-held-loopback"}:
        errors.append("publish-session example must stay local-first (loopback-only or broker-held-loopback)")
    auth = example.get("authority") or {}
    if auth.get("trigger") == "trusted-ui" and not auth.get("consent_receipt_digest"):
        errors.append("trusted-ui publish-session example must carry consent_receipt_digest")
    if not auth.get("expires_at"):
        errors.append("publish-session example must carry authority.expires_at")
    relay = example.get("relay") or {}
    if not relay.get("transport_policy_digest") or not relay.get("transport_receipt_digest"):
        errors.append("publish-session example must carry relay transport digests")
    endpoint = example.get("published_endpoint") or {}
    if endpoint.get("access_model") == "relay-url" and not endpoint.get("url_hint"):
        errors.append("relay-url publish-session example must carry published_endpoint.url_hint")

    doc_checks = {
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["`net.publish.session`", "temporary sharing"],
        "docs/460-inbound-listen-posture-by-profile.md": ["`net.publish.session`", "relay-backed publish session"],
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["`net.publish.session`", "relay-backed publish session", "temporary sharing"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_contract.py", "net.publish.session"],
        "docs/99-llm-runbook.md": ["docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md", "tools/check_publish_session_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should be relay-backed publish sessions", "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0152", "net.publish.session"],
        "README.md": ["docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md", "spec/net.publish.session.schema.json"],
        "docs/00-index.md": ["docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md", "spec/net.publish.session.schema.json"],
        "CHANGELOG.md": ["ADR-0152", "spec/net.publish.session.schema.json"],
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

    print("Publish-session contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
