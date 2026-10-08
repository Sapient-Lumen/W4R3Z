#!/usr/bin/env python3
"""Validate the rev0836 rights/release-manifest count-cycle repair."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_rights_readiness import GENERATED_DIGEST_CYCLE_EXCLUSIONS  # noqa: E402

AUDIT_JSON = ROOT / "AUDIT" / "RIGHTS_RELEASE_MANIFEST_COUNT_CYCLE_REV0836.json"
AUDIT_MD = ROOT / "AUDIT" / "RIGHTS_RELEASE_MANIFEST_COUNT_CYCLE_REV0836.md"
LEDGER = ROOT / "RIGHTS" / "component_license_ledger.json"
REQUIRED = "RELEASE_MANIFEST.json"


def fail(msg: str) -> None:
    print(f"rights-release-manifest-cycle-rev0836-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if REQUIRED not in GENERATED_DIGEST_CYCLE_EXCLUSIONS:
        fail("build_rights_readiness.py does not exclude RELEASE_MANIFEST.json from rights byte counts")
    for path in (AUDIT_JSON, AUDIT_MD, LEDGER):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT).as_posix()}")
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    if audit.get("status") != "rights_release_manifest_count_cycle_repaired":
        fail("audit status mismatch")
    if audit.get("required_exclusion") != REQUIRED:
        fail("audit required exclusion mismatch")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    exclusions = set(ledger.get("generated_digest_cycle_exclusions", []))
    if REQUIRED not in exclusions:
        fail("component license ledger does not record RELEASE_MANIFEST.json as an excluded generated surface")
    rev0833 = json.loads((ROOT / "AUDIT" / "RELEASE_REFRESH_CYCLE_AUDIT_REV0833.json").read_text(encoding="utf-8"))
    if REQUIRED not in set(rev0833.get("rights_byte_count_excluded_paths", [])):
        fail("rev0833 release-refresh audit does not record the rev0836 rights exclusion")
    print("rights-release-manifest-cycle-rev0836-validate: OK (RELEASE_MANIFEST.json rights count-cycle exclusion present)")


if __name__ == "__main__":
    main()
