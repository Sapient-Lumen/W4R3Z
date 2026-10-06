#!/usr/bin/env python3
"""Guardrail for publish-session lease-frozen outward surface continuity."""
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


def continuity_contract_errors(before: dict, after: dict) -> list[str]:
    errors: list[str] = []
    before_surface = before.get("published_endpoint") or {}
    after_surface = after.get("published_endpoint") or {}
    if before_surface == after_surface:
        return errors
    before_lease = ((before.get("authority") or {}).get("lease_id"))
    after_lease = ((after.get("authority") or {}).get("lease_id"))
    if before_lease == after_lease:
        errors.append("material published_endpoint change must not reuse authority.lease_id")
    if before.get("session_id") == after.get("session_id"):
        errors.append("material published_endpoint change must not reuse session_id")
    return errors


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

    if (example.get("published_endpoint") or {}).get("continuity_posture") != "lease-frozen":
        errors.append("publish-session example must carry published_endpoint.continuity_posture = lease-frozen")

    same_surface_ok = deepcopy(example)
    if validate(validator, same_surface_ok):
        errors.append("publish-session example with lease-frozen continuity posture should validate")
    if continuity_contract_errors(example, same_surface_ok):
        errors.append("unchanged published surface should not require a new session or lease")

    same_lease_bad = deepcopy(example)
    same_lease_bad["session_id"] = "publish-7c3f-demo-preview-v2"
    same_lease_bad["published_endpoint"]["hostname"] = "preview-9d2a.relay.example.invalid"
    same_lease_bad["published_endpoint"]["url_hint"] = "https://preview-9d2a.relay.example.invalid:443/hooks/demo-v2"
    same_lease_bad["published_endpoint"]["path_prefix"] = "/hooks/demo-v2"
    if validate(validator, same_lease_bad):
        errors.append("changed published surface with a fresh session_id but reused authority.lease_id should still validate as a single receipt")
    if not continuity_contract_errors(example, same_lease_bad):
        errors.append("material published_endpoint change must fail continuity contract when authority.lease_id is reused")

    same_session_bad = deepcopy(example)
    same_session_bad["authority"]["lease_id"] = "lease-publish-9d2a"
    same_session_bad["published_endpoint"]["hostname"] = "preview-9d2a.relay.example.invalid"
    same_session_bad["published_endpoint"]["url_hint"] = "https://preview-9d2a.relay.example.invalid:443/hooks/demo-v2"
    same_session_bad["published_endpoint"]["path_prefix"] = "/hooks/demo-v2"
    if validate(validator, same_session_bad):
        errors.append("changed published surface with a fresh authority.lease_id but reused session_id should still validate as a single receipt")
    if not continuity_contract_errors(example, same_session_bad):
        errors.append("material published_endpoint change must fail continuity contract when session_id is reused")

    fresh_ok = deepcopy(example)
    fresh_ok["session_id"] = "publish-9d2a-demo-preview"
    fresh_ok["authority"]["lease_id"] = "lease-publish-9d2a"
    fresh_ok["authority"]["expires_at"] = "2026-03-19T04:18:00Z"
    fresh_ok["published_endpoint"]["hostname"] = "preview-9d2a.relay.example.invalid"
    fresh_ok["published_endpoint"]["url_hint"] = "https://preview-9d2a.relay.example.invalid:443/hooks/demo-v2"
    fresh_ok["published_endpoint"]["path_prefix"] = "/hooks/demo-v2"
    fresh_ok["published_endpoint"]["secret_handoff"]["expires_at"] = "2026-03-19T04:18:00Z"
    if validate(validator, fresh_ok):
        errors.append("material published_endpoint change with fresh session_id and authority.lease_id should validate")
    if continuity_contract_errors(example, fresh_ok):
        errors.append("material published_endpoint change should be allowed once both session_id and authority.lease_id are fresh")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["lease-frozen", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md": ["new `session_id` and fresh `authority.lease_id`", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/565-publish-session-session-scoped-locator-posture-boundary.md": ["lease-frozen", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/579-publish-session-url-hints-follow-endpoint-tuple.md": ["lease-frozen", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/587-publish-session-authority-stays-lease-addressable.md": ["same bounded share instance", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["lease-frozen", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["lease-frozen", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_surface_continuity_contract.py", "lease-frozen"],
        "docs/99-llm-runbook.md": ["docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md", "tools/check_publish_session_surface_continuity_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing published endpoint surfaces should stay lease-frozen", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0184", "lease-frozen"],
        "README.md": ["docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md", "lease-frozen"],
        "docs/00-index.md": ["docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md", "lease-frozen"],
        "CHANGELOG.md": ["ADR-0184", "docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session surface-continuity token: {needle}")

    if errors:
        print("Publish-session surface continuity contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session surface continuity contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
