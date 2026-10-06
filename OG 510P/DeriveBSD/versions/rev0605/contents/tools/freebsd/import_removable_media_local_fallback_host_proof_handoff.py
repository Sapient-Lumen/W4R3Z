#!/usr/bin/env python3
"""Import a verified FreeBSD host-proof handoff into a finite cube directory.

Default mode accepts only strict real-host proof.  The importer first runs the
handoff verifier, then copies the finite handoff into a digest-named import
directory and writes an import receipt beside the copied handoff.  Checker
simulations require an explicit non-proof flag and should only be used by the
Linux release-critical checker.
"""
from __future__ import annotations

import argparse
import errno
import os
import shutil
import stat
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
import verify_removable_media_local_fallback_host_proof_handoff as handoff_verifier  # noqa: E402

DEFAULT_IMPORT_ROOT = ROOT / contract.DEFAULT_IMPORT_ROOT_REL
# Surface alias: copied_handoff_snapshot() delegates this policy to the shared contract.
IMPORT_RECEIPT_SNAPSHOT_POLICY = contract.IMPORT_RECEIPT_SNAPSHOT_POLICY


def sha256_file(path: Path) -> str:
    return contract.sha256_file(path)


def _load_json(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _fsync_dir(path: Path) -> None:
    """Fsync a real directory so scarce proof imports survive a crash boundary."""
    fd = os.open(path, _dir_open_flags())
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_pretty_json_durable(path: Path, obj: dict[str, Any]) -> None:
    """Write deterministic JSON and fsync the file plus containing directory."""
    data = pretty_json_text(obj).encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags | nofollow, 0o644)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise
    os.chmod(path, contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0o777)
    _fsync_dir(path.parent)


def _checked_handoff_source(source: Path) -> Path:
    """Return a real source handoff directory without following a final symlink."""
    raw_source = source.expanduser()
    contract.require_no_existing_symlink_component(raw_source, "handoff directory")
    if raw_source.is_symlink():
        raise ValueError(f"handoff directory must not be a symlink: {raw_source}")
    if not raw_source.exists():
        raise FileNotFoundError(f"handoff directory does not exist: {raw_source}")
    if not raw_source.is_dir():
        raise ValueError(f"handoff path is not a directory: {raw_source}")
    return raw_source.resolve()


def _checked_import_root(import_root: Path) -> Path:
    """Create/return a real import root without following a final symlink."""
    raw_root = import_root.expanduser()
    contract.require_no_existing_symlink_component(raw_root, "import root")
    if raw_root.is_symlink():
        raise ValueError(f"import root is not a real directory: {raw_root}")
    raw_parent = raw_root.parent
    raw_parent.mkdir(parents=True, exist_ok=True)
    contract.require_no_existing_symlink_component(raw_root, "import root")
    if raw_parent.is_symlink() or not raw_parent.is_dir():
        raise ValueError(f"import root parent is not a real directory: {raw_parent}")
    checked = raw_parent.resolve() / raw_root.name
    if checked.is_symlink():
        raise ValueError(f"import root is not a real directory: {checked}")
    checked.mkdir(parents=True, exist_ok=True)
    if not checked.is_dir():
        raise ValueError(f"import root is not a real directory: {checked}")
    return checked


def _dir_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    return flags


def _file_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _same_regular_file(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        stat.S_ISREG(before.st_mode)
        and stat.S_ISREG(after.st_mode)
        and before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and before.st_size == after.st_size
    )


def _copy_regular_member_from_dirfd(source_fd: int, source_dir: Path, name: str, destination: Path) -> bool:
    """Copy one finite handoff member without following source symlinks.

    The importer has already verified the handoff directory, but loose removable
    media paths are still mutable.  Copy through a directory file descriptor,
    reject symlinks/non-regular files with ``O_NOFOLLOW`` where available, bound
    member size, and write into a fresh staging path with exclusive creation.
    """
    try:
        before = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"handoff member must be a regular file without symlink: {source_dir / name}")
    if before.st_size > contract.MAX_HANDOFF_MEMBER_BYTES:
        raise ValueError(f"handoff member exceeds finite copy limit: {source_dir / name}")

    try:
        in_fd = os.open(name, _file_open_flags(), dir_fd=source_fd)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError(f"handoff member must not be a symlink: {source_dir / name}") from exc
        raise
    try:
        after_open = os.fstat(in_fd)
        if not _same_regular_file(before, after_open):
            raise ValueError(f"handoff member changed before copy: {source_dir / name}")
        out_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        out_fd = os.open(destination, out_flags, contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE)
        copied = 0
        try:
            while True:
                chunk = os.read(in_fd, 1024 * 1024)
                if not chunk:
                    break
                copied += len(chunk)
                if copied > contract.MAX_HANDOFF_MEMBER_BYTES:
                    raise ValueError(f"handoff member exceeds finite copy limit while reading: {source_dir / name}")
                os.write(out_fd, chunk)
            os.fsync(out_fd)
        finally:
            os.close(out_fd)
        after_read = os.fstat(in_fd)
        if not _same_regular_file(after_open, after_read) or copied != after_read.st_size:
            raise ValueError(f"handoff member changed during copy: {source_dir / name}")
        os.chmod(destination, contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0o777)
        return True
    finally:
        os.close(in_fd)


