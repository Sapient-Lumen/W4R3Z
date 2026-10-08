#!/usr/bin/env python3
"""mxtest: deterministic pytest collection, chunking, and JSON summaries.

The ordinary ``make test`` path stays simple, but large handoff archives need a
runway that can prove which slice was collected, which slice was run, and which
checks were intentionally skipped or delegated to another chunk.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]


class UsageError(ValueError):
    """Raised for user-facing chunk syntax errors."""


class MxtestInterrupted(BaseException):
    """Raised after mxtest has cleaned up a live pytest child."""

    def __init__(self, signum: int) -> None:
        self.signum = int(signum)
        try:
            name = signal.Signals(signum).name
        except (ValueError, TypeError):
            name = f"SIG{signum}"
        self.signal_name = str(name)
        super().__init__(f"interrupted by {self.signal_name}")

    @property
    def returncode(self) -> int:
        """Return the conventional shell code for signal termination."""

        return 128 + max(0, int(self.signum))


VALID_STRATEGIES = {"node", "file", "segment", "duration"}

SOURCE_MANIFEST_SCHEMA = "micromax.mxtest.source.v1"
SOURCE_MANIFEST_PARTITION_SCHEMA = "micromax.mxtest.source.partitions.v1"
SOURCE_DEPENDENCY_SCHEMA = "micromax.mxtest.source-dependency.v1"
ENVIRONMENT_MANIFEST_SCHEMA = "micromax.mxtest.environment.v1"
ENVIRONMENT_PACKAGE_NAMES = ["pytest"]
ENVIRONMENT_ENV_KEYS = ["PYTEST_DISABLE_PLUGIN_AUTOLOAD", "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED", "PYTHONPATH"]
DEFAULT_HEARTBEAT_SECONDS = 30
_HEARTBEAT_SECONDS_OVERRIDE: int | None = None
RUNTIME_BUDGET_SKIP_REASON = "max-runtime-seconds-reached"
RUNTIME_BUDGET_MIN_CHILD_SECONDS = 5
INTERRUPTED_SKIP_REASON_PREFIX = "interrupted"
TEST_STATUS_ORDER = ["passed", "failed", "timed_out", "partial", "not_run", "running"]
SOURCE_MANIFEST_TOP_LEVEL_FILES = [
    ".editorconfig",
    ".pre-commit-config.yaml",
    "Makefile",
    "README.md",
    "TODO.md",
    "mypy.ini",
    "pyproject.toml",
    "requirements-dev.txt",
    "ruff.toml",
]
SOURCE_MANIFEST_DIRS = [
    "docs",
    "examples",
    "plugins",
    "portability",
    "scripts",
    "src",
    "tests",
    "tools",
]
SOURCE_MANIFEST_SKIP_PARTS = {
    ".artifacts",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
SOURCE_MANIFEST_SKIP_SUFFIXES = {".pyc", ".pyo", ".zip"}
SOURCE_DEPENDENCY_BASE_PARTITIONS = ["runtime"]
SOURCE_DEPENDENCY_BASE_FILES = ["tests/conftest.py"]
SOURCE_DEPENDENCY_TOKEN_PARTITIONS = {
    "docs": [
        "docs",
        "MICROMAX_DOCS",
        "README",
        "TODO",
        "revision-index",
        "help-doc",
        "help docs",
    ],
    "plugins": ["plugins", "plugin"],
    "portability": ["portability"],
    "examples": ["examples"],
    "scripts": ["scripts/", "scripts."],
    "test-config": [
        ".pre-commit-config.yaml",
        "bundled_runtime_resources",
        "data-files",
        "installed-help-manifest",
        "mypy.ini",
        "package-data",
        "pyproject.toml",
        "requirements-dev.txt",
        "ruff.toml",
    ],
    "tooling": ["tools/", "tools.", "mxtest", "mxdoctor", "mxcontext", "mxlint", "mxformat", "mkrevzip"],
    "workflow": [
        "Makefile",
        "doctor-chunked",
        "make test-all-chunks",
        "make test-verify-current",
        "MAX_RUNTIME_SECONDS",
        "TEST_MANIFEST",
        "test-all-chunks",
        "test-verify-current",
    ],
}

PYTEST_OPTIONS_WITH_VALUES = {
    "-k",
    "-m",
    "-o",
    "-p",
    "--basetemp",
    "--cache-clear",
    "--capture",
    "--color",
    "--confcutdir",
    "--deselect",
    "--doctest-glob",
    "--ignore",
    "--ignore-glob",
    "--import-mode",
    "--junit-prefix",
    "--junit-xml",
    "--junitxml",
    "--last-failed-no-failures",
    "--log-cli-level",
    "--log-date-format",
    "--log-file",
    "--log-file-date-format",
    "--log-file-format",
    "--log-file-level",
    "--log-format",
    "--log-level",
    "--maxfail",
    "--override-ini",
    "--rootdir",
    "--tb",
}


PYTEST_COLLECTION_OUTPUT_OPTIONS_WITH_VALUES = {
    "--capture",
    "--color",
    "--durations",
    "--durations-min",
    "--junit-prefix",
    "--junit-xml",
    "--junitxml",
    "--log-cli-level",
    "--log-date-format",
    "--log-file",
    "--log-file-date-format",
    "--log-file-format",
    "--log-file-level",
    "--log-format",
    "--log-level",
    "--tb",
}
PYTEST_COLLECTION_OUTPUT_FLAGS = {
    "--disable-warnings",
    "--quiet",
    "--verbose",
    "-q",
    "-qq",
    "-qqq",
    "-s",
    "-v",
    "-vv",
    "-vvv",
}



def configure_mxtest_heartbeat(seconds: int | None) -> None:
    """Set or clear this process's mxtest child-process heartbeat override."""

    global _HEARTBEAT_SECONDS_OVERRIDE
    if seconds is None:
        _HEARTBEAT_SECONDS_OVERRIDE = None
    else:
        _HEARTBEAT_SECONDS_OVERRIDE = max(0, int(seconds))


def mxtest_heartbeat_seconds() -> int:
    """Return the parent-side child-process heartbeat interval in seconds.

    Long quiet pytest children can look like hung cloudtainer sessions even when
    they are making progress.  Keep the default modest and let automation set
    ``MXTEST_HEARTBEAT_SECONDS=0`` or pass ``--heartbeat 0`` to silence it.
    """

    if _HEARTBEAT_SECONDS_OVERRIDE is not None:
        return int(_HEARTBEAT_SECONDS_OVERRIDE)
    raw = os.environ.get("MXTEST_HEARTBEAT_SECONDS", str(DEFAULT_HEARTBEAT_SECONDS))
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return DEFAULT_HEARTBEAT_SECONDS
    return max(0, value)


def _child_process_group_kwargs() -> dict[str, Any]:
    """Return Popen kwargs that put pytest children in their own process group.

    Some tests intentionally exercise CLI/subprocess paths.  If one of those
    grandchildren survives pytest and keeps stdout/stderr open, the outer
    cloudtainer command can look hung even though the pytest process itself has
    already reported success.  Start each pytest child in a separate group so
    mxtest can terminate descendants on timeout without signaling itself.
    """

    if os.name == "posix":
        return {"start_new_session": True}
    creationflags = int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) or 0)
    return {"creationflags": creationflags} if creationflags else {}


def _confirmed_child_process_group_id(proc: subprocess.Popen[Any]) -> int | None:
    """Return the child's separate POSIX process-group id when confirmed."""

    if os.name != "posix":
        return None
    pid = getattr(proc, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        return None
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return None
    except OSError:
        return None
    # Never signal an unconfirmed group by raw PID.  If start_new_session was
    # unavailable, ignored, or raced with a very short child, a blind killpg(pid)
    # can hit an unrelated process group.
    return int(pgid) if int(pgid) == int(pid) else None


def _signal_process_group(proc: subprocess.Popen[Any], sig: int, *, pgid: int | None = None) -> bool:
    """Best-effort signal for a confirmed pytest child process group."""

    if os.name == "posix":
        target_pgid = pgid if pgid is not None else _confirmed_child_process_group_id(proc)
        if not isinstance(target_pgid, int) or target_pgid <= 0:
            return False
        try:
            os.killpg(target_pgid, sig)
            return True
        except ProcessLookupError:
            return False
        except OSError:
            return False
    if sig == signal.SIGTERM:
        try:
            proc.terminate()
            return True
        except ProcessLookupError:
            return False
        except OSError:
            return False
    try:
        proc.kill()
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return False


def _terminate_process(proc: subprocess.Popen[Any], *, timeout: float = 5.0, pgid: int | None = None) -> None:
    """Best-effort subprocess teardown used after timeout."""

    if proc.poll() is not None:
        return
    signaled_group = _signal_process_group(proc, signal.SIGTERM, pgid=pgid)
    if not signaled_group:
        try:
            proc.terminate()
        except ProcessLookupError:
            return
    deadline = time.monotonic() + max(0.0, float(timeout))
    while proc.poll() is None and time.monotonic() < deadline:
        time.sleep(0.05)
    if proc.poll() is None:
        signaled_group = _signal_process_group(proc, signal.SIGKILL, pgid=pgid)
        if not signaled_group:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
        proc.wait()


def _interruption_signal_numbers() -> list[int]:
    """Return process signals that should clean up a live pytest child."""

    numbers = [signal.SIGINT, signal.SIGTERM]
    sighup = getattr(signal, "SIGHUP", None)
    if sighup is not None:
        numbers.append(sighup)
    out: list[int] = []
    for sig in numbers:
        try:
            value = int(sig)
        except (TypeError, ValueError):
            continue
        if value not in out:
            out.append(value)
    return out


def _install_child_cleanup_signal_handlers(
    proc: subprocess.Popen[Any],
    *,
    pgid: int | None,
    teardown_timeout: float = 2.0,
) -> dict[int, Any]:
    """Install temporary handlers that tear down the active pytest child.

    Cloudtainer/CI wrappers often terminate the parent process on wall-clock
    timeout.  Without a handler, Python exits immediately on SIGTERM and a
    pytest child in its own process group can survive as an orphan.  While a
    child is active, translate interrupting signals into ``MxtestInterrupted``
    after terminating the confirmed child process group.
    """

    previous: dict[int, Any] = {}
    terminating = {"active": False}

    def handler(signum: int, _frame: object) -> None:
        if not terminating["active"]:
            terminating["active"] = True
            _terminate_process(proc, timeout=teardown_timeout, pgid=pgid)
        raise MxtestInterrupted(int(signum))

    for signum in _interruption_signal_numbers():
        try:
            previous[signum] = signal.getsignal(signum)
            signal.signal(signum, handler)
        except (OSError, RuntimeError, ValueError):
            previous.pop(signum, None)
            continue
    return previous


def _restore_signal_handlers(previous: dict[int, Any]) -> None:
    """Restore handlers installed by ``_install_child_cleanup_signal_handlers``."""

    for signum, old_handler in previous.items():
        try:
            signal.signal(signum, old_handler)
        except (OSError, RuntimeError, ValueError):
            continue


def run_subprocess_with_heartbeat(
    cmd: list[str],
    *,
    timeout: int | None = None,
    label: str = "pytest",
    heartbeat_seconds: int | None = None,
) -> int:
    """Run a child process while emitting low-frequency liveness lines.

    The child inherits stdout/stderr so pytest output remains natural.  The
    parent prints only when the child is otherwise quiet for a configured
    interval; this prevents platform inactivity timeouts without requiring
    diagnostic ``-vv`` runs that can perturb collection behavior.
    """

    interval = mxtest_heartbeat_seconds() if heartbeat_seconds is None else max(0, int(heartbeat_seconds))
    started = time.monotonic()
    next_heartbeat = started + interval if interval > 0 else float("inf")
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=isolated_pytest_env(),
        **_child_process_group_kwargs(),
    )
    child_pgid = _confirmed_child_process_group_id(proc)
    previous_handlers = _install_child_cleanup_signal_handlers(proc, pgid=child_pgid)
    try:
        while True:
            rc = proc.poll()
            if rc is not None:
                return int(rc)
            now = time.monotonic()
            if timeout is not None and now - started >= float(timeout):
                _terminate_process(proc, pgid=child_pgid)
                return 124
            if now >= next_heartbeat:
                # Re-poll before emitting: a quiet child may have completed exactly
                # at the heartbeat boundary, and a stale "still running" line after
                # pytest's own summary is misleading during handoff audits.
                rc = proc.poll()
                if rc is not None:
                    return int(rc)
                elapsed = int(now - started)
                print(f"mxtest: still running {label} ({elapsed}s elapsed)", file=sys.stderr, flush=True)
                next_heartbeat = now + interval
            sleep_for = 0.2
            if timeout is not None:
                sleep_for = min(sleep_for, max(0.0, float(timeout) - (now - started)))
            if interval > 0:
                sleep_for = min(sleep_for, max(0.0, next_heartbeat - now))
            time.sleep(max(0.01, sleep_for))
    except KeyboardInterrupt as exc:
        _terminate_process(proc, timeout=2.0, pgid=child_pgid)
        raise MxtestInterrupted(int(signal.SIGINT)) from exc
    finally:
        _restore_signal_handlers(previous_handlers)


def isolated_pytest_env() -> dict[str, str]:
    """Return a deterministic pytest environment.

    Keep this aligned with ``scripts/test.sh`` and ``tools/mxdoctor.py`` so
    source trees, doctors, and chunked runs do not accidentally inherit host
    pytest plugins from the surrounding machine.
    """

    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    return env


def parse_chunk_spec(spec: str) -> tuple[int, int]:
    """Parse ``INDEX/TOTAL`` chunk syntax using one-based indexes."""

    match = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", spec)
    if not match:
        raise UsageError("chunk must use INDEX/TOTAL syntax, for example 1/8")
    index = int(match.group(1))
    total = int(match.group(2))
    if total <= 0:
        raise UsageError("chunk total must be greater than zero")
    if index <= 0 or index > total:
        raise UsageError("chunk index must be between 1 and the chunk total")
    return index, total


def validate_strategy(strategy: str) -> str:
    """Return a normalized chunk strategy or raise a user-facing error."""

    value = str(strategy or "node").strip().lower()
    if value not in VALID_STRATEGIES:
        choices = ", ".join(sorted(VALID_STRATEGIES))
        raise UsageError(f"strategy must be one of: {choices}")
    return value


def split_pytest_args_for_execution(pytest_args: list[str]) -> tuple[list[str], list[str]]:
    """Return (execution args, dropped selectors) for explicit-node runs.

    Collection args may include positional selectors such as ``tests/foo.py``.
    Once mxtest has collected and chunked exact node ids, passing those
    selectors to the execution subprocess can widen the run again.  Keep common
    option flags and their values, but drop positional selectors from execution.
    """

    execution: list[str] = []
    dropped: list[str] = []
    i = 0
    while i < len(pytest_args):
        arg = pytest_args[i]
        if arg == "--":
            i += 1
            continue
        if arg.startswith("-"):
            execution.append(arg)
            option_name = arg.split("=", 1)[0]
            if "=" not in arg and option_name in PYTEST_OPTIONS_WITH_VALUES and i + 1 < len(pytest_args):
                execution.append(pytest_args[i + 1])
                i += 2
                continue
            i += 1
            continue
        dropped.append(arg)
        i += 1
    return execution, dropped


def _is_compact_verbosity_flag(arg: str) -> bool:
    """Return True for compact pytest verbosity/quiet flags such as ``-vv``."""

    return len(arg) > 1 and arg.startswith("-") and not arg.startswith("--") and set(arg[1:]) <= {"v", "q"}


def split_pytest_args_for_collection(pytest_args: list[str]) -> tuple[list[str], list[str]]:
    """Return (collection args, dropped output args) for stable node-id collection.

    ``mxtest`` depends on pytest's quiet ``--collect-only`` node-id output.
    Diagnostic flags such as ``-vv`` are useful for execution, but they change
    collection output into a tree that no longer contains plain node-id lines.
    Preserve selectors and filters while removing output-only/reporting flags
    from the collection subprocess.
    """

    collection: list[str] = []
    dropped: list[str] = []
    i = 0
    while i < len(pytest_args):
        arg = pytest_args[i]
        if arg == "--":
            i += 1
            continue
        option_name = arg.split("=", 1)[0] if arg.startswith("-") else ""
        if arg in PYTEST_COLLECTION_OUTPUT_FLAGS or _is_compact_verbosity_flag(arg):
            dropped.append(arg)
            i += 1
            continue
        if option_name in PYTEST_COLLECTION_OUTPUT_OPTIONS_WITH_VALUES:
            dropped.append(arg)
            if "=" not in arg and i + 1 < len(pytest_args):
                dropped.append(pytest_args[i + 1])
                i += 2
                continue
            i += 1
            continue
        collection.append(arg)
        i += 1
    return collection, dropped


def nodeids_digest(nodeids: list[str]) -> str:
    """Return a stable digest for an exact ordered node-id selection."""

    h = hashlib.sha256()
    for nodeid in nodeids:
        h.update(nodeid.encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def first_last(nodeids: list[str]) -> tuple[str, str]:
    """Return stable first/last node-id evidence for a selection."""

    if not nodeids:
        return "", ""
    return nodeids[0], nodeids[-1]


def _source_manifest_skip(rel: Path) -> bool:
    """Return True when a path is generated/noisy rather than source evidence."""

    parts = rel.parts
    if any(part in SOURCE_MANIFEST_SKIP_PARTS for part in parts):
        return True
    if any(part.endswith(".egg-info") for part in parts):
        return True
    if rel.suffix.lower() in SOURCE_MANIFEST_SKIP_SUFFIXES:
        return True
    if rel.name.endswith("~") or rel.name.startswith(".") and rel.name.endswith(".swp"):
        return True
    return False


def iter_source_manifest_paths(root: Path = ROOT) -> list[Path]:
    """Return repo-relative source paths covered by mxtest source attestation."""

    seen: set[Path] = set()
    out: list[Path] = []

    def add(rel: Path) -> None:
        if rel in seen or _source_manifest_skip(rel):
            return
        path = root / rel
        if not path.is_file() or path.is_symlink():
            return
        seen.add(rel)
        out.append(rel)

    for name in SOURCE_MANIFEST_TOP_LEVEL_FILES:
        add(Path(name))
    for dirname in SOURCE_MANIFEST_DIRS:
        base = root / dirname
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(root)
            add(rel)
    return sorted(out, key=lambda item: item.as_posix())


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_manifest_digest(entries: list[dict[str, Any]]) -> str:
    """Return the stable digest implied by source-manifest file entries."""

    h = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: str(item.get("path", ""))):
        path = str(entry.get("path", ""))
        try:
            size_value = int(entry.get("size", 0))
        except (TypeError, ValueError):
            size_value = 0
        size = str(size_value)
        sha = str(entry.get("sha256", ""))
        h.update(path.encode("utf-8"))
        h.update(b"\0")
        h.update(size.encode("ascii", errors="ignore"))
        h.update(b"\0")
        h.update(sha.encode("ascii", errors="ignore"))
        h.update(b"\0")
    return h.hexdigest()


def source_manifest_partition_for_path(path: str | Path) -> str:
    """Return the coarse source partition for a repo-relative path."""

    rel = Path(str(path))
    first = rel.parts[0] if rel.parts else str(rel)
    if first == "src":
        return "runtime"
    if first in {"docs", "examples", "plugins", "portability", "scripts", "tests", "tools"}:
        return first if first != "tools" else "tooling"
    if rel.name in {"pyproject.toml", "requirements-dev.txt", "mypy.ini", "ruff.toml", ".pre-commit-config.yaml"}:
        return "test-config"
    if rel.name in {"README.md", "TODO.md"}:
        return "docs"
    if rel.name == "Makefile":
        return "workflow"
    return "repo"


