#!/usr/bin/env python3
"""Release-gate smoke test for scripts/verify_release_zip.py.

The release gate already checks the extracted tree. This check exercises the
archive-artifact verifier against a freshly built deterministic ZIP and then
runs small probes so the verifier cannot silently mix multiple reads of the
input path or accept lexically ambiguous or symlink-routed inputs, duplicate,
unsafe, compressed-method, hash-mismatched, or byte-noncanonical archives.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import build_release_zip
import verify_release_zip

ROOT = Path(__file__).resolve().parents[1]
FIXED_ZIP_DT = verify_release_zip.FIXED_ZIP_DT


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def zipinfo(name: str, *, mode: int = 0o644) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(name)
    zi.compress_type = zipfile.ZIP_STORED
    zi.date_time = FIXED_ZIP_DT
    zi.create_system = 3
    zi.create_version = 20
    zi.extract_version = 20
    zi.flag_bits = 0
    zi.external_attr = (mode & 0xFFFF) << 16
    return zi


def write_entry(zf: zipfile.ZipFile, name: str, data: bytes, *, mode: int = 0o644) -> None:
    zf.writestr(zipinfo(name, mode=mode), data)


def build_zip_with_fresh_manifest(out_zip: Path) -> None:
    """Build a ZIP using a freshly computed manifest without leaving tree edits."""

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


def make_bad_hash_zip(path: Path) -> None:
    version = b"v999\n"
    manifest = ("0" * 64 + "  VERSION\n").encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)


def make_crlf_manifest_zip(path: Path) -> None:
    version = b"v999\n"
    manifest = (hashlib.sha256(version).hexdigest() + "  VERSION\r\n").encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)


def make_crlf_version_zip(path: Path) -> None:
    version = b"v999\r\n"
    manifest = (hashlib.sha256(version).hexdigest() + "  VERSION\n").encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)


def make_duplicate_zip(path: Path) -> None:
    version = b"v999\n"
    digest = hashlib.sha256(version).hexdigest()
    manifest = (digest + "  VERSION\n").encode("utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
            write_entry(zf, "MANIFEST.sha256", manifest)
            write_entry(zf, "VERSION", version)
            write_entry(zf, "VERSION", version)


def make_unsafe_zip(path: Path) -> None:
    version = b"v999\n"
    evil = b"not shipped"
    manifest = (
        hashlib.sha256(version).hexdigest() + "  VERSION\n" +
        hashlib.sha256(evil).hexdigest() + "  ../evil.txt\n"
    ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)
        write_entry(zf, "../evil.txt", evil)





def make_whitespace_path_zip(path: Path) -> None:
    version = b"v999\n"
    payload = b"ambiguous path"
    manifest = (
        hashlib.sha256(version).hexdigest() + "  VERSION\n" +
        hashlib.sha256(payload).hexdigest() + "  objects/bad name.txt\n"
    ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)
        write_entry(zf, "objects/bad name.txt", payload)


def make_reserved_path_zip(path: Path) -> None:
    version = b"v999\n"
    payload = b"reserved basename"
    manifest = (
        hashlib.sha256(version).hexdigest() + "  VERSION\n" +
        hashlib.sha256(payload).hexdigest() + "  objects/AUX.json\n"
    ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)
        write_entry(zf, "objects/AUX.json", payload)


def make_case_collision_zip(path: Path) -> None:
    version = b"v999\n"
    one = b"first"
    two = b"second"
    manifest = (
        hashlib.sha256(version).hexdigest() + "  VERSION\n" +
        hashlib.sha256(one).hexdigest() + "  objects/Case.json\n" +
        hashlib.sha256(two).hexdigest() + "  objects/case.json\n"
    ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)
        write_entry(zf, "objects/Case.json", one)
        write_entry(zf, "objects/case.json", two)

def make_extraction_shape_conflict_zip(path: Path) -> None:
    version = b"v999\n"
    prefix = b"regular file at would-be directory path"
    child = b"child file under the same path"
    manifest = (
        hashlib.sha256(version).hexdigest() + "  VERSION\n" +
        hashlib.sha256(prefix).hexdigest() + "  objects/prefix\n" +
        hashlib.sha256(child).hexdigest() + "  objects/prefix/child.json\n"
    ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)
        write_entry(zf, "objects/prefix", prefix)
        write_entry(zf, "objects/prefix/child.json", child)

def make_bad_mode_zip(path: Path) -> None:
    version = b"v999\n"
    digest = hashlib.sha256(version).hexdigest()
    manifest = (digest + "  VERSION\n").encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version, mode=0o755)

def make_overlay_zip(good: Path, path: Path) -> None:
    path.write_bytes(good.read_bytes() + b"\nnot part of the deterministic release\n")


def make_preamble_zip(good: Path, path: Path) -> None:
    path.write_bytes(b"#!/bin/sh\necho not a canonical Election Stack release\n" + good.read_bytes())


def make_deflated_zip(good: Path, path: Path) -> None:
    """Rewrite a good stored archive as deflated while preserving payload bytes."""

    with zipfile.ZipFile(good, "r") as src:
        infos = sorted(src.infolist(), key=lambda item: item.filename)
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=False) as dst:
            for info in infos:
                zi = zipfile.ZipInfo(info.filename)
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.date_time = FIXED_ZIP_DT
                zi.create_system = 3
                zi.create_version = 20
                zi.extract_version = 20
                zi.flag_bits = 0
                zi.external_attr = (0o644 & 0xFFFF) << 16
                dst.writestr(zi, src.read(info.filename))


def symlink_or_skip(target: Path, link: Path) -> bool:
    """Create a symlink when supported; return whether the probe can run."""

    if not hasattr(os, "symlink"):
        return False
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        return False
    return True


def expect_bad(path: Path | str, needle: str) -> None:
    result = verify_release_zip.verify_zip(path)
    display_name = Path(os.fspath(path)).name
    if result.ok:
        fail(f"negative probe unexpectedly passed: {display_name}")
    joined = "\n".join(result.problems)
    if needle not in joined:
        fail(f"negative probe {display_name} did not report {needle!r}; problems={result.problems!r}")


def check_input_path_lexical_firewall(good: Path, tdir: Path) -> None:
    """Ensure raw operator path spellings cannot be normalized before audit."""

    parent = tdir / "lexical-parent"
    parent.mkdir()
    probe = parent / good.name
    shutil.copyfile(good, probe)

    expect_bad(str(parent) + "/./" + good.name, "current/parent traversal components")

    child = parent / "child"
    child.mkdir()
    expect_bad(str(child) + "/../" + good.name, "current/parent traversal components")

    expect_bad(str(parent) + "//" + good.name, "empty separator components")
    expect_bad(str(probe) + "/", "trailing separator")


def check_single_snapshot_source(good: Path, tdir: Path) -> None:
    """Ensure verification uses one immutable byte snapshot after input preflight."""

    probe = tdir / ("snapshot-" + good.name)
    shutil.copyfile(good, probe)
    expected_hash = hashlib.sha256(probe.read_bytes()).hexdigest()
    original_snapshot = verify_release_zip._read_zip_snapshot

    def mutating_snapshot(path: Path):  # type: ignore[no-untyped-def]
        data, problems = original_snapshot(path)
        if data is not None and not problems:
            Path(path).write_bytes(b"not a ZIP after the verifier snapshot\n")
        return data, problems

    verify_release_zip._read_zip_snapshot = mutating_snapshot
    try:
        result = verify_release_zip.verify_zip(probe)
    finally:
        verify_release_zip._read_zip_snapshot = original_snapshot

    if not result.ok:
        fail("single-snapshot probe did not verify the snapshotted bytes: " + "; ".join(result.problems[:10]))
    if result.zip_sha256 != expected_hash:
        fail(f"single-snapshot probe reported hash {result.zip_sha256}, expected {expected_hash}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tes_zip_verify_") as td:
        tdir = Path(td)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        rev = int(version[1:])
        good = tdir / f"The-Election-Stack-rev{rev:04d}.zip"
        build_zip_with_fresh_manifest(good)
        result = verify_release_zip.verify_zip(good)
        if not result.ok:
            fail("fresh deterministic release ZIP did not verify: " + "; ".join(result.problems[:10]))

        check_input_path_lexical_firewall(good, tdir)
        check_single_snapshot_source(good, tdir)

        mixed_canonical_name = tdir / f"The-Election-Stack-rev{rev:04d}-v{rev}.zip"
        shutil.copyfile(good, mixed_canonical_name)
        result = verify_release_zip.verify_zip(mixed_canonical_name)
        if not result.ok:
            fail("canonical mixed rev/v filename tokens did not verify: " + "; ".join(result.problems[:10]))

        conflicting_filename = tdir / f"The-Election-Stack-rev{rev:04d}-v{rev - 1}.zip"
        shutil.copyfile(good, conflicting_filename)
        expect_bad(conflicting_filename, "filename version tokens disagree")

        padded_semantic_filename = tdir / f"The-Election-Stack-v{rev:04d}.zip"
        shutil.copyfile(good, padded_semantic_filename)
        expect_bad(padded_semantic_filename, "filename semantic version token")

        symlink_alias = tdir / f"The-Election-Stack-rev{rev - 1:04d}.zip"
        if symlink_or_skip(good.name, symlink_alias):
            expect_bad(symlink_alias, "must not be a symlink")

        real_parent = tdir / "real-parent"
        real_parent.mkdir()
        parent_good = real_parent / good.name
        shutil.copyfile(good, parent_good)
        linked_parent = tdir / "linked-parent"
        if symlink_or_skip(real_parent, linked_parent):
            expect_bad(linked_parent / good.name, "ancestry must not contain symlink")

        bad_hash = tdir / "bad-hash.zip"
        make_bad_hash_zip(bad_hash)
        expect_bad(bad_hash, "sha256 mismatch")

        crlf_manifest = tdir / "crlf-manifest.zip"
        make_crlf_manifest_zip(crlf_manifest)
        expect_bad(crlf_manifest, "CR bytes")

        crlf_version = tdir / "crlf-version.zip"
        make_crlf_version_zip(crlf_version)
        expect_bad(crlf_version, "VERSION must use LF")

        duplicate = tdir / "duplicate.zip"
        make_duplicate_zip(duplicate)
        expect_bad(duplicate, "duplicate ZIP members")

        unsafe = tdir / "unsafe.zip"
        make_unsafe_zip(unsafe)
        expect_bad(unsafe, "unsafe")

        whitespace_path = tdir / "whitespace-path.zip"
        make_whitespace_path_zip(whitespace_path)
        expect_bad(whitespace_path, "whitespace")

        reserved_path = tdir / "reserved-path.zip"
        make_reserved_path_zip(reserved_path)
        expect_bad(reserved_path, "reserved Windows device basename")

        case_collision = tdir / "case-collision.zip"
        make_case_collision_zip(case_collision)
        expect_bad(case_collision, "portable ZIP member path collision")

        shape_conflict = tdir / "shape-conflict.zip"
        make_extraction_shape_conflict_zip(shape_conflict)
        expect_bad(shape_conflict, "extraction shape conflict")

        bad_mode = tdir / "bad-mode.zip"
        make_bad_mode_zip(bad_mode)
        expect_bad(bad_mode, "canonical 0o644")

        overlay = tdir / "overlay.zip"
        make_overlay_zip(good, overlay)
        expect_bad(overlay, "final empty-comment")

        preamble = tdir / "preamble.zip"
        make_preamble_zip(good, preamble)
        expect_bad(preamble, "preamble/self-extractor")

        deflated = tdir / "deflated.zip"
        make_deflated_zip(good, deflated)
        expect_bad(deflated, "ZIP_STORED")

    print("PASS: release ZIP verifier accepts built archive, uses a canonical raw input path and single input-byte snapshot, and rejects filename-token/input-symlink/hash/control-file/duplicate/path/whitespace/reserved/case/shape/mode/layout/compression-method probes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
