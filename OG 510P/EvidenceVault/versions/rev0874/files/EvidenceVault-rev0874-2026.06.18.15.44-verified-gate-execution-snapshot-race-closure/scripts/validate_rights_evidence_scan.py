#!/usr/bin/env python3
"""Validate rights evidence scan surfaces."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_rights_evidence_scan import build, render_markdown  # noqa: E402

JSON_PATH = ROOT / "RIGHTS" / "license_evidence_scan.json"
MD_PATH = ROOT / "RIGHTS" / "license_evidence_scan.md"


def fail(msg: str) -> None:
    print(f"rights-evidence-scan-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        fail("missing RIGHTS/license_evidence_scan.json or .md")
    try:
        actual = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON: {exc}")
    expected = build(ROOT)
    if actual != expected:
        fail("RIGHTS/license_evidence_scan.json is stale")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(expected):
        fail("RIGHTS/license_evidence_scan.md is stale")
    print(
        "rights-evidence-scan-validate: OK "
        f"({expected['summary']['files_with_rights_evidence']} evidence files)"
    )


if __name__ == "__main__":
    main()
