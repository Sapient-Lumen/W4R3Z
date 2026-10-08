#!/usr/bin/env python3
"""Validate source/model parity for current wishlist scheduler evidence."""
from __future__ import annotations

import argparse
import copy
import json
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

CONTRACT_PATH = Path("data/current_model_source_differential_contract.json")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(
    root: Path,
    contract: dict[str, Any],
    *,
    overrides: dict[str, Any] | None = None,
) -> tuple[list[dict[str, str]], list[str]]:
    revision = derive_revision(root)
    checks: list[dict[str, str]] = []
    errors: list[str] = []
    overrides = overrides or {}

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    expected_fields = {
        "version", "revision", "packet_id", "source", "candidate_patch", "artifacts",
        "states", "required_scenarios", "expected_policy", "corrected_false_green", "summary",
    }
    add("contract fields exact", set(contract) == expected_fields, sorted(set(contract) ^ expected_fields))
    add("contract version", contract.get("version") == 1, contract.get("version"))
    add("contract revision", contract.get("revision") == revision, contract.get("revision"))
    add("packet id", contract.get("packet_id") == "WISHLIST-SCHED-01", contract.get("packet_id"))

    source = contract.get("source")
    add("source descriptor", isinstance(source, dict) and set(source) == {"lane", "ref", "public_head_contract"}, source)
    if isinstance(source, dict):
        public_path = source.get("public_head_contract")
        add("public-head contract path", public_path == "data/current_public_head_contract.json", public_path)
        try:
            public = _load(root / str(public_path))
        except Exception as exc:
            add("public-head contract readable", False, exc)
        else:
            add("public-head contract readable", True)
            add("source lane bound", source.get("lane") == public.get("derived_lane_id"), source.get("lane"))
            add("source ref bound", source.get("ref") == public.get("target_ref"), source.get("ref"))

    for label, descriptor in (("candidate patch", contract.get("candidate_patch")),):
        valid = isinstance(descriptor, dict) and set(descriptor) == {"path", "sha256"}
        add(f"{label} descriptor", valid, descriptor)
        if valid:
            relative = descriptor["path"]
            path = root / relative
            add(f"{label} safe path", safe_relative(relative), relative)
            add(f"{label} exists", path.is_file() and not path.is_symlink(), relative)
            if path.is_file():
                add(f"{label} digest", sha256_path(path) == descriptor["sha256"], descriptor["sha256"])

    artifacts = contract.get("artifacts")
    add("artifact descriptors", isinstance(artifacts, dict) and set(artifacts) == {"model", "source_witness"}, artifacts)
    if isinstance(artifacts, dict):
        for name, descriptor in artifacts.items():
            valid = isinstance(descriptor, dict) and set(descriptor) == {"path", "sha256"}
            add(f"artifact {name} descriptor", valid, descriptor)
            if not valid:
                continue
            relative = descriptor["path"]
            path = root / relative
            add(f"artifact {name} safe path", safe_relative(relative), relative)
            add(f"artifact {name} exists", path.is_file() and not path.is_symlink(), relative)
            if path.is_file():
                add(f"artifact {name} digest", sha256_path(path) == descriptor["sha256"], descriptor["sha256"])

    corrected = contract.get("corrected_false_green")
    expected_corrected = {
        "forbidden_model_fragment", "forbidden_test_name", "model_path", "required_test_name", "test_path"
    }
    add("false-green descriptor", isinstance(corrected, dict) and set(corrected) == expected_corrected, corrected)
    if isinstance(corrected, dict):
        try:
            model_text = (root / corrected["model_path"]).read_text(encoding="utf-8")
            test_text = (root / corrected["test_path"]).read_text(encoding="utf-8")
        except Exception as exc:
            add("false-green files readable", False, exc)
        else:
            add("false-green files readable", True)
            add("forbidden model shortcut absent", corrected["forbidden_model_fragment"] not in model_text)
            add("forbidden test absent", corrected["forbidden_test_name"] not in test_text)
            add("current-bug witness test present", corrected["required_test_name"] in test_text)

    required = contract.get("required_scenarios")
    add(
        "required scenarios",
        isinstance(required, list) and bool(required) and len(required) == len(set(required))
        and all(isinstance(item, str) and item for item in required),
        required,
    )
    required_set = set(required) if isinstance(required, list) else set()

    states = contract.get("states")
    add("states exact", isinstance(states, dict) and set(states) == {"current", "candidate"}, states)
    loaded: dict[str, dict[str, Any]] = {}
    if isinstance(states, dict):
        for state in ("current", "candidate"):
            descriptor = states.get(state)
            valid = isinstance(descriptor, dict) and set(descriptor) == {"model", "source"}
            add(f"{state} state descriptor", valid, descriptor)
            if not valid:
                continue
            for kind in ("model", "source"):
                relative = descriptor[kind]
                add(f"{state} {kind} safe path", safe_relative(relative), relative)
                try:
                    payload = copy.deepcopy(overrides.get(relative, _load(root / relative)))
                except Exception as exc:
                    add(f"{state} {kind} readable", False, exc)
                    continue
                add(f"{state} {kind} readable", isinstance(payload, dict), type(payload).__name__)
                if isinstance(payload, dict):
                    loaded[f"{state}:{kind}"] = payload
                    add(f"{state} {kind} scenario set", set(payload) == required_set, sorted(set(payload) ^ required_set))
            model = loaded.get(f"{state}:model")
            source_payload = loaded.get(f"{state}:source")
            add(f"{state} model/source exact parity", model is not None and model == source_payload)

    policy = contract.get("expected_policy")
    expected_policy_fields = {
        "current_single_disabled_selected", "current_all_disabled_selected",
        "candidate_single_disabled_selected", "candidate_all_disabled_selected", "unchanged_scenarios",
    }
    add("expected-policy fields", isinstance(policy, dict) and set(policy) == expected_policy_fields, policy)
    if isinstance(policy, dict):
        current = loaded.get("current:source", {})
        candidate = loaded.get("candidate:source", {})
        add(
            "current single-disabled policy",
            current.get("single_disabled", {}).get("selected") == policy.get("current_single_disabled_selected"),
        )
        add(
            "current all-disabled policy",
            current.get("all_disabled", {}).get("selected") == policy.get("current_all_disabled_selected"),
        )
        add(
            "candidate single-disabled policy",
            candidate.get("single_disabled", {}).get("selected") == policy.get("candidate_single_disabled_selected"),
        )
        add(
            "candidate all-disabled policy",
            candidate.get("all_disabled", {}).get("selected") == policy.get("candidate_all_disabled_selected"),
        )
        unchanged = policy.get("unchanged_scenarios")
        unchanged_ok = isinstance(unchanged, list) and all(current.get(name) == candidate.get(name) for name in unchanged)
        add("unchanged scenario parity", unchanged_ok, unchanged)

    summary_relative = contract.get("summary")
    add("summary safe path", safe_relative(summary_relative), summary_relative)
    try:
        summary = copy.deepcopy(overrides.get(summary_relative, _load(root / str(summary_relative))))
    except Exception as exc:
        add("summary readable", False, exc)
    else:
        add("summary readable", isinstance(summary, dict), type(summary).__name__)
        if isinstance(summary, dict):
            add("summary status", summary.get("status") == "pass", summary.get("status"))
            add("summary revision", summary.get("revision") == revision, summary.get("revision"))
            add("summary packet", summary.get("packet_id") == contract.get("packet_id"), summary.get("packet_id"))
            add(
                "summary patch digest",
                summary.get("candidate_patch", {}).get("sha256") == contract.get("candidate_patch", {}).get("sha256"),
            )
            add(
                "summary source ref",
                summary.get("source", {}).get("executable_source_ref") == source.get("ref") if isinstance(source, dict) else False,
            )

    return checks, errors


