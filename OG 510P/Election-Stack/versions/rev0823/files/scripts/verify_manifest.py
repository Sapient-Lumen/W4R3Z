#!/usr/bin/env python3
"""Verify an extracted Election Stack release tree against MANIFEST.sha256.

This verifier is for recipients who have an extracted archive tree rather than
(or in addition to) the original ZIP artifact.  It checks strict manifest syntax,
release-path safety, portable namespace uniqueness, hash closure, regular-file
status, canonical file and directory modes including the extraction root, and
that no release-scope files or stray release-scope directories are present
outside MANIFEST.sha256.

It is stdlib-only and does not rewrite the tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

import build_manifest
import release_control_files
import release_path_policy

MANIFEST_NAME = release_control_files.MANIFEST_NAME
VERSION_NAME = release_control_files.VERSION_NAME
CANONICAL_FILE_MODE = 0o644
CANONICAL_DIR_MODE = 0o755
CANONICAL_ROOT_DIR_MODE = CANONICAL_DIR_MODE


@dataclass
class ManifestVerifyResult:
    ok: bool
    root: str
    manifest_entries: int
    release_files: int
    release_dirs: int = 0
    problems: list[str] = field(default_factory=list)


def sha256_file(path: Path) -> str:
    """Return SHA-256 for a concrete path kept for compatibility."""

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest_text(text: str) -> tuple[dict[str, str], list[str]]:
    """Compatibility wrapper for older callers; prefer parse_manifest_bytes."""

    return release_control_files.parse_manifest_bytes(text.encode("utf-8"))


def parse_manifest_bytes(raw: bytes) -> tuple[dict[str, str], list[str]]:
    """Parse MANIFEST.sha256 bytes through the shared control-file parser."""

    return release_control_files.parse_manifest_bytes(raw)


def _read_manifest(root: Path) -> tuple[dict[str, str], list[str]]:
    path = root / MANIFEST_NAME
    if not path.exists():
        return {}, [f"missing {MANIFEST_NAME}"]
    if path.is_symlink():
        return {}, [f"{MANIFEST_NAME} must be a regular file, not a symlink"]
    if not path.is_file():
        return {}, [f"{MANIFEST_NAME} must be a regular file"]
    try:
        raw = build_manifest.read_manifest_member_bytes(root, MANIFEST_NAME)
    except SystemExit as exc:
        return {}, [f"could not read {MANIFEST_NAME}: {exc}"]
    except OSError as exc:
        return {}, [f"could not read {MANIFEST_NAME}: {exc}"]
    return parse_manifest_bytes(raw)


def _path_text(path_arg: Any) -> str:
    """Return an operator-supplied path string without pathlib normalization."""

    try:
        return os.fsdecode(os.fspath(path_arg))
    except TypeError:
        return str(path_arg)


def _lexical_absolute(path: Path) -> Path:
    """Return an absolute path without resolving symlink components."""

    return Path(os.path.abspath(os.fspath(path)))


def _verification_root_lexical_problems(root_arg: Any) -> list[str]:
    """Return problems if the raw verifier root spelling is ambiguous."""

    raw = _path_text(root_arg)
    if raw == "":
        return ["verification root path must not be empty"]
    if "\x00" in raw:
        return ["verification root path must not contain NUL bytes"]

    seps = [os.sep]
    if os.altsep and os.altsep not in seps:
        seps.append(os.altsep)

    if len(raw) > 1 and any(raw.endswith(sep) for sep in seps):
        return [f"verification root path must not have a trailing separator: {raw!r}"]

    normalized = raw
    for sep in seps:
        if sep != "/":
            normalized = normalized.replace(sep, "/")

    parts = normalized.split("/")
    for idx, part in enumerate(parts):
        if idx == 0 and part == "":
            continue
        if part == "":
            return [f"verification root path must not contain empty separator components: {raw!r}"]
        if part in {".", ".."}:
            return [f"verification root path must not contain current/parent traversal components: {raw!r}"]
    return []


def _verification_root_component_problems(root_arg: Any) -> list[str]:
    """Return problems when the verifier root is symlink-routed.

    ``Path.resolve()`` follows symlinks.  The extracted-tree verifier is the
    recipient-side proof that a concrete directory tree has the canonical
    release shape, so it must not silently accept a symlink root or symlinked
    ancestry and then verify the target under a different path.
    """

    absolute = _lexical_absolute(Path(_path_text(root_arg)))
    problems: list[str] = []
    chain = [absolute, *absolute.parents]
    for component in reversed(chain):
        try:
            is_link = component.is_symlink()
        except OSError as exc:
            problems.append(f"could not inspect verification root component {component}: {exc}")
            continue
        if is_link:
            problems.append(f"verification root must not traverse symlink component: {component}")
            break
    return problems


def _safe_dest(root: Path, rel: str) -> Path | None:
    dest = release_path_policy.safe_extract_destination(root, rel)
    if dest is None:
        return None
    return dest


def iter_release_scope(root: Path) -> tuple[set[str], set[str], list[str]]:
    """Return release-scope files, directories, and tree-shape problems.

    Walk with ``followlinks=False`` and check symlink entries explicitly.  The
    manifest is a hash over bytes in the extracted tree, so release-scope
    entries must be ordinary files and ordinary directories, not links or local
    filesystem-dependent nodes.  Directory names are not hashed, but their
    presence and mode are part of the canonical extracted release tree shape.
    """

    files: set[str] = set()
    dirs: set[str] = set()
    problems: list[str] = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(dirpath)

        for dirname in list(dirnames):
            p = current / dirname
            rel = p.relative_to(root).as_posix()
            if build_manifest.is_local_only_rel(rel):
                # Do not traverse local-only cache/output trees while verifying
                # release closure; they are deliberately outside the artifact.
                dirnames.remove(dirname)
                continue
            path_problem = build_manifest.governed_path_problem(rel)
            if path_problem:
                problems.append(f"unsafe release-scope directory present: {rel}: {path_problem}")
                dirnames.remove(dirname)
                continue
            if p.is_symlink():
                if build_manifest.should_include_rel(rel):
                    problems.append(f"release-scope symlink directory present: {rel}")
                dirnames.remove(dirname)
                continue
            if not p.is_dir():
                problems.append(f"release-scope directory path is not a directory: {rel}")
                dirnames.remove(dirname)
                continue
            try:
                mode = p.stat(follow_symlinks=False).st_mode & 0o777
            except OSError as exc:
                problems.append(f"release-scope directory mode could not be inspected: {rel}: {exc}")
            else:
                if mode != CANONICAL_DIR_MODE:
                    problems.append(
                        f"release-scope directory mode is not canonical 0755: {rel}: {oct(mode)}"
                    )
            dirs.add(rel)

        for filename in filenames:
            p = current / filename
            rel = p.relative_to(root).as_posix()
            if build_manifest.is_local_only_rel(rel):
                continue
            path_problem = build_manifest.governed_path_problem(rel)
            if path_problem:
                problems.append(f"unsafe release-scope file present: {rel}: {path_problem}")
                continue
            if not build_manifest.should_include_rel(rel):
                continue
            if p.is_symlink():
                problems.append(f"release-scope symlink file present: {rel}")
                continue
            if not p.is_file():
                problems.append(f"release-scope path is not a regular file: {rel}")
                continue
            try:
                mode = p.stat(follow_symlinks=False).st_mode & 0o777
            except OSError as exc:
                problems.append(f"release-scope file mode could not be inspected: {rel}: {exc}")
            else:
                if mode != CANONICAL_FILE_MODE:
                    problems.append(
                        f"release-scope file mode is not canonical 0644: {rel}: {oct(mode)}"
                    )
            files.add(rel)

    collisions = release_path_policy.find_portable_path_collisions(files)
    for key, vals in sorted(collisions.items()):
        problems.append(f"release-scope portable path collision for {key!r}: {', '.join(vals)}")

    shape_conflicts = release_path_policy.find_extraction_shape_conflicts(files)
    for prefix, children in sorted(shape_conflicts.items()):
        problems.append(
            f"release-scope extraction shape conflict: file path {prefix!r} also prefixes {', '.join(children)}"
        )

    return files, dirs, problems


def expected_release_dirs(paths: set[str]) -> set[str]:
    """Return directory prefixes required by manifest file paths."""

    dirs: set[str] = set()
    for rel in paths:
        parts = rel.split('/')[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add('/'.join(parts[:i]))
    return dirs


def _version_problems(root: Path, release_files: set[str]) -> list[str]:
    problems: list[str] = []
    if VERSION_NAME not in release_files:
        return [f"missing {VERSION_NAME} file"]
    dest = _safe_dest(root, VERSION_NAME)
    if dest is None:
        return [f"{VERSION_NAME}: unsafe release path"]
    try:
        raw = build_manifest.read_manifest_member_bytes(root, VERSION_NAME)
    except SystemExit as exc:
        return [f"could not read {VERSION_NAME}: {exc}"]
    except OSError as exc:
        return [f"could not read {VERSION_NAME}: {exc}"]
    _version, version_problems = release_control_files.parse_version_bytes(raw)
    problems.extend(version_problems)
    return problems


def verify_tree(root: Path | str) -> ManifestVerifyResult:
    root_input = root
    root_arg = Path(_path_text(root_input))
    root = _lexical_absolute(root_arg)
    problems: list[str] = _verification_root_lexical_problems(root_input)
    if not problems:
        problems.extend(_verification_root_component_problems(root_input))
    if problems:
        return ManifestVerifyResult(False, str(root), 0, 0, problems=problems)
    if not root.exists():
        return ManifestVerifyResult(False, str(root), 0, 0, problems=[f"root does not exist: {root}"])
    if not root.is_dir():
        return ManifestVerifyResult(False, str(root), 0, 0, problems=[f"root is not a directory: {root}"])
    try:
        root_mode = root.stat(follow_symlinks=False).st_mode & 0o777
    except OSError as exc:
        problems.append(f"extraction root mode could not be inspected: {exc}")
    else:
        if root_mode != CANONICAL_ROOT_DIR_MODE:
            problems.append(
                f"extraction root directory mode is not canonical 0755: {oct(root_mode)}"
            )

    manifest_entries, manifest_problems = _read_manifest(root)
    problems.extend(manifest_problems)

    release_files, release_dirs, scope_problems = iter_release_scope(root)
    problems.extend(scope_problems)
    problems.extend(_version_problems(root, release_files))

    manifest_paths = set(manifest_entries)
    expected_dirs = expected_release_dirs(manifest_paths)
    extra_dirs = sorted(release_dirs - expected_dirs)
    if extra_dirs:
        problems.append("release-scope directories not implied by MANIFEST.sha256: " + ", ".join(extra_dirs[:20]))

    manifest_paths = set(manifest_entries)
    missing = sorted(manifest_paths - release_files)
    unlisted = sorted(release_files - manifest_paths)
    if missing:
        problems.append("manifest entries missing from extracted tree: " + ", ".join(missing[:20]))
    if unlisted:
        problems.append("release-scope files not listed in MANIFEST.sha256: " + ", ".join(unlisted[:20]))

    for rel, expected in manifest_entries.items():
        dest = _safe_dest(root, rel)
        if dest is None:
            continue
        if rel not in release_files:
            # Already reported as missing/symlink/non-regular above.
            continue
        try:
            actual = build_manifest.file_sha256_for_rel(root, rel)
        except SystemExit as exc:
            problems.append(f"{rel}: could not read for SHA-256: {exc}")
            continue
        except OSError as exc:
            problems.append(f"{rel}: could not read for SHA-256: {exc}")
            continue
        if actual != expected:
            problems.append(f"{rel}: sha256 mismatch manifest={expected} actual={actual}")

    return ManifestVerifyResult(
        ok=not problems,
        root=str(root),
        manifest_entries=len(manifest_entries),
        release_files=len(release_files),
        release_dirs=len(release_dirs),
        problems=problems,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify an extracted Election Stack tree against MANIFEST.sha256")
    ap.add_argument("root", nargs="?", default=None, help="extracted release tree root (default: current working directory)")
    ap.add_argument("--quiet", action="store_true", help="only print failures")
    ap.add_argument("--json", action="store_true", help="emit a machine-readable summary")
    args = ap.parse_args()

    root_arg = Path.cwd() if args.root is None else args.root
    result = verify_tree(root_arg)
    if args.json:
        print(json.dumps({
            "ok": result.ok,
            "root": result.root,
            "manifest_entries": result.manifest_entries,
            "release_files": result.release_files,
            "release_dirs": result.release_dirs,
            "problems": result.problems,
        }, sort_keys=True))
        return 0 if result.ok else 2

    if result.ok:
        if not args.quiet:
            print(
                "PASS: extracted tree verified against MANIFEST.sha256 "
                f"(manifest_entries={result.manifest_entries}, release_files={result.release_files}, "
                f"release_dirs={result.release_dirs})"
            )
        return 0

    print("FAIL: extracted tree manifest verification failed", file=sys.stderr)
    for problem in result.problems[:100]:
        print(f"  - {problem}", file=sys.stderr)
    if len(result.problems) > 100:
        print(f"  ... {len(result.problems) - 100} more", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
