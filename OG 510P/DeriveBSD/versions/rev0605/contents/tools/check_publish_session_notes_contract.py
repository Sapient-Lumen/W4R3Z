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
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md",
    ROOT / "docs" / "595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md",
    ROOT / "docs" / "596-publish-session-notes-stay-off-baseline-envelope.md",
    ROOT / "docs" / "98-archive-hygiene.md",
    ROOT / "docs" / "99-llm-runbook.md",
    ROOT / "docs" / "110-juicy-os-lessons.md",
    ROOT / "docs" / "266-open-questions-and-risk-register.md",
]
REQUIRED_DOC_TOKENS = {
    ROOT / "README.md": ["docs/596-publish-session-notes-stay-off-baseline-envelope.md", "evidence.notes", "note-free"],
    ROOT / "CHANGELOG.md": ["ADR-0186", "evidence.notes", "0.33"],
    ROOT / "docs" / "00-index.md": ["ADR-0186", "evidence.notes", "0.33"],
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["docs/596-publish-session-notes-stay-off-baseline-envelope.md", "evidence.notes", "note-free"],
    ROOT / "docs" / "595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md": ["docs/596-publish-session-notes-stay-off-baseline-envelope.md", "evidence.notes", "Last updated: 2026-03-20r327"],
    ROOT / "docs" / "596-publish-session-notes-stay-off-baseline-envelope.md": ["tools/check_publish_session_notes_contract.py", "evidence.notes", "Last updated: 2026-03-20r326"],
    ROOT / "docs" / "98-archive-hygiene.md": ["tools/check_publish_session_notes_contract.py", "evidence.notes", "note-free"],
    ROOT / "docs" / "99-llm-runbook.md": ["tools/check_publish_session_notes_contract.py", "evidence.notes", "docs/596-publish-session-notes-stay-off-baseline-envelope.md"],
    ROOT / "docs" / "110-juicy-os-lessons.md": ["Temporary sharing envelopes should stay note-free", "docs/596-publish-session-notes-stay-off-baseline-envelope.md"],
    ROOT / "docs" / "266-open-questions-and-risk-register.md": ["ADR-0186", "evidence.notes"],
}

def fail(msg: str) -> None:
    print(msg, file=sys.stderr)

def main() -> int:
    ok = True

    schema = strict_load_json(ROOT, "spec/net.publish.session.schema.json")
    if schema.get("properties", {}).get("evidence", {}).get("properties", {}).get("notes") is not None:
        fail("spec/net.publish.session.schema.json must not define evidence.notes")
        ok = False
    if schema.get("properties", {}).get("session_version", {}).get("const") != "0.33":
        fail("spec/net.publish.session.schema.json must pin session_version 0.33")
        ok = False
    if "(v0.33)" not in schema.get("title", ""):
        fail("spec/net.publish.session.schema.json title must say v0.33")
        ok = False

    example = strict_load_json(ROOT, "spec/examples/net.publish.session.json")
    if example.get("session_version") != "0.33":
        fail("spec/examples/net.publish.session.json must set session_version 0.33")
        ok = False
    if example.get("evidence", {}).get("notes") is not None:
        fail("spec/examples/net.publish.session.json must not carry evidence.notes")
        ok = False

    for doc in DOCS:
        if not doc.exists():
            fail(f"missing required doc: {doc.relative_to(ROOT)}")
            ok = False
            continue
        text = doc.read_text()
        for token in REQUIRED_DOC_TOKENS.get(doc, []):
            if token not in text:
                fail(f"{doc.relative_to(ROOT)} missing required publish-session notes token: {token}")
                ok = False

    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
