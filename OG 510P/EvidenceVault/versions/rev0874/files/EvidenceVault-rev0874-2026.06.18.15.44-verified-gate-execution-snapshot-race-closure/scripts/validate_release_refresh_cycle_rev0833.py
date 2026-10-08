#!/usr/bin/env python3
"""Validate the rev0833 release-refresh cycle repair.

The core invariant: generated rights/SBOM surfaces may be rebuilt during the
normal release refresh path, and the final MANIFEST/INDEX may then describe
those generated surfaces, but the generated surfaces must not in turn digest or
byte-count the final MANIFEST/INDEX files. Otherwise a canonical release rebuild
would require an impossible hash/count fixed point or would leave stale ledgers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_rights_readiness import GENERATED_DIGEST_CYCLE_EXCLUSIONS as RIGHTS_EXCLUSIONS  # noqa: E402
from build_spdx_inventory import EXCLUDED_FROM_SPDX  # noqa: E402

REQUIRED_SPDX_EXCLUSIONS = {
    "SBOM/EvidenceVault-file-inventory.spdx.json",
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}
REQUIRED_RIGHTS_EXCLUSIONS = {
    "RELEASE_MANIFEST.json",
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}
REQUIRED_REFRESH_BUILDERS = [
    "build_upstream_retention_coverage",
    "build_absolute_path_reference_audit",
    "build_path_reference_shape_audit",
    "build_rights_evidence_scan",
    "build_license_reference_integrity_audit",
    "build_rights_readiness",
    "build_spdx_inventory",
]
AUDIT_JSON = ROOT / "AUDIT" / "RELEASE_REFRESH_CYCLE_AUDIT_REV0833.json"
AUDIT_MD = ROOT / "AUDIT" / "RELEASE_REFRESH_CYCLE_AUDIT_REV0833.md"


def fail(msg: str) -> None:
    print(f"release-refresh-cycle-rev0833-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def manifest_paths() -> set[str]:
    rows = set()
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            _digest, rel = line.split(None, 1)
        except ValueError:
            fail("MANIFEST.sha256 contains malformed row")
        rows.add(rel.strip())
    return rows


def spdx_file_names() -> set[str]:
    try:
        data = json.loads((ROOT / "SBOM" / "EvidenceVault-file-inventory.spdx.json").read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot parse SPDX inventory: {exc}")
    files = data.get("files")
    if not isinstance(files, list):
        fail("SPDX inventory files member is not a list")
    return {row.get("fileName") for row in files if isinstance(row, dict)}


def main() -> None:
    if not REQUIRED_SPDX_EXCLUSIONS.issubset(EXCLUDED_FROM_SPDX):
        fail("build_spdx_inventory.py does not declare the required digest-cycle exclusions")
    if not REQUIRED_RIGHTS_EXCLUSIONS.issubset(RIGHTS_EXCLUSIONS):
        fail("build_rights_readiness.py does not declare the required generated-index exclusions")

    names = spdx_file_names()
    forbidden_spdx_names = {f"./{rel}" for rel in REQUIRED_SPDX_EXCLUSIONS}
    present = sorted(names & forbidden_spdx_names)
    if present:
        fail(f"SPDX inventory includes excluded digest-cycle paths: {present}")

    rows = manifest_paths()
    if "SBOM/EvidenceVault-file-inventory.spdx.json" not in rows:
        fail("MANIFEST.sha256 does not cover the SPDX inventory")
    for rel in ("INDEX/files.json", "INDEX/files.csv"):
        if rel not in rows:
            fail(f"MANIFEST.sha256 does not cover generated index file: {rel}")

    rebuild_source = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    if "refresh_cycle_safe_material_surfaces" not in rebuild_source:
        fail("rebuild_indexes.py is missing refresh_cycle_safe_material_surfaces")
    for builder in REQUIRED_REFRESH_BUILDERS:
        if builder not in rebuild_source:
            fail(f"rebuild_indexes.py does not refresh {builder}.py")

    for path in (AUDIT_JSON, AUDIT_MD):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT).as_posix()}")
    try:
        audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid rev0833 audit JSON: {exc}")
    if audit.get("status") != "release_refresh_cycle_repaired":
        fail("rev0833 audit status mismatch")
    if audit.get("spdx_excluded_paths") != sorted(REQUIRED_SPDX_EXCLUSIONS):
        fail("rev0833 audit SPDX exclusion list mismatch")
    if audit.get("rights_byte_count_excluded_paths") != sorted(REQUIRED_RIGHTS_EXCLUSIONS):
        fail("rev0833 audit rights exclusion list mismatch")
    if audit.get("refresh_builders") != REQUIRED_REFRESH_BUILDERS:
        fail("rev0833 audit refresh builder list mismatch")

    print(
        "release-refresh-cycle-rev0833-validate: OK "
        f"({len(REQUIRED_REFRESH_BUILDERS)} refreshed builders, "
        f"{len(REQUIRED_SPDX_EXCLUSIONS)} SPDX cycle exclusions)"
    )


if __name__ == "__main__":
    main()
