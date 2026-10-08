#!/usr/bin/env python3
"""Run EvidenceVault checks from one hash-verified private execution snapshot.

The overlay is verified and copied before any other in-tree Python is imported or
executed.  Every configured check then runs in an isolated interpreter against
that private read-only snapshot.  The original source tree and the execution
snapshot are both reverified before success is returned.
"""
from __future__ import annotations

# Re-exec before importing ordinary modules.  Isolated/no-site mode prevents the
# mutable bundle, PYTHONPATH, user site, or site hooks from shadowing stdlib code
# during the bootstrap verifier itself.
import os as _bootstrap_os
import sys as _bootstrap_sys

if not (_bootstrap_sys.flags.isolated and _bootstrap_sys.flags.no_site):
    _env = {
        key: value
        for key, value in _bootstrap_os.environ.items()
        if key
        not in {
            "PYTHONHOME",
            "PYTHONPATH",
            "PYTHONSTARTUP",
            "PYTHONINSPECT",
            "PYTHONUSERBASE",
        }
    }
    _env["PYTHONDONTWRITEBYTECODE"] = "1"
    _env["PYTHONNOUSERSITE"] = "1"
    _bootstrap_os.execve(
        _bootstrap_sys.executable,
        [
            _bootstrap_sys.executable,
            "-I",
            "-S",
            _bootstrap_os.path.abspath(__file__),
            *_bootstrap_sys.argv[1:],
        ],
        _env,
    )

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable
import unicodedata

sys.dont_write_bytecode = True
SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT_RESOLVED = SOURCE_ROOT.resolve()
OVERLAY_MANIFEST_REL = "CHECKS/overlay-manifest.json"
OVERLAY_MANIFEST_SIDECAR_REL = "CHECKS/overlay-manifest.sha256"
PATCH_MANIFEST_REL = "PATCH_BUNDLE_MANIFEST.json"
INTEGRITY_CHECK_ID = "overlay-integrity"
_ISOLATED_RUNNER = (
    "import runpy,sys;"
    "d=sys.argv[1];p=sys.argv[2];a=sys.argv[3:];"
    "sys.path.append(d);sys.argv=[p,*a];"
    "runpy.run_path(p,run_name='__main__')"
)


class GateError(RuntimeError):
    """Configuration, integrity, execution-snapshot, or safe-output error."""


@dataclass
class TreeAnchor:
    path: Path
    fd: int
    device: int
    inode: int

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


@dataclass(frozen=True)
class InventoryEntry:
    path: str
    size: int
    sha256: str


@dataclass
class VerifiedExecutionSnapshot:
    temporary: tempfile.TemporaryDirectory[str]
    root: Path
    source_anchor: TreeAnchor
    snapshot_anchor: TreeAnchor
    manifest_sha256: str
    inventory_sha256: str
    file_count: int
    total_bytes: int

    def close(self) -> None:
        self.snapshot_anchor.close()
        self.source_anchor.close()
        self.temporary.cleanup()


