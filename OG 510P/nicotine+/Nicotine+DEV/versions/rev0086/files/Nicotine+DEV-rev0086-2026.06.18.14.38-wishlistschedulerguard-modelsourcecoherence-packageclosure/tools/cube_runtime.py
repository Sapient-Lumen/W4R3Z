#!/usr/bin/env python3
"""Small, dependency-free runtime helpers for current cube tooling.

Historical probes remain immutable evidence. New probes should import these
helpers instead of copying archive, hashing, CSV, isolation, and subprocess
plumbing into every revision.
"""
from __future__ import annotations

import csv
import io
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import tarfile
import zipfile
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

sys.dont_write_bytecode = True


class CubeRuntimeError(RuntimeError):
    """Raised when a fail-closed runtime invariant is violated."""


def canonical_json(value: object) -> str:
    """Return deterministic, human-readable JSON with a final newline."""
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def digest_stream(handle: BinaryIO) -> tuple[str, int]:
    """Return a SHA-256 digest and byte count for a binary stream."""
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: handle.read(1 << 20), b""):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def sha256_path(path: Path) -> str:
    """Hash a regular file without loading it into memory."""
    with path.open("rb") as handle:
        digest, _size = digest_stream(handle)
    return digest


def git_blob_sha1_path(path: Path) -> str:
    """Return Git's SHA-1 object ID for a regular file's blob bytes."""
    size = path.stat().st_size
    digest = hashlib.sha1(usedforsecurity=False)
    digest.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], *, fields: Sequence[str] | None = None) -> None:
    materialized = [dict(row) for row in rows]
    if fields is None:
        discovered: list[str] = []
        for row in materialized:
            for field in row:
                if field not in discovered:
                    discovered.append(field)
        fields = discovered or ("status",)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="raise")
        writer.writeheader()
        writer.writerows(materialized)


def safe_relative(value: object, *, prefix: str | None = None, suffix: str | None = None) -> bool:
    """Validate a portable package-relative POSIX path."""
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return False
    if prefix is not None and path.parts[:1] != (prefix,):
        return False
    if suffix is not None and path.suffix != suffix:
        return False
    return True


def derive_revision(root: Path) -> str:
    revision = (root / "REVISION.txt").read_text(encoding="utf-8").strip()
    if len(revision) != 7 or not revision.startswith("rev") or not revision[3:].isdigit():
        raise CubeRuntimeError(f"invalid revision marker: {revision!r}")
    return revision


def isolated_environment(
    runtime_root: Path,
    *,
    python_paths: Sequence[Path] = (),
    inherit: Mapping[str, str] | None = None,
) -> tuple[dict[str, str], Path]:
    """Create isolated HOME/XDG/TMP/cwd paths and a deterministic Python env."""
    runtime_root.mkdir(parents=True, exist_ok=True)
    cwd = runtime_root / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)

    path_vars = {
        "HOME": runtime_root / "home",
        "XDG_CONFIG_HOME": runtime_root / "xdg-config",
        "XDG_DATA_HOME": runtime_root / "xdg-data",
        "XDG_CACHE_HOME": runtime_root / "xdg-cache",
        "TMPDIR": runtime_root / "tmp",
    }
    for path in path_vars.values():
        path.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if inherit:
        env.update(inherit)
    env.update({key: str(path) for key, path in path_vars.items()})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if python_paths:
        inherited = env.get("PYTHONPATH")
        entries = [str(path) for path in python_paths]
        if inherited:
            entries.append(inherited)
        env["PYTHONPATH"] = os.pathsep.join(entries)
    return env, cwd


ISOLATED_ENVIRONMENT_DIR_NAMES = (
    "cwd",
    "home",
    "tmp",
    "xdg-cache",
    "xdg-config",
    "xdg-data",
)


def purge_isolated_environment(runtime_root: Path) -> dict[str, Any]:
    """Inventory and remove transient process-environment trees.

    Logs and JUnit reports must live outside the directories created by
    :func:`isolated_environment`. Regular files and symlinks are represented by
    path, kind, size, and SHA-256 only; mutable contents and link targets are
    removed with the transient tree.
    """
    runtime_root = runtime_root.resolve()
    entries: list[dict[str, Any]] = []
    removed_directories: list[str] = []

    for name in ISOLATED_ENVIRONMENT_DIR_NAMES:
        path = runtime_root / name
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_dir():
            raise CubeRuntimeError(f"unsafe isolated-environment root: {path}")

        removed_directories.append(name)
        for current_root, directory_names, file_names in os.walk(path, followlinks=False):
            current = Path(current_root)

            for child_name in tuple(directory_names):
                child = current / child_name
                if not child.is_symlink():
                    continue
                target = os.readlink(child).encode("utf-8", errors="surrogateescape")
                relative = (Path(name) / child.relative_to(path)).as_posix()
                entries.append({
                    "path": relative,
                    "kind": "symlink",
                    "bytes": len(target),
                    "sha256": sha256_bytes(target),
                })
                directory_names.remove(child_name)

            for child_name in file_names:
                child = current / child_name
                relative = (Path(name) / child.relative_to(path)).as_posix()
                if child.is_symlink():
                    target = os.readlink(child).encode("utf-8", errors="surrogateescape")
                    entries.append({
                        "path": relative,
                        "kind": "symlink",
                        "bytes": len(target),
                        "sha256": sha256_bytes(target),
                    })
                    continue
                if not child.is_file():
                    raise CubeRuntimeError(f"special file in isolated environment: {child}")
                entries.append({
                    "path": relative,
                    "kind": "file",
                    "bytes": child.stat().st_size,
                    "sha256": sha256_path(child),
                })

        shutil.rmtree(path)

    remaining = [
        name for name in ISOLATED_ENVIRONMENT_DIR_NAMES
        if (runtime_root / name).exists() or (runtime_root / name).is_symlink()
    ]
    if remaining:
        raise CubeRuntimeError(
            f"isolated-environment cleanup incomplete under {runtime_root}: {remaining}"
        )

    return {
        "removed_directories": removed_directories,
        "entries": entries,
        "entry_count": len(entries),
        "regular_files": sum(row["kind"] == "file" for row in entries),
        "symlinks": sum(row["kind"] == "symlink" for row in entries),
        "bytes": sum(int(row["bytes"]) for row in entries),
        "residual_directories": remaining,
    }


