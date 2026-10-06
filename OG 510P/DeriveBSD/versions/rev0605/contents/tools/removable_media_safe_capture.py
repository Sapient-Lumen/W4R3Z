#!/usr/bin/env python3
"""Dirfd-pinned removable-media member capture helper.

The first local-fallback lane must not trust a selected media path just because a
string normalizes cleanly or a final ``Path.is_file()`` check passed.  This
helper keeps the runnable proof close to the production shape: start from a
broker-owned media-root fd, walk each ancestor with ``openat``/``O_DIRECTORY`` /
``O_NOFOLLOW``, open the final member read-only with ``O_NOFOLLOW``, verify the
opened object is a regular file, copy it into a digest-addressed store, and
verify the stored copy.

It is still a cloudtainer/userland helper.  It does not perform a real FreeBSD
mount, jail launch, or ``cap_enter``.  It removes a concrete bypass class from
our executable evidence: symlink ancestors and symlink leaves no longer rely on
friendly path resolution.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import stat
import sys
import unicodedata
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any


class CaptureError(ValueError):
    """Structured closed-failure for removable-media member capture."""

    def __init__(self, reason: str, detail: str | None = None) -> None:
        self.reason = reason
        self.detail = detail or reason
        super().__init__(f"{reason}: {self.detail}")


@dataclass(frozen=True)
class OpenedMember:
    fd: int
    normalized_member: str
    before_stat: os.stat_result
    after_stat: os.stat_result
    opened_with_openat: bool
    opened_with_no_follow: bool
    root_fd_pinned: bool
    lstat_fstat_same_object: bool


@dataclass(frozen=True)
class CaptureResult:
    member: str
    normalized_member: str
    digest: str
    size_bytes: int
    store_rel: str
    object_path: Path
    opened_with_openat: bool
    opened_with_no_follow: bool
    root_fd_pinned: bool
    ancestor_symlink_policy: str
    leaf_symlink_policy: str
    regular_file_only: bool
    lstat_fstat_same_object: bool
    source_stable_after_copy: bool
    verified_after_copy: bool
    capture_api: str
    cas_write_policy: str
    cas_object_preexisted: bool
    cas_existing_object_verified: bool

    def evidence(self) -> dict[str, Any]:
        data = asdict(self)
        data["object_path"] = self.object_path.as_posix()
        return data


O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def normalize_member(member: str) -> tuple[str | None, str | None]:
    """Return an NFC relative POSIX member path or a closed-failure reason."""
    if not isinstance(member, str) or not member:
        return None, "empty-member-path"
    if "\x00" in member:
        return None, "nul-byte-member-path"
    p = PurePosixPath(member)
    if p.is_absolute():
        return None, "absolute-member-path"
    parts = p.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None, "non-relative-clean-member-path"
    normalized_parts = [unicodedata.normalize("NFC", part) for part in parts]
    if any(part in {"", ".", ".."} or "/" in part or "\x00" in part for part in normalized_parts):
        return None, "invalid-normalized-member-component"
    return PurePosixPath(*normalized_parts).as_posix(), None


def _same_object(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_size,
        getattr(before, "st_mtime_ns", int(before.st_mtime * 1_000_000_000)),
    ) == (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_size,
        getattr(after, "st_mtime_ns", int(after.st_mtime * 1_000_000_000)),
    )


def _reject_for_lstat(st: os.stat_result, *, leaf: bool) -> str | None:
    mode = st.st_mode
    if stat.S_ISLNK(mode):
        return "symlink-subject-denied" if leaf else "symlink-ancestor-denied"
    if leaf:
        if stat.S_ISDIR(mode):
            return "directory-subject-denied-in-first-cut"
        if not stat.S_ISREG(mode):
            return "non-regular-subject-denied"
    else:
        if not stat.S_ISDIR(mode):
            return "non-directory-ancestor-denied"
    return None


def _open_child(parent_fd: int, name: str, *, leaf: bool) -> tuple[int, os.stat_result, os.stat_result]:
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError as exc:
        raise CaptureError("missing-member", name) from exc
    except NotADirectoryError as exc:
        raise CaptureError("non-directory-ancestor-denied", name) from exc
    except OSError as exc:
        raise CaptureError("member-lstat-failed", f"{name}: errno={exc.errno}") from exc

    reason = _reject_for_lstat(before, leaf=leaf)
    if reason:
        raise CaptureError(reason, name)

    flags = os.O_RDONLY | O_CLOEXEC | O_NOFOLLOW
    if not leaf:
        flags |= O_DIRECTORY
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.EMLINK}:
            raise CaptureError("symlink-subject-denied" if leaf else "symlink-ancestor-denied", name) from exc
        if exc.errno == errno.ENOTDIR:
            raise CaptureError("non-directory-ancestor-denied" if not leaf else "non-regular-subject-denied", name) from exc
        raise CaptureError("member-openat-failed", f"{name}: errno={exc.errno}") from exc

    after = os.fstat(fd)
    if leaf and not stat.S_ISREG(after.st_mode):
        os.close(fd)
        raise CaptureError("non-regular-subject-denied", name)
    if not leaf and not stat.S_ISDIR(after.st_mode):
        os.close(fd)
        raise CaptureError("non-directory-ancestor-denied", name)
    if not _same_object(before, after):
        os.close(fd)
        raise CaptureError("member-changed-during-open", name)
    return fd, before, after


def open_regular_member_fd(media_root: Path, member: str) -> OpenedMember:
    """Open one selected regular file using a dirfd-pinned no-symlink walk."""
    if not os.supports_dir_fd or os.open not in os.supports_dir_fd:
        raise CaptureError("dirfd-openat-unavailable", "os.open(dir_fd=...) is required")
    normalized, reason = normalize_member(member)
    if reason:
        raise CaptureError(reason, member)
    assert normalized is not None

    try:
        root_lstat = media_root.lstat()
    except FileNotFoundError as exc:
        raise CaptureError("missing-media-root", media_root.as_posix()) from exc
    if stat.S_ISLNK(root_lstat.st_mode):
        raise CaptureError("symlink-media-root-denied", media_root.as_posix())
    if not stat.S_ISDIR(root_lstat.st_mode):
        raise CaptureError("media-root-not-directory", media_root.as_posix())

    root_flags = os.O_RDONLY | O_CLOEXEC | O_DIRECTORY | O_NOFOLLOW
    try:
        root_fd = os.open(media_root, root_flags)
    except FileNotFoundError as exc:
        raise CaptureError("missing-media-root", media_root.as_posix()) from exc
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.EMLINK}:
            raise CaptureError("symlink-media-root-denied", media_root.as_posix()) from exc
        raise CaptureError("media-root-open-failed", f"{media_root}: errno={exc.errno}") from exc

    fds_to_close = [root_fd]
    current_fd = root_fd
    parts = PurePosixPath(normalized).parts
    try:
        for part in parts[:-1]:
            next_fd, _before, _after = _open_child(current_fd, part, leaf=False)
            fds_to_close.append(next_fd)
            current_fd = next_fd
        leaf_fd, before, after = _open_child(current_fd, parts[-1], leaf=True)
    except Exception:
        for fd in reversed(fds_to_close):
            try:
                os.close(fd)
            except OSError:
                pass
        raise

    for fd in reversed(fds_to_close):
        try:
            os.close(fd)
        except OSError:
            pass

    return OpenedMember(
        fd=leaf_fd,
        normalized_member=normalized,
        before_stat=before,
        after_stat=after,
        opened_with_openat=True,
        opened_with_no_follow=bool(O_NOFOLLOW),
        root_fd_pinned=True,
        lstat_fstat_same_object=_same_object(before, after),
    )


def reject_reason(media_root: Path, member: str) -> str | None:
    """Return None when the member would be capturable, else the fail-closed reason."""
    try:
        opened = open_regular_member_fd(media_root, member)
    except CaptureError as exc:
        return exc.reason
    else:
        os.close(opened.fd)
        return None


def _commit_tmp_to_digest_object(tmp: Path, obj_path: Path, digest: str) -> tuple[bool, bool]:
    """Atomically publish ``tmp`` without ever overwriting an existing CAS object.

    A digest-addressed store is only trustworthy when the object name is a
    commitment, not a mutable slot.  The previous helper used ``Path.replace``;
    that was fine for a throwaway fixture but wrong for a hostile-media lane
    because a corrupt pre-existing object at the same digest path would be
    silently overwritten instead of detected.  This function links the temp file
    into place, treats an existing matching object as an idempotent success, and
    fails closed if the existing bytes do not match the digest encoded in the
    object path.
    """
    tmp_digest = sha256_file(tmp)
    if tmp_digest != digest:
        raise CaptureError("temporary-capture-digest-mismatch", tmp.as_posix())
    try:
        os.link(tmp, obj_path)
        return False, False
    except FileExistsError:
        existing_digest = sha256_file(obj_path)
        if existing_digest != digest:
            raise CaptureError("cas-object-digest-mismatch", obj_path.as_posix())
        return True, True
    except OSError as exc:
        raise CaptureError("cas-object-link-failed", f"{obj_path}: errno={exc.errno}") from exc


def capture_regular_member(media_root: Path, member: str, cas_root: Path) -> CaptureResult:
    opened = open_regular_member_fd(media_root, member)
    h = hashlib.sha256()
    size = 0
    final_stat: os.stat_result | None = None
    tmp: Path | None = None
    cas_object_preexisted = False
    cas_existing_object_verified = False
    try:
        # Write temporary captures inside the same digest-store filesystem so the
        # final publish can be no-overwrite and atomic via link(2).
        tmp_root = cas_root / "cas" / ".tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp = tmp_root / f"capture-{os.getpid()}-{uuid.uuid4().hex}.tmp"
        with tmp.open("xb") as out:
            while True:
                chunk = os.read(opened.fd, 1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
                size += len(chunk)
                out.write(chunk)
        final_stat = os.fstat(opened.fd)

        digest = "sha256:" + h.hexdigest()
        algo, hex_digest = digest.split(":", 1)
        obj_dir = cas_root / "cas" / algo
        obj_dir.mkdir(parents=True, exist_ok=True)
        obj_path = obj_dir / hex_digest
        cas_object_preexisted, cas_existing_object_verified = _commit_tmp_to_digest_object(tmp, obj_path, digest)
    finally:
        os.close(opened.fd)
        if tmp is not None:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass

    assert final_stat is not None
    verified = sha256_file(obj_path) == digest
    return CaptureResult(
        member=member,
        normalized_member=opened.normalized_member,
        digest=digest,
        size_bytes=size,
        store_rel=f"cas/{algo}/{hex_digest}",
        object_path=obj_path,
        opened_with_openat=opened.opened_with_openat,
        opened_with_no_follow=opened.opened_with_no_follow,
        root_fd_pinned=opened.root_fd_pinned,
        ancestor_symlink_policy="deny-each-ancestor-by-openat-o_directory-o_nofollow",
        leaf_symlink_policy="deny-leaf-by-openat-o_nofollow",
        regular_file_only=stat.S_ISREG(opened.after_stat.st_mode),
        lstat_fstat_same_object=opened.lstat_fstat_same_object,
        source_stable_after_copy=_same_object(opened.after_stat, final_stat),
        verified_after_copy=verified,
        capture_api="dirfd-openat-no-symlink-components",
        cas_write_policy="no-overwrite-link-then-verify-existing",
        cas_object_preexisted=cas_object_preexisted,
        cas_existing_object_verified=cas_existing_object_verified,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("media_root", type=Path)
    parser.add_argument("member")
    parser.add_argument("--cas-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = capture_regular_member(args.media_root, args.member, args.cas_root)
    except CaptureError as exc:
        print(f"capture rejected: {exc.reason}: {exc.detail}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.evidence(), indent=2, sort_keys=True))
    else:
        print(f"{result.digest} {result.store_rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
