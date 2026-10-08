#!/usr/bin/env python3
"""Validate the Search Again cap regression and repeat-policy split.

Research-only.  The probe confirms current same-token behavior, executes the
cap/waste counterexample, and compares page replacement with the more complex
in-place epoch branch without selecting upstream contribution material.
"""
from __future__ import annotations

import argparse
import ast
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    isolated_environment,
    parse_junit_report,
    run_bounded,
    safe_extract_tar_gz_member,
    write_csv,
    write_json,
)
from source_bundle_locator import (  # noqa: E402
    EXPECTED_SOURCE_SHA256,
    SOURCE_PREFIX,
    inspect_bundle,
    locate_source_bundle,
)

REVISION = derive_revision(ROOT)
LANE = "github-branch-master"
EXECUTABLE_SOURCE_REF = "f4e17d59783dbc48ea31d2e899a681e2dd1ed500"
PUBLIC_SOURCE_REF = "a96406e7aa285a3fb2a3e35900686d164a22bf02"
ARTIFACTS = ROOT / "maintainer_artifacts/search-repeat-01"
RUNTIME = ROOT / f"evidence/{REVISION}-search-repeat-runtime"
OUTPUT_SUMMARY = ROOT / f"data/{REVISION}_search_repeat_summary.json"
OUTPUT_INVARIANTS = ROOT / f"data/{REVISION}_search_repeat_source_invariants.csv"
OUTPUT_TESTS = ROOT / f"data/{REVISION}_search_repeat_test_matrix.csv"
OUTPUT_COMPILE = ROOT / f"data/{REVISION}_search_repeat_compile_matrix.csv"
OUTPUT_POLICY = ROOT / f"data/{REVISION}_search_repeat_policy_matrix.csv"
OUTPUT_WASTE = ROOT / f"data/{REVISION}_search_repeat_cap_waste.csv"
TEST_FILES = (
    "test_current_retry_merge.py",
    "test_result_cap_regression.py",
    "test_same_token_clear_counterexample.py",
    "test_fresh_token_replacement.py",
    "test_source_ownership.py",
)
EXPECTED_TESTS = 17


def lane_head(source_zip: Path, lane: str) -> str:
    suffix = f"git-full/.git/worktrees/{lane}/HEAD"
    with zipfile.ZipFile(source_zip) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix}, found {len(matches)}")
        return archive.read(matches[0]).decode("ascii").strip()


def nested_archive_name(lane: str) -> str:
    base = SOURCE_PREFIX.rsplit("source-trees/", 1)[0]
    return f"{base}archives/{lane}.tar.gz"


