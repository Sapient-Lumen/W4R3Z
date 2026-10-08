#!/usr/bin/env python3
"""Validate rev0835 release-refresh freshness repair.

This validator catches the class of problem found after rev0834: a cumulative
patch could apply cleanly and pass identity checks while generated freshness
surfaces such as DEDUPE_REPORT.md or RIGHTS/component_license_ledger.* remained
stale.  It intentionally checks live builder output rather than only checking
that an audit file exists.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dedupe_report  # noqa: E402
import build_rights_readiness  # noqa: E402
from build_spdx_inventory import EXCLUDED_FROM_SPDX  # noqa: E402

AUDIT_JSON = ROOT / "AUDIT" / "RELEASE_REFRESH_FRESHNESS_REPAIR_REV0835.json"
AUDIT_MD = ROOT / "AUDIT" / "RELEASE_REFRESH_FRESHNESS_REPAIR_REV0835.md"
REQUIRED_DEDUPE_EXCLUSIONS = {
    "DEDUPE_REPORT.md",
    "SBOM/EvidenceVault-file-inventory.spdx.json",
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}
REQUIRED_SPDX_EXCLUSIONS = {
    "SBOM/EvidenceVault-file-inventory.spdx.json",
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}


def fail(msg: str) -> None:
    print(f"release-refresh-freshness-rev0835-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def manifest_paths() -> set[str]:
    rows = set()
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            _digest, rel = line.split(None, 1)
        except ValueError:
            fail("MANIFEST.sha256 contains a malformed row")
        rows.add(rel.strip())
    return rows


def spdx_file_names() -> set[str]:
    data = json.loads((ROOT / "SBOM" / "EvidenceVault-file-inventory.spdx.json").read_text(encoding="utf-8"))
    files = data.get("files")
    if not isinstance(files, list):
        fail("SPDX inventory files field is not a list")
    return {row.get("fileName") for row in files if isinstance(row, dict)}


def main() -> None:
    for path in (AUDIT_JSON, AUDIT_MD):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT).as_posix()}")
    try:
        audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid audit JSON: {exc}")
    if audit.get("status") != "release_refresh_freshness_repaired":
        fail("audit status mismatch")
    if set(audit.get("dedupe_excluded_paths", [])) != REQUIRED_DEDUPE_EXCLUSIONS:
        fail("audit dedupe exclusion list mismatch")

    if set(build_dedupe_report.EXCLUDE) != REQUIRED_DEDUPE_EXCLUSIONS:
        fail("build_dedupe_report.py does not exclude the required generated-surface paths")
    expected_dedupe = build_dedupe_report.render()
    if (ROOT / "DEDUPE_REPORT.md").read_text(encoding="utf-8") != expected_dedupe:
        fail("DEDUPE_REPORT.md is stale relative to current builder output")

    expected_rights = build_rights_readiness.build(ROOT)
    rights_json_path = ROOT / "RIGHTS" / "component_license_ledger.json"
    rights_md_path = ROOT / "RIGHTS" / "component_license_ledger.md"
    actual_rights = json.loads(rights_json_path.read_text(encoding="utf-8"))
    if actual_rights != expected_rights:
        fail("RIGHTS/component_license_ledger.json is stale relative to current builder output")
    if rights_md_path.read_text(encoding="utf-8") != build_rights_readiness.render_markdown(expected_rights):
        fail("RIGHTS/component_license_ledger.md is stale relative to current builder output")

    rebuild = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    for snippet in ("import build_dedupe_report", "build_dedupe_report.main()", "import build_spdx_inventory"):
        if snippet not in rebuild:
            fail(f"rebuild_indexes.py missing freshness-refresh snippet: {snippet}")
    if rebuild.index("build_dedupe_report.main()") > rebuild.index("build_spdx_inventory.main()"):
        fail("rebuild_indexes.py must refresh DEDUPE_REPORT.md before SPDX inventory")

    if not REQUIRED_SPDX_EXCLUSIONS.issubset(EXCLUDED_FROM_SPDX):
        fail("SPDX builder no longer declares required digest-cycle exclusions")
    names = spdx_file_names()
    forbidden_spdx_names = {f"./{rel}" for rel in REQUIRED_SPDX_EXCLUSIONS}
    present_forbidden = sorted(names & forbidden_spdx_names)
    if present_forbidden:
        fail(f"SPDX inventory includes forbidden digest-cycle paths: {present_forbidden}")
    if "./DEDUPE_REPORT.md" not in names:
        fail("SPDX inventory should digest DEDUPE_REPORT.md after dedupe has settled")

    rows = manifest_paths()
    for rel in ("DEDUPE_REPORT.md", "SBOM/EvidenceVault-file-inventory.spdx.json"):
        if rel not in rows:
            fail(f"MANIFEST.sha256 does not cover {rel}")

    print("release-refresh-freshness-rev0835-validate: OK (dedupe/rights/SPDX refresh chain live)")


if __name__ == "__main__":
    main()
