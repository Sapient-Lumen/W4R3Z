from __future__ import annotations

"""Durable crash/restart recovery records for Micromax editor buffers.

The journal owns private, checksummed recovery records.  It deliberately does
not own the editor's document writer or overwrite policy: normal saves still go
through ``file_write.write_file_bytes``, while recovery restores are staged in
an editor buffer before a user chooses whether and where to save.
"""

from dataclasses import dataclass, field
from enum import Enum
import heapq
from pathlib import Path
from typing import BinaryIO, Callable, Iterable, Mapping, Optional, Union
import base64
import binascii
import errno
import hashlib
import json
import os
import stat
import struct
import time

from .save_residue import (
    ProcessIdentity,
    TempOwnerState,
    build_private_temp_name,
    normalize_save_lease_id,
    parse_private_temp_name,
    private_temp_lease,
    temp_owner_state,
)

SCHEMA = "micromax.recovery.v1"
FRAMED_SCHEMA = "micromax.recovery.v2"
DEFAULT_MAX_PAYLOAD_BYTES = 32 * 1024 * 1024
DEFAULT_MAX_SCAN_RECORDS = 64
DEFAULT_MAX_SCAN_DIRECTORY_ENTRIES = 4096
DEFAULT_MAX_SCAN_RECORD_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_SCAN_COMPARISON_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_RESIDUE_FILES = 128
DEFAULT_MAX_RESIDUE_DIRECTORY_ENTRIES = 4096
PAYLOAD_KIND_BYTES = "bytes"
PAYLOAD_KIND_EDITOR_TEXT = "editor-text-utf8-surrogatepass"
MODE_REPAIR_CONTRACT_V1 = "atomic-private-temp-mode-v1"
PRIVATE_ATOMIC_COMMIT_MODE = 0o600
_METADATA_MAX_FIELDS = 32
_METADATA_MAX_BYTES = 16 * 1024
_RECORD_SUFFIX = ".recovery.json"
_FRAMED_RECORD_MAGIC = b"MICROMAX-RECOVERY\x00\x02\r\n"
_FRAMED_HEADER_LENGTH = struct.Struct(">I")
_FRAMED_HEADER_MAX_BYTES = 128 * 1024
_FRAMED_PAYLOAD_ENCODING = "raw-tail"
_FRAMED_HEADER_DIGEST_DOMAIN = b"micromax.recovery.v2.header\x00"
_DIR_FD_SUPPORT = set(getattr(os, "supports_dir_fd", set()))
_FOLLOW_SYMLINK_SUPPORT = set(getattr(os, "supports_follow_symlinks", set()))
_FD_SUPPORT = set(getattr(os, "supports_fd", set()))
_MODE_REPAIR_DIRFD_SUPPORTED = (
    os.name != "nt"
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and os.open in _DIR_FD_SUPPORT
    and os.stat in _DIR_FD_SUPPORT
    and os.stat in _FOLLOW_SYMLINK_SUPPORT
)
_SCANDIR_FD_SUPPORTED = os.scandir in _FD_SUPPORT
_SAFE_RESIDUE_UNLINK = (
    os.name != "nt"
    and os.open in _DIR_FD_SUPPORT
    and os.stat in _DIR_FD_SUPPORT
    and os.stat in _FOLLOW_SYMLINK_SUPPORT
    and os.unlink in _DIR_FD_SUPPORT
    and _SCANDIR_FD_SUPPORTED
)
_UNSUPPORTED_DIRECTORY_SYNC_ERRNOS = frozenset(
    value
    for value in (
        getattr(errno, "EINVAL", None),
        getattr(errno, "ENOSYS", None),
        getattr(errno, "ENOTSUP", None),
        getattr(errno, "EOPNOTSUPP", None),
    )
    if value is not None
)


class RecoveryError(Exception):
    """Base class for recovery journal failures."""


class RecoveryCorruptError(RecoveryError):
    """A recovery record failed structural or integrity validation."""


class RecoveryConflictError(RecoveryError):
    """The target's authority or contents conflict with a destructive restore."""


class RecoveryTooLargeError(RecoveryError):
    """A payload or comparison target exceeds the configured recovery budget."""


class RecoverySelectorError(RecoveryError):
    """A human recovery selector is missing, ambiguous, or out of range."""


class RecoveryStatus(str, Enum):
    RECOVERABLE = "recoverable"
    TARGET_CHANGED = "target_changed"
    TARGET_UNREADABLE = "target_unreadable"
    ALREADY_PERSISTED = "already_persisted"


class RecoveryResidueKind(str, Enum):
    CHECKPOINT_TEMP = "checkpoint_temp"
    DOCUMENT_TEMP = "document_temp"