def method_source(path: Path, class_name: str, method_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                segment = ast.get_source_segment(source, item)
                if segment is not None:
                    return segment
    raise RuntimeError(f"missing {class_name}.{method_name} in {path}")


def source_invariants(source: Path, source_zip: Path) -> list[dict[str, str]]:
    gui_path = source / "pynicotine/gtkgui/search.py"
    core_path = source / "pynicotine/search.py"
    config_path = source / "pynicotine/config.py"
    again = method_source(gui_path, "Search", "on_search_again")
    dispatch = method_source(gui_path, "Searches", "file_search_response")
    page_response = method_source(gui_path, "Search", "file_search_response")
    clear_model = method_source(gui_path, "Search", "clear_model")
    do_search = method_source(core_path, "Search", "do_search")
    send = method_source(core_path, "Search", "send_search_request")
    remove = method_source(core_path, "Search", "remove_search")
    restore = method_source(gui_path, "Searches", "on_restore_removed_page")
    full_gui = gui_path.read_text(encoding="utf-8")
    full_config = config_path.read_text(encoding="utf-8")

    cap_check = 'page.num_results_found >= config.sections["searches"]["max_displayed_results"]'
    raw: list[tuple[str, bool, str]] = [
        ("source bundle digest contract", inspect_bundle(source_zip).sha256 == EXPECTED_SOURCE_SHA256, EXPECTED_SOURCE_SHA256),
        ("bundled master lane head", lane_head(source_zip, LANE) == EXECUTABLE_SOURCE_REF, EXECUTABLE_SOURCE_REF),
        ("Search Again reuses page token", "core.search.send_search_request(self.token)" in again, "same-token resend"),
        ("Search Again does not clear stored rows", "clear_model" not in again, "rows retained"),
        ("Search Again does not allocate a new search", "do_search" not in again, "no fresh-token path"),
        ("send re-allows token before request dispatch", send.index("self.add_allowed_token(token)") < send.index("if search.mode"), "admission re-added"),
        ("dispatcher checks cap before page response", dispatch.index(cap_check) < dispatch.rindex("page.file_search_response(msg)"), "pre-page gate"),
        ("cap gate retires token", "core.search.remove_allowed_token(msg.token)" in dispatch, "admission removed"),
        ("cap gate returns without adding rows", dispatch.index("core.search.remove_allowed_token(msg.token)") < dispatch.index("return", dispatch.index("core.search.remove_allowed_token(msg.token)")) < dispatch.rindex("page.file_search_response(msg)"), "first over-cap response discarded"),
        ("page deduplicates by username", "if user in self.users:" in page_response, "one accepted response per user"),
        ("username gate precedes page initialization", page_response.index("if user in self.users:") < page_response.index("self.initialized = True"), "repeat result ignored early"),
        ("current Clear All Results label absent", "Clear All Results" not in full_gui, "manual reset removed"),
        ("current on_clear method absent", "def on_clear(" not in full_gui, "manual reset handler removed"),
        ("clear_model can reset stored-result count", "self.num_results_found = 0" in clear_model, "capacity reset primitive remains"),
        ("new search allocates fresh token", "self.token = increment_token(self.token)" in do_search, "existing fresh-token path"),
        ("new search emits a new page", 'events.emit("add-search"' in do_search, "existing page creation event"),
        ("removed-page restore uses new-search path", "core.search.do_search(search_term, mode" in restore, "existing page recreation precedent"),
        ("remove search retires token first", remove.index("self.remove_allowed_token(token)") < remove.index("search = self.searches.get(token)"), "late-token barrier requested"),
        ("default display cap is 2500", '"max_displayed_results": 2500' in full_config, "default"),
    ]
    return [
        {"invariant": name, "status": "pass" if passed else "fail", "detail": detail}
        for name, passed, detail in raw
    ]


def policy_rows() -> list[dict[str, str]]:
    sys.path.insert(0, str(ARTIFACTS))
    from search_repeat_model import policy_matrix  # noqa: PLC0415
    return policy_matrix()


def cap_waste_rows() -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for clicks in (1, 4, 12, 32):
        for recipients in (1, 10, 32, 100):
            rows.append({
                "clicks_at_cap": clicks,
                "recipients_per_click": recipients,
                "outgoing_requests": clicks * recipients,
                "new_display_rows": 0,
                "token_retire_cycles": clicks,
                "classification": "bounded local request waste; remote amplification not established",
            })
    return rows


def compile_rows() -> list[dict[str, str]]:
    paths = [ARTIFACTS / "search_repeat_model.py"]
    paths.extend(ARTIFACTS / name for name in TEST_FILES)
    paths.extend([
        ROOT / "tools/probe_rev0080_search_repeat.py",
        ROOT / "tools/audit_current_source_history.py",
    ])
    rows: list[dict[str, str]] = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        try:
            compile(path.read_text(encoding="utf-8"), relative, "exec")
        except Exception as exc:  # pragma: no cover - reported in matrix
            rows.append({"path": relative, "status": "fail", "detail": f"{type(exc).__name__}: {exc}"})
        else:
            rows.append({"path": relative, "status": "pass", "detail": "compiled"})
    return rows


def run_probe(source_zip: Path) -> dict[str, Any]:
    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix=f"{REVISION}-search-repeat-") as temp_name:
        source = Path(temp_name) / "source"
        extracted_files = safe_extract_tar_gz_member(source_zip, nested_archive_name(LANE), source)
        invariants = source_invariants(source, source_zip)
        compiles = compile_rows()

        artifact_runtime = RUNTIME / "artifact-tests"
        env, cwd = isolated_environment(
            artifact_runtime,
            python_paths=(ARTIFACTS, source),
            inherit={"NICOTINE_SOURCE_ROOT": str(source)},
        )
        artifact_junit = artifact_runtime / "junit.xml"
        artifact_run = run_bounded(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                *(str(ARTIFACTS / name) for name in TEST_FILES),
                f"--junitxml={artifact_junit}",
            ],
            cwd=cwd,
            env=env,
            timeout=180,
            output_path=artifact_runtime / "pytest.log",
        )
        artifact_tests = parse_junit_report(artifact_junit) if artifact_junit.is_file() else []
        for row in artifact_tests:
            row["lane"] = "search-repeat-model-and-source"

        unit_runtime = RUNTIME / "upstream-units"
        unit_env, _unit_cwd = isolated_environment(unit_runtime, python_paths=(source,))
        unit_junit = unit_runtime / "junit.xml"
        unit_run = run_bounded(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                str(source / "pynicotine/tests/unit"),
                f"--ignore={source / 'pynicotine/tests/unit/test_i18n.py'}",
                f"--junitxml={unit_junit}",
            ],
            cwd=source,
            env=unit_env,
            timeout=300,
            output_path=unit_runtime / "pytest.log",
        )
        unit_tests = parse_junit_report(unit_junit) if unit_junit.is_file() else []

    artifact_failed = sum(row["outcome"] in {"failed", "error"} for row in artifact_tests)
    unit_failed = sum(row["outcome"] in {"failed", "error"} for row in unit_tests)
    errors: list[str] = []
    if artifact_run.returncode != 0 or artifact_failed or len(artifact_tests) != EXPECTED_TESTS:
        errors.append(f"artifact tests rc={artifact_run.returncode}, rows={len(artifact_tests)}, failed={artifact_failed}")
    if unit_run.returncode != 0 or unit_failed:
        errors.append(f"upstream units rc={unit_run.returncode}, failed={unit_failed}")
    failed_invariants = [row["invariant"] for row in invariants if row["status"] != "pass"]
    if failed_invariants:
        errors.append(f"source invariants failed: {failed_invariants}")
    failed_compiles = [row["path"] for row in compiles if row["status"] != "pass"]
    if failed_compiles:
        errors.append(f"compile checks failed: {failed_compiles}")

    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "disposition": "open-fresh-token-replacement-research",
        "selected_patch": None,
        "source": {
            "bundle": source_zip.name,
            "bundle_sha256": inspect_bundle(source_zip).sha256,
            "lane": LANE,
            "executable_source_ref": EXECUTABLE_SOURCE_REF,
            "public_source_ref": PUBLIC_SOURCE_REF,
            "extracted_files": extracted_files,
            "scope": "executable tests use bundled proxy; current public-flow review is separate",
        },
        "findings": {
            "confirmed_regression": "at the display cap, Search Again emits requests but the first response retires the unchanged token before adding a row",
            "waste_boundary": "repeated clicks can multiply local buddy/user fan-out while display capacity remains zero; remote processing impact was not measured",
            "same_token_clear": "restores capacity but cannot distinguish delayed responses from the prior request lifetime",
            "architecture_correction": "stable logical identity plus network acknowledgement is required only for a failure-atomic in-place refresh, not for best-effort fresh-token page recreation",
            "preferred_next_direction": "fresh-token page replacement with explicit page-state, wishlist, plugin, tab-order, and undo semantics",
            "selected_implementation": None,
        },
        "artifact_tests": {
            "passed": sum(row["outcome"] == "passed" for row in artifact_tests),
            "failed": artifact_failed,
            "total": len(artifact_tests),
            "returncode": artifact_run.returncode,
        },
        "source_invariants": {
            "passed": sum(row["status"] == "pass" for row in invariants),
            "total": len(invariants),
        },
        "compile_checks": {
            "passed": sum(row["status"] == "pass" for row in compiles),
            "total": len(compiles),
        },
        "upstream_units": {
            "passed": sum(row["outcome"] == "passed" for row in unit_tests),
            "skipped": sum(row["outcome"] == "skipped" for row in unit_tests),
            "failed": unit_failed,
            "total": len(unit_tests),
            "returncode": unit_run.returncode,
            "excluded": ["pynicotine/tests/unit/test_i18n.py (msgfmt unavailable)"],
        },
        "active_artifact": {
            "files": len([path for path in ARTIFACTS.iterdir() if path.is_file()]),
            "bytes": sum(path.stat().st_size for path in ARTIFACTS.iterdir() if path.is_file()),
            "lines": sum(len(path.read_text(encoding="utf-8").splitlines()) for path in ARTIFACTS.iterdir() if path.is_file()),
        },
        "superseded_in_place_artifact": {
            "path": "maintainer_artifacts/search-epoch-01",
            "files": len([path for path in (ROOT / "maintainer_artifacts/search-epoch-01").iterdir() if path.is_file()]),
            "bytes": sum(path.stat().st_size for path in (ROOT / "maintainer_artifacts/search-epoch-01").iterdir() if path.is_file()),
            "lines": sum(len(path.read_text(encoding="utf-8").splitlines()) for path in (ROOT / "maintainer_artifacts/search-epoch-01").iterdir() if path.is_file()),
            "status": "retained historical optional-branch evidence; removed from current authority",
        },
        "errors": errors,
        "_rows": {
            "invariants": invariants,
            "tests": artifact_tests,
            "compiles": compiles,
            "policy": policy_rows(),
            "waste": cap_waste_rows(),
        },
    }
    return result


