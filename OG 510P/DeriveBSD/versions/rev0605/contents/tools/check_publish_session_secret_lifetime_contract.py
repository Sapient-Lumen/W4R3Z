#!/usr/bin/env python3
"""Guardrail for publish-session secret-handoff lifetime coupling posture."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return strict_load_json(ROOT, rel)


def parse_ts(raw: str) -> datetime:
    if raw.endswith('Z'):
        raw = raw[:-1] + '+00:00'
    return datetime.fromisoformat(raw).astimezone(timezone.utc)


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
    if ((secret_handoff.get("properties") or {}).get("lifetime_binding") or {}).get("const") != "session-authority-bounded":
        errors.append("spec/net.publish.session.schema.json must keep secret_handoff.lifetime_binding fixed to session-authority-bounded")
    if "expires_at" not in (secret_handoff.get("required") or []):
        errors.append("spec/net.publish.session.schema.json must require secret_handoff.expires_at")

    endpoint = example.get("published_endpoint") or {}
    audience = endpoint.get("audience") or {}
    handoff = endpoint.get("secret_handoff") or {}
    authority = example.get("authority") or {}
    if audience.get("authn_mode") in {"single-use-secret", "shared-secret"}:
        if handoff.get("lifetime_binding") != "session-authority-bounded":
            errors.append("secret-gated publish-session example must use secret_handoff.lifetime_binding = session-authority-bounded")
        if not handoff.get("expires_at"):
            errors.append("secret-gated publish-session example must carry secret_handoff.expires_at")
        elif authority.get("expires_at"):
            try:
                if parse_ts(handoff["expires_at"]) > parse_ts(authority["expires_at"]):
                    errors.append("publish-session example secret_handoff.expires_at must not outlive authority.expires_at")
            except Exception as exc:
                errors.append(f"publish-session example has unparsable expiry timestamps: {exc}")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["session-authority-bounded", "secret lifetime"],
        "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md": ["docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md", "session-authority-bounded"],
        "docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md": ["`secret_handoff.expires_at`", "session-authority-bounded"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["secret lifetime", "session authority"],
        "docs/460-inbound-listen-posture-by-profile.md": ["secret lifetime", "share secret"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_secret_lifetime_contract.py", "secret_handoff.expires_at"],
        "docs/99-llm-runbook.md": ["docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md", "tools/check_publish_session_secret_lifetime_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing secret handoffs should die with the session authority", "docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0157", "still-valid secret"],
        "docs/32-curated-references.md": ["AWS S3 presigned URLs", "Response wrapping"],
        "README.md": ["docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md", "session-authority-bounded"],
        "docs/00-index.md": ["docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md", "secret lifetime-coupled posture"],
        "CHANGELOG.md": ["ADR-0157", "docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session secret-lifetime token: {needle}")

    if errors:
        print("Publish-session secret-lifetime contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session secret-lifetime contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
