#!/usr/bin/env python3
"""Audit imported FreeBSD removable-media host-proof handoff directories.

The importer makes a finite digest-named directory.  This audit scans an import
root after the fact and refuses loose files, stale import receipts, digest-name
mismatches, and checker-simulation imports unless a caller passes the explicit
non-proof flag used by release-critical Linux tests.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cube_digest_lib import CanonicalJsonError, canonical_digest, load_json_strict_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import verify_removable_media_local_fallback_host_proof_handoff as handoff_verifier  # noqa: E402

DEFAULT_IMPORT_ROOT = ROOT / contract.DEFAULT_IMPORT_ROOT_REL


def sha256_file(path: Path) -> str:
    return contract.sha256_file(path)


def _load_json(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _list(obj: Any) -> list[Any]:
    return obj if isinstance(obj, list) else []


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _expected_handoff_file_rows(handoff: Path) -> dict[str, str]:
    return {row["path"]: row["sha256"] for row in contract.handoff_file_rows(handoff)}


def _expected_copied_handoff_snapshot(handoff: Path) -> dict[str, Any]:
    return contract.copied_handoff_snapshot(handoff)


def _snapshot_errors(record: dict[str, Any], handoff: Path) -> list[str]:
    errors: list[str] = []
    observed = _dict(record.get("copied_handoff_snapshot"))
    expected = _expected_copied_handoff_snapshot(handoff)
    if not observed:
        return ["import receipt must bind copied_handoff_snapshot manifest"]
    for key in ["kind", "snapshot_policy", "file_count", "total_size_bytes", "files", "canonical_sha256"]:
        _require(errors, observed.get(key) == expected.get(key), f"copied_handoff_snapshot.{key} must match imported handoff snapshot")
    return errors


def _receipt_file_rows(record: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    rows: dict[str, str] = {}
    for idx, row in enumerate(_list(record.get("files"))):
        if not isinstance(row, dict):
            errors.append(f"files[{idx}] must be an object")
            continue
        rel = row.get("path")
        digest = row.get("sha256")
        if not isinstance(rel, str) or not rel.startswith("handoff/"):
            errors.append(f"files[{idx}].path must be a handoff-relative path")
            continue
        if rel in rows:
            errors.append(f"duplicate import receipt file row for {rel}")
            continue
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            errors.append(f"files[{idx}].sha256 must be a sha256 digest")
            continue
        rows[rel] = digest
    return rows, errors


def _is_sha256_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value.removeprefix("sha256:")) == 64
        and all(ch in "0123456789abcdef" for ch in value.removeprefix("sha256:"))
    )


def _source_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def _source_transport_errors(record: dict[str, Any], imported_handoff: Path) -> list[str]:
    errors: list[str] = []
    transport = _dict(record.get("source_transport"))
    if not transport:
        return ["import receipt must bind source_transport provenance"]
    kind = transport.get("kind")
    _require(errors, kind in {contract.DIRECTORY_IMPORT_SOURCE_KIND, contract.SEALED_IMPORT_SOURCE_KIND}, "source_transport.kind must be a supported source kind")
    _require(errors, transport.get("transport_policy") == contract.IMPORT_RECEIPT_SOURCE_TRANSPORT_POLICY, "source_transport must bind the source transport policy")
    source_path_text = transport.get("path")
    _require(errors, isinstance(source_path_text, str) and bool(source_path_text), "source_transport.path must be a non-empty string")

    if kind == contract.DIRECTORY_IMPORT_SOURCE_KIND:
        _require(errors, transport.get("path") == record.get("source_handoff_dir"), "directory source_transport.path must match source_handoff_dir")
        _require(errors, transport.get("sha256sums_byte_sha256") == sha256_file(imported_handoff / contract.SUMS_NAME), "directory source_transport must bind SHA256SUMS bytes")
    elif kind == contract.SEALED_IMPORT_SOURCE_KIND:
        _require(errors, _is_sha256_digest(transport.get("byte_sha256")), "sealed source_transport.byte_sha256 must be a sha256 digest")
        _require(errors, transport.get("archive_format") == contract.HANDOFF_ARCHIVE_FORMAT, "sealed source_transport must bind the handoff archive format")
        archive_size = transport.get("archive_size_bytes")
        _require(errors, isinstance(archive_size, int) and 0 < archive_size <= contract.MAX_HANDOFF_ARCHIVE_BYTES, "sealed source_transport archive_size_bytes must be finite")
        _require(errors, transport.get("sealed_import_policy") == contract.SEALED_IMPORT_POLICY, "sealed source_transport must bind the sealed import policy")
        _require(errors, transport.get("sealed_import_lock_policy") == contract.SEALED_IMPORT_LOCK_POLICY, "sealed source_transport must bind the sealed import lock policy")
        _require(errors, isinstance(transport.get("sealed_import_lock_path"), str) and ".sealed-import.lock" in transport.get("sealed_import_lock_path", ""), "sealed source_transport must bind the sibling lock path used during publish")
        _require(errors, transport.get("canonical_zip_metadata_policy") == contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY, "sealed source_transport must bind the canonical ZIP metadata policy")
        _require(errors, transport.get("unsealed_scratch_handoff") == record.get("source_handoff_dir"), "sealed source_transport scratch handoff must match source_handoff_dir")
        _require(errors, transport.get("scratch_cleanup") in {"removed-after-import-or-failure", "retained-by-operator-request"}, "sealed source_transport must state scratch cleanup behavior")
        snapshot = _dict(transport.get("archive_snapshot"))
        _require(errors, snapshot.get("kind") == contract.HANDOFF_ARCHIVE_SNAPSHOT_KIND, "sealed source_transport archive_snapshot.kind must bind the snapshot kind")
        _require(errors, snapshot.get("snapshot_policy") == contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY, "sealed source_transport archive_snapshot must bind the nofollow archive snapshot policy")
        _require(errors, snapshot.get("canonical_zip_metadata_policy") == contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY, "sealed source_transport archive_snapshot must bind the canonical ZIP metadata policy")
        _require(errors, snapshot.get("byte_sha256") == transport.get("byte_sha256"), "sealed source_transport byte_sha256 must equal archive snapshot digest")
        _require(errors, snapshot.get("archive_size_bytes") == archive_size, "sealed source_transport archive_size_bytes must equal archive snapshot size")
        _require(errors, snapshot.get("source_path") == source_path_text, "sealed source_transport archive_snapshot.source_path must match source path")
        _require(errors, snapshot.get("cleanup") == transport.get("scratch_cleanup"), "sealed source_transport archive_snapshot cleanup must match scratch cleanup")
    return errors


def _primary_target_errors(record: dict[str, Any], proof_status: str, *, require_primary_target: bool) -> list[str]:
    """Reject checked-in real host proof that is not from the primary target tier."""
    if not require_primary_target or proof_status != "real-host-proof":
        return []
    errors: list[str] = []
    receipt_summary = _dict(record.get("receipt"))
    bundle_summary = _dict(record.get("bundle"))
    for label, summary in [("receipt", receipt_summary), ("bundle", bundle_summary)]:
        _require(
            errors,
            summary.get("host_target_matrix_id") == contract.HOST_TARGET_MATRIX_ID,
            f"primary-target audit {label} summary must bind current host target matrix id",
        )
        _require(
            errors,
            summary.get("host_target_tier") == contract.HOST_TARGET_PRIMARY_TIER,
            f"checked-in real-host-proof must be from primary-production target tier in {label} summary",
        )
    invariants = _dict(record.get("invariants"))
    _require(errors, invariants.get("import_receipt_preserves_host_target_tier") is True, "primary-target audit requires preserved host target tier evidence")
    return errors


def validate_import_dir(import_dir: Path, *, import_root: Path, allow_checker_simulation: bool = False, require_primary_target: bool = False) -> list[str]:
    errors: list[str] = []
    if not import_dir.exists():
        return [f"import directory does not exist: {import_dir}"]
    if import_dir.is_symlink():
        return [f"import directory must not be a symlink: {import_dir}"]
    if not import_dir.is_dir():
        return [f"import path is not a directory: {import_dir}"]

    names = {child.name for child in import_dir.iterdir()}
    expected_names = {"handoff", contract.IMPORT_RECEIPT_NAME}
    _require(errors, names == expected_names, f"import directory must contain exactly {sorted(expected_names)!r}, observed {sorted(names)!r}")

    handoff = import_dir / "handoff"
    import_receipt_path = import_dir / contract.IMPORT_RECEIPT_NAME
    if handoff.is_symlink():
        errors.append("handoff subdirectory must not be a symlink")
    if not handoff.is_dir():
        errors.append("handoff must be a directory")
    if import_receipt_path.is_symlink():
        errors.append(f"{contract.IMPORT_RECEIPT_NAME} must not be a symlink")
    if not import_receipt_path.is_file():
        errors.append(f"{contract.IMPORT_RECEIPT_NAME} must be a regular file")
    if errors:
        return errors

    try:
        record = _load_json(import_receipt_path)
    except (OSError, CanonicalJsonError) as exc:
        return [f"import receipt strict JSON load failed: {exc}"]
    if not isinstance(record, dict):
        return ["import receipt root must be a JSON object"]

    try:
        receipt = _load_json(handoff / contract.RECEIPT_NAME)
        bundle = _load_json(handoff / contract.BUNDLE_NAME)
    except (OSError, CanonicalJsonError) as exc:
        return [f"handoff JSON strict load failed: {exc}"]
    if not isinstance(receipt, dict) or not isinstance(bundle, dict):
        return ["handoff receipt.json and bundle.json must be JSON objects"]

    proof_status = str(bundle.get("proof_status"))
    expected_import_status = "checker-simulation-non-proof-import" if proof_status == "checker-simulation-non-proof" else "real-host-proof-import"
    if allow_checker_simulation:
        _require(errors, proof_status in {"real-host-proof", "checker-simulation-non-proof"}, "allowed audit accepts only known proof statuses")
    else:
        _require(errors, proof_status == "real-host-proof", "default import audit accepts only real-host-proof imports")

    _require(errors, record.get("kind") == contract.IMPORT_RECEIPT_KIND, "wrong import receipt kind")
    _require(errors, record.get("schema_version") == contract.IMPORT_RECEIPT_SCHEMA_VERSION, "wrong import receipt schema_version")
    _require(errors, record.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "import receipt generated_for_version must bind current cube cut")
    _require(errors, record.get("cube_cut_version") == contract.CURRENT_CUBE_CUT_VERSION, "import receipt cube_cut_version must bind current cube cut")
    _require(errors, record.get("proof_status") == proof_status, "import receipt proof_status must match bundle")
    _require(errors, record.get("import_status") == expected_import_status, "import receipt import_status must match proof_status")
    _require(errors, record.get("import_root") == _rel_or_abs(import_root), "import receipt import_root must match audited root")
    _require(errors, record.get("imported_handoff_dir") == _rel_or_abs(handoff), "import receipt imported_handoff_dir must match audited handoff")
    errors.extend(_source_transport_errors(record, handoff))

    receipt_summary = _dict(record.get("receipt"))
    bundle_summary = _dict(record.get("bundle"))
    _require(errors, receipt_summary.get("byte_sha256") == sha256_file(handoff / contract.RECEIPT_NAME), "import receipt must bind receipt.json bytes")
    _require(errors, receipt_summary.get("canonical_sha256") == canonical_digest(receipt), "import receipt must bind receipt.json canonical digest")
    _require(errors, receipt_summary.get("kind") == receipt.get("kind"), "import receipt kind summary must match receipt.json")
    _require(errors, receipt_summary.get("schema_version") == receipt.get("schema_version"), "import receipt schema_version summary must match receipt.json")
    _require(errors, receipt_summary.get("smoke_id") == receipt.get("smoke_id"), "import receipt smoke_id summary must match receipt.json")
    _require(errors, receipt_summary.get("generated_for_version") == receipt.get("generated_for_version"), "import receipt generated_for_version summary must match receipt.json")
    _require(errors, receipt_summary.get("runner_contract_version") == receipt.get("runner_contract_version"), "import receipt runner_contract_version summary must match receipt.json")
    _require(errors, receipt_summary.get("cube_cut_version") == receipt.get("cube_cut_version"), "import receipt cube_cut_version summary must match receipt.json")
    _require(errors, receipt_summary.get("generated_at_utc") == receipt.get("generated_at_utc"), "import receipt generated_at_utc summary must match receipt.json")
    _require(errors, receipt_summary.get("result") == receipt.get("result"), "import receipt result summary must match receipt.json")
    receipt_host = _dict(receipt.get("host"))
    receipt_host_smoke = _dict(receipt.get("host_smoke"))
    bundle_receipt_summary = _dict(bundle.get("receipt"))
    _require(errors, receipt_summary.get("host_target_matrix_id") == receipt_host_smoke.get("host_target_matrix_id"), "import receipt host_target_matrix_id summary must match receipt.json")
    _require(errors, receipt_summary.get("host_target_tier") == receipt_host.get("host_target_tier"), "import receipt host_target_tier summary must match receipt.json")
    for key in [
        "host_probe_observed_system",
        "host_probe_uname_release",
        "host_probe_uname_machine",
        "host_probe_osreldate",
        "host_probe_effective_uid",
    ]:
        _require(errors, receipt_summary.get(key) == receipt_host.get(key), f"import receipt {key} summary must match receipt.json host")

    _require(errors, bundle_summary.get("byte_sha256") == sha256_file(handoff / contract.BUNDLE_NAME), "import receipt must bind bundle.json bytes")
    _require(errors, bundle_summary.get("canonical_sha256") == canonical_digest(bundle), "import receipt must bind bundle.json canonical digest")
    _require(errors, bundle_summary.get("bundle_id") == bundle.get("bundle_id"), "import receipt bundle_id summary must match bundle.json")
    _require(errors, bundle_summary.get("generated_for_version") == bundle.get("generated_for_version"), "import receipt bundle generated_for_version summary must match bundle.json")
    _require(errors, bundle_summary.get("cube_cut_version") == bundle.get("cube_cut_version"), "import receipt bundle cube_cut_version summary must match bundle.json")
    _require(errors, bundle_summary.get("proof_status") == proof_status, "import receipt bundle proof_status summary must match bundle.json")
    _require(errors, bundle_summary.get("host_target_matrix_id") == bundle_receipt_summary.get("host_target_matrix_id"), "import receipt bundle host_target_matrix_id summary must match bundle.json")
    _require(errors, bundle_summary.get("host_target_tier") == bundle_receipt_summary.get("host_target_tier"), "import receipt bundle host_target_tier summary must match bundle.json")
    invariants = _dict(record.get("invariants"))
    _require(errors, invariants.get("import_receipt_preserves_host_target_tier") is True, "import receipt must assert host target tier preservation")
    _require(errors, invariants.get("import_receipt_preserves_host_probe_binding_fields") is True, "import receipt must assert host probe binding field preservation")
    errors.extend(_primary_target_errors(record, proof_status, require_primary_target=require_primary_target))

    snapshot = _dict(record.get("copied_handoff_snapshot"))
    snapshot_digest = snapshot.get("canonical_sha256")
    if isinstance(snapshot_digest, str):
        try:
            expected_name = contract.import_directory_name(proof_status, snapshot_digest)
        except ValueError as exc:
            errors.append(f"copied_handoff_snapshot canonical digest is not usable as import identity: {exc}")
        else:
            _require(errors, import_dir.name == expected_name, "import directory name must bind proof status and full copied handoff snapshot canonical digest")
    else:
        errors.append("copied_handoff_snapshot.canonical_sha256 must be present before import directory identity check")

    actual_rows = _expected_handoff_file_rows(handoff)
    recorded_rows, row_errors = _receipt_file_rows(record)
    errors.extend(row_errors)
    _require(errors, recorded_rows == actual_rows, "import receipt files list must enumerate every imported handoff file and digest exactly")
    errors.extend(_snapshot_errors(record, handoff))

    _require(errors, record.get("copy_policy") == contract.DIRECTORY_IMPORT_COPY_POLICY, "import receipt must bind the nofollow staging copy policy")
    _require(errors, record.get("identity_policy") == contract.IMPORT_STAGED_IDENTITY_POLICY, "import receipt must bind staged snapshot identity policy")
    _require(errors, record.get("durable_write_policy") == contract.IMPORT_DURABLE_WRITE_POLICY, "import receipt must bind the durable fsync write policy")
    _require(
        errors,
        record.get("atomic_publish_policy") == "copy-verify-fsync-write-receipt-fsync-then-rename-and-fsync-parent-to-full-digest-import-dir",
        "import receipt must bind the staging/fsync/rename atomic publish policy",
    )

    invariants = _dict(record.get("invariants"))
    required_true = {
        "handoff_verified_before_copy",
        "handoff_reverified_after_copy",
        "checker_simulation_import_requires_explicit_flag",
        "import_directory_name_binds_full_copied_handoff_snapshot_canonical_digest",
        "import_preserves_finite_handoff_subdirectory",
        "import_receipt_enumerates_all_imported_handoff_files",
        "import_copied_to_staging_before_publish",
        "import_receipt_written_before_publish",
        "import_published_by_atomic_rename_after_reverification",
        "failed_import_keeps_existing_digest_import_until_publish",
        "import_receipt_binds_source_transport",
        "directory_import_copies_allowed_regular_files_without_following_symlinks",
        "import_receipt_binds_copied_snapshot_not_mutable_source",
        "import_receipt_binds_copied_snapshot_manifest_digest",
        "import_directory_identity_derived_from_reverified_copied_snapshot",
        "import_receipt_summaries_loaded_from_reverified_copied_snapshot",
        "import_receipt_preserves_host_probe_binding_fields",
        "staged_files_and_import_receipt_fsynced_before_publish",
        "import_parent_directory_fsynced_after_publish",
    }
    for key in sorted(required_true):
        _require(errors, invariants.get(key) is True, f"import invariant {key} must be true")
    if proof_status == "real-host-proof":
        _require(errors, invariants.get("default_import_accepts_only_real_host_proof") is True, "real proof import must use default real-proof mode")
    else:
        _require(errors, invariants.get("default_import_accepts_only_real_host_proof") is False, "checker simulation import must not claim default real-proof mode")

    source_kind = _dict(record.get("source_transport")).get("kind")
    if source_kind == contract.SEALED_IMPORT_SOURCE_KIND:
        _require(errors, invariants.get("sealed_import_receipt_binds_archive_digest") is True, "sealed import receipt must assert archive digest provenance")
        _require(errors, invariants.get("sealed_import_receipt_binds_copied_archive_snapshot") is True, "sealed import receipt must assert copied archive snapshot provenance")
        _require(errors, invariants.get("sealed_import_archive_snapshot_taken_before_zip_validation") is True, "sealed import receipt must assert archive snapshot before ZIP validation")
        _require(errors, invariants.get("sealed_import_rejects_noncanonical_zip_metadata") is True, "sealed import receipt must assert noncanonical ZIP metadata rejection")
        _require(errors, _dict(record.get("source_transport")).get("sealed_import_lock_policy") == contract.SEALED_IMPORT_LOCK_POLICY, "sealed import receipt must bind exclusive import lock policy")
        _require(errors, invariants.get("directory_import_receipt_binds_source_handoff") is False, "sealed import receipt must not claim direct directory provenance")
    elif source_kind == contract.DIRECTORY_IMPORT_SOURCE_KIND:
        _require(errors, invariants.get("directory_import_receipt_binds_source_handoff") is True, "directory import receipt must assert handoff directory provenance")
        _require(errors, invariants.get("sealed_import_receipt_binds_archive_digest") is False, "directory import receipt must not claim sealed archive provenance")
        _require(errors, invariants.get("sealed_import_receipt_binds_copied_archive_snapshot") is False, "directory import receipt must not claim sealed archive snapshot provenance")
        _require(errors, invariants.get("sealed_import_archive_snapshot_taken_before_zip_validation") is False, "directory import receipt must not claim sealed archive snapshot timing")
        _require(errors, invariants.get("sealed_import_rejects_noncanonical_zip_metadata") is False, "directory import receipt must not claim sealed ZIP metadata validation")

    errors.extend(handoff_verifier.validate_handoff_dir(handoff, allow_checker_simulation=allow_checker_simulation and proof_status == "checker-simulation-non-proof"))
    return errors


def audit_import_root(import_root: Path, *, allow_checker_simulation: bool = False, require_primary_target: bool = False) -> list[str]:
    errors: list[str] = []
    if not import_root.exists():
        return []
    if import_root.is_symlink():
        return [f"import root must not be a symlink: {import_root}"]
    if not import_root.is_dir():
        return [f"import root is not a directory: {import_root}"]
    for child in sorted(import_root.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.is_symlink():
            errors.append(f"import root may contain only import directories, got {child.name!r}")
            continue
        child_errors = validate_import_dir(
            child,
            import_root=import_root,
            allow_checker_simulation=allow_checker_simulation,
            require_primary_target=require_primary_target,
        )
        for error in child_errors:
            errors.append(f"{child.name}: {error}")
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("import_root", nargs="?", type=Path, default=DEFAULT_IMPORT_ROOT, help="directory containing digest-named imported host-proof handoffs")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="accept checker-simulation imports for release-critical tests only")
    parser.add_argument("--require-primary-target", action="store_true", help="for checked-in release evidence, reject real-host-proof imports unless host_target_tier is primary-production")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    errors = audit_import_root(
        args.import_root,
        allow_checker_simulation=args.allow_checker_simulation,
        require_primary_target=args.require_primary_target,
    )
    if errors:
        print("host-proof import audit FAILED:", file=sys.stderr)
        for error in errors[:40]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > 40:
            print(f"- ... {len(errors) - 40} more errors", file=sys.stderr)
        return 1
    print("host-proof import audit OK")
    print(f"import_root={args.import_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