def write_outputs(result: dict[str, Any]) -> None:
    rows = result.pop("_rows")
    write_json(OUTPUT_SUMMARY, result)
    write_csv(OUTPUT_INVARIANTS, rows["invariants"], fields=("invariant", "status", "detail"))
    write_csv(
        OUTPUT_TESTS,
        rows["tests"],
        fields=("lane", "nodeid", "name", "outcome", "passed", "duration", "detail"),
    )
    write_csv(OUTPUT_COMPILE, rows["compiles"], fields=("path", "status", "detail"))
    write_csv(
        OUTPUT_POLICY,
        rows["policy"],
        fields=("policy", "cap_recovery", "late_old_response_isolation", "page_local_state", "network_ack_required", "principal_cost"),
    )
    write_csv(
        OUTPUT_WASTE,
        rows["waste"],
        fields=("clicks_at_cap", "recipients_per_click", "outgoing_requests", "new_display_rows", "token_retire_cycles", "classification"),
    )
    lines = [
        f"# {REVISION} Search Again repeat-policy probe",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"model/source tests: {result['artifact_tests']['passed']}/{result['artifact_tests']['total']}",
        f"source invariants: {result['source_invariants']['passed']}/{result['source_invariants']['total']}",
        f"compile checks: {result['compile_checks']['passed']}/{result['compile_checks']['total']}",
        f"upstream units: {result['upstream_units']['passed']} passed, {result['upstream_units']['skipped']} skipped",
        f"selected patch: {result['selected_patch']}",
        "```",
        "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in result["errors"]])
    (ROOT / f"evidence/{REVISION}-search-repeat-probe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    selected, _inspections = locate_source_bundle(args.source_zip)
    result = run_probe(selected)
    if args.write_data:
        write_outputs(result)
    else:
        result.pop("_rows", None)
    print(canonical_json(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
