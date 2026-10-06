#!/usr/bin/env python3
"""Guardrail for publish-session maintenance trigger posture."""
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

    maint_ok = deepcopy(example)
    maint_ok["session_id"] = "publish-maint-7c3f"
    maint_ok["authority"]["trigger"] = "maintenance"
    maint_ok["authority"].pop("consent_receipt_digest", None)
    maint_ok["authority"].pop("policy_decision_digest", None)
    maint_ok["authority"].pop("operator_session_digest", None)
    maint_ok["authority"].pop("support_session_digest", None)
    ends = set(maint_ok["lifecycle"]["end_conditions"])
    ends.discard("initiating-user-session-end")
    ends.add("maintenance-window-end")
    maint_ok["lifecycle"]["end_conditions"] = sorted(ends)
    if validate(validator, maint_ok):
        errors.append("maintenance-triggered publish session without borrowed digest lanes should validate")

    for field in [
        "consent_receipt_digest",
        "policy_decision_digest",
        "operator_session_digest",
        "support_session_digest",
    ]:
        bad = deepcopy(maint_ok)
        bad["authority"][field] = "sha256:" + {
            "consent_receipt_digest": "40",
            "policy_decision_digest": "41",
            "operator_session_digest": "42",
            "support_session_digest": "43",
        }[field] * 32
        if not validate(validator, bad):
            errors.append(f"maintenance-triggered publish session carrying {field} must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": [
            "maintenance stays reserved and digest-empty",
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
        ],
        "docs/586-publish-session-authority-joins-follow-trigger.md": [
            "maintenance borrow",
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
        ],
        "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md": [
            "digest-empty",
            "maintenance-window-end",
            "tools/check_publish_session_maintenance_trigger_contract.py",
        ],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": [
            "maintenance stays reserved and digest-empty",
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
        ],
        "docs/460-inbound-listen-posture-by-profile.md": [
            "maintenance stays reserved and digest-empty",
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
        ],
        "docs/98-archive-hygiene.md": [
            "tools/check_publish_session_maintenance_trigger_contract.py",
            "maintenance stays reserved and digest-empty",
        ],
        "docs/99-llm-runbook.md": [
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
            "tools/check_publish_session_maintenance_trigger_contract.py",
        ],
        "docs/110-juicy-os-lessons.md": [
            "Temporary sharing maintenance triggers should stay digest-empty",
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0180",
            "maintenance-window",
            "digest-empty",
        ],
        "README.md": [
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
            "digest-empty",
        ],
        "docs/00-index.md": [
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
            "digest-empty",
        ],
        "CHANGELOG.md": [
            "ADR-0180",
            "docs/590-publish-session-maintenance-triggers-stay-digest-empty.md",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required maintenance-trigger token: {needle}")

    if errors:
        print("Publish-session maintenance-trigger contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session maintenance-trigger contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
