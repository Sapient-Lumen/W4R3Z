#!/usr/bin/env python3
"""Audit stable GUI notification identity for Search Again.

The probe executes a full research candidate against the content-addressed
master proxy, checks source ownership invariants, runs the isolated model suite,
and binds fresh upstream-unit evidence. It does not select an upstream patch
or claim native GTK validation.
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
PATCH = ARTIFACTS / "search_again_stable_notification_rekey_rev0084.patch"
MODEL = ARTIFACTS / "search_notification_identity_model.py"
TEST_FILE = ARTIFACTS / "test_search_notification_identity_contract.py"
EVIDENCE = ROOT / f"evidence/{REVISION}-search-notification-identity-runtime"


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


def add(rows: list[dict[str, str]], check: str, passed: bool, detail: object, state: str) -> None:
    rows.append({
        "state": state,
        "check": check,
        "status": "pass" if passed else "fail",
        "detail": str(detail),
    })


def source_invariants(baseline: Path, patched: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    base_core = baseline / "pynicotine/search.py"
    base_gui = baseline / "pynicotine/gtkgui/search.py"
    base_app = baseline / "pynicotine/gtkgui/application.py"
    base_notify = baseline / "pynicotine/notifications.py"
    base_wishlist = baseline / "pynicotine/gtkgui/dialogs/wishlist.py"
    patch_core = patched / "pynicotine/search.py"
    patch_gui = patched / "pynicotine/gtkgui/search.py"
    patch_app = patched / "pynicotine/gtkgui/application.py"
    patch_notify = patched / "pynicotine/notifications.py"
    patch_events = patched / "pynicotine/events.py"
    patch_tray = patched / "pynicotine/gtkgui/widgets/trayicon.py"

    wishlist = base_wishlist.read_text(encoding="utf-8")
    add(rows, "manual wishlist creates normal page search",
        wishlist.count('core.search.do_search(wish, mode="wishlist")') >= 2,
        "Search for Item and Set Custom Filters", "baseline")
    add_search = extract_method(base_core, "Search", "_add_search")
    add_wish = extract_method(base_core, "Search", "_add_wish_search")
    add(rows, "normal page owner is SearchRequest",
        "SearchRequest(" in add_search and "WishSearchRequest(" not in add_search,
        "_add_search", "baseline")
    add(rows, "scheduled wish owner is WishSearchRequest",
        "WishSearchRequest(" in add_wish, "_add_wish_search", "baseline")

    response = extract_method(base_gui, "Search", "file_search_response")
    add(rows, "wishlist notification captures wire token",
        "show_search_notification(" in response and "str(self.token)" in response,
        "desktop target changes when token changes", "baseline")
    activation = extract_method(base_app, "Application", "on_search_notification_activated")
    add(rows, "activation parses exact wire token",
        "int(search_token_variant.get_string())" in activation and "core.search.show_search(search_token)" in activation,
        "no stable GUI-page identity", "baseline")
    show_notification = extract_method(base_app, "Application", "_show_notification")
    add(rows, "Gio notification is unaddressable",
        "send_notification(id=None" in show_notification,
        "cannot replace or withdraw by ID", "baseline")
    add(rows, "core wrapper has no withdrawal operation",
        "withdraw_search_notification" not in base_notify.read_text(encoding="utf-8"),
        "close cannot retract a search notification", "baseline")

    repeat = extract_method(patch_core, "Search", "repeat_search")
    add(rows, "persistent wish classification is request-owned",
        "isinstance(search, WishSearchRequest)" in repeat,
        "only persistent scheduler/seen-history owner keeps same-token Retry", "patched")
    add(rows, "manual wishlist no longer trapped by page mode",
        'search.mode == "wishlist"' not in repeat,
        "manual SearchRequest can rotate token", "patched")
    positions = {
        "remove": repeat.find("self.remove_allowed_token(token)"),
        "core": repeat.find("self.searches[new_token] = search"),
        "gui": repeat.find('events.emit("rekey-search"'),
        "send": repeat.find("self.send_search_request(new_token)"),
    }
    add(rows, "rekey barrier order",
        -1 not in positions.values() and positions["remove"] < positions["core"] < positions["gui"] < positions["send"],
        positions, "patched")

    create_page = extract_method(patch_gui, "Searches", "create_page")
    add(rows, "page identity is UUID-backed",
        "uuid.uuid4().hex" in create_page,
        "non-reused across token rotation and normal restarts", "patched")
    add(rows, "logical page map is separate from token map",
        "self.notification_pages[notification_id] = page" in create_page,
        "one stable activation owner per page", "patched")
    rekey = extract_method(patch_gui, "Searches", "rekey_search")
    add(rows, "rekey changes wire key but not notification identity",
        "page.token = new_token" in rekey and "notification_id" not in rekey,
        "old notification opens the same page at its new token", "patched")
    route = extract_method(patch_gui, "Searches", "show_search_notification_page")
    add(rows, "activation resolves stable page map",
        "self.notification_pages.get(notification_id)" in route and "self.show_search(page.token)" in route,
        "current token is resolved at activation time", "patched")
    remove = extract_method(patch_gui, "Searches", "remove_search")
    add(rows, "page close removes stable mapping",
        "self.notification_pages.pop(page.notification_id, None)" in remove,
        "stale actions cannot resolve", "patched")
    add(rows, "page close withdraws notification",
        "withdraw_search_notification(page.notification_id)" in remove,
        "lifecycle cleanup", "patched")
    destroy = extract_method(patch_gui, "Searches", "destroy")
    add(rows, "clean shutdown withdraws all search notifications",
        "for notification_id in tuple(self.notification_pages)" in destroy and
        "withdraw_search_notification(notification_id)" in destroy,
        "Gio notifications may otherwise outlive process", "patched")

    patched_response = extract_method(patch_gui, "Search", "file_search_response")
    add(rows, "notification emits stable page ID",
        "self.notification_id" in patched_response and "str(self.token)" not in patched_response,
        "wire token is no longer action identity", "patched")
    patched_activation = extract_method(patch_app, "Application", "on_search_notification_activated")
    add(rows, "application activation avoids integer token parsing",
        "int(" not in patched_activation and "show_search_notification_page" in patched_activation,
        "GUI-owned routing", "patched")
    patched_show = extract_method(patch_app, "Application", "_show_search_notification")
    add(rows, "search notifications receive stable Gio ID",
        "notification_id=self._get_search_notification_id(search_page_id)" in patched_show,
        "repeated page notification replaces prior one", "patched")
    patched_generic = extract_method(patch_app, "Application", "_show_notification")
    add(rows, "generic notification forwards optional ID",
        "send_notification(id=notification_id" in patched_generic,
        "other notification callers remain None-addressed", "patched")
    patched_withdraw = extract_method(patch_app, "Application", "_withdraw_search_notification")
    add(rows, "Gio withdrawal uses same namespaced ID",
        "withdraw_notification(self._get_search_notification_id(search_page_id))" in patched_withdraw,
        "replace and withdraw key agree", "patched")
    add(rows, "Windows withdrawal is target-qualified",
        "action_target=search_page_id" in patched_withdraw,
        "closing page A cannot dismiss newer page B balloon", "patched")

    tray_source = patch_tray.read_text(encoding="utf-8")
    add(rows, "Win32 compares both action and target",
        "self._click_action != expected_action or current_target != action_target" in tray_source,
        "bounded single-balloon ownership", "patched")
    add(rows, "Win32 clears balloon with empty info",
        'self._notify_id.sz_info = ""' in tray_source and "Shell_NotifyIconW(self.NIM_MODIFY" in tray_source,
        "documented NIF_INFO withdrawal mechanism", "patched")
    add(rows, "notification withdrawal event is registered",
        '"withdraw-search-notification"' in patch_events.read_text(encoding="utf-8") and
        "withdraw_search_notification" in patch_notify.read_text(encoding="utf-8"),
        "cross-layer lifecycle contract", "patched")
    add(rows, "candidate has no token alias registry",
        "token_alias" not in patch_gui.read_text(encoding="utf-8") and
        "old_to_new" not in patch_gui.read_text(encoding="utf-8"),
        "mapping size bounded by open pages", "patched")
    return rows


def ownership_inventory() -> list[dict[str, str]]:
    return [
        {
            "surface": "ordinary global/room/buddy/user page",
            "request_owner": "SearchRequest",
            "wire_action": "fresh-token rekey",
            "notification_identity": "stable UUID page ID (normally unused)",
            "remaining_boundary": "native GTK3/GTK4 state validation",
        },
        {
            "surface": "manual Search for Item wishlist page",
            "request_owner": "SearchRequest",
            "wire_action": "fresh-token rekey",
            "notification_identity": "stable UUID page ID",
            "remaining_boundary": "native GTK3/GTK4 notification and page-state validation",
        },
        {
            "surface": "manual Set Custom Filters wishlist page",
            "request_owner": "SearchRequest",
            "wire_action": "fresh-token rekey",
            "notification_identity": "stable UUID page ID",
            "remaining_boundary": "native GTK3/GTK4 filter preservation validation",
        },
        {
            "surface": "scheduled persistent wishlist page",
            "request_owner": "WishSearchRequest",
            "wire_action": "same-token Retry",
            "notification_identity": "stable UUID page ID",
            "remaining_boundary": "product policy for true refresh/reset",
        },
        {
            "surface": "Gio desktop shell",
            "request_owner": "application notification ID",
            "wire_action": "not applicable",
            "notification_identity": "search-<UUID>",
            "remaining_boundary": "native desktop-shell integration",
        },
        {
            "surface": "Win32 tray balloon",
            "request_owner": "single current action/target pair",
            "wire_action": "not applicable",
            "notification_identity": "UUID target",
            "remaining_boundary": "native Windows integration",
        },
    ]


def compile_rows(patched: Path) -> list[dict[str, str]]:
    paths = [
        patched / "pynicotine/events.py",
        patched / "pynicotine/search.py",
        patched / "pynicotine/notifications.py",
        patched / "pynicotine/gtkgui/search.py",
        patched / "pynicotine/gtkgui/application.py",
        patched / "pynicotine/gtkgui/widgets/trayicon.py",
        MODEL,
        TEST_FILE,
        ROOT / "tools/probe_rev0084_search_notification_identity.py",
        ROOT / "tools/run_rev0084_unit_lane.py",
        ROOT / "tools/audit_current_environment_capabilities.py",
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


def unit_evidence_checks(source_zip: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    inspection = inspect_bundle(source_zip)
    patch_digest = sha256_path(PATCH)
    lanes: dict[str, Any] = {}
    for lane in ("baseline", "patched"):
        relative = Path(f"data/{REVISION}_search_notification_unit_{lane}.json")
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
        lanes[lane] = {"record": relative.as_posix(), "junit": junit_value, "tests": record.get("tests")}
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
    with tempfile.TemporaryDirectory(prefix=f"{REVISION}-notification-identity-", dir="/mnt/data") as temp_name:
        temp = Path(temp_name)
        baseline = temp / "baseline"
        patched = temp / "patched"
        extracted = safe_extract_tar_gz_member(source_zip, archive_member_name(LANE), baseline)
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
        junit = EVIDENCE / "notification-identity.junit.xml"
        test_result = run_bounded(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(TEST_FILE), f"--junitxml={junit}"],
            cwd=cwd, env=env, timeout=120, output_path=EVIDENCE / "notification-identity.log",
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
            errors.append("notification identity model failure")
        if len(tests) != 25:
            errors.append(f"expected 25 model tests, found {len(tests)}")
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
                "identity_split": "wire token is a response capability; desktop actions require stable GUI page identity",
                "manual_wishlist": "manual wishlist SearchRequest pages can mechanically rekey once notifications target stable page IDs",
                "persistent_wishlist": "WishSearchRequest pages remain same-token Retry pending product policy",
                "gio_lifecycle": "stable notification IDs bound repeated notifications and enable close/shutdown withdrawal",
                "win32_lifecycle": "withdraw only the current matching balloon action/target",
                "remaining": "native GTK3/GTK4 and desktop-shell integration validation",
            },
            "source_invariants": {
                "passed": sum(row["status"] == "pass" for row in invariants),
                "total": len(invariants),
            },
            "model_tests": {
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
            "inventory_rows": len(inventory),
            "environment_cleanup": cleanup,
            "selected_patch": None,
            "errors": errors,
        }

        write_csv(ROOT / f"data/{REVISION}_search_notification_source_invariants.csv", invariants,
                  fields=("state", "check", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_notification_ownership_inventory.csv", inventory,
                  fields=("surface", "request_owner", "wire_action", "notification_identity", "remaining_boundary"))
        write_csv(ROOT / f"data/{REVISION}_search_notification_test_matrix.csv", tests,
                  fields=("nodeid", "name", "outcome", "passed", "status", "duration", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_notification_compile_matrix.csv", compiles,
                  fields=("path", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_notification_unit_checks.csv", unit_rows,
                  fields=("lane", "check", "status", "detail"))
        write_json(ROOT / f"data/{REVISION}_search_notification_summary.json", result)
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
