#!/usr/bin/env python3
"""Validate the rev0836 gate diagnostics/refactor surface."""
from __future__ import annotations

import json
import re
import ast
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "gate.py"
AUDIT_JSON = ROOT / "AUDIT" / "GATE_DIAGNOSTICS_REFACTOR_REV0836.json"
AUDIT_MD = ROOT / "AUDIT" / "GATE_DIAGNOSTICS_REFACTOR_REV0836.md"


def fail(msg: str) -> None:
    print(f"gate-diagnostics-rev0836-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    source = GATE.read_text(encoding="utf-8")
    required_snippets = [
        "PYTHONUNBUFFERED",
        "GATE_STEP_TIMEOUT_SECONDS",
        "runner: START",
        "runner: OK",
        "gate: TIMEOUT",
        "time.monotonic",
        "'-u'",
    ]
    for snippet in required_snippets:
        if snippet not in source:
            fail(f"scripts/gate.py is missing diagnostic snippet {snippet!r}")
    for path in (AUDIT_JSON, AUDIT_MD):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT).as_posix()}")
    try:
        audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid audit JSON: {exc}")
    if audit.get("status") != "gate_diagnostics_refactored":
        fail("gate diagnostics audit status mismatch")
    if audit.get("timeout_environment_variable") != "GATE_STEP_TIMEOUT_SECONDS":
        fail("gate diagnostics audit timeout variable mismatch")
    try:
        ast.parse(source, filename="scripts/gate.py")
    except SyntaxError as exc:
        fail(f"scripts/gate.py does not parse: {exc}")
    if not re.search(r"gate: OK \(\{count\} steps, \{total_elapsed:\.2f\}s\)", source):
        fail("scripts/gate.py does not report total step count and duration")
    print("gate-diagnostics-rev0836-validate: OK (unbuffered/timed gate diagnostics present)")


if __name__ == "__main__":
    main()
