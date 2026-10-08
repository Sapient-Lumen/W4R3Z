#!/usr/bin/env python3
"""Validate SEARCH-AGAIN-EPOCH-01 models and source ownership boundaries.

Research-only. This probe selects no production patch. It tests a stable
logical-search identity, replaceable wire epochs, fail-closed main-thread
routing, and an explicit composite network publication contract.
"""
from __future__ import annotations

import argparse
import ast
import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
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
    SourceBundleError,
    inspect_bundle,
    locate_source_bundle,
)

REVISION = "rev0078"
LANE = "github-branch-master"
EXECUTABLE_SOURCE_REF = "f4e17d59783dbc48ea31d2e899a681e2dd1ed500"
PUBLIC_SOURCE_REF = "a96406e7aa285a3fb2a3e35900686d164a22bf02"
ARTIFACTS = ROOT / "maintainer_artifacts/search-epoch-01"
RUNTIME = ROOT / "evidence/rev0078-search-epoch-runtime"
OUTPUT_SUMMARY = ROOT / "data/rev0078_search_epoch_summary.json"
OUTPUT_INVARIANTS = ROOT / "data/rev0078_search_epoch_source_invariants.csv"
OUTPUT_TESTS = ROOT / "data/rev0078_search_epoch_test_matrix.csv"
OUTPUT_COMPILE = ROOT / "data/rev0078_search_epoch_compile_matrix.csv"
OUTPUT_OWNERS = ROOT / "data/rev0078_search_epoch_owner_map.csv"

ARTIFACT_TEST_FILES = (
    "test_search_epoch_transaction.py",
    "test_search_epoch_races.py",
    "test_search_epoch_lifecycle.py",
    "test_search_epoch_queue_contract.py",
    "test_search_epoch_source_ownership.py",
)


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
                if segment is None:
                    break
                return segment
    raise RuntimeError(f"missing {class_name}.{method_name} in {path}")


