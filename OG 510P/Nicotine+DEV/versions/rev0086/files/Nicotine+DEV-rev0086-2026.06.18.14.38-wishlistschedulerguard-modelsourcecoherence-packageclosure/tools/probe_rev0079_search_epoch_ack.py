#!/usr/bin/env python3
"""Validate the Search Again acknowledgement/ownership research contract.

Research-only. No upstream patch is selected. The probe distinguishes main-
thread enqueue acceptance, network-thread ownership, socket serialization, and
remote result delivery, and requires all fan-out requests to be network-owned
before a local epoch acknowledgement can commit visible state.
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
    SourceBundleError,
    inspect_bundle,
    locate_source_bundle,
)

REVISION = derive_revision(ROOT)
LANE = "github-branch-master"
EXECUTABLE_SOURCE_REF = "f4e17d59783dbc48ea31d2e899a681e2dd1ed500"
PUBLIC_SOURCE_REF = "a96406e7aa285a3fb2a3e35900686d164a22bf02"
ARTIFACTS = ROOT / "maintainer_artifacts/search-epoch-01"
RUNTIME = ROOT / f"evidence/{REVISION}-search-epoch-ack-runtime"
OUTPUT_SUMMARY = ROOT / f"data/{REVISION}_search_epoch_ack_summary.json"
OUTPUT_INVARIANTS = ROOT / f"data/{REVISION}_search_epoch_ack_source_invariants.csv"
OUTPUT_TESTS = ROOT / f"data/{REVISION}_search_epoch_ack_test_matrix.csv"
OUTPUT_COMPILE = ROOT / f"data/{REVISION}_search_epoch_ack_compile_matrix.csv"
OUTPUT_STAGES = ROOT / f"data/{REVISION}_search_epoch_ack_stage_matrix.csv"
OUTPUT_FANOUT = ROOT / f"data/{REVISION}_search_epoch_ack_fanout.csv"

ARTIFACT_TEST_FILES = (
    "test_search_epoch_transaction.py",
    "test_search_epoch_races.py",
    "test_search_epoch_lifecycle.py",
    "test_search_epoch_queue_contract.py",
    "test_search_epoch_source_ownership.py",
    "test_search_epoch_ack_transaction.py",
    "test_search_epoch_ack_disconnect.py",
    "test_search_epoch_ack_counterexamples.py",
    "test_search_epoch_ack_lifecycle.py",
    "test_search_epoch_ack_source_ownership.py",
)
EXPECTED_ARTIFACT_TESTS = 78


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
    proto_path = source / "pynicotine/slskproto.py"
    events_path = source / "pynicotine/events.py"
    search_path = source / "pynicotine/search.py"
    gui_path = source / "pynicotine/gtkgui/search.py"
    message_path = source / "pynicotine/slskmessages.py"

    queue = method_source(proto_path, "NetworkThread", "_queue_network_message")
    drain = method_source(proto_path, "NetworkThread", "_process_queue_messages")
    outgoing = method_source(proto_path, "NetworkThread", "_process_outgoing_messages")
    server_output = method_source(proto_path, "NetworkThread", "_process_server_output")
    internal = method_source(proto_path, "NetworkThread", "_process_internal_messages")
    loop = method_source(proto_path, "NetworkThread", "_loop")
    disconnect = method_source(proto_path, "NetworkThread", "_server_disconnect")
    disable = method_source(proto_path, "NetworkThread", "_disable_message_queue")
    clear = method_source(proto_path, "NetworkThread", "_clear_message_queue")
    emit = method_source(events_path, "Events", "emit")
    emit_main = method_source(events_path, "Events", "emit_main_thread")
    process_events = method_source(events_path, "Events", "process_thread_events")
    send = method_source(search_path, "Search", "send_search_request")
    buddy = method_source(search_path, "Search", "_send_buddies_search_request")
    peer = method_source(search_path, "Search", "_send_peer_search_request")
    login = method_source(search_path, "Search", "_server_login")
    search_disconnect = method_source(search_path, "Search", "_server_disconnect")
    remove_search = method_source(search_path, "Search", "remove_search")
    retire_token = method_source(search_path, "Search", "remove_allowed_token")
    again = method_source(gui_path, "Search", "on_search_again")
    response = method_source(gui_path, "Search", "file_search_response")
    parse = method_source(message_path, "FileSearchResponse", "parse_network_message")

    raw: list[tuple[str, bool, str]] = [
        ("source bundle digest contract", inspect_bundle(source_zip).digest_ok, EXPECTED_SOURCE_SHA256),
        ("bundled master lane head", lane_head(source_zip, LANE) == EXECUTABLE_SOURCE_REF, EXECUTABLE_SOURCE_REF),
        ("queue acceptance conditional", "if self._should_process_queue:" in queue, "conditional put"),
        ("queue acceptance returns no status", "return" not in queue and "else" not in queue, "silent ignore while disabled"),
        ("queue drain batches messages", "msgs.append(self._message_queue.get_nowait())" in drain, "drain into list"),
        ("queue drain delegates outgoing processing", "self._process_outgoing_messages(msgs)" in drain, "list handoff"),
        ("outgoing processing can stop when disabled", "if not self._should_process_queue:" in outgoing and "return" in outgoing, "post-acceptance drop"),
        ("server-message permission can stop a batch", "if not self._is_outgoing_server_message_permitted(msg):" in outgoing, "early return"),
        ("closed connection can skip a message", "Cannot send the message over the closed connection" in outgoing, "continue"),
        ("outgoing batch has no per-message success result", "if process_func(conn, msg)" not in outgoing and "results.append" not in outgoing, "silent helper contract"),
        ("server output packs before buffer append", server_output.index("msg_content = self._pack_network_message(msg)") < server_output.index("out_buffer += msg_content"), "local serialization order"),
        ("server output can silently drop packing failure", "if msg_content is None:" in server_output and "return True" not in server_output and "return False" not in server_output, "no status"),
        ("server output arms socket write after append", server_output.index("out_buffer += msg_content") < server_output.index("selectors.EVENT_WRITE"), "buffer ownership before I/O"),
        ("network owns add-admission control", "AddAllowedResponse" in internal and ".add(msg.response_id)" in internal, "network-thread set mutation"),
        ("network owns remove-admission control", "RemoveAllowedResponse" in internal and ".discard(msg.response_id)" in internal, "network-thread set mutation"),
        ("no composite search epoch command", all(term not in internal for term in ("SearchEpoch", "EpochApplied", "transaction_id")), "absent"),
        ("network queue precedes ready sockets", loop.index("self._process_queue_messages()") < loop.index("self._process_ready_sockets(current_time)"), "loop ordering"),
        ("disconnect disables queue first", disconnect.index("self._disable_message_queue()") < disconnect.index("self._allowed_message_responses.clear()"), "disable before admission clear"),
        ("disconnect emits after admission clear", disconnect.index("self._allowed_message_responses.clear()") < disconnect.index('"server-disconnect"'), "clear before main event"),
        ("queue disable clears accepted commands", "self._clear_message_queue()" in disable and "self._message_queue.get_nowait()" in clear, "destructive drain"),
        ("network-to-main event is queued", "self._thread_events.put_nowait" in emit_main, "SimpleQueue handoff"),
        ("main-thread events preserve drained order", "event_list.append(self._thread_events.get_nowait())" in process_events and "for event in event_list:" in process_events, "FIFO batch"),
        ("event callback returns are ignored", "function(*args, **kwargs)" in emit and "return function" not in emit, "no synchronous ack channel"),
        ("search admission is requested before sends", send.index("self.add_allowed_token(token)") < send.index("self._send_global_search_request(search)"), "main-thread enqueue order only"),
        ("buddy search is per-recipient fan-out", "for username in core.buddies.users:" in buddy and "UserSearch(username" in buddy, "one server message per buddy"),
        ("user search is per-recipient fan-out", "for username in search.users:" in peer and "UserSearch(username" in peer, "one server message per user"),
        ("login does not republish extant admissions", "add_allowed_token" not in login and "send_search_request" not in login, "no replay"),
        ("search disconnect leaves registry intact", "self.searches.clear()" not in search_disconnect, "logical records survive"),
        ("search close queues parser-admission retirement", remove_search.index("self.remove_allowed_token(token)") < remove_search.index("search = self.searches.get(token)") and "RemoveAllowedResponse" in retire_token, "network-owned cancellation"),
        ("Search Again reuses page token", "core.search.send_search_request(self.token)" in again, "same-token retry/merge"),
        ("Search Again does not clear page", "clear_model" not in again, "rows retained"),
        ("page deduplicates by username", "if user in self.users:" in response, "repeat user suppressed"),
        ("parser token gate precedes full decompression", parse.index("if self.token not in self.allowed_responses:") < parse.rindex("decompressor.decompress"), "network admission boundary"),
        ("no applied event name", '"search-epoch-applied"' not in events_path.read_text(encoding="utf-8"), "absent"),
        ("no rejected event name", '"search-epoch-rejected"' not in events_path.read_text(encoding="utf-8"), "absent"),
    ]
    return [
        {"invariant": name, "status": "pass" if passed else "fail", "detail": detail}
        for name, passed, detail in raw
    ]


def stage_rows() -> list[dict[str, str]]:
    return [
        {"stage": "main enqueue", "owner": "main-thread queue producer", "proves": "command accepted by local queue call", "does_not_prove": "network thread observed command", "commit_safe": "no"},
        {"stage": "network dequeue", "owner": "network thread", "proves": "command reached processing", "does_not_prove": "admission and all fan-out requests were retained", "commit_safe": "no"},
        {"stage": "network output ownership", "owner": "network thread", "proves": "admission changed and every prepacked fan-out request entered the server output buffer", "does_not_prove": "OS socket write or remote delivery", "commit_safe": "policy-dependent local boundary"},
        {"stage": "main applied acknowledgement", "owner": "main thread after FIFO event handoff", "proves": "matching generation/transaction output ownership was reported", "does_not_prove": "buffered work survived a later disconnect", "commit_safe": "only with explicit disconnect policy"},
        {"stage": "socket write", "owner": "network connection output", "proves": "the local socket accepted some bytes", "does_not_prove": "remote receipt, complete frame receipt, or response", "commit_safe": "still not remote completion"},
        {"stage": "first matching result", "owner": "remote response plus local parser/core route", "proves": "at least one request produced an admitted result", "does_not_prove": "complete fan-out or zero-result peers", "commit_safe": "possible stale-view swap policy"},
    ]


def fanout_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for clicks in (1, 4, 12):
        for recipients in (1, 10, 40):
            for policy, epochs in (
                ("allow", clicks),
                ("reject-while-pending", 1),
                ("coalesce-one-trailing", min(clicks, 2)),
            ):
                rows.append({
                    "clicks": clicks,
                    "recipients": recipients,
                    "policy": policy,
                    "epochs": epochs,
                    "peer_requests": epochs * recipients,
                })
    return rows


def compile_rows() -> list[dict[str, str]]:
    paths = [ARTIFACTS / "search_epoch_model.py", ARTIFACTS / "search_epoch_ack_model.py"]
    paths.extend(ARTIFACTS / name for name in ARTIFACT_TEST_FILES)
    paths.extend([
        ROOT / "tools/cube_runtime.py",
        ROOT / "tools/source_bundle_locator.py",
        ROOT / "tools/probe_rev0079_search_epoch_ack.py",
        ROOT / "tools/audit_cube_runtime_adoption.py",
        ROOT / "tools/audit_current_navigation.py",
        ROOT / "tools/audit_current_package.py",
        ROOT / "tools/build_current_manifest.py",
        ROOT / "tools/build_current_delta_inventory.py",
        ROOT / "tools/validate_current_packet_dispositions.py",
    ])
    rows: list[dict[str, str]] = []
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, detail = "pass", ""
        except Exception as exc:  # pragma: no cover - fail-closed artifact check
            status, detail = "fail", f"{type(exc).__name__}: {exc}"
        rows.append({"path": path.relative_to(ROOT).as_posix(), "status": status, "detail": detail})
    return rows


def run_probe(source_zip: Path) -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    with tempfile.TemporaryDirectory(prefix=f"{REVISION}-search-epoch-ack-") as temp_name:
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
                sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                *(str(ARTIFACTS / name) for name in ARTIFACT_TEST_FILES),
                f"--junitxml={artifact_junit}",
            ],
            cwd=cwd,
            env=env,
            timeout=180,
            output_path=artifact_runtime / "pytest.log",
        )
        artifact_tests = parse_junit_report(artifact_junit) if artifact_junit.is_file() else []
        for row in artifact_tests:
            row["lane"] = "research-model-and-source"

        unit_runtime = RUNTIME / "upstream-units"
        unit_env, _unit_cwd = isolated_environment(unit_runtime, python_paths=(source,))
        unit_junit = unit_runtime / "junit.xml"
        unit_run = run_bounded(
            [
                sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
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
    if artifact_run.returncode != 0 or artifact_failed or len(artifact_tests) != EXPECTED_ARTIFACT_TESTS:
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

    result = {
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
            "scope": "executable tests use bundled proxy; current public-flow review is separate",
        },
        "findings": {
            "queue_acceptance": "not an acknowledgement; disabled queues silently ignore and disconnect clears accepted work",
            "minimum_local_ack": "after prepacking and output-buffer ownership of every fan-out request in the network thread",
            "fanout_correction": "buddy and user searches require one successfully staged request per intended recipient before acknowledgement",
            "existing_helper_gap": "current outgoing/server helpers silently return on permission, connection, or packing failures and expose no per-message success result",
            "ack_limit": "local output ownership does not prove OS socket write, remote delivery, a result, or survival across later disconnect",
            "commit_policy_gap": "maintainers must choose rollback/replay, stale-view swap, failure state, or acceptance of an empty committed page after disconnect",
            "current_implementation": "no composite epoch command, transaction/generation acknowledgement, or reconnect replay exists",
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
        "errors": errors,
        "_rows": {
            "invariants": invariants,
            "tests": artifact_tests,
            "compiles": compiles,
            "stages": stage_rows(),
            "fanout": fanout_rows(),
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
        OUTPUT_STAGES,
        rows["stages"],
        fields=("stage", "owner", "proves", "does_not_prove", "commit_safe"),
    )
    write_csv(
        OUTPUT_FANOUT,
        rows["fanout"],
        fields=("clicks", "recipients", "policy", "epochs", "peer_requests"),
    )
    (ROOT / f"evidence/{REVISION}-search-epoch-ack-probe.md").write_text(
        "\n".join([
            f"# {REVISION} search-epoch acknowledgement probe",
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
            "A local applied acknowledgement is meaningful only after every fan-out request is prepacked and staged in network-owned output state. It remains weaker than socket write, delivery, or reconnect durability.",
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
    except (SourceBundleError, OSError, RuntimeError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
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
