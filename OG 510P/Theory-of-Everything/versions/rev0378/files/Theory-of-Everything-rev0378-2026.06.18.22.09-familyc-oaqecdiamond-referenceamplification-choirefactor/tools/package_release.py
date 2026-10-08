#!/usr/bin/env python3
"""Build a deterministic release zip from the source tree.

The release archive is an output artifact, not a source input. This tool removes
local transients, excludes nested release archives, writes files in stable order,
and fixes zip metadata from the manifest timestamp so a clean extraction can
rebuild byte-identical package bytes.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import stat
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

TRANSIENT_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git"}
TRANSIENT_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".tmp",
    ".swp",
    ".zip",
}
TRANSIENT_FILE_NAMES = {".DS_Store"}
DEFAULT_ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def canonical_release_root_name(manifest: dict) -> str:
    bundle = manifest["bundle"]
    return bundle[:-4] if bundle.endswith(".zip") else bundle


def manifest_zip_date_time(manifest: dict) -> tuple[int, int, int, int, int, int]:
    """Return a stable zip timestamp derived from YYYY.MM.DD.HH.MM manifest time."""
    try:
        year, month, day, hour, minute = [int(part) for part in str(manifest["timestamp"]).split(".")]
    except Exception:
        return DEFAULT_ZIP_DATE_TIME
    if year < 1980:
        return DEFAULT_ZIP_DATE_TIME
    return (year, month, day, hour, minute, 0)


def is_transient_release_path(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in TRANSIENT_DIR_NAMES for part in rel.parts):
        return True
    if path.name in TRANSIENT_FILE_NAMES:
        return True
    if path.suffix in TRANSIENT_FILE_SUFFIXES:
        return True
    return False


def remove_transients(root: Path) -> None:
    for p in sorted(root.rglob("*"), key=lambda path: len(path.parts), reverse=True):
        if p == root or not is_transient_release_path(p, root):
            continue
        if p.is_dir():
            shutil.rmtree(p)
        elif p.is_file():
            p.unlink()


def iter_release_files(root: Path) -> list[Path]:
    return sorted(
        (p for p in root.rglob("*") if p.is_file() and not is_transient_release_path(p, root)),
        key=lambda p: p.relative_to(root).as_posix(),
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_info_for(path: Path, arcname: Path, date_time: tuple[int, int, int, int, int, int]) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname.as_posix(), date_time=date_time)
    info.compress_type = zipfile.ZIP_DEFLATED
    # Normalize file mode as well as timestamp. Some extraction tools do not
    # round-trip executable bits, so preserving local chmod state would make a
    # clean extracted rebuild byte-drift from the source-tree build.
    mode = 0o644
    info.external_attr = (stat.S_IFREG | mode) << 16
    return info


def build_release(root: Path) -> Path:
    remove_transients(root)
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text())
    out = root.parent / manifest["bundle"]
    archive_root = Path(canonical_release_root_name(manifest))
    date_time = manifest_zip_date_time(manifest)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        for p in iter_release_files(root):
            arcname = archive_root / p.relative_to(root)
            zf.writestr(zip_info_for(p, arcname, date_time), p.read_bytes(), compresslevel=1)
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = build_release(root)
    print(out)
    print(f"sha256={sha256_file(out)}")


if __name__ == "__main__":
    main()