def _kill_process_tree(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()


def run_bounded(
    command: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
    timeout: int = 240,
    output_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a process group with bounded lifetime and regular-file capture.

    A regular file avoids waiting on a pipe inherited by descendant processes.
    The returned stdout contains the complete captured text.
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    cwd = cwd.resolve()
    if output_path is None:
        output_dir = Path(tempfile.mkdtemp(prefix="cube-runtime-"))
        output_path = output_dir / "output.log"
        cleanup_dir: Path | None = output_dir
    else:
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleanup_dir = None

    process: subprocess.Popen[Any]
    timed_out = False
    with output_path.open("w+", encoding="utf-8") as output:
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            env=dict(env) if env is not None else None,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=(os.name == "posix"),
        )
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_tree(process)
            process.wait(timeout=10)
            return_code = 124
        output.flush()
        output.seek(0)
        captured = output.read()

    if timed_out:
        captured += "\n[timeout]\n"
    result = subprocess.CompletedProcess(list(command), return_code, captured)
    if cleanup_dir is not None:
        shutil.rmtree(cleanup_dir, ignore_errors=True)
    return result



def safe_extract_tar_gz_member(zip_path: Path, member_name: str, destination: Path) -> int:
    """Extract one tar.gz payload from a ZIP through a single safe root.

    Symlinks and hard links are resolved only when their target remains inside
    the tar's top-level directory. Special files are rejected.
    """
    with zipfile.ZipFile(zip_path) as outer:
        try:
            payload = outer.read(member_name)
        except KeyError as exc:
            raise CubeRuntimeError(f"missing nested archive: {member_name}") from exc

    count = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as inner:
        members = inner.getmembers()
        roots = {PurePosixPath(member.name).parts[0] for member in members if member.name}
        if len(roots) != 1:
            raise CubeRuntimeError(f"expected one tar root, found {sorted(roots)}")
        root = next(iter(roots))

        for member in members:
            pure = PurePosixPath(member.name)
            if not pure.parts or pure.parts[0] != root:
                raise CubeRuntimeError(f"entry escapes tar root: {member.name}")
            relative = PurePosixPath(*pure.parts[1:])
            if not relative.parts:
                continue
            if relative.is_absolute() or ".." in relative.parts:
                raise CubeRuntimeError(f"unsafe tar entry: {member.name}")
            target = destination.joinpath(*relative.parts)

            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            source_member = member
            if member.issym() or member.islnk():
                base = PurePosixPath(member.name).parent
                resolved = PurePosixPath(os.path.normpath((base / member.linkname).as_posix()))
                if not resolved.parts or resolved.parts[0] != root or ".." in resolved.parts:
                    raise CubeRuntimeError(
                        f"link escapes tar root: {member.name} -> {member.linkname}"
                    )
                try:
                    source_member = inner.getmember(resolved.as_posix())
                except KeyError as exc:
                    raise CubeRuntimeError(
                        f"link target missing: {member.name} -> {member.linkname}"
                    ) from exc

            if not source_member.isfile():
                raise CubeRuntimeError(f"unsupported tar entry: {member.name}")
            source = inner.extractfile(source_member)
            if source is None:
                raise CubeRuntimeError(f"cannot read tar entry: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            count += 1
    return count


def parse_junit_report(report_path: Path) -> list[dict[str, Any]]:
    """Normalize a pytest JUnit XML report into one row per testcase."""
    tree = ET.parse(report_path)
    rows: list[dict[str, Any]] = []
    for case in tree.iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if failure is not None:
            outcome = "failed"
            detail = failure.get("message", "")
        elif error is not None:
            outcome = "error"
            detail = error.get("message", "")
        elif skipped is not None:
            outcome = "skipped"
            detail = skipped.get("message", "")
        else:
            outcome = "passed"
            detail = ""
        classname = case.get("classname", "")
        name = case.get("name", "")
        nodeid = f"{classname}::{name}" if classname else name
        rows.append({
            "nodeid": nodeid,
            "name": name,
            "outcome": outcome,
            "passed": outcome == "passed",
            "duration": round(float(case.get("time", "0") or 0), 6),
            "detail": detail,
        })
    return rows


def parse_pytest_report(report_path: Path) -> list[dict[str, Any]]:
    """Normalize pytest's JSON report into one row per test."""
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for test in payload.get("tests", []):
        outcome = str(test.get("outcome", "unknown"))
        rows.append({
            "nodeid": str(test.get("nodeid", "")),
            "outcome": outcome,
            "passed": outcome == "passed",
            "duration": round(float(test.get("duration", 0.0)), 6),
        })
    return rows


def file_inventory(root: Path, *, exclude: Iterable[Path] = ()) -> dict[Path, tuple[str, int]]:
    """Return package-relative file hashes and sizes, excluding symlinks."""
    excluded = {path.as_posix() for path in exclude}
    rows: dict[Path, tuple[str, int]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if relative.as_posix() in excluded:
            continue
        rows[relative] = (sha256_path(path), path.stat().st_size)
    return rows
