#!/usr/bin/env python3
"""Validate rev0848 material-builder subprocess path hardening in rebuild_indexes.py."""
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
    "PY_MODULE_RE = re.compile",
    "def archive_python_script_path",
    "unsafe material builder module name",
    "material builder resolves through a symlink component",
    "script = archive_python_script_path(module_name)",
]


def fail(message: str) -> None:
    print(f"rebuild-indexes-material-builder-boundary-rev0848: FAIL: {message}", file=sys.stderr)
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


def make_root(prefix: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix=prefix)
    root = Path(tmp.name) / "EvidenceVault-fixture"
    (root / "scripts").mkdir(parents=True)
    return tmp, root


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "rebuild_indexes.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def expect_runtime_error(fn, wanted: str, label: str) -> None:
    try:
        fn()
    except RuntimeError as exc:
        if wanted not in str(exc):
            fail(f"{label} raised wrong diagnostic: {exc}")
        return
    fail(f"{label} did not fail closed")


def assert_regular_builder_path_passes() -> None:
    tmp, root = make_root("ev-rev0848-rebuild-builder-ok-")
    with tmp:
        script = root / "scripts" / "build_source_index.py"
        script.write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
        with with_root(root):
            resolved = ri.archive_python_script_path("build_source_index")
        if resolved != script:
            fail(f"regular builder resolved to unexpected path: {resolved}")


def assert_unsafe_module_name_rejected() -> None:
    tmp, root = make_root("ev-rev0848-rebuild-builder-name-")
    with tmp, with_root(root):
        for name in ["../evil", "build-source-index", "build_source_index.py", "pkg/build_source_index"]:
            expect_runtime_error(lambda n=name: ri.archive_python_script_path(n), "unsafe material builder module name", f"unsafe module name {name!r}")


def assert_symlinked_builder_rejected_before_execution() -> None:
    tmp, root = make_root("ev-rev0848-rebuild-builder-link-")
    with tmp:
        outside = Path(tmp.name) / "outside_builder.py"
        outside.write_text("raise SystemExit('should not execute')\n", encoding="utf-8")
        os.symlink(outside, root / "scripts" / "build_source_index.py")
        with with_root(root):
            expect_runtime_error(
                lambda: ri.archive_python_script_path("build_source_index"),
                "material builder resolves through a symlink component",
                "symlinked material builder",
            )


def assert_symlinked_scripts_dir_rejected_before_execution() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0848-rebuild-builder-dirlink-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        outside_scripts = Path(tmp) / "outside_scripts"
        outside_scripts.mkdir()
        (outside_scripts / "build_source_index.py").write_text("raise SystemExit('should not execute')\n", encoding="utf-8")
        os.symlink(outside_scripts, root / "scripts")
        with with_root(root):
            expect_runtime_error(
                lambda: ri.archive_python_script_path("build_source_index"),
                "material builder resolves through a symlink component",
                "symlinked scripts directory",
            )


def assert_missing_builder_rejected() -> None:
    tmp, root = make_root("ev-rev0848-rebuild-builder-missing-")
    with tmp, with_root(root):
        expect_runtime_error(
            lambda: ri.archive_python_script_path("build_source_index"),
            "material builder is missing or not a regular file",
            "missing material builder",
        )


def main() -> int:
    assert_static_contract()
    assert_regular_builder_path_passes()
    assert_unsafe_module_name_rejected()
    assert_symlinked_builder_rejected_before_execution()
    assert_symlinked_scripts_dir_rejected_before_execution()
    assert_missing_builder_rejected()
    print("rebuild-indexes-material-builder-boundary-rev0848: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
