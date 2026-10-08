#!/usr/bin/env python3
"""Release-gate smoke test for scripts/verify_manifest.py.

The release ZIP verifier checks an archive without extraction.  This companion
check exercises the extracted-tree manifest verifier so recipients who only have
an unpacked tree still get strict hash-closure, path-policy, and symlink-safety
coverage.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "MANIFEST.sha256"


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_file(root: Path, rel: str, data: bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o644)


def write_manifest(root: Path, entries: list[tuple[str, str]]) -> None:
    text = "".join(f"{sha}  {rel}\n" for rel, sha in entries)
    (root / MANIFEST).write_text(text, encoding="utf-8")


def make_good_tree(root: Path) -> None:
    root.chmod(0o755)
    write_file(root, "README.md", b"minimal extracted tree\n")
    write_file(root, "VERSION", b"v999\n")
    entries = [
        ("README.md", digest(b"minimal extracted tree\n")),
        ("VERSION", digest(b"v999\n")),
    ]
    write_manifest(root, entries)


def expect_bad(root: Path, needle: str) -> None:
    result = verify_manifest.verify_tree(root)
    if result.ok:
        fail(f"negative manifest-verifier probe unexpectedly passed: {root}")
    joined = "\n".join(result.problems)
    if needle not in joined:
        fail(f"negative probe did not report {needle!r}; problems={result.problems!r}")


def expect_bad_root_arg(root_arg: str, needle: str) -> None:
    result = verify_manifest.verify_tree(root_arg)
    if result.ok:
        fail(f"negative manifest-verifier root-path probe unexpectedly passed: {root_arg!r}")
    joined = "\n".join(result.problems)
    if needle not in joined:
        fail(f"root-path probe did not report {needle!r}; problems={result.problems!r}")


def verify_current_tree_with_fresh_manifest() -> None:
    """Exercise the verifier on the live tree without requiring a pre-refreshed manifest."""

    manifest_path = ROOT / MANIFEST
    old = manifest_path.read_bytes() if manifest_path.exists() else None
    try:
        manifest_path.write_text(build_manifest.build_manifest_text(), encoding="utf-8")
        current = verify_manifest.verify_tree(ROOT)
        if not current.ok:
            fail("current tree did not verify with a freshly computed manifest: " + "; ".join(current.problems[:10]))
    finally:
        if old is None:
            try:
                manifest_path.unlink()
            except FileNotFoundError:
                pass
        else:
            manifest_path.write_bytes(old)


def main() -> int:
    verify_current_tree_with_fresh_manifest()

    with tempfile.TemporaryDirectory(prefix="tes_manifest_verify_") as td:
        base = Path(td)

        good = base / "good"
        good.mkdir()
        make_good_tree(good)
        if not verify_manifest.verify_tree(good).ok:
            fail("minimal good tree did not verify")

        expect_bad_root_arg("", "verification root path must not be empty")
        expect_bad_root_arg(str(good) + "\x00suffix", "verification root path must not contain NUL bytes")
        expect_bad_root_arg(str(good) + "/", "verification root path must not have a trailing separator")
        expect_bad_root_arg(str(good) + "/./child", "verification root path must not contain current/parent traversal components")
        expect_bad_root_arg(str(good) + f"/../{good.name}", "verification root path must not contain current/parent traversal components")
        expect_bad_root_arg(str(good.parent) + "//" + good.name, "verification root path must not contain empty separator components")

        bad_hash = base / "bad_hash"
        shutil.copytree(good, bad_hash)
        write_manifest(bad_hash, [
            ("README.md", "0" * 64),
            ("VERSION", digest(b"v999\n")),
        ])
        expect_bad(bad_hash, "sha256 mismatch")


        bad_mode = base / "bad_mode"
        shutil.copytree(good, bad_mode)
        (bad_mode / "README.md").chmod(0o755)
        expect_bad(bad_mode, "file mode is not canonical 0644")

        bad_root_mode = base / "bad_root_mode"
        shutil.copytree(good, bad_root_mode)
        bad_root_mode.chmod(0o700)
        expect_bad(bad_root_mode, "extraction root directory mode is not canonical 0755")

        bad_dir_mode = base / "bad_dir_mode"
        shutil.copytree(good, bad_dir_mode)
        write_file(bad_dir_mode, "docs/listed.md", b"listed child\n")
        write_manifest(bad_dir_mode, [
            ("README.md", digest(b"minimal extracted tree\n")),
            ("VERSION", digest(b"v999\n")),
            ("docs/listed.md", digest(b"listed child\n")),
        ])
        (bad_dir_mode / "docs").chmod(0o700)
        expect_bad(bad_dir_mode, "directory mode is not canonical 0755")

        extra_dir = base / "extra_dir"
        shutil.copytree(good, extra_dir)
        (extra_dir / "docs" / "empty-extra").mkdir(parents=True)
        (extra_dir / "docs" / "empty-extra").chmod(0o755)
        (extra_dir / "docs").chmod(0o755)
        expect_bad(extra_dir, "directories not implied by MANIFEST.sha256")

        missing = base / "missing"
        shutil.copytree(good, missing)
        (missing / "README.md").unlink()
        expect_bad(missing, "missing from extracted tree")

        unlisted = base / "unlisted"
        shutil.copytree(good, unlisted)
        write_file(unlisted, "docs/unlisted.md", b"not in manifest\n")
        expect_bad(unlisted, "not listed in MANIFEST.sha256")

        unsafe_unlisted = base / "unsafe_unlisted"
        shutil.copytree(good, unsafe_unlisted)
        write_file(unsafe_unlisted, "docs/bad name.md", b"unsafe extra file\n")
        expect_bad(unsafe_unlisted, "unsafe release-scope file present")

        unsafe = base / "unsafe"
        shutil.copytree(good, unsafe)
        write_manifest(unsafe, [
            ("../outside.txt", digest(b"outside\n")),
            ("README.md", digest(b"minimal extracted tree\n")),
            ("VERSION", digest(b"v999\n")),
        ])
        expect_bad(unsafe, "unsafe path")

        duplicate = base / "duplicate"
        shutil.copytree(good, duplicate)
        write_manifest(duplicate, [
            ("README.md", digest(b"minimal extracted tree\n")),
            ("README.md", digest(b"minimal extracted tree\n")),
            ("VERSION", digest(b"v999\n")),
        ])
        expect_bad(duplicate, "duplicate path")

        case_collision = base / "case_collision"
        shutil.copytree(good, case_collision)
        write_file(case_collision, "docs/Case.md", b"A\n")
        write_file(case_collision, "docs/case.md", b"B\n")
        write_manifest(case_collision, [
            ("README.md", digest(b"minimal extracted tree\n")),
            ("VERSION", digest(b"v999\n")),
            ("docs/Case.md", digest(b"A\n")),
            ("docs/case.md", digest(b"B\n")),
        ])
        expect_bad(case_collision, "portable path collision")

        shape_conflict = base / "shape_conflict"
        shutil.copytree(good, shape_conflict)
        # A real filesystem cannot contain both a regular file at docs/prefix
        # and a child below docs/prefix/.  The parser must still reject the
        # manifest shape explicitly so extracted-tree and ZIP verification agree.
        write_file(shape_conflict, "docs/prefix/child.md", b"child\n")
        write_manifest(shape_conflict, [
            ("README.md", digest(b"minimal extracted tree\n")),
            ("VERSION", digest(b"v999\n")),
            ("docs/prefix", digest(b"prefix\n")),
            ("docs/prefix/child.md", digest(b"child\n")),
        ])
        expect_bad(shape_conflict, "extraction shape conflict")

        if hasattr(os, "symlink"):
            symlink_tree = base / "symlink"
            shutil.copytree(good, symlink_tree)
            try:
                os.symlink("README.md", symlink_tree / "linked.md")
            except (OSError, NotImplementedError):
                pass
            else:
                expect_bad(symlink_tree, "symlink")

            symlink_root = base / "symlink_root"
            try:
                os.symlink(good, symlink_root)
            except (OSError, NotImplementedError):
                pass
            else:
                expect_bad(symlink_root, "verification root must not traverse symlink component")


            hash_leaf_swap = base / "hash_leaf_swap"
            shutil.copytree(good, hash_leaf_swap)
            write_file(hash_leaf_swap, "redirect.md", b"redirected bytes that must not verify\n")
            original_open_member = build_manifest._open_manifest_member_fd
            swapped = False
            try:
                def mutating_open_member(root, rel):
                    nonlocal swapped
                    if Path(root) == hash_leaf_swap and rel == "README.md" and not swapped:
                        swapped = True
                        (hash_leaf_swap / "README.md").unlink()
                        os.symlink("redirect.md", hash_leaf_swap / "README.md")
                    return original_open_member(root, rel)

                build_manifest._open_manifest_member_fd = mutating_open_member  # type: ignore[attr-defined]
                expect_bad(hash_leaf_swap, "manifest member")
            finally:
                build_manifest._open_manifest_member_fd = original_open_member  # type: ignore[attr-defined]

            hash_parent_swap = base / "hash_parent_swap"
            shutil.copytree(good, hash_parent_swap)
            write_file(hash_parent_swap, "docs/listed.md", b"listed child\n")
            write_manifest(hash_parent_swap, [
                ("README.md", digest(b"minimal extracted tree\n")),
                ("VERSION", digest(b"v999\n")),
                ("docs/listed.md", digest(b"listed child\n")),
            ])
            redirect_parent = hash_parent_swap / "redirect_parent"
            redirect_parent.mkdir()
            write_file(hash_parent_swap, "redirect_parent/listed.md", b"redirected child that must not verify\n")
            original_open_member = build_manifest._open_manifest_member_fd
            swapped = False
            try:
                def mutating_parent_open_member(root, rel):
                    nonlocal swapped
                    if Path(root) == hash_parent_swap and rel == "docs/listed.md" and not swapped:
                        swapped = True
                        (hash_parent_swap / "docs" / "listed.md").unlink()
                        (hash_parent_swap / "docs").rmdir()
                        os.symlink("redirect_parent", hash_parent_swap / "docs")
                    return original_open_member(root, rel)

                build_manifest._open_manifest_member_fd = mutating_parent_open_member  # type: ignore[attr-defined]
                expect_bad(hash_parent_swap, "manifest member ancestry")
            finally:
                build_manifest._open_manifest_member_fd = original_open_member  # type: ignore[attr-defined]

    print("PASS: manifest verifier accepts freshly manifested/good trees and rejects root-lexical/hash/file-mode/root-mode/dir-mode/extra-dir/missing/unlisted/unsafe-extra/path/duplicate/case/shape/symlink/root-symlink/hash-read-symlink-swap probes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
