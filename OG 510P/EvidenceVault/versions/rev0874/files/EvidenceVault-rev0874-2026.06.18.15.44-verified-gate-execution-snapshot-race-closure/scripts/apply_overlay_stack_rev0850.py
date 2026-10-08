#!/usr/bin/env python3
"""Safely validate or apply the EvidenceVault overlay patch stack.

This helper closes a practical completion gap: overlay bundles after rev0840
carried incremental patches, but operators did not have a single guarded command
that proves the patch stack is continuous and applies it to a full canonical tree.

By default the script validates the bundle-local patch chain and patch payload
shapes.  With --target-root it also performs a dry-run application on a temporary
copy of that target.  With --apply it first performs the same temporary dry run
and then applies the patches to the target root.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

try:
    from root_anchor import RootAnchorError, clean_relative_path as clean_anchored_relative_path
except ImportError:  # pragma: no cover - package-style import fallback
    from .root_anchor import RootAnchorError, clean_relative_path as clean_anchored_relative_path

DEFAULT_BUNDLE_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_HANDOFF_REVISION = 840
OVERLAY_PATCH_RE = re.compile(r"^rev(?P<from>\d{4})-to-rev(?P<to>\d{4})-overlay\.patch$")
CURRENT_REVISION_RE = re.compile(r"rev(\d{4})")
PATCH_PATH_PREFIX_RE = re.compile(r"^(?P<prefix>a|b)/(?P<path>.+)$")
PATCH_PATH_HEADERS = ("--- ", "+++ ")
PATCH_RENAME_HEADERS = ("rename from ", "rename to ", "copy from ", "copy to ")


class OverlayApplyError(RuntimeError):
    """Raised when the overlay stack is unsafe or cannot be applied."""


def clean_archive_path(text: str, field: str) -> str:
    """Require one exact archive-relative POSIX spelling from a patch header."""
    if not isinstance(text, str) or not text:
        raise OverlayApplyError(f"{field} must be a non-empty path")
    if text == "/dev/null":
        return text
    match = PATCH_PATH_PREFIX_RE.match(text)
    if match:
        text = match.group("path")
    try:
        return clean_anchored_relative_path(text, field)
    except RootAnchorError as exc:
        raise OverlayApplyError(str(exc)) from exc


def parse_overlay_patch_name(path: Path) -> tuple[int, int] | None:
    match = OVERLAY_PATCH_RE.match(path.name)
    if not match:
        return None
    return int(match.group("from")), int(match.group("to"))


def infer_current_revision(bundle_root: Path) -> int | None:
    candidates = [bundle_root.name]
    checks = bundle_root / "CHECKS"
    if checks.is_dir():
        candidates.extend(path.name for path in checks.glob("patch-bundle-identity-rev*.json"))
    revisions: list[int] = []
    for text in candidates:
        revisions.extend(int(match.group(1)) for match in CURRENT_REVISION_RE.finditer(text))
    return max(revisions) if revisions else None


def assert_no_symlink_components(root: Path, path: Path, label: str) -> None:
    root = root.resolve()
    try:
        rel = path.relative_to(root)
    except ValueError:
        try:
            rel = path.resolve(strict=False).relative_to(root)
        except ValueError as exc:
            raise OverlayApplyError(f"{label} escapes root: {path}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise OverlayApplyError(f"{label} resolves through a symlink component: {cursor.relative_to(root).as_posix()}")


def validate_bundle_root(bundle_root: Path) -> Path:
    bundle_root = bundle_root.resolve()
    if bundle_root.is_symlink() or not bundle_root.is_dir():
        raise OverlayApplyError(f"bundle root must be a real directory: {bundle_root}")
    patches = bundle_root / "PATCHES"
    assert_no_symlink_components(bundle_root, patches, "PATCHES directory")
    if not patches.is_dir():
        raise OverlayApplyError(f"bundle PATCHES directory is missing: {patches}")
    return bundle_root


def patch_files(bundle_root: Path) -> list[Path]:
    patches = []
    for path in sorted((bundle_root / "PATCHES").glob("rev*-to-rev*-overlay.patch")):
        assert_no_symlink_components(bundle_root, path, f"overlay patch {path.name}")
        if not path.is_file():
            raise OverlayApplyError(f"overlay patch is not a regular file: {path.name}")
        if parse_overlay_patch_name(path) is None:
            raise OverlayApplyError(f"overlay patch has invalid name: {path.name}")
        patches.append(path)
    if not patches:
        raise OverlayApplyError("no overlay patches found in PATCHES/")
    return patches


def validate_patch_payload(path: Path) -> dict[str, Any]:
    """Reject path-traversing or binary patch payloads before invoking git."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise OverlayApplyError(f"cannot read patch {path.name}: {exc}") from exc
    if b"\x00" in raw:
        raise OverlayApplyError(f"patch {path.name} contains NUL bytes")
    text = raw.decode("utf-8", errors="replace")
    if re.search(r"(?m)^GIT binary patch$", text):
        raise OverlayApplyError(f"patch {path.name} contains a git binary patch; binary overlay application is not supported by this guard")
    paths: set[str] = set()
    diff_headers = 0
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.startswith("diff --git "):
            diff_headers += 1
            parts = line.split()
            if len(parts) < 4:
                raise OverlayApplyError(f"malformed diff header in {path.name}:{line_no}")
            for token in parts[2:4]:
                clean = clean_archive_path(token, f"{path.name}:{line_no}")
                if clean != "/dev/null":
                    paths.add(clean)
        elif line.startswith(PATCH_PATH_HEADERS):
            token = line[4:].split("\t", 1)[0].strip()
            if token and token != "/dev/null":
                clean = clean_archive_path(token, f"{path.name}:{line_no}")
                paths.add(clean)
        else:
            for header in PATCH_RENAME_HEADERS:
                if line.startswith(header):
                    clean = clean_archive_path(line[len(header):].strip(), f"{path.name}:{line_no}")
                    paths.add(clean)
                    break
    if diff_headers <= 0:
        raise OverlayApplyError(f"patch {path.name} does not contain any git diff headers")
    return {"path": path.name, "diff_headers": diff_headers, "archive_paths_touched": sorted(paths)}