def _clean_rel(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise GateError(f"{label} must be a non-empty canonical POSIX relative path")
    if unicodedata.normalize("NFC", value) != value:
        raise GateError(f"{label} is not NFC-normalized: {value!r}")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise GateError(f"{label} contains a control character: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise GateError(f"{label} is unsafe or non-canonical: {value!r}")
    if pure.as_posix() != value or value.endswith("/"):
        raise GateError(f"{label} is not canonical POSIX spelling: {value!r}")
    first = pure.parts[0]
    if ":" in first or first.startswith("~"):
        raise GateError(f"{label} has a platform-sensitive first component: {value!r}")
    for part in pure.parts:
        if part.endswith((" ", ".")):
            raise GateError(f"{label} has a platform-ambiguous component: {value!r}")
    return value


def _safe_rel(text: Any, label: str) -> str:
    """Compatibility name for inherited strict path-spelling assertions."""
    try:
        return _clean_rel(text, label)
    except GateError as exc:
        message = str(exc).replace("canonical POSIX spelling", "canonical spelling")
        raise GateError(message) from exc


def _clean_component(name: str, label: str) -> str:
    cleaned = _clean_rel(name, label)
    if "/" in cleaned:
        raise GateError(f"{label} must be one path component: {name!r}")
    return cleaned


def _full_signature(st: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        st.st_dev,
        st.st_ino,
        st.st_mode,
        st.st_size,
        st.st_mtime_ns,
        st.st_ctime_ns,
    )


def _open_tree_anchor(path: Path, label: str) -> TreeAnchor:
    try:
        lexical = path.lstat()
    except OSError as exc:
        raise GateError(f"cannot inspect {label}: {exc}") from exc
    if stat.S_ISLNK(lexical.st_mode) or not stat.S_ISDIR(lexical.st_mode):
        raise GateError(f"{label} must be a real directory, not a symlink or special file")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise GateError(f"cannot open {label} without following symlinks: {exc}") from exc
    opened = os.fstat(fd)
    if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
        lexical.st_dev,
        lexical.st_ino,
    ):
        os.close(fd)
        raise GateError(f"{label} changed while it was opened")
    return TreeAnchor(path=path, fd=fd, device=opened.st_dev, inode=opened.st_ino)


def _assert_anchor_path(anchor: TreeAnchor, phase: str) -> None:
    try:
        current = anchor.path.lstat()
        opened = os.fstat(anchor.fd)
    except OSError as exc:
        raise GateError(f"cannot revalidate tree root during {phase}: {exc}") from exc
    if (
        stat.S_ISLNK(current.st_mode)
        or not stat.S_ISDIR(current.st_mode)
        or not stat.S_ISDIR(opened.st_mode)
        or (current.st_dev, current.st_ino) != (anchor.device, anchor.inode)
        or (opened.st_dev, opened.st_ino) != (anchor.device, anchor.inode)
    ):
        raise GateError(f"tree root no longer names the validated directory during {phase}")


def _open_directory_at(parent_fd: int, name: str, label: str) -> int:
    name = _clean_component(name, label)
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as exc:
        raise GateError(f"cannot inspect directory component {label}: {exc}") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise GateError(f"directory component is symlinked or non-directory: {label}")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise GateError(f"cannot open directory component {label}: {exc}") from exc
    opened = os.fstat(fd)
    if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
        before.st_dev,
        before.st_ino,
    ):
        os.close(fd)
        raise GateError(f"directory component changed while opening: {label}")
    return fd


def _open_regular_at(root_fd: int, rel: str) -> tuple[int, os.stat_result]:
    rel = _clean_rel(rel, "inventory path")
    parts = PurePosixPath(rel).parts
    current_fd = os.dup(root_fd)
    try:
        for index, part in enumerate(parts[:-1]):
            next_fd = _open_directory_at(
                current_fd, part, "/".join(parts[: index + 1])
            )
            os.close(current_fd)
            current_fd = next_fd
        final = parts[-1]
        try:
            before = os.stat(final, dir_fd=current_fd, follow_symlinks=False)
        except OSError as exc:
            raise GateError(f"cannot inspect inventory file {rel}: {exc}") from exc
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            raise GateError(f"inventory path is symlinked or non-regular: {rel}")
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(final, flags, dir_fd=current_fd)
        except OSError as exc:
            raise GateError(f"cannot open inventory file {rel}: {exc}") from exc
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
            before.st_dev,
            before.st_ino,
        ):
            os.close(fd)
            raise GateError(f"inventory file changed while opening: {rel}")
        return fd, opened
    finally:
        os.close(current_fd)


def _read_regular_at(root_fd: int, rel: str) -> tuple[bytes, os.stat_result, str]:
    fd, opened = _open_regular_at(root_fd, rel)
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    try:
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
            digest.update(chunk)
        after = os.fstat(fd)
    except OSError as exc:
        raise GateError(f"cannot read inventory file {rel}: {exc}") from exc
    finally:
        os.close(fd)
    if _full_signature(after) != _full_signature(opened):
        raise GateError(f"inventory file changed while being read: {rel}")
    payload = b"".join(chunks)
    if len(payload) != opened.st_size:
        raise GateError(f"short read for inventory file: {rel}")
    return payload, opened, digest.hexdigest()


def _fresh_root_scan_fd(anchor: TreeAnchor) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(".", flags, dir_fd=anchor.fd)
    except OSError as exc:
        raise GateError(f"cannot duplicate tree root for enumeration: {exc}") from exc
    opened = os.fstat(fd)
    if (opened.st_dev, opened.st_ino) != (anchor.device, anchor.inode):
        os.close(fd)
        raise GateError("enumeration root does not match retained tree anchor")
    return fd


