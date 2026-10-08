from __future__ import annotations

from dataclasses import dataclass
import errno
import hashlib
import multiprocessing
import os
from pathlib import Path
import stat
from typing import Callable

from .save_residue import (
    build_private_temp_name,
    normalize_save_lease_id,
    parse_private_temp_name,
    private_temp_lease,
)
from .worker_process import (
    WorkerResultChannel,
    WorkerResultTimeoutError,
    collect_worker_result,
    create_one_shot_worker,
    isolated_worker_context,
    normalize_worker_timeout_seconds,
)


FileStateSignature = tuple[int, int, int, int, int]
MISSING_FILE_SIGNATURE: FileStateSignature = (-1, -1, -1, -1, -1)
FileWriteFault = Callable[[str], None]
WorkerErrorFactory = Callable[[], BaseException]
WorkerCleanup = Callable[[int | None], None]


# Save workers return only fixed-size witnesses or bounded error text.  Keep a
# dedicated ceiling so a future accidental payload cannot silently inherit the
# shared transport's much larger compatibility default.
_FILE_WRITE_RESULT_MAX_BYTES = 1024 * 1024


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

_UNSUPPORTED_UNNAMED_TEMP_ERRNOS = frozenset(
    value
    for value in (
        # Linux documents EOPNOTSUPP for filesystems without O_TMPFILE and
        # EISDIR/ENOENT for kernels predating the implementation.  EINVAL is
        # also used by filesystem/kernel combinations that reject the flag.
        getattr(errno, "EOPNOTSUPP", None),
        getattr(errno, "ENOTSUP", None),
        getattr(errno, "EISDIR", None),
        getattr(errno, "ENOENT", None),
        getattr(errno, "EINVAL", None),
        getattr(errno, "ENOSYS", None),
    )
    if value is not None
)


@dataclass(frozen=True)
class FileFreshness:
    """Expected on-disk state used by the save conflict boundary."""

    signature: FileStateSignature | None
    content_hash: str | None = None


class FileFreshnessConflict(RuntimeError):
    """Raised when a save target changed after the caller's freshness check."""


class FileContainmentError(RuntimeError):
    """Raised when a file operation would escape its capability root."""


class FileWriteTimeoutError(RuntimeError):
    """Raised when an atomic filesystem write exceeds its wall-clock budget."""


class FileFreshnessTimeoutError(RuntimeError):
    """Raised when save freshness/hash capture exceeds its wall-clock budget."""


class FileMkparentsTimeoutError(RuntimeError):
    """Raised when save parent-directory creation exceeds its wall-clock budget."""


class FileWritePlanTimeoutError(RuntimeError):
    """Raised when atomic-save authority planning exceeds its wall-clock budget."""


@dataclass(frozen=True)
class FileWriteResult:
    """Small witness for the save path and synchronization actually completed.

    ``fsync`` remains the caller's effective request for compatibility.
    ``file_synced`` and ``directory_synced`` are narrower completion witnesses;
    they are never inferred merely from the request.
    """

    path: str
    write_path: str
    atomic: bool
    preserve_mode: bool
    fsync: bool
    followed_symlink: bool = False
    file_synced: bool = False
    directory_synced: bool = False
    final_mode: int | None = None


@dataclass(frozen=True)
class ResolvedFileWriteTarget:
    """One nominal save path and the concrete file it currently names.

    Recovery, freshness checks, and the writer must agree on this authority.
    Keeping the result explicit prevents callers from reimplementing the
    editor's symlink-preserving save rule with subtly different semantics.
    """

    requested_path: Path
    write_path: Path
    followed_symlink: bool


@dataclass(frozen=True)
class AtomicWritePlan:
    """Pinned authority and permission intent for one atomic save.

    Recovery must describe the exact mode the writer will publish, not a later
    best-effort reconstruction.  The plan is created before the recovery
    checkpoint and is safe to serialize to the killable writer process.  The
    writer re-resolves the nominal path and rejects the plan if authority or
    options changed before it creates a document temp.
    """

    requested_path: str
    write_path: str
    followed_symlink: bool
    preserve_mode: bool
    preserved_existing_mode: bool
    final_mode: int
    parent_dev: int
    parent_ino: int


_DIR_FD_SUPPORT = set(getattr(os, "supports_dir_fd", set()))
_DIR_FD_IO_SUPPORTED = (
    os.name != "nt"
    and os.open in _DIR_FD_SUPPORT
    and os.stat in _DIR_FD_SUPPORT
    and os.unlink in _DIR_FD_SUPPORT
    and os.rename in _DIR_FD_SUPPORT
)
_DIR_FD_MKDIR_SUPPORTED = (
    os.name != "nt"
    and os.open in _DIR_FD_SUPPORT
    and os.mkdir in _DIR_FD_SUPPORT
)


def _dir_fd_io_available() -> bool:
    """Return whether this host supports the dir-fd commit path.

    The path-based writer is kept as a portability fallback, but POSIX hosts can
    bind temporary-file cleanup and the final rename to an already-open parent
    directory.  That matters for script-capability saves: if a parent path is
    swapped to a symlink while a save is in flight, path-only cleanup/replace can
    either leak the prepared temp file or act on a different directory than the
    one that passed containment checks.
    """

    return bool(_DIR_FD_IO_SUPPORTED)


def resolve_open_fd_path(fd: int) -> Path | None:
    """Return the concrete path of an open file descriptor when the host exposes it."""

    proc = Path(f"/proc/self/fd/{fd}")
    if not proc.exists():
        return None
    try:
        return proc.resolve(strict=True)
    except OSError:
        return None


def _resolve_dir_fd(fd: int) -> Path | None:
    """Return the concrete path of an open directory fd when the host exposes it."""

    return resolve_open_fd_path(fd)


def _open_parent_dir_fd(parent: Path, containment_root: str | Path | None) -> int:
    """Open ``parent`` as a directory and recheck containment on the fd target."""

    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= getattr(os, "O_DIRECTORY")
    fd = os.open(parent, flags)
    try:
        resolved = _resolve_dir_fd(fd)
        if resolved is not None:
            assert_path_within_root(resolved, containment_root)
        return fd
    except Exception:
        os.close(fd)
        raise


def _assert_parent_fd_still_current(
    parent: Path,
    dir_fd: int,
    containment_root: str | Path | None,
) -> None:
    """Raise if ``parent`` no longer names the already-open directory inode.

    ``/proc/self/fd`` is useful diagnostic evidence but is not a portable
    authority check: it may be unavailable, mounted with restrictions, or show
    a renamed path.  Compare the pathname's current device/inode pair with the
    pinned descriptor instead, then use resolved paths only to explain a
    refusal.  This closes the in-root parent-replacement race even on POSIX
    hosts where descriptor-path introspection is unavailable.
    """

    try:
        current_st = os.stat(parent)
    except OSError as exc:
        raise FileContainmentError(
            f"parent directory became unavailable before save commit: {parent}"
        ) from exc
    opened_st = os.fstat(dir_fd)
    current_identity = (
        int(getattr(current_st, "st_dev", 0) or 0),
        int(getattr(current_st, "st_ino", 0) or 0),
    )
    opened_identity = (
        int(getattr(opened_st, "st_dev", 0) or 0),
        int(getattr(opened_st, "st_ino", 0) or 0),
    )
    if current_identity == opened_identity:
        return

    current_path = _resolve_for_containment(parent)
    if containment_root is not None:
        assert_path_within_root(current_path, containment_root)
    opened_path = _resolve_dir_fd(dir_fd)
    opened_label = str(opened_path) if opened_path is not None else repr(opened_identity)
    raise FileContainmentError(
        "parent directory changed before save commit "
        f"({opened_label} != {current_path})"
    )


def _close_fd(fd: int) -> None:
    try:
        os.close(fd)
    except OSError:
        pass





def _dir_fd_mkdir_available() -> bool:
    """Return whether this host can create parent directories via dir_fd."""

    return bool(_DIR_FD_MKDIR_SUPPORTED)


def _absolute_path(path: str | Path) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    try:
        return p.absolute()
    except OSError:
        return p


def _canonical_authority_path(path: str | Path) -> Path:
    """Resolve parent authority without following a final-component redirect."""

    absolute = _absolute_path(path)
    return absolute.parent.resolve(strict=False) / absolute.name


