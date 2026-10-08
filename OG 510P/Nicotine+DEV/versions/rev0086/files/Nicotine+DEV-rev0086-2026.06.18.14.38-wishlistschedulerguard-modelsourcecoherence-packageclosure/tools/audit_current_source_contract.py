#!/usr/bin/env python3
"""Validate bundled, derived-executable, and public-observation source authority."""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, safe_relative, write_csv, write_json  # noqa: E402
from materialize_current_public_head import (  # noqa: E402
    load_contract as load_public_head_contract,
    validate_contract as validate_public_head_contract,
)
from source_bundle_locator import (  # noqa: E402
    ARCHIVE_PREFIX,
    DEFAULT_PATTERNS,
    DERIVED_SOURCE_REFS,
    EXPECTED_SOURCE_SHA256,
    GIT_ROOT_SUFFIX,
    LANE_HEADS,
    PUBLIC_SOURCE_REFS,
    REQUIRED_LANES,
    SOURCE_CONTRACT_PATH,
    SOURCE_PREFIX,
    archive_member_name,
    bundle_contract,
    inspect_bundle,
    load_source_contract,
    locate_source_bundle,
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_LANES = {
    "github-tag-3.3.10",
    "github-branch-3.3.x",
    "github-branch-master",
}
EXPECTED_DERIVED_LANES = {"github-public-master-exact-content"}
EXPECTED_DATE = "2026-06-18"


def _valid_head(value: object) -> bool:
    return isinstance(value, str) and HEX40.fullmatch(value) is not None


def validate_contract_shape(contract: object) -> list[str]:
    """Validate the revision-neutral structure without touching the filesystem."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["contract is not an object"]
    expected_top = {"version", "source_bundle", "derived_lanes", "public_observations"}
    if set(contract) != expected_top:
        errors.append(f"top-level fields differ: {sorted(set(contract) ^ expected_top)}")
    if contract.get("version") != 2:
        errors.append(f"version is {contract.get('version')!r}")

    bundle = contract.get("source_bundle")
    expected_bundle_keys = {
        "sha256", "source_prefix", "archive_prefix", "git_root_suffix",
        "default_patterns", "lanes",
    }
    if not isinstance(bundle, dict):
        errors.append("source_bundle is not an object")
        bundle = {}
    elif set(bundle) != expected_bundle_keys:
        errors.append(f"source_bundle fields differ: {sorted(set(bundle) ^ expected_bundle_keys)}")

    digest = bundle.get("sha256")
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        errors.append("source_bundle.sha256 is not 64 lowercase hex characters")

    source_prefix = bundle.get("source_prefix")
    archive_prefix = bundle.get("archive_prefix")
    for label, value, suffix in (
        ("source_prefix", source_prefix, "/source-trees/"),
        ("archive_prefix", archive_prefix, "/archives/"),
    ):
        if not isinstance(value, str) or not value.endswith(suffix):
            errors.append(f"{label} has invalid suffix")
        elif not safe_relative(value.rstrip("/")):
            errors.append(f"{label} is unsafe")
    if isinstance(source_prefix, str) and isinstance(archive_prefix, str):
        source_root = source_prefix.split("/source-trees/", 1)[0]
        archive_root = archive_prefix.split("/archives/", 1)[0]
        if source_root != archive_root:
            errors.append("source and archive prefixes have different roots")
    if bundle.get("git_root_suffix") != "git-full/":
        errors.append("git_root_suffix is not git-full/")

    patterns = bundle.get("default_patterns")
    if not isinstance(patterns, list) or not patterns or not all(
        isinstance(item, str) and item and "/" not in item and "\\" not in item
        for item in patterns
    ):
        errors.append("default_patterns is not a nonempty filename-pattern list")
    elif len(patterns) != len(set(patterns)):
        errors.append("default_patterns contains duplicates")

    lanes = bundle.get("lanes")
    if not isinstance(lanes, dict):
        errors.append("lanes is not an object")
        lanes = {}
    if set(lanes) != EXPECTED_LANES:
        errors.append(f"lane set differs: {sorted(set(lanes) ^ EXPECTED_LANES)}")
    heads: list[str] = []
    archives: list[str] = []
    for lane, details in lanes.items():
        if not isinstance(details, dict) or set(details) != {"archive", "head"}:
            errors.append(f"lane {lane} fields invalid")
            continue
        archive = details.get("archive")
        head = details.get("head")
        if not isinstance(archive, str) or Path(archive).name != archive or not archive.endswith(".tar.gz"):
            errors.append(f"lane {lane} archive invalid")
        else:
            archives.append(archive)
        if not _valid_head(head):
            errors.append(f"lane {lane} head invalid")
        else:
            heads.append(str(head))
    if len(archives) != len(set(archives)):
        errors.append("lane archives are not unique")
    if len(heads) != len(set(heads)):
        errors.append("lane heads are not unique")

    derived = contract.get("derived_lanes")
    if not isinstance(derived, dict):
        errors.append("derived_lanes is not an object")
        derived = {}
    if set(derived) != EXPECTED_DERIVED_LANES:
        errors.append(f"derived lane set differs: {sorted(set(derived) ^ EXPECTED_DERIVED_LANES)}")
    for lane, details in derived.items():
        expected_keys = {"base_lane", "head", "materialization_contract", "mode"}
        if not isinstance(details, dict) or set(details) != expected_keys:
            errors.append(f"derived lane {lane} fields invalid")
            continue
        base_lane = details.get("base_lane")
        if base_lane not in lanes:
            errors.append(f"derived lane {lane} base lane invalid")
        if not _valid_head(details.get("head")):
            errors.append(f"derived lane {lane} head invalid")
        elif isinstance(lanes.get(base_lane), dict) and details.get("head") == lanes[base_lane].get("head"):
            errors.append(f"derived lane {lane} does not advance its base")
        materialization = details.get("materialization_contract")
        if not safe_relative(materialization, suffix=".json"):
            errors.append(f"derived lane {lane} materialization path invalid")
        if details.get("mode") != "verified-delta-derived-executable-lane":
            errors.append(f"derived lane {lane} mode invalid")

    observations = contract.get("public_observations")
    if not isinstance(observations, dict) or set(observations) != {"github-branch-master"}:
        errors.append("public observation set invalid")
        observations = {}
    master = observations.get("github-branch-master")
    expected_public_keys = {
        "head", "observed_date", "commits_ahead_of_executable_proxy",
        "changed_files_ahead_of_executable_proxy", "executable_proxy_lane", "scope",
    }
    if not isinstance(master, dict) or set(master) != expected_public_keys:
        errors.append("public master observation fields invalid")
    else:
        if not _valid_head(master.get("head")):
            errors.append("public master head invalid")
        observed_date = master.get("observed_date")
        try:
            date.fromisoformat(observed_date)
        except (TypeError, ValueError):
            errors.append("public master observed_date invalid")
        if observed_date != EXPECTED_DATE:
            errors.append("public master observed_date is stale for this revision")
        proxy_lane = master.get("executable_proxy_lane")
        if proxy_lane not in lanes:
            errors.append("public master executable proxy lane invalid")
        for key in ("commits_ahead_of_executable_proxy", "changed_files_ahead_of_executable_proxy"):
            if not isinstance(master.get(key), int) or master[key] <= 0:
                errors.append(f"public master {key} invalid")
        if not isinstance(master.get("scope"), str) or len(master["scope"]) < 30:
            errors.append("public master scope too short")
        proxy = lanes.get(proxy_lane, {}) if isinstance(lanes, dict) else {}
        if master.get("head") == proxy.get("head"):
            errors.append("public master head equals executable proxy")
        derived_master = derived.get("github-public-master-exact-content", {})
        if isinstance(derived_master, dict):
            if derived_master.get("base_lane") != proxy_lane:
                errors.append("public observation proxy differs from derived-lane base")
            if derived_master.get("head") != master.get("head"):
                errors.append("public observation head differs from derived executable head")
    return errors


def audit(root: Path, source_zip: Path) -> dict[str, Any]:
    revision = derive_revision(root)
    contract = load_source_contract(root)
    bundle = bundle_contract(contract)
    history = json.loads((root / "data/current_source_history_contract.json").read_text(encoding="utf-8"))
    inspection = inspect_bundle(source_zip)
    rows: list[dict[str, str]] = []
    errors: list[str] = []

    def add(check: str, passed: bool, detail: object = "") -> None:
        rows.append({"check": check, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{check}: {detail}")

    shape_errors = validate_contract_shape(contract)
    add("source contract shape", not shape_errors, shape_errors)
    add("deprecated parallel source contract absent", not (root / "data/current_source_bundle_contract.json").exists())
    add("bundle inspection", inspection.status == "pass", inspection.status)
    add("bundle digest", inspection.sha256 == bundle.get("sha256"), inspection.sha256)
    add("bundle lanes", set(inspection.lanes) == EXPECTED_LANES, inspection.lanes)

    add("locator digest export", EXPECTED_SOURCE_SHA256 == bundle.get("sha256"), EXPECTED_SOURCE_SHA256)
    add("locator source prefix export", SOURCE_PREFIX == bundle.get("source_prefix"), SOURCE_PREFIX)
    add("locator archive prefix export", ARCHIVE_PREFIX == bundle.get("archive_prefix"), ARCHIVE_PREFIX)
    add("locator Git suffix export", GIT_ROOT_SUFFIX == bundle.get("git_root_suffix"), GIT_ROOT_SUFFIX)
    add("locator pattern export", DEFAULT_PATTERNS == tuple(bundle.get("default_patterns", ())), DEFAULT_PATTERNS)
    lanes = bundle.get("lanes", {})
    expected_heads = {
        lane: details.get("head")
        for lane, details in lanes.items()
        if isinstance(details, dict)
    } if isinstance(lanes, dict) else {}
    add("locator lane set export", set(REQUIRED_LANES) == EXPECTED_LANES, REQUIRED_LANES)
    add("locator lane heads export", LANE_HEADS == expected_heads, LANE_HEADS)

    derived = contract.get("derived_lanes", {})
    expected_derived = {
        lane: details.get("head")
        for lane, details in derived.items()
        if isinstance(details, dict)
    } if isinstance(derived, dict) else {}
    add("locator derived refs export", DERIVED_SOURCE_REFS == expected_derived, DERIVED_SOURCE_REFS)
    observations = contract.get("public_observations", {})
    expected_public = {
        lane: details.get("head")
        for lane, details in observations.items()
        if isinstance(details, dict)
    } if isinstance(observations, dict) else {}
    add("locator public refs export", PUBLIC_SOURCE_REFS == expected_public, PUBLIC_SOURCE_REFS)

    with zipfile.ZipFile(source_zip) as archive:
        names = set(archive.namelist())
        for lane in sorted(EXPECTED_LANES):
            details = lanes.get(lane, {}) if isinstance(lanes, dict) else {}
            member = archive_member_name(lane, contract=contract)
            add(f"archive member exists: {lane}", member in names, member)
            lane_prefix = f"{bundle.get('source_prefix')}{lane}/"
            add(f"source lane entries exist: {lane}", any(name.startswith(lane_prefix) for name in names), lane_prefix)
            suffix = f"git-full/.git/worktrees/{lane}/HEAD"
            matches = [name for name in names if name.endswith(suffix)]
            add(f"one worktree HEAD: {lane}", len(matches) == 1, matches)
            observed = archive.read(matches[0]).decode("ascii").strip() if len(matches) == 1 else ""
            add(f"worktree HEAD matches: {lane}", observed == details.get("head"), observed)

    derived_details = derived.get("github-public-master-exact-content", {}) if isinstance(derived, dict) else {}
    materialization_relative = derived_details.get("materialization_contract") if isinstance(derived_details, dict) else None
    add("derived materialization path safe", safe_relative(materialization_relative, suffix=".json"), materialization_relative)
    materialization_path = root / str(materialization_relative)
    add("derived materialization contract exists", materialization_path.is_file(), materialization_relative)
    try:
        public_contract = load_public_head_contract(root)
        public_errors = validate_public_head_contract(root, public_contract)
    except Exception as exc:
        public_contract = {}
        public_errors = [str(exc)]
    add("derived materialization contract valid", not public_errors, public_errors)
    add("derived materialization target matches", public_contract.get("target_ref") == derived_details.get("head"), public_contract.get("target_ref"))
    add("derived materialization base matches", public_contract.get("base_lane") == derived_details.get("base_lane"), public_contract.get("base_lane"))

    add("history contract version", history.get("version") == 3, history.get("version"))
    add("history uses source contract", history.get("source_contract") == SOURCE_CONTRACT_PATH.as_posix(), history.get("source_contract"))
    for stale_key in ("source_bundle_contract", "source_bundle_sha256", "executable_head", "git_root_suffix"):
        add(f"history omits duplicate {stale_key}", stale_key not in history, stale_key)

    revision_contract = json.loads((root / "data/current_revision_contract.json").read_text(encoding="utf-8"))
    current_tools: list[Path] = []
    for relative in revision_contract.get("current_scripts", []):
        path = root / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if path.name == "source_bundle_locator.py" or "source_bundle_locator" in text:
            current_tools.append(path)
    add("source-consuming current tools discovered", bool(current_tools), [path.name for path in current_tools])
    concrete_values = [
        str(bundle.get("sha256", "")),
        *[str(item) for item in expected_heads.values()],
        *[str(item) for item in expected_derived.values()],
        *[str(item) for item in expected_public.values()],
    ]
    for path in current_tools:
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        add(f"current tool exists: {path.name}", path.is_file(), path.relative_to(root))
        leaked = [value for value in concrete_values if value and value in text]
        add(f"current tool has no copied source identity: {path.name}", not leaked, leaked)

    mutants: list[tuple[str, dict[str, Any]]] = []
    wrong_digest = copy.deepcopy(contract)
    wrong_digest["source_bundle"]["sha256"] = "x" * 64
    mutants.append(("bad digest", wrong_digest))
    missing_lane = copy.deepcopy(contract)
    del missing_lane["source_bundle"]["lanes"]["github-branch-master"]
    mutants.append(("missing bundled lane", missing_lane))
    duplicate_head = copy.deepcopy(contract)
    duplicate_head["source_bundle"]["lanes"]["github-branch-master"]["head"] = duplicate_head["source_bundle"]["lanes"]["github-branch-3.3.x"]["head"]
    mutants.append(("duplicate bundled head", duplicate_head))
    unsafe_prefix = copy.deepcopy(contract)
    unsafe_prefix["source_bundle"]["source_prefix"] = "../source-trees/"
    mutants.append(("unsafe prefix", unsafe_prefix))
    stale_date = copy.deepcopy(contract)
    stale_date["public_observations"]["github-branch-master"]["observed_date"] = "2026-06-17"
    mutants.append(("stale public date", stale_date))
    missing_derived = copy.deepcopy(contract)
    missing_derived["derived_lanes"] = {}
    mutants.append(("missing derived lane", missing_derived))
    wrong_base = copy.deepcopy(contract)
    wrong_base["derived_lanes"]["github-public-master-exact-content"]["base_lane"] = "missing-lane"
    mutants.append(("derived base missing", wrong_base))
    unsafe_materialization = copy.deepcopy(contract)
    unsafe_materialization["derived_lanes"]["github-public-master-exact-content"]["materialization_contract"] = "../escape.json"
    mutants.append(("unsafe materialization path", unsafe_materialization))
    mismatched_public = copy.deepcopy(contract)
    mismatched_public["public_observations"]["github-branch-master"]["head"] = "0" * 40
    mutants.append(("derived and public head mismatch", mismatched_public))
    for label, mutant in mutants:
        add(f"mutation rejected: {label}", bool(validate_contract_shape(mutant)), label)

    return {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "source_zip": source_zip.name,
        "source_sha256": inspection.sha256,
        "bundled_lanes": len(expected_heads),
        "derived_executable_lanes": len(expected_derived),
        "public_observations": len(expected_public),
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "mutation_controls": len(mutants),
        "rows": rows,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_source_contract_audit.json", {key: value for key, value in result.items() if key != "rows"})
    write_csv(root / f"data/{revision}_source_contract_checks.csv", result["rows"], fields=("check", "status", "detail"))
    lines = [
        f"# {revision} source-contract authority audit", "", f"Status: **{result['status']}**", "", "```text",
        f"bundled lanes: {result['bundled_lanes']}",
        f"derived executable lanes: {result['derived_executable_lanes']}",
        f"public observations: {result['public_observations']}",
        f"checks: {result['checks_passed']}/{result['checks_total']}",
        f"mutation controls: {result['mutation_controls']}",
        f"source SHA-256: {result['source_sha256']}", "```", "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {item}" for item in result["errors"]])
    (root / f"evidence/{revision}-source-contract-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    selected, _inspections = locate_source_bundle(args.source_zip)
    result = audit(root, selected)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json({key: value for key, value in result.items() if key != "rows"}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
