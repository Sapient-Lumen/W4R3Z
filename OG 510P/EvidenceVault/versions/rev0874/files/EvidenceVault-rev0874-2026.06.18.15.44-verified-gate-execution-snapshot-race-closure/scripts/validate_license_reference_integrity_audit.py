#!/usr/bin/env python3
"""Validate the local LICENSE/COPYING/NOTICE reference integrity audit."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_license_reference_integrity_audit import build, render_markdown  # noqa: E402

JSON_PATH = ROOT / "RIGHTS" / "license_reference_integrity_audit.json"
MD_PATH = ROOT / "RIGHTS" / "license_reference_integrity_audit.md"


def fail(msg: str) -> None:
    print(f"license-reference-integrity-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    for path in (JSON_PATH, MD_PATH):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT).as_posix()}")
    expected = build(ROOT)
    try:
        actual = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {JSON_PATH.relative_to(ROOT).as_posix()}: {exc}")
    if actual != expected:
        fail("RIGHTS/license_reference_integrity_audit.json is stale relative to current payload references")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(expected):
        fail("RIGHTS/license_reference_integrity_audit.md does not exactly mirror the JSON audit")
    # The current archive should continue surfacing the MCP README missing LICENSE
    # reference until a pinned upstream snapshot and license file are added.
    missing_paths = {row.get("resolved_archive_path") for row in expected.get("missing_or_outside_references", [])}
    required = "sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE"
    if required not in missing_paths:
        fail("expected missing PACT/MCP local LICENSE reference is not surfaced")
    print(
        "license-reference-integrity-validate: OK "
        f"({expected['files_examined']} files, {expected['local_references_missing']} missing local references)"
    )


if __name__ == "__main__":
    main()
