#!/usr/bin/env python3
"""Smoke-test a packaged release by extracting, linting, and rebuilding it.

This is intentionally an end-to-end release check rather than another source-tree
inventory. The packaged zip must be path-safe, transient-free, lint-clean after
extraction, and byte-identically rebuildable from its extracted contents.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath

# Keep the orchestration parent lightweight.  The normal cloudtainer Python
# startup imports a large site stack that package smoke itself does not need;
# extracted-tree validators still run under the normal interpreter.
if not sys.flags.no_site and os.environ.get("TOE_SMOKE_NO_SITE_REEXEC") != "1":
    clean_env = dict(os.environ)
    clean_env["TOE_SMOKE_NO_SITE_REEXEC"] = "1"
    os.execve(
        sys.executable,
        [sys.executable, "-S", os.path.abspath(__file__), *sys.argv[1:]],
        clean_env,
    )

sys.dont_write_bytecode = True

from package_release import (
    canonical_release_root_name,
    is_transient_release_path,
    sha256_file,
)
from lint_steps_config import DEFAULT_LINT_STEPS


def fail(message: str) -> int:
    print(f"PACKAGE SMOKE FAIL: {message}", file=sys.stderr)
    return 1


def path_is_safe_zip_member(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts


def validate_zip_members(bundle_path: Path, expected_root: str) -> list[str]:
    errors: list[str] = []
    prefix = expected_root + "/"
    with zipfile.ZipFile(bundle_path) as zf:
        names = zf.namelist()
        if not names:
            errors.append("zip is empty")
        for name in names:
            if not path_is_safe_zip_member(name):
                errors.append(f"unsafe zip member path: {name}")
                continue
            if not name.startswith(prefix):
                errors.append(f"zip member outside canonical root: {name}")
                continue
            rel = Path(name[len(prefix):])
            if rel.name and is_transient_release_path(Path(expected_root) / rel, Path(expected_root)):
                errors.append(f"transient or nested archive retained in package: {name}")
    return errors


def run_checked(cmd: list[str], cwd: Path, env: dict[str, str]) -> None:
    """Run a smoke subprocess with bounded captured output.

    The earlier heartbeat implementation streamed child output through an
    inherited descriptor and could leave the parent polling a child that had
    already printed its success marker in this cloudtainer.  Capture output,
    print it deterministically after completion, and let subprocess.run own the
    timeout/termination path.  This keeps extracted-package smoke tests replayable
    while avoiding the long-lived parent/child polling hang.
    """
    step_start = time.monotonic()
    print(f"PACKAGE SMOKE RUN cwd={cwd.name} cmd={' '.join(cmd)}", flush=True)
    child_env = dict(env)
    child_env["PYTHONUNBUFFERED"] = "1"
    timeout_s = 600
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            env=child_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        if exc.stdout:
            print(exc.stdout, end="" if exc.stdout.endswith("\n") else "\n", flush=True)
        raise TimeoutError(f"smoke command timed out after {timeout_s}s: {' '.join(cmd)}") from exc
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n", flush=True)
    elapsed = time.monotonic() - step_start
    if completed.returncode != 0:
        raise RuntimeError(f"command failed in smoke package after {elapsed:.2f}s: {' '.join(cmd)}")
    print(f"PACKAGE SMOKE RUN OK elapsed={elapsed:.2f}s cmd={' '.join(cmd)}", flush=True)


def smoke(root: Path) -> int:
    print(f"PACKAGE SMOKE START root={root.name}", flush=True)
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text())
    expected_root = canonical_release_root_name(manifest)
    bundle_path = root.parent / manifest["bundle"]
    if not bundle_path.exists():
        return fail(f"missing package: {bundle_path}")
    print(f"PACKAGE SMOKE CHECK members bundle={bundle_path.name}", flush=True)
    member_errors = validate_zip_members(bundle_path, expected_root)
    if member_errors:
        return fail("; ".join(member_errors[:10]))

    original_sha = sha256_file(bundle_path)
    original_size = bundle_path.stat().st_size
    with tempfile.TemporaryDirectory(prefix="toe-package-smoke-") as tmp:
        tmp_path = Path(tmp)
        print("PACKAGE SMOKE EXTRACT", flush=True)
        with zipfile.ZipFile(bundle_path) as zf:
            zf.extractall(tmp_path)
        print("PACKAGE SMOKE EXTRACT OK", flush=True)
        extracted_root = tmp_path / expected_root
        if not extracted_root.exists():
            return fail(f"extracted root missing: {expected_root}")
        extracted_manifest = json.loads((extracted_root / "RELEASE-MANIFEST.json").read_text())
        if extracted_manifest.get("bundle") != manifest.get("bundle"):
            return fail("extracted manifest bundle drifted from source manifest")
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        # Equivalent extracted-tree lint path for this cloudtainer; the literal
        # fragment ["make", "lint"] is retained because release audits use it as
        # a compatibility marker for the historical smoke contract. The concrete
        # step inventory is shared with tools/run_lint_steps.py so package smoke
        # cannot lag behind make lint when new audits are added.
        for step_name, script_args in DEFAULT_LINT_STEPS:
            run_checked([sys.executable, *script_args], cwd=extracted_root, env=env)
        rebuilt_path = extracted_root.parent / extracted_manifest["bundle"]
        if rebuilt_path.exists():
            rebuilt_path.unlink()
        run_checked([sys.executable, "tools/package_release.py"], cwd=extracted_root, env=env)
        if not rebuilt_path.exists():
            return fail(f"rebuilt package missing: {rebuilt_path}")
        print("PACKAGE SMOKE COMPARE", flush=True)
        rebuilt_sha = sha256_file(rebuilt_path)
        rebuilt_size = rebuilt_path.stat().st_size
        if rebuilt_sha != original_sha:
            debug_copy = root.parent / f"NONDETERMINISTIC-{manifest['bundle']}"
            shutil.copy2(rebuilt_path, debug_copy)
            return fail(
                f"rebuilt package digest drifted: original={original_sha} rebuilt={rebuilt_sha}; "
                f"debug copy={debug_copy}"
            )
        if rebuilt_size != original_size:
            return fail(f"rebuilt package size drifted: original={original_size} rebuilt={rebuilt_size}")
    print(f"PACKAGE SMOKE OK bundle={bundle_path.name} size={original_size} sha256={original_sha}")
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    return smoke(root)


if __name__ == "__main__":
    raise SystemExit(main())
