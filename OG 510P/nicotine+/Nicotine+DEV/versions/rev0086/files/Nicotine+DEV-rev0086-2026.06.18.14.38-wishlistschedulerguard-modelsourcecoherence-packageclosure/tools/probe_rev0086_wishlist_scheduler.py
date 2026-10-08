#!/usr/bin/env python3
"""Confirm wishlist scheduler eligibility behavior and test a narrow correction."""
from __future__ import annotations

import argparse
import importlib.util
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
    sha256_path,
    write_csv,
    write_json,
)
from materialize_current_public_head import load_contract, materialize  # noqa: E402
from source_bundle_locator import inspect_bundle, locate_source_bundle  # noqa: E402

REVISION = derive_revision(ROOT)
CONTRACT = load_contract(ROOT)
SOURCE_REF = CONTRACT["target_ref"]
SOURCE_LANE = CONTRACT["derived_lane_id"]
ARTIFACTS = ROOT / "maintainer_artifacts/wishlist-scheduler-01"
PATCH = ARTIFACTS / "wishlist_scheduler_enabled_only_rev0086.patch"
WITNESS = ARTIFACTS / "source_witness.py"
MODEL = ARTIFACTS / "wishlist_scheduler_model.py"
EVIDENCE = ROOT / f"evidence/{REVISION}-wishlist-scheduler-runtime"
MARKER_ENV = "CUBE_PYTEST_COMPLETION_MARKER"


