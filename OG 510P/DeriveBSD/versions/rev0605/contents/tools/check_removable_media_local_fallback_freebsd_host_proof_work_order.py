#!/usr/bin/env python3
"""Guard the concrete FreeBSD real-host proof work order.

The risky unfinished milestone is the first imported primary-production FreeBSD
proof.  This check keeps the generated work order synced with the live proof
status reporter and rejects drift back into checker-simulation theatre.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
STAGER_REL = contract.HOST_PROOF_WORK_ORDER_STAGER_REL
VERIFIER_REL = contract.HOST_PROOF_WORK_ORDER_VERIFIER_REL
WORK_ORDER_REL = "validation/freebsd-real-host-proof-work-order/current"
MANIFEST_REL = f"{WORK_ORDER_REL}/real-host-proof-work-order.json"
RUN_REL = f"{WORK_ORDER_REL}/RUN_ON_FREEBSD.sh"
IMPORT_REL = f"{WORK_ORDER_REL}/IMPORT_IN_CLOUDTAINER.sh"
VERIFY_REL = f"{WORK_ORDER_REL}/VERIFY_WORK_ORDER.sh"
PREFLIGHT_REL = f"{WORK_ORDER_REL}/PREFLIGHT_ON_FREEBSD.sh"
README_REL = f"{WORK_ORDER_REL}/README.md"
DOCS = [
    "README.md",
    "docs/current/freebsd-real-host-proof-operator-packet.md",
    "docs/current/removable-media-freebsd-host-smoke.md",
    "docs/current/start-here-now.md",
]


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def load_json(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def run_stager(out_dir: Path, generated_at: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-S", str(ROOT / STAGER_REL), str(out_dir), "--generated-at", generated_at, "--replace", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_verifier(work_order_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-S", str(ROOT / VERIFIER_REL), str(work_order_dir), "--repo-root", str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def check_surface(errors: list[str]) -> None:
    stager = ROOT / STAGER_REL
    require(errors, stager.exists(), f"missing {STAGER_REL}")
    require(errors, bool(stager.stat().st_mode & 0o111), f"{STAGER_REL} must be executable")
    text = stager.read_text(encoding="utf-8", errors="replace")
    for token in [
        "host_proof_contract",
        "report_removable_media_local_fallback_host_proof_imports",
        "WORK_ORDER_POLICY",
        "CURRENT_CUBE_CUT_VERSION",
        "PRIMARY_FREEBSD_RELEASE",
        "SUPPORTED_FREEBSD_RELEASE_FLOOR",
        "HOST_TARGET_MATRIX_ID",
        "WORK_ORDER_FILE_DIGEST_POLICY",
        "WORK_ORDER_REPO_TOOL_DIGEST_POLICY",
        "VERIFY_WORK_ORDER_NAME",
        "PREFLIGHT_ON_FREEBSD_NAME",
        "HOST_PROOF_WORK_ORDER_VERIFIER_REL",
        "--fail-if-incomplete",
        "--require-primary-target",
        "HOST_PROOF_THEATRE_GATE_REL",
        "HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL",
        "does_not_claim_empty_import_root_is_complete",
    ]:
        require(errors, token in text, f"{STAGER_REL} missing token {token!r}")
    for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"]:
        # The strings may appear only as manifest-forbidden values, not in the runnable command text.
        runnable = text.split("forbidden_flags", 1)[0]
        require(errors, banned not in runnable, f"{STAGER_REL} runnable command templates must not contain {banned}")


def check_generated_sync(errors: list[str]) -> None:
    manifest_path = ROOT / MANIFEST_REL
    require(errors, manifest_path.exists(), f"missing {MANIFEST_REL}")
    if not manifest_path.exists():
        return
    observed = load_json(MANIFEST_REL)
    generated_at = str(observed.get("generated_at_utc") or contract.CURRENT_CUBE_CUT_VERSION)
    with tempfile.TemporaryDirectory(prefix="derivebsd-proof-work-order.") as td:
        proc = run_stager(Path(td) / "current", generated_at)
        require(errors, proc.returncode == 0, f"work-order stager should pass: stdout={proc.stdout!r} stderr={proc.stderr!r}")
        if proc.returncode == 0:
            expected = json.loads(proc.stdout)
            require(errors, observed == expected, f"{MANIFEST_REL} must match regenerated work order manifest")
            for name in ["PREFLIGHT_ON_FREEBSD.sh", "RUN_ON_FREEBSD.sh", "IMPORT_IN_CLOUDTAINER.sh", "VERIFY_WORK_ORDER.sh", "README.md"]:
                observed_text = (ROOT / WORK_ORDER_REL / name).read_text(encoding="utf-8", errors="replace")
                expected_text = (Path(td) / "current" / name).read_text(encoding="utf-8", errors="replace")
                require(errors, observed_text == expected_text, f"{WORK_ORDER_REL}/{name} must match regenerated output")
            verify_proc = run_verifier(ROOT / WORK_ORDER_REL)
            require(errors, verify_proc.returncode == 0, f"checked-in work-order verifier should pass: stdout={verify_proc.stdout!r} stderr={verify_proc.stderr!r}")
            temp_verify_proc = run_verifier(Path(td) / "current")
            require(errors, temp_verify_proc.returncode == 0, f"regenerated work-order verifier should pass: stdout={temp_verify_proc.stdout!r} stderr={temp_verify_proc.stderr!r}")


def check_manifest_semantics(errors: list[str]) -> None:
    obj = load_json(MANIFEST_REL)
    require(errors, obj.get("kind") == "removable.media.local.freebsd.real_host_proof.work_order", "manifest kind mismatch")
    require(errors, obj.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "manifest generated_for_version must bind current cube cut")
    require(errors, obj.get("manifest_digest_policy") == "canonical-sha256-over-manifest-excluding-manifest_canonical_sha256", "manifest digest policy drifted")
    require(errors, isinstance(obj.get("work_order_file_digests"), list) and len(obj.get("work_order_file_digests")) == 4, "manifest must bind four runnable work-order script digests")
    require(errors, isinstance(obj.get("repo_tool_digests"), list) and len(obj.get("repo_tool_digests")) >= 18, "manifest must bind repo proof-tool digests")
    risk = obj.get("risk", {}) if isinstance(obj.get("risk"), dict) else {}
    require(errors, risk.get("current_status") == "blocked-no-real-host-proof-import", "checked-in work order should show empty proof root as blocked")
    require(errors, risk.get("proof_complete") is False, "checked-in work order must not claim proof completion")
    target = obj.get("target_matrix", {}) if isinstance(obj.get("target_matrix"), dict) else {}
    require(errors, target.get("host_target_matrix_id") == contract.HOST_TARGET_MATRIX_ID, "manifest target matrix id drifted")
    primary = target.get("primary", {}) if isinstance(target.get("primary"), dict) else {}
    floor = target.get("supported_floor", {}) if isinstance(target.get("supported_floor"), dict) else {}
    for token in [contract.PRIMARY_FREEBSD_RELEASE, contract.SUPPORTED_FREEBSD_RELEASE_FLOOR, contract.HOST_TARGET_PRIMARY_TIER, contract.HOST_TARGET_LEGACY_TIER]:
        require(errors, token in json.dumps(obj, sort_keys=True), f"manifest missing target token {token!r}")
    require(errors, primary.get("minimum_kern_osreldate") == contract.PRIMARY_FREEBSD_OSRELDATE_MINIMUM, "primary osreldate floor drifted")
    require(errors, floor.get("minimum_kern_osreldate") == contract.MIN_FREEBSD_OSRELDATE, "legacy floor osreldate drifted")
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    for key in [
        "does_not_claim_empty_import_root_is_complete",
        "no_checker_simulation_flags_in_scripts",
        "cloudtainer_import_requires_primary_target",
        "cloudtainer_import_preflights_before_publish",
        "freebsd_preflight_runs_through_root_helper_before_collection",
        "preflight_only_host_check_available",
        "work_order_binds_live_proof_status",
        "work_order_binds_current_host_target_matrix",
        "work_order_binds_runnable_script_digests",
        "work_order_binds_repo_tool_digests",
    ]:
        require(errors, inv.get(key) is True, f"manifest invariant {key} must be true")


def check_scripts(errors: list[str]) -> None:
    for rel in [PREFLIGHT_REL, RUN_REL, IMPORT_REL, VERIFY_REL]:
        path = ROOT / rel
        require(errors, path.exists(), f"missing {rel}")
        require(errors, bool(path.stat().st_mode & 0o111), f"{rel} must be executable")
        text = path.read_text(encoding="utf-8", errors="replace")
        require(errors, text.startswith("#!/bin/sh\nset -eu"), f"{rel} must be a strict sh script")
        for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"]:
            require(errors, banned not in text, f"{rel} must not include non-proof flag {banned}")
    import_text = (ROOT / IMPORT_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["--require-primary-target", "--fail-if-incomplete", contract.HOST_PROOF_THEATRE_GATE_REL, contract.HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL, "VERIFY_WORK_ORDER.sh"]:
        require(errors, token in import_text, f"{IMPORT_REL} missing import success gate token {token!r}")
    preflight_text = (ROOT / PREFLIGHT_REL).read_text(encoding="utf-8", errors="replace")
    for token in [contract.HOST_PROOF_PREFLIGHT_REL, "sudo env PYTHON", "VERIFY_WORK_ORDER.sh", "uid"]:
        require(errors, token in preflight_text, f"{PREFLIGHT_REL} missing preflight token {token!r}")
    run_text = (ROOT / RUN_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["PREFLIGHT_ON_FREEBSD.sh", contract.HOST_SMOKE_COLLECTOR_REL, contract.HOST_PROOF_HANDOFF_SEALER_REL, "sudo env PYTHON", "uid"]:
        require(errors, token in run_text, f"{RUN_REL} missing collection token {token!r}")
    verify_text = (ROOT / VERIFY_REL).read_text(encoding="utf-8", errors="replace")
    for token in [contract.HOST_PROOF_WORK_ORDER_VERIFIER_REL, "--repo-root"]:
        require(errors, token in verify_text, f"{VERIFY_REL} missing verification token {token!r}")


def check_docs(errors: list[str]) -> None:
    for rel in DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in [STAGER_REL, VERIFIER_REL, WORK_ORDER_REL, "real-host proof work order"]:
            require(errors, token in text, f"{rel} missing work-order token {token!r}")


def main() -> int:
    errors: list[str] = []
    check_surface(errors)
    check_generated_sync(errors)
    check_manifest_semantics(errors)
    check_scripts(errors)
    check_docs(errors)
    if errors:
        print("FreeBSD real-host proof work-order check FAILED.")
        for error in errors[:60]:
            print("-", error)
        if len(errors) > 60:
            print(f"- ... {len(errors)-60} more errors")
        return 1
    print("FreeBSD real-host proof work-order check OK")
    print("Generated work order is synced, default-real-proof-only, and status-gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
