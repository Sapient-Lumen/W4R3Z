#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "spec" / "net.publish.session.schema.json"
EXAMPLE = ROOT / "spec" / "examples" / "net.publish.session.json"
DOCS = [
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "docs" / "00-index.md",
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md",
    ROOT / "docs" / "597-publish-session-visible-indicators-stay-durable-until-ended.md",
    ROOT / "docs" / "599-publish-session-revocation-affordances-stay-same-surface-durable.md",
    ROOT / "docs" / "98-archive-hygiene.md",
    ROOT / "docs" / "99-llm-runbook.md",
    ROOT / "docs" / "110-juicy-os-lessons.md",
    ROOT / "docs" / "266-open-questions-and-risk-register.md",
]
REQUIRED_DOC_TOKENS = {
    ROOT / "README.md": ["docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md", "revocation_affordance_posture", "same-surface-durable-until-ended"],
    ROOT / "CHANGELOG.md": ["ADR-0189", "revocation_affordance_posture", "0.33"],
    ROOT / "docs" / "00-index.md": ["ADR-0189", "revocation_affordance_posture", "0.33"],
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md", "revocation_affordance_posture", "same-surface-durable-until-ended"],
    ROOT / "docs" / "597-publish-session-visible-indicators-stay-durable-until-ended.md": ["revocation affordance", "docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md"],
    ROOT / "docs" / "599-publish-session-revocation-affordances-stay-same-surface-durable.md": ["tools/check_publish_session_revocation_affordance_contract.py", "revocation_affordance_posture", "Last updated: 2026-03-20r334"],
    ROOT / "docs" / "98-archive-hygiene.md": ["tools/check_publish_session_revocation_affordance_contract.py", "revocation_affordance_posture", "same-surface-durable-until-ended"],
    ROOT / "docs" / "99-llm-runbook.md": ["tools/check_publish_session_revocation_affordance_contract.py", "revocation_affordance_posture", "docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md"],
    ROOT / "docs" / "110-juicy-os-lessons.md": ["Temporary sharing should keep the stop/revoke affordance on the same durable active-share surface", "docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md"],
    ROOT / "docs" / "266-open-questions-and-risk-register.md": ["ADR-0189", "revocation_affordance_posture", "same-surface-durable-until-ended"],
}

def fail(msg: str) -> None:
    print(msg, file=sys.stderr)

def main() -> int:
    ok = True
    schema = json.loads(SCHEMA.read_text())
    ev = schema.get("properties", {}).get("evidence", {})
    if schema.get("properties", {}).get("session_version", {}).get("const") != "0.33":
        fail("spec/net.publish.session.schema.json must pin session_version 0.33")
        ok = False
    if "(v0.33)" not in schema.get("title", ""):
        fail("spec/net.publish.session.schema.json title must say v0.33")
        ok = False
    rap = ev.get("properties", {}).get("revocation_affordance_posture")
    if not isinstance(rap, dict) or rap.get("const") != "same-surface-durable-until-ended":
        fail("spec/net.publish.session.schema.json must define evidence.revocation_affordance_posture = same-surface-durable-until-ended")
        ok = False
    if "revocation_affordance_posture" not in ev.get("required", []):
        fail("spec/net.publish.session.schema.json must require evidence.revocation_affordance_posture")
        ok = False
    example = json.loads(EXAMPLE.read_text())
    if example.get("session_version") != "0.33":
        fail("spec/examples/net.publish.session.json must set session_version 0.33")
        ok = False
    if example.get("evidence", {}).get("revocation_affordance_posture") != "same-surface-durable-until-ended":
        fail("spec/examples/net.publish.session.json must set evidence.revocation_affordance_posture = same-surface-durable-until-ended")
        ok = False
    for doc in DOCS:
        if not doc.exists():
            fail(f"missing required doc: {doc.relative_to(ROOT)}")
            ok = False
            continue
        text = doc.read_text()
        for token in REQUIRED_DOC_TOKENS.get(doc, []):
            if token not in text:
                fail(f"{doc.relative_to(ROOT)} missing required publish-session revocation-affordance token: {token}")
                ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
