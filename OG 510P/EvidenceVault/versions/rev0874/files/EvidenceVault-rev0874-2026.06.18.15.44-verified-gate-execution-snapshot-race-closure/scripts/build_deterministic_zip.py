#!/usr/bin/env python3
"""Build a deterministic-order, policy-checked EvidenceVault ZIP.

The builder refuses symlinks and special files, writes canonical POSIX member
names with stable modes/timestamps/order, validates the temporary archive, and
publishes it atomically outside the source tree.  Deflate output is reproducible
under the same Python/zlib runtime; all logical content and metadata are pinned.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
import unicodedata
from typing import Any, Iterable
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "scripts").resolve()))
try:
    from validate_zip_container import ZipContainerError, validate_archive
finally:
    try:
        sys.path.remove(str((ROOT / "scripts").resolve()))
    except ValueError:
        pass


class ZipBuildError(RuntimeError):
    """Raised when a source tree or output target violates build policy."""


@dataclass(frozen=True)
class DirectorySnapshot:
    path: Path
    rel: str
    device: int
    inode: int
    mode: int
    mtime_ns: int
    ctime_ns: int


@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    rel: str
    device: int
    inode: int
    mode: int
    size: int
    mtime_ns: int
    ctime_ns: int
    sha256: str

    @property
    def executable(self) -> bool:
        return bool(self.mode & 0o111)


@dataclass(frozen=True)
class SourceSnapshot:
    directories: tuple[DirectorySnapshot, ...]
    files: tuple[FileSnapshot, ...]
    portable_sha256: str
    total_file_bytes: int


def _assert_no_symlink_components(path: Path, *, existing_only: bool = True) -> None:
    absolute = Path(os.path.abspath(os.fspath(path)))
    parts = absolute.parts
    cursor = Path(parts[0])
    for part in parts[1:]:
        cursor /= part
        if not cursor.exists() and existing_only:
            break
        if cursor.is_symlink():
            raise ZipBuildError(f"path traverses a symlink component: {cursor}")


def _safe_source_root(source: Path) -> Path:
    if source.is_symlink() or not source.is_dir():
        raise ZipBuildError(f"source root must be a non-symlink directory: {source}")
    source = source.resolve()
    if not source.name or source.name in {".", ".."}:
        raise ZipBuildError("source root must have a stable basename")
    if unicodedata.normalize("NFC", source.name) != source.name:
        raise ZipBuildError("source root basename must be NFC-normalized")
    return source


def _safe_output(source: Path, output: Path) -> Path:
    output = output.expanduser()
    candidate = output if output.is_absolute() else Path.cwd() / output
    candidate = Path(os.path.abspath(os.fspath(candidate)))
    _assert_no_symlink_components(candidate.parent)
    if not candidate.parent.is_dir():
        raise ZipBuildError("output parent must already exist")
    resolved = candidate.resolve(strict=False)
    if resolved == source or source in resolved.parents:
        raise ZipBuildError("output ZIP must be outside the source tree")
    if candidate.name != source.name + ".zip":
        raise ZipBuildError("output filename must equal source-root basename plus .zip")
    if candidate.exists() and (candidate.is_symlink() or not candidate.is_file()):
        raise ZipBuildError("existing output must be a non-symlink regular file")
    return candidate


def _manifest_timestamp(snapshot: SourceSnapshot) -> datetime:
    row = next((item for item in snapshot.files if item.rel == "PATCH_BUNDLE_MANIFEST.json"), None)
    if row is None:
        raise ZipBuildError("source snapshot lacks PATCH_BUNDLE_MANIFEST.json")
    try:
        payload = json.loads(_read_snapshot_bytes(row).decode("utf-8"))
        text = payload["created_at_utc"]
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception as exc:
        raise ZipBuildError(f"cannot obtain created_at_utc from PATCH_BUNDLE_MANIFEST.json: {exc}") from exc
    if parsed.tzinfo is None:
        raise ZipBuildError("created_at_utc must be timezone-aware")
    parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None, microsecond=0)
    # ZIP stores seconds in two-second increments.
    return parsed.replace(second=parsed.second - parsed.second % 2)


def _zip_datetime(value: datetime) -> tuple[int, int, int, int, int, int]:
    if value.year < 1980 or value.year > 2107:
        raise ZipBuildError("ZIP timestamp must be between 1980 and 2107")
    return (value.year, value.month, value.day, value.hour, value.minute, value.second)


def _clean_rel(rel: str, *, directory: bool) -> str:
    if not rel or "\x00" in rel or "\\" in rel:
        raise ZipBuildError(f"unsafe source-relative path: {rel!r}")
    if unicodedata.normalize("NFC", rel) != rel:
        raise ZipBuildError(f"source-relative path is not NFC-normalized: {rel!r}")
    pure = PurePosixPath(rel)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ZipBuildError(f"unsafe source-relative path: {rel!r}")
    for part in pure.parts:
        if any(ord(char) < 32 or ord(char) == 127 for char in part):
            raise ZipBuildError(f"control character in source path: {rel!r}")
        if part.endswith((" ", ".")):
            raise ZipBuildError(f"platform-ambiguous source path: {rel!r}")
    text = pure.as_posix()
    return text + "/" if directory else text


def _stat_signature(row: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        row.st_dev,
        row.st_ino,
        row.st_mode,
        row.st_size,
        row.st_mtime_ns,
        row.st_ctime_ns,
    )


def _open_regular_nofollow(path: Path) -> tuple[int, os.stat_result]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        before = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise ZipBuildError(f"cannot stat source file {path}: {exc}") from exc
    if not stat.S_ISREG(before.st_mode):
        raise ZipBuildError(f"source entry is not a regular file: {path}")
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ZipBuildError(f"cannot open source file without following symlinks {path}: {exc}") from exc
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or _stat_signature(opened) != _stat_signature(before):
            raise ZipBuildError(f"source file changed identity while opening: {path}")
        return fd, opened
    except Exception:
        os.close(fd)
        raise


def _capture_file(path: Path, rel: str) -> FileSnapshot:
    fd, opened = _open_regular_nofollow(path)
    digest = hashlib.sha256()
    try:
        with os.fdopen(fd, "rb", closefd=True) as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise ZipBuildError(f"cannot snapshot source file {rel}: {exc}") from exc
    if _stat_signature(after) != _stat_signature(opened):
        raise ZipBuildError(f"source file changed while being snapshotted: {rel}")
    return FileSnapshot(
        path=path,
        rel=rel,
        device=opened.st_dev,
        inode=opened.st_ino,
        mode=opened.st_mode,
        size=opened.st_size,
        mtime_ns=opened.st_mtime_ns,
        ctime_ns=opened.st_ctime_ns,
        sha256=digest.hexdigest(),
    )


def _directory_snapshot(path: Path, rel: str) -> DirectorySnapshot:
    try:
        row = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise ZipBuildError(f"cannot stat source directory {rel or '.'}: {exc}") from exc
    if not stat.S_ISDIR(row.st_mode):
        raise ZipBuildError(f"source directory entry is not a directory: {rel or '.'}")
    return DirectorySnapshot(
        path=path,
        rel=rel,
        device=row.st_dev,
        inode=row.st_ino,
        mode=row.st_mode,
        mtime_ns=row.st_mtime_ns,
        ctime_ns=row.st_ctime_ns,
    )


def _snapshot_portable_digest(
    directories: list[DirectorySnapshot], files: list[FileSnapshot]
) -> str:
    payload = {
        "directories": [row.rel for row in directories],
        "files": [
            {
                "executable": row.executable,
                "path": row.rel,
                "sha256": row.sha256,
                "size": row.size,
            }
            for row in files
        ],
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _capture_snapshot(source: Path) -> SourceSnapshot:
    directories: list[DirectorySnapshot] = [_directory_snapshot(source, "")]
    files: list[FileSnapshot] = []
    seen_folded: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(source, topdown=True, followlinks=False):
        directory = Path(dirpath)
        dirnames.sort()
        filenames.sort()
        for name in list(dirnames):
            child = directory / name
            if child.is_symlink():
                raise ZipBuildError(f"source tree contains a symlink directory: {child.relative_to(source)}")
            mode = child.stat(follow_symlinks=False).st_mode
            if not stat.S_ISDIR(mode):
                raise ZipBuildError(f"source directory entry is not a directory: {child.relative_to(source)}")
            rel = child.relative_to(source).as_posix()
            directories.append(_directory_snapshot(child, rel))
        for name in filenames:
            child = directory / name
            if child.is_symlink():
                raise ZipBuildError(f"source tree contains a symlink file: {child.relative_to(source)}")
            mode = child.stat(follow_symlinks=False).st_mode
            if not stat.S_ISREG(mode):
                raise ZipBuildError(f"source entry is not a regular file: {child.relative_to(source)}")
            if name.endswith(".pyc") or "__pycache__" in child.relative_to(source).parts:
                raise ZipBuildError(f"transient Python cache is forbidden: {child.relative_to(source)}")
            rel = child.relative_to(source).as_posix()
            files.append(_capture_file(child, rel))
    for rel in [*(row.rel for row in directories), *(row.rel for row in files)]:
        archive_rel = source.name if not rel else f"{source.name}/{rel}"
        logical = archive_rel.casefold()
        previous = seen_folded.setdefault(logical, archive_rel)
        if previous != archive_rel:
            raise ZipBuildError(f"case-folded source path collision: {previous!r} vs {archive_rel!r}")
    directories.sort(key=lambda row: (0 if not row.rel else len(PurePosixPath(row.rel).parts), row.rel))
    files.sort(key=lambda row: row.rel)
    return SourceSnapshot(
        directories=tuple(directories),
        files=tuple(files),
        portable_sha256=_snapshot_portable_digest(directories, files),
        total_file_bytes=sum(row.size for row in files),
    )


def _identity_tuple(row: DirectorySnapshot | FileSnapshot) -> tuple[int, int, int, int, int]:
    return (row.device, row.inode, row.mode, row.mtime_ns, row.ctime_ns)


def _assert_snapshot_unchanged(source: Path, expected: SourceSnapshot) -> None:
    observed = _capture_snapshot(source)
    if observed.portable_sha256 != expected.portable_sha256:
        raise ZipBuildError(
            "source tree content or path set changed after the build snapshot was captured"
        )
    expected_dirs = {row.rel: _identity_tuple(row) for row in expected.directories}
    observed_dirs = {row.rel: _identity_tuple(row) for row in observed.directories}
    expected_files = {row.rel: _identity_tuple(row) for row in expected.files}
    observed_files = {row.rel: _identity_tuple(row) for row in observed.files}
    if observed_dirs != expected_dirs or observed_files != expected_files:
        raise ZipBuildError(
            "source tree identity or metadata changed after the build snapshot was captured"
        )


def _read_snapshot_bytes(row: FileSnapshot) -> bytes:
    chunks: list[bytes] = []
    digest = hashlib.sha256()
    fd, opened = _open_regular_nofollow(row.path)
    wrapped = False
    try:
        if _stat_signature(opened) != (
            row.device,
            row.inode,
            row.mode,
            row.size,
            row.mtime_ns,
            row.ctime_ns,
        ):
            raise ZipBuildError(f"source file changed after snapshot: {row.rel}")
        with os.fdopen(fd, "rb", closefd=True) as handle:
            wrapped = True
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                chunks.append(chunk)
                digest.update(chunk)
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise ZipBuildError(f"cannot read snapshotted source file {row.rel}: {exc}") from exc
    finally:
        if not wrapped:
            os.close(fd)
    if _stat_signature(after) != _stat_signature(opened) or digest.hexdigest() != row.sha256:
        raise ZipBuildError(f"source file changed while reading snapshot: {row.rel}")
    return b"".join(chunks)


def _write_snapshot_file(row: FileSnapshot, member: Any) -> None:
    digest = hashlib.sha256()
    fd, opened = _open_regular_nofollow(row.path)
    expected_stat = (
        row.device,
        row.inode,
        row.mode,
        row.size,
        row.mtime_ns,
        row.ctime_ns,
    )
    wrapped = False
    try:
        if _stat_signature(opened) != expected_stat:
            raise ZipBuildError(f"source file changed after snapshot: {row.rel}")
        with os.fdopen(fd, "rb", closefd=True) as handle:
            wrapped = True
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                member.write(chunk)
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise ZipBuildError(f"cannot package snapshotted source file {row.rel}: {exc}") from exc
    finally:
        if not wrapped:
            os.close(fd)
    if _stat_signature(after) != expected_stat or digest.hexdigest() != row.sha256:
        raise ZipBuildError(f"source file changed while being packaged: {row.rel}")


def _verify_published_output(
    output: Path, *, expected_device: int, expected_inode: int, expected_sha256: str
) -> None:
    """Verify the published path still names the validated temporary inode."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(output, flags)
    except OSError as exc:
        raise ZipBuildError(f"cannot reopen published ZIP without following symlinks: {exc}") from exc
    digest = hashlib.sha256()
    try:
        with os.fdopen(fd, "rb", closefd=True) as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise ZipBuildError("published ZIP is no longer a regular file")
            if (opened.st_dev, opened.st_ino) != (expected_device, expected_inode):
                raise ZipBuildError("published ZIP path no longer names the validated temporary inode")
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise ZipBuildError(f"cannot verify published ZIP bytes: {exc}") from exc
    if _stat_signature(after) != _stat_signature(opened):
        raise ZipBuildError("published ZIP changed while its bytes were being verified")
    if digest.hexdigest() != expected_sha256:
        raise ZipBuildError("published ZIP bytes differ from the validated temporary archive")


