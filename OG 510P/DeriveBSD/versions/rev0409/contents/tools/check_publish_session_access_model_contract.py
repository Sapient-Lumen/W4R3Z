#!/usr/bin/env python3
"""Guardrail for publish-session access-model posture boundary."""
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

    access_enum = set((((schema.get("properties") or {}).get("published_endpoint") or {}).get("properties") or {}).get("access_model", {}).get("enum") or [])
    for need in {"relay-url", "peer-relay", "reverse-forward"}:
        if need not in access_enum:
            errors.append(f"spec/net.publish.session.schema.json access_model missing {need}")

    public_ok = deepcopy(example)
    public_ok["published_endpoint"]["audience"]["class"] = "public-webhook"
    public_ok["published_endpoint"]["audience"]["authn_mode"] = "shared-secret"
    public_ok["published_endpoint"]["access_model"] = "relay-url"
    public_ok["relay"]["remote_locator"] = {"kind": "uri-hint", "value": "relay://preview-7c3f"}
    if validate(validator, public_ok):
        errors.append("canonical public-webhook publish session with access_model=relay-url should validate")

    public_bad = deepcopy(public_ok)
    public_bad["published_endpoint"]["access_model"] = "peer-relay"
    if not validate(validator, public_bad):
        errors.append("public-webhook publish session with access_model=peer-relay must fail validation")

    link_ok = deepcopy(example)
    link_ok["published_endpoint"]["audience"]["class"] = "public-link"
    link_ok["published_endpoint"]["audience"]["authn_mode"] = "none"
    link_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    link_ok["published_endpoint"]["audience"].pop("identity_provider_hint", None)
    link_ok["published_endpoint"]["audience"].pop("recipient_hint", None)
    link_ok["published_endpoint"].pop("secret_handoff", None)
    link_ok["published_endpoint"]["access_model"] = "relay-url"
    if validate(validator, link_ok):
        errors.append("public-link publish session with access_model=relay-url should validate")

    link_bad = deepcopy(link_ok)
    link_bad["published_endpoint"]["access_model"] = "peer-relay"
    if not validate(validator, link_bad):
        errors.append("public-link publish session with access_model=peer-relay must fail validation")

    support_ok = deepcopy(example)
    support_ok["session_id"] = "support-share-7c3f"
    support_ok["published_endpoint"]["exposure_scope"] = "support-peer"
    support_ok["published_endpoint"]["access_model"] = "peer-relay"
    support_ok["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/7c3f"}
    support_ok["relay"]["destination_hint"] = "support-session/7c3f"
    support_ok["published_endpoint"]["audience"]["class"] = "support-session-peer"
    support_ok["published_endpoint"]["audience"]["authn_mode"] = "support-session"
    support_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    support_ok["published_endpoint"].pop("secret_handoff", None)
    for key in ["hostname", "port", "url_hint", "path_prefix"]:
        support_ok["published_endpoint"].pop(key, None)
    support_ok["authority"]["trigger"] = "support-session"
    support_ok["authority"].pop("consent_receipt_digest", None)
    support_ok["authority"]["support_session_digest"] = "sha256:909192939495969798999a9b9c9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeaf0"
    ends = set(support_ok["lifecycle"]["end_conditions"])
    ends.discard("initiating-user-session-end")
    ends.add("support-session-end")
    support_ok["lifecycle"]["end_conditions"] = sorted(ends)
    if validate(validator, support_ok):
        errors.append("support-peer publish session with access_model=peer-relay should validate")

    support_bad = deepcopy(support_ok)
    support_bad["published_endpoint"]["access_model"] = "relay-url"
    if not validate(validator, support_bad):
        errors.append("support-peer publish session with access_model=relay-url must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["access-model posture", "peer-relay", "relay-url"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["relay-url", "peer-relay", "docs/570-publish-session-access-model-posture-boundary.md"],
        "docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md": ["peer-relay", "docs/570-publish-session-access-model-posture-boundary.md"],
        "docs/570-publish-session-access-model-posture-boundary.md": ["public-webhook", "relay-url", "peer-relay"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["peer-relay", "relay-url"],
        "docs/460-inbound-listen-posture-by-profile.md": ["peer-relay", "relay-url"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_access_model_contract.py", "peer-relay"],
        "docs/99-llm-runbook.md": ["docs/570-publish-session-access-model-posture-boundary.md", "tools/check_publish_session_access_model_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should keep support-peer publication peer-relay-shaped", "docs/570-publish-session-access-model-posture-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0160", "peer-relay"],
        "README.md": ["docs/570-publish-session-access-model-posture-boundary.md", "peer-relay"],
        "docs/00-index.md": ["docs/570-publish-session-access-model-posture-boundary.md", "peer-relay"],
        "CHANGELOG.md": ["ADR-0160", "docs/570-publish-session-access-model-posture-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session access-model token: {needle}")

    if errors:
        print("Publish-session access-model posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session access-model posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
