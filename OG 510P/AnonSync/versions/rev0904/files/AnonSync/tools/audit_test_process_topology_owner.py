#!/usr/bin/env python3
"""Fail-closed audit for shared test-process PID/process-group authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("tests/test_process_topology_owner.hpp"),
    Path("tests/test_process_topology_owner.cpp"),
    Path("tests/test_process_topology_owner_test.cpp"),
    Path("tests/inherited_test_process.hpp"),
    Path("tests/inherited_test_process.cpp"),
    Path("tests/inherited_test_process_test.cpp"),
    Path("tests/self_exec_test_process.hpp"),
    Path("tests/self_exec_test_process.cpp"),
    Path("tests/self_exec_test_process_test.cpp"),
    Path("tools/audit_test_process_topology_owner.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def block_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-test-process-topology-owner-audit-v2",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks, {})

    text = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = text[Path("CMakeLists.txt")]
    header = text[Path("tests/test_process_topology_owner.hpp")]
    source = text[Path("tests/test_process_topology_owner.cpp")]
    runtime = text[Path("tests/test_process_topology_owner_test.cpp")]
    inherited_header = text[Path("tests/inherited_test_process.hpp")]
    inherited_source = text[Path("tests/inherited_test_process.cpp")]
    inherited_runtime = text[Path("tests/inherited_test_process_test.cpp")]
    selfexec_header = text[Path("tests/self_exec_test_process.hpp")]
    selfexec_source = text[Path("tests/self_exec_test_process.cpp")]
    selfexec_runtime = text[Path("tests/self_exec_test_process_test.cpp")]
    audit_source = text[Path("tools/audit_test_process_topology_owner.py")]
    verifier = text[Path("tools/verify_release_package.py")]

    production_references: list[str] = []
    for directory in (root / "src", root / "include"):
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in {".c", ".cc", ".cpp", ".h", ".hpp"}:
                if "test_process_topology_owner" in path.read_text(
                    encoding="utf-8", errors="replace"
                ):
                    production_references.append(path.relative_to(root).as_posix())
    require(
        not production_references
        and "namespace anonsync::test::detail" in header
        and "namespace anonsync::test::detail" in source,
        "topology_owner_is_test_only",
        f"production_references={production_references}",
    )

    require(
        all(
            token in header
            for token in (
                "class TestProcessTopologyOwner final",
                "TestProcessTopologyOwner(const TestProcessTopologyOwner&) = delete",
                "operator=(const TestProcessTopologyOwner&) = delete",
                "TestProcessTopologyOwner(TestProcessTopologyOwner&& other) noexcept",
                "~TestProcessTopologyOwner();",
                "pid_t leader_ = -1",
                "pid_t process_group_ = -1",
            )
        ),
        "one_move_only_owner_holds_both_numeric_identifiers",
        "leader and top-level process-group authority cannot be copied or independently transferred",
    )

    direct_lifecycle = re.compile(r"::(?:kill|waitid|waitpid)\s*\(")
    require(
        len(header.splitlines()) < 100
        and direct_lifecycle.search(header) is None
        and "std::exchange" not in header
        and '#include "test_process_topology_owner.hpp"' in source,
        "public_header_exposes_contract_not_choreography",
        "syscall implementation and transition ordering compile once in a private source file instead of fanning out through consumers",
    )

    require(
        all(
            '#include "test_process_topology_owner.hpp"' in wrapper_header
            and "detail::TestProcessTopologyOwner topology_" in wrapper_header
            and "pid_t leader_" not in wrapper_header
            and "pid_t process_group_" not in wrapper_header
            and "pid_t child_" not in wrapper_header
            for wrapper_header in (inherited_header, selfexec_header)
        ),
        "wrapper_owners_store_no_parallel_numeric_authority",
        "both process wrappers contain one common topology capability rather than independent PID/group fields",
    )

    wrapper_lifecycle_sites = {
        "tests/inherited_test_process.cpp": len(
            direct_lifecycle.findall(inherited_source)
        ),
        "tests/self_exec_test_process.cpp": len(
            direct_lifecycle.findall(selfexec_source)
        ),
    }
    source_lifecycle_sites = len(direct_lifecycle.findall(source))
    require(
        not any(wrapper_lifecycle_sites.values()) and source_lifecycle_sites == 9,
        "all_signal_wait_and_reap_syscalls_have_one_compiled_owner",
        f"wrapper_sites={wrapper_lifecycle_sites}; owner_source_sites={source_lifecycle_sites}",
    )

    require(
        "std::optional<int> try_complete_exit_or_throw(" in header
        and "leader_exit_is_waitable_or_throw" not in header
        and "complete_observed_exit_or_throw" not in header
        and "leader_exit_is_waitable_or_throw" not in source
        and "complete_observed_exit_or_throw" not in source,
        "observation_and_completion_are_one_public_transition",
        "a wrapper cannot claim completion without first obtaining exact WNOWAIT evidence from the same owner call",
    )

    completion = block_between(
        source,
        "std::optional<int> TestProcessTopologyOwner::try_complete_exit_or_throw(",
        "void TestProcessTopologyOwner::terminate_and_reap_or_throw(",
    )
    require(
        bool(completion)
        and "::waitid(P_PID, static_cast<id_t>(leader_)" in completion
        and "WEXITED | WNOHANG | WNOWAIT" in completion
        and "information.si_pid == 0" in completion
        and "information.si_pid == leader_" in completion,
        "terminal_observation_is_exact_nonreaping_and_nonblocking",
        "completion evidence is tied to the owned leader while the zombie still pins numeric identity",
    )

    require(
        bool(completion)
        and ordered(
            completion,
            "information.si_pid == leader_",
            "::kill(-process_group_, SIGKILL)",
            "const pid_t exact_leader = leader_",
            "::waitpid(exact_leader, &status, 0)",
            "relinquish_numeric_authority_noexcept();",
            "return status",
        ),
        "success_observes_then_signals_then_reaps_then_consumes",
        "the exact waitable leader pins group identity until signaling; both numeric identifiers are cleared before status escapes",
    )

    require(
        completion.count("wait_error == ECHILD") >= 2
        and completion.count("relinquish_numeric_authority_noexcept();") >= 3
        and ordered(
            source,
            "void TestProcessTopologyOwner::relinquish_numeric_authority_noexcept() noexcept",
            "leader_ = -1",
            "process_group_ = -1",
        ),
        "echild_relinquishes_pid_and_group_together",
        "external reap denies later signaling through either potentially reusable numeric identifier",
    )

    throwing_cleanup = block_between(
        source,
        "void TestProcessTopologyOwner::terminate_and_reap_or_throw(",
        "void TestProcessTopologyOwner::terminate_and_reap_noexcept() noexcept",
    )
    noexcept_cleanup = block_between(
        source,
        "void TestProcessTopologyOwner::terminate_and_reap_noexcept() noexcept",
        "void TestProcessTopologyOwner::relinquish_numeric_authority_noexcept() noexcept",
    )
    require(
        all(
            bool(block)
            and ordered(
                block,
                "std::exchange(leader_, -1)",
                "std::exchange(process_group_, -1)",
                "::kill(-process_group, SIGKILL)",
                "::kill(leader, SIGKILL)",
                "::waitpid(leader, &status, 0)",
            )
            for block in (throwing_cleanup, noexcept_cleanup)
        ),
        "cleanup_consumes_authority_before_signal_or_wait",
        "teardown cannot retain or re-enter numeric authority after any partial cleanup outcome",
    )

    inherited_capture = block_between(
        inherited_source,
        "InheritedTestProcessOutput InheritedTestProcess::wait_for_exit_with_output(",
        "InheritedTestProcess detail_spawn_inherited_test_process_or_throw(",
    )
    selfexec_capture = block_between(
        selfexec_source,
        "SelfExecTestProcessOutput SelfExecTestProcess::wait_for_exact_exit_with_output(",
        "fs::path current_self_executable_or_throw()",
    )
    require(
        all(
            bool(block)
            and "bool leader_completed = false" in block
            and "topology_.try_complete_exit_or_throw(label)" in block
            and "topology_.terminate_and_reap_noexcept()" in block
            and "pid_t process_group" not in block
            and "const pid_t completed" not in block
            and direct_lifecycle.search(block) is None
            for block in (inherited_capture, selfexec_capture)
        ),
        "post_reap_drain_paths_cache_no_numeric_group",
        "after exact reap, EOF/overflow/poll/timeout handling can close descriptors but cannot signal a cached numeric group",
    )

    require(
        inherited_source.count("topology_.try_complete_exit_or_throw(label)") == 2
        and selfexec_source.count("topology_.try_complete_exit_or_throw(label)") == 2
        and "topology_.terminate_and_reap_or_throw(" in selfexec_source
        and all(
            "topology_.terminate_and_reap_noexcept()" in wrapper
            for wrapper in (inherited_source, selfexec_source)
        ),
        "both_wrappers_delegate_every_terminal_transition",
        "plain wait, captured wait, timeout, exception, destructor, and move displacement share one lifecycle implementation",
    )

    require(
        all(
            token in inherited_runtime
            for token in (
                "test_post_reap_capture_timeout_consumes_group_authority",
                "inherited post-reap capture authority",
                "timed out while collecting inherited output",
                "::getpgid(escaped) == escaped",
            )
        )
        and all(
            token in selfexec_runtime
            for token in (
                "test_post_reap_capture_timeout_consumes_group_authority",
                "return-with-escaped-capture-descendant",
                "timed out while draining captured output",
                "::getpgid(escaped) == escaped",
            )
        )
        and inherited_runtime.count("::alarm(kFixtureFailSafeSeconds)") == 4
        and selfexec_runtime.count("::alarm(kFixtureFailSafeSeconds)") == 4,
        "integration_oracles_hold_output_open_beyond_leader_reap",
        "both raw-fork and fresh-image wrappers cross the leader-reap/output-EOF frontier",
    )

    require(
        all(
            token in runtime
            for token in (
                "__wrap_kill",
                "__wrap_waitid",
                "__wrap_waitpid",
                "test_exact_completion_consumes_before_return",
                "cleanup after exact reap issued a stale numeric syscall",
                "test_external_reap_relinquishes_without_signal",
                "test_group_signal_error_reports_after_cleanup",
                "test_throwing_cleanup_consumes_before_syscalls",
                "test_move_transfers_one_topology",
            )
        )
        and runtime.count("script.require_complete();") >= 10,
        "deterministic_syscall_oracle_covers_success_and_error_traces",
        "the compiled owner is exercised without scheduler timing or PID reuse across pending, terminal, EINTR, ESRCH, ECHILD, hard-error, impossible-result, cleanup, and move traces",
    )

    require(
        all(
            token in cmake
            for token in (
                "add_library(anonsync_test_process_topology_owner STATIC",
                "tests/test_process_topology_owner.cpp",
                "target_link_libraries(anonsync_inherited_test_process PRIVATE\n    anonsync_test_process_topology_owner)",
                "target_link_libraries(anonsync_self_exec_test_process PRIVATE\n    anonsync_test_process_topology_owner)",
                "test process topology owner must remain dependency-free",
                "inherited test process must depend only on the topology owner",
                "self-exec test process must depend only on the topology owner",
            )
        ),
        "compiled_owner_is_one_dependency_free_leaf",
        "both wrappers have exactly one reviewed lifecycle dependency and the common implementation has none",
    )

    require(
        all(
            token in cmake
            for token in (
                "add_executable(anonsync_test_process_topology_owner_test",
                "tests/test_process_topology_owner_test.cpp",
                "-Wl,--wrap=kill",
                "-Wl,--wrap=waitid",
                "-Wl,--wrap=waitpid",
                "add_test(NAME anonsync_test_process_topology_owner_test",
                "add_test(NAME anonsync_test_process_topology_owner_source_audit",
            )
        ),
        "runtime_and_source_oracles_are_bounded_ctest_gates",
        "neither compiled transition behavior nor structural ownership can silently disappear from release validation",
    )

    require(
        "anonsync_test_process_topology_owner" in block_between(
            cmake,
            "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
            "include(CTest)",
        )
        and "anonsync_test_process_topology_owner_test" in block_between(
            cmake,
            "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
            "include(CTest)",
        ),
        "common_owner_and_oracle_are_in_sanitizer_lane",
        "focused ASan/UBSan validation instruments the compiled owner and its scripted transition oracle",
    )

    require(
        all(
            path in verifier
            for path in (
                "tests/test_process_topology_owner.hpp",
                "tests/test_process_topology_owner.cpp",
                "tests/test_process_topology_owner_test.cpp",
                "tools/audit_test_process_topology_owner.py",
            )
        ),
        "release_verifier_requires_owner_implementation_and_oracles",
        "a sealed cube cannot omit the contract, compiled implementation, runtime oracle, or structural audit",
    )

    require(
        len(audit_source.splitlines()) >= 350
        and all(
            token in audit_source
            for token in (
                "all_signal_wait_and_reap_syscalls_have_one_compiled_owner",
                "observation_and_completion_are_one_public_transition",
                "success_observes_then_signals_then_reaps_then_consumes",
                "post_reap_drain_paths_cache_no_numeric_group",
                "deterministic_syscall_oracle_covers_success_and_error_traces",
                "compiled_owner_is_one_dependency_free_leaf",
            )
        ),
        "audit_is_substantive_and_self_describing",
        "the gate proves API shape, ordering, exclusivity, failure transitions, integration fixtures, deterministic traces, build topology, sanitizer registration, and release inclusion",
    )

    metrics = {
        "topology_header_lines": len(header.splitlines()),
        "topology_source_lines": len(source.splitlines()),
        "topology_runtime_oracle_lines": len(runtime.splitlines()),
        "inherited_wrapper_lifecycle_syscalls": wrapper_lifecycle_sites[
            "tests/inherited_test_process.cpp"
        ],
        "self_exec_wrapper_lifecycle_syscalls": wrapper_lifecycle_sites[
            "tests/self_exec_test_process.cpp"
        ],
        "topology_owner_lifecycle_syscalls": source_lifecycle_sites,
        "runtime_script_completion_assertions": runtime.count(
            "script.require_complete();"
        ),
        "production_references": production_references,
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