def _info(name: str, timestamp: tuple[int, int, int, int, int, int], *, directory: bool, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=name, date_time=timestamp)
    info.create_system = 3
    info.extract_version = 20
    info.create_version = 20
    info.flag_bits = 0x800
    info.comment = b""
    info.extra = b""
    if directory:
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = ((stat.S_IFDIR | 0o755) << 16) | 0x10
    else:
        info.compress_type = zipfile.ZIP_DEFLATED
        mode = 0o755 if executable else 0o644
        info.external_attr = (stat.S_IFREG | mode) << 16
    return info


def build_archive(
    source: Path,
    output: Path,
    *,
    compression_level: int = 9,
    replace: bool = False,
) -> dict[str, Any]:
    source = _safe_source_root(source)
    output = _safe_output(source, output)
    if output.exists() and not replace:
        raise ZipBuildError(f"output already exists (use --replace): {output}")
    if not 0 <= compression_level <= 9:
        raise ZipBuildError("compression level must be 0..9")
    snapshot = _capture_snapshot(source)
    timestamp = _zip_datetime(_manifest_timestamp(snapshot))

    fd, tmp_text = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    try:
        os.fchmod(fd, 0o644)
    finally:
        os.close(fd)
    tmp = Path(tmp_text)
    try:
        with zipfile.ZipFile(
            tmp,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compression_level,
            allowZip64=True,
            strict_timestamps=True,
        ) as zf:
            zf.comment = b""
            for directory in snapshot.directories:
                if not directory.rel:
                    rel = source.name + "/"
                else:
                    rel = f"{source.name}/{directory.rel}"
                    rel = _clean_rel(rel, directory=True)
                zf.writestr(_info(rel, timestamp, directory=True), b"")
            for row in snapshot.files:
                rel = _clean_rel(f"{source.name}/{row.rel}", directory=False)
                info = _info(rel, timestamp, directory=False, executable=row.executable)
                with zf.open(info, "w", force_zip64=True) as member:
                    _write_snapshot_file(row, member)
        with tmp.open("rb") as handle:
            os.fsync(handle.fileno())
        _assert_snapshot_unchanged(source, snapshot)
        report = validate_archive(
            tmp,
            expected_root=source.name,
            logical_archive_name=output.name,
            require_overlay_manifest=True,
        )
        _assert_snapshot_unchanged(source, snapshot)
        temporary_stat = tmp.stat(follow_symlinks=False)
        if replace:
            os.replace(tmp, output)
        else:
            # Hard-link publication is atomic and refuses a destination created
            # after the preflight check; unlike os.replace it cannot clobber a
            # racing writer.  The temporary file is on the same filesystem.
            try:
                os.link(tmp, output)
            except FileExistsError as exc:
                raise ZipBuildError(f"output appeared during build; refusing to clobber: {output}") from exc
            except OSError as exc:
                raise ZipBuildError(f"atomic no-clobber publication failed: {exc}") from exc
            tmp.unlink()
        try:
            directory_fd = os.open(output.parent, os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        _verify_published_output(
            output,
            expected_device=temporary_stat.st_dev,
            expected_inode=temporary_stat.st_ino,
            expected_sha256=str(report.get("archive_sha256", "")),
        )
        report["archive"] = output.name
        report["output_path"] = os.fspath(output)
        report["builder"] = "scripts/build_deterministic_zip.py"
        report["compression_level"] = compression_level
        report["zip_timestamp"] = "%04d-%02d-%02dT%02d:%02d:%02dZ" % timestamp
        report["source_snapshot_sha256"] = snapshot.portable_sha256
        report["source_snapshot_files"] = len(snapshot.files)
        report["source_snapshot_bytes"] = snapshot.total_file_bytes
        report["source_snapshot_reverified_before_publication"] = True
        report["published_inode_and_bytes_reverified"] = True
        return report
    except ZipContainerError as exc:
        raise ZipBuildError(f"temporary archive failed container validation: {exc}") from exc
    finally:
        tmp.unlink(missing_ok=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output_zip", type=Path)
    parser.add_argument("--compression-level", type=int, default=9)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        report = build_archive(
            args.source_root,
            args.output_zip,
            compression_level=args.compression_level,
            replace=args.replace,
        )
    except ZipBuildError as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"deterministic-zip-builder: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "deterministic-zip-builder: OK "
            f"({report['archive']}; {report['file_count']} files; "
            f"sha256={report['archive_sha256']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
