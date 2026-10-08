#!/usr/bin/env python3
"""Validate rights-readiness/component license triage surfaces."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_rights_readiness import GENERATED_DIGEST_CYCLE_EXCLUSIONS, build, render_markdown  # noqa: E402

REQUIRED_RIGHTS_COUNT_EXCLUSIONS = {"RELEASE_MANIFEST.json", "MANIFEST.sha256", "INDEX/files.json", "INDEX/files.csv"}


def fail(msg: str) -> None:
    print(f"rights-readiness-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    expected = build(ROOT)
    if not REQUIRED_RIGHTS_COUNT_EXCLUSIONS.issubset(GENERATED_DIGEST_CYCLE_EXCLUSIONS):
        fail("rights readiness builder is missing required generated digest/index exclusions")
    json_path = ROOT / "RIGHTS" / "component_license_ledger.json"
    md_path = ROOT / "RIGHTS" / "component_license_ledger.md"
    blocker = ROOT / "RIGHTS" / "LICENSE_DECISION_BLOCKER.md"
    notice = ROOT / "RIGHTS" / "NOTICE.draft"
    reference_audit = ROOT / "RIGHTS" / "license_reference_integrity_audit.json"
    for path in (json_path, md_path, blocker, notice, reference_audit):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT).as_posix()}")
    try:
        actual = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in RIGHTS/component_license_ledger.json: {exc}")
    if actual != expected:
        fail("RIGHTS/component_license_ledger.json is stale relative to current rights inputs/filesystem")
    if md_path.read_text(encoding="utf-8") != render_markdown(expected):
        fail("RIGHTS/component_license_ledger.md does not exactly mirror JSON readiness output")
    if expected["ro_crate_root_license_value"] == "See README.md":
        fail("RO-Crate root license remains an unresolved README pointer")
    if expected.get("missing_or_outside_local_license_reference_count", 0) < 1:
        fail("rights readiness should surface at least one unresolved local license-reference target in the current archive")
    if not any(f.get("id") == "missing_local_license_reference_targets" for f in expected.get("blocking_findings", [])):
        fail("rights readiness is not treating missing local license-reference targets as a blocker")
    if expected["decision_required_before_publication"] and not blocker.is_file():
        fail("publication is blocked but RIGHTS/LICENSE_DECISION_BLOCKER.md is missing")
    print(
        "rights-readiness-validate: OK "
        f"({len(expected['components'])} components, {len(expected['blocking_findings'])} blockers surfaced)"
    )


if __name__ == "__main__":
    main()
