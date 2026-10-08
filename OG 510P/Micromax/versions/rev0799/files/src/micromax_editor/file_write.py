from __future__ import annotations

from dataclasses import dataclass
import errno
import hashlib
import os
from pathlib import Path
import secrets
import stat


FileStateSignature = tuple[int, int, int, int, int]
MISSING_FILE_SIGNATURE: FileStateSignature = (-1, -1, -1, -1, -1)


@dataclass(frozen=True)
class FileFreshness:
    """Expected on-disk state used by the save conflict boundary."""

    signature: FileStateSignature | None
    content_hash: str | None = None


class FileFreshnessConflict(RuntimeError):
    """Raised when a save target changed after the caller's freshness check."""


class FileContainmentError(RuntimeError):
    """Raised when a file operation would escape its capability root."""


@dataclass(frozen=True)
class FileWriteResult:
    """Small witness for the save path actually used."""

    path: str
    write_path: str
    atomic: bool
    preserve_mode: bool
    fsync: bool
    followed_symlink: bool = False


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
    """Raise if an opened parent fd no longer matches the pathname parent."""

    fd_path = _resolve_dir_fd(dir_fd)
    if fd_path is None:
        return
    current_path = _resolve_for_containment(parent)
    if current_path == fd_path:
        return
    if containment_root is not None:
        assert_path_within_root(current_path, containment_root)
    raise FileContainmentError(
        f"parent directory changed before save commit ({fd_path} != {current_path})"
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

    target, _followed = _follow_symlink_target(Path(path))
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
    target, _followed = _follow_symlink_target(Path(path))
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


def _open_temp_file(parent: Path, basename: str, *, dir_fd: int | None = None) -> tuple[int, Path]:
    safe_base = str(basename or "file").replace(os.sep, "_")
    if os.altsep:
        safe_base = safe_base.replace(os.altsep, "_")
    parent = Path(parent)
    for _ in range(128):
        token = secrets.token_hex(8)
        tmp_name = f".{safe_base}.micromax-{os.getpid()}-{token}.tmp"
        tmp = Path(tmp_name) if dir_fd is not None else parent / tmp_name
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        try:
            if dir_fd is None:
                fd = os.open(tmp, flags, 0o666)
            else:
                fd = os.open(str(tmp), flags, 0o666, dir_fd=dir_fd)
            return fd, tmp
        except FileExistsError:
            continue
    raise FileExistsError(f"could not create a unique temporary file in {parent}")


def _fsync_directory(parent: Path) -> None:
    if not hasattr(os, "O_DIRECTORY"):
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY")
    fd = os.open(parent, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_directory_fd(fd: int) -> None:
    os.fsync(fd)


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
) -> None:
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
            os.ftruncate(fd, 0)
            with os.fdopen(fd, "wb") as f:
                fd = -1
                f.write(payload)
                if fsync:
                    f.flush()
                    os.fsync(f.fileno())
            if fsync:
                _fsync_directory_fd(dir_fd)
        finally:
            if fd >= 0:
                _close_fd(fd)
    finally:
        _close_fd(dir_fd)


def _write_file_bytes_direct_path(
    write_target: Path,
    payload: bytes,
    *,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
) -> None:
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
        os.ftruncate(fd, 0)
        with os.fdopen(fd, "wb") as f:
            fd = -1
            f.write(payload)
            if fsync:
                f.flush()
                os.fsync(f.fileno())
        if fsync:
            _fsync_directory(write_target.parent)
    finally:
        if fd >= 0:
            _close_fd(fd)


def _write_file_bytes_atomic_dirfd(
    write_target: Path,
    payload: bytes,
    *,
    preserve_mode: bool,
    fsync: bool,
    expected_state: FileFreshness | None,
    expected_hash_max: int,
    containment_root: str | Path | None,
) -> bool:
    dir_fd = _open_parent_dir_fd(write_target.parent, containment_root)
    tmp: Path | None = None
    tmp_live = False
    mode: int | None = None
    try:
        name = write_target.name
        if _entry_is_dir_at(dir_fd, name):
            raise IsADirectoryError(f"is a directory: {write_target}")
        if preserve_mode:
            try:
                mode = int(os.stat(name, dir_fd=dir_fd).st_mode & 0o7777)
            except FileNotFoundError:
                mode = None
        fd, tmp = _open_temp_file(write_target.parent, name, dir_fd=dir_fd)
        tmp_live = True
        try:
            if mode is not None:
                _chmod_temp(tmp, mode, fd=fd, dir_fd=dir_fd)
            with os.fdopen(fd, "wb") as f:
                fd = -1
                f.write(payload)
                if fsync:
                    f.flush()
                    os.fsync(f.fileno())
            _assert_parent_fd_still_current(write_target.parent, dir_fd, containment_root)
            _assert_file_freshness_at(
                dir_fd,
                name,
                expected_state,
                max_hash_bytes=expected_hash_max,
                containment_root=containment_root,
            )
            if _expected_target_missing(expected_state) and _commit_missing_target_link_at(dir_fd, tmp, name):
                tmp_live = False
            else:
                os.replace(str(tmp), name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
                tmp_live = False
            if fsync:
                _fsync_directory_fd(dir_fd)
        finally:
            if fd >= 0:
                _close_fd(fd)
    finally:
        if tmp_live and tmp is not None:
            _unlink_temp(tmp, dir_fd=dir_fd)
        _close_fd(dir_fd)
    return bool(preserve_mode and mode is not None)


def write_file_bytes(
    path: str | Path,
    payload: bytes,
    *,
    atomic: bool = True,
    preserve_mode: bool = True,
    fsync: bool = False,
    expected_state: FileFreshness | None = None,
    expected_hash_max: int = 0,
    containment_root: str | Path | None = None,
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
        write_target, followed_symlink = _follow_symlink_target(target)
        assert_path_within_root(write_target, containment_root)
        if _dir_fd_io_available():
            _write_file_bytes_direct_dirfd(
                write_target,
                payload,
                fsync=bool(fsync),
                expected_state=expected_state,
                expected_hash_max=expected_hash_max,
                containment_root=containment_root,
            )
        else:
            _write_file_bytes_direct_path(
                write_target,
                payload,
                fsync=bool(fsync),
                expected_state=expected_state,
                expected_hash_max=expected_hash_max,
            )
        return FileWriteResult(
            path=str(target),
            write_path=str(write_target),
            atomic=False,
            preserve_mode=False,
            fsync=bool(fsync),
            followed_symlink=bool(followed_symlink),
        )

    write_target, followed_symlink = _follow_symlink_target(target)
    assert_path_within_root(write_target, containment_root)
    if _dir_fd_io_available():
        preserved_mode = _write_file_bytes_atomic_dirfd(
            write_target,
            payload,
            preserve_mode=preserve_mode,
            fsync=fsync,
            expected_state=expected_state,
            expected_hash_max=expected_hash_max,
            containment_root=containment_root,
        )
        return FileWriteResult(
            path=str(target),
            write_path=str(write_target),
            atomic=True,
            preserve_mode=bool(preserved_mode),
            fsync=bool(fsync),
            followed_symlink=bool(followed_symlink),
        )
    if write_target.exists() and write_target.is_dir():
        raise IsADirectoryError(f"is a directory: {write_target}")
    parent = write_target.parent
    mode: int | None = None
    if preserve_mode:
        try:
            mode = int(write_target.stat().st_mode & 0o7777)
        except FileNotFoundError:
            mode = None

    fd, tmp = _open_temp_file(parent, write_target.name)
    tmp_live = True
    try:
        try:
            with os.fdopen(fd, "wb") as f:
                fd = -1
                f.write(payload)
                if fsync:
                    f.flush()
                    os.fsync(f.fileno())
            if mode is not None:
                os.chmod(tmp, mode)
            assert_path_within_root(write_target, containment_root)
            assert_file_freshness(write_target, expected_state, max_hash_bytes=expected_hash_max)
            if _expected_target_missing(expected_state) and _commit_missing_target_link_path(tmp, write_target):
                tmp_live = False
            else:
                os.replace(tmp, write_target)
                tmp_live = False
            if fsync:
                _fsync_directory(parent)
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
    )
