#!/usr/bin/env python3
"""Rebuild compact archive surfaces until they settle to a fixed point."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import os
import subprocess

SETTLE_TARGETS = [
    "release_queue/DECISION_INDEX.json",
    "release_queue/LATEST_DECISION.json",
    "release_queue/DECISION_INDEX.md",
    "release_queue/STATUS.md",
    "release_queue/QUEUE.md",
    "release_queue/LATEST_DECISION.md",
    "reports/surface_schema_validation.json",
    "reports/archive_invariants.json",
    "reports/context_pack_contract.json",
    "reports/context_pack_budget.json",
    "reports/archive_budget.json",
    "TRANSFER_SOURCES.md",
    "TRANSFER_INPUTS.sha256",
    "reports/transfer_source_receipt.json",
    "reports/transient_surface_audit.json",
    "reports/manifest_sha256_verification.json",
    "reports/manifest_coverage_audit.json",
    "reports/lifecycle_gate_status.json",
    "reports/archive_surface_coherence.json",
    "MANIFEST.json",
    "MANIFEST.sha256",
]


def file_hash(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def snapshot(root: pathlib.Path) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for rel in SETTLE_TARGETS:
        path = root / rel
        out[rel] = file_hash(path) if path.exists() else None
    return out




def update_revision_bound_surfaces(root: pathlib.Path) -> None:
    revision = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))["revision"]

    path = root / "release_queue" / "QUEUE_INDEX.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["generated_for_revision"] = revision
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    assurance_path = root / "ASSURANCE_ARTIFACTS.json"
    assurance = json.loads(assurance_path.read_text(encoding="utf-8"))
    assurance["generated_for_revision"] = revision
    assurance_path.write_text(json.dumps(assurance, indent=2) + "\n", encoding="utf-8")


def build_manifest_json(root: pathlib.Path) -> None:
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    (root / "MANIFEST.json").write_text(json.dumps({"files": files}, indent=2) + "\n", encoding="utf-8")


def build_manifest_sha256(root: pathlib.Path) -> None:
    files = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "MANIFEST.sha256"
    )
    lines = []
    for rel in files:
        h = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        lines.append(f"{h}  {rel}")
    (root / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_script(root: pathlib.Path, *args: str) -> int:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run(["python3", *args], cwd=root, text=True, capture_output=True, env=env)
    return proc.returncode


def full_pass(root: pathlib.Path) -> dict[str, int]:
    codes: dict[str, int] = {}
    update_revision_bound_surfaces(root)

    for script in [
        ("publishing/render_transfer_sources.py", "--root", "."),
        ("publishing/build_decision_index.py", "--root", "."),
        ("publishing/render_queue_surfaces.py", "--root", "."),
        ("publishing/check_surface_schemas.py", "--root", ".", "--write-report", "reports/surface_schema_validation.json"),
        ("publishing/check_context_pack_budget.py", "--root", ".", "--write-report", "reports/context_pack_budget.json"),
        ("publishing/check_archive_budget.py", "--root", ".", "--write-report", "reports/archive_budget.json"),
        ("publishing/check_transfer_source_receipt.py", "--root", ".", "--write-report", "reports/transfer_source_receipt.json"),
        ("publishing/check_transient_surface.py", "--root", ".", "--write-report", "reports/transient_surface_audit.json"),
    ]:
        codes[script[0]] = run_script(root, *script)

    build_manifest_json(root)
    build_manifest_sha256(root)

    for script in [
        ("publishing/verify_manifest_sha256.py", "--root", ".", "--write-report", "reports/manifest_sha256_verification.json"),
        ("publishing/check_manifest_coverage.py", "--root", ".", "--write-report", "reports/manifest_coverage_audit.json"),
        ("publishing/check_archive_invariants.py", "--root", ".", "--write-report", "reports/archive_invariants.json"),
        ("publishing/check_context_pack_contract.py", "--root", ".", "--write-report", "reports/context_pack_contract.json"),
        ("publishing/build_lifecycle_gate_status.py", "--root", ".", "--write-report", "reports/lifecycle_gate_status.json"),
        ("publishing/check_archive_coherence.py", "--root", ".", "--write-report", "reports/archive_surface_coherence.json"),
    ]:
        codes[script[0]] = run_script(root, *script)
    return codes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-passes", type=int, default=6)
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    previous = None
    codes: dict[str, int] = {}
    for _ in range(args.max_passes):
        codes = full_pass(root)
        current = snapshot(root)
        if current == previous:
            break
        previous = current
    else:
        print(json.dumps({"status": "fail", "reason": "surface rebuild did not settle within max passes"}, indent=2))
        return 1

    # Final pass after settling so the manifest covers the final reports.
    codes = full_pass(root)
    ok = all(
        codes.get(script, 1) == 0
        for script in [
            "publishing/check_surface_schemas.py",
            "publishing/check_archive_invariants.py",
            "publishing/check_context_pack_contract.py",
            "publishing/check_context_pack_budget.py",
            "publishing/check_archive_budget.py",
            "publishing/check_transfer_source_receipt.py",
            "publishing/render_queue_surfaces.py",
            "publishing/check_transient_surface.py",
            "publishing/verify_manifest_sha256.py",
            "publishing/check_manifest_coverage.py",
            "publishing/check_archive_coherence.py",
        ]
    )
    print(json.dumps({"status": "pass" if ok else "fail", "final_returncodes": codes}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
