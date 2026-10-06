#!/usr/bin/env python3
"""Guardrail for publish-session baseline-envelope diagnostic artifact separation."""
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

    if (example.get("session_version")) != "0.33":
        errors.append("publish-session example must carry session_version = 0.33")

    good = deepcopy(example)
    if validate(validator, good):
        errors.append("publish-session example without diagnostic_artifact_digests should validate")

    bad = deepcopy(example)
    bad["evidence"]["diagnostic_artifact_digests"] = ["sha256:diag00"]
    if not validate(validator, bad):
        errors.append("publish-session carrying evidence.diagnostic_artifact_digests must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["baseline-envelope shaped", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
        "docs/216-incident-snapshots-and-support-bundles.md": ["publish-session envelope itself", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
        "docs/291-remote-assistance-sessions-as-evidence.md": ["backstage diagnostics stay on support/operator/incident evidence joins", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["baseline-safe", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["baseline-safe", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_diagnostic_artifact_contract.py", "baseline-safe"],
        "docs/99-llm-runbook.md": ["docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md", "tools/check_publish_session_diagnostic_artifact_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing envelopes should stay baseline-safe", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0185", "diagnostic_artifact_digests"],
        "README.md": ["docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md", "baseline-safe"],
        "docs/00-index.md": ["docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md", "baseline-safe"],
        "CHANGELOG.md": ["ADR-0185", "docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session diagnostic-artifact token: {needle}")

    if errors:
        print("Publish-session diagnostic artifact contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session diagnostic artifact contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
