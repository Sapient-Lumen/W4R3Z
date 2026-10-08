#!/usr/bin/env python3
"""Audit persistent wishlist inbox ownership and the inherited repeat action."""
from __future__ import annotations

import argparse
import ast
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
    isolated_environment,
    parse_junit_report,
    purge_isolated_environment,
    run_bounded,
    sha256_path,
    write_csv,
    write_json,
)
from materialize_current_public_head import (  # noqa: E402
    load_contract as load_public_head_contract,
    materialize,
)
from source_bundle_locator import inspect_bundle, locate_source_bundle  # noqa: E402

REVISION = derive_revision(ROOT)
PUBLIC_HEAD_CONTRACT = load_public_head_contract(ROOT)
BASE_LANE = PUBLIC_HEAD_CONTRACT["base_lane"]
DERIVED_LANE = PUBLIC_HEAD_CONTRACT["derived_lane_id"]
EXECUTABLE_REF = PUBLIC_HEAD_CONTRACT["target_ref"]
ARTIFACTS = ROOT / "maintainer_artifacts/wishlist-inbox-01"
PATCH = ROOT / PUBLIC_HEAD_CONTRACT["candidate"]["path"]
EVIDENCE = ROOT / f"evidence/{REVISION}-wishlist-inbox-runtime"


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


def add(rows: list[dict[str, str]], state: str, check: str, passed: bool, detail: object = "") -> None:
    rows.append({
        "state": state,
        "check": check,
        "status": "pass" if passed else "fail",
        "detail": str(detail),
    })


