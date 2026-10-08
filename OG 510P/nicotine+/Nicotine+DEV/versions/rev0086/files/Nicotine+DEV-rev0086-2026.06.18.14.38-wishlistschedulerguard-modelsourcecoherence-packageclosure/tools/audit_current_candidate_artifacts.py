#!/usr/bin/env python3
"""Validate immutable candidate lineage and historical evidence bindings."""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    safe_relative,
    sha256_path,
    write_csv,
    write_json,
)

CONTRACT_PATH = Path("data/current_candidate_artifact_contract.json")
HEX64 = re.compile(r"[0-9a-f]{64}")


def pointer_value(value: object, pointer: object) -> object:
    if pointer is None:
        return None
    if not isinstance(pointer, list) or not all(isinstance(part, str) for part in pointer):
        raise ValueError(f"invalid pointer: {pointer!r}")
    current = value
    for part in pointer:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(part)
        current = current[part]
    return current


def validate_contract(root: Path, contract: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    revision = derive_revision(root)
    rows: list[dict[str, str]] = []
    errors: list[str] = []

    def add(check: str, passed: bool, detail: object = "") -> None:
        rows.append({"check": check, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{check}: {detail}")

    add("contract version", contract.get("version") == 4, contract.get("version"))
    expected_top_level_fields = {
        "artifacts",
        "current_candidate_id",
        "evidence_bindings",
        "required_current_evidence_records",
        "required_packet_bindings",
        "revision",
        "version",
    }
    add(
        "contract top-level fields exact",
        set(contract) == expected_top_level_fields,
        {
            "missing": sorted(expected_top_level_fields - set(contract)),
            "unexpected": sorted(set(contract) - expected_top_level_fields),
        },
    )
    add("contract revision", contract.get("revision") == revision, contract.get("revision"))
    artifacts = contract.get("artifacts")
    add("artifacts list", isinstance(artifacts, list) and bool(artifacts), type(artifacts).__name__)
    artifacts = artifacts if isinstance(artifacts, list) else []

    by_id: dict[str, dict[str, Any]] = {}
    paths: list[str] = []
    for index, artifact in enumerate(artifacts):
        valid_mapping = isinstance(artifact, dict)
        add(f"artifact {index} mapping", valid_mapping)
        if not valid_mapping:
            continue
        artifact_id = artifact.get("artifact_id")
        path_value = artifact.get("path")
        digest = artifact.get("sha256")
        lifecycle = artifact.get("lifecycle")
        add(f"artifact {index} id", isinstance(artifact_id, str) and bool(artifact_id), artifact_id)
        add(f"artifact {index} safe path", isinstance(path_value, str) and safe_relative(path_value), path_value)
        add(f"artifact {index} digest", isinstance(digest, str) and HEX64.fullmatch(digest) is not None, digest)
        add(f"artifact {index} lifecycle", lifecycle in {
            "current-research-prototype", "superseded-research-prototype"
        }, lifecycle)
        add(f"artifact {index} not selected", artifact.get("selected") is False, artifact.get("selected"))
        revisions = artifact.get("validated_revisions")
        add(
            f"artifact {index} validated revisions",
            isinstance(revisions, list) and bool(revisions)
            and all(isinstance(item, str) and re.fullmatch(r"rev\d{4}", item) for item in revisions),
            revisions,
        )
        packet_ids = artifact.get("packet_ids")
        add(
            f"artifact {index} packet IDs",
            isinstance(packet_ids, list) and bool(packet_ids)
            and len(packet_ids) == len(set(packet_ids))
            and all(isinstance(item, str) and item for item in packet_ids),
            packet_ids,
        )
        if isinstance(artifact_id, str):
            add(f"artifact id unique: {artifact_id}", artifact_id not in by_id)
            by_id[artifact_id] = artifact
        if isinstance(path_value, str):
            paths.append(path_value)
            path = root / path_value
            add(f"artifact exists: {path_value}", path.is_file() and not path.is_symlink())
            if path.is_file() and isinstance(digest, str):
                add(f"artifact digest matches: {path_value}", sha256_path(path) == digest, digest)

    add("artifact paths unique", len(paths) == len(set(paths)), paths)
    current_id = contract.get("current_candidate_id")
    add("current candidate id exists", isinstance(current_id, str) and current_id in by_id, current_id)
    if isinstance(current_id, str) and current_id in by_id:
        current = by_id[current_id]
        current_path = current.get("path", "")
        add("current lifecycle", current.get("lifecycle") == "current-research-prototype", current.get("lifecycle"))
        origin_revisions = re.findall(r"rev\d{4}", current_id)
        origin_revision = origin_revisions[-1] if origin_revisions else None
        add("current artifact origin revision in ID", origin_revision is not None, current_id)
        add(
            "current path origin-qualified",
            origin_revision is not None and origin_revision in str(current_path),
            {"origin": origin_revision, "path": current_path},
        )
        validated = current.get("validated_revisions", [])
        add("current revision explicitly revalidated", revision in validated, validated)
        current_count = sum(
            item.get("lifecycle") == "current-research-prototype"
            for item in artifacts if isinstance(item, dict)
        )
        add("one current prototype", current_count == 1, current_count)

    bindings = contract.get("evidence_bindings")
    add("evidence bindings list", isinstance(bindings, list) and bool(bindings), type(bindings).__name__)
    bindings = bindings if isinstance(bindings, list) else []
    for index, binding in enumerate(bindings):
        valid = isinstance(binding, dict)
        add(f"binding {index} mapping", valid)
        if not valid:
            continue
        record_value = binding.get("record")
        artifact_id = binding.get("artifact_id")
        role = binding.get("role")
        add(f"binding {index} role", role in {"historical", "current"}, role)
        add(f"binding {index} record path", isinstance(record_value, str) and safe_relative(record_value), record_value)
        add(f"binding {index} artifact exists", isinstance(artifact_id, str) and artifact_id in by_id, artifact_id)
        if not isinstance(record_value, str) or not safe_relative(record_value) or artifact_id not in by_id:
            continue
        record_path = root / record_value
        add(f"binding {index} record exists", record_path.is_file() and not record_path.is_symlink(), record_value)
        if not record_path.is_file():
            continue
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
            expected = by_id[artifact_id]
            digest_value = pointer_value(record, binding.get("sha256_pointer"))
            path_pointer = binding.get("path_pointer")
            path_observed = pointer_value(record, path_pointer) if path_pointer is not None else None
        except Exception as exc:
            add(f"binding {index} readable", False, exc)
            continue
        add(f"binding {index} readable", True)
        add(f"binding {index} digest bound", digest_value == expected.get("sha256"), digest_value)
        if path_pointer is not None:
            add(f"binding {index} path bound", path_observed == expected.get("path"), path_observed)
        if role == "current":
            add(f"binding {index} current artifact", artifact_id == current_id, artifact_id)

    required_current = contract.get("required_current_evidence_records")
    current_records = {
        item.get("record") for item in bindings
        if isinstance(item, dict) and item.get("role") == "current" and item.get("artifact_id") == current_id
    }
    add(
        "required current evidence records",
        isinstance(required_current, list)
        and len(required_current) == len(set(required_current))
        and all(isinstance(item, str) and safe_relative(item) for item in required_current),
        required_current,
    )
    if isinstance(required_current, list):
        add("current evidence coverage exact", current_records == set(required_current), {"observed": sorted(current_records), "required": sorted(required_current)})

    try:
        ledger = json.loads((root / "data/current_packet_dispositions.json").read_text(encoding="utf-8"))
        packets = {
            item.get("packet_id"): item for item in ledger.get("packets", [])
            if isinstance(item, dict) and isinstance(item.get("packet_id"), str)
        }
    except Exception as exc:
        add("packet ledger readable", False, exc)
    else:
        add("packet ledger readable", True)
        bindings = contract.get("required_packet_bindings")
        add("required packet bindings mapping", isinstance(bindings, dict) and bool(bindings), type(bindings).__name__)
        bindings = bindings if isinstance(bindings, dict) else {}
        bound_current: set[str] = set()
        for packet_id, artifact_id in bindings.items():
            add(f"binding packet exists: {packet_id}", packet_id in packets, packet_id)
            add(f"binding packet unselected: {packet_id}", packet_id in packets and packets[packet_id].get("selected_patch") is None)
            add(
                f"binding artifact valid: {packet_id}",
                artifact_id is None or artifact_id in by_id,
                artifact_id,
            )
            if artifact_id is not None and artifact_id in by_id:
                add(
                    f"artifact declares packet: {packet_id}",
                    packet_id in by_id[artifact_id].get("packet_ids", []),
                    by_id[artifact_id].get("packet_ids"),
                )
            if artifact_id == current_id:
                bound_current.add(packet_id)
        if isinstance(current_id, str) and current_id in by_id:
            declared = set(by_id[current_id].get("packet_ids", []))
            add("current packet bindings exact", declared == bound_current, {"declared": sorted(declared), "bound": sorted(bound_current)})
        relevant = {
            packet_id: item for packet_id, item in packets.items()
            if packet_id.startswith("SEARCH-AGAIN-EPOCH-01") or packet_id == "WISHLIST-CAP-01"
        }
        add("research candidates remain unselected", all(item.get("selected_patch") is None for item in relevant.values()), relevant)

    return rows, errors


def mutation_checks(root: Path, contract: dict[str, Any]) -> list[dict[str, str]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    wrong_revision = copy.deepcopy(contract)
    wrong_revision["revision"] = "rev0000"
    mutations.append(("wrong revision", wrong_revision))

    wrong_digest = copy.deepcopy(contract)
    wrong_digest["artifacts"][0]["sha256"] = "0" * 64
    mutations.append(("historical digest drift", wrong_digest))

    mutable_alias = copy.deepcopy(contract)
    current_id = mutable_alias["current_candidate_id"]
    for artifact in mutable_alias["artifacts"]:
        if artifact["artifact_id"] == current_id:
            artifact["path"] = "maintainer_artifacts/search-rekey-01/current.patch"
    mutations.append(("unqualified current path", mutable_alias))

    duplicate_current = copy.deepcopy(contract)
    duplicate_current["artifacts"][0]["lifecycle"] = "current-research-prototype"
    mutations.append(("multiple current candidates", duplicate_current))

    missing_revalidation = copy.deepcopy(contract)
    current_id = missing_revalidation["current_candidate_id"]
    for artifact in missing_revalidation["artifacts"]:
        if artifact.get("artifact_id") == current_id:
            artifact["validated_revisions"] = [
                item for item in artifact.get("validated_revisions", [])
                if item != derive_revision(root)
            ]
    mutations.append(("current revision not revalidated", missing_revalidation))

    broken_binding = copy.deepcopy(contract)
    broken_binding["evidence_bindings"][0]["sha256_pointer"] = ["missing"]
    mutations.append(("broken evidence pointer", broken_binding))

    wrong_packet_binding = copy.deepcopy(contract)
    wrong_packet_binding["required_packet_bindings"]["WISHLIST-CAP-01"] = wrong_packet_binding["current_candidate_id"]
    mutations.append(("cap packet falsely bound", wrong_packet_binding))

    missing_current_evidence = copy.deepcopy(contract)
    missing_current_evidence["evidence_bindings"] = [
        item for item in missing_current_evidence["evidence_bindings"]
        if item.get("record") != missing_current_evidence["required_current_evidence_records"][0]
    ]
    mutations.append(("missing current evidence binding", missing_current_evidence))

    legacy_alias = copy.deepcopy(contract)
    legacy_alias["historical_evidence_bindings"] = []
    mutations.append(("legacy duplicate evidence authority", legacy_alias))

    rows: list[dict[str, str]] = []
    for name, mutant in mutations:
        _checks, errors = validate_contract(root, mutant)
        rows.append({
            "mutation": name,
            "status": "pass" if errors else "fail",
            "detail": f"rejected with {len(errors)} error(s)" if errors else "mutation was accepted",
        })
    return rows


def audit(root: Path) -> dict[str, Any]:
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    checks, errors = validate_contract(root, contract)
    mutations = mutation_checks(root, contract)
    if any(row["status"] != "pass" for row in mutations):
        errors.append("one or more negative-control mutations were accepted")
    return {
        "revision": derive_revision(root),
        "status": "pass" if not errors else "fail",
        "contract": CONTRACT_PATH.as_posix(),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "mutation_checks_passed": sum(row["status"] == "pass" for row in mutations),
        "mutation_checks_total": len(mutations),
        "checks": checks,
        "mutations": mutations,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_candidate_artifact_audit.json", result)
    write_csv(
        root / f"data/{revision}_candidate_artifact_checks.csv",
        result["checks"],
        fields=("check", "status", "detail"),
    )
    write_csv(
        root / f"data/{revision}_candidate_artifact_mutations.csv",
        result["mutations"],
        fields=("mutation", "status", "detail"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    result = audit(args.root.resolve())
    if args.write_data:
        write_outputs(args.root.resolve(), result)
    print(canonical_json({key: value for key, value in result.items() if key not in {"checks", "mutations"}}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
