#!/usr/bin/env python3
"""Rebind unchanged rev0085 search-candidate unit evidence to the current revision.

The candidate bytes, source identities, JUnit reports, and completion markers are
immutable.  This tool verifies those bindings before creating revision-current
records; it does not claim a fresh pytest execution.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, parse_junit_report, safe_relative, sha256_path, write_csv, write_json  # noqa: E402

OLD_REVISION = "rev0085"
OLD_PROFILES = {
    "bundled-master-current-candidate": {
        "old_root": "evidence/rev0085-wishlist-inbox-runtime/upstream-units",
        "old_result": "data/rev0085_wishlist_inbox_unit_{lane}.json",
        "new_root": "evidence/rev0086-search-candidate-revalidation/bundled-master/upstream-units",
        "new_result": "data/rev0086_search_candidate_bundled_unit_{lane}.json",
    },
    "exact-public-head-current-candidate": {
        "old_root": "evidence/rev0085-public-head-runtime/upstream-units",
        "old_result": "data/rev0085_public_head_unit_{lane}.json",
        "new_root": "evidence/rev0086-search-candidate-revalidation/exact-public-head/upstream-units",
        "new_result": "data/rev0086_search_candidate_public_unit_{lane}.json",
    },
}
LANES = ("baseline", "patched")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    revision = derive_revision(root)
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    candidate_contract = _load(root / "data/current_candidate_artifact_contract.json")
    candidate_id = candidate_contract.get("current_candidate_id")
    candidates = {item.get("artifact_id"): item for item in candidate_contract.get("artifacts", []) if isinstance(item, dict)}
    candidate = candidates.get(candidate_id, {})
    candidate_path = candidate.get("path")
    candidate_sha = candidate.get("sha256")
    add("current revision", revision == "rev0086", revision)
    add("candidate exists", isinstance(candidate_path, str) and safe_relative(candidate_path) and (root / candidate_path).is_file(), candidate_path)
    add("candidate digest", isinstance(candidate_sha, str) and (root / str(candidate_path)).is_file() and sha256_path(root / str(candidate_path)) == candidate_sha, candidate_sha)
    add("current revision validated", revision in candidate.get("validated_revisions", []), candidate.get("validated_revisions"))

    public = _load(root / "data/current_public_head_contract.json")
    source = _load(root / "data/current_source_contract.json")
    expected_refs = {
        "bundled-master-current-candidate": source.get("source_bundle", {}).get("lanes", {}).get("github-branch-master", {}).get("head"),
        "exact-public-head-current-candidate": public.get("target_ref"),
    }

    reused: list[dict[str, Any]] = []
    for profile, spec in OLD_PROFILES.items():
        expected_ref = expected_refs[profile]
        for lane in LANES:
            old_result_rel = spec["old_result"].format(lane=lane)
            old_result_path = root / old_result_rel
            add(f"old result exists: {profile}/{lane}", old_result_path.is_file(), old_result_rel)
            if not old_result_path.is_file():
                continue
            old = _load(old_result_path)
            prefix = f"{profile}/{lane}"
            add(f"old result pass: {prefix}", old.get("status") == "pass", old.get("status"))
            add(f"old revision: {prefix}", old.get("revision") == OLD_REVISION, old.get("revision"))
            add(f"old profile: {prefix}", old.get("profile") == profile, old.get("profile"))
            add(f"old lane: {prefix}", old.get("lane") == lane, old.get("lane"))
            tests = old.get("tests", {})
            add(f"old outcomes: {prefix}", tests.get("total") == 61 and tests.get("passed") == 60 and tests.get("skipped") == 1 and tests.get("failed") == 0 and tests.get("error") == 0 and tests.get("returncode") == 0, tests)
            add(f"old source ref: {prefix}", old.get("source", {}).get("executable_source_ref") == expected_ref, old.get("source", {}).get("executable_source_ref"))
            old_patch = old.get("candidate_patch", {})
            if lane == "patched":
                add(f"old candidate ID: {prefix}", old_patch.get("artifact_id") == candidate_id, old_patch.get("artifact_id"))
                add(f"old candidate path: {prefix}", old_patch.get("path") == candidate_path, old_patch.get("path"))
                add(f"old candidate digest: {prefix}", old_patch.get("sha256") == candidate_sha, old_patch.get("sha256"))
            else:
                add(f"old baseline unpatched: {prefix}", old_patch.get("applied") is False and old_patch.get("path") is None and old_patch.get("sha256") is None, old_patch)

            new_lane_root = root / spec["new_root"] / lane
            if new_lane_root.exists():
                shutil.rmtree(new_lane_root)
            new_lane_root.mkdir(parents=True)
            copied: list[dict[str, str]] = []
            for key, filename in (("junit", "junit.xml"), ("pytest_completion", "pytest-completion.json")):
                block = old.get(key, {})
                old_artifact_rel = block.get("path")
                old_artifact = root / str(old_artifact_rel)
                add(f"old {key} path safe: {prefix}", isinstance(old_artifact_rel, str) and safe_relative(old_artifact_rel), old_artifact_rel)
                add(f"old {key} exists: {prefix}", old_artifact.is_file() and not old_artifact.is_symlink(), old_artifact_rel)
                add(f"old {key} digest: {prefix}", old_artifact.is_file() and sha256_path(old_artifact) == block.get("sha256"), block.get("sha256"))
                target = new_lane_root / filename
                if old_artifact.is_file():
                    shutil.copyfile(old_artifact, target)
                copied.append({"kind": key, "from": str(old_artifact_rel), "to": target.relative_to(root).as_posix(), "sha256": sha256_path(target) if target.is_file() else ""})
            old_log = root / spec["old_root"] / lane / "pytest.log"
            add(f"old log exists: {prefix}", old_log.is_file(), old_log.relative_to(root).as_posix())
            if old_log.is_file():
                shutil.copyfile(old_log, new_lane_root / "pytest.log")
                add(f"old terminal summary: {prefix}", "60 passed, 1 skipped" in old_log.read_text(encoding="utf-8", errors="replace"))
            rows = parse_junit_report(new_lane_root / "junit.xml") if (new_lane_root / "junit.xml").is_file() else []
            add(f"copied JUnit rows: {prefix}", len(rows) == 61, len(rows))
            add(f"copied JUnit outcomes: {prefix}", sum(row["outcome"] == "passed" for row in rows) == 60 and sum(row["outcome"] == "skipped" for row in rows) == 1, len(rows))

            new = copy.deepcopy(old)
            new["revision"] = revision
            new["evidence_mode"] = "digest-bound-immutable-evidence-revalidation"
            new["evidence_provenance"] = {
                "execution_revision": OLD_REVISION,
                "revalidated_revision": revision,
                "fresh_execution": False,
                "reason": "candidate bytes and executable source identity unchanged",
                "source_record": old_result_rel,
                "source_record_sha256": sha256_path(old_result_path),
            }
            new["junit"]["path"] = (new_lane_root / "junit.xml").relative_to(root).as_posix()
            new["junit"]["sha256"] = sha256_path(new_lane_root / "junit.xml")
            new["pytest_completion"]["path"] = (new_lane_root / "pytest-completion.json").relative_to(root).as_posix()
            new["pytest_completion"]["sha256"] = sha256_path(new_lane_root / "pytest-completion.json")
            new_result_rel = spec["new_result"].format(lane=lane)
            write_json(root / new_result_rel, new)
            reused.append({
                "profile": profile,
                "lane": lane,
                "source_record": old_result_rel,
                "source_record_sha256": sha256_path(old_result_path),
                "current_record": new_result_rel,
                "current_record_sha256": sha256_path(root / new_result_rel),
                "artifacts": copied,
                "tests": tests,
            })

    result = {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "candidate_patch": {"artifact_id": candidate_id, "path": candidate_path, "sha256": candidate_sha},
        "source": {"bundled_ref": expected_refs["bundled-master-current-candidate"], "public_head_ref": expected_refs["exact-public-head-current-candidate"]},
        "execution_revision": OLD_REVISION,
        "fresh_execution": False,
        "reused_lanes": len(reused),
        "tests_revalidated": sum(item.get("tests", {}).get("total", 0) for item in reused),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "records": reused,
        "checks": checks,
        "errors": errors,
    }
    write_json(root / f"data/{revision}_search_candidate_revalidation.json", result)
    write_csv(root / f"data/{revision}_search_candidate_revalidation_checks.csv", checks, fields=("check", "status", "detail"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true", help="outputs are always written")
    args = parser.parse_args()
    result = run(args.root)
    print(canonical_json({k: v for k, v in result.items() if k not in {"checks", "records"}}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