def mutation_checks(root: Path, contract: dict[str, Any]) -> list[dict[str, str]]:
    mutations: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    wrong_revision = copy.deepcopy(contract)
    wrong_revision["revision"] = "rev0000"
    mutations.append(("stale revision", wrong_revision, {}))

    wrong_digest = copy.deepcopy(contract)
    wrong_digest["candidate_patch"]["sha256"] = "0" * 64
    mutations.append(("patch digest drift", wrong_digest, {}))

    omitted = copy.deepcopy(contract)
    omitted["required_scenarios"] = omitted["required_scenarios"][:-1]
    mutations.append(("scenario omitted", omitted, {}))

    current_source_path = contract["states"]["current"]["source"]
    current_source = _load(root / current_source_path)
    hidden_bug = copy.deepcopy(current_source)
    hidden_bug["single_disabled"]["selected"] = [None]
    mutations.append(("current source bug hidden", copy.deepcopy(contract), {current_source_path: hidden_bug}))

    candidate_source_path = contract["states"]["candidate"]["source"]
    candidate_source = _load(root / candidate_source_path)
    regressed = copy.deepcopy(candidate_source)
    regressed["all_disabled"]["selected"] = ["c", "c", "c", "c"]
    mutations.append(("candidate regression", copy.deepcopy(contract), {candidate_source_path: regressed}))

    summary_path = contract["summary"]
    summary = _load(root / summary_path)
    failed_summary = copy.deepcopy(summary)
    failed_summary["status"] = "fail"
    mutations.append(("retained summary no longer passes", copy.deepcopy(contract), {summary_path: failed_summary}))

    rows: list[dict[str, str]] = []
    for name, mutant, overrides in mutations:
        _checks, errors = validate(root, mutant, overrides=overrides)
        rows.append({
            "mutation": name,
            "status": "pass" if errors else "fail",
            "detail": f"rejected with {len(errors)} error(s)" if errors else "mutation was accepted",
        })
    return rows


def audit(root: Path) -> dict[str, Any]:
    contract = _load(root / CONTRACT_PATH)
    checks, errors = validate(root, contract)
    mutations = mutation_checks(root, contract) if not errors else []
    if mutations and any(row["status"] != "pass" for row in mutations):
        errors.append("one or more differential mutations were accepted")
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
    write_json(root / f"data/{revision}_model_source_differential_audit.json", result)
    write_csv(
        root / f"data/{revision}_model_source_differential_checks.csv",
        result["checks"],
        fields=("check", "status", "detail"),
    )
    write_csv(
        root / f"data/{revision}_model_source_differential_mutations.csv",
        result["mutations"],
        fields=("mutation", "status", "detail"),
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
    print(canonical_json({key: value for key, value in result.items() if key not in {"checks", "mutations"}}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
