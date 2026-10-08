#!/usr/bin/env python3
"""Validate rev0847 atomic generated-output writes in rebuild_indexes.py."""
from __future__ import annotations

import contextlib
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rebuild_indexes as ri  # noqa: E402

REQUIRED_SNIPPETS = [
    "import tempfile",
    "def prepare_generated_output_path",
    "def atomic_write_bytes",
    "tempfile.mkstemp",
    "os.fchmod(f.fileno(), 0o644)",
    "os.fsync(f.fileno())",
    "os.replace(tmp_path, path)",
    "atomic_write_json(path, data, label=\"RELEASE_MANIFEST.json\")",
    "atomic_write_json(path, crate, label='ro-crate-metadata.json')",
    "atomic_write_text(ROOT / 'RO_CRATE_PROFILE.md'",
    "atomic_write_text(INDEX_DIR / \"files.json\"",
    "atomic_write_text(INDEX_DIR / \"files.csv\"",
    "atomic_write_text(ROOT / \"MANIFEST.sha256\"",
]
FORBIDDEN_SNIPPETS = [
    "INDEX_DIR.mkdir(exist_ok=True)",
    "(INDEX_DIR / \"files.json\").write_text",
    "(ROOT / \"MANIFEST.sha256\").write_text",
]


def fail(message: str) -> None:
    print(f"rebuild-indexes-atomic-outputs-rev0847: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


@contextlib.contextmanager
def with_root(root: Path):
    old_root = ri.ROOT
    old_index = ri.INDEX_DIR
    ri.ROOT = root
    ri.INDEX_DIR = root / "INDEX"
    try:
        yield
    finally:
        ri.ROOT = old_root
        ri.INDEX_DIR = old_index


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    forbidden = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))
    if forbidden:
        fail("forbidden direct-write/import-time snippets remain: " + ", ".join(forbidden))


def assert_no_transients(root: Path) -> None:
    offenders = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".tmp"}
    ]
    if offenders:
        fail("transient generated-output files remain: " + ", ".join(offenders[:10]))


def make_root(prefix: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix=prefix)
    root = Path(tmp.name) / "EvidenceVault-fixture"
    root.mkdir()
    return tmp, root


def assert_clean_atomic_write_replaces_bytes() -> None:
    tmp, root = make_root("ev-rev0847-rebuild-clean-")
    with tmp:
        target = root / "INDEX" / "files.json"
        with with_root(root):
            ri.atomic_write_text(target, "one\n", label="INDEX/files.json")
            ri.atomic_write_text(target, "two\n", label="INDEX/files.json")
        if target.read_text(encoding="utf-8") != "two\n":
            fail("atomic generated-output replacement did not leave final payload")
        assert_no_transients(root)


def assert_generated_output_outside_root_is_rejected() -> None:
    tmp, root = make_root("ev-rev0847-rebuild-outside-")
    with tmp:
        outside_target = Path(tmp.name) / "outside" / "files.json"
        with with_root(root):
            try:
                ri.atomic_write_text(outside_target, "outside\n", label="INDEX/files.json")
            except RuntimeError as exc:
                if "escapes archive root" not in str(exc):
                    fail(f"outside-root output raised wrong diagnostic: {exc}")
            else:
                fail("outside-root generated output was accepted")
        if outside_target.exists():
            fail("outside-root generated output path was created")
        assert_no_transients(root)


def assert_symlinked_generated_output_parent_is_rejected() -> None:
    tmp, root = make_root("ev-rev0847-rebuild-link-")
    with tmp:
        outside = Path(tmp.name) / "outside-index"
        outside.mkdir()
        os.symlink(outside, root / "INDEX")
        target = root / "INDEX" / "files.json"
        with with_root(root):
            try:
                ri.atomic_write_text(target, "redirected\n", label="INDEX/files.json")
            except RuntimeError as exc:
                if "symlink component" not in str(exc):
                    fail(f"symlinked output parent raised wrong diagnostic: {exc}")
            else:
                fail("symlinked generated-output parent was accepted")
        if list(outside.rglob("*")):
            fail("symlinked generated-output parent received bytes")
        assert_no_transients(root)


def assert_failed_replace_cleans_temporary_file() -> None:
    tmp, root = make_root("ev-rev0847-rebuild-replace-fail-")
    with tmp:
        target = root / "MANIFEST.sha256"
        original_replace = ri.os.replace

        def boom(_src, _dst):
            raise OSError("simulated replace failure")

        with with_root(root):
            try:
                ri.os.replace = boom
                try:
                    ri.atomic_write_text(target, "payload\n", label="MANIFEST.sha256")
                except OSError as exc:
                    if "simulated replace failure" not in str(exc):
                        fail(f"replace failure raised unexpected error: {exc}")
                else:
                    fail("simulated replace failure did not propagate")
            finally:
                ri.os.replace = original_replace
        if target.exists():
            fail("target exists after simulated replace failure")
        assert_no_transients(root)


def main() -> int:
    assert_static_contract()
    assert_clean_atomic_write_replaces_bytes()
    assert_generated_output_outside_root_is_rejected()
    assert_symlinked_generated_output_parent_is_rejected()
    assert_failed_replace_cleans_temporary_file()
    print("rebuild-indexes-atomic-outputs-rev0847: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