def source_manifest_partition_payload(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return partition summaries for source-manifest entries."""

    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            continue
        partition = str(entry.get("partition") or source_manifest_partition_for_path(path))
        grouped.setdefault(partition, []).append(entry)

    out: list[dict[str, Any]] = []
    for name in sorted(grouped):
        items = grouped[name]
        total_bytes = 0
        for item in items:
            try:
                total_bytes += int(item.get("size", 0))
            except (TypeError, ValueError):
                pass
        out.append(
            {
                "name": name,
                "digest": source_manifest_digest(items),
                "file_count": len(items),
                "total_bytes": total_bytes,
            }
        )
    return out


def source_manifest_partition_map(source_manifest: object) -> dict[str, dict[str, Any]]:
    """Return source partition summaries, deriving them for old manifests."""

    if not isinstance(source_manifest, dict):
        return {}
    partitions = source_manifest.get("partitions")
    if isinstance(partitions, list):
        out: dict[str, dict[str, Any]] = {}
        for row in partitions:
            if not isinstance(row, dict):
                continue
            name = row.get("name")
            digest = row.get("digest")
            if isinstance(name, str) and isinstance(digest, str):
                out[name] = dict(row)
        if out:
            return out
    files = source_manifest.get("files")
    if not isinstance(files, list):
        return {}
    entries = [entry for entry in files if isinstance(entry, dict)]
    return {str(row["name"]): row for row in source_manifest_partition_payload(entries)}


def source_manifest_partition_differences(old: object, new: object) -> dict[str, Any]:
    """Return partition-level differences between two source manifests."""

    old_map = source_manifest_partition_map(old)
    new_map = source_manifest_partition_map(new)
    added = sorted(set(new_map) - set(old_map))
    removed = sorted(set(old_map) - set(new_map))
    changed = sorted(
        name
        for name in set(old_map) & set(new_map)
        if old_map[name].get("digest") != new_map[name].get("digest")
        or old_map[name].get("file_count") != new_map[name].get("file_count")
        or old_map[name].get("total_bytes") != new_map[name].get("total_bytes")
    )
    return {
        "available": bool(old_map or new_map),
        "added": added,
        "removed": removed,
        "changed": changed,
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(changed),
    }


def source_manifest_payload(root: Path = ROOT) -> dict[str, Any]:
    """Return a source-content attestation for the repo surfaces tests depend on."""

    entries: list[dict[str, Any]] = []
    total_bytes = 0
    for rel in iter_source_manifest_paths(root):
        path = root / rel
        size = path.stat().st_size
        total_bytes += int(size)
        rel_path = rel.as_posix()
        entries.append(
            {
                "path": rel_path,
                "partition": source_manifest_partition_for_path(rel_path),
                "size": int(size),
                "sha256": _file_sha256(path),
            }
        )
    return {
        "schema": SOURCE_MANIFEST_SCHEMA,
        "partition_schema": SOURCE_MANIFEST_PARTITION_SCHEMA,
        "algorithm": "sha256",
        "digest": source_manifest_digest(entries),
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "partitions": source_manifest_partition_payload(entries),
        "files": entries,
    }


def _source_file_map(source_manifest: object) -> dict[str, dict[str, Any]]:
    if not isinstance(source_manifest, dict):
        return {}
    files = source_manifest.get("files")
    if not isinstance(files, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        sha = entry.get("sha256")
        if isinstance(path, str) and isinstance(sha, str):
            out[path] = entry
    return out


def source_manifest_differences(old: object, new: object) -> dict[str, Any]:
    """Return path-level differences between two source manifests when available."""

    old_map = _source_file_map(old)
    new_map = _source_file_map(new)
    added = sorted(set(new_map) - set(old_map))
    removed = sorted(set(old_map) - set(new_map))
    changed = sorted(
        path
        for path in set(old_map) & set(new_map)
        if old_map[path].get("sha256") != new_map[path].get("sha256")
        or old_map[path].get("size") != new_map[path].get("size")
    )
    return {
        "available": bool(old_map or new_map),
        "added": added,
        "removed": removed,
        "changed": changed,
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(changed),
    }


def source_manifest_issues(payload: dict[str, Any]) -> list[str]:
    """Return internal consistency issues for an embedded source manifest."""

    manifest = payload.get("source_manifest")
    if manifest is None:
        return []
    if not isinstance(manifest, dict):
        return ["source_manifest must be an object"]
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["source_manifest.files must be a list"]
    entries = [entry for entry in files if isinstance(entry, dict)]
    issues: list[str] = []
    if len(entries) != len(files):
        issues.append("source_manifest.files contains non-object entries")
    computed_digest = source_manifest_digest(entries)
    manifest_digest = manifest.get("digest")
    if manifest_digest != computed_digest:
        issues.append(f"source_manifest digest {manifest_digest!r} does not match computed {computed_digest!r}")
    if payload.get("source_digest") is not None and payload.get("source_digest") != manifest_digest:
        issues.append("source_digest does not match source_manifest.digest")
    if manifest.get("file_count") != len(entries):
        issues.append(f"source_manifest file_count {manifest.get('file_count')!r} does not match {len(entries)}")
    total_bytes = 0
    for entry in entries:
        try:
            total_bytes += int(entry.get("size", 0))
        except (TypeError, ValueError):
            issues.append(f"source_manifest entry {entry.get('path')!r} has non-integer size")
    if manifest.get("total_bytes") != total_bytes:
        issues.append(f"source_manifest total_bytes {manifest.get('total_bytes')!r} does not match {total_bytes}")
    if "partitions" in manifest:
        if manifest.get("partition_schema") != SOURCE_MANIFEST_PARTITION_SCHEMA:
            issues.append(
                f"source_manifest partition_schema {manifest.get('partition_schema')!r} "
                f"is not {SOURCE_MANIFEST_PARTITION_SCHEMA!r}"
            )
        partitions = manifest.get("partitions")
        if not isinstance(partitions, list):
            issues.append("source_manifest.partitions must be a list")
        else:
            computed_partitions = source_manifest_partition_payload(entries)
            normalized_computed = {str(row.get("name")): row for row in computed_partitions}
            normalized_manifest: dict[str, dict[str, Any]] = {}
            for row in partitions:
                if not isinstance(row, dict):
                    issues.append("source_manifest.partitions contains non-object entries")
                    continue
                name = row.get("name")
                if not isinstance(name, str):
                    issues.append("source_manifest partition without string name")
                    continue
                normalized_manifest[name] = row
            if set(normalized_manifest) != set(normalized_computed):
                issues.append("source_manifest partition names do not match computed source partitions")
            for name in sorted(set(normalized_manifest) & set(normalized_computed)):
                for field in ["digest", "file_count", "total_bytes"]:
                    if normalized_manifest[name].get(field) != normalized_computed[name].get(field):
                        issues.append(
                            f"source_manifest partition {name!r} field {field} "
                            f"{normalized_manifest[name].get(field)!r} does not match "
                            f"computed {normalized_computed[name].get(field)!r}"
                        )
    return issues


def _source_entry_map(source_manifest: object) -> dict[str, dict[str, Any]]:
    """Return source-manifest file entries keyed by repo-relative path."""

    if not isinstance(source_manifest, dict):
        return {}
    files = source_manifest.get("files")
    if not isinstance(files, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if isinstance(path, str):
            out[path] = entry
    return out


def _source_file_component(entry: dict[str, Any], *, path: str | None = None) -> dict[str, Any]:
    """Return a compact source-dependency component for one file entry."""

    component_path = path if path is not None else entry.get("path")
    component: dict[str, Any] = {
        "kind": "file",
        "path": component_path,
        "size": entry.get("size"),
        "sha256": entry.get("sha256"),
    }
    partition = entry.get("partition")
    if not isinstance(partition, str) and isinstance(component_path, str):
        partition = source_manifest_partition_for_path(component_path)
    if isinstance(partition, str):
        component["partition"] = partition
    return component


def _missing_source_file_component(path: str) -> dict[str, Any]:
    """Return a conservative dependency component for a missing manifest path."""

    return {"kind": "file", "path": path, "missing": True, "sha256": None, "size": None}


def _source_partition_component(name: str, source_manifest: object) -> dict[str, Any]:
    """Return a compact source-dependency component for one partition."""

    row = source_manifest_partition_map(source_manifest).get(name)
    if not isinstance(row, dict):
        return {"kind": "partition", "name": name, "missing": True, "digest": None}
    return {
        "kind": "partition",
        "name": name,
        "digest": row.get("digest"),
        "file_count": row.get("file_count"),
        "total_bytes": row.get("total_bytes"),
    }


def source_dependency_components_digest(components: list[dict[str, Any]]) -> str:
    """Return the stable digest for source-dependency components."""

    normalized = sorted(
        components,
        key=lambda item: (str(item.get("kind", "")), str(item.get("name", item.get("path", "")))),
    )
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_dependency_issues(record: dict[str, Any]) -> list[str]:
    """Return internal consistency issues for a chunk source-dependency record."""

    dependency = record.get("source_dependency")
    if dependency is None:
        return []
    if not isinstance(dependency, dict):
        return ["source_dependency must be an object"]
    issues: list[str] = []
    if dependency.get("schema") != SOURCE_DEPENDENCY_SCHEMA:
        issues.append(f"source_dependency schema {dependency.get('schema')!r} is not {SOURCE_DEPENDENCY_SCHEMA!r}")
    components = dependency.get("components")
    if not isinstance(components, list):
        issues.append("source_dependency.components must be a list")
        component_dicts: list[dict[str, Any]] = []
    else:
        component_dicts = [component for component in components if isinstance(component, dict)]
        if len(component_dicts) != len(components):
            issues.append("source_dependency.components contains non-object entries")
    computed = source_dependency_components_digest(component_dicts)
    if dependency.get("digest") != computed:
        issues.append(f"source_dependency digest {dependency.get('digest')!r} does not match computed {computed!r}")
    if record.get("source_dependency_digest") is not None and record.get("source_dependency_digest") != dependency.get("digest"):
        issues.append("source_dependency_digest does not match source_dependency.digest")
    partitions = sorted(
        str(component.get("name"))
        for component in component_dicts
        if component.get("kind") == "partition" and isinstance(component.get("name"), str)
    )
    files = sorted(
        str(component.get("path"))
        for component in component_dicts
        if component.get("kind") == "file" and isinstance(component.get("path"), str)
    )
    if record.get("source_dependency_partitions") is not None and record.get("source_dependency_partitions") != partitions:
        issues.append("source_dependency_partitions does not match source_dependency partition components")
    if record.get("source_dependency_files") is not None and record.get("source_dependency_files") != files:
        issues.append("source_dependency_files does not match source_dependency file components")
    if dependency.get("component_count") is not None and dependency.get("component_count") != len(component_dicts):
        issues.append("source_dependency component_count does not match source_dependency.components")
    return issues


def _selected_test_files(nodeids: list[str]) -> list[str]:
    """Return selected test files from node ids in collection order."""

    out: list[str] = []
    seen: set[str] = set()
    for nodeid in nodeids:
        filename = str(nodeid).split("::", 1)[0]
        if filename and filename not in seen:
            seen.add(filename)
            out.append(filename)
    return out


def _test_file_text_for_dependency(filename: str, *, root: Path = ROOT) -> str:
    """Return a test file's text for dependency-token scanning."""

    try:
        path = root / filename
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def source_dependency_partitions_for_test_files(test_files: list[str], *, root: Path = ROOT) -> list[str]:
    """Return non-base source partitions implied by selected test file contents."""

    required: set[str] = set()
    for filename in test_files:
        lowered_name = filename.lower()
        text = _test_file_text_for_dependency(filename, root=root)
        haystack = f"{filename}\n{text}"
        lowered_haystack = haystack.lower()
        for partition, tokens in SOURCE_DEPENDENCY_TOKEN_PARTITIONS.items():
            for token in tokens:
                if token.lower() in lowered_haystack:
                    required.add(partition)
                    break
        if lowered_name.startswith("tests/test_tui_md_"):
            required.discard("docs")
    return sorted(required)


def source_dependency_payload_for_nodeids(source_manifest: object, nodeids: list[str]) -> dict[str, Any]:
    """Return chunk-scoped source dependencies for a selected node-id span.

    The global source digest remains useful for whole-tree attestation, but it
    makes every docs-only handoff edit invalidate every passed test span.  This
    payload records the narrower evidence that a chunk actually depends on: the
    runtime partition, shared pytest config, the selected test files, and extra
    partitions only when the selected tests visibly touch docs/plugins/tools.
    """

    entry_map = _source_entry_map(source_manifest)
    test_files = _selected_test_files(nodeids)
    partition_names = sorted(
        set(SOURCE_DEPENDENCY_BASE_PARTITIONS)
        | set(source_dependency_partitions_for_test_files(test_files))
    )
    file_paths = sorted(set(SOURCE_DEPENDENCY_BASE_FILES) | set(test_files))
    components: list[dict[str, Any]] = []
    for name in partition_names:
        components.append(_source_partition_component(name, source_manifest))
    for path in file_paths:
        entry = entry_map.get(path)
        components.append(_source_file_component(entry, path=path) if isinstance(entry, dict) else _missing_source_file_component(path))
    digest = source_dependency_components_digest(components)
    return {
        "schema": SOURCE_DEPENDENCY_SCHEMA,
        "algorithm": "sha256-components",
        "digest": digest,
        "component_count": len(components),
        "partitions": partition_names,
        "files": file_paths,
        "components": components,
    }


def attach_source_dependency(record: dict[str, Any], source_manifest: object, nodeids: list[str]) -> dict[str, Any]:
    """Return a copy of a chunk record with chunk-scoped source evidence."""

    dependency = source_dependency_payload_for_nodeids(source_manifest, nodeids)
    copied = dict(record)
    copied["source_dependency_digest"] = dependency["digest"]
    copied["source_dependency_partitions"] = dependency["partitions"]
    copied["source_dependency_files"] = dependency["files"]
    copied["source_dependency_component_count"] = dependency["component_count"]
    copied["source_dependency"] = dependency
    return copied


def source_dependency_digest_for_record(
    record: dict[str, Any], *, manifest: dict[str, Any], selected: list[str]
) -> str | None:
    """Return the source-dependency digest for a record, deriving old evidence."""

    digest = record.get("source_dependency_digest")
    if isinstance(digest, str):
        return digest
    dependency = record.get("source_dependency")
    if isinstance(dependency, dict) and isinstance(dependency.get("digest"), str):
        return str(dependency["digest"])
    source_manifest = manifest.get("source_manifest")
    if isinstance(source_manifest, dict):
        return str(source_dependency_payload_for_nodeids(source_manifest, selected).get("digest"))
    return None


def chunk_source_dependency_matches(
    previous: dict[str, Any],
    planned: dict[str, Any],
    *,
    previous_manifest: dict[str, Any],
    selected: list[str],
    fallback_source_digest_matches: bool,
) -> bool:
    """Return True when previous source evidence still applies to this chunk."""

    planned_digest = planned.get("source_dependency_digest")
    previous_digest = source_dependency_digest_for_record(previous, manifest=previous_manifest, selected=selected)
    if isinstance(planned_digest, str) and isinstance(previous_digest, str):
        return previous_digest == planned_digest
    return bool(fallback_source_digest_matches)


def resumed_chunk_record(previous: dict[str, Any], planned: dict[str, Any], *, reason: str) -> dict[str, Any]:
    """Return a terminal record that preserves matching previous pass evidence."""

    resumed = dict(previous)
    resumed["resumed"] = True
    resumed["skipped"] = True
    resumed["skip_reason"] = reason
    if "source_dependency_digest" not in resumed:
        resumed.update(
            {
                "source_dependency_digest": planned.get("source_dependency_digest"),
                "source_dependency_partitions": planned.get("source_dependency_partitions"),
                "source_dependency_files": planned.get("source_dependency_files"),
                "source_dependency_component_count": planned.get("source_dependency_component_count"),
                "source_dependency": planned.get("source_dependency"),
            }
        )
    return resumed


def should_preserve_resumed_remainder(reason: str) -> bool:
    """Return True when a stop should still keep later passed evidence.

    Chunk-level skip reasons can combine several file-level budget reasons with
    ``+``.  Treat the combined stop as preservable only when every component is
    one of the intentional bounded-stop classes.
    """

    parts = [part for part in str(reason or "").split("+") if part]
    if not parts:
        return False
    return all(
        part == RUNTIME_BUDGET_SKIP_REASON
        or part.startswith("max-new-")
        or part.startswith(INTERRUPTED_SKIP_REASON_PREFIX)
        for part in parts
    )


def _package_version(name: str) -> str | None:
    """Return an installed distribution version without importing the package."""

    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment_manifest_digest(manifest: dict[str, Any]) -> str:
    """Return a stable digest for an environment manifest payload."""

    normalized = dict(manifest)
    normalized.pop("digest", None)
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def environment_manifest_payload(env: dict[str, str] | None = None) -> dict[str, Any]:
    """Return lightweight host/dependency evidence for an mxtest run.

    Source attestation answers "what files did this manifest validate?"  This
    environment attestation answers the separate handoff question "what Python,
    pytest, platform, and relevant test-environment knobs produced it?"  Keep it
    intentionally small: it is not a lockfile, but it makes host drift visible in
    no-run manifest audits.
    """

    effective_env = dict(env if env is not None else isolated_pytest_env())
    packages = [
        {"name": name, "version": _package_version(name)}
        for name in ENVIRONMENT_PACKAGE_NAMES
    ]
    manifest: dict[str, Any] = {
        "schema": ENVIRONMENT_MANIFEST_SCHEMA,
        "algorithm": "sha256-json",
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "version_info": [
                int(sys.version_info.major),
                int(sys.version_info.minor),
                int(sys.version_info.micro),
                str(sys.version_info.releaselevel),
                int(sys.version_info.serial),
            ],
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "pytest": {
            "version": _package_version("pytest"),
            "disable_plugin_autoload": effective_env.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD"),
        },
        "packages": packages,
        "env": {key: effective_env.get(key) for key in ENVIRONMENT_ENV_KEYS if key in effective_env},
    }
    manifest["digest"] = environment_manifest_digest(manifest)
    return manifest


def environment_manifest_issues(payload: dict[str, Any]) -> list[str]:
    """Return internal consistency issues for an embedded environment manifest."""

    manifest = payload.get("environment_manifest")
    if manifest is None:
        return []
    if not isinstance(manifest, dict):
        return ["environment_manifest must be an object"]
    issues: list[str] = []
    if manifest.get("schema") != ENVIRONMENT_MANIFEST_SCHEMA:
        issues.append(f"environment_manifest schema {manifest.get('schema')!r} is not {ENVIRONMENT_MANIFEST_SCHEMA!r}")
    if manifest.get("algorithm") != "sha256-json":
        issues.append("environment_manifest algorithm must be 'sha256-json'")
    computed_digest = environment_manifest_digest(manifest)
    manifest_digest = manifest.get("digest")
    if manifest_digest != computed_digest:
        issues.append(f"environment_manifest digest {manifest_digest!r} does not match computed {computed_digest!r}")
    if payload.get("environment_digest") is not None and payload.get("environment_digest") != manifest_digest:
        issues.append("environment_digest does not match environment_manifest.digest")
    for field in ["python", "platform", "pytest"]:
        if not isinstance(manifest.get(field), dict):
            issues.append(f"environment_manifest.{field} must be an object")
    if not isinstance(manifest.get("packages"), list):
        issues.append("environment_manifest.packages must be a list")
    if not isinstance(manifest.get("env"), dict):
        issues.append("environment_manifest.env must be an object")
    return issues


def _environment_comparison_map(manifest: object) -> dict[str, object]:
    """Flatten the stable environment fields used for human diffs."""

    if not isinstance(manifest, dict):
        return {}
    out: dict[str, object] = {}

    def add(prefix: str, value: object) -> None:
        if isinstance(value, dict):
            for key in sorted(value):
                add(f"{prefix}.{key}" if prefix else str(key), value[key])
        elif isinstance(value, list):
            if prefix == "packages":
                for item in value:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name")
                    if isinstance(name, str):
                        out[f"packages.{name}"] = item.get("version")
            else:
                out[prefix] = value
        else:
            out[prefix] = value

    for key in ["schema", "algorithm", "python", "platform", "pytest", "packages", "env"]:
        add(key, manifest.get(key))
    return out


def environment_manifest_differences(old: object, new: object) -> dict[str, Any]:
    """Return field-level differences between two environment manifests."""

    old_map = _environment_comparison_map(old)
    new_map = _environment_comparison_map(new)
    added = sorted(set(new_map) - set(old_map))
    removed = sorted(set(old_map) - set(new_map))
    changed = sorted(path for path in set(old_map) & set(new_map) if old_map[path] != new_map[path])
    return {
        "available": bool(old_map or new_map),
        "added": added,
        "removed": removed,
        "changed": changed,
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(changed),
    }


def select_chunk(items: list[str], *, index: int, total: int) -> list[str]:
    """Return the balanced contiguous chunk for ``index`` of ``total``."""

    if total <= 0:
        raise UsageError("chunk total must be greater than zero")
    if index <= 0 or index > total:
        raise UsageError("chunk index must be between 1 and the chunk total")
    count = len(items)
    base, extra = divmod(count, total)
    start = (index - 1) * base + min(index - 1, extra)
    stop = start + base + (1 if index <= extra else 0)
    return items[start:stop]


def chunk_counts(count: int, total: int) -> list[int]:
    """Return the selected-test count for each node-balanced chunk."""

    return [len(select_chunk([""] * count, index=i, total=total)) for i in range(1, total + 1)]


def group_nodeids_by_file(nodeids: list[str]) -> list[tuple[str, list[str]]]:
    """Group collected node ids by file while preserving collection order."""

    groups: list[tuple[str, list[str]]] = []
    by_file: dict[str, list[str]] = {}
    for nodeid in nodeids:
        filename = nodeid.split("::", 1)[0]
        bucket = by_file.get(filename)
        if bucket is None:
            bucket = []
            by_file[filename] = bucket
            groups.append((filename, bucket))
        bucket.append(nodeid)
    return groups


def nodeid_batches(nodeids: list[str], *, batch_size: int) -> list[list[str]]:
    """Return non-empty node-id batches preserving order.

    A size of zero keeps the historical behavior: one pytest subprocess per
    selected file/group.  Positive sizes let interrupt-prone aggregate runs
    checkpoint progress inside a large test file without changing collection or
    chunk selection semantics.
    """

    if not nodeids:
        return []
    size = max(0, int(batch_size or 0))
    if size <= 0 or size >= len(nodeids):
        return [list(nodeids)]
    return [list(nodeids[index : index + size]) for index in range(0, len(nodeids), size)]


def _duration_value(value: object) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if number < 0:
        return None
    return number


def file_duration_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return per-file duration records from single-run or aggregate JSON.

    Rev750 taught mxtest to consume ``--isolate-files`` summaries, which store
    file rows at top-level ``files``.  Rev751 aggregate manifests preserve those
    rows under each ``chunk_results[*].files`` entry.  Treat both shapes as
    duration-history sources so an all-chunks manifest can directly drive the
    next duration-balanced run.
    """

    records: list[dict[str, Any]] = []

    def add_files(value: object) -> None:
        if not isinstance(value, list):
            return
        for record in value:
            if isinstance(record, dict):
                records.append(record)

    add_files(payload.get("files"))
    chunk_results = payload.get("chunk_results")
    if isinstance(chunk_results, list):
        for chunk in chunk_results:
            if isinstance(chunk, dict):
                add_files(chunk.get("files"))
    return records


def load_duration_history(paths: list[Path]) -> dict[str, float]:
    """Load per-file duration hints from previous mxtest JSON summaries.

    The expected source is a run JSON emitted by ``--isolate-files`` or a
    rev751+ all-chunks aggregate JSON that contains isolated per-file rows under
    ``chunk_results[*].files``.  Multiple histories are merged by keeping the
    largest observed duration for a file, so an unusually slow but real run is
    not hidden by a later warm-cache run.
    """

    history: dict[str, float] = {}
    for path in paths:
        p = Path(path)
        if not p.exists():
            raise UsageError(f"history file not found: {p}")
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise UsageError(f"history file is not valid JSON: {p}: {exc}") from exc
        if not isinstance(payload, dict):
            continue
        for record in file_duration_records(payload):
            filename = record.get("file")
            duration = _duration_value(record.get("duration_seconds"))
            if not isinstance(filename, str) or duration is None:
                continue
            previous = history.get(filename)
            if previous is None or duration > previous:
                history[filename] = duration
    return history


def _file_weight(filename: str, nodeids: list[str], *, strategy: str, duration_history: dict[str, float]) -> float:
    if strategy == "duration":
        duration = duration_history.get(filename)
        if duration is not None:
            return max(0.001, float(duration))
    return float(max(1, len(nodeids)))


def _strategy_weight_unit(strategy: str, duration_history: dict[str, float]) -> str:
    if strategy == "duration":
        if duration_history:
            return "seconds-with-test-count-fallback"
        return "test-count-fallback"
    return "tests"


def build_chunks(
    nodeids: list[str],
    total: int,
    *,
    strategy: str = "node",
    duration_history: dict[str, float] | None = None,
) -> list[list[str]]:
    """Return selected node ids for every chunk using the requested strategy.

    ``node`` preserves the rev748/rev749 contiguous node-id slicing.  ``file``
    keeps each test file whole and balances by tests per file.  ``segment``
    keeps ordinary files whole but splits oversized files into contiguous
    segments so one very large file does not own a chunk.  ``duration`` keeps
    files whole but uses previous per-file mxtest durations when present,
    falling back to test counts for new or missing files.
    """

    if total <= 0:
        raise UsageError("chunk total must be greater than zero")
    strategy = validate_strategy(strategy)
    history = dict(duration_history or {})
    if strategy == "node":
        return [select_chunk(nodeids, index=i, total=total) for i in range(1, total + 1)]

    groups = group_nodeids_by_file(nodeids)
    weighted: list[tuple[float, str, list[str], float]] = []
    target_count = max(1, math.ceil(len(nodeids) / total)) if total else max(1, len(nodeids))
    for order, (filename, group_nodeids) in enumerate(groups):
        group_nodeids = list(group_nodeids)
        if strategy == "segment" and len(group_nodeids) > target_count and len(group_nodeids) > 1:
            pieces = min(len(group_nodeids), max(2, math.ceil(len(group_nodeids) / target_count)))
            for segment_index in range(1, pieces + 1):
                segment_nodeids = select_chunk(group_nodeids, index=segment_index, total=pieces)
                if not segment_nodeids:
                    continue
                # Keep segment order stable within a file while letting the
                # scheduler place different segments into different chunks.
                order_key = float(order) + (segment_index / (pieces + 1))
                weighted.append((order_key, filename, segment_nodeids, float(len(segment_nodeids))))
            continue
        weighted.append(
            (
                float(order),
                filename,
                group_nodeids,
                _file_weight(filename, group_nodeids, strategy=strategy, duration_history=history),
            )
        )

    chunk_items: list[list[tuple[float, str, list[str], float]]] = [[] for _ in range(total)]
    chunk_weights = [0.0 for _ in range(total)]
    # Longest-processing-time scheduling gives a deterministic, small scheduler
    # that reduces the chance of one chunk becoming a docs-heavy cliff.  Each
    # chunk re-sorts by collection order before returning node ids, so per-file
    # execution still follows pytest's natural order inside the selected slice.
    for item in sorted(weighted, key=lambda it: (-it[3], -len(it[2]), it[0])):
        target = min(range(total), key=lambda idx: (chunk_weights[idx], len(chunk_items[idx]), idx))
        chunk_items[target].append(item)
        chunk_weights[target] += item[3]

    chunks: list[list[str]] = []
    for items in chunk_items:
        selected: list[str] = []
        for _order, _filename, group_nodeids, _weight in sorted(items, key=lambda it: it[0]):
            selected.extend(group_nodeids)
        chunks.append(selected)
    return chunks


def _nodeid_weight(nodeids: list[str], *, strategy: str, duration_history: dict[str, float]) -> float:
    if strategy == "node":
        return float(len(nodeids))
    total = 0.0
    for filename, group in group_nodeids_by_file(nodeids):
        total += _file_weight(filename, group, strategy=strategy, duration_history=duration_history)
    return total


def _history_flags(history_paths: list[Path]) -> list[str]:
    out: list[str] = []
    for p in history_paths:
        out.extend(["--history", str(p)])
    return out


def _chunk_command(
    *, index: int, total: int, strategy: str, history_paths: list[Path], pytest_args: list[str]
) -> str:
    parts = ["python", "tools/mxtest.py", "--chunk", f"{index}/{total}"]
    if strategy != "node":
        parts.extend(["--strategy", strategy])
    parts.append("--isolate-files")
    parts.extend(_history_flags(history_paths))
    if pytest_args:
        parts.append("--")
        parts.extend(pytest_args)
    return " ".join(shlex.quote(part) for part in parts)


def chunk_plan(
    nodeids: list[str],
    total: int,
    *,
    strategy: str = "node",
    duration_history: dict[str, float] | None = None,
    history_paths: list[Path] | None = None,
    pytest_args: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return resumable metadata for each chunk."""

    if total <= 0:
        raise UsageError("chunk total must be greater than zero")
    strategy = validate_strategy(strategy)
    history = dict(duration_history or {})
    paths = list(history_paths or [])
    extra_args = list(pytest_args or [])
    chunks = build_chunks(nodeids, total, strategy=strategy, duration_history=history)
    out: list[dict[str, Any]] = []
    for index, selected in enumerate(chunks, start=1):
        files = [name for name, _group in group_nodeids_by_file(selected)]
        out.append(
            {
                "index": index,
                "total": total,
                "strategy": strategy,
                "selected": len(selected),
                "strategy_weight": round(_nodeid_weight(selected, strategy=strategy, duration_history=history), 3),
                "strategy_weight_unit": _strategy_weight_unit(strategy, history),
                "file_count": len(files),
                "first": first_last(selected)[0],
                "last": first_last(selected)[1],
                "nodeids_digest": nodeids_digest(selected),
                "files": files,
                "command": _chunk_command(
                    index=index,
                    total=total,
                    strategy=strategy,
                    history_paths=paths,
                    pytest_args=extra_args,
                ),
            }
        )
    return out


def status_for_returncode(rc: int) -> str:
    """Return a stable JSON status label for a pytest subprocess code."""

    if int(rc) == 0:
        return "passed"
    if int(rc) == 124:
        return "timed_out"
    return "failed"


def _looks_like_nodeid(line: str) -> bool:
    if not line or line.startswith("="):
        return False
    if line.endswith(" collected") or " collected in " in line:
        return False
    return "::" in line or line.startswith("tests/")


def collect_nodeids(pytest_args: list[str]) -> list[str]:
    """Collect pytest node ids with plugin autoload disabled by default."""

    collection_args, dropped_output_args = split_pytest_args_for_collection(pytest_args)
    if dropped_output_args:
        print(
            "mxtest: collection ignores output-only pytest args: "
            + " ".join(shlex.quote(arg) for arg in dropped_output_args),
            file=sys.stderr,
        )
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", *collection_args]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=isolated_pytest_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        print(proc.stdout, end="")
        raise SystemExit(proc.returncode)
    nodeids = [line.strip() for line in proc.stdout.splitlines() if _looks_like_nodeid(line.strip())]
    return nodeids


def write_json_summary(path: Path, payload: dict[str, Any]) -> None:
    """Atomically write a JSON checkpoint/summary manifest.

    ``--run-chunks`` updates the same aggregate file after every chunk.  A
    direct truncate/write can corrupt the only resume witness if a cloudtainer
    or terminal is interrupted mid-write.  Write in the same directory and
    promote with ``os.replace`` so readers see either the old complete manifest
    or the new complete manifest.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp_path), str(path))
    except Exception:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise


def _pytest_run_label(nodeids: list[str]) -> str:
    """Return a compact human label for a selected pytest child."""

    files = [name for name, _group in group_nodeids_by_file(nodeids)]
    if not files:
        return "pytest"
    if len(files) == 1:
        return f"pytest {files[0]} ({len(nodeids)} tests)"
    return f"pytest {len(nodeids)} tests across {len(files)} files"


def run_pytest(
    nodeids: list[str],
    pytest_args: list[str],
    *,
    durations: int,
    timeout: int | None = None,
    progress_jsonl: Path | None = None,
) -> int:
    if not nodeids:
        print("mxtest: no selected tests; not invoking pytest with an empty node-id list", file=sys.stderr)
        return 5
    cmd = [sys.executable, "-m", "pytest", "-q"]
    if durations > 0:
        cmd.extend(["--durations", str(durations)])
    if progress_jsonl is not None:
        cmd.extend(["-p", "tools.mxtest_progress_plugin", "--mxtest-progress-jsonl", str(progress_jsonl)])
    cmd.extend(nodeids)
    cmd.extend(pytest_args)
    label = _pytest_run_label(nodeids)
    rc = run_subprocess_with_heartbeat(cmd, timeout=timeout, label=label)
    if int(rc) == 124 and timeout is not None:
        joined = " ".join(nodeids[:3])
        suffix = " ..." if len(nodeids) > 3 else ""
        print(f"mxtest: pytest subprocess timed out after {timeout}s: {joined}{suffix}", file=sys.stderr)
    return int(rc)


FileProgressCallback = Callable[[list[dict[str, Any]]], None]
StopRequestedCallback = Callable[[], bool]
ChildTimeoutCallback = Callable[[int | None], int | None]


def nodeid_span_fields(nodeids: list[str]) -> dict[str, str]:
    """Return stable first/last node-id fields for a manifest file row."""

    if not nodeids:
        return {"nodeid_first": "", "nodeid_last": ""}
    return {"nodeid_first": str(nodeids[0]), "nodeid_last": str(nodeids[-1])}


def _file_row_meta_for_nodeids(
    filename: str,
    nodeids: list[str],
    *,
    batch_index: int | None = None,
    batch_total: int | None = None,
    batch_size: int = 0,
    file_selected: int | None = None,
) -> dict[str, Any]:
    """Return common manifest row fields for an exact node-id span."""

    row: dict[str, Any] = {
        "file": filename,
        "selected": len(nodeids),
        "nodeids_digest": nodeids_digest(nodeids),
        **nodeid_span_fields(nodeids),
    }
    if batch_index is not None and batch_total is not None and batch_total > 1:
        row["batch_index"] = int(batch_index)
        row["batch_total"] = int(batch_total)
        row["batch_size"] = max(0, int(batch_size or 0))
        row["file_selected"] = int(file_selected if file_selected is not None else len(nodeids))
    return row


def progress_jsonl_ok_prefix(path: Path | None, selected: list[str]) -> list[str]:
    """Return the contiguous selected prefix with resume-safe pytest progress records."""

    if path is None or not selected or not path.exists():
        return []
    ok_nodeids: set[str] = set()
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                nodeid = record.get("nodeid")
                if not isinstance(nodeid, str):
                    continue
                if record.get("outcome") in {"passed", "skipped"}:
                    ok_nodeids.add(nodeid)
    except OSError:
        return []
    prefix: list[str] = []
    for nodeid in selected:
        if nodeid not in ok_nodeids:
            break
        prefix.append(nodeid)
    return prefix


def _file_row_nodeids_from_selected(row: dict[str, Any], selected: list[str]) -> list[str]:
    """Return the selected node ids covered by one manifest file row.

    New rows carry ``nodeid_first``/``nodeid_last`` so a single test file can be
    represented by multiple resumable segments.  Older manifests only carried a
    file name, so preserve the whole-file fallback for rev829/rev0830 evidence.
    """

    filename = row.get("file")
    if not isinstance(filename, str):
        return []
    try:
        expected_count = int(row.get("selected", 0) or 0)
    except (TypeError, ValueError):
        expected_count = 0
    if expected_count <= 0:
        return []

    first = row.get("nodeid_first")
    last = row.get("nodeid_last")
    if isinstance(first, str) and isinstance(last, str) and first and last:
        try:
            start = selected.index(first)
        except ValueError:
            return []
        expected_stop = start + expected_count - 1
        if 0 <= expected_stop < len(selected) and selected[expected_stop] == last:
            span = selected[start : expected_stop + 1]
        else:
            try:
                stop = selected.index(last, start)
            except ValueError:
                return []
            span = selected[start : stop + 1]
        if len(span) != expected_count:
            return []
        if any(nodeid.split("::", 1)[0] != filename for nodeid in span):
            return []
        return list(span)

    whole_file = [nodeid for nodeid in selected if nodeid.split("::", 1)[0] == filename]
    return whole_file if len(whole_file) == expected_count else []


def run_pytest_file_isolated(
    nodeids: list[str],
    pytest_args: list[str],
    *,
    durations: int,
    file_timeout: int | None,
    progress: FileProgressCallback | None = None,
    test_batch_size: int = 0,
    checkpoint_tests: bool = False,
    stop_requested: StopRequestedCallback | None = None,
    stop_reason: str = RUNTIME_BUDGET_SKIP_REASON,
    child_timeout: ChildTimeoutCallback | None = None,
) -> tuple[int, list[dict[str, Any]]]:
    """Run selected node ids in one fresh pytest process per file or batch.

    ``progress`` receives a manifest-safe snapshot before each file starts and
    after each file reaches a terminal state.  Runtime-stop callbacks can record
    the remaining selected spans as ``not_run``.  When ``checkpoint_tests`` is
    set, pytest children also write per-test JSONL progress so an interruption
    inside a long subprocess can still preserve the contiguous prefix that
    completed test teardown successfully.
    """

    if not nodeids:
        print("mxtest: no selected tests; not invoking pytest with an empty node-id list", file=sys.stderr)
        return 5, []

    def publish(rows: list[dict[str, Any]]) -> None:
        if progress is not None:
            progress([dict(row) for row in rows])

    final_rc = 0
    summaries: list[dict[str, Any]] = []
    groups = group_nodeids_by_file(nodeids)
    for file_index, (filename, group_nodeids) in enumerate(groups, start=1):
        batches = nodeid_batches(group_nodeids, batch_size=test_batch_size)
        for batch_index, batch_nodeids in enumerate(batches, start=1):
            if stop_requested is not None and stop_requested():
                remaining_nodeids = [*batch_nodeids]
                for later_batch in batches[batch_index:]:
                    remaining_nodeids.extend(later_batch)
                for _later_filename, later_group in groups[file_index:]:
                    remaining_nodeids.extend(later_group)
                summaries.extend(not_run_file_rows_for_nodeids(remaining_nodeids, reason=stop_reason))
                publish(summaries)
                return final_rc, summaries
            if len(batches) == 1:
                print(f"mxtest: file {file_index}/{len(groups)} {filename} ({len(batch_nodeids)} tests)")
            else:
                print(
                    "mxtest: file "
                    f"{file_index}/{len(groups)} batch {batch_index}/{len(batches)} "
                    f"{filename} ({len(batch_nodeids)}/{len(group_nodeids)} tests)"
                )
            sys.stdout.flush()
            row_meta = _file_row_meta_for_nodeids(
                filename,
                batch_nodeids,
                batch_index=batch_index,
                batch_total=len(batches),
                batch_size=int(test_batch_size or 0),
                file_selected=len(group_nodeids),
            )
            timeout_seconds = child_timeout(file_timeout) if child_timeout is not None else file_timeout
            if timeout_seconds is not None:
                timeout_seconds = max(1, int(timeout_seconds))
                row_meta["timeout_seconds"] = timeout_seconds
            running_record: dict[str, Any] = {
                **row_meta,
                "returncode": None,
                "duration_seconds": 0.0,
                "timed_out": False,
                "status": "running",
                "checkpoint_reason": "file-started" if len(batches) == 1 else "file-batch-started",
            }
            if checkpoint_tests:
                running_record["checkpoint_tests"] = True
            publish([*summaries, running_record])
            started = time.monotonic()
            progress_path: Path | None = None
            tmpdir_obj: tempfile.TemporaryDirectory[str] | None = None
            try:
                if checkpoint_tests:
                    tmpdir_obj = tempfile.TemporaryDirectory(prefix="mxtest-progress-")
                    progress_path = Path(tmpdir_obj.name) / "pytest-progress.jsonl"
                run_kwargs: dict[str, Any] = {"durations": durations, "timeout": timeout_seconds}
                if progress_path is not None:
                    run_kwargs["progress_jsonl"] = progress_path
                rc = run_pytest(batch_nodeids, pytest_args, **run_kwargs)
            except MxtestInterrupted as exc:
                elapsed = round(time.monotonic() - started, 3)
                completed_prefix = progress_jsonl_ok_prefix(progress_path, batch_nodeids)
                if completed_prefix:
                    completed_meta = _file_row_meta_for_nodeids(
                        filename,
                        completed_prefix,
                        batch_index=batch_index,
                        batch_total=len(batches),
                        batch_size=int(test_batch_size or 0),
                        file_selected=len(group_nodeids),
                    )
                    if timeout_seconds is not None:
                        completed_meta["timeout_seconds"] = timeout_seconds
                    summaries.append(
                        {
                            **completed_meta,
                            "returncode": 0,
                            "duration_seconds": elapsed,
                            "timed_out": False,
                            "status": "passed",
                            "checkpoint_reason": "pytest-test-progress",
                            "checkpoint_tests": True,
                        }
                    )
                remaining = batch_nodeids[len(completed_prefix) :]
                if remaining:
                    remaining_meta = _file_row_meta_for_nodeids(
                        filename,
                        remaining,
                        batch_index=batch_index,
                        batch_total=len(batches),
                        batch_size=int(test_batch_size or 0),
                        file_selected=len(group_nodeids),
                    )
                    if timeout_seconds is not None:
                        remaining_meta["timeout_seconds"] = timeout_seconds
                    summaries.append(
                        {
                            **remaining_meta,
                            "returncode": int(exc.returncode),
                            "duration_seconds": elapsed,
                            "timed_out": False,
                            "status": "partial",
                            "interrupted": True,
                            "signal": exc.signal_name,
                            "checkpoint_reason": "interrupted-during-pytest-batch",
                            "checkpoint_tests": bool(checkpoint_tests),
                        }
                    )
                publish(summaries)
                if tmpdir_obj is not None:
                    tmpdir_obj.cleanup()
                raise
            elapsed = round(time.monotonic() - started, 3)
            runtime_limited_timeout = bool(
                child_timeout is not None
                and int(rc) == 124
                and timeout_seconds is not None
                and (file_timeout is None or int(timeout_seconds) < int(file_timeout))
            )
            if runtime_limited_timeout:
                completed_prefix = progress_jsonl_ok_prefix(progress_path, batch_nodeids) if checkpoint_tests else []
                if completed_prefix:
                    completed_meta = _file_row_meta_for_nodeids(
                        filename,
                        completed_prefix,
                        batch_index=batch_index,
                        batch_total=len(batches),
                        batch_size=int(test_batch_size or 0),
                        file_selected=len(group_nodeids),
                    )
                    completed_meta["timeout_seconds"] = timeout_seconds
                    summaries.append(
                        {
                            **completed_meta,
                            "returncode": 0,
                            "duration_seconds": elapsed,
                            "timed_out": False,
                            "status": "passed",
                            "checkpoint_reason": "pytest-test-progress",
                            "checkpoint_tests": True,
                        }
                    )
                remaining_nodeids = batch_nodeids[len(completed_prefix) :]
                for later_batch in batches[batch_index:]:
                    remaining_nodeids.extend(later_batch)
                for _later_filename, later_group in groups[file_index:]:
                    remaining_nodeids.extend(later_group)
                if remaining_nodeids:
                    remaining_rows = not_run_file_rows_for_nodeids(remaining_nodeids, reason=stop_reason)
                    for row in remaining_rows:
                        row["checkpoint_reason"] = "runtime-budget-child-timeout"
                        row["timeout_seconds"] = timeout_seconds
                        if checkpoint_tests:
                            row["checkpoint_tests"] = True
                    summaries.extend(remaining_rows)
                publish(summaries)
                if tmpdir_obj is not None:
                    tmpdir_obj.cleanup()
                return final_rc, summaries
            if checkpoint_tests and int(rc) == 124:
                completed_prefix = progress_jsonl_ok_prefix(progress_path, batch_nodeids)
                remaining = batch_nodeids[len(completed_prefix) :]
                if completed_prefix and remaining:
                    completed_meta = _file_row_meta_for_nodeids(
                        filename,
                        completed_prefix,
                        batch_index=batch_index,
                        batch_total=len(batches),
                        batch_size=int(test_batch_size or 0),
                        file_selected=len(group_nodeids),
                    )
                    remaining_meta = _file_row_meta_for_nodeids(
                        filename,
                        remaining,
                        batch_index=batch_index,
                        batch_total=len(batches),
                        batch_size=int(test_batch_size or 0),
                        file_selected=len(group_nodeids),
                    )
                    if timeout_seconds is not None:
                        completed_meta["timeout_seconds"] = timeout_seconds
                        remaining_meta["timeout_seconds"] = timeout_seconds
                    summaries.extend(
                        [
                            {
                                **completed_meta,
                                "returncode": 0,
                                "duration_seconds": elapsed,
                                "timed_out": False,
                                "status": "passed",
                                "checkpoint_reason": "pytest-test-progress",
                                "checkpoint_tests": True,
                            },
                            {
                                **remaining_meta,
                                "returncode": 124,
                                "duration_seconds": elapsed,
                                "timed_out": True,
                                "status": "timed_out",
                                "checkpoint_reason": "timeout-after-pytest-test-progress",
                                "checkpoint_tests": True,
                            },
                        ]
                    )
                    publish(summaries)
                    if tmpdir_obj is not None:
                        tmpdir_obj.cleanup()
                    if final_rc == 0:
                        final_rc = 124
                    continue
            summaries.append(
                {
                    **row_meta,
                    "returncode": int(rc),
                    "duration_seconds": elapsed,
                    "timed_out": int(rc) == 124,
                    "status": status_for_returncode(int(rc)),
                    **({"checkpoint_tests": True} if checkpoint_tests else {}),
                }
            )
            publish(summaries)
            if tmpdir_obj is not None:
                tmpdir_obj.cleanup()
            if rc != 0 and final_rc == 0:
                final_rc = int(rc)
    return final_rc, summaries


def chunk_selection_payload(
    *,
    selected: list[str],
    index: int | None,
    total: int | None,
    strategy: str,
    duration_history: dict[str, float],
) -> dict[str, Any]:
    """Return plain-data evidence for a selected chunk or whole run."""

    first, last = first_last(selected)
    files = [name for name, _group in group_nodeids_by_file(selected)]
    return {
        "selected": len(selected),
        "chunk": {"index": index, "total": total} if index is not None and total is not None else None,
        "strategy": strategy,
        "strategy_weight": round(_nodeid_weight(selected, strategy=strategy, duration_history=duration_history), 3),
        "strategy_weight_unit": _strategy_weight_unit(strategy, duration_history),
        "first": first,
        "last": last,
        "nodeids_digest": nodeids_digest(selected),
        "file_count": len(files),
    }


def previous_chunk_results(manifest: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Return prior all-chunk records keyed by chunk index."""

    out: dict[int, dict[str, Any]] = {}
    records = manifest.get("chunk_results")
    if not isinstance(records, list):
        return out
    for record in records:
        if not isinstance(record, dict):
            continue
        chunk = record.get("chunk")
        if not isinstance(chunk, dict):
            continue
        index = chunk.get("index")
        if isinstance(index, int):
            out[index] = record
    return out


def load_resume_manifest(path: Path) -> dict[str, Any]:
    """Load an existing mxtest aggregate manifest for --resume."""

    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UsageError(f"resume manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise UsageError(f"resume manifest must be a JSON object: {path}")
    return payload


def chunk_resume_match(
    previous: dict[str, Any],
    planned: dict[str, Any],
    *,
    source_digest_matches: bool = True,
    environment_digest_matches: bool = True,
) -> bool:
    """Return True when a previous passed chunk is safe to skip."""

    if previous.get("status") != "passed":
        return False
    return chunk_selection_resume_match(
        previous,
        planned,
        source_digest_matches=source_digest_matches,
        environment_digest_matches=environment_digest_matches,
    )


def chunk_selection_resume_match(
    previous: dict[str, Any],
    planned: dict[str, Any],
    *,
    source_digest_matches: bool = True,
    environment_digest_matches: bool = True,
) -> bool:
    """Return True when previous chunk evidence matches the planned slice.

    Whole-chunk resume additionally requires ``status == passed``.  File-level
    resume uses the same selection/source/environment checks but can harvest
    already-passed file rows from a partial chunk.
    """

    if not source_digest_matches or not environment_digest_matches:
        return False
    for key in ["selected", "strategy", "first", "last", "nodeids_digest"]:
        if previous.get(key) != planned.get(key):
            return False
    prev_chunk = previous.get("chunk")
    plan_chunk = planned.get("chunk")
    if not isinstance(prev_chunk, dict) or not isinstance(plan_chunk, dict):
        return False
    return prev_chunk.get("index") == plan_chunk.get("index") and prev_chunk.get("total") == plan_chunk.get("total")


def resumable_passed_file_rows(previous: dict[str, Any], selected: list[str]) -> list[dict[str, Any]]:
    """Return safe passed file/segment rows from a previous matching partial chunk.

    The caller is responsible for first checking source, environment, and chunk
    selection identity.  This helper then checks each file row against the
    current selected node ids so a stale or malformed row cannot make mxtest
    skip a file segment accidentally.
    """

    previous_files = previous.get("files")
    if not isinstance(previous_files, list):
        return []

    safe_by_span: dict[tuple[int, str, str], dict[str, Any]] = {}
    for row in previous_files:
        if not isinstance(row, dict):
            continue
        filename = row.get("file")
        if not isinstance(filename, str):
            continue
        if row.get("status") != "passed" or row.get("returncode") != 0:
            continue
        row_nodeids = _file_row_nodeids_from_selected(row, selected)
        if not row_nodeids:
            continue
        if row.get("selected") != len(row_nodeids):
            continue
        digest = nodeids_digest(row_nodeids)
        row_digest = row.get("nodeids_digest")
        # New partial-file rows must carry an exact digest.  For old whole-file
        # rows, preserve the rev829/rev0830 fallback when the span is the whole
        # selected file group.
        if isinstance(row_digest, str) and row_digest != digest:
            continue
        if not isinstance(row_digest, str):
            whole_file = [nodeid for nodeid in selected if nodeid.split("::", 1)[0] == filename]
            if row_nodeids != whole_file:
                continue
        copied = dict(row)
        copied.setdefault("nodeids_digest", digest)
        copied.update(nodeid_span_fields(row_nodeids))
        copied["resumed"] = True
        copied["skipped"] = True
        copied["skip_reason"] = "previous-passed-selection-matching-source-dependency-environment-and-nodeids"
        safe_by_span[(selected.index(row_nodeids[0]), filename, digest)] = copied

    return [row for _key, row in sorted(safe_by_span.items(), key=lambda item: item[0])]


def drop_resumed_files(selected: list[str], resumed_file_rows: list[dict[str, Any]]) -> list[str]:
    """Return selected node ids whose exact rows are not covered by resume."""

    resumed_nodeids: set[str] = set()
    for row in resumed_file_rows:
        resumed_nodeids.update(_file_row_nodeids_from_selected(row, selected))
    if not resumed_nodeids:
        return list(selected)
    return [nodeid for nodeid in selected if nodeid not in resumed_nodeids]


def order_file_rows_for_selected(selected: list[str], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return file/segment rows in the same order as the selected node ids.

    File-level resume can combine old passed rows, newly run rows, and budgeted
    ``not_run`` rows.  Keeping the manifest in selection order makes resume
    evidence easier to audit and avoids misleading handoff summaries.
    """

    node_position = {nodeid: index for index, nodeid in enumerate(selected)}
    file_first_position: dict[str, int] = {}
    for index, nodeid in enumerate(selected):
        file_first_position.setdefault(nodeid.split("::", 1)[0], index)

    decorated: list[tuple[int, int, dict[str, Any]]] = []
    fallback_base = len(selected) + len(rows) + 1
    for order, row in enumerate(rows):
        copied = dict(row)
        row_nodeids = _file_row_nodeids_from_selected(copied, selected)
        if row_nodeids:
            position = node_position.get(row_nodeids[0], fallback_base + order)
        else:
            filename = copied.get("file")
            position = file_first_position.get(filename, fallback_base + order) if isinstance(filename, str) else fallback_base + order
        decorated.append((int(position), order, copied))
    return [row for _position, _order, row in sorted(decorated, key=lambda item: (item[0], item[1]))]


def not_run_file_rows_for_nodeids(nodeids: list[str], *, reason: str) -> list[dict[str, Any]]:
    """Return manifest rows for selected file segments intentionally left unrun."""

    return [
        {
            "file": filename,
            "selected": len(group),
            "nodeids_digest": nodeids_digest(group),
            **nodeid_span_fields(group),
            "returncode": None,
            "duration_seconds": 0.0,
            "timed_out": False,
            "status": "not_run",
            "resumed": False,
            "skipped": True,
            "skip_reason": reason,
        }
        for filename, group in group_nodeids_by_file(nodeids)
    ]


def split_nodeids_by_file_budget(
    nodeids: list[str], *, max_new_files: int
) -> tuple[list[str], list[dict[str, Any]], int]:
    """Split selected node ids into runnable and budget-skipped file rows.

    ``max_new_files`` is a per-invocation budget for non-resumed files.  It lets
    cloudtainer sessions make bounded forward progress on a large aggregate
    manifest without risking a long all-or-nothing run.
    """

    budget = max(0, int(max_new_files or 0))
    if budget <= 0:
        return list(nodeids), [], len(group_nodeids_by_file(nodeids))

    groups = group_nodeids_by_file(nodeids)
    run_groups = groups[:budget]
    skipped_groups = groups[budget:]
    runnable = [nodeid for _filename, group in run_groups for nodeid in group]
    skipped_nodeids = [nodeid for _filename, group in skipped_groups for nodeid in group]
    return runnable, not_run_file_rows_for_nodeids(skipped_nodeids, reason="max-new-files-reached"), len(run_groups)


def split_nodeids_by_test_budget(
    nodeids: list[str], *, max_new_tests: int
) -> tuple[list[str], list[dict[str, Any]], int]:
    """Split selected node ids into runnable and budget-skipped test rows.

    Unlike ``--max-new-files``, this can stop inside one large test file.  The
    skipped rows still carry node-id spans and digests, so later ``--resume``
    calls can make forward progress through the same file without rerunning the
    already-passed prefix.
    """

    budget = max(0, int(max_new_tests or 0))
    if budget <= 0:
        return list(nodeids), [], len(nodeids)
    runnable = list(nodeids[:budget])
    skipped = list(nodeids[budget:])
    return runnable, not_run_file_rows_for_nodeids(skipped, reason="max-new-tests-reached"), len(runnable)


def combined_skip_reason(rows: list[dict[str, Any]], *, default: str) -> str:
    """Return a stable combined skip reason for chunk-level summaries."""

    reasons: list[str] = []
    for row in rows:
        reason = row.get("skip_reason")
        if isinstance(reason, str) and reason and reason not in reasons:
            reasons.append(reason)
    if not reasons:
        return default
    return reasons[0] if len(reasons) == 1 else "+".join(reasons)


def interruption_skip_reason(signal_name: str) -> str:
    """Return a stable skip reason for planned work left after a signal."""

    cleaned = str(signal_name or "signal").strip() or "signal"
    return f"{INTERRUPTED_SKIP_REASON_PREFIX}-{cleaned}"


def not_run_chunk_record(
    *,
    selected: list[str],
    index: int,
    total: int,
    strategy: str,
    duration_history: dict[str, float],
    reason: str,
) -> dict[str, Any]:
    """Build a terminal chunk row for planned work intentionally not run."""

    record = chunk_selection_payload(
        selected=selected,
        index=index,
        total=total,
        strategy=strategy,
        duration_history=duration_history,
    )
    record["returncode"] = None
    record["status"] = "not_run"
    record["duration_seconds"] = 0.0
    record["resumed"] = False
    record["skipped"] = True
    record["skip_reason"] = reason
    return record

def aggregate_status(records: list[dict[str, Any]], total: int) -> str:
    """Return a stable aggregate status for an all-chunks run."""

    known_statuses = {"passed", "failed", "timed_out", "partial", "not_run", "running"}
    if len(records) < total:
        return "partial"
    if any(record.get("status") in {"not_run", "partial", "running"} for record in records):
        return "partial"
    if any(record.get("status") not in known_statuses for record in records):
        return "partial"
    if any(record.get("status") == "failed" for record in records):
        return "failed"
    if any(record.get("status") == "timed_out" for record in records):
        return "timed_out"
    return "passed"


def aggregate_complete(records: list[dict[str, Any]], total: int) -> bool:
    """Return True when every planned chunk has a terminal record."""

    terminal = {"passed", "failed", "timed_out"}
    return bool(total and len(records) == total and all(record.get("status") in terminal for record in records))


def aggregate_returncode(records: list[dict[str, Any]], total: int) -> int:
    """Return the process code implied by all chunk records."""

    status = aggregate_status(records, total)
    if status == "passed":
        return 0
    if status == "timed_out":
        return 124
    return 1


def chunk_status_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    """Count stable chunk statuses in an aggregate manifest."""

    counts = {"passed": 0, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 0}
    for record in records:
        status = str(record.get("status", "partial"))
        if status not in counts:
            status = "partial"
        counts[status] += 1
    return counts


def _nonnegative_int(value: object) -> int:
    """Return a non-negative integer count for manifest accounting."""

    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
    return max(0, number)


def _stable_test_status(value: object) -> str:
    """Return the stable status bucket used for selected-test accounting."""

    status = str(value or "partial")
    return status if status in TEST_STATUS_ORDER else "partial"


def aggregate_test_status_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    """Count selected pytest node ids by manifest status.

    Chunk status alone is too coarse for resume-safe handoffs: a partial chunk
    can contain passed file spans, skipped node-id suffixes, and a small failed
    span. Prefer per-file/per-span rows when present, then charge any uncovered
    selected tests to the chunk-level status so older manifests still summarize
    sensibly.
    """

    counts = {status: 0 for status in TEST_STATUS_ORDER}
    for record in records:
        selected = _nonnegative_int(record.get("selected"))
        covered = 0
        files = record.get("files")
        if isinstance(files, list):
            for row in files:
                if not isinstance(row, dict):
                    continue
                row_selected = _nonnegative_int(row.get("selected"))
                counts[_stable_test_status(row.get("status"))] += row_selected
                covered += row_selected
        remainder = selected - covered
        if remainder > 0:
            counts[_stable_test_status(record.get("status"))] += remainder
    return counts


def aggregate_remaining_selected(records: list[dict[str, Any]]) -> int:
    """Return selected pytest node ids not yet represented by passed evidence."""

    counts = aggregate_test_status_counts(records)
    return sum(value for status, value in counts.items() if status != "passed")


def aggregate_manifest_payload(
    *,
    base_payload: dict[str, Any],
    total: int,
    chunks: list[list[str]],
    chunk_results: list[dict[str, Any]],
    started: float,
    complete: bool,
) -> dict[str, Any]:
    """Build the all-chunks JSON manifest payload."""

    payload = dict(base_payload)
    payload["mode"] = "run-chunks"
    payload["run_chunks"] = total
    payload["selected"] = sum(len(chunk) for chunk in chunks)
    payload["chunks"] = [len(chunk) for chunk in chunks]
    payload["chunk_results"] = list(chunk_results)
    payload["chunk_status_counts"] = chunk_status_counts(chunk_results)
    test_status_counts = aggregate_test_status_counts(chunk_results)
    payload["test_status_counts"] = test_status_counts
    payload["passed_selected"] = test_status_counts.get("passed", 0)
    payload["remaining_selected"] = sum(
        value for status, value in test_status_counts.items() if status != "passed"
    )
    payload["complete"] = bool(complete)
    payload["returncode"] = aggregate_returncode(chunk_results, total)
    payload["status"] = aggregate_status(chunk_results, total)
    payload["duration_seconds"] = round(time.monotonic() - started, 3)
    return payload


def run_all_chunks(
    *,
    chunks: list[list[str]],
    strategy: str,
    duration_history: dict[str, float],
    execution_pytest_args: list[str],
    durations: int,
    isolate_files: bool,
    file_timeout: int | None,
    chunk_timeout: int | None,
    json_path: Path | None,
    resume: bool,
    fail_fast: bool,
    max_new_chunks: int,
    max_new_files: int,
    max_new_tests: int,
    test_batch_size: int,
    checkpoint_tests: bool,
    max_runtime_seconds: float,
    base_payload: dict[str, Any],
    started: float,
) -> tuple[int, list[dict[str, Any]], dict[str, Any]]:
    """Run every planned chunk and optionally checkpoint one aggregate manifest."""

    total = len(chunks)
    previous: dict[int, dict[str, Any]] = {}
    resume_manifest: dict[str, Any] = {}
    source_digest_matches = False
    environment_digest_matches = False
    if resume and json_path is not None:
        resume_manifest = load_resume_manifest(json_path)
        previous = previous_chunk_results(resume_manifest)
        previous_source_digest = resume_manifest.get("source_digest")
        current_source_digest = base_payload.get("source_digest")
        source_digest_matches = (
            isinstance(previous_source_digest, str)
            and isinstance(current_source_digest, str)
            and previous_source_digest == current_source_digest
        )
        previous_environment_digest = resume_manifest.get("environment_digest")
        current_environment_digest = base_payload.get("environment_digest")
        environment_digest_matches = (
            isinstance(previous_environment_digest, str)
            and isinstance(current_environment_digest, str)
            and previous_environment_digest == current_environment_digest
        )
        if previous and not source_digest_matches:
            print("mxtest: resume source digest changed or missing; checking chunk source dependencies")
        if previous and not environment_digest_matches:
            print("mxtest: resume environment digest changed or missing; rerunning previous chunks")

    results: list[dict[str, Any]] = []
    stopped = False
    stop_remaining_reason = "fail-fast-after-earlier-nonzero"
    interrupted_returncode: int | None = None
    interrupted_signal: str | None = None
    new_chunks_run = 0
    new_files_run = 0
    new_tests_run = 0
    max_new = max(0, int(max_new_chunks or 0))
    max_new_file_budget = max(0, int(max_new_files or 0))
    max_new_test_budget = max(0, int(max_new_tests or 0))
    runtime_budget = max(0.0, float(max_runtime_seconds or 0.0))

    def runtime_budget_remaining_seconds() -> float:
        return runtime_budget - (time.monotonic() - started) if runtime_budget else 0.0

    def runtime_budget_exhausted() -> bool:
        return bool(runtime_budget and runtime_budget_remaining_seconds() < RUNTIME_BUDGET_MIN_CHILD_SECONDS)

    def child_timeout_with_runtime(configured_timeout: int | None) -> int | None:
        configured = int(configured_timeout) if configured_timeout is not None and int(configured_timeout) > 0 else None
        if not runtime_budget:
            return configured
        remaining = runtime_budget_remaining_seconds()
        runtime_timeout = max(1, int(math.ceil(remaining)))
        return min(configured, runtime_timeout) if configured is not None else runtime_timeout

    for index, selected in enumerate(chunks, start=1):
        planned = chunk_selection_payload(
            selected=selected,
            index=index,
            total=total,
            strategy=strategy,
            duration_history=duration_history,
        )
        planned = attach_source_dependency(planned, base_payload.get("source_manifest"), selected)
        old = previous.get(index)
        source_dependency_matches = bool(source_digest_matches)
        if old is not None:
            source_dependency_matches = chunk_source_dependency_matches(
                old,
                planned,
                previous_manifest=resume_manifest,
                selected=selected,
                fallback_source_digest_matches=source_digest_matches,
            )
        if old is not None and chunk_resume_match(
            old,
            planned,
            source_digest_matches=source_dependency_matches,
            environment_digest_matches=environment_digest_matches,
        ):
            results.append(
                resumed_chunk_record(
                    old,
                    planned,
                    reason="previous-passed-matching-source-dependency-environment-and-chunk",
                )
            )
            print(f"mxtest: chunk {index}/{total} already passed; resumed")
            continue

        if max_new and selected and new_chunks_run >= max_new:
            print(f"mxtest: max-new-chunks reached; marking chunk {index}/{total} not_run")
            record = not_run_chunk_record(
                selected=selected,
                index=index,
                total=total,
                strategy=strategy,
                duration_history=duration_history,
                reason="max-new-chunks-reached",
            )
            results.append(record)
            stopped = True
            stop_remaining_reason = "max-new-chunks-reached"
            break

        if selected and runtime_budget_exhausted():
            print(f"mxtest: max-runtime-seconds reached; marking chunk {index}/{total} not_run")
            record = not_run_chunk_record(
                selected=selected,
                index=index,
                total=total,
                strategy=strategy,
                duration_history=duration_history,
                reason=RUNTIME_BUDGET_SKIP_REASON,
            )
            results.append(record)
            stopped = True
            stop_remaining_reason = RUNTIME_BUDGET_SKIP_REASON
            break

        print(f"mxtest: running chunk {index}/{total} ({len(selected)} tests)")
        if isolate_files:
            print("mxtest: isolating selected files")
        sys.stdout.flush()
        chunk_started = time.monotonic()
        budget_exhausted_after_current = False
        resumed_file_rows: list[dict[str, Any]] = []
        selected_to_run = list(selected)
        if (
            resume
            and isolate_files
            and old is not None
            and chunk_selection_resume_match(
                old,
                planned,
                source_digest_matches=source_dependency_matches,
                environment_digest_matches=environment_digest_matches,
            )
        ):
            resumed_file_rows = resumable_passed_file_rows(old, selected)
            selected_to_run = drop_resumed_files(selected, resumed_file_rows)
            if resumed_file_rows:
                resumed_tests = sum(int(row.get("selected", 0) or 0) for row in resumed_file_rows)
                print(
                    "mxtest: resuming "
                    f"{len(resumed_file_rows)} passed file(s), {resumed_tests} test(s); "
                    f"running {len(selected_to_run)} remaining test(s)"
                )
        skipped_file_rows: list[dict[str, Any]] = []
        scheduled_new_file_count = 0
        scheduled_new_test_count = 0
        if isolate_files and max_new_file_budget and selected_to_run:
            remaining_files = max_new_file_budget - new_files_run
            if remaining_files <= 0:
                skipped_file_rows.extend(not_run_file_rows_for_nodeids(selected_to_run, reason="max-new-files-reached"))
                selected_to_run = []
                print(f"mxtest: max-new-files reached; marking remaining files in chunk {index}/{total} not_run")
            else:
                selected_to_run, file_budget_skipped, scheduled_new_file_count = split_nodeids_by_file_budget(
                    selected_to_run, max_new_files=remaining_files
                )
                skipped_file_rows.extend(file_budget_skipped)
                if file_budget_skipped:
                    skipped_tests = sum(int(row.get("selected", 0) or 0) for row in file_budget_skipped)
                    print(
                        "mxtest: max-new-files budget leaves "
                        f"{len(file_budget_skipped)} file(s), {skipped_tests} test(s) not_run in chunk {index}/{total}"
                    )
        if isolate_files and max_new_test_budget and selected_to_run:
            remaining_tests = max_new_test_budget - new_tests_run
            if remaining_tests <= 0:
                skipped_file_rows.extend(not_run_file_rows_for_nodeids(selected_to_run, reason="max-new-tests-reached"))
                selected_to_run = []
                print(f"mxtest: max-new-tests reached; marking remaining tests in chunk {index}/{total} not_run")
            else:
                selected_to_run, test_budget_skipped, scheduled_new_test_count = split_nodeids_by_test_budget(
                    selected_to_run, max_new_tests=remaining_tests
                )
                skipped_file_rows.extend(test_budget_skipped)
                if test_budget_skipped:
                    skipped_tests = sum(int(row.get("selected", 0) or 0) for row in test_budget_skipped)
                    print(
                        "mxtest: max-new-tests budget leaves "
                        f"{len(test_budget_skipped)} row(s), {skipped_tests} test(s) not_run in chunk {index}/{total}"
                    )
        if isolate_files and selected_to_run:
            if not scheduled_new_file_count:
                scheduled_new_file_count = len(group_nodeids_by_file(selected_to_run))
            if not scheduled_new_test_count:
                scheduled_new_test_count = len(selected_to_run)

        file_summaries: list[dict[str, Any]] = order_file_rows_for_selected(
            selected, [*(dict(row) for row in resumed_file_rows), *(dict(row) for row in skipped_file_rows)]
        )
        record = dict(planned)
        if resumed_file_rows:
            record["resumed_file_count"] = len(resumed_file_rows)
            record["resumed_selected"] = sum(int(row.get("selected", 0) or 0) for row in resumed_file_rows)
        if skipped_file_rows:
            record["skipped_file_count"] = len(skipped_file_rows)
            record["skipped_selected"] = sum(int(row.get("selected", 0) or 0) for row in skipped_file_rows)
        if selected and json_path is not None:
            running_record = dict(record)
            running_record["returncode"] = None
            running_record["status"] = "running"
            running_record["duration_seconds"] = 0.0
            running_record["resumed"] = bool(resumed_file_rows)
            running_record["skipped"] = False
            running_record["checkpoint_reason"] = "chunk-started"
            if file_summaries:
                running_record["files"] = file_summaries
            write_json_summary(
                json_path,
                aggregate_manifest_payload(
                    base_payload=base_payload,
                    total=total,
                    chunks=chunks,
                    chunk_results=[*results, running_record],
                    started=started,
                    complete=False,
                ),
            )
        if not selected:
            print(f"mxtest: chunk {index}/{total} is empty; skipping pytest invocation")
            rc = 0
            record["returncode"] = 0
            record["status"] = "passed"
            record["duration_seconds"] = 0.0
            record["resumed"] = False
            record["skipped"] = True
            record["skip_reason"] = "empty-chunk-selection"
        elif not selected_to_run and skipped_file_rows:
            print(f"mxtest: chunk {index}/{total} has no remaining file/test budget")
            rc = 0
            record["returncode"] = None
            record["status"] = "partial" if resumed_file_rows else "not_run"
            record["duration_seconds"] = round(time.monotonic() - chunk_started, 3)
            record["resumed"] = bool(resumed_file_rows)
            record["skipped"] = not bool(resumed_file_rows)
            record["skip_reason"] = combined_skip_reason(skipped_file_rows, default="max-new-budget-reached")
            record["files"] = file_summaries
            budget_exhausted_after_current = True
        elif not selected_to_run:
            print(f"mxtest: chunk {index}/{total} already has passed file evidence; resumed")
            rc = 0
            record["returncode"] = 0
            record["status"] = "passed"
            record["duration_seconds"] = round(time.monotonic() - chunk_started, 3)
            record["resumed"] = True
            record["skipped"] = True
            record["skip_reason"] = "previous-passed-files-cover-chunk"
            record["files"] = file_summaries
        else:
            new_chunks_run += 1
            if isolate_files:
                new_files_run += scheduled_new_file_count
                new_tests_run += scheduled_new_test_count
            try:
                if isolate_files:
                    def checkpoint_files(rows: list[dict[str, Any]]) -> None:
                        nonlocal file_summaries
                        file_summaries = order_file_rows_for_selected(
                            selected,
                            [
                                *(dict(row) for row in resumed_file_rows),
                                *(dict(row) for row in rows),
                                *(dict(row) for row in skipped_file_rows),
                            ],
                        )
                        if json_path is None:
                            return
                        running_record = dict(record)
                        running_record["returncode"] = None
                        running_record["status"] = "running"
                        running_record["duration_seconds"] = round(time.monotonic() - chunk_started, 3)
                        running_record["resumed"] = bool(resumed_file_rows)
                        running_record["skipped"] = False
                        running_record["checkpoint_reason"] = "file-isolated-progress"
                        running_record["files"] = file_summaries
                        write_json_summary(
                            json_path,
                            aggregate_manifest_payload(
                                base_payload=base_payload,
                                total=total,
                                chunks=chunks,
                                chunk_results=[*results, running_record],
                                started=started,
                                complete=False,
                            ),
                        )

                    isolated_kwargs: dict[str, Any] = {
                        "durations": durations,
                        "file_timeout": file_timeout,
                        "progress": checkpoint_files,
                    }
                    if runtime_budget:
                        isolated_kwargs["stop_requested"] = runtime_budget_exhausted
                        isolated_kwargs["stop_reason"] = RUNTIME_BUDGET_SKIP_REASON
                        isolated_kwargs["child_timeout"] = child_timeout_with_runtime
                    if int(test_batch_size or 0) > 0:
                        isolated_kwargs["test_batch_size"] = int(test_batch_size)
                    if checkpoint_tests:
                        isolated_kwargs["checkpoint_tests"] = True
                    rc, file_summaries = run_pytest_file_isolated(
                        selected_to_run,
                        execution_pytest_args,
                        **isolated_kwargs,
                    )
                    file_summaries = order_file_rows_for_selected(
                        selected,
                        [
                            *(dict(row) for row in resumed_file_rows),
                            *(dict(row) for row in file_summaries),
                            *(dict(row) for row in skipped_file_rows),
                        ],
                    )
                else:
                    rc = run_pytest(
                        selected,
                        execution_pytest_args,
                        durations=durations,
                        timeout=child_timeout_with_runtime(chunk_timeout),
                    )
            except MxtestInterrupted as exc:
                record["returncode"] = int(exc.returncode)
                record["status"] = "partial"
                record["duration_seconds"] = round(time.monotonic() - chunk_started, 3)
                record["resumed"] = bool(resumed_file_rows)
                record["skipped"] = False
                record["interrupted"] = True
                record["signal"] = exc.signal_name
                record["checkpoint_reason"] = "interrupted-during-chunk"
                if file_summaries:
                    record["files"] = file_summaries
                results.append(record)
                interrupted_returncode = int(exc.returncode)
                interrupted_signal = exc.signal_name
                stopped = True
                stop_remaining_reason = interruption_skip_reason(exc.signal_name)
                print(f"mxtest: interrupted by {exc.signal_name}; pytest child cleaned up", file=sys.stderr)
                break
            terminal_not_run_rows = [
                dict(row) for row in file_summaries if str(row.get("status")) == "not_run"
            ]
            if terminal_not_run_rows and int(rc) == 0:
                record["returncode"] = None
                record["status"] = "partial"
                record["skip_reason"] = combined_skip_reason(terminal_not_run_rows, default="max-new-budget-reached")
                budget_exhausted_after_current = True
            else:
                record["returncode"] = int(rc)
                record["status"] = status_for_returncode(int(rc))
            record["duration_seconds"] = round(time.monotonic() - chunk_started, 3)
            record["resumed"] = bool(resumed_file_rows)
            record["skipped"] = False
            if file_summaries:
                record["files"] = file_summaries
        results.append(record)
        if json_path is not None:
            write_json_summary(
                json_path,
                aggregate_manifest_payload(
                    base_payload=base_payload,
                    total=total,
                    chunks=chunks,
                    chunk_results=results,
                    started=started,
                    complete=aggregate_complete(results, total),
                ),
            )
        if budget_exhausted_after_current:
            stopped = True
            stop_remaining_reason = str(record.get("skip_reason") or "max-new-budget-reached")
            break
        if int(rc) != 0 and fail_fast:
            stopped = True
            stop_remaining_reason = "fail-fast-after-earlier-nonzero"
            break
        if runtime_budget_exhausted():
            stopped = True
            stop_remaining_reason = RUNTIME_BUDGET_SKIP_REASON
            break

    if stopped:
        preserve_resumed_remainder = resume and should_preserve_resumed_remainder(stop_remaining_reason)
        for index in range(len(results) + 1, total + 1):
            selected = chunks[index - 1]
            planned = chunk_selection_payload(
                selected=selected,
                index=index,
                total=total,
                strategy=strategy,
                duration_history=duration_history,
            )
            planned = attach_source_dependency(planned, base_payload.get("source_manifest"), selected)
            old = previous.get(index)
            if preserve_resumed_remainder and old is not None:
                source_dependency_matches = bool(source_digest_matches)
                source_dependency_matches = chunk_source_dependency_matches(
                    old,
                    planned,
                    previous_manifest=resume_manifest,
                    selected=selected,
                    fallback_source_digest_matches=source_digest_matches,
                )
                if chunk_resume_match(
                    old,
                    planned,
                    source_digest_matches=source_dependency_matches,
                    environment_digest_matches=environment_digest_matches,
                ):
                    results.append(
                        resumed_chunk_record(
                            old,
                            planned,
                            reason=f"previous-passed-preserved-after-{stop_remaining_reason}",
                        )
                    )
                    continue
            record = not_run_chunk_record(
                selected=selected,
                index=index,
                total=total,
                strategy=strategy,
                duration_history=duration_history,
                reason=stop_remaining_reason,
            )
            results.append(record)

    complete = aggregate_complete(results, total)
    payload = aggregate_manifest_payload(
        base_payload=base_payload,
        total=total,
        chunks=chunks,
        chunk_results=results,
        started=started,
        complete=complete,
    )
    if interrupted_signal is not None:
        payload["interrupted"] = True
        payload["signal"] = interrupted_signal
        payload["process_returncode"] = interrupted_returncode
    if json_path is not None:
        write_json_summary(json_path, payload)
    return int(interrupted_returncode if interrupted_returncode is not None else payload["returncode"]), results, payload



def verify_manifest_payload(payload: dict[str, Any]) -> tuple[int, list[str], list[str]]:
    """Verify an aggregate mxtest manifest without rerunning tests."""

    issues: list[str] = []
    lines: list[str] = []
    if payload.get("mode") != "run-chunks":
        issues.append("mode is not run-chunks")
    run_chunks = payload.get("run_chunks")
    if not isinstance(run_chunks, int) or run_chunks <= 0:
        issues.append("run_chunks must be a positive integer")
        total = 0
    else:
        total = run_chunks
    records_obj = payload.get("chunk_results")
    if not isinstance(records_obj, list):
        issues.append("chunk_results must be a list")
        records: list[dict[str, Any]] = []
    else:
        records = [record for record in records_obj if isinstance(record, dict)]
        if len(records) != len(records_obj):
            issues.append("chunk_results contains non-object entries")
    if total and len(records) > total:
        issues.append(f"chunk_results length {len(records)} exceeds run_chunks {total}")
    elif total and len(records) != total and bool(payload.get("complete")):
        issues.append(f"complete manifest has chunk_results length {len(records)} but run_chunks {total}")
    issues.extend(source_manifest_issues(payload))
    issues.extend(environment_manifest_issues(payload))
    counts = chunk_status_counts(records)
    computed_test_counts = aggregate_test_status_counts(records)
    embedded_test_counts = payload.get("test_status_counts")
    if embedded_test_counts is not None:
        if not isinstance(embedded_test_counts, dict):
            issues.append("test_status_counts must be an object")
        else:
            normalized_embedded = {status: _nonnegative_int(embedded_test_counts.get(status)) for status in TEST_STATUS_ORDER}
            if normalized_embedded != computed_test_counts:
                issues.append(
                    f"test_status_counts {normalized_embedded!r} does not match computed {computed_test_counts!r}"
                )
    computed_status = aggregate_status(records, total) if total else "partial"
    computed_complete = aggregate_complete(records, total)
    if payload.get("status") != computed_status:
        issues.append(f"status {payload.get('status')!r} does not match computed {computed_status!r}")
    if bool(payload.get("complete")) != computed_complete:
        issues.append(f"complete {payload.get('complete')!r} does not match computed {computed_complete!r}")
    if total:
        seen_indexes: set[int] = set()
        for record in records:
            chunk = record.get("chunk")
            if not isinstance(chunk, dict):
                issues.append("chunk result missing chunk object")
                continue
            index = chunk.get("index")
            chunk_total = chunk.get("total")
            if not isinstance(index, int) or index < 1 or index > total:
                issues.append(f"chunk result has invalid index {index!r}")
            else:
                seen_indexes.add(index)
            if chunk_total != total:
                issues.append(f"chunk {index!r} total {chunk_total!r} does not match run_chunks {total}")
            digest = record.get("nodeids_digest")
            if not isinstance(digest, str) or len(digest) != 64:
                issues.append(f"chunk {index!r} is missing a 64-character nodeids_digest")
            for issue in source_dependency_issues(record):
                issues.append(f"chunk {index!r}: {issue}")
        missing = sorted(set(range(1, total + 1)) - seen_indexes)
        if missing and computed_complete:
            issues.append("missing chunk indexes: " + ", ".join(str(i) for i in missing))
    lines.append(f"mxtest manifest: {total} chunk(s)")
    lines.append(f"status: {computed_status}")
    lines.append(f"complete: {str(computed_complete).lower()}")
    lines.append(
        "chunks: "
        + " ".join(f"{name}={counts[name]}" for name in ["passed", "failed", "timed_out", "partial", "not_run"])
    )
    lines.append(
        "tests: "
        + " ".join(f"{name}={computed_test_counts.get(name, 0)}" for name in TEST_STATUS_ORDER)
    )
    if issues:
        lines.append("issues:")
        lines.extend(f"- {issue}" for issue in issues)
        return 2, lines, issues
    return (0 if computed_status == "passed" else 1), lines, issues


def verify_manifest_file(path: Path) -> tuple[int, list[str], list[str]]:
    """Load and verify an mxtest aggregate manifest file."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise UsageError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise UsageError(f"manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise UsageError(f"manifest must be a JSON object: {path}")
    return verify_manifest_payload(payload)


def verify_current_source_payload(
    manifest: dict[str, Any], *, current_source: dict[str, Any] | None = None, manifest_path: Path | None = None
) -> tuple[int, list[str], dict[str, Any]]:
    """Compare a manifest's embedded source attestation with the current tree.

    This is deliberately separate from ``--verify-manifest``.  Plain manifest
    verification is an offline consistency check.  Current-source verification
    reads the working tree but still avoids pytest collection and execution.
    """

    embedded = manifest.get("source_manifest")
    current = current_source if current_source is not None else source_manifest_payload()
    embedded_digest = manifest.get("source_digest")
    current_digest = current.get("digest")
    source_diff = source_manifest_differences(embedded, current)
    partition_diff = source_manifest_partition_differences(embedded, current)
    manifest_issues = source_manifest_issues(manifest)
    missing_embedded = not isinstance(embedded, dict)

    matches = (
        not manifest_issues
        and not missing_embedded
        and isinstance(embedded_digest, str)
        and embedded_digest == current_digest
    )
    issues: list[str] = []
    if missing_embedded:
        issues.append("manifest does not contain an embedded source_manifest")
    if not isinstance(embedded_digest, str):
        issues.append("manifest does not contain a string source_digest")
    elif embedded_digest != current_digest:
        issues.append("manifest source_digest does not match current source digest")
    issues.extend(manifest_issues)

    payload = {
        "mode": "verify-current-source",
        "manifest_path": str(manifest_path) if manifest_path is not None else None,
        "matches_current_source": bool(matches),
        "source_digest": embedded_digest,
        "current_source_digest": current_digest,
        "source_file_count": manifest.get("source_file_count"),
        "current_source_file_count": current.get("file_count"),
        "source_total_bytes": manifest.get("source_total_bytes"),
        "current_source_total_bytes": current.get("total_bytes"),
        "source_differences": source_diff,
        "source_partition_differences": partition_diff,
        "issues": issues,
    }

    lines = [
        "mxtest current-source verification:",
        f"manifest source: {str(embedded_digest)[:12] if isinstance(embedded_digest, str) else embedded_digest}",
        f"current source: {str(current_digest)[:12] if isinstance(current_digest, str) else current_digest}",
        f"matches: {str(matches).lower()}",
    ]
    if source_diff["available"] and (
        source_diff["added_count"] or source_diff["removed_count"] or source_diff["changed_count"]
    ):
        lines.append(
            "source files: "
            + f"added={source_diff['added_count']} "
            + f"removed={source_diff['removed_count']} "
            + f"changed={source_diff['changed_count']}"
        )
        examples = (
            [("added", path) for path in source_diff["added"][:3]]
            + [("removed", path) for path in source_diff["removed"][:3]]
            + [("changed", path) for path in source_diff["changed"][:3]]
        )[:6]
        for label, path in examples:
            lines.append(f"- source {label}: {path}")
    if partition_diff["available"] and (
        partition_diff["added_count"] or partition_diff["removed_count"] or partition_diff["changed_count"]
    ):
        lines.append(
            "source partitions: "
            + f"added={partition_diff['added_count']} "
            + f"removed={partition_diff['removed_count']} "
            + f"changed={partition_diff['changed_count']}"
        )
        examples = (
            [("added", name) for name in partition_diff["added"][:3]]
            + [("removed", name) for name in partition_diff["removed"][:3]]
            + [("changed", name) for name in partition_diff["changed"][:3]]
        )[:6]
        for label, name in examples:
            lines.append(f"- source partition {label}: {name}")
    if issues:
        lines.append("issues:")
        lines.extend(f"- {issue}" for issue in issues)
    structural_issue = bool(missing_embedded or not isinstance(embedded_digest, str) or manifest_issues)
    return (2 if structural_issue else (0 if matches else 1)), lines, payload


def verify_current_source_file(path: Path) -> tuple[int, list[str], dict[str, Any]]:
    """Load a manifest and compare its embedded source manifest to this tree."""

    manifest = load_json_object(path, kind="manifest")
    return verify_current_source_payload(manifest, manifest_path=path)


def verify_current_environment_payload(
    manifest: dict[str, Any], *, current_environment: dict[str, Any] | None = None, manifest_path: Path | None = None
) -> tuple[int, list[str], dict[str, Any]]:
    """Compare a manifest's embedded environment attestation with this host."""

    embedded = manifest.get("environment_manifest")
    current = current_environment if current_environment is not None else environment_manifest_payload()
    embedded_digest = manifest.get("environment_digest")
    current_digest = current.get("digest")
    environment_diff = environment_manifest_differences(embedded, current)
    manifest_issues = environment_manifest_issues(manifest)
    missing_embedded = not isinstance(embedded, dict)

    matches = (
        not manifest_issues
        and not missing_embedded
        and isinstance(embedded_digest, str)
        and embedded_digest == current_digest
    )
    issues: list[str] = []
    if missing_embedded:
        issues.append("manifest does not contain an embedded environment_manifest")
    if not isinstance(embedded_digest, str):
        issues.append("manifest does not contain a string environment_digest")
    elif embedded_digest != current_digest:
        issues.append("manifest environment_digest does not match current environment digest")
    issues.extend(manifest_issues)

    payload = {
        "mode": "verify-current-environment",
        "manifest_path": str(manifest_path) if manifest_path is not None else None,
        "matches_current_environment": bool(matches),
        "environment_digest": embedded_digest,
        "current_environment_digest": current_digest,
        "environment_manifest": embedded if isinstance(embedded, dict) else None,
        "current_environment_manifest": current,
        "environment_differences": environment_diff,
        "issues": issues,
    }

    lines = [
        "mxtest current-environment verification:",
        f"manifest environment: {str(embedded_digest)[:12] if isinstance(embedded_digest, str) else embedded_digest}",
        f"current environment: {str(current_digest)[:12] if isinstance(current_digest, str) else current_digest}",
        f"matches: {str(matches).lower()}",
    ]
    if environment_diff["available"] and (
        environment_diff["added_count"] or environment_diff["removed_count"] or environment_diff["changed_count"]
    ):
        lines.append(
            "environment fields: "
            + f"added={environment_diff['added_count']} "
            + f"removed={environment_diff['removed_count']} "
            + f"changed={environment_diff['changed_count']}"
        )
        examples = (
            [("added", path) for path in environment_diff["added"][:3]]
            + [("removed", path) for path in environment_diff["removed"][:3]]
            + [("changed", path) for path in environment_diff["changed"][:3]]
        )[:6]
        for label, path in examples:
            lines.append(f"- environment {label}: {path}")
    if issues:
        lines.append("issues:")
        lines.extend(f"- {issue}" for issue in issues)
    structural_issue = bool(missing_embedded or not isinstance(embedded_digest, str) or manifest_issues)
    return (2 if structural_issue else (0 if matches else 1)), lines, payload


def verify_current_environment_file(path: Path) -> tuple[int, list[str], dict[str, Any]]:
    """Load a manifest and compare its embedded environment manifest to this host."""

    manifest = load_json_object(path, kind="manifest")
    return verify_current_environment_payload(manifest, manifest_path=path)


def verify_current_manifest_payload(
    manifest: dict[str, Any],
    *,
    current_source: dict[str, Any] | None = None,
    current_environment: dict[str, Any] | None = None,
    manifest_path: Path | None = None,
) -> tuple[int, list[str], dict[str, Any]]:
    """Verify manifest integrity plus current source/environment applicability.

    ``--verify-manifest`` answers whether an aggregate JSON claim is internally
    consistent and whether its status is a full pass.  ``--verify-current-source``
    and ``--verify-current-environment`` answer each drift question separately.
    Handoffs usually need the bundled question: is this manifest structurally
    valid and still safe to resume or trust as current evidence for this
    checkout and host?
    """

    manifest_rc, manifest_lines, manifest_issues = verify_manifest_payload(manifest)
    source_rc, source_lines, source_payload = verify_current_source_payload(
        manifest, current_source=current_source, manifest_path=manifest_path
    )
    environment_rc, environment_lines, environment_payload = verify_current_environment_payload(
        manifest, current_environment=current_environment, manifest_path=manifest_path
    )

    manifest_ok = not manifest_issues
    manifest_passed = manifest_rc == 0
    source_ok = bool(source_payload.get("matches_current_source"))
    environment_ok = bool(environment_payload.get("matches_current_environment"))
    resume_safe = bool(manifest_ok and source_ok and environment_ok)

    issues: list[str] = []
    issues.extend(f"manifest: {issue}" for issue in manifest_issues)
    issues.extend(f"source: {issue}" for issue in source_payload.get("issues", []) if isinstance(issue, str))
    issues.extend(
        f"environment: {issue}"
        for issue in environment_payload.get("issues", [])
        if isinstance(issue, str)
    )

    records_obj = manifest.get("chunk_results")
    records = [record for record in records_obj if isinstance(record, dict)] if isinstance(records_obj, list) else []
    test_counts = _manifest_test_status_counts(manifest, records)
    remaining_selected = sum(value for status, value in test_counts.items() if status != "passed")

    payload = {
        "mode": "verify-current",
        "manifest_path": str(manifest_path) if manifest_path is not None else None,
        "resume_safe": resume_safe,
        "manifest_ok": manifest_ok,
        "manifest_passed": manifest_passed,
        "source_ok": source_ok,
        "environment_ok": environment_ok,
        "manifest_returncode": manifest_rc,
        "source_returncode": source_rc,
        "environment_returncode": environment_rc,
        "manifest_status": manifest.get("status"),
        "manifest_complete": manifest.get("complete"),
        "source_digest": source_payload.get("source_digest"),
        "current_source_digest": source_payload.get("current_source_digest"),
        "environment_digest": environment_payload.get("environment_digest"),
        "current_environment_digest": environment_payload.get("current_environment_digest"),
        "source_differences": source_payload.get("source_differences"),
        "environment_differences": environment_payload.get("environment_differences"),
        "test_status_counts": test_counts,
        "remaining_selected": remaining_selected,
        "issues": issues,
        "manifest_lines": manifest_lines,
        "source_lines": source_lines,
        "environment_lines": environment_lines,
    }

    lines = [
        "mxtest current-manifest verification:",
        f"manifest: {'ok' if manifest_ok else 'not-ok'}",
        f"manifest-passed: {str(manifest_passed).lower()}",
        f"source: {'ok' if source_ok else 'not-ok'}",
        f"environment: {'ok' if environment_ok else 'not-ok'}",
        f"resume-safe: {str(resume_safe).lower()}",
    ]
    if test_counts:
        lines.append(
            "test progress: "
            + " ".join(f"{name}={test_counts.get(name, 0)}" for name in TEST_STATUS_ORDER)
            + f" remaining={remaining_selected}"
        )
    source_diff = source_payload.get("source_differences")
    if isinstance(source_diff, dict) and (
        source_diff.get("added_count") or source_diff.get("removed_count") or source_diff.get("changed_count")
    ):
        lines.append(
            "source files: "
            + f"added={source_diff.get('added_count')} "
            + f"removed={source_diff.get('removed_count')} "
            + f"changed={source_diff.get('changed_count')}"
        )
    environment_diff = environment_payload.get("environment_differences")
    if isinstance(environment_diff, dict) and (
        environment_diff.get("added_count")
        or environment_diff.get("removed_count")
        or environment_diff.get("changed_count")
    ):
        lines.append(
            "environment fields: "
            + f"added={environment_diff.get('added_count')} "
            + f"removed={environment_diff.get('removed_count')} "
            + f"changed={environment_diff.get('changed_count')}"
        )
    if issues:
        lines.append("issues:")
        lines.extend(f"- {issue}" for issue in issues)

    if manifest_rc == 2 or source_rc == 2 or environment_rc == 2:
        return 2, lines, payload
    return (0 if resume_safe else 1), lines, payload


def verify_current_manifest_file(path: Path) -> tuple[int, list[str], dict[str, Any]]:
    """Load a manifest and verify integrity plus current source/environment."""

    manifest = load_json_object(path, kind="manifest")
    return verify_current_manifest_payload(manifest, manifest_path=path)



def _duration_or_none(value: object) -> float | None:
    """Return a rounded non-negative duration or None."""

    duration = _duration_value(value)
    if duration is None:
        return None
    return round(duration, 3)


def _short_digest(value: object) -> object:
    """Return a human-sized digest preview while preserving non-string evidence."""

    if isinstance(value, str) and len(value) > 12:
        return value[:12]
    return value


def _summary_chunk_rows(records: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    """Return the slowest chunk rows from an aggregate manifest."""

    rows: list[dict[str, Any]] = []
    for record in records:
        duration = _duration_or_none(record.get("duration_seconds"))
        if duration is None:
            continue
        chunk = record.get("chunk") if isinstance(record.get("chunk"), dict) else {}
        files_obj = record.get("files")
        if isinstance(files_obj, list):
            file_count = len(files_obj)
        else:
            file_count = record.get("file_count")
        rows.append(
            {
                "index": chunk.get("index") if isinstance(chunk, dict) else None,
                "total": chunk.get("total") if isinstance(chunk, dict) else None,
                "status": record.get("status"),
                "returncode": record.get("returncode"),
                "selected": record.get("selected"),
                "duration_seconds": duration,
                "file_count": file_count,
                "resumed": bool(record.get("resumed")),
                "skipped": bool(record.get("skipped")),
                "resumed_file_count": record.get("resumed_file_count"),
                "resumed_selected": record.get("resumed_selected"),
                "skipped_file_count": record.get("skipped_file_count"),
                "skipped_selected": record.get("skipped_selected"),
                "first": record.get("first"),
                "last": record.get("last"),
                "nodeids_digest": record.get("nodeids_digest"),
            }
        )
    rows.sort(key=lambda row: (-(row["duration_seconds"] or 0.0), int(row.get("index") or 0)))
    return rows[: max(0, int(limit))]


def _summary_incomplete_chunk_rows(records: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    """Return the earliest non-passed chunk rows from an aggregate manifest."""

    rows: list[dict[str, Any]] = []
    for record in records:
        status = str(record.get("status") or "")
        if status == "passed":
            continue
        chunk = record.get("chunk") if isinstance(record.get("chunk"), dict) else {}
        files_obj = record.get("files")
        file_counts: dict[str, int] = {}
        if isinstance(files_obj, list):
            for row in files_obj:
                if not isinstance(row, dict):
                    continue
                file_status = str(row.get("status") or "unknown")
                file_counts[file_status] = file_counts.get(file_status, 0) + 1
            file_count = len(files_obj)
        else:
            file_count = record.get("file_count")
        rows.append(
            {
                "index": chunk.get("index") if isinstance(chunk, dict) else None,
                "total": chunk.get("total") if isinstance(chunk, dict) else None,
                "status": record.get("status"),
                "returncode": record.get("returncode"),
                "selected": record.get("selected"),
                "file_count": file_count,
                "file_status_counts": file_counts,
                "skip_reason": record.get("skip_reason"),
                "first": record.get("first"),
                "last": record.get("last"),
                "nodeids_digest": record.get("nodeids_digest"),
            }
        )
    rows.sort(key=lambda row: (row.get("index") is None, int(row.get("index") or 0)))
    return rows[: max(0, int(limit))]


def _short_summary_nodeid(value: object, *, limit: int = 96) -> str:
    """Return a compact node-id string for human manifest summaries."""

    if not isinstance(value, str) or not value:
        return ""
    text = value
    cap = max(8, int(limit))
    return text if len(text) <= cap else text[: cap - 3] + "..."


def _summary_file_rows(payload: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
    """Return the slowest isolated-file rows from a run or aggregate manifest."""

    rows: list[dict[str, Any]] = []

    def add_files(value: object, *, chunk: dict[str, Any] | None = None) -> None:
        if not isinstance(value, list):
            return
        for record in value:
            if not isinstance(record, dict):
                continue
            duration = _duration_or_none(record.get("duration_seconds"))
            filename = record.get("file")
            if duration is None or not isinstance(filename, str):
                continue
            rows.append(
                {
                    "file": filename,
                    "status": record.get("status"),
                    "returncode": record.get("returncode"),
                    "selected": record.get("selected"),
                    "duration_seconds": duration,
                    "timed_out": bool(record.get("timed_out")),
                    "resumed": bool(record.get("resumed")),
                    "skipped": bool(record.get("skipped")),
                    "skip_reason": record.get("skip_reason"),
                    "batch_index": record.get("batch_index"),
                    "batch_total": record.get("batch_total"),
                    "batch_size": record.get("batch_size"),
                    "file_selected": record.get("file_selected"),
                    "nodeid_first": record.get("nodeid_first"),
                    "nodeid_last": record.get("nodeid_last"),
                    "nodeids_digest": record.get("nodeids_digest"),
                    "chunk_index": chunk.get("index") if isinstance(chunk, dict) else None,
                    "chunk_total": chunk.get("total") if isinstance(chunk, dict) else None,
                }
            )

    add_files(payload.get("files"))
    chunk_results = payload.get("chunk_results")
    if isinstance(chunk_results, list):
        for chunk_record in chunk_results:
            if isinstance(chunk_record, dict):
                chunk = chunk_record.get("chunk") if isinstance(chunk_record.get("chunk"), dict) else None
                add_files(chunk_record.get("files"), chunk=chunk)
    rows.sort(key=lambda row: (-(row["duration_seconds"] or 0.0), str(row.get("file") or "")))
    return rows[: max(0, int(limit))]


def _manifest_status_counts(payload: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, int]:
    """Return status counts from records, falling back to embedded aggregate counts."""

    if records:
        return chunk_status_counts(records)
    counts = payload.get("chunk_status_counts")
    if isinstance(counts, dict):
        out: dict[str, int] = {}
        for key, value in counts.items():
            try:
                out[str(key)] = int(value)
            except (TypeError, ValueError):
                continue
        return out
    return {}


def _manifest_test_status_counts(payload: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, int]:
    """Return selected-test status counts from rows or embedded aggregate counts."""

    if records:
        return aggregate_test_status_counts(records)
    counts = payload.get("test_status_counts")
    if isinstance(counts, dict):
        return {status: _nonnegative_int(counts.get(status)) for status in TEST_STATUS_ORDER}
    return {status: 0 for status in TEST_STATUS_ORDER}


def manifest_summary_payload(
    payload: dict[str, Any], *, source_path: Path | None = None, slowest: int = 5
) -> tuple[int, list[str], dict[str, Any]]:
    """Summarize an mxtest manifest without collecting or running tests."""

    limit = max(0, int(slowest))
    chunk_results_obj = payload.get("chunk_results")
    records = [record for record in chunk_results_obj if isinstance(record, dict)] if isinstance(chunk_results_obj, list) else []
    counts = _manifest_status_counts(payload, records)
    test_counts = _manifest_test_status_counts(payload, records)
    remaining_selected = sum(value for status, value in test_counts.items() if status != "passed")
    slowest_chunks = _summary_chunk_rows(records, limit=limit)
    slowest_files = _summary_file_rows(payload, limit=limit)
    incomplete_chunk_count = sum(1 for record in records if str(record.get("status") or "") != "passed")
    next_incomplete_chunks = _summary_incomplete_chunk_rows(records, limit=limit)
    environment = payload.get("environment_manifest") if isinstance(payload.get("environment_manifest"), dict) else {}
    python_payload = environment.get("python") if isinstance(environment, dict) and isinstance(environment.get("python"), dict) else {}
    pytest_payload = environment.get("pytest") if isinstance(environment, dict) and isinstance(environment.get("pytest"), dict) else {}
    duration = _duration_or_none(payload.get("duration_seconds"))
    manifest_issues: list[str] = []
    manifest_returncode: int | None = None
    if payload.get("mode") == "run-chunks":
        verify_rc, _verify_lines, manifest_issues = verify_manifest_payload(payload)
        manifest_returncode = int(verify_rc)

    result = {
        "mode": "manifest-summary",
        "source_path": str(source_path) if source_path is not None else None,
        "manifest_mode": payload.get("mode"),
        "status": payload.get("status"),
        "complete": payload.get("complete"),
        "returncode": payload.get("returncode"),
        "manifest_returncode": manifest_returncode,
        "collected": payload.get("collected"),
        "selected": payload.get("selected"),
        "run_chunks": payload.get("run_chunks"),
        "strategy": payload.get("strategy"),
        "duration_seconds": duration,
        "chunk_status_counts": counts,
        "test_status_counts": test_counts,
        "passed_selected": test_counts.get("passed", 0),
        "remaining_selected": remaining_selected,
        "source_digest": payload.get("source_digest"),
        "source_digest_short": _short_digest(payload.get("source_digest")),
        "source_file_count": payload.get("source_file_count"),
        "source_total_bytes": payload.get("source_total_bytes"),
        "environment_digest": payload.get("environment_digest"),
        "environment_digest_short": _short_digest(payload.get("environment_digest")),
        "python_version": python_payload.get("version") if isinstance(python_payload, dict) else None,
        "pytest_version": pytest_payload.get("version") if isinstance(pytest_payload, dict) else None,
        "slowest_limit": limit,
        "slowest_chunks": slowest_chunks,
        "slowest_files": slowest_files,
        "next_incomplete_count": incomplete_chunk_count,
        "next_incomplete_chunks": next_incomplete_chunks,
        "manifest_issues": manifest_issues,
    }

    lines = ["mxtest manifest summary:"]
    lines.append(
        "status: "
        + f"{payload.get('status')} complete={str(payload.get('complete')).lower()} "
        + f"returncode={payload.get('returncode')}"
    )
    lines.append(
        "selection: "
        + f"collected={payload.get('collected')} selected={payload.get('selected')} "
        + f"chunks={payload.get('run_chunks')} strategy={payload.get('strategy')}"
    )
    if duration is not None:
        lines.append(f"duration: {duration:.3f}s")
    if counts:
        ordered = ["passed", "failed", "timed_out", "partial", "not_run"]
        extras = sorted(key for key in counts if key not in ordered)
        parts = [f"{name}={counts.get(name, 0)}" for name in ordered if name in counts]
        parts.extend(f"{name}={counts[name]}" for name in extras)
        lines.append("chunk statuses: " + " ".join(parts))
    if test_counts:
        lines.append(
            "test progress: "
            + " ".join(f"{name}={test_counts.get(name, 0)}" for name in TEST_STATUS_ORDER)
            + f" remaining={remaining_selected}"
        )
    lines.append(
        "source: "
        + f"{_short_digest(payload.get('source_digest'))} "
        + f"files={payload.get('source_file_count')} bytes={payload.get('source_total_bytes')}"
    )
    lines.append(
        "environment: "
        + f"{_short_digest(payload.get('environment_digest'))} "
        + f"python={result['python_version']} pytest={result['pytest_version']}"
    )
    if next_incomplete_chunks:
        lines.append(
            f"next incomplete chunks (top {len(next_incomplete_chunks)} of {incomplete_chunk_count}):"
        )
        for row in next_incomplete_chunks:
            index = row.get("index")
            total = row.get("total")
            label = f"{index}/{total}" if index is not None and total is not None else "?/?"
            file_counts = row.get("file_status_counts") if isinstance(row.get("file_status_counts"), dict) else {}
            file_count_text = ""
            if file_counts:
                ordered = ["passed", "failed", "timed_out", "partial", "not_run", "running"]
                parts = [f"{name}={file_counts.get(name, 0)}" for name in ordered if file_counts.get(name, 0)]
                parts.extend(
                    f"{name}={file_counts[name]}" for name in sorted(file_counts) if name not in ordered
                )
                file_count_text = " files[" + " ".join(parts) + "]"
            reason = row.get("skip_reason")
            reason_text = f" reason={reason}" if isinstance(reason, str) and reason else ""
            first = _short_summary_nodeid(row.get("first"))
            first_text = f" first={first}" if first else ""
            lines.append(
                f"- chunk {label}: status={row.get('status')} selected={row.get('selected')}"
                f"{reason_text}{file_count_text}{first_text}"
            )
    if slowest_chunks:
        lines.append(f"slowest chunks (top {len(slowest_chunks)}):")
        for row in slowest_chunks:
            index = row.get("index")
            total = row.get("total")
            label = f"{index}/{total}" if index is not None and total is not None else "?/?"
            flags = []
            if row.get("resumed"):
                flags.append("resumed")
            if row.get("skipped") and not row.get("resumed"):
                flags.append("skipped")
            resumed_file_count = row.get("resumed_file_count")
            if isinstance(resumed_file_count, int) and resumed_file_count > 0:
                flags.append(f"resumed_files={resumed_file_count}")
            skipped_file_count = row.get("skipped_file_count")
            if isinstance(skipped_file_count, int) and skipped_file_count > 0:
                flags.append(f"skipped_files={skipped_file_count}")
            suffix = f" {' '.join(flags)}" if flags else ""
            lines.append(
                f"- chunk {label}: {row['duration_seconds']:.3f}s "
                f"status={row.get('status')} selected={row.get('selected')}{suffix}"
            )
    if slowest_files:
        lines.append(f"slowest file/test spans (top {len(slowest_files)}):")
        for row in slowest_files:
            chunk_index = row.get("chunk_index")
            chunk_total = row.get("chunk_total")
            prefix = f"chunk {chunk_index}/{chunk_total} " if chunk_index is not None and chunk_total is not None else ""
            flags = []
            batch_index = row.get("batch_index")
            batch_total = row.get("batch_total")
            if isinstance(batch_index, int) and isinstance(batch_total, int) and batch_total > 1:
                flags.append(f"batch={batch_index}/{batch_total}")
            if row.get("resumed"):
                flags.append("resumed")
            if row.get("skipped") and not row.get("resumed"):
                flags.append("skipped")
            skip_reason = row.get("skip_reason")
            if isinstance(skip_reason, str) and skip_reason and not row.get("resumed"):
                flags.append(skip_reason)
            suffix = f" {' '.join(flags)}" if flags else ""
            lines.append(
                f"- {prefix}{row.get('file')}: {row['duration_seconds']:.3f}s "
                f"status={row.get('status')} selected={row.get('selected')}{suffix}"
            )
    if manifest_issues:
        lines.append("manifest issues:")
        lines.extend(f"- {issue}" for issue in manifest_issues[:10])
        if len(manifest_issues) > 10:
            lines.append(f"... {len(manifest_issues) - 10} more issue(s)")
    return 0, lines, result


def manifest_summary_file(path: Path, *, slowest: int) -> tuple[int, list[str], dict[str, Any]]:
    """Load an mxtest JSON manifest and return a compact summary."""

    payload = load_json_object(path, kind="manifest")
    return manifest_summary_payload(payload, source_path=path, slowest=slowest)


def emit_lines_and_json(rc: int, lines: list[str], payload: dict[str, Any], json_path: str) -> int:
    """Emit no-run command output and optional JSON through one audited path."""

    if json_path:
        write_json_summary(Path(json_path), payload)
    for line in lines:
        print(line)
    return int(rc)

def emit_manifest_handoff_summary(
    payload: dict[str, Any],
    *,
    source_path: Path | None = None,
    slowest: int = 5,
) -> dict[str, Any]:
    """Print and return the compact manifest-first handoff summary for a run."""

    _rc, lines, summary_payload = manifest_summary_payload(payload, source_path=source_path, slowest=slowest)
    print("mxtest: manifest-first handoff summary")
    if source_path is not None:
        print(f"mxtest: manifest {source_path}")
    for line in lines:
        print(line)
    return summary_payload

def load_json_object(path: Path, *, kind: str) -> dict[str, Any]:
    """Load a JSON object with a user-facing error label."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise UsageError(f"{kind} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise UsageError(f"{kind} is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise UsageError(f"{kind} must be a JSON object: {path}")
    return payload


def _chunk_map(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    records = payload.get("chunk_results")
    if not isinstance(records, list):
        return out
    for record in records:
        if not isinstance(record, dict):
            continue
        chunk = record.get("chunk")
        if not isinstance(chunk, dict):
            continue
        index = chunk.get("index")
        if isinstance(index, int):
            out[index] = record
    return out


def diff_manifest_payloads(old: dict[str, Any], new: dict[str, Any]) -> tuple[int, list[str], dict[str, Any]]:
    """Compare two mxtest manifests and return CLI lines plus JSON evidence."""

    differences: list[dict[str, Any]] = []

    def add(kind: str, field: str, old_value: object, new_value: object, *, detail: str = "") -> None:
        item: dict[str, Any] = {"kind": kind, "field": field, "old": old_value, "new": new_value}
        if detail:
            item["detail"] = detail
        differences.append(item)

    for field in [
        "mode",
        "collected",
        "selected",
        "strategy",
        "run_chunks",
        "nodeids_digest",
        "source_digest",
        "environment_digest",
        "status",
        "complete",
        "chunk_status_counts",
    ]:
        if old.get(field) != new.get(field):
            add("summary", field, old.get(field), new.get(field))
    if old.get("chunks") != new.get("chunks"):
        add("summary", "chunks", old.get("chunks"), new.get("chunks"))

    old_chunks = _chunk_map(old)
    new_chunks = _chunk_map(new)
    for index in sorted(set(old_chunks) - set(new_chunks)):
        add("chunk", f"chunk[{index}]", old_chunks[index].get("nodeids_digest"), None, detail="removed")
    for index in sorted(set(new_chunks) - set(old_chunks)):
        add("chunk", f"chunk[{index}]", None, new_chunks[index].get("nodeids_digest"), detail="added")
    for index in sorted(set(old_chunks) & set(new_chunks)):
        old_record = old_chunks[index]
        new_record = new_chunks[index]
        for field in ["selected", "strategy", "first", "last", "nodeids_digest", "status", "returncode"]:
            if old_record.get(field) != new_record.get(field):
                add("chunk", f"chunk[{index}].{field}", old_record.get(field), new_record.get(field))

    source_diff = source_manifest_differences(old.get("source_manifest"), new.get("source_manifest"))
    source_partition_diff = source_manifest_partition_differences(old.get("source_manifest"), new.get("source_manifest"))
    if source_diff["available"] and (
        source_diff["added_count"] or source_diff["removed_count"] or source_diff["changed_count"]
    ):
        detail = (
            f"added={source_diff['added_count']} "
            f"removed={source_diff['removed_count']} "
            f"changed={source_diff['changed_count']}"
        )
        add("source", "source_files", old.get("source_digest"), new.get("source_digest"), detail=detail)

    environment_diff = environment_manifest_differences(old.get("environment_manifest"), new.get("environment_manifest"))
    if environment_diff["available"] and (
        environment_diff["added_count"] or environment_diff["removed_count"] or environment_diff["changed_count"]
    ):
        detail = (
            f"added={environment_diff['added_count']} "
            f"removed={environment_diff['removed_count']} "
            f"changed={environment_diff['changed_count']}"
        )
        add("environment", "environment_fields", old.get("environment_digest"), new.get("environment_digest"), detail=detail)

    payload = {
        "mode": "diff-manifests",
        "differences": differences,
        "difference_count": len(differences),
        "same": not differences,
        "old": {
            "status": old.get("status"),
            "complete": old.get("complete"),
            "collected": old.get("collected"),
            "run_chunks": old.get("run_chunks"),
            "nodeids_digest": old.get("nodeids_digest"),
            "source_digest": old.get("source_digest"),
            "environment_digest": old.get("environment_digest"),
        },
        "new": {
            "status": new.get("status"),
            "complete": new.get("complete"),
            "collected": new.get("collected"),
            "run_chunks": new.get("run_chunks"),
            "nodeids_digest": new.get("nodeids_digest"),
            "source_digest": new.get("source_digest"),
            "environment_digest": new.get("environment_digest"),
        },
        "source_differences": source_diff,
        "source_partition_differences": source_partition_diff,
        "environment_differences": environment_diff,
    }
    lines = [f"mxtest manifest diff: {len(differences)} difference(s)"]
    lines.append(
        "old: "
        + f"status={old.get('status')} complete={old.get('complete')} "
        + f"collected={old.get('collected')} chunks={old.get('run_chunks')}"
    )
    lines.append(
        "new: "
        + f"status={new.get('status')} complete={new.get('complete')} "
        + f"collected={new.get('collected')} chunks={new.get('run_chunks')}"
    )
    if source_diff["available"] and (
        source_diff["added_count"] or source_diff["removed_count"] or source_diff["changed_count"]
    ):
        lines.append(
            "source files: "
            + f"added={source_diff['added_count']} "
            + f"removed={source_diff['removed_count']} "
            + f"changed={source_diff['changed_count']}"
        )
        examples = (
            [("added", path) for path in source_diff["added"][:3]]
            + [("removed", path) for path in source_diff["removed"][:3]]
            + [("changed", path) for path in source_diff["changed"][:3]]
        )[:6]
        for label, path in examples:
            lines.append(f"- source {label}: {path}")
    if source_partition_diff["available"] and (
        source_partition_diff["added_count"]
        or source_partition_diff["removed_count"]
        or source_partition_diff["changed_count"]
    ):
        lines.append(
            "source partitions: "
            + f"added={source_partition_diff['added_count']} "
            + f"removed={source_partition_diff['removed_count']} "
            + f"changed={source_partition_diff['changed_count']}"
        )
        examples = (
            [("added", name) for name in source_partition_diff["added"][:3]]
            + [("removed", name) for name in source_partition_diff["removed"][:3]]
            + [("changed", name) for name in source_partition_diff["changed"][:3]]
        )[:6]
        for label, name in examples:
            lines.append(f"- source partition {label}: {name}")
    if environment_diff["available"] and (
        environment_diff["added_count"] or environment_diff["removed_count"] or environment_diff["changed_count"]
    ):
        lines.append(
            "environment fields: "
            + f"added={environment_diff['added_count']} "
            + f"removed={environment_diff['removed_count']} "
            + f"changed={environment_diff['changed_count']}"
        )
        examples = (
            [("added", path) for path in environment_diff["added"][:3]]
            + [("removed", path) for path in environment_diff["removed"][:3]]
            + [("changed", path) for path in environment_diff["changed"][:3]]
        )[:6]
        for label, path in examples:
            lines.append(f"- environment {label}: {path}")
    for difference in differences[:20]:
        detail = difference.get("detail")
        suffix = f" ({detail})" if detail else ""
        lines.append(f"- {difference['field']}{suffix}: {difference.get('old')!r} -> {difference.get('new')!r}")
    if len(differences) > 20:
        lines.append(f"... {len(differences) - 20} more difference(s)")
    return (1 if differences else 0), lines, payload


def diff_manifest_files(old_path: Path, new_path: Path) -> tuple[int, list[str], dict[str, Any]]:
    """Load and compare two mxtest manifest files."""

    old = load_json_object(old_path, kind="old manifest")
    new = load_json_object(new_path, kind="new manifest")
    rc, lines, payload = diff_manifest_payloads(old, new)
    payload["old_path"] = str(old_path)
    payload["new_path"] = str(new_path)
    return rc, lines, payload


def _safe_positive_int(value: int, *, fallback: int) -> int:
    return int(value) if int(value) > 0 else fallback


def recommend_chunks_payload(
    payload: dict[str, Any],
    *,
    source_path: Path | None,
    target_seconds: float,
    min_chunks: int,
    max_chunks: int,
) -> tuple[int, list[str], dict[str, Any]]:
    """Recommend a future chunk count from an aggregate run manifest."""

    if target_seconds <= 0:
        raise UsageError("target seconds must be greater than zero")
    min_chunks = _safe_positive_int(min_chunks, fallback=1)
    max_chunks = _safe_positive_int(max_chunks, fallback=max(1, min_chunks))
    if max_chunks < min_chunks:
        raise UsageError("max chunks must be greater than or equal to min chunks")

    records_obj = payload.get("chunk_results")
    if not isinstance(records_obj, list):
        raise UsageError("manifest does not contain chunk_results")
    durations: list[float] = []
    statuses: list[str] = []
    for record in records_obj:
        if not isinstance(record, dict):
            continue
        duration = _duration_value(record.get("duration_seconds"))
        status = str(record.get("status", "partial"))
        if duration is not None and status != "not_run":
            durations.append(duration)
            statuses.append(status)
    if not durations:
        raise UsageError("manifest does not contain completed chunk durations")

    observed_chunks = len(durations)
    observed_total = sum(durations)
    slowest = max(durations)
    average = observed_total / observed_chunks if observed_chunks else 0.0
    by_total = max(1, math.ceil(observed_total / target_seconds))
    recommended = max(min_chunks, by_total)
    notes: list[str] = []
    if slowest > target_seconds and recommended <= observed_chunks:
        recommended = observed_chunks + 1
        notes.append("slowest chunk exceeded target; increasing chunk count can expose a finer split")
    recommended = min(max_chunks, max(min_chunks, recommended))
    if recommended == max_chunks and by_total > max_chunks:
        notes.append("recommendation was capped by max_chunks")

    strategy = str(payload.get("strategy") or "segment")
    recommended_strategy = strategy
    history_files = {
        str(record.get("file"))
        for record in file_duration_records(payload)
        if isinstance(record.get("file"), str)
    }
    history_file_count = len(history_files)
    if history_file_count and strategy != "duration":
        recommended_strategy = "duration"
        notes.append("manifest includes per-file durations; use it as --history with duration strategy")
    elif not history_file_count:
        notes.append("no per-file duration rows found; recommendation uses chunk durations only")

    source = str(source_path) if source_path is not None else "MANIFEST"
    command_parts = [
        "python",
        "tools/mxtest.py",
        "--run-chunks",
        str(recommended),
        "--strategy",
        recommended_strategy,
        "--isolate-files",
        "--resume",
        "--json",
        ".artifacts/mxtest-all.json",
    ]
    if recommended_strategy == "duration":
        command_parts.extend(["--history", source])
    command = " ".join(shlex.quote(part) for part in command_parts)

    result = {
        "mode": "recommend-chunks",
        "source_path": str(source_path) if source_path is not None else None,
        "source_status": payload.get("status"),
        "source_complete": payload.get("complete"),
        "observed_chunks": observed_chunks,
        "observed_total_seconds": round(observed_total, 3),
        "observed_average_chunk_seconds": round(average, 3),
        "observed_slowest_chunk_seconds": round(slowest, 3),
        "target_seconds": float(target_seconds),
        "min_chunks": min_chunks,
        "max_chunks": max_chunks,
        "recommended_chunks": recommended,
        "current_strategy": strategy,
        "recommended_strategy": recommended_strategy,
        "history_file_count": history_file_count,
        "status_counts": {status: statuses.count(status) for status in sorted(set(statuses))},
        "command": command,
        "notes": notes,
    }
    lines = [
        f"mxtest recommendation: {recommended} chunk(s) using {recommended_strategy} strategy",
        f"observed: chunks={observed_chunks} total={observed_total:.3f}s average={average:.3f}s slowest={slowest:.3f}s",
        f"target: {float(target_seconds):.3f}s per chunk",
        f"command: {command}",
    ]
    lines.extend(f"note: {note}" for note in notes)
    return 0, lines, result


def recommend_chunks_file(
    path: Path, *, target_seconds: float, min_chunks: int, max_chunks: int
) -> tuple[int, list[str], dict[str, Any]]:
    """Load an aggregate manifest and recommend a future chunk count."""

    payload = load_json_object(path, kind="manifest")
    return recommend_chunks_payload(
        payload,
        source_path=path,
        target_seconds=target_seconds,
        min_chunks=min_chunks,
        max_chunks=max_chunks,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect and run Micromax pytest slices deterministically.")
    parser.add_argument("--plan", action="store_true", help="collect tests and print counts without running them")
    parser.add_argument("--chunks", type=int, default=0, help="with --plan, print balanced counts for this many chunks")
    parser.add_argument("--chunk", default="", help="run one balanced chunk using INDEX/TOTAL syntax, for example 1/8")
    parser.add_argument("--run-chunks", type=int, default=0, help="run every chunk sequentially and write one aggregate manifest")
    parser.add_argument("--resume", action="store_true", help="with --run-chunks and --json, skip matching passed chunks from an existing manifest")
    parser.add_argument("--fail-fast", action="store_true", help="with --run-chunks, stop after the first non-zero chunk")
    parser.add_argument("--max-new-chunks", type=int, default=0, help="with --run-chunks, run at most this many non-resumed chunks and mark the rest not_run")
    parser.add_argument("--max-new-files", type=int, default=0, help="with --run-chunks --isolate-files, run at most this many non-resumed files and mark the rest not_run")
    parser.add_argument("--max-new-tests", type=int, default=0, help="with --run-chunks --isolate-files, run at most this many non-resumed tests and mark the rest not_run")
    parser.add_argument("--test-batch-size", type=int, default=0, help="with --isolate-files, split each selected file into pytest subprocess batches of at most this many node ids")
    parser.add_argument("--checkpoint-tests", action="store_true", help="with --isolate-files, record per-test progress from pytest children so interrupted batches can resume completed prefixes")
    parser.add_argument("--max-runtime-seconds", type=float, default=0.0, help="with --run-chunks, stop gracefully after this wall-clock budget and mark remaining chunks/tests not_run")
    parser.add_argument("--verify-manifest", default="", help="verify an aggregate mxtest JSON manifest without running tests")
    parser.add_argument(
        "--verify-current-source",
        default="",
        help="compare a manifest's embedded source attestation with the current tree without collecting tests",
    )
    parser.add_argument(
        "--verify-current-environment",
        default="",
        help="compare a manifest's embedded environment attestation with this host without collecting tests",
    )
    parser.add_argument(
        "--verify-current",
        default="",
        help="verify a manifest plus current source/environment applicability without collecting tests",
    )
    parser.add_argument(
        "--manifest-summary",
        default="",
        help="print a compact manifest status/digest/slowest-row summary without collecting tests",
    )
    parser.add_argument("--summary-limit", type=int, default=5, help="number of slowest chunks/files to show in manifest summaries")
    parser.add_argument(
        "--no-run-summary",
        action="store_true",
        help="suppress the automatic compact manifest handoff summary after --run-chunks",
    )
    parser.add_argument("--diff-manifests", nargs=2, metavar=("OLD", "NEW"), default=[], help="compare two mxtest manifests without running tests")
    parser.add_argument("--recommend-chunks", default="", help="recommend a future chunk count from an aggregate manifest")
    parser.add_argument("--target-seconds", type=float, default=300.0, help="target seconds per chunk for --recommend-chunks")
    parser.add_argument("--min-chunks", type=int, default=1, help="minimum chunk recommendation")
    parser.add_argument("--max-chunks", type=int, default=64, help="maximum chunk recommendation")
    parser.add_argument(
        "--strategy",
        default="node",
        choices=sorted(VALID_STRATEGIES),
        help="chunking strategy: node slices node ids; file keeps files whole; segment splits oversized files; duration uses history",
    )
    parser.add_argument(
        "--history",
        action="append",
        default=[],
        help="mxtest JSON run summary to use for duration strategy; may be passed more than once",
    )
    parser.add_argument("--json", dest="json_path", default="", help="write a JSON run/plan summary to this path")
    parser.add_argument("--durations", type=int, default=10, help="pytest --durations value for runs; use 0 to omit")
    parser.add_argument("--heartbeat", type=int, default=None, help="parent-side liveness interval for long pytest children; 0 disables")
    parser.add_argument("--isolate-files", action="store_true", help="run each selected test file in a fresh pytest process")
    parser.add_argument("--file-timeout", type=int, default=120, help="per-file timeout in seconds for --isolate-files; use 0 to disable")
    parser.add_argument("--chunk-timeout", type=int, default=0, help="per-chunk timeout in seconds for non-isolated pytest children; use 0 to disable")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="extra pytest args after --")
    args = parser.parse_args(argv)
    if args.heartbeat is not None:
        configure_mxtest_heartbeat(int(args.heartbeat))

    pytest_args = list(args.pytest_args)
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]

    if args.verify_manifest:
        try:
            rc, lines, _issues = verify_manifest_file(Path(args.verify_manifest))
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        for line in lines:
            print(line)
        return int(rc)

    if args.verify_current_source:
        try:
            rc, lines, payload = verify_current_source_file(Path(args.verify_current_source))
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        return emit_lines_and_json(int(rc), lines, payload, args.json_path)

    if args.verify_current_environment:
        try:
            rc, lines, payload = verify_current_environment_file(Path(args.verify_current_environment))
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        return emit_lines_and_json(int(rc), lines, payload, args.json_path)

    if args.verify_current:
        try:
            rc, lines, payload = verify_current_manifest_file(Path(args.verify_current))
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        return emit_lines_and_json(int(rc), lines, payload, args.json_path)

    if args.manifest_summary:
        try:
            rc, lines, payload = manifest_summary_file(Path(args.manifest_summary), slowest=int(args.summary_limit))
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        return emit_lines_and_json(int(rc), lines, payload, args.json_path)

    if args.diff_manifests:
        try:
            old_path, new_path = [Path(p) for p in args.diff_manifests]
            rc, lines, payload = diff_manifest_files(old_path, new_path)
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        return emit_lines_and_json(int(rc), lines, payload, args.json_path)

    if args.recommend_chunks:
        try:
            rc, lines, payload = recommend_chunks_file(
                Path(args.recommend_chunks),
                target_seconds=float(args.target_seconds),
                min_chunks=int(args.min_chunks),
                max_chunks=int(args.max_chunks),
            )
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        return emit_lines_and_json(int(rc), lines, payload, args.json_path)

    try:
        strategy = validate_strategy(str(args.strategy))
        history_paths = [Path(p) for p in list(args.history or [])]
        duration_history = load_duration_history(history_paths) if history_paths else {}
    except UsageError as exc:
        print(f"mxtest: {exc}", file=sys.stderr)
        return 2

    chunk: tuple[int, int] | None = None
    if args.chunk:
        try:
            chunk = parse_chunk_spec(args.chunk)
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
    if args.run_chunks < 0:
        print("mxtest: --run-chunks must be greater than zero", file=sys.stderr)
        return 2
    if args.run_chunks and chunk is not None:
        print("mxtest: --run-chunks cannot be combined with --chunk", file=sys.stderr)
        return 2
    if args.resume and not args.run_chunks:
        print("mxtest: --resume requires --run-chunks", file=sys.stderr)
        return 2
    if args.resume and not args.json_path:
        print("mxtest: --resume requires --json", file=sys.stderr)
        return 2
    if int(args.max_new_chunks) < 0:
        print("mxtest: --max-new-chunks must be non-negative", file=sys.stderr)
        return 2
    if int(args.max_new_chunks) and not args.run_chunks:
        print("mxtest: --max-new-chunks requires --run-chunks", file=sys.stderr)
        return 2
    if int(args.max_new_files) < 0:
        print("mxtest: --max-new-files must be non-negative", file=sys.stderr)
        return 2
    if int(args.max_new_files) and not args.run_chunks:
        print("mxtest: --max-new-files requires --run-chunks", file=sys.stderr)
        return 2
    if int(args.max_new_files) and not args.isolate_files:
        print("mxtest: --max-new-files requires --isolate-files", file=sys.stderr)
        return 2
    if int(args.max_new_tests) < 0:
        print("mxtest: --max-new-tests must be non-negative", file=sys.stderr)
        return 2
    if int(args.max_new_tests) and not args.run_chunks:
        print("mxtest: --max-new-tests requires --run-chunks", file=sys.stderr)
        return 2
    if int(args.max_new_tests) and not args.isolate_files:
        print("mxtest: --max-new-tests requires --isolate-files", file=sys.stderr)
        return 2
    if int(args.test_batch_size) < 0:
        print("mxtest: --test-batch-size must be non-negative", file=sys.stderr)
        return 2
    if int(args.test_batch_size) and not args.isolate_files:
        print("mxtest: --test-batch-size requires --isolate-files", file=sys.stderr)
        return 2
    if bool(args.checkpoint_tests) and not args.isolate_files:
        print("mxtest: --checkpoint-tests requires --isolate-files", file=sys.stderr)
        return 2
    if float(args.max_runtime_seconds) < 0:
        print("mxtest: --max-runtime-seconds must be non-negative", file=sys.stderr)
        return 2
    if float(args.max_runtime_seconds) and not args.run_chunks:
        print("mxtest: --max-runtime-seconds requires --run-chunks", file=sys.stderr)
        return 2

    started = time.monotonic()
    nodeids = collect_nodeids(pytest_args)
    all_chunks: list[list[str]] | None = None
    selected = list(nodeids)
    if chunk is not None:
        all_chunks = build_chunks(nodeids, chunk[1], strategy=strategy, duration_history=duration_history)
        selected = all_chunks[chunk[0] - 1]

    collection_pytest_args, dropped_collection_pytest_args = split_pytest_args_for_collection(pytest_args)
    execution_pytest_args, dropped_pytest_selectors = split_pytest_args_for_execution(pytest_args)
    source_manifest = source_manifest_payload()
    environment_manifest = environment_manifest_payload()

    plan_payload: dict[str, Any] = {
        "collected": len(nodeids),
        "history_paths": [str(p) for p in history_paths],
        "history_file_count": len(duration_history),
        "pytest_args": pytest_args,
        "collection_pytest_args": collection_pytest_args,
        "dropped_collection_pytest_args": dropped_collection_pytest_args,
        "execution_pytest_args": execution_pytest_args,
        "dropped_pytest_selectors": dropped_pytest_selectors,
        "source_digest": source_manifest["digest"],
        "source_file_count": source_manifest["file_count"],
        "source_total_bytes": source_manifest["total_bytes"],
        "source_manifest": source_manifest,
        "environment_digest": environment_manifest["digest"],
        "environment_manifest": environment_manifest,
        "plugin_autoload": isolated_pytest_env().get("PYTEST_DISABLE_PLUGIN_AUTOLOAD"),
        "heartbeat_seconds": mxtest_heartbeat_seconds(),
        "isolate_files": bool(args.isolate_files),
        "file_timeout_seconds": int(args.file_timeout) if args.isolate_files and int(args.file_timeout) > 0 else None,
        "chunk_timeout_seconds": int(args.chunk_timeout) if not args.isolate_files and int(args.chunk_timeout) > 0 else None,
        "max_new_chunks": int(args.max_new_chunks) if int(args.max_new_chunks) > 0 else None,
        "max_new_files": int(args.max_new_files) if int(args.max_new_files) > 0 else None,
        "max_new_tests": int(args.max_new_tests) if int(args.max_new_tests) > 0 else None,
        "test_batch_size": int(args.test_batch_size) if int(args.test_batch_size) > 0 else None,
        "checkpoint_tests": bool(args.checkpoint_tests),
        "max_runtime_seconds": float(args.max_runtime_seconds) if float(args.max_runtime_seconds) > 0 else None,
    }
    plan_payload.update(
        chunk_selection_payload(
            selected=selected,
            index=chunk[0] if chunk is not None else None,
            total=chunk[1] if chunk is not None else None,
            strategy=strategy,
            duration_history=duration_history,
        )
    )

    if args.chunks:
        if args.chunks <= 0:
            print("mxtest: --chunks must be greater than zero", file=sys.stderr)
            return 2
        chunks = build_chunks(nodeids, args.chunks, strategy=strategy, duration_history=duration_history)
        plan_payload["chunks"] = [len(c) for c in chunks]
        plan_payload["chunk_plan"] = chunk_plan(
            nodeids,
            args.chunks,
            strategy=strategy,
            duration_history=duration_history,
            history_paths=history_paths,
            pytest_args=pytest_args,
        )
    elif all_chunks is not None:
        plan_payload["chunks"] = [len(c) for c in all_chunks]

    if args.run_chunks:
        chunks = build_chunks(nodeids, int(args.run_chunks), strategy=strategy, duration_history=duration_history)
        plan_payload["chunks"] = [len(c) for c in chunks]
        plan_payload["chunk_plan"] = chunk_plan(
            nodeids,
            int(args.run_chunks),
            strategy=strategy,
            duration_history=duration_history,
            history_paths=history_paths,
            pytest_args=pytest_args,
        )
        file_timeout = int(args.file_timeout) if args.isolate_files and int(args.file_timeout) > 0 else None
        chunk_timeout = int(args.chunk_timeout) if not args.isolate_files and int(args.chunk_timeout) > 0 else None
        print(f"mxtest: collected {len(nodeids)} tests; running {int(args.run_chunks)} chunks")
        print(f"mxtest: strategy {strategy}")
        print(f"mxtest: source {source_manifest['digest'][:12]} ({source_manifest['file_count']} files)")
        print(f"mxtest: environment {environment_manifest['digest'][:12]}")
        if args.resume:
            print(f"mxtest: resume manifest {args.json_path}")
        sys.stdout.flush()
        try:
            rc, _records, run_payload = run_all_chunks(
                chunks=chunks,
                strategy=strategy,
                duration_history=duration_history,
                execution_pytest_args=execution_pytest_args,
                durations=int(args.durations),
                isolate_files=bool(args.isolate_files),
                file_timeout=file_timeout,
                chunk_timeout=chunk_timeout,
                json_path=Path(args.json_path) if args.json_path else None,
                resume=bool(args.resume),
                fail_fast=bool(args.fail_fast),
                max_new_chunks=int(args.max_new_chunks),
                max_new_files=int(args.max_new_files),
                max_new_tests=int(args.max_new_tests),
                test_batch_size=int(args.test_batch_size),
                checkpoint_tests=bool(args.checkpoint_tests),
                max_runtime_seconds=float(args.max_runtime_seconds),
                base_payload=plan_payload,
                started=started,
            )
        except UsageError as exc:
            print(f"mxtest: {exc}", file=sys.stderr)
            return 2
        except MxtestInterrupted as exc:
            print(f"mxtest: interrupted by {exc.signal_name}; pytest child cleaned up", file=sys.stderr)
            return int(exc.returncode)
        if not bool(args.no_run_summary):
            emit_manifest_handoff_summary(
                run_payload,
                source_path=Path(args.json_path) if args.json_path else None,
                slowest=int(args.summary_limit),
            )
        return int(rc)

    if args.plan:
        print(f"collected: {len(nodeids)}")
        print(f"strategy: {strategy}")
        print(f"source: {source_manifest['digest'][:12]} ({source_manifest['file_count']} files)")
        print(f"environment: {environment_manifest['digest'][:12]}")
        if chunk is not None:
            print(f"selected: {len(selected)} (chunk {chunk[0]}/{chunk[1]})")
        if args.chunks:
            counts = plan_payload["chunks"]
            assert isinstance(counts, list)
            print("chunks:", " ".join(f"{i + 1}:{count}" for i, count in enumerate(counts)))
        if args.json_path:
            plan_payload["duration_seconds"] = round(time.monotonic() - started, 3)
            write_json_summary(Path(args.json_path), plan_payload)
        return 0

    print(f"mxtest: collected {len(nodeids)} tests; running {len(selected)}")
    print(f"mxtest: strategy {strategy}")
    print(f"mxtest: source {source_manifest['digest'][:12]} ({source_manifest['file_count']} files)")
    print(f"mxtest: environment {environment_manifest['digest'][:12]}")
    if chunk is not None:
        print(f"mxtest: chunk {chunk[0]}/{chunk[1]}")
    if args.isolate_files:
        print("mxtest: isolating selected files")
    sys.stdout.flush()
    payload = dict(plan_payload)
    file_summaries: list[dict[str, Any]] = []
    chunk_timeout = int(args.chunk_timeout) if not args.isolate_files and int(args.chunk_timeout) > 0 else None
    try:
        if not selected:
            if chunk is not None and nodeids:
                print(f"mxtest: chunk {chunk[0]}/{chunk[1]} is empty; skipping pytest invocation")
                rc = 0
                payload["status"] = "passed"
                payload["skipped"] = True
                payload["skip_reason"] = "empty-chunk-selection"
            else:
                print("mxtest: no tests selected; not invoking pytest with an empty node-id list", file=sys.stderr)
                rc = 5
                payload["status"] = status_for_returncode(int(rc))
                payload["skipped"] = False
                payload["skip_reason"] = "no-tests-selected"
        elif args.isolate_files:
            file_timeout = int(args.file_timeout) if int(args.file_timeout) > 0 else None
            def checkpoint_single_files(rows: list[dict[str, Any]]) -> None:
                nonlocal file_summaries
                file_summaries = [dict(row) for row in rows]
                if args.json_path:
                    checkpoint_payload = dict(payload)
                    checkpoint_payload["returncode"] = None
                    checkpoint_payload["status"] = "running"
                    checkpoint_payload["skipped"] = False
                    checkpoint_payload["duration_seconds"] = round(time.monotonic() - started, 3)
                    checkpoint_payload["checkpoint_reason"] = "file-isolated-progress"
                    checkpoint_payload["files"] = file_summaries
                    write_json_summary(Path(args.json_path), checkpoint_payload)

            isolated_kwargs: dict[str, Any] = {
                "durations": int(args.durations),
                "file_timeout": file_timeout,
                "progress": checkpoint_single_files,
            }
            if int(args.test_batch_size) > 0:
                isolated_kwargs["test_batch_size"] = int(args.test_batch_size)
            if bool(args.checkpoint_tests):
                isolated_kwargs["checkpoint_tests"] = True
            rc, file_summaries = run_pytest_file_isolated(
                selected,
                execution_pytest_args,
                **isolated_kwargs,
            )
            payload["status"] = status_for_returncode(int(rc))
            payload["skipped"] = False
        else:
            rc = run_pytest(selected, execution_pytest_args, durations=int(args.durations), timeout=chunk_timeout)
            payload["status"] = status_for_returncode(int(rc))
            payload["skipped"] = False
    except MxtestInterrupted as exc:
        print(f"mxtest: interrupted by {exc.signal_name}; pytest child cleaned up", file=sys.stderr)
        rc = int(exc.returncode)
        payload["status"] = "partial"
        payload["skipped"] = False
        payload["interrupted"] = True
        payload["signal"] = exc.signal_name
    payload["returncode"] = int(rc)
    payload["duration_seconds"] = round(time.monotonic() - started, 3)
    if file_summaries:
        payload["files"] = file_summaries
    if args.json_path:
        write_json_summary(Path(args.json_path), payload)
    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
