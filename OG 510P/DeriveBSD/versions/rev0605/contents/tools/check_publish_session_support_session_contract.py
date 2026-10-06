#!/usr/bin/env python3
"""Guardrail for publish-session support-session authority binding."""
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

    # Support-peer synthetic valid example.
    support = deepcopy(example)
    support["session_id"] = "support-share-7c3f"
    support["published_endpoint"]["exposure_scope"] = "support-peer"
    support["published_endpoint"]["audience"]["class"] = "support-session-peer"
    support["published_endpoint"]["audience"]["authn_mode"] = "support-session"
    support["published_endpoint"]["access_model"] = "peer-relay"
    support["relay"]["remote_locator"] = {"kind": "portal-object", "value": "support-session/7c3f"}
    support["relay"]["destination_hint"] = "support-session/7c3f"
    support["published_endpoint"]["audience"].pop("validation_hint", None)
    support["published_endpoint"].pop("secret_handoff", None)
    for key in ["hostname", "port", "url_hint", "path_prefix"]:
        support["published_endpoint"].pop(key, None)
    support["authority"]["trigger"] = "support-session"
    support["authority"].pop("consent_receipt_digest", None)
    support["authority"]["support_session_digest"] = "sha256:909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeaf"
    ends = set(support["lifecycle"]["end_conditions"])
    ends.discard("initiating-user-session-end")
    ends.add("support-session-end")
    support["lifecycle"]["end_conditions"] = sorted(ends)
    serrs = validate(validator, support)
    if serrs:
        errors.append("synthetic support-peer publish session should validate but failed: " + "; ".join(serrs[:5]))

    missing_digest = deepcopy(support)
    missing_digest["authority"].pop("support_session_digest", None)
    if not validate(validator, missing_digest):
        errors.append("support-peer publish session without authority.support_session_digest must fail validation")

    wrong_trigger = deepcopy(support)
    wrong_trigger["authority"]["trigger"] = "trusted-ui"
    if not validate(validator, wrong_trigger):
        errors.append("support-peer publish session with authority.trigger != support-session must fail validation")

    authn_drift = deepcopy(support)
    authn_drift["published_endpoint"]["exposure_scope"] = "internet"
    if not validate(validator, authn_drift):
        errors.append("support-session authn_mode must fail when exposure_scope drifts off support-peer")

    doc_checks = {
        "docs/291-remote-assistance-sessions-as-evidence.md": ["support-peer publish session", "support_session_digest"],
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["support_session_digest", "authority.trigger = support-session"],
        "docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md": ["support-session authority join", "support_session_digest"],
        "docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md": ["support-session authority join", "support_session_digest"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["support_session_digest", "support-session authority"],
        "docs/460-inbound-listen-posture-by-profile.md": ["support_session_digest", "support-session authority"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_support_session_contract.py", "support_session_digest"],
        "docs/99-llm-runbook.md": ["docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md", "tools/check_publish_session_support_session_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing support-peer shares should join an exact support session", "docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0159", "support_session_digest"],
        "docs/32-curated-references.md": ["Chrome Remote Desktop support codes", "TeamViewer Remote Support sessions"],
        "README.md": ["docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md", "support-session authority"],
        "docs/00-index.md": ["docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md", "support-session authority join"],
        "CHANGELOG.md": ["ADR-0159", "docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session support-session token: {needle}")

    if errors:
        print("Publish-session support-session authority contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session support-session authority contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
