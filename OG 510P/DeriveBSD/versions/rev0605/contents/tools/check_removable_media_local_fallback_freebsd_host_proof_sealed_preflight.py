#!/usr/bin/env python3
"""Guard sealed FreeBSD host-proof import preflight.

The first real host proof is scarce.  Before the cloudtainer publishes a returned
sealed archive into the checked import root, the operator needs a dry run that
uses the same snapshot/unseal/verify/copy/identity path and proves what import
directory would be created without writing it.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cube_digest_lib import canonical_digest, load_json_strict_text  # noqa: E402
from freebsd import host_proof_contract as contract  # noqa: E402

FINALIZER_REL = contract.HOST_PROOF_FINALIZER_REL
SEAL_REL = contract.HOST_PROOF_HANDOFF_SEALER_REL
PREFLIGHT_REL = contract.HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL
SEALED_IMPORT_REL = contract.HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL
WORK_ORDER_REL = contract.HOST_PROOF_WORK_ORDER_STAGER_REL
VERIFY_WORK_ORDER_REL = contract.HOST_PROOF_WORK_ORDER_VERIFIER_REL
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
DOCS = [
    "README.md",
    "docs/current/freebsd-real-host-proof-operator-packet.md",
    "docs/current/removable-media-freebsd-host-smoke.md",
    "docs/current/start-here-now.md",
]
GENERATED_AT = "2026-06-12T23:00:00Z"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-S", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def write_sums(directory: Path) -> None:
    rows = [contract.RECEIPT_NAME, contract.BUNDLE_NAME]
    if (directory / contract.README_NAME).exists():
        rows.append(contract.README_NAME)
    (directory / contract.SUMS_NAME).write_text(
        "".join(f"{sha256_file(directory / name).removeprefix('sha256:')}  {name}\n" for name in rows),
        encoding="utf-8",
    )


def build_checker_handoff(directory: Path) -> None:
    directory.mkdir()
    shutil.copy2(ROOT / SUCCESS_SIM_REL, directory / contract.RECEIPT_NAME)
    proc = run_tool([
        FINALIZER_REL,
        str(directory / contract.RECEIPT_NAME),
        "--allow-checker-simulation",
        "--generated-at",
        GENERATED_AT,
        "--output",
        str(directory / contract.BUNDLE_NAME),
    ])
    if proc.returncode != 0:
        raise RuntimeError(f"could not build checker handoff: {proc.stdout} {proc.stderr}")
    (directory / contract.README_NAME).write_text(
        "Checker-simulation handoff for release-critical sealed preflight mechanics only; not release proof.\n",
        encoding="utf-8",
    )
    write_sums(directory)


def copied_snapshot_manifest(handoff: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    total_size = 0
    for name in sorted(contract.HANDOFF_ALLOWED_NAMES):
        child = handoff / name
        if child.exists() and child.is_file() and not child.is_symlink():
            size = child.stat().st_size
            total_size += size
            rows.append({"path": f"handoff/{child.name}", "sha256": sha256_file(child), "size_bytes": size})
    core: dict[str, object] = {
        "kind": contract.IMPORT_RECEIPT_SNAPSHOT_KIND,
        "snapshot_policy": contract.IMPORT_RECEIPT_SNAPSHOT_POLICY,
        "file_count": len(rows),
        "total_size_bytes": total_size,
        "files": rows,
    }
    return {**core, "canonical_sha256": canonical_digest(core)}


def import_root_children(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(child.name for child in root.iterdir())


def mode_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-sealed-preflight-check-") as td_name:
        tmp = Path(td_name)
        handoff = tmp / "handoff"
        import_root = tmp / "imports"
        build_checker_handoff(handoff)
        archive = tmp / "handoff.zip"
        sealed = run_tool([SEAL_REL, str(handoff), "--output", str(archive), "--allow-checker-simulation"])
        require(errors, sealed.returncode == 0, f"checker handoff should seal explicitly: {sealed.stdout} {sealed.stderr}")

        default_preflight = run_tool([PREFLIGHT_REL, str(archive), "--import-root", str(import_root)])
        require(errors, default_preflight.returncode != 0, "default sealed preflight must reject checker-simulation-non-proof archives")
        require(errors, "default handoff verification accepts only real-host-proof" in default_preflight.stderr, "default preflight rejection should come from strict handoff verification")
        require(errors, import_root_children(import_root) == [], "failed default preflight must not publish import-root children")
        require(errors, not any(child.name.startswith(".imports.sealed-handoff-preflight-") for child in tmp.iterdir()), "failed default preflight must cleanup scratch state")

        allowed = run_tool([PREFLIGHT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation", "--json"])
        require(errors, allowed.returncode == 0, f"explicit checker preflight should pass: {allowed.stdout} {allowed.stderr}")
        require(errors, import_root_children(import_root) == [], "successful preflight must not publish import-root children")
        require(errors, not any(child.name.startswith(".imports.sealed-handoff-preflight-") for child in tmp.iterdir()), "successful preflight must cleanup scratch state")
        try:
            report = json.loads(allowed.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"preflight JSON was not parseable: {exc}: {allowed.stdout!r}")
            report = {}
        expected_name = contract.import_directory_name("checker-simulation-non-proof", str(copied_snapshot_manifest(handoff)["canonical_sha256"]))
        if isinstance(report, dict):
            require(errors, report.get("kind") == "removable.media.local.freebsd.host.proof.sealed_import.preflight", "preflight report kind mismatch")
            require(errors, report.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "preflight report must bind current cube cut")
            require(errors, report.get("preflight_policy") == contract.SEALED_IMPORT_PREFLIGHT_POLICY, "preflight report must bind preflight policy")
            require(errors, report.get("preflight_ready") is True, "explicit checker preflight should be ready")
            require(errors, report.get("status") == "ready-to-import-checker-simulation-non-proof", "explicit checker preflight status mismatch")
            require(errors, report.get("predicted_import_dir", "").endswith(expected_name), "preflight must predict the full copied-snapshot import identity")
            require(errors, report.get("predicted_import_dir_exists") is False, "preflight should show no predicted collision before import")
            invariants = report.get("invariants", {}) if isinstance(report.get("invariants"), dict) else {}
            for key in [
                "does_not_publish_import",
                "archive_snapshot_taken_before_zip_validation",
                "canonical_zip_metadata_validated_before_unseal",
                "handoff_verified_before_import_prediction",
                "handoff_copied_through_importer_nofollow_staging_path",
                "predicted_import_dir_uses_full_copied_handoff_snapshot_digest",
            ]:
                require(errors, invariants.get(key) is True, f"preflight invariant {key} must be true")
            require(errors, report.get("copied_handoff_snapshot") == copied_snapshot_manifest(handoff), "preflight must bind the copied handoff snapshot")

            collision_dir = import_root / expected_name
            collision_dir.mkdir(parents=True)
            duplicate_preflight = run_tool([PREFLIGHT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation", "--json"])
            require(errors, duplicate_preflight.returncode != 0, "preflight must block an existing predicted import directory by default")
            try:
                duplicate_report = json.loads(duplicate_preflight.stdout)
            except json.JSONDecodeError as exc:
                errors.append(f"duplicate preflight JSON was not parseable: {exc}: {duplicate_preflight.stdout!r}")
                duplicate_report = {}
            if isinstance(duplicate_report, dict):
                require(errors, duplicate_report.get("preflight_ready") is False, "duplicate preflight should not be ready")
                require(errors, duplicate_report.get("status") == "blocked-sealed-handoff-not-ready-for-import", "duplicate preflight status should be blocked")
                require(errors, any("already exists" in str(err) for err in duplicate_report.get("errors", [])), "duplicate preflight should name predicted import collision")
            allowed_existing = run_tool([PREFLIGHT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation", "--allow-existing-import", "--json"])
            require(errors, allowed_existing.returncode == 0, f"preflight --allow-existing-import should pass: {allowed_existing.stdout} {allowed_existing.stderr}")
            shutil.rmtree(collision_dir)

        sealed_import = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, sealed_import.returncode == 0, f"normal sealed importer should still publish after preflight once the predicted collision is absent: {sealed_import.stdout} {sealed_import.stderr}")
        require(errors, import_root_children(import_root) == [expected_name], "preflight must not change the import identity used by sealed importer")

        reuse_preflight = run_tool([PREFLIGHT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation", "--reuse-existing-import", "--json"])
        require(errors, reuse_preflight.returncode == 0, f"preflight --reuse-existing-import should accept the matching already-published sealed import: {reuse_preflight.stdout} {reuse_preflight.stderr}")
        try:
            reuse_report = json.loads(reuse_preflight.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"reuse preflight JSON was not parseable: {exc}: {reuse_preflight.stdout!r}")
            reuse_report = {}
        if isinstance(reuse_report, dict):
            require(errors, reuse_report.get("preflight_ready") is True, "reuse preflight should be ready")
            require(errors, reuse_report.get("status") == "ready-to-reuse-existing-checker-simulation-non-proof-import", "reuse preflight status should identify an idempotent existing import")
            require(errors, reuse_report.get("existing_import_reuse_ready") is True, "reuse preflight must confirm existing import reuse readiness")
            require(errors, reuse_report.get("existing_import_reuse_policy") == contract.SEALED_IMPORT_EXISTING_REUSE_POLICY, "reuse preflight must bind the existing import reuse policy")
            invariants = reuse_report.get("invariants", {}) if isinstance(reuse_report.get("invariants"), dict) else {}
            require(errors, invariants.get("existing_import_reuse_requires_audit_clean_matching_archive_digest") is True, "reuse preflight must assert audit-clean matching archive digest reuse")
    return errors


def surface_errors() -> list[str]:
    errors: list[str] = []
    for rel in [PREFLIGHT_REL, SEALED_IMPORT_REL, SEAL_REL, WORK_ORDER_REL, VERIFY_WORK_ORDER_REL]:
        require(errors, (ROOT / rel).exists(), f"missing {rel}")
    tool_text = (ROOT / PREFLIGHT_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        "SEALED_IMPORT_PREFLIGHT_POLICY",
        "copy_archive_snapshot",
        "_archive_errors",
        "unseal_archive",
        "copy_handoff",
        "copied_handoff_snapshot",
        "predicted_import_dir",
        "--require-primary-target",
        "--allow-existing-import",
        "--reuse-existing-import",
        "existing_import_reuse_requires_audit_clean_matching_archive_digest",
        "does_not_publish_import",
    ]:
        require(errors, token in tool_text, f"sealed preflight tool must bind token {token!r}")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL", PREFLIGHT_REL, "SEALED_IMPORT_PREFLIGHT_POLICY"]:
        require(errors, token in contract_text, f"shared proof-tool contract must bind sealed preflight token {token!r}")
    work_order_text = (ROOT / WORK_ORDER_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL", "cloudtainer_import_preflights_before_publish"]:
        require(errors, token in work_order_text, f"work-order stager must bind sealed preflight token {token!r}")
    for rel in DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in [PREFLIGHT_REL, "sealed", "preflight"]:
            require(errors, token in text, f"{rel} missing sealed-preflight operator token {token!r}")
    return errors


def main() -> int:
    errors = mode_errors() + surface_errors()
    if errors:
        print("FreeBSD host proof sealed preflight check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof sealed preflight check OK")
    print("Sealed archives can now be dry-run verified and identity-predicted before publish")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
