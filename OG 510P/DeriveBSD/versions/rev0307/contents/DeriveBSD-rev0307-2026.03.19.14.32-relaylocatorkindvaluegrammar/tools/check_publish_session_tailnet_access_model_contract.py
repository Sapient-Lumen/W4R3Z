#!/usr/bin/env python3
"""Guardrail for publish-session tailnet reverse-forward posture boundary."""
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

    tailnet_ok = deepcopy(example)
    tailnet_ok["session_id"] = "tailnet-share-7c3f"
    tailnet_ok["published_endpoint"]["exposure_scope"] = "tailnet"
    tailnet_ok["published_endpoint"]["access_model"] = "reverse-forward"
    tailnet_ok["published_endpoint"]["hostname"] = "preview-workstation.tailnet.example.invalid"
    tailnet_ok["published_endpoint"]["port"] = 8443
    tailnet_ok["published_endpoint"].pop("url_hint", None)
    tailnet_ok["published_endpoint"].pop("path_prefix", None)
    tailnet_ok["published_endpoint"]["audience"]["class"] = "tailnet-users"
    tailnet_ok["published_endpoint"]["audience"]["authn_mode"] = "tailnet-identity"
    tailnet_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    tailnet_ok["published_endpoint"]["locator_posture"] = "tailnet-device-name"
    tailnet_ok["relay"]["remote_locator"] = {"kind": "object-path", "value": "tailnet/preview-workstation:8443"}
    tailnet_ok["published_endpoint"].pop("secret_handoff", None)
    if validate(validator, tailnet_ok):
        errors.append("tailnet publish session with access_model=reverse-forward should validate")

    tailnet_bad_model = deepcopy(tailnet_ok)
    tailnet_bad_model["published_endpoint"]["access_model"] = "relay-url"
    if not validate(validator, tailnet_bad_model):
        errors.append("tailnet publish session with access_model=relay-url must fail validation")

    tailnet_bad_scope = deepcopy(tailnet_ok)
    tailnet_bad_scope["published_endpoint"]["exposure_scope"] = "internet"
    if not validate(validator, tailnet_bad_scope):
        errors.append("tailnet-users/tailnet-identity/tailnet-device-name posture must fail outside exposure_scope=tailnet")

    tailnet_bad_locator = deepcopy(tailnet_ok)
    tailnet_bad_locator["published_endpoint"]["locator_posture"] = "session-scoped"
    if not validate(validator, tailnet_bad_locator):
        errors.append("tailnet publish session with locator_posture=session-scoped must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["tailnet", "reverse-forward", "tailnet-device-name"],
        "docs/565-publish-session-session-scoped-locator-posture-boundary.md": ["tailnet-device-name", "reverse-forward", "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md"],
        "docs/570-publish-session-access-model-posture-boundary.md": ["tailnet", "reverse-forward", "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md"],
        "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md": ["tailnet-users", "reverse-forward", "tailnet-device-name"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["tailnet", "reverse-forward"],
        "docs/460-inbound-listen-posture-by-profile.md": ["tailnet", "reverse-forward"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_tailnet_access_model_contract.py", "reverse-forward"],
        "docs/99-llm-runbook.md": ["docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md", "tools/check_publish_session_tailnet_access_model_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should keep tailnet publication reverse-forward-shaped", "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0161", "reverse-forward"],
        "README.md": ["docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md", "reverse-forward"],
        "docs/00-index.md": ["docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md", "reverse-forward"],
        "CHANGELOG.md": ["ADR-0161", "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session tailnet token: {needle}")

    if errors:
        print("Publish-session tailnet reverse-forward posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session tailnet reverse-forward posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
