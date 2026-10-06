#!/usr/bin/env python3
"""Guardrail for publish-session lease-addressable authority."""
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

    if not ((example.get("authority") or {}).get("lease_id")):
        errors.append("publish-session example must carry authority.lease_id")

    missing_lease = deepcopy(example)
    missing_lease["authority"].pop("lease_id", None)
    if not validate(validator, missing_lease):
        errors.append("publish-session without authority.lease_id must fail validation")

    policy_ok = deepcopy(example)
    policy_ok["session_id"] = "publish-policy-lease-check"
    policy_ok["authority"]["trigger"] = "policy"
    policy_ok["authority"]["policy_decision_digest"] = "sha256:" + "91" * 32
    policy_ok["authority"].pop("consent_receipt_digest", None)
    policy_ok["authority"]["lease_id"] = "lease-publish-policy-7c3f"
    if validate(validator, policy_ok):
        errors.append("policy-triggered publish session with authority.lease_id should validate")

    maintenance_ok = deepcopy(example)
    maintenance_ok["session_id"] = "publish-maint-window"
    maintenance_ok["authority"].pop("consent_receipt_digest", None)
    maintenance_ok["authority"]["trigger"] = "maintenance"
    maintenance_ok["authority"]["lease_id"] = "lease-publish-maint-7c3f"
    maintenance_ok["lifecycle"]["end_conditions"] = sorted(set(maintenance_ok["lifecycle"]["end_conditions"]) | {"maintenance-window-end"})
    if validate(validator, maintenance_ok):
        errors.append("maintenance-shaped publish session with authority.lease_id and maintenance-window-end should validate")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["`lease_id` / `expires_at`", "docs/587-publish-session-authority-stays-lease-addressable.md"],
        "docs/587-publish-session-authority-stays-lease-addressable.md": ["authority.lease_id", "lease-addressable", "docs/249-lease-registry-and-cross-lane-revocation.md"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["authority.lease_id", "docs/587-publish-session-authority-stays-lease-addressable.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["authority.lease_id", "docs/587-publish-session-authority-stays-lease-addressable.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_lease_id_contract.py", "authority.lease_id"],
        "docs/99-llm-runbook.md": ["docs/587-publish-session-authority-stays-lease-addressable.md", "tools/check_publish_session_lease_id_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing should stay lease-addressable", "docs/587-publish-session-authority-stays-lease-addressable.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0177", "authority.lease_id"],
        "README.md": ["docs/587-publish-session-authority-stays-lease-addressable.md", "authority.lease_id"],
        "docs/00-index.md": ["docs/587-publish-session-authority-stays-lease-addressable.md", "authority.lease_id"],
        "CHANGELOG.md": ["ADR-0177", "docs/587-publish-session-authority-stays-lease-addressable.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session lease-addressable token: {needle}")

    if errors:
        print("Publish-session lease-id contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session lease-id contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
