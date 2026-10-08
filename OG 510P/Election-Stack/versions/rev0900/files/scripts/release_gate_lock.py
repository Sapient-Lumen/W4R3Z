#!/usr/bin/env python3
"""Single-instance lock for the release-gate runner.

The release gate mutates generated release-control surfaces before checking and
sealing the manifest. Two concurrent gate runs against the same source root can
interleave those generated writes. The lock lives outside the repository tree so
lock files are not accidentally packaged.

This lock intentionally uses an atomic lock file rather than process-scoped
``flock``. Some container/PID-namespace hosts can leave advisory locks looking
held after a diagnostic runner is killed, which turns a safety feature into a
false release blocker. Atomic create plus stale-holder PID detection is simpler,
portable enough for this stdlib gate, and auditable by negative controls.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import tempfile
import time
from pathlib import Path
from typing import Iterator


class ReleaseGateLockError(RuntimeError):
    """Raised when another release-gate invocation already holds the lock."""


def lock_path_for_root(root: Path, *, lock_dir: Path | None = None) -> Path:
    resolved = str(root.resolve())
    digest = hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:24]
    base = lock_dir or Path(os.environ.get("ELECTION_STACK_RELEASE_GATE_LOCK_DIR", tempfile.gettempdir()))
    return base / f"election_stack_release_gate_{digest}.lock"


def _holder_text(root: Path) -> str:
    return f"pid={os.getpid()} root={root.resolve()} acquired_at_unix={time.time():.6f}\n"


def _parse_holder_pid(holder: str) -> int | None:
    for part in holder.split():
        if part.startswith("pid="):
            try:
                return int(part.split("=", 1)[1])
            except ValueError:
                return None
    return None


def _pid_is_live(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def _try_create_lock(path: Path, holder: str) -> int | None:
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return None
    os.write(fd, holder.encode("utf-8"))
    os.fsync(fd)
    return fd


@contextlib.contextmanager
def acquire_release_gate_lock(root: Path, *, lock_dir: Path | None = None) -> Iterator[Path]:
    """Acquire a non-blocking single-instance lock for ``root``.

    The implementation is fail-closed for live holders and self-healing for
    stale lock files whose recorded PID no longer exists. It never uses a lock
    file inside the repository tree.
    """

    path = lock_path_for_root(root, lock_dir=lock_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    holder = _holder_text(root)

    fd = _try_create_lock(path, holder)
    if fd is None:
        existing = path.read_text(encoding="utf-8", errors="replace").strip()
        pid = _parse_holder_pid(existing)
        if pid is not None and not _pid_is_live(pid):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            fd = _try_create_lock(path, holder)
        if fd is None:
            detail = f"; holder={existing}" if existing else ""
            raise ReleaseGateLockError(f"another release gate is already running for this source root ({path}){detail}")

    try:
        yield path
    finally:
        try:
            os.close(fd)
        finally:
            try:
                # Only remove the lock file if it is still ours.  If a host or
                # maintainer manually replaced it, leave that evidence alone.
                if path.read_text(encoding="utf-8", errors="replace") == holder:
                    path.unlink()
            except FileNotFoundError:
                pass
