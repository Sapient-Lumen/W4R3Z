#!/usr/bin/env python3
"""Run a declared current upstream-unit lane in a disposable source tree."""
from __future__ import annotations

import argparse
import json
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
    isolated_environment,
    parse_junit_report,
    purge_isolated_environment,
    run_bounded,
    safe_extract_tar_gz_member,
    safe_relative,
    sha256_path,
    write_json,
)
from materialize_current_public_head import load_contract as load_public_contract  # noqa: E402
from materialize_current_public_head import materialize  # noqa: E402
from source_bundle_locator import (  # noqa: E402
    archive_member_name,
    inspect_bundle,
    load_source_contract,
    locate_source_bundle,
)

CONTRACT_PATH = Path("data/current_unit_lane_contract.json")
MARKER_ENV = "CUBE_PYTEST_COMPLETION_MARKER"


class UnitLaneError(RuntimeError):
    """Raised when current unit-lane authority is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UnitLaneError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise UnitLaneError(f"{path} is not a JSON object")
    return value


def _current_candidate(root: Path, relative: str) -> dict[str, Any]:
    contract = _load_json(root / relative)
    current_id = contract.get("current_candidate_id")
    artifacts = contract.get("artifacts")
    if not isinstance(current_id, str) or not isinstance(artifacts, list):
        raise UnitLaneError("candidate contract lacks current candidate authority")
    matches = [item for item in artifacts if isinstance(item, dict) and item.get("artifact_id") == current_id]
    if len(matches) != 1:
        raise UnitLaneError(f"expected one current candidate, found {len(matches)}")
    candidate = matches[0]
    path_value = candidate.get("path")
    digest = candidate.get("sha256")
    if not safe_relative(path_value) or not isinstance(digest, str):
        raise UnitLaneError("current candidate path or digest invalid")
    path = root / path_value
    if not path.is_file() or path.is_symlink() or sha256_path(path) != digest:
        raise UnitLaneError("current candidate artifact identity mismatch")
    return candidate


def _changed_inventory(
    before: dict[Path, tuple[str, int]], after: dict[Path, tuple[str, int]]
) -> list[str]:
    return sorted(
        path.as_posix()
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )


def _validate_contract(root: Path, contract: dict[str, Any]) -> None:
    revision = derive_revision(root)
    if contract.get("version") != 2 or contract.get("revision") != revision:
        raise UnitLaneError("unit-lane contract version or revision mismatch")
    for key in ("candidate_contract", "completion_wrapper", "suite_path"):
        if not safe_relative(contract.get(key)):
            raise UnitLaneError(f"unsafe or missing contract path: {key}")
    tool_bindings = contract.get("tool_bindings")
    if not isinstance(tool_bindings, dict) or set(tool_bindings) != {"runner", "completion_wrapper"}:
        raise UnitLaneError("unit-lane tool bindings invalid")
    for name, binding in tool_bindings.items():
        if not isinstance(binding, dict) or not safe_relative(binding.get("path")):
            raise UnitLaneError(f"unit-lane tool binding path invalid: {name}")
        digest = binding.get("sha256")
        path = root / binding["path"]
        if not isinstance(digest, str) or not path.is_file() or sha256_path(path) != digest:
            raise UnitLaneError(f"unit-lane tool binding digest mismatch: {name}")
    if tool_bindings["completion_wrapper"]["path"] != contract["completion_wrapper"]:
        raise UnitLaneError("completion wrapper path disagrees with tool binding")
    if tool_bindings["runner"]["path"] != Path(__file__).resolve().relative_to(root).as_posix():
        raise UnitLaneError("runner path disagrees with executing tool")
    expected = contract.get("expected_testcases")
    if not isinstance(expected, int) or expected <= 0:
        raise UnitLaneError("expected_testcases must be positive")
    profiles = contract.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise UnitLaneError("unit-lane profiles missing")
    for name, profile in profiles.items():
        if not isinstance(name, str) or not isinstance(profile, dict):
            raise UnitLaneError("invalid unit-lane profile")
        for key in ("evidence_root", "result_template", "evidence_mode"):
            value = profile.get(key)
            candidate_value = value.replace("{lane}", "baseline") if isinstance(value, str) else value
            if key != "evidence_mode" and not safe_relative(candidate_value):
                raise UnitLaneError(f"profile {name} has unsafe {key}")
        if profile.get("source_mode") not in {"bundled-lane", "derived-public-head"}:
            raise UnitLaneError(f"profile {name} source mode invalid")


def _materialize_profile(
    *, root: Path, contract: dict[str, Any], profile: dict[str, Any], source_zip: Path, destination: Path
) -> dict[str, Any]:
    source_mode = profile["source_mode"]
    inspection = inspect_bundle(source_zip)
    if source_mode == "bundled-lane":
        lane = profile.get("source_lane")
        source_contract = load_source_contract(root)
        lanes = source_contract.get("source_bundle", {}).get("lanes", {})
        if not isinstance(lane, str) or lane not in lanes:
            raise UnitLaneError(f"unknown bundled source lane: {lane}")
        destination.mkdir(parents=True)
        extracted = safe_extract_tar_gz_member(source_zip, archive_member_name(lane), destination)
        return {
            "bundle": source_zip.name,
            "bundle_sha256": inspection.sha256,
            "lane": lane,
            "executable_source_ref": lanes[lane]["head"],
            "extracted_files": extracted,
        }

    public_path = profile.get("public_head_contract")
    if public_path != CONTRACT_PATH.parent.joinpath("current_public_head_contract.json").as_posix():
        # Keep the profile path explicit and safe without accepting an arbitrary authority alias.
        if public_path != "data/current_public_head_contract.json":
            raise UnitLaneError("derived profile public-head contract path mismatch")
    public_contract = load_public_contract(root)
    result = materialize(source_zip, destination, root=root, contract=public_contract)
    return {
        "bundle": source_zip.name,
        "bundle_sha256": inspection.sha256,
        "base_lane": public_contract["base_lane"],
        "base_ref": public_contract["base_ref"],
        "derived_lane": profile.get("derived_lane"),
        "executable_source_ref": public_contract["target_ref"],
        "materialization": result,
    }


def _completion_marker(path: Path, process_returncode: int) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not path.is_file() or path.is_symlink():
        return None, ["pytest completion marker missing"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"pytest completion marker unreadable: {exc}"]
    expected_keys = {"version", "pytest_main_returned", "exit_code"}
    if not isinstance(value, dict) or set(value) != expected_keys:
        errors.append("pytest completion marker fields invalid")
        return value if isinstance(value, dict) else None, errors
    if value.get("version") != 1 or value.get("pytest_main_returned") is not True:
        errors.append("pytest completion marker semantics invalid")
    if value.get("exit_code") != process_returncode:
        errors.append(
            f"pytest completion/process returncode mismatch: {value.get('exit_code')} != {process_returncode}"
        )
    return value, errors


def run_lane(root: Path, profile_name: str, lane: str, source_zip: Path) -> dict[str, Any]:
    contract = _load_json(root / CONTRACT_PATH)
    _validate_contract(root, contract)
    profiles = contract["profiles"]
    if profile_name not in profiles:
        raise UnitLaneError(f"unknown profile: {profile_name}")
    profile = profiles[profile_name]
    candidate = _current_candidate(root, contract["candidate_contract"])
    candidate_path = root / candidate["path"]
    revision = derive_revision(root)
    lane_root = root / profile["evidence_root"] / lane
    if lane_root.exists():
        shutil.rmtree(lane_root)
    lane_root.mkdir(parents=True)

    scratch = Path(tempfile.mkdtemp(prefix=f"{revision}-{profile_name}-{lane}-", dir="/mnt/data"))
    source = scratch / "source"
    environment_root = scratch / "environment"
    errors: list[str] = []
    result: dict[str, Any] | None = None
    source_cleaned = False
    environment_cleanup: dict[str, Any] = {
        "removed_directories": [], "entries": [], "entry_count": 0, "regular_files": 0,
        "symlinks": 0, "bytes": 0, "residual_directories": []
    }

    try:
        source_metadata = _materialize_profile(
            root=root, contract=contract, profile=profile, source_zip=source_zip, destination=source
        )
        suite = source / contract["suite_path"]
        if not suite.is_dir():
            raise UnitLaneError(f"unit suite missing: {suite}")

        patch_applied = False
        if lane == "patched":
            check = run_bounded(
                ["git", "apply", "--check", "--whitespace=error-all", str(candidate_path)],
                cwd=source,
                timeout=60,
                output_path=lane_root / "candidate-check.log",
            )
            if check.returncode != 0:
                errors.append(f"candidate check returncode={check.returncode}")
            else:
                apply = run_bounded(
                    ["git", "apply", "--whitespace=error-all", str(candidate_path)],
                    cwd=source,
                    timeout=60,
                    output_path=lane_root / "candidate-apply.log",
                )
                patch_applied = apply.returncode == 0
                if not patch_applied:
                    errors.append(f"candidate apply returncode={apply.returncode}")

        before = file_inventory(source)
        env, _cwd = isolated_environment(environment_root, python_paths=(source,))
        marker = lane_root / "pytest-completion.json"
        env[MARKER_ENV] = str(marker)
        junit = lane_root / "junit.xml"
        wrapper = root / contract["completion_wrapper"]
        command = [
            sys.executable,
            str(wrapper),
            "-q",
            "-p",
            "no:cacheprovider",
            str(suite),
        ]
        exclusions: list[str] = []
        for item in contract.get("optional_exclusions", []):
            if not isinstance(item, dict):
                continue
            command_name = item.get("when_command_missing")
            relative = item.get("path")
            if isinstance(command_name, str) and shutil.which(command_name) is None and safe_relative(relative):
                command.append(f"--ignore={source / relative}")
                exclusions.append(f"{relative} ({item.get('reason', 'optional tool unavailable')})")
        command.append(f"--junitxml={junit}")

        try:
            run = run_bounded(
                command,
                cwd=source,
                env=env,
                timeout=180,
                output_path=lane_root / "pytest.log",
            )
            rows = parse_junit_report(junit) if junit.is_file() else []
            marker_value, marker_errors = _completion_marker(marker, run.returncode)
            errors.extend(marker_errors)
        finally:
            environment_cleanup = purge_isolated_environment(environment_root)

        after = file_inventory(source)
        writes = _changed_inventory(before, after)
        outcomes = {
            outcome: sum(row["outcome"] == outcome for row in rows)
            for outcome in ("passed", "skipped", "failed", "error")
        }
        if run.returncode != 0:
            errors.append(f"pytest returncode={run.returncode}")
        if outcomes["failed"] or outcomes["error"]:
            errors.append(f"unit failures={outcomes['failed']}, errors={outcomes['error']}")
        if len(rows) != contract["expected_testcases"]:
            errors.append(f"unit row count={len(rows)}, expected={contract['expected_testcases']}")
        if lane == "patched" and not patch_applied:
            errors.append("patched lane did not apply current candidate")
        if environment_cleanup["residual_directories"]:
            errors.append(f"isolated environment residue={environment_cleanup['residual_directories']}")

        result = {
            "revision": revision,
            "status": "pending-cleanup",
            "profile": profile_name,
            "lane": lane,
            "evidence_mode": profile["evidence_mode"],
            "source": source_metadata,
            "candidate_patch": {
                "artifact_id": candidate["artifact_id"] if lane == "patched" else None,
                "path": candidate["path"] if lane == "patched" else None,
                "sha256": candidate["sha256"] if lane == "patched" else None,
                "applied": patch_applied,
            },
            "excluded": exclusions,
            "tests": {**outcomes, "total": len(rows), "returncode": run.returncode},
            "pytest_completion": {
                "path": marker.relative_to(root).as_posix(),
                "sha256": sha256_path(marker) if marker.is_file() else None,
                "marker": marker_value,
            },
            "junit": {
                "path": junit.relative_to(root).as_posix(),
                "sha256": sha256_path(junit) if junit.is_file() else None,
            },
            "source_tree_final_writes": writes,
            "runtime_environment_cleanup": environment_cleanup,
            "source_isolation": {
                "dedicated_extraction": True,
                "shared_with_other_test_lanes": False,
                "source_extraction_cleaned_after_run": False,
                "isolated_environment_cleaned_after_run": not environment_cleanup["residual_directories"],
                "cleaned_after_run": False,
            },
            "errors": errors,
        }
    finally:
        if environment_root.exists():
            purge_isolated_environment(environment_root)
        shutil.rmtree(scratch, ignore_errors=True)
        source_cleaned = not scratch.exists()

    if result is None:
        raise UnitLaneError(f"unit lane {profile_name}/{lane} produced no result")
    if not source_cleaned:
        errors.append("disposable source cleanup failed")
    isolation = result["source_isolation"]
    isolation["source_extraction_cleaned_after_run"] = source_cleaned
    isolation["cleaned_after_run"] = source_cleaned and isolation["isolated_environment_cleaned_after_run"]
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    output = root / profile["result_template"].format(lane=lane)
    write_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--lane", choices=("baseline", "patched"), required=True)
    parser.add_argument("--source-zip", default="auto")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        source_zip, _inspections = locate_source_bundle(args.source_zip)
        result = run_lane(root, args.profile, args.lane, source_zip)
    except (UnitLaneError, OSError, ValueError) as exc:
        result = {"revision": derive_revision(root), "status": "fail", "error": str(exc)}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
