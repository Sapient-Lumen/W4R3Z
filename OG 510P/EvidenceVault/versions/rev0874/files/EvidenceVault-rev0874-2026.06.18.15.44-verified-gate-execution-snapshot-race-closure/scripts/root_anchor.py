#!/usr/bin/env python3
"""Stable root-directory anchors and canonical relative-path validation.

A lexical pathname is not an identity.  This module captures a root by walking
its absolute components with no-follow directory descriptors, records the
opened directory's device/inode/type identity, and requires every later open to
resolve to that same identity.  Callers can therefore retain one RootAnchor
across a multi-step read or publication workflow without silently switching to
a replacement directory installed at the same pathname.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any


class RootAnchorError(RuntimeError):
    """Raised when a root/path is aliased, substituted, or otherwise unsafe."""


RootIdentity = tuple[int, int, int]


@dataclass(frozen=True)
class RootAnchor(os.PathLike[str]):
    """A pathname paired with the exact directory identity it must continue naming."""

    path: Path
    identity: RootIdentity

    def __fspath__(self) -> str:
        return os.fspath(self.path)

    def __str__(self) -> str:
        return os.fspath(self.path)

    def resolve(self, strict: bool = False) -> Path:
        # The path was made absolute and walked without symlinks at capture.
        # Re-resolving here would follow a later alias, so return the anchored
        # lexical path after first proving that it still names the same inode.
        assert_root_path(self)
        return self.path


def clean_relative_path(text: Any, label: str = "relative path") -> str:
    """Require one exact canonical POSIX spelling; never normalize aliases."""
    if not isinstance(text, str) or not text or "\x00" in text or "\\" in text:
        raise RootAnchorError(f"{label} must be a non-empty POSIX relative path")
    pure = PurePosixPath(text)
    canonical = pure.as_posix()
    if (
        pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or canonical != text
    ):
        raise RootAnchorError(f"{label} is not a clean relative path with one canonical spelling: {text!r}")
    return canonical


def component_identity(st: os.stat_result) -> RootIdentity:
    return (st.st_dev, st.st_ino, stat.S_IFMT(st.st_mode))


def directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _absolute_lexical(root: os.PathLike[str] | str) -> Path:
    try:
        expanded = Path(os.fspath(root)).expanduser()
    except (TypeError, ValueError, OSError) as exc:
        raise RootAnchorError(f"root is not a valid filesystem path: {root!r}: {exc}") from exc
    if "\x00" in os.fspath(expanded):
        raise RootAnchorError("root contains a NUL byte")
    # abspath removes lexical '.' and '..' but does not dereference symlinks.
    return Path(os.path.abspath(os.fspath(expanded)))


def _open_verified_directory_at(parent_fd: int, name: str, display: Path) -> int:
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as exc:
        raise RootAnchorError(f"cannot inspect root component {display}: {exc}") from exc
    if stat.S_ISLNK(before.st_mode):
        raise RootAnchorError(f"root may not pass through a symlink: {display}")
    if not stat.S_ISDIR(before.st_mode):
        raise RootAnchorError(f"root component is not a directory: {display}")
    try:
        fd = os.open(name, directory_open_flags(), dir_fd=parent_fd)
    except OSError as exc:
        raise RootAnchorError(f"cannot open root component {display}: {exc}") from exc
    try:
        opened = os.fstat(fd)
        after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        expected = component_identity(before)
        if component_identity(opened) != expected or component_identity(after) != expected:
            raise RootAnchorError(f"root component identity changed during open: {display}")
        if not stat.S_ISDIR(opened.st_mode):
            raise RootAnchorError(f"opened root component is not a directory: {display}")
        return fd
    except Exception:
        os.close(fd)
        raise


def capture_root(root: os.PathLike[str] | str | RootAnchor) -> RootAnchor:
    """Capture one real directory identity by walking from the filesystem root."""
    if isinstance(root, RootAnchor):
        fd = open_root(root)
        os.close(fd)
        return root

    lexical = _absolute_lexical(root)
    parts = lexical.parts
    if not parts or not lexical.is_absolute():
        raise RootAnchorError(f"root must be absolute after normalization: {lexical}")

    try:
        fd = os.open(parts[0], directory_open_flags())
    except OSError as exc:
        raise RootAnchorError(f"cannot open filesystem root {parts[0]!r}: {exc}") from exc
    cursor = Path(parts[0])
    try:
        opened_root = os.fstat(fd)
        if not stat.S_ISDIR(opened_root.st_mode):
            raise RootAnchorError(f"filesystem root is not a directory: {parts[0]!r}")
        for part in parts[1:]:
            cursor = cursor / part
            next_fd = _open_verified_directory_at(fd, part, cursor)
            os.close(fd)
            fd = next_fd
        expected = component_identity(os.fstat(fd))
        try:
            final_path = os.stat(lexical, follow_symlinks=False)
        except OSError as exc:
            raise RootAnchorError(f"root path disappeared during capture: {lexical}: {exc}") from exc
        if component_identity(final_path) != expected:
            raise RootAnchorError(f"root path identity changed during capture: {lexical}")
        return RootAnchor(lexical, expected)
    finally:
        os.close(fd)


def open_root(anchor: RootAnchor) -> int:
    """Open an anchored root and require the original identity before/after open."""
    if not isinstance(anchor, RootAnchor):
        raise RootAnchorError("open_root requires a RootAnchor")
    try:
        before = os.stat(anchor.path, follow_symlinks=False)
    except OSError as exc:
        raise RootAnchorError(f"anchored root path is unavailable: {anchor.path}: {exc}") from exc
    if component_identity(before) != anchor.identity or not stat.S_ISDIR(before.st_mode):
        raise RootAnchorError(f"anchored root path no longer names the validated directory: {anchor.path}")
    try:
        fd = os.open(anchor.path, directory_open_flags())
    except OSError as exc:
        raise RootAnchorError(f"cannot reopen anchored root {anchor.path}: {exc}") from exc
    try:
        opened = os.fstat(fd)
        after = os.stat(anchor.path, follow_symlinks=False)
        if component_identity(opened) != anchor.identity or component_identity(after) != anchor.identity:
            raise RootAnchorError(f"anchored root identity changed during open: {anchor.path}")
        if not stat.S_ISDIR(opened.st_mode):
            raise RootAnchorError(f"anchored root opened as a non-directory: {anchor.path}")
        return fd
    except Exception:
        os.close(fd)
        raise


def assert_root_path(anchor: RootAnchor) -> None:
    """Require the anchor pathname to still name the captured directory identity."""
    try:
        current = os.stat(anchor.path, follow_symlinks=False)
    except OSError as exc:
        raise RootAnchorError(f"anchored root path is unavailable: {anchor.path}: {exc}") from exc
    if component_identity(current) != anchor.identity or not stat.S_ISDIR(current.st_mode):
        raise RootAnchorError(f"anchored root path no longer names the validated directory: {anchor.path}")
