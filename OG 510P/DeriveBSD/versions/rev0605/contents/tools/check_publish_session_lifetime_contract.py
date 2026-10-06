#!/usr/bin/env python3
"""Guardrail for publish-session end conditions and no-auto-resume posture."""
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
    lifecycle = schema.get("properties", {}).get("lifecycle") or {}
    if "lifecycle" not in (schema.get("required") or []):
        errors.append("spec/net.publish.session.schema.json must require lifecycle")
    props = lifecycle.get("properties") or {}
    ends = set((((props.get("end_conditions") or {}).get("items") or {}).get("enum") or []))
    required_ends = {"lease-expiry","manual-revoke","local-service-unavailable","host-reboot","initiating-user-session-end","support-session-end","operator-session-end","maintenance-window-end"}
    missing = sorted(required_ends - ends)
    if missing:
        errors.append("spec/net.publish.session.schema.json lifecycle.end_conditions missing: " + ", ".join(missing))
    if (props.get("resume_policy") or {}).get("const") != "new-session-with-fresh-authority":
        errors.append("spec/net.publish.session.schema.json must keep resume_policy fixed to new-session-with-fresh-authority")
    life_ex = example.get("lifecycle") or {}
    ex_ends = set(life_ex.get("end_conditions") or [])
    for end in ["lease-expiry","manual-revoke","local-service-unavailable","host-reboot"]:
        if end not in ex_ends:
            errors.append(f"publish-session example must include lifecycle.end_conditions containing {end}")
    if life_ex.get("resume_policy") != "new-session-with-fresh-authority":
        errors.append("publish-session example must keep resume_policy = new-session-with-fresh-authority")
    if ((example.get("authority") or {}).get("trigger") == "trusted-ui") and "initiating-user-session-end" not in ex_ends:
        errors.append("trusted-ui publish-session example must end on initiating-user-session-end")
    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["reboot-cleared", "new-session-with-fresh-authority"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["no-auto-resume", "reboot-cleared"],
        "docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md": ["`net.publish.session.lifecycle`", "new-session-with-fresh-authority"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["reboot-cleared", "docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["reboot-cleared", "new-session-with-fresh-authority"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_lifetime_contract.py", "new-session-with-fresh-authority"],
        "docs/99-llm-runbook.md": ["docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md", "tools/check_publish_session_lifetime_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should be reboot-cleared and no-auto-resume by default", "docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0154", "reboot-cleared"],
        "README.md": ["docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md", "reboot-cleared"],
        "docs/00-index.md": ["docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md", "new-session-with-fresh-authority"],
        "CHANGELOG.md": ["ADR-0154", "docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session lifetime token: {needle}")
    if errors:
        print("Publish-session lifetime contract check FAILED:")
        [print(f"- {e}") for e in errors]
        return 1
    print("Publish-session lifetime contract check OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
