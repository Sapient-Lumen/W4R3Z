#!/usr/bin/env python3
"""Validate the rev0839 rebuild-index material-surface subprocess isolation audit."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_rebuild_indexes_subprocess_refresh_audit_rev0839 import JSON_OUT, MD_OUT, build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"rebuild-indexes-subprocess-refresh-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    expected = build()
    if expected["status"] != "material_surface_refresh_uses_subprocess_isolation":
        fail(expected["status"])
    if not JSON_OUT.is_file() or not MD_OUT.is_file():
        fail("audit files are missing")
    try:
        actual = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid {JSON_OUT.relative_to(ROOT).as_posix()}: {exc}")
    if actual != expected:
        fail(f"{JSON_OUT.relative_to(ROOT).as_posix()} is stale")
    if MD_OUT.read_text(encoding="utf-8") != render_markdown(expected):
        fail(f"{MD_OUT.relative_to(ROOT).as_posix()} is stale")
    print("rebuild-indexes-subprocess-refresh-validate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
