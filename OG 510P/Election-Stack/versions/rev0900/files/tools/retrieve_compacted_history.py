#!/usr/bin/env python3
"""Safely recover exact bytes behind a v894 retrievable-history stub.

The release tree keeps superseded paths as small JSON stubs.  Their original
bytes remain in one deterministic tar+gzip bundle inside the same carrier.
This tool reads one exact member, verifies its size and SHA-256 against the
stub, and writes it without using tarfile.extract().
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tarfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = None


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"ERROR: {message}")


def safe_repo_rel(raw: str) -> str:
    if not raw or raw.startswith("/") or "\\" in raw or "\x00" in raw:
        fail("--path must be a concrete POSIX repository-relative path")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        fail("--path contains an empty/current/parent component")
    return raw


def load_stub(rel: str) -> dict:
    path = ROOT / rel
    try:
        st = path.lstat()
    except OSError as exc:
        fail(f"could not stat stub {rel}: {exc}")
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        fail(f"stub is not a concrete regular file: {rel}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"stub JSON is unreadable: {rel}: {exc}")
    if not isinstance(obj, dict) or obj.get("compacted_historical_artifact") is not True:
        fail(f"path is not a compacted historical artifact stub: {rel}")
    if obj.get("path") != rel:
        fail(f"stub path binding mismatch: expected {rel!r}, got {obj.get('path')!r}")
    retrieval = obj.get("retrieval")
    if not isinstance(retrieval, dict) or retrieval.get("format") != "tar+gzip":
        fail("stub has no supported tar+gzip retrieval record")
    if retrieval.get("member_path") != rel:
        fail("stub member-path binding mismatch")
    return obj


def read_verified(bundle: Path, rel: str, stub: dict) -> bytes:
    try:
        bst = bundle.lstat()
    except OSError as exc:
        fail(f"could not stat bundle: {exc}")
    if stat.S_ISLNK(bst.st_mode) or not stat.S_ISREG(bst.st_mode):
        fail("bundle must be a concrete regular file")
    try:
        with tarfile.open(bundle, mode="r:gz") as tf:
            members = [m for m in tf.getmembers() if m.name == rel]
            if len(members) != 1:
                fail(f"expected exactly one bundle member for {rel}, found {len(members)}")
            member = members[0]
            if not member.isfile() or member.issym() or member.islnk():
                fail("bundle member is not an ordinary file")
            fh = tf.extractfile(member)
            if fh is None:
                fail("bundle member could not be opened")
            data = fh.read()
    except (tarfile.TarError, OSError) as exc:
        fail(f"could not read history bundle: {exc}")
    expected_size = stub.get("original_size_bytes")
    expected_sha = stub.get("original_sha256")
    actual_sha = "sha256:" + hashlib.sha256(data).hexdigest()
    if len(data) != expected_size:
        fail(f"size mismatch: recovered {len(data)}, expected {expected_size}")
    if actual_sha != expected_sha:
        fail(f"SHA-256 mismatch: recovered {actual_sha}, expected {expected_sha}")
    return data


def write_exclusive(path: Path, data: bytes, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if force else os.O_EXCL)
    try:
        fd = os.open(path, flags, 0o644)
    except FileExistsError:
        fail(f"output exists (use --force to replace): {path}")
    except OSError as exc:
        fail(f"could not open output {path}: {exc}")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
    except Exception:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise


def list_members(bundle: Path) -> int:
    try:
        with tarfile.open(bundle, mode="r:gz") as tf:
            names = [m.name for m in tf.getmembers() if m.isfile()]
    except (tarfile.TarError, OSError) as exc:
        fail(f"could not list history bundle: {exc}")
    for name in names:
        print(name)
    print(f"LISTED: {len(names)} exact historical payload(s)", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", help="history bundle path; defaults to the bundle bound by the selected stub")
    ap.add_argument("--list", action="store_true", help="list exact member paths")
    ap.add_argument("--path", help="repository-relative historical stub path")
    ap.add_argument("--output", help="destination for recovered original bytes")
    ap.add_argument("--force", action="store_true", help="replace an existing output file")
    args = ap.parse_args()
    if args.list:
        if args.path or args.output:
            fail("--list cannot be combined with --path/--output")
        if not args.bundle:
            fail("--list requires --bundle when multiple history bundles may exist")
        return list_members(Path(args.bundle))
    if not args.path or not args.output:
        fail("recovery requires both --path and --output")
    rel = safe_repo_rel(args.path)
    stub = load_stub(rel)
    recorded = stub["retrieval"].get("bundle_path")
    recorded_rel = safe_repo_rel(recorded)
    if recorded_rel is None:
        fail("stub has an unsafe or missing bundle_path")
    bundle = Path(args.bundle) if args.bundle else ROOT / recorded_rel
    try:
        supplied_rel = bundle.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        supplied_rel = None
    if supplied_rel is not None and supplied_rel != recorded_rel:
        fail(f"supplied bundle does not match stub binding: {supplied_rel!r} != {recorded_rel!r}")
    data = read_verified(bundle, rel, stub)
    out = Path(args.output)
    write_exclusive(out, data, args.force)
    print(f"PASS: recovered {rel} -> {out} ({len(data)} bytes, {stub['original_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