def _relative_parts_under_root(path: str | Path, root: str | Path) -> tuple[Path, list[str]]:
    """Return root-resolved path plus safe relative parts for a contained path."""

    root_path = _resolve_for_containment(root)
    nominal = _absolute_path(path)
    assert_path_within_root(nominal, root_path)
    try:
        rel = nominal.relative_to(root_path)
    except ValueError:
        resolved = _resolve_for_containment(nominal)
        rel = resolved.relative_to(root_path)
    parts: list[str] = []
    for part in rel.parts:
        if part in {"", "."}:
            continue
        if part == ".." or os.sep in part or (os.altsep and os.altsep in part):
            raise FileContainmentError(f"unsafe parent directory component: {part}")
        parts.append(str(part))
    return root_path, parts


def _open_child_dir_no_follow(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= getattr(os, "O_DIRECTORY")
    if hasattr(os, "O_NOFOLLOW"):
        flags |= getattr(os, "O_NOFOLLOW")
    if hasattr(os, "O_CLOEXEC"):
        flags |= getattr(os, "O_CLOEXEC")
    return os.open(name, flags, dir_fd=parent_fd)


def _ensure_parent_dir_dirfd(parent: Path, root: str | Path) -> None:
    """Create missing parent directories without following swapped symlinks."""

    root_path, parts = _relative_parts_under_root(parent, root)
    root_fd = _open_parent_dir_fd(root_path, root_path)
    fd = root_fd
    try:
        for part in parts:
            try:
                os.mkdir(part, 0o777, dir_fd=fd)
            except FileExistsError:
                pass
            next_fd = _open_child_dir_no_follow(fd, part)
            try:
                resolved = _resolve_dir_fd(next_fd)
                if resolved is not None:
                    assert_path_within_root(resolved, root_path)
            except Exception:
                _close_fd(next_fd)
                raise
            if fd != root_fd:
                _close_fd(fd)
            fd = next_fd
    finally:
        _close_fd(fd)
        if fd != root_fd:
            _close_fd(root_fd)


def ensure_parent_directory(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
) -> None:
    """Create a save target's parent directory with cap-root containment.

    Interactive saves keep ordinary ``mkdir -p`` behavior.  Script/capability
    saves pass ``containment_root``; on POSIX-capable hosts the creation walks
    from an opened root directory fd and opens each component without following
    symlinks.  That prevents a late parent swap from causing ``mkparents`` to
    create directories outside the configured capability root before the writer
    has a chance to refuse the save.
    """

    parent = Path(path).expanduser()
    if containment_root is None or str(containment_root).strip() == "":
        parent.mkdir(parents=True, exist_ok=True)
        return
    if _dir_fd_mkdir_available():
        _ensure_parent_dir_dirfd(parent, containment_root)
        return
    # Portable fallback: still recheck before and after the path-based mkdir.
    assert_path_within_root(parent, containment_root)
    parent.mkdir(parents=True, exist_ok=True)
    assert_path_within_root(parent, containment_root)

def _ensure_parent_directory_worker(
    path: str,
    containment_root: str | None,
    queue: object,
) -> None:
    try:
        ensure_parent_directory(path, containment_root=containment_root)
        queue.put(("ok", None))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(e).__name__, str(e)))


def ensure_parent_directory_bounded(
    path: str | Path,
    *,
    containment_root: str | Path | None = None,
    timeout_seconds: float | None = None,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> None:
    """Create save parents through a killable worker when timed.

    ``mkparents`` happens before the atomic writer owns target-temp cleanup.  A
    positive timeout gives the editor a recovery boundary around blocking
    parent-directory walks or unusual filesystem ``mkdir`` behavior.  A timed-out
    worker can leave already-created parent directories behind, but it cannot
    partially write the target file; this is the acceptable failure mode for the
    convenience ``mkparents`` surface.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        ensure_parent_directory(path, containment_root=containment_root)
        return

    ctx = worker_context or _file_write_worker_context()
    root = None if containment_root is None else str(containment_root)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_ensure_parent_directory_worker,
        args=(str(path), root),
        max_result_bytes=_FILE_WRITE_RESULT_MAX_BYTES,
    )
    payload = _collect_write_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        operation=f"filesystem parent creation: {path}",
        timeout_error=lambda: FileMkparentsTimeoutError(
            f"filesystem parent creation timed out after {timeout:.3g}s: {path}"
        ),
    )

    status = payload[0]
    if status == "ok":
        return
    if status == "err" and len(payload) >= 3:
        _raise_freshness_worker_error(str(payload[1]), str(payload[2]))
    raise RuntimeError(str(payload))


def _resolve_for_containment(path: str | Path) -> Path:
    """Return a best-effort absolute/resolved path for root checks."""

    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    try:
        return p.resolve(strict=False)
    except TypeError:  # pragma: no cover - old Python fallback
        try:
            return p.resolve()
        except OSError:
            return p.absolute()
    except OSError:
        try:
            return p.absolute()
        except OSError:
            return p


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        return path.is_relative_to(root)
    except AttributeError:  # pragma: no cover - Python <3.9 fallback
        try:
            path_s = str(path)
            root_s = str(root)
            return path_s == root_s or path_s.startswith(root_s.rstrip(os.sep) + os.sep)
        except Exception:
            return False


def assert_path_within_root(path: str | Path, root: str | Path | None) -> None:
    """Raise if *path* resolves outside *root*.

    This is the final, low-level sibling of the script capability preflight.
    Script-facing helpers validate user paths before calling the editor, but a
    symlink can change between that preflight and the actual write/read.  Recheck
    the concrete target near the filesystem operation so a late symlink swap
    fails closed instead of following ambient authority outside ``cap.fs-root``.
    """

    if root is None or str(root).strip() == "":
        return
    resolved_root = _resolve_for_containment(root)
    resolved_path = _resolve_for_containment(path)
    if not _is_relative_to(resolved_path, resolved_root):
        raise FileContainmentError(f"outside containment root ({resolved_root}): {resolved_path}")


def _follow_symlink_target(path: Path) -> tuple[Path, bool]:
    """Return the real write target while preserving a user-visible symlink.

    ``os.replace(tmp, link)`` replaces the symlink itself with a regular file.
    That is surprising for an editor save: opening/saving ``notes-link.md``
    should update the pointed-to file, not silently destroy the link.  Follow a
    bounded chain so atomic saves keep the same visible symlink topology that a
    plain file write would have followed.
    """

    cur = Path(path)
    seen: set[str] = set()
    followed = False
    for _ in range(40):
        try:
            if not cur.is_symlink():
                return cur, followed
            key = str(cur.absolute())
            if key in seen:
                raise OSError(errno.ELOOP, f"too many levels of symbolic links: {path}")
            seen.add(key)
            raw = os.readlink(cur)
        except OSError:
            raise
        target = Path(raw)
        if not target.is_absolute():
            target = cur.parent / target
        cur = target
        followed = True
    raise OSError(errno.ELOOP, f"too many levels of symbolic links: {path}")


def resolve_file_write_target(path: str | Path) -> ResolvedFileWriteTarget:
    """Resolve the concrete authority used by :func:`write_file_bytes`.

    The final visible symlink is preserved: the returned ``write_path`` names
    the pointed-to file while ``requested_path`` remains the path the user
    opened.  Callers that checkpoint or audit a save should use this seam rather
    than calling ``Path.resolve`` (which has different missing-link behavior).
    """

    requested = Path(path)
    write_path, followed = _follow_symlink_target(requested)
    return ResolvedFileWriteTarget(
        requested_path=requested,
        write_path=write_path,
        followed_symlink=bool(followed),
    )


def file_state_signature(path: str | Path) -> FileStateSignature:
    """Return a tiny on-disk freshness witness for a save target.

    The signature follows symlinks in the same way the editor save path does,
    so a buffer opened through a symlink is checked against the pointed-to file
    rather than the link inode.  The mode bits are included because atomic save
    preserves permissions; a chmod race is a real save-boundary conflict too.
    A stable ``MISSING_FILE_SIGNATURE`` sentinel
    means the target does not currently exist; callers can distinguish that
    from an unknown/pathless buffer.
    """

    target = resolve_file_write_target(path).write_path
    try:
        st = target.stat()
    except FileNotFoundError:
        return MISSING_FILE_SIGNATURE
    return (
        int(getattr(st, "st_dev", 0) or 0),
        int(getattr(st, "st_ino", 0) or 0),
        int(getattr(st, "st_size", 0) or 0),
        int(getattr(st, "st_mtime_ns", 0) or 0),
        int(getattr(st, "st_mode", 0) & 0o7777),
    )


def disk_freshness_signature(path: str | Path) -> FileStateSignature:
    """Return a save-guard freshness witness that distinguishes missing files."""

    return file_state_signature(path)


def is_missing_file_signature(sig: FileStateSignature | None) -> bool:
    return sig == MISSING_FILE_SIGNATURE


def file_content_digest(path: str | Path, *, max_bytes: int = 1024 * 1024) -> str | None:
    """Return a small content digest for existing files within ``max_bytes``.

    The digest follows symlinks exactly like the save path.  ``None`` means the
    target is missing, too large for the configured budget, or hashing was
    disabled with a non-positive budget.  I/O errors are allowed to propagate so
    callers do not silently downgrade a freshness check they explicitly asked
    for.
    """

    limit = int(max_bytes)
    if limit <= 0:
        return None
    target = resolve_file_write_target(path).write_path
    try:
        st = target.stat()
    except FileNotFoundError:
        return None
    if int(getattr(st, "st_size", 0) or 0) > limit:
        return None
    h = hashlib.blake2b(digest_size=16)
    with target.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def capture_file_freshness(path: str | Path, *, max_hash_bytes: int = 0) -> FileFreshness:
    """Capture a stat witness and optional small-file digest for ``path``."""

    sig = disk_freshness_signature(path)
    digest: str | None = None
    if not is_missing_file_signature(sig):
        digest = file_content_digest(path, max_bytes=max_hash_bytes)
    return FileFreshness(signature=sig, content_hash=digest)


def _capture_file_freshness_worker(
    path: str,
    max_hash_bytes: int,
    queue: object,
) -> None:
    try:
        result = capture_file_freshness(path, max_hash_bytes=int(max_hash_bytes))
        queue.put(("ok", result))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(e).__name__, str(e)))


def _raise_freshness_worker_error(kind: str, message: str) -> None:
    if kind == "FileFreshnessConflict":
        raise FileFreshnessConflict(message)
    if kind == "FileContainmentError":
        raise FileContainmentError(message)
    if kind == "FileNotFoundError":
        raise FileNotFoundError(message)
    if kind == "FileExistsError":
        raise FileExistsError(message)
    if kind == "IsADirectoryError":
        raise IsADirectoryError(message)
    if kind == "NotADirectoryError":
        raise NotADirectoryError(message)
    if kind == "PermissionError":
        raise PermissionError(message)
    if kind == "OSError":
        raise OSError(message)
    raise RuntimeError(message or kind)


def capture_file_freshness_bounded(
    path: str | Path,
    *,
    max_hash_bytes: int = 0,
    timeout_seconds: float | None = None,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> FileFreshness:
    """Capture save freshness through a killable worker when timed.

    Save preflight may include both path metadata and an optional small-file
    digest.  On unusual or remote filesystems either stat/open/read can block
    before the atomic write worker owns cleanup.  Positive timeouts move that
    preflight into the same short-lived process family as atomic writes;
    non-positive values keep the historical in-process path for lightweight
    embeddings and very hot status surfaces.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    if timeout <= 0:
        return capture_file_freshness(path, max_hash_bytes=max_hash_bytes)

    ctx = worker_context or _file_write_worker_context()
    proc, channel = create_one_shot_worker(
        ctx,
        target=_capture_file_freshness_worker,
        args=(str(path), int(max_hash_bytes)),
        max_result_bytes=_FILE_WRITE_RESULT_MAX_BYTES,
    )
    payload = _collect_write_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        operation=f"filesystem freshness check: {path}",
        timeout_error=lambda: FileFreshnessTimeoutError(
            f"filesystem freshness check timed out after {timeout:.3g}s: {path}"
        ),
    )

    status = payload[0]
    if status == "ok":
        return payload[1]
    if status == "err" and len(payload) >= 3:
        _raise_freshness_worker_error(str(payload[1]), str(payload[2]))
    raise RuntimeError(str(payload))


