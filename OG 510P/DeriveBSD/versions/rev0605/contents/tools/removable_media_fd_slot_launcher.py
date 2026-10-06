#!/usr/bin/env python3
"""Descriptor-slot launcher helpers for removable-media worker probes.

The host-smoke and Capsicum bridge probes delegate fixed fd numbers to a child
process.  Those fds are authority, so the parent must not confuse newly opened
worker fds with pre-existing parent fd slots, and it must restore or close the
slots after the child exits.
"""
from __future__ import annotations

import fcntl
import os
from dataclasses import dataclass, field
from typing import Any, Iterable


TARGET_FDS = (3, 4, 5)
POLICY = "duplicate-target-fds-above-delegated-range-before-clearing-slots"
SAVE_DUP_MIN_FD = 64


def fd_identity(fd: int) -> dict[str, Any]:
    """Return a small, JSON-safe identity for an fd, or closed state."""
    try:
        st = os.fstat(fd)
    except OSError:
        return {"open": False}
    try:
        inheritable = os.get_inheritable(fd)
    except OSError:
        inheritable = None
    return {
        "open": True,
        "st_dev": int(st.st_dev),
        "st_ino": int(st.st_ino),
        "st_mode": int(st.st_mode),
        "st_rdev": int(getattr(st, "st_rdev", 0)),
        "inheritable": inheritable,
    }


def identities_match(before: dict[str, Any], after: dict[str, Any]) -> bool:
    if before.get("open") is not True or after.get("open") is not True:
        return before.get("open") is False and after.get("open") is False
    return all(before.get(key) == after.get(key) for key in ("st_dev", "st_ino", "st_mode", "st_rdev", "inheritable"))


def duplicate_above_delegated_range(fd: int) -> int:
    """Duplicate fd into a non-target slot before target slots are cleared."""
    try:
        saved = fcntl.fcntl(fd, fcntl.F_DUPFD_CLOEXEC, SAVE_DUP_MIN_FD)
    except AttributeError:
        saved = fcntl.fcntl(fd, fcntl.F_DUPFD, SAVE_DUP_MIN_FD)
        os.set_inheritable(saved, False)
    return int(saved)


@dataclass
class FdSlotGuard:
    """Save fixed parent fd slots before opening delegated worker files."""

    target_fds: Iterable[int] = TARGET_FDS
    saved: dict[int, int | None] = field(default_factory=dict)
    before: dict[int, dict[str, Any]] = field(default_factory=dict)
    after: dict[int, dict[str, Any]] = field(default_factory=dict)
    saved_inheritable: dict[int, bool | None] = field(default_factory=dict)
    saved_fd_numbers: dict[int, int | None] = field(default_factory=dict)
    saved_and_cleared: bool = False
    restored: bool = False

    def save_and_clear(self) -> "FdSlotGuard":
        """Duplicate targets out of band first, then close target slots.

        Duplicating fd 3 before fd 4 is closed can otherwise allocate fd 4 as the
        backup.  The next loop iteration then mistakes the backup for a real
        pre-existing fd 4.  We avoid that by forcing backups above the delegated
        range before any target slot is cleared.
        """
        targets = tuple(self.target_fds)
        for fd in targets:
            self.before[fd] = fd_identity(fd)
            if self.before[fd].get("open") is True:
                saved_fd = duplicate_above_delegated_range(fd)
                self.saved[fd] = saved_fd
                self.saved_fd_numbers[fd] = saved_fd
                self.saved_inheritable[fd] = bool(self.before[fd].get("inheritable"))
            else:
                self.saved[fd] = None
                self.saved_fd_numbers[fd] = None
                self.saved_inheritable[fd] = None
        for fd in targets:
            try:
                os.close(fd)
            except OSError:
                pass
        self.saved_and_cleared = True
        return self

    def install_owned_fd(self, src_fd: int, target_fd: int) -> None:
        """Install an owned source fd into a target slot and close the source if moved."""
        if not self.saved_and_cleared:
            raise RuntimeError("fd target slots must be saved before delegation")
        if target_fd not in set(self.target_fds):
            raise RuntimeError(f"unexpected delegated fd target: {target_fd}")
        if src_fd != target_fd:
            os.dup2(src_fd, target_fd)
            os.close(src_fd)
        os.set_inheritable(target_fd, True)

    def restore(self) -> None:
        """Close delegated target slots and restore any pre-existing parent slots."""
        for fd in sorted(self.target_fds):
            try:
                os.close(fd)
            except OSError:
                pass
            saved_fd = self.saved.get(fd)
            if saved_fd is not None:
                original_inheritable = self.before.get(fd, {}).get("inheritable")
                os.dup2(saved_fd, fd)
                if isinstance(original_inheritable, bool):
                    os.set_inheritable(fd, original_inheritable)
                os.close(saved_fd)
        for fd in self.target_fds:
            self.after[fd] = fd_identity(fd)
        self.restored = True

    def evidence(self) -> dict[str, Any]:
        matches = {
            str(fd): identities_match(self.before.get(fd, {"open": False}), self.after.get(fd, {"open": False}))
            for fd in self.target_fds
        }
        return {
            "policy": POLICY,
            "target_fds": list(self.target_fds),
            "save_duplicate_min_fd": SAVE_DUP_MIN_FD,
            "saved_duplicates_outside_target_fds": all((saved is None or saved >= SAVE_DUP_MIN_FD) for saved in self.saved_fd_numbers.values()),
            "saved_fd_numbers": {str(fd): self.saved_fd_numbers.get(fd) for fd in self.target_fds},
            "saved_and_cleared_before_opening_delegated_files": self.saved_and_cleared,
            "restored_after_worker": self.restored,
            "preexisting_parent_fd_slots_preserved": all(matches.values()),
            "preexisting_parent_fd_inheritable_flags_preserved": all(matches.values()),
            "slot_identity_matches_after_restore": matches,
            "open_before": {str(fd): self.before.get(fd, {"open": False}) for fd in self.target_fds},
            "open_after": {str(fd): self.after.get(fd, {"open": False}) for fd in self.target_fds},
        }
