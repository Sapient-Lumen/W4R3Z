#!/usr/bin/env python3
"""Verify deterministic ZIP rebuild from a stdlib-extracted release tree.

This catches release ZIP drift that is not visible in MANIFEST.sha256, especially
metadata such as executable bits that a generic extractor may not preserve.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
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



def build_zip_with_progress(repo_root: Path, out_zip: Path, label: str) -> None:
    """Build a deterministic ZIP while emitting bounded progress for long CI logs."""

    original_reader = build_release_zip._read_source_member_bytes
    count = 0

    def progress_reader(root, rel):
        nonlocal count
        count += 1
        if count % 300 == 0:
            print(f"INFO {label}: read {count} release members", flush=True)
        return original_reader(root, rel)

    build_release_zip._read_source_member_bytes = progress_reader  # type: ignore[attr-defined]
    try:
        build_release_zip.build_zip(repo_root, out_zip)
    finally:
        build_release_zip._read_source_member_bytes = original_reader  # type: ignore[attr-defined]

def build_zip_with_fresh_manifest(out_zip: Path) -> None:
    manifest = ROOT / "MANIFEST.sha256"
    old = manifest.read_bytes() if manifest.exists() else None
    try:
        print("INFO regenerating in-memory manifest for rebuild probe", flush=True)
        manifest.write_text(build_manifest.build_manifest_text(), encoding="utf-8")
        print("INFO writing first deterministic ZIP for rebuild probe", flush=True)
        build_zip_with_progress(ROOT, out_zip, "fresh ZIP build")
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
        for idx, info in enumerate(zf.infolist(), start=1):
            dest = release_path_policy.safe_extract_destination(out_dir, info.filename)
            if dest is None:
                fail(f"unsafe member during extraction probe: {info.filename}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, dest.open("wb") as dst:
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    dst.write(chunk)
            if idx % 100 == 0:
                print(f"INFO extracted {idx} release members", flush=True)


def _cleanup_scratch_nonblocking(path: Path) -> None:
    """Best-effort scratch cleanup without making the release gate wait on rmtree.

    The rebuild probe intentionally creates thousands of extracted files.  On
    some container filesystems, synchronous TemporaryDirectory cleanup can take
    longer than the actual verification and cause the release-gate child step to
    hit its timeout after it has already produced a PASS verdict.  Spawn a
    detached local cleanup process so the gate verdict is not hostage to slow
    scratch deletion.  The scratch tree lives outside the archive root and is
    never release content.
    """

    try:
        if os.name == "posix":
            subprocess.Popen(
                ["rm", "-rf", os.fspath(path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        else:  # pragma: no cover - non-POSIX fallback for local developer runs
            import shutil
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        # Cleanup must not flip a completed rebuild verdict.  The scratch path is
        # outside release scope and can be removed manually if a local host blocks
        # process creation.
        pass


def main() -> int:
    tdir = Path(tempfile.mkdtemp(prefix="tes_zip_rebuild_extract_"))
    try:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        rev = int(version[1:])
        good = tdir / f"The-Election-Stack-rev{rev:04d}.zip"
        rebuilt = tdir / "rebuilt-from-stdlib-extract.zip"
        extract_root = tdir / "extract"
        extract_root.mkdir()

        print("INFO building fresh deterministic release ZIP", flush=True)
        build_zip_with_fresh_manifest(good)
        print("INFO verifying fresh deterministic release ZIP", flush=True)
        result = verify_release_zip.verify_zip(good)
        if not result.ok:
            fail("fresh deterministic release ZIP did not verify: " + "; ".join(result.problems[:10]))

        print("INFO extracting release ZIP with stdlib zipfile", flush=True)
        safe_extract(good, extract_root)
        print("INFO rebuilding ZIP from stdlib-extracted tree", flush=True)
        build_zip_with_progress(extract_root, rebuilt, "rebuild from extract")

        # If the rebuilt carrier is byte-for-byte identical to the already
        # verified fresh release ZIP, a second full verifier pass over the same
        # bytes is redundant.  Compare bytes first and rely on the verified
        # original verdict for the identical rebuild.
        print("INFO comparing original and rebuilt ZIP bytes", flush=True)
        if good.read_bytes() != rebuilt.read_bytes():
            fail(
                "release ZIP is not byte-reproducible after stdlib extraction: "
                f"original={sha256_file(good)} rebuilt={sha256_file(rebuilt)}"
            )

        print("PASS: release ZIP rebuilds byte-for-byte from stdlib-extracted tree")
        return 0
    finally:
        _cleanup_scratch_nonblocking(tdir)


if __name__ == "__main__":
    raise SystemExit(main())
