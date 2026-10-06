#!/usr/bin/env python3
"""Guardrail for publish-session locator posture and naming boundary."""
from __future__ import annotations
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
def load_json(rel: str) -> dict:
    return strict_load_json(ROOT, rel)
def main() -> int:
    errors=[]
    schema = load_json("spec/net.publish.session.schema.json")
    example = load_json("spec/examples/net.publish.session.json")
    errs = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.absolute_path))
    for e in errs[:20]:
        path = "/".join(str(x) for x in e.absolute_path) or "<root>"
        errors.append(f"spec/examples/net.publish.session.json invalid at {path}: {e.message}")
    published = (schema.get("properties", {}).get("published_endpoint") or {})
    if "locator_posture" not in (published.get("required") or []):
        errors.append("spec/net.publish.session.schema.json must require published_endpoint.locator_posture")
    enums = set((((published.get("properties") or {}).get("locator_posture") or {}).get("enum") or []))
    needed = {"session-scoped", "tailnet-device-name"}
    missing = sorted(needed - enums)
    if missing:
        errors.append("spec/net.publish.session.schema.json locator_posture missing: " + ", ".join(missing))
    endpoint = example.get("published_endpoint") or {}
    if endpoint.get("locator_posture") not in needed:
        errors.append("publish-session example must carry a recognized published_endpoint.locator_posture")
    if endpoint.get("exposure_scope") == "tailnet" and endpoint.get("locator_posture") != "tailnet-device-name":
        errors.append("tailnet publish-session example must stay tailnet-device-name scoped")
    if endpoint.get("exposure_scope") in {"organization", "internet", "support-peer"} and endpoint.get("locator_posture") != "session-scoped":
        errors.append("organization/internet/support-peer publish-session example must stay session-scoped")
    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["session-scoped", "durable ingress"],
        "docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md": ["session-scoped", "remembered public hostname"],
        "docs/565-publish-session-session-scoped-locator-posture-boundary.md": ["`published_endpoint.locator_posture`", "session-scoped"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["session-scoped", "reserved relay domains"],
        "docs/460-inbound-listen-posture-by-profile.md": ["session-scoped", "tailnet-device-name"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_locator_posture_contract.py", "session-scoped"],
        "docs/99-llm-runbook.md": ["docs/565-publish-session-session-scoped-locator-posture-boundary.md", "tools/check_publish_session_locator_posture_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should keep public locators session-scoped", "docs/565-publish-session-session-scoped-locator-posture-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0155", "reserved relay domains"],
        "README.md": ["docs/565-publish-session-session-scoped-locator-posture-boundary.md", "session-scoped"],
        "docs/00-index.md": ["docs/565-publish-session-session-scoped-locator-posture-boundary.md", "session-scoped"],
        "CHANGELOG.md": ["ADR-0155", "docs/565-publish-session-session-scoped-locator-posture-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session locator token: {needle}")
    if errors:
        print("Publish-session locator posture contract check FAILED:")
        [print(f"- {e}") for e in errors]
        return 1
    print("Publish-session locator posture contract check OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