def copy_handoff(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    source_fd = os.open(source, _dir_open_flags())
    try:
        for name in sorted(contract.HANDOFF_ALLOWED_NAMES):
            _copy_regular_member_from_dirfd(source_fd, source, name, destination / name)
    finally:
        os.close(source_fd)
    _fsync_dir(destination)
    _fsync_dir(destination.parent)


def _remove_tree_if_present(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_dir():
            path.unlink()
        else:
            shutil.rmtree(path)


def _atomic_publish_import(staging_dir: Path, import_dir: Path, *, replace: bool) -> None:
    """Publish a fully verified staging directory to the digest-named path.

    A real host run is scarce evidence.  The importer must therefore avoid
    leaving half-copied final import directories and must not delete an existing
    digest import until a complete replacement is ready to publish.
    """
    backup_dir: Path | None = None
    if import_dir.exists() or import_dir.is_symlink():
        if not replace:
            raise FileExistsError(f"import directory already exists: {import_dir}; pass --replace only for a deliberate re-import")
        if import_dir.is_symlink() or not import_dir.is_dir():
            raise ValueError(f"existing import path is not a directory: {import_dir}")
        backup_dir = import_dir.with_name(f".{import_dir.name}.replace-backup-{os.getpid()}")
        if backup_dir.exists() or backup_dir.is_symlink():
            raise FileExistsError(f"stale import replacement backup already exists: {backup_dir}")
    try:
        if backup_dir is not None:
            os.replace(import_dir, backup_dir)
        os.replace(staging_dir, import_dir)
    except Exception:
        if backup_dir is not None and backup_dir.exists() and not import_dir.exists():
            os.replace(backup_dir, import_dir)
        raise
    else:
        _fsync_dir(import_dir.parent)
        if backup_dir is not None and backup_dir.exists():
            shutil.rmtree(backup_dir)
            _fsync_dir(import_dir.parent)


def import_file_rows(imported_handoff: Path) -> list[dict[str, str]]:
    return contract.handoff_file_rows(imported_handoff)


def copied_handoff_snapshot(imported_handoff: Path) -> dict[str, Any]:
    """Return the shared digest-bound manifest for the copied handoff snapshot."""
    return contract.copied_handoff_snapshot(imported_handoff)


def directory_source_transport(source_handoff: Path, copied_handoff: Path) -> dict[str, Any]:
    """Return durable provenance for a direct directory handoff import.

    The path records where the operator pointed the importer.  The digest is
    intentionally computed from the copied, reverified staging snapshot instead
    of the mutable source directory, so the durable receipt binds the imported
    bytes rather than a source that may be edited after import.
    """
    return {
        "kind": contract.DIRECTORY_IMPORT_SOURCE_KIND,
        "path": _rel_or_abs(source_handoff),
        "sha256sums_byte_sha256": sha256_file(copied_handoff / contract.SUMS_NAME),
        "transport_policy": contract.IMPORT_RECEIPT_SOURCE_TRANSPORT_POLICY,
    }


def build_import_receipt(
    *,
    source_handoff: Path,
    imported_root: Path,
    imported_handoff: Path,
    digest_handoff: Path,
    receipt: dict[str, Any],
    bundle: dict[str, Any],
    allow_checker_simulation: bool,
    copied_snapshot: dict[str, Any],
    source_transport: dict[str, Any] | None = None,
) -> dict[str, Any]:
    proof_status = str(bundle.get("proof_status"))
    transport = source_transport or directory_source_transport(source_handoff, digest_handoff)
    transport_kind = str(transport.get("kind"))
    receipt_path = digest_handoff / contract.RECEIPT_NAME
    bundle_path = digest_handoff / contract.BUNDLE_NAME
    receipt_summary = _dict(bundle.get("receipt"))
    receipt_host = _dict(receipt.get("host"))
    receipt_host_smoke = _dict(receipt.get("host_smoke"))
    return {
        "kind": contract.IMPORT_RECEIPT_KIND,
        "schema_version": contract.IMPORT_RECEIPT_SCHEMA_VERSION,
        "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
        "cube_cut_version": contract.CURRENT_CUBE_CUT_VERSION,
        "import_status": "checker-simulation-non-proof-import" if allow_checker_simulation else "real-host-proof-import",
        "proof_status": proof_status,
        "source_handoff_dir": _rel_or_abs(source_handoff),
        "source_transport": transport,
        "import_root": _rel_or_abs(imported_root),
        "imported_handoff_dir": _rel_or_abs(imported_handoff),
        "receipt": {
            "byte_sha256": sha256_file(receipt_path),
            "canonical_sha256": canonical_digest(receipt),
            "kind": receipt.get("kind"),
            "schema_version": receipt.get("schema_version"),
            "smoke_id": receipt.get("smoke_id"),
            "generated_for_version": receipt.get("generated_for_version"),
            "runner_contract_version": receipt.get("runner_contract_version"),
            "cube_cut_version": receipt.get("cube_cut_version"),
            "generated_at_utc": receipt.get("generated_at_utc"),
            "result": receipt.get("result"),
            "host_target_matrix_id": receipt_summary.get("host_target_matrix_id") or receipt_host_smoke.get("host_target_matrix_id"),
            "host_target_tier": receipt_summary.get("host_target_tier") or receipt_host.get("host_target_tier"),
            "host_probe_observed_system": receipt_host.get("host_probe_observed_system"),
            "host_probe_uname_release": receipt_host.get("host_probe_uname_release"),
            "host_probe_uname_machine": receipt_host.get("host_probe_uname_machine"),
            "host_probe_osreldate": receipt_host.get("host_probe_osreldate"),
            "host_probe_effective_uid": receipt_host.get("host_probe_effective_uid"),
            "checker_only_host_command_simulation": receipt_summary.get("checker_only_host_command_simulation"),
        },
        "bundle": {
            "byte_sha256": sha256_file(bundle_path),
            "canonical_sha256": canonical_digest(bundle),
            "bundle_id": bundle.get("bundle_id"),
            "generated_for_version": bundle.get("generated_for_version"),
            "cube_cut_version": bundle.get("cube_cut_version"),
            "proof_status": proof_status,
            "host_target_matrix_id": receipt_summary.get("host_target_matrix_id") or receipt_host_smoke.get("host_target_matrix_id"),
            "host_target_tier": receipt_summary.get("host_target_tier") or receipt_host.get("host_target_tier"),
        },
        "copied_handoff_snapshot": copied_snapshot,
        "files": import_file_rows(digest_handoff),
        "copy_policy": contract.DIRECTORY_IMPORT_COPY_POLICY,
        "identity_policy": contract.IMPORT_STAGED_IDENTITY_POLICY,
        "durable_write_policy": contract.IMPORT_DURABLE_WRITE_POLICY,
        "atomic_publish_policy": "copy-verify-fsync-write-receipt-fsync-then-rename-and-fsync-parent-to-full-digest-import-dir",
        "invariants": {
            "handoff_verified_before_copy": True,
            "handoff_reverified_after_copy": True,
            "default_import_accepts_only_real_host_proof": not allow_checker_simulation,
            "checker_simulation_import_requires_explicit_flag": allow_checker_simulation == (proof_status == "checker-simulation-non-proof"),
            "import_directory_name_binds_full_copied_handoff_snapshot_canonical_digest": True,
            "import_preserves_finite_handoff_subdirectory": True,
            "import_receipt_enumerates_all_imported_handoff_files": True,
            "import_copied_to_staging_before_publish": True,
            "import_receipt_written_before_publish": True,
            "import_published_by_atomic_rename_after_reverification": True,
            "failed_import_keeps_existing_digest_import_until_publish": True,
            "import_receipt_binds_source_transport": True,
            "directory_import_copies_allowed_regular_files_without_following_symlinks": True,
            "import_receipt_binds_copied_snapshot_not_mutable_source": True,
            "import_receipt_binds_copied_snapshot_manifest_digest": True,
            "import_directory_identity_derived_from_reverified_copied_snapshot": True,
            "import_receipt_summaries_loaded_from_reverified_copied_snapshot": True,
            "import_receipt_preserves_host_target_tier": True,
            "import_receipt_preserves_host_probe_binding_fields": True,
            "staged_files_and_import_receipt_fsynced_before_publish": True,
            "import_parent_directory_fsynced_after_publish": True,
            "sealed_import_receipt_binds_archive_digest": transport_kind == contract.SEALED_IMPORT_SOURCE_KIND,
            "sealed_import_receipt_binds_copied_archive_snapshot": transport_kind == contract.SEALED_IMPORT_SOURCE_KIND,
            "sealed_import_archive_snapshot_taken_before_zip_validation": transport_kind == contract.SEALED_IMPORT_SOURCE_KIND,
            "sealed_import_rejects_noncanonical_zip_metadata": transport_kind == contract.SEALED_IMPORT_SOURCE_KIND,
            "directory_import_receipt_binds_source_handoff": transport_kind == contract.DIRECTORY_IMPORT_SOURCE_KIND,
        },
    }


def import_handoff(
    source: Path,
    *,
    import_root: Path,
    allow_checker_simulation: bool = False,
    replace: bool = False,
    source_transport: dict[str, Any] | None = None,
) -> Path:
    source = _checked_handoff_source(source)
    errors = handoff_verifier.validate_handoff_dir(source, allow_checker_simulation=allow_checker_simulation)
    if errors:
        raise ValueError("handoff verification failed before import: " + "; ".join(errors[:10]))

    import_root = _checked_import_root(import_root)

    # Removable-media source directories are mutable.  The final import identity
    # must therefore be computed from the copied and reverified snapshot, not
    # from JSON read out of the source before the copy boundary.
    staging_dir = Path(tempfile.mkdtemp(prefix=".host-proof-import.staging-", dir=import_root))
    import_dir: Path | None = None
    final_handoff: Path | None = None
    try:
        staging_handoff = staging_dir / "handoff"
        copy_handoff(source, staging_handoff)

        post_errors = handoff_verifier.validate_handoff_dir(staging_handoff, allow_checker_simulation=allow_checker_simulation)
        if post_errors:
            raise ValueError("copied handoff verification failed: " + "; ".join(post_errors[:10]))

        receipt = _load_json(staging_handoff / contract.RECEIPT_NAME)
        bundle = _load_json(staging_handoff / contract.BUNDLE_NAME)
        if not isinstance(receipt, dict):
            raise ValueError("copied receipt.json root must be a JSON object")
        if not isinstance(bundle, dict):
            raise ValueError("copied bundle.json root must be a JSON object")

        copied_snapshot = copied_handoff_snapshot(staging_handoff)
        proof_status = str(bundle.get("proof_status"))
        snapshot_canonical = copied_snapshot["canonical_sha256"]
        import_dir = import_root / contract.import_directory_name(proof_status, snapshot_canonical)
        final_handoff = import_dir / "handoff"
        if import_dir.exists() and not replace:
            raise FileExistsError(f"import directory already exists: {import_dir}; pass --replace only for a deliberate re-import")

        import_receipt = build_import_receipt(
            source_handoff=source,
            imported_root=import_root,
            imported_handoff=final_handoff,
            digest_handoff=staging_handoff,
            receipt=receipt,
            bundle=bundle,
            allow_checker_simulation=allow_checker_simulation,
            copied_snapshot=copied_snapshot,
            source_transport=source_transport,
        )
        _write_pretty_json_durable(staging_dir / contract.IMPORT_RECEIPT_NAME, import_receipt)
        _atomic_publish_import(staging_dir, import_dir, replace=replace)
    except Exception:
        _remove_tree_if_present(staging_dir)
        raise

    if import_dir is None or final_handoff is None:
        raise RuntimeError("import identity was not derived from the copied handoff snapshot")
    final_errors = handoff_verifier.validate_handoff_dir(final_handoff, allow_checker_simulation=allow_checker_simulation)
    if final_errors:
        raise ValueError("published handoff verification failed: " + "; ".join(final_errors[:10]))
    return import_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff_dir", type=Path, help="directory containing receipt.json, bundle.json, and SHA256SUMS")
    parser.add_argument("--import-root", type=Path, default=DEFAULT_IMPORT_ROOT, help="directory under which a digest-named import directory is created")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="import checker-simulation-non-proof handoff for release-critical tests only")
    parser.add_argument("--replace", action="store_true", help="replace an existing digest-named import directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        import_dir = import_handoff(
            args.handoff_dir,
            import_root=args.import_root,
            allow_checker_simulation=args.allow_checker_simulation,
            replace=args.replace,
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing import command
        print("host-proof handoff import FAILED", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return 1
    print("host-proof handoff import OK")
    print(f"import_dir={import_dir}")
    print(f"import_receipt={import_dir / contract.IMPORT_RECEIPT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
