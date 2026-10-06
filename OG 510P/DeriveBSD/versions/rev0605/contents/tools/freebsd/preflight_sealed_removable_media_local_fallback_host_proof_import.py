#!/usr/bin/env python3
"""Preflight a sealed FreeBSD host-proof handoff before publishing an import.

This command is deliberately not an importer. It snapshots the returned ZIP,
validates/unseals it through the same strict handoff path, copies the finite
handoff through the same nofollow staging copier used by import, predicts the
full-digest import directory name, and exits nonzero if the archive is not ready
for the default real-proof import path; it can also verify a matching existing
digest import for idempotent operator retries.

Default mode accepts only real-host proof. ``--allow-checker-simulation`` exists
only for release-critical Linux mechanics.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cube_digest_lib import canonical_digest, load_json_strict_text, pretty_json_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import audit_removable_media_local_fallback_host_proof_imports as import_auditor  # noqa: E402
import import_removable_media_local_fallback_host_proof_handoff as handoff_importer  # noqa: E402
import unseal_removable_media_local_fallback_host_proof_handoff as handoff_unsealer  # noqa: E402
import verify_removable_media_local_fallback_host_proof_handoff as handoff_verifier  # noqa: E402

DEFAULT_IMPORT_ROOT = ROOT / contract.DEFAULT_IMPORT_ROOT_REL
PREFLIGHT_KIND = "removable.media.local.freebsd.host.proof.sealed_import.preflight"
PREFLIGHT_SCHEMA_VERSION = "0.1"
STATUS_READY_PRIMARY = "ready-to-import-primary-real-host-proof"
STATUS_READY_LEGACY = "ready-to-import-supported-legacy-real-host-proof"
STATUS_READY_CHECKER = "ready-to-import-checker-simulation-non-proof"
STATUS_BLOCKED = "blocked-sealed-handoff-not-ready-for-import"
STATUS_REUSE_PRIMARY = "ready-to-reuse-existing-primary-real-host-proof-import"
STATUS_REUSE_LEGACY = "ready-to-reuse-existing-supported-legacy-real-host-proof-import"
STATUS_REUSE_CHECKER = "ready-to-reuse-existing-checker-simulation-non-proof-import"


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    value = load_json_strict_text(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} root must be a JSON object")
    return value


def _summary_target(receipt: dict[str, Any], bundle: dict[str, Any]) -> tuple[str, str]:
    receipt_summary = _dict(bundle.get("receipt"))
    receipt_host = _dict(receipt.get("host"))
    receipt_host_smoke = _dict(receipt.get("host_smoke"))
    tier = str(receipt_summary.get("host_target_tier") or receipt_host.get("host_target_tier") or "unknown")
    matrix = str(receipt_summary.get("host_target_matrix_id") or receipt_host_smoke.get("host_target_matrix_id") or "unknown")
    return tier, matrix


def _status(proof_status: str, host_target_tier: str, errors: list[str], *, existing_import_reuse_ready: bool = False) -> str:
    if errors:
        return STATUS_BLOCKED
    if existing_import_reuse_ready and proof_status == "checker-simulation-non-proof":
        return STATUS_REUSE_CHECKER
    if existing_import_reuse_ready and proof_status == "real-host-proof" and host_target_tier == contract.HOST_TARGET_PRIMARY_TIER:
        return STATUS_REUSE_PRIMARY
    if existing_import_reuse_ready and proof_status == "real-host-proof" and host_target_tier == contract.HOST_TARGET_LEGACY_TIER:
        return STATUS_REUSE_LEGACY
    if proof_status == "checker-simulation-non-proof":
        return STATUS_READY_CHECKER
    if proof_status == "real-host-proof" and host_target_tier == contract.HOST_TARGET_PRIMARY_TIER:
        return STATUS_READY_PRIMARY
    if proof_status == "real-host-proof" and host_target_tier == contract.HOST_TARGET_LEGACY_TIER:
        return STATUS_READY_LEGACY
    return STATUS_BLOCKED


def _existing_import_reuse_errors(
    import_dir: Path,
    *,
    import_root: Path,
    copied_snapshot: dict[str, Any],
    archive_digest: str,
    archive_size: int,
    allow_checker_simulation: bool,
    require_primary_target: bool,
) -> list[str]:
    errors = import_auditor.validate_import_dir(
        import_dir,
        import_root=import_root,
        allow_checker_simulation=allow_checker_simulation,
        require_primary_target=require_primary_target,
    )
    if errors:
        return ["existing import is not audit-clean for reuse: " + "; ".join(errors[:10])]
    record = _load_json(import_dir / contract.IMPORT_RECEIPT_NAME)
    if record.get("copied_handoff_snapshot") != copied_snapshot:
        errors.append("existing import copied_handoff_snapshot does not match this sealed archive")
    transport = _dict(record.get("source_transport"))
    if transport.get("kind") != contract.SEALED_IMPORT_SOURCE_KIND:
        errors.append("existing import was not produced from a sealed handoff archive")
    if transport.get("byte_sha256") != archive_digest:
        errors.append("existing sealed import archive digest does not match this archive")
    if transport.get("archive_size_bytes") != archive_size:
        errors.append("existing sealed import archive size does not match this archive")
    snapshot = _dict(transport.get("archive_snapshot"))
    if snapshot.get("byte_sha256") != archive_digest or snapshot.get("archive_size_bytes") != archive_size:
        errors.append("existing sealed import archive snapshot does not match this archive")
    return errors


def preflight_sealed_handoff(
    archive: Path,
    *,
    import_root: Path,
    allow_checker_simulation: bool = False,
    require_primary_target: bool = False,
    allow_existing_import: bool = False,
    reuse_existing_import: bool = False,
) -> dict[str, Any]:
    """Return a deterministic readiness report without publishing an import."""
    checked_import_root = handoff_importer._checked_import_root(import_root)  # noqa: SLF001 - same proof-lane command family
    checked_archive = handoff_unsealer._checked_archive_path(archive)  # noqa: SLF001 - same proof-lane command family
    scratch_parent = Path(tempfile.mkdtemp(prefix=f".{checked_import_root.name}.sealed-handoff-preflight-", dir=checked_import_root.parent))
    try:
        archive_snapshot_path = scratch_parent / "source-archive.snapshot.zip"
        archive_snapshot = handoff_unsealer.copy_archive_snapshot(checked_archive, archive_snapshot_path)
        archive_snapshot_file = archive_snapshot.get("path")
        if not isinstance(archive_snapshot_file, Path):
            raise TypeError("archive snapshot path must be a Path")
        archive_errors = handoff_unsealer._archive_errors(archive_snapshot_file)  # noqa: SLF001 - same proof-lane validation primitive
        if archive_errors:
            raise ValueError("sealed handoff archive validation failed: " + "; ".join(archive_errors[:10]))

        unsealed_handoff = scratch_parent / "unsealed-handoff"
        handoff_unsealer.unseal_archive(
            archive_snapshot_file,
            output_dir=unsealed_handoff,
            allow_checker_simulation=allow_checker_simulation,
            replace=False,
        )
        verify_errors = handoff_verifier.validate_handoff_dir(
            unsealed_handoff,
            allow_checker_simulation=allow_checker_simulation,
        )
        if verify_errors:
            raise ValueError("unsealed handoff verification failed: " + "; ".join(verify_errors[:10]))

        copied_handoff = scratch_parent / "copied-handoff"
        handoff_importer.copy_handoff(unsealed_handoff, copied_handoff)
        copied_errors = handoff_verifier.validate_handoff_dir(
            copied_handoff,
            allow_checker_simulation=allow_checker_simulation,
        )
        if copied_errors:
            raise ValueError("preflight copied handoff verification failed: " + "; ".join(copied_errors[:10]))

        receipt = _load_json(copied_handoff / contract.RECEIPT_NAME)
        bundle = _load_json(copied_handoff / contract.BUNDLE_NAME)
        copied_snapshot = contract.copied_handoff_snapshot(copied_handoff)
        proof_status = str(bundle.get("proof_status") or "unknown")
        host_target_tier, host_target_matrix_id = _summary_target(receipt, bundle)
        predicted_import_dir = checked_import_root / contract.import_directory_name(proof_status, str(copied_snapshot["canonical_sha256"]))

        errors: list[str] = []
        if proof_status != "real-host-proof" and not allow_checker_simulation:
            errors.append("default sealed import preflight accepts only real-host-proof")
        if require_primary_target and host_target_tier != contract.HOST_TARGET_PRIMARY_TIER:
            errors.append(f"preflight requires primary target tier {contract.HOST_TARGET_PRIMARY_TIER}, observed {host_target_tier}")
        existing_import_reuse_errors: list[str] = []
        existing_import_reuse_ready = False
        if predicted_import_dir.exists():
            if reuse_existing_import:
                existing_import_reuse_errors = _existing_import_reuse_errors(
                    predicted_import_dir,
                    import_root=checked_import_root,
                    copied_snapshot=copied_snapshot,
                    archive_digest=str(archive_snapshot.get("byte_sha256")),
                    archive_size=int(archive_snapshot.get("archive_size_bytes") or 0),
                    allow_checker_simulation=allow_checker_simulation,
                    require_primary_target=require_primary_target,
                )
                existing_import_reuse_ready = not existing_import_reuse_errors
                errors.extend(existing_import_reuse_errors)
            elif not allow_existing_import:
                errors.append(f"predicted import directory already exists: {_rel_or_abs(predicted_import_dir)}")
        if host_target_matrix_id != contract.HOST_TARGET_MATRIX_ID:
            errors.append(f"host_target_matrix_id mismatch: {host_target_matrix_id} != {contract.HOST_TARGET_MATRIX_ID}")

        report_core: dict[str, Any] = {
            "kind": PREFLIGHT_KIND,
            "schema_version": PREFLIGHT_SCHEMA_VERSION,
            "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
            "preflight_policy": contract.SEALED_IMPORT_PREFLIGHT_POLICY,
            "sealed_import_policy": contract.SEALED_IMPORT_POLICY,
            "archive_snapshot_policy": contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY,
            "canonical_zip_metadata_policy": contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY,
            "directory_import_copy_policy": contract.DIRECTORY_IMPORT_COPY_POLICY,
            "import_directory_digest_policy": contract.IMPORT_DIRECTORY_DIGEST_POLICY,
            "archive": {
                "path": _rel_or_abs(checked_archive),
                "byte_sha256": archive_snapshot.get("byte_sha256"),
                "archive_size_bytes": archive_snapshot.get("archive_size_bytes"),
            },
            "import_root": _rel_or_abs(checked_import_root),
            "predicted_import_dir": _rel_or_abs(predicted_import_dir),
            "predicted_import_dir_exists": predicted_import_dir.exists(),
            "proof_status": proof_status,
            "host_target_tier": host_target_tier,
            "host_target_matrix_id": host_target_matrix_id,
            "require_primary_target": require_primary_target,
            "allow_checker_simulation": allow_checker_simulation,
            "allow_existing_import": allow_existing_import,
            "reuse_existing_import": reuse_existing_import,
            "existing_import_reuse_ready": existing_import_reuse_ready,
            "existing_import_reuse_policy": contract.SEALED_IMPORT_EXISTING_REUSE_POLICY,
            "receipt": {
                "canonical_sha256": canonical_digest(receipt),
                "byte_sha256": contract.sha256_file(copied_handoff / contract.RECEIPT_NAME),
                "smoke_id": receipt.get("smoke_id"),
                "result": receipt.get("result"),
                "cube_cut_version": receipt.get("cube_cut_version"),
            },
            "bundle": {
                "canonical_sha256": canonical_digest(bundle),
                "byte_sha256": contract.sha256_file(copied_handoff / contract.BUNDLE_NAME),
                "bundle_id": bundle.get("bundle_id"),
                "cube_cut_version": bundle.get("cube_cut_version"),
                "proof_status": proof_status,
            },
            "copied_handoff_snapshot": copied_snapshot,
            "preflight_ready": not errors,
            "status": _status(proof_status, host_target_tier, errors, existing_import_reuse_ready=existing_import_reuse_ready),
            "errors": errors,
            "invariants": {
                "does_not_publish_import": True,
                "archive_snapshot_taken_before_zip_validation": True,
                "canonical_zip_metadata_validated_before_unseal": True,
                "handoff_verified_before_import_prediction": True,
                "handoff_copied_through_importer_nofollow_staging_path": True,
                "predicted_import_dir_uses_full_copied_handoff_snapshot_digest": True,
                "primary_target_can_be_required_before_publish": require_primary_target,
                "existing_import_reuse_requires_audit_clean_matching_archive_digest": reuse_existing_import,
            },
        }
        return {**report_core, "report_canonical_sha256": canonical_digest(report_core)}
    finally:
        if scratch_parent.exists():
            shutil.rmtree(scratch_parent)


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "FreeBSD sealed host-proof import preflight",
        f"generated_for_version={report.get('generated_for_version')}",
        f"status={report.get('status')}",
        f"preflight_ready={str(report.get('preflight_ready')).lower()}",
        f"proof_status={report.get('proof_status')}",
        f"host_target_tier={report.get('host_target_tier')}",
        f"host_target_matrix_id={report.get('host_target_matrix_id')}",
        f"archive_sha256={(report.get('archive') or {}).get('byte_sha256') if isinstance(report.get('archive'), dict) else None}",
        f"predicted_import_dir={report.get('predicted_import_dir')}",
        f"predicted_import_dir_exists={str(report.get('predicted_import_dir_exists')).lower()}",
        f"reuse_existing_import={str(report.get('reuse_existing_import')).lower()}",
        f"existing_import_reuse_ready={str(report.get('existing_import_reuse_ready')).lower()}",
        f"report_canonical_sha256={report.get('report_canonical_sha256')}",
    ]
    errors = report.get("errors") if isinstance(report.get("errors"), list) else []
    for error in errors:
        lines.append(f"error={error}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="preflight a sealed host-proof ZIP without publishing an import")
    parser.add_argument("archive", type=Path, help="sealed handoff ZIP archive")
    parser.add_argument("--import-root", type=Path, default=DEFAULT_IMPORT_ROOT, help="import root to check for predicted import collisions")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="accept checker-simulation archives for release-critical tests only")
    parser.add_argument("--require-primary-target", action="store_true", help="fail unless the handoff records the primary-production target tier")
    parser.add_argument("--allow-existing-import", action="store_true", help="do not fail when the predicted digest import already exists")
    parser.add_argument("--reuse-existing-import", action="store_true", help="allow an existing predicted import only if it is audit-clean and matches this sealed archive digest")
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = preflight_sealed_handoff(
            args.archive,
            import_root=args.import_root,
            allow_checker_simulation=args.allow_checker_simulation,
            require_primary_target=args.require_primary_target,
            allow_existing_import=args.allow_existing_import,
            reuse_existing_import=args.reuse_existing_import,
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing preflight command
        if args.json:
            sys.stdout.write(pretty_json_text({
                "kind": PREFLIGHT_KIND,
                "schema_version": PREFLIGHT_SCHEMA_VERSION,
                "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
                "preflight_ready": False,
                "status": STATUS_BLOCKED,
                "errors": [str(exc)],
            }))
        else:
            print("host-proof sealed import preflight FAILED", file=sys.stderr)
            print(f"- {exc}", file=sys.stderr)
        return 1
    if args.json:
        sys.stdout.write(pretty_json_text(report))
    else:
        sys.stdout.write(render_text(report))
    return 0 if report.get("preflight_ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
