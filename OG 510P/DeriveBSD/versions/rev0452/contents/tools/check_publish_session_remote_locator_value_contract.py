#!/usr/bin/env python3
"""Guardrail for publish-session relay remote-locator value posture by locator kind."""
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

    uri_ok = deepcopy(example)
    uri_ok["session_id"] = "publish-uri-value-7c3f"
    uri_ok["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "relay://preview-7c3f"}
    if validate(validator, uri_ok):
        errors.append("uri-hint remote locator with URI-shaped value should validate")

    uri_bad = deepcopy(uri_ok)
    uri_bad["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "support-session/7c3f"}
    if not validate(validator, uri_bad):
        errors.append("uri-hint remote locator with non-URI value must fail validation")

    uri_query_bad = deepcopy(uri_ok)
    uri_query_bad["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "relay://preview-7c3f?token=secret"}
    if not validate(validator, uri_query_bad):
        errors.append("uri-hint remote locator with query-bearing value must fail validation")

    peer_ok = deepcopy(example)
    peer_ok["session_id"] = "publish-support-portal-value-7c3f"
    peer_ok["published_endpoint"]["exposure_scope"] = "support-peer"
    peer_ok["published_endpoint"]["access_model"] = "peer-relay"
    peer_ok["published_endpoint"].pop("hostname", None)
    peer_ok["published_endpoint"].pop("port", None)
    peer_ok["published_endpoint"].pop("url_hint", None)
    peer_ok["published_endpoint"].pop("path_prefix", None)
    peer_ok["published_endpoint"]["audience"]["class"] = "support-session-peer"
    peer_ok["published_endpoint"]["audience"]["authn_mode"] = "support-session"
    peer_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    peer_ok["published_endpoint"].pop("secret_handoff", None)
    peer_ok["authority"]["trigger"] = "support-session"
    peer_ok["authority"].pop("consent_receipt_digest", None)
    peer_ok["authority"]["support_session_digest"] = "sha256:909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeaf"
    ends = set(peer_ok["lifecycle"]["end_conditions"])
    ends.add("support-session-end")
    peer_ok["lifecycle"]["end_conditions"] = sorted(ends)
    peer_ok["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/7c3f"}
    peer_ok["relay"]["destination_hint"] = "support-session/7c3f"
    if validate(validator, peer_ok):
        errors.append("portal-object remote locator with non-URI value should validate")

    peer_bad = deepcopy(peer_ok)
    peer_bad["relay"]["remote_locator"] = {"kind": "portal-object", "value": "https://support.example.invalid/session/7c3f"}
    if not validate(validator, peer_bad):
        errors.append("portal-object remote locator with URI-shaped value must fail validation")

    reverse_ok = deepcopy(example)
    reverse_ok["session_id"] = "publish-tailnet-object-path-value-7c3f"
    reverse_ok["published_endpoint"]["exposure_scope"] = "tailnet"
    reverse_ok["published_endpoint"]["access_model"] = "reverse-forward"
    reverse_ok["published_endpoint"]["hostname"] = "preview-workstation.tailnet.example.invalid"
    reverse_ok["published_endpoint"]["port"] = 8443
    reverse_ok["published_endpoint"].pop("url_hint", None)
    reverse_ok["published_endpoint"].pop("path_prefix", None)
    reverse_ok["published_endpoint"]["audience"]["class"] = "tailnet-users"
    reverse_ok["published_endpoint"]["audience"]["authn_mode"] = "tailnet-identity"
    reverse_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    reverse_ok["published_endpoint"]["locator_posture"] = "tailnet-device-name"
    reverse_ok["published_endpoint"].pop("secret_handoff", None)
    reverse_ok["relay"]["remote_locator"] = {"kind": "object-path", "value": "tailnet/preview-workstation:8443"}
    reverse_ok["relay"]["destination_hint"] = "tailnet/preview-workstation:8443"
    if validate(validator, reverse_ok):
        errors.append("object-path remote locator with non-URI value should validate")

    reverse_bad = deepcopy(reverse_ok)
    reverse_bad["relay"]["remote_locator"] = {"kind": "object-path", "value": "https://preview-workstation.tailnet.example.invalid:8443"}
    if not validate(validator, reverse_bad):
        errors.append("object-path remote locator with URI-shaped value must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["relay.remote_locator.value", "non-URI-shaped", "docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md"],
        "docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md": ["relay.remote_locator.value", "docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md"],
        "docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md": ["relay.remote_locator.value", "uri-hint", "non-URI-shaped"],
        "docs/570-publish-session-access-model-posture-boundary.md": ["relay.remote_locator.value", "non-URI-shaped"],
        "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md": ["relay.remote_locator.value", "object-path"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["relay.remote_locator.value", "non-URI-shaped"],
        "docs/460-inbound-listen-posture-by-profile.md": ["relay.remote_locator.value", "non-URI-shaped"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_remote_locator_value_contract.py", "relay.remote_locator.value"],
        "docs/99-llm-runbook.md": ["docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md", "tools/check_publish_session_remote_locator_value_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing relay remote locator values should follow locator kind", "docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0167", "relay.remote_locator.value"],
        "README.md": ["docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md", "relay.remote_locator.value"],
        "docs/00-index.md": ["docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md", "relay.remote_locator.value"],
        "CHANGELOG.md": ["ADR-0167", "docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session remote-locator-value token: {needle}")

    if errors:
        print("Publish-session remote-locator-value posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session remote-locator-value posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
