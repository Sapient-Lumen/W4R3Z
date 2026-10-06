#!/usr/bin/env python3
"""Import a deterministic sealed FreeBSD host-proof handoff archive.

This is the cloudtainer-side one-command path for a scarce real FreeBSD proof
that arrives as a sealed ZIP.  It does not create a new proof source: the command
validates the archive, unseals into a private temporary directory, verifies the
handoff, imports through the normal full-digest importer, audits the import root,
removes the temporary unsealed handoff, and can deliberately reuse an already-published matching digest import after audit.

default mode accepts only strict ``real-host-proof``.  Checker simulations require
``--allow-checker-simulation`` and are only for release-critical Linux mechanics.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import os
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

from cube_digest_lib import load_json_strict_text, pretty_json_text  # noqa: E402
import audit_removable_media_local_fallback_host_proof_imports as import_auditor  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import import_removable_media_local_fallback_host_proof_handoff as handoff_importer  # noqa: E402
import unseal_removable_media_local_fallback_host_proof_handoff as handoff_unsealer  # noqa: E402

DEFAULT_IMPORT_ROOT = ROOT / contract.DEFAULT_IMPORT_ROOT_REL
SEALED_IMPORT_POLICY = contract.SEALED_IMPORT_POLICY
DIRECTORY_IMPORT_COPY_POLICY = contract.DIRECTORY_IMPORT_COPY_POLICY
IMPORT_DURABLE_WRITE_POLICY = contract.IMPORT_DURABLE_WRITE_POLICY
SEALED_IMPORT_PRIMARY_TARGET_POLICY = contract.SEALED_IMPORT_PRIMARY_TARGET_POLICY
SEALED_IMPORT_FAILURE_CLEANUP_POLICY = contract.SEALED_IMPORT_FAILURE_CLEANUP_POLICY
SEALED_IMPORT_EXISTING_REUSE_POLICY = contract.SEALED_IMPORT_EXISTING_REUSE_POLICY
SEALED_IMPORT_LOCK_POLICY = contract.SEALED_IMPORT_LOCK_POLICY


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _load_json(path: Path) -> dict[str, Any]:
    value = load_json_strict_text(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} root must be a JSON object")
    return value


def _summary_target(receipt: dict[str, Any], bundle: dict[str, Any]) -> tuple[str, str, str]:
    receipt_summary = _dict(bundle.get("receipt"))
    receipt_host = _dict(receipt.get("host"))
    receipt_host_smoke = _dict(receipt.get("host_smoke"))
    proof_status = str(bundle.get("proof_status") or "unknown")
    tier = str(receipt_summary.get("host_target_tier") or receipt_host.get("host_target_tier") or "unknown")
    matrix = str(receipt_summary.get("host_target_matrix_id") or receipt_host_smoke.get("host_target_matrix_id") or "unknown")
    return proof_status, tier, matrix


def _enforce_primary_target(handoff_dir: Path) -> None:
    """Fail before publish unless the unsealed handoff is primary-production proof."""
    receipt = _load_json(handoff_dir / contract.RECEIPT_NAME)
    bundle = _load_json(handoff_dir / contract.BUNDLE_NAME)
    proof_status, host_target_tier, host_target_matrix_id = _summary_target(receipt, bundle)
    if proof_status != "real-host-proof":
        raise ValueError(f"primary-target sealed import requires real-host-proof, observed {proof_status}")
    if host_target_matrix_id != contract.HOST_TARGET_MATRIX_ID:
        raise ValueError(f"primary-target sealed import requires host target matrix {contract.HOST_TARGET_MATRIX_ID}, observed {host_target_matrix_id}")
    if host_target_tier != contract.HOST_TARGET_PRIMARY_TIER:
        raise ValueError(f"primary-target sealed import requires {contract.HOST_TARGET_PRIMARY_TIER}, observed {host_target_tier}")


def _cleanup_new_failed_import(import_dir: Path, import_root: Path) -> None:
    """Remove only the just-published digest directory after a failed clean-root audit."""
    if import_dir.parent.resolve() != import_root.resolve():
        raise ValueError(f"refusing failed-import cleanup outside import root: {import_dir}")
    if import_dir.is_symlink() or not import_dir.is_dir():
        raise ValueError(f"refusing failed-import cleanup for non-directory import path: {import_dir}")
    shutil.rmtree(import_dir)
    handoff_importer._fsync_dir(import_root)  # noqa: SLF001 - shared durable import primitive


def _reuse_existing_import_if_matching_archive(
    import_dir: Path,
    *,
    import_root: Path,
    copied_snapshot: dict[str, Any],
    archive_digest: str,
    archive_size: int,
    allow_checker_simulation: bool,
    require_primary_target: bool,
) -> None:
    """Verify an existing digest import before treating a rerun as success.

    This is intentionally not a replacement path.  It is only for operator
    interruption/retry after the same sealed archive was already imported.
    """
    errors = import_auditor.validate_import_dir(
        import_dir,
        import_root=import_root,
        allow_checker_simulation=allow_checker_simulation,
        require_primary_target=require_primary_target,
    )
    if errors:
        raise ValueError("existing import is not audit-clean for sealed reuse: " + "; ".join(errors[:10]))
    record = _load_json(import_dir / contract.IMPORT_RECEIPT_NAME)
    if record.get("copied_handoff_snapshot") != copied_snapshot:
        raise ValueError("existing import snapshot does not match the returned sealed archive handoff")
    transport = _dict(record.get("source_transport"))
    if transport.get("kind") != contract.SEALED_IMPORT_SOURCE_KIND:
        raise ValueError("existing import was not created from a sealed handoff archive; refusing sealed-import reuse")
    if transport.get("byte_sha256") != archive_digest:
        raise ValueError("existing sealed import archive digest does not match this returned archive")
    if transport.get("archive_size_bytes") != archive_size:
        raise ValueError("existing sealed import archive size does not match this returned archive")
    snapshot = _dict(transport.get("archive_snapshot"))
    if snapshot.get("byte_sha256") != archive_digest or snapshot.get("archive_size_bytes") != archive_size:
        raise ValueError("existing sealed import archive snapshot does not match this returned archive")


def _sealed_import_lock_path(import_root: Path) -> Path:
    """Return the sibling lock path used to serialize sealed import publish work."""
    return import_root.parent / f".{import_root.name}.sealed-import.lock"


@contextmanager
def _sealed_import_lock(import_root: Path):
    """Hold an exclusive sibling lock while publish/reuse decisions are made.

    The lock deliberately lives beside the checked import root, not inside it, so
    the import-root auditor never mistakes lock state for proof evidence.  It is
    acquired with mkdir for process-safe exclusivity and removed in the normal
    cleanup path.  A remaining lock is treated as an interrupted import that must
    be investigated before scarce proof is retried.
    """
    lock_path = _sealed_import_lock_path(import_root)
    try:
        os.mkdir(lock_path, 0o700)
    except FileExistsError as exc:
        raise FileExistsError(
            f"active sealed import lock already exists: {lock_path}; another import may be running or a prior import was interrupted after lock acquisition"
        ) from exc
    owner = {
        "kind": "removable.media.local.freebsd.host.proof.sealed_import.lock",
        "schema_version": "0.1",
        "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
        "lock_policy": contract.SEALED_IMPORT_LOCK_POLICY,
        "import_root": _rel_or_abs(import_root),
        "lock_path": _rel_or_abs(lock_path),
        "pid": os.getpid(),
    }
    try:
        (lock_path / "lock.json").write_text(pretty_json_text(owner), encoding="utf-8")
        handoff_importer._fsync_dir(lock_path)  # noqa: SLF001 - shared durable import primitive
        handoff_importer._fsync_dir(lock_path.parent)  # noqa: SLF001 - shared durable import primitive
        yield lock_path
    finally:
        if lock_path.exists() or lock_path.is_symlink():
            if lock_path.is_symlink() or not lock_path.is_dir():
                raise ValueError(f"sealed import lock path was replaced during import: {lock_path}")
            shutil.rmtree(lock_path)
            handoff_importer._fsync_dir(lock_path.parent)  # noqa: SLF001 - shared durable import primitive

def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def import_sealed_handoff(
    archive: Path,
    *,
    import_root: Path,
    allow_checker_simulation: bool = False,
    replace: bool = False,
    keep_unsealed_temp: bool = False,
    require_primary_target: bool = False,
    keep_failed_import: bool = False,
    reuse_existing_import: bool = False,
) -> Path:
    """Unseal, import, and audit one sealed host-proof handoff archive.

    The temporary directory is created beside the checked import root so the
    post-import audit never sees scratch state as evidence.  A sibling lock
    serializes publish/reuse/replace decisions across concurrent operator
    sessions.  The normal unsealer still performs deterministic ZIP validation
    and strict handoff verification; the normal importer still performs
    full-digest atomic publish.
    """
    checked_import_root = handoff_importer._checked_import_root(import_root)  # noqa: SLF001 - same proof-lane command family
    checked_archive = handoff_unsealer._checked_archive_path(archive)  # noqa: SLF001 - same proof-lane command family
    if reuse_existing_import and replace:
        raise ValueError("--reuse-existing-import and --replace are mutually exclusive")
    with _sealed_import_lock(checked_import_root) as lock_path:
        scratch_parent = Path(tempfile.mkdtemp(prefix=f".{checked_import_root.name}.sealed-handoff-import-", dir=checked_import_root.parent))
        try:
            archive_snapshot = scratch_parent / "source-archive.snapshot.zip"
            snapshot_info = handoff_unsealer.copy_archive_snapshot(checked_archive, archive_snapshot)
            archive_digest = str(snapshot_info["byte_sha256"])
            archive_size = int(snapshot_info["archive_size_bytes"])
            unsealed_handoff = scratch_parent / "handoff"
            scratch_cleanup = "retained-by-operator-request" if keep_unsealed_temp else "removed-after-import-or-failure"
            source_transport = {
                "kind": contract.SEALED_IMPORT_SOURCE_KIND,
                "path": _rel_or_abs(checked_archive),
                "byte_sha256": archive_digest,
                "archive_format": contract.HANDOFF_ARCHIVE_FORMAT,
                "archive_size_bytes": archive_size,
                "sealed_import_policy": contract.SEALED_IMPORT_POLICY,
                "sealed_import_lock_policy": contract.SEALED_IMPORT_LOCK_POLICY,
                "sealed_import_lock_path": _rel_or_abs(lock_path),
                "canonical_zip_metadata_policy": contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY,
                "transport_policy": contract.IMPORT_RECEIPT_SOURCE_TRANSPORT_POLICY,
                "archive_snapshot": {
                    "kind": contract.HANDOFF_ARCHIVE_SNAPSHOT_KIND,
                    "snapshot_policy": contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY,
                    "canonical_zip_metadata_policy": contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY,
                    "byte_sha256": archive_digest,
                    "archive_size_bytes": archive_size,
                    "source_path": _rel_or_abs(checked_archive),
                    "cleanup": scratch_cleanup,
                },
                "unsealed_scratch_parent": _rel_or_abs(scratch_parent),
                "unsealed_scratch_handoff": _rel_or_abs(unsealed_handoff),
                "scratch_cleanup": scratch_cleanup,
            }
            handoff_unsealer.unseal_archive(
                archive_snapshot,
                output_dir=unsealed_handoff,
                allow_checker_simulation=allow_checker_simulation,
                replace=False,
            )
            if require_primary_target:
                _enforce_primary_target(unsealed_handoff)
            receipt = _load_json(unsealed_handoff / contract.RECEIPT_NAME)
            bundle = _load_json(unsealed_handoff / contract.BUNDLE_NAME)
            copied_snapshot = contract.copied_handoff_snapshot(unsealed_handoff)
            proof_status = str(bundle.get("proof_status") or "unknown")
            predicted_import_dir = checked_import_root / contract.import_directory_name(proof_status, str(copied_snapshot["canonical_sha256"]))
            if predicted_import_dir.exists() and not replace:
                if not reuse_existing_import:
                    raise FileExistsError(f"import directory already exists: {predicted_import_dir}; pass --reuse-existing-import for an idempotent retry or --replace only for deliberate re-import")
                _reuse_existing_import_if_matching_archive(
                    predicted_import_dir,
                    import_root=checked_import_root,
                    copied_snapshot=copied_snapshot,
                    archive_digest=archive_digest,
                    archive_size=archive_size,
                    allow_checker_simulation=allow_checker_simulation,
                    require_primary_target=require_primary_target,
                )
                return predicted_import_dir
            pre_audit_errors = import_auditor.audit_import_root(
                checked_import_root,
                allow_checker_simulation=allow_checker_simulation,
                require_primary_target=require_primary_target,
            )
            if pre_audit_errors:
                raise ValueError("pre-import audit failed; refusing to publish into dirty import root: " + "; ".join(pre_audit_errors[:10]))
            import_dir = handoff_importer.import_handoff(
                unsealed_handoff,
                import_root=checked_import_root,
                allow_checker_simulation=allow_checker_simulation,
                replace=replace,
                source_transport=source_transport,
            )
            audit_errors = import_auditor.audit_import_root(
                checked_import_root,
                allow_checker_simulation=allow_checker_simulation,
                require_primary_target=require_primary_target,
            )
            if audit_errors:
                if not keep_failed_import and not replace:
                    _cleanup_new_failed_import(import_dir, checked_import_root)
                    raise ValueError("post-import audit failed; removed newly published import per failed-import cleanup policy: " + "; ".join(audit_errors[:10]))
                raise ValueError("post-import audit failed; import retained for forensics: " + "; ".join(audit_errors[:10]))
            return import_dir
        finally:
            if not keep_unsealed_temp and scratch_parent.exists():
                shutil.rmtree(scratch_parent)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="unseal, import, and audit a deterministic host-proof handoff ZIP archive")
    parser.add_argument("archive", type=Path, help="sealed handoff ZIP archive")
    parser.add_argument("--import-root", type=Path, default=DEFAULT_IMPORT_ROOT, help="directory under which the full-digest import directory is created")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="import checker-simulation-non-proof archives for release-critical tests only")
    parser.add_argument("--replace", action="store_true", help="replace an existing full-digest import directory after successful unseal/import/audit staging")
    parser.add_argument("--keep-unsealed-temp", action="store_true", help="retain the temporary unsealed handoff directory for failure forensics")
    parser.add_argument("--require-primary-target", action="store_true", help="fail before publish unless the sealed handoff is primary-production real-host proof")
    parser.add_argument("--keep-failed-import", action="store_true", help="retain a newly published import if the post-import audit fails")
    parser.add_argument("--reuse-existing-import", action="store_true", help="treat an existing matching sealed digest import as success after audit instead of replacing it")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        import_dir = import_sealed_handoff(
            args.archive,
            import_root=args.import_root,
            allow_checker_simulation=args.allow_checker_simulation,
            replace=args.replace,
            keep_unsealed_temp=args.keep_unsealed_temp,
            require_primary_target=args.require_primary_target,
            keep_failed_import=args.keep_failed_import,
            reuse_existing_import=args.reuse_existing_import,
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing sealed import command
        print("host-proof sealed handoff import FAILED", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return 1
    print("host-proof sealed handoff import OK")
    print(f"sealed_import_policy={SEALED_IMPORT_POLICY}")
    print(f"directory_import_copy_policy={DIRECTORY_IMPORT_COPY_POLICY}")
    print(f"import_durable_write_policy={IMPORT_DURABLE_WRITE_POLICY}")
    print(f"archive_snapshot_policy={contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY}")
    print(f"primary_target_policy={SEALED_IMPORT_PRIMARY_TARGET_POLICY}")
    print(f"failed_import_cleanup_policy={SEALED_IMPORT_FAILURE_CLEANUP_POLICY}")
    print(f"existing_import_reuse_policy={SEALED_IMPORT_EXISTING_REUSE_POLICY}")
    print(f"sealed_import_lock_policy={SEALED_IMPORT_LOCK_POLICY}")
    print(f"reuse_existing_import_requested={str(args.reuse_existing_import).lower()}")
    print(f"canonical_zip_metadata_policy={contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY}")
    print(f"archive_sha256:{sha256_file(args.archive)}")
    print(f"import_dir={import_dir}")
    print(f"import_receipt={import_dir / contract.IMPORT_RECEIPT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
