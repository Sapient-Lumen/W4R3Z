#!/usr/bin/env python3
"""Audit Search Again mode ownership and the hybrid manual-wishlist page.

The probe executes against the bundled master proxy, applies the revisioned
research candidate, runs source-backed core/model tests, and verifies fresh
upstream-unit evidence.  It does not select an upstream patch.
"""
from __future__ import annotations

import argparse
import ast
import json
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
    purge_isolated_environment,
    run_bounded,
    safe_extract_tar_gz_member,
    sha256_path,
    write_csv,
    write_json,
)
from source_bundle_locator import (  # noqa: E402
    LANE_HEADS,
    PUBLIC_SOURCE_REFS,
    archive_member_name,
    inspect_bundle,
    locate_source_bundle,
)

REVISION = derive_revision(ROOT)
LANE = "github-branch-master"
EXECUTABLE_REF = LANE_HEADS[LANE]
PUBLIC_REF = PUBLIC_SOURCE_REFS[LANE]
ARTIFACTS = ROOT / "maintainer_artifacts/search-rekey-01"
PATCH = ARTIFACTS / "search_again_mode_owned_rekey_rev0083.patch"
OLD_PATCH = ARTIFACTS / "search_again_fresh_token_rekey.patch"
TEST_FILE = ARTIFACTS / "test_search_mode_ownership_contract.py"
EVIDENCE = ROOT / f"evidence/{REVISION}-search-mode-ownership-runtime"


def bundled_lane_head(source_zip: Path) -> str:
    suffix = f"git-full/.git/worktrees/{LANE}/HEAD"
    with zipfile.ZipFile(source_zip) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix}, found {len(matches)}")
        return archive.read(matches[0]).decode("ascii").strip()


def extract_method(path: Path, class_name: str, method_name: str) -> str:
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


def add_row(rows: list[dict[str, str]], check: str, passed: bool, detail: object, *, state: str) -> None:
    rows.append({
        "check": check,
        "state": state,
        "status": "pass" if passed else "fail",
        "detail": str(detail),
    })


