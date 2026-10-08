#!/usr/bin/env python3
"""Build a file-level rev0075 -> rev0076 delta inventory."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import BinaryIO

REVISION = "rev0076"
SELF_OUTPUTS = {
    Path("data/rev0076_delta_inventory.csv"),
    Path("data/rev0076_delta_inventory.json"),
    Path("handoff/rev0076/MANIFEST.sha256"),
    Path("data/rev0076_package_audit.json"),
    Path("evidence/rev0076-package-validation.md"),
}


def digest_stream(handle: BinaryIO) -> tuple[str, int]:
    value = hashlib.sha256()
    total = 0
    for chunk in iter(lambda: handle.read(1 << 20), b""):
        value.update(chunk)
        total += len(chunk)
    return value.hexdigest(), total


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
        prefix = next(iter(roots)) + "/"
        for name in names:
            if not name.startswith(prefix):
                raise ValueError(f"entry escapes top-level directory: {name}")
            relative = Path(name[len(prefix):])
            if relative in SELF_OUTPUTS:
                continue
            with archive.open(name) as handle:
                rows[relative] = digest_stream(handle)
    return rows


def current_files(root: Path) -> dict[Path, tuple[str, int]]:
    rows: dict[Path, tuple[str, int]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if relative in SELF_OUTPUTS:
            continue
        rows[relative] = digest_file(path)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--previous-zip", type=Path, required=True)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    previous_zip = args.previous_zip.resolve()
    old = previous_files(previous_zip)
    new = current_files(root)
    rows = []
    for path in sorted(set(old) | set(new)):
        old_hash, old_bytes = old.get(path, ("", 0))
        new_hash, new_bytes = new.get(path, ("", 0))
        if path not in old:
            status = "added"
        elif path not in new:
            status = "deleted"
        elif old_hash != new_hash:
            status = "modified"
        else:
            continue
        rows.append({
            "path": path.as_posix(),
            "status": status,
            "old_bytes": old_bytes,
            "new_bytes": new_bytes,
            "byte_delta": new_bytes - old_bytes,
            "old_sha256": old_hash,
            "new_sha256": new_hash,
        })
    counts = {name: sum(row["status"] == name for row in rows) for name in ("added", "modified", "deleted")}
    result = {
        "revision": REVISION,
        "previous_archive": previous_zip.name,
        "previous_archive_sha256": digest_file(previous_zip)[0],
        "previous_files": len(old),
        "current_files_excluding_finalization_outputs": len(new),
        "excluded_paths": sorted(path.as_posix() for path in SELF_OUTPUTS),
        "changed_rows": len(rows),
        "counts": counts,
        "net_byte_delta_for_changed_paths": sum(int(row["byte_delta"]) for row in rows),
        "rows": rows,
    }
    if args.write_data:
        data = root / "data"
        data.mkdir(exist_ok=True)
        (data / "rev0076_delta_inventory.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with (data / "rev0076_delta_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=(
                "path", "status", "old_bytes", "new_bytes", "byte_delta", "old_sha256", "new_sha256",
            ))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
