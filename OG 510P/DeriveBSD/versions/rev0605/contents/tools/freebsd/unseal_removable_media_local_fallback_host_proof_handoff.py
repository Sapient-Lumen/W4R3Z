#!/usr/bin/env python3
"""Safely unseal a deterministic FreeBSD host-proof handoff ZIP archive.

The sealed ZIP is only transport.  This command first snapshots the source
archive through a bounded nofollow regular-file copy, validates only that
snapshot, extracts only finite handoff filenames into a fresh directory, and
then runs the normal handoff verifier before publishing the directory for import.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import os
import stat
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import host_proof_contract as contract  # noqa: E402
import verify_removable_media_local_fallback_host_proof_handoff as handoff_verifier  # noqa: E402

ALLOWED_NAMES = set(contract.HANDOFF_ALLOWED_NAMES)
REQUIRED_NAMES = set(contract.HANDOFF_REQUIRED_NAMES)
FIXED_ZIP_DATE = contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE
FIXED_FILE_MODE = contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE
MAX_MEMBER_BYTES = contract.MAX_HANDOFF_MEMBER_BYTES
MAX_ARCHIVE_BYTES = contract.MAX_HANDOFF_ARCHIVE_BYTES


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


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


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, _dir_open_flags())
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _same_regular_file(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        stat.S_ISREG(before.st_mode)
        and stat.S_ISREG(after.st_mode)
        and before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and before.st_size == after.st_size
    )


def _archive_errors(path: Path) -> list[str]:
    errors: list[str] = []
    if path.is_symlink():
        return [f"handoff archive must be a regular file, not symlink or directory: {path}"]
    if not path.exists():
        return [f"handoff archive does not exist: {path}"]
    if not path.is_file():
        return [f"handoff archive must be a regular file, not symlink or directory: {path}"]
    archive_bytes = path.stat().st_size
    if archive_bytes > MAX_ARCHIVE_BYTES:
        errors.append(f"handoff archive exceeds finite size limit: {archive_bytes} > {MAX_ARCHIVE_BYTES} bytes")
    try:
        with zipfile.ZipFile(path) as zf:
            if zf.comment:
                errors.append("archive comment must be empty for deterministic sealed handoff transport")
            rows = zf.infolist()
    except zipfile.BadZipFile as exc:
        return [f"handoff archive is not a readable ZIP: {exc}"]
    names: list[str] = []
    seen: set[str] = set()
    total_member_bytes = 0
    expected_order = sorted(name for name in ALLOWED_NAMES if name in {row.filename for row in rows})
    observed_order = [row.filename for row in rows if row.filename in ALLOWED_NAMES and not row.filename.endswith("/")]
    if observed_order != expected_order:
        errors.append(f"archive entries must appear in canonical sorted handoff order: observed {observed_order!r} expected {expected_order!r}")
    for row in rows:
        name = row.filename
        if name.endswith("/") or row.is_dir():
            errors.append(f"archive contains directory entry {name!r}")
            continue
        if name not in ALLOWED_NAMES:
            errors.append(f"archive contains unexpected or unsafe filename {name!r}")
            continue
        if name in seen:
            errors.append(f"archive contains duplicate entry for {name!r}")
            continue
        seen.add(name)
        names.append(name)
        if row.flag_bits & 0x1:
            errors.append(f"archive entry {name!r} must not be encrypted")
        if row.compress_type != zipfile.ZIP_STORED:
            errors.append(f"archive entry {name!r} must use stored deterministic ZIP entry")
        if row.create_system != 3:
            errors.append(f"archive entry {name!r} must use Unix create_system metadata")
        if row.extra:
            errors.append(f"archive entry {name!r} must not carry ZIP extra fields")
        if row.comment:
            errors.append(f"archive entry {name!r} must not carry ZIP entry comments")
        if row.date_time != FIXED_ZIP_DATE:
            errors.append(f"archive entry {name!r} must use fixed ZIP timestamp")
        file_mode = (row.external_attr >> 16) & 0o777777
        if file_mode != FIXED_FILE_MODE:
            errors.append(f"archive entry {name!r} must encode exact regular-file mode {oct(FIXED_FILE_MODE)}")
        if row.file_size > MAX_MEMBER_BYTES:
            errors.append(f"archive entry {name!r} exceeds finite member size limit: {row.file_size} > {MAX_MEMBER_BYTES} bytes")
        if row.compress_size > MAX_MEMBER_BYTES:
            errors.append(f"archive entry {name!r} exceeds finite compressed size limit: {row.compress_size} > {MAX_MEMBER_BYTES} bytes")
        total_member_bytes += row.file_size
    if total_member_bytes > MAX_ARCHIVE_BYTES:
        errors.append(f"archive uncompressed handoff payload exceeds finite size limit: {total_member_bytes} > {MAX_ARCHIVE_BYTES} bytes")
    missing = sorted(REQUIRED_NAMES - set(names))
    if missing:
        errors.append(f"archive missing required handoff files: {missing!r}")
    return errors


def _write_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo, destination: Path) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(destination, flags | nofollow, 0o644)
    bytes_written = 0
    try:
        with os.fdopen(fd, "wb") as handle, zf.open(info, "r") as source:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > MAX_MEMBER_BYTES:
                    raise ValueError(f"archive entry {info.filename!r} exceeded finite member size limit while extracting")
                handle.write(chunk)
            if bytes_written != info.file_size:
                raise ValueError(f"archive entry {info.filename!r} size changed while extracting")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            destination.unlink()
        except FileNotFoundError:
            pass
        raise


# reject existing symlink components before host proof work
def _checked_archive_path(archive: Path) -> Path:
    raw_archive = archive.expanduser()
    contract.require_no_existing_symlink_component(raw_archive, "handoff archive")
    if raw_archive.is_symlink():
        raise ValueError(f"handoff archive must be a regular file, not symlink or directory: {raw_archive}")
    if not raw_archive.exists():
        raise FileNotFoundError(f"handoff archive does not exist: {raw_archive}")
    if not raw_archive.is_file():
        raise ValueError(f"handoff archive must be a regular file, not symlink or directory: {raw_archive}")
    return raw_archive.resolve()


def copy_archive_snapshot(source_archive: Path, snapshot_path: Path) -> dict[str, Any]:
    """Copy a sealed archive into a bounded nofollow snapshot before ZIP reads.

    The sealed archive path can be on mutable removable media or a downloaded
    staging area.  Validation and extraction must operate on a copied regular
    file whose identity is checked before open, after open, and after read.
    """
    source = _checked_archive_path(source_archive)
    if snapshot_path.exists() or snapshot_path.is_symlink():
        raise FileExistsError(f"archive snapshot path already exists: {snapshot_path}")
    before = os.stat(source, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"handoff archive snapshot source must be a regular file: {source}")
    if before.st_size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"handoff archive exceeds finite size limit before snapshot: {before.st_size} > {MAX_ARCHIVE_BYTES} bytes")

    try:
        in_fd = os.open(source, _file_open_flags())
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError(f"handoff archive must not be a symlink: {source}") from exc
        raise
    digest = hashlib.sha256()
    copied = 0
    out_fd: int | None = None
    try:
        after_open = os.fstat(in_fd)
        if not _same_regular_file(before, after_open):
            raise ValueError(f"handoff archive changed before snapshot copy: {source}")
        out_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        out_fd = os.open(snapshot_path, out_flags, contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0o777)
        while True:
            chunk = os.read(in_fd, 1024 * 1024)
            if not chunk:
                break
            copied += len(chunk)
            if copied > MAX_ARCHIVE_BYTES:
                raise ValueError(f"handoff archive exceeds finite size limit while snapshotting: {source}")
            digest.update(chunk)
            os.write(out_fd, chunk)
        os.fsync(out_fd)
        after_read = os.fstat(in_fd)
        if not _same_regular_file(after_open, after_read) or copied != after_read.st_size:
            raise ValueError(f"handoff archive changed during snapshot copy: {source}")
    except Exception:
        try:
            snapshot_path.unlink()
        except FileNotFoundError:
            pass
        raise
    finally:
        if out_fd is not None:
            os.close(out_fd)
        os.close(in_fd)
    os.chmod(snapshot_path, contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0o777)
    _fsync_dir(snapshot_path.parent)
    return {
        "kind": contract.HANDOFF_ARCHIVE_SNAPSHOT_KIND,
        "snapshot_policy": contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY,
        "path": snapshot_path,
        "byte_sha256": "sha256:" + digest.hexdigest(),
        "archive_size_bytes": copied,
    }


def _checked_output_dir(output_dir: Path, *, replace: bool) -> Path:
    """Return an absolute output directory path without following a final symlink."""
    raw_output = output_dir.expanduser()
    contract.require_no_existing_symlink_component(raw_output, "handoff output directory")
    if raw_output.is_symlink():
        raise ValueError(f"refusing to replace non-directory or symlink output: {raw_output}")
    raw_parent = raw_output.parent
    raw_parent.mkdir(parents=True, exist_ok=True)
    contract.require_no_existing_symlink_component(raw_output, "handoff output directory")
    if raw_parent.is_symlink() or not raw_parent.is_dir():
        raise ValueError(f"handoff output parent is not a real directory: {raw_parent}")
    checked = raw_parent.resolve() / raw_output.name
    if checked.is_symlink():
        raise ValueError(f"refusing to replace non-directory or symlink output: {checked}")
    if checked.exists():
        if not replace:
            raise FileExistsError(f"handoff output directory already exists: {checked}; pass --replace only for a deliberate rewrite")
        if not checked.is_dir():
            raise ValueError(f"refusing to replace non-directory or symlink output: {checked}")
    return checked


def _atomic_publish_unsealed(staging_dir: Path, output_dir: Path, *, replace: bool) -> None:
    """Publish a verified unsealed handoff without an availability gap.

    A sealed real-host handoff may be the only copy in the cloudtainer.  When
    replacing a previous unsealed directory, keep the old directory in a private
    sibling backup until the staged directory has been atomically published.
    """
    backup_dir: Path | None = None
    if output_dir.exists() or output_dir.is_symlink():
        if not replace:
            raise FileExistsError(f"handoff output directory already exists: {output_dir}; pass --replace only for a deliberate rewrite")
        if output_dir.is_symlink() or not output_dir.is_dir():
            raise ValueError(f"refusing to replace non-directory or symlink output: {output_dir}")
        backup_prefix = f".{output_dir.name}.replace-backup-"
        stale_backups = sorted(child for child in output_dir.parent.iterdir() if child.name.startswith(backup_prefix))
        if stale_backups:
            names = ", ".join(child.name for child in stale_backups[:5])
            raise FileExistsError(f"stale unseal replacement backup already exists: {names}")
        backup_dir = output_dir.with_name(f"{backup_prefix}{os.getpid()}")
    try:
        if backup_dir is not None:
            os.replace(output_dir, backup_dir)
        os.replace(staging_dir, output_dir)
    except Exception:
        if backup_dir is not None and backup_dir.exists() and not output_dir.exists():
            os.replace(backup_dir, output_dir)
        raise
    else:
        _fsync_dir(output_dir.parent)
        if backup_dir is not None and backup_dir.exists():
            shutil.rmtree(backup_dir)
            _fsync_dir(output_dir.parent)


def unseal_archive(
    archive: Path,
    *,
    output_dir: Path,
    allow_checker_simulation: bool = False,
    replace: bool = False,
) -> Path:
    archive = _checked_archive_path(archive)
    output_dir = _checked_output_dir(output_dir, replace=replace)

    work_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.unseal-", dir=output_dir.parent))
    staging = work_dir / "handoff"
    staging.mkdir()
    snapshot = work_dir / "source-archive.snapshot.zip"
    try:
        snapshot_info = copy_archive_snapshot(archive, snapshot)
        archive_snapshot = snapshot_info["path"]
        if not isinstance(archive_snapshot, Path):
            raise TypeError("archive snapshot path must be a Path")
        archive_errors = _archive_errors(archive_snapshot)
        if archive_errors:
            raise ValueError("handoff archive validation failed before extraction: " + "; ".join(archive_errors[:10]))
        with zipfile.ZipFile(archive_snapshot) as zf:
            by_name = {row.filename: row for row in zf.infolist() if row.filename in ALLOWED_NAMES and not row.is_dir()}
            for name in sorted(by_name):
                _write_member(zf, by_name[name], staging / name)
        _fsync_dir(staging)
        errors = handoff_verifier.validate_handoff_dir(staging, allow_checker_simulation=allow_checker_simulation)
        if errors:
            raise ValueError("unsealed handoff verification failed: " + "; ".join(errors[:10]))
        _atomic_publish_unsealed(staging, output_dir, replace=replace)
    except Exception:
        if work_dir.exists():
            shutil.rmtree(work_dir)
        raise
    else:
        if work_dir.exists():
            shutil.rmtree(work_dir)
    return output_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="safely extract a deterministic host-proof handoff ZIP archive")
    parser.add_argument("archive", type=Path, help="sealed handoff ZIP archive")
    parser.add_argument("--output-dir", type=Path, required=True, help="fresh handoff directory to publish after verification")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="unseal checker-simulation-non-proof handoffs for release-critical tests only")
    parser.add_argument("--replace", action="store_true", help="replace an existing non-symlink output directory after successful staging verification")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        out = unseal_archive(
            args.archive,
            output_dir=args.output_dir,
            allow_checker_simulation=args.allow_checker_simulation,
            replace=args.replace,
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing archive command
        print("host-proof handoff unseal FAILED", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return 1
    print("host-proof handoff unseal OK")
    print(f"archive_snapshot_policy={contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY}")
    print(f"canonical_zip_metadata_policy={contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY}")
    print(f"handoff_dir={out}")
    print(f"archive_sha256:{sha256_file(args.archive)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
