#!/usr/bin/env python3
"""Validate rev0839's direct published-state transition rights gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_publication_state_transition_rights_gate_audit_rev0839 import JSON_OUT, MD_OUT, build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"publication-state-transition-rights-gate-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    expected = build(ROOT, run_probe=True)
    if expected["status"] != "direct_published_state_transition_rights_gated":
        fail(f"unexpected audit status: {expected['status']}")
    if not expected["static_checks_pass"]:
        fail("static transition guard checks did not pass")
    if not expected["blocked_probe_pass"]:
        fail("blocked transition probe did not fail closed without mutation")
    if not JSON_OUT.is_file() or not MD_OUT.is_file():
        fail("audit files are missing")
    try:
        recorded = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid {JSON_OUT.relative_to(ROOT).as_posix()}: {exc}")
    volatile_paths = [
        ("blocked_transition_probe", "stdout"),
        ("blocked_transition_probe", "stderr"),
    ]
    comparable_expected = json.loads(json.dumps(expected))
    comparable_recorded = json.loads(json.dumps(recorded))
    for head, key in volatile_paths:
        if isinstance(comparable_expected.get(head), dict):
            comparable_expected[head][key] = "<volatile-output>"
        if isinstance(comparable_recorded.get(head), dict):
            comparable_recorded[head][key] = "<volatile-output>"
    if comparable_recorded != comparable_expected:
        fail(f"{JSON_OUT.relative_to(ROOT).as_posix()} is stale")
    expected_md = render_markdown(recorded)
    if MD_OUT.read_text(encoding="utf-8") != expected_md:
        fail(f"{MD_OUT.relative_to(ROOT).as_posix()} is stale")
    print("publication-state-transition-rights-gate-validate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