def _enumerate_files(anchor: TreeAnchor) -> set[str]:
    files: set[str] = set()

    def walk(directory_fd: int, prefix: tuple[str, ...]) -> None:
        try:
            with os.scandir(directory_fd) as iterator:
                names = sorted(entry.name for entry in iterator)
        except OSError as exc:
            label = "/".join(prefix) or "."
            raise GateError(f"cannot enumerate tree directory {label}: {exc}") from exc
        for raw_name in names:
            name = _clean_component(raw_name, "filesystem path component")
            rel_parts = (*prefix, name)
            rel = "/".join(rel_parts)
            try:
                before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as exc:
                raise GateError(f"cannot inspect tree entry {rel}: {exc}") from exc
            if stat.S_ISLNK(before.st_mode):
                raise GateError(f"tree contains a symlink: {rel}")
            if stat.S_ISDIR(before.st_mode):
                child_fd = _open_directory_at(directory_fd, name, rel)
                try:
                    walk(child_fd, rel_parts)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(before.st_mode):
                files.add(rel)
            else:
                raise GateError(f"tree contains a special file: {rel}")

    root_fd = _fresh_root_scan_fd(anchor)
    try:
        walk(root_fd, ())
    finally:
        os.close(root_fd)
    return files


def _parse_inventory(anchor: TreeAnchor) -> tuple[bytes, bytes, str, list[InventoryEntry]]:
    manifest_bytes, _, manifest_sha = _read_regular_at(anchor.fd, OVERLAY_MANIFEST_REL)
    sidecar_bytes, _, _ = _read_regular_at(anchor.fd, OVERLAY_MANIFEST_SIDECAR_REL)
    expected_sidecar = f"{manifest_sha}  {OVERLAY_MANIFEST_REL}\n".encode("ascii")
    if sidecar_bytes != expected_sidecar:
        raise GateError("overlay manifest sidecar does not bind the exact inventory payload")
    try:
        data = json.loads(manifest_bytes.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"invalid {OVERLAY_MANIFEST_REL}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        raise GateError("overlay manifest must be an object with a files list")
    entries: list[InventoryEntry] = []
    seen: set[str] = set()
    for index, item in enumerate(data["files"]):
        if not isinstance(item, dict):
            raise GateError(f"overlay manifest files[{index}] must be an object")
        rel = _clean_rel(item.get("path"), f"overlay manifest files[{index}].path")
        if rel in {OVERLAY_MANIFEST_REL, OVERLAY_MANIFEST_SIDECAR_REL}:
            raise GateError(f"overlay manifest may not inventory itself: {rel}")
        if rel in seen:
            raise GateError(f"duplicate overlay manifest path: {rel}")
        seen.add(rel)
        size = item.get("bytes")
        digest = item.get("sha256")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise GateError(f"overlay manifest size is invalid for {rel}")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise GateError(f"overlay manifest SHA-256 is invalid for {rel}")
        entries.append(InventoryEntry(rel, size, digest))
    if data.get("file_count") != len(entries):
        raise GateError("overlay manifest file_count does not match its entries")
    return manifest_bytes, sidecar_bytes, manifest_sha, sorted(entries, key=lambda row: row.path)


def _inventory_digest(rows: Iterable[InventoryEntry], special: dict[str, tuple[int, str]]) -> str:
    digest = hashlib.sha256()
    combined = [(row.path, row.size, row.sha256) for row in rows]
    combined.extend((path, size, sha) for path, (size, sha) in special.items())
    for rel, size, sha in sorted(combined):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(sha.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _verify_inventory(
    anchor: TreeAnchor,
    *,
    expected_manifest_sha256: str | None = None,
    expected_inventory_sha256: str | None = None,
) -> dict[str, Any]:
    _assert_anchor_path(anchor, "inventory verification")
    manifest_bytes, sidecar_bytes, manifest_sha, entries = _parse_inventory(anchor)
    if expected_manifest_sha256 is not None and manifest_sha != expected_manifest_sha256:
        raise GateError("overlay manifest payload changed after execution snapshot capture")
    expected_paths = {row.path for row in entries} | {
        OVERLAY_MANIFEST_REL,
        OVERLAY_MANIFEST_SIDECAR_REL,
    }
    actual_paths = _enumerate_files(anchor)
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        raise GateError(
            "tree file set differs from overlay inventory; "
            f"missing={missing[:10]} extra={extra[:10]}"
        )
    total_bytes = 0
    for row in entries:
        payload, _, digest = _read_regular_at(anchor.fd, row.path)
        if len(payload) != row.size or digest != row.sha256:
            raise GateError(f"overlay inventory mismatch for {row.path}")
        total_bytes += len(payload)
    special = {
        OVERLAY_MANIFEST_REL: (len(manifest_bytes), manifest_sha),
        OVERLAY_MANIFEST_SIDECAR_REL: (
            len(sidecar_bytes),
            hashlib.sha256(sidecar_bytes).hexdigest(),
        ),
    }
    total_bytes += sum(size for size, _ in special.values())
    inventory_sha = _inventory_digest(entries, special)
    if expected_inventory_sha256 is not None and inventory_sha != expected_inventory_sha256:
        raise GateError("tree inventory identity changed after execution snapshot capture")
    _assert_anchor_path(anchor, "inventory verification completion")
    return {
        "manifest_bytes": manifest_bytes,
        "sidecar_bytes": sidecar_bytes,
        "manifest_sha256": manifest_sha,
        "entries": entries,
        "inventory_sha256": inventory_sha,
        "file_count": len(entries) + 2,
        "total_bytes": total_bytes,
    }


def _write_snapshot_file(root: Path, rel: str, payload: bytes, source_mode: int) -> None:
    destination = root.joinpath(*PurePosixPath(rel).parts)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    mode = 0o555 if source_mode & 0o111 else 0o444
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(destination, flags, mode)
    except OSError as exc:
        raise GateError(f"cannot create private execution-snapshot file {rel}: {exc}") from exc
    try:
        view = memoryview(payload)
        offset = 0
        while offset < len(view):
            written = os.write(fd, view[offset:])
            if written <= 0:
                raise GateError(f"short write while creating execution snapshot: {rel}")
            offset += written
        os.fsync(fd)
        os.fchmod(fd, mode)
    finally:
        os.close(fd)


def _lock_snapshot_directories(root: Path) -> None:
    directories = [path for path in root.rglob("*") if path.is_dir()]
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        os.chmod(directory, 0o555, follow_symlinks=False)
    os.chmod(root, 0o555, follow_symlinks=False)


def _capture_verified_execution_snapshot() -> VerifiedExecutionSnapshot:
    source_anchor = _open_tree_anchor(SOURCE_ROOT, "overlay source root")
    temporary: tempfile.TemporaryDirectory[str] | None = None
    snapshot_anchor: TreeAnchor | None = None
    try:
        verified = _verify_inventory(source_anchor)
        temporary = tempfile.TemporaryDirectory(prefix="ev-overlay-gate-snapshot-")
        os.chmod(temporary.name, 0o700)
        snapshot_root = Path(temporary.name) / SOURCE_ROOT.name
        snapshot_root.mkdir(mode=0o700)
        manifest_payload = verified["manifest_bytes"]
        sidecar_payload = verified["sidecar_bytes"]
        entries: list[InventoryEntry] = verified["entries"]
        special_payloads = {
            OVERLAY_MANIFEST_REL: manifest_payload,
            OVERLAY_MANIFEST_SIDECAR_REL: sidecar_payload,
        }
        for rel, expected_payload in special_payloads.items():
            payload, opened, _ = _read_regular_at(source_anchor.fd, rel)
            if payload != expected_payload:
                raise GateError(f"source metadata changed while snapshotting: {rel}")
            _write_snapshot_file(snapshot_root, rel, payload, opened.st_mode)
        for row in entries:
            payload, opened, digest = _read_regular_at(source_anchor.fd, row.path)
            if len(payload) != row.size or digest != row.sha256:
                raise GateError(f"source file changed while snapshotting: {row.path}")
            _write_snapshot_file(snapshot_root, row.path, payload, opened.st_mode)
        _lock_snapshot_directories(snapshot_root)
        snapshot_anchor = _open_tree_anchor(snapshot_root, "private execution snapshot")
        snapshot_report = _verify_inventory(
            snapshot_anchor,
            expected_manifest_sha256=verified["manifest_sha256"],
            expected_inventory_sha256=verified["inventory_sha256"],
        )
        _verify_inventory(
            source_anchor,
            expected_manifest_sha256=verified["manifest_sha256"],
            expected_inventory_sha256=verified["inventory_sha256"],
        )
        return VerifiedExecutionSnapshot(
            temporary=temporary,
            root=snapshot_root,
            source_anchor=source_anchor,
            snapshot_anchor=snapshot_anchor,
            manifest_sha256=verified["manifest_sha256"],
            inventory_sha256=verified["inventory_sha256"],
            file_count=snapshot_report["file_count"],
            total_bytes=snapshot_report["total_bytes"],
        )
    except Exception:
        if snapshot_anchor is not None:
            snapshot_anchor.close()
        source_anchor.close()
        if temporary is not None:
            temporary.cleanup()
        raise


def _isolated_python_command(root: Path, script_rel: str, arguments: Iterable[str]) -> list[str]:
    script_rel = _clean_rel(script_rel, "Python script path")
    script_path = root / script_rel
    if not script_path.is_file() or script_path.is_symlink():
        raise GateError(f"verified snapshot lacks Python script: {script_rel}")
    return [
        sys.executable,
        "-I",
        "-S",
        "-c",
        _ISOLATED_RUNNER,
        os.fspath(root / "scripts"),
        os.fspath(script_path),
        *arguments,
    ]


def _safe_environment() -> dict[str, str]:
    blocked = {
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONINSPECT",
        "PYTHONUSERBASE",
    }
    env = {key: value for key, value in os.environ.items() if key not in blocked}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _load_json_file(root: Path, rel: str) -> dict[str, Any]:
    rel = _clean_rel(rel, "JSON path")
    path = root / rel
    if path.is_symlink() or not path.is_file():
        raise GateError(f"required JSON file is missing or unsafe: {rel}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"invalid {rel}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{rel} must contain a JSON object")
    return value


def _run_coverage(root: Path, include_recovery: bool) -> dict[str, Any]:
    args = ["--root", os.fspath(root), "--json"]
    if include_recovery:
        args.append("--include-recovery")
    command = _isolated_python_command(root, "scripts/canonical_coverage.py", args)
    completed = subprocess.run(
        command,
        cwd=root,
        env=_safe_environment(),
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise GateError(f"canonical coverage engine failed: {detail}")
    try:
        value = json.loads(completed.stdout)
    except Exception as exc:
        raise GateError(f"canonical coverage engine emitted invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError("canonical coverage engine did not emit a JSON object")
    return value


def _load_profiles(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    declared_representation = manifest.get("representation_profile")
    declared_recovery = manifest.get("recovery_profile")
    if not isinstance(declared_representation, dict) or not isinstance(declared_recovery, dict):
        raise GateError("PATCH_BUNDLE_MANIFEST.json must declare representation and recovery profiles")
    live_representation = _run_coverage(root, False)
    live_recovery = _run_coverage(root, True)
    representation_keys = (
        "canonical_index_files",
        "canonical_index_bytes",
        "canonical_exact_files_present",
        "canonical_exact_bytes_present",
        "canonical_mismatched_files_present",
        "canonical_missing_files",
        "canonical_source_files",
        "canonical_source_exact_files_present",
        "kind",
    )
    recovery_keys = (
        "canonical_index_files",
        "canonical_index_bytes",
        "canonical_at_path_exact_files",
        "canonical_at_path_exact_bytes",
        "canonical_recovery_object_files",
        "canonical_recovery_object_bytes",
        "canonical_rehydratable_files",
        "canonical_rehydratable_bytes",
        "canonical_unavailable_files",
        "canonical_unavailable_bytes",
        "canonical_mismatched_files_recoverable",
        "canonical_mismatched_files_unresolved",
        "canonical_missing_files_recoverable",
        "canonical_missing_files_unresolved",
        "canonical_source_files",
        "canonical_source_rehydratable_files",
        "kind",
        "recovery_inventory",
        "recovery_inventory_sha256",
    )
    rep_diff = [
        f"{key}: declared={declared_representation.get(key)!r} live={live_representation.get(key)!r}"
        for key in representation_keys
        if declared_representation.get(key) != live_representation.get(key)
    ]
    recovery_diff = [
        f"{key}: declared={declared_recovery.get(key)!r} live={live_recovery.get(key)!r}"
        for key in recovery_keys
        if declared_recovery.get(key) != live_recovery.get(key)
    ]
    if rep_diff:
        raise GateError("representation_profile is stale: " + "; ".join(rep_diff))
    if recovery_diff:
        raise GateError("recovery_profile is stale: " + "; ".join(recovery_diff))
    evidence_paths = [declared_representation.get("evidence"), declared_recovery.get("evidence")]
    for raw in evidence_paths:
        rel = _clean_rel(raw, "profile evidence")
        path = root / rel
        if path.is_symlink() or not path.is_file():
            raise GateError(f"profile evidence is absent or unsafe: {rel}")
    representation = dict(declared_representation)
    representation.update(live_representation)
    representation["live_verified"] = True
    recovery = dict(declared_recovery)
    recovery.update(live_recovery)
    recovery["live_verified"] = True
    return representation, recovery


def _load_checks(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    raw = manifest.get("gate_checks")
    if not isinstance(raw, list) or not raw:
        raise GateError("PATCH_BUNDLE_MANIFEST.json gate_checks must be a non-empty list")
    checks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise GateError(f"gate_checks[{index}] must be an object")
        check_id = item.get("id")
        if not isinstance(check_id, str) or not check_id or check_id in seen:
            raise GateError(f"gate_checks[{index}].id must be unique and non-empty")
        seen.add(check_id)
        command = item.get("command")
        if not isinstance(command, list) or len(command) < 2 or not all(
            isinstance(part, str) and part for part in command
        ):
            raise GateError(f"gate_checks[{index}].command must be an argument vector")
        if command[0] not in {"python3", sys.executable}:
            raise GateError(f"gate check {check_id} must invoke Python directly")
        script_rel = _clean_rel(command[1], f"gate_checks[{index}].command[1]")
        if not script_rel.startswith("scripts/"):
            raise GateError(f"gate check {check_id} script must live under scripts/")
        script = root / script_rel
        if script.is_symlink() or not script.is_file():
            raise GateError(f"gate check script is missing or unsafe: {script_rel}")
        timeout = item.get("timeout_seconds", 180)
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 1800:
            raise GateError(f"gate check {check_id} timeout_seconds must be 1..1800")
        checks.append(
            {
                "id": check_id,
                "description": str(item.get("description", "")),
                "script": script_rel,
                "arguments": list(command[2:]),
                "logical_command": ["python3", script_rel, *command[2:]],
                "timeout_seconds": timeout,
            }
        )
    if checks[0]["id"] != INTEGRITY_CHECK_ID:
        raise GateError(f"{INTEGRITY_CHECK_ID} must be the first configured gate check")
    return checks


def _select_checks(checks: list[dict[str, Any]], requested: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    known = {row["id"] for row in checks}
    unknown = sorted(set(requested) - known)
    if unknown:
        raise GateError("unknown --check id(s): " + ", ".join(unknown))
    full_gate = not requested
    requested_set = set(requested)
    selected = list(checks) if full_gate else [
        row for row in checks if row["id"] == INTEGRITY_CHECK_ID or row["id"] in requested_set
    ]
    return selected, {
        "scope": "full_gate" if full_gate else "selected_checks",
        "full_gate": full_gate,
        "requested_check_ids": list(requested),
        "selected_configured_check_ids": [row["id"] for row in selected],
        "integrity_forced": bool(requested and INTEGRITY_CHECK_ID not in requested_set),
        "postflight_integrity_planned": len(selected) > 1,
    }


def _run_check(
    check: dict[str, Any], root: Path, timeout_override: int | None, phase: str
) -> dict[str, Any]:
    timeout = timeout_override or int(check["timeout_seconds"])
    effective_command = _isolated_python_command(root, check["script"], check["arguments"])
    started = time.monotonic()
    try:
        completed = subprocess.run(
            effective_command,
            cwd=root,
            env=_safe_environment(),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "id": check["id"],
            "phase": phase,
            "description": check["description"],
            "command": check["logical_command"],
            "isolated_interpreter": True,
            "execution_root": "verified_private_snapshot",
            "timeout_seconds": timeout,
            "duration_seconds": round(time.monotonic() - started, 3),
            "exit_code": completed.returncode,
            "status": "pass" if completed.returncode == 0 else "fail",
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "id": check["id"],
            "phase": phase,
            "description": check["description"],
            "command": check["logical_command"],
            "isolated_interpreter": True,
            "execution_root": "verified_private_snapshot",
            "timeout_seconds": timeout,
            "duration_seconds": round(time.monotonic() - started, 3),
            "exit_code": None,
            "status": "timeout",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }


def _first_existing_symlink_component(path: Path) -> Path | None:
    if not path.is_absolute():
        raise GateError(f"expected absolute path, got: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            return current
    return None


def _resolve_report_path(text: str) -> Path:
    if not text or "\x00" in text:
        raise GateError("--report must be a non-empty filesystem path")
    expanded = Path(text).expanduser()
    candidate = expanded if expanded.is_absolute() else Path.cwd() / expanded
    candidate = Path(os.path.abspath(os.fspath(candidate)))
    symlink = _first_existing_symlink_component(candidate)
    if symlink is not None:
        raise GateError(f"--report may not pass through a symlink: {symlink}")
    resolved = candidate.resolve(strict=False)
    if resolved == SOURCE_ROOT_RESOLVED or SOURCE_ROOT_RESOLVED in resolved.parents:
        raise GateError("--report must resolve outside the immutable overlay bundle")
    if not candidate.parent.is_dir():
        raise GateError("--report parent directory must already exist")
    if candidate.exists() and (candidate.is_symlink() or not candidate.is_file()):
        raise GateError("--report target must be absent or an existing regular file")
    return candidate


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    parent_stat = path.parent.lstat()
    if stat.S_ISLNK(parent_stat.st_mode) or not stat.S_ISDIR(parent_stat.st_mode):
        raise GateError("--report parent must be a real directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    parent_fd = os.open(path.parent, flags)
    temporary_name = f".overlay-gate-report.{secrets.token_hex(16)}.tmp"
    created = False
    try:
        opened_parent = os.fstat(parent_fd)
        if (opened_parent.st_dev, opened_parent.st_ino) != (
            parent_stat.st_dev,
            parent_stat.st_ino,
        ):
            raise GateError("--report parent changed while opening")
        out_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
        out_fd = os.open(temporary_name, out_flags, 0o600, dir_fd=parent_fd)
        created = True
        try:
            view = memoryview(encoded)
            offset = 0
            while offset < len(view):
                written = os.write(out_fd, view[offset:])
                if written <= 0:
                    raise GateError("short write while creating --report")
                offset += written
            os.fchmod(out_fd, 0o644)
            os.fsync(out_fd)
        finally:
            os.close(out_fd)
        os.replace(temporary_name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        created = False
        os.fsync(parent_fd)
    finally:
        if created:
            try:
                os.unlink(temporary_name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
        os.close(parent_fd)


def _profile_summary(profile: dict[str, Any], recovery: dict[str, Any]) -> str:
    return (
        f"partial ({profile['canonical_exact_files_present']} exact at path; "
        f"{recovery['canonical_recovery_object_files']} additional exact recovery objects; "
        f"{recovery['canonical_rehydratable_files']}/{profile['canonical_index_files']} "
        f"files rehydratable; {recovery['canonical_mismatched_files_unresolved']} "
        "same-path mismatch unresolved)"
    )


def _snapshot_metadata(snapshot: VerifiedExecutionSnapshot) -> dict[str, Any]:
    return {
        "status": "verified_private_snapshot",
        "source_root": SOURCE_ROOT.name,
        "source_root_device": snapshot.source_anchor.device,
        "source_root_inode": snapshot.source_anchor.inode,
        "overlay_manifest_sha256": snapshot.manifest_sha256,
        "inventory_sha256": snapshot.inventory_sha256,
        "file_count": snapshot.file_count,
        "total_bytes": snapshot.total_bytes,
        "read_only": True,
        "isolated_python": True,
        "python_environment_sanitized": True,
        "children_execute_source_paths": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the current EvidenceVault overlay gate.")
    parser.add_argument("--json", action="store_true", help="emit one JSON result object")
    parser.add_argument("--list", action="store_true", help="list configured checks without running them")
    parser.add_argument("--check", action="append", default=[], help="run only the named check; repeatable")
    parser.add_argument("--report", help="atomically write JSON outside the immutable overlay bundle")
    parser.add_argument("--timeout", type=int, help="override each check timeout in seconds (1..1800)")
    args = parser.parse_args()
    if args.timeout is not None and not 1 <= args.timeout <= 1800:
        parser.error("--timeout must be between 1 and 1800")

    snapshot: VerifiedExecutionSnapshot | None = None
    payload: dict[str, Any] | None = None
    return_code = 2
    try:
        report_path = _resolve_report_path(args.report) if args.report else None
        snapshot = _capture_verified_execution_snapshot()
        root = snapshot.root
        manifest = _load_json_file(root, PATCH_MANIFEST_REL)
        profile, recovery_profile = _load_profiles(root, manifest)
        checks = _load_checks(root, manifest)
        selected, selection = _select_checks(checks, args.check)

        if args.list:
            payload = {
                "project": manifest.get("project"),
                "overlay_revision": manifest.get("overlay_revision"),
                "archive_name": manifest.get("archive_name"),
                "mode": "list",
                **selection,
                "representation_profile": profile,
                "recovery_profile": recovery_profile,
                "execution_snapshot": _snapshot_metadata(snapshot),
                "checks": [
                    {
                        "id": row["id"],
                        "description": row["description"],
                        "command": row["logical_command"],
                        "timeout_seconds": row["timeout_seconds"],
                    }
                    for row in selected
                ],
            }
            return_code = 0
        else:
            integrity = selected[0]
            results: list[dict[str, Any]] = [
                _run_check(integrity, root, args.timeout, "preflight")
            ]
            aborted = results[0]["status"] != "pass"
            if not aborted:
                for row in selected[1:]:
                    results.append(_run_check(row, root, args.timeout, "main"))
                if len(selected) > 1:
                    results.append(_run_check(integrity, root, args.timeout, "postflight"))
            failed = [row for row in results if row["status"] != "pass"]
            payload = {
                "project": manifest.get("project"),
                "overlay_revision": manifest.get("overlay_revision"),
                "archive_name": manifest.get("archive_name"),
                "mode": "run",
                **selection,
                "status": "pass" if not failed else "fail",
                "overlay_integrity_status": (
                    "pass"
                    if results
                    and results[0]["status"] == "pass"
                    and (
                        len(selected) == 1
                        or (
                            results[-1]["id"] == INTEGRITY_CHECK_ID
                            and results[-1]["status"] == "pass"
                        )
                    )
                    else "fail"
                ),
                "aborted_after_preflight": aborted,
                "configured_check_count": len(selected),
                "execution_count": len(results),
                "passed_executions": len(results) - len(failed),
                "failed_executions": len(failed),
                "representation_profile": profile,
                "recovery_profile": recovery_profile,
                "execution_snapshot": _snapshot_metadata(snapshot),
                "results": results,
            }
            return_code = 0 if not failed else 1

        # The configured integrity command checks the snapshot as ordinary gate
        # work.  These bootstrap checks independently bind both roots to the exact
        # inventory that was captured before any child process ran.
        _verify_inventory(
            snapshot.snapshot_anchor,
            expected_manifest_sha256=snapshot.manifest_sha256,
            expected_inventory_sha256=snapshot.inventory_sha256,
        )
        _verify_inventory(
            snapshot.source_anchor,
            expected_manifest_sha256=snapshot.manifest_sha256,
            expected_inventory_sha256=snapshot.inventory_sha256,
        )
        payload["execution_snapshot"]["snapshot_postflight"] = "pass"
        payload["execution_snapshot"]["source_postflight"] = "pass"

        if report_path is not None:
            _atomic_write_json(report_path, payload)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.list:
            label = "full gate" if selection["full_gate"] else "selected checks (not a full gate)"
            print(f"scope: {label}")
            for row in selected:
                print(f"{row['id']}: {' '.join(row['logical_command'])}")
            if selection["postflight_integrity_planned"]:
                print(f"{INTEGRITY_CHECK_ID}: repeated after selected work (postflight)")
            print(
                "execution boundary: verified private read-only snapshot; "
                "isolated Python; source and snapshot postflight verified"
            )
            print(f"canonical availability: {_profile_summary(profile, recovery_profile)}")
        else:
            assert payload is not None
            for row in payload["results"]:
                suffix = f" exit={row['exit_code']}" if row["exit_code"] is not None else ""
                print(
                    f"[{row['status'].upper()}] {row['id']}:{row['phase']} "
                    f"({row['duration_seconds']:.3f}s){suffix}"
                )
                if row["status"] != "pass":
                    detail = (row["stderr"] or row["stdout"]).strip()
                    if detail:
                        print(detail, file=sys.stderr)
            label = "overlay-gate" if selection["full_gate"] else "overlay-check-selection"
            status_label = (
                f"OVERLAY {payload['status'].upper()}"
                if selection["full_gate"]
                else payload["status"].upper()
            )
            disclaimer = "" if selection["full_gate"] else "; NOT A FULL GATE"
            print(
                f"{label}: {status_label} "
                f"({payload['passed_executions']}/{payload['execution_count']} executions passed)"
                f"{disclaimer}; verified-snapshot execution; source+snapshot postflight PASS; "
                f"canonical availability: {_profile_summary(profile, recovery_profile)}"
            )
        return return_code
    except (GateError, OSError, subprocess.SubprocessError) as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"overlay-gate: ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if snapshot is not None:
            snapshot.close()


if __name__ == "__main__":
    raise SystemExit(main())
