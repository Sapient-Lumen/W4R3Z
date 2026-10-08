#!/usr/bin/env python3
"""Validate rev0834 asset-index refresh-cycle repair."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "AUDIT" / "RELEASE_REFRESH_ASSET_INDEX_REPAIR_REV0834.json"
ASSET_INDEX_FILES = [
    "artifacts/ARTIFACTS_INDEX.json",
    "artifacts/ARTIFACTS_INDEX.csv",
    "certs/CERTS_INDEX.json",
    "certs/CERTS_INDEX.csv",
]


def fail(msg: str) -> None:
    print(f"release-refresh-asset-index-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest_map() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        out[rel] = digest
    return out


def main() -> None:
    # First check the underlying asset indexes with their dedicated validator.
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_asset_indexes.py")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        fail("validate_asset_indexes.py failed: " + (result.stderr or result.stdout).strip())

    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    if data.get("status") != "asset_index_refresh_cycle_repaired":
        fail(f"unexpected audit status: {data.get('status')!r}")
    if data.get("blockers"):
        fail(f"audit blockers present: {data['blockers']!r}")
    snapshot = data.get("asset_index_file_snapshot", {})
    if not snapshot.get("asset_index_files_present_and_parseable"):
        fail("asset-index file snapshot is missing or unparseable")
    order = data.get("rebuild_indexes_refresh_order_status", {})
    if not order.get("rebuild_indexes_includes_build_asset_indexes"):
        fail("rebuild_indexes.py does not include build_asset_indexes.py")
    if not order.get("order_ok"):
        fail("rebuild_indexes.py refresh order is invalid")

    release_manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    digests = release_manifest.get("identity_digests", {})
    if digests.get("artifact_index_json_sha256") != sha256_file(ROOT / "artifacts" / "ARTIFACTS_INDEX.json"):
        fail("RELEASE_MANIFEST artifact_index_json_sha256 mismatch")
    if digests.get("cert_index_json_sha256") != sha256_file(ROOT / "certs" / "CERTS_INDEX.json"):
        fail("RELEASE_MANIFEST cert_index_json_sha256 mismatch")

    manifest = load_manifest_map()
    index_rows = {
        row["path"]: row
        for row in json.loads((ROOT / "INDEX" / "files.json").read_text(encoding="utf-8"))
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    for rel in ASSET_INDEX_FILES:
        current = sha256_file(ROOT / rel)
        if manifest.get(rel) != current:
            fail(f"MANIFEST.sha256 is stale for {rel}")
        row = index_rows.get(rel)
        if row is None or row.get("sha256") != current:
            fail(f"INDEX/files.json is stale for {rel}")

    print("release-refresh-asset-index-validate: OK")


if __name__ == "__main__":
    main()
