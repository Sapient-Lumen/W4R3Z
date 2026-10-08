#!/usr/bin/env python3
"""Build a file-level rev0074 -> rev0075 delta inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import BinaryIO

REVISION = "rev0075"
SELF_OUTPUTS = {
    Path("data/rev0075_delta_inventory.csv"),
    Path("data/rev0075_delta_inventory.json"),
    Path("handoff/rev0075/MANIFEST.sha256"),
    Path("data/rev0075_package_preflight.json"),
    Path("evidence/rev0075-package-validation.md"),
}


def digest_stream(handle: BinaryIO) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
        total += len(chunk)
    return digest.hexdigest(), total


def digest_file(path: Path) -> tuple[str, int]:
    with path.open("rb") as handle:
        return digest_stream(handle)


def previous_files(path: Path) -> dict[Path, tuple[str, int]]:
    rows: dict[Path, tuple[str, int]] = {}
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name and not name.endswith("/")]
        roots = {name.split("/", 1)[0] for name in names if "/" in name}
        if len(roots) != 1:
            raise ValueError(f"expected one top-level directory, found {sorted(roots)}")
        root = next(iter(roots)) + "/"
        for name in names:
            if not name.startswith(root):
                raise ValueError(f"entry escapes top-level directory: {name}")
            relative = Path(name[len(root):])
            with archive.open(name) as handle:
                rows[relative] = digest_stream(handle)
    return rows


def current_files(root: Path) -> dict[Path, tuple[str, int]]:
    rows: dict[Path, tuple[str, int]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative in SELF_OUTPUTS:
            continue
        rows[relative] = digest_file(path)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--previous-zip", type=Path, required=True)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    old = previous_files(args.previous_zip.resolve())
    new = current_files(root)
    paths = sorted(set(old) | set(new))
    rows: list[dict[str, object]] = []

    for path in paths:
        old_digest, old_bytes = old.get(path, ("", 0))
        new_digest, new_bytes = new.get(path, ("", 0))
        if path not in old:
            status = "added"
        elif path not in new:
            status = "deleted"
        elif old_digest != new_digest:
            status = "modified"
        else:
            status = "unchanged"
        if status == "unchanged":
            continue
        rows.append({
            "path": str(path),
            "status": status,
            "old_bytes": old_bytes,
            "new_bytes": new_bytes,
            "byte_delta": new_bytes - old_bytes,
            "old_sha256": old_digest,
            "new_sha256": new_digest,
        })

    counts = {status: sum(row["status"] == status for row in rows) for status in ("added", "modified", "deleted")}
    summary = {
        "revision": REVISION,
        "previous_archive": args.previous_zip.name,
        "previous_archive_sha256": digest_file(args.previous_zip.resolve())[0],
        "previous_files": len(old),
        "current_files_excluding_finalization_outputs_and_manifest": len(new),
        "excluded_paths": sorted(str(path) for path in SELF_OUTPUTS),
        "changed_rows": len(rows),
        "counts": counts,
        "net_byte_delta_for_changed_paths": sum(int(row["byte_delta"]) for row in rows),
        "rows": rows,
    }

    if args.write_data:
        data = root / "data"
        data.mkdir(parents=True, exist_ok=True)
        json_path = data / "rev0075_delta_inventory.json"
        csv_path = data / "rev0075_delta_inventory.csv"
        json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=(
                "path", "status", "old_bytes", "new_bytes", "byte_delta", "old_sha256", "new_sha256"
            ))
            writer.writeheader()
            writer.writerows(rows)

    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
