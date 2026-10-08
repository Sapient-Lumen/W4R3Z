#!/usr/bin/env python3
"""Audit the one reviewed raw-fork owner and every inherited-state consumer."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_raw_fork_boundaries import (
    FORK_CALL,
    INHERITED_CONSUMERS,
    INHERITED_CONSUMER_TARGETS,
    SPAWN_INHERITED_CALL,
    erase_non_code,
    inherited_spawn_inventory,
)
FORBIDDEN_CONSUMER_PRIMITIVES = {
    "fork": FORK_CALL,
    "waitpid": re.compile(r"(?<![A-Za-z0-9_])(?:::)?waitpid\s*\("),
    "pipe": re.compile(r"(?<![A-Za-z0-9_])(?:::)?pipe(?:2)?\s*\("),
    "kill": re.compile(r"(?<![A-Za-z0-9_])(?:::)?kill\s*\("),
}


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    if start < 0:
        return ""
    stop = text.find(end, start + len(begin))
    return text[start:] if stop < 0 else text[start:stop]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    required = {
        "CMakeLists.txt",
        "tests/inherited_test_process.hpp",
        "tests/inherited_test_process.cpp",
        "tests/inherited_test_process_test.cpp",
        "tests/test_process_topology_owner.hpp",
        "tests/test_process_topology_owner.cpp",
        "tests/test_process_topology_owner_test.cpp",
        "tests/self_exec_test_process.hpp",
        "tools/audit_test_process_topology_owner.py",
        *INHERITED_CONSUMERS,
    }
    missing = sorted(path for path in required if not (root / path).is_file())
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(args.json, root, checks)

    header = (root / "tests/inherited_test_process.hpp").read_text(
        encoding="utf-8"
    )
    source = (root / "tests/inherited_test_process.cpp").read_text(
        encoding="utf-8"
    )
    runtime = (root / "tests/inherited_test_process_test.cpp").read_text(
        encoding="utf-8"
    )
    topology_header = (root / "tests/test_process_topology_owner.hpp").read_text(
        encoding="utf-8"
    )
    topology = (root / "tests/test_process_topology_owner.cpp").read_text(
        encoding="utf-8"
    )
    topology_runtime = (root / "tests/test_process_topology_owner_test.cpp").read_text(
        encoding="utf-8"
    )
    cmake = (root / "CMakeLists.txt").read_text(encoding="utf-8")
    source_code = erase_non_code(source)

    production_refs: list[str] = []
    for base in (root / "src", root / "include"):
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".cpp", ".hpp", ".h", ".cc", ".cxx"}:
                if "inherited_test_process" in path.read_text(
                    encoding="utf-8", errors="replace"
                ):
                    production_refs.append(path.relative_to(root).as_posix())
    require(
        not production_refs
        and "namespace anonsync::test" in header
        and "namespace anonsync::test" in source,
        "owner_is_test_only",
        f"production_references={production_refs}",
    )

    require(
        all(
            token in header
            for token in (
                "class InheritedTestProcess final",
                "InheritedTestProcess(const InheritedTestProcess&) = delete",
                "operator=(const InheritedTestProcess&) = delete",
                "InheritedTestProcess(InheritedTestProcess&& other) noexcept",
                "~InheritedTestProcess()",
                "wait_for_exit(",
                "wait_for_exact_exit(",
                "wait_for_exit_with_output(",
                '#include "test_process_topology_owner.hpp"',
                "detail::TestProcessTopologyOwner topology_",
                "int output_read_ = -1",
            )
        ),
        "joint_owner_is_move_only_raii",
        "one noncopyable capability owns leader, group, optional output descriptor, wait, and teardown",
    )

    raw_forks = len(FORK_CALL.findall(source_code))
    require(
        raw_forks == 1
        and "const pid_t child = ::fork();" in source
        and "detail_spawn_inherited_test_process_or_throw(" in source
        and "std::addressof(function)" in header,
        "one_raw_fork_is_centralized",
        f"raw_fork_calls={raw_forks}",
    )

    process_owner = between(source, "void InheritedTestProcess::terminate_and_reap_noexcept()", "int InheritedTestProcess::wait_for_exit(")
    require(
        "thread_local bool inside_inherited_test_process_child" in source
        and "::setpgid(0, 0)" in source
        and "topology_.terminate_and_reap_noexcept();" in process_owner
        and all(
            token in topology
            for token in (
                "::kill(-process_group, SIGKILL)",
                "::kill(leader, SIGKILL)",
                "::waitpid(leader, &status, 0)",
                "std::exchange(leader_, -1)",
                "std::exchange(process_group_, -1)",
            )
        ),
        "nested_process_group_and_reap_authority_are_centralized",
        "top-level child owns a group; nested probes inherit it; one shared topology capability kills group and leader then reaps once",
    )

    plain_wait = between(
        source,
        "int InheritedTestProcess::wait_for_exit(",
        "void InheritedTestProcess::wait_for_exact_exit(",
    )
    capture_wait = between(
        source,
        "InheritedTestProcessOutput InheritedTestProcess::wait_for_exit_with_output(",
        "InheritedTestProcess detail_spawn_inherited_test_process_or_throw(",
    )
    require(
        all(
            token in plain_wait
            for token in (
                "std::chrono::steady_clock::now() + timeout",
                "topology_.try_complete_exit_or_throw(label)",
                "topology_.terminate_and_reap_noexcept()",
                "timed out and was killed and reaped",
            )
        ),
        "plain_wait_is_bounded_and_reuse_safe",
        "timeout consumes authority; ECHILD relinquishes numeric PID/group authority before throwing",
    )
    require(
        all(
            token in source
            for token in (
                "O_CLOEXEC",
                "O_NONBLOCK",
                "kMaximumInheritedCaptureBytes",
                "output exceeded its",
                "POLLIN | POLLHUP",
            )
        )
        and all(
            token in capture_wait
            for token in (
                "leader_completed && output_read_ < 0",
                "std::chrono::steady_clock::now() + timeout",
                "topology_.try_complete_exit_or_throw(label)",
                "topology_.terminate_and_reap_noexcept()",
            )
        )
        and "process_group_" not in capture_wait
        and "pid_t process_group" not in capture_wait,
        "capture_is_bounded_under_one_deadline",
        "nonblocking close-on-exec pipe, byte cap, leader completion, EOF, and cleanup share one deadline without caching group authority",
    )

    child_branch = between(source, "if (child == 0)", "return InheritedTestProcess(")
    require(
        all(
            token in child_branch
            for token in (
                "inside_inherited_test_process_child = true",
                "exit_code = entry(context",
                "catch (...) {",
                "::_exit(kInheritedTestProcessUnhandledExceptionExitCode)",
                "::_exit(kInheritedTestProcessInvalidReturnExitCode)",
                "::_exit(exit_code)",
            )
        ),
        "child_executes_only_reviewed_callback_and_exits_without_unwind",
        "the centralized child branch sets group state, invokes one callback, range-checks status, and uses _exit",
    )

    observed_counts = inherited_spawn_inventory(root)
    primitive_violations: dict[str, list[str]] = {}
    for relative in observed_counts:
        text = (root / relative).read_text(encoding="utf-8")
        code = erase_non_code(text)
        hits = [
            name
            for name, pattern in FORBIDDEN_CONSUMER_PRIMITIVES.items()
            if pattern.search(code)
        ]
        if hits:
            primitive_violations[relative] = hits
    require(
        observed_counts == INHERITED_CONSUMERS,
        "discovered_inherited_spawn_inventory_is_exact",
        f"discovered={observed_counts}; expected={INHERITED_CONSUMERS}",
    )
    require(
        not primitive_violations,
        "consumers_contain_no_process_choreography",
        f"violations={primitive_violations}",
    )

    incarnation = (root / "tests/process_incarnation_tests.cpp").read_text(
        encoding="utf-8"
    )
    require(
        "struct ProcessIncarnationObservation final" in incarnation
        and "std::is_trivially_copyable_v<ProcessIncarnationObservation>" in incarnation
        and "observe_process_incarnation(" in incarnation
        and "&token, sizeof(token)" not in incarnation
        and "SyncProcessIncarnation token;" not in incarnation,
        "lineage_pipe_exports_observation_not_capability_representation",
        "only typed pid/generation facts cross the pipe; non-trivially-copyable authority bytes never do",
    )

    require(
        all(
            token in runtime
            for token in (
                "kFixtureFailSafeSeconds",
                "test_exact_exit_and_move",
                "test_child_exception_and_invalid_return",
                "test_capture_is_exact_and_bounded",
                "test_wait_mode_mismatch_is_recoverable",
                "test_timeout_and_destructor_reap",
                "test_external_reap_relinquishes_numeric_authority",
                "test_nested_child_stays_in_top_level_group",
                "test_successful_exit_kills_remaining_group",
                "test_post_reap_capture_timeout_consumes_group_authority",
                "timed out while collecting inherited output",
                "ScopedChildSubreaper",
                "reap_exact_sigkill_bounded",
                "checks=",
                "failures=0",
            )
        )
        and runtime.count("::alarm(kFixtureFailSafeSeconds)") == 4,
        "runtime_contract_exercises_failure_and_lifetime_frontiers",
        "move, status, exception, capture, overflow, API misuse, timeout, destructor, ECHILD, nested-group, successful-leader cleanup, and post-reap drain-timeout paths execute",
    )

    require(
        "std::optional<int> try_complete_exit_or_throw(" in topology_header
        and "WEXITED | WNOHANG | WNOWAIT" in topology
        and "::kill(-process_group_, SIGKILL)" in topology
        and "::waitpid(exact_leader, &status, 0)" in topology
        and "relinquish_numeric_authority_noexcept();" in topology
        and "waitable zombie" in topology
        and "cleanup after exact reap issued a stale numeric syscall" in topology_runtime
        and "process_group_" not in capture_wait,
        "successful_wait_kills_group_before_identity_release",
        "plain and captured success observe without reaping, signal the still-bound group, reap the exact leader, and clear both numeric identifiers before later drain work",
    )

    cmake_consumers = all(name in cmake for name in INHERITED_CONSUMER_TARGETS)
    require(
        all(
            token in cmake
            for token in (
                "add_library(anonsync_inherited_test_process STATIC",
                "add_executable(anonsync_inherited_test_process_test",
                "ANONSYNC_INHERITED_PROCESS_CONSUMER",
                "inherited test process must depend only on the topology owner",
                "test process topology owner must remain dependency-free",
                "add_test(NAME anonsync_test_process_topology_owner_test",
                "anonsync_inherited_test_process_source_audit",
                "tools/audit_inherited_test_process.py",
                "anonsync_test_process_topology_owner_source_audit",
                "tools/audit_test_process_topology_owner.py",
                "add_test(NAME anonsync_inherited_test_process_test",
            )
        )
        and cmake_consumers,
        "build_graph_and_ctest_gate_are_bound",
        "one dependency-free topology leaf, all consumers, deterministic/runtime proofs, source audits, and sanitizer lanes are represented in CMake",
    )

    total_spawns = sum(observed_counts.values())
    require(
        raw_forks == 1
        and len(INHERITED_CONSUMERS) == 16
        and total_spawns == 33,
        "inventory_metrics_are_exact",
        f"raw_forks={raw_forks}, consumer_tus={len(INHERITED_CONSUMERS)}, spawn_sites={total_spawns}",
    )
    return emit(
        args.json,
        root,
        checks,
        {
            "centralized_raw_fork_calls": raw_forks,
            "inherited_consumer_translation_units": len(INHERITED_CONSUMERS),
            "inherited_spawn_sites": total_spawns,
            "shared_topology_owner_header_lines": len(topology_header.splitlines()),
            "shared_topology_owner_source_lines": len(topology.splitlines()),
            "shared_topology_owner_runtime_lines": len(topology_runtime.splitlines()),
        },
    )


def emit(
    destination: Path | None,
    root: Path,
    checks: list[Check],
    metrics: dict[str, int] | None = None,
) -> int:
    failures = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-inherited-test-process-audit-v7",
        "root": str(root),
        "passed": not failures,
        "passed_checks": sum(check.passed for check in checks),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics or {},
        "violations": failures,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
