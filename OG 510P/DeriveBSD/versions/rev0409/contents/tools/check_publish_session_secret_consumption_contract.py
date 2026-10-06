#!/usr/bin/env python3
"""Guardrail for publish-session secret consumption semantics posture."""
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
    handoff_props = secret_handoff.get("properties") or {}
    if "consumption_posture" not in (secret_handoff.get("required") or []):
        errors.append("spec/net.publish.session.schema.json must require secret_handoff.consumption_posture")
    allowed = set((handoff_props.get("consumption_posture") or {}).get("enum") or [])
    missing = {"single-successful-admission", "reusable-until-expiry"} - allowed
    if missing:
        errors.append("spec/net.publish.session.schema.json secret_handoff.consumption_posture missing: " + ", ".join(sorted(missing)))

    endpoint = example.get("published_endpoint") or {}
    audience = endpoint.get("audience") or {}
    handoff = endpoint.get("secret_handoff") or {}
    mode = audience.get("authn_mode")
    posture = handoff.get("consumption_posture")
    if mode == "single-use-secret" and posture != "single-successful-admission":
        errors.append("single-use-secret publish-session example must use secret_handoff.consumption_posture = single-successful-admission")
    if mode == "shared-secret" and posture != "reusable-until-expiry":
        errors.append("shared-secret publish-session example must use secret_handoff.consumption_posture = reusable-until-expiry")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["consumption posture", "single-successful-admission", "reusable-until-expiry"],
        "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md": ["docs/568-publish-session-secret-consumption-semantics-boundary.md", "consumption_posture"],
        "docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md": ["docs/568-publish-session-secret-consumption-semantics-boundary.md", "single-successful-admission"],
        "docs/568-publish-session-secret-consumption-semantics-boundary.md": ["`single-use-secret`", "single-successful-admission", "reusable-until-expiry"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["single-successful-admission", "reusable-until-expiry"],
        "docs/460-inbound-listen-posture-by-profile.md": ["single-successful-admission", "reusable-until-expiry"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_secret_consumption_contract.py", "consumption_posture"],
        "docs/99-llm-runbook.md": ["docs/568-publish-session-secret-consumption-semantics-boundary.md", "tools/check_publish_session_secret_consumption_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing secret handoffs should distinguish single-use from reusable secrets", "docs/568-publish-session-secret-consumption-semantics-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0158", "single-successful-admission"],
        "docs/32-curated-references.md": ["Vault response wrapping", "use the presigned URL multiple times"],
        "README.md": ["docs/568-publish-session-secret-consumption-semantics-boundary.md", "single-successful-admission"],
        "docs/00-index.md": ["docs/568-publish-session-secret-consumption-semantics-boundary.md", "secret consumption semantics posture"],
        "CHANGELOG.md": ["ADR-0158", "docs/568-publish-session-secret-consumption-semantics-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session secret-consumption token: {needle}")

    if errors:
        print("Publish-session secret-consumption contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session secret-consumption contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
