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
    ROOT / "docs" / "461-remote-assistance-posture-by-profile.md",
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md",
    ROOT / "docs" / "600-publish-session-return-paths-stay-trusted-ui-persistent.md",
    ROOT / "docs" / "601-publish-session-management-return-paths-stay-lease-exact.md",
    ROOT / "docs" / "98-archive-hygiene.md",
    ROOT / "docs" / "99-llm-runbook.md",
    ROOT / "docs" / "110-juicy-os-lessons.md",
    ROOT / "docs" / "266-open-questions-and-risk-register.md",
]
REQUIRED_DOC_TOKENS = {
    ROOT / "README.md": ["docs/601-publish-session-management-return-paths-stay-lease-exact.md", "management_return_binding", "lease-exact"],
    ROOT / "CHANGELOG.md": ["ADR-0191", "management_return_binding", "0.33"],
    ROOT / "docs" / "00-index.md": ["ADR-0191", "management_return_binding", "0.33"],
    ROOT / "docs" / "461-remote-assistance-posture-by-profile.md": ["exact live-share surface for that lease", "stable trusted-UI return path"],
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["docs/601-publish-session-management-return-paths-stay-lease-exact.md", "management_return_binding", "lease-exact"],
    ROOT / "docs" / "600-publish-session-return-paths-stay-trusted-ui-persistent.md": ["docs/601-publish-session-management-return-paths-stay-lease-exact.md", "lease-exact"],
    ROOT / "docs" / "601-publish-session-management-return-paths-stay-lease-exact.md": ["tools/check_publish_session_management_return_binding_contract.py", "management_return_binding", "Last updated: 2026-03-20r334"],
    ROOT / "docs" / "98-archive-hygiene.md": ["tools/check_publish_session_management_return_binding_contract.py", "management_return_binding", "lease-exact"],
    ROOT / "docs" / "99-llm-runbook.md": ["tools/check_publish_session_management_return_binding_contract.py", "management_return_binding", "docs/601-publish-session-management-return-paths-stay-lease-exact.md"],
    ROOT / "docs" / "110-juicy-os-lessons.md": ["exact live-share surface for that lease", "docs/601-publish-session-management-return-paths-stay-lease-exact.md"],
    ROOT / "docs" / "266-open-questions-and-risk-register.md": ["ADR-0191", "management_return_binding", "lease-exact"],
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
    mrb = ev.get("properties", {}).get("management_return_binding")
    if not isinstance(mrb, dict) or mrb.get("const") != "lease-exact":
        fail("spec/net.publish.session.schema.json must define evidence.management_return_binding = lease-exact")
        ok = False
    if "management_return_binding" not in ev.get("required", []):
        fail("spec/net.publish.session.schema.json must require evidence.management_return_binding")
        ok = False
    example = json.loads(EXAMPLE.read_text())
    if example.get("session_version") != "0.33":
        fail("spec/examples/net.publish.session.json must set session_version 0.33")
        ok = False
    if example.get("evidence", {}).get("management_return_binding") != "lease-exact":
        fail("spec/examples/net.publish.session.json must set evidence.management_return_binding = lease-exact")
        ok = False
    for doc in DOCS:
        if not doc.exists():
            fail(f"missing required doc: {doc.relative_to(ROOT)}")
            ok = False
            continue
        text = doc.read_text()
        for token in REQUIRED_DOC_TOKENS.get(doc, []):
            if token not in text:
                fail(f"{doc.relative_to(ROOT)} missing required publish-session management-return-binding token: {token}")
                ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
