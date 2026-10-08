#!/usr/bin/env python3
"""Compute live EvidenceVault canonical-index representation coverage.

The overlay manifest protects the files that are shipped. This module answers a
different question: how many paths and bytes named by INDEX/files.csv are
materialized at their canonical paths, and how many are absent, divergent, or
preserved only as content-addressed recovery objects.

Gate-critical reads are descriptor-bound snapshots. Every path component is
opened beneath a real root without following symlinks; the opened file must stay
regular and metadata-stable while read; and a fresh no-follow lookup must still
resolve to the same identity afterward. This prevents pathname prechecks and
later hashes from silently referring to different bytes.
"""
from __future__ import annotations

import argparse
import csv
import errno
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, BinaryIO, Iterable, Iterator

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

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_COLUMNS = {"path", "size", "sha256"}
RECOVERY_INVENTORY_REL = "RECOVERY/canonical-index/inventory.json"
CHUNK_SIZE = 1024 * 1024


class CoverageError(RuntimeError):
    """Raised when the canonical index or tree is unsafe or malformed."""


def clean_rel_path(text: Any, label: str) -> str:
    try:
        return clean_anchored_relative_path(text, label)
    except RootAnchorError as exc:
        raise CoverageError(str(exc)) from exc


def _prepare_root_anchor(root: Path | RootAnchor) -> RootAnchor:
    try:
        return capture_root(root)
    except RootAnchorError as exc:
        raise CoverageError(str(exc)) from exc


def prepare_root(root: Path | RootAnchor) -> Path:
    """Compatibility wrapper returning the currently anchored absolute path."""
    return _prepare_root_anchor(root).path

def _assert_no_symlink_components(root: Path, target: Path, label: str) -> None:
    """Compatibility precheck; descriptor-bound reads enforce the actual boundary."""
    try:
        rel = target.relative_to(root)
    except ValueError as exc:
        raise CoverageError(f"{label} escapes root: {target}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise CoverageError(
                f"{label} resolves through a symlink component: "
                f"{cursor.relative_to(root).as_posix()}"
            )


def _dir_open_flags() -> int:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    return flags


def _file_open_flags() -> int:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    return flags


def _component_identity(st: os.stat_result) -> tuple[int, int, int]:
    return (st.st_dev, st.st_ino, stat.S_IFMT(st.st_mode))


def _open_verified_component(
    parent_fd: int,
    name: str,
    flags: int,
    label: str,
    *,
    require_directory: bool,
) -> int:
    """Open one component and prove no symlink or identity substitution occurred.

    Some container/filesystem combinations do not enforce O_NOFOLLOW for a
    directory symlink as expected. Therefore every component is lstat-checked
    before and after open, and the opened descriptor must identify the same
    inode and file type.
    """
    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if stat.S_ISLNK(before.st_mode):
        raise CoverageError(f"{label} contains a symlink component: {name}")
    if require_directory and not stat.S_ISDIR(before.st_mode):
        raise CoverageError(f"{label} contains a non-directory component: {name}")
    if not require_directory and not stat.S_ISREG(before.st_mode):
        raise CoverageError(f"{label} is not a regular file: {name}")
    opened_fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        opened = os.fstat(opened_fd)
        after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        expected = _component_identity(before)
        if _component_identity(opened) != expected or _component_identity(after) != expected:
            raise CoverageError(f"{label} component identity changed during open: {name}")
        if require_directory and not stat.S_ISDIR(opened.st_mode):
            raise CoverageError(f"{label} opened component is not a directory: {name}")
        if not require_directory and not stat.S_ISREG(opened.st_mode):
            raise CoverageError(f"{label} opened target is not a regular file: {name}")
        return opened_fd
    except Exception:
        os.close(opened_fd)
        raise


