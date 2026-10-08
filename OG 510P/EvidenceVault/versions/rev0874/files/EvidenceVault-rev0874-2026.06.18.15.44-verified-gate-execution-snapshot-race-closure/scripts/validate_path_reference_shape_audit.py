#!/usr/bin/env python3
"""Validate path-reference shape audit surfaces."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_path_reference_shape_audit import build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"path-reference-shape-audit-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    expected = build(ROOT)
    json_path = ROOT / "AUDIT" / "PATH_REFERENCE_SHAPE_AUDIT.json"
    md_path = ROOT / "AUDIT" / "PATH_REFERENCE_SHAPE_AUDIT.md"
    if not json_path.is_file() or not md_path.is_file():
        fail("missing AUDIT/PATH_REFERENCE_SHAPE_AUDIT.json or .md")
    try:
        actual = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in path-reference shape audit: {exc}")
    if actual != expected:
        fail("AUDIT/PATH_REFERENCE_SHAPE_AUDIT.json is stale relative to current text payloads")
    if md_path.read_text(encoding="utf-8") != render_markdown(expected):
        fail("AUDIT/PATH_REFERENCE_SHAPE_AUDIT.md does not exactly mirror JSON audit output")
    print(
        "path-reference-shape-audit-validate: OK "
        f"({expected['summary']['files_with_shape_anomalies']} files, {expected['summary']['shape_anomaly_count']} findings)"
    )


if __name__ == "__main__":
    main()