def _load_model_module():
    spec = importlib.util.spec_from_file_location("wishlist_scheduler_model", MODEL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scheduler model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run_witness(source_root: Path, output_path: Path, log_path: Path) -> dict[str, Any]:
    run = run_bounded(
        [sys.executable, str(WITNESS), "--source-root", str(source_root)],
        cwd=source_root,
        timeout=60,
        output_path=log_path,
    )
    if run.returncode != 0:
        raise RuntimeError(f"source witness failed: {run.stdout[-2000:]}")
    payload = json.loads(run.stdout)
    write_json(output_path, payload)
    return payload


def _changed(before: dict[Path, tuple[str, int]], after: dict[Path, tuple[str, int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(set(before) | set(after)):
        if before.get(path) == after.get(path):
            continue
        old = before.get(path)
        new = after.get(path)
        rows.append({
            "path": path.as_posix(),
            "before_sha256": old[0] if old else None,
            "before_bytes": old[1] if old else None,
            "after_sha256": new[0] if new else None,
            "after_bytes": new[1] if new else None,
        })
    return rows


def _completion(path: Path, returncode: int) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, ["pytest completion marker missing"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"pytest completion marker unreadable: {exc}"]
    errors = []
    if set(value) != {"version", "pytest_main_returned", "exit_code"}:
        errors.append("pytest completion marker fields invalid")
    if value.get("version") != 1 or value.get("pytest_main_returned") is not True:
        errors.append("pytest completion marker semantics invalid")
    if value.get("exit_code") != returncode:
        errors.append("pytest completion marker returncode mismatch")
    return value, errors


def _run_upstream_units(source: Path, lane: str) -> dict[str, Any]:
    lane_root = EVIDENCE / "upstream-units" / lane
    if lane_root.exists():
        shutil.rmtree(lane_root)
    lane_root.mkdir(parents=True)
    runtime = Path(tempfile.mkdtemp(prefix=f"{REVISION}-{lane}-env-", dir="/mnt/data"))
    before = file_inventory(source)
    errors: list[str] = []
    cleanup: dict[str, Any] = {}
    try:
        env, _cwd = isolated_environment(runtime, python_paths=(source,))
        marker = lane_root / "pytest-completion.json"
        junit = lane_root / "junit.xml"
        env[MARKER_ENV] = str(marker)
        command = [
            sys.executable,
            str(ROOT / "tools/run_pytest_completion_exit.py"),
            "-q",
            "-p",
            "no:cacheprovider",
            str(source / "pynicotine/tests/unit"),
        ]
        excluded: list[str] = []
        if shutil.which("msgfmt") is None:
            relative = "pynicotine/tests/unit/test_i18n.py"
            command.append(f"--ignore={source / relative}")
            excluded.append(f"{relative} (msgfmt unavailable)")
        command.append(f"--junitxml={junit}")
        run = run_bounded(command, cwd=source, env=env, timeout=180, output_path=lane_root / "pytest.log")
        rows = parse_junit_report(junit) if junit.is_file() else []
        marker_value, marker_errors = _completion(marker, run.returncode)
        errors.extend(marker_errors)
        outcomes = {
            outcome: sum(row["outcome"] == outcome for row in rows)
            for outcome in ("passed", "skipped", "failed", "error")
        }
        if run.returncode != 0:
            errors.append(f"pytest returncode={run.returncode}")
        if outcomes["failed"] or outcomes["error"]:
            errors.append(f"unit failures={outcomes['failed']}, errors={outcomes['error']}")
        if len(rows) != 61:
            errors.append(f"unit row count={len(rows)}, expected=61")
    finally:
        cleanup = purge_isolated_environment(runtime)
        shutil.rmtree(runtime, ignore_errors=True)
    after = file_inventory(source)
    writes = _changed(before, after)
    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "lane": lane,
        "source_lane": SOURCE_LANE,
        "source_ref": SOURCE_REF,
        "candidate_patch": {
            "path": PATCH.relative_to(ROOT).as_posix() if lane == "candidate" else None,
            "sha256": sha256_path(PATCH) if lane == "candidate" else None,
            "applied": lane == "candidate",
        },
        "excluded": excluded,
        "tests": {**outcomes, "total": len(rows), "returncode": run.returncode},
        "pytest_completion": {
            "path": marker.relative_to(ROOT).as_posix(),
            "sha256": sha256_path(marker) if marker.is_file() else None,
            "marker": marker_value,
        },
        "junit": {
            "path": junit.relative_to(ROOT).as_posix(),
            "sha256": sha256_path(junit) if junit.is_file() else None,
        },
        "source_tree_final_writes": writes,
        "runtime_environment_cleanup": cleanup,
        "errors": errors,
    }
    write_json(ROOT / f"data/{REVISION}_wishlist_scheduler_unit_{lane}.json", result)
    return result


def _compile_checks(candidate_source: Path) -> list[dict[str, str]]:
    paths = [
        candidate_source / "pynicotine/search.py",
        MODEL,
        WITNESS,
        ARTIFACTS / "test_wishlist_scheduler_model.py",
        ARTIFACTS / "test_wishlist_scheduler_source_semantics.py",
        ROOT / "maintainer_artifacts/wishlist-inbox-01/wishlist_inbox_model.py",
        ROOT / "maintainer_artifacts/wishlist-inbox-01/test_wishlist_inbox_model.py",
        ROOT / "tools/probe_rev0086_wishlist_scheduler.py",
        ROOT / "tools/audit_current_model_source_differential.py",
    ]
    rows: list[dict[str, str]] = []
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, detail = "pass", ""
        except Exception as exc:
            status, detail = "fail", str(exc)
        relative = path.relative_to(candidate_source).as_posix() if candidate_source in path.parents else path.relative_to(ROOT).as_posix()
        rows.append({"path": relative, "status": status, "detail": detail})
    return rows


def _source_invariants(baseline: Path, candidate: Path) -> list[dict[str, str]]:
    current = (baseline / "pynicotine/search.py").read_text(encoding="utf-8")
    patched = (candidate / "pynicotine/search.py").read_text(encoding="utf-8")
    checks = [
        ("baseline", "current fallback guard present", "if search is not None:" in current),
        ("baseline", "current enabled guard absent", "if search is not None and search.auto_search:" not in current),
        ("candidate", "enabled guard present", "if search is not None and search.auto_search:" in patched),
        ("candidate", "old fallback guard absent", "if search is not None:\n            search.is_ignored" not in patched),
        ("both", "bounded scan retained", all("while nth_search < len(self.wishlist):" in text for text in (current, patched))),
        ("both", "rotation retained", all("search = self.wishlist.pop(term)" in text and "self.wishlist[term] = search" in text for text in (current, patched))),
        ("both", "first enabled break retained", all("if search.auto_search:\n                break" in text for text in (current, patched))),
        ("both", "wishlist send path retained", all("self._do_wishlist_search(search)" in text for text in (current, patched))),
    ]
    return [
        {"state": state, "check": name, "status": "pass" if passed else "fail", "detail": ""}
        for state, name, passed in checks
    ]


def run(source_arg: str) -> dict[str, Any]:
    source_zip, inspections = locate_source_bundle(source_arg)
    inspection = inspect_bundle(source_zip)
    if inspection.status != "pass":
        raise RuntimeError("source bundle failed content contract")
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{REVISION}-wishlist-scheduler-", dir="/mnt/data") as temp_name:
        temp = Path(temp_name)
        baseline = temp / "baseline"
        candidate = temp / "candidate"
        materialization = materialize(source_zip, baseline, root=ROOT, contract=CONTRACT)
        shutil.copytree(baseline, candidate)
        check = run_bounded(
            ["git", "apply", "--check", "--whitespace=error-all", str(PATCH)],
            cwd=candidate,
            timeout=60,
            output_path=EVIDENCE / "candidate-check.log",
        )
        if check.returncode != 0:
            raise RuntimeError(f"candidate check failed: {check.stdout[-2000:]}")
        apply = run_bounded(
            ["git", "apply", "--whitespace=error-all", str(PATCH)],
            cwd=candidate,
            timeout=60,
            output_path=EVIDENCE / "candidate-apply.log",
        )
        if apply.returncode != 0:
            raise RuntimeError(f"candidate apply failed: {apply.stdout[-2000:]}")

        source_current = _run_witness(
            baseline,
            ROOT / f"data/{REVISION}_wishlist_scheduler_source_baseline.json",
            EVIDENCE / "source-baseline.log",
        )
        source_candidate = _run_witness(
            candidate,
            ROOT / f"data/{REVISION}_wishlist_scheduler_source_candidate.json",
            EVIDENCE / "source-candidate.log",
        )
        model_module = _load_model_module()
        model_current = model_module.run_matrix(candidate=False)
        model_candidate = model_module.run_matrix(candidate=True)
        write_json(ROOT / f"data/{REVISION}_wishlist_scheduler_model_current.json", model_current)
        write_json(ROOT / f"data/{REVISION}_wishlist_scheduler_model_candidate.json", model_candidate)

        invariants = _source_invariants(baseline, candidate)
        compiles = _compile_checks(candidate)

        runtime = temp / "research-environment"
        env, cwd = isolated_environment(runtime, python_paths=(ARTIFACTS, ROOT / "maintainer_artifacts/wishlist-inbox-01"))
        env["NICOTINE_SOURCE_ROOT"] = str(baseline)
        env["NICOTINE_PATCHED_SOURCE_ROOT"] = str(candidate)
        research_junit = EVIDENCE / "research-tests.junit.xml"
        research_run = run_bounded(
            [
                sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                str(ARTIFACTS / "test_wishlist_scheduler_model.py"),
                str(ARTIFACTS / "test_wishlist_scheduler_source_semantics.py"),
                str(ROOT / "maintainer_artifacts/wishlist-inbox-01/test_wishlist_inbox_model.py"),
                f"--junitxml={research_junit}",
            ],
            cwd=cwd,
            env=env,
            timeout=120,
            output_path=EVIDENCE / "research-tests.log",
        )
        research_cleanup = purge_isolated_environment(runtime)
        research_rows = parse_junit_report(research_junit) if research_junit.is_file() else []
        for row in research_rows:
            row["status"] = "pass" if row["passed"] else "fail"

        baseline_units = _run_upstream_units(baseline, "baseline")
        candidate_units = _run_upstream_units(candidate, "candidate")

        errors: list[str] = []
        if source_current != model_current:
            errors.append("current model/source mismatch")
        if source_candidate != model_candidate:
            errors.append("candidate model/source mismatch")
        if any(row["status"] != "pass" for row in invariants):
            errors.append("source invariant failure")
        if any(row["status"] != "pass" for row in compiles):
            errors.append("compile failure")
        if research_run.returncode != 0 or any(not row["passed"] for row in research_rows):
            errors.append("research test failure")
        if len(research_rows) != 30:
            errors.append(f"expected 30 research tests, found {len(research_rows)}")
        if baseline_units["status"] != "pass" or candidate_units["status"] != "pass":
            errors.append("upstream unit failure")
        if research_cleanup.get("residual_directories"):
            errors.append("research environment residue")

        result = {
            "revision": REVISION,
            "status": "pass" if not errors else "fail",
            "packet_id": "WISHLIST-SCHED-01",
            "source": {
                "bundle": source_zip.name,
                "bundle_sha256": inspection.sha256,
                "derived_lane": SOURCE_LANE,
                "executable_source_ref": SOURCE_REF,
                "candidates_inspected": len(inspections),
                "materialization": materialization,
            },
            "candidate_patch": {
                "path": PATCH.relative_to(ROOT).as_posix(),
                "sha256": sha256_path(PATCH),
                "selected_research_correction": True,
                "upstream_contribution_material": False,
            },
            "finding": {
                "current_single_disabled": source_current["single_disabled"]["selected"],
                "current_all_disabled": source_current["all_disabled"]["selected"],
                "candidate_single_disabled": source_candidate["single_disabled"]["selected"],
                "candidate_all_disabled": source_candidate["all_disabled"]["selected"],
                "impact": "disabled local wishlist preference can leak one recurring query and consume bounded recurring traffic",
                "security_threshold": "not established",
            },
            "model_source_parity": {
                "current": source_current == model_current,
                "candidate": source_candidate == model_candidate,
                "scenarios": len(source_current),
            },
            "source_invariants": {
                "passed": sum(row["status"] == "pass" for row in invariants),
                "total": len(invariants),
            },
            "compile_checks": {
                "passed": sum(row["status"] == "pass" for row in compiles),
                "total": len(compiles),
            },
            "research_tests": {
                "passed": sum(row["passed"] for row in research_rows),
                "total": len(research_rows),
                "returncode": research_run.returncode,
                "junit": research_junit.relative_to(ROOT).as_posix(),
            },
            "upstream_units": {
                "baseline": baseline_units["tests"],
                "candidate": candidate_units["tests"],
            },
            "environment_cleanup": research_cleanup,
            "errors": errors,
        }
        write_csv(
            ROOT / f"data/{REVISION}_wishlist_scheduler_source_invariants.csv",
            invariants,
            fields=("state", "check", "status", "detail"),
        )
        write_csv(
            ROOT / f"data/{REVISION}_wishlist_scheduler_compile_matrix.csv",
            compiles,
            fields=("path", "status", "detail"),
        )
        write_csv(
            ROOT / f"data/{REVISION}_wishlist_scheduler_test_matrix.csv",
            research_rows,
            fields=("nodeid", "name", "outcome", "passed", "status", "duration", "detail"),
        )
        write_json(ROOT / f"data/{REVISION}_wishlist_scheduler_summary.json", result)
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true", help="retained for current-tool CLI consistency")
    args = parser.parse_args()
    try:
        result = run(args.source_zip)
    except Exception as exc:
        result = {"revision": REVISION, "status": "fail", "errors": [f"{type(exc).__name__}: {exc}"]}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