@dataclass(frozen=True)
class Fingerprint:
    exists: bool
    size: int = 0
    sha256: Optional[str] = None

    def to_json(self) -> dict[str, object]:
        return {"exists": self.exists, "size": self.size, "sha256": self.sha256}

    @classmethod
    def from_json(cls, value: object, *, label: str = "fingerprint") -> "Fingerprint":
        if not isinstance(value, dict) or type(value.get("exists")) is not bool:
            raise RecoveryCorruptError(f"invalid {label}")
        exists = value["exists"]
        size = value.get("size", 0)
        digest = value.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise RecoveryCorruptError(f"invalid {label} size")
        if digest is not None and (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise RecoveryCorruptError(f"invalid {label} digest")
        if exists and digest is None:
            raise RecoveryCorruptError(f"existing {label} requires a digest")
        if not exists and (size != 0 or digest is not None):
            raise RecoveryCorruptError(f"missing {label} carries content")
        return cls(exists=exists, size=size, sha256=digest)

    @classmethod
    def for_bytes(cls, data: bytes) -> "Fingerprint":
        return cls(True, len(data), _sha256(data))


@dataclass(frozen=True)
class RecoveryCandidate:
    entry_id: str
    buffer_id: str
    target: Path
    created_ns: int
    payload_size: int
    payload_sha256: str
    base: Fingerprint
    status: RecoveryStatus
    commit: Fingerprint = field(default_factory=lambda: Fingerprint(False))
    payload_kind: str = PAYLOAD_KIND_BYTES
    metadata: dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    current_mode: int | None = None
    intended_mode: int | None = None
    mode_repair_available: bool = False
    mode_repair_required: bool = False
    mode_repair_conflict: bool = False


@dataclass(frozen=True)
class RecoverySnapshot:
    candidate: RecoveryCandidate
    payload: bytes

    def editor_text(self) -> str:
        """Decode a staged editor-text snapshot without losing lone surrogates."""

        if self.candidate.payload_kind == PAYLOAD_KIND_EDITOR_TEXT:
            return self.payload.decode("utf-8", errors="surrogatepass")
        encoding = str(
            self.candidate.metadata.get("encoding")
            or self.candidate.metadata.get("file_encoding")
            or "utf-8"
        )
        try:
            return self.payload.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            # Legacy rev0959 records contain document bytes rather than internal
            # editor text.  Preserve every byte for inspection instead of making
            # recovery discovery unusable because the original codec is unknown.
            return self.payload.decode("utf-8", errors="surrogateescape")


@dataclass(frozen=True)
class RecoveryPresence:
    """Cheap filename-only startup truth about journal records.

    Presence checks never decode records or inspect document targets.
    ``truncated`` means ``count`` is a lower bound because the directory or
    record-count budget was reached.
    """

    count: int
    truncated: bool = False


@dataclass(frozen=True)
class RecoveryScan:
    """Bounded explicit inventory returned by recovery listing."""

    candidates: tuple[RecoveryCandidate, ...]
    omitted: int = 0
    corrupt: int = 0
    truncated: bool = False
    comparison_limited: int = 0
    record_bytes_limited: bool = False


@dataclass(frozen=True)
class SaveOutcome:
    entry_id: str
    committed: bool
    recovery_retired: bool
    cleanup_error: Optional[str] = None


@dataclass(frozen=True)
class ModeRepairOutcome:
    entry_id: str
    target: Path
    previous_mode: int
    intended_mode: int
    changed: bool
    file_synced: bool
    directory_synced: bool
    recovery_retired: bool
    recovery_retire_directory_synced: bool
    cleanup_error: Optional[str] = None


@dataclass(frozen=True)
class RecoveryResidue:
    """One bounded, metadata-only private-temp inventory row."""

    residue_id: str
    path: Path
    kind: RecoveryResidueKind
    lease_id: str
    owner: ProcessIdentity
    owner_state: TempOwnerState
    size: int
    mode: int
    uid: int
    nlink: int
    dev: int
    ino: int
    mtime_ns: int
    parent_dev: int
    parent_ino: int
    entry_id: str | None = None
    cleanup_eligible: bool = False
    reason: str = ""


@dataclass(frozen=True)
class RecoveryResidueScan:
    residues: tuple[RecoveryResidue, ...]
    omitted: int = 0
    directory_entries_visited: int = 0
    truncated: bool = False
    records_omitted: int = 0
    record_bytes_limited: bool = False
    unreadable_directories: int = 0


@dataclass(frozen=True)
class ResidueCleanupOutcome:
    residue_id: str
    path: Path
    removed: bool
    directory_synced: bool


@dataclass(frozen=True)
class _RecordAuthority:
    entry_id: str
    buffer_id: str
    target: Path
    created_ns: int
    base: Fingerprint
    commit: Fingerprint
    payload_kind: str
    metadata: dict[str, str]
    payload_size: int
    payload_sha256: str
    path: Path


@dataclass(frozen=True)
class _Record(_RecordAuthority):
    payload: bytes


@dataclass(frozen=True)
class _CheckpointWitness:
    authority: _RecordAuthority
    file_signature: tuple[int, ...]


@dataclass(frozen=True)
class _JournalPath:
    entry_id: str
    path: Path
    mtime_ns: int
    size: int


@dataclass(frozen=True)
class _TargetInspection:
    fingerprint: Fingerprint
    mode: int | None = None
    uid: int | None = None
    nlink: int | None = None
    dev: int | None = None
    ino: int | None = None


@dataclass(frozen=True)
class _ModeRepairContract:
    private_mode: int
    intended_mode: int
    parent_dev: int
    parent_ino: int


BytesLike = Union[bytes, bytearray, memoryview, str]
ContentWriter = Callable[[Path, bytes], None]
FaultInjector = Callable[[str], None]


def default_recovery_root(
    *,
    environ: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the host-owned recovery state directory without creating it.

    ``MICROMAX_RECOVERY_DIR`` is an explicit override.  On Unix-like hosts the
    normal location follows XDG_STATE_HOME (falling back to ``~/.local/state``),
    because recovery must survive application restarts but is not portable user
    data.  A relative XDG_STATE_HOME is ignored as required by the XDG spec.
    """

    env = os.environ if environ is None else environ
    override = str(env.get("MICROMAX_RECOVERY_DIR", "") or "").strip()
    if override:
        return Path(override).expanduser().resolve(strict=False)

    if os.name == "nt":
        local = str(env.get("LOCALAPPDATA", "") or "").strip()
        if local:
            return (Path(local).expanduser() / "Micromax" / "Recovery").resolve(strict=False)

    xdg = str(env.get("XDG_STATE_HOME", "") or "").strip()
    if xdg:
        xdg_path = Path(xdg).expanduser()
        if xdg_path.is_absolute():
            return (xdg_path / "micromax" / "recovery").resolve(strict=False)

    base_home = Path(home).expanduser() if home is not None else Path.home()
    return (base_home / ".local" / "state" / "micromax" / "recovery").resolve(strict=False)


def _bytes(value: BytesLike) -> bytes:
    """Return immutable bytes without copying an already immutable payload."""

    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return bytes(value)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: dict[str, object]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _framed_header_sha256(body: bytes) -> str:
    """Checksum one compact v2 header without concatenating its domain tag."""

    digest = hashlib.sha256()
    digest.update(_FRAMED_HEADER_DIGEST_DOMAIN)
    digest.update(body)
    return digest.hexdigest()


def _strict_json(raw: bytes) -> dict[str, object]:
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise RecoveryCorruptError(f"duplicate JSON field: {key}")
            value[key] = item
        return value

    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise RecoveryCorruptError("journal root must be an object")
    return value


def _canonical_target(path: Union[str, os.PathLike[str]]) -> Path:
    expanded = Path(path).expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    # Resolve parent authority and dot segments, but do not silently follow a
    # final-component symbolic link that could redirect recovery writes.
    return expanded.parent.resolve(strict=False) / expanded.name


def _target_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _inspection_stat_signature(st: os.stat_result) -> tuple[int, ...]:
    """Return metadata that must remain stable across a content inspection."""

    return (
        int(getattr(st, "st_dev", 0) or 0),
        int(getattr(st, "st_ino", 0) or 0),
        int(getattr(st, "st_size", 0) or 0),
        int(getattr(st, "st_mtime_ns", 0) or 0),
        int(getattr(st, "st_ctime_ns", 0) or 0),
        int(getattr(st, "st_mode", 0) or 0),
        int(getattr(st, "st_uid", -1)),
        int(getattr(st, "st_nlink", 0) or 0),
    )


def _inspect_open_target(
    fd: int,
    path: Path,
    max_bytes: int,
    *,
    shared_budget: list[int] | None = None,
) -> _TargetInspection:
    """Hash and stat one already-open, non-redirected target inode.

    The file descriptor pins the inode while the digest is computed.  A second
    ``fstat`` rejects concurrent content or metadata mutation rather than
    returning a digest assembled across two different file states.
    """

    before = os.fstat(fd)
    if not stat.S_ISREG(before.st_mode):
        raise RecoveryConflictError(f"target is not a regular file: {path}")
    if before.st_size > max_bytes:
        raise RecoveryTooLargeError(
            f"target exceeds recovery comparison limit: {before.st_size} bytes"
        )
    reserved = 0
    if shared_budget is not None:
        remaining = int(shared_budget[0])
        if before.st_size > remaining:
            raise RecoveryTooLargeError("recovery inventory comparison budget exhausted")
        shared_budget[0] = remaining - int(before.st_size)
        reserved = int(before.st_size)

    os.lseek(fd, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    size = 0
    while True:
        block = os.read(fd, 1024 * 1024)
        if not block:
            break
        size += len(block)
        if size > max_bytes:
            raise RecoveryTooLargeError(
                f"target exceeds recovery comparison limit: more than {max_bytes} bytes"
            )
        if shared_budget is not None and size > reserved:
            extra = size - reserved
            remaining = int(shared_budget[0])
            if extra > remaining:
                raise RecoveryTooLargeError(
                    "recovery inventory comparison budget exhausted"
                )
            shared_budget[0] = remaining - extra
            reserved = size
        digest.update(block)

    after = os.fstat(fd)
    if _inspection_stat_signature(before) != _inspection_stat_signature(after):
        raise RecoveryConflictError(f"target changed while being inspected: {path}")
    return _TargetInspection(
        fingerprint=Fingerprint(True, size, digest.hexdigest()),
        mode=int(stat.S_IMODE(after.st_mode)),
        uid=int(getattr(after, "st_uid", -1)),
        nlink=int(getattr(after, "st_nlink", 0) or 0),
        dev=int(getattr(after, "st_dev", 0) or 0),
        ino=int(getattr(after, "st_ino", 0) or 0),
    )


def _open_target_no_follow(path: Path) -> int:
    try:
        return os.open(str(path), _target_open_flags())
    except FileNotFoundError:
        raise
    except OSError as exc:
        # ELOOP is the usual O_NOFOLLOW signal.  Recovery must never silently
        # treat a newly introduced symbolic link as the old target.
        if exc.errno == getattr(errno, "ELOOP", None) or path.is_symlink():
            raise RecoveryConflictError(f"target is a symbolic link: {path}") from exc
        raise


def _open_verified_parent(path: Path, contract: _ModeRepairContract) -> int:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        fd = os.open(str(path.parent), flags)
    except OSError as exc:
        raise RecoveryConflictError(
            f"target parent authority is unavailable: {path.parent}"
        ) from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISDIR(st.st_mode):
            raise RecoveryConflictError(
                f"target parent is not a directory: {path.parent}"
            )
        actual = (
            int(getattr(st, "st_dev", 0) or 0),
            int(getattr(st, "st_ino", 0) or 0),
        )
        expected = (contract.parent_dev, contract.parent_ino)
        if actual != expected:
            raise RecoveryConflictError(
                "target parent authority changed after recovery checkpoint"
            )
        return fd
    except Exception:
        os.close(fd)
        raise


def _open_target_at(parent_fd: int, path: Path) -> int:
    try:
        return os.open(path.name, _target_open_flags(), dir_fd=parent_fd)
    except FileNotFoundError:
        raise
    except OSError as exc:
        if exc.errno == getattr(errno, "ELOOP", None):
            raise RecoveryConflictError(f"target is a symbolic link: {path}") from exc
        raise


def _assert_named_target_at(
    parent_fd: int,
    path: Path,
    inspection: _TargetInspection,
    *,
    expected_mode: int | None = None,
) -> None:
    """Require ``path.name`` to still name the fd-inspected regular inode."""

    try:
        named = os.stat(
            path.name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError as exc:
        raise RecoveryConflictError(
            "target authority disappeared during permission repair"
        ) from exc
    if (
        not stat.S_ISREG(named.st_mode)
        or int(getattr(named, "st_dev", 0) or 0) != inspection.dev
        or int(getattr(named, "st_ino", 0) or 0) != inspection.ino
        or (
            inspection.uid is not None
            and int(getattr(named, "st_uid", -1)) != inspection.uid
        )
        or (
            inspection.nlink is not None
            and int(getattr(named, "st_nlink", 0) or 0) != inspection.nlink
        )
    ):
        raise RecoveryConflictError(
            "target authority changed during permission repair"
        )
    if (
        expected_mode is not None
        and int(stat.S_IMODE(named.st_mode)) != int(expected_mode)
    ):
        raise RecoveryConflictError(
            "target mode changed during permission repair"
        )


def _inspect_target_with_contract(
    path: Path,
    contract: _ModeRepairContract,
    max_bytes: int,
    *,
    shared_budget: list[int] | None = None,
) -> _TargetInspection:
    parent_fd = _open_verified_parent(path, contract)
    try:
        try:
            fd = _open_target_at(parent_fd, path)
        except FileNotFoundError:
            return _TargetInspection(Fingerprint(False))
        try:
            return _inspect_open_target(
                fd,
                path,
                max_bytes,
                shared_budget=shared_budget,
            )
        finally:
            os.close(fd)
    finally:
        os.close(parent_fd)


def _inspect_target(
    path: Path,
    max_bytes: int,
    *,
    shared_budget: list[int] | None = None,
) -> _TargetInspection:
    try:
        fd = _open_target_no_follow(path)
    except FileNotFoundError:
        return _TargetInspection(Fingerprint(False))
    try:
        return _inspect_open_target(
            fd,
            path,
            max_bytes,
            shared_budget=shared_budget,
        )
    finally:
        os.close(fd)


def _fingerprint(
    path: Path,
    max_bytes: int,
    *,
    shared_budget: list[int] | None = None,
) -> Fingerprint:
    """Compatibility content view over the fd-bound target inspector."""

    return _inspect_target(
        path,
        max_bytes,
        shared_budget=shared_budget,
    ).fingerprint


def _open_regular_bounded(path: Path, max_bytes: int) -> tuple[int, int]:
    """Open one bounded regular record without following the final component."""

    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        fd = os.open(str(path), flags)
    except FileNotFoundError:
        raise
    except OSError as exc:
        if path.is_symlink():
            raise RecoveryCorruptError("journal entry is a symbolic link") from exc
        raise RecoveryCorruptError("journal record is unreadable") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise RecoveryCorruptError("journal entry is not a regular file")
        if st.st_size > max_bytes:
            raise RecoveryTooLargeError("journal record exceeds bounded read limit")
        return fd, max(0, int(st.st_size))
    except BaseException:
        os.close(fd)
        raise


def _read_exact(stream: BinaryIO, size: int, *, label: str) -> bytes:
    """Read exactly ``size`` bytes, copying only after an exceptional short read."""

    if size < 0:
        raise RecoveryCorruptError(f"invalid {label} size")
    first = stream.read(size)
    if len(first) == size:
        return first
    chunks = [first]
    remaining = size - len(first)
    while remaining:
        block = stream.read(remaining)
        if not block:
            raise RecoveryCorruptError(f"truncated {label}")
        chunks.append(block)
        remaining -= len(block)
    return b"".join(chunks)


def _hash_exact(stream: BinaryIO, size: int, *, label: str) -> str:
    """Hash exactly ``size`` bytes with bounded transient allocation."""

    if size < 0:
        raise RecoveryCorruptError(f"invalid {label} size")
    digest = hashlib.sha256()
    remaining = size
    while remaining:
        block = stream.read(min(1024 * 1024, remaining))
        if not block:
            raise RecoveryCorruptError(f"truncated {label}")
        digest.update(block)
        remaining -= len(block)
    return digest.hexdigest()


def _read_regular_bounded(path: Path, max_bytes: int) -> bytes:
    """Read one journal record without following a final-component symlink."""

    fd, size = _open_regular_bounded(path, max_bytes)
    try:
        with os.fdopen(fd, "rb", closefd=True) as stream:
            fd = -1
            return _read_exact(stream, size, label="journal record")
    finally:
        if fd >= 0:
            os.close(fd)


def _record_file_signature(path: Path, max_bytes: int) -> tuple[int, ...]:
    """Return no-follow inode/content metadata for a just-published record."""

    fd, _size = _open_regular_bounded(path, max_bytes)
    try:
        return _inspection_stat_signature(os.fstat(fd))
    finally:
        os.close(fd)


def _publication_identity(signature: tuple[int, ...]) -> tuple[int, ...]:
    """Select inode fields expected to survive publishing a private temp.

    Renaming may advance ctime on some hosts, so the pre-publish temp and the
    final pathname are bound by device/inode, exact size and mtime, ownership,
    mode, and link count.  The complete post-publish signature still guards the
    later fast path against any subsequent content or metadata change.
    """

    return (
        signature[0],  # st_dev
        signature[1],  # st_ino
        signature[2],  # st_size
        signature[3],  # st_mtime_ns
        signature[5],  # st_mode
        signature[6],  # st_uid
        signature[7],  # st_nlink
    )


def _same_content(left: Fingerprint, right: Fingerprint) -> bool:
    return left.exists == right.exists and (
        not left.exists
        or (left.size == right.size and left.sha256 == right.sha256)
    )


def _parse_octal_mode(value: str, *, label: str) -> int:
    raw = str(value or "")
    if len(raw) != 4 or any(char not in "01234567" for char in raw):
        raise RecoveryCorruptError(f"invalid {label}")
    mode = int(raw, 8)
    if mode < 0 or mode > 0o7777:
        raise RecoveryCorruptError(f"invalid {label}")
    return mode


def _parse_identity_number(value: str, *, label: str) -> int:
    raw = str(value or "")
    if not raw or not raw.isdigit() or len(raw) > 32:
        raise RecoveryCorruptError(f"invalid {label}")
    number = int(raw, 10)
    if number < 0:
        raise RecoveryCorruptError(f"invalid {label}")
    return number


def _mode_repair_modes(metadata: Mapping[str, str]) -> _ModeRepairContract | None:
    """Return the fd-bound permission contract recorded before atomic save."""

    contract = str(metadata.get("mode_repair_contract") or "")
    if contract != MODE_REPAIR_CONTRACT_V1:
        return None
    private_mode = _parse_octal_mode(
        str(metadata.get("private_commit_mode") or ""),
        label="private commit mode",
    )
    intended_mode = _parse_octal_mode(
        str(metadata.get("intended_mode") or ""),
        label="intended commit mode",
    )
    if private_mode != PRIVATE_ATOMIC_COMMIT_MODE:
        raise RecoveryCorruptError("invalid private atomic commit mode")
    return _ModeRepairContract(
        private_mode=private_mode,
        intended_mode=intended_mode,
        parent_dev=_parse_identity_number(
            str(metadata.get("target_parent_dev") or ""),
            label="mode repair parent device",
        ),
        parent_ino=_parse_identity_number(
            str(metadata.get("target_parent_ino") or ""),
            label="mode repair parent inode",
        ),
    )


def _mode_repair_authority_error(inspection: _TargetInspection) -> str | None:
    if (
        not _MODE_REPAIR_DIRFD_SUPPORTED
        or not hasattr(os, "fchmod")
        or not hasattr(os, "geteuid")
    ):
        return "host cannot verify and repair POSIX file permissions"
    if inspection.uid != int(os.geteuid()):
        return "target is not owned by the current effective user"
    if inspection.nlink != 1:
        return "target inode has multiple hard links"
    return None


def _metadata_decimal(metadata: Mapping[str, str], key: str) -> int | None:
    raw = str(metadata.get(key) or "")
    if not raw or not raw.isdigit():
        return None
    try:
        value = int(raw, 10)
    except ValueError:
        return None
    return value if value >= 0 else None


def _residue_identity(
    *,
    kind: RecoveryResidueKind,
    parent_dev: int,
    parent_ino: int,
    name: str,
    st: os.stat_result,
) -> str:
    fields = (
        kind.value,
        str(int(parent_dev)),
        str(int(parent_ino)),
        str(name),
        str(int(getattr(st, "st_dev", 0) or 0)),
        str(int(getattr(st, "st_ino", 0) or 0)),
        str(int(getattr(st, "st_size", 0) or 0)),
        str(int(getattr(st, "st_mtime_ns", 0) or 0)),
        str(int(getattr(st, "st_mode", 0) or 0)),
        str(int(getattr(st, "st_uid", -1))),
        str(int(getattr(st, "st_nlink", 0) or 0)),
    )
    return hashlib.sha256("\0".join(fields).encode("utf-8")).hexdigest()


def _residue_cleanup_reason(
    *,
    st: os.stat_result,
    owner_state: TempOwnerState,
) -> str:
    if not _SAFE_RESIDUE_UNLINK:
        return "descriptor-relative no-follow unlink is unavailable"
    if not stat.S_ISREG(st.st_mode):
        return "entry is not a regular file"
    if int(stat.S_IMODE(st.st_mode)) != 0o600:
        return "entry is not owner-only mode 0600"
    if not hasattr(os, "geteuid"):
        return "host cannot verify current file ownership"
    if int(getattr(st, "st_uid", -1)) != int(os.geteuid()):
        return "entry is not owned by the current effective user"
    if int(getattr(st, "st_nlink", 0) or 0) != 1:
        return "entry inode has multiple hard links"
    if owner_state is TempOwnerState.ACTIVE:
        return "creator process is still active"
    if owner_state is TempOwnerState.UNKNOWN:
        return "creator process identity cannot be disproved"
    return ""


def _residue_row(
    *,
    parent: Path,
    parent_st: os.stat_result,
    name: str,
    st: os.stat_result,
    kind: RecoveryResidueKind,
    entry_id: str | None = None,
) -> RecoveryResidue | None:
    parsed = parse_private_temp_name(name)
    if parsed is None:
        return None
    owner_state = temp_owner_state(parsed.owner)
    reason = _residue_cleanup_reason(st=st, owner_state=owner_state)
    parent_dev = int(getattr(parent_st, "st_dev", 0) or 0)
    parent_ino = int(getattr(parent_st, "st_ino", 0) or 0)
    return RecoveryResidue(
        residue_id=_residue_identity(
            kind=kind,
            parent_dev=parent_dev,
            parent_ino=parent_ino,
            name=name,
            st=st,
        ),
        path=parent / name,
        kind=kind,
        lease_id=parsed.lease_id,
        owner=parsed.owner,
        owner_state=owner_state,
        size=max(0, int(getattr(st, "st_size", 0) or 0)),
        mode=int(stat.S_IMODE(st.st_mode)),
        uid=int(getattr(st, "st_uid", -1)),
        nlink=int(getattr(st, "st_nlink", 0) or 0),
        dev=int(getattr(st, "st_dev", 0) or 0),
        ino=int(getattr(st, "st_ino", 0) or 0),
        mtime_ns=int(getattr(st, "st_mtime_ns", 0) or 0),
        parent_dev=parent_dev,
        parent_ino=parent_ino,
        entry_id=entry_id,
        cleanup_eligible=not reason,
        reason=reason,
    )


def _directory_sync_is_unsupported(exc: OSError) -> bool:
    """Distinguish unavailable directory synchronization from real I/O loss."""

    return exc.errno in _UNSUPPORTED_DIRECTORY_SYNC_ERRNOS


def _fsync_dir(directory: Path) -> bool:
    if not hasattr(os, "O_DIRECTORY"):
        return False
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY")
    try:
        fd = os.open(str(directory), flags)
    except OSError as exc:
        if _directory_sync_is_unsupported(exc):
            return False
        raise
    try:
        try:
            os.fsync(fd)
        except OSError as exc:
            if _directory_sync_is_unsupported(exc):
                return False
            raise
        return True
    finally:
        os.close(fd)


def _fsync_dir_fd(fd: int) -> bool:
    try:
        os.fsync(fd)
    except OSError as exc:
        if _directory_sync_is_unsupported(exc):
            return False
        raise
    return True


def _open_directory_no_follow(directory: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_DIRECTORY"):
        flags |= getattr(os, "O_DIRECTORY")
    if hasattr(os, "O_NOFOLLOW"):
        flags |= getattr(os, "O_NOFOLLOW")
    return os.open(str(directory), flags)


def _directory_identity(directory: Path) -> tuple[int, int]:
    fd = _open_directory_no_follow(directory)
    try:
        st = os.fstat(fd)
        if not stat.S_ISDIR(st.st_mode):
            raise NotADirectoryError(str(directory))
        return (
            int(getattr(st, "st_dev", 0) or 0),
            int(getattr(st, "st_ino", 0) or 0),
        )
    finally:
        os.close(fd)


def _write_all(stream: BinaryIO, data: bytes) -> None:
    """Write one bytes object completely without materializing a remainder."""

    view = memoryview(data)
    try:
        offset = 0
        while offset < len(view):
            written = stream.write(view[offset:])
            if written is None or written <= 0:
                raise OSError("journal writer made no forward progress")
            offset += int(written)
    finally:
        view.release()


def _private_atomic_write_parts(
    path: Path,
    parts: Iterable[bytes],
    *,
    fault: FaultInjector | None = None,
    lease_id: str | None = None,
) -> tuple[bool, bool, tuple[int, ...]]:
    """Durably publish bounded parts and return the exact published signature."""

    inject = fault or (lambda _stage: None)
    file_synced = False
    directory_synced = False
    temp_signature: tuple[int, ...] | None = None
    written_bytes = 0
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(path.parent, 0o700)
    except OSError:
        pass
    fd = -1
    temp: Path | None = None
    with private_temp_lease(lease_id):
        for _ in range(128):
            candidate = path.parent / build_private_temp_name(path.parent, path.name)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
            try:
                fd = os.open(str(candidate), flags, 0o600)
                temp = candidate
                break
            except FileExistsError:
                continue
    if fd < 0 or temp is None:
        raise FileExistsError(
            f"could not create a unique recovery temp in {path.parent}"
        )
    fd_open = True
    try:
        inject("checkpoint_temp_created")
        try:
            os.fchmod(fd, 0o600)
        except OSError:
            pass
        with os.fdopen(fd, "wb", closefd=True) as stream:
            fd_open = False
            for part in parts:
                _write_all(stream, part)
                written_bytes += len(part)
            stream.flush()
            os.fsync(stream.fileno())
            file_synced = True
            temp_signature = _inspection_stat_signature(os.fstat(stream.fileno()))
        inject("checkpoint_temp_synced")
        inject("before_checkpoint_replace")
        os.replace(temp, path)
        inject("after_checkpoint_replace")
        # ``mkstemp`` plus the pre-write ``fchmod`` already made the inode
        # private.  Do not mutate its metadata after the file fsync; otherwise
        # the completion witness would not cover the final published mode.
        directory_synced = _fsync_dir(path.parent)
        inject("after_checkpoint_directory_sync")
        if temp_signature is None:
            raise RecoveryError("recovery temp synchronization produced no witness")
        published_signature = _record_file_signature(path, written_bytes)
        if _publication_identity(published_signature) != _publication_identity(
            temp_signature
        ):
            raise RecoveryConflictError(
                "published recovery inode does not match the fsynced temp"
            )
    except BaseException:
        if fd_open:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise
    return file_synced, directory_synced, published_signature


def _private_atomic_write(
    path: Path,
    data: bytes,
    *,
    fault: FaultInjector | None = None,
    lease_id: str | None = None,
) -> tuple[bool, bool]:
    """Compatibility one-part wrapper around the streaming atomic writer."""

    file_synced, directory_synced, _signature = _private_atomic_write_parts(
        path,
        (data,),
        fault=fault,
        lease_id=lease_id,
    )
    return file_synced, directory_synced


def _normalize_metadata(metadata: Mapping[str, object] | None) -> dict[str, str]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise ValueError("recovery metadata must be a mapping")
    if len(metadata) > _METADATA_MAX_FIELDS:
        raise ValueError(f"recovery metadata exceeds {_METADATA_MAX_FIELDS} fields")
    normalized: dict[str, str] = {}
    total = 0
    for key, value in metadata.items():
        if not isinstance(key, str) or not key or len(key.encode("utf-8")) > 128:
            raise ValueError("recovery metadata key is empty or too large")
        if not isinstance(value, str):
            raise ValueError("recovery metadata values must be strings")
        total += len(key.encode("utf-8")) + len(
            value.encode("utf-8", errors="surrogatepass")
        )
        if total > _METADATA_MAX_BYTES:
            raise ValueError(f"recovery metadata exceeds {_METADATA_MAX_BYTES} bytes")
        normalized[key] = value
    return normalized


def _checkpoint_parent_identity(
    metadata: Mapping[str, object],
) -> tuple[int, int] | None:
    """Return caller-pinned parent authority, requiring a complete pair.

    Atomic saves plan their final mode and parent inode before publishing the
    recovery record.  The journal must preserve that exact authority rather
    than replacing it with whichever directory the pathname happens to resolve
    to a few instructions later.
    """

    dev_raw = metadata.get("target_parent_dev")
    ino_raw = metadata.get("target_parent_ino")
    if dev_raw is None and ino_raw is None:
        return None
    if dev_raw is None or ino_raw is None:
        raise ValueError("recovery target parent identity is incomplete")
    if not isinstance(dev_raw, str) or not isinstance(ino_raw, str):
        raise ValueError("recovery target parent identity must be decimal strings")
    if (
        not dev_raw
        or not ino_raw
        or not dev_raw.isdigit()
        or not ino_raw.isdigit()
        or len(dev_raw) > 32
        or len(ino_raw) > 32
    ):
        raise ValueError("recovery target parent identity is invalid")
    return int(dev_raw, 10), int(ino_raw, 10)


def _read_metadata(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict) or len(value) > _METADATA_MAX_FIELDS:
        raise RecoveryCorruptError("invalid recovery metadata")
    normalized: dict[str, str] = {}
    total = 0
    for key, item in value.items():
        if not isinstance(key, str) or not key or not isinstance(item, str):
            raise RecoveryCorruptError("recovery metadata must contain string fields")
        total += len(key.encode("utf-8")) + len(item.encode("utf-8", errors="surrogatepass"))
        if total > _METADATA_MAX_BYTES:
            raise RecoveryCorruptError("recovery metadata exceeds bounded read limit")
        normalized[key] = item
    return normalized


class RecoveryJournal:
    def __init__(
        self,
        root: Union[str, os.PathLike[str]],
        *,
        max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES,
        max_comparison_bytes: int | None = None,
        max_scan_records: int = DEFAULT_MAX_SCAN_RECORDS,
        max_scan_directory_entries: int = DEFAULT_MAX_SCAN_DIRECTORY_ENTRIES,
        max_scan_record_bytes: int = DEFAULT_MAX_SCAN_RECORD_BYTES,
        max_scan_comparison_bytes: int = DEFAULT_MAX_SCAN_COMPARISON_BYTES,
        max_residue_files: int = DEFAULT_MAX_RESIDUE_FILES,
        max_residue_directory_entries: int = DEFAULT_MAX_RESIDUE_DIRECTORY_ENTRIES,
        journal_writer: Optional[ContentWriter] = None,
        fault: Optional[FaultInjector] = None,
    ) -> None:
        if max_payload_bytes <= 0:
            raise ValueError("max_payload_bytes must be positive")
        comparison_limit = max_payload_bytes if max_comparison_bytes is None else int(max_comparison_bytes)
        if comparison_limit <= 0:
            raise ValueError("max_comparison_bytes must be positive")
        if int(max_scan_records) <= 0:
            raise ValueError("max_scan_records must be positive")
        if int(max_scan_directory_entries) <= 0:
            raise ValueError("max_scan_directory_entries must be positive")
        if int(max_scan_record_bytes) <= 0:
            raise ValueError("max_scan_record_bytes must be positive")
        if int(max_scan_comparison_bytes) <= 0:
            raise ValueError("max_scan_comparison_bytes must be positive")
        if int(max_residue_files) <= 0:
            raise ValueError("max_residue_files must be positive")
        if int(max_residue_directory_entries) <= 0:
            raise ValueError("max_residue_directory_entries must be positive")
        self.root = Path(root).expanduser().resolve(strict=False)
        self.max_payload_bytes = int(max_payload_bytes)
        self.max_comparison_bytes = comparison_limit
        self.max_scan_records = int(max_scan_records)
        self.max_scan_directory_entries = int(max_scan_directory_entries)
        self.max_scan_record_bytes = int(max_scan_record_bytes)
        self.max_scan_comparison_bytes = int(max_scan_comparison_bytes)
        self.max_residue_files = int(max_residue_files)
        self.max_residue_directory_entries = int(max_residue_directory_entries)
        self._record_limit = self.max_payload_bytes * 2 + 128 * 1024
        self._journal_writer = journal_writer
        self._fault = fault or (lambda _stage: None)
        self._checkpoint_witnesses: dict[str, _CheckpointWitness] = {}
        self._last_checkpoint_file_synced = False
        self._last_checkpoint_directory_synced = False
        self._last_dismiss_directory_synced = False
        # Construction and startup discovery remain read-only.  The private
        # state directory is created only when the first checkpoint is written.

    @property
    def last_checkpoint_file_synced(self) -> bool:
        """Whether the most recent default checkpoint writer completed file fsync."""

        return self._last_checkpoint_file_synced

    @property
    def last_checkpoint_directory_synced(self) -> bool:
        """Whether the most recent checkpoint published a synced directory entry."""

        return self._last_checkpoint_directory_synced

    @property
    def last_dismiss_directory_synced(self) -> bool:
        """Whether the most recent dismissal synced the journal directory."""

        return self._last_dismiss_directory_synced

    def _read_root_exists(self) -> bool:
        """Return whether the recovery root exists and still has directory authority."""

        try:
            mode = self.root.lstat().st_mode
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise RecoveryError(f"could not inspect recovery journal root: {exc}") from exc
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise RecoveryCorruptError(
                "recovery journal root is not a trusted directory"
            )
        return True

    def _id(self, target: Path, buffer_id: str) -> str:
        material = (str(target) + "\0" + buffer_id).encode("utf-8", "surrogatepass")
        return hashlib.sha256(material).hexdigest()

    def _entry_path(self, entry_id: str) -> Path:
        if len(entry_id) != 64 or any(c not in "0123456789abcdef" for c in entry_id):
            raise RecoveryCorruptError("invalid recovery entry id")
        path = self.root / f"{entry_id}{_RECORD_SUFFIX}"
        if path.parent.resolve(strict=False) != self.root:
            raise RecoveryCorruptError("journal path escaped recovery root")
        return path

    @staticmethod
    def _entry_id_from_name(name: str) -> str | None:
        raw = str(name)
        if not raw.endswith(_RECORD_SUFFIX):
            return None
        entry_id = raw[: -len(_RECORD_SUFFIX)]
        if len(entry_id) != 64 or any(c not in "0123456789abcdef" for c in entry_id):
            return None
        return entry_id

    def presence(self) -> RecoveryPresence:
        """Return bounded filename-only startup truth.

        Startup must not decode private records or hash arbitrary document
        targets.  The explicit recovery inventory performs those heavier checks
        when the user asks for them.
        """

        if not self._read_root_exists():
            return RecoveryPresence(0, False)
        count = 0
        visited = 0
        try:
            with os.scandir(self.root) as entries:
                for entry in entries:
                    visited += 1
                    if visited > self.max_scan_directory_entries:
                        return RecoveryPresence(count=count, truncated=True)
                    if self._entry_id_from_name(entry.name) is None:
                        continue
                    count += 1
                    if count > self.max_scan_records:
                        return RecoveryPresence(
                            count=self.max_scan_records,
                            truncated=True,
                        )
        except FileNotFoundError:
            return RecoveryPresence(0, False)
        except OSError as exc:
            raise RecoveryError(f"could not scan recovery journal: {exc}") from exc
        return RecoveryPresence(count=count, truncated=False)

    def _bounded_record_paths(self) -> tuple[list[_JournalPath], int, bool]:
        """Select the newest record paths with bounded traversal and memory."""

        if not self._read_root_exists():
            return [], 0, False
        heap: list[tuple[int, str, _JournalPath]] = []
        matching = 0
        visited = 0
        truncated = False
        try:
            with os.scandir(self.root) as entries:
                for entry in entries:
                    visited += 1
                    if visited > self.max_scan_directory_entries:
                        truncated = True
                        break
                    entry_id = self._entry_id_from_name(entry.name)
                    if entry_id is None:
                        continue
                    matching += 1
                    try:
                        st = entry.stat(follow_symlinks=False)
                        mtime_ns = int(getattr(st, "st_mtime_ns", 0) or 0)
                        size = max(0, int(getattr(st, "st_size", 0) or 0))
                    except OSError:
                        # Retain the row so normal validation can expose or
                        # quarantine it instead of silently hiding it.
                        mtime_ns = 0
                        size = 0
                    row = _JournalPath(
                        entry_id=entry_id,
                        path=self.root / entry.name,
                        mtime_ns=mtime_ns,
                        size=size,
                    )
                    item = (mtime_ns, entry.name, row)
                    if len(heap) < self.max_scan_records:
                        heapq.heappush(heap, item)
                    elif item[:2] > heap[0][:2]:
                        heapq.heapreplace(heap, item)
        except FileNotFoundError:
            return [], 0, False
        except OSError as exc:
            raise RecoveryError(f"could not scan recovery journal: {exc}") from exc

        selected = [item[2] for item in sorted(heap, reverse=True)]
        omitted = max(0, matching - len(selected))
        return selected, omitted, truncated

    def checkpoint(
        self,
        target: Union[str, os.PathLike[str]],
        content: BytesLike,
        *,
        buffer_id: str = "default",
        commit_content: BytesLike | None = None,
        payload_kind: str = PAYLOAD_KIND_BYTES,
        metadata: Mapping[str, object] | None = None,
    ) -> str:
        """Persist one exact recovery payload before the normal document write.

        ``content`` is what recovery must give back to the editor.  The optional
        ``commit_content`` is the separately encoded/normalized byte sequence the
        save writer intends to commit.  Keeping those identities separate fixes a
        subtle data-loss bug: trailing-space/EOF/line-ending normalization must
        never replace the exact unsaved buffer text in the recovery record.
        """

        # Witnesses describe this attempt, never an earlier successful call.
        self._last_checkpoint_file_synced = False
        self._last_checkpoint_directory_synced = False
        if not isinstance(buffer_id, str) or not buffer_id or len(buffer_id.encode("utf-8")) > 1024:
            raise ValueError("buffer_id must be a non-empty string of at most 1024 bytes")
        kind = str(payload_kind or "").strip()
        if not kind or len(kind.encode("utf-8")) > 128:
            raise ValueError("payload_kind must be a short non-empty string")
        payload = _bytes(content)
        commit_payload = payload if commit_content is None else _bytes(commit_content)
        if len(payload) > self.max_payload_bytes:
            raise RecoveryTooLargeError(f"payload exceeds {self.max_payload_bytes} bytes")
        if len(commit_payload) > self.max_comparison_bytes:
            raise RecoveryTooLargeError(
                f"commit payload exceeds {self.max_comparison_bytes} comparison bytes"
            )
        canonical = _canonical_target(target)
        if metadata is None:
            enriched_metadata: dict[str, object] = {}
        elif isinstance(metadata, Mapping):
            enriched_metadata = dict(metadata)
        else:
            raise ValueError("recovery metadata must be a mapping")
        lease_id = normalize_save_lease_id(
            str(enriched_metadata.get("save_lease_id") or ""),
            create=True,
        )
        assert lease_id is not None
        enriched_metadata["save_lease_id"] = lease_id
        expected_parent = _checkpoint_parent_identity(enriched_metadata)
        try:
            parent_dev, parent_ino = _directory_identity(canonical.parent)
        except OSError as exc:
            if expected_parent is not None:
                raise RecoveryConflictError(
                    "target parent authority became unavailable before recovery "
                    "checkpoint"
                ) from exc
            # The checkpoint may still be useful for a missing/uncreatable
            # target.  Absence of parent authority evidence only disables
            # future document-temp cleanup; it does not weaken text recovery.
            enriched_metadata.pop("target_parent_dev", None)
            enriched_metadata.pop("target_parent_ino", None)
        else:
            actual_parent = (int(parent_dev), int(parent_ino))
            if expected_parent is not None and actual_parent != expected_parent:
                raise RecoveryConflictError(
                    "target parent authority changed before recovery checkpoint"
                )
            enriched_metadata["target_parent_dev"] = str(parent_dev)
            enriched_metadata["target_parent_ino"] = str(parent_ino)
        normalized_metadata = _normalize_metadata(enriched_metadata)
        # Validate an opted-in permission contract before durable publication.
        # Discovery must never need to quarantine a record produced by this
        # implementation merely because its transaction metadata was partial.
        mode_contract = _mode_repair_modes(normalized_metadata)
        if mode_contract is not None and _MODE_REPAIR_DIRFD_SUPPORTED:
            base_fingerprint = _inspect_target_with_contract(
                canonical,
                mode_contract,
                self.max_comparison_bytes,
            ).fingerprint
        else:
            base_fingerprint = _fingerprint(
                canonical,
                self.max_comparison_bytes,
            )
        entry_id = self._id(canonical, buffer_id)
        entry_path = self._entry_path(entry_id)
        created_ns = time.time_ns()
        payload_sha256 = _sha256(payload)
        commit_fingerprint = (
            Fingerprint(True, len(payload), payload_sha256)
            if commit_payload is payload
            else Fingerprint.for_bytes(commit_payload)
        )
        body: dict[str, object] = {
            "schema": FRAMED_SCHEMA,
            "entry_id": entry_id,
            "buffer_id": buffer_id,
            "target": str(canonical),
            "created_ns": created_ns,
            "base": base_fingerprint.to_json(),
            "commit": commit_fingerprint.to_json(),
            "payload_kind": kind,
            "metadata": normalized_metadata,
            "payload": {
                "encoding": _FRAMED_PAYLOAD_ENCODING,
                "size": len(payload),
                "sha256": payload_sha256,
            },
        }
        body_bytes = _canonical_json(body)
        record = dict(body)
        record["record_sha256"] = _framed_header_sha256(body_bytes)
        header = _canonical_json(record)
        if len(header) > _FRAMED_HEADER_MAX_BYTES:
            raise RecoveryTooLargeError("recovery header exceeds bounded write limit")
        parts = (
            _FRAMED_RECORD_MAGIC,
            _FRAMED_HEADER_LENGTH.pack(len(header)),
            header,
            payload,
        )
        if sum(len(part) for part in parts) > self._record_limit:
            raise RecoveryTooLargeError("journal record exceeds bounded write limit")
        # A failed replacement must never leave authority for an older in-memory
        # witness under the same deterministic entry id.
        self._checkpoint_witnesses.pop(entry_id, None)
        self._fault("before_checkpoint_write")
        published_signature: tuple[int, ...] | None = None
        if self._journal_writer is None:
            (
                self._last_checkpoint_file_synced,
                self._last_checkpoint_directory_synced,
                published_signature,
            ) = _private_atomic_write_parts(
                entry_path,
                parts,
                fault=self._fault,
                lease_id=lease_id,
            )
        else:
            # The injection seam retains its historical bytes callback.  Normal
            # checkpointing never joins these parts and therefore never copies
            # the raw payload merely to hand it to the private atomic writer.
            self._journal_writer(entry_path, b"".join(parts))
        self._fault("after_checkpoint_write")
        if published_signature is not None:
            current_signature = _record_file_signature(
                entry_path,
                self._record_limit,
            )
            if current_signature != published_signature:
                raise RecoveryConflictError(
                    "recovery record changed after checkpoint publication"
                )
            authority = _RecordAuthority(
                entry_id=entry_id,
                buffer_id=buffer_id,
                target=canonical,
                created_ns=created_ns,
                base=base_fingerprint,
                commit=commit_fingerprint,
                payload_kind=kind,
                metadata=dict(normalized_metadata),
                payload_size=len(payload),
                payload_sha256=payload_sha256,
                path=entry_path,
            )
            self._checkpoint_witnesses[entry_id] = _CheckpointWitness(
                authority=authority,
                file_signature=published_signature,
            )
        return entry_id

    def _authority_from_value(
        self,
        value: dict[str, object],
        *,
        entry_id: str,
        path: Path,
        payload_size: int,
        payload_sha256: str,
    ) -> _RecordAuthority:
        """Validate shared record authority after format-specific payload proof."""

        if value.get("entry_id") != entry_id:
            raise RecoveryCorruptError("entry id mismatch")
        target_raw = value.get("target")
        buffer_id = value.get("buffer_id")
        created_ns = value.get("created_ns")
        if (
            not isinstance(target_raw, str)
            or not isinstance(buffer_id, str)
            or not buffer_id
            or not isinstance(created_ns, int)
            or isinstance(created_ns, bool)
            or created_ns < 0
        ):
            raise RecoveryCorruptError("invalid journal metadata")
        target = _canonical_target(target_raw)
        if self._id(target, buffer_id) != entry_id:
            raise RecoveryCorruptError("entry authority mismatch")

        base = Fingerprint.from_json(value.get("base"), label="base fingerprint")
        # Backward compatibility for rev0959 records: when no separate commit
        # identity exists, the journal payload was also the intended disk bytes.
        commit_raw = value.get("commit")
        commit = (
            Fingerprint(True, payload_size, payload_sha256)
            if commit_raw is None
            else Fingerprint.from_json(commit_raw, label="commit fingerprint")
        )
        payload_kind_raw = value.get("payload_kind", PAYLOAD_KIND_BYTES)
        if (
            not isinstance(payload_kind_raw, str)
            or not payload_kind_raw
            or len(payload_kind_raw.encode("utf-8")) > 128
        ):
            raise RecoveryCorruptError("invalid payload kind")
        metadata = _read_metadata(value.get("metadata"))
        return _RecordAuthority(
            entry_id=entry_id,
            buffer_id=buffer_id,
            target=target,
            created_ns=created_ns,
            base=base,
            commit=commit,
            payload_kind=payload_kind_raw,
            metadata=metadata,
            payload_size=payload_size,
            payload_sha256=payload_sha256,
            path=path,
        )

    @staticmethod
    def _record_with_payload(
        authority: _RecordAuthority,
        payload: bytes,
    ) -> _Record:
        return _Record(
            entry_id=authority.entry_id,
            buffer_id=authority.buffer_id,
            target=authority.target,
            created_ns=authority.created_ns,
            base=authority.base,
            commit=authority.commit,
            payload_kind=authority.payload_kind,
            metadata=authority.metadata,
            payload_size=authority.payload_size,
            payload_sha256=authority.payload_sha256,
            path=authority.path,
            payload=payload,
        )

    def _read_legacy_record(
        self,
        raw: bytes,
        *,
        entry_id: str,
        path: Path,
    ) -> _Record:
        """Read the rev0959-rev0995 JSON/base64 format for compatibility."""

        try:
            value = _strict_json(raw)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise RecoveryCorruptError("journal record is unreadable") from exc
        if value.get("schema") != SCHEMA:
            raise RecoveryCorruptError("unsupported recovery schema")
        checksum = value.pop("record_sha256", None)
        if not isinstance(checksum, str) or checksum != _sha256(
            _canonical_json(value)
        ):
            raise RecoveryCorruptError("journal record checksum mismatch")
        payload_envelope = value.get("payload")
        if (
            not isinstance(payload_envelope, dict)
            or payload_envelope.get("encoding") != "base64"
        ):
            raise RecoveryCorruptError("invalid payload envelope")
        size = payload_envelope.get("size")
        digest = payload_envelope.get("sha256")
        encoded = payload_envelope.get("data")
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
            or size > self.max_payload_bytes
        ):
            raise RecoveryTooLargeError("invalid or oversized payload")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
            or not isinstance(encoded, str)
        ):
            raise RecoveryCorruptError("invalid payload metadata")
        if len(encoded) > ((self.max_payload_bytes + 2) // 3) * 4:
            raise RecoveryTooLargeError(
                "encoded payload exceeds bounded decode limit"
            )
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise RecoveryCorruptError("payload base64 is invalid") from exc
        if len(decoded) != size or _sha256(decoded) != digest:
            raise RecoveryCorruptError("payload integrity check failed")
        authority = self._authority_from_value(
            value,
            entry_id=entry_id,
            path=path,
            payload_size=size,
            payload_sha256=digest,
        )
        return self._record_with_payload(authority, decoded)

    def _read_framed_record(
        self,
        stream: BinaryIO,
        *,
        file_size: int,
        entry_id: str,
        path: Path,
        load_payload: bool,
    ) -> _RecordAuthority:
        """Verify one v2 compact header and exact raw payload tail."""

        length_raw = _read_exact(
            stream,
            _FRAMED_HEADER_LENGTH.size,
            label="recovery header length",
        )
        (header_size,) = _FRAMED_HEADER_LENGTH.unpack(length_raw)
        if header_size <= 0:
            raise RecoveryCorruptError("invalid recovery header size")
        if header_size > _FRAMED_HEADER_MAX_BYTES:
            raise RecoveryTooLargeError(
                "recovery header exceeds bounded read limit"
            )
        header = _read_exact(stream, header_size, label="recovery header")
        try:
            value = _strict_json(header)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise RecoveryCorruptError("recovery header is unreadable") from exc
        if value.get("schema") != FRAMED_SCHEMA:
            raise RecoveryCorruptError("unsupported recovery schema")
        checksum = value.pop("record_sha256", None)
        if not isinstance(checksum, str) or checksum != _framed_header_sha256(
            _canonical_json(value)
        ):
            raise RecoveryCorruptError("journal record checksum mismatch")

        payload_envelope = value.get("payload")
        if (
            not isinstance(payload_envelope, dict)
            or payload_envelope.get("encoding") != _FRAMED_PAYLOAD_ENCODING
        ):
            raise RecoveryCorruptError("invalid payload envelope")
        size = payload_envelope.get("size")
        digest = payload_envelope.get("sha256")
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
            or size > self.max_payload_bytes
        ):
            raise RecoveryTooLargeError("invalid or oversized payload")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise RecoveryCorruptError("invalid payload metadata")

        expected_size = (
            len(_FRAMED_RECORD_MAGIC)
            + _FRAMED_HEADER_LENGTH.size
            + header_size
            + size
        )
        if file_size != expected_size:
            raise RecoveryCorruptError(
                "framed recovery size does not match its header"
            )
        if load_payload:
            payload = _read_exact(stream, size, label="recovery payload")
            actual_digest = _sha256(payload)
        else:
            payload = None
            actual_digest = _hash_exact(
                stream,
                size,
                label="recovery payload",
            )
        if stream.read(1):
            raise RecoveryCorruptError("framed recovery has trailing bytes")
        if actual_digest != digest:
            raise RecoveryCorruptError("payload integrity check failed")
        authority = self._authority_from_value(
            value,
            entry_id=entry_id,
            path=path,
            payload_size=size,
            payload_sha256=digest,
        )
        if payload is None:
            return authority
        return self._record_with_payload(authority, payload)

    def _read_entry(
        self,
        entry_id: str,
        *,
        load_payload: bool,
    ) -> _RecordAuthority:
        path = self._entry_path(entry_id)
        try:
            fd, file_size = _open_regular_bounded(path, self._record_limit)
        except FileNotFoundError as exc:
            raise RecoveryError(f"recovery entry not found: {entry_id}") from exc
        try:
            with os.fdopen(fd, "rb", closefd=True) as stream:
                fd = -1
                prefix = stream.read(len(_FRAMED_RECORD_MAGIC))
                if prefix == _FRAMED_RECORD_MAGIC:
                    return self._read_framed_record(
                        stream,
                        file_size=file_size,
                        entry_id=entry_id,
                        path=path,
                        load_payload=load_payload,
                    )
                remainder = _read_exact(
                    stream,
                    file_size - len(prefix),
                    label="legacy recovery record",
                )
                # Legacy v1 embeds base64 inside one JSON value.  Compatibility
                # therefore retains its historical full decode even when the
                # caller needs only authority; all new v2 records stream here.
                return self._read_legacy_record(
                    prefix + remainder,
                    entry_id=entry_id,
                    path=path,
                )
        finally:
            if fd >= 0:
                os.close(fd)

    def _read_authority(self, entry_id: str) -> _RecordAuthority:
        return self._read_entry(entry_id, load_payload=False)

    def _read(self, entry_id: str) -> _Record:
        record = self._read_entry(entry_id, load_payload=True)
        if not isinstance(record, _Record):
            raise RecoveryError("recovery payload was not materialized")
        return record

    def _trusted_checkpoint_authority(
        self,
        entry_id: str,
    ) -> _RecordAuthority | None:
        """Reuse just-written metadata only while the published inode is exact."""

        witness = self._checkpoint_witnesses.get(entry_id)
        if witness is None:
            return None
        try:
            current = _record_file_signature(
                witness.authority.path,
                self._record_limit,
            )
        except (OSError, RecoveryError):
            self._checkpoint_witnesses.pop(entry_id, None)
            return None
        if current != witness.file_signature:
            self._checkpoint_witnesses.pop(entry_id, None)
            return None
        return witness.authority

    def _candidate_from_record(
        self,
        record: _RecordAuthority,
        *,
        comparison_budget: list[int] | None = None,
    ) -> RecoveryCandidate:
        error: str | None = None
        inspection = _TargetInspection(Fingerprint(False))
        contract = _mode_repair_modes(record.metadata)
        try:
            inspection = (
                _inspect_target_with_contract(
                    record.target,
                    contract,
                    self.max_comparison_bytes,
                    shared_budget=comparison_budget,
                )
                if contract is not None and _MODE_REPAIR_DIRFD_SUPPORTED
                else _inspect_target(
                    record.target,
                    self.max_comparison_bytes,
                    shared_budget=comparison_budget,
                )
            )
            current = inspection.fingerprint
        except RecoveryConflictError as exc:
            current = Fingerprint(False)
            status = RecoveryStatus.TARGET_CHANGED
            error = str(exc)
        except (OSError, RecoveryTooLargeError) as exc:
            current = Fingerprint(False)
            status = RecoveryStatus.TARGET_UNREADABLE
            error = str(exc)
        else:
            if _same_content(current, record.commit):
                status = RecoveryStatus.ALREADY_PERSISTED
            elif _same_content(current, record.base):
                status = RecoveryStatus.RECOVERABLE
            else:
                status = RecoveryStatus.TARGET_CHANGED

        intended_mode: int | None = None
        mode_repair_available = False
        mode_repair_required = False
        mode_repair_conflict = False
        if contract is not None:
            private_mode = contract.private_mode
            intended_mode = contract.intended_mode
            if status is RecoveryStatus.ALREADY_PERSISTED:
                authority_error = _mode_repair_authority_error(inspection)
                if authority_error is None and inspection.mode in {
                    private_mode,
                    intended_mode,
                }:
                    mode_repair_available = True
                    mode_repair_required = inspection.mode != intended_mode
                else:
                    mode_repair_conflict = True
                    if error is None:
                        if authority_error is not None:
                            error = f"permission repair unavailable: {authority_error}"
                        else:
                            error = (
                                "permission repair unavailable: target mode is neither "
                                "the private crash mode nor the intended mode"
                            )
        return RecoveryCandidate(
            entry_id=record.entry_id,
            buffer_id=record.buffer_id,
            target=record.target,
            created_ns=record.created_ns,
            payload_size=record.payload_size,
            payload_sha256=record.payload_sha256,
            base=record.base,
            commit=record.commit,
            payload_kind=record.payload_kind,
            metadata=dict(record.metadata),
            status=status,
            error=error,
            current_mode=inspection.mode,
            intended_mode=intended_mode,
            mode_repair_available=mode_repair_available,
            mode_repair_required=mode_repair_required,
            mode_repair_conflict=mode_repair_conflict,
        )

    def _candidate(self, entry_id: str) -> RecoveryCandidate:
        return self._candidate_from_record(self._read_authority(entry_id))

    def inspect(self, entry_id: str) -> RecoveryCandidate:
        """Return one verified candidate without scanning the journal root."""

        return self._candidate(entry_id)

    def scan_residue(self) -> RecoveryResidueScan:
        """Return a bounded metadata-only inventory of private save temps.

        No temp payload is opened or hashed.  Checkpoint temps are found only
        under the private recovery root.  Document temps are considered only in
        parent directories named by verified recovery records, and only when the
        record's random save lease and pinned parent ``st_dev/st_ino`` match.
        """

        candidates: list[RecoveryResidue] = []
        visited = 0
        truncated = False
        unreadable_directories = 0
        record_bytes_limited = False

        paths, records_omitted, records_truncated = self._bounded_record_paths()
        record_bytes_left = int(self.max_scan_record_bytes)
        parent_leases: dict[
            tuple[str, int, int], dict[str, str]
        ] = {}
        lease_entries: dict[str, str] = {}
        for row in paths:
            if row.size > record_bytes_left:
                records_omitted += 1
                record_bytes_limited = True
                continue
            record_bytes_left -= row.size
            try:
                record = self._read_authority(row.entry_id)
            except RecoveryError:
                continue
            try:
                lease_id = normalize_save_lease_id(
                    record.metadata.get("save_lease_id"),
                    create=False,
                )
            except ValueError:
                continue
            parent_dev = _metadata_decimal(record.metadata, "target_parent_dev")
            parent_ino = _metadata_decimal(record.metadata, "target_parent_ino")
            if lease_id is None or parent_dev is None or parent_ino is None:
                continue
            lease_entries[lease_id] = record.entry_id
            key = (str(record.target.parent), parent_dev, parent_ino)
            parent_leases.setdefault(key, {})[lease_id] = record.entry_id

        def scan_directory(
            parent: Path,
            *,
            kind: RecoveryResidueKind,
            leases: Mapping[str, str] | None = None,
            expected_identity: tuple[int, int] | None = None,
        ) -> None:
            nonlocal visited, truncated, unreadable_directories
            if visited >= self.max_residue_directory_entries:
                truncated = True
                return
            try:
                fd = _open_directory_no_follow(parent)
            except FileNotFoundError:
                return
            except OSError:
                unreadable_directories += 1
                return
            try:
                parent_st = os.fstat(fd)
                actual_identity = (
                    int(getattr(parent_st, "st_dev", 0) or 0),
                    int(getattr(parent_st, "st_ino", 0) or 0),
                )
                if (
                    expected_identity is not None
                    and actual_identity != expected_identity
                ):
                    unreadable_directories += 1
                    return
                if not _SCANDIR_FD_SUPPORTED:
                    unreadable_directories += 1
                    return
                try:
                    entries = os.scandir(fd)
                except (OSError, TypeError):
                    unreadable_directories += 1
                    return
                with entries:
                    for entry in entries:
                        if visited >= self.max_residue_directory_entries:
                            truncated = True
                            break
                        visited += 1
                        parsed = parse_private_temp_name(str(entry.name))
                        if parsed is None:
                            continue
                        if leases is not None and parsed.lease_id not in leases:
                            continue
                        try:
                            entry_st = entry.stat(follow_symlinks=False)
                        except OSError:
                            continue
                        entry_id = (
                            lease_entries.get(parsed.lease_id)
                            if kind is RecoveryResidueKind.CHECKPOINT_TEMP
                            else (
                                leases.get(parsed.lease_id)
                                if leases is not None
                                else None
                            )
                        )
                        residue = _residue_row(
                            parent=parent,
                            parent_st=parent_st,
                            name=str(entry.name),
                            st=entry_st,
                            kind=kind,
                            entry_id=entry_id,
                        )
                        if residue is not None:
                            candidates.append(residue)
            finally:
                os.close(fd)

        # The recovery root may not exist yet.  Its scan is filename/metadata
        # only and includes orphan checkpoint temps whose record was never
        # published.
        scan_directory(
            self.root,
            kind=RecoveryResidueKind.CHECKPOINT_TEMP,
        )
        for (parent_raw, parent_dev, parent_ino), leases in sorted(
            parent_leases.items()
        ):
            if visited >= self.max_residue_directory_entries:
                truncated = True
                break
            scan_directory(
                Path(parent_raw),
                kind=RecoveryResidueKind.DOCUMENT_TEMP,
                leases=leases,
                expected_identity=(parent_dev, parent_ino),
            )

        candidates.sort(
            key=lambda item: (item.mtime_ns, str(item.path), item.residue_id)
        )
        omitted = max(0, len(candidates) - self.max_residue_files)
        selected = tuple(candidates[: self.max_residue_files])
        return RecoveryResidueScan(
            residues=selected,
            omitted=omitted,
            directory_entries_visited=visited,
            truncated=bool(truncated or records_truncated),
            records_omitted=records_omitted,
            record_bytes_limited=record_bytes_limited,
            unreadable_directories=unreadable_directories,
        )

    def resolve_residue_selector(
        self,
        selector: str,
        *,
        residues: list[RecoveryResidue] | None = None,
    ) -> RecoveryResidue:
        rows = list(
            self.scan_residue().residues if residues is None else residues
        )
        raw = str(selector or "").strip()
        if not raw:
            raise RecoverySelectorError("recovery temp selector is empty")
        lowered = raw.lower()
        if raw.startswith("#"):
            token = raw[1:]
            if not token.isdigit() or int(token) <= 0:
                raise RecoverySelectorError(f"invalid recovery temp index: {raw}")
            index = int(token) - 1
            if index >= len(rows):
                raise RecoverySelectorError(
                    f"recovery temp index out of range: {raw}"
                )
            return rows[index]
        if len(lowered) < 8:
            raise RecoverySelectorError(
                "recovery temp id prefix must contain at least 8 characters"
            )
        matches = [row for row in rows if row.residue_id.startswith(lowered)]
        if not matches:
            raise RecoverySelectorError(f"no recovery temp matches: {raw}")
        if len(matches) > 1:
            raise RecoverySelectorError(f"ambiguous recovery temp prefix: {raw}")
        return matches[0]

    def cleanup_residue(self, residue: RecoveryResidue) -> ResidueCleanupOutcome:
        """Revalidate and unlink exactly one definitively stale private temp."""

        if not isinstance(residue, RecoveryResidue):
            raise TypeError("cleanup_residue requires a RecoveryResidue witness")
        if not _SAFE_RESIDUE_UNLINK:
            raise RecoveryConflictError(
                "recovery temp cleanup requires descriptor-relative no-follow unlink"
            )
        parent = residue.path.parent
        name = residue.path.name
        try:
            dir_fd = _open_directory_no_follow(parent)
        except OSError as exc:
            raise RecoveryConflictError(
                f"recovery temp parent is unavailable: {parent}"
            ) from exc
        try:
            parent_st = os.fstat(dir_fd)
            if (
                int(getattr(parent_st, "st_dev", 0) or 0) != residue.parent_dev
                or int(getattr(parent_st, "st_ino", 0) or 0)
                != residue.parent_ino
            ):
                raise RecoveryConflictError(
                    "recovery temp parent authority changed after inventory"
                )
            try:
                current_st = os.stat(
                    name,
                    dir_fd=dir_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError as exc:
                raise RecoveryConflictError(
                    "recovery temp disappeared after inventory"
                ) from exc
            parsed = parse_private_temp_name(name)
            if (
                parsed is None
                or parsed.lease_id != residue.lease_id
                or parsed.owner != residue.owner
            ):
                raise RecoveryConflictError(
                    "recovery temp identity changed after inventory"
                )
            current_id = _residue_identity(
                kind=residue.kind,
                parent_dev=residue.parent_dev,
                parent_ino=residue.parent_ino,
                name=name,
                st=current_st,
            )
            if current_id != residue.residue_id:
                raise RecoveryConflictError(
                    "recovery temp metadata changed after inventory"
                )
            current_owner_state = temp_owner_state(parsed.owner)
            reason = _residue_cleanup_reason(
                st=current_st,
                owner_state=current_owner_state,
            )
            if reason:
                raise RecoveryConflictError(
                    f"recovery temp cleanup refused: {reason}"
                )
            self._fault("before_residue_unlink")
            os.unlink(name, dir_fd=dir_fd)
            self._fault("after_residue_unlink")
            directory_synced = _fsync_dir_fd(dir_fd)
            self._fault("after_residue_directory_sync")
        finally:
            os.close(dir_fd)
        return ResidueCleanupOutcome(
            residue_id=residue.residue_id,
            path=residue.path,
            removed=True,
            directory_synced=directory_synced,
        )

    def repair_mode(self, entry_id: str) -> ModeRepairOutcome:
        """Finish one interrupted atomic save's permission transaction.

        This is deliberately narrower than a generic chmod operation.  The
        journal must carry Micromax's versioned private-temp contract and the
        recorded parent inode must still be reachable.  The target is opened
        relative to that pinned directory, must be the exact committed regular
        file, must be owned by the current effective user with one hard link,
        and may have only the known crash-private or intended mode.  File and
        directory synchronization complete before the record is retired.
        """

        record = self._trusted_checkpoint_authority(entry_id)
        if record is None:
            record = self._read_authority(entry_id)
        contract = _mode_repair_modes(record.metadata)
        if contract is None:
            raise RecoveryConflictError(
                "recovery entry does not carry an atomic permission-repair contract"
            )
        private_mode = contract.private_mode
        intended_mode = contract.intended_mode
        if (
            not _MODE_REPAIR_DIRFD_SUPPORTED
            or not hasattr(os, "fchmod")
            or not hasattr(os, "geteuid")
        ):
            raise RecoveryConflictError(
                "host cannot verify and repair POSIX file permissions"
            )

        previous_mode = -1
        changed = False
        file_synced = False
        directory_synced = False
        parent_fd = _open_verified_parent(record.target, contract)
        fd = -1
        try:
            try:
                fd = _open_target_at(parent_fd, record.target)
            except FileNotFoundError as exc:
                raise RecoveryConflictError(
                    "permission repair target no longer exists"
                ) from exc
            inspection = _inspect_open_target(
                fd,
                record.target,
                self.max_comparison_bytes,
            )
            if not _same_content(inspection.fingerprint, record.commit):
                raise RecoveryConflictError(
                    "target bytes no longer match the interrupted save commit"
                )
            authority_error = _mode_repair_authority_error(inspection)
            if authority_error is not None:
                raise RecoveryConflictError(
                    f"permission repair refused: {authority_error}"
                )
            previous_mode = int(inspection.mode if inspection.mode is not None else -1)
            if previous_mode not in {private_mode, intended_mode}:
                raise RecoveryConflictError(
                    "permission repair refused: target mode changed outside the "
                    "recorded atomic-save transaction"
                )

            _assert_named_target_at(
                parent_fd,
                record.target,
                inspection,
                expected_mode=previous_mode,
            )
            self._fault("before_mode_repair")
            # The fault hook is also the deterministic concurrency boundary in
            # tests.  Revalidate after it, immediately before fchmod, so an
            # external mode or name change is refused rather than overwritten.
            _assert_named_target_at(
                parent_fd,
                record.target,
                inspection,
                expected_mode=previous_mode,
            )
            if previous_mode != intended_mode:
                os.fchmod(fd, intended_mode)
                changed = True
                self._fault("after_mode_repair_chmod")
            after_chmod = os.fstat(fd)
            if int(stat.S_IMODE(after_chmod.st_mode)) != intended_mode:
                raise RecoveryError("permission repair did not apply the intended mode")

            # The chmod is inode metadata.  Synchronize that inode first, then
            # the already-pinned containing directory that carries the earlier
            # atomic replacement, before treating the transaction as complete.
            os.fsync(fd)
            file_synced = True
            self._fault("after_mode_repair_file_sync")
            directory_synced = _fsync_dir_fd(parent_fd)
            if not directory_synced:
                raise RecoveryError(
                    "permission transaction directory sync is unavailable; "
                    "recovery entry retained"
                )
            self._fault("after_mode_repair_directory_sync")

            current = _inspect_open_target(
                fd,
                record.target,
                self.max_comparison_bytes,
            )
            if (
                not _same_content(current.fingerprint, record.commit)
                or current.dev != inspection.dev
                or current.ino != inspection.ino
                or current.mode != intended_mode
            ):
                raise RecoveryConflictError(
                    "target inode changed during permission repair"
                )
            _assert_named_target_at(
                parent_fd,
                record.target,
                current,
                expected_mode=intended_mode,
            )
            self._fault("after_mode_repair_verify")
        finally:
            if fd >= 0:
                os.close(fd)
            os.close(parent_fd)

        cleanup_error: str | None = None
        retired = False
        try:
            retired = self.dismiss(entry_id)
        except (OSError, RecoveryError) as exc:
            cleanup_error = str(exc)
        return ModeRepairOutcome(
            entry_id=entry_id,
            target=record.target,
            previous_mode=previous_mode,
            intended_mode=intended_mode,
            changed=changed,
            file_synced=file_synced,
            directory_synced=directory_synced,
            recovery_retired=retired,
            recovery_retire_directory_synced=bool(
                self.last_dismiss_directory_synced
            ),
            cleanup_error=cleanup_error,
        )

    def scan(self, *, quarantine_corrupt: bool = True) -> RecoveryScan:
        """Validate a bounded recovery inventory.

        The inventory caps directory traversal, retained records, decoded record
        bytes, and total document bytes hashed.  It returns useful partial truth
        with explicit truncation metadata instead of stalling or pretending an
        unbounded directory was fully inspected.
        """

        candidates: list[RecoveryCandidate] = []
        paths, omitted, truncated = self._bounded_record_paths()
        corrupt = 0
        record_bytes_left = int(self.max_scan_record_bytes)
        record_bytes_limited = False
        comparison_budget = [int(self.max_scan_comparison_bytes)]

        for row in paths:
            if row.size > record_bytes_left:
                omitted += 1
                record_bytes_limited = True
                continue
            record_bytes_left -= row.size
            try:
                record = self._read_authority(row.entry_id)
                candidates.append(
                    self._candidate_from_record(
                        record,
                        comparison_budget=comparison_budget,
                    )
                )
            except (RecoveryCorruptError, RecoveryTooLargeError):
                corrupt += 1
                if quarantine_corrupt:
                    try:
                        self._quarantine(row.path)
                    except OSError:
                        pass
                continue
            except RecoveryError:
                # A valid-looking filename whose record vanished during the scan
                # is simply absent from this point-in-time inventory.
                continue
        candidates.sort(key=lambda item: (item.created_ns, item.entry_id), reverse=True)
        comparison_limited = sum(
            1
            for candidate in candidates
            if candidate.error
            and "inventory comparison budget" in candidate.error
        )
        return RecoveryScan(
            candidates=tuple(candidates),
            omitted=int(omitted),
            corrupt=int(corrupt),
            truncated=bool(truncated),
            comparison_limited=int(comparison_limited),
            record_bytes_limited=bool(record_bytes_limited),
        )

    def discover(self, *, quarantine_corrupt: bool = True) -> list[RecoveryCandidate]:
        """Compatibility list view of the bounded explicit inventory."""

        return list(self.scan(quarantine_corrupt=quarantine_corrupt).candidates)

    def _quarantine(self, path: Path) -> Path:
        quarantine = self.root / "quarantine"
        quarantine.mkdir(mode=0o700, exist_ok=True)
        suffix = f".{time.time_ns()}.corrupt"
        destination = quarantine / (path.name + suffix)
        os.replace(path, destination)
        _fsync_dir(self.root)
        _fsync_dir(quarantine)
        return destination

    def entry_present(self, entry_id: str) -> bool:
        """Return bounded, no-follow presence for one exact recovery record.

        Undo/Redo uses this after a save boundary to avoid resurrecting retired
        journal authority.  The check deliberately does not decode the private
        payload or inspect its document target, but it does require the trusted
        journal root and a bounded regular-file record.  A symlink, directory,
        or oversized replacement is known not to be usable recovery authority.
        """

        path = self._entry_path(entry_id)
        if not self._read_root_exists():
            return False
        try:
            st = path.lstat()
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise RecoveryError(
                f"could not inspect recovery entry {entry_id}: {exc}"
            ) from exc
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
            raise RecoveryCorruptError(
                f"recovery entry is not a trusted regular file: {entry_id}"
            )
        if int(st.st_size) > int(self._record_limit):
            raise RecoveryTooLargeError(
                f"recovery entry exceeds bounded read limit: {entry_id}"
            )
        return True

    def load(self, entry_id: str) -> RecoverySnapshot:
        record = self._read(entry_id)
        return RecoverySnapshot(
            candidate=self._candidate_from_record(record),
            payload=record.payload,
        )

    def payload(self, entry_id: str) -> bytes:
        return self._read(entry_id).payload

    def entry_ids_for_buffer(
        self,
        buffer_id: str,
        *,
        quarantine_corrupt: bool = True,
    ) -> list[str]:
        """Return valid journal rows for ``buffer_id`` without reading targets.

        This is the post-commit cleanup lane.  Calling ``discover`` here would
        hash document targets again after a successful writer return, adding
        duplicate I/O and reopening a race with unrelated writers.  Journal
        records still receive their normal bounded integrity validation.
        """

        wanted = str(buffer_id or "")
        if not wanted:
            return []
        found: list[str] = []
        paths, _omitted, _truncated = self._bounded_record_paths()
        record_bytes_left = int(self.max_scan_record_bytes)
        for row in paths:
            if row.size > record_bytes_left:
                continue
            record_bytes_left -= row.size
            try:
                record = self._read_authority(row.entry_id)
            except (RecoveryCorruptError, RecoveryTooLargeError):
                if quarantine_corrupt:
                    try:
                        self._quarantine(row.path)
                    except OSError:
                        pass
                continue
            except RecoveryError:
                continue
            if record.buffer_id == wanted:
                found.append(record.entry_id)
        return found

    def resolve_selector(
        self,
        selector: str,
        *,
        candidates: list[RecoveryCandidate] | None = None,
    ) -> RecoveryCandidate:
        rows = list(self.discover() if candidates is None else candidates)
        raw = str(selector or "").strip()
        if not raw:
            raise RecoverySelectorError("recovery selector is empty")
        lowered = raw.lower()
        if len(lowered) == 64 and all(c in "0123456789abcdef" for c in lowered):
            # A complete id is an explicit authority reference and may address a
            # record omitted from the bounded list inventory.
            return self._candidate(lowered)
        if raw.startswith("#"):
            token = raw[1:]
            if not token.isdigit() or int(token) <= 0:
                raise RecoverySelectorError(f"invalid recovery index: {raw}")
            index = int(token) - 1
            if index >= len(rows):
                raise RecoverySelectorError(f"recovery index out of range: {raw}")
            return rows[index]
        if len(raw) < 8:
            raise RecoverySelectorError("recovery id prefix must contain at least 8 characters")
        matches = [candidate for candidate in rows if candidate.entry_id.startswith(raw.lower())]
        if not matches:
            raise RecoverySelectorError(f"no recovery snapshot matches: {raw}")
        if len(matches) > 1:
            raise RecoverySelectorError(f"ambiguous recovery snapshot prefix: {raw}")
        return matches[0]

    def restore(
        self,
        entry_id: str,
        writer: ContentWriter,
        *,
        allow_changed_target: bool = False,
    ) -> RecoveryCandidate:
        """Legacy direct restore for byte-for-byte records.

        Product recovery uses ``load`` and stages exact text in an editor buffer.
        Direct target overwrite remains only for legacy byte records where the
        recovery payload and intended disk bytes are identical.
        """

        snapshot = self.load(entry_id)
        before = snapshot.candidate
        payload_fp = Fingerprint.for_bytes(snapshot.payload)
        if before.payload_kind != PAYLOAD_KIND_BYTES or not _same_content(before.commit, payload_fp):
            raise RecoveryError("editor-text recovery must be staged in a buffer")
        if before.status is RecoveryStatus.TARGET_CHANGED and not allow_changed_target:
            raise RecoveryConflictError("target changed after checkpoint; explicit override required")
        if before.status is RecoveryStatus.TARGET_UNREADABLE and not allow_changed_target:
            raise RecoveryConflictError("target cannot be safely inspected; explicit override required")
        immediately_before = self._candidate(entry_id)
        if immediately_before.status != before.status or immediately_before.target != before.target:
            raise RecoveryConflictError("target changed while preparing recovery")
        self._fault("before_restore_write")
        writer(before.target, snapshot.payload)
        self._fault("after_restore_write")
        persisted = _fingerprint(before.target, self.max_comparison_bytes)
        if not _same_content(persisted, payload_fp):
            raise RecoveryError("restore writer returned without committing the recovery payload")
        self.dismiss(entry_id)
        return RecoveryCandidate(
            **{
                **before.__dict__,
                "status": RecoveryStatus.ALREADY_PERSISTED,
                "error": None,
            }
        )

    def dismiss(self, entry_id: str) -> bool:
        path = self._entry_path(entry_id)
        self._last_dismiss_directory_synced = False
        self._fault("before_dismiss")
        try:
            path.unlink()
        except FileNotFoundError:
            self._checkpoint_witnesses.pop(entry_id, None)
            return False
        self._checkpoint_witnesses.pop(entry_id, None)
        self._fault("after_dismiss_unlink")
        self._last_dismiss_directory_synced = _fsync_dir(self.root)
        self._fault("after_dismiss")
        return True

    def commit_checkpoint(
        self,
        entry_id: str,
        commit_content: BytesLike,
        writer: ContentWriter,
    ) -> SaveOutcome:
        """Commit bytes covered by an existing recovery checkpoint.

        ``writer`` must honor the durability policy chosen by its caller.  The
        Micromax editor requests file synchronization whenever a checkpoint is
        active and also requests containing-directory synchronization on hosts
        where its writer exposes that operation.  The journal remains present on
        writer failure, authority change, or content-verification failure.

        Successful return is therefore a transaction-ordering guarantee, not a
        universal power-loss claim: the exact persistence boundary depends on
        the writer, filesystem, operating system, and storage stack.
        """

        record = self._trusted_checkpoint_authority(entry_id)
        if record is None:
            record = self._read_authority(entry_id)
        commit_payload = _bytes(commit_content)
        supplied = Fingerprint.for_bytes(commit_payload)
        if not _same_content(record.commit, supplied):
            raise RecoveryConflictError(
                "commit bytes do not match the recovery checkpoint"
            )
        before = self._candidate_from_record(record)
        if before.status is RecoveryStatus.TARGET_CHANGED:
            raise RecoveryConflictError("target changed after recovery checkpoint")
        if before.status is RecoveryStatus.TARGET_UNREADABLE:
            raise RecoveryConflictError("target cannot be safely inspected")

        self._fault("before_content_write")
        writer(record.target, commit_payload)
        self._fault("after_content_write")
        mode_contract = _mode_repair_modes(record.metadata)
        persisted_inspection = (
            _inspect_target_with_contract(
                record.target,
                mode_contract,
                self.max_comparison_bytes,
            )
            if mode_contract is not None and _MODE_REPAIR_DIRFD_SUPPORTED
            else _inspect_target(record.target, self.max_comparison_bytes)
        )
        if not _same_content(persisted_inspection.fingerprint, record.commit):
            raise RecoveryError(
                "content writer returned without committing the checkpoint bytes"
            )
        if (
            mode_contract is not None
            and persisted_inspection.mode != mode_contract.intended_mode
        ):
            raise RecoveryError(
                "content writer returned before completing the recorded "
                "permission transaction"
            )
        try:
            retired = self.dismiss(entry_id)
            return SaveOutcome(entry_id, committed=True, recovery_retired=retired)
        except OSError as exc:
            # The document bytes were written and verified in the running
            # kernel.  A stale record is harmless: startup will classify it as
            # already_persisted and retry cleanup.  Do not turn this ordering
            # fact into a universal power-loss durability claim.
            return SaveOutcome(
                entry_id,
                committed=True,
                recovery_retired=False,
                cleanup_error=str(exc),
            )

    def save_with_recovery(
        self,
        target: Union[str, os.PathLike[str]],
        content: BytesLike,
        writer: ContentWriter,
        *,
        buffer_id: str = "default",
        metadata: Mapping[str, object] | None = None,
    ) -> SaveOutcome:
        """Checkpoint and durably commit one byte-for-byte document payload."""

        payload = _bytes(content)
        entry_id = self.checkpoint(
            target,
            payload,
            buffer_id=buffer_id,
            payload_kind=PAYLOAD_KIND_BYTES,
            metadata=metadata,
        )
        return self.commit_checkpoint(entry_id, payload, writer)
