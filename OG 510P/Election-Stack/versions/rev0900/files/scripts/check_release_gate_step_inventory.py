#!/usr/bin/env python3
"""Validate the canonical release-gate step inventory.

The release gate is most auditable when the ordered child-step list has one
source of truth. This check keeps that inventory from drifting away from the
runner CLI or from the actual scripts on disk.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

import release_gate
import release_gate_steps

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "release_gate.py"


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def _listed_step_names() -> list[str]:
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--list"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"release_gate.py --list failed: {proc.stderr.strip() or proc.stdout.strip()}")

    names: list[str] = []
    saw_manifest = False
    for line in proc.stdout.splitlines():
        if line.startswith("manifest "):
            saw_manifest = release_gate_steps.MANIFEST_STEP_NAME in line and "--check" in line
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and parts[0].isdigit():
            names.append(parts[1].strip())

    if not saw_manifest:
        fail("release_gate.py --list did not show the final manifest --check step")
    return names


def _runner_args(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "write_manifest": True,
        "skip_manifest": False,
        "only": None,
        "from_step": None,
        "to_step": None,
        "quiet": True,
        "step_timeout": None,
        "progress": False,
        "profile": False,
        "keep_going": False,
        "build_zip": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _run_with_fake_child(
    args: argparse.Namespace,
    check_steps: list[list[str]],
    manifest_step: list[str],
    *,
    fail_when: object | None = None,
) -> tuple[int, list[list[str]]]:
    calls: list[list[str]] = []
    original = release_gate.run

    def fake_run(cmd: list[str], **_kwargs: object) -> bool:
        calls.append(list(cmd))
        return not (callable(fail_when) and fail_when(cmd))

    release_gate.run = fake_run  # type: ignore[assignment]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = release_gate._run_selected_gate(args, check_steps, manifest_step)
    finally:
        release_gate.run = original  # type: ignore[assignment]
    return rc, calls


def _check_lock_held_release_build_contract(errors: list[str]) -> None:
    py = sys.executable
    checks = [[py, "synthetic_check.py"]]
    manifest = [py, "synthetic_manifest.py", "--write"]

    with tempfile.TemporaryDirectory(prefix="tes_gate_build_contract_") as td:
        out = str(Path(td) / "release.zip")
        rc, calls = _run_with_fake_child(_runner_args(build_zip=out), checks, manifest)
        expected = checks + [manifest] + release_gate.release_zip_steps(out)
        if rc != 0 or calls != expected:
            errors.append(
                "--build-zip orchestration must run checks, manifest write, deterministic build, and verifier in order "
                f"(rc={rc}, calls={calls!r})"
            )

        rc, calls = _run_with_fake_child(
            _runner_args(build_zip=out),
            checks,
            manifest,
            fail_when=lambda cmd: cmd == manifest,
        )
        if rc == 0 or any("build_release_zip.py" in part or "verify_release_zip.py" in part for cmd in calls for part in cmd):
            errors.append("--build-zip must not run when the manifest step fails")

        rc, calls = _run_with_fake_child(
            _runner_args(build_zip=out),
            checks,
            manifest,
            fail_when=lambda cmd: any(part.endswith("build_release_zip.py") for part in cmd),
        )
        if rc == 0 or any(part.endswith("verify_release_zip.py") for cmd in calls for part in cmd):
            errors.append("release ZIP verification must not run when deterministic construction fails")

        invalid_cases = [
            _runner_args(build_zip=out, write_manifest=False),
            _runner_args(build_zip=out, only="1"),
            _runner_args(build_zip="relative-release.zip"),
        ]
        for args in invalid_cases:
            rc, calls = _run_with_fake_child(args, checks, manifest)
            if rc == 0 or calls:
                errors.append(f"invalid --build-zip request was not rejected before child execution: {args!r}")

        existing = Path(td) / "existing.zip"
        existing.write_bytes(b"existing")
        rc, calls = _run_with_fake_child(_runner_args(build_zip=str(existing)), checks, manifest)
        if rc == 0 or calls:
            errors.append("--build-zip must refuse to replace an existing carrier")


def main() -> int:
    names = list(release_gate_steps.CHECK_STEP_NAMES)
    errors: list[str] = []

    if not names:
        errors.append("CHECK_STEP_NAMES is empty")

    seen: set[str] = set()
    for i, name in enumerate(names, 1):
        if not name.endswith(".py"):
            errors.append(f"step {i}: {name!r} is not a Python script name")
        if "/" in name or "\\" in name or name in {".", ".."} or ".." in Path(name).parts:
            errors.append(f"step {i}: {name!r} must be a bare script filename")
        if name in seen:
            errors.append(f"duplicate release-gate step: {name}")
        seen.add(name)
        if name == release_gate_steps.MANIFEST_STEP_NAME:
            errors.append("build_manifest.py must remain the separate final manifest step, not a child check")
        if not (ROOT / "scripts" / name).is_file():
            errors.append(f"step {i}: missing scripts/{name}")

    required = {
        "check_release_gate_doc_coverage.py",
        "check_release_gate_step_inventory.py",
        "check_release_gate_single_instance_lock.py",
        "check_release_packaging_alignment.py",
        "check_release_path_policy.py",
        "check_release_control_files.py",
        "check_release_zip_rebuild_from_extract.py",
        "check_release_zip_verifier.py",
        "check_release_safe_extractor.py",
        "check_version_consistency.py",
    }
    missing_required = sorted(required - seen)
    if missing_required:
        errors.append("required release-control checks missing: " + ", ".join(missing_required))

    if (ROOT / "scripts" / release_gate_steps.MANIFEST_STEP_NAME).is_file() is False:
        errors.append(f"missing manifest step script: scripts/{release_gate_steps.MANIFEST_STEP_NAME}")

    runner_text = RUNNER.read_text(encoding="utf-8")
    if "check_steps: list[list[str]] = [" in runner_text:
        errors.append("release_gate.py still contains an inline check_steps list instead of the shared inventory")
    if "release_gate_steps.build_check_steps" not in runner_text:
        errors.append("release_gate.py does not appear to build checks from release_gate_steps")

    listed = _listed_step_names()
    if listed != names:
        errors.append(
            "release_gate.py --list order differs from release_gate_steps.CHECK_STEP_NAMES "
            f"(listed={len(listed)} inventory={len(names)})"
        )

    _check_lock_held_release_build_contract(errors)

    if errors:
        for err in errors:
            print("ERROR:", err, file=sys.stderr)
        return 2

    print(
        f"PASS: release-gate inventory has {len(names)} child steps plus final manifest check; "
        "lock-held --build-zip ordering/rejection contract passes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
