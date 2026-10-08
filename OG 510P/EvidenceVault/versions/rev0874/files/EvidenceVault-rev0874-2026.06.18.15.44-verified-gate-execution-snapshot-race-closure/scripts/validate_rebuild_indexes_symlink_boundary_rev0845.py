#!/usr/bin/env python3
"""Validate rev0845 symlink-boundary hardening in rebuild_indexes.py."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rebuild_indexes as ri  # noqa: E402

REQUIRED_SNIPPETS = [
    "def collect_regular_archive_files",
    "followlinks=False",
    "refusing to index symlink paths",
    "all_files = collect_regular_archive_files(ROOT)",
    "require_regular_file(target, f\"RO-Crate digested entity {rel}\")",
]


def fail(message: str) -> None:
    print(f"rebuild-indexes-symlink-boundary-rev0845: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def with_root(root: Path):
    class Ctx:
        def __enter__(self):
            self.old_root = ri.ROOT
            ri.ROOT = root
            return self
        def __exit__(self, exc_type, exc, tb):
            ri.ROOT = self.old_root
    return Ctx()


def expect_runtime_error(fn, label: str) -> None:
    try:
        fn()
    except RuntimeError as exc:
        if "symlink" not in str(exc):
            fail(f"{label} raised RuntimeError without symlink diagnostic: {exc}")
        return
    fail(f"{label} did not reject symlink boundary")


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_clean_tree_collects_regular_files() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0845-rebuild-clean-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        (root / "dir").mkdir(parents=True)
        (root / "a.txt").write_text("a\n", encoding="utf-8")
        (root / "dir" / "b.txt").write_text("b\n", encoding="utf-8")
        files = [path.relative_to(root).as_posix() for path in ri.collect_regular_archive_files(root)]
        if files != ["a.txt", "dir/b.txt"]:
            fail(f"clean collection produced unexpected paths: {files}")
        with with_root(root):
            digest = ri.sha256_file(root / "a.txt")
        if len(digest) != 64:
            fail(f"sha256_file returned malformed digest: {digest}")


def assert_symlink_file_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0845-rebuild-link-file-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        outside = Path(tmp) / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        os.symlink(outside, root / "leak.txt")
        expect_runtime_error(lambda: ri.collect_regular_archive_files(root), "symlink file collection")
        with with_root(root):
            expect_runtime_error(lambda: ri.sha256_file(root / "leak.txt"), "symlink sha256")


def assert_symlink_directory_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0845-rebuild-link-dir-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        outside = Path(tmp) / "outside-dir"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret\n", encoding="utf-8")
        os.symlink(outside, root / "linked-dir")
        expect_runtime_error(lambda: ri.collect_regular_archive_files(root), "symlink directory collection")


def main() -> int:
    assert_static_contract()
    assert_clean_tree_collects_regular_files()
    assert_symlink_file_is_rejected()
    assert_symlink_directory_is_rejected()
    print("rebuild-indexes-symlink-boundary-rev0845: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
