#!/usr/bin/env python3
"""Validate absolute path reference audit surfaces."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_absolute_path_reference_audit import build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"absolute-path-reference-audit-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    expected = build(ROOT)
    json_path = ROOT / "AUDIT" / "ABSOLUTE_PATH_REFERENCE_AUDIT.json"
    md_path = ROOT / "AUDIT" / "ABSOLUTE_PATH_REFERENCE_AUDIT.md"
    if not json_path.is_file() or not md_path.is_file():
        fail("missing AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json or .md")
    try:
        actual = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json: {exc}")
    if actual != expected:
        fail("AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json is stale relative to current text payloads")
    if md_path.read_text(encoding="utf-8") != render_markdown(expected):
        fail("AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.md does not exactly mirror JSON audit output")
    print(
        "absolute-path-reference-audit-validate: OK "
        f"({expected['summary']['files_with_absolute_path_references']} files, "
        f"{expected['summary']['absolute_path_reference_count']} references surfaced)"
    )


if __name__ == "__main__":
    main()
