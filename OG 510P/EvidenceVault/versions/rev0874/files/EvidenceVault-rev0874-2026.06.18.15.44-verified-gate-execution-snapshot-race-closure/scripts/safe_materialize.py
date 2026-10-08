#!/usr/bin/env python3
"""Shared descriptor-bound, exact-byte, no-clobber materialization helpers.

This module is intentionally small and policy-focused.  Callers supply a clean
relative path plus the exact bytes and SHA-256 they expect.  Publication walks
and creates parent directories beneath a verified root using directory file
descriptors, refuses symlinks and non-directories, creates the final file with
O_EXCL, verifies the bytes through the opened descriptor, and unlinks on failure
only when the current invocation created the same inode.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import sys
from typing import Any

sys.dont_write_bytecode = True

try:
    from root_anchor import (
        RootAnchor,
        RootAnchorError,
        assert_root_path as assert_anchored_root_path,
        capture_root,
        clean_relative_path as clean_anchored_relative_path,
        open_root as open_anchored_root,
    )
except ImportError:  # pragma: no cover - package-style import fallback
    from .root_anchor import (
        RootAnchor,
        RootAnchorError,
        assert_root_path as assert_anchored_root_path,
        capture_root,
        clean_relative_path as clean_anchored_relative_path,
        open_root as open_anchored_root,
    )



class MaterializationError(RuntimeError):
    """Unsafe path, conflicting target, or exact-byte verification failure."""


@dataclass(frozen=True)
class MaterializationResult:
    path: str
    status: str
    size: int
    sha256: str


def clean_relative_path(text: Any, label: str = "materialization path") -> str:
    try:
        return clean_anchored_relative_path(text, label)
    except RootAnchorError as exc:
        raise MaterializationError(str(exc)) from exc


def _identity(st: os.stat_result) -> tuple[int, int, int]:
    return (st.st_dev, st.st_ino, stat.S_IFMT(st.st_mode))


def _full_identity(st: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        st.st_dev,
        st.st_ino,
        st.st_mode,
        st.st_nlink,
        st.st_size,
        st.st_mtime_ns,
        st.st_ctime_ns,
    )


def _directory_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _file_read_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def _coerce_root_anchor(root: Path | RootAnchor) -> RootAnchor:
    try:
        return capture_root(root)
    except RootAnchorError as exc:
        raise MaterializationError(str(exc)) from exc


def prepare_root_anchor(root: Path | RootAnchor) -> RootAnchor:
    """Capture one stable directory identity for a multi-step workflow."""
    return _coerce_root_anchor(root)


def prepare_real_root(root: Path | RootAnchor) -> Path:
    """Compatibility wrapper returning the currently anchored absolute path."""
    return _coerce_root_anchor(root).path




def _assert_root_current(root: RootAnchor) -> None:
    try:
        assert_anchored_root_path(root)
    except RootAnchorError as exc:
        raise MaterializationError(str(exc)) from exc

def _open_verified_root(root: RootAnchor) -> tuple[int, tuple[int, int, int]]:
    try:
        fd = open_anchored_root(root)
    except RootAnchorError as exc:
        raise MaterializationError(str(exc)) from exc
    return fd, root.identity


def _open_verified_directory(
    parent_fd: int, name: str, rel: str, *, create: bool
) -> int:
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        if not create:
            raise
        try:
            os.mkdir(name, mode=0o755, dir_fd=parent_fd)
        except FileExistsError:
            pass
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise MaterializationError(f"materialization parent is symlinked or non-directory: {rel}")
    try:
        fd = os.open(name, _directory_flags(), dir_fd=parent_fd)
    except OSError as exc:
        raise MaterializationError(f"cannot open materialization parent {rel}: {exc}") from exc
    try:
        opened = os.fstat(fd)
        after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        expected = _identity(before)
        if _identity(opened) != expected or _identity(after) != expected:
            raise MaterializationError(f"materialization parent identity changed during open: {rel}")
        if not stat.S_ISDIR(opened.st_mode):
            raise MaterializationError(f"materialization parent opened as non-directory: {rel}")
        return fd
    except Exception:
        os.close(fd)
        raise


def _open_parent(
    root: RootAnchor, rel: str, *, create_parents: bool
) -> tuple[int, str, tuple[int, int, int]]:
    clean = clean_relative_path(rel)
    parts = PurePosixPath(clean).parts
    directory_fd, root_identity = _open_verified_root(root)
    traversed: list[str] = []
    try:
        for part in parts[:-1]:
            traversed.append(part)
            next_fd = _open_verified_directory(
                directory_fd, part, "/".join(traversed), create=create_parents
            )
            os.close(directory_fd)
            directory_fd = next_fd
        return directory_fd, parts[-1], root_identity
    except Exception:
        os.close(directory_fd)
        raise


def _hash_open_fd(fd: int) -> tuple[int, str, tuple[int, int, int, int, int, int, int]]:
    before = os.fstat(fd)
    if not stat.S_ISREG(before.st_mode):
        raise MaterializationError("opened target is not a regular file")
    digest = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    after = os.fstat(fd)
    if _full_identity(before) != _full_identity(after):
        raise MaterializationError("opened target changed while being verified")
    return after.st_size, digest.hexdigest(), _full_identity(after)


def _inspect_at(parent_fd: int, name: str, rel: str) -> tuple[str, int | None, str | None]:
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return "missing", None, None
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        return "unsafe_non_regular", None, None
    try:
        fd = os.open(name, _file_read_flags(), dir_fd=parent_fd)
    except OSError as exc:
        raise MaterializationError(f"cannot inspect existing target {rel}: {exc}") from exc
    try:
        opened = os.fstat(fd)
        after_open = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        expected = _identity(before)
        if _identity(opened) != expected or _identity(after_open) != expected:
            raise MaterializationError(f"existing target identity changed during open: {rel}")
        size, digest, full_after = _hash_open_fd(fd)
        after_read = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if _identity(after_read) != expected or _full_identity(after_read) != full_after:
            raise MaterializationError(f"existing target path changed during verification: {rel}")
        return "regular", size, digest
    finally:
        os.close(fd)


def target_status(
    root: Path | RootAnchor,
    rel: str,
    *,
    expected_size: int,
    expected_sha256: str,
) -> str:
    """Classify one target without following any target-path symlink."""
    root = _coerce_root_anchor(root)
    try:
        parent_fd, name, root_identity = _open_parent(root, rel, create_parents=False)
    except FileNotFoundError:
        _assert_root_current(root)
        return "missing"
    try:
        kind, size, digest = _inspect_at(parent_fd, name, rel)
        _assert_root_current(root)
        if kind == "missing":
            return "missing"
        if kind == "unsafe_non_regular":
            return "unsafe_non_regular"
        if size == expected_size and digest == expected_sha256:
            return "exact"
        return "mismatch"
    finally:
        os.close(parent_fd)


def materialize_exact_bytes(
    root: Path | RootAnchor,
    rel: str,
    data: bytes,
    *,
    expected_sha256: str | None = None,
    mode: int = 0o644,
    allow_existing_exact: bool = True,
) -> MaterializationResult:
    """Create one exact file beneath *root* without overwriting any pathname."""
    if not isinstance(data, bytes):
        raise MaterializationError("materialization data must be bytes")
    rel = clean_relative_path(rel)
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise MaterializationError(
            f"supplied bytes do not match expected SHA-256 for {rel}: {digest}"
        )
    root = _coerce_root_anchor(root)
    parent_fd, name, root_identity = _open_parent(root, rel, create_parents=True)
    fd: int | None = None
    created = False
    created_identity: tuple[int, int, int] | None = None
    try:
        kind, size, existing_digest = _inspect_at(parent_fd, name, rel)
        if kind != "missing":
            if (
                allow_existing_exact
                and kind == "regular"
                and size == len(data)
                and existing_digest == digest
            ):
                _assert_root_current(root)
                return MaterializationResult(rel, "already_exact", len(data), digest)
            if kind == "unsafe_non_regular":
                raise MaterializationError(
                    f"refusing unsafe symlink or non-regular target: {rel}"
                )
            raise MaterializationError(f"refusing to overwrite non-matching target: {rel}")

        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(name, flags, mode, dir_fd=parent_fd)
            created = True
        except FileExistsError:
            # A race winner may be accepted only if it independently has the
            # exact bytes; no path is ever replaced.
            kind, size, existing_digest = _inspect_at(parent_fd, name, rel)
            if (
                allow_existing_exact
                and kind == "regular"
                and size == len(data)
                and existing_digest == digest
            ):
                _assert_root_current(root)
                return MaterializationResult(rel, "already_exact", len(data), digest)
            raise MaterializationError(f"target appeared during no-clobber write: {rel}")
        except OSError as exc:
            raise MaterializationError(f"cannot create materialization target {rel}: {exc}") from exc

        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise MaterializationError(f"created target is not a regular file: {rel}")
        created_identity = _identity(opened)
        os.fchmod(fd, mode)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise MaterializationError(f"short write while materializing {rel}")
            view = view[written:]
        os.fsync(fd)
        size, actual_digest, full_identity = _hash_open_fd(fd)
        if size != len(data) or actual_digest != digest:
            raise MaterializationError(f"descriptor verification failed after writing {rel}")
        path_stat = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if _identity(path_stat) != created_identity or _full_identity(path_stat) != full_identity:
            raise MaterializationError(f"target path identity changed after writing {rel}")
        _assert_root_current(root)
        try:
            os.fsync(parent_fd)
        except OSError:
            pass
        return MaterializationResult(rel, "written", len(data), digest)
    except Exception:
        if created and created_identity is not None:
            try:
                current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except OSError:
                current = None
            if current is not None and _identity(current) == created_identity:
                try:
                    os.unlink(name, dir_fd=parent_fd)
                except OSError:
                    pass
        raise
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent_fd)


def prepare_external_target_root(
    target_root: Path | RootAnchor,
    *,
    bundle_root: Path | RootAnchor,
    index_rel: str = "INDEX/files.csv",
) -> RootAnchor:
    """Return a stable non-overlapping target anchor carrying the identical index."""
    target = _coerce_root_anchor(target_root)
    bundle = _coerce_root_anchor(bundle_root)
    target_path = target.path
    bundle_path = bundle.path
    if (
        target.identity == bundle.identity
        or target_path == bundle_path
        or bundle_path in target_path.parents
        or target_path in bundle_path.parents
    ):
        raise MaterializationError("target root may not overlap the immutable tool bundle")
    clean_index = clean_relative_path(index_rel, "canonical index path")
    try:
        target_parent, target_name, _ = _open_parent(
            target, clean_index, create_parents=False
        )
        bundle_parent, bundle_name, _ = _open_parent(
            bundle, clean_index, create_parents=False
        )
    except FileNotFoundError as exc:
        _assert_root_current(target)
        _assert_root_current(bundle)
        raise MaterializationError(
            f"both trees must contain a regular {clean_index}"
        ) from exc
    try:
        target_kind, target_size, target_digest = _inspect_at(
            target_parent, target_name, f"target {clean_index}"
        )
        bundle_kind, bundle_size, bundle_digest = _inspect_at(
            bundle_parent, bundle_name, f"bundle {clean_index}"
        )
        _assert_root_current(target)
        _assert_root_current(bundle)
    finally:
        os.close(target_parent)
        os.close(bundle_parent)
    if target_kind != "regular" or bundle_kind != "regular":
        raise MaterializationError(f"both trees must contain a regular {clean_index}")
    if target_size != bundle_size or target_digest != bundle_digest:
        raise MaterializationError("target canonical index is not byte-identical to bundle index")
    return target
