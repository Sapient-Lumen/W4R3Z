#!/usr/bin/env python3
"""Validate a bounded same-page fresh-token Search Again experiment.

Research-only. The probe applies the candidate patch to a clean bundled master
proxy, classifies state ownership, runs model/source/core regressions, and keeps
wishlist seen-history policy explicitly unresolved.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import ast
import json
import shutil
import sys
import time
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable

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
EXECUTABLE_SOURCE_REF = LANE_HEADS[LANE]
PUBLIC_SOURCE_REF = PUBLIC_SOURCE_REFS[LANE]
ARTIFACTS = ROOT / "maintainer_artifacts/search-rekey-01"
PATCH = ARTIFACTS / "search_again_fresh_token_rekey.patch"
RUNTIME = ROOT / f"evidence/{REVISION}-search-rekey-runtime"
OUTPUT_SUMMARY = ROOT / f"data/{REVISION}_search_rekey_summary.json"
OUTPUT_INVARIANTS = ROOT / f"data/{REVISION}_search_rekey_source_invariants.csv"
OUTPUT_TESTS = ROOT / f"data/{REVISION}_search_rekey_test_matrix.csv"
OUTPUT_UNITS = ROOT / f"data/{REVISION}_search_rekey_unit_matrix.csv"
OUTPUT_COMPILE = ROOT / f"data/{REVISION}_search_rekey_compile_matrix.csv"
OUTPUT_OWNERSHIP = ROOT / f"data/{REVISION}_search_rekey_state_ownership.csv"
OUTPUT_POLICY = ROOT / f"data/{REVISION}_search_rekey_policy_matrix.csv"
OUTPUT_RUNTIME_WRITES = ROOT / f"data/{REVISION}_search_rekey_runtime_writes.csv"
OUTPUT_ENVIRONMENT_WRITES = ROOT / f"data/{REVISION}_search_rekey_environment_writes.csv"
EXPECTED_CHANGED_FILES = {
    "pynicotine/events.py",
    "pynicotine/search.py",
    "pynicotine/gtkgui/search.py",
}
TEST_LANES = {
    "model": ("test_rekey_model.py",),
    "source-and-gui": ("test_source_contract.py", "test_gui_rekey_prototype.py"),
    "core-and-network": ("test_core_rekey_prototype.py", "test_core_network_integration.py"),
}
EXPECTED_ARTIFACT_TESTS = 28


def lane_head(source_zip: Path, lane: str) -> str:
    suffix = f"git-full/.git/worktrees/{lane}/HEAD"
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


def files_modified_since(root: Path, marker_ns: int) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.stat().st_mtime_ns >= marker_ns
    }


def changed_files(before: Path, after: Path) -> set[str]:
    relative_paths = {
        path.relative_to(before).as_posix()
        for path in before.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    relative_paths.update(
        path.relative_to(after).as_posix()
        for path in after.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    return {
        relative
        for relative in relative_paths
        if not (before / relative).is_file()
        or not (after / relative).is_file()
        or (before / relative).read_bytes() != (after / relative).read_bytes()
    }


def source_invariants(
    baseline: Path, patched: Path, source_zip: Path, patch_apply_ok: bool, changed: set[str]
) -> list[dict[str, str]]:
    base_core = baseline / "pynicotine/search.py"
    base_gui = baseline / "pynicotine/gtkgui/search.py"
    patch_core = patched / "pynicotine/search.py"
    patch_gui = patched / "pynicotine/gtkgui/search.py"
    base_again = method_source(base_gui, "Search", "on_search_again")
    base_dispatch = method_source(base_gui, "Searches", "file_search_response")
    base_clear = method_source(base_gui, "Search", "clear_model")
    patched_repeat = method_source(patch_core, "Search", "repeat_search")
    patched_send = method_source(patch_core, "Search", "send_search_request")
    patched_rekey = method_source(patch_gui, "Searches", "rekey_search")
    patched_reset = method_source(patch_gui, "Search", "reset_for_search_again")
    patched_again = method_source(patch_gui, "Search", "on_search_again")
    patched_response = method_source(patch_gui, "Search", "file_search_response")
    patch_events = (patched / "pynicotine/events.py").read_text(encoding="utf-8")
    patch_gui_full = patch_gui.read_text(encoding="utf-8")
    wishlist = (baseline / "pynicotine/gtkgui/dialogs/wishlist.py").read_text(encoding="utf-8")
    cap_check = 'page.num_results_found >= config.sections["searches"]["max_displayed_results"]'

    raw: list[tuple[str, bool, str]] = [
        ("source bundle passes content contract", inspect_bundle(source_zip).status == "pass", source_zip.name),
        ("bundled master lane head matches source contract", lane_head(source_zip, LANE) == EXECUTABLE_SOURCE_REF, EXECUTABLE_SOURCE_REF),
        ("candidate patch applies to a clean extraction", patch_apply_ok, PATCH.relative_to(ROOT).as_posix()),
        ("candidate changes exactly three upstream files", changed == EXPECTED_CHANGED_FILES, ", ".join(sorted(changed))),
        ("baseline Search Again reuses page token", "core.search.send_search_request(self.token)" in base_again, "same-token Retry/Merge"),
        ("baseline cap gate precedes page dispatch", base_dispatch.index(cap_check) < base_dispatch.rindex("page.file_search_response(msg)"), "pre-page cap gate"),
        ("baseline cap gate retires the token", "core.search.remove_allowed_token(msg.token)" in base_dispatch, "dead at cap"),
        ("existing clear primitive resets result count", "self.num_results_found = 0" in base_clear, "capacity reset primitive"),
        ("existing clear primitive clears user and folder dedupe", "self.users.clear()" in base_clear and "self.folders.clear()" in base_clear, "dedupe reset"),
        ("wishlist has explicit Reset Seen Results action", '_(' + '"Reset Seen Results"' + ')' in wishlist and "search.ignored_users.clear()" in wishlist, "separate persistent-state policy"),
        ("wishlist response admission consults persistent seen users", "username in search.ignored_users" in base_core.read_text(encoding="utf-8"), "seen-user response suppression"),
        ("wishlist seen users are recorded only when the result tab becomes read", "search.ignored_users.add(username)" in base_gui.read_text(encoding="utf-8"), "unread rows are intentionally not yet seen"),
        ("rekey event is registered", '"rekey-search"' in patch_events and '("rekey-search", self.rekey_search)' in patch_gui_full, "core-to-GUI event"),
        ("repeat rejects missing and wishlist searches", "search is None or isinstance(search, WishSearchRequest)" in patched_repeat, "scope boundary"),
        ("old network admission is removed before core rekey", patched_repeat.index("self.remove_allowed_token(token)") < patched_repeat.index("del self.searches[token]"), "old-token barrier"),
        ("old self-search suppression token is retired", "self._own_tokens.discard(token)" in patched_repeat, "self-search bookkeeping"),
        ("fresh token is allocated before request-object rekey", patched_repeat.index("increment_token") < patched_repeat.index("search.token = new_token"), "fresh epoch"),
        ("same core request object is re-keyed", "search.token = new_token" in patched_repeat and "self.searches[new_token] = search" in patched_repeat, "processed request preserved"),
        ("core map is re-keyed before GUI event", patched_repeat.index("self.searches[new_token] = search") < patched_repeat.index('events.emit("rekey-search"'), "core authority first"),
        ("GUI event precedes new request dispatch", patched_repeat.index('events.emit("rekey-search"') < patched_repeat.index("self.send_search_request(new_token)"), "page reset before request enqueue"),
        ("new admission precedes mode dispatch", patched_send.index("self.add_allowed_token(token)") < patched_send.index("if search.mode"), "new-token admission"),
        ("GUI lookup key changes without page replacement", "self.pages.clear()" in patched_rekey and "self.pages.update(pages)" in patched_rekey and "self.remove_page" not in patched_rekey and "self.create_page" not in patched_rekey, "same page object"),
        ("GUI mapping is updated before page token/reset", patched_rekey.index("self.pages.update(pages)") < patched_rekey.index("page.token = new_token") < patched_rekey.index("page.reset_for_search_again()"), "no new-token/old-key callback window"),
        ("tab order is reconstructed in insertion order", "for token, search_page in self.pages.items()" in patched_rekey, "ordered dict rekey"),
        ("result-generation state is cleared", "self.clear_model(stored_results=True)" in patched_reset, "rows, count, users, folders, tree"),
        ("selection state is cleared", "self.selected_results.clear()" in patched_reset and "self.selected_users.clear()" in patched_reset, "stale iterators removed"),
        ("reset does not rewrite filters or grouping", all(term not in patched_reset for term in ("self.filters =", "self.grouping_mode =", "self.sort")), "view controls retained"),
        ("offline guard precedes destructive rekey", patched_again.index("status == UserStatus.OFFLINE") < patched_again.index("core.search.repeat_search(self.token)"), "offline page preserved"),
        ("wishlist retains explicit same-token branch", 'if self.mode == "wishlist":' in patched_again and "core.search.send_search_request(self.token)" in patched_again, "wishlist unresolved"),
        ("online paths retain post-send status recheck", patched_again.rindex("self.show_error_message()") > patched_again.index("core.search.repeat_search(self.token)"), "disconnect-race feedback"),
        ("prototype retains no old-token alias table", "search_token_aliases" not in patch_core.read_text(encoding="utf-8") and "search_token_aliases" not in patch_gui_full, "bounded state"),
        ("desktop result notifications are wishlist-only", patched_response.rfind("if tab_changed and is_wish:", 0, patched_response.index("core.notifications.show_search_notification(")) >= 0, "no ordinary-search stale notification token"),
    ]
    return [
        {"invariant": name, "status": "pass" if passed else "fail", "detail": detail}
        for name, passed, detail in raw
    ]


def ownership_rows() -> list[dict[str, str]]:
    return [
        {"state": "wire response token", "owner": "core Search.token / SearchRequest.token", "ordinary rekey": "allocate fresh; update same request object", "wishlist": "unchanged", "evidence": "core and model tests"},
        {"state": "parser admission", "owner": "network thread allowed-response set", "ordinary rekey": "remove old, then add new", "wishlist": "re-add same token", "evidence": "network-message order integration"},
        {"state": "already-parsed old response", "owner": "main-thread core search lookup", "ordinary rekey": "old key absent; msg.token becomes None", "wishlist": "same epoch remains", "evidence": "core stale-response test"},
        {"state": "self-search suppression", "owner": "Search._own_tokens", "ordinary rekey": "discard old; sender records current new token", "wishlist": "not applicable", "evidence": "core test and source invariant"},
        {"state": "GUI page lookup", "owner": "Searches.pages / Search.token", "ordinary rekey": "change key in-place; preserve insertion order", "wishlist": "unchanged", "evidence": "GUI method test"},
        {"state": "rows and dedupe", "owner": "all_data, users, folders, tree, counters", "ordinary rekey": "clear", "wishlist": "preserve current Retry/Merge", "evidence": "clear_model source and GUI test"},
        {"state": "selection", "owner": "selected_results / selected_users", "ordinary rekey": "clear stale iterators", "wishlist": "preserve", "evidence": "GUI reset test"},
        {"state": "view controls", "owner": "filters, grouping, sort, widgets", "ordinary rekey": "preserve", "wishlist": "preserve", "evidence": "same-object GUI/model tests"},
        {"state": "tab identity and order", "owner": "existing page/container and pages order", "ordinary rekey": "preserve; mark read", "wishlist": "preserve", "evidence": "GUI mapping-order test"},
        {"state": "recently-closed undo", "owner": "page removal path", "ordinary rekey": "no entry created", "wishlist": "no entry", "evidence": "no remove_page plus model test"},
        {"state": "room/user audience", "owner": "same SearchRequest room/users fields", "ordinary rekey": "preserve", "wishlist": "not applicable", "evidence": "request identity and user-audience integration"},
        {"state": "buddy audience", "owner": "live buddy list at send time", "ordinary rekey": "re-resolve live audience", "wishlist": "not applicable", "evidence": "current send path"},
        {"state": "wishlist seen history", "owner": "WishSearchRequest.ignored_users", "ordinary rekey": "not applicable", "wishlist": "policy unresolved; explicit reset exists", "evidence": "wishlist source and tests"},
        {"state": "desktop notification routing", "owner": "wishlist-only result notification", "ordinary rekey": "no aliases needed", "wishlist": "token unchanged", "evidence": "source contract test"},
    ]


def policy_rows() -> list[dict[str, str]]:
    return [
        {"policy": "current same-token Retry/Merge", "cap recovery": "no", "late old response isolation": "no", "page/view preservation": "yes", "wishlist semantics": "preserved", "network acknowledgement": "none", "disposition": "confirmed current defect at cap"},
        {"policy": "same-token clear", "cap recovery": "yes", "late old response isolation": "no", "page/view preservation": "yes", "wishlist semantics": "requires seen-history choice", "network acknowledgement": "none", "disposition": "rejected counterexample"},
        {"policy": "fresh-token page replacement", "cap recovery": "yes", "late old response isolation": "yes", "page/view preservation": "requires migration", "wishlist semantics": "requires seen-history choice", "network acknowledgement": "none under best-effort semantics", "disposition": "viable but not minimum for ordinary searches"},
        {"policy": "fresh-token same-page ordinary rekey", "cap recovery": "yes", "late old response isolation": "yes", "page/view preservation": "yes", "wishlist semantics": "excluded", "network acknowledgement": "none under existing best-effort semantics", "disposition": "mechanically viable research prototype"},
        {"policy": "failure-atomic in-place refresh", "cap recovery": "yes", "late old response isolation": "yes", "page/view preservation": "yes", "wishlist semantics": "requires policy", "network acknowledgement": "required with disconnect/replay contract", "disposition": "optional stronger design, not minimum"},
        {"policy": "wishlist rekey; clear rows; preserve ignored_users", "cap recovery": "yes", "late old response isolation": "yes", "page/view preservation": "yes", "wishlist semantics": "can discard unread/unseen rows before they enter seen history", "network acknowledgement": "not inherently", "disposition": "rejected as an implicit command"},
        {"policy": "wishlist rekey; clear rows and ignored_users", "cap recovery": "yes", "late old response isolation": "yes", "page/view preservation": "yes", "wishlist semantics": "silently duplicates explicit Reset Seen Results and replays seen users", "network acknowledgement": "not inherently", "disposition": "rejected as an implicit command"},
        {"policy": "wishlist keep Retry/Merge plus explicit Reset Seen Results", "cap recovery": "no", "late old response isolation": "no", "page/view preservation": "yes", "wishlist semantics": "preserves current seen/unseen contract", "network acknowledgement": "none", "disposition": "safest current behavior; wording/product decision remains"},
        {"policy": "wishlist explicit destructive Refresh", "cap recovery": "yes", "late old response isolation": "yes", "page/view preservation": "yes", "wishlist semantics": "must define unread-row handling and seen-history reset separately", "network acknowledgement": "not inherently", "disposition": "open product-policy branch"},
    ]


def compile_rows() -> list[dict[str, str]]:
    paths = sorted(ARTIFACTS.glob("*.py"))
    paths.extend([
        ROOT / f"tools/probe_{REVISION}_search_rekey.py",
        ROOT / "tools/source_bundle_locator.py",
        ROOT / "tools/audit_current_source_contract.py",
        ROOT / "tools/audit_current_source_history.py",
        ROOT / "tools/run_pytest_forced_exit.py",
        ROOT / f"tools/run_{REVISION}_unit_lane.py",
    ])
    rows: list[dict[str, str]] = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        try:
            compile(path.read_text(encoding="utf-8"), relative, "exec")
        except Exception as exc:  # pragma: no cover
            rows.append({"path": relative, "status": "fail", "detail": f"{type(exc).__name__}: {exc}"})
        else:
            rows.append({"path": relative, "status": "pass", "detail": "compiled"})
    return rows


def run_pytest_lane(
    lane: str,
    files: Iterable[str],
    *,
    baseline: Path,
    patched: Path,
) -> tuple[Any, list[dict[str, Any]], dict[str, Any]]:
    runtime = RUNTIME / f"artifact-{lane}"
    runtime.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"{REVISION}-{lane}-environment-", dir="/mnt/data"))
    environment_root = scratch / "environment"
    python_paths = [ARTIFACTS]
    if lane == "core-and-network":
        python_paths.insert(0, patched)
    env, cwd = isolated_environment(
        environment_root,
        python_paths=python_paths,
        inherit={
            "NICOTINE_BASE_SOURCE_ROOT": str(baseline),
            "NICOTINE_PATCH_SOURCE_ROOT": str(patched),
        },
    )
    junit = runtime / "junit.xml"
    environment_cleanup: dict[str, Any] = {}
    try:
        result = run_bounded(
            [
                sys.executable, str(ROOT / "tools/run_pytest_forced_exit.py"), "-q", "-p", "no:cacheprovider",
                *(str(ARTIFACTS / name) for name in files),
                f"--junitxml={junit}",
            ],
            cwd=cwd,
            env=env,
            timeout=180,
            output_path=runtime / "pytest.log",
        )
        rows = parse_junit_report(junit) if junit.is_file() else []
    finally:
        try:
            environment_cleanup = purge_isolated_environment(environment_root)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    for row in rows:
        row["lane"] = lane
    return result, rows, environment_cleanup


def clone_source_tree(source: Path, destination: Path, label: str) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    result = run_bounded(
        ["cp", "-a", "--reflink=auto", f"{source}/.", str(destination)],
        cwd=destination.parent,
        timeout=60,
        output_path=RUNTIME / f"clone-{label}.log",
    )
    if result.returncode != 0:
        raise RuntimeError(f"source clone failed for {label}: {result.stdout}")


def artifact_metrics(path: Path) -> dict[str, int]:
    files = [item for item in path.iterdir() if item.is_file()]
    return {
        "files": len(files),
        "bytes": sum(item.stat().st_size for item in files),
        "lines": sum(len(item.read_text(encoding="utf-8").splitlines()) for item in files),
    }


def load_prevalidated_unit_lane(
    label: str, source_zip: Path
) -> tuple[Any, list[dict[str, Any]], list[str], list[str], list[str], dict[str, Any]]:
    """Load and verify one expensive unit lane before reusing its JUnit rows."""
    result_path = ROOT / f"data/{REVISION}_search_rekey_unit_{label}.json"
    errors: list[str] = []
    if not result_path.is_file():
        return None, [], [], [f"missing unit evidence: {result_path.relative_to(ROOT)}"], [], {}
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [], [], [f"invalid unit evidence {label}: {exc}"], [], {}

    source = payload.get("source", {})
    tests = payload.get("tests", {})
    candidate = payload.get("candidate_patch", {})
    isolation = payload.get("source_isolation", {})
    environment_cleanup = payload.get("runtime_environment_cleanup", {})
    if not isinstance(environment_cleanup, dict):
        environment_cleanup = {}
    environment_entries = environment_cleanup.get("entries", [])
    if not isinstance(environment_entries, list):
        environment_entries = []
    inspection = inspect_bundle(source_zip)
    expected_patch = sha256_path(PATCH) if label == "patched" else None
    checks = [
        (payload.get("revision") == REVISION, "revision mismatch"),
        (payload.get("status") == "pass", "recorded status is not pass"),
        (payload.get("lane") == label, "lane label mismatch"),
        (payload.get("evidence_mode") == "bounded-disposable-source-lane", "evidence mode mismatch"),
        (source.get("bundle_sha256") == inspection.sha256, "source bundle digest mismatch"),
        (source.get("lane") == LANE, "source lane mismatch"),
        (source.get("executable_source_ref") == EXECUTABLE_SOURCE_REF, "source ref mismatch"),
        (candidate.get("sha256") == expected_patch, "candidate patch digest mismatch"),
        (candidate.get("applied") is (label == "patched"), "candidate patch application mismatch"),
        (isolation.get("dedicated_extraction") is True, "unit source was not dedicated"),
        (isolation.get("source_extraction_cleaned_after_run") is True, "unit source cleanup not recorded"),
        (isolation.get("isolated_environment_cleaned_after_run") is True, "unit environment cleanup not recorded"),
        (isolation.get("cleaned_after_run") is True, "combined cleanup not recorded"),
        (isolation.get("shared_with_other_test_lanes") is False, "unit source was shared"),
        (environment_cleanup.get("residual_directories") == [], "unit environment has residual directories"),
        (environment_cleanup.get("entry_count") == len(environment_entries), "unit environment write count mismatch"),
        (environment_cleanup.get("bytes") == sum(int(row.get("bytes", 0)) for row in environment_entries if isinstance(row, dict)), "unit environment write byte count mismatch"),
        (tests.get("returncode") == 0, "pytest return code is not zero"),
        (tests.get("failed") == 0 and tests.get("error") == 0, "recorded unit failures"),
        (tests.get("total") == 61, "unit total is not 61"),
    ]
    errors.extend(f"{label} unit evidence: {detail}" for passed, detail in checks if not passed)

    junit_info = payload.get("junit", {})
    junit_value = junit_info.get("path")
    junit = ROOT / junit_value if isinstance(junit_value, str) else Path()
    if not isinstance(junit_value, str) or not junit.is_file():
        errors.append(f"{label} unit evidence: JUnit report missing")
        rows: list[dict[str, Any]] = []
    else:
        if sha256_path(junit) != junit_info.get("sha256"):
            errors.append(f"{label} unit evidence: JUnit digest mismatch")
        rows = parse_junit_report(junit)
        for row in rows:
            row["lane"] = label
        outcomes = {
            outcome: sum(row["outcome"] == outcome for row in rows)
            for outcome in ("passed", "skipped", "failed", "error")
        }
        for key, observed in outcomes.items():
            if observed != tests.get(key):
                errors.append(
                    f"{label} unit evidence: JUnit {key}={observed}, JSON={tests.get(key)}"
                )
        if len(rows) != tests.get("total"):
            errors.append(
                f"{label} unit evidence: JUnit rows={len(rows)}, JSON={tests.get('total')}"
            )

    class RecordedRun:
        returncode = int(tests.get("returncode", 1))

    exclusions = payload.get("excluded") if isinstance(payload.get("excluded"), list) else []
    writes = payload.get("source_tree_final_writes")
    return (
        RecordedRun(),
        rows,
        exclusions,
        errors,
        writes if isinstance(writes, list) else [],
        environment_cleanup,
    )


def run_probe(source_zip: Path) -> dict[str, Any]:
    # Preserve separately generated expensive-unit evidence while rebuilding all
    # lightweight artifacts from clean source states.
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for child in list(RUNTIME.iterdir()):
        if child.name == "prevalidated-units":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    work = RUNTIME / "source-states"
    work.mkdir(parents=True)

    baseline = work / "baseline-template"
    patched = work / "patched-template"
    member = archive_member_name(LANE)
    baseline_files = safe_extract_tar_gz_member(source_zip, member, baseline)
    clone_source_tree(baseline, patched, "patched-template")
    patched_files = baseline_files
    for source_root in (baseline, patched):
        expected = source_root / "pynicotine/gtkgui/search.py"
        if not expected.is_file():
            raise RuntimeError(f"source extraction is incomplete: {expected}")

    patch_marker_ns = time.time_ns()
    patch_check = run_bounded(
        ["git", "apply", "--check", str(PATCH)], cwd=patched, timeout=60,
        output_path=RUNTIME / "patch-check.log",
    )
    patch_apply = run_bounded(
        ["git", "apply", str(PATCH)], cwd=patched, timeout=60,
        output_path=RUNTIME / "patch-apply.log",
    ) if patch_check.returncode == 0 else patch_check
    patch_apply_ok = patch_check.returncode == 0 and patch_apply.returncode == 0
    patch_changed_files = files_modified_since(patched, patch_marker_ns)

    patched_core = work / "patched-core"
    clone_source_tree(patched, patched_core, "patched-core")
    runtime_marker_ns = time.time_ns()

    with ThreadPoolExecutor(max_workers=3) as executor:
        artifact_futures = {
            "model": executor.submit(run_pytest_lane, "model", TEST_LANES["model"], baseline=baseline, patched=patched),
            "source-and-gui": executor.submit(run_pytest_lane, "source-and-gui", TEST_LANES["source-and-gui"], baseline=baseline, patched=patched),
            "core-and-network": executor.submit(run_pytest_lane, "core-and-network", TEST_LANES["core-and-network"], baseline=baseline, patched=patched_core),
        }
        invariants = source_invariants(baseline, patched, source_zip, patch_apply_ok, patch_changed_files)
        compiles = compile_rows()
        artifact_rows: list[dict[str, Any]] = []
        artifact_runs: dict[str, Any] = {}
        artifact_environment_cleanups: dict[str, dict[str, Any]] = {}
        for lane in TEST_LANES:
            run, rows, cleanup = artifact_futures[lane].result()
            artifact_runs[lane] = run
            artifact_environment_cleanups[lane] = cleanup
            artifact_rows.extend(rows)

    (
        baseline_run, baseline_units, exclusions, baseline_evidence_errors,
        baseline_writes, baseline_environment_cleanup,
    ) = load_prevalidated_unit_lane("baseline", source_zip)
    (
        patched_run, patched_units, patched_exclusions, patched_evidence_errors,
        patched_writes, patched_environment_cleanup,
    ) = load_prevalidated_unit_lane("patched", source_zip)
    unit_rows = baseline_units + patched_units
    core_writes = files_modified_since(patched_core, runtime_marker_ns)

    runtime_write_rows: list[dict[str, str]] = []
    if not core_writes:
        runtime_write_rows.append({"lane": "core-and-network", "path": "(none)", "classification": "no persistent source-tree writes"})
    else:
        runtime_write_rows.extend({"lane": "core-and-network", "path": path, "classification": "unexpected source-tree write"} for path in sorted(core_writes))
    for lane, paths in (("baseline-units", baseline_writes), ("patched-units", patched_writes)):
        if not paths:
            runtime_write_rows.append({"lane": lane, "path": "(none)", "classification": "dedicated extraction; no final source-tree writes; extraction removed"})
        else:
            runtime_write_rows.extend({"lane": lane, "path": path, "classification": "lane-local final source-tree write; extraction removed"} for path in paths)

    environment_cleanups = {
        **{f"artifact-{lane}": cleanup for lane, cleanup in artifact_environment_cleanups.items()},
        "baseline-units": baseline_environment_cleanup,
        "patched-units": patched_environment_cleanup,
    }
    environment_write_rows: list[dict[str, Any]] = []
    for lane, cleanup in environment_cleanups.items():
        entries = cleanup.get("entries", []) if isinstance(cleanup, dict) else []
        if not entries:
            environment_write_rows.append({
                "lane": lane, "path": "(none)", "kind": "none", "bytes": 0, "sha256": "",
                "classification": "no transient environment files; isolated roots removed",
            })
            continue
        for row in entries:
            environment_write_rows.append({
                "lane": lane,
                "path": row.get("path", ""),
                "kind": row.get("kind", ""),
                "bytes": row.get("bytes", 0),
                "sha256": row.get("sha256", ""),
                "classification": "digest-only ledger; transient entry removed",
            })

    errors: list[str] = baseline_evidence_errors + patched_evidence_errors
    failed_invariants = [row["invariant"] for row in invariants if row["status"] != "pass"]
    if failed_invariants:
        errors.append(f"source invariants failed: {failed_invariants}")
    failed_compiles = [row["path"] for row in compiles if row["status"] != "pass"]
    if failed_compiles:
        errors.append(f"compile checks failed: {failed_compiles}")
    artifact_failed = sum(row["outcome"] in {"failed", "error"} for row in artifact_rows)
    if len(artifact_rows) != EXPECTED_ARTIFACT_TESTS or artifact_failed:
        errors.append(f"artifact tests rows={len(artifact_rows)}, failed={artifact_failed}, expected={EXPECTED_ARTIFACT_TESTS}")
    for lane, run in artifact_runs.items():
        if run.returncode != 0:
            errors.append(f"artifact lane {lane} returncode={run.returncode}")
    baseline_failed = sum(row["outcome"] in {"failed", "error"} for row in baseline_units)
    patched_failed = sum(row["outcome"] in {"failed", "error"} for row in patched_units)
    if baseline_run is None or baseline_run.returncode != 0 or baseline_failed:
        errors.append(f"baseline units rc={getattr(baseline_run, 'returncode', None)}, failed={baseline_failed}")
    if patched_run is None or patched_run.returncode != 0 or patched_failed:
        errors.append(f"patched units rc={getattr(patched_run, 'returncode', None)}, failed={patched_failed}")
    if len(baseline_units) != len(patched_units):
        errors.append(f"unit row count drift: baseline={len(baseline_units)}, patched={len(patched_units)}")
    if exclusions != patched_exclusions:
        errors.append("baseline/patched unit exclusion drift")
    if core_writes:
        errors.append(f"core/network source writes: {sorted(core_writes)}")
    cleanup_residuals = {
        lane: cleanup.get("residual_directories", ["invalid-cleanup-record"])
        for lane, cleanup in environment_cleanups.items()
        if not isinstance(cleanup, dict) or cleanup.get("residual_directories")
    }
    if cleanup_residuals:
        errors.append(f"runtime environment cleanup residuals: {cleanup_residuals}")

    archived = ROOT / "docs/archive/rev0080-active-search-repeat-01"
    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "disposition": "open-wishlist-policy-and-native-ui-validation",
        "selected_patch": None,
        "candidate_patch": PATCH.relative_to(ROOT).as_posix(),
        "source": {
            "bundle": source_zip.name,
            "bundle_sha256": inspect_bundle(source_zip).sha256,
            "lane": LANE,
            "executable_source_ref": EXECUTABLE_SOURCE_REF,
            "public_source_ref": PUBLIC_SOURCE_REF,
            "extracted_files_per_template": {"baseline": baseline_files, "patched": patched_files},
            "scope": "executable tests use bundled proxy; current public-flow review is separate",
        },
        "findings": {
            "architecture_correction": "ordinary searches can use a same-page fresh-token rekey; page replacement is not the minimum best-effort design",
            "late_response_boundary": "old parser admission is removed and any already-parsed old response is rejected by the missing old core lookup key",
            "capacity_boundary": "clearing result-derived state under a fresh token restores display capacity without accepting delayed prior-epoch rows",
            "wishlist_boundary": "ignored_users is persistent wishlist domain state with a separate Reset Seen Results action; automatic preserve/reset remains product policy",
            "acknowledgement_boundary": "network-applied acknowledgement is needed only for stronger failure-atomic semantics, not existing best-effort new-search semantics",
            "probe_isolation_correction": "HOME/XDG isolation alone was insufficient because mutable unit lanes can write inside source; bounded lanes now use independent disposable extractions",
            "runtime_evidence_correction": "transient HOME/XDG/TMP/CWD files are reduced to a digest ledger and removed before packaging",
            "selected_implementation": None,
        },
        "artifact_tests": {
            "passed": sum(row["outcome"] == "passed" for row in artifact_rows),
            "failed": artifact_failed,
            "total": len(artifact_rows),
            "lanes": {lane: {"returncode": artifact_runs[lane].returncode, "tests": sum(row["lane"] == lane for row in artifact_rows)} for lane in TEST_LANES},
        },
        "source_invariants": {"passed": sum(row["status"] == "pass" for row in invariants), "total": len(invariants)},
        "compile_checks": {"passed": sum(row["status"] == "pass" for row in compiles), "total": len(compiles)},
        "upstream_units": {
            "evidence_mode": "prevalidated-bounded-disposable-source-lanes",
            "baseline": {"passed": sum(row["outcome"] == "passed" for row in baseline_units), "skipped": sum(row["outcome"] == "skipped" for row in baseline_units), "failed": baseline_failed, "total": len(baseline_units), "returncode": getattr(baseline_run, "returncode", None)},
            "patched": {"passed": sum(row["outcome"] == "passed" for row in patched_units), "skipped": sum(row["outcome"] == "skipped" for row in patched_units), "failed": patched_failed, "total": len(patched_units), "returncode": getattr(patched_run, "returncode", None)},
            "excluded": exclusions,
        },
        "runtime_source_writes": {"core-and-network": sorted(core_writes), "baseline-units-final": baseline_writes, "patched-units-final": patched_writes},
        "runtime_environment_hygiene": {
            "lanes": len(environment_cleanups),
            "removed_directories": sum(len(cleanup.get("removed_directories", [])) for cleanup in environment_cleanups.values()),
            "written_entries_recorded": sum(int(cleanup.get("entry_count", 0)) for cleanup in environment_cleanups.values()),
            "regular_files_recorded": sum(int(cleanup.get("regular_files", 0)) for cleanup in environment_cleanups.values()),
            "symlinks_recorded": sum(int(cleanup.get("symlinks", 0)) for cleanup in environment_cleanups.values()),
            "written_bytes_recorded": sum(int(cleanup.get("bytes", 0)) for cleanup in environment_cleanups.values()),
            "residual_directories": sum(len(cleanup.get("residual_directories", [])) for cleanup in environment_cleanups.values()),
            "packaged_transient_files": 0,
        },
        "artifact_refactor": {"archived_rev0080": artifact_metrics(archived) if archived.is_dir() else None, "active_rev0081": artifact_metrics(ARTIFACTS)},
        "errors": errors,
        "_rows": {"invariants": invariants, "tests": artifact_rows, "units": unit_rows, "compiles": compiles, "ownership": ownership_rows(), "policy": policy_rows(), "runtime_writes": runtime_write_rows, "environment_writes": environment_write_rows},
    }
    shutil.rmtree(work, ignore_errors=True)
    return result

def write_outputs(result: dict[str, Any]) -> None:
    rows = result.pop("_rows")
    write_json(OUTPUT_SUMMARY, result)
    write_csv(OUTPUT_INVARIANTS, rows["invariants"], fields=("invariant", "status", "detail"))
    write_csv(OUTPUT_TESTS, rows["tests"], fields=("lane", "nodeid", "name", "outcome", "passed", "duration", "detail"))
    write_csv(OUTPUT_UNITS, rows["units"], fields=("lane", "nodeid", "name", "outcome", "passed", "duration", "detail"))
    write_csv(OUTPUT_COMPILE, rows["compiles"], fields=("path", "status", "detail"))
    write_csv(OUTPUT_OWNERSHIP, rows["ownership"], fields=("state", "owner", "ordinary rekey", "wishlist", "evidence"))
    write_csv(OUTPUT_POLICY, rows["policy"], fields=("policy", "cap recovery", "late old response isolation", "page/view preservation", "wishlist semantics", "network acknowledgement", "disposition"))
    write_csv(OUTPUT_RUNTIME_WRITES, rows["runtime_writes"], fields=("lane", "path", "classification"))
    write_csv(OUTPUT_ENVIRONMENT_WRITES, rows["environment_writes"], fields=("lane", "path", "kind", "bytes", "sha256", "classification"))
    lines = [
        f"# {REVISION} Search Again same-page re-key probe", "", f"Status: **{result['status']}**", "", "```text",
        f"classified tests: {result['artifact_tests']['passed']}/{result['artifact_tests']['total']}",
        f"source invariants: {result['source_invariants']['passed']}/{result['source_invariants']['total']}",
        f"compile checks: {result['compile_checks']['passed']}/{result['compile_checks']['total']}",
        f"baseline units: {result['upstream_units']['baseline']['passed']} passed, {result['upstream_units']['baseline']['skipped']} skipped",
        f"patched units: {result['upstream_units']['patched']['passed']} passed, {result['upstream_units']['patched']['skipped']} skipped",
        f"runtime environment entries reduced to digest rows: {result['runtime_environment_hygiene']['written_entries_recorded']}",
        f"runtime environment residual directories: {result['runtime_environment_hygiene']['residual_directories']}",
        f"selected patch: {result['selected_patch']}", "```", "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in result["errors"]])
    (ROOT / f"evidence/{REVISION}-search-rekey-probe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
