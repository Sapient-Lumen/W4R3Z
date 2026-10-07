#!/usr/bin/env python3
"""Project-scoped fail-fast lock for live TeX compile evidence refreshes."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
from typing import Iterator


class LiveCompileLockTimeout(RuntimeError):
    """Raised when another live compile refresh already holds the lock."""


def lock_scope_token(root: pathlib.Path) -> str:
    """Return the default live-compile lock scope.

    rev0848 made TeX refreshes mutually exclusive per unpacked root.  In this
    cloudtainer that was still too weak: two copies of the same cube can run in
    parallel and fight for TeX/memory budget.  The default is now project-wide
    when RELEASE_MANIFEST.json is present, with an explicit root-scoped escape
    hatch for unusual local debugging.
    """
    mode = os.environ.get("ANONYMITY_LIVE_COMPILE_LOCK_SCOPE", "project").strip().lower() or "project"
    root = pathlib.Path(root).resolve()
    if mode == "root":
        return f"root:{root}"
    if mode not in {"project", "root"}:
        return f"custom:{mode}"
    manifest = root / "RELEASE_MANIFEST.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            project = str(data.get("project") or "").strip()
            if project:
                return f"project:{project}"
        except Exception:
            pass
    return f"root-fallback:{root}"


def default_lock_path(root: pathlib.Path) -> pathlib.Path:
    override = os.environ.get("ANONYMITY_LIVE_COMPILE_LOCK")
    if override:
        return pathlib.Path(override)
    lock_dir = pathlib.Path(os.environ.get("ANONYMITY_LIVE_COMPILE_LOCK_DIR", tempfile.gettempdir()))
    token = lock_scope_token(root)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]
    return lock_dir / f"anonymity-live-tex-compile-{digest}.lock"


def env_wait_seconds(default: float) -> float:
    raw = os.environ.get("ANONYMITY_LIVE_COMPILE_LOCK_WAIT_SECONDS")
    if raw in {None, ""}:
        return default
    try:
        return max(0.0, float(raw))
    except ValueError:
        return default


@contextlib.contextmanager
def temporary_env(key: str, value: str) -> Iterator[None]:
    old = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old


@contextlib.contextmanager
def live_compile_lock(root: pathlib.Path, label: str, wait_seconds: float | None = None) -> Iterator[pathlib.Path]:
    root = pathlib.Path(root).resolve()
    wait = env_wait_seconds(0.0 if wait_seconds is None else wait_seconds)
    path = default_lock_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + wait
    with path.open("a+", encoding="utf-8") as handle:
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                handle.seek(0)
                handle.truncate()
                handle.write(json.dumps({"pid": os.getpid(), "label": label, "root": str(root), "lock_scope": lock_scope_token(root)}, sort_keys=True) + "\n")
                handle.flush()
                try:
                    yield path
                finally:
                    try:
                        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                    except OSError:
                        pass
                return
            except BlockingIOError as exc:
                if time.monotonic() >= deadline:
                    raise LiveCompileLockTimeout(f"another live TeX compile refresh already holds {path}") from exc
                time.sleep(min(0.2, max(0.01, deadline - time.monotonic())))


def acquire_once(root: pathlib.Path, label: str, wait_seconds: float) -> dict:
    try:
        with live_compile_lock(root, label, wait_seconds):
            return {"status": "pass", "acquired": True, "publication_authorized": False}
    except LiveCompileLockTimeout as exc:
        return {
            "status": "fail",
            "acquired": False,
            "publication_authorized": False,
            "failure_category": "live_compile_lock_busy",
            "detail": str(exc),
        }


def self_test(root: pathlib.Path) -> dict:
    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="anonymity_live_compile_lock_test."))
    lock_path = temp_dir / "test.lock"
    env = os.environ.copy()
    env["ANONYMITY_LIVE_COMPILE_LOCK"] = str(lock_path)
    cmd = [
        sys.executable,
        "-S",
        "-B",
        str(pathlib.Path(__file__).resolve()),
        "--root",
        str(root),
        "--try-acquire",
        "--label",
        "child",
        "--wait-seconds",
        "0",
    ]
    failures = []
    with temporary_env("ANONYMITY_LIVE_COMPILE_LOCK", str(lock_path)):
        with live_compile_lock(root, "self-test-parent", wait_seconds=0):
            blocked = subprocess.run(cmd, env=env, text=True, capture_output=True, timeout=10)
            owner_text = lock_path.read_text(encoding="utf-8", errors="replace") if lock_path.exists() else ""
    acquired = subprocess.run(cmd, env=env, text=True, capture_output=True, timeout=10)
    child_blocked = blocked.returncode != 0 and "live_compile_lock_busy" in (blocked.stdout + blocked.stderr)
    child_acquired = acquired.returncode == 0 and '"acquired": true' in acquired.stdout
    owner_has_scope = "lock_scope" in owner_text and "self-test-parent" in owner_text

    clone_root = temp_dir / "clone-root"
    clone_root.mkdir()
    manifest = root / "RELEASE_MANIFEST.json"
    if manifest.is_file():
        (clone_root / "RELEASE_MANIFEST.json").write_text(manifest.read_text(encoding="utf-8"), encoding="utf-8")
    project_env = os.environ.copy()
    project_env.pop("ANONYMITY_LIVE_COMPILE_LOCK", None)
    project_env["ANONYMITY_LIVE_COMPILE_LOCK_DIR"] = str(temp_dir)
    project_env["ANONYMITY_LIVE_COMPILE_LOCK_SCOPE"] = "project"
    clone_cmd = [
        sys.executable,
        "-S",
        "-B",
        str(pathlib.Path(__file__).resolve()),
        "--root",
        str(clone_root),
        "--try-acquire",
        "--label",
        "clone-child",
        "--wait-seconds",
        "0",
    ]
    with temporary_env("ANONYMITY_LIVE_COMPILE_LOCK_DIR", str(temp_dir)):
        with temporary_env("ANONYMITY_LIVE_COMPILE_LOCK_SCOPE", "project"):
            same_project_path = default_lock_path(root) == default_lock_path(clone_root)
            with live_compile_lock(root, "project-scope-parent", wait_seconds=0):
                project_blocked_proc = subprocess.run(clone_cmd, env=project_env, text=True, capture_output=True, timeout=10)
    project_scope_blocks_clone = project_blocked_proc.returncode != 0 and "live_compile_lock_busy" in (project_blocked_proc.stdout + project_blocked_proc.stderr)

    if not child_blocked:
        failures.append({"category": "child_not_blocked_while_parent_held_lock", "stdout": blocked.stdout[-500:], "stderr": blocked.stderr[-500:]})
    if not child_acquired:
        failures.append({"category": "child_did_not_acquire_after_release", "stdout": acquired.stdout[-500:], "stderr": acquired.stderr[-500:]})
    if not owner_has_scope:
        failures.append({"category": "lock_owner_record_missing_scope", "owner_record": owner_text[-500:]})
    if not same_project_path:
        failures.append({"category": "project_scope_lock_path_not_shared_across_clone"})
    if not project_scope_blocks_clone:
        failures.append({"category": "project_scope_clone_not_blocked", "stdout": project_blocked_proc.stdout[-500:], "stderr": project_blocked_proc.stderr[-500:]})
    return {
        "status": "pass" if not failures else "fail",
        "report_kind": "live_compile_lock_self_test",
        "publication_authorized": False,
        "summary": {
            "checks_failed": len(failures),
            "child_blocked_while_parent_holds_lock": child_blocked,
            "child_acquires_after_parent_release": child_acquired,
            "owner_record_has_lock_scope": owner_has_scope,
            "project_scope_lock_path_shared_across_clone": same_project_path,
            "project_scope_blocks_clone_worktree": project_scope_blocks_clone,
        },
        "failures": failures,
        "fail_closed_rule": "If live compile locking cannot prove project-wide mutual exclusion across unpacked clones, do not run long TeX evidence refreshes concurrently in this cloudtainer.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--try-acquire", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=0.0)
    parser.add_argument("--label", default="live-compile")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    if args.self_test:
        report = self_test(root)
    else:
        report = acquire_once(root, args.label, args.wait_seconds)
    print(json.dumps(report, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