def source_invariants(source: Path, source_zip: Path) -> list[dict[str, Any]]:
    search_path = source / "pynicotine/search.py"
    gui_path = source / "pynicotine/gtkgui/search.py"
    events_path = source / "pynicotine/events.py"
    core_path = source / "pynicotine/core.py"
    proto_path = source / "pynicotine/slskproto.py"
    messages_path = source / "pynicotine/slskmessages.py"
    search_text = search_path.read_text(encoding="utf-8")
    gui_text = gui_path.read_text(encoding="utf-8")
    core_text = core_path.read_text(encoding="utf-8")
    proto_text = proto_path.read_text(encoding="utf-8")
    events_text = events_path.read_text(encoding="utf-8")
    parse_source = method_source(messages_path, "FileSearchResponse", "parse_network_message")
    queue_source = method_source(proto_path, "NetworkThread", "_queue_network_message")
    disable_queue_source = method_source(proto_path, "NetworkThread", "_disable_message_queue")
    clear_queue_source = method_source(proto_path, "NetworkThread", "_clear_message_queue")
    disconnect_source = method_source(proto_path, "NetworkThread", "_server_disconnect")
    again_source = method_source(gui_path, "Search", "on_search_again")
    response_source = method_source(gui_path, "Searches", "file_search_response")

    slots_line = next(
        line for line in search_text.splitlines()
        if line.strip().startswith("__slots__ = (\"token\"")
    )
    gate_index = parse_source.index("if self.token not in self.allowed_responses:")
    full_decompress = parse_source.rindex("decompressor.decompress")
    cap = response_source.index("if page.num_results_found >=")
    retire = response_source.index("core.search.remove_allowed_token(msg.token)")
    dispatch = response_source.index("page.file_search_response(msg)")

    raw = [
        ("source bundle digest contract", inspect_bundle(source_zip).digest_ok, EXPECTED_SOURCE_SHA256),
        ("bundled master lane head", lane_head(source_zip, LANE) == EXECUTABLE_SOURCE_REF, lane_head(source_zip, LANE)),
        ("SearchRequest has wire token", '"token"' in slots_line, slots_line.strip()),
        ("SearchRequest lacks logical id", "logical" not in slots_line, slots_line.strip()),
        ("core search registry keyed by token", "self.searches[token] = search = SearchRequest(" in search_text, "search.py"),
        ("send path admits token", "self.add_allowed_token(token)" in method_source(search_path, "Search", "send_search_request"), "Search.send_search_request"),
        ("wire fanout uses search token", "UserSearch(username, search.token" in search_text, "search.py"),
        ("GUI page registry keyed by token", "self.pages[token] = page = Search(" in gui_text, "gtkgui/search.py"),
        ("page stores token identity", "self.token = token" in gui_text, "gtkgui/search.py"),
        ("notification target stores token", "str(self.token), self.text" in gui_text, "gtkgui/search.py"),
        ("Search Again reuses page token", "core.search.send_search_request(self.token)" in again_source, again_source.strip()),
        ("Search Again does not clear", "clear_model" not in again_source, again_source.strip()),
        ("page deduplicates username", "if user in self.users:" in method_source(gui_path, "Search", "file_search_response"), "Search.file_search_response"),
        ("clear resets username set", "self.users.clear()" in method_source(gui_path, "Search", "clear_model"), "Search.clear_model"),
        ("main emit is synchronous", "function(*args, **kwargs)" in method_source(events_path, "Events", "emit"), "Events.emit"),
        ("network events are main-thread queued", "self._thread_events.put_nowait" in method_source(events_path, "Events", "emit_main_thread"), "Events.emit_main_thread"),
        ("network queue silent drop branch", "if self._should_process_queue:" in queue_source and "else" not in queue_source, queue_source.strip()),
        ("queue disable clears pending messages", "self._clear_message_queue()" in disable_queue_source and "self._message_queue.get_nowait()" in clear_queue_source, "NetworkThread queue lifecycle"),
        ("disconnect clears response admission", "self._allowed_message_responses.clear()" in disconnect_source, "NetworkThread._server_disconnect"),
        ("control and server messages share queue", core_text.count('events.emit("queue-network-message", message)') >= 2, "core.py"),
        ("network handles add/remove admission", "elif msg_class is AddAllowedResponse:" in proto_text and "elif msg_class is RemoveAllowedResponse:" in proto_text, "slskproto.py"),
        ("token gate precedes full decompression", gate_index < full_decompress, f"gate={gate_index}, full={full_decompress}"),
        ("display cap retires before page dispatch", cap < retire < dispatch, f"cap={cap}, retire={retire}, dispatch={dispatch}"),
        ("event queue cadence documented", "Called by the main loop 10 times per second" in events_text, "events.py"),
    ]
    return [
        {"invariant": name, "status": "pass" if passed else "fail", "detail": detail}
        for name, passed, detail in raw
    ]


def owner_rows() -> list[dict[str, str]]:
    return [
        {"owner": "allocator cursor", "current_identity": "Search.token", "desired_identity": "wire token allocator", "rotation_risk": "none if monotonic"},
        {"owner": "wire request/response capability", "current_identity": "SearchRequest.token", "desired_identity": "wire epoch token", "rotation_risk": "required for late-reply rejection"},
        {"owner": "core search registry", "current_identity": "searches[token]", "desired_identity": "logical search registry plus token route", "rotation_risk": "orphaned lookup if partially rekeyed"},
        {"owner": "network parser admission", "current_identity": "allowed response token", "desired_identity": "wire epoch token", "rotation_risk": "old traffic can parse during control lag"},
        {"owner": "GUI page registry", "current_identity": "pages[token]", "desired_identity": "stable logical search ID", "rotation_risk": "tab disappears under old key"},
        {"owner": "page instance", "current_identity": "page.token", "desired_identity": "logical ID plus current wire token", "rotation_risk": "callbacks send stale token"},
        {"owner": "notification activation", "current_identity": "stringified token", "desired_identity": "stable logical search ID", "rotation_risk": "old notification points nowhere"},
        {"owner": "show/remove API", "current_identity": "token argument", "desired_identity": "logical search ID", "rotation_risk": "close/show targets wrong epoch"},
        {"owner": "self-search response gate", "current_identity": "_own_tokens", "desired_identity": "wire epoch token", "rotation_risk": "must retire with epoch"},
        {"owner": "buddy audience", "current_identity": "live list at each send", "desired_identity": "explicit per-epoch policy", "rotation_risk": "silent snapshot/live mismatch"},
        {"owner": "network queue generation", "current_identity": "queue can disable and clear without an acknowledgement", "desired_identity": "applied acknowledgement or reconnect reconciliation", "rotation_risk": "accepted epoch can disappear before processing"},
    ]