def discover_overlay_chain(
    bundle_root: Path,
    *,
    expected_start_rev: int = CANONICAL_HANDOFF_REVISION,
    expected_end_rev: int | None = None,
) -> dict[str, Any]:
    bundle_root = validate_bundle_root(bundle_root)
    patch_rows: list[dict[str, Any]] = []
    edges: list[tuple[int, int, Path]] = []
    for path in patch_files(bundle_root):
        parsed = parse_overlay_patch_name(path)
        assert parsed is not None
        start, end = parsed
        if end != start + 1:
            raise OverlayApplyError(f"overlay patch is not a one-revision step: {path.name}")
        payload = validate_patch_payload(path)
        patch_rows.append({"from_revision": f"rev{start:04d}", "to_revision": f"rev{end:04d}", **payload})
        edges.append((start, end, path))
    edges.sort(key=lambda row: (row[0], row[1], row[2].name))
    if len({(start, end) for start, end, _ in edges}) != len(edges):
        raise OverlayApplyError("duplicate overlay patch edges found")
    first_from = edges[0][0]
    if first_from != expected_start_rev:
        raise OverlayApplyError(
            f"overlay chain starts at rev{first_from:04d}, expected rev{expected_start_rev:04d}; "
            "missing handoff patch prevents a full canonical application pass"
        )
    for previous, current in zip(edges, edges[1:]):
        if previous[1] != current[0]:
            raise OverlayApplyError(f"overlay patch chain gap: {previous[2].name} then {current[2].name}")
    if expected_end_rev is None:
        expected_end_rev = infer_current_revision(bundle_root)
    if expected_end_rev is not None and edges[-1][1] != expected_end_rev:
        raise OverlayApplyError(f"overlay chain ends at rev{edges[-1][1]:04d}, expected rev{expected_end_rev:04d}")
    ordered_patches = [path for _, _, path in edges]
    return {
        "status": "overlay_chain_ready",
        "bundle_root": str(bundle_root),
        "expected_start_revision": f"rev{expected_start_rev:04d}",
        "expected_end_revision": f"rev{expected_end_rev:04d}" if expected_end_rev is not None else None,
        "patch_count": len(ordered_patches),
        "patches": patch_rows,
        "ordered_patch_paths": [path.relative_to(bundle_root).as_posix() for path in ordered_patches],
    }


