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
    ROOT / "docs" / "564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md",
    ROOT / "docs" / "598-publish-session-post-end-access-stays-fail-closed.md",
    ROOT / "docs" / "602-publish-session-post-end-management-return-stays-lease-exact-ended.md",
    ROOT / "docs" / "603-publish-session-ended-states-stay-terminal-cause-exact.md",
    ROOT / "docs" / "98-archive-hygiene.md",
    ROOT / "docs" / "99-llm-runbook.md",
    ROOT / "docs" / "110-juicy-os-lessons.md",
    ROOT / "docs" / "266-open-questions-and-risk-register.md",
]
REQUIRED_DOC_TOKENS = {
    ROOT / "README.md": ["docs/603-publish-session-ended-states-stay-terminal-cause-exact.md", "terminal_end_condition", "0.33"],
    ROOT / "CHANGELOG.md": ["ADR-0193", "terminal_end_condition", "0.33"],
    ROOT / "docs" / "00-index.md": ["ADR-0193", "terminal_end_condition", "0.33"],
    ROOT / "docs" / "461-remote-assistance-posture-by-profile.md": ["exact terminal cause", "terminal_end_condition"],
    ROOT / "docs" / "562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["docs/603-publish-session-ended-states-stay-terminal-cause-exact.md", "terminal_end_condition", "0.33"],
    ROOT / "docs" / "564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md": ["terminal_end_condition", "docs/603-publish-session-ended-states-stay-terminal-cause-exact.md"],
    ROOT / "docs" / "598-publish-session-post-end-access-stays-fail-closed.md": ["terminal_end_condition", "exact bounded end-condition class"],
    ROOT / "docs" / "602-publish-session-post-end-management-return-stays-lease-exact-ended.md": ["terminal_end_condition", "exact terminal cause"],
    ROOT / "docs" / "603-publish-session-ended-states-stay-terminal-cause-exact.md": ["tools/check_publish_session_terminal_end_condition_contract.py", "terminal_end_condition", "Last updated: 2026-03-20r334"],
    ROOT / "docs" / "98-archive-hygiene.md": ["tools/check_publish_session_terminal_end_condition_contract.py", "terminal_end_condition", "exact terminal cause"],
    ROOT / "docs" / "99-llm-runbook.md": ["tools/check_publish_session_terminal_end_condition_contract.py", "terminal_end_condition", "docs/603-publish-session-ended-states-stay-terminal-cause-exact.md"],
    ROOT / "docs" / "110-juicy-os-lessons.md": ["terminal_end_condition", "docs/603-publish-session-ended-states-stay-terminal-cause-exact.md"],
    ROOT / "docs" / "266-open-questions-and-risk-register.md": ["ADR-0193", "terminal_end_condition", "exact terminal cause"],
}

def fail(msg: str) -> None:
    print(msg, file=sys.stderr)


def main() -> int:
    ok = True
    schema = json.loads(SCHEMA.read_text())
    if schema.get("properties", {}).get("session_version", {}).get("const") != "0.33":
        fail("spec/net.publish.session.schema.json must pin session_version 0.33")
        ok = False
    if "(v0.33)" not in schema.get("title", ""):
        fail("spec/net.publish.session.schema.json title must say v0.33")
        ok = False
    lifecycle = schema.get("properties", {}).get("lifecycle", {})
    terminal = lifecycle.get("properties", {}).get("terminal_end_condition")
    allowed = [
        "lease-expiry",
        "manual-revoke",
        "local-service-unavailable",
        "initiating-user-session-end",
        "support-session-end",
        "operator-session-end",
        "maintenance-window-end",
        "host-reboot",
    ]
    if not isinstance(terminal, dict) or terminal.get("enum") != allowed:
        fail("spec/net.publish.session.schema.json must define lifecycle.terminal_end_condition with the exact publish-session end-condition enum")
        ok = False
    schema_text = SCHEMA.read_text()
    for token in ['"terminal_end_condition"', '"ended_at"', '"lease-expiry"']:
        if token not in schema_text:
            fail(f"spec/net.publish.session.schema.json missing terminal-end-condition contract token: {token}")
            ok = False
    example = json.loads(EXAMPLE.read_text())
    if example.get("session_version") != "0.33":
        fail("spec/examples/net.publish.session.json must set session_version 0.33")
        ok = False
    if "terminal_end_condition" in example.get("lifecycle", {}):
        fail("spec/examples/net.publish.session.json must omit lifecycle.terminal_end_condition while ended_at is absent")
        ok = False
    for doc in DOCS:
        if not doc.exists():
            fail(f"missing required doc: {doc.relative_to(ROOT)}")
            ok = False
            continue
        text = doc.read_text()
        for token in REQUIRED_DOC_TOKENS.get(doc, []):
            if token not in text:
                fail(f"{doc.relative_to(ROOT)} missing required publish-session terminal-end-condition token: {token}")
                ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
