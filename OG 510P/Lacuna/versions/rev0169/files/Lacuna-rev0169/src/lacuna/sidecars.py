from __future__ import annotations

import errno
import hashlib
import json
import os
import secrets
import shlex
import shutil
import stat
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

from .errors import LacunaError
from .util import atomic_write_json, canonical_json, sha256_text

DEFAULT_MEMBER_LIMIT = 16 * 1024 * 1024


def canonical_json_digest(value: Any, *, error_code: str, label: str) -> str:
    """Hash one JSON value under Lacuna's canonical JSON contract."""
    try:
        return sha256_text(canonical_json(value))
    except (TypeError, ValueError) as exc:
        raise LacunaError(error_code, f"{label} is not canonical JSON: {exc}") from exc


def _open_authenticated_sidecar_member(
    path: Path,
    *,
    label: str,
    error_prefix: str,
    max_bytes: int,
) -> tuple[int, os.stat_result]:
    """Open and authenticate one bounded, single-link regular sidecar member."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError as exc:
        raise LacunaError(
            f"{error_prefix}-artifact-missing",
            f"required {label} is missing: {path}",
        ) from exc
    except OSError as exc:
        code = (
            f"{error_prefix}-member-unsafe"
            if exc.errno in {errno.ELOOP, errno.EMLINK}
            else f"{error_prefix}-read-failed"
        )
        raise LacunaError(code, f"cannot open {label} at {path}: {exc}") from exc
    try:
        before = os.fstat(descriptor)
        try:
            link_before = os.lstat(path)
        except OSError as exc:
            raise LacunaError(
                f"{error_prefix}-member-unsafe",
                f"cannot authenticate {label} path at {path}: {exc}",
            ) from exc
        if (
            not stat.S_ISREG(before.st_mode)
            or not stat.S_ISREG(link_before.st_mode)
            or before.st_dev != link_before.st_dev
            or before.st_ino != link_before.st_ino
            or before.st_nlink != 1
            or link_before.st_nlink != 1
        ):
            raise LacunaError(
                f"{error_prefix}-member-unsafe",
                f"{label} must be one non-symlink regular file with one link",
                {"path": str(path)},
            )
        if before.st_size > max_bytes:
            raise LacunaError(
                f"{error_prefix}-member-too-large",
                f"{label} exceeds the sidecar read limit",
                {"path": str(path), "size": before.st_size, "limit": max_bytes},
            )
        return descriptor, before
    except Exception:
        os.close(descriptor)
        raise


def _authenticate_sidecar_member_after_read(
    path: Path,
    descriptor: int,
    before: os.stat_result,
    *,
    label: str,
    error_prefix: str,
) -> None:
    """Confirm that a descriptor and its pathname stayed bound through a read."""
    after = os.fstat(descriptor)
    try:
        link_after = os.lstat(path)
    except OSError as exc:
        raise LacunaError(
            f"{error_prefix}-member-unsafe",
            f"{label} path changed during read at {path}: {exc}",
        ) from exc
    stable_fields = (
        "st_dev",
        "st_ino",
        "st_nlink",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
    )
    if any(
        getattr(before, field, None) != getattr(after, field, None)
        for field in stable_fields
    ):
        raise LacunaError(
            f"{error_prefix}-member-unsafe",
            f"{label} changed while it was being read",
            {"path": str(path)},
        )
    if (
        after.st_dev != link_after.st_dev
        or after.st_ino != link_after.st_ino
        or after.st_nlink != 1
        or link_after.st_nlink != 1
        or not stat.S_ISREG(link_after.st_mode)
    ):
        raise LacunaError(
            f"{error_prefix}-member-unsafe",
            f"{label} path was substituted during read",
            {"path": str(path)},
        )


def read_sidecar_member_bytes(
    path: Path,
    *,
    label: str,
    error_prefix: str,
    max_bytes: int = DEFAULT_MEMBER_LIMIT,
) -> bytes:
    """Read one sidecar member through a descriptor bound to one regular file.

    Digest custody is meaningful only when the path inspected before and after
    the read names the same regular file. This refuses symlinks, hard links,
    non-regular files, oversized members, and detected substitution or mutation
    during the read. It remains a cooperative same-host boundary, not a hostile
    same-user sandbox.
    """
    descriptor, before = _open_authenticated_sidecar_member(
        path,
        label=label,
        error_prefix=error_prefix,
        max_bytes=max_bytes,
    )
    try:
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        value = b"".join(chunks)
        if len(value) > max_bytes:
            raise LacunaError(
                f"{error_prefix}-member-too-large",
                f"{label} exceeds the sidecar read limit",
                {"path": str(path), "size": len(value), "limit": max_bytes},
            )
        _authenticate_sidecar_member_after_read(
            path,
            descriptor,
            before,
            label=label,
            error_prefix=error_prefix,
        )
        return value
    finally:
        os.close(descriptor)


def _scan_exact_token_window(
    window: bytes,
    token: bytes,
    *,
    window_start: int,
    search_cursor: int,
) -> tuple[int, int]:
    """Scan one overlapping window using whole-stream non-overlap semantics.

    ``search_cursor`` is the first global byte offset at which the next match may
    begin. After scanning, starts that now have enough following bytes to decide
    are retired even when they did not match. This preserves ``bytes.count``
    semantics across chunk boundaries, including self-overlapping tokens.
    """
    count = 0
    offset = max(0, search_cursor - window_start)
    while True:
        position = window.find(token, offset)
        if position < 0:
            break
        global_position = window_start + position
        count += 1
        search_cursor = global_position + len(token)
        offset = search_cursor - window_start
    first_undecidable_start = window_start + len(window) - len(token) + 1
    search_cursor = max(search_cursor, first_undecidable_start, 0)
    return count, search_cursor


def scan_sidecar_member_exact_tokens(
    path: Path,
    *,
    exact_tokens: list[bytes] | tuple[bytes, ...],
    label: str,
    error_prefix: str,
    max_bytes: int = DEFAULT_MEMBER_LIMIT,
    chunk_bytes: int = 65536,
) -> dict[str, Any]:
    """Hash and exact-token-scan one authenticated member without retaining its body.

    Matches that straddle read boundaries are counted exactly once. Counts use
    the same non-overlapping semantics as the existing in-memory canary scan.
    The return object contains ``size``, ``sha256``, and one occurrence count
    per input token, in input order.
    """
    if isinstance(chunk_bytes, bool) or not isinstance(chunk_bytes, int) or chunk_bytes < 1:
        raise ValueError("chunk_bytes must be a positive integer")
    tokens = tuple(exact_tokens)
    if any(not isinstance(token, bytes) or not token for token in tokens):
        raise ValueError("exact_tokens must contain only nonempty bytes values")
    max_token_bytes = max((len(token) for token in tokens), default=1)
    descriptor, before = _open_authenticated_sidecar_member(
        path,
        label=label,
        error_prefix=error_prefix,
        max_bytes=max_bytes,
    )
    digest = hashlib.sha256()
    counts = [0 for _ in tokens]
    search_cursors = [0 for _ in tokens]
    total = 0
    tail = b""
    try:
        while True:
            chunk = os.read(descriptor, chunk_bytes)
            if not chunk:
                break
            total_before = total
            total += len(chunk)
            if total > max_bytes:
                raise LacunaError(
                    f"{error_prefix}-member-too-large",
                    f"{label} exceeds the sidecar read limit",
                    {"path": str(path), "size": total, "limit": max_bytes},
                )
            digest.update(chunk)
            window = tail + chunk
            window_start = total_before - len(tail)
            for index, token in enumerate(tokens):
                added, search_cursors[index] = _scan_exact_token_window(
                    window,
                    token,
                    window_start=window_start,
                    search_cursor=search_cursors[index],
                )
                counts[index] += added
            tail = window[-(max_token_bytes - 1) :] if max_token_bytes > 1 else b""
        _authenticate_sidecar_member_after_read(
            path,
            descriptor,
            before,
            label=label,
            error_prefix=error_prefix,
        )
        return {
            "size": total,
            "sha256": digest.hexdigest(),
            "occurrence_counts": counts,
        }
    finally:
        os.close(descriptor)


def write_sidecar_json_once_or_verify(
    path: Path,
    value: dict[str, Any],
    *,
    label: str,
    error_prefix: str,
    mismatch_code: str,
) -> bool:
    """Publish one immutable JSON member or verify an exact prior publication.

    Sidecar transitions write authority-bearing artifacts before advancing their
    manifest. A crash in that narrow window must not let a retry silently
    replace the first artifact. Cooperative callers already hold the sidecar
    lock; this helper makes retry semantics explicit: an absent path is written,
    an exact existing object is reused, and any different existing object is a
    typed refusal. It is not a hostile same-user filesystem boundary.

    Returns ``True`` when a new member was written and ``False`` when an exact
    existing member was reused.
    """
    path = Path(path)
    if os.path.lexists(path):
        existing = read_sidecar_json_object(
            path,
            label=label,
            error_prefix=error_prefix,
            root_error_code=f"bad-{error_prefix}-artifact",
        )
        if existing != value:
            raise LacunaError(
                mismatch_code,
                f"refusing to replace a different already-published {label}",
                {"path": str(path)},
            )
        return False
    atomic_write_json(path, value)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return True


def read_sidecar_json_object(
    path: Path,
    *,
    label: str,
    error_prefix: str,
    root_error_code: str,
) -> dict[str, Any]:
    try:
        text = read_sidecar_member_bytes(
            path,
            label=label,
            error_prefix=error_prefix,
        ).decode("utf-8")
        value = json.loads(text)
    except UnicodeError as exc:
        raise LacunaError(
            f"{error_prefix}-read-failed",
            f"{label} at {path} is not UTF-8: {exc}",
        ) from exc
    except json.JSONDecodeError as exc:
        raise LacunaError(
            f"{error_prefix}-read-failed",
            f"cannot parse {label} at {path}: {exc}",
        ) from exc
    if not isinstance(value, dict):
        raise LacunaError(root_error_code, f"{label} root must be a JSON object")
    return value


def read_sidecar_text(path: Path, *, label: str, error_prefix: str) -> str:
    try:
        return read_sidecar_member_bytes(
            path,
            label=label,
            error_prefix=error_prefix,
        ).decode("utf-8")
    except UnicodeError as exc:
        raise LacunaError(
            f"{error_prefix}-read-failed",
            f"{label} at {path} is not UTF-8: {exc}",
        ) from exc


def resolve_sidecar_member_directory(
    root: Path,
    relative_path: str | PurePosixPath,
    *,
    error_prefix: str,
    label: str,
) -> Path:
    """Resolve one fixed child directory without following mutable symlink components.

    A canonical manifest path is not enough when an owner-controlled child directory can
    later be replaced by a symlink.  Walk every relative component with ``lstat`` and
    require a real directory beneath the already-resolved sidecar root.  This narrows
    accidental and same-user substitution; it is not a mount-namespace or hostile-host
    confinement boundary.
    """
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise LacunaError(
            f"{error_prefix}-member-missing",
            f"cannot resolve sidecar root for {label}: {exc}",
        ) from exc
    relative = PurePosixPath(relative_path)
    if relative.is_absolute() or not relative.parts or any(
        part in {"", ".", ".."} for part in relative.parts
    ):
        raise LacunaError(
            f"{error_prefix}-member-unsafe",
            f"{label} must use one normalized relative directory path",
            {"path": str(relative)},
        )
    current = resolved_root
    for part in relative.parts:
        candidate = current / part
        try:
            metadata = os.lstat(candidate)
        except OSError as exc:
            raise LacunaError(
                f"{error_prefix}-member-missing",
                f"cannot inspect {label} component {candidate}: {exc}",
            ) from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise LacunaError(
                f"{error_prefix}-member-unsafe",
                f"{label} components must be real directories, not links or other nodes",
                {"path": str(candidate)},
            )
        current = candidate
    try:
        resolved = current.resolve(strict=True)
    except OSError as exc:
        raise LacunaError(
            f"{error_prefix}-member-missing",
            f"cannot resolve {label} at {current}: {exc}",
        ) from exc
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise LacunaError(
            f"{error_prefix}-member-unsafe",
            f"{label} escapes its sidecar root",
            {"path": str(resolved)},
        ) from exc
    return resolved


def make_private_directory(path: Path) -> None:
    """Create one owner-private directory and fail rather than merge with it."""
    path.mkdir(parents=True, exist_ok=False, mode=0o700)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass


def resolve_sidecar_directory(
    value: str | Path,
    *,
    manifest_file: str,
    unknown_code: str,
    kind_label: str,
) -> Path:
    candidate = Path(value).expanduser()
    if candidate.name == manifest_file and candidate.is_file():
        candidate = candidate.parent
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise LacunaError(
            unknown_code,
            f"cannot resolve {kind_label} {candidate}: {exc}",
        ) from exc
    if not resolved.is_dir():
        raise LacunaError(unknown_code, f"{kind_label} path is not a directory: {resolved}")
    return resolved


def open_sidecar_lock(
    run_path: Path,
    *,
    lock_file: str,
    error_prefix: str,
    kind_label: str,
    create: bool,
) -> int:
    path = run_path / lock_file
    flags = os.O_RDWR
    if create:
        flags |= os.O_CREAT
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileNotFoundError as exc:
        raise LacunaError(
            f"{error_prefix}-lock-missing",
            f"{kind_label} lock is missing: {path}",
        ) from exc
    except OSError as exc:
        code = (
            f"{error_prefix}-lock-unsafe"
            if exc.errno in {errno.ELOOP, errno.EMLINK}
            else f"{error_prefix}-lock-failed"
        )
        raise LacunaError(code, f"cannot open {kind_label} lock {path}: {exc}") from exc
    try:
        descriptor = os.fstat(fd)
        link = os.lstat(path)
        if (
            not stat.S_ISREG(descriptor.st_mode)
            or not stat.S_ISREG(link.st_mode)
            or descriptor.st_dev != link.st_dev
            or descriptor.st_ino != link.st_ino
            or descriptor.st_nlink != 1
        ):
            raise LacunaError(
                f"{error_prefix}-lock-unsafe",
                f"{kind_label} lock must be one non-symlink regular file",
                {"path": str(path)},
            )
        mode = stat.S_IMODE(descriptor.st_mode)
        if create:
            if hasattr(os, "fchmod"):
                os.fchmod(fd, 0o600)
        elif mode != 0o600:
            raise LacunaError(
                f"{error_prefix}-lock-unsafe",
                f"{kind_label} lock permissions must be owner read/write only",
                {"path": str(path), "mode": oct(mode)},
            )
        if os.name == "nt" and descriptor.st_size == 0:
            os.write(fd, b"\0")
            os.lseek(fd, 0, os.SEEK_SET)
        return fd
    except Exception:
        os.close(fd)
        raise


def ensure_sidecar_lock(
    run_path: Path,
    *,
    lock_file: str,
    error_prefix: str,
    kind_label: str,
) -> None:
    fd = open_sidecar_lock(
        run_path,
        lock_file=lock_file,
        error_prefix=error_prefix,
        kind_label=kind_label,
        create=True,
    )
    os.close(fd)


@contextmanager
def sidecar_lock(
    run_path: Path,
    *,
    lock_file: str,
    error_prefix: str,
    kind_label: str,
    busy_message: str,
) -> Iterator[None]:
    """Take one nonblocking advisory lock for a complete sidecar transition."""
    fd = open_sidecar_lock(
        run_path,
        lock_file=lock_file,
        error_prefix=error_prefix,
        kind_label=kind_label,
        create=False,
    )
    locked = False
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise LacunaError(
                        f"{error_prefix}-busy",
                        busy_message,
                        {"run_path": str(run_path)},
                    ) from exc
                raise
        else:
            import fcntl

            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno in {errno.EACCES, errno.EAGAIN}:
                    raise LacunaError(
                        f"{error_prefix}-busy",
                        busy_message,
                        {"run_path": str(run_path)},
                    ) from exc
                raise
        locked = True
        yield
    finally:
        if locked:
            try:
                if os.name == "nt":
                    import msvcrt

                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        os.close(fd)


def shell_command(parts: list[str]) -> str:
    return " ".join(shlex.quote(item) for item in parts)


def _fsync_directory(path: Path) -> None:
    """Best-effort durability barrier for a directory entry update."""
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def publish_private_directory(
    final_path: Path,
    *,
    error_code: str,
    kind_label: str,
) -> Iterator[Path]:
    """Build one private directory off-path and publish it with one rename.

    A managed sidecar should not become discoverable under its authoritative
    name until its lock, members, manifest, and deterministic pointer all exist.
    The caller writes into the yielded staging directory while embedding
    ``final_path`` in any authority documents.  Successful exit renames the
    complete staging directory into place; failed construction removes the
    staging tree and leaves no run-shaped final directory.

    This narrows crash publication windows on one local filesystem.  It is not
    a distributed transaction, and a process killed while the final rename is
    in progress still relies on the host filesystem's rename semantics.
    """
    final_path = Path(final_path)
    parent = final_path.parent
    if final_path.exists():
        raise LacunaError(
            error_code,
            f"refusing to publish {kind_label} over an existing path: {final_path}",
        )
    staging_path = parent / (
        f".{final_path.name}.publishing-{secrets.token_hex(8)}"
    )
    try:
        staging_path.mkdir(mode=0o700)
    except OSError as exc:
        raise LacunaError(
            error_code,
            f"cannot create staged {kind_label} {staging_path}: {exc}",
        ) from exc

    published = False
    try:
        yield staging_path
        if final_path.exists():
            raise LacunaError(
                error_code,
                f"refusing to publish {kind_label} over an existing path: {final_path}",
            )
        try:
            staging_path.rename(final_path)
        except OSError as exc:
            raise LacunaError(
                error_code,
                f"cannot publish {kind_label} {final_path}: {exc}",
            ) from exc
        published = True
        _fsync_directory(parent)
    finally:
        if not published and staging_path.exists():
            shutil.rmtree(staging_path, ignore_errors=True)
