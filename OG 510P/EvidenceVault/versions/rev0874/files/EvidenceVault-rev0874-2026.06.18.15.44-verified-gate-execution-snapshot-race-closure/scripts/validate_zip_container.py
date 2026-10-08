#!/usr/bin/env python3
"""Validate an EvidenceVault ZIP before extraction.

The extracted-tree overlay manifest cannot detect source-container ambiguity such
as duplicate ZIP member names, path aliases, symlink metadata, local/central
header disagreement, or overlapping member ranges.  This validator checks the
container itself and, by default, binds every archived payload byte to the
embedded CHECKS/overlay-manifest.json inventory.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import io
import os
import json
from pathlib import Path, PurePosixPath
import stat
import struct
import sys
import tempfile
import unicodedata
from typing import Any, BinaryIO, Iterable
import zipfile

sys.dont_write_bytecode = True
SHA256_RE = __import__("re").compile(r"^[0-9a-f]{64}$")
LOCAL_FILE_HEADER = struct.Struct("<IHHHHHIIIHH")
LOCAL_FILE_SIGNATURE = 0x04034B50
EOCD = struct.Struct("<IHHHHIIH")
EOCD_SIGNATURE = 0x06054B50
ALLOWED_COMPRESSION = {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
DEFAULT_MAX_MEMBERS = 100_000
DEFAULT_MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
DEFAULT_MAX_MEMBER_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_RATIO = 1_000.0


class ZipContainerError(RuntimeError):
    """Raised when an archive is ambiguous, unsafe, or byte-inconsistent."""


@dataclass(frozen=True)
class MemberDigest:
    size: int
    sha256: str


@dataclass(frozen=True)
class ArchiveIdentity:
    device: int
    inode: int
    mode: int
    link_count: int
    size: int
    mtime_ns: int
    ctime_ns: int

    @classmethod
    def from_stat(cls, value: os.stat_result) -> "ArchiveIdentity":
        return cls(
            device=value.st_dev,
            inode=value.st_ino,
            mode=value.st_mode,
            link_count=value.st_nlink,
            size=value.st_size,
            mtime_ns=value.st_mtime_ns,
            ctime_ns=value.st_ctime_ns,
        )

    def same_object(self, other: "ArchiveIdentity") -> bool:
        return (self.device, self.inode, stat.S_IFMT(self.mode)) == (
            other.device,
            other.inode,
            stat.S_IFMT(other.mode),
        )


class _PreadView(io.RawIOBase):
    """Independent seek cursor over one retained descriptor via os.pread()."""

    def __init__(self, fd: int, size: int) -> None:
        super().__init__()
        self._fd = fd
        self._size = size
        self._offset = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._offset

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            position = offset
        elif whence == os.SEEK_CUR:
            position = self._offset + offset
        elif whence == os.SEEK_END:
            position = self._size + offset
        else:
            raise ValueError(f"unsupported seek mode: {whence}")
        if position < 0:
            raise ValueError("negative seek position")
        self._offset = position
        return position

    def read(self, size: int = -1) -> bytes:
        if self.closed:
            raise ValueError("I/O operation on closed descriptor view")
        if size is None or size < 0:
            size = max(0, self._size - self._offset)
        else:
            size = min(size, max(0, self._size - self._offset))
        if size == 0:
            return b""
        data = os.pread(self._fd, size, self._offset)
        self._offset += len(data)
        return data

    def readinto(self, buffer: Any) -> int:
        data = self.read(len(buffer))
        buffer[: len(data)] = data
        return len(data)


def _absolute_lexical_path(path: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    return Path(os.path.abspath(os.fspath(expanded)))


def _capture_regular_identity(value: os.stat_result, label: str) -> ArchiveIdentity:
    identity = ArchiveIdentity.from_stat(value)
    if not stat.S_ISREG(identity.mode):
        raise ZipContainerError(f"{label} must be a regular file")
    if identity.link_count < 1:
        raise ZipContainerError(f"{label} has no live filesystem link")
    return identity


def _path_identity(path: Path, label: str) -> ArchiveIdentity:
    try:
        value = os.lstat(path)
    except OSError as exc:
        raise ZipContainerError(f"cannot inspect {label}: {exc}") from exc
    if stat.S_ISLNK(value.st_mode):
        raise ZipContainerError(f"{label} must not be a symlink: {path}")
    return _capture_regular_identity(value, label)


def _assert_source_identity(
    path: Path, fd: int, expected: ArchiveIdentity, *, phase: str
) -> None:
    try:
        opened = _capture_regular_identity(os.fstat(fd), f"archive descriptor at {phase}")
    except OSError as exc:
        raise ZipContainerError(f"cannot inspect archive descriptor at {phase}: {exc}") from exc
    named = _path_identity(path, f"archive path at {phase}")
    if opened != expected:
        raise ZipContainerError(f"archive descriptor metadata changed during {phase}")
    if not named.same_object(expected):
        raise ZipContainerError(
            f"archive path no longer names the validated inode during {phase}"
        )
    if named != expected:
        raise ZipContainerError(f"archive path metadata changed during {phase}")


def _open_archive_descriptor(path: Path) -> tuple[Path, int, ArchiveIdentity]:
    archive = _absolute_lexical_path(path)
    before = _path_identity(archive, "archive path before open")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(archive, flags)
    except OSError as exc:
        raise ZipContainerError(f"cannot open archive without following a symlink: {exc}") from exc
    try:
        opened = _capture_regular_identity(os.fstat(fd), "opened archive")
        after = _path_identity(archive, "archive path after open")
        if not opened.same_object(before) or not after.same_object(opened):
            raise ZipContainerError("archive path was substituted while opening")
        if opened != before or after != opened:
            raise ZipContainerError("archive metadata changed while opening")
        return archive, fd, opened
    except Exception:
        os.close(fd)
        raise


def _sha256_fd(fd: int, expected_size: int) -> str:
    digest = hashlib.sha256()
    offset = 0
    while offset < expected_size:
        chunk = os.pread(fd, min(1024 * 1024, expected_size - offset), offset)
        if not chunk:
            raise ZipContainerError("archive descriptor became truncated while hashing")
        digest.update(chunk)
        offset += len(chunk)
    if os.pread(fd, 1, expected_size):
        raise ZipContainerError("archive descriptor grew while hashing")
    return digest.hexdigest()


def _snapshot_descriptor(fd: int, expected_size: int) -> tuple[BinaryIO, str]:
    snapshot = tempfile.TemporaryFile(mode="w+b")
    digest = hashlib.sha256()
    offset = 0
    try:
        while offset < expected_size:
            chunk = os.pread(fd, min(1024 * 1024, expected_size - offset), offset)
            if not chunk:
                raise ZipContainerError("archive became truncated while snapshotting")
            snapshot.write(chunk)
            digest.update(chunk)
            offset += len(chunk)
        if os.pread(fd, 1, expected_size):
            raise ZipContainerError("archive grew while snapshotting")
        snapshot.flush()
        snapshot.seek(0)
        return snapshot, digest.hexdigest()
    except Exception:
        snapshot.close()
        raise


def sha256_file(path: Path) -> str:
    """Hash one stable regular-file identity without reopening its pathname."""
    archive, fd, identity = _open_archive_descriptor(path)
    try:
        digest = _sha256_fd(fd, identity.size)
        _assert_source_identity(archive, fd, identity, phase="hash completion")
        return digest
    finally:
        os.close(fd)


def _clean_member_name(name: Any, label: str) -> str:
    if not isinstance(name, str) or not name or "\x00" in name or "\\" in name:
        raise ZipContainerError(f"{label} must be a non-empty POSIX archive path")
    if unicodedata.normalize("NFC", name) != name:
        raise ZipContainerError(f"{label} is not NFC-normalized: {name!r}")
    if any(ord(char) < 32 or ord(char) == 127 for char in name):
        raise ZipContainerError(f"{label} contains a control character: {name!r}")
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ZipContainerError(f"{label} is unsafe or non-canonical: {name!r}")
    if not pure.parts:
        raise ZipContainerError(f"{label} has no path components")
    first = pure.parts[0]
    if ":" in first or first.startswith("~"):
        raise ZipContainerError(f"{label} has a platform-sensitive root component: {name!r}")
    for part in pure.parts:
        if part.endswith((" ", ".")):
            raise ZipContainerError(f"{label} has a platform-ambiguous component: {name!r}")
    canonical = pure.as_posix()
    if name.endswith("/"):
        canonical += "/"
    if canonical != name:
        raise ZipContainerError(f"{label} is not canonical POSIX spelling: {name!r}")
    return name


def _relative_payload_name(name: str, root_name: str) -> str | None:
    prefix = root_name + "/"
    if name == prefix:
        return None
    if not name.startswith(prefix):
        raise ZipContainerError(f"member escapes the single archive root {root_name!r}: {name!r}")
    rel = name[len(prefix) :]
    if not rel or rel.endswith("/"):
        return None
    return rel


def _member_kind(info: zipfile.ZipInfo) -> str:
    mode = (info.external_attr >> 16) & 0xFFFF
    file_type = stat.S_IFMT(mode)
    if stat.S_ISLNK(mode):
        raise ZipContainerError(f"ZIP member is a symlink: {info.filename}")
    if info.is_dir():
        if file_type not in {0, stat.S_IFDIR}:
            raise ZipContainerError(f"directory member carries non-directory mode: {info.filename}")
        return "directory"
    if info.filename.endswith("/"):
        raise ZipContainerError(f"file member has a directory-form name: {info.filename}")
    if file_type not in {0, stat.S_IFREG}:
        raise ZipContainerError(f"ZIP member is not a regular file: {info.filename}")
    return "file"


def _decode_local_name(raw: bytes, flag_bits: int) -> str:
    encoding = "utf-8" if flag_bits & 0x800 else "cp437"
    try:
        return raw.decode(encoding)
    except UnicodeDecodeError as exc:
        raise ZipContainerError(f"local ZIP filename is not valid {encoding}") from exc


def _read_eocd(handle: BinaryIO, archive_size: int) -> dict[str, int]:
    """Require a single-disk, comment-free, non-ZIP64 EOCD at exact EOF."""
    if archive_size < EOCD.size:
        raise ZipContainerError("archive is too small to contain an end-of-central-directory record")
    eocd_offset = archive_size - EOCD.size
    handle.seek(eocd_offset)
    raw = handle.read(EOCD.size)
    if len(raw) != EOCD.size:
        raise ZipContainerError("truncated end-of-central-directory record")
    (
        signature,
        disk_number,
        central_disk,
        disk_entries,
        total_entries,
        central_size,
        central_offset,
        comment_length,
    ) = EOCD.unpack(raw)
    if signature != EOCD_SIGNATURE:
        raise ZipContainerError("end-of-central-directory record is not exactly at EOF")
    if comment_length != 0:
        raise ZipContainerError("ZIP comments and trailing bytes are not allowed")
    if disk_number != 0 or central_disk != 0 or disk_entries != total_entries:
        raise ZipContainerError("multi-disk ZIP archives are not allowed")
    if total_entries == 0xFFFF or central_size == 0xFFFFFFFF or central_offset == 0xFFFFFFFF:
        raise ZipContainerError("ZIP64 central-directory records are outside ev-safe-zip-v1")
    if central_offset + central_size != eocd_offset:
        raise ZipContainerError("central-directory extent does not end exactly at the EOCD")
    return {
        "offset": eocd_offset,
        "entries": total_entries,
        "central_size": central_size,
        "central_offset": central_offset,
    }


def _parse_extra_records(extra: bytes, *, label: str) -> list[tuple[int, bytes]]:
    """Parse an extra-field area without accepting unclaimed trailing bytes."""
    records: list[tuple[int, bytes]] = []
    cursor = 0
    while cursor + 4 <= len(extra):
        header_id, data_size = struct.unpack_from("<HH", extra, cursor)
        cursor += 4
        end = cursor + data_size
        if end > len(extra):
            raise ZipContainerError(f"truncated {label} extra-field record")
        records.append((header_id, extra[cursor:end]))
        cursor = end
    if cursor != len(extra):
        raise ZipContainerError(f"trailing bytes in {label} extra-field area")
    return records


def _zip64_local_sizes(
    extra: bytes,
    *,
    need_uncompressed: bool,
    need_compressed: bool,
    member_name: str,
) -> tuple[int | None, int | None]:
    """Accept only the exact local ZIP64 size record emitted by our builder.

    Extra fields can carry alternate path, platform, encryption, or timestamp
    semantics interpreted differently by extractors.  ev-safe-zip-v1 therefore
    rejects every local extra field except a single ZIP64 record when the fixed
    local-header size slots are the ZIP64 sentinels.  Central extra fields are
    rejected separately.
    """
    records = _parse_extra_records(extra, label="local")
    needed_values = int(need_uncompressed) + int(need_compressed)
    if needed_values == 0:
        if records:
            ids = ", ".join(f"0x{header_id:04x}" for header_id, _ in records)
            raise ZipContainerError(
                f"unsupported local extra field(s) for {member_name}: {ids}"
            )
        return None, None
    if len(records) != 1 or records[0][0] != 0x0001:
        ids = ", ".join(f"0x{header_id:04x}" for header_id, _ in records) or "none"
        raise ZipContainerError(
            f"local ZIP64 size sentinel requires one exclusive 0x0001 record for "
            f"{member_name}; found {ids}"
        )
    data = records[0][1]
    expected_length = needed_values * 8
    if len(data) != expected_length:
        raise ZipContainerError(
            f"local ZIP64 size field has non-canonical length for {member_name}: "
            f"{len(data)} != {expected_length}"
        )
    position = 0
    uncompressed = compressed = None
    if need_uncompressed:
        uncompressed = struct.unpack_from("<Q", data, position)[0]
        position += 8
    if need_compressed:
        compressed = struct.unpack_from("<Q", data, position)[0]
    return uncompressed, compressed


def _read_local_layout(
    handle: BinaryIO,
    info: zipfile.ZipInfo,
    *,
    central_directory_start: int,
    archive_size: int,
) -> tuple[int, int]:
    offset = info.header_offset
    if offset < 0 or offset + LOCAL_FILE_HEADER.size > archive_size:
        raise ZipContainerError(f"local header offset is out of range: {info.filename}")
    handle.seek(offset)
    raw = handle.read(LOCAL_FILE_HEADER.size)
    if len(raw) != LOCAL_FILE_HEADER.size:
        raise ZipContainerError(f"truncated local header: {info.filename}")
    (
        signature,
        local_version,
        local_flags,
        local_method,
        _mtime,
        _mdate,
        local_crc,
        local_compressed,
        local_uncompressed,
        filename_length,
        extra_length,
    ) = LOCAL_FILE_HEADER.unpack(raw)
    if signature != LOCAL_FILE_SIGNATURE:
        raise ZipContainerError(f"bad local header signature: {info.filename}")
    local_name_raw = handle.read(filename_length)
    if len(local_name_raw) != filename_length:
        raise ZipContainerError(f"truncated local filename: {info.filename}")
    local_extra = handle.read(extra_length)
    if len(local_extra) != extra_length:
        raise ZipContainerError(f"truncated local extra field: {info.filename}")
    local_name = _decode_local_name(local_name_raw, local_flags)
    if local_name != info.filename:
        raise ZipContainerError(
            f"local/central filename disagreement: {local_name!r} != {info.filename!r}"
        )
    if local_method != info.compress_type:
        raise ZipContainerError(f"local/central compression disagreement: {info.filename}")
    if local_version != info.extract_version:
        raise ZipContainerError(f"local/central extraction-version disagreement: {info.filename}")
    if local_flags != info.flag_bits:
        raise ZipContainerError(f"local/central flag disagreement: {info.filename}")
    if local_crc != info.CRC:
        raise ZipContainerError(f"local/central CRC disagreement: {info.filename}")
    zip64_uncompressed, zip64_compressed = _zip64_local_sizes(
        local_extra,
        need_uncompressed=local_uncompressed == 0xFFFFFFFF,
        need_compressed=local_compressed == 0xFFFFFFFF,
        member_name=info.filename,
    )
    effective_uncompressed = zip64_uncompressed if local_uncompressed == 0xFFFFFFFF else local_uncompressed
    effective_compressed = zip64_compressed if local_compressed == 0xFFFFFFFF else local_compressed
    if effective_uncompressed != info.file_size or effective_compressed != info.compress_size:
        raise ZipContainerError(f"local/central size disagreement: {info.filename}")
    data_start = offset + LOCAL_FILE_HEADER.size + filename_length + extra_length
    data_end = data_start + info.compress_size
    if data_start < offset or data_end < data_start:
        raise ZipContainerError(f"integer-overflow-like member layout: {info.filename}")
    if data_end > central_directory_start or data_end > archive_size:
        raise ZipContainerError(f"member data overlaps central directory or EOF: {info.filename}")
    return offset, data_end


def _load_json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(data.decode("utf-8"))
    except Exception as exc:
        raise ZipContainerError(f"invalid {label}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ZipContainerError(f"{label} must be a JSON object")
    return parsed


def _validate_embedded_overlay_inventory(
    zf: zipfile.ZipFile,
    root_name: str,
    file_digests: dict[str, MemberDigest],
    *,
    logical_archive_name: str,
) -> dict[str, Any]:
    manifest_rel = "CHECKS/overlay-manifest.json"
    sidecar_rel = "CHECKS/overlay-manifest.sha256"
    patch_manifest_rel = "PATCH_BUNDLE_MANIFEST.json"
    required = {manifest_rel, sidecar_rel, patch_manifest_rel}
    absent = sorted(required - set(file_digests))
    if absent:
        raise ZipContainerError("archive lacks required embedded control files: " + ", ".join(absent))

    def read_rel(rel: str) -> bytes:
        try:
            return zf.read(f"{root_name}/{rel}")
        except KeyError as exc:
            raise ZipContainerError(f"archive member disappeared during validation: {rel}") from exc

    manifest_bytes = read_rel(manifest_rel)
    sidecar = read_rel(sidecar_rel).decode("utf-8", errors="strict").strip()
    expected_sidecar = f"{hashlib.sha256(manifest_bytes).hexdigest()}  {manifest_rel}"
    if sidecar != expected_sidecar:
        raise ZipContainerError("embedded overlay-manifest sidecar is inconsistent")
    manifest = _load_json_bytes(manifest_bytes, manifest_rel)
    entries = manifest.get("files")
    if not isinstance(entries, list) or manifest.get("file_count") != len(entries):
        raise ZipContainerError("embedded overlay manifest has invalid file_count/files")

    declared: dict[str, MemberDigest] = {}
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise ZipContainerError(f"overlay manifest entry {index} is not an object")
        rel = _clean_member_name(raw.get("path"), f"overlay manifest files[{index}].path")
        if rel.endswith("/"):
            raise ZipContainerError(f"overlay manifest declares a directory: {rel}")
        if rel in declared:
            raise ZipContainerError(f"overlay manifest repeats a path: {rel}")
        size = raw.get("bytes")
        digest = raw.get("sha256")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ZipContainerError(f"overlay manifest has invalid size for {rel}")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ZipContainerError(f"overlay manifest has invalid SHA-256 for {rel}")
        declared[rel] = MemberDigest(size=size, sha256=digest)

    excluded = {manifest_rel, sidecar_rel}
    actual_payload = {rel: row for rel, row in file_digests.items() if rel not in excluded}
    if set(declared) != set(actual_payload):
        missing = sorted(set(actual_payload) - set(declared))
        extra = sorted(set(declared) - set(actual_payload))
        raise ZipContainerError(
            f"embedded overlay manifest file set mismatch; missing={missing[:10]} extra={extra[:10]}"
        )
    for rel, expected in declared.items():
        actual = actual_payload[rel]
        if actual != expected:
            raise ZipContainerError(f"embedded overlay manifest byte mismatch: {rel}")

    patch_manifest = _load_json_bytes(read_rel(patch_manifest_rel), patch_manifest_rel)
    if patch_manifest.get("archive_root") != root_name:
        raise ZipContainerError("PATCH_BUNDLE_MANIFEST.json archive_root differs from ZIP root")
    if patch_manifest.get("archive_name") != logical_archive_name:
        raise ZipContainerError("PATCH_BUNDLE_MANIFEST.json archive_name differs from ZIP filename")
    profile = patch_manifest.get("archive_container_profile")
    if not isinstance(profile, dict):
        raise ZipContainerError("PATCH_BUNDLE_MANIFEST.json lacks archive_container_profile")
    if profile.get("policy") != "ev-safe-zip-v1":
        raise ZipContainerError("archive_container_profile.policy is not ev-safe-zip-v1")
    if profile.get("expected_root") != root_name:
        raise ZipContainerError("archive_container_profile.expected_root differs from ZIP root")
    if profile.get("validator") != "scripts/validate_zip_container.py":
        raise ZipContainerError("archive_container_profile.validator is not pinned")

    return {
        "overlay_manifest_entries": len(declared),
        "overlay_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "patch_bundle_revision": patch_manifest.get("overlay_revision"),
        "archive_policy": profile.get("policy"),
    }


def validate_archive(
    archive: Path,
    *,
    expected_root: str | None = None,
    logical_archive_name: str | None = None,
    require_overlay_manifest: bool = True,
    max_members: int = DEFAULT_MAX_MEMBERS,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_member_bytes: int = DEFAULT_MAX_MEMBER_BYTES,
    max_ratio: float = DEFAULT_MAX_RATIO,
) -> dict[str, Any]:
    """Validate one immutable descriptor snapshot and return its report."""
    source_path, source_fd, source_identity = _open_archive_descriptor(archive)
    snapshot: BinaryIO | None = None
    try:
        logical_archive_name = logical_archive_name or source_path.name
        if (
            Path(logical_archive_name).name != logical_archive_name
            or not logical_archive_name.endswith(".zip")
        ):
            raise ZipContainerError("logical archive name must be a .zip basename")
        if max_members < 1 or max_total_bytes < 1 or max_member_bytes < 1 or max_ratio <= 0:
            raise ZipContainerError("archive limits must be positive")

        archive_size = source_identity.size
        if archive_size < 22:
            raise ZipContainerError("archive is too small to be a ZIP")
        snapshot, snapshot_sha256 = _snapshot_descriptor(source_fd, archive_size)
        _assert_source_identity(
            source_path, source_fd, source_identity, phase="snapshot completion"
        )

        snapshot_fd = snapshot.fileno()
        zip_view = _PreadView(snapshot_fd, archive_size)
        raw_handle = _PreadView(snapshot_fd, archive_size)
        try:
            zf = zipfile.ZipFile(zip_view, "r")
        except (OSError, zipfile.BadZipFile) as exc:
            raise ZipContainerError(f"cannot open ZIP snapshot: {exc}") from exc

        with zf, raw_handle:
            eocd = _read_eocd(raw_handle, archive_size)
            infos = zf.infolist()
            if not infos:
                raise ZipContainerError("archive contains no members")
            if len(infos) > max_members:
                raise ZipContainerError(
                    f"archive member count exceeds limit: {len(infos)} > {max_members}"
                )
            if zf.comment:
                raise ZipContainerError("archive comment is not allowed")
            central_directory_start = getattr(zf, "start_dir", None)
            if not isinstance(central_directory_start, int) or not 0 <= central_directory_start <= archive_size:
                raise ZipContainerError("cannot establish central-directory boundary")
            if central_directory_start != eocd["central_offset"]:
                raise ZipContainerError("central-directory offset is adjusted, prefixed, or inconsistent")
            if len(infos) != eocd["entries"]:
                raise ZipContainerError("central-directory entry count differs from EOCD")

            exact_names: set[str] = set()
            normalized_keys: dict[str, str] = {}
            casefold_keys: dict[str, str] = {}
            member_kinds: dict[str, str] = {}
            top_levels: set[str] = set()
            layouts: list[tuple[int, int, str]] = []
            total_uncompressed = 0
            total_compressed = 0
            file_infos: list[zipfile.ZipInfo] = []

            for index, info in enumerate(infos):
                name = _clean_member_name(info.filename, f"member[{index}]")
                if name in exact_names:
                    raise ZipContainerError(f"duplicate ZIP member name: {name}")
                exact_names.add(name)
                logical = name[:-1] if name.endswith("/") else name
                normalized = unicodedata.normalize("NFC", logical)
                folded = normalized.casefold()
                previous = normalized_keys.setdefault(normalized, name)
                if previous != name:
                    raise ZipContainerError(
                        f"Unicode-normalized member collision: {previous!r} vs {name!r}"
                    )
                previous = casefold_keys.setdefault(folded, name)
                if previous != name:
                    raise ZipContainerError(
                        f"case-folded member collision: {previous!r} vs {name!r}"
                    )
                top_levels.add(PurePosixPath(logical).parts[0])
                kind = _member_kind(info)
                member_kinds[logical] = kind
                if info.comment:
                    raise ZipContainerError(f"member comment is not allowed: {name}")
                if info.extra:
                    records = _parse_extra_records(info.extra, label="central")
                    ids = ", ".join(f"0x{header_id:04x}" for header_id, _ in records)
                    raise ZipContainerError(
                        f"central extra fields are outside ev-safe-zip-v1 for {name}: {ids}"
                    )
                if info.flag_bits & 0x1:
                    raise ZipContainerError(f"encrypted ZIP member is not allowed: {name}")
                if info.flag_bits & 0x8:
                    raise ZipContainerError(
                        f"data-descriptor ZIP members are outside ev-safe-zip-v1: {name}"
                    )
                if info.flag_bits & ~0x0800:
                    raise ZipContainerError(
                        f"unsupported general-purpose ZIP flags for {name}: {info.flag_bits:#x}"
                    )
                if info.compress_type not in ALLOWED_COMPRESSION:
                    raise ZipContainerError(
                        f"unsupported compression method for {name}: {info.compress_type}"
                    )
                if info.file_size < 0 or info.compress_size < 0:
                    raise ZipContainerError(f"negative member size: {name}")
                if info.file_size > max_member_bytes:
                    raise ZipContainerError(f"member exceeds uncompressed-size limit: {name}")
                if info.file_size and info.compress_size == 0:
                    raise ZipContainerError(
                        f"non-empty member claims zero compressed bytes: {name}"
                    )
                if info.compress_size and info.file_size / info.compress_size > max_ratio:
                    raise ZipContainerError(f"member compression ratio exceeds limit: {name}")
                total_uncompressed += info.file_size
                total_compressed += info.compress_size
                if total_uncompressed > max_total_bytes:
                    raise ZipContainerError("archive total uncompressed bytes exceed limit")
                start, end = _read_local_layout(
                    raw_handle,
                    info,
                    central_directory_start=central_directory_start,
                    archive_size=archive_size,
                )
                layouts.append((start, end, name))
                if kind == "file":
                    file_infos.append(info)

            if len(top_levels) != 1:
                raise ZipContainerError(
                    f"archive must contain exactly one top-level root: {sorted(top_levels)}"
                )
            root_name = next(iter(top_levels))
            _clean_member_name(root_name, "archive root")
            if expected_root is not None and root_name != expected_root:
                raise ZipContainerError(
                    f"archive root mismatch: {root_name!r} != {expected_root!r}"
                )
            if logical_archive_name[:-4] != root_name:
                raise ZipContainerError(
                    "archive filename stem must equal the single top-level root"
                )

            for name, kind in member_kinds.items():
                parts = PurePosixPath(name).parts
                for depth in range(1, len(parts)):
                    ancestor = PurePosixPath(*parts[:depth]).as_posix()
                    if member_kinds.get(ancestor) == "file":
                        raise ZipContainerError(
                            f"file member is also a parent path: {ancestor}"
                        )

            layouts.sort()
            previous_end = 0
            previous_name = ""
            for start, end, name in layouts:
                if start < previous_end:
                    raise ZipContainerError(
                        f"overlapping local member ranges: {previous_name!r} and {name!r}"
                    )
                if start != previous_end:
                    raise ZipContainerError(
                        f"unclaimed bytes or a gap precedes local member {name!r}: "
                        f"{previous_end}..{start}"
                    )
                previous_end = end
                previous_name = name
            if previous_end != central_directory_start:
                raise ZipContainerError(
                    "local member stream does not end exactly at the central directory"
                )

            file_digests: dict[str, MemberDigest] = {}
            for info in file_infos:
                rel = _relative_payload_name(info.filename, root_name)
                if rel is None:
                    raise ZipContainerError(
                        f"root entry is unexpectedly a file: {info.filename}"
                    )
                digest = hashlib.sha256()
                read_bytes = 0
                try:
                    with zf.open(info, "r") as member:
                        for chunk in iter(lambda: member.read(1024 * 1024), b""):
                            digest.update(chunk)
                            read_bytes += len(chunk)
                except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                    raise ZipContainerError(
                        f"cannot safely read member {info.filename}: {exc}"
                    ) from exc
                if read_bytes != info.file_size:
                    raise ZipContainerError(
                        f"decompressed-size mismatch: {info.filename}"
                    )
                file_digests[rel] = MemberDigest(read_bytes, digest.hexdigest())

            inventory_report: dict[str, Any] = {}
            if require_overlay_manifest:
                inventory_report = _validate_embedded_overlay_inventory(
                    zf,
                    root_name,
                    file_digests,
                    logical_archive_name=logical_archive_name,
                )

        final_source_sha256 = _sha256_fd(source_fd, archive_size)
        if final_source_sha256 != snapshot_sha256:
            raise ZipContainerError(
                "archive bytes changed after the validated descriptor snapshot was captured"
            )
        _assert_source_identity(
            source_path, source_fd, source_identity, phase="validation completion"
        )

        ratio = (total_uncompressed / total_compressed) if total_compressed else 1.0
        return {
            "status": "zip_container_valid",
            "archive": source_path.name,
            "archive_sha256": snapshot_sha256,
            "archive_bytes": archive_size,
            "root": root_name,
            "member_count": len(infos),
            "file_count": len(file_infos),
            "directory_count": len(infos) - len(file_infos),
            "total_uncompressed_bytes": total_uncompressed,
            "total_compressed_bytes": total_compressed,
            "aggregate_compression_ratio": round(ratio, 6),
            "source_container_checks": {
                "descriptor_bound_source": "verified",
                "immutable_validation_snapshot": "verified",
                "source_bytes_equal_validated_snapshot_at_return": "verified",
                "source_path_still_names_opened_inode": "verified",
                "duplicate_names": "rejected",
                "unsafe_paths": "rejected",
                "unicode_or_case_aliases": "rejected",
                "symlinks_or_special_files": "rejected",
                "encrypted_or_unsupported_members": "rejected",
                "local_central_header_disagreement": "rejected",
                "alternate_or_unsupported_extra_fields": "rejected",
                "overlapping_member_ranges": "rejected",
                "crc_and_decompression": "verified",
            },
            "embedded_inventory_verified": require_overlay_manifest,
            **inventory_report,
        }
    finally:
        if snapshot is not None:
            snapshot.close()
        os.close(source_fd)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-root")
    parser.add_argument(
        "--structural-only",
        action="store_true",
        help="skip embedded EvidenceVault manifest binding (for synthetic tests only)",
    )
    parser.add_argument("--logical-archive-name", help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-members", type=int, default=DEFAULT_MAX_MEMBERS)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--max-member-bytes", type=int, default=DEFAULT_MAX_MEMBER_BYTES)
    parser.add_argument("--max-ratio", type=float, default=DEFAULT_MAX_RATIO)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        report = validate_archive(
            args.archive,
            expected_root=args.expected_root,
            logical_archive_name=args.logical_archive_name,
            require_overlay_manifest=not args.structural_only,
            max_members=args.max_members,
            max_total_bytes=args.max_total_bytes,
            max_member_bytes=args.max_member_bytes,
            max_ratio=args.max_ratio,
        )
    except ZipContainerError as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"zip-container: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "zip-container: OK "
            f"({report['member_count']} members; {report['file_count']} files; "
            f"root={report['root']}; sha256={report['archive_sha256']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
