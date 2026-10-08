#!/usr/bin/env python3
"""Validate deterministic SPDX file inventory."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_spdx_inventory import EXCLUDED_FROM_SPDX, OUT, build  # noqa: E402

REQUIRED_DIGEST_CYCLE_EXCLUSIONS = {
    "SBOM/EvidenceVault-file-inventory.spdx.json",
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}


def fail(msg: str) -> None:
    print(f"spdx-inventory-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not OUT.is_file():
        fail("missing SBOM/EvidenceVault-file-inventory.spdx.json")
    try:
        actual = json.loads(OUT.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid SPDX JSON: {exc}")
    expected = build(ROOT)
    if actual != expected:
        fail("SBOM/EvidenceVault-file-inventory.spdx.json is stale relative to current filesystem")
    if actual.get("spdxVersion") != "SPDX-2.3":
        fail("unexpected SPDX version")
    if not REQUIRED_DIGEST_CYCLE_EXCLUSIONS.issubset(EXCLUDED_FROM_SPDX):
        fail("SPDX builder is missing required digest-cycle exclusions")
    files = actual.get("files")
    if not isinstance(files, list) or not files:
        fail("SPDX files list is empty or invalid")
    file_names = {row.get("fileName") for row in files}
    forbidden_file_names = {f"./{rel}" for rel in REQUIRED_DIGEST_CYCLE_EXCLUSIONS}
    present_forbidden = sorted(file_names & forbidden_file_names)
    if present_forbidden:
        fail(f"SPDX file inventory includes digest-cycle-excluded paths: {present_forbidden}")
    if any(row.get("licenseConcluded") != "NOASSERTION" for row in files):
        fail("file licenseConcluded values must remain NOASSERTION until rights review is completed")
    described = {rel.get("relatedSpdxElement") for rel in actual.get("relationships", []) if rel.get("relationshipType") == "DESCRIBES"}
    file_ids = {row.get("SPDXID") for row in files}
    if described != file_ids:
        fail("SPDX DESCRIBES relationships do not exactly cover file SPDX IDs")
    print(f"spdx-inventory-validate: OK ({len(files)} files, SHA1/SHA256 checksums, NOASSERTION licenses)")


if __name__ == "__main__":
    main()
