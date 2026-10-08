#!/usr/bin/env python3
"""Validate rights-gate coverage for all artifact-emitting publication entry points."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_publication_entrypoint_rights_gate_audit_rev0838 import ENTRYPOINTS, build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"publication-entrypoint-rights-gate-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def snapshot_paths(paths: list[Path]) -> dict[str, tuple[int, int] | None]:
    out: dict[str, tuple[int, int] | None] = {}
    for path in paths:
        key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        if path.exists():
            stat = path.stat()
            out[key] = (stat.st_size, stat.st_mtime_ns)
        else:
            out[key] = None
    return out


def assert_snapshot_unchanged(label: str, before: dict[str, tuple[int, int] | None], paths: list[Path]) -> None:
    after = snapshot_paths(paths)
    if after != before:
        changed = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
        fail(f"{label} changed publication artifacts during refusal test: {changed[:10]}")


def existing_publication_files() -> list[Path]:
    roots = [
        ROOT / "published" / "releases",
        ROOT / "published" / "releases" / "artifacts",
        ROOT / "published" / "releases" / "snapshots",
        ROOT / "release_queue",
    ]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(sorted(path for path in root.rglob("*") if path.is_file()))
    return sorted(set(files))


def assert_no_transient_bytecode() -> None:
    offenders = []
    for path in ROOT.rglob("*"):
        if path.name == "__pycache__" or path.suffix == ".pyc":
            offenders.append(path.relative_to(ROOT).as_posix())
            if len(offenders) >= 5:
                break
    if offenders:
        fail("transient bytecode present: " + ", ".join(offenders))


def run_probe(label: str, command: list[str], forbidden: list[str], tracked_paths: list[Path]) -> None:
    before = snapshot_paths(tracked_paths)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        fail(f"{label} succeeded even though rights readiness says publication is blocked")
    if "publication rights gate blocked" not in combined:
        fail(f"{label} did not fail with the publication rights gate message; output={combined[-400:]!r}")
    for marker in forbidden:
        if marker in combined:
            fail(f"{label} reached forbidden marker {marker!r} despite rights blocker")
    assert_snapshot_unchanged(label, before, tracked_paths)


def assert_entrypoint_refusals() -> None:
    publication_files = existing_publication_files()
    manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    bundle_path = ROOT.parent / manifest.get("bundle", "")
    package_paths = [bundle_path, bundle_path.with_name(bundle_path.name + ".sha256")]

    by_id = {cfg["id"]: cfg for cfg in ENTRYPOINTS}
    run_probe(
        "publish_audit.py",
        [sys.executable, str(ROOT / "scripts" / "publish_audit.py")],
        by_id["publish_audit_runner"]["forbidden_after_block_markers"],
        publication_files,
    )
    run_probe(
        "package_release.py",
        [sys.executable, str(ROOT / "scripts" / "package_release.py")],
        by_id["full_archive_package_release"]["forbidden_after_block_markers"],
        package_paths,
    )
    run_probe(
        "materialize_public_release.py",
        [sys.executable, str(ROOT / "scripts" / "materialize_public_release.py")],
        by_id["public_release_materializer"]["forbidden_after_block_markers"],
        publication_files,
    )
    run_probe(
        "publish_queue_item.py",
        [
            sys.executable,
            str(ROOT / "scripts" / "publish_queue_item.py"),
            "--item",
            "rev0838-rights-gate-probe-item-does-not-exist",
            "--release-slug",
            "rev0838-rights-gate-probe",
            "--dry-run",
        ],
        by_id["public_queue_publisher"]["forbidden_after_block_markers"],
        publication_files,
    )


def main() -> None:
    data = build(ROOT)
    json_path = ROOT / "AUDIT" / "PUBLICATION_ENTRYPOINT_RIGHTS_GATE_REV0838.json"
    md_path = ROOT / "AUDIT" / "PUBLICATION_ENTRYPOINT_RIGHTS_GATE_REV0838.md"
    if not json_path.is_file() or not md_path.is_file():
        fail("publication entrypoint rights gate audit files are missing")
    actual = json.loads(json_path.read_text(encoding="utf-8"))
    if actual != data:
        fail("AUDIT/PUBLICATION_ENTRYPOINT_RIGHTS_GATE_REV0838.json is stale")
    if md_path.read_text(encoding="utf-8") != render_markdown(data):
        fail("AUDIT/PUBLICATION_ENTRYPOINT_RIGHTS_GATE_REV0838.md does not exactly mirror JSON audit output")
    if data["shared_helper"]["missing_required_snippets"]:
        fail("shared rights helper missing snippets: " + ", ".join(data["shared_helper"]["missing_required_snippets"]))
    if not data["current_tree_expected_to_refuse_publication_entrypoints"]:
        fail("current tree is no longer rights-blocked; update/review the rev0838 refusal probes")
    for item in data["entrypoints"]:
        if not item["imports_shared_helper"]:
            fail(f"{item['path']} does not import shared publication rights helper")
        if not item["guard_call_present"]:
            fail(f"{item['path']} missing expected guard call {item['expected_guard_call']}")
        if not item["guard_precedes_first_mutation_marker"]:
            fail(f"{item['path']} rights guard does not precede first mutation marker")
    assert_no_transient_bytecode()
    assert_entrypoint_refusals()
    assert_no_transient_bytecode()
    print("publication-entrypoint-rights-gate-validate: OK (4 publication entrypoints refuse before mutation while rights-blocked)")


if __name__ == "__main__":
    main()
