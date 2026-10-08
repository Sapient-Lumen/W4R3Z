#!/usr/bin/env python3
"""Close the official Search Again token-consumer inventory on the bundled master proxy.

The probe applies the unchanged rev0081 ordinary-search rekey prototype to a
clean source extraction, checks event ordering and every in-tree supported token
consumer, runs source-backed model tests, and verifies that the unchanged
upstream-unit evidence can be reused by digest instead of rerun.
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
PATCH = ARTIFACTS / "search_again_fresh_token_rekey.patch"
TEST_FILE = ARTIFACTS / "test_search_consumer_contract.py"
EVIDENCE = ROOT / f"evidence/{REVISION}-search-consumer-runtime"


def lane_head(source_zip: Path) -> str:
    suffix = f"git-full/.git/worktrees/{LANE}/HEAD"
    with zipfile.ZipFile(source_zip) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix}, found {len(matches)}")
        return archive.read(matches[0]).decode("ascii").strip()


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


def add_check(rows: list[dict[str, Any]], check_id: str, passed: bool, detail: str, *, state: str) -> None:
    rows.append({
        "check_id": check_id,
        "state": state,
        "status": "pass" if passed else "fail",
        "detail": detail,
    })


def source_checks(baseline: Path, patched: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    baseline_events = (baseline / "pynicotine/events.py").read_text(encoding="utf-8")
    patched_events = (patched / "pynicotine/events.py").read_text(encoding="utf-8")
    add_check(rows, "baseline has no rekey event", '"rekey-search"' not in baseline_events,
              "candidate event is absent before patch", state="baseline")
    add_check(rows, "patched has rekey event", '"rekey-search"' in patched_events,
              "candidate event is registered after patch", state="patched")

    emit = method_source(patched / "pynicotine/events.py", "Events", "emit")
    add_check(rows, "event dispatch synchronous", "for function in self._callbacks[event_name]" in emit,
              "emit iterates callbacks inline", state="patched")
    add_check(rows, "event dispatch not queued", "emit_main_thread" not in emit,
              "rekey callback completes before send_search_request continues", state="patched")

    repeat = method_source(patched / "pynicotine/search.py", "Search", "repeat_search")
    positions = {
        "core": repeat.find("self.searches[new_token] = search"),
        "event": repeat.find('events.emit("rekey-search"'),
        "send": repeat.find("self.send_search_request(new_token)"),
    }
    add_check(rows, "core event send order", -1 not in positions.values() and positions["core"] < positions["event"] < positions["send"],
              str(positions), state="patched")
    for check_id, needle in (
        ("old parser admission retired", "self.remove_allowed_token(token)"),
        ("old self token retired", "self._own_tokens.discard(token)"),
        ("wishlist excluded", "isinstance(search, WishSearchRequest)"),
        ("request object retained", "search.token = new_token"),
    ):
        add_check(rows, check_id, needle in repeat, needle, state="patched")

    parent = (patched / "pynicotine/gtkgui/search.py").read_text(encoding="utf-8")
    gui_rekey = method_source(patched / "pynicotine/gtkgui/search.py", "Searches", "rekey_search")
    reset = method_source(patched / "pynicotine/gtkgui/search.py", "Search", "reset_for_search_again")
    add_check(rows, "GUI event consumer registered", '("rekey-search", self.rekey_search)' in parent,
              "single in-tree GUI callback", state="patched")
    for check_id, needle in (
        ("page lookup uses old key", "page = self.pages.get(old_token)"),
        ("page order preserved", "new_token if token == old_token else token"),
        ("page token rotated", "page.token = new_token"),
        ("page reset follows rekey", "page.reset_for_search_again()"),
    ):
        add_check(rows, check_id, needle in gui_rekey, needle, state="patched")
    for check_id, needle in (
        ("selection iterator cache cleared", "self.selected_results.clear()"),
        ("selection user cache cleared", "self.selected_users.clear()"),
        ("result model cleared", "self.clear_model(stored_results=True)"),
    ):
        add_check(rows, check_id, needle in reset, needle, state="patched")

    core_response = method_source(patched / "pynicotine/search.py", "Search", "_file_search_response")
    gui_response = method_source(patched / "pynicotine/gtkgui/search.py", "Searches", "file_search_response")
    add_check(rows, "queued old response core rejection", "search = self.searches.get(msg.token)" in core_response and
              "if search is None:" in core_response and "msg.token = None" in core_response,
              "old core key is absent after synchronous rekey", state="patched")
    add_check(rows, "GUI routes by current token", "page = self.pages.get(msg.token)" in gui_response,
              "new token resolves; old token does not", state="patched")

    page_response = method_source(patched / "pynicotine/gtkgui/search.py", "Search", "file_search_response")
    notification_position = page_response.find("core.notifications.show_search_notification")
    wish_guard_position = page_response.find("if tab_changed and is_wish:")
    add_check(rows, "search notification wishlist-only",
              -1 not in (notification_position, wish_guard_position) and wish_guard_position < notification_position,
              "ordinary pages cannot leave stale notification action targets", state="patched")
    notification_action = method_source(
        patched / "pynicotine/gtkgui/application.py", "Application", "_show_search_notification"
    )
    add_check(rows, "notification action token-bound", "action_target=search_token" in notification_action,
              "classified as wishlist-only boundary", state="patched")

    plugin_source = patched / "pynicotine/pluginsystem.py"
    plugin_methods = {
        "outgoing_global_search_event": ["self", "text"],
        "outgoing_room_search_event": ["self", "rooms", "text"],
        "outgoing_buddy_search_event": ["self", "text"],
        "outgoing_user_search_event": ["self", "users", "text"],
        "outgoing_wishlist_search_event": ["self", "text"],
    }
    tree = ast.parse(plugin_source.read_text(encoding="utf-8"))
    base = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "BasePlugin")
    functions = {node.name: node for node in base.body if isinstance(node, ast.FunctionDef)}
    for name, expected in plugin_methods.items():
        actual = [arg.arg for arg in functions[name].args.args]
        add_check(rows, f"plugin hook token-free: {name}", actual == expected,
                  f"actual={actual}; expected={expected}", state="patched")
    add_check(rows, "repeat does not rerun plugins", "pluginhandler" not in repeat,
              "existing processed request is reused, matching legacy Search Again", state="patched")

    remove = method_source(patched / "pynicotine/gtkgui/search.py", "Searches", "remove_search")
    restore = method_source(patched / "pynicotine/gtkgui/search.py", "Searches", "on_restore_removed_page")
    close = method_source(patched / "pynicotine/gtkgui/search.py", "Search", "on_close")
    add_check(rows, "recently closed identity token-free",
              "page_args=(page.text, page.mode, page.room, page.searched_users)" in remove and "page.token" not in remove,
              "restore payload is logical search identity", state="patched")
    add_check(rows, "recently closed creates fresh search",
              "core.search.do_search(search_term, mode, room=room, users=users)" in restore,
              "restoration does not depend on old token", state="patched")
    add_check(rows, "close follows current page token", "core.search.remove_search(self.token)" in close,
              "rekeyed page closes the new core key", state="patched")

    search_again = method_source(patched / "pynicotine/gtkgui/search.py", "Search", "on_search_again")
    add_check(rows, "GUI mode split explicit", 'if self.mode == "wishlist":' in search_again and
              "core.search.send_search_request(self.token)" in search_again and
              "core.search.repeat_search(self.token)" in search_again,
              "ordinary rekey and wishlist retry remain separate", state="patched")
    return rows


def consumer_inventory() -> list[dict[str, Any]]:
    return [
        {"consumer": "parser admission", "path": "pynicotine/search.py", "token_role": "response capability",
         "ordinary_rekey_effect": "old removed, new added before send", "blocker": "no", "status": "closed"},
        {"consumer": "core searches map", "path": "pynicotine/search.py", "token_role": "request lookup key",
         "ordinary_rekey_effect": "same request object moved to new key", "blocker": "no", "status": "closed"},
        {"consumer": "own-search tokens", "path": "pynicotine/search.py", "token_role": "self-request admission",
         "ordinary_rekey_effect": "old discarded; send path binds new", "blocker": "no", "status": "closed"},
        {"consumer": "GUI pages map", "path": "pynicotine/gtkgui/search.py", "token_role": "page lookup key",
         "ordinary_rekey_effect": "same page moved in insertion order", "blocker": "no", "status": "closed"},
        {"consumer": "GUI page token", "path": "pynicotine/gtkgui/search.py", "token_role": "close and response identity",
         "ordinary_rekey_effect": "rotated synchronously before send", "blocker": "no", "status": "closed"},
        {"consumer": "queued responses", "path": "pynicotine/search.py", "token_role": "message token lookup",
         "ordinary_rekey_effect": "old token becomes unresolvable", "blocker": "no", "status": "closed"},
        {"consumer": "search notifications", "path": "pynicotine/gtkgui/search.py", "token_role": "activation target",
         "ordinary_rekey_effect": "not emitted for ordinary pages", "blocker": "no", "status": "wishlist-only"},
        {"consumer": "plugin search hooks", "path": "pynicotine/pluginsystem.py", "token_role": "none in supported API",
         "ordinary_rekey_effect": "processed request reused; no token contract", "blocker": "no", "status": "closed"},
        {"consumer": "built-in search plugins", "path": "pynicotine/plugins/", "token_role": "none",
         "ordinary_rekey_effect": "same token-free hook surface", "blocker": "no", "status": "closed"},
        {"consumer": "recently closed tabs", "path": "pynicotine/gtkgui/search.py", "token_role": "none",
         "ordinary_rekey_effect": "logical args restored through do_search", "blocker": "no", "status": "closed"},
        {"consumer": "wishlist seen history", "path": "pynicotine/search.py", "token_role": "persistent domain state",
         "ordinary_rekey_effect": "excluded from candidate", "blocker": "yes", "status": "separate-policy"},
        {"consumer": "native GTK widget state", "path": "pynicotine/gtkgui/search.py", "token_role": "page-local state",
         "ordinary_rekey_effect": "source/model only; native behavior untested", "blocker": "yes", "status": "open"},
        {"consumer": "third-party internal imports", "path": "outside supported plugin API", "token_role": "unknown",
         "ordinary_rekey_effect": "not enumerable; no compatibility guarantee claimed", "blocker": "no", "status": "out-of-scope"},
    ]


def evidence_reuse_checks(source_zip: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    patch_digest = sha256_path(PATCH)
    results: dict[str, Any] = {}
    for lane in ("baseline", "patched"):
        relative = Path(f"data/rev0081_search_rekey_unit_{lane}.json")
        record = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        junit = ROOT / record["junit"]["path"]
        checks = {
            "record status": record.get("status") == "pass",
            "source bundle digest": record.get("source", {}).get("bundle_sha256") == sha256_path(source_zip),
            "source ref": record.get("source", {}).get("executable_source_ref") == EXECUTABLE_REF,
            "junit exists": junit.is_file(),
            "junit digest": junit.is_file() and sha256_path(junit) == record.get("junit", {}).get("sha256"),
            "test count": record.get("tests", {}).get("total") == 61,
            "test result": record.get("tests", {}).get("passed") == 60 and record.get("tests", {}).get("skipped") == 1,
        }
        if lane == "patched":
            checks["patch digest"] = record.get("candidate_patch", {}).get("sha256") == patch_digest
            checks["patch path"] = record.get("candidate_patch", {}).get("path") == PATCH.relative_to(ROOT).as_posix()
        else:
            checks["baseline unpatched"] = record.get("candidate_patch", {}).get("applied") is False
        for check_id, passed in checks.items():
            rows.append({
                "lane": lane,
                "check_id": check_id,
                "status": "pass" if passed else "fail",
                "detail": relative.as_posix(),
            })
        results[lane] = {
            "record": relative.as_posix(),
            "junit": record["junit"]["path"],
            "tests": record["tests"],
            "checks": len(checks),
        }
    summary = {
        "revision": REVISION,
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
        "mode": "digest-bound reuse; no redundant upstream unit rerun",
        "source_bundle_sha256": sha256_path(source_zip),
        "source_ref": EXECUTABLE_REF,
        "patch_sha256": patch_digest,
        "lanes": results,
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "avoided_test_executions": 122,
    }
    return rows, summary


def compile_checks(patched: Path) -> list[dict[str, Any]]:
    paths = [
        patched / "pynicotine/events.py",
        patched / "pynicotine/search.py",
        patched / "pynicotine/gtkgui/search.py",
        ARTIFACTS / "search_consumer_model.py",
        ARTIFACTS / "test_search_consumer_contract.py",
        ROOT / "tools/probe_rev0082_search_consumers.py",
    ]
    rows = []
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, detail = "pass", ""
        except (OSError, SyntaxError) as exc:
            status, detail = "fail", str(exc)
        rows.append({
            "path": path.relative_to(patched).as_posix() if patched in path.parents else path.relative_to(ROOT).as_posix(),
            "status": status,
            "detail": detail,
        })
    return rows


def run(source_arg: str) -> dict[str, Any]:
    source_zip, inspections = locate_source_bundle(source_arg)
    inspection = inspect_bundle(source_zip)
    if inspection.status != "pass":
        raise RuntimeError("source bundle failed its content contract")
    if lane_head(source_zip) != EXECUTABLE_REF:
        raise RuntimeError("bundled Git lane head does not match source contract")

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rev0082-search-consumers-", dir="/mnt/data") as temp_name:
        temp = Path(temp_name)
        baseline = temp / "baseline"
        patched = temp / "patched"
        extracted = safe_extract_tar_gz_member(source_zip, archive_member_name(LANE), baseline)
        shutil.copytree(baseline, patched)

        patch_log = EVIDENCE / "patch-apply.log"
        patch_result = run_bounded(
            ["patch", "-p1", "--batch", "--forward", "-i", str(PATCH)],
            cwd=patched,
            timeout=60,
            output_path=patch_log,
        )
        if patch_result.returncode != 0:
            raise RuntimeError(f"candidate patch failed: {patch_result.stdout}")

        invariants = source_checks(baseline, patched)
        compile_rows = compile_checks(patched)

        runtime = temp / "test-environment"
        env, cwd = isolated_environment(
            runtime,
            python_paths=(ARTIFACTS,),
            inherit={"NICOTINE_SOURCE_ROOT": str(patched), "PYTHONDONTWRITEBYTECODE": "1"},
        )
        junit = EVIDENCE / "consumer-contract.junit.xml"
        test_log = EVIDENCE / "consumer-contract.log"
        test_result = run_bounded(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(TEST_FILE),
             f"--junitxml={junit}"],
            cwd=cwd,
            env=env,
            timeout=120,
            output_path=test_log,
        )
        cleanup = purge_isolated_environment(runtime)
        tests = parse_junit_report(junit) if junit.is_file() else []
        for row in tests:
            row["status"] = "pass" if row["passed"] else "fail"

        reuse_rows, reuse_summary = evidence_reuse_checks(source_zip)
        inventory = consumer_inventory()
        errors: list[str] = []
        if any(row["status"] != "pass" for row in invariants):
            errors.append("source invariant failure")
        if any(row["status"] != "pass" for row in compile_rows):
            errors.append("compile failure")
        if test_result.returncode != 0 or any(not row["passed"] for row in tests):
            errors.append("consumer contract test failure")
        if len(tests) != 29:
            errors.append(f"expected 29 consumer tests, found {len(tests)}")
        if reuse_summary["status"] != "pass":
            errors.append("prior unit evidence reuse contract failed")
        if cleanup["residual_directories"]:
            errors.append("isolated test environment was not purged")

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
                "scope": "executable proxy plus separate current-public-flow observation",
                "candidates_inspected": len(inspections),
            },
            "candidate_patch": {
                "path": PATCH.relative_to(ROOT).as_posix(),
                "sha256": sha256_path(PATCH),
                "selected": False,
            },
            "findings": {
                "official_consumer_closure": "all in-tree and supported plugin/API token consumers are classified for ordinary searches",
                "ordering_boundary": "core and GUI identities rekey synchronously before the new request is sent",
                "late_response_boundary": "old unparsed admission is removed and already-parsed old responses lose both core and GUI lookup keys",
                "notification_boundary": "token-addressed search notifications are wishlist-only, and wishlist is excluded",
                "plugin_boundary": "documented outgoing search hooks expose no wire token and repeat reuses the processed request",
                "recently_closed_boundary": "restore payload is logical search data and creates a new search rather than retaining a wire token",
                "unsupported_extension_boundary": "third-party code importing internal dictionaries cannot be enumerated or guaranteed",
                "packet_split": "ordinary rekey mechanics and wishlist product semantics are now separate packets",
                "selected_patch": None,
            },
            "source_invariants": {
                "passed": sum(row["status"] == "pass" for row in invariants),
                "total": len(invariants),
            },
            "consumer_inventory": {
                "closed": sum(row["blocker"] == "no" for row in inventory),
                "open": sum(row["blocker"] == "yes" for row in inventory),
                "total": len(inventory),
            },
            "artifact_tests": {
                "passed": sum(row["passed"] for row in tests),
                "failed": sum(not row["passed"] for row in tests),
                "total": len(tests),
                "returncode": test_result.returncode,
            },
            "compile_checks": {
                "passed": sum(row["status"] == "pass" for row in compile_rows),
                "total": len(compile_rows),
            },
            "upstream_unit_evidence_reuse": reuse_summary,
            "runtime_environment_cleanup": cleanup,
            "errors": errors,
        }

        write_csv(ROOT / f"data/{REVISION}_search_consumer_source_invariants.csv", invariants,
                  fields=("check_id", "state", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_consumer_inventory.csv", inventory,
                  fields=("consumer", "path", "token_role", "ordinary_rekey_effect", "blocker", "status"))
        write_csv(ROOT / f"data/{REVISION}_search_consumer_test_matrix.csv", tests,
                  fields=("nodeid", "name", "outcome", "passed", "status", "duration", "detail"))
        write_csv(ROOT / f"data/{REVISION}_search_consumer_compile_matrix.csv", compile_rows,
                  fields=("path", "status", "detail"))
        write_csv(ROOT / f"data/{REVISION}_evidence_reuse_checks.csv", reuse_rows,
                  fields=("lane", "check_id", "status", "detail"))
        write_json(ROOT / f"data/{REVISION}_evidence_reuse.json", reuse_summary)
        write_json(ROOT / f"data/{REVISION}_search_consumer_summary.json", result)
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true", help="retained for current-tool CLI consistency")
    args = parser.parse_args()
    try:
        result = run(args.source_zip)
    except Exception as exc:  # bounded audit tool: preserve one machine-readable failure
        result = {"revision": REVISION, "status": "fail", "errors": [f"{type(exc).__name__}: {exc}"]}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