def freshness_changed(
    path: str | Path,
    expected: FileFreshness | None,
    *,
    max_hash_bytes: int = 0,
) -> bool:
    """Return whether ``path`` differs from an expected freshness witness."""

    if expected is None or expected.signature is None:
        return False
    current = capture_file_freshness(path, max_hash_bytes=max_hash_bytes)
    changed = current.signature != expected.signature
    if not changed and expected.content_hash is not None and current.content_hash is not None:
        changed = current.content_hash != expected.content_hash
    return bool(changed)


def assert_file_freshness(
    path: str | Path,
    expected: FileFreshness | None,
    *,
    max_hash_bytes: int = 0,
) -> None:
    """Raise if ``path`` has changed since ``expected`` was captured."""

    if freshness_changed(path, expected, max_hash_bytes=max_hash_bytes):
        raise FileFreshnessConflict(
            "file changed on disk before save commit; "
            "run `diff`, `revert!`, or `save!` to choose a recovery path"
        )


def _open_temp_file(
    parent: Path,
    basename: str,
    *,
    dir_fd: int | None = None,
    create_mode: int = 0o600,
) -> tuple[int, Path]:
    parent = Path(parent)
    for _ in range(128):
        tmp_name = build_private_temp_name(parent, basename)
        tmp = Path(tmp_name) if dir_fd is not None else parent / tmp_name
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        try:
            if dir_fd is None:
                fd = os.open(tmp, flags, int(create_mode))
            else:
                fd = os.open(str(tmp), flags, int(create_mode), dir_fd=dir_fd)
            return fd, tmp
        except FileExistsError:
            continue
    raise FileExistsError(f"could not create a unique temporary file in {parent}")


def _open_unnamed_mode_probe(
    parent: Path,
    *,
    dir_fd: int | None = None,
) -> int | None:
    """Open an unnamed ``0666`` probe inode when Linux/filesystem support it.

    ``O_TMPFILE`` removes the last hard-death residue window from default-mode
    discovery: the probe never has a pathname and is discarded when its file
    descriptor closes.  Capability absence falls back to the portable named,
    immediately-unlinked probe.  Permission, capacity, and I/O failures remain
    real save failures rather than being mislabeled as unsupported behavior.
    """

    if os.name == "nt" or not hasattr(os, "O_TMPFILE"):
        return None
    flags = os.O_RDWR | int(getattr(os, "O_TMPFILE"))
    if hasattr(os, "O_CLOEXEC"):
        flags |= int(getattr(os, "O_CLOEXEC"))
    try:
        if dir_fd is not None:
            return os.open(".", flags, 0o666, dir_fd=dir_fd)
        return os.open(parent, flags, 0o666)
    except OSError as exc:
        if exc.errno in _UNSUPPORTED_UNNAMED_TEMP_ERRNOS:
            return None
        raise


def _probe_default_create_mode(
    parent: Path,
    basename: str,
    *,
    dir_fd: int | None = None,
) -> int:
    """Measure this directory's ordinary ``0666`` create mode without payload.

    Reading the process umask by temporarily changing it is unsafe once other
    threads exist, and a bare umask calculation would miss default ACL effects.
    Prefer an unnamed ``O_TMPFILE`` inode.  On unsupported hosts/filesystems,
    create an empty disposable inode with the ordinary requested mode and
    unlink it before the sensitive document temp is created.  No document bytes
    are ever written to either probe.
    """

    anonymous_fd = _open_unnamed_mode_probe(parent, dir_fd=dir_fd)
    if anonymous_fd is not None:
        try:
            return int(stat.S_IMODE(os.fstat(anonymous_fd).st_mode))
        finally:
            _close_fd(anonymous_fd)

    fd, probe = _open_temp_file(
        parent,
        basename,
        dir_fd=dir_fd,
        create_mode=0o666,
    )
    probe_live = True
    try:
        # POSIX permits unlinking an open inode.  Remove the probe name before
        # inspecting it so a hard process death cannot strand even an empty
        # mode-probe file.  Windows keeps the short named fallback because it
        # generally refuses unlinking an open file.
        if os.name != "nt":
            _unlink_temp(probe, dir_fd=dir_fd)
            probe_live = False
        return int(stat.S_IMODE(os.fstat(fd).st_mode))
    finally:
        _close_fd(fd)
        if probe_live:
            _unlink_temp(probe, dir_fd=dir_fd)


