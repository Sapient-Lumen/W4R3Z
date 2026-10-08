#!/usr/bin/env python3
"""Validate overlay-bundle self-integrity surfaces for rev0848+ bundles."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

try:
    from root_anchor import RootAnchorError, clean_relative_path as clean_anchored_relative_path
except ImportError:  # pragma: no cover - package-style import fallback
    from .root_anchor import RootAnchorError, clean_relative_path as clean_anchored_relative_path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_REVISION_RE = re.compile(r"rev(\d{4})")
CANONICAL_HANDOFF_REVISION = 840
OVERLAY_PATCH_RE = re.compile(r"^PATCHES/rev(\d{4})-to-rev(\d{4})-overlay\.patch$")
SHA_LINE_RE = re.compile(r"^(?P<sha>[0-9a-f]{64})  (?P<path>.+)$")


def fail(message: str) -> None:
    print(f"overlay-bundle-integrity-rev0848: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        fail(f"cannot hash non-regular file: {rel(path)}")
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def clean_archive_path(text: Any, field: str) -> str:
    try:
        return clean_anchored_relative_path(text, field)
    except RootAnchorError as exc:
        fail(str(exc))
    raise AssertionError("unreachable")

def all_regular_file_paths() -> list[str]:
    files: list[str] = []
    symlinks: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_symlink():
            symlinks.append(rel(path))
        elif path.is_file():
            files.append(rel(path))
    if symlinks:
        fail("overlay bundle contains symlink entries after extraction: " + ", ".join(symlinks[:10]))
    return files


def load_overlay_manifest() -> dict[str, Any]:
    path = ROOT / "CHECKS" / "overlay-manifest.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid CHECKS/overlay-manifest.json: {exc}")
    if not isinstance(data, dict):
        fail("CHECKS/overlay-manifest.json must be a JSON object")
    return data


def assert_overlay_manifest() -> None:
    data = load_overlay_manifest()
    entries = data.get("files")
    if not isinstance(entries, list):
        fail("overlay manifest files must be a list")
    if data.get("file_count") != len(entries):
        fail(f"overlay manifest file_count mismatch: {data.get('file_count')} != {len(entries)}")
    expected_payload = sha256_file(ROOT / "CHECKS" / "overlay-manifest.json")
    sidecar_line = (ROOT / "CHECKS" / "overlay-manifest.sha256").read_text(encoding="utf-8").strip()
    if sidecar_line != f"{expected_payload}  CHECKS/overlay-manifest.json":
        fail("overlay manifest sidecar does not match CHECKS/overlay-manifest.json")

    manifest_paths: set[str] = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"overlay manifest entry {idx} is not an object")
        entry_path = clean_archive_path(entry.get("path"), f"overlay manifest files[{idx}].path")
        if entry_path in manifest_paths:
            fail(f"duplicate overlay manifest path: {entry_path}")
        manifest_paths.add(entry_path)
        target = ROOT / entry_path
        if not target.is_file() or target.is_symlink():
            fail(f"overlay manifest path is not a regular file: {entry_path}")
        size = target.stat().st_size
        digest = sha256_file(target)
        if entry.get("bytes") != size or entry.get("sha256") != digest:
            fail(f"overlay manifest mismatch for {entry_path}")

    actual_paths = set(all_regular_file_paths())
    excluded = {"CHECKS/overlay-manifest.json", "CHECKS/overlay-manifest.sha256"}
    expected_paths = actual_paths - excluded
    if manifest_paths != expected_paths:
        missing = sorted(expected_paths - manifest_paths)
        extra = sorted(manifest_paths - expected_paths)
        fail(f"overlay manifest file set mismatch; missing={missing[:10]} extra={extra[:10]}")


def parse_sha_lines(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        match = SHA_LINE_RE.match(line)
        if not match:
            fail(f"malformed SHA-256 line in {rel(path)}:{line_no}: {line!r}")
        digest = match.group("sha")
        rel_path = clean_archive_path(match.group("path"), f"{rel(path)}:{line_no}")
        if rel_path in rows:
            fail(f"duplicate SHA-256 entry in {rel(path)}: {rel_path}")
        rows[rel_path] = digest
    return rows


def assert_patch_hashes_and_chain() -> None:
    rows = parse_sha_lines(ROOT / "CHECKS" / "patches.sha256")
    actual_patch_paths = sorted((p.relative_to(ROOT).as_posix() for p in (ROOT / "PATCHES").glob("*.patch")))
    if set(rows) != set(actual_patch_paths):
        fail(f"CHECKS/patches.sha256 does not exactly cover PATCHES/*.patch; rows={sorted(rows)} actual={actual_patch_paths}")
    for rel_path, digest in rows.items():
        if sha256_file(ROOT / rel_path) != digest:
            fail(f"patch hash mismatch for {rel_path}")

    overlay_edges: list[tuple[int, int, str]] = []
    for rel_path in actual_patch_paths:
        match = OVERLAY_PATCH_RE.match(rel_path)
        if match:
            overlay_edges.append((int(match.group(1)), int(match.group(2)), rel_path))
    if overlay_edges:
        overlay_edges.sort()
        if overlay_edges[0][0] != CANONICAL_HANDOFF_REVISION:
            fail(
                f"overlay patch chain starts at rev{overlay_edges[0][0]:04d}, "
                f"expected rev{CANONICAL_HANDOFF_REVISION:04d}; missing seed handoff patch"
            )
        for edge in overlay_edges:
            if edge[1] != edge[0] + 1:
                fail(f"overlay patch is not a one-revision step: {edge[2]}")
        for previous, current in zip(overlay_edges, overlay_edges[1:]):
            if previous[1] != current[0]:
                fail(f"overlay patch chain has a gap: {previous[2]} then {current[2]}")
        current_rev = current_revision_number()
        last_to = overlay_edges[-1][1]
        if current_rev is not None and last_to != current_rev:
            fail(f"latest overlay patch ends at rev{last_to:04d}, but current revision appears to be rev{current_rev:04d}")


def current_revision_number() -> int | None:
    candidates = [ROOT.name]
    for path in (ROOT / "CHECKS").glob("patch-bundle-identity-rev*.json"):
        candidates.append(path.name)
    numbers: list[int] = []
    for text in candidates:
        for match in CURRENT_REVISION_RE.finditer(text):
            numbers.append(int(match.group(1)))
    return max(numbers) if numbers else None


def assert_input_artifacts_are_portable() -> None:
    rows = parse_sha_lines(ROOT / "CHECKS" / "input-artifacts.sha256")
    for rel_path in rows:
        if "/" in rel_path or "\\" in rel_path or rel_path.startswith("."):
            fail(f"input artifact line must use a portable artifact basename, not a local path: {rel_path}")


def assert_changed_canonical_file_list_is_clean() -> None:
    path = ROOT / "CHECKS" / "changed-canonical-files.txt"
    rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != len(set(rows)):
        fail("CHECKS/changed-canonical-files.txt contains duplicate paths")
    for idx, item in enumerate(rows, start=1):
        clean = clean_archive_path(item, f"changed-canonical-files:{idx}")
        if not (ROOT / clean).exists():
            fail(f"changed-canonical-files path is absent from overlay bundle: {clean}")
    current_rev = current_revision_number()
    if current_rev is not None:
        required = [
            f"SESSION_REVIEW_REV{current_rev:04d}.json",
            f"SESSION_REVIEW_REV{current_rev:04d}.md",
            f"VALIDATION/rev{current_rev:04d}_targeted_validation.txt",
            f"CHECKS/patch-bundle-identity-rev{current_rev:04d}.json",
            f"CHECKS/build-provenance-rev{current_rev:04d}.intoto.json",
        ]
        missing = [item for item in required if item not in rows]
        if missing:
            fail("changed-canonical-files omits current revision evidence: " + ", ".join(missing))


def main() -> int:
    assert_overlay_manifest()
    assert_patch_hashes_and_chain()
    assert_input_artifacts_are_portable()
    assert_changed_canonical_file_list_is_clean()
    print("overlay-bundle-integrity-rev0848: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
