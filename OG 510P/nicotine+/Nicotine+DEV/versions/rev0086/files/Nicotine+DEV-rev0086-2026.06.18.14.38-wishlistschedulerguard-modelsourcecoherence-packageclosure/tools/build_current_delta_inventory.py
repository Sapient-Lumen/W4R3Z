#!/usr/bin/env python3
"""Build a revision-neutral file delta against the prior cube archive."""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    digest_stream,
    sha256_path,
    write_csv,
    write_json,
)



def excluded_outputs(revision: str) -> set[Path]:
    return {
        Path(f"data/{revision}_delta_inventory.csv"),
        Path(f"data/{revision}_delta_inventory.json"),
        Path(f"handoff/{revision}/MANIFEST.sha256"),
        Path(f"data/{revision}_package_audit.json"),
        Path(f"evidence/{revision}-package-validation.md"),
    }


def previous_files(path: Path, excluded: set[Path]) -> dict[Path, tuple[str, int]]:
    rows: dict[Path, tuple[str, int]] = {}
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name and not name.endswith("/")]
        roots = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
        if len(roots) != 1:
            raise ValueError(f"expected one top-level directory, found {sorted(roots)}")
        root = next(iter(roots))
        prefix = root + "/"
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts or not name.startswith(prefix):
                raise ValueError(f"unsafe or rootless archive entry: {name}")
            relative = Path(*PurePosixPath(name[len(prefix):]).parts)
            if relative in excluded:
                continue
            with archive.open(name) as handle:
                rows[relative] = digest_stream(handle)
    return rows


def current_files(root: Path, excluded: set[Path]) -> dict[Path, tuple[str, int]]:
    rows: dict[Path, tuple[str, int]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if relative in excluded:
            continue
        rows[relative] = (sha256_path(path), path.stat().st_size)
    return rows


def build(root: Path, previous_zip: Path) -> dict[str, object]:
    revision = derive_revision(root)
    excluded = excluded_outputs(revision)
    old = previous_files(previous_zip, excluded)
    new = current_files(root, excluded)
    rows: list[dict[str, object]] = []
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
    counts = {
        name: sum(row["status"] == name for row in rows)
        for name in ("added", "modified", "deleted")
    }
    return {
        "revision": revision,
        "status": "pass",
        "previous_archive": previous_zip.name,
        "previous_archive_sha256": sha256_path(previous_zip),
        "previous_files": len(old),
        "current_files_excluding_finalization_outputs": len(new),
        "excluded_paths": sorted(path.as_posix() for path in excluded),
        "changed_rows": len(rows),
        "counts": counts,
        "net_byte_delta_for_changed_paths": sum(int(row["byte_delta"]) for row in rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--previous-zip", type=Path, required=True)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = build(root, args.previous_zip.resolve())
    revision = str(result["revision"])
    if args.write_data:
        rows = list(result["rows"])
        write_json(root / f"data/{revision}_delta_inventory.json", result)
        write_csv(
            root / f"data/{revision}_delta_inventory.csv",
            rows,
            fields=(
                "path", "status", "old_bytes", "new_bytes", "byte_delta",
                "old_sha256", "new_sha256",
            ),
        )
    print(canonical_json({key: value for key, value in result.items() if key != "rows"}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
