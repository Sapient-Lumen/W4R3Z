#!/usr/bin/env python3
"""Audit the const-heavy net.publish.session schema classification.

The schema-refactor backlog used to treat every const-heavy surface as likely
fixture debt.  That is wrong for net.publish.session: its many constants are a
runtime policy mesh for temporary service sharing, not exact fixture literals.
This checker keeps that distinction concrete by proving the schema leaves live
session identity, endpoint, authority, relay, and digest fields dynamic while
retaining the semantic posture constants that make the publish boundary safe.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "net.publish.session.schema.json"
EXAMPLE_PATH = ROOT / "spec" / "examples" / "net.publish.session.json"
HEX = "0123456789abcdef"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

DYNAMIC_FIELD_CASES = [
    ("session_id", "publish-different-session"),
    ("created_at", "2026-03-19T02:19:00Z"),
    ("subject.digest", "sha256:" + "b" * 64),
    ("subject.instance", "appvm-preview-18"),
    ("local_service.listen_receipt_digest", "sha256:" + "c" * 64),
    ("published_endpoint.hostname", "preview-alt.relay.example.invalid"),
    ("published_endpoint.url_hint", "https://preview-alt.relay.example.invalid:443/hooks/demo"),
    ("authority.lease_id", "lease-publish-alt"),
    ("authority.expires_at", "2026-03-19T04:18:00Z"),
    ("relay.destination_hint", "relay://preview-alt"),
    ("relay.remote_locator.value", "relay://preview-alt"),
]

REQUIRED_RUNTIME_CONSTS = {
    "kind": "net.publish.session",
    "session_version": "0.33",
    "properties.published_endpoint.properties.continuity_posture.const": "lease-frozen",
    "properties.evidence.properties.visible_indicator_posture.const": "durable-until-ended",
    "properties.evidence.properties.revocation_affordance_posture.const": "same-surface-durable-until-ended",
    "properties.evidence.properties.management_return_path_posture.const": "trusted-ui-persistent-until-ended",
    "properties.evidence.properties.management_return_binding.const": "lease-exact",
    "properties.lifecycle.properties.resume_policy.const": "new-session-with-fresh-authority",
    "properties.lifecycle.properties.post_end_access_posture.const": "explicit-ended-or-fresh-share",
    "properties.lifecycle.properties.post_end_management_return_posture.const": "exact-ended-state-if-followed",
}

PROHIBITED_FIXTURE_CONST_PATHS = [
    "properties.session_id.const",
    "properties.created_at.const",
    "properties.subject.properties.digest.const",
    "properties.subject.properties.instance.const",
    "properties.local_service.properties.listen_receipt_digest.const",
    "properties.published_endpoint.properties.hostname.const",
    "properties.published_endpoint.properties.url_hint.const",
    "properties.authority.properties.lease_id.const",
    "properties.authority.properties.expires_at.const",
    "properties.relay.properties.destination_hint.const",
    "properties.relay.properties.remote_locator.properties.value.const",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dotted_get(obj: dict, path: str):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def dotted_set(obj: dict, path: str, value) -> None:
    cur = obj
    parts = path.split(".")
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def count_consts(node) -> int:
    if isinstance(node, dict):
        return (1 if "const" in node else 0) + sum(count_consts(v) for v in node.values())
    if isinstance(node, list):
        return sum(count_consts(v) for v in node)
    return 0


def validator_accepts(validator: Draft202012Validator, obj: dict) -> bool:
    return not list(validator.iter_errors(obj))


def main() -> int:
    errors: list[str] = []
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)
    validator = Draft202012Validator(schema)

    const_count = count_consts(schema)
    if const_count < 100:
        errors.append(f"expected net.publish.session to remain visibly const-heavy for policy reasons; observed {const_count}")

    if not validator_accepts(validator, example):
        errors.append("canonical net.publish.session example must validate")

    # Exact fixture schemas freeze identifiers and timestamps.  This runtime
    # schema must not: mutate one live field at a time and ensure it still admits
    # a different valid session shape.
    for field, value in DYNAMIC_FIELD_CASES:
        candidate = copy.deepcopy(example)
        dotted_set(candidate, field, value)
        if not validator_accepts(validator, candidate):
            errors.append(f"runtime schema rejected dynamic field mutation {field}={value!r}")

    for path in PROHIBITED_FIXTURE_CONST_PATHS:
        if dotted_get(schema, path) is not None:
            errors.append(f"schema must not freeze fixture field at {path}")

    for path, expected in REQUIRED_RUNTIME_CONSTS.items():
        if "." not in path:
            observed = dotted_get(schema.get("properties", {}), f"{path}.const")
        else:
            observed = dotted_get(schema, path)
        if observed != expected:
            errors.append(f"runtime policy const {path} != {expected!r} (observed {observed!r})")

    for digest_path in [
        "subject.digest",
        "local_service.listen_receipt_digest",
        "authority.consent_receipt_digest",
        "relay.transport_policy_digest",
        "relay.transport_receipt_digest",
    ]:
        value = dotted_get(example, digest_path)
        if not isinstance(value, str) or not DIGEST_RE.match(value):
            errors.append(f"example digest field {digest_path} should remain sha256-like evidence, got {value!r}")

    required_tokens = {
        "docs/current/cube-schema-refactor-backlog.md": [
            "spec/net.publish.session.schema.json",
            "audited-runtime-policy-const-mesh",
        ],
        "spec/examples/cube.schema.refactor.backlog.json": [
            "spec/net.publish.session.schema.json",
            "audited-runtime-policy-const-mesh",
        ],
        "CHANGELOG.md": [
            "tools/check_net_publish_session_schema_classification.py",
            "audited-runtime-policy-const-mesh",
        ],
    }
    for rel, tokens in required_tokens.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel} missing required token: {token}")

    if errors:
        print("net.publish.session schema classification FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("net.publish.session schema classification OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