def validate_target_root(target_root: Path) -> Path:
    target_root = target_root.resolve()
    if target_root.is_symlink() or not target_root.is_dir():
        raise OverlayApplyError(f"target root must be a real directory: {target_root}")
    symlinks: list[str] = []
    for dirpath, dirnames, filenames in os.walk(target_root, followlinks=False):
        directory = Path(dirpath)
        for name in dirnames + filenames:
            child = directory / name
            if child.is_symlink():
                try:
                    symlinks.append(child.relative_to(target_root).as_posix())
                except ValueError:
                    symlinks.append(str(child))
    if symlinks:
        shown = ", ".join(symlinks[:10])
        suffix = "" if len(symlinks) <= 10 else f"; +{len(symlinks) - 10} more"
        raise OverlayApplyError(f"target root contains symlink paths; refusing patch application: {shown}{suffix}")
    return target_root


def run_git_apply(target_root: Path, patch_path: Path, *, check_only: bool) -> None:
    cmd = ["git", "apply", "--whitespace=nowarn"]
    if check_only:
        cmd.append("--check")
    cmd.append(str(patch_path))
    env = os.environ.copy()
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    result = subprocess.run(cmd, cwd=target_root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise OverlayApplyError(f"git apply {'--check ' if check_only else ''}failed for {patch_path.name}: {detail}")


def copy_target_for_dry_run(target_root: Path) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix="ev-overlay-apply-dry-run-")
    dry_root = Path(tmp.name) / target_root.name
    shutil.copytree(target_root, dry_root, symlinks=False)
    return tmp, dry_root


def apply_patch_chain(
    bundle_root: Path,
    target_root: Path,
    *,
    apply: bool = False,
    expected_start_rev: int = CANONICAL_HANDOFF_REVISION,
    expected_end_rev: int | None = None,
) -> dict[str, Any]:
    chain = discover_overlay_chain(bundle_root, expected_start_rev=expected_start_rev, expected_end_rev=expected_end_rev)
    target_root = validate_target_root(target_root)
    patch_paths = [bundle_root / rel for rel in chain["ordered_patch_paths"]]

    dry_tmp, dry_root = copy_target_for_dry_run(target_root)
    with dry_tmp:
        for patch in patch_paths:
            run_git_apply(dry_root, patch, check_only=False)
    applied_to_target = False
    if apply:
        for patch in patch_paths:
            run_git_apply(target_root, patch, check_only=False)
        applied_to_target = True
    return {
        "status": "overlay_chain_applied" if applied_to_target else "overlay_chain_dry_run_ok",
        "target_root": str(target_root),
        "applied_to_target": applied_to_target,
        "dry_run_copy_used": True,
        "patch_count": chain["patch_count"],
        "ordered_patch_paths": chain["ordered_patch_paths"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate or apply EvidenceVault overlay patch stack safely.")
    parser.add_argument("--bundle-root", default=str(DEFAULT_BUNDLE_ROOT), help="overlay bundle root; defaults to this script's archive root")
    parser.add_argument("--target-root", default=None, help="complete canonical tree to test/apply the overlay stack against")
    parser.add_argument("--apply", action="store_true", help="after a temporary dry run succeeds, apply the patch chain to --target-root")
    parser.add_argument("--expected-start-rev", type=int, default=CANONICAL_HANDOFF_REVISION, help="first from-revision required in the overlay chain")
    parser.add_argument("--expected-end-rev", type=int, default=None, help="last to-revision required in the overlay chain; defaults to inferred current revision")
    parser.add_argument("--json", action="store_true", help="emit JSON status")
    args = parser.parse_args(argv)

    try:
        bundle_root = validate_bundle_root(Path(args.bundle_root))
        if args.target_root:
            result = apply_patch_chain(
                bundle_root,
                Path(args.target_root),
                apply=args.apply,
                expected_start_rev=args.expected_start_rev,
                expected_end_rev=args.expected_end_rev,
            )
        else:
            result = discover_overlay_chain(
                bundle_root,
                expected_start_rev=args.expected_start_rev,
                expected_end_rev=args.expected_end_rev,
            )
    except OverlayApplyError as exc:
        if args.json:
            print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"apply-overlay-stack-rev0850: FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if args.target_root:
            action = "applied" if result["applied_to_target"] else "dry-run validated"
            print(f"apply-overlay-stack-rev0850: {action} {result['patch_count']} patches")
        else:
            print(f"apply-overlay-stack-rev0850: validated {result['patch_count']} overlay patches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