def source_invariants(baseline: Path, patched: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    core = baseline / "pynicotine/search.py"
    gui = baseline / "pynicotine/gtkgui/search.py"
    dialog = baseline / "pynicotine/gtkgui/dialogs/wishlist.py"
    patched_core = patched / "pynicotine/search.py"
    patched_gui = patched / "pynicotine/gtkgui/search.py"

    wish_init = extract_method(core, "WishSearchRequest", "__init__")
    wish_dict = extract_method(core, "WishSearchRequest", "as_dict")
    scheduler = extract_method(core, "Search", "_do_next_wishlist_search")
    schedule_send = extract_method(core, "Search", "_do_wishlist_search")
    dispatch = extract_method(core, "Search", "send_search_request")
    incoming = extract_method(core, "Search", "_file_search_response")
    remove = extract_method(core, "Search", "remove_search")
    cap = extract_method(gui, "Searches", "file_search_response")
    read = extract_method(gui, "Search", "on_read_changed")
    repeat = extract_method(gui, "Search", "on_search_again")
    dialog_text = dialog.read_text(encoding="utf-8")

    add(rows, "baseline", "persistent owner starts ignored", "self.is_ignored = True" in wish_init)
    add(rows, "baseline", "persistent owner owns ignored users", "self.ignored_users" in wish_init)
    add(rows, "baseline", "ignored users are serialized", '"ignored_users"' in wish_dict)
    add(rows, "baseline", "scheduler reactivates request", "search.is_ignored = False" in scheduler)
    add(rows, "baseline", "scheduler calls special wishlist send", "self._do_wishlist_search(search)" in scheduler)
    add(rows, "baseline", "scheduled send adds response admission", "self.add_allowed_token(search.token)" in schedule_send)
    add(rows, "baseline", "scheduled send uses WishlistSearch", "WishlistSearch(search.token, text)" in schedule_send)
    add(rows, "baseline", "manual repeat uses same page token", "send_search_request(self.token)" in repeat)
    add(rows, "baseline", "wishlist mode manual repeat uses global path",
        'search.mode in {"global", "wishlist"}' in dispatch and "_send_global_search_request(search)" in dispatch)
    add(rows, "baseline", "seen sender rejected in core", "username in search.ignored_users" in incoming)
    add(rows, "baseline", "read transition stores sender identity", "search.ignored_users.add(username)" in read)
    add(rows, "baseline", "cap gate removes parser admission", "remove_allowed_token(msg.token)" in cap)
    add(rows, "baseline", "cap gate has no scheduler pause", "pause" not in cap.lower())
    add(rows, "baseline", "close preserves persistent request", "search.is_ignored = True" in remove)
    add(rows, "baseline", "manual Search for Item exists", "_Search for Item" in dialog_text)
    add(rows, "baseline", "Reset Seen Results exists", "Reset Seen Results" in dialog_text)

    eligibility = extract_method(patched_core, "Search", "can_repeat_search")
    patched_repeat = extract_method(patched_core, "Search", "repeat_search")
    patched_callback = extract_method(patched_gui, "Search", "on_search_again")
    patched_text = patched_gui.read_text(encoding="utf-8")
    add(rows, "candidate", "eligibility follows request class",
        "not isinstance(search, WishSearchRequest)" in eligibility and ".mode" not in eligibility)
    add(rows, "candidate", "persistent repeat fails closed",
        "search is None or isinstance(search, WishSearchRequest)" in patched_repeat)
    add(rows, "candidate", "persistent repeat does not resend same token",
        "self.send_search_request(token)" not in patched_repeat)
    add(rows, "candidate", "persistent repeat does not reset seen history", "ignored_users" not in patched_repeat)
    add(rows, "candidate", "disabled action is hidden", '("=" + _("Search _Again")' in patched_text)
    add(rows, "candidate", "menu action uses core eligibility", "can_repeat_search(self.token)" in patched_text)
    add(rows, "candidate", "callback has defensive eligibility guard",
        "if not core.search.can_repeat_search(self.token):" in patched_callback)
    return rows


def compile_rows(patched: Path) -> list[dict[str, str]]:
    paths = [
        patched / "pynicotine/events.py",
        patched / "pynicotine/search.py",
        patched / "pynicotine/notifications.py",
        patched / "pynicotine/gtkgui/search.py",
        patched / "pynicotine/gtkgui/application.py",
        patched / "pynicotine/gtkgui/widgets/trayicon.py",
        ARTIFACTS / "wishlist_inbox_model.py",
        ARTIFACTS / "test_wishlist_inbox_model.py",
        ARTIFACTS / "test_wishlist_inbox_source_semantics.py",
        ROOT / "tools/probe_rev0085_wishlist_inbox.py",
        ROOT / "tools/run_current_unit_lane.py",
        ROOT / "tools/run_pytest_completion_exit.py",
        ROOT / "tools/audit_current_public_head.py",
        ROOT / "tools/audit_current_patch_composition.py",
        ROOT / "tools/audit_current_search_action_policy.py",
    ]
    rows: list[dict[str, str]] = []
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, detail = "pass", ""
        except (OSError, SyntaxError) as exc:
            status, detail = "fail", str(exc)
        relative = path.relative_to(patched).as_posix() if patched in path.parents else path.relative_to(ROOT).as_posix()
        rows.append({"path": relative, "status": status, "detail": detail})
    return rows


def policy_inventory() -> list[dict[str, str]]:
    return [
        {
            "surface": "ordinary search page",
            "owner": "SearchRequest",
            "current_action": "same-token resend",
            "candidate_action": "fresh-token same-page refresh",
            "remaining_boundary": "native GTK validation",
        },
        {
            "surface": "manual wishlist page",
            "owner": "SearchRequest(mode=wishlist)",
            "current_action": "same-token resend",
            "candidate_action": "fresh-token same-page refresh",
            "remaining_boundary": "native notification and GTK validation",
        },
        {
            "surface": "persistent wishlist result page",
            "owner": "WishSearchRequest",
            "current_action": "same-token ordinary FileSearch",
            "candidate_action": "Search Again absent",
            "remaining_boundary": "native action visibility and maintainer acceptance",
        },
        {
            "surface": "wishlist dialog Search for Item",
            "owner": "new SearchRequest(mode=wishlist)",
            "current_action": "independent manual page",
            "candidate_action": "unchanged explicit manual alternative",
            "remaining_boundary": "none in this packet",
        },
        {
            "surface": "persistent scheduler at display cap",
            "owner": "WishSearchRequest plus GUI page",
            "current_action": "repeated WishlistSearch with no page capacity",
            "candidate_action": "unresolved separate packet",
            "remaining_boundary": "pause, rollover, eviction, or inbox archive policy",
        },
    ]


def unit_evidence_checks(source_zip: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    inspection = inspect_bundle(source_zip)
    patch_digest = sha256_path(PATCH)
    lanes: dict[str, Any] = {}
    for lane in ("baseline", "patched"):
        relative = Path(f"data/{REVISION}_public_head_unit_{lane}.json")
        path = ROOT / relative
        record = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        junit_value = record.get("junit", {}).get("path")
        junit = ROOT / junit_value if isinstance(junit_value, str) else ROOT / "missing"
        completion = record.get("pytest_completion", {})
        marker = completion.get("marker", {}) if isinstance(completion, dict) else {}
        marker_value = completion.get("path") if isinstance(completion, dict) else None
        marker_path = ROOT / marker_value if isinstance(marker_value, str) else ROOT / "missing"
        checks = {
            "record exists": path.is_file(),
            "record status": record.get("status") == "pass",
            "record revision": record.get("revision") == REVISION,
            "source bundle digest": record.get("source", {}).get("bundle_sha256") == inspection.sha256,
            "derived lane": record.get("source", {}).get("derived_lane") == DERIVED_LANE,
            "source ref": record.get("source", {}).get("executable_source_ref") == EXECUTABLE_REF,
            "test count": record.get("tests", {}).get("total") == 61,
            "test outcomes": record.get("tests", {}).get("passed") == 60 and record.get("tests", {}).get("skipped") == 1,
            "junit exists": junit.is_file(),
            "junit digest": junit.is_file() and sha256_path(junit) == record.get("junit", {}).get("sha256"),
            "pytest main returned": (
                marker.get("pytest_main_returned") is True
                and marker.get("version") == 1
                and marker.get("exit_code") == record.get("tests", {}).get("returncode") == 0
            ),
            "completion marker exists": marker_path.is_file(),
            "completion marker digest": (
                marker_path.is_file() and sha256_path(marker_path) == completion.get("sha256")
            ),
            "unit profile": record.get("profile") == "exact-public-head-current-candidate",
            "source extraction cleaned": record.get("source_isolation", {}).get("source_extraction_cleaned_after_run") is True,
            "environment cleaned": record.get("source_isolation", {}).get("isolated_environment_cleaned_after_run") is True,
        }
        if lane == "patched":
            checks.update({
                "patch applied": record.get("candidate_patch", {}).get("applied") is True,
                "candidate artifact": record.get("candidate_patch", {}).get("artifact_id") == "SEARCH-REKEY-01-rev0085",
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
            "runner_mode": "pytest-main-returned" if marker.get("pytest_main_returned") is True else None,
            "tests": record.get("tests"),
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

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{REVISION}-wishlist-inbox-", dir="/mnt/data") as temp_name:
        temp = Path(temp_name)
        baseline = temp / "baseline"
        patched = temp / "patched"
        materialization = materialize(
            source_zip, baseline, root=ROOT, contract=PUBLIC_HEAD_CONTRACT
        )
        extracted = materialization["extracted_files"]
        shutil.copytree(baseline, patched)
        patch_result = run_bounded(
            ["git", "apply", str(PATCH)], cwd=patched, timeout=60,
            output_path=EVIDENCE / "patch-apply.log",
        )
        if patch_result.returncode != 0:
            raise RuntimeError(f"candidate patch failed: {patch_result.stdout}")

        invariants = source_invariants(baseline, patched)
        compiles = compile_rows(patched)
        runtime = temp / "environment"
        env, cwd = isolated_environment(runtime, python_paths=(ARTIFACTS,))
        env["NICOTINE_SOURCE_ROOT"] = str(baseline)
        env["NICOTINE_PATCHED_SOURCE_ROOT"] = str(patched)
        junit = EVIDENCE / "wishlist-inbox.junit.xml"
        test_result = run_bounded(
            [
                sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                str(ARTIFACTS / "test_wishlist_inbox_model.py"),
                str(ARTIFACTS / "test_wishlist_inbox_source_semantics.py"),
                f"--junitxml={junit}",
            ],
            cwd=cwd, env=env, timeout=120, output_path=EVIDENCE / "wishlist-inbox.log",
        )
        cleanup = purge_isolated_environment(runtime)
        tests = parse_junit_report(junit) if junit.is_file() else []
        for row in tests:
            row["status"] = "pass" if row["passed"] else "fail"

        unit_rows, unit_summary = unit_evidence_checks(source_zip)
        inventory = policy_inventory()
        errors: list[str] = []
        if any(row["status"] != "pass" for row in invariants):
            errors.append("source invariant failure")
        if any(row["status"] != "pass" for row in compiles):
            errors.append("compile failure")
        if test_result.returncode != 0 or any(not row["passed"] for row in tests):
            errors.append("wishlist inbox model/source failure")
        if len(tests) != 28:
            errors.append(f"expected 28 research tests, found {len(tests)}")
        if unit_summary["status"] != "pass":
            errors.append("upstream unit evidence failed binding contract")
        if cleanup["residual_directories"]:
            errors.append("isolated environment residue")

        result = {
            "revision": REVISION,
            "status": "pass" if not errors else "fail",
            "source": {
                "bundle": source_zip.name,
                "bundle_sha256": inspection.sha256,
                "base_lane": BASE_LANE,
                "derived_lane": DERIVED_LANE,
                "executable_source_ref": EXECUTABLE_REF,
                "extracted_files": extracted,
                "candidates_inspected": len(inspections),
                "materialization": materialization,
                "scope": "exact public-master file content derived from a pinned bundled base and blob-verified delta",
            },
            "candidate_patch": {
                "path": PATCH.relative_to(ROOT).as_posix(),
                "sha256": sha256_path(PATCH),
                "selected": False,
            },
            "findings": {
                "persistent_page_role": "delivered batch for a scheduled subscription, not a page-owned search epoch",
                "action_mismatch": "inherited Search Again emits ordinary FileSearch while scheduled delivery uses WishlistSearch",
                "seen_history": "sender-level durable state with a separate explicit Reset Seen Results command",
                "candidate_policy": "remove Search Again from WishSearchRequest pages; retain Search for Item as manual alternative",
                "separate_cap_packet": "scheduler can continue issuing requests after the open page has no display capacity",
            },
            "source_invariants": {
                "passed": sum(row["status"] == "pass" for row in invariants),
                "total": len(invariants),
            },
            "research_tests": {
                "passed": sum(row["passed"] for row in tests),
                "total": len(tests),
                "returncode": test_result.returncode,
                "junit": junit.relative_to(ROOT).as_posix(),
            },
            "compile_checks": {
                "passed": sum(row["status"] == "pass" for row in compiles),
                "total": len(compiles),
            },
            "unit_evidence": unit_summary,
            "policy_inventory_rows": len(inventory),
            "environment_cleanup": cleanup,
            "selected_patch": None,
            "errors": errors,
        }

        write_csv(ROOT / f"data/{REVISION}_wishlist_inbox_source_invariants.csv", invariants,
                  fields=("state", "check", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_wishlist_inbox_policy_inventory.csv", inventory,
                  fields=("surface", "owner", "current_action", "candidate_action", "remaining_boundary"))
        write_csv(ROOT / f"data/{REVISION}_wishlist_inbox_test_matrix.csv", tests,
                  fields=("nodeid", "name", "outcome", "passed", "status", "duration", "detail"))
        write_csv(ROOT / f"data/{REVISION}_wishlist_inbox_compile_matrix.csv", compiles,
                  fields=("path", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_wishlist_inbox_unit_checks.csv", unit_rows,
                  fields=("lane", "check", "status", "detail"))
        write_json(ROOT / f"data/{REVISION}_wishlist_inbox_summary.json", result)
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
