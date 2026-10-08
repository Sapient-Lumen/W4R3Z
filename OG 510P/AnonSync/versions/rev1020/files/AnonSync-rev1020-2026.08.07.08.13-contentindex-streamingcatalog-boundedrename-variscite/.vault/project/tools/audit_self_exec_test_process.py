#!/usr/bin/env python3
"""Fail-closed audit for the Linux test-only self-exec process boundary."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("tests/self_exec_test_process.hpp"),
    Path("tests/self_exec_test_process.cpp"),
    Path("tests/self_exec_test_process_test.cpp"),
    Path("tests/test_process_topology_owner.hpp"),
    Path("tests/test_process_topology_owner.cpp"),
    Path("tests/test_process_topology_owner_test.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp"),
    Path("tests/sync_atomic_file_publication_test.cpp"),
    Path("tests/sync_atomic_file_publication_cutpoint_test.cpp"),
    Path("tests/sqlite_runtime_payload_store_test.cpp"),
    Path("tests/peer_ingress_schema_attestation_test.cpp"),
    Path("tests/sqlite_transaction_allocator_fault_test.cpp"),
    Path("tests/sqlite_connection_authority_test.cpp"),
    Path("tests/sqlite_owner_generation_borrow_test.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tools/audit_raw_fork_boundaries.py"),
    Path("tools/audit_sqlite_transaction_allocator_fault.py"),
    Path("tools/audit_self_exec_test_process.py"),
    Path("tools/audit_test_process_topology_owner.py"),
    Path("tools/audit_sqlite_replay_ledger_reset.py"),
    Path("tools/audit_sqlite_replay_ledger_reset_crash_frontier.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def block_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def report_missing(root: Path, missing: list[str], output: Path | None) -> int:
    report = {
        "format": "anonsync-self-exec-test-process-audit-v10",
        "root": str(root),
        "passed": False,
        "passed_checks": 0,
        "total_checks": 0,
        "checks": [],
        "violations": [f"missing required file: {path}" for path in missing],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 2


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
    if missing:
        return report_missing(root, missing, args.json)

    text = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = text[Path("CMakeLists.txt")]
    header = text[Path("tests/self_exec_test_process.hpp")]
    source = text[Path("tests/self_exec_test_process.cpp")]
    runtime_test = text[Path("tests/self_exec_test_process_test.cpp")]
    topology_header = text[Path("tests/test_process_topology_owner.hpp")]
    topology = text[Path("tests/test_process_topology_owner.cpp")]
    topology_runtime = text[Path("tests/test_process_topology_owner_test.cpp")]
    reset_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp")]
    frontier_test = text[
        Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp")
    ]
    atomic_test = text[Path("tests/sync_atomic_file_publication_test.cpp")]
    atomic_cutpoint_test = text[
        Path("tests/sync_atomic_file_publication_cutpoint_test.cpp")
    ]
    payload_test = text[Path("tests/sqlite_runtime_payload_store_test.cpp")]
    peer_schema_test = text[Path("tests/peer_ingress_schema_attestation_test.cpp")]
    allocator_fault_test = text[
        Path("tests/sqlite_transaction_allocator_fault_test.cpp")
    ]
    connection_authority_test = text[
        Path("tests/sqlite_connection_authority_test.cpp")
    ]
    owner_generation_test = text[
        Path("tests/sqlite_owner_generation_borrow_test.cpp")
    ]
    replica_sqlite_owner_test = text[Path("tests/sync_replica_sqlite_owner_test.cpp")]
    raw_fork_audit = text[Path("tools/audit_raw_fork_boundaries.py")]
    allocator_fault_audit = text[
        Path("tools/audit_sqlite_transaction_allocator_fault.py")
    ]
    reset_audit = text[Path("tools/audit_sqlite_replay_ledger_reset.py")]
    frontier_audit = text[
        Path("tools/audit_sqlite_replay_ledger_reset_crash_frontier.py")
    ]
    audit_source = text[Path("tools/audit_self_exec_test_process.py")]
    topology_audit = text[Path("tools/audit_test_process_topology_owner.py")]
    verifier = text[Path("tools/verify_release_package.py")]
    checks: list[Check] = []

    production_references: list[str] = []
    for directory in (root / "src", root / "include"):
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in {".c", ".cc", ".cpp", ".h", ".hpp"}:
                if "self_exec_test_process" in path.read_text(
                    encoding="utf-8", errors="replace"
                ):
                    production_references.append(path.relative_to(root).as_posix())
    require(
        checks,
        not production_references
        and "namespace anonsync::test" in header
        and "namespace anonsync::test" in source,
        "support_is_test_only_and_absent_from_production",
        "the process harness is owned by tests/ and no production translation unit can depend on it",
    )

    require(
        checks,
        all(
            token in header
            for token in (
                "struct SelfExecTestProcessOutput final",
                "class SelfExecTestProcess final",
                "SelfExecTestProcess(const SelfExecTestProcess&) = delete",
                "operator=(const SelfExecTestProcess&) = delete",
                "SelfExecTestProcess(SelfExecTestProcess&& other) noexcept",
                "~SelfExecTestProcess()",
                "wait_for_exit_code(",
                "wait_for_exact_exit_with_output(",
                '#include "test_process_topology_owner.hpp"',
                "detail::TestProcessTopologyOwner topology_",
                "int stdout_read_ = -1",
                "int stderr_read_ = -1",
            )
        )
        and "stdout_read_(std::exchange(other.stdout_read_, -1))" in source
        and "stderr_read_(std::exchange(other.stderr_read_, -1))" in source,
        "process_and_capture_owner_is_move_only_raii",
        "one move-only wrapper jointly owns the shared leader/group capability and any two capture descriptors; copy cannot duplicate kill, reap, read, or close authority",
    )
    terminate_owner = block_between(
        source,
        "void SelfExecTestProcess::terminate_and_reap_noexcept()",
        "void SelfExecTestProcess::close_output_capture_noexcept()",
    )
    require(
        checks,
        ordered(
            source,
            "SelfExecTestProcess::~SelfExecTestProcess()",
            "terminate_and_reap_noexcept();",
        )
        and bool(terminate_owner)
        and ordered(
            terminate_owner,
            "topology_.terminate_and_reap_noexcept();",
            "close_output_capture_noexcept();",
        ),
        "destructor_consumes_process_and_capture_authority",
        "abandoned helpers and descendants are consumed by the common topology owner before both capture descriptors are single-consumption closed",
    )

    require(
        checks,
        '::readlink("/proc/self/exe"' in source
        and "fs::canonical(executable, error)" in source
        and "fs::is_regular_file(canonical, error)" in source
        and "requested_path.find('\\0')" in source
        and "pin_current_executable_or_throw(canonical)" in source
        and "O_NOFOLLOW" in source
        and "same_file_identity(pinned_status, running_status)" in source
        and "posix_spawnp" not in source
        and 'getenv("PATH")' not in source
        and "argv[0]" not in source,
        "self_executable_is_nul_fenced_and_object_bound",
        "helper execution pins the exact current image rather than trusting an aliasable argv[0], PATH lookup, or pathname-only check",
    )
    require(
        checks,
        all(
            token in source
            for token in (
                "kMaximumArgumentCount",
                "kMaximumArgumentBytes",
                "kMaximumSingleArgumentBytes",
                "argument.find('\\0')",
                "kMaximumEnvironmentBytes",
            )
        ),
        "argv_and_environment_have_explicit_budgets",
        "untrusted helper instructions cannot create unbounded argv/environment allocations",
    )

    require(
        checks,
        "::posix_spawn(" in source
        and "::fork(" not in source
        and re.search(r"(?<![A-Za-z0-9_])fork\s*\(", source) is None
        and "::system(" not in source
        and "::popen(" not in source,
        "spawn_boundary_contains_no_application_postfork_path",
        "the parent delegates process creation to posix_spawn and never runs project C++ in a raw post-fork child",
    )
    require(
        checks,
        "make_non_cloexec_sentinel_or_throw" in source
        and "F_SETFD, 0" in source
        and "posix_spawn_file_actions_adddup2" in source
        and "actions.add_dup2(pinned_executable.get()," in source
        and "posix_spawn_file_actions_addclosefrom_np" in source
        and "actions.add_close_from(kFirstSanitizedDescriptor)" in source
        and "concurrent parent opens" in source,
        "pinned_exec_and_closefrom_cover_descriptor_races",
        "descriptor 3 pins the exact image while a deliberate non-CLOEXEC sentinel and closefrom prove every unrelated descriptor is removed",
    )
    child_boundary = block_between(
        source,
        "void verify_self_exec_child_boundary_or_throw()",
        "}  // namespace anonsync::test",
    )
    require(
        checks,
        bool(child_boundary)
        and "descriptor <= 2" in child_boundary
        and "F_GETFD" in child_boundary
        and "::fstat(kPinnedExecutableDescriptor" in child_boundary
        and "same_file_identity(pinned_status, running_status)" in child_boundary
        and "::close(kPinnedExecutableDescriptor)" in child_boundary
        and "open_nonstandard_descriptors_or_throw()" in child_boundary
        and "if (!descriptors.empty())" in child_boundary
        and "inherited non-standard descriptors" in child_boundary,
        "child_consumes_pinned_image_then_rejects_descriptor_leaks",
        "the exec image proves descriptor 3 names itself, consumes it, verifies stdin/stdout/stderr, and denies every remaining leaked descriptor",
    )

    require(
        checks,
        "retrying close() after EINTR" in source
        and "const int descriptor = std::exchange(descriptor_, -1)" in source
        and "while (::close(descriptor_)" not in source,
        "descriptor_close_consumes_authority_once",
        "the move-only descriptor owner cannot retry close after EINTR and accidentally close a concurrently reused descriptor number",
    )

    capture_pipe = block_between(
        source,
        "[[nodiscard]] CapturePipe make_capture_pipe_or_throw(",
        "[[nodiscard]] bool same_file_identity(",
    )
    capture_spawn = block_between(
        source,
        "spawn_self_exec_test_process_components_or_throw(",
        "SelfExecTestProcess spawn_self_exec_test_process_or_throw(",
    )
    require(
        checks,
        bool(capture_pipe)
        and "::pipe2(raw_descriptors, O_CLOEXEC)" in capture_pipe
        and "O_CLOEXEC | O_NONBLOCK" not in capture_pipe
        and "pipe.read_end.get(), F_GETFL" in capture_pipe
        and "pipe.read_end.get(), F_SETFL, flags | O_NONBLOCK" in capture_pipe
        and "pipe.write_end.get(), F_SETFL" not in capture_pipe
        and bool(capture_spawn)
        and "actions.add_dup2(stdout_pipe->write_end.get(), STDOUT_FILENO)" in capture_spawn
        and "actions.add_dup2(stderr_pipe->write_end.get(), STDERR_FILENO)" in capture_spawn
        and ordered(
            capture_spawn,
            "actions.add_dup2(stdout_pipe->write_end.get(), STDOUT_FILENO)",
            "actions.add_dup2(stderr_pipe->write_end.get(), STDERR_FILENO)",
            "actions.add_close_from(kFirstSanitizedDescriptor)",
            "::posix_spawn(",
            "stdout_pipe->read_end.release()",
            "stderr_pipe->read_end.release()",
        ),
        "capture_pipes_keep_child_writes_blocking_and_parent_reads_nonblocking",
        "close-on-exec pipes are promoted before spawn; only parent read ends become nonblocking, exact stdout/stderr dup2 actions precede closefrom, and ownership transfers only after successful spawn",
    )

    require(
        checks,
        'environment.emplace_back("LC_ALL=C")' in source
        and 'environment.emplace_back("TZ=UTC")' in source
        and "kPropagatedEnvironmentNames" in source
        and "envp.data()" in source
        and "environ" not in source[source.find("::posix_spawn("):source.find("::posix_spawn(") + 500],
        "child_environment_is_constructed_not_inherited",
        "only canonical locale/timezone and sanitizer diagnostics cross the exec boundary",
    )
    require(
        checks,
        bool(child_boundary)
        and "is_allowed_environment_name(name)" in child_boundary
        and 'name == "LC_ALL"' in child_boundary
        and 'value != "C"' in child_boundary
        and 'name == "TZ"' in child_boundary
        and 'value != "UTC"' in child_boundary,
        "child_reverifies_exact_environment_contract",
        "helper mode denies extra names, duplicate canonical names, and noncanonical locale/timezone values",
    )

    require(
        checks,
        all(
            token in source
            for token in (
                "posix_spawnattr_setsigmask",
                "posix_spawnattr_setsigdefault",
                "POSIX_SPAWN_SETSIGMASK",
                "POSIX_SPAWN_SETSIGDEF",
                "sigaction(SIGUSR1, nullptr",
                "user_signal_action.sa_handler != SIG_DFL",
                "sigprocmask(SIG_SETMASK, nullptr",
                "sigismember(&current_mask",
            )
        ),
        "signal_mask_and_disposition_boundary_is_executable",
        "spawn requests defaults and an empty mask; helper mode verifies both a deliberately ignored disposition and a deliberately blocked signal were reset",
    )
    require(
        checks,
        "posix_spawnattr_setpgroup(&attributes_, 0)" in source
        and "POSIX_SPAWN_SETPGROUP" in source
        and "::getpgrp() != ::getpid()" in child_boundary
        and "::kill(-process_group, SIGKILL)" in topology,
        "helper_has_isolated_killable_process_group",
        "timeouts target the helper group and the child proves it is that group leader",
    )

    exit_code_wait = block_between(
        source,
        "int SelfExecTestProcess::wait_for_exit_code(",
        "void SelfExecTestProcess::wait_for_exact_exit(",
    )
    exact_wait = block_between(
        source,
        "void SelfExecTestProcess::wait_for_exact_exit(",
        "SelfExecTestProcessOutput SelfExecTestProcess::wait_for_exact_exit_with_output(",
    )
    require(
        checks,
        bool(exit_code_wait)
        and "timeout <= std::chrono::milliseconds::zero()" in exit_code_wait
        and "std::chrono::steady_clock::now() + timeout" in exit_code_wait
        and "topology_.try_complete_exit_or_throw(label)" in exit_code_wait
        and "WIFEXITED(*status)" in exit_code_wait
        and "return WEXITSTATUS(*status);" in exit_code_wait
        and bool(exact_wait)
        and "expected_exit < 0 || expected_exit > 255" in exact_wait
        and "wait_for_exit_code(timeout, label)" in exact_wait
        and "observed_exit != expected_exit" in exact_wait,
        "wait_is_bounded_and_exact_status_typed",
        "one bounded owner returns a reviewed normal status; the exact-status adapter validates and compares its byte-sized expectation",
    )
    require(
        checks,
        bool(exit_code_wait)
        and "topology_.terminate_and_reap_or_throw(" in exit_code_wait
        and "timed out and was killed and reaped" in exit_code_wait
        and "std::exchange(leader_, -1)" in topology
        and "std::exchange(process_group_, -1)" in topology,
        "wait_errors_and_timeouts_consume_process_authority",
        "every non-success wait path delegates to one owner that consumes leader and group authority before kill/reap",
    )

    capture_wait = block_between(
        source,
        "SelfExecTestProcessOutput SelfExecTestProcess::wait_for_exact_exit_with_output(",
        "fs::path current_self_executable_or_throw()",
    )
    require(
        checks,
        bool(capture_wait)
        and "maximum_bytes_per_stream == 0" in capture_wait
        and "maximum_bytes_per_stream > kMaximumCaptureBytesPerStream" in capture_wait
        and capture_wait.count("drain_capture_descriptor_or_throw(") == 2
        and "topology_.try_complete_exit_or_throw(label)" in capture_wait
        and "bool leader_completed = false" in capture_wait
        and "std::chrono::steady_clock::now() + timeout" in capture_wait
        and "::poll(" in capture_wait
        and "POLLIN" in capture_wait
        and "POLLNVAL" in capture_wait
        and "leader_completed && stdout_read_ < 0 && stderr_read_ < 0" in capture_wait,
        "capture_wait_drains_both_streams_under_one_deadline",
        "stdout and stderr are multiplexed while the child runs, bounded independently, and completion requires both exact leader status and EOF on both streams",
    )
    require(
        checks,
        bool(capture_wait)
        and "topology_.terminate_and_reap_noexcept();" in capture_wait
        and "close_output_capture_noexcept();" in capture_wait
        and "pid_t process_group" not in capture_wait
        and "const pid_t completed" not in capture_wait
        and "captured_output_context(output)" in capture_wait,
        "capture_failures_consume_authority_and_status_errors_preserve_evidence",
        "pre-reap failures kill/reap/close through the common owner; post-reap failures close only descriptors; nonzero status preserves bounded output evidence",
    )

    require(
        checks,
        all(
            token in runtime_test
            for token in (
                "--anonsync-self-exec-test-helper-v1",
                "verify_self_exec_child_boundary_or_throw();",
                "return-exact",
                "kSuccessExit",
                "child.process_id() > 0",
                "SelfExecTestProcess transferred(std::move(child))",
                "!child.active() && transferred.active()",
                "!transferred.active()",
                "test_move_assignment_consumes_displaced_owner",
                "displaced = std::move(replacement)",
                "displaced.process_id() == replacement_pid",
            )
        ),
        "runtime_oracle_proves_exec_boundary_and_exact_exit",
        "the support test enters a versioned helper mode and proves move construction, destructive move assignment, and exact consumed-owner transitions",
    )
    require(
        checks,
        all(
            token in runtime_test
            for token in (
                "hang-until-parent-kills",
                "75ms",
                "timed out and was killed and reaped",
                "does-not-exist",
                "aliased.push_back('\\0')",
                'fs::path("/bin/sh")',
                "std::string(4097, 'x')",
                'std::string("ok\\0hidden", 9)',
                "ANONSYNC_SELF_EXEC_PARENT_LEAK",
                "sigaction(SIGUSR1, &ignored",
                "sigaddset(&blocked, SIGUSR2)",
                "test_destructor_kills_and_reaps",
                "errno == ECHILD",
            )
        ),
        "runtime_oracle_exercises_identity_signal_environment_and_input_denials",
        "runtime proof covers pinned-image identity, NUL aliases, environment and signal sanitation, timeout/destructor reap, and argument budgets",
    )

    require(
        checks,
        all(
            token in runtime_test
            for token in (
                "emit-captured",
                "emit-large-captured",
                "F_GETPIPE_SZ",
                "static_cast<std::size_t>(stdout_capacity) + 4096",
                "static_cast<std::size_t>(stderr_capacity) + 4096",
                "wait_for_exact_exit_with_output(",
                "stdout-evidence",
                "stderr-evidence",
                "test_large_capture_drains_while_child_runs",
                "capture byte budget did not reject",
                "capture-aware wait did not enforce its monotonic deadline",
                "test_post_reap_capture_timeout_consumes_group_authority",
                "return-with-escaped-capture-descendant",
                "timed out while draining captured output",
                "test_wait_api_mode_mismatch_is_fail_closed",
                "count_parent_open_descriptors_or_throw",
                "capture paths leaked a parent descriptor",
                "kFixtureFailSafeSeconds",
            )
        )
        and runtime_test.count("::alarm(kFixtureFailSafeSeconds)") == 4,
        "runtime_oracle_proves_concurrent_bounded_separate_capture",
        "the executable oracle distinguishes streams, writes beyond each measured pipe capacity, detects parent descriptor residue, and proves overflow, ordinary timeout, post-reap drain timeout, and wait-mode misuse fail closed",
    )

    require(
        checks,
        "std::optional<int> try_complete_exit_or_throw(" in topology_header
        and "WEXITED | WNOHANG | WNOWAIT" in topology
        and "::kill(-process_group_, SIGKILL)" in topology
        and "::waitpid(exact_leader, &status, 0)" in topology
        and ordered(
            topology,
            "information.si_pid == leader_",
            "::kill(-process_group_, SIGKILL)",
            "::waitpid(exact_leader, &status, 0)",
            "relinquish_numeric_authority_noexcept();",
            "return status",
        )
        and "cleanup after exact reap issued a stale numeric syscall" in topology_runtime
        and all(
            token in runtime_test
            for token in (
                "test_successful_exit_kills_remaining_group",
                "ScopedChildSubreaper",
                "return-with-lingering-descendant",
                "parse_exact_descendant_report_or_throw",
                "reap_exact_sigkill_bounded",
            )
        ),
        "successful_wait_kills_identity_bound_group_before_reap",
        "both plain and captured waits preserve leader identity with WNOWAIT, kill remaining group members, reap exactly once, then consume PID/group authority before any further pipe work",
    )

    additional_campaigns = (
        (
            atomic_test,
            "--anonsync-atomic-publication-writer-helper-v1",
            "wait_for_exact_exit(",
            "atomic same-payload process campaign",
        ),
        (
            atomic_cutpoint_test,
            "--anonsync-atomic-publication-crash-helper-v1",
            "wait_for_exact_exit(",
            "atomic publication crash frontier",
        ),
        (
            payload_test,
            "--anonsync-payload-crash-helper-v1",
            "wait_for_exact_exit(",
            "SQLite payload commit/rollback crash campaign",
        ),
        (
            peer_schema_test,
            "--anonsync-peer-schema-owner-close-helper-v1",
            "wait_for_exact_exit(",
            "peer-schema owner-close fail-stop probe",
        ),
        (
            connection_authority_test,
            "--anonsync-sqlite-connection-authority-affinity-worker-v1",
            "wait_for_exit_code(",
            "SQLite connection-affinity fail-stop campaign",
        ),
        (
            owner_generation_test,
            "--anonsync-sqlite-owner-generation-borrow-close-worker-v1",
            "wait_for_exit_code(",
            "SQLite owner-generation borrow/close race campaign",
        ),
        (
            replica_sqlite_owner_test,
            "--anonsync-replica-sqlite-owner-crash-helper-v1",
            "wait_for_exact_exit(",
            "replica SQLite publication cutpoint crash campaign",
        ),
    )
    require(
        checks,
        all(
            '#include "self_exec_test_process.hpp"' in body
            and helper_flag in body
            and "verify_self_exec_child_boundary_or_throw();" in body
            and "spawn_self_exec_test_process_or_throw(" in body
            and wait_token in body
            and "::fork(" not in body
            and "::waitpid(" not in body
            for body, helper_flag, wait_token, _ in additional_campaigns
        ),
        "seven_non_capture_campaigns_use_fresh_images",
        "; ".join(label for _, _, _, label in additional_campaigns),
    )
    require(
        checks,
        '#include "self_exec_test_process.hpp"' in allocator_fault_test
        and "--anonsync-sqlite-transaction-allocator-fault-worker-v1"
        in allocator_fault_test
        and "verify_self_exec_child_boundary_or_throw();"
        in allocator_fault_test
        and "spawn_self_exec_test_process_with_output_capture_or_throw("
        in allocator_fault_test
        and "wait_for_exact_exit_with_output(" in allocator_fault_test
        and "kWorkerCaptureBytesPerStream = 16U * 1024U" in allocator_fault_test
        and "kWorkerTimeout = 5s" in allocator_fault_test
        and "!output.standard_error.empty()" in allocator_fault_test
        and "::fork(" not in allocator_fault_test
        and "::pipe(" not in allocator_fault_test
        and "::dup2(" not in allocator_fault_test
        and "::waitpid(" not in allocator_fault_test
        and "allocator_fault_campaign_uses_fresh_image_capture" in allocator_fault_audit,
        "allocator_campaign_uses_bounded_capture_owner",
        "all 318 allocator workers enter the pinned fresh image and return parseable stdout under independent stderr, byte, deadline, process-group, and reap authority",
    )

    require(
        checks,
        "EXPECTED_TEST_CALLS" in raw_fork_audit
        and "production_contains_no_raw_fork_calls" in raw_fork_audit
        and "one_raw_fork_is_owned_by_the_shared_test_boundary" in raw_fork_audit
        and "discovered_inherited_state_consumers_match_the_exact_inventory"
        in raw_fork_audit
        and "eight_fresh_state_campaigns_use_pinned_self_exec_images"
        in raw_fork_audit
        and "inventory_metrics_are_exact" in raw_fork_audit
        and '"test_raw_fork_calls": 1' in raw_fork_audit
        and '"inherited_spawn_sites": 33' in raw_fork_audit,
        "raw_fork_inventory_is_fail_closed_and_exact",
        "a separately registered audit rejects any production raw fork, centralizes the sole test call, discovers every wrapper consumer, and classifies all 39 inherited or fresh-image process sites",
    )

    require(
        checks,
        '#include "self_exec_test_process.hpp"' in reset_test
        and "--anonsync-reset-focused-helper-v1" in reset_test
        and "argc != 7" in reset_test
        and "verify_self_exec_child_boundary_or_throw();" in reset_test
        and "::fork(" not in reset_test
        and "::waitpid(" not in reset_test,
        "focused_reset_failstop_cases_use_selfexec_only",
        "write-gate fail-stop and commit/report-loss probes cannot perform application work in a raw fork child",
    )
    reset_helper = block_between(
        reset_test,
        "int run_focused_reset_helper(int argc, char** argv)",
        "void test_streaming_digest(",
    )
    require(
        checks,
        bool(reset_helper)
        and ordered(
            reset_helper,
            "verify_self_exec_child_boundary_or_throw();",
            "parse_focused_helper_instruction_or_throw(argc, argv)",
            "inspect_sqlite_replay_ledger_reset_state(instruction.ledger_path)",
            "state.state_sha256 != instruction.expected_state_sha256",
            "sqlite_replay_ledger_reset_receipt_sha256(request) !=",
            "reset_sqlite_replay_ledger(request)",
        ),
        "focused_reset_helper_rebinds_parent_evidence_after_exec",
        "SQLite opens only after boundary verification and exact state/receipt evidence is reconstructed from the exec instruction",
    )

    require(
        checks,
        '#include "self_exec_test_process.hpp"' in frontier_test
        and "--anonsync-reset-receipt-crash-helper-v1" in frontier_test
        and "argc != 9" in frontier_test
        and "verify_self_exec_child_boundary_or_throw();" in frontier_test
        and "::fork(" not in frontier_test
        and "::waitpid(" not in frontier_test,
        "combined_crash_frontier_uses_selfexec_only",
        "the cross-resource crash oracle enters a fresh exec image for every selected cutpoint",
    )
    frontier_helper = block_between(
        frontier_test,
        "int run_crash_helper(int argc, char** argv)",
        "void recover_receipt_to_fresh_path(",
    )
    require(
        checks,
        bool(frontier_helper)
        and ordered(
            frontier_helper,
            "verify_self_exec_child_boundary_or_throw();",
            "parse_crash_helper_instruction_or_throw(argc, argv)",
            "bind_crash_helper_fixture_or_throw(instruction)",
            "SqliteReplayLedgerResetReceiptProtocolObserverAccess::",
            "execute_or_throw(",
        )
        and all(
            token in frontier_test
            for token in (
                "instruction.fixture_root.filename().generic_string()",
                "instruction.expected_state_sha256",
                "instruction.expected_receipt_sha256",
                "instruction.request_sha256",
                "parse_publication_index_or_throw",
            )
        ),
        "frontier_helper_rebinds_path_hashes_and_cutpoint_after_exec",
        "the fresh image proves exact root identity, state/receipt/request digests, and reviewed cutpoint index before executing production choreography",
    )
    require(
        checks,
        reset_test.count("wait_for_exact_exit(") >= 3
        and frontier_test.count("wait_for_exact_exit(") >= 2
        and reset_test.count("10s") >= 3
        and frontier_test.count("10s") >= 2,
        "critical_callers_use_positive_bounded_waits",
        "all migrated fail-stop and crash-frontier children have explicit parent deadlines",
    )

    require(
        checks,
        'if(CMAKE_SYSTEM_NAME STREQUAL "Linux")' in cmake
        and "add_library(anonsync_self_exec_test_process STATIC" in cmake
        and "tests/self_exec_test_process.cpp" in cmake
        and "add_executable(anonsync_self_exec_test_process_test" in cmake
        and "anonsync_self_exec_test_process)" in cmake
        and """target_link_libraries(
    anonsync_sqlite_transaction_allocator_fault_test PRIVATE
    anonsync_sqlite_support
    anonsync_self_exec_test_process)""" in cmake,
        "cmake_owns_linux_test_only_support_and_oracle",
        "the harness and runtime oracle are explicit Linux test targets rather than production-library sources",
    )
    require(
        checks,
        "ANONSYNC_SELF_EXEC_TEST_PROCESS_LINK_LIBRARIES" in cmake
        and "self-exec test process must depend only on the topology owner" in cmake
        and "test process topology owner must remain dependency-free" in cmake
        and "anonsync_test_process_topology_owner" in cmake[
            cmake.find("ANONSYNC_SANITIZER_COMPILE_TARGETS"):
        ]
        and "anonsync_self_exec_test_process" in cmake[
            cmake.find("ANONSYNC_SANITIZER_COMPILE_TARGETS"):
        ]
        and "target_link_options(anonsync_test_process_topology_owner_test PRIVATE" in cmake
        and "target_link_options(anonsync_self_exec_test_process_test PRIVATE" in cmake,
        "support_has_one_dependency_free_leaf_and_sanitizer_guards",
        "the wrapper depends only on the common topology leaf; the owner, scripted oracle, wrapper, and runtime oracle participate in sanitizer lanes",
    )
    require(
        checks,
        "add_test(NAME anonsync_self_exec_test_process_test" in cmake
        and "PROPERTIES TIMEOUT 20" in cmake
        and "add_test(NAME anonsync_self_exec_test_process_source_audit" in cmake
        and "audit_self_exec_test_process.py" in cmake
        and "add_test(NAME anonsync_test_process_topology_owner_source_audit" in cmake
        and "audit_test_process_topology_owner.py" in cmake,
        "runtime_and_structural_oracles_are_ctest_gates",
        "release CTest enforces both execution semantics and source topology with explicit time bounds",
    )

    require(
        checks,
        all(
            path in verifier
            for path in (
                "tests/self_exec_test_process.hpp",
                "tests/self_exec_test_process.cpp",
                "tests/self_exec_test_process_test.cpp",
                "tests/test_process_topology_owner.hpp",
                "tests/test_process_topology_owner.cpp",
                "tests/test_process_topology_owner_test.cpp",
                "tools/audit_self_exec_test_process.py",
                "tools/audit_test_process_topology_owner.py",
                "tools/audit_raw_fork_boundaries.py",
                "tests/sqlite_transaction_allocator_fault_test.cpp",
                "tools/audit_sqlite_transaction_allocator_fault.py",
            )
        ),
        "release_verifier_requires_entire_selfexec_surface",
        "a sealed cube cannot omit the owner, implementation, executable oracle, or structural audit",
    )
    require(
        checks,
        "self_exec" in reset_audit
        and "self_exec" in frontier_audit
        and "fork_oracle_spans_prepare_commit_publish_reopen" not in frontier_audit,
        "owner_audits_promote_selfexec_as_required_topology",
        "legacy reset audits must reject regressions back to direct post-fork application execution",
    )
    require(
        checks,
        len(audit_source.splitlines()) >= 300
        and all(
            token in audit_source
            for token in (
                "pinned_exec_and_closefrom_cover_descriptor_races",
                "descriptor_close_consumes_authority_once",
                "capture_pipes_keep_child_writes_blocking_and_parent_reads_nonblocking",
                "wait_errors_and_timeouts_consume_process_authority",
                "capture_wait_drains_both_streams_under_one_deadline",
                "capture_failures_consume_authority_and_status_errors_preserve_evidence",
                "runtime_oracle_proves_concurrent_bounded_separate_capture",
                "focused_reset_helper_rebinds_parent_evidence_after_exec",
                "frontier_helper_rebinds_path_hashes_and_cutpoint_after_exec",
                "release_verifier_requires_entire_selfexec_surface",
                "seven_non_capture_campaigns_use_fresh_images",
                "raw_fork_inventory_is_fail_closed_and_exact",
                "successful_wait_kills_identity_bound_group_before_reap",
                "support_has_one_dependency_free_leaf_and_sanitizer_guards",
                "test_process_topology_owner",
            )
        )
        and "post_reap_drain_paths_cache_no_numeric_group" in topology_audit,
        "audit_is_substantive_and_self_describing",
        "the structural gate cannot pass merely because the self-exec implementation disappeared",
    )

    raw_fork_files: list[str] = []
    for path in (root / "tests").rglob("*.cpp"):
        body = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?<![A-Za-z0-9_])(?:::)?fork\s*\(", body):
            raw_fork_files.append(path.relative_to(root).as_posix())

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-self-exec-test-process-audit-v10",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "header_lines": len(header.splitlines()),
            "implementation_lines": len(source.splitlines()),
            "runtime_test_lines": len(runtime_test.splitlines()),
            "audit_lines": len(audit_source.splitlines()),
            "shared_topology_owner_header_lines": len(topology_header.splitlines()),
            "shared_topology_owner_source_lines": len(topology.splitlines()),
            "shared_topology_owner_runtime_lines": len(topology_runtime.splitlines()),
            "remaining_raw_fork_translation_units": len(raw_fork_files),
            "remaining_raw_fork_files": sorted(raw_fork_files),
            "production_references": production_references,
        },
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
