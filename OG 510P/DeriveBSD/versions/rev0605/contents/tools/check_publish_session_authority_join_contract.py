#!/usr/bin/env python3
"""Guardrail for publish-session authority trigger/join coherence."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return strict_load_json(ROOT, rel)


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

    auth = example.get("authority") or {}
    if auth.get("trigger") != "trusted-ui" or not auth.get("consent_receipt_digest"):
        errors.append("publish-session example must keep trusted-ui joined to consent_receipt_digest")

    policy_ok = deepcopy(example)
    policy_ok["session_id"] = "publish-policy-7c3f"
    policy_ok["authority"]["trigger"] = "policy"
    policy_ok["authority"].pop("consent_receipt_digest", None)
    policy_ok["authority"]["policy_decision_digest"] = "sha256:" + "91" * 32
    if validate(validator, policy_ok):
        errors.append("policy-triggered publish session joined to policy_decision_digest should validate")

    trusted_missing = deepcopy(example)
    trusted_missing["authority"].pop("consent_receipt_digest", None)
    if not validate(validator, trusted_missing):
        errors.append("trusted-ui publish session without consent_receipt_digest must fail validation")

    policy_mixed = deepcopy(policy_ok)
    policy_mixed["authority"]["consent_receipt_digest"] = "sha256:" + "40" * 32
    if not validate(validator, policy_mixed):
        errors.append("policy-triggered publish session carrying consent_receipt_digest must fail validation")

    operator_ok = deepcopy(example)
    operator_ok["session_id"] = "publish-operator-7c3f"
    operator_ok["published_endpoint"]["access_model"] = "reverse-forward"
    operator_ok["published_endpoint"]["exposure_scope"] = "tailnet"
    operator_ok["published_endpoint"]["audience"]["class"] = "tailnet-users"
    operator_ok["published_endpoint"]["audience"]["authn_mode"] = "tailnet-identity"
    operator_ok["published_endpoint"]["audience"].pop("validation_hint", None)
    operator_ok["published_endpoint"]["audience"].pop("identity_provider_hint", None)
    operator_ok["published_endpoint"]["audience"].pop("recipient_hint", None)
    operator_ok["published_endpoint"].pop("url_hint", None)
    operator_ok["published_endpoint"].pop("path_prefix", None)
    operator_ok["published_endpoint"]["hostname"] = "preview-7c3f"
    operator_ok["published_endpoint"]["locator_posture"] = "tailnet-device-name"
    operator_ok["relay"]["remote_locator"] = {"kind": "object-path", "value": "tailnet/publish-7c3f"}
    operator_ok["relay"]["destination_hint"] = "tailnet/publish-7c3f"
    operator_ok["published_endpoint"].pop("secret_handoff", None)
    operator_ok["authority"]["trigger"] = "operator-session"
    operator_ok["authority"].pop("consent_receipt_digest", None)
    operator_ok["authority"]["operator_session_digest"] = "sha256:" + "ab" * 32
    ends = set(operator_ok["lifecycle"]["end_conditions"])
    ends.discard("initiating-user-session-end")
    ends.add("operator-session-end")
    operator_ok["lifecycle"]["end_conditions"] = sorted(ends)
    if validate(validator, operator_ok):
        errors.append("operator-session publish session joined to operator_session_digest should validate")

    operator_wrong = deepcopy(operator_ok)
    operator_wrong["authority"].pop("operator_session_digest", None)
    operator_wrong["authority"]["policy_decision_digest"] = "sha256:" + "92" * 32
    if not validate(validator, operator_wrong):
        errors.append("operator-session publish session carrying policy_decision_digest instead of operator_session_digest must fail validation")

    support_mixed = deepcopy(example)
    support_mixed["authority"]["support_session_digest"] = "sha256:" + "93" * 32
    if not validate(validator, support_mixed):
        errors.append("publish-session carrying support_session_digest outside support-session trigger must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["authority joins now follow `authority.trigger`", "consent_receipt_digest", "policy_decision_digest", "operator_session_digest", "docs/586-publish-session-authority-joins-follow-trigger.md"],
        "docs/586-publish-session-authority-joins-follow-trigger.md": ["authority joins now follow **`authority.trigger` exactly**", "operator_session_digest", "maintenance"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["authority joins now follow `authority.trigger`", "policy_decision_digest", "docs/586-publish-session-authority-joins-follow-trigger.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["authority joins now follow `authority.trigger`", "operator_session_digest", "docs/586-publish-session-authority-joins-follow-trigger.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_authority_join_contract.py", "authority joins now follow `authority.trigger`"],
        "docs/99-llm-runbook.md": ["docs/586-publish-session-authority-joins-follow-trigger.md", "tools/check_publish_session_authority_join_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing authority joins should follow trigger", "docs/586-publish-session-authority-joins-follow-trigger.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0176", "operator_session_digest", "policy_decision_digest"],
        "README.md": ["docs/586-publish-session-authority-joins-follow-trigger.md", "operator_session_digest", "policy_decision_digest"],
        "docs/00-index.md": ["docs/586-publish-session-authority-joins-follow-trigger.md", "operator_session_digest", "policy_decision_digest"],
        "CHANGELOG.md": ["ADR-0176", "docs/586-publish-session-authority-joins-follow-trigger.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session authority-join token: {needle}")

    if errors:
        print("Publish-session authority-join contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session authority-join contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
