#!/usr/bin/env python3
"""Fail-closed inventory of raw fork() boundaries in AnonSync tests.

Only the dependency-free InheritedTestProcess implementation may call raw
fork(). Tests that intentionally inspect inherited state consume that owner;
all fresh-state crash/fault campaigns cross the pinned self-exec boundary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
FORK_CALL = re.compile(r"(?<![A-Za-z0-9_])(?:::)?fork\s*\(")
RAW_LITERAL_START = re.compile(r'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')
QUOTED_LITERAL_START = re.compile(r'(?:u8|u|U|L)?(["\'])')
SPAWN_INHERITED_CALL = re.compile(
    r"(?<![A-Za-z0-9_])spawn_inherited_test_process"
    r"(?:_with_output_capture)?_or_throw\s*\("
)

EXPECTED_TEST_CALLS = {"tests/inherited_test_process.cpp": 1}
INHERITED_CONSUMERS = {
    "tests/local_jsonl_replay_backend_namespace_test.cpp": 1,
    "tests/persistence/local_jsonl_replay_directory_authority_tests.cpp": 2,
    "tests/persistence/sqlite_persistence_process_authority_fork_test.cpp": 5,
    "tests/persistence/sqlite_verification_budget_tests.cpp": 2,
    "tests/persistence/local_jsonl_replay_namespace_tests.cpp": 2,
    "tests/process_incarnation_tests.cpp": 4,
    "tests/thread_incarnation_tests.cpp": 2,
    "tests/sqlite_owner_generation_borrow_test.cpp": 1,
    "tests/sqlite_owned_authorizer_policy_test.cpp": 2,
    "tests/sqlite_process_authority_fork_test.cpp": 1,
    "tests/sqlite_replay_ledger_selftests.cpp": 3,
    "tests/sqlite_source_first_move_test.cpp": 1,
    "tests/sync_replica_tls_transport_test.cpp": 3,
    "tests/sync_atomic_file_publication_prepared_test.cpp": 1,
    "tests/sync_posix_directory_resolution_test.cpp": 1,
    "tests/sync_replica_file_payload_store_test.cpp": 1,
}
INHERITED_CONSUMER_TARGETS = (
    "anonsync_local_jsonl_replay_backend_namespace_test",
    "anonsync_local_jsonl_replay_directory_authority_test",
    "anonsync_local_jsonl_replay_namespace_test",
    "anonsync_process_incarnation_test",
    "anonsync_thread_incarnation_test",
    "anonsync_sqlite_owner_generation_borrow_test",
    "anonsync_sqlite_owned_authorizer_policy_test",
    "anonsync_sqlite_persistence_process_authority_fork_test",
    "anonsync_sqlite_verification_budget_test",
    "anonsync_sqlite_process_authority_fork_test",
    "anonsync_sqlite_replay_ledger_selftests_lib",
    "anonsync_sqlite_source_first_move_test",
    "anonsync_sync_replica_tls_transport_test",
    "anonsync_sync_atomic_file_publication_prepared_test",
    "anonsync_sync_posix_directory_resolution_test",
    "anonsync_sync_replica_file_payload_store_test",
)
INHERITED_OWNER_IMPLEMENTATION_FILES = {
    "tests/inherited_test_process.hpp",
    "tests/inherited_test_process.cpp",
    "tests/inherited_test_process_test.cpp",
}
MIGRATED_CAMPAIGNS = {
    "tests/sync_atomic_file_publication_test.cpp": (
        "--anonsync-atomic-publication-writer-helper-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exact_exit(",
    ),
    "tests/sync_atomic_file_publication_cutpoint_test.cpp": (
        "--anonsync-atomic-publication-crash-helper-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exact_exit(",
    ),
    "tests/sqlite_runtime_payload_store_test.cpp": (
        "--anonsync-payload-crash-helper-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exact_exit(",
    ),
    "tests/peer_ingress_schema_attestation_test.cpp": (
        "--anonsync-peer-schema-owner-close-helper-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exact_exit(",
    ),
    "tests/sqlite_transaction_allocator_fault_test.cpp": (
        "--anonsync-sqlite-transaction-allocator-fault-worker-v1",
        "spawn_self_exec_test_process_with_output_capture_or_throw(",
        "wait_for_exact_exit_with_output(",
    ),
    "tests/sqlite_connection_authority_test.cpp": (
        "--anonsync-sqlite-connection-authority-affinity-worker-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exit_code(",
    ),
    "tests/sqlite_owner_generation_borrow_test.cpp": (
        "--anonsync-sqlite-owner-generation-borrow-close-worker-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exit_code(",
    ),
    "tests/sync_replica_sqlite_owner_test.cpp": (
        "--anonsync-replica-sqlite-owner-crash-helper-v1",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exact_exit(",
    ),
}
FORBIDDEN_CHOREOGRAPHY = {
    "fork": FORK_CALL,
    "waitpid": re.compile(r"(?<![A-Za-z0-9_])(?:::)?waitpid\s*\("),
    "kill": re.compile(r"(?<![A-Za-z0-9_])(?:::)?kill\s*\("),
    "pipe": re.compile(r"(?<![A-Za-z0-9_])(?:::)?pipe(?:2)?\s*\("),
}
REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("tests/inherited_test_process.hpp"),
    Path("tests/inherited_test_process.cpp"),
    Path("tests/inherited_test_process_test.cpp"),
    Path("tools/audit_raw_fork_boundaries.py"),
    *tuple(Path(path) for path in EXPECTED_TEST_CALLS),
    *tuple(Path(path) for path in INHERITED_CONSUMERS),
    *tuple(Path(path) for path in MIGRATED_CAMPAIGNS),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def erase_non_code(text: str) -> str:
    """Replace C/C++ comments and literals with spaces, preserving newlines."""

    out = list(text)
    n = len(text)
    i = 0

    def blank(start: int, stop: int) -> None:
        for index in range(start, min(stop, n)):
            if out[index] != "\n":
                out[index] = " "

    while i < n:
        if text.startswith("//", i):
            stop = text.find("\n", i + 2)
            stop = n if stop < 0 else stop
            blank(i, stop)
            i = stop
            continue
        if text.startswith("/*", i):
            stop = text.find("*/", i + 2)
            stop = n if stop < 0 else stop + 2
            blank(i, stop)
            i = stop
            continue
        raw_match = RAW_LITERAL_START.match(text, i)
        if raw_match:
            terminator = ")" + raw_match.group(1) + '"'
            end = text.find(terminator, raw_match.end())
            stop = n if end < 0 else end + len(terminator)
            blank(i, stop)
            i = stop
            continue
        quoted_match = QUOTED_LITERAL_START.match(text, i)
        if quoted_match:
            quote = quoted_match.group(1)
            j = quoted_match.end()
            escaped = False
            while j < n:
                char = text[j]
                if char == "\n" and not escaped:
                    break
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    j += 1
                    break
                j += 1
            blank(i, j)
            i = j
            continue
        i += 1
    return "".join(out)


def source_files(root: Path, directory: str) -> list[Path]:
    base = root / directory
    if not base.is_dir():
        return []
    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES
    )


def raw_fork_inventory(root: Path, directory: str) -> dict[str, int]:
    inventory: dict[str, int] = {}
    for path in source_files(root, directory):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "fork" not in text:
            continue
        count = len(FORK_CALL.findall(erase_non_code(text)))
        if count:
            inventory[path.relative_to(root).as_posix()] = count
    return inventory


def inherited_spawn_inventory(root: Path) -> dict[str, int]:
    """Discover every test translation unit that consumes the fork owner."""

    inventory: dict[str, int] = {}
    for path in source_files(root, "tests"):
        relative = path.relative_to(root).as_posix()
        if relative in INHERITED_OWNER_IMPLEMENTATION_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "spawn_inherited_test_process" not in text:
            continue
        count = len(SPAWN_INHERITED_CALL.findall(erase_non_code(text)))
        if count:
            inventory[relative] = count
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = sorted(path.as_posix() for path in REQUIRED if not (root / path).is_file())
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(args.json, root, checks, {}, {}, {})

    production = {
        **raw_fork_inventory(root, "src"),
        **raw_fork_inventory(root, "include"),
    }
    tests = raw_fork_inventory(root, "tests")
    require(
        not production,
        "production_contains_no_raw_fork_calls",
        f"production_raw_fork_calls={production}",
    )
    require(
        tests == EXPECTED_TEST_CALLS,
        "one_raw_fork_is_owned_by_the_shared_test_boundary",
        f"observed={tests}; expected={EXPECTED_TEST_CALLS}",
    )

    inherited_counts = inherited_spawn_inventory(root)
    inherited_violations: dict[str, list[str]] = {}
    for relative in inherited_counts:
        text = (root / relative).read_text(encoding="utf-8")
        code = erase_non_code(text)
        hits = [name for name, pattern in FORBIDDEN_CHOREOGRAPHY.items() if pattern.search(code)]
        if hits:
            inherited_violations[relative] = hits
    require(
        inherited_counts == INHERITED_CONSUMERS,
        "discovered_inherited_state_consumers_match_the_exact_inventory",
        f"discovered={inherited_counts}; expected={INHERITED_CONSUMERS}",
    )
    require(
        not inherited_violations,
        "inherited_state_consumers_contain_no_process_choreography",
        f"violations={inherited_violations}",
    )

    migrated_detail: list[str] = []
    migrated_ok = True
    for relative, campaign_tokens in MIGRATED_CAMPAIGNS.items():
        helper_flag, spawn_token, wait_token = campaign_tokens
        text = (root / relative).read_text(encoding="utf-8")
        code = erase_non_code(text)
        primitive_hits = [
            name
            for name, pattern in FORBIDDEN_CHOREOGRAPHY.items()
            if name in {"fork", "waitpid", "kill"} and pattern.search(code)
        ]
        tokens_ok = all(
            token in text
            for token in (
                '#include "self_exec_test_process.hpp"',
                helper_flag,
                "verify_self_exec_child_boundary_or_throw()",
                spawn_token,
                wait_token,
            )
        )
        file_ok = tokens_ok and not primitive_hits
        migrated_ok = migrated_ok and file_ok
        migrated_detail.append(
            f"{relative}:tokens={tokens_ok},forbidden={primitive_hits}"
        )
    require(
        migrated_ok,
        "eight_fresh_state_campaigns_use_pinned_self_exec_images",
        "; ".join(migrated_detail),
    )

    prepared = (root / "tests/sync_atomic_file_publication_prepared_test.cpp").read_text(
        encoding="utf-8"
    )
    prepared_code = erase_non_code(prepared)
    prepared_hits = [
        name for name, pattern in FORBIDDEN_CHOREOGRAPHY.items() if pattern.search(prepared_code)
    ]
    require(
        '#include "inherited_test_process.hpp"' in prepared
        and len(SPAWN_INHERITED_CALL.findall(prepared_code)) == 1
        and "fork_plan.publish_or_throw();" in prepared
        and "return 91;" in prepared
        and "return 92;" in prepared
        and "wait_for_exit(" in prepared
        and not prepared_hits,
        "prepared_publication_inheritance_probe_is_minimal_and_owned",
        f"shared spawn=1, callback publishes then returns reviewed statuses, forbidden={prepared_hits}",
    )

    publication = (root / "src/sync_atomic_file_publication.cpp").read_text(
        encoding="utf-8"
    )
    require(
        "require_sync_process_incarnation_or_fail_stop(" in publication
        and "implementation->owner_process_incarnation" in publication
        and "prepared immutable JSON publication destination authority" in publication
        and "implementation->label +" not in publication
        and "belongs to a different process incarnation" not in publication,
        "prepared_publication_process_mismatch_fail_stops",
        "inherited publication authority cannot unwind through application code before filesystem effects",
    )

    cmake = (root / "CMakeLists.txt").read_text(encoding="utf-8")
    cmake_tokens = (
        "add_library(anonsync_inherited_test_process STATIC",
        "add_executable(anonsync_inherited_test_process_test",
        "ANONSYNC_INHERITED_PROCESS_CONSUMER",
        "anonsync_sqlite_connection_authority_test PRIVATE\n    anonsync_self_exec_test_process",
        "anonsync_sqlite_owner_generation_borrow_test PRIVATE\n    anonsync_self_exec_test_process",
        "anonsync_sync_atomic_file_publication_test",
        "anonsync_sync_atomic_file_publication_cutpoint_test",
        "anonsync_sqlite_runtime_payload_store_test PRIVATE\n    anonsync_self_exec_test_process",
        "anonsync_peer_ingress_schema_attestation_test PRIVATE\n    anonsync_self_exec_test_process",
        "anonsync_sqlite_transaction_allocator_fault_test PRIVATE",
        "anonsync_sync_replica_sqlite_owner_test PRIVATE\n    anonsync_self_exec_test_process",
    )
    require(
        all(token in cmake for token in cmake_tokens)
        and all(target in cmake for target in INHERITED_CONSUMER_TARGETS),
        "build_graph_binds_inherited_and_fresh_image_owners",
        "CMake carries the exact discovered inherited-consumer inventory and all eight fresh-image campaigns",
    )
    require(
        "anonsync_raw_fork_boundary_source_audit" in cmake
        and "tools/audit_raw_fork_boundaries.py" in cmake
        and "anonsync_inherited_test_process_source_audit" in cmake
        and "PROPERTIES TIMEOUT 20" in cmake,
        "fork_ownership_inventory_is_in_the_ctest_gate",
        "raw-fork and inherited-owner audits are release obligations",
    )

    total_production = sum(production.values())
    total_test = sum(tests.values())
    metrics = {
        "production_raw_fork_calls": total_production,
        "test_raw_fork_calls": total_test,
        "raw_fork_translation_units": len(tests),
        "inherited_consumer_translation_units": len(INHERITED_CONSUMERS),
        "inherited_spawn_sites": sum(inherited_counts.values()),
        "fresh_image_migrated_campaigns": len(MIGRATED_CAMPAIGNS),
    }
    require(
        metrics
        == {
            "production_raw_fork_calls": 0,
            "test_raw_fork_calls": 1,
            "raw_fork_translation_units": 1,
            "inherited_consumer_translation_units": 16,
            "inherited_spawn_sites": 32,
            "fresh_image_migrated_campaigns": 8,
        },
        "inventory_metrics_are_exact",
        ", ".join(f"{key}={value}" for key, value in metrics.items()),
    )
    return emit(args.json, root, checks, metrics, production, tests)


def emit(
    output: Path | None,
    root: Path,
    checks: list[Check],
    metrics: dict[str, int],
    production: dict[str, int],
    tests: dict[str, int],
) -> int:
    failures = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-raw-fork-boundary-audit-v5",
        "root": str(root),
        "passed": not failures,
        "passed_checks": sum(check.passed for check in checks),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
        "production_inventory": production,
        "test_inventory": tests,
        "violations": failures,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
