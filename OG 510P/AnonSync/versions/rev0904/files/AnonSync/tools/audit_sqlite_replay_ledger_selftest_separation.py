#!/usr/bin/env python3
"""Audit replay-ledger restore-lock ownership and diagnostic separation.

The audit is intentionally lexical: executable behavior is proved separately by
focused and full CTest lanes. It fails closed when production regains subprocess
choreography, when lock-holder tests regress to raw post-fork application work,
or when the extracted corpus leaks into the runtime source list.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace : index + 1]
    return ""


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def target_body(cmake: str, target: str) -> str:
    start = cmake.find(f"add_library({target}")
    if start < 0:
        return ""
    candidates = [
        position
        for marker in ("\nadd_library(", "\nadd_executable(", "\nif(")
        if (position := cmake.find(marker, start + 1)) >= 0
    ]
    end = min(candidates) if candidates else len(cmake)
    return cmake[start:end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    required = [
        Path("CMakeLists.txt"),
        Path("include/anonsync_selftest_api.hpp"),
        Path("src/anonsync_core.cpp"),
        Path("src/sqlite_replay_ledger.cpp"),
        Path("src/sqlite_replay_ledger_selftest_bridge.hpp"),
        Path("tests/sqlite_replay_ledger_selftests.cpp"),
        Path("src/persistence/sqlite_replay_ledger_restore_lock.hpp"),
        Path("src/persistence/sqlite_replay_ledger_restore_lock.cpp"),
        Path("src/persistence/sqlite_replay_ledger_write_gate.cpp"),
        Path("tests/self_exec_test_process.hpp"),
        Path("tests/self_exec_test_process.cpp"),
        Path("tests/inherited_test_process.hpp"),
        Path("tests/inherited_test_process.cpp"),
        Path("tests/test_process_topology_owner.hpp"),
        Path("tests/test_process_topology_owner.cpp"),
    ]
    missing = [path.as_posix() for path in required if not (root / path).is_file()]
    if missing:
        result = {
            "format": "anonsync-sqlite-replay-ledger-selftest-separation-audit-v3",
            "passed": False,
            "violations": [f"missing required file: {path}" for path in missing],
        }
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered)
        else:
            sys.stdout.write(rendered)
        return 2

    text = {path: (root / path).read_text(errors="replace") for path in required}
    cmake = text[Path("CMakeLists.txt")]
    api = text[Path("include/anonsync_selftest_api.hpp")]
    cli = text[Path("src/anonsync_core.cpp")]
    runtime = text[Path("src/sqlite_replay_ledger.cpp")]
    bridge = text[Path("src/sqlite_replay_ledger_selftest_bridge.hpp")]
    corpus = text[Path("tests/sqlite_replay_ledger_selftests.cpp")]
    restore_hpp = text[Path("src/persistence/sqlite_replay_ledger_restore_lock.hpp")]
    restore_cpp = text[Path("src/persistence/sqlite_replay_ledger_restore_lock.cpp")]
    write_gate_cpp = text[Path("src/persistence/sqlite_replay_ledger_write_gate.cpp")]
    self_exec_hpp = text[Path("tests/self_exec_test_process.hpp")]
    self_exec_cpp = text[Path("tests/self_exec_test_process.cpp")]
    inherited_hpp = text[Path("tests/inherited_test_process.hpp")]
    inherited_cpp = text[Path("tests/inherited_test_process.cpp")]
    topology_owner = text[Path("tests/test_process_topology_owner.cpp")]

    checks: list[dict[str, object]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    selftest_definitions = re.findall(
        r"\bint\s+(run_ledger_sqlite_(?:readonly_snapshot_verifier|restore_prefix_continuity|restore_write_gate|restore_locking|restore_manifest_binding)_selftest)\s*\(",
        corpus,
    )
    runtime_selftest_defs = re.findall(r"\bint\s+run_ledger_sqlite_[A-Za-z0-9_]+_selftest\s*\(", runtime)

    check(
        "five_restore_diagnostics_have_one_test_only_owner",
        len(selftest_definitions) == 5 and len(set(selftest_definitions)) == 5,
        f"definitions={sorted(selftest_definitions)}",
    )
    check(
        "runtime_translation_unit_has_no_selftest_entry_points",
        not runtime_selftest_defs,
        f"runtime selftest definitions={runtime_selftest_defs}",
    )
    check(
        "runtime_translation_unit_has_no_process_choreography",
        all(token not in runtime for token in ("::fork(", "::waitpid(", "<sys/wait.h>", "std::this_thread::sleep_for")),
        "production replay-ledger source contains no fork, waitpid, wait header, or test sleep",
    )
    check(
        "runtime_translation_unit_is_reduced",
        len(runtime.splitlines()) < 4600 and len(corpus.splitlines()) >= 1000,
        f"runtime_lines={len(runtime.splitlines())} corpus_lines={len(corpus.splitlines())}",
    )

    core_sources = cmake[cmake.find("set(ANONSYNC_CORE_SOURCES") : cmake.find("add_library(anonsync_core_lib")]
    selftest_sources = cmake[cmake.find("set(ANONSYNC_SELFTEST_SOURCES") : cmake.find("# Keep independent diagnostic owners")]
    corpus_target = target_body(cmake, "anonsync_sqlite_replay_ledger_selftests_lib")
    core_target = target_body(cmake, "anonsync_core_lib")
    check(
        "cmake_places_corpus_only_in_selftest_source_inventory",
        "tests/sqlite_replay_ledger_selftests.cpp" not in core_sources
        and "${ANONSYNC_SQLITE_REPLAY_LEDGER_SELFTEST_SOURCE}" in selftest_sources
        and "${ANONSYNC_SQLITE_REPLAY_LEDGER_SELFTEST_SOURCE}" in corpus_target,
        "corpus is guarded outside ANONSYNC_CORE_SOURCES",
    )
    check(
        "dependency_direction_is_test_to_runtime_only",
        "PUBLIC anonsync_core_lib" in corpus_target
        and "anonsync_sqlite_replay_ledger_selftests_lib" not in core_target
        and "anonsync_sqlite_replay_ledger_selftests_lib" in cmake[cmake.find("add_library(anonsync_selftests_lib INTERFACE)") : cmake.find("add_executable(anonsync_core")],
        "diagnostic corpus depends on runtime; runtime never depends on diagnostic corpus",
    )
    check(
        "ordinary_runtime_source_inventory_guard_covers_corpus",
        "foreach(ANONSYNC_SELFTEST_SOURCE IN LISTS ANONSYNC_SELFTEST_SOURCES)" in cmake
        and 'list(FIND ANONSYNC_CORE_SOURCES "${ANONSYNC_SELFTEST_SOURCE}"' in cmake,
        "CMake configure fails if any selftest source is reabsorbed",
    )

    restore_destructor = function_body(
        restore_cpp, "SqliteReplayLedgerRestoreLock::~SqliteReplayLedgerRestoreLock()"
    )
    state_destructor = function_body(restore_cpp, "~State()")
    check(
        "restore_lock_is_separately_linked_invariant_owner",
        "add_library(anonsync_sqlite_replay_ledger_restore_lock STATIC" in cmake
        and "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESTORE_LOCK_SOURCE}" in cmake
        and "anonsync_sqlite_replay_ledger_restore_lock" in core_target,
        "restore-lock source is outside core source list and linked as an owner",
    )
    check(
        "restore_lock_type_is_noncopyable_nonmovable",
        all(token in restore_hpp for token in (
            "SqliteReplayLedgerRestoreLock(const SqliteReplayLedgerRestoreLock&) = delete",
            "operator=(\n        const SqliteReplayLedgerRestoreLock&) = delete",
            "SqliteReplayLedgerRestoreLock(SqliteReplayLedgerRestoreLock&&) = delete",
            "operator=(\n        SqliteReplayLedgerRestoreLock&&) = delete",
        )),
        "one object uniquely owns one process-bound flock lifetime",
    )
    check(
        "restore_lock_acquisition_is_hardened_and_observable",
        ordered(
            restore_cpp,
            "guard_sqlite_path_family_or_throw",
            "open_private_lock_file_or_throw",
            "LOCK_EX | LOCK_NB",
            "write_owner_marker_or_throw",
        )
        and all(token in restore_cpp for token in ("::ftruncate", "::lseek", "::write", "::fsync", '"pid="')),
        "path guard, private descriptor, nonblocking flock, and exact durable owner marker are one acquisition",
    )
    check(
        "restore_lock_destruction_checks_process_before_release",
        ordered(restore_destructor, "sync_process_incarnation_is_current", "state_.reset()")
        and "release_flocked_descriptor_noexcept" in state_destructor,
        "fork child cannot unlock or close parent authority during destruction",
    )
    check(
        "restore_path_uses_extracted_owner",
        "persistence::SqliteReplayLedgerRestoreLock restore_lock(ledger_path);" in runtime
        and "class SqliteRestoreLock" not in runtime,
        "production restore acquires only the focused owner",
    )

    helper_body = function_body(corpus, "dispatch_sqlite_replay_ledger_self_exec_helper")
    main_body = function_body(cli, "int main(int argc, char** argv)")
    check(
        "versioned_helper_dispatch_precedes_cli_state",
        ordered(
            main_body,
            "dispatch_sqlite_replay_ledger_self_exec_helper",
            "kSqliteReplayLedgerSelfExecHelperNotMatched",
            "std::string controls",
        )
        and "kSqliteReplayLedgerSelfExecHelperNotMatched" in api,
        "exact helper dispatch runs before ordinary CLI allocations and parsing",
    )
    check(
        "helper_proves_fresh_exec_boundary_before_path_authority",
        ordered(
            helper_body,
            "verify_self_exec_child_boundary_or_throw",
            "argc != 5",
            "normalized_absolute_helper_path_or_throw",
            "parse_helper_seconds_or_throw",
        )
        and "--anonsync-sqlite-replay-ledger-lock-holder-helper-v1" in helper_body,
        "fresh-image descriptor, environment, signal, and process-group evidence precedes filesystem use",
    )
    check(
        "self_exec_owner_is_descriptor_and_wait_bounded",
        all(token in self_exec_hpp + self_exec_cpp for token in (
            "posix_spawn",
            "posix_spawn_file_actions_addclosefrom_np",
            "wait_for_exact_exit",
            "terminate_and_reap_noexcept",
            "verify_self_exec_child_boundary_or_throw",
        )),
        "test subprocess owner pins executable authority, sanitizes descriptors, and bounds reap",
    )
    check(
        "lock_holder_tests_use_fresh_exec_and_exact_readiness",
        corpus.count("spawn_self_exec_test_process_or_throw") == 2
        and corpus.count("wait_for_lock_owner_marker_or_throw(") == 3  # definition plus two calls
        and corpus.count("wait_for_exact_exit(") == 2
        and "milliseconds(250)" not in corpus,
        "two isolation holders use self-exec, exact PID marker readiness, and bounded exit",
    )
    check(
        "three_inheritance_subjects_use_one_shared_process_owner",
        corpus.count("spawn_inherited_test_process_or_throw(") == 3
        and '#include "inherited_test_process.hpp"' in corpus
        and "::fork()" not in corpus
        and "::waitpid(" not in corpus
        and "run_sqlite_write_gate_holder(dst_gate_locked" not in corpus
        and "run_sqlite_restore_lock_holder(dst_locked" not in corpus,
        "copied capability state remains the subject, while raw process choreography is owned once",
    )
    check(
        "inheritance_waits_are_bounded_and_fail_closed",
        corpus.count("wait_for_exit(") == 3
        and corpus.count('5s, "restore') >= 3
        and "class InheritedTestProcess final" in inherited_hpp
        and "detail::TestProcessTopologyOwner topology_" in inherited_hpp
        and "topology_.try_complete_exit_or_throw(label)" in inherited_cpp
        and "WEXITED | WNOHANG | WNOWAIT" in topology_owner
        and "::kill(-process_group_, SIGKILL)" in topology_owner
        and "::waitpid(exact_leader, &status, 0)" in topology_owner
        and "timed out and was killed and reaped" in inherited_cpp
        and "anonsync_inherited_test_process_source_audit" in cmake,
        "three inheritance probes share monotonic timeout and one common process-group/leader authority owner with structural CTest coverage",
    )

    bridge_declarations = re.findall(
        r"\b(?:ReplayLedgerStats|std::string)\s+([A-Za-z0-9_]+_for_selftest)\s*\(", bridge
    )
    check(
        "private_bridge_is_narrow_and_fixture_free",
        len(bridge_declarations) == 3
        and len(set(bridge_declarations)) == 3
        and all(token not in bridge for token in ("fork", "waitpid", "sqlite3_open", "write_file")),
        f"bridge declarations={sorted(bridge_declarations)}",
    )
    check(
        "bridge_definitions_stay_with_runtime_invariants",
        all(runtime.count(name + "(") == 1 for name in bridge_declarations)
        and all(corpus.count(name + "(") >= 1 for name in bridge_declarations),
        "test corpus invokes exact production verifier/report hooks without copying their invariants",
    )
    check(
        "write_gate_and_restore_lock_markers_share_exact_pid_grammar",
        '"pid=" + std::to_string(static_cast<long long>(::getpid())) + "\\n"' in restore_cpp
        and '"pid=" + std::to_string(static_cast<long long>(::getpid())) + "\\n"' in write_gate_cpp,
        "readiness oracle is the exact marker written by each production lock owner",
    )

    passed = all(bool(item["passed"]) for item in checks)
    result = {
        "format": "anonsync-sqlite-replay-ledger-selftest-separation-audit-v3",
        "passed": passed,
        "checks_passed": sum(1 for item in checks if item["passed"]),
        "checks_total": len(checks),
        "metrics": {
            "runtime_lines": len(runtime.splitlines()),
            "selftest_corpus_lines": len(corpus.splitlines()),
            "raw_fork_count": corpus.count("::fork()"),
            "inherited_owner_spawn_count": corpus.count("spawn_inherited_test_process_or_throw("),
            "self_exec_holder_count": corpus.count("spawn_self_exec_test_process_or_throw"),
            "bridge_declaration_count": len(bridge_declarations),
        },
        "checks": checks,
        "violations": [item["detail"] for item in checks if not item["passed"]],
        "interpretation": [
            "This source-shape audit does not replace compilation, focused behavior tests, or the complete CTest gate.",
            "Three inherited-state probes remain, but their sole raw fork, deadlines, signaling, and reaping are centralized in the test-only owner; isolation helpers use fresh self-exec images.",
            "An owner marker is readiness evidence for these tests, not durable authorization for production transitions.",
        ],
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
