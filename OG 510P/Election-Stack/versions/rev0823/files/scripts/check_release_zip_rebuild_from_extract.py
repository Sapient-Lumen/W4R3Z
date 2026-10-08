#!/usr/bin/env python3
"""Verify deterministic ZIP rebuild from a stdlib-extracted release tree.

This catches release ZIP drift that is not visible in MANIFEST.sha256, especially
metadata such as executable bits that a generic extractor may not preserve.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import build_release_zip
import verify_release_zip
import release_path_policy

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_zip_with_fresh_manifest(out_zip: Path) -> None:
    manifest = ROOT / "MANIFEST.sha256"
    old = manifest.read_bytes() if manifest.exists() else None
    try:
        manifest.write_text(build_manifest.build_manifest_text(), encoding="utf-8")
        build_release_zip.build_zip(ROOT, out_zip)
    finally:
        if old is None:
            try:
                manifest.unlink()
            except FileNotFoundError:
                pass
        else:
            manifest.write_bytes(old)


def safe_extract(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            dest = release_path_policy.safe_extract_destination(out_dir, info.filename)
            if dest is None:
                fail(f"unsafe member during extraction probe: {info.filename}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, dest.open("wb") as dst:
                dst.write(src.read())


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tes_zip_rebuild_extract_") as td:
        tdir = Path(td)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        rev = int(version[1:])
        good = tdir / f"The-Election-Stack-rev{rev:04d}.zip"
        rebuilt = tdir / "rebuilt-from-stdlib-extract.zip"
        extract_root = tdir / "extract"
        extract_root.mkdir()

        build_zip_with_fresh_manifest(good)
        result = verify_release_zip.verify_zip(good)
        if not result.ok:
            fail("fresh deterministic release ZIP did not verify: " + "; ".join(result.problems[:10]))

        safe_extract(good, extract_root)
        build_release_zip.build_zip(extract_root, rebuilt)
        rebuilt_result = verify_release_zip.verify_zip(rebuilt)
        if not rebuilt_result.ok:
            fail("rebuilt ZIP did not verify: " + "; ".join(rebuilt_result.problems[:10]))

        if good.read_bytes() != rebuilt.read_bytes():
            fail(
                "release ZIP is not byte-reproducible after stdlib extraction: "
                f"original={sha256_file(good)} rebuilt={sha256_file(rebuilt)}"
            )

    print("PASS: release ZIP rebuilds byte-for-byte from stdlib-extracted tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
