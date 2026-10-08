#!/usr/bin/env python3
"""Recover exact indexed files whose complete bytes survive in unified patches.

A unified diff normally carries only changed hunks, so it is not generally a
backup.  Some EvidenceVault patch sections nevertheless contain the complete
new-side byte stream.  This tool reconstructs only contiguous new-side streams
starting at line 1, then admits a candidate only when both byte count and
SHA-256 exactly match INDEX/files.csv.  Hash-mismatched or partial candidates
are never written.

By default the tool audits the bundle.  With --target-root it can plan recovery
into a separate tree carrying the same canonical index; --write performs
no-clobber, symlink-safe writes there.  It refuses to mutate its own bundle.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable

sys.dont_write_bytecode = True

from safe_materialize import (
    MaterializationError,
    materialize_exact_bytes,
    prepare_external_target_root,
    target_status as shared_target_status,
)
from root_anchor import RootAnchorError, clean_relative_path as clean_anchored_relative_path

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / "PATCHES"
INDEX_REL = "INDEX/files.csv"
HUNK_RE = re.compile(br"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DIFF_PREFIXES = (b"diff --git ", b"diff -ruN ")
KNOWN_CUMULATIVE_PREFIXES = (
    "EvidenceVault-rev0826/",
    "/mnt/data/rev0826_base/EvidenceVault-rev0826/",
)


class RecoveryError(RuntimeError):
    """Raised for malformed patch data or unsafe recovery targets."""


@dataclass(frozen=True)
class IndexRow:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class Hunk:
    line_index: int
    old_start: int
    old_count: int
    new_start: int
    new_count: int


@dataclass
class PatchSection:
    patch_name: str
    old_path: str | None
    new_path: str | None
    lines: list[bytes]
    hunks: list[Hunk]


@dataclass
class Candidate:
    path: str
    size: int
    sha256: str
    data: bytes
    origins: list[str]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_relative_path(text: str, label: str) -> str:
    try:
        return clean_anchored_relative_path(text, label)
    except RootAnchorError as exc:
        raise RecoveryError(str(exc)) from exc


def normalize_patch_header_path(raw: bytes, label: str) -> str | None:
    token = raw.split(b"\t", 1)[0].strip()
    if token == b"/dev/null":
        return None
    try:
        text = token.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RecoveryError(f"{label} is not UTF-8: {token!r}") from exc
    if text.startswith(('"', "'")):
        raise RecoveryError(f"{label} uses an unsupported quoted path: {text!r}")
    if text.startswith("a/") or text.startswith("b/"):
        text = text[2:]
    for prefix in KNOWN_CUMULATIVE_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    return clean_relative_path(text, label)


def _parse_count(value: bytes | None) -> int:
    return 1 if value is None else int(value)


def parse_patch(path: Path) -> list[PatchSection]:
    if path.is_symlink() or not path.is_file():
        raise RecoveryError(f"patch is missing, non-regular, or symlinked: {path}")
    raw = path.read_bytes()
    if b"\x00" in raw:
        raise RecoveryError(f"patch contains NUL bytes: {path.name}")
    if re.search(br"(?m)^GIT binary patch$", raw):
        raise RecoveryError(f"binary patch payload is unsupported: {path.name}")
    lines = raw.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.startswith(DIFF_PREFIXES)]
    if not starts:
        raise RecoveryError(f"patch has no recognized diff sections: {path.name}")
    starts.append(len(lines))

    sections: list[PatchSection] = []
    for start, end in zip(starts, starts[1:]):
        section_lines = lines[start:end]
        old_path: str | None = None
        new_path: str | None = None
        old_header_index: int | None = None
        for index, line in enumerate(section_lines):
            if line.startswith(b"--- "):
                old_path = normalize_patch_header_path(
                    line[4:], f"{path.name}:{start + index + 1} old path"
                )
                old_header_index = index
                break
        if old_header_index is None:
            raise RecoveryError(f"diff section lacks --- header in {path.name}:{start + 1}")
        for index in range(old_header_index + 1, len(section_lines)):
            line = section_lines[index]
            if line.startswith(b"+++ "):
                new_path = normalize_patch_header_path(
                    line[4:], f"{path.name}:{start + index + 1} new path"
                )
                break
        else:
            raise RecoveryError(f"diff section lacks +++ header in {path.name}:{start + 1}")

        hunks: list[Hunk] = []
        for index, line in enumerate(section_lines):
            match = HUNK_RE.match(line)
            if not match:
                continue
            old_start = int(match.group(1))
            old_count = _parse_count(match.group(2))
            new_start = int(match.group(3))
            new_count = _parse_count(match.group(4))
            hunks.append(Hunk(index, old_start, old_count, new_start, new_count))
        sections.append(PatchSection(path.name, old_path, new_path, section_lines, hunks))
    return sections


def reconstruct_contiguous_new_side(section: PatchSection) -> bytes | None:
    """Return complete-looking new-side bytes, subject to later index verification."""
    if not section.hunks or section.new_path is None:
        return None
    expected_new_start = 1
    output = bytearray()

    for hunk_index, hunk in enumerate(section.hunks):
        if hunk.new_start != expected_new_start:
            return None
        body_end = (
            section.hunks[hunk_index + 1].line_index
            if hunk_index + 1 < len(section.hunks)
            else len(section.lines)
        )
        old_seen = 0
        new_seen = 0
        last_prefix: bytes | None = None
        for line in section.lines[hunk.line_index + 1 : body_end]:
            if old_seen == hunk.old_count and new_seen == hunk.new_count:
                break
            if line.startswith(b"\\ No newline at end of file"):
                if last_prefix in {b"+", b" "} and output.endswith(b"\n"):
                    output.pop()
                last_prefix = None
                continue
            if not line:
                raise RecoveryError(
                    f"empty raw patch line inside hunk: {section.patch_name}:{section.new_path}"
                )
            prefix = line[:1]
            if prefix == b" ":
                output.extend(line[1:])
                old_seen += 1
                new_seen += 1
            elif prefix == b"+":
                output.extend(line[1:])
                new_seen += 1
            elif prefix == b"-":
                old_seen += 1
            else:
                raise RecoveryError(
                    "malformed hunk body line in "
                    f"{section.patch_name}:{section.new_path}: {line[:80]!r}"
                )
            last_prefix = prefix
        if old_seen != hunk.old_count or new_seen != hunk.new_count:
            raise RecoveryError(
                f"hunk count mismatch in {section.patch_name}:{section.new_path}; "
                f"declared old/new={hunk.old_count}/{hunk.new_count}, "
                f"observed={old_seen}/{new_seen}"
            )
        expected_new_start = hunk.new_start + hunk.new_count
    return bytes(output)


def load_index(root: Path = ROOT) -> dict[str, IndexRow]:
    # Import the shared, independently usable index parser.
    sys.path.insert(0, str((root / "scripts").resolve()))
    try:
        from canonical_coverage import load_index as shared_load_index  # type: ignore
    except Exception as exc:  # pragma: no cover - diagnostic path
        raise RecoveryError(f"cannot import scripts/canonical_coverage.py: {exc}") from exc
    finally:
        try:
            sys.path.remove(str((root / "scripts").resolve()))
        except ValueError:
            pass
    rows = shared_load_index(root, index_rel=INDEX_REL)
    return {
        row["path"]: IndexRow(row["path"], int(row["size"]), row["sha256"])
        for row in rows
    }


def discover_candidates(
    root: Path = ROOT,
    *,
    exclude_patch_names: Iterable[str] = (),
) -> tuple[dict[str, Candidate], dict[str, int]]:
    index = load_index(root)
    patch_dir = root / "PATCHES"
    if patch_dir.is_symlink() or not patch_dir.is_dir():
        raise RecoveryError(f"PATCHES directory is absent or unsafe: {patch_dir}")

    excluded: set[str] = set()
    for name in exclude_patch_names:
        if not name or Path(name).name != name or not name.endswith(".patch"):
            raise RecoveryError(f"excluded patch must be a .patch basename: {name!r}")
        excluded.add(name)
    all_patch_paths = sorted(patch_dir.glob("*.patch"))
    unknown = excluded - {path.name for path in all_patch_paths}
    if unknown:
        raise RecoveryError("excluded patch not found: " + ", ".join(sorted(unknown)))
    patch_paths = [path for path in all_patch_paths if path.name not in excluded]
    if not patch_paths:
        raise RecoveryError("no patch files remain after exclusions")
    candidates: dict[str, Candidate] = {}
    section_count = 0
    contiguous_count = 0
    indexed_contiguous_count = 0

    for patch_path in patch_paths:
        for section in parse_patch(patch_path):
            section_count += 1
            data = reconstruct_contiguous_new_side(section)
            if data is None:
                continue
            contiguous_count += 1
            if section.new_path not in index:
                continue
            indexed_contiguous_count += 1
            row = index[section.new_path]
            digest = sha256_bytes(data)
            if len(data) != row.size or digest != row.sha256:
                continue
            origin = f"PATCHES/{patch_path.name}:{section.new_path}"
            existing = candidates.get(section.new_path)
            if existing is None:
                candidates[section.new_path] = Candidate(
                    path=section.new_path,
                    size=row.size,
                    sha256=row.sha256,
                    data=data,
                    origins=[origin],
                )
            else:
                if existing.data != data:
                    raise RecoveryError(
                        f"conflicting exact candidates for indexed path: {section.new_path}"
                    )
                existing.origins.append(origin)

    metrics = {
        "patch_files_available": len(all_patch_paths),
        "patch_files_excluded": len(excluded),
        "patch_files_scanned": len(patch_paths),
        "patch_sections_scanned": section_count,
        "contiguous_new_side_streams": contiguous_count,
        "indexed_contiguous_new_side_streams": indexed_contiguous_count,
        "exact_index_verified_candidate_paths": len(candidates),
    }
    return candidates, metrics


def candidate_status(root: Path, candidate: Candidate) -> str:
    try:
        return shared_target_status(
            root,
            candidate.path,
            expected_size=candidate.size,
            expected_sha256=candidate.sha256,
        )
    except MaterializationError as exc:
        raise RecoveryError(str(exc)) from exc


def _assert_external_target_root(target_root: Path) -> Path:
    try:
        return prepare_external_target_root(
            target_root, bundle_root=ROOT, index_rel=INDEX_REL
        )
    except MaterializationError as exc:
        raise RecoveryError(str(exc)) from exc


def _write_no_clobber(root: Path, candidate: Candidate) -> None:
    try:
        materialize_exact_bytes(
            root,
            candidate.path,
            candidate.data,
            expected_sha256=candidate.sha256,
            allow_existing_exact=True,
        )
    except MaterializationError as exc:
        raise RecoveryError(str(exc)) from exc


def build_report(
    candidates: dict[str, Candidate],
    metrics: dict[str, int],
    status_root: Path,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts = {"exact": 0, "missing": 0, "mismatch": 0, "unsafe_non_regular": 0}
    for path in sorted(candidates):
        candidate = candidates[path]
        status = candidate_status(status_root, candidate)
        counts[status] = counts.get(status, 0) + 1
        rows.append(
            {
                "path": path,
                "bytes": candidate.size,
                "sha256": candidate.sha256,
                "status": status,
                "source_payload": path.startswith("sources/"),
                "origins": sorted(candidate.origins),
            }
        )
    return {
        "status": "candidate_set_verified",
        "method": (
            "contiguous new-side bytes beginning at line 1, admitted only by exact "
            "INDEX/files.csv byte-count and SHA-256 match"
        ),
        **metrics,
        "status_root": str(status_root.resolve()),
        "candidate_status_counts": counts,
        "source_candidate_paths": sum(row["source_payload"] for row in rows),
        "candidate_bytes": sum(row["bytes"] for row in rows),
        "candidates": rows,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exclude-patch",
        action="append",
        default=[],
        help="exclude one .patch basename from candidate discovery; repeatable",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        help="separate tree carrying the identical INDEX/files.csv",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write exact missing candidates to --target-root; never overwrite",
    )
    parser.add_argument(
        "--require-present",
        action="store_true",
        help=(
            "fail if any exact candidate path is absent; later-revision bytes at an "
            "existing path are reported but not treated as missing"
        ),
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="also fail when an existing candidate path carries later-revision bytes",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.write and args.target_root is None:
            raise RecoveryError("--write requires --target-root")
        candidates, metrics = discover_candidates(
            ROOT, exclude_patch_names=args.exclude_patch
        )
        status_root = ROOT
        if args.target_root is not None:
            status_root = _assert_external_target_root(args.target_root)
        before = build_report(candidates, metrics, status_root)
        written = 0
        if args.write:
            for path in sorted(candidates):
                if candidate_status(status_root, candidates[path]) == "missing":
                    _write_no_clobber(status_root, candidates[path])
                    written += 1
            report = build_report(candidates, metrics, status_root)
        else:
            report = before
        report["write_requested"] = bool(args.write)
        report["files_written"] = written
        counts = report["candidate_status_counts"]
        mismatch = counts.get("mismatch", 0)
        unsafe = counts.get("unsafe_non_regular", 0)
        missing = counts.get("missing", 0)
        report["revision_divergent_candidate_paths"] = mismatch
        report["files_skipped_revision_divergent"] = mismatch if args.write else 0

        if unsafe:
            report["status"] = "candidate_target_unsafe"
        elif args.fail_on_mismatch and mismatch:
            report["status"] = "candidate_target_conflict"
        elif args.require_present and missing:
            report["status"] = "required_candidates_missing"
        elif args.write and missing:
            report["status"] = "recovery_incomplete"
        elif missing:
            report["status"] = "exact_candidates_available"
        elif mismatch:
            report["status"] = "candidates_present_with_revision_divergences"
        else:
            report["status"] = "all_exact_candidates_present"

        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(
                "patch-index-recovery: "
                f"candidates={report['exact_index_verified_candidate_paths']} "
                f"exact={counts.get('exact', 0)} missing={missing} "
                f"revision_divergent={mismatch} written={written}"
            )
        if (
            unsafe
            or (args.fail_on_mismatch and mismatch)
            or (args.require_present and missing)
            or (args.write and missing)
        ):
            return 1
        return 0
    except RecoveryError as exc:
        print(f"patch-index-recovery: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
