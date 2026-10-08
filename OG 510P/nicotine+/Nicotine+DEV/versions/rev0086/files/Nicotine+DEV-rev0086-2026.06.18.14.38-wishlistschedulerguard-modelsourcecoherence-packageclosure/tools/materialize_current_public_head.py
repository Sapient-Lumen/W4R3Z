#!/usr/bin/env python3
"""Materialize the exact current public-master file content from pinned inputs.

The cube does not embed another upstream tree. It extracts the content-addressed
bundled master proxy, applies the verified public compare delta, and validates
all changed Git blob IDs plus a whole-tree inventory digest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    file_inventory,
    git_blob_sha1_path,
    run_bounded,
    safe_extract_tar_gz_member,
    safe_relative,
    sha256_path,
)
from source_bundle_locator import (  # noqa: E402
    archive_member_name,
    load_source_contract,
    locate_source_bundle,
)

CONTRACT_PATH = Path("data/current_public_head_contract.json")
HEX40 = set("0123456789abcdef")
HEX64 = set("0123456789abcdef")


class PublicHeadError(RuntimeError):
    """Raised when exact public-head materialization cannot be established."""


def _hex(value: object, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and set(value) <= HEX40


def inventory_identity(root: Path) -> tuple[str, int, int]:
    """Hash deterministic path/hash/size rows for one extracted source tree."""
    digest = hashlib.sha256()
    rows = file_inventory(root)
    total = 0
    for path, (file_sha256, size) in rows.items():
        digest.update(f"{file_sha256}  {size}  {path.as_posix()}\n".encode("utf-8"))
        total += size
    return digest.hexdigest(), len(rows), total


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    try:
        value = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicHeadError(f"cannot read {CONTRACT_PATH}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublicHeadError("public-head contract is not an object")
    return value


def validate_contract(root: Path, contract: dict[str, Any]) -> list[str]:
    """Validate shape, cross-contract identity, paths, and artifact digests."""
    errors: list[str] = []
    expected_keys = {
        "version", "revision", "source_contract", "derived_lane_id", "base_lane",
        "base_ref", "target_ref", "observed_date", "derivation", "candidate",
    }
    if set(contract) != expected_keys:
        errors.append(f"top-level fields differ: {sorted(set(contract) ^ expected_keys)}")
    if contract.get("version") != 1:
        errors.append("version is not 1")
    revision = (root / "REVISION.txt").read_text(encoding="utf-8").strip()
    if contract.get("revision") != revision:
        errors.append("revision mismatch")
    source_relative = contract.get("source_contract")
    if source_relative != "data/current_source_contract.json":
        errors.append("source contract path mismatch")
    try:
        source_contract = load_source_contract(root)
    except Exception as exc:  # fail closed at the authority boundary
        errors.append(f"source contract unreadable: {exc}")
        source_contract = {}

    lanes = source_contract.get("source_bundle", {}).get("lanes", {})
    derived = source_contract.get("derived_lanes", {})
    base_lane = contract.get("base_lane")
    derived_lane = contract.get("derived_lane_id")
    if base_lane not in lanes:
        errors.append("base lane missing from source contract")
    elif lanes[base_lane].get("head") != contract.get("base_ref"):
        errors.append("base ref differs from source contract")
    if derived_lane not in derived:
        errors.append("derived lane missing from source contract")
    else:
        details = derived[derived_lane]
        if details.get("base_lane") != base_lane:
            errors.append("derived lane base mismatch")
        if details.get("head") != contract.get("target_ref"):
            errors.append("derived lane head mismatch")
        if details.get("materialization_contract") != CONTRACT_PATH.as_posix():
            errors.append("derived lane materialization path mismatch")

    for field in ("base_ref", "target_ref"):
        if not _hex(contract.get(field), 40):
            errors.append(f"{field} is not a full SHA-1")

    derivation = contract.get("derivation")
    if not isinstance(derivation, dict):
        errors.append("derivation is not an object")
        derivation = {}
    patch = derivation.get("delta_patch")
    if not isinstance(patch, dict) or set(patch) != {"path", "sha256"}:
        errors.append("delta patch descriptor invalid")
    else:
        path = patch.get("path")
        digest = patch.get("sha256")
        if not safe_relative(path):
            errors.append("delta patch path unsafe")
        elif not (root / path).is_file():
            errors.append("delta patch missing")
        elif sha256_path(root / path) != digest:
            errors.append("delta patch digest mismatch")
        if not _hex(digest, 64):
            errors.append("delta patch SHA-256 invalid")

    changed = derivation.get("changed_files")
    paths: list[str] = []
    if not isinstance(changed, list) or not changed:
        errors.append("changed_files is empty or invalid")
        changed = []
    for index, row in enumerate(changed):
        if not isinstance(row, dict) or set(row) != {"path", "old_blob_sha1", "new_blob_sha1"}:
            errors.append(f"changed file {index} fields invalid")
            continue
        path = row.get("path")
        if not safe_relative(path):
            errors.append(f"changed file {index} path unsafe")
        else:
            paths.append(path)
        for field in ("old_blob_sha1", "new_blob_sha1"):
            if not _hex(row.get(field), 40):
                errors.append(f"changed file {index} {field} invalid")
    if len(paths) != len(set(paths)):
        errors.append("changed paths are not unique")
    if len(paths) != 8:
        errors.append("changed path count is not 8")

    sequence = derivation.get("commit_sequence")
    if not isinstance(sequence, list) or len(sequence) != derivation.get("commits_ahead"):
        errors.append("commit sequence/count mismatch")
        sequence = []
    if sequence and sequence[-1].get("ref") != contract.get("target_ref"):
        errors.append("commit sequence does not end at target")
    if sum(isinstance(row, dict) and row.get("kind") == "patch" for row in sequence) != derivation.get("patch_bearing_commits"):
        errors.append("patch-bearing commit count mismatch")
    for row in sequence:
        if not isinstance(row, dict) or set(row) != {"ref", "kind", "subject"}:
            errors.append("commit sequence row invalid")
            continue
        if not _hex(row.get("ref"), 40) or row.get("kind") not in {"patch", "merge"}:
            errors.append("commit sequence identity invalid")

    for field in ("base_tree_inventory_sha256", "target_tree_inventory_sha256"):
        if not _hex(derivation.get(field), 64):
            errors.append(f"{field} invalid")
    if not isinstance(derivation.get("tree_file_count"), int) or derivation.get("tree_file_count", 0) <= 0:
        errors.append("tree_file_count invalid")
    if not isinstance(derivation.get("tree_bytes"), int) or derivation.get("tree_bytes", 0) <= 0:
        errors.append("tree_bytes invalid")

    candidate = contract.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != {"path", "sha256", "target_paths"}:
        errors.append("candidate descriptor invalid")
        candidate = {}
    candidate_path = candidate.get("path")
    if not safe_relative(candidate_path):
        errors.append("candidate path unsafe")
    elif not (root / candidate_path).is_file():
        errors.append("candidate missing")
    elif sha256_path(root / candidate_path) != candidate.get("sha256"):
        errors.append("candidate digest mismatch")
    targets = candidate.get("target_paths")
    if not isinstance(targets, list) or not targets or not all(safe_relative(item) for item in targets):
        errors.append("candidate target paths invalid")
        targets = []
    elif len(targets) != len(set(targets)):
        errors.append("candidate target paths not unique")
    overlap = sorted(set(paths) & set(targets))
    if overlap:
        errors.append(f"public delta overlaps candidate targets: {overlap}")
    return errors


def materialize(
    source_zip: Path,
    destination: Path,
    *,
    root: Path = ROOT,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract the base lane, apply the exact delta, and prove content identity."""
    root = root.resolve()
    source_zip = source_zip.resolve()
    destination = destination.resolve()
    contract = load_contract(root) if contract is None else contract
    errors = validate_contract(root, contract)
    if errors:
        raise PublicHeadError("contract validation failed: " + "; ".join(errors))
    if destination.exists() and any(destination.iterdir()):
        raise PublicHeadError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    derivation = contract["derivation"]
    changed = derivation["changed_files"]
    expected_paths = {row["path"] for row in changed}
    extracted = safe_extract_tar_gz_member(
        source_zip,
        archive_member_name(contract["base_lane"]),
        destination,
    )
    base_identity = inventory_identity(destination)
    if base_identity[0] != derivation["base_tree_inventory_sha256"]:
        raise PublicHeadError(f"base tree digest mismatch: {base_identity[0]}")
    for row in changed:
        observed = git_blob_sha1_path(destination / row["path"])
        if observed != row["old_blob_sha1"]:
            raise PublicHeadError(f"base blob mismatch for {row['path']}: {observed}")

    before = file_inventory(destination)
    patch_path = root / derivation["delta_patch"]["path"]
    check = run_bounded(
        ["git", "apply", "--check", str(patch_path)],
        cwd=destination,
        timeout=60,
    )
    if check.returncode != 0:
        raise PublicHeadError(f"public delta check failed: {check.stdout[-2000:]}")
    apply = run_bounded(["git", "apply", str(patch_path)], cwd=destination, timeout=60)
    if apply.returncode != 0:
        raise PublicHeadError(f"public delta apply failed: {apply.stdout[-2000:]}")

    after = file_inventory(destination)
    observed_changed = {
        path.as_posix() for path in set(before) | set(after) if before.get(path) != after.get(path)
    }
    if observed_changed != expected_paths:
        raise PublicHeadError(
            f"changed path set mismatch: expected={sorted(expected_paths)} observed={sorted(observed_changed)}"
        )
    for row in changed:
        observed = git_blob_sha1_path(destination / row["path"])
        if observed != row["new_blob_sha1"]:
            raise PublicHeadError(f"target blob mismatch for {row['path']}: {observed}")

    target_identity = inventory_identity(destination)
    expected_identity = (
        derivation["target_tree_inventory_sha256"],
        derivation["tree_file_count"],
        derivation["tree_bytes"],
    )
    if target_identity != expected_identity:
        raise PublicHeadError(
            f"target tree identity mismatch: expected={expected_identity} observed={target_identity}"
        )
    return {
        "status": "pass",
        "base_lane": contract["base_lane"],
        "base_ref": contract["base_ref"],
        "target_ref": contract["target_ref"],
        "extracted_files": extracted,
        "changed_paths": sorted(observed_changed),
        "base_tree": {
            "inventory_sha256": base_identity[0], "files": base_identity[1], "bytes": base_identity[2]
        },
        "target_tree": {
            "inventory_sha256": target_identity[0], "files": target_identity[1], "bytes": target_identity[2]
        },
        "delta_patch": derivation["delta_patch"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    destination = args.destination.resolve()
    if args.replace and destination.exists():
        shutil.rmtree(destination)
    try:
        source_zip, _rows = locate_source_bundle(args.source_zip)
        result = materialize(source_zip, destination, root=root)
        print(canonical_json(result), end="")
        return 0
    except (PublicHeadError, OSError) as exc:
        print(canonical_json({"status": "fail", "error": str(exc)}), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