def _open_beneath(
    root: RootAnchor, rel: str, label: str
) -> tuple[int, list[int]]:
    """Open a relative regular file beneath root with verified components.

    FileNotFoundError is deliberately propagated so callers can classify an
    indexed canonical path as absent. Other failures are unsafe/malformed tree
    conditions and become CoverageError.
    """
    clean = clean_rel_path(rel, label)
    parts = PurePosixPath(clean).parts
    directory_fds: list[int] = []
    file_fd: int | None = None
    try:
        try:
            root_fd = open_anchored_root(root)
        except RootAnchorError as exc:
            raise CoverageError(str(exc)) from exc
        directory_fds.append(root_fd)
        for part in parts[:-1]:
            next_fd = _open_verified_component(
                directory_fds[-1],
                part,
                _dir_open_flags(),
                label,
                require_directory=True,
            )
            directory_fds.append(next_fd)
        file_fd = _open_verified_component(
            directory_fds[-1],
            parts[-1],
            _file_open_flags(),
            label,
            require_directory=False,
        )
        return file_fd, directory_fds
    except FileNotFoundError:
        if file_fd is not None:
            os.close(file_fd)
        for fd in reversed(directory_fds):
            os.close(fd)
        raise
    except CoverageError:
        if file_fd is not None:
            os.close(file_fd)
        for fd in reversed(directory_fds):
            os.close(fd)
        raise
    except OSError as exc:
        if file_fd is not None:
            os.close(file_fd)
        for fd in reversed(directory_fds):
            os.close(fd)
        detail = os.strerror(exc.errno) if exc.errno else str(exc)
        raise CoverageError(f"cannot open {label} without following symlinks: {detail}") from exc


def _identity(st: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        st.st_dev,
        st.st_ino,
        st.st_mode,
        st.st_nlink,
        st.st_size,
        st.st_mtime_ns,
        st.st_ctime_ns,
    )


def _iter_file_chunks(handle: BinaryIO) -> Iterator[bytes]:
    """Yield chunks for snapshot hashing; kept separate for adversarial tests."""
    while True:
        chunk = handle.read(CHUNK_SIZE)
        if not chunk:
            return
        yield chunk


def _fresh_identity(root: RootAnchor, rel: str, label: str) -> tuple[int, int, int, int, int, int, int]:
    fd, directory_fds = _open_beneath(root, rel, label)
    try:
        current = os.fstat(fd)
        if not stat.S_ISREG(current.st_mode):
            raise CoverageError(f"{label} is not a regular file: {rel}")
        return _identity(current)
    finally:
        os.close(fd)
        for directory_fd in reversed(directory_fds):
            os.close(directory_fd)


def _snapshot_regular_file_prepared(
    root: RootAnchor,
    rel: str,
    label: str,
    *,
    capture_bytes: bool = False,
) -> dict[str, Any]:
    """Hash one file beneath one stable, identity-bound root."""
    rel = clean_rel_path(rel, label)
    try:
        fd, directory_fds = _open_beneath(root, rel, label)
    except FileNotFoundError:
        try:
            assert_anchored_root_path(root)
        except RootAnchorError as exc:
            raise CoverageError(str(exc)) from exc
        raise
    captured: list[bytes] | None = [] if capture_bytes else None
    digest = hashlib.sha256()
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise CoverageError(f"{label} is not a regular file: {rel}")
        try:
            with os.fdopen(fd, "rb", closefd=False) as handle:
                for chunk in _iter_file_chunks(handle):
                    digest.update(chunk)
                    if captured is not None:
                        captured.append(chunk)
        except OSError as exc:
            raise CoverageError(f"cannot read {label}: {exc}") from exc
        after = os.fstat(fd)
        if _identity(before) != _identity(after):
            raise CoverageError(f"{label} changed while it was being read: {rel}")
    finally:
        os.close(fd)
        for directory_fd in reversed(directory_fds):
            os.close(directory_fd)

    fresh = _fresh_identity(root, rel, label)
    if fresh != _identity(after):
        raise CoverageError(f"{label} path identity changed during snapshot: {rel}")
    try:
        assert_anchored_root_path(root)
    except RootAnchorError as exc:
        raise CoverageError(str(exc)) from exc
    result: dict[str, Any] = {
        "path": rel,
        "size": after.st_size,
        "sha256": digest.hexdigest(),
        "identity": fresh,
    }
    if captured is not None:
        result["bytes"] = b"".join(captured)
    return result


def snapshot_regular_file(
    root: Path | RootAnchor,
    rel: str,
    label: str,
    *,
    capture_bytes: bool = False,
) -> dict[str, Any]:
    """Hash one regular file as a stable, descriptor-bound snapshot."""
    return _snapshot_regular_file_prepared(
        _prepare_root_anchor(root),
        rel,
        label,
        capture_bytes=capture_bytes,
    )

