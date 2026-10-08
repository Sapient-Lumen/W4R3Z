#!/usr/bin/env python3
"""Validate rev0832 OCF portable replay command annotations."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from add_ocf_portable_replay_commands import AUDIT_JSON, AUDIT_MD, build_audit, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"ocf-portable-replay-commands-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    expected = build_audit(ROOT)
    if expected["summary"]["historical_private_interpreter_commands"] != 25:
        fail("expected exactly 25 historical private-interpreter commands in OCF benchmark records")
    if expected["summary"]["portable_commands_present"] != 25:
        fail("not every historical command has a portable_cmd")
    if expected["summary"]["portable_commands_with_private_interpreter"]:
        fail("portable_cmd still contains /opt/pyvenv")
    if expected["summary"]["portable_commands_with_missing_paths"]:
        fail("one or more portable command path arguments do not resolve inside the archive")
    if not AUDIT_JSON.is_file() or not AUDIT_MD.is_file():
        fail("missing OCF portable replay command audit outputs")
    actual = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    if actual != expected:
        fail("OCF portable replay command JSON audit is stale")
    if AUDIT_MD.read_text(encoding="utf-8") != render_markdown(expected):
        fail("OCF portable replay command Markdown audit is stale")
    print("ocf-portable-replay-commands-validate: OK (25 portable commands)")


if __name__ == "__main__":
    main()
