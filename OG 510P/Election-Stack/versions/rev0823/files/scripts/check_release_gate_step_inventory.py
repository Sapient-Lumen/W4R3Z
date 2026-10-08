#!/usr/bin/env python3
"""Validate the canonical release-gate step inventory.

The release gate is most auditable when the ordered child-step list has one
source of truth. This check keeps that inventory from drifting away from the
runner CLI or from the actual scripts on disk.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

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

    if errors:
        for err in errors:
            print("ERROR:", err, file=sys.stderr)
        return 2

    print(f"PASS: release-gate inventory has {len(names)} child steps plus final manifest check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