def source_invariants(baseline: Path, patched: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    base_search = baseline / "pynicotine/search.py"
    base_gui = baseline / "pynicotine/gtkgui/search.py"
    base_wishlist = baseline / "pynicotine/gtkgui/dialogs/wishlist.py"
    base_app = baseline / "pynicotine/gtkgui/application.py"
    patch_search = patched / "pynicotine/search.py"
    patch_gui = patched / "pynicotine/gtkgui/search.py"

    wishlist_dialog = base_wishlist.read_text(encoding="utf-8")
    add_row(
        rows,
        "manual wishlist actions use do_search",
        wishlist_dialog.count('core.search.do_search(wish, mode="wishlist")') >= 2,
        "Search for Item and Set Custom Filters both create page searches",
        state="baseline",
    )
    do_search = extract_method(base_search, "Search", "do_search")
    add_row(rows, "do_search constructs SearchRequest path", "self._add_search(" in do_search,
            "manual wishlist mode does not call _add_wish_search", state="baseline")
    add_search = extract_method(base_search, "Search", "_add_search")
    add_wish = extract_method(base_search, "Search", "_add_wish_search")
    add_row(rows, "normal constructor is SearchRequest", "SearchRequest(" in add_search and "WishSearchRequest(" not in add_search,
            "_add_search", state="baseline")
    add_row(rows, "persistent constructor is WishSearchRequest", "WishSearchRequest(" in add_wish,
            "_add_wish_search", state="baseline")

    response = extract_method(base_gui, "Search", "file_search_response")
    add_row(rows, "GUI wishlist semantics are mode-owned", 'is_wish = (self.mode == "wishlist")' in response,
            "notifications are selected from page mode", state="baseline")
    add_row(rows, "wishlist notification target is page token", "show_search_notification(" in response and "str(self.token)" in response,
            "notification action captures the current wire token", state="baseline")
    activation = extract_method(base_app, "Application", "on_search_notification_activated")
    add_row(rows, "notification activation resolves exact token", "core.search.show_search(search_token)" in activation,
            "no logical-search fallback or alias", state="baseline")
    read_changed = extract_method(base_gui, "Search", "on_read_changed")
    add_row(rows, "seen history requires persistent token match", "search.token != self.token" in read_changed,
            "manual wishlist page token does not mutate the persistent wish", state="baseline")

    old_patch = OLD_PATCH.read_text(encoding="utf-8")
    add_row(rows, "superseded prototype split classifiers", "isinstance(search, WishSearchRequest)" in old_patch and 'self.mode == "wishlist"' in old_patch,
            "core used request class while GUI used mode", state="historical-candidate")

    repeat = extract_method(patch_search, "Search", "repeat_search")
    add_row(rows, "current candidate guards missing search", "if search is None:" in repeat,
            "no send or mutation without an owner", state="patched")
    add_row(rows, "current candidate classifies wishlist by mode", 'if search.mode == "wishlist":' in repeat,
            "covers both manual and scheduled wishlist pages", state="patched")
    add_row(rows, "wishlist path preserves token", "self.send_search_request(token)" in repeat and "return token" in repeat,
            "same-token retry retained pending policy", state="patched")
    add_row(rows, "current candidate removes request-class classifier", "isinstance(search, WishSearchRequest)" not in repeat,
            "one eligibility owner", state="patched")
    positions = {
        "remove": repeat.find("self.remove_allowed_token(token)"),
        "core": repeat.find("self.searches[new_token] = search"),
        "event": repeat.find('events.emit("rekey-search"'),
        "send": repeat.find("self.send_search_request(new_token)"),
    }
    add_row(rows, "ordinary rekey barrier order",
            -1 not in positions.values() and positions["remove"] < positions["core"] < positions["event"] < positions["send"],
            positions, state="patched")
    on_again = extract_method(patch_gui, "Search", "on_search_again")
    add_row(rows, "GUI delegates to core decision", "core.search.repeat_search(self.token)" in on_again,
            "single mode classifier", state="patched")
    add_row(rows, "GUI has no duplicate wishlist branch", 'self.mode == "wishlist"' not in on_again,
            "future callers cannot diverge from GUI branch logic", state="patched")
    add_row(rows, "offline click remains nondestructive", "UserStatus.OFFLINE" in on_again and "return" in on_again,
            "no repeat call before offline return", state="patched")

    events_source = (patched / "pynicotine/events.py").read_text(encoding="utf-8")
    add_row(rows, "rekey event registered", '"rekey-search"' in events_source,
            "event contract exists", state="patched")
    emit = extract_method(patched / "pynicotine/events.py", "Events", "emit")
    add_row(rows, "rekey callback is synchronous", "for function in self._callbacks[event_name]" in emit,
            "GUI key changes before new request send", state="patched")
    return rows


def ownership_inventory() -> list[dict[str, str]]:
    return [
        {
            "surface": "global/room/buddy/user page",
            "core_request": "SearchRequest",
            "gui_mode": "non-wishlist",
            "persistent_seen_history": "no",
            "token_notification": "no",
            "candidate_action": "fresh-token same-page rekey",
            "status": "mechanically supported; native GTK open",
        },
        {
            "surface": "manual Search for Item page",
            "core_request": "SearchRequest",
            "gui_mode": "wishlist",
            "persistent_seen_history": "no; token mismatch prevents update",
            "token_notification": "yes",
            "candidate_action": "same-token retry",
            "status": "hybrid policy packet",
        },
        {
            "surface": "manual Set Custom Filters page",
            "core_request": "SearchRequest",
            "gui_mode": "wishlist",
            "persistent_seen_history": "no; filters are read by term",
            "token_notification": "yes",
            "candidate_action": "same-token retry",
            "status": "hybrid policy packet",
        },
        {
            "surface": "scheduled wishlist result page",
            "core_request": "WishSearchRequest",
            "gui_mode": "wishlist",
            "persistent_seen_history": "yes",
            "token_notification": "yes",
            "candidate_action": "same-token retry",
            "status": "persistent wishlist policy packet",
        },
        {
            "surface": "notification activation",
            "core_request": "n/a",
            "gui_mode": "wishlist",
            "persistent_seen_history": "n/a",
            "token_notification": "exact token lookup",
            "candidate_action": "token remains stable for wishlist mode",
            "status": "closed for conservative candidate",
        },
        {
            "surface": "future direct core repeat caller",
            "core_request": "either",
            "gui_mode": "encoded in SearchRequest.mode",
            "persistent_seen_history": "varies",
            "token_notification": "varies",
            "candidate_action": "same central mode decision as GUI",
            "status": "split-brain removed",
        },
    ]


def compile_rows(patched: Path) -> list[dict[str, str]]:
    paths = [
        patched / "pynicotine/events.py",
        patched / "pynicotine/search.py",
        patched / "pynicotine/gtkgui/search.py",
        ARTIFACTS / "search_mode_ownership_model.py",
        ARTIFACTS / "test_search_mode_ownership_contract.py",
        ROOT / "tools/probe_rev0083_search_mode_ownership.py",
        ROOT / "tools/run_rev0083_unit_lane.py",
        ROOT / "tools/audit_current_candidate_artifacts.py",
    ]
    rows: list[dict[str, str]] = []
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, detail = "pass", ""
        except (OSError, SyntaxError) as exc:
            status, detail = "fail", str(exc)
        if patched in path.parents:
            relative = path.relative_to(patched).as_posix()
        else:
            relative = path.relative_to(ROOT).as_posix()
        rows.append({"path": relative, "status": status, "detail": detail})
    return rows


def unit_evidence_checks(source_zip: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    inspection = inspect_bundle(source_zip)
    patch_digest = sha256_path(PATCH)
    lanes: dict[str, Any] = {}
    for lane in ("baseline", "patched"):
        relative = Path(f"data/{REVISION}_search_mode_unit_{lane}.json")
        path = ROOT / relative
        record = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        junit_value = record.get("junit", {}).get("path")
        junit = ROOT / junit_value if isinstance(junit_value, str) else ROOT / "missing"
        checks = {
            "record exists": path.is_file(),
            "record status": record.get("status") == "pass",
            "record revision": record.get("revision") == REVISION,
            "source bundle digest": record.get("source", {}).get("bundle_sha256") == inspection.sha256,
            "source lane": record.get("source", {}).get("lane") == LANE,
            "source ref": record.get("source", {}).get("executable_source_ref") == EXECUTABLE_REF,
            "test count": record.get("tests", {}).get("total") == 61,
            "test outcomes": record.get("tests", {}).get("passed") == 60 and record.get("tests", {}).get("skipped") == 1,
            "junit exists": junit.is_file(),
            "junit digest": junit.is_file() and sha256_path(junit) == record.get("junit", {}).get("sha256"),
            "source extraction cleaned": record.get("source_isolation", {}).get("source_extraction_cleaned_after_run") is True,
            "environment cleaned": record.get("source_isolation", {}).get("isolated_environment_cleaned_after_run") is True,
        }
        if lane == "patched":
            checks.update({
                "patch applied": record.get("candidate_patch", {}).get("applied") is True,
                "patch path": record.get("candidate_patch", {}).get("path") == PATCH.relative_to(ROOT).as_posix(),
                "patch digest": record.get("candidate_patch", {}).get("sha256") == patch_digest,
            })
        else:
            checks["baseline unpatched"] = record.get("candidate_patch", {}).get("applied") is False
        for check, passed in checks.items():
            rows.append({
                "lane": lane,
                "check": check,
                "status": "pass" if passed else "fail",
                "detail": relative.as_posix(),
            })
        lanes[lane] = {
            "record": relative.as_posix(),
            "junit": junit_value,
            "tests": record.get("tests"),
            "checks": len(checks),
        }
    summary = {
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "lanes": lanes,
    }
    return rows, summary


def run(source_arg: str) -> dict[str, Any]:
    source_zip, inspections = locate_source_bundle(source_arg)
    inspection = inspect_bundle(source_zip)
    if inspection.status != "pass":
        raise RuntimeError("source bundle failed content contract")
    if bundled_lane_head(source_zip) != EXECUTABLE_REF:
        raise RuntimeError("bundled master lane head drifted")

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{REVISION}-mode-ownership-", dir="/mnt/data") as temp_name:
        temp = Path(temp_name)
        baseline = temp / "baseline"
        patched = temp / "patched"
        extracted = safe_extract_tar_gz_member(source_zip, archive_member_name(LANE), baseline)
        shutil.copytree(baseline, patched)
        patch_result = run_bounded(
            ["git", "apply", str(PATCH)],
            cwd=patched,
            timeout=60,
            output_path=EVIDENCE / "patch-apply.log",
        )
        if patch_result.returncode != 0:
            raise RuntimeError(f"candidate patch failed: {patch_result.stdout}")

        invariants = source_invariants(baseline, patched)
        compiles = compile_rows(patched)
        runtime = temp / "environment"
        env, cwd = isolated_environment(
            runtime,
            python_paths=(patched, ARTIFACTS),
            inherit={
                "NICOTINE_SOURCE_ROOT": str(baseline),
                "NICOTINE_PATCH_SOURCE_ROOT": str(patched),
            },
        )
        junit = EVIDENCE / "mode-ownership.junit.xml"
        test_result = run_bounded(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(TEST_FILE), f"--junitxml={junit}"],
            cwd=cwd,
            env=env,
            timeout=120,
            output_path=EVIDENCE / "mode-ownership.log",
        )
        cleanup = purge_isolated_environment(runtime)
        tests = parse_junit_report(junit) if junit.is_file() else []
        for row in tests:
            row["status"] = "pass" if row["passed"] else "fail"

        unit_rows, unit_summary = unit_evidence_checks(source_zip)
        inventory = ownership_inventory()
        errors: list[str] = []
        if any(row["status"] != "pass" for row in invariants):
            errors.append("source invariant failure")
        if any(row["status"] != "pass" for row in compiles):
            errors.append("compile failure")
        if test_result.returncode != 0 or any(not row["passed"] for row in tests):
            errors.append("mode ownership test failure")
        if len(tests) != 16:
            errors.append(f"expected 16 mode ownership tests, found {len(tests)}")
        if unit_summary["status"] != "pass":
            errors.append("fresh upstream unit evidence failed its binding contract")
        if cleanup["residual_directories"]:
            errors.append("isolated environment residue")

        result = {
            "revision": REVISION,
            "status": "pass" if not errors else "fail",
            "source": {
                "bundle": source_zip.name,
                "bundle_sha256": inspection.sha256,
                "lane": LANE,
                "executable_source_ref": EXECUTABLE_REF,
                "public_source_ref": PUBLIC_REF,
                "extracted_files": extracted,
                "candidates_inspected": len(inspections),
                "scope": "executable proxy plus separately reviewed current public flow",
            },
            "candidate_patch": {
                "path": PATCH.relative_to(ROOT).as_posix(),
                "sha256": sha256_path(PATCH),
                "selected": False,
            },
            "findings": {
                "hybrid_page": "manual wishlist searches are SearchRequest records with wishlist GUI semantics",
                "notification_counterexample": "request-class-only rekey can stale an already displayed manual-wishlist notification token",
                "persistent_boundary": "only WishSearchRequest owns ignored_users, but both wishlist page types own token-addressed notification semantics",
                "candidate_correction": "mode classification is centralized in Search.repeat_search; GUI delegates without a second policy branch",
                "ordinary_scope": "fresh-token rekey remains limited to non-wishlist page modes",
                "wishlist_scope": "manual and scheduled wishlist pages retain same-token Retry pending separate policies",
                "selected_patch": None,
            },
            "source_invariants": {
                "passed": sum(row["status"] == "pass" for row in invariants),
                "total": len(invariants),
            },
            "ownership_inventory": {
                "rows": len(inventory),
                "hybrid_rows": sum("hybrid" in row["status"] for row in inventory),
            },
            "artifact_tests": {
                "passed": sum(row["passed"] for row in tests),
                "failed": sum(not row["passed"] for row in tests),
                "total": len(tests),
                "returncode": test_result.returncode,
            },
            "compile_checks": {
                "passed": sum(row["status"] == "pass" for row in compiles),
                "total": len(compiles),
            },
            "upstream_units": unit_summary,
            "runtime_environment_cleanup": cleanup,
            "errors": errors,
        }

        write_csv(ROOT / f"data/{REVISION}_search_mode_source_invariants.csv", invariants,
                  fields=("check", "state", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_mode_ownership_inventory.csv", inventory,
                  fields=("surface", "core_request", "gui_mode", "persistent_seen_history", "token_notification", "candidate_action", "status"))
        write_csv(ROOT / f"data/{REVISION}_search_mode_test_matrix.csv", tests,
                  fields=("nodeid", "name", "outcome", "passed", "status", "duration", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_mode_compile_matrix.csv", compiles,
                  fields=("path", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_mode_unit_checks.csv", unit_rows,
                  fields=("lane", "check", "status", "detail"))
        write_json(ROOT / f"data/{REVISION}_search_mode_summary.json", result)
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
