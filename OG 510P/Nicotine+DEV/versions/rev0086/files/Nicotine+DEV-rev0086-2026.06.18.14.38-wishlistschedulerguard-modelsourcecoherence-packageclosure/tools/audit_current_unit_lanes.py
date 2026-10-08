#!/usr/bin/env python3
"""Audit current unit-lane authority, completion semantics, and retained evidence."""
from __future__ import annotations

import argparse
import ast
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
    parse_junit_report,
    safe_relative,
    sha256_path,
    write_csv,
    write_json,
)

CONTRACT_PATH = Path("data/current_unit_lane_contract.json")
HEX64 = re.compile(r"[0-9a-f]{64}")
LANES = ("baseline", "patched")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def validate_contract(root: Path, contract: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    revision = derive_revision(root)
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("contract version", contract.get("version") == 2, contract.get("version"))
    add("contract revision", contract.get("revision") == revision, contract.get("revision"))
    for key in ("candidate_contract", "completion_wrapper", "suite_path"):
        add(f"safe path: {key}", safe_relative(contract.get(key)), contract.get(key))
    expected = contract.get("expected_testcases")
    add("expected testcase count", isinstance(expected, int) and expected > 0, expected)

    bindings = contract.get("tool_bindings")
    add("tool bindings exact keys", isinstance(bindings, dict) and set(bindings) == {"runner", "completion_wrapper"}, bindings)
    if isinstance(bindings, dict):
        paths: list[str] = []
        for name in ("runner", "completion_wrapper"):
            binding = bindings.get(name)
            add(f"tool binding object: {name}", isinstance(binding, dict), binding)
            if not isinstance(binding, dict):
                continue
            relative = binding.get("path")
            digest = binding.get("sha256")
            add(f"tool binding path: {name}", safe_relative(relative), relative)
            add(f"tool binding digest syntax: {name}", isinstance(digest, str) and HEX64.fullmatch(digest) is not None, digest)
            if safe_relative(relative):
                path = root / relative
                paths.append(str(relative))
                add(f"tool exists: {name}", path.is_file() and not path.is_symlink(), relative)
                if path.is_file() and isinstance(digest, str):
                    add(f"tool digest matches: {name}", sha256_path(path) == digest, digest)
        add("tool binding paths unique", len(paths) == len(set(paths)), paths)
        wrapper = bindings.get("completion_wrapper", {}) if isinstance(bindings.get("completion_wrapper"), dict) else {}
        add("wrapper binding agrees with path", wrapper.get("path") == contract.get("completion_wrapper"), wrapper)

    profiles = contract.get("profiles")
    add("profiles nonempty mapping", isinstance(profiles, dict) and bool(profiles), type(profiles).__name__)
    result_templates: list[str] = []
    evidence_roots: list[str] = []
    if isinstance(profiles, dict):
        for name, profile in profiles.items():
            add(f"profile mapping: {name}", isinstance(profile, dict), profile)
            if not isinstance(profile, dict):
                continue
            add(f"profile source mode: {name}", profile.get("source_mode") in {"bundled-lane", "derived-public-head"}, profile.get("source_mode"))
            for field in ("evidence_root", "result_template"):
                value = profile.get(field)
                sample = value.replace("{lane}", "baseline") if isinstance(value, str) else value
                add(f"profile safe {field}: {name}", safe_relative(sample), value)
            result_templates.append(str(profile.get("result_template")))
            evidence_roots.append(str(profile.get("evidence_root")))
        add("result templates unique", len(result_templates) == len(set(result_templates)), result_templates)
        add("evidence roots unique", len(evidence_roots) == len(set(evidence_roots)), evidence_roots)
    return checks, errors


def wrapper_semantics(root: Path, contract: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    path = root / str(contract.get("completion_wrapper", ""))
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        add("completion wrapper parse", False, exc)
        return checks, errors
    add("completion wrapper parse", True, path.relative_to(root))
    main = next((node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"), None)
    add("completion wrapper main", main is not None)
    segment = ast.get_source_segment(source, main) if main is not None else ""
    segment = segment or ""
    pytest_index = segment.find("pytest.main(")
    marker_index = segment.find("_write_marker(")
    exit_index = segment.find("os._exit(")
    add("pytest main called", pytest_index >= 0, pytest_index)
    add("marker follows pytest return", pytest_index >= 0 and marker_index > pytest_index, {"pytest": pytest_index, "marker": marker_index})
    add("immediate exit follows marker", marker_index >= 0 and exit_index > marker_index, {"marker": marker_index, "exit": exit_index})
    lowered = segment.lower()
    add("no junit completion inference", "junit" not in lowered and "xml" not in lowered, segment[:240])
    add("no timer or thread completion inference", "sleep(" not in lowered and "thread" not in lowered, segment[:240])
    add("atomic marker fsync", "os.fsync" in source and ".replace(path)" in source)
    return checks, errors


def evidence_checks(root: Path, contract: dict[str, Any]) -> tuple[list[dict[str, str]], list[str], list[dict[str, Any]]]:
    revision = derive_revision(root)
    candidate_contract = _load(root / contract["candidate_contract"])
    current_id = candidate_contract.get("current_candidate_id")
    candidates = {
        item.get("artifact_id"): item for item in candidate_contract.get("artifacts", [])
        if isinstance(item, dict)
    }
    current = candidates.get(current_id, {})
    source_contract = _load(root / "data/current_source_contract.json")
    public_contract = _load(root / "data/current_public_head_contract.json")
    checks: list[dict[str, str]] = []
    errors: list[str] = []
    inventory: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    profiles = contract.get("profiles", {})
    for profile_name, profile in profiles.items():
        expected_ref = None
        if profile.get("source_mode") == "bundled-lane":
            lane = profile.get("source_lane")
            expected_ref = source_contract.get("source_bundle", {}).get("lanes", {}).get(lane, {}).get("head")
        elif profile.get("source_mode") == "derived-public-head":
            expected_ref = public_contract.get("target_ref")
        for lane in LANES:
            relative = profile["result_template"].format(lane=lane)
            path = root / relative
            prefix = f"{profile_name}/{lane}"
            add(f"result exists: {prefix}", path.is_file() and not path.is_symlink(), relative)
            if not path.is_file():
                continue
            try:
                record = _load(path)
            except Exception as exc:
                add(f"result readable: {prefix}", False, exc)
                continue
            add(f"result readable: {prefix}", True)
            add(f"result pass: {prefix}", record.get("status") == "pass", record.get("status"))
            add(f"result revision: {prefix}", record.get("revision") == revision, record.get("revision"))
            add(f"result profile: {prefix}", record.get("profile") == profile_name, record.get("profile"))
            add(f"result lane: {prefix}", record.get("lane") == lane, record.get("lane"))
            tests = record.get("tests", {})
            expected_count = contract.get("expected_testcases")
            add(f"test count: {prefix}", tests.get("total") == expected_count, tests)
            add(f"test outcomes: {prefix}", tests.get("passed") == 60 and tests.get("skipped") == 1 and tests.get("failed") == 0 and tests.get("error") == 0 and tests.get("returncode") == 0, tests)
            source = record.get("source", {})
            add(f"source ref: {prefix}", source.get("executable_source_ref") == expected_ref, {"actual": source.get("executable_source_ref"), "expected": expected_ref})
            completion = record.get("pytest_completion", {})
            marker_relative = completion.get("path")
            marker_path = root / marker_relative if safe_relative(marker_relative) else root / "missing"
            marker = completion.get("marker", {})
            add(f"completion marker path: {prefix}", safe_relative(marker_relative), marker_relative)
            add(f"completion marker exists: {prefix}", marker_path.is_file() and not marker_path.is_symlink(), marker_relative)
            add(f"completion marker digest: {prefix}", marker_path.is_file() and sha256_path(marker_path) == completion.get("sha256"), completion.get("sha256"))
            add(f"pytest main returned: {prefix}", marker.get("version") == 1 and marker.get("pytest_main_returned") is True and marker.get("exit_code") == 0, marker)
            junit = record.get("junit", {})
            junit_relative = junit.get("path")
            junit_path = root / junit_relative if safe_relative(junit_relative) else root / "missing"
            add(f"junit path: {prefix}", safe_relative(junit_relative), junit_relative)
            add(f"junit exists: {prefix}", junit_path.is_file() and not junit_path.is_symlink(), junit_relative)
            add(f"junit digest: {prefix}", junit_path.is_file() and sha256_path(junit_path) == junit.get("sha256"), junit.get("sha256"))
            rows = parse_junit_report(junit_path) if junit_path.is_file() else []
            add(f"junit rows: {prefix}", len(rows) == expected_count, len(rows))
            add(f"junit outcomes: {prefix}", all(row.get("outcome") in {"passed", "skipped"} for row in rows), len(rows))
            isolation = record.get("source_isolation", {})
            add(f"source cleanup: {prefix}", isolation.get("source_extraction_cleaned_after_run") is True and isolation.get("isolated_environment_cleaned_after_run") is True and isolation.get("cleaned_after_run") is True, isolation)
            add(f"no source writes: {prefix}", record.get("source_tree_final_writes") == [], record.get("source_tree_final_writes"))
            patch = record.get("candidate_patch", {})
            if lane == "patched":
                add(f"candidate applied: {prefix}", patch.get("applied") is True)
                add(f"candidate id: {prefix}", patch.get("artifact_id") == current_id, patch.get("artifact_id"))
                add(f"candidate path: {prefix}", patch.get("path") == current.get("path"), patch.get("path"))
                add(f"candidate digest: {prefix}", patch.get("sha256") == current.get("sha256"), patch.get("sha256"))
            else:
                add(f"baseline unpatched: {prefix}", patch.get("applied") is False and patch.get("path") is None and patch.get("sha256") is None, patch)
            lane_root = root / profile["evidence_root"] / lane
            residue = sorted(
                item.name for item in lane_root.iterdir()
                if item.name in {"pytest-exit-attestation.json", "source", "environment"}
            ) if lane_root.is_dir() else ["missing-lane-root"]
            add(f"no legacy lifecycle residue: {prefix}", not residue, residue)
            log = lane_root / "pytest.log"
            log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
            add(f"terminal summary retained: {prefix}", "60 passed, 1 skipped" in log_text, log_text[-160:])
            inventory.append({
                "profile": profile_name,
                "lane": lane,
                "record": relative,
                "source_ref": source.get("executable_source_ref", ""),
                "tests": tests.get("total", 0),
                "passed": tests.get("passed", 0),
                "skipped": tests.get("skipped", 0),
                "junit_sha256": junit.get("sha256", ""),
                "completion_sha256": completion.get("sha256", ""),
                "status": "pass" if record.get("status") == "pass" else "fail",
            })
    return checks, errors, inventory


def mutation_checks(root: Path, contract: dict[str, Any]) -> list[dict[str, str]]:
    mutations: list[tuple[str, dict[str, Any]]] = []
    wrong_revision = copy.deepcopy(contract)
    wrong_revision["revision"] = "rev0000"
    mutations.append(("wrong revision", wrong_revision))
    wrong_digest = copy.deepcopy(contract)
    wrong_digest["tool_bindings"]["completion_wrapper"]["sha256"] = "0" * 64
    mutations.append(("wrapper digest drift", wrong_digest))
    duplicate_template = copy.deepcopy(contract)
    names = list(duplicate_template["profiles"])
    duplicate_template["profiles"][names[1]]["result_template"] = duplicate_template["profiles"][names[0]]["result_template"]
    mutations.append(("duplicate result template", duplicate_template))
    unsafe_root = copy.deepcopy(contract)
    unsafe_root["profiles"][names[0]]["evidence_root"] = "../escape"
    mutations.append(("unsafe evidence root", unsafe_root))
    wrong_count = copy.deepcopy(contract)
    wrong_count["expected_testcases"] = 0
    mutations.append(("invalid testcase count", wrong_count))
    wrong_mode = copy.deepcopy(contract)
    wrong_mode["profiles"][names[0]]["source_mode"] = "guess"
    mutations.append(("unknown source mode", wrong_mode))

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
    contract = _load(root / CONTRACT_PATH)
    contract_checks, contract_errors = validate_contract(root, contract)
    wrapper_checks, wrapper_errors = wrapper_semantics(root, contract)
    evidence_rows, evidence_errors, inventory = evidence_checks(root, contract)
    mutations = mutation_checks(root, contract)
    errors = contract_errors + wrapper_errors + evidence_errors
    if any(row["status"] != "pass" for row in mutations):
        errors.append("one or more unit-lane mutations were accepted")
    checks = contract_checks + wrapper_checks + evidence_rows
    return {
        "revision": derive_revision(root),
        "status": "pass" if not errors else "fail",
        "contract": CONTRACT_PATH.as_posix(),
        "profiles": len(contract.get("profiles", {})),
        "lanes": len(inventory),
        "tests_observed": sum(int(row["tests"]) for row in inventory),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "mutation_checks_passed": sum(row["status"] == "pass" for row in mutations),
        "mutation_checks_total": len(mutations),
        "checks": checks,
        "mutations": mutations,
        "inventory": inventory,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_unit_lane_audit.json", result)
    write_csv(root / f"data/{revision}_unit_lane_checks.csv", result["checks"], fields=("check", "status", "detail"))
    write_csv(root / f"data/{revision}_unit_lane_mutations.csv", result["mutations"], fields=("mutation", "status", "detail"))
    write_csv(
        root / f"data/{revision}_unit_lane_inventory.csv",
        result["inventory"],
        fields=("profile", "lane", "record", "source_ref", "tests", "passed", "skipped", "junit_sha256", "completion_sha256", "status"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json({key: value for key, value in result.items() if key not in {"checks", "mutations", "inventory"}}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