def plan_atomic_write(
    path: str | Path,
    *,
    preserve_mode: bool = True,
    containment_root: str | Path | None = None,
) -> AtomicWritePlan:
    """Capture the concrete authority and final mode for one atomic save.

    The ordinary writer historically discovered the final mode only after the
    recovery record had been published.  A crash after ``os.replace`` but
    before ``chmod`` therefore left the journal unable to distinguish an
    intentionally-private ``0600`` file from an interrupted permission restore.
    This plan moves that small piece of intent ahead of the checkpoint and is
    then consumed verbatim by the writer.
    """

    requested = _canonical_authority_path(path)
    resolved = resolve_file_write_target(requested)
    write_target = _canonical_authority_path(resolved.write_path)
    assert_path_within_root(write_target, containment_root)

    preserved_mode: int | None = None
    parent_dev = 0
    parent_ino = 0
    if _dir_fd_io_available():
        dir_fd = _open_parent_dir_fd(write_target.parent, containment_root)
        try:
            parent_stat = os.fstat(dir_fd)
            parent_dev = int(getattr(parent_stat, "st_dev", 0) or 0)
            parent_ino = int(getattr(parent_stat, "st_ino", 0) or 0)
            name = write_target.name
            if _entry_is_dir_at(dir_fd, name):
                raise IsADirectoryError(f"is a directory: {write_target}")
            if preserve_mode:
                try:
                    preserved_mode = int(
                        stat.S_IMODE(os.stat(name, dir_fd=dir_fd).st_mode)
                    )
                except FileNotFoundError:
                    preserved_mode = None
            final_mode = int(
                preserved_mode
                if preserved_mode is not None
                else _probe_default_create_mode(
                    write_target.parent,
                    name,
                    dir_fd=dir_fd,
                )
            )
        finally:
            _close_fd(dir_fd)
    else:
        parent_stat = write_target.parent.stat()
        if not stat.S_ISDIR(parent_stat.st_mode):
            raise NotADirectoryError(f"not a directory: {write_target.parent}")
        parent_dev = int(getattr(parent_stat, "st_dev", 0) or 0)
        parent_ino = int(getattr(parent_stat, "st_ino", 0) or 0)
        if write_target.exists() and write_target.is_dir():
            raise IsADirectoryError(f"is a directory: {write_target}")
        if preserve_mode:
            try:
                preserved_mode = int(stat.S_IMODE(write_target.stat().st_mode))
            except FileNotFoundError:
                preserved_mode = None
        final_mode = int(
            preserved_mode
            if preserved_mode is not None
            else _probe_default_create_mode(write_target.parent, write_target.name)
        )

    return AtomicWritePlan(
        requested_path=str(requested),
        write_path=str(write_target),
        followed_symlink=bool(resolved.followed_symlink),
        preserve_mode=bool(preserve_mode),
        preserved_existing_mode=preserved_mode is not None,
        final_mode=int(final_mode),
        parent_dev=parent_dev,
        parent_ino=parent_ino,
    )


def _plan_atomic_write_worker(
    path: str,
    preserve_mode: bool,
    containment_root: str | None,
    temp_lease_id: str,
    queue: object,
) -> None:
    try:
        # A portable default-mode probe may need a short-lived named inode.
        # Binding it to this save's random lease lets timeout cleanup remove
        # only residue created by this exact planner process and transaction.
        with private_temp_lease(temp_lease_id):
            result = plan_atomic_write(
                path,
                preserve_mode=bool(preserve_mode),
                containment_root=containment_root,
            )
        queue.put(("ok", result))
    except BaseException as exc:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(exc).__name__, str(exc)))


