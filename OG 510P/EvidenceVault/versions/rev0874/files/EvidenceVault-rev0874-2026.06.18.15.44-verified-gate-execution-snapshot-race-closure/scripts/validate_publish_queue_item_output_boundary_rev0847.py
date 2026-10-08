#!/usr/bin/env python3
"""Validate rev0847 publication-output symlink/root-boundary hardening."""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish_queue_item as pqi  # noqa: E402

REQUIRED_SNIPPETS = [
    "def prepare_publication_output_path",
    "publication output path escapes archive root",
    "prepare_publication_output_path(path, 'atomic output')",
    "path.parent.mkdir(parents=True, exist_ok=True)",
    "transition_script = archive_file_path('scripts/transition_queue_item.py', 'transition_queue_item')",
    "env['PYTHONDONTWRITEBYTECODE'] = '1'",
    "cwd=ROOT, env=env, check=True",
]


def fail(message: str) -> None:
    print(f"publish-queue-item-output-boundary-rev0847: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


@contextlib.contextmanager
def with_root(root: Path):
    old_root = pqi.ROOT
    pqi.ROOT = root
    try:
        yield
    finally:
        pqi.ROOT = old_root


def expect_system_exit(fn, label: str, expected_fragment: str) -> None:
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            fn()
    except SystemExit as exc:
        if exc.code == 0:
            fail(f"{label} exited successfully instead of failing closed")
        diagnostic = stderr.getvalue() or str(exc)
        if expected_fragment not in diagnostic:
            fail(f"{label} failed without expected diagnostic {expected_fragment!r}: {diagnostic!r}")
        return
    fail(f"{label} did not fail closed")


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publish_queue_item.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_no_transients(root: Path) -> None:
    offenders = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".tmp"}
    ]
    if offenders:
        fail("transient helper files remain: " + ", ".join(offenders[:10]))


def make_root(prefix: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix=prefix)
    root = Path(tmp.name) / "EvidenceVault-fixture"
    root.mkdir()
    return tmp, root


def assert_clean_output_write_still_works() -> None:
    tmp, root = make_root("ev-rev0847-output-clean-")
    with tmp:
        target = root / "published" / "releases" / "clean.json"
        with with_root(root):
            pqi.atomic_write_bytes(target, b"clean\n", overwrite=False)
        if target.read_bytes() != b"clean\n":
            fail("clean output write did not create the expected payload")
        assert_no_transients(root)


def assert_output_outside_root_is_rejected() -> None:
    tmp, root = make_root("ev-rev0847-output-outside-")
    with tmp:
        outside_target = Path(tmp.name) / "outside" / "record.json"
        with with_root(root):
            expect_system_exit(
                lambda: pqi.atomic_write_bytes(outside_target, b"outside\n", overwrite=False),
                "outside-root output path",
                "escapes archive root",
            )
        if outside_target.exists():
            fail("outside-root output path was created")
        assert_no_transients(root)


def assert_symlinked_top_level_output_parent_is_rejected() -> None:
    tmp, root = make_root("ev-rev0847-output-top-link-")
    with tmp:
        outside = Path(tmp.name) / "outside-published"
        outside.mkdir()
        os.symlink(outside, root / "published")
        target = root / "published" / "releases" / "record.json"
        with with_root(root):
            expect_system_exit(
                lambda: pqi.atomic_write_bytes(target, b"redirected\n", overwrite=False),
                "symlinked top-level output parent",
                "symlink component",
            )
        if list(outside.rglob("*")):
            fail("symlinked top-level parent received publication output bytes")
        assert_no_transients(root)


def assert_symlinked_nested_output_parent_is_rejected() -> None:
    tmp, root = make_root("ev-rev0847-output-nested-link-")
    with tmp:
        outside = Path(tmp.name) / "outside-releases"
        outside.mkdir()
        (root / "published").mkdir()
        os.symlink(outside, root / "published" / "releases")
        target = root / "published" / "releases" / "record.json"
        with with_root(root):
            expect_system_exit(
                lambda: pqi.atomic_write_bytes(target, b"redirected\n", overwrite=False),
                "symlinked nested output parent",
                "symlink component",
            )
        if list(outside.rglob("*")):
            fail("symlinked nested parent received publication output bytes")
        assert_no_transients(root)


def assert_symlinked_transition_script_is_rejected() -> None:
    tmp, root = make_root("ev-rev0847-transition-link-")
    with tmp:
        outside = Path(tmp.name) / "outside-transition.py"
        outside.write_text("#!/usr/bin/env python3\nprint('outside')\n", encoding="utf-8")
        (root / "scripts").mkdir()
        os.symlink(outside, root / "scripts" / "transition_queue_item.py")
        with with_root(root):
            expect_system_exit(
                lambda: pqi.archive_file_path("scripts/transition_queue_item.py", "transition_queue_item"),
                "symlinked transition script",
                "symlink component",
            )
        assert_no_transients(root)


def assert_rev0844_validator_still_passes() -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_publish_queue_item_no_clobber_rev0844.py")],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        fail(f"rev0844 no-clobber validator regressed: stdout={result.stdout!r} stderr={result.stderr!r}")


def main() -> int:
    assert_static_contract()
    assert_clean_output_write_still_works()
    assert_output_outside_root_is_rejected()
    assert_symlinked_top_level_output_parent_is_rejected()
    assert_symlinked_nested_output_parent_is_rejected()
    assert_symlinked_transition_script_is_rejected()
    assert_rev0844_validator_still_passes()
    print("publish-queue-item-output-boundary-rev0847: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
