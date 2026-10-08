#!/usr/bin/env python3
"""Build a deterministic SPDX 2.3 JSON file inventory for EvidenceVault.

The document is intentionally conservative: every file license conclusion is
NOASSERTION until the rights review produces an owner-approved LICENSE/NOTICE and
component conclusions.  The SPDX document excludes itself and the archive's
self-describing digest/index files to avoid impossible hash cycles.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SBOM" / "EvidenceVault-file-inventory.spdx.json"
EXCLUDED_FROM_SPDX = {
    "SBOM/EvidenceVault-file-inventory.spdx.json",
    # MANIFEST.sha256 includes the SPDX document digest, so an SPDX file that
    # also digests MANIFEST.sha256 would require a cryptographic fixed point.
    "MANIFEST.sha256",
    # INDEX/files.* include the SPDX document row; they are regenerated after
    # this SBOM and are intentionally outside the SBOM digest closure.
    "INDEX/files.json",
    "INDEX/files.csv",
}
SKIP_DIR_PARTS = {".git", "__pycache__"}
HEX_SAFE_RE = re.compile(r"[^A-Za-z0-9.-]+")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm.lower().replace("-", ""))
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def spdx_id_for_path(r: str) -> str:
    value = HEX_SAFE_RE.sub("-", r).strip("-")
    return "SPDXRef-File-" + value[:220]


def receipt_created() -> str:
    try:
        receipt = json.loads((ROOT / "REVISION_RECEIPT.json").read_text(encoding="utf-8"))
        ts = receipt["timestamp"]
        year, month, day, hour, minute = ts.split(".")
        return f"{year}-{month}-{day}T{hour}:{minute}:00Z"
    except Exception:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iter_files(root: Path = ROOT):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if not path.is_file():
            continue
        r = rel(path)
        if r in EXCLUDED_FROM_SPDX:
            continue
        yield path


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT
    old_root = ROOT
    ROOT = root
    try:
        receipt = json.loads((ROOT / "REVISION_RECEIPT.json").read_text(encoding="utf-8"))
        files = []
        relationships = []
        for index, path in enumerate(iter_files(ROOT), start=1):
            r = rel(path)
            sid = spdx_id_for_path(r)
            files.append({
                "SPDXID": sid,
                "fileName": f"./{r}",
                "checksums": [
                    {"algorithm": "SHA1", "checksumValue": sha(path, "sha1")},
                    {"algorithm": "SHA256", "checksumValue": sha(path, "sha256")},
                ],
                "licenseConcluded": "NOASSERTION",
                "licenseInfoInFiles": ["NOASSERTION"],
                "copyrightText": "NOASSERTION",
            })
            relationships.append({
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": sid,
            })
            if index % 500 == 0:
                print(f'spdx-inventory-build: inventoried {index}', flush=True)
        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"EvidenceVault {receipt.get('revision', 'unknown')} file inventory",
            "documentNamespace": f"https://example.invalid/evidencevault/{receipt.get('revision', 'unknown')}/spdx/file-inventory",
            "creationInfo": {
                "created": receipt_created(),
                "creators": ["Tool: scripts/build_spdx_inventory.py", "Organization: EvidenceVault session overlay"],
                "licenseListVersion": "3.25",
            },
            "documentComment": "Generated file-level SPDX inventory. License conclusions are intentionally NOASSERTION pending owner/upstream rights review. The SPDX document excludes itself plus MANIFEST.sha256 and INDEX/files.* to avoid digest/index cycles during release refresh.",
            "files": files,
            "relationships": relationships,
            "annotations": [
                {
                    "annotationDate": receipt_created(),
                    "annotationType": "OTHER",
                    "annotator": "Tool: scripts/build_spdx_inventory.py",
                    "comment": "Excluded from file list: " + ", ".join(sorted(EXCLUDED_FROM_SPDX)),
                }
            ],
        }
    finally:
        ROOT = old_root


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = build(ROOT)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"spdx-inventory-build: OK ({len(data['files'])} files, self-exclusion documented)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
