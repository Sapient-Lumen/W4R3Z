#!/usr/bin/env python3
"""Shared post-detach fd-only derivative worker launcher.

The removable-media local-fallback lane has two executable proofs that must not
silently diverge:

* the no-root fixture prototype, and
* the FreeBSD-shaped backend runner.

Both need the same worker property: after the source media is gone, the child
process receives only a read fd for the preserved capture and a write fd for the
broker-owned derivative slot.  This module keeps that descriptor envelope in one
place so future hardening changes do not land in only one proof.
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import removable_media_safe_capture as safe_capture

sha256_bytes = safe_capture.sha256_bytes
sha256_file = safe_capture.sha256_file

WORKER_CODE = r'''
import hashlib, json, os, sys
in_fd = int(os.environ["DERIVE_INPUT_FD"])
out_fd = int(os.environ["DERIVE_OUTPUT_FD"])
expected = os.environ["DERIVE_EXPECTED_DIGEST"]
leak_canary_fd = int(os.environ.get("DERIVE_LEAK_CANARY_FD", "-1"))
expected_fds = {0, 1, 2, in_fd, out_fd}
open_fds = []
for fd in range(0, 64):
    try:
        os.fstat(fd)
    except OSError:
        continue
    open_fds.append(fd)
unexpected_fds = sorted(set(open_fds) - expected_fds)
leak_canary_fd_seen = leak_canary_fd in open_fds
h = hashlib.sha256()
size = 0
while True:
    chunk = os.read(in_fd, 1024 * 1024)
    if not chunk:
        break
    h.update(chunk)
    size += len(chunk)
observed = "sha256:" + h.hexdigest()
result = {
    "kind": "prototype.derivative",
    "input_digest": observed,
    "input_size_bytes": size,
    "expected_digest_matched": observed == expected,
    "operation": "classify-and-sanitize-stub",
    "media_path_seen": False,
    "fd_inventory_supported": True,
    "open_fds": open_fds,
    "expected_fds": sorted(expected_fds),
    "unexpected_fds": unexpected_fds,
    "leak_canary_fd_seen": leak_canary_fd_seen,
}
os.write(out_fd, (json.dumps(result, sort_keys=True) + "\n").encode("utf-8"))
sys.exit(0 if observed == expected and not unexpected_fds and not leak_canary_fd_seen else 12)
'''


def preflight_preserved_input(input_path: Path, expected_digest: str) -> dict[str, Any]:
    """Validate the preserved CAS object before delegating it to the worker fd."""
    evidence: dict[str, Any] = {
        "prelaunch_input_lstat_regular": False,
        "prelaunch_input_not_symlink": False,
        "prelaunch_input_digest": None,
        "prelaunch_input_digest_matched": False,
        "prelaunch_input_size_bytes": None,
    }
    try:
        st = input_path.lstat()
    except FileNotFoundError as exc:
        raise ValueError("prelaunch-input-missing") from exc
    evidence["prelaunch_input_not_symlink"] = not stat.S_ISLNK(st.st_mode)
    if not evidence["prelaunch_input_not_symlink"]:
        raise ValueError("prelaunch-input-symlink-denied")
    evidence["prelaunch_input_lstat_regular"] = stat.S_ISREG(st.st_mode)
    if not evidence["prelaunch_input_lstat_regular"]:
        raise ValueError("prelaunch-input-not-regular")
    evidence["prelaunch_input_size_bytes"] = st.st_size
    observed = sha256_file(input_path)
    evidence["prelaunch_input_digest"] = observed
    evidence["prelaunch_input_digest_matched"] = observed == expected_digest
    if not evidence["prelaunch_input_digest_matched"]:
        raise ValueError("prelaunch-input-digest-mismatch")
    return evidence


def run_fd_worker(
    input_path: Path,
    output_path: Path,
    expected_digest: str,
    *,
    leak_canary_fd: int | None = None,
    timeout_seconds: float = 10,
) -> dict[str, Any]:
    """Launch the isolated derivative stub with only the two declared fds.

    ``leak_canary_fd`` is intentionally *not* passed through ``pass_fds``.  When
    supplied, the child inventories its fd table and fails if that parent media
    descriptor appears in the child.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prelaunch = preflight_preserved_input(input_path, expected_digest)
    in_fd: int | None = None
    out_fd: int | None = None
    try:
        in_fd = os.open(input_path, os.O_RDONLY)
        # A derivative slot is evidence, not scratch.  Create it exactly once and
        # never truncate an existing file; stale or malicious output must fail
        # closed instead of being overwritten by a later worker attempt.
        out_fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_APPEND", 0), 0o600)
        env = {
            "DERIVE_INPUT_FD": str(in_fd),
            "DERIVE_OUTPUT_FD": str(out_fd),
            "DERIVE_EXPECTED_DIGEST": expected_digest,
            "DERIVE_LEAK_CANARY_FD": str(leak_canary_fd if leak_canary_fd is not None else -1),
        }
        proc = subprocess.run(
            [sys.executable, "-I", "-c", WORKER_CODE],
            cwd="/",
            env=env,
            pass_fds=(in_fd, out_fd),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
    finally:
        if in_fd is not None:
            os.close(in_fd)
        if out_fd is not None:
            os.close(out_fd)

    derivative_digest = sha256_file(output_path)
    try:
        derivative_payload = json.loads(output_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        derivative_payload = {}
    return {
        "exit_code": proc.returncode,
        **prelaunch,
        "output_open_policy": "create-exclusive-no-truncate",
        "output_truncates_existing": False,
        "stdout_sha256": sha256_bytes((proc.stdout or "").encode("utf-8")),
        "stderr_sha256": sha256_bytes((proc.stderr or "").encode("utf-8")),
        "derivative_digest": derivative_digest,
        "derivative_size_bytes": output_path.stat().st_size,
        "fd_inventory_supported": derivative_payload.get("fd_inventory_supported") is True,
        "open_fds": derivative_payload.get("open_fds", []),
        "expected_fds": derivative_payload.get("expected_fds", []),
        "unexpected_fds": derivative_payload.get("unexpected_fds", []),
        "leak_canary_fd_seen": derivative_payload.get("leak_canary_fd_seen"),
        "derivative_payload": derivative_payload,
    }
