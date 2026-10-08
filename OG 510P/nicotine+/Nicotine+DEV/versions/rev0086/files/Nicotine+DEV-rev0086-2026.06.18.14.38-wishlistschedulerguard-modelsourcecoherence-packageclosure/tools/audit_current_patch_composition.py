#!/usr/bin/env python3
"""Audit current public-delta/candidate composition in both application orders."""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    file_inventory,
    run_bounded,
    safe_extract_tar_gz_member,
    safe_relative,
    sha256_path,
    write_csv,
    write_json,
)
from materialize_current_public_head import (  # noqa: E402
    inventory_identity,
    load_contract as load_public_contract,
    materialize,
)
from source_bundle_locator import archive_member_name, load_source_contract, locate_source_bundle  # noqa: E402

CONTRACT_PATH = Path("data/current_patch_composition_contract.json")
DIFF_HEADER = re.compile(r"^diff --git a/(.+) b/(.+)$")


class CompositionError(RuntimeError):
    """Raised when patch-composition authority cannot be established."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompositionError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompositionError(f"{path} is not an object")
    return value


def patch_targets(path: Path) -> list[str]:
    targets: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = DIFF_HEADER.match(line)
        if not match:
            continue
        old, new = match.groups()
        if old != new or not safe_relative(old):
            raise CompositionError(f"non-canonical patch header: {line}")
        targets.append(old)
    if not targets or len(targets) != len(set(targets)):
        raise CompositionError(f"empty or duplicate patch targets in {path}")
    return targets


def current_candidate(root: Path, relative: str) -> dict[str, Any]:
    contract = load_json(root / relative)
    current_id = contract.get("current_candidate_id")
    matches = [
        item for item in contract.get("artifacts", [])
        if isinstance(item, dict) and item.get("artifact_id") == current_id
    ]
    if len(matches) != 1:
        raise CompositionError("candidate contract does not identify exactly one current artifact")
    return matches[0]


def validate_authority(root: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_keys = {
        "version", "revision", "source_contract", "public_head_contract",
        "candidate_artifact_contract", "unit_lane_contract", "expected",
    }
    if set(contract) != expected_keys:
        errors.append(f"top-level fields differ: {sorted(set(contract) ^ expected_keys)}")
    revision = derive_revision(root)
    if contract.get("version") != 1 or contract.get("revision") != revision:
        errors.append("version or revision mismatch")
    for key in (
        "source_contract", "public_head_contract", "candidate_artifact_contract", "unit_lane_contract"
    ):
        if not safe_relative(contract.get(key)) or not (root / str(contract.get(key))).is_file():
            errors.append(f"authority path invalid: {key}")

    expected = contract.get("expected")
    if not isinstance(expected, dict) or set(expected) != {"candidate_id", "relationship", "composed_tree"}:
        errors.append("expected composition descriptor invalid")
        return errors
    if expected.get("relationship") != "disjoint-commutative":
        errors.append("composition relationship mismatch")
    tree = expected.get("composed_tree")
    if not isinstance(tree, dict) or set(tree) != {"inventory_sha256", "files", "bytes"}:
        errors.append("composed tree descriptor invalid")
    elif (
        not isinstance(tree.get("inventory_sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", tree["inventory_sha256"])
        or not isinstance(tree.get("files"), int)
        or tree["files"] <= 0
        or not isinstance(tree.get("bytes"), int)
        or tree["bytes"] <= 0
    ):
        errors.append("composed tree identity invalid")

    try:
        public = load_public_contract(root)
        candidate = current_candidate(root, contract["candidate_artifact_contract"])
        unit = load_json(root / contract["unit_lane_contract"])
    except Exception as exc:
        errors.append(str(exc))
        return errors
    if expected.get("candidate_id") != candidate.get("artifact_id"):
        errors.append("expected candidate ID is stale")
    public_candidate = public.get("candidate", {})
    if public_candidate.get("path") != candidate.get("path") or public_candidate.get("sha256") != candidate.get("sha256"):
        errors.append("public-head contract is not bound to current candidate")
    profiles = unit.get("profiles", {})
    exact = profiles.get("exact-public-head-current-candidate", {}) if isinstance(profiles, dict) else {}
    if exact.get("derived_lane") != public.get("derived_lane_id"):
        errors.append("exact-public-head unit profile is not bound to derived lane")
    return errors


def apply_patch(tree: Path, patch: Path, label: str, evidence: Path) -> tuple[bool, str]:
    check = run_bounded(
        ["git", "apply", "--check", "--whitespace=error-all", str(patch)],
        cwd=tree,
        timeout=60,
        output_path=evidence / f"{label}-check.log",
    )
    if check.returncode != 0:
        return False, f"{label} check returncode={check.returncode}"
    apply = run_bounded(
        ["git", "apply", "--whitespace=error-all", str(patch)],
        cwd=tree,
        timeout=60,
        output_path=evidence / f"{label}-apply.log",
    )
    if apply.returncode != 0:
        return False, f"{label} apply returncode={apply.returncode}"
    reverse = run_bounded(
        ["git", "apply", "--reverse", "--check", str(patch)],
        cwd=tree,
        timeout=60,
        output_path=evidence / f"{label}-reverse-check.log",
    )
    if reverse.returncode != 0:
        return False, f"{label} reverse check returncode={reverse.returncode}"
    return True, "clean apply and reverse preimage"


def audit(root: Path, source_zip: Path) -> dict[str, Any]:
    revision = derive_revision(root)
    contract = load_json(root / CONTRACT_PATH)
    rows: list[dict[str, str]] = []
    errors: list[str] = []

    def add(check: str, passed: bool, detail: object = "") -> None:
        rows.append({"check": check, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{check}: {detail}")

    authority_errors = validate_authority(root, contract)
    add("composition authority", not authority_errors, authority_errors)
    public = load_public_contract(root)
    candidate = current_candidate(root, contract["candidate_artifact_contract"])
    candidate_path = root / candidate["path"]
    public_path = root / public["derivation"]["delta_patch"]["path"]
    candidate_targets = patch_targets(candidate_path)
    public_targets = patch_targets(public_path)
    add("candidate digest", sha256_path(candidate_path) == candidate.get("sha256"), candidate.get("sha256"))
    add(
        "public delta digest",
        sha256_path(public_path) == public["derivation"]["delta_patch"]["sha256"],
        public["derivation"]["delta_patch"]["sha256"],
    )
    add("candidate targets match public-head descriptor", candidate_targets == public["candidate"]["target_paths"], candidate_targets)
    overlap = sorted(set(candidate_targets) & set(public_targets))
    add("patch target sets disjoint", not overlap, overlap)

    evidence = root / f"evidence/{revision}-patch-composition"
    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"{revision}-composition-", dir="/mnt/data"))
    public_first = scratch / "public-first"
    candidate_first = scratch / "candidate-first"
    identities: dict[str, dict[str, Any]] = {}
    try:
        materialize(source_zip, public_first, root=root, contract=public)
        ok, detail = apply_patch(public_first, candidate_path, "public-first-candidate", evidence)
        add("public then candidate applies", ok, detail)
        if ok:
            identity = inventory_identity(public_first)
            identities["public_then_candidate"] = {
                "inventory_sha256": identity[0], "files": identity[1], "bytes": identity[2]
            }

        candidate_first.mkdir(parents=True)
        source_contract = load_source_contract(root)
        base_lane = public["base_lane"]
        extracted = safe_extract_tar_gz_member(source_zip, archive_member_name(base_lane), candidate_first)
        add("candidate-first base extraction", extracted == public["derivation"]["tree_file_count"], extracted)
        ok_candidate, detail_candidate = apply_patch(
            candidate_first, candidate_path, "candidate-first-candidate", evidence
        )
        add("candidate applies to base", ok_candidate, detail_candidate)
        ok_public = False
        if ok_candidate:
            ok_public, detail_public = apply_patch(
                candidate_first, public_path, "candidate-first-public", evidence
            )
            add("public delta applies after candidate", ok_public, detail_public)
        if ok_candidate and ok_public:
            identity = inventory_identity(candidate_first)
            identities["candidate_then_public"] = {
                "inventory_sha256": identity[0], "files": identity[1], "bytes": identity[2]
            }

        first_inventory = file_inventory(public_first) if public_first.is_dir() else {}
        second_inventory = file_inventory(candidate_first) if candidate_first.is_dir() else {}
        differences = sorted(
            path.as_posix()
            for path in set(first_inventory) | set(second_inventory)
            if first_inventory.get(path) != second_inventory.get(path)
        )
        add("application orders byte-identical", not differences, differences[:20])
        expected_tree = contract["expected"]["composed_tree"]
        add("composed tree identity pinned", identities.get("public_then_candidate") == expected_tree, identities.get("public_then_candidate"))
        add("both orders share pinned identity", identities.get("candidate_then_public") == expected_tree, identities.get("candidate_then_public"))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    add("composition scratch removed", not scratch.exists(), scratch)

    mutations: list[tuple[str, dict[str, Any]]] = []
    wrong_revision = copy.deepcopy(contract); wrong_revision["revision"] = "rev0000"
    mutations.append(("stale revision", wrong_revision))
    wrong_candidate = copy.deepcopy(contract); wrong_candidate["expected"]["candidate_id"] = "SEARCH-REKEY-01-rev0084"
    mutations.append(("stale current candidate", wrong_candidate))
    wrong_tree = copy.deepcopy(contract); wrong_tree["expected"]["composed_tree"]["inventory_sha256"] = "0" * 64
    mutations.append(("wrong composed tree", wrong_tree))
    wrong_relation = copy.deepcopy(contract); wrong_relation["expected"]["relationship"] = "order-sensitive"
    mutations.append(("wrong relationship", wrong_relation))
    unsafe_path = copy.deepcopy(contract); unsafe_path["unit_lane_contract"] = "../outside.json"
    mutations.append(("unsafe authority path", unsafe_path))
    mutation_rows: list[dict[str, str]] = []
    for label, mutant in mutations:
        mutant_errors = validate_authority(root, mutant)
        observed_identity = identities.get("public_then_candidate")
        if observed_identity != mutant.get("expected", {}).get("composed_tree"):
            mutant_errors.append("observed composed tree differs")
        rejected = bool(mutant_errors)
        mutation_rows.append({
            "mutation": label,
            "status": "pass" if rejected else "fail",
            "detail": "rejected" if rejected else "accepted",
        })
    add("negative controls rejected", all(row["status"] == "pass" for row in mutation_rows), mutation_rows)

    return {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "contract": CONTRACT_PATH.as_posix(),
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "mutation_checks_passed": sum(row["status"] == "pass" for row in mutation_rows),
        "mutation_checks_total": len(mutation_rows),
        "candidate": {
            "artifact_id": candidate.get("artifact_id"),
            "path": candidate.get("path"),
            "sha256": candidate.get("sha256"),
            "targets": candidate_targets,
        },
        "public_delta": {
            "path": public["derivation"]["delta_patch"]["path"],
            "sha256": public["derivation"]["delta_patch"]["sha256"],
            "targets": public_targets,
        },
        "identities": identities,
        "checks": rows,
        "mutations": mutation_rows,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_patch_composition_audit.json", {k: v for k, v in result.items() if k not in {"checks", "mutations"}})
    write_csv(root / f"data/{revision}_patch_composition_checks.csv", result["checks"], fields=("check", "status", "detail"))
    write_csv(root / f"data/{revision}_patch_composition_mutations.csv", result["mutations"], fields=("mutation", "status", "detail"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        source_zip, _inspections = locate_source_bundle(args.source_zip)
        result = audit(root, source_zip)
    except (CompositionError, OSError, ValueError) as exc:
        result = {"revision": derive_revision(root), "status": "fail", "error": str(exc)}
    if args.write_data and "checks" in result:
        write_outputs(root, result)
    print(canonical_json({k: v for k, v in result.items() if k not in {"checks", "mutations"}}), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
