#!/usr/bin/env python3
"""Exercise the FreeBSD host-proof import-root auditor.

The importer creates a finite digest-named import.  This check proves the next
maintenance guard: any checked/imported proof directory can be rescanned after
import, checker simulations are rejected by default, import receipts must bind
all copied handoff files, and import roots cannot accumulate loose evidence
files.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cube_digest_lib import canonical_digest, load_json_strict_text, write_pretty_json
from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
FINALIZER_REL = contract.HOST_PROOF_FINALIZER_REL
IMPORT_REL = contract.HOST_PROOF_HANDOFF_IMPORTER_REL
AUDIT_REL = contract.HOST_PROOF_IMPORT_AUDITOR_REL
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
GENERATED_AT = "2026-06-12T23:00:00Z"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-S", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def load_json(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def load_auditor_module() -> Any:
    spec = importlib.util.spec_from_file_location("derivebsd_host_proof_import_auditor_under_test", ROOT / AUDIT_REL)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load import auditor module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return "sha256:" + sha256sum(path)


def copied_snapshot_manifest(handoff: Path) -> dict[str, Any]:
    return contract.copied_handoff_snapshot(handoff)


def sha256sum(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_checker_handoff(directory: Path, *, with_readme: bool = True) -> None:
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
    if with_readme:
        (directory / contract.README_NAME).write_text(
            "Checker-simulation handoff for release-critical import-audit mechanics only; not release proof.\n",
            encoding="utf-8",
        )
    rows = [contract.RECEIPT_NAME, contract.BUNDLE_NAME]
    if with_readme:
        rows.append(contract.README_NAME)
    (directory / contract.SUMS_NAME).write_text(
        "".join(f"{sha256sum(directory / name)}  {name}\n" for name in rows),
        encoding="utf-8",
    )


def audit_mode_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-import-audit-check-") as td_name:
        tmp = Path(td_name)
        handoff = tmp / "handoff"
        import_root = tmp / "imports"
        build_checker_handoff(handoff)

        imported = run_tool([IMPORT_REL, str(handoff), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, imported.returncode == 0, f"checker import should pass for audit setup: {imported.stdout} {imported.stderr}")
        import_dirs = sorted(import_root.iterdir()) if import_root.exists() else []
        require(errors, len(import_dirs) == 1, "setup import should create exactly one import directory")
        import_dir = import_dirs[0] if import_dirs else None

        default_audit = run_tool([AUDIT_REL, str(import_root)])
        require(errors, default_audit.returncode != 0, "default import audit must reject checker-simulation imports")
        require(errors, "default import audit accepts only real-host-proof imports" in default_audit.stderr, "default audit rejection should name real-host-proof requirement")

        allowed = run_tool([AUDIT_REL, str(import_root), "--allow-checker-simulation"])
        require(errors, allowed.returncode == 0, f"explicit checker import audit should pass: {allowed.stdout} {allowed.stderr}")

        primary_flag_with_checker = run_tool([AUDIT_REL, str(import_root), "--allow-checker-simulation", "--require-primary-target"])
        require(errors, primary_flag_with_checker.returncode == 0, f"primary-target flag should be inert for checker-simulation imports: {primary_flag_with_checker.stdout} {primary_flag_with_checker.stderr}")

        auditor_module = load_auditor_module()
        legacy_real_record = {
            "proof_status": "real-host-proof",
            "receipt": {
                "host_target_matrix_id": contract.HOST_TARGET_MATRIX_ID,
                "host_target_tier": contract.HOST_TARGET_LEGACY_TIER,
            },
            "bundle": {
                "host_target_matrix_id": contract.HOST_TARGET_MATRIX_ID,
                "host_target_tier": contract.HOST_TARGET_LEGACY_TIER,
            },
            "invariants": {"import_receipt_preserves_host_target_tier": True},
        }
        primary_errors = auditor_module._primary_target_errors(
            legacy_real_record,
            "real-host-proof",
            require_primary_target=True,
        )
        require(errors, any("primary-production target tier" in error for error in primary_errors), "primary-target audit must reject legacy-floor real-host-proof release evidence")
        require(
            errors,
            auditor_module._primary_target_errors(legacy_real_record, "real-host-proof", require_primary_target=False) == [],
            "legacy-floor target helper must remain opt-in so ad-hoc imports can still be audited without release promotion",
        )

        if import_dir is not None:
            record_path = import_dir / contract.IMPORT_RECEIPT_NAME
            record = load_json(record_path)
            paths = sorted(row.get("path") for row in record.get("files", []) if isinstance(row, dict))
            require(errors, f"handoff/{contract.README_NAME}" in paths, "import receipt must enumerate optional README.import.txt when copied")
            invariants = record.get("invariants", {}) if isinstance(record.get("invariants"), dict) else {}
            require(errors, invariants.get("import_receipt_enumerates_all_imported_handoff_files") is True, "import receipt must assert full handoff-file enumeration")
            require(errors, invariants.get("import_directory_name_binds_full_copied_handoff_snapshot_canonical_digest") is True, "import receipt must assert full copied-snapshot import directory binding")
            require(errors, invariants.get("import_receipt_binds_source_transport") is True, "import receipt must assert source transport provenance")
            require(errors, invariants.get("directory_import_copies_allowed_regular_files_without_following_symlinks") is True, "import receipt must assert nofollow staging copy")
            require(errors, invariants.get("import_receipt_binds_copied_snapshot_not_mutable_source") is True, "import receipt must assert copied snapshot provenance")
            require(errors, invariants.get("import_receipt_binds_copied_snapshot_manifest_digest") is True, "import receipt must assert copied snapshot manifest digest provenance")
            require(errors, invariants.get("staged_files_and_import_receipt_fsynced_before_publish") is True, "import receipt must assert staging fsync before publish")
            require(errors, invariants.get("import_parent_directory_fsynced_after_publish") is True, "import receipt must assert import parent fsync after publish")
            require(errors, record.get("copy_policy") == contract.DIRECTORY_IMPORT_COPY_POLICY, "import receipt must bind the shared directory copy policy")
            require(errors, record.get("durable_write_policy") == contract.IMPORT_DURABLE_WRITE_POLICY, "import receipt must bind the durable fsync write policy")
            require(errors, record.get("atomic_publish_policy") == "copy-verify-fsync-write-receipt-fsync-then-rename-and-fsync-parent-to-full-digest-import-dir", "import receipt must bind the fsync atomic publish policy")
            require(errors, record.get("copied_handoff_snapshot") == copied_snapshot_manifest(import_dir / "handoff"), "import receipt must bind the copied handoff snapshot manifest")
            transport = record.get("source_transport", {}) if isinstance(record.get("source_transport"), dict) else {}
            require(errors, transport.get("kind") == contract.DIRECTORY_IMPORT_SOURCE_KIND, "directory import receipt must bind directory source transport")
            require(errors, transport.get("transport_policy") == contract.IMPORT_RECEIPT_SOURCE_TRANSPORT_POLICY, "import receipt source transport must bind the shared policy")
            snapshot_digest = copied_snapshot_manifest(import_dir / "handoff")["canonical_sha256"]
            expected_name = contract.import_directory_name("checker-simulation-non-proof", snapshot_digest)
            require(errors, import_dir.name == expected_name, "setup import must use full copied handoff snapshot canonical digest in the directory name")

            truncated_name_root = tmp / "truncated-name-imports"
            shutil.copytree(import_root, truncated_name_root)
            truncated_import = next(truncated_name_root.iterdir())
            truncated_target = truncated_name_root / f"checker-simulation-non-proof-{snapshot_digest.removeprefix('sha256:')[:16]}"
            truncated_import.rename(truncated_target)
            truncated_proc = run_tool([AUDIT_REL, str(truncated_name_root), "--allow-checker-simulation"])
            require(errors, truncated_proc.returncode != 0, "import audit must reject legacy short-prefix digest import directory names")
            require(errors, "full copied handoff snapshot canonical digest" in truncated_proc.stderr, "truncated-name rejection should name full digest binding")

            stale_record = tmp / "stale-record-imports"
            shutil.copytree(import_root, stale_record)
            stale_import = next(stale_record.iterdir())
            stale_json = load_json(stale_import / contract.IMPORT_RECEIPT_NAME)
            stale_json["bundle"]["canonical_sha256"] = "sha256:" + "0" * 64
            write_pretty_json(stale_import / contract.IMPORT_RECEIPT_NAME, stale_json)
            stale_proc = run_tool([AUDIT_REL, str(stale_record), "--allow-checker-simulation"])
            require(errors, stale_proc.returncode != 0, "import audit must reject stale import receipt bundle digest")
            require(errors, "bind bundle.json canonical digest" in stale_proc.stderr, "stale import receipt rejection should name bundle canonical digest")

            missing_readme_row_root = tmp / "missing-readme-row-imports"
            shutil.copytree(import_root, missing_readme_row_root)
            missing_import = next(missing_readme_row_root.iterdir())
            missing_json = load_json(missing_import / contract.IMPORT_RECEIPT_NAME)
            missing_json["files"] = [row for row in missing_json.get("files", []) if row.get("path") != f"handoff/{contract.README_NAME}"]
            write_pretty_json(missing_import / contract.IMPORT_RECEIPT_NAME, missing_json)
            missing_proc = run_tool([AUDIT_REL, str(missing_readme_row_root), "--allow-checker-simulation"])
            require(errors, missing_proc.returncode != 0, "import audit must reject import receipts that omit copied handoff files")
            require(errors, "files list must enumerate every imported handoff file" in missing_proc.stderr, "missing-file-row rejection should name full handoff enumeration")

            missing_transport_root = tmp / "missing-source-transport-imports"
            shutil.copytree(import_root, missing_transport_root)
            missing_transport_import = next(missing_transport_root.iterdir())
            missing_transport_json = load_json(missing_transport_import / contract.IMPORT_RECEIPT_NAME)
            missing_transport_json.pop("source_transport", None)
            write_pretty_json(missing_transport_import / contract.IMPORT_RECEIPT_NAME, missing_transport_json)
            missing_transport_proc = run_tool([AUDIT_REL, str(missing_transport_root), "--allow-checker-simulation"])
            require(errors, missing_transport_proc.returncode != 0, "import audit must reject import receipts without source_transport provenance")
            require(errors, "source_transport provenance" in missing_transport_proc.stderr, "missing source_transport rejection should name provenance")

            missing_copy_policy_root = tmp / "missing-copy-policy-imports"
            shutil.copytree(import_root, missing_copy_policy_root)
            missing_copy_policy_import = next(missing_copy_policy_root.iterdir())
            missing_copy_policy_json = load_json(missing_copy_policy_import / contract.IMPORT_RECEIPT_NAME)
            missing_copy_policy_json.pop("copy_policy", None)
            write_pretty_json(missing_copy_policy_import / contract.IMPORT_RECEIPT_NAME, missing_copy_policy_json)
            missing_copy_policy_proc = run_tool([AUDIT_REL, str(missing_copy_policy_root), "--allow-checker-simulation"])
            require(errors, missing_copy_policy_proc.returncode != 0, "import audit must reject import receipts without copy_policy")
            require(errors, "nofollow staging copy policy" in missing_copy_policy_proc.stderr, "missing copy policy rejection should name nofollow staging copy")

            missing_snapshot_root = tmp / "missing-copied-snapshot-imports"
            shutil.copytree(import_root, missing_snapshot_root)
            missing_snapshot_import = next(missing_snapshot_root.iterdir())
            missing_snapshot_json = load_json(missing_snapshot_import / contract.IMPORT_RECEIPT_NAME)
            missing_snapshot_json.pop("copied_handoff_snapshot", None)
            write_pretty_json(missing_snapshot_import / contract.IMPORT_RECEIPT_NAME, missing_snapshot_json)
            missing_snapshot_proc = run_tool([AUDIT_REL, str(missing_snapshot_root), "--allow-checker-simulation"])
            require(errors, missing_snapshot_proc.returncode != 0, "import audit must reject import receipts without copied_handoff_snapshot")
            require(errors, "copied_handoff_snapshot" in missing_snapshot_proc.stderr, "missing copied snapshot rejection should name copied_handoff_snapshot")

            tampered_snapshot_root = tmp / "tampered-copied-snapshot-imports"
            shutil.copytree(import_root, tampered_snapshot_root)
            tampered_snapshot_import = next(tampered_snapshot_root.iterdir())
            tampered_snapshot_json = load_json(tampered_snapshot_import / contract.IMPORT_RECEIPT_NAME)
            tampered_snapshot_json["copied_handoff_snapshot"]["canonical_sha256"] = "sha256:" + "0" * 64
            write_pretty_json(tampered_snapshot_import / contract.IMPORT_RECEIPT_NAME, tampered_snapshot_json)
            tampered_snapshot_proc = run_tool([AUDIT_REL, str(tampered_snapshot_root), "--allow-checker-simulation"])
            require(errors, tampered_snapshot_proc.returncode != 0, "import audit must reject stale copied_handoff_snapshot canonical digests")
            require(errors, "copied_handoff_snapshot.canonical_sha256" in tampered_snapshot_proc.stderr, "tampered copied snapshot rejection should name canonical digest")

            loose_child_root = tmp / "loose-child-imports"
            shutil.copytree(import_root, loose_child_root)
            loose_import = next(loose_child_root.iterdir())
            (loose_import / "loose.json").write_text("{}\n", encoding="utf-8")
            loose_proc = run_tool([AUDIT_REL, str(loose_child_root), "--allow-checker-simulation"])
            require(errors, loose_proc.returncode != 0, "import audit must reject loose files inside import directories")
            require(errors, "must contain exactly" in loose_proc.stderr, "loose-file rejection should name finite import directory contract")

            loose_root = tmp / "loose-root-imports"
            shutil.copytree(import_root, loose_root)
            (loose_root / "bundle-copy.json").write_text("{}\n", encoding="utf-8")
            loose_root_proc = run_tool([AUDIT_REL, str(loose_root), "--allow-checker-simulation"])
            require(errors, loose_root_proc.returncode != 0, "import audit must reject loose files at import root")
            require(errors, "may contain only import directories" in loose_root_proc.stderr, "loose-root rejection should name import-root directory-only contract")

        empty = run_tool([AUDIT_REL, str(tmp / "no-imports-yet")])
        require(errors, empty.returncode == 0, f"missing import root should pass as no imports yet: {empty.stdout} {empty.stderr}")
    return errors


def surface_errors() -> list[str]:
    errors: list[str] = []
    for rel in [AUDIT_REL, IMPORT_REL, contract.HOST_PROOF_CONTRACT_REL]:
        require(errors, (ROOT / rel).exists(), f"missing {rel}")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, "HOST_PROOF_IMPORT_AUDITOR_REL" in contract_text, "shared contract must name import auditor")
    require(errors, AUDIT_REL in contract_text, "shared proof-tool path set must include import auditor")
    importer_text = (ROOT / IMPORT_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        "import_file_rows",
        "copied_handoff_snapshot",
        "HANDOFF_ALLOWED_NAMES",
        "contract.handoff_file_rows",
        "contract.copied_handoff_snapshot",
        "import_receipt_enumerates_all_imported_handoff_files",
        "import_directory_name_binds_full_copied_handoff_snapshot_canonical_digest",
        "contract.import_directory_name",
        "source_transport",
        "copy_policy",
        "durable_write_policy",
        "DIRECTORY_IMPORT_COPY_POLICY",
        "IMPORT_DURABLE_WRITE_POLICY",
    ]:
        require(errors, token in importer_text, f"importer missing import-audit token {token!r}")
    auditor_text = (ROOT / AUDIT_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["--require-primary-target", "primary-production target tier", "contract.copied_handoff_snapshot"]:
        require(errors, token in auditor_text, f"auditor missing import-audit token {token!r}")
    doc = (ROOT / DOC_REL).read_text(encoding="utf-8", errors="replace")
    for token in [AUDIT_REL, "import audit", f"exactly {len(contract.REQUIRED_PROOF_TOOL_PATHS)} tool digest rows", "import_receipt_enumerates_all_imported_handoff_files", "full copied handoff snapshot canonical digest", "source transport", "nofollow staging copy policy", "copied_handoff_snapshot", "primary-production target tier"]:
        require(errors, token in doc, f"{DOC_REL} missing import-audit token {token!r}")
    return errors


def main() -> int:
    errors = audit_mode_errors() + surface_errors()
    if errors:
        print("FreeBSD host proof import audit check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof import audit check OK")
    print("Import roots are rescanned after import; checker-simulation imports remain explicit non-proof and copied handoff files are fully enumerated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