def plan_atomic_write_bounded(
    path: str | Path,
    *,
    preserve_mode: bool = True,
    containment_root: str | Path | None = None,
    temp_lease_id: str | None = None,
    timeout_seconds: float | None = None,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> AtomicWritePlan:
    """Plan one atomic save through a killable worker when timed.

    Planning opens the target parent, resolves the final save authority, and
    may create an unnamed or immediately-unlinked inode to measure default ACL
    and umask effects.  Those are filesystem operations and can block just as
    the eventual write can.  A positive timeout keeps this new pre-checkpoint
    transaction from reopening an unbounded UI hang that the write worker was
    specifically introduced to contain.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    lease_id = normalize_save_lease_id(temp_lease_id, create=True)
    assert lease_id is not None
    if timeout <= 0:
        with private_temp_lease(lease_id):
            return plan_atomic_write(
                path,
                preserve_mode=preserve_mode,
                containment_root=containment_root,
            )

    ctx = worker_context or _file_write_worker_context()
    root = None if containment_root is None else str(containment_root)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_plan_atomic_write_worker,
        args=(str(path), bool(preserve_mode), root, lease_id),
        max_result_bytes=_FILE_WRITE_RESULT_MAX_BYTES,
    )
    payload = _collect_write_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        operation=f"atomic save planning: {path}",
        timeout_error=lambda: FileWritePlanTimeoutError(
            f"atomic save planning timed out after {timeout:.3g}s: {path}"
        ),
        abnormal_cleanup=lambda worker_pid: _cleanup_atomic_write_temps_bounded(
            path,
            worker_pid,
            lease_id=lease_id,
            containment_root=containment_root,
        ),
    )
    status = payload[0]
    if status == "ok":
        return payload[1]
    if status == "err" and len(payload) >= 3:
        _raise_file_write_worker_error(str(payload[1]), str(payload[2]))
    raise RuntimeError(str(payload))


def _assert_planned_parent_identity(
    plan: AtomicWritePlan | None,
    *,
    parent: Path,
    dir_fd: int | None = None,
) -> None:
    if plan is None:
        return
    st = os.fstat(dir_fd) if dir_fd is not None else parent.stat()
    actual = (
        int(getattr(st, "st_dev", 0) or 0),
        int(getattr(st, "st_ino", 0) or 0),
    )
    expected = (int(plan.parent_dev), int(plan.parent_ino))
    if actual != expected:
        raise FileFreshnessConflict(
            "atomic save parent authority changed after recovery checkpoint"
        )


def _validated_atomic_write_plan(
    plan: AtomicWritePlan | None,
    *,
    target: Path,
    resolved_target: ResolvedFileWriteTarget,
    preserve_mode: bool,
) -> AtomicWritePlan | None:
    if plan is None:
        return None
    if not isinstance(plan, AtomicWritePlan):
        raise TypeError("write_plan must be an AtomicWritePlan")
    requested = _canonical_authority_path(target)
    write_target = _canonical_authority_path(resolved_target.write_path)
    if requested != Path(plan.requested_path):
        raise FileFreshnessConflict(
            "atomic save request path changed after recovery checkpoint"
        )
    if write_target != Path(plan.write_path) or bool(
        resolved_target.followed_symlink
    ) != bool(plan.followed_symlink):
        raise FileFreshnessConflict(
            "atomic save target authority changed after recovery checkpoint"
        )
    if bool(preserve_mode) != bool(plan.preserve_mode):
        raise FileFreshnessConflict(
            "atomic save permission policy changed after recovery checkpoint"
        )
    mode = int(plan.final_mode)
    if mode < 0 or mode > 0o7777:
        raise ValueError("atomic write plan contains an invalid final mode")
    return plan


def _secure_temp_before_payload(
    tmp: Path,
    *,
    fd: int,
    dir_fd: int | None = None,
) -> None:
    """Make a named save temp owner-only before any document bytes are written.

    Sensitive temps are created with ``0600`` rather than created broad and
    narrowed later.  The extra chmod is defense in depth for unusual host mode
    handling.  The intended committed mode is restored only after namespace
    commit, so a hard crash before replace cannot strand readable unsaved bytes
    under a discoverable ``.micromax-*.tmp`` name.
    """

    _chmod_temp(tmp, 0o600, fd=fd, dir_fd=dir_fd)


def _write_payload_to_open_fd(fd: int, payload: bytes, *, fsync: bool) -> bool:
    """Write one complete payload while retaining the fd across atomic commit."""

    with os.fdopen(fd, "wb", closefd=False) as stream:
        stream.write(payload)
        stream.flush()
    if not fsync:
        return False
    os.fsync(fd)
    return True


def _apply_committed_mode(
    *,
    fd: int,
    mode: int,
    write_target: Path,
    name: str | None = None,
    dir_fd: int | None = None,
) -> None:
    """Apply final permission bits to the committed inode, preferring its fd."""

    if hasattr(os, "fchmod"):
        os.fchmod(fd, int(mode))
        return
    if dir_fd is not None and name is not None:
        os.chmod(name, int(mode), dir_fd=dir_fd)
        return
    os.chmod(write_target, int(mode))


def _run_write_fault(fault: FileWriteFault | None, stage: str) -> None:
    if fault is not None:
        fault(stage)


def _directory_sync_is_unsupported(exc: OSError) -> bool:
    """Return whether the host/filesystem explicitly rejects directory fsync.

    Some platforms expose ``O_DIRECTORY`` yet reject ``open`` or ``fsync`` for
    directories with an unsupported-operation errno.  That is a capability
    absence, so callers get an honest ``False`` witness.  Media, permission,
    and other I/O errors remain failures: swallowing those would falsely report
    a save as complete after the namespace update became uncertain.
    """

    return exc.errno in _UNSUPPORTED_DIRECTORY_SYNC_ERRNOS


def _fsync_directory(parent: Path) -> bool:
    if not hasattr(os, "O_DIRECTORY"):
        return False
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY")
    try:
        fd = os.open(parent, flags)
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


def _fsync_directory_fd(fd: int) -> bool:
    try:
        os.fsync(fd)
    except OSError as exc:
        if _directory_sync_is_unsupported(exc):
            return False
        raise
    return True


def _stat_signature(st: os.stat_result) -> FileStateSignature:
    return (
        int(getattr(st, "st_dev", 0) or 0),
        int(getattr(st, "st_ino", 0) or 0),
        int(getattr(st, "st_size", 0) or 0),
        int(getattr(st, "st_mtime_ns", 0) or 0),
        int(getattr(st, "st_mode", 0) & 0o7777),
    )


def _entry_is_symlink_at(dir_fd: int, name: str) -> bool:
    try:
        st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(int(getattr(st, "st_mode", 0) or 0))


def _entry_is_dir_at(dir_fd: int, name: str) -> bool:
    try:
        st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return stat.S_ISDIR(int(getattr(st, "st_mode", 0) or 0))


def _file_state_signature_at(dir_fd: int, name: str) -> FileStateSignature:
    try:
        st = os.stat(name, dir_fd=dir_fd)
    except FileNotFoundError:
        return MISSING_FILE_SIGNATURE
    return _stat_signature(st)


def _file_content_digest_at(dir_fd: int, name: str, *, max_bytes: int = 1024 * 1024) -> str | None:
    limit = int(max_bytes)
    if limit <= 0:
        return None
    try:
        st = os.stat(name, dir_fd=dir_fd)
    except FileNotFoundError:
        return None
    if int(getattr(st, "st_size", 0) or 0) > limit:
        return None
    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(name, flags, dir_fd=dir_fd)
    try:
        h = hashlib.blake2b(digest_size=16)
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            h.update(chunk)
        return h.hexdigest()
    finally:
        os.close(fd)


def _file_content_digest_fd(fd: int, *, max_bytes: int = 1024 * 1024) -> str | None:
    """Return a content digest for the already-open direct-write target fd."""

    limit = int(max_bytes)
    if limit <= 0:
        return None
    st = os.fstat(fd)
    if int(getattr(st, "st_size", 0) or 0) > limit:
        return None
    try:
        pos = os.lseek(fd, 0, os.SEEK_CUR)
    except OSError:
        pos = None
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        h = hashlib.blake2b(digest_size=16)
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            h.update(chunk)
        return h.hexdigest()
    finally:
        if pos is not None:
            try:
                os.lseek(fd, pos, os.SEEK_SET)
            except OSError:
                pass


def _direct_open_flags(expected: FileFreshness | None, *, expected_hash_max: int) -> int:
    """Return open flags for the direct-write lane.

    The direct writer must sometimes read the target after opening it but before
    truncating it.  Use read/write mode only when a small-file content witness is
    actually part of the freshness contract; otherwise keep the old write-only
    compatibility behavior.
    """

    needs_digest = bool(
        expected is not None
        and expected.content_hash is not None
        and int(expected_hash_max) > 0
        and not _expected_target_missing(expected)
    )
    return os.O_RDWR if needs_digest else os.O_WRONLY


def _assert_file_freshness_at(
    dir_fd: int,
    name: str,
    expected: FileFreshness | None,
    *,
    max_hash_bytes: int = 0,
    containment_root: str | Path | None = None,
) -> None:
    if containment_root is not None and _entry_is_symlink_at(dir_fd, name):
        raise FileContainmentError(
            f"target changed to a symbolic link before save commit: {name}"
        )
    if expected is None or expected.signature is None:
        return
    sig = _file_state_signature_at(dir_fd, name)
    changed = sig != expected.signature
    if not changed and expected.content_hash is not None:
        digest = _file_content_digest_at(dir_fd, name, max_bytes=max_hash_bytes)
        if digest is not None:
            changed = digest != expected.content_hash
    if changed:
        raise FileFreshnessConflict(
            "file changed on disk before save commit; "
            "run `diff`, `revert!`, or `save!` to choose a recovery path"
        )


def _expected_target_missing(expected: FileFreshness | None) -> bool:
    return bool(expected is not None and expected.signature == MISSING_FILE_SIGNATURE)


def _raise_freshness_conflict() -> None:
    raise FileFreshnessConflict(
        "file changed on disk before save commit; "
        "run `diff`, `revert!`, or `save!` to choose a recovery path"
    )


def _assert_open_fd_freshness(
    fd: int,
    expected: FileFreshness | None,
    *,
    max_hash_bytes: int = 0,
) -> None:
    """Raise if an opened direct-write fd no longer matches ``expected``.

    Direct writes cannot offer atomic replace semantics, but they should still
    bind the final truncation to the file that passed the freshness check.  Open
    first without ``O_TRUNC``, compare the fd's stat witness, compare the
    optional small-file content digest on that same fd, and only then
    truncate/write.  Missing-target creates are already protected by ``O_EXCL``
    and intentionally have a new fd signature.
    """

    if expected is None or expected.signature is None or _expected_target_missing(expected):
        return
    if _stat_signature(os.fstat(fd)) != expected.signature:
        _raise_freshness_conflict()
    if expected.content_hash is not None:
        digest = _file_content_digest_fd(fd, max_bytes=max_hash_bytes)
        if digest is not None and digest != expected.content_hash:
            _raise_freshness_conflict()


def _commit_missing_target_link_at(dir_fd: int, tmp: Path, name: str) -> bool:
    """Atomically create ``name`` from ``tmp`` only if ``name`` is still missing."""

    try:
        os.link(str(tmp), name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd, follow_symlinks=False)
        os.unlink(str(tmp), dir_fd=dir_fd)
        return True
    except FileExistsError as e:
        raise FileFreshnessConflict(
            "file changed on disk before save commit; "
            "run `diff`, `revert!`, or `save!` to choose a recovery path"
        ) from e
    except OSError:
        return False


def _commit_missing_target_link_path(tmp: Path, target: Path) -> bool:
    """Atomically create ``target`` from ``tmp`` only if ``target`` is still missing."""

    try:
        os.link(tmp, target, follow_symlinks=False)
        tmp.unlink()
        return True
    except FileExistsError as e:
        raise FileFreshnessConflict(
            "file changed on disk before save commit; "
            "run `diff`, `revert!`, or `save!` to choose a recovery path"
        ) from e
    except OSError:
        return False


def _unlink_temp(tmp: Path, *, dir_fd: int | None = None) -> None:
    try:
        if dir_fd is None:
            tmp.unlink()
        else:
            os.unlink(str(tmp), dir_fd=dir_fd)
    except FileNotFoundError:
        pass


def _chmod_temp(tmp: Path, mode: int, *, fd: int, dir_fd: int | None = None) -> None:
    if hasattr(os, "fchmod"):
        os.fchmod(fd, mode)
        return
    if dir_fd is None:
        os.chmod(tmp, mode)
    else:
        os.chmod(str(tmp), mode, dir_fd=dir_fd)


def _write_file_bytes_direct_dirfd(
    write_target: Path,
    payload: bytes,
    *,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
    containment_root: str | Path | None,
    fault: FileWriteFault | None,
) -> tuple[bool, bool]:
    file_synced = False
    directory_synced = False
    dir_fd = _open_parent_dir_fd(write_target.parent, containment_root)
    try:
        name = write_target.name
        if _entry_is_dir_at(dir_fd, name):
            raise IsADirectoryError(f"is a directory: {write_target}")
        _assert_file_freshness_at(
            dir_fd,
            name,
            expected_state,
            max_hash_bytes=expected_hash_max,
            containment_root=containment_root,
        )
        _assert_parent_fd_still_current(write_target.parent, dir_fd, containment_root)
        flags = _direct_open_flags(expected_state, expected_hash_max=expected_hash_max) | os.O_CREAT
        if _expected_target_missing(expected_state):
            flags |= os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= getattr(os, "O_NOFOLLOW")
        try:
            fd = os.open(name, flags, 0o666, dir_fd=dir_fd)
        except FileExistsError as e:
            raise FileFreshnessConflict(
                "file changed on disk before save commit; "
                "run `diff`, `revert!`, or `save!` to choose a recovery path"
            ) from e
        try:
            _assert_open_fd_freshness(
                fd, expected_state, max_hash_bytes=expected_hash_max
            )
            _run_write_fault(fault, "before_document_truncate")
            os.ftruncate(fd, 0)
            _run_write_fault(fault, "after_document_truncate")
            with os.fdopen(fd, "wb") as f:
                fd = -1
                f.write(payload)
                _run_write_fault(fault, "document_content_written")
                if fsync:
                    f.flush()
                    os.fsync(f.fileno())
                    file_synced = True
                    _run_write_fault(fault, "after_document_file_sync")
            if fsync:
                directory_synced = _fsync_directory_fd(dir_fd)
                _run_write_fault(fault, "after_document_directory_sync")
        finally:
            if fd >= 0:
                _close_fd(fd)
    finally:
        _close_fd(dir_fd)
    return file_synced, directory_synced


def _write_file_bytes_direct_path(
    write_target: Path,
    payload: bytes,
    *,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
    fault: FileWriteFault | None,
) -> tuple[bool, bool]:
    file_synced = False
    directory_synced = False
    assert_file_freshness(write_target, expected_state, max_hash_bytes=expected_hash_max)
    flags = _direct_open_flags(expected_state, expected_hash_max=expected_hash_max) | os.O_CREAT
    if _expected_target_missing(expected_state):
        flags |= os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= getattr(os, "O_NOFOLLOW")
    try:
        fd = os.open(write_target, flags, 0o666)
    except FileExistsError as e:
        raise FileFreshnessConflict(
            "file changed on disk before save commit; "
            "run `diff`, `revert!`, or `save!` to choose a recovery path"
        ) from e
    try:
        _assert_open_fd_freshness(fd, expected_state, max_hash_bytes=expected_hash_max)
        _run_write_fault(fault, "before_document_truncate")
        os.ftruncate(fd, 0)
        _run_write_fault(fault, "after_document_truncate")
        with os.fdopen(fd, "wb") as f:
            fd = -1
            f.write(payload)
            _run_write_fault(fault, "document_content_written")
            if fsync:
                f.flush()
                os.fsync(f.fileno())
                file_synced = True
                _run_write_fault(fault, "after_document_file_sync")
        if fsync:
            directory_synced = _fsync_directory(write_target.parent)
            _run_write_fault(fault, "after_document_directory_sync")
    finally:
        if fd >= 0:
            _close_fd(fd)
    return file_synced, directory_synced


def _write_file_bytes_atomic_dirfd(
    write_target: Path,
    payload: bytes,
    *,
    preserve_mode: bool,
    write_plan: AtomicWritePlan | None,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
    containment_root: str | Path | None,
    fault: FileWriteFault | None,
) -> tuple[bool, bool, bool, int]:
    file_synced = False
    directory_synced = False
    dir_fd = _open_parent_dir_fd(write_target.parent, containment_root)
    tmp: Path | None = None
    tmp_live = False
    mode: int | None = None
    fd = -1
    try:
        _assert_planned_parent_identity(
            write_plan,
            parent=write_target.parent,
            dir_fd=dir_fd,
        )
        name = write_target.name
        if _entry_is_dir_at(dir_fd, name):
            raise IsADirectoryError(f"is a directory: {write_target}")
        if write_plan is not None:
            final_mode = int(write_plan.final_mode)
            mode = final_mode if write_plan.preserved_existing_mode else None
        else:
            if preserve_mode:
                try:
                    mode = int(stat.S_IMODE(os.stat(name, dir_fd=dir_fd).st_mode))
                except FileNotFoundError:
                    mode = None
            final_mode = int(
                mode
                if mode is not None
                else _probe_default_create_mode(
                    write_target.parent,
                    name,
                    dir_fd=dir_fd,
                )
            )
        fd, tmp = _open_temp_file(
            write_target.parent,
            name,
            dir_fd=dir_fd,
            create_mode=0o600,
        )
        tmp_live = True
        try:
            _secure_temp_before_payload(tmp, fd=fd, dir_fd=dir_fd)
            _run_write_fault(fault, "document_temp_created")
            file_synced = _write_payload_to_open_fd(fd, payload, fsync=fsync)
            _run_write_fault(
                fault,
                "document_temp_synced" if file_synced else "document_temp_written",
            )
            _assert_parent_fd_still_current(write_target.parent, dir_fd, containment_root)
            _assert_file_freshness_at(
                dir_fd,
                name,
                expected_state,
                max_hash_bytes=expected_hash_max,
                containment_root=containment_root,
            )
            _run_write_fault(fault, "before_document_replace")
            if _expected_target_missing(expected_state) and _commit_missing_target_link_at(dir_fd, tmp, name):
                tmp_live = False
            else:
                os.replace(str(tmp), name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
                tmp_live = False
            _run_write_fault(fault, "after_document_replace")
            _apply_committed_mode(
                fd=fd,
                mode=final_mode,
                write_target=write_target,
                name=name,
                dir_fd=dir_fd,
            )
            _run_write_fault(fault, "after_document_mode_restore")
            if fsync:
                # Permission restoration is part of the committed inode state,
                # so synchronize again after chmod before claiming completion.
                os.fsync(fd)
                file_synced = True
                _run_write_fault(fault, "after_document_metadata_sync")
                directory_synced = _fsync_directory_fd(dir_fd)
                _run_write_fault(fault, "after_document_directory_sync")
        finally:
            if fd >= 0:
                _close_fd(fd)
    finally:
        if tmp_live and tmp is not None:
            _unlink_temp(tmp, dir_fd=dir_fd)
        _close_fd(dir_fd)
    return (
        bool(preserve_mode and mode is not None),
        file_synced,
        directory_synced,
        int(final_mode),
    )


def _write_file_bytes_impl_active(
    path: str | Path,
    payload: bytes,
    *,
    atomic: bool = True,
    preserve_mode: bool = True,
    fsync: bool = False,
    expected_state: FileFreshness | None = None,
    expected_hash_max: int = 0,
    containment_root: str | Path | None = None,
    write_plan: AtomicWritePlan | None = None,
    fault: FileWriteFault | None = None,
) -> FileWriteResult:
    """Write bytes to ``path`` with an editor-friendly atomic default.

    Atomic mode writes a temporary file in the final target directory and then
    commits it with ``os.replace``.  If ``path`` is a symlink, the replacement is
    applied to the resolved file target so saving does not destroy the link.

    ``expected_state`` is a near-commit conflict guard.  The editor already
    checks freshness before preparing the save payload; this writer rechecks the
    same witness after the temporary file is ready and immediately before the
    direct write/atomic replace.

    ``containment_root`` is used by script/capability surfaces.  It does not
    make the host filesystem a perfect sandbox, but it does re-resolve the
    concrete target near the write so late symlink swaps are refused.
    """

    target = Path(path)
    if not atomic:
        if write_plan is not None:
            raise ValueError("an atomic write plan cannot be used for a direct write")
        resolved_target = resolve_file_write_target(target)
        write_target = resolved_target.write_path
        followed_symlink = resolved_target.followed_symlink
        assert_path_within_root(write_target, containment_root)
        if _dir_fd_io_available():
            file_synced, directory_synced = _write_file_bytes_direct_dirfd(
                write_target,
                payload,
                fsync=bool(fsync),
                expected_state=expected_state,
                expected_hash_max=expected_hash_max,
                containment_root=containment_root,
                fault=fault,
            )
        else:
            file_synced, directory_synced = _write_file_bytes_direct_path(
                write_target,
                payload,
                fsync=bool(fsync),
                expected_state=expected_state,
                expected_hash_max=expected_hash_max,
                fault=fault,
            )
        return FileWriteResult(
            path=str(target),
            write_path=str(write_target),
            atomic=False,
            preserve_mode=False,
            fsync=bool(fsync),
            followed_symlink=bool(followed_symlink),
            file_synced=bool(file_synced),
            directory_synced=bool(directory_synced),
            final_mode=None,
        )

    resolved_target = resolve_file_write_target(target)
    write_target = resolved_target.write_path
    followed_symlink = resolved_target.followed_symlink
    assert_path_within_root(write_target, containment_root)
    write_plan = _validated_atomic_write_plan(
        write_plan,
        target=target,
        resolved_target=resolved_target,
        preserve_mode=preserve_mode,
    )
    if _dir_fd_io_available():
        (
            preserved_mode,
            file_synced,
            directory_synced,
            final_mode,
        ) = _write_file_bytes_atomic_dirfd(
            write_target,
            payload,
            preserve_mode=preserve_mode,
            write_plan=write_plan,
            fsync=fsync,
            expected_state=expected_state,
            expected_hash_max=expected_hash_max,
            containment_root=containment_root,
            fault=fault,
        )
        return FileWriteResult(
            path=str(target),
            write_path=str(write_target),
            atomic=True,
            preserve_mode=bool(preserved_mode),
            fsync=bool(fsync),
            followed_symlink=bool(followed_symlink),
            file_synced=bool(file_synced),
            directory_synced=bool(directory_synced),
            final_mode=int(final_mode),
        )
    if write_target.exists() and write_target.is_dir():
        raise IsADirectoryError(f"is a directory: {write_target}")
    parent = write_target.parent
    _assert_planned_parent_identity(write_plan, parent=parent)
    mode: int | None = None
    if write_plan is not None:
        final_mode = int(write_plan.final_mode)
        mode = final_mode if write_plan.preserved_existing_mode else None
    else:
        if preserve_mode:
            try:
                mode = int(stat.S_IMODE(write_target.stat().st_mode))
            except FileNotFoundError:
                mode = None
        final_mode = int(
            mode
            if mode is not None
            else _probe_default_create_mode(parent, write_target.name)
        )

    file_synced = False
    directory_synced = False
    fd, tmp = _open_temp_file(
        parent,
        write_target.name,
        create_mode=0o600,
    )
    tmp_live = True
    try:
        try:
            _secure_temp_before_payload(tmp, fd=fd)
            _run_write_fault(fault, "document_temp_created")
            file_synced = _write_payload_to_open_fd(fd, payload, fsync=fsync)
            _run_write_fault(
                fault,
                "document_temp_synced" if file_synced else "document_temp_written",
            )
            assert_path_within_root(write_target, containment_root)
            assert_file_freshness(write_target, expected_state, max_hash_bytes=expected_hash_max)
            _run_write_fault(fault, "before_document_replace")

            # Windows generally refuses replacing an open named temp.  Its
            # POSIX permission bits do not provide the local privacy boundary
            # enforced below, so restore the eventual mode before closing.
            if os.name == "nt":
                _chmod_temp(tmp, final_mode, fd=fd)
                if fsync:
                    os.fsync(fd)
                os.close(fd)
                fd = -1
            if _expected_target_missing(expected_state) and _commit_missing_target_link_path(tmp, write_target):
                tmp_live = False
            else:
                os.replace(tmp, write_target)
                tmp_live = False
            _run_write_fault(fault, "after_document_replace")
            if fd >= 0:
                _apply_committed_mode(
                    fd=fd,
                    mode=final_mode,
                    write_target=write_target,
                )
                _run_write_fault(fault, "after_document_mode_restore")
            if fsync:
                if fd >= 0:
                    os.fsync(fd)
                    file_synced = True
                    _run_write_fault(fault, "after_document_metadata_sync")
                directory_synced = _fsync_directory(parent)
                _run_write_fault(fault, "after_document_directory_sync")
        finally:
            if fd >= 0:
                os.close(fd)
    finally:
        if tmp_live:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass
    return FileWriteResult(
        path=str(target),
        write_path=str(write_target),
        atomic=True,
        preserve_mode=bool(preserve_mode and mode is not None),
        fsync=bool(fsync),
        followed_symlink=bool(followed_symlink),
        file_synced=bool(file_synced),
        directory_synced=bool(directory_synced),
        final_mode=int(final_mode),
    )


def _write_file_bytes_impl(
    path: str | Path,
    payload: bytes,
    *,
    atomic: bool = True,
    preserve_mode: bool = True,
    fsync: bool = False,
    expected_state: FileFreshness | None = None,
    expected_hash_max: int = 0,
    containment_root: str | Path | None = None,
    write_plan: AtomicWritePlan | None = None,
    temp_lease_id: str | None = None,
    fault: FileWriteFault | None = None,
) -> FileWriteResult:
    """Run one write with every named temp bound to the same private lease."""

    with private_temp_lease(temp_lease_id):
        return _write_file_bytes_impl_active(
            path,
            payload,
            atomic=atomic,
            preserve_mode=preserve_mode,
            fsync=fsync,
            expected_state=expected_state,
            expected_hash_max=expected_hash_max,
            containment_root=containment_root,
            write_plan=write_plan,
            fault=fault,
        )


def _file_write_worker_context() -> multiprocessing.context.BaseContext:
    """Return an isolated process context for killable file workers."""

    return isolated_worker_context()


def _collect_write_worker_result(
    proc: multiprocessing.Process,
    channel: WorkerResultChannel,
    *,
    timeout_seconds: float,
    operation: str,
    timeout_error: WorkerErrorFactory,
    abnormal_cleanup: WorkerCleanup | None = None,
) -> object:
    """Receive one finite frame and preserve save-specific timeout taxonomy."""

    try:
        return collect_worker_result(
            proc,
            channel,
            timeout_seconds=timeout_seconds,
            operation=operation,
            require_clean_exit=True,
            abnormal_cleanup=abnormal_cleanup,
        )
    except WorkerResultTimeoutError as exc:
        raise timeout_error() from exc


def _cleanup_micromax_temps_in_parent(
    parent: Path,
    worker_pid: int,
    *,
    lease_id: str | None,
    containment_root: str | Path | None,
) -> None:
    """Best-effort cleanup for temp files left by a killed atomic writer.

    Current temp names carry both the worker pid and the parent's unguessable
    save lease.  Require both, rather than treating pid as transaction
    authority: a reused pid or a second save by the same process must not widen
    cleanup.  Use the existing dir-fd path where available so cleanup stays
    bound to the directory that passed containment rather than following a
    swapped pathname during recovery.
    """

    if lease_id is None:
        return

    def owned_by_worker(name: str) -> bool:
        parsed = parse_private_temp_name(name)
        return bool(
            parsed is not None
            and int(parsed.owner.pid) == int(worker_pid)
            and parsed.lease_id == lease_id
        )

    try:
        if _dir_fd_io_available():
            dir_fd = _open_parent_dir_fd(parent, containment_root)
            try:
                with os.scandir(dir_fd) as entries:
                    for entry in entries:
                        name = str(entry.name)
                        if owned_by_worker(name):
                            try:
                                os.unlink(name, dir_fd=dir_fd)
                            except OSError:
                                pass
            finally:
                _close_fd(dir_fd)
            return
        assert_path_within_root(parent, containment_root)
        with os.scandir(parent) as entries:
            for entry in entries:
                name = str(entry.name)
                if owned_by_worker(name):
                    try:
                        os.unlink(parent / name)
                    except OSError:
                        pass
    except Exception:
        # Timeout reporting must not hang or fail just because cleanup evidence
        # is unavailable on an unusual filesystem.
        return


def _cleanup_atomic_write_temps_for_worker(
    path: str | Path,
    worker_pid: int | None,
    *,
    lease_id: str | None,
    containment_root: str | Path | None,
) -> None:
    if worker_pid is None:
        return
    target = Path(path)
    candidates: list[Path] = [target.parent]
    try:
        write_target = resolve_file_write_target(target).write_path
        candidates.append(write_target.parent)
    except Exception:
        pass
    seen: set[str] = set()
    for parent in candidates:
        # Cleanup authority is transaction lease + worker PID, not basename.
        # Deduplicate directories so a nominal symlink and its concrete target
        # in the same parent do not trigger two complete scans.
        key = str(_absolute_path(parent))
        if key in seen:
            continue
        seen.add(key)
        _cleanup_micromax_temps_in_parent(
            parent,
            int(worker_pid),
            lease_id=lease_id,
            containment_root=containment_root,
        )


def _cleanup_atomic_write_temps_worker(
    path: str,
    worker_pid: int,
    lease_id: str,
    containment_root: str | None,
    queue: object,
) -> None:
    try:
        _cleanup_atomic_write_temps_for_worker(
            path,
            worker_pid,
            lease_id=lease_id,
            containment_root=containment_root,
        )
        queue.put(("ok", None))
    except BaseException as exc:  # pragma: no cover - best-effort child report.
        queue.put(("err", type(exc).__name__, str(exc)))


def _cleanup_atomic_write_temps_bounded(
    path: str | Path,
    worker_pid: int | None,
    *,
    lease_id: str | None,
    containment_root: str | Path | None,
    timeout_seconds: float = 0.5,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> None:
    """Best-effort residue cleanup without reopening the timeout hang.

    Resolving a retargeted symlink or scanning a remote parent can block for the
    same reason the original save worker did.  Cleanup therefore gets its own
    small killable budget.  Exhaustion deliberately leaves an owner-only temp
    for the explicit recovery inventory rather than delaying the original
    timeout indefinitely.
    """

    if worker_pid is None or lease_id is None:
        return
    timeout = max(
        0.01,
        normalize_worker_timeout_seconds(timeout_seconds, default=0.5),
    )
    try:
        ctx = worker_context or _file_write_worker_context()
        root = None if containment_root is None else str(containment_root)
        proc, channel = create_one_shot_worker(
            ctx,
            target=_cleanup_atomic_write_temps_worker,
            args=(str(path), int(worker_pid), str(lease_id), root),
            max_result_bytes=_FILE_WRITE_RESULT_MAX_BYTES,
        )
        payload = _collect_write_worker_result(
            proc,
            channel,
            timeout_seconds=timeout,
            operation=f"atomic save residue cleanup: {path}",
            timeout_error=lambda: RuntimeError(
                f"atomic save residue cleanup exceeded {timeout:.3g}s"
            ),
        )
        if not payload or payload[0] != "ok":
            return
    except BaseException:
        # Timeout cleanup is a privacy/waste optimization.  The original save
        # failure remains authoritative, and explicit recovertemps/recoverclean
        # can safely inventory a temp that could not be removed here.
        return


def _write_file_bytes_worker(
    path: str,
    payload: bytes,
    atomic: bool,
    preserve_mode: bool,
    write_plan: AtomicWritePlan | None,
    temp_lease_id: str | None,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
    containment_root: str | None,
    queue: object,
) -> None:
    try:
        # Bind the lease at the process entrypoint as well as inside the normal
        # implementation wrapper.  This keeps auxiliary probes and injected
        # worker implementations inside the same cleanup authority.
        with private_temp_lease(temp_lease_id):
            result = _write_file_bytes_impl(
                path,
                payload,
                atomic=bool(atomic),
                preserve_mode=bool(preserve_mode),
                write_plan=write_plan,
                temp_lease_id=temp_lease_id,
                fsync=bool(fsync),
                expected_state=expected_state,
                expected_hash_max=int(expected_hash_max),
                containment_root=containment_root,
            )
        queue.put(("ok", result))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(e).__name__, str(e)))


def _raise_file_write_worker_error(kind: str, message: str) -> None:
    if kind == "FileFreshnessConflict":
        raise FileFreshnessConflict(message)
    if kind == "FileContainmentError":
        raise FileContainmentError(message)
    if kind == "FileNotFoundError":
        raise FileNotFoundError(message)
    if kind == "FileExistsError":
        raise FileExistsError(message)
    if kind == "IsADirectoryError":
        raise IsADirectoryError(message)
    if kind == "NotADirectoryError":
        raise NotADirectoryError(message)
    if kind == "PermissionError":
        raise PermissionError(message)
    if kind == "OSError":
        raise OSError(message)
    raise RuntimeError(message or kind)


def _write_file_bytes_bounded(
    path: str | Path,
    payload: bytes,
    *,
    atomic: bool,
    preserve_mode: bool,
    write_plan: AtomicWritePlan | None,
    temp_lease_id: str | None,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
    containment_root: str | Path | None,
    timeout_seconds: float,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> FileWriteResult:
    timeout = max(
        0.01,
        normalize_worker_timeout_seconds(timeout_seconds, default=5.0),
    )
    ctx = worker_context or _file_write_worker_context()
    root = None if containment_root is None else str(containment_root)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_write_file_bytes_worker,
        args=(
            str(path),
            payload,
            bool(atomic),
            bool(preserve_mode),
            write_plan,
            temp_lease_id,
            bool(fsync),
            expected_state,
            int(expected_hash_max),
            root,
        ),
        max_result_bytes=_FILE_WRITE_RESULT_MAX_BYTES,
    )
    payload_out = _collect_write_worker_result(
        proc,
        channel,
        timeout_seconds=timeout,
        operation=f"filesystem write: {path}",
        timeout_error=lambda: FileWriteTimeoutError(
            f"filesystem write timed out after {timeout:.3g}s: {path}"
        ),
        abnormal_cleanup=lambda worker_pid: _cleanup_atomic_write_temps_bounded(
            path,
            worker_pid,
            lease_id=temp_lease_id,
            containment_root=containment_root,
        ),
    )

    status = payload_out[0]
    if status == "ok":
        return payload_out[1]
    if status == "err" and len(payload_out) >= 3:
        _raise_file_write_worker_error(str(payload_out[1]), str(payload_out[2]))
    raise RuntimeError(str(payload_out))


def write_file_bytes(
    path: str | Path,
    payload: bytes,
    *,
    atomic: bool = True,
    preserve_mode: bool = True,
    write_plan: AtomicWritePlan | None = None,
    temp_lease_id: str | None = None,
    fsync: bool = False,
    expected_state: FileFreshness | None = None,
    expected_hash_max: int = 0,
    containment_root: str | Path | None = None,
    timeout_seconds: float | None = None,
    worker_context: multiprocessing.context.BaseContext | None = None,
    _fault: FileWriteFault | None = None,
) -> FileWriteResult:
    """Write bytes to ``path`` with an optional killable atomic timeout.

    Positive ``timeout_seconds`` values run atomic writes in a short-lived worker
    process so the host can kill stuck open/write/fsync/rename work.  The worker
    owns the temp-file commit; if it is killed, the parent removes only temp
    files carrying both that worker pid and this write's random save lease on a
    best-effort basis.  Direct writes deliberately remain in-process even when a
    timeout is supplied, because killing a direct writer can leave the real
    target partially written.
    """

    timeout = normalize_worker_timeout_seconds(
        timeout_seconds, default=5.0, none_disables=True
    )
    effective_temp_lease_id = (
        normalize_save_lease_id(temp_lease_id, create=True)
        if bool(atomic)
        else normalize_save_lease_id(temp_lease_id, create=False)
    )
    if timeout > 0 and bool(atomic) and _fault is None:
        return _write_file_bytes_bounded(
            path,
            payload,
            atomic=bool(atomic),
            preserve_mode=bool(preserve_mode),
            write_plan=write_plan,
            temp_lease_id=effective_temp_lease_id,
            fsync=bool(fsync),
            expected_state=expected_state,
            expected_hash_max=int(expected_hash_max),
            containment_root=containment_root,
            timeout_seconds=timeout,
            worker_context=worker_context,
        )
    return _write_file_bytes_impl(
        path,
        payload,
        atomic=bool(atomic),
        preserve_mode=bool(preserve_mode),
        write_plan=write_plan,
        temp_lease_id=effective_temp_lease_id,
        fsync=bool(fsync),
        expected_state=expected_state,
        expected_hash_max=int(expected_hash_max),
        containment_root=containment_root,
        fault=_fault,
    )

