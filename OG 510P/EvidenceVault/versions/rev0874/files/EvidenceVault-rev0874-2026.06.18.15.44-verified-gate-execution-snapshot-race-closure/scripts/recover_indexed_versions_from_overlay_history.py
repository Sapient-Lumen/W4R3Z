#!/usr/bin/env python3
"""Recover exact canonical-index versions preserved only in overlay patch history.

The current overlay intentionally carries newer bytes at some paths named by
INDEX/files.csv.  For each such mismatch, this tool walks contiguous overlay
patches backward in an isolated temporary tree and checks every resulting byte
stream against the canonical size and SHA-256.  Exact matches may be preserved
in the bundle's content-addressed recovery store and safely materialized into a
separate canonical tree.

This tool never writes into its own EvidenceVault bundle.  External writes are
hash-gated, no-clobber, symlink-averse, and require an identical INDEX/files.csv.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
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
ROOT_RESOLVED = ROOT.resolve()
INDEX_REL = "INDEX/files.csv"
INVENTORY_REL = "RECOVERY/canonical-index/inventory.json"
OVERLAY_PATCH_RE = re.compile(r"^rev(?P<from>\d{4})-to-rev(?P<to>\d{4})-overlay\.patch$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class HistoryRecoveryError(RuntimeError):
    """Unsafe input, malformed evidence, or reconstruction failure."""


@dataclass(frozen=True)
class IndexRow:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class RecoveryCandidate:
    path: str
    size: int
    sha256: str
    data: bytes
    reverse_patches_applied: tuple[str, ...]
    matched_after_reverse_patch: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_rel(text: Any, label: str) -> str:
    try:
        return clean_anchored_relative_path(text, label)
    except RootAnchorError as exc:
        raise HistoryRecoveryError(str(exc)) from exc


def _assert_no_symlink_components(root: Path, target: Path, label: str) -> None:
    try:
        rel = target.relative_to(root)
    except ValueError as exc:
        raise HistoryRecoveryError(f"{label} escapes root: {target}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise HistoryRecoveryError(
                f"{label} resolves through a symlink component: "
                f"{cursor.relative_to(root).as_posix()}"
            )


def _load_index(root: Path) -> dict[str, IndexRow]:
    try:
        from canonical_coverage import load_index
    except ImportError as exc:
        raise HistoryRecoveryError(f"cannot import canonical index reader: {exc}") from exc
    rows = load_index(root, index_rel=INDEX_REL)
    return {
        row["path"]: IndexRow(row["path"], int(row["size"]), str(row["sha256"]))
        for row in rows
    }


def _load_mismatched_paths(root: Path) -> list[str]:
    try:
        from canonical_coverage import compute_coverage
    except ImportError as exc:
        raise HistoryRecoveryError(f"cannot import canonical coverage engine: {exc}") from exc
    coverage = compute_coverage(root, include_paths=True)
    return sorted(coverage["paths"]["mismatch"])


def overlay_patches(root: Path) -> list[Path]:
    patch_dir = root / "PATCHES"
    _assert_no_symlink_components(root, patch_dir, "patch directory")
    if not patch_dir.is_dir():
        raise HistoryRecoveryError("PATCHES directory is missing")
    rows: list[tuple[int, int, Path]] = []
    for path in patch_dir.iterdir():
        match = OVERLAY_PATCH_RE.fullmatch(path.name)
        if match is None:
            continue
        if path.is_symlink() or not path.is_file():
            raise HistoryRecoveryError(f"overlay patch is unsafe: PATCHES/{path.name}")
        from_rev = int(match.group("from"))
        to_rev = int(match.group("to"))
        if to_rev != from_rev + 1:
            raise HistoryRecoveryError(f"non-contiguous overlay patch edge: {path.name}")
        rows.append((from_rev, to_rev, path))
    if not rows:
        raise HistoryRecoveryError("no incremental overlay patches found")
    rows.sort()
    for previous, current in zip(rows, rows[1:]):
        if previous[1] != current[0]:
            raise HistoryRecoveryError(
                f"overlay patch chain gap: {previous[2].name} -> {current[2].name}"
            )
    return [row[2] for row in rows]


def _patch_touches_path(patch: Path, rel: str) -> bool:
    wanted_a = f"a/{rel}"
    wanted_b = f"b/{rel}"
    try:
        text = patch.read_text(encoding="utf-8", errors="surrogateescape")
    except OSError as exc:
        raise HistoryRecoveryError(f"cannot read patch {patch.name}: {exc}") from exc
    for line in text.splitlines():
        if not line.startswith("diff --git "):
            continue
        # EvidenceVault paths contain no whitespace requiring git's quoted form.
        parts = line.split(" ", 3)
        if len(parts) == 4 and parts[2] == wanted_a and parts[3] == wanted_b:
            return True
    return False


def _matches(path: Path, row: IndexRow) -> bool:
    return path.is_file() and path.stat().st_size == row.size and sha256_file(path) == row.sha256


def _reverse_one_patch(work_root: Path, patch: Path, rel: str) -> None:
    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "HOME": os.devnull,
            "XDG_CONFIG_HOME": os.devnull,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    proc = subprocess.run(
        [
            "git",
            "-c",
            "core.safecrlf=false",
            "apply",
            "-R",
            "--whitespace=nowarn",
            f"--include={rel}",
            os.fspath(patch),
        ],
        cwd=work_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise HistoryRecoveryError(
            f"cannot reverse {patch.name} for {rel}: {detail or 'git apply failed'}"
        )


def discover_historical_versions(root: Path = ROOT) -> tuple[dict[str, RecoveryCandidate], dict[str, Any]]:
    root = root.resolve()
    if root.is_symlink() or not root.is_dir():
        raise HistoryRecoveryError(f"root must be a real directory: {root}")
    index = _load_index(root)
    mismatches = _load_mismatched_paths(root)
    patches = overlay_patches(root)
    candidates: dict[str, RecoveryCandidate] = {}
    unresolved: list[dict[str, Any]] = []
    touched_mismatches = 0
    reverse_attempts = 0

    for rel in mismatches:
        row = index[rel]
        current = root / rel
        _assert_no_symlink_components(root, current, f"current indexed path {rel}")
        if not current.is_file():
            raise HistoryRecoveryError(f"mismatched indexed path is not a regular file: {rel}")
        relevant = [patch for patch in reversed(patches) if _patch_touches_path(patch, rel)]
        if not relevant:
            unresolved.append({"path": rel, "reason": "not_touched_by_incremental_overlay_history"})
            continue
        touched_mismatches += 1
        applied: list[str] = []
        matched: RecoveryCandidate | None = None
        reverse_failure: str | None = None
        with tempfile.TemporaryDirectory(prefix="ev-history-recovery-") as tmp_text:
            work = Path(tmp_text)
            target = work / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(current, target)
            for patch in relevant:
                try:
                    _reverse_one_patch(work, patch, rel)
                except HistoryRecoveryError as exc:
                    reverse_failure = str(exc)
                    break
                reverse_attempts += 1
                applied.append(f"PATCHES/{patch.name}")
                if _matches(target, row):
                    data = target.read_bytes()
                    matched = RecoveryCandidate(
                        path=rel,
                        size=row.size,
                        sha256=row.sha256,
                        data=data,
                        reverse_patches_applied=tuple(applied),
                        matched_after_reverse_patch=f"PATCHES/{patch.name}",
                    )
                    break
        if matched is None:
            unresolved_row: dict[str, Any] = {
                "path": rel,
                "reason": (
                    "reverse_patch_application_failed"
                    if reverse_failure is not None
                    else "no_reverse_history_state_matches_canonical_index"
                ),
                "patches_reversed": list(applied),
            }
            if reverse_failure is not None:
                unresolved_row["failure"] = reverse_failure
            unresolved.append(unresolved_row)
        else:
            candidates[rel] = matched

    metrics = {
        "canonical_mismatches_examined": len(mismatches),
        "mismatches_touched_by_overlay_history": touched_mismatches,
        "exact_historical_versions_recovered": len(candidates),
        "exact_historical_bytes_recovered": sum(row.size for row in candidates.values()),
        "unresolved_mismatches": len(unresolved),
        "unresolved": unresolved,
        "overlay_patches_available": len(patches),
        "reverse_patch_applications": reverse_attempts,
    }
    return candidates, metrics


def load_inventory(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    path = root / INVENTORY_REL
    _assert_no_symlink_components(root, path, "recovery inventory")
    if not path.is_file():
        raise HistoryRecoveryError(f"recovery inventory is missing: {INVENTORY_REL}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HistoryRecoveryError(f"invalid recovery inventory: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        raise HistoryRecoveryError("recovery inventory must be an object with an entries array")
    return value


def verify_inventory(
    root: Path = ROOT,
    *,
    discovered: dict[str, RecoveryCandidate] | None = None,
) -> tuple[dict[str, RecoveryCandidate], dict[str, Any]]:
    root = root.resolve()
    index = _load_index(root)
    inventory = load_inventory(root)
    entries: dict[str, RecoveryCandidate] = {}
    total_bytes = 0
    for position, raw in enumerate(inventory["entries"]):
        if not isinstance(raw, dict):
            raise HistoryRecoveryError(f"inventory entry {position} is not an object")
        rel = clean_rel(raw.get("path"), f"inventory entry {position} path")
        if rel in entries:
            raise HistoryRecoveryError(f"duplicate recovery inventory path: {rel}")
        row = index.get(rel)
        if row is None:
            raise HistoryRecoveryError(f"recovery inventory path is absent from index: {rel}")
        size = raw.get("size")
        digest = raw.get("sha256")
        if size != row.size or digest != row.sha256:
            raise HistoryRecoveryError(f"recovery inventory identity differs from index: {rel}")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise HistoryRecoveryError(f"invalid recovery inventory SHA-256: {rel}")
        object_rel = clean_rel(raw.get("object_path"), f"inventory entry {position} object_path")
        expected_object_rel = f"RECOVERY/canonical-index/objects/sha256/{digest}"
        if object_rel != expected_object_rel:
            raise HistoryRecoveryError(
                f"recovery object path is not content-addressed as expected: {rel}"
            )
        object_path = root / object_rel
        _assert_no_symlink_components(root, object_path, f"recovery object {rel}")
        if not object_path.is_file():
            raise HistoryRecoveryError(f"recovery object is absent or non-regular: {object_rel}")
        data = object_path.read_bytes()
        if len(data) != size or sha256_bytes(data) != digest:
            raise HistoryRecoveryError(f"recovery object bytes do not match index: {rel}")
        patches = raw.get("reverse_patches_applied")
        match_patch = raw.get("matched_after_reverse_patch")
        if not isinstance(patches, list) or not patches or not all(isinstance(x, str) for x in patches):
            raise HistoryRecoveryError(f"invalid reverse patch sequence in inventory: {rel}")
        if match_patch != patches[-1]:
            raise HistoryRecoveryError(f"matched patch must be final applied patch: {rel}")
        candidate = RecoveryCandidate(
            path=rel,
            size=size,
            sha256=digest,
            data=data,
            reverse_patches_applied=tuple(patches),
            matched_after_reverse_patch=match_patch,
        )
        entries[rel] = candidate
        total_bytes += size

    if inventory.get("recovered_files") != len(entries):
        raise HistoryRecoveryError("inventory recovered_files count is stale")
    if inventory.get("recovered_bytes") != total_bytes:
        raise HistoryRecoveryError("inventory recovered_bytes count is stale")
    if inventory.get("canonical_index_sha256") != sha256_file(root / INDEX_REL):
        raise HistoryRecoveryError("inventory canonical index digest is stale")

    if discovered is not None:
        if set(discovered) != set(entries):
            missing = sorted(set(discovered) - set(entries))
            extra = sorted(set(entries) - set(discovered))
            raise HistoryRecoveryError(
                f"inventory/history path drift: missing={missing!r} extra={extra!r}"
            )
        for rel, candidate in discovered.items():
            stored = entries[rel]
            if (
                candidate.size != stored.size
                or candidate.sha256 != stored.sha256
                or candidate.data != stored.data
                or candidate.reverse_patches_applied != stored.reverse_patches_applied
                or candidate.matched_after_reverse_patch != stored.matched_after_reverse_patch
            ):
                raise HistoryRecoveryError(f"inventory/history evidence drift: {rel}")

    metrics = {
        "inventory_path": INVENTORY_REL,
        "inventory_verified": True,
        "recovery_object_files": len(entries),
        "recovery_object_bytes": total_bytes,
        "unique_object_digests": len({row.sha256 for row in entries.values()}),
    }
    return entries, metrics


def _external_target_root(path: Path) -> Path:
    try:
        return prepare_external_target_root(
            path, bundle_root=ROOT, index_rel=INDEX_REL
        )
    except MaterializationError as exc:
        raise HistoryRecoveryError(str(exc)) from exc


def _target_status(root: Path, rel: str, candidate: RecoveryCandidate) -> str:
    try:
        status = shared_target_status(
            root,
            rel,
            expected_size=candidate.size,
            expected_sha256=candidate.sha256,
        )
    except MaterializationError as exc:
        raise HistoryRecoveryError(str(exc)) from exc
    return "mismatch" if status == "unsafe_non_regular" else status


def _atomic_no_clobber(
    root: Path, rel: str, candidate: RecoveryCandidate
) -> bool:
    try:
        result = materialize_exact_bytes(
            root,
            rel,
            candidate.data,
            expected_sha256=candidate.sha256,
            allow_existing_exact=True,
        )
    except MaterializationError as exc:
        raise HistoryRecoveryError(str(exc)) from exc
    return result.status == "written"


def materialize(
    entries: dict[str, RecoveryCandidate],
    target_root: Path,
    *,
    write: bool,
    require_present: bool,
    fail_on_mismatch: bool,
) -> tuple[dict[str, Any], int]:
    root = _external_target_root(target_root)
    written = 0
    statuses: dict[str, str] = {}
    for rel, candidate in sorted(entries.items()):
        status = _target_status(root, rel, candidate)
        if status == "missing" and write:
            created = _atomic_no_clobber(root, rel, candidate)
            if created:
                written += 1
            status = _target_status(root, rel, candidate)
        statuses[rel] = status

    counts = {name: sum(1 for value in statuses.values() if value == name) for name in ("exact", "missing", "mismatch")}
    conflicts = counts["mismatch"] > 0
    incomplete = counts["missing"] > 0
    if conflicts and fail_on_mismatch:
        status = "candidate_target_conflict"
        return_code = 1
    elif incomplete and require_present:
        status = "recovery_target_incomplete"
        return_code = 1
    elif not conflicts and not incomplete:
        status = "all_recovery_objects_present"
        return_code = 0
    else:
        status = "recovery_target_audited"
        return_code = 0
    report = {
        "status": status,
        "target_root": os.fspath(root),
        "write_requested": write,
        "files_written": written,
        "candidate_status_counts": counts,
        "candidate_files": len(entries),
        "candidate_bytes": sum(row.size for row in entries.values()),
    }
    return report, return_code


def build_report(root: Path = ROOT, *, rediscover: bool = True) -> dict[str, Any]:
    discovered: dict[str, RecoveryCandidate] | None = None
    history_metrics: dict[str, Any] | None = None
    if rediscover:
        discovered, history_metrics = discover_historical_versions(root)
    entries, inventory_metrics = verify_inventory(root, discovered=discovered)
    report: dict[str, Any] = {
        "status": "overlay_history_recovery_verified",
        **inventory_metrics,
    }
    if history_metrics is not None:
        report["history_reconstruction"] = history_metrics
    report["paths"] = sorted(entries)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--inventory-only", action="store_true", help="verify stored objects without replaying patch history")
    parser.add_argument("--target-root", type=Path, help="separate tree containing the identical canonical index")
    parser.add_argument("--write", action="store_true", help="materialize missing exact objects into --target-root")
    parser.add_argument("--require-present", action="store_true", help="fail unless every recovery object is exact at target")
    parser.add_argument("--fail-on-mismatch", action="store_true", help="fail when a target path has non-matching bytes")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    if args.write and args.target_root is None:
        print("overlay-history-recovery: FAIL: --write requires --target-root", file=sys.stderr)
        return 2
    if (args.require_present or args.fail_on_mismatch) and args.target_root is None:
        print("overlay-history-recovery: FAIL: target policy flags require --target-root", file=sys.stderr)
        return 2
    try:
        discovered = None
        history_metrics = None
        if not args.inventory_only:
            discovered, history_metrics = discover_historical_versions(args.root)
        entries, inventory_metrics = verify_inventory(args.root, discovered=discovered)
        payload: dict[str, Any] = {
            "status": "overlay_history_recovery_verified",
            **inventory_metrics,
        }
        if history_metrics is not None:
            payload["history_reconstruction"] = history_metrics
        payload["paths"] = sorted(entries)
        return_code = 0
        if args.target_root is not None:
            target_report, return_code = materialize(
                entries,
                args.target_root,
                write=args.write,
                require_present=args.require_present,
                fail_on_mismatch=args.fail_on_mismatch,
            )
            payload.update(target_report)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "overlay-history-recovery: "
                f"{payload['status']} ({payload['recovery_object_files']} files, "
                f"{payload['recovery_object_bytes']} bytes)"
            )
        return return_code
    except HistoryRecoveryError as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"overlay-history-recovery: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