def sha256_file(path: Path) -> str:
    """Compatibility helper for callers outside the coverage trust path."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in _iter_file_chunks(handle):
            digest.update(chunk)
    return digest.hexdigest()


def _load_index_prepared(root: RootAnchor, index_rel: str) -> list[dict[str, Any]]:
    index_rel = clean_rel_path(index_rel, "index path")
    try:
        snapshot = _snapshot_regular_file_prepared(
            root,
            index_rel,
            "canonical index",
            capture_bytes=True,
        )
    except FileNotFoundError as exc:
        raise CoverageError(f"canonical index is missing: {index_rel}") from exc
    try:
        text = snapshot["bytes"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CoverageError(f"canonical index is not UTF-8: {index_rel}: {exc}") from exc

    reader = csv.DictReader(io.StringIO(text, newline=""))
    fieldnames = reader.fieldnames
    if fieldnames is None or not REQUIRED_COLUMNS.issubset(fieldnames):
        raise CoverageError(
            f"canonical index must contain columns {sorted(REQUIRED_COLUMNS)}; found {fieldnames}"
        )
    if len(fieldnames) != len(set(fieldnames)):
        raise CoverageError(f"canonical index contains duplicate column names: {fieldnames}")

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(reader, start=2):
        if None in raw:
            raise CoverageError(f"canonical index has extra unnamed cells at {index_rel}:{line_no}")
        rel = clean_rel_path(raw.get("path"), f"{index_rel}:{line_no} path")
        if rel in seen:
            raise CoverageError(f"duplicate canonical index path at line {line_no}: {rel}")
        seen.add(rel)
        size_text = raw.get("size")
        try:
            size = int(size_text) if size_text is not None else -1
        except ValueError as exc:
            raise CoverageError(
                f"invalid canonical size at {index_rel}:{line_no}: {size_text!r}"
            ) from exc
        if size < 0:
            raise CoverageError(f"negative canonical size at {index_rel}:{line_no}: {size}")
        digest = raw.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise CoverageError(
                f"invalid canonical SHA-256 at {index_rel}:{line_no}: {digest!r}"
            )
        rows.append(
            {
                "path": rel,
                "size": size,
                "sha256": digest,
                "category": raw.get("category", ""),
                "project": raw.get("project", ""),
                "ext": raw.get("ext", ""),
            }
        )
    return rows


def load_index(root: Path | RootAnchor, index_rel: str = "INDEX/files.csv") -> list[dict[str, Any]]:
    return _load_index_prepared(_prepare_root_anchor(root), index_rel)

def _compute_coverage_prepared(
    root: RootAnchor,
    rows: list[dict[str, Any]],
    *,
    include_paths: bool,
) -> dict[str, Any]:
    exact_files = 0
    exact_bytes = 0
    mismatch_files = 0
    missing_files = 0
    source_files = 0
    source_exact_files = 0
    status_paths: dict[str, list[str]] = {"exact": [], "mismatch": [], "missing": []}

    for row in rows:
        rel = row["path"]
        is_source = rel.startswith("sources/")
        if is_source:
            source_files += 1
        try:
            snapshot = _snapshot_regular_file_prepared(root, rel, f"indexed path {rel}")
        except FileNotFoundError:
            status = "missing"
            missing_files += 1
        else:
            if snapshot["size"] == row["size"] and snapshot["sha256"] == row["sha256"]:
                status = "exact"
                exact_files += 1
                exact_bytes += row["size"]
                if is_source:
                    source_exact_files += 1
            else:
                status = "mismatch"
                mismatch_files += 1
        if include_paths:
            status_paths[status].append(rel)

    result: dict[str, Any] = {
        "kind": "partial_overlay" if missing_files or mismatch_files else "complete_canonical_tree",
        "canonical_index_files": len(rows),
        "canonical_index_bytes": sum(row["size"] for row in rows),
        "canonical_exact_files_present": exact_files,
        "canonical_exact_bytes_present": exact_bytes,
        "canonical_mismatched_files_present": mismatch_files,
        "canonical_missing_files": missing_files,
        "canonical_source_files": source_files,
        "canonical_source_exact_files_present": source_exact_files,
    }
    if include_paths:
        result["paths"] = status_paths
    return result


def compute_coverage(
    root: Path | RootAnchor = DEFAULT_ROOT,
    *,
    index_rel: str = "INDEX/files.csv",
    include_paths: bool = False,
) -> dict[str, Any]:
    prepared = _prepare_root_anchor(root)
    rows = _load_index_prepared(prepared, index_rel)
    result = _compute_coverage_prepared(prepared, rows, include_paths=include_paths)
    try:
        assert_anchored_root_path(prepared)
    except RootAnchorError as exc:
        raise CoverageError(str(exc)) from exc
    return result


def _compute_recovery_prepared(
    root: RootAnchor,
    rows: list[dict[str, Any]],
    live: dict[str, Any],
    *,
    index_rel: str,
    inventory_rel: str,
    include_paths: bool,
) -> dict[str, Any]:
    by_path = {row["path"]: row for row in rows}
    status_by_path = {
        rel: status
        for status, paths in live["paths"].items()
        for rel in paths
    }

    inventory_rel = clean_rel_path(inventory_rel, "recovery inventory path")
    try:
        inventory_snapshot = _snapshot_regular_file_prepared(
            root,
            inventory_rel,
            "recovery inventory",
            capture_bytes=True,
        )
    except FileNotFoundError as exc:
        raise CoverageError(f"recovery inventory is missing: {inventory_rel}") from exc
    try:
        inventory = json.loads(inventory_snapshot["bytes"].decode("utf-8"))
    except Exception as exc:
        raise CoverageError(f"invalid recovery inventory {inventory_rel}: {exc}") from exc
    if not isinstance(inventory, dict) or not isinstance(inventory.get("entries"), list):
        raise CoverageError("recovery inventory must be an object with an entries array")

    recovery_paths: list[str] = []
    recovery_bytes = 0
    source_recovery_files = 0
    seen: set[str] = set()
    for position, raw in enumerate(inventory["entries"]):
        if not isinstance(raw, dict):
            raise CoverageError(f"recovery inventory entry {position} is not an object")
        rel = clean_rel_path(raw.get("path"), f"recovery inventory entry {position} path")
        if rel in seen:
            raise CoverageError(f"duplicate recovery inventory path: {rel}")
        seen.add(rel)
        row = by_path.get(rel)
        if row is None:
            raise CoverageError(f"recovery inventory path is absent from canonical index: {rel}")
        if raw.get("size") != row["size"] or raw.get("sha256") != row["sha256"]:
            raise CoverageError(f"recovery inventory identity differs from canonical index: {rel}")
        object_rel = clean_rel_path(
            raw.get("object_path"),
            f"recovery inventory entry {position} object_path",
        )
        expected_object = f"RECOVERY/canonical-index/objects/sha256/{row['sha256']}"
        if object_rel != expected_object:
            raise CoverageError(f"recovery object path is not content-addressed: {rel}")
        try:
            object_snapshot = _snapshot_regular_file_prepared(root, object_rel, f"recovery object {rel}")
        except FileNotFoundError as exc:
            raise CoverageError(f"recovery object is missing: {object_rel}") from exc
        if object_snapshot["size"] != row["size"] or object_snapshot["sha256"] != row["sha256"]:
            raise CoverageError(f"recovery object does not match canonical index: {rel}")
        if status_by_path.get(rel) == "exact":
            raise CoverageError(f"recovery inventory redundantly counts an at-path exact file: {rel}")
        recovery_paths.append(rel)
        recovery_bytes += row["size"]
        if rel.startswith("sources/"):
            source_recovery_files += 1

    if inventory.get("recovered_files") != len(recovery_paths):
        raise CoverageError("recovery inventory recovered_files count is stale")
    if inventory.get("recovered_bytes") != recovery_bytes:
        raise CoverageError("recovery inventory recovered_bytes count is stale")
    try:
        index_snapshot = _snapshot_regular_file_prepared(root, index_rel, "canonical index digest")
    except FileNotFoundError as exc:
        raise CoverageError(f"canonical index is missing: {index_rel}") from exc
    if inventory.get("canonical_index_sha256") != index_snapshot["sha256"]:
        raise CoverageError("recovery inventory canonical index digest is stale")

    recovery_set = set(recovery_paths)
    mismatch_set = set(live["paths"]["mismatch"])
    missing_set = set(live["paths"]["missing"])
    rehydratable_files = live["canonical_exact_files_present"] + len(recovery_paths)
    rehydratable_bytes = live["canonical_exact_bytes_present"] + recovery_bytes
    result: dict[str, Any] = {
        "kind": "partial_recovery_overlay"
        if rehydratable_files < live["canonical_index_files"]
        else "complete_rehydratable_tree",
        "canonical_index_files": live["canonical_index_files"],
        "canonical_index_bytes": live["canonical_index_bytes"],
        "canonical_at_path_exact_files": live["canonical_exact_files_present"],
        "canonical_at_path_exact_bytes": live["canonical_exact_bytes_present"],
        "canonical_recovery_object_files": len(recovery_paths),
        "canonical_recovery_object_bytes": recovery_bytes,
        "canonical_rehydratable_files": rehydratable_files,
        "canonical_rehydratable_bytes": rehydratable_bytes,
        "canonical_unavailable_files": live["canonical_index_files"] - rehydratable_files,
        "canonical_unavailable_bytes": live["canonical_index_bytes"] - rehydratable_bytes,
        "canonical_mismatched_files_recoverable": len(mismatch_set & recovery_set),
        "canonical_mismatched_files_unresolved": len(mismatch_set - recovery_set),
        "canonical_missing_files_recoverable": len(missing_set & recovery_set),
        "canonical_missing_files_unresolved": len(missing_set - recovery_set),
        "canonical_source_files": live["canonical_source_files"],
        "canonical_source_rehydratable_files": (
            live["canonical_source_exact_files_present"] + source_recovery_files
        ),
        "recovery_inventory": inventory_rel,
        "recovery_inventory_sha256": inventory_snapshot["sha256"],
    }
    if include_paths:
        result["paths"] = {
            "recovery_objects": sorted(recovery_paths),
            "unresolved_mismatches": sorted(mismatch_set - recovery_set),
            "unresolved_missing": sorted(missing_set - recovery_set),
        }
    return result


def compute_profiles(
    root: Path | RootAnchor = DEFAULT_ROOT,
    *,
    index_rel: str = "INDEX/files.csv",
    inventory_rel: str = RECOVERY_INVENTORY_REL,
    include_paths: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compute representation and recovery profiles from one canonical scan."""
    prepared = _prepare_root_anchor(root)
    index_rel = clean_rel_path(index_rel, "index path")
    rows = _load_index_prepared(prepared, index_rel)
    live = _compute_coverage_prepared(prepared, rows, include_paths=True)
    recovery = _compute_recovery_prepared(
        prepared,
        rows,
        live,
        index_rel=index_rel,
        inventory_rel=inventory_rel,
        include_paths=include_paths,
    )
    if not include_paths:
        live = {key: value for key, value in live.items() if key != "paths"}
    try:
        assert_anchored_root_path(prepared)
    except RootAnchorError as exc:
        raise CoverageError(str(exc)) from exc
    return live, recovery


