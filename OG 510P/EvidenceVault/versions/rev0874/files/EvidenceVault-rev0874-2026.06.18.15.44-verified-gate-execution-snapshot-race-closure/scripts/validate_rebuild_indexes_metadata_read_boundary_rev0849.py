#!/usr/bin/env python3
"""Validate rev0849 symlink-boundary checks for early rebuild metadata reads."""
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
    "def read_text_file",
    "def load_json_file",
    "Rebuild-indexes reads several metadata files before the final full-tree",
    "resolves through a symlink component",
    "data = load_json_file(path, \"RELEASE_MANIFEST.json\")",
    "data = load_json_file(path, path.relative_to(ROOT).as_posix())",
]


def fail(message: str) -> None:
    print(f"rebuild-indexes-metadata-read-boundary-rev0849: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def expect_runtime_error(fn, label: str, expected: str = "symlink") -> None:
    try:
        fn()
    except RuntimeError as exc:
        if expected not in str(exc):
            fail(f"{label} raised RuntimeError without {expected!r} diagnostic: {exc}")
        return
    fail(f"{label} did not fail closed")


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def with_root(root: Path):
    class Ctx:
        def __enter__(self):
            self.old_root = ri.ROOT
            ri.ROOT = root
            return self
        def __exit__(self, exc_type, exc, tb):
            ri.ROOT = self.old_root
    return Ctx()


def assert_regular_metadata_read_passes() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-rebuild-meta-ok-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        target = root / "meta.json"
        target.write_text('{"ok": true}\n', encoding="utf-8")
        with with_root(root):
            data = ri.load_json_file(target, "meta.json")
            if data != {"ok": True}:
                fail(f"regular metadata read produced unexpected data: {data}")
            digest = ri.sha256_file(target)
            if len(digest) != 64:
                fail(f"sha256_file returned malformed digest: {digest}")


def assert_final_symlink_metadata_read_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-rebuild-meta-final-link-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        real = root / "real.json"
        real.write_text('{"ok": true}\n', encoding="utf-8")
        os.symlink(real, root / "meta.json")
        with with_root(root):
            expect_runtime_error(lambda: ri.load_json_file(root / "meta.json", "meta.json"), "final symlink JSON read")
            expect_runtime_error(lambda: ri.sha256_file(root / "meta.json"), "final symlink sha256")


def assert_intermediate_symlink_metadata_read_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-rebuild-meta-dir-link-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        real_dir = root / "real-dir"
        real_dir.mkdir()
        (real_dir / "meta.json").write_text('{"ok": true}\n', encoding="utf-8")
        os.symlink(real_dir, root / "linked-dir")
        with with_root(root):
            expect_runtime_error(lambda: ri.load_json_file(root / "linked-dir" / "meta.json", "linked-dir/meta.json"), "intermediate symlink JSON read")
            expect_runtime_error(lambda: ri.sha256_file(root / "linked-dir" / "meta.json"), "intermediate symlink sha256")


def assert_outside_path_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-rebuild-meta-outside-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        outside = Path(tmp) / "outside.json"
        outside.write_text('{"ok": true}\n', encoding="utf-8")
        with with_root(root):
            expect_runtime_error(lambda: ri.load_json_file(outside, "outside.json"), "outside JSON read", expected="escapes archive root")


def main() -> int:
    assert_static_contract()
    assert_regular_metadata_read_passes()
    assert_final_symlink_metadata_read_blocks()
    assert_intermediate_symlink_metadata_read_blocks()
    assert_outside_path_blocks()
    print("rebuild-indexes-metadata-read-boundary-rev0849: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
