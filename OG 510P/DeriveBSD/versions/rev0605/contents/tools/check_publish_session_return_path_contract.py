#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "spec" / "net.publish.session.schema.json"
EXAMPLE = ROOT / "spec" / "examples" / "net.publish.session.json"
DOCS = [
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "docs" / "00-index.md",
    ROOT / "docs" / "461-remote-assistance-posture-by-profile.md",
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md",
    ROOT / "docs" / "599-publish-session-revocation-affordances-stay-same-surface-durable.md",
    ROOT / "docs" / "600-publish-session-return-paths-stay-trusted-ui-persistent.md",
    ROOT / "docs" / "98-archive-hygiene.md",
    ROOT / "docs" / "99-llm-runbook.md",
    ROOT / "docs" / "110-juicy-os-lessons.md",
    ROOT / "docs" / "266-open-questions-and-risk-register.md",
]
REQUIRED_DOC_TOKENS = {
    ROOT / "README.md": ["docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md", "management_return_path_posture", "trusted-ui-persistent-until-ended"],
    ROOT / "CHANGELOG.md": ["ADR-0190", "management_return_path_posture", "0.33"],
    ROOT / "docs" / "00-index.md": ["ADR-0190", "management_return_path_posture", "0.33"],
    ROOT / "docs" / "461-remote-assistance-posture-by-profile.md": ["stable trusted-UI return path", "live-share surface"],
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md", "management_return_path_posture", "trusted-ui-persistent-until-ended"],
    ROOT / "docs" / "599-publish-session-revocation-affordances-stay-same-surface-durable.md": ["docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md", "return/re-entry persistence"],
    ROOT / "docs" / "600-publish-session-return-paths-stay-trusted-ui-persistent.md": ["tools/check_publish_session_return_path_contract.py", "management_return_path_posture", "Last updated: 2026-03-20r334"],
    ROOT / "docs" / "98-archive-hygiene.md": ["tools/check_publish_session_return_path_contract.py", "management_return_path_posture", "trusted-ui-persistent-until-ended"],
    ROOT / "docs" / "99-llm-runbook.md": ["tools/check_publish_session_return_path_contract.py", "management_return_path_posture", "docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md"],
    ROOT / "docs" / "110-juicy-os-lessons.md": ["stable trusted-UI return path back to that active-share surface", "docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md"],
    ROOT / "docs" / "266-open-questions-and-risk-register.md": ["ADR-0190", "management_return_path_posture", "trusted-ui-persistent-until-ended"],
}

def fail(msg: str) -> None:
    print(msg, file=sys.stderr)

def main() -> int:
    ok = True
    schema = strict_load_json(ROOT, "spec/net.publish.session.schema.json")
    ev = schema.get("properties", {}).get("evidence", {})
    if schema.get("properties", {}).get("session_version", {}).get("const") != "0.33":
        fail("spec/net.publish.session.schema.json must pin session_version 0.33")
        ok = False
    if "(v0.33)" not in schema.get("title", ""):
        fail("spec/net.publish.session.schema.json title must say v0.33")
        ok = False
    mrp = ev.get("properties", {}).get("management_return_path_posture")
    if not isinstance(mrp, dict) or mrp.get("const") != "trusted-ui-persistent-until-ended":
        fail("spec/net.publish.session.schema.json must define evidence.management_return_path_posture = trusted-ui-persistent-until-ended")
        ok = False
    if "management_return_path_posture" not in ev.get("required", []):
        fail("spec/net.publish.session.schema.json must require evidence.management_return_path_posture")
        ok = False
    example = strict_load_json(ROOT, "spec/examples/net.publish.session.json")
    if example.get("session_version") != "0.33":
        fail("spec/examples/net.publish.session.json must set session_version 0.33")
        ok = False
    if example.get("evidence", {}).get("management_return_path_posture") != "trusted-ui-persistent-until-ended":
        fail("spec/examples/net.publish.session.json must set evidence.management_return_path_posture = trusted-ui-persistent-until-ended")
        ok = False
    for doc in DOCS:
        if not doc.exists():
            fail(f"missing required doc: {doc.relative_to(ROOT)}")
            ok = False
            continue
        text = doc.read_text()
        for token in REQUIRED_DOC_TOKENS.get(doc, []):
            if token not in text:
                fail(f"{doc.relative_to(ROOT)} missing required publish-session return-path token: {token}")
                ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