def compute_recovery_availability(
    root: Path | RootAnchor = DEFAULT_ROOT,
    *,
    index_rel: str = "INDEX/files.csv",
    inventory_rel: str = RECOVERY_INVENTORY_REL,
    include_paths: bool = False,
) -> dict[str, Any]:
    """Compute exact canonical bytes available live or as recovery objects."""
    _, recovery = compute_profiles(
        root,
        index_rel=index_rel,
        inventory_rel=inventory_rel,
        include_paths=include_paths,
    )
    return recovery

def compare_recovery_profile(live: dict[str, Any], declared: dict[str, Any]) -> list[str]:
    keys = (
        "kind",
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
        "recovery_inventory",
        "recovery_inventory_sha256",
    )
    return [
        f"{key}: declared={declared.get(key)!r} live={live.get(key)!r}"
        for key in keys
        if declared.get(key) != live.get(key)
    ]


def compare_profile(live: dict[str, Any], declared: dict[str, Any]) -> list[str]:
    keys = (
        "kind",
        "canonical_index_files",
        "canonical_index_bytes",
        "canonical_exact_files_present",
        "canonical_exact_bytes_present",
        "canonical_mismatched_files_present",
        "canonical_missing_files",
        "canonical_source_files",
        "canonical_source_exact_files_present",
    )
    return [
        f"{key}: declared={declared.get(key)!r} live={live.get(key)!r}"
        for key in keys
        if declared.get(key) != live.get(key)
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--index", default="INDEX/files.csv")
    parser.add_argument("--include-paths", action="store_true")
    parser.add_argument("--include-recovery", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.include_recovery:
            result = compute_recovery_availability(
                args.root,
                index_rel=args.index,
                include_paths=args.include_paths,
            )
        else:
            result = compute_coverage(
                args.root,
                index_rel=args.index,
                include_paths=args.include_paths,
            )
    except CoverageError as exc:
        print(f"canonical-coverage: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.include_recovery:
        print(
            "canonical-recovery-availability: "
            f"rehydratable={result['canonical_rehydratable_files']}/"
            f"{result['canonical_index_files']} "
            f"at_path={result['canonical_at_path_exact_files']} "
            f"objects={result['canonical_recovery_object_files']} "
            f"unavailable={result['canonical_unavailable_files']}"
        )
    else:
        print(
            "canonical-coverage: "
            f"exact={result['canonical_exact_files_present']} "
            f"mismatch={result['canonical_mismatched_files_present']} "
            f"missing={result['canonical_missing_files']} "
            f"indexed={result['canonical_index_files']} "
            f"sources_exact={result['canonical_source_exact_files_present']}/"
            f"{result['canonical_source_files']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