def compile_rows() -> list[dict[str, Any]]:
    paths = [ARTIFACTS / "search_epoch_model.py"]
    paths.extend(ARTIFACTS / name for name in ARTIFACT_TEST_FILES)
    paths.extend([
        ROOT / "tools/cube_runtime.py",
        ROOT / "tools/probe_rev0078_search_epoch.py",
        ROOT / "tools/audit_cube_runtime_adoption.py",
        ROOT / "tools/audit_current_package.py",
        ROOT / "tools/build_current_manifest.py",
        ROOT / "tools/build_current_delta_inventory.py",
        ROOT / "tools/validate_current_packet_dispositions.py",
    ])
    rows: list[dict[str, Any]] = []
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status = "pass"
            detail = ""
        except Exception as exc:  # pragma: no cover - fail-closed artifact check
            status = "fail"
            detail = f"{type(exc).__name__}: {exc}"
        rows.append({
            "path": path.relative_to(ROOT).as_posix(),
            "status": status,
            "detail": detail,
        })
    return rows


def run_probe(source_zip: Path) -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    with tempfile.TemporaryDirectory(prefix="rev0078-search-epoch-") as temp_name:
        temp = Path(temp_name)
        source = temp / "source"
        extracted_files = safe_extract_tar_gz_member(
            source_zip,
            nested_archive_name(LANE),
            source,
        )
        invariants = source_invariants(source, source_zip)
        compiles = compile_rows()

        artifact_runtime = RUNTIME / "artifact-tests"
        env, cwd = isolated_environment(
            artifact_runtime,
            python_paths=(ARTIFACTS, source),
            inherit={"NICOTINE_SOURCE_ROOT": str(source)},
        )
        artifact_junit = artifact_runtime / "junit.xml"
        artifact_command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            *(str(ARTIFACTS / name) for name in ARTIFACT_TEST_FILES),
            f"--junitxml={artifact_junit}",
        ]
        artifact_run = run_bounded(
            artifact_command,
            cwd=cwd,
            env=env,
            timeout=180,
            output_path=artifact_runtime / "pytest.log",
        )
        artifact_tests = parse_junit_report(artifact_junit) if artifact_junit.is_file() else []
        for row in artifact_tests:
            row["lane"] = "research-model-and-source"

        unit_runtime = RUNTIME / "upstream-units"
        unit_env, _unit_cwd = isolated_environment(
            unit_runtime,
            python_paths=(source,),
        )
        unit_junit = unit_runtime / "junit.xml"
        unit_command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            str(source / "pynicotine/tests/unit"),
            f"--ignore={source / 'pynicotine/tests/unit/test_i18n.py'}",
            f"--junitxml={unit_junit}",
        ]
        unit_run = run_bounded(
            unit_command,
            cwd=source,
            env=unit_env,
            timeout=300,
            output_path=unit_runtime / "pytest.log",
        )
        unit_tests = parse_junit_report(unit_junit) if unit_junit.is_file() else []

    artifact_passed = sum(row["outcome"] == "passed" for row in artifact_tests)
    artifact_failed = sum(row["outcome"] in {"failed", "error"} for row in artifact_tests)
    unit_passed = sum(row["outcome"] == "passed" for row in unit_tests)
    unit_skipped = sum(row["outcome"] == "skipped" for row in unit_tests)
    unit_failed = sum(row["outcome"] in {"failed", "error"} for row in unit_tests)
    errors: list[str] = []
    if artifact_run.returncode != 0 or artifact_failed or len(artifact_tests) != 33:
        errors.append(
            f"artifact tests rc={artifact_run.returncode}, rows={len(artifact_tests)}, failed={artifact_failed}"
        )
    if unit_run.returncode != 0 or unit_failed:
        errors.append(f"upstream units rc={unit_run.returncode}, failed={unit_failed}")
    failed_invariants = [row["invariant"] for row in invariants if row["status"] != "pass"]
    if failed_invariants:
        errors.append(f"source invariants failed: {failed_invariants}")
    failed_compiles = [row["path"] for row in compiles if row["status"] != "pass"]
    if failed_compiles:
        errors.append(f"compile checks failed: {failed_compiles}")

    return {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "disposition": "open-public-design-research",
        "selected_patch": None,
        "source": {
            "bundle": source_zip.name,
            "bundle_sha256": inspect_bundle(source_zip).sha256,
            "lane": LANE,
            "executable_source_ref": EXECUTABLE_SOURCE_REF,
            "public_source_ref": PUBLIC_SOURCE_REF,
            "extracted_files": extracted_files,
            "scope": "executable tests use bundled proxy; public current-flow review is separate",
        },
        "findings": {
            "current_semantics": "same-token Retry/Merge with no clear and per-page username deduplication",
            "display_cap_behavior": "the first repeated response at the result cap retires admission before page processing",
            "required_identity_split": "stable logical search ID plus replaceable wire epoch token",
            "late_reply_layers": "retire old core route before enqueue, then retire network admission in an ordered batch",
            "network_contract_gap": "the current queue can silently drop while disabled and clear accepted work on disconnect; enqueue acceptance alone is not an applied acknowledgement",
            "disconnect_requirement": "retain a pending epoch until network application is acknowledged, or reconcile/replay it after reconnect",
            "selected_implementation": None,
        },
        "artifact_tests": {
            "passed": artifact_passed,
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
            "passed": unit_passed,
            "skipped": unit_skipped,
            "failed": unit_failed,
            "total": len(unit_tests),
            "returncode": unit_run.returncode,
            "excluded": ["pynicotine/tests/unit/test_i18n.py (msgfmt unavailable)"],
        },
        "errors": errors,
        "_rows": {
            "invariants": invariants,
            "tests": artifact_tests,
            "compiles": compiles,
            "owners": owner_rows(),
        },
    }


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
        OUTPUT_OWNERS,
        rows["owners"],
        fields=("owner", "current_identity", "desired_identity", "rotation_risk"),
    )
    evidence = ROOT / "evidence/rev0078-search-epoch-probe.md"
    evidence.write_text(
        "\n".join([
            "# rev0078 search-epoch probe",
            "",
            f"Status: **{result['status']}**",
            "",
            "```text",
            f"artifact tests: {result['artifact_tests']['passed']}/{result['artifact_tests']['total']} passed",
            f"source invariants: {result['source_invariants']['passed']}/{result['source_invariants']['total']} passed",
            f"compile checks: {result['compile_checks']['passed']}/{result['compile_checks']['total']} passed",
            f"upstream units: {result['upstream_units']['passed']} passed, {result['upstream_units']['skipped']} skipped",
            f"selected patch: {result['selected_patch']}",
            "```",
            "",
            "The composite enqueue closes only the immediate rejection gap; the disconnect counterexample still requires an applied acknowledgement or reconciliation.",
            "",
        ]) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    try:
        source_zip, inspections = locate_source_bundle(args.source_zip)
        result = run_probe(source_zip)
        result["source_candidates"] = [asdict(row) for row in inspections]
    except (SourceBundleError, OSError, RuntimeError, zipfile.BadZipFile) as exc:
        result = {
            "revision": REVISION,
            "status": "fail",
            "selected_patch": None,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    if args.write_data and "_rows" in result:
        write_outputs(result)
    print(canonical_json({key: value for key, value in result.items() if key != "_rows"}), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
