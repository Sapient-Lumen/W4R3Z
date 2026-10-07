#!/usr/bin/env python3
"""Check that active operator-facing Python commands are bytecode-safe.

Direct `python3 publishing/...` examples can create `__pycache__` files in a
fresh checkout, which then breaks transient-surface hygiene.  Active operator
surfaces should document `python3 -B ...`, `make ...`, or another explicitly
bytecode-safe path.  Historical patch notes are intentionally not scanned.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

CHECKED_FILES = [
    "START_HERE.md",
    "README.md",
    "PUBLISHING.md",
    "CONTEXT_PACK.json",
    "Makefile",
    "publishing/CONTROL_SURFACES.md",
    "publishing/OPERATOR_STARTUP.md",
    "publishing/RELEASE_FLOW.md",
    "publishing/CONSERVATIVE_RELEASE_POLICY.md",
    "publishing/TURN_DECISION_PROTOCOL.md",
    "release_queue/STATUS.md",
    "release_queue/QUEUE.md",
    "release_queue/LATEST_DECISION.md",
]

UNSAFE_RE = re.compile(r"python3\s+(?:publishing|series|published)/")
SAFE_RE = re.compile(r"python3\s+-B\s+(?:publishing|series|published)/")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    findings = []
    missing = []
    for rel in CHECKED_FILES:
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            if UNSAFE_RE.search(line) and not SAFE_RE.search(line):
                findings.append({"path": rel, "line": line_no, "text": line.strip()[:220]})

    checks = [
        {"name": "checked_files_exist", "status": "pass" if not missing else "fail", "details": "missing=" + (", ".join(missing) if missing else "none")},
        {"name": "active_operator_commands_are_bytecode_safe", "status": "pass" if not findings else "fail", "details": f"unsafe_command_lines={len(findings)}"},
    ]
    failures = [check for check in checks if check["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release.get("revision"),
        "checked_bundle": release.get("bundle"),
        "publication_authorized": False,
        "checked_files": CHECKED_FILES,
        "checks": checks,
        "findings": findings,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "checked_file_count": len(CHECKED_FILES),
            "unsafe_command_line_count": len(findings),
        },
        "fail_closed_rule": "If active operator command hygiene fails, default to no publication and repair unsafe quick-check commands before relying on transient-surface cleanliness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
