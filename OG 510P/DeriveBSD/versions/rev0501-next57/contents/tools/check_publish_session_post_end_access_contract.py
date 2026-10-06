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
    ROOT / "docs" / "564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md",
    ROOT / "docs" / "598-publish-session-post-end-access-stays-fail-closed.md",
    ROOT / "docs" / "98-archive-hygiene.md",
    ROOT / "docs" / "99-llm-runbook.md",
    ROOT / "docs" / "110-juicy-os-lessons.md",
    ROOT / "docs" / "266-open-questions-and-risk-register.md",
]
REQUIRED_DOC_TOKENS = {
    ROOT / "README.md": ["docs/598-publish-session-post-end-access-stays-fail-closed.md", "post_end_access_posture", "explicit-ended-or-fresh-share"],
    ROOT / "CHANGELOG.md": ["ADR-0188", "post_end_access_posture", "0.33"],
    ROOT / "docs" / "00-index.md": ["ADR-0188", "post_end_access_posture", "0.33"],
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["docs/598-publish-session-post-end-access-stays-fail-closed.md", "post_end_access_posture", "explicit-ended-or-fresh-share"],
    ROOT / "docs" / "564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md": ["post_end_access_posture", "explicit-ended-or-fresh-share", "Last updated: 2026-05-15r482"],
    ROOT / "docs" / "598-publish-session-post-end-access-stays-fail-closed.md": ["tools/check_publish_session_post_end_access_contract.py", "post_end_access_posture", "Last updated: 2026-03-20r334"],
    ROOT / "docs" / "98-archive-hygiene.md": ["tools/check_publish_session_post_end_access_contract.py", "post_end_access_posture", "explicit-ended-or-fresh-share"],
    ROOT / "docs" / "99-llm-runbook.md": ["tools/check_publish_session_post_end_access_contract.py", "post_end_access_posture", "docs/598-publish-session-post-end-access-stays-fail-closed.md"],
    ROOT / "docs" / "110-juicy-os-lessons.md": ["Temporary sharing should keep stale share handles fail-closed after end", "docs/598-publish-session-post-end-access-stays-fail-closed.md"],
    ROOT / "docs" / "266-open-questions-and-risk-register.md": ["ADR-0188", "post_end_access_posture", "explicit-ended-or-fresh-share"],
}

def fail(msg: str) -> None:
    print(msg, file=sys.stderr)

def main() -> int:
    ok = True
    schema = json.loads(SCHEMA.read_text())
    lifecycle = schema.get("properties", {}).get("lifecycle", {})
    if schema.get("properties", {}).get("session_version", {}).get("const") != "0.33":
        fail("spec/net.publish.session.schema.json must pin session_version 0.33")
        ok = False
    if "(v0.33)" not in schema.get("title", ""):
        fail("spec/net.publish.session.schema.json title must say v0.33")
        ok = False
    lep = lifecycle.get("properties", {}).get("post_end_access_posture")
    if not isinstance(lep, dict) or lep.get("const") != "explicit-ended-or-fresh-share":
        fail("spec/net.publish.session.schema.json must define lifecycle.post_end_access_posture = explicit-ended-or-fresh-share")
        ok = False
    if "post_end_access_posture" not in lifecycle.get("required", []):
        fail("spec/net.publish.session.schema.json must require lifecycle.post_end_access_posture")
        ok = False
    example = json.loads(EXAMPLE.read_text())
    if example.get("session_version") != "0.33":
        fail("spec/examples/net.publish.session.json must set session_version 0.33")
        ok = False
    if example.get("lifecycle", {}).get("post_end_access_posture") != "explicit-ended-or-fresh-share":
        fail("spec/examples/net.publish.session.json must set lifecycle.post_end_access_posture = explicit-ended-or-fresh-share")
        ok = False
    for doc in DOCS:
        if not doc.exists():
            fail(f"missing required doc: {doc.relative_to(ROOT)}")
            ok = False
            continue
        text = doc.read_text()
        for token in REQUIRED_DOC_TOKENS.get(doc, []):
            if token not in text:
                fail(f"{doc.relative_to(ROOT)} missing required publish-session post-end-access token: {token}")
                ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
