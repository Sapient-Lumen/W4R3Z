#!/usr/bin/env python3
"""Cross-bind all current cube authorities and retained results.

A retained ``status: pass`` is not current evidence when its revision, source,
or candidate binding has drifted.  This audit validates both the unchanged
Search Again candidate and the independent WISHLIST-SCHED-01 correction.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, safe_relative, sha256_path, write_csv, write_json  # noqa: E402

CONTRACT_PATH = Path("data/current_contract_coherence_contract.json")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _current_candidate(contract: dict[str, Any]) -> dict[str, Any]:
    current_id = contract.get("current_candidate_id")
    matches = [item for item in contract.get("artifacts", []) if isinstance(item, dict) and item.get("artifact_id") == current_id]
    if len(matches) != 1:
        raise ValueError(f"current candidate count={len(matches)}")
    return matches[0]


def _snapshot_digest(root: Path, relatives: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(set(relatives)):
        path = root / relative
        digest.update(relative.encode("utf-8") + b"\0")
        if path.is_file() and not path.is_symlink():
            digest.update(sha256_path(path).encode("ascii"))
        else:
            digest.update(b"missing")
        digest.update(b"\n")
    return digest.hexdigest()


def _load_documents(root: Path, contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    relatives: set[str] = set()
    for field in ("revision_bound_contracts", "revision_neutral_contracts", "required_result_records"):
        values = contract.get(field)
        if isinstance(values, list):
            relatives.update(item for item in values if isinstance(item, str) and safe_relative(item))
    for field in (
        "revision_contract", "package_contract", "candidate_contract", "public_head_contract",
        "composition_contract", "unit_lane_contract", "search_action_contract",
        "model_source_contract", "packet_ledger",
    ):
        value = contract.get(field)
        if isinstance(value, str) and safe_relative(value):
            relatives.add(value)
    documents: dict[str, dict[str, Any]] = {}
    for relative in sorted(relatives):
        path = root / relative
        if path.is_file() and not path.is_symlink():
            try:
                documents[relative] = _load(path)
            except Exception:
                pass
    return documents


def validate(root: Path, contract: dict[str, Any], documents: dict[str, dict[str, Any]]) -> tuple[list[dict[str, str]], list[str], dict[str, Any]]:
    revision = derive_revision(root)
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    expected_fields = {
        "version", "revision", "revision_bound_contracts", "revision_neutral_contracts",
        "required_result_records", "revision_contract", "package_contract", "candidate_contract",
        "public_head_contract", "composition_contract", "unit_lane_contract", "search_action_contract",
        "model_source_contract", "packet_ledger",
    }
    add("coherence contract fields", set(contract) == expected_fields, sorted(set(contract) ^ expected_fields))
    add("coherence contract version", contract.get("version") == 2, contract.get("version"))
    add("coherence contract revision", contract.get("revision") == revision, contract.get("revision"))

    bound = contract.get("revision_bound_contracts") if isinstance(contract.get("revision_bound_contracts"), list) else []
    neutral = contract.get("revision_neutral_contracts") if isinstance(contract.get("revision_neutral_contracts"), list) else []
    results = contract.get("required_result_records") if isinstance(contract.get("required_result_records"), list) else []
    for name, values in (("revision-bound contracts", bound), ("revision-neutral contracts", neutral), ("result records", results)):
        add(f"{name} valid", bool(values) and len(values) == len(set(values)) and all(isinstance(v, str) and safe_relative(v) for v in values), values)
    add("bound and neutral sets disjoint", not (set(bound) & set(neutral)), sorted(set(bound) & set(neutral)))
    add("coherence contract self-bound", CONTRACT_PATH.as_posix() in bound, bound)

    for relative in bound:
        payload = documents.get(relative)
        add(f"revision-bound loaded: {relative}", isinstance(payload, dict))
        if isinstance(payload, dict):
            add(f"revision-bound value: {relative}", payload.get("revision") == revision, payload.get("revision"))
    for relative in neutral:
        payload = documents.get(relative)
        add(f"revision-neutral loaded: {relative}", isinstance(payload, dict))
        if isinstance(payload, dict):
            add(f"revision-neutral has no revision: {relative}", "revision" not in payload, payload.get("revision"))

    candidate_contract = documents.get(str(contract.get("candidate_contract")), {})
    public = documents.get(str(contract.get("public_head_contract")), {})
    composition = documents.get(str(contract.get("composition_contract")), {})
    unit = documents.get(str(contract.get("unit_lane_contract")), {})
    action = documents.get(str(contract.get("search_action_contract")), {})
    model_source = documents.get(str(contract.get("model_source_contract")), {})
    package = documents.get(str(contract.get("package_contract")), {})
    revision_contract = documents.get(str(contract.get("revision_contract")), {})
    ledger = documents.get(str(contract.get("packet_ledger")), {})
    source = documents.get("data/current_source_contract.json", {})

    try:
        search_candidate = _current_candidate(candidate_contract)
    except Exception as exc:
        search_candidate = {}
        add("search candidate resolvable", False, exc)
    else:
        add("search candidate resolvable", True, search_candidate.get("artifact_id"))
    search_id = search_candidate.get("artifact_id")
    search_path = search_candidate.get("path")
    search_sha = search_candidate.get("sha256")
    add("search candidate validates current revision", revision in search_candidate.get("validated_revisions", []), search_candidate.get("validated_revisions"))
    public_candidate = public.get("candidate", {})
    add("public candidate path current", public_candidate.get("path") == search_path, public_candidate)
    add("public candidate digest current", public_candidate.get("sha256") == search_sha, public_candidate)
    add("composition candidate current", composition.get("expected", {}).get("candidate_id") == search_id, composition.get("expected", {}).get("candidate_id"))
    add("search action candidate current", action.get("candidate_artifact_id") == search_id, action.get("candidate_artifact_id"))

    base_lane = public.get("base_lane")
    derived_lane = public.get("derived_lane_id")
    add("public base ref source-bound", source.get("source_bundle", {}).get("lanes", {}).get(base_lane, {}).get("head") == public.get("base_ref"), public.get("base_ref"))
    add("public target ref source-bound", source.get("derived_lanes", {}).get(derived_lane, {}).get("head") == public.get("target_ref"), public.get("target_ref"))
    exact_profile = unit.get("profiles", {}).get("exact-public-head-current-candidate", {})
    add("unit exact lane public-bound", exact_profile.get("derived_lane") == derived_lane, exact_profile.get("derived_lane"))

    scheduler_patch = model_source.get("candidate_patch", {})
    scheduler_path = scheduler_patch.get("path")
    scheduler_sha = scheduler_patch.get("sha256")
    add("scheduler patch path safe", isinstance(scheduler_path, str) and safe_relative(scheduler_path), scheduler_path)
    add("scheduler patch exists", isinstance(scheduler_path, str) and (root / scheduler_path).is_file(), scheduler_path)
    add("scheduler patch digest live", isinstance(scheduler_path, str) and (root / scheduler_path).is_file() and sha256_path(root / scheduler_path) == scheduler_sha, scheduler_sha)
    packets = {p.get("packet_id"): p for p in ledger.get("packets", []) if isinstance(p, dict)}
    scheduler_packet = packets.get("WISHLIST-SCHED-01", {})
    add("scheduler packet selected path", scheduler_packet.get("selected_patch") == scheduler_path, scheduler_packet.get("selected_patch"))
    add("scheduler packet closed", scheduler_packet.get("status") == "closed-research-disposition", scheduler_packet.get("status"))
    add("scheduler contract source ref", model_source.get("source", {}).get("ref") == public.get("target_ref"), model_source.get("source", {}).get("ref"))

    coherence_tool = "tools/audit_current_contract_coherence.py"
    add("package requires coherence contract", CONTRACT_PATH.as_posix() in package.get("base_required_paths", []), package.get("base_required_paths"))
    add("package requires model/source contract", "data/current_model_source_differential_contract.json" in package.get("base_required_paths", []), package.get("base_required_paths"))
    add("revision nominates coherence contract", CONTRACT_PATH.as_posix() in revision_contract.get("authority_paths", []))
    add("revision nominates coherence tool", coherence_tool in revision_contract.get("authority_paths", []))
    add("coherence tool current", coherence_tool in revision_contract.get("current_scripts", []))

    result_payloads: dict[str, dict[str, Any]] = {}
    for relative in results:
        payload = documents.get(relative)
        add(f"result loaded: {relative}", isinstance(payload, dict))
        if isinstance(payload, dict):
            result_payloads[relative] = payload
            add(f"result pass: {relative}", payload.get("status") == "pass", payload.get("status"))
            add(f"result current: {relative}", payload.get("revision") == revision, payload.get("revision"))

    public_result = result_payloads.get(f"data/{revision}_public_head_audit.json", {})
    expected_public_tree = {
        "inventory_sha256": public.get("derivation", {}).get("target_tree_inventory_sha256"),
        "files": public.get("derivation", {}).get("tree_file_count"),
        "bytes": public.get("derivation", {}).get("tree_bytes"),
    }
    add("public result ref bound", public_result.get("target_ref") == public.get("target_ref"), public_result.get("target_ref"))
    add("public result tree bound", public_result.get("materialization", {}).get("target_tree") == expected_public_tree, public_result.get("materialization", {}).get("target_tree"))

    composition_result = result_payloads.get(f"data/{revision}_patch_composition_audit.json", {})
    add("composition result candidate ID", composition_result.get("candidate", {}).get("artifact_id") == search_id)
    add("composition result candidate path", composition_result.get("candidate", {}).get("path") == search_path)
    add("composition result candidate digest", composition_result.get("candidate", {}).get("sha256") == search_sha)
    expected_tree = composition.get("expected", {}).get("composed_tree")
    add("composition public-first tree", composition_result.get("identities", {}).get("public_then_candidate") == expected_tree)
    add("composition candidate-first tree", composition_result.get("identities", {}).get("candidate_then_public") == expected_tree)

    revalidation = result_payloads.get(f"data/{revision}_search_candidate_revalidation.json", {})
    add("revalidation candidate path", revalidation.get("candidate_patch", {}).get("path") == search_path)
    add("revalidation candidate digest", revalidation.get("candidate_patch", {}).get("sha256") == search_sha)
    add("revalidation is transparent", revalidation.get("fresh_execution") is False and revalidation.get("execution_revision") == "rev0085", revalidation.get("fresh_execution"))
    add("revalidation lane count", revalidation.get("reused_lanes") == 4, revalidation.get("reused_lanes"))
    add("revalidation testcase count", revalidation.get("tests_revalidated") == 244, revalidation.get("tests_revalidated"))

    unit_result = result_payloads.get(f"data/{revision}_unit_lane_audit.json", {})
    add("unit audit profiles", unit_result.get("profiles") == 2, unit_result.get("profiles"))
    add("unit audit lanes", unit_result.get("lanes") == 4, unit_result.get("lanes"))
    add("unit audit tests", unit_result.get("tests_observed") == 244, unit_result.get("tests_observed"))

    scheduler_result = result_payloads.get(f"data/{revision}_wishlist_scheduler_summary.json", {})
    add("scheduler result packet", scheduler_result.get("packet_id") == "WISHLIST-SCHED-01", scheduler_result.get("packet_id"))
    add("scheduler result source ref", scheduler_result.get("source", {}).get("executable_source_ref") == public.get("target_ref"), scheduler_result.get("source", {}).get("executable_source_ref"))
    add("scheduler result patch path", scheduler_result.get("candidate_patch", {}).get("path") == scheduler_path)
    add("scheduler result patch digest", scheduler_result.get("candidate_patch", {}).get("sha256") == scheduler_sha)
    add("scheduler current parity", scheduler_result.get("model_source_parity", {}).get("current") is True)
    add("scheduler candidate parity", scheduler_result.get("model_source_parity", {}).get("candidate") is True)
    add("scheduler research tests", scheduler_result.get("research_tests", {}).get("passed") == 30 and scheduler_result.get("research_tests", {}).get("total") == 30, scheduler_result.get("research_tests"))
    for lane in ("baseline", "candidate"):
        tests = scheduler_result.get("upstream_units", {}).get(lane, {})
        add(f"scheduler {lane} units", tests.get("total") == 61 and tests.get("passed") == 60 and tests.get("skipped") == 1 and tests.get("failed") == 0 and tests.get("error") == 0, tests)

    differential = result_payloads.get(f"data/{revision}_model_source_differential_audit.json", {})
    add("differential contract current", differential.get("contract") == "data/current_model_source_differential_contract.json", differential.get("contract"))
    add("differential checks", differential.get("checks_passed") == differential.get("checks_total") and differential.get("checks_total", 0) > 0, differential.get("checks_total"))
    add("differential mutations", differential.get("mutation_checks_passed") == differential.get("mutation_checks_total") and differential.get("mutation_checks_total", 0) > 0, differential.get("mutation_checks_total"))

    snapshot_paths = sorted(set(bound + neutral + results + ["REVISION.txt", "README.md", "docs/START-HERE.md", coherence_tool]))
    snapshot = {
        "paths": len(snapshot_paths),
        "sha256": _snapshot_digest(root, snapshot_paths),
        "search_candidate_id": search_id,
        "search_candidate_sha256": search_sha,
        "scheduler_candidate_sha256": scheduler_sha,
        "public_target_ref": public.get("target_ref"),
    }
    return checks, errors, snapshot


def mutation_checks(root: Path, contract: dict[str, Any], documents: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    mutations: list[tuple[str, dict[str, dict[str, Any]], dict[str, Any]]] = []
    def docs_copy() -> dict[str, dict[str, Any]]:
        return copy.deepcopy(documents)

    d = docs_copy(); d["data/current_public_head_contract.json"]["revision"] = "rev0000"; mutations.append(("stale revision-bound contract", d, copy.deepcopy(contract)))
    d = docs_copy(); d["data/current_source_contract.json"]["revision"] = derive_revision(root); mutations.append(("revision added to neutral contract", d, copy.deepcopy(contract)))
    d = docs_copy(); d["data/current_public_head_contract.json"]["candidate"]["sha256"] = "0" * 64; mutations.append(("stale search candidate", d, copy.deepcopy(contract)))
    d = docs_copy(); d["data/current_model_source_differential_contract.json"]["candidate_patch"]["sha256"] = "0" * 64; mutations.append(("stale scheduler candidate", d, copy.deepcopy(contract)))
    d = docs_copy();
    for packet in d["data/current_packet_dispositions.json"].get("packets", []):
        if packet.get("packet_id") == "WISHLIST-SCHED-01": packet["selected_patch"] = None
    mutations.append(("scheduler ledger selection removed", d, copy.deepcopy(contract)))
    d = docs_copy(); result = f"data/{derive_revision(root)}_wishlist_scheduler_summary.json"; d[result]["status"] = "fail"; mutations.append(("retained scheduler result failed", d, copy.deepcopy(contract)))
    d = docs_copy(); d[result]["candidate_patch"]["sha256"] = "0" * 64; mutations.append(("scheduler result stale digest", d, copy.deepcopy(contract)))
    d = docs_copy(); d["data/current_package_contract.json"]["base_required_paths"] = [x for x in d["data/current_package_contract.json"].get("base_required_paths", []) if x != CONTRACT_PATH.as_posix()]; mutations.append(("package omits coherence contract", d, copy.deepcopy(contract)))
    d = docs_copy(); d["data/current_revision_contract.json"]["current_scripts"] = [x for x in d["data/current_revision_contract.json"].get("current_scripts", []) if x != "tools/audit_current_contract_coherence.py"]; mutations.append(("revision omits coherence tool", d, copy.deepcopy(contract)))

    rows: list[dict[str, str]] = []
    for name, mutant_docs, mutant_contract in mutations:
        _checks, errors, _snapshot = validate(root, mutant_contract, mutant_docs)
        rows.append({"mutation": name, "status": "pass" if errors else "fail", "detail": f"rejected with {len(errors)} error(s)" if errors else "mutation was accepted"})
    return rows


def audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    contract = _load(root / CONTRACT_PATH)
    documents = _load_documents(root, contract)
    checks, errors, snapshot = validate(root, contract, documents)
    mutations = mutation_checks(root, contract, documents)
    if any(row["status"] != "pass" for row in mutations):
        errors.append("one or more coherence mutations were accepted")
    return {
        "revision": derive_revision(root),
        "status": "pass" if not errors else "fail",
        "contract": CONTRACT_PATH.as_posix(),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "mutation_checks_passed": sum(row["status"] == "pass" for row in mutations),
        "mutation_checks_total": len(mutations),
        "authority_snapshot": snapshot,
        "checks": checks,
        "mutations": mutations,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_contract_coherence_audit.json", result)
    write_csv(root / f"data/{revision}_contract_coherence_checks.csv", result["checks"], fields=("check", "status", "detail"))
    write_csv(root / f"data/{revision}_contract_coherence_mutations.csv", result["mutations"], fields=("mutation", "status", "detail"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    result = audit(args.root.resolve())
    if args.write_data:
        write_outputs(args.root.resolve(), result)
    print(canonical_json({k: v for k, v in result.items() if k not in {"checks", "mutations"}}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
