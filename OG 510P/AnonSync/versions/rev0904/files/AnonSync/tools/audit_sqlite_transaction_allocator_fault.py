#!/usr/bin/env python3
"""Deterministic source audit for SQLite transaction allocator-fault recovery.

The runtime campaign proves compiled behavior under allocation cuts. This audit
binds the fresh-image process owner, concurrent bounded output capture,
allocator overlay, tri-state authority classification, retry/revocation split,
and removal of redundant sqlite3_exec() error-buffer ownership from the
reviewed runtime helpers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SENSITIVE_FILES = (
    Path("CMakeLists.txt"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_connection_authority_internal.hpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sync_sqlite_runtime.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("src/runner.cpp"),
    Path("tests/sqlite_transaction_allocator_fault_test.cpp"),
    Path("tests/self_exec_test_process.hpp"),
    Path("tests/self_exec_test_process.cpp"),
    Path("tests/test_process_topology_owner.hpp"),
    Path("tests/test_process_topology_owner.cpp"),
    Path("tools/audit_raw_fork_boundaries.py"),
    Path("tools/audit_sqlite_transaction_stack_authority.py"),
    Path("tools/audit_sqlite_transaction_exception_composition.py"),
    Path("tools/audit_sqlite_replay_ledger_schema_contract.py"),
    Path("tools/verify_release_package.py"),
)

RUNTIME_EXEC_HELPERS = (
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sync_sqlite_runtime.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("src/runner.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def segment(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start)) if begin >= 0 else -1
    if begin < 0 or finish < 0:
        return ""
    return text[begin:finish]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path, help="write deterministic JSON report")
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in SENSITIVE_FILES if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-transaction-allocator-fault-audit-v4",
            "root": str(root),
            "passed": False,
            "check_count": 0,
            "checks": [],
            "violations": [f"missing sensitive file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    texts = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in SENSITIVE_FILES
    }
    cmake = texts[Path("CMakeLists.txt")]
    authority = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    authority_internal = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    transaction = texts[Path("src/sync_sqlite_transaction.cpp")]
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    worker = texts[Path("tests/sqlite_transaction_allocator_fault_test.cpp")]
    self_exec_header = texts[Path("tests/self_exec_test_process.hpp")]
    self_exec_source = texts[Path("tests/self_exec_test_process.cpp")]
    topology_owner = texts[Path("tests/test_process_topology_owner.cpp")]
    raw_fork_audit = texts[Path("tools/audit_raw_fork_boundaries.py")]
    stack_audit = texts[Path("tools/audit_sqlite_transaction_stack_authority.py")]
    composition_audit = texts[
        Path("tools/audit_sqlite_transaction_exception_composition.py")
    ]
    schema_contract_audit = texts[
        Path("tools/audit_sqlite_replay_ledger_schema_contract.py")
    ]
    package_verifier = texts[Path("tools/verify_release_package.py")]

    checks: list[Check] = []

    target_section = segment(
        cmake,
        'if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND ANONSYNC_USE_BUNDLED_SQLITE)',
        "add_executable(anonsync_sqlite_process_authority_fork_test",
    )
    for needle, check_id in (
        ('if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND ANONSYNC_USE_BUNDLED_SQLITE)', "target_requires_linux_and_bundled_sqlite"),
        ("add_executable(anonsync_sqlite_transaction_allocator_fault_test", "allocator_campaign_target_exists"),
        ("tests/sqlite_transaction_allocator_fault_test.cpp", "allocator_campaign_source_is_compiled"),
        ("${CMAKE_CURRENT_SOURCE_DIR}/tests", "allocator_campaign_includes_test_owner_surface"),
        ("anonsync_sqlite_support", "allocator_campaign_links_reviewed_sqlite_owner"),
        ("anonsync_self_exec_test_process", "allocator_campaign_links_fresh_image_owner"),
        ("-Wall -Wextra -Wpedantic", "allocator_campaign_enables_warnings"),
    ):
        require(checks, needle in target_section, check_id, f"required target marker: {needle}")
    require(
        checks,
        "anonsync_core_lib" not in target_section,
        "allocator_campaign_avoids_unrelated_core_graph",
        "the focused worker links the SQLite support boundary, not the full application core",
    )
    require(
        checks,
        cmake.count("add_executable(anonsync_sqlite_transaction_allocator_fault_test") == 1,
        "allocator_campaign_target_is_singular",
        "one conditional target must own the process campaign",
    )
    for needle, check_id in (
        ("list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS\n      anonsync_sqlite_transaction_allocator_fault_test)", "allocator_campaign_is_sanitizer_compiled"),
        ("target_link_options(anonsync_sqlite_transaction_allocator_fault_test PRIVATE\n      -fsanitize=address,undefined)", "allocator_campaign_is_sanitizer_linked"),
        ("add_test(NAME anonsync_sqlite_transaction_allocator_fault_test", "allocator_campaign_is_registered_in_ctest"),
        ("set_tests_properties(anonsync_sqlite_transaction_allocator_fault_test\n    PROPERTIES TIMEOUT 120)", "allocator_campaign_has_bounded_ctest_timeout"),
        ("anonsync_sqlite_transaction_allocator_fault_source_audit", "allocator_source_audit_is_registered_in_ctest"),
        ("tools/audit_sqlite_transaction_allocator_fault.py", "allocator_source_audit_script_is_registered"),
    ):
        require(checks, needle in cmake, check_id, f"required CMake proof marker: {needle}")

    for needle, check_id in (
        ("enum class SyncSqliteBoundaryAuthorityStatus", "tri_state_authority_type_exists"),
        ("Current", "tri_state_has_current"),
        ("Invalid", "tri_state_has_invalid"),
        ("Indeterminate", "tri_state_has_indeterminate"),
        ("sync_sqlite_savepoint_boundary_authority_status_noexcept", "savepoint_status_api_exists"),
        ("sync_sqlite_transaction_boundary_authority_status_noexcept", "transaction_status_api_exists"),
    ):
        require(checks, needle in authority_internal, check_id, f"required tri-state marker: {needle}")

    classifier = segment(
        authority,
        "SyncSqliteBoundaryAuthorityStatus classify_authorizer_observation_noexcept(",
        "void run_authorizer_ownership_probe_or_throw(",
    )
    require(
        checks,
        ordered(
            classifier,
            "if (observation.callback_observed)",
            "observation.prepare_result == SQLITE_OK",
            "observation.statement_produced",
            "observation.finalize_result == SQLITE_OK",
            "SyncSqliteBoundaryAuthorityStatus::Current",
        ),
        "current_requires_observed_completed_probe",
        "Current requires the exact callback plus successful prepare, statement production, and finalize",
    )
    for result in (
        "SQLITE_NOMEM",
        "SQLITE_BUSY",
        "SQLITE_LOCKED",
        "SQLITE_INTERRUPT",
        "SQLITE_IOERR",
        "SQLITE_FULL",
        "SQLITE_CANTOPEN",
        "SQLITE_PROTOCOL",
        "SQLITE_ABORT",
    ):
        require(
            checks,
            result in classifier,
            "indeterminate_classifies_" + result.lower(),
            f"resource/transient result remains retryable uncertainty: {result}",
        )
    require(
        checks,
        "return SyncSqliteBoundaryAuthorityStatus::Invalid;" in classifier,
        "deterministic_probe_failure_is_invalid",
        "absence of the exact callback without a transient result cannot preserve authority",
    )
    require(
        checks,
        authority.count("observe_authorizer_ownership_noexcept(") >= 4,
        "throwing_and_noexcept_paths_share_probe_observation",
        "one observation primitive feeds the normal probe and both use-time status paths",
    )
    require(
        checks,
        authority.count("SyncSqliteBoundaryAuthorityStatus::Indeterminate") >= 6,
        "indeterminate_is_explicit_through_owner",
        "resource uncertainty must not collapse back into a boolean owner test",
    )
    require(
        checks,
        authority.count("==\n           SyncSqliteBoundaryAuthorityStatus::Current") == 2,
        "boolean_compatibility_wrappers_grant_only_current",
        "legacy bool queries may authorize only the exact Current state",
    )

    authority_query = segment(
        transaction,
        "bool SyncSqliteTransactionAuthority::authorizes(",
        "bool SyncSqliteTransactionAuthority::authorizes_snapshot(",
    )
    require(
        checks,
        "if (status == SyncSqliteBoundaryAuthorityStatus::Invalid)" in authority_query,
        "authority_handle_revokes_only_invalid",
        "an indeterminate probe fails this use without poisoning the retained generation",
    )
    require(
        checks,
        "return status == SyncSqliteBoundaryAuthorityStatus::Current;" in authority_query,
        "authority_handle_fails_closed_when_not_current",
        "both Invalid and Indeterminate must deny the current use",
    )
    require(
        checks,
        transaction.count("boundary ownership could not be revalidated; retry is required") == 4,
        "four_mutating_preflights_expose_retryable_uncertainty",
        "commit, rollback, release, and savepoint rollback distinguish Indeterminate",
    )
    require(
        checks,
        transaction.count("==\n            SyncSqliteBoundaryAuthorityStatus::Invalid") >= 4,
        "catch_paths_revoke_only_observed_invalidity",
        "post-effect exceptions preserve a still-live exact generation when revalidation is indeterminate",
    )
    require(
        checks,
        "if (!sync_sqlite_transaction_boundary_authorizes_noexcept" not in transaction
        and "if (!sync_sqlite_savepoint_boundary_authorizes_noexcept" not in transaction,
        "mutating_paths_do_not_conflate_false_with_revocation",
        "the old boolean catch/preflight pattern must not return",
    )
    require(
        checks,
        "indeterminate false result" in support_hpp
        and "Only observed end/supersession/replacement revokes it" in support_hpp,
        "public_authority_contract_documents_indeterminate_retry",
        "callers are told that fail-closed false does not always mean permanent revocation",
    )

    for needle, check_id in (
        ("SQLITE_CONFIG_GETMALLOC", "worker_reads_exact_base_allocator"),
        ("SQLITE_CONFIG_MALLOC", "worker_installs_allocator_overlay"),
        ("sqlite3_initialize()", "worker_initializes_after_configuration"),
        ("sqlite3_shutdown()", "worker_owns_global_sqlite_lifecycle"),
        ("fault_malloc", "worker_wraps_malloc"),
        ("fault_free", "worker_wraps_free"),
        ("fault_realloc", "worker_wraps_realloc"),
        ("fault_size", "worker_wraps_size"),
        ("fault_roundup", "worker_wraps_roundup"),
        ("fault_init", "worker_wraps_init"),
        ("fault_shutdown", "worker_wraps_shutdown"),
        ("live_blocks", "worker_tracks_live_blocks"),
        ("live_bytes", "worker_tracks_live_bytes"),
        ("accounting_corrupt", "worker_detects_accounting_underflow"),
    ):
        require(checks, needle in worker, check_id, f"required allocator marker: {needle}")
    require(
        checks,
        ordered(
            worker,
            "sqlite3_shutdown()",
            "SQLITE_CONFIG_GETMALLOC",
            "SQLITE_CONFIG_MALLOC",
            "sqlite3_initialize()",
        ),
        "allocator_overlay_is_installed_before_initialization",
        "SQLite global allocator configuration is startup-sensitive",
    )
    require(
        checks,
        ordered(
            segment(worker, "void shutdown_or_throw()", "FaultAllocatorRuntime(const"),
            "g_allocator.armed = false",
            "sqlite3_shutdown()",
            "g_allocator.live_blocks != 0",
            "g_allocator.live_bytes != 0",
        ),
        "worker_proves_overlay_allocations_are_released",
        "shutdown is followed by explicit live-block and live-byte accounting checks",
    )
    require(
        checks,
        "g_allocator.sticky\n                              ? g_allocator.attempts >= g_allocator.fail_at\n                              : g_allocator.attempts == g_allocator.fail_at" in worker,
        "worker_has_one_shot_and_persistent_failure_modes",
        "one-shot cuts one allocation; sticky cuts the selected allocation and all successors",
    )
    require(
        checks,
        "std::exception_ptr error" in worker and "std::current_exception()" in worker,
        "worker_preserves_boundary_exception_for_state_composition",
        "the cut result is separated from the later recovery assertions",
    )

    scenario_names = (
        "transaction-begin",
        "savepoint-begin",
        "savepoint-release",
        "savepoint-rollback",
        "transaction-commit",
        "transaction-rollback",
    )
    for name in scenario_names:
        require(
            checks,
            worker.count(f'"{name}"') >= 1,
            "worker_covers_" + name.replace("-", "_"),
            f"allocator campaign scenario is present: {name}",
        )
    require(
        checks,
        "constexpr std::array<std::pair<std::string_view, Scenario>, 6>" in worker,
        "scenario_inventory_is_exactly_six",
        "the reviewed transaction/savepoint boundaries have a fixed inventory",
    )
    for needle, check_id in (
        ("failed transaction begin orphaned an explicit transaction", "begin_failure_cannot_orphan_transaction"),
        ("savepoint begin cut revoked a still-live outer transaction", "savepoint_begin_preserves_live_outer_generation"),
        ("failed savepoint release permanently revoked a live mark", "release_failure_preserves_live_mark"),
        ("failed savepoint rollback permanently revoked a live mark", "rollback_failure_preserves_live_mark"),
        ("failed commit revoked a still-live transaction", "commit_failure_preserves_live_transaction"),
        ("failed rollback revoked a still-live transaction", "rollback_failure_preserves_live_transaction"),
        ("automatic outer rollback", "worker_models_sqlite_automatic_outer_rollback"),
        ("post-commit generation isolation", "worker_proves_post_commit_generation_isolation"),
        ("post-rollback generation isolation", "worker_proves_post_rollback_generation_isolation"),
    ):
        require(checks, needle in worker, check_id, f"required recovery assertion: {needle}")
    require(
        checks,
        worker.count("sqlite3_get_autocommit") >= 8,
        "worker_observes_automatic_transaction_end",
        "resource errors may end the outer transaction and must revoke both typed levels",
    )
    require(
        checks,
        "insert_row(fixture.db.get(), 3);\n        savepoint.rollback();" in worker,
        "split_rollback_retry_rewinds_later_work",
        "retry after a partial ROLLBACK TO must rewind work added after the failed close",
    )

    process_segment = segment(
        worker,
        "anonsync::test::SelfExecTestProcessOutput run_worker_process(",
        "std::uint64_t parse_output_field(",
    )
    require(
        checks,
        all(
            marker in process_segment
            for marker in (
                "spawn_self_exec_test_process_with_output_capture_or_throw(",
                "wait_for_exact_exit_with_output(",
                "kWorkerTimeout",
                "kWorkerCaptureBytesPerStream",
                "!output.standard_error.empty()",
            )
        )
        and all(
            marker not in worker
            for marker in (
                "::fork(",
                "::pipe(",
                "::dup2(",
                "::execl(",
                "::waitpid(",
            )
        ),
        "allocator_fault_campaign_uses_fresh_image_capture",
        "every cut enters the pinned self-exec image and returns evidence through bounded, separately owned stdout/stderr without a raw post-fork C++ path",
    )
    require(
        checks,
        "struct SelfExecTestProcessOutput final" in self_exec_header
        and "wait_for_exact_exit_with_output(" in self_exec_header
        and "kMaximumCaptureBytesPerStream" in self_exec_source
        and "::pipe2(raw_descriptors, O_CLOEXEC)" in self_exec_source
        and "O_CLOEXEC | O_NONBLOCK" not in self_exec_source
        and "::poll(" in self_exec_source
        and self_exec_source.count("drain_capture_descriptor_or_throw(") >= 3
        and "topology_.terminate_and_reap_noexcept();" in self_exec_source
        and "::kill(-process_group, SIGKILL)" in topology_owner
        and "::waitpid(leader, &status, 0)" in topology_owner
        and "std::exchange(leader_, -1)" in topology_owner
        and "std::exchange(process_group_, -1)" in topology_owner
        and "close_output_capture_noexcept();" in self_exec_source,
        "capture_owner_is_bounded_concurrent_and_fail_closed",
        "the reusable owner keeps child writes blocking, multiplexes nonblocking parent reads under one hard deadline and byte cap, and delegates numeric kill/reap authority to the shared consume-before-use topology owner",
    )
    helper_main_start = worker.find("int main(int argc, char** argv)")
    helper_main = worker[helper_main_start:] if helper_main_start >= 0 else ""
    require(
        checks,
        bool(helper_main)
        and ordered(
            helper_main,
            "std::string_view(argv[1]) == kWorkerFlag",
            "verify_self_exec_child_boundary_or_throw();",
            "argc != 5",
            "worker_main(argv[2], argv[3], argv[4])",
        ),
        "allocator_worker_verifies_boundary_before_instruction_or_sqlite_work",
        "the helper proves its pinned image, isolated process group, environment, signals, and descriptor hygiene before parsing the exact worker instruction or initializing SQLite",
    )
    require(
        checks,
        "tests/sqlite_transaction_allocator_fault_test.cpp" in raw_fork_audit
        and "eight_fresh_state_campaigns_use_pinned_self_exec_images"
        in raw_fork_audit
        and '"test_raw_fork_calls": 1' in raw_fork_audit
        and '"tests/inherited_test_process.cpp": 1' in raw_fork_audit
        and '"tests/sqlite_transaction_allocator_fault_test.cpp": 1'
        not in raw_fork_audit,
        "raw_fork_inventory_removes_allocator_bridge_exception",
        "the exact raw-fork gate centralizes its sole test call and classifies the allocator campaign as one of eight pinned fresh-image migrations",
    )
    parent_segment = segment(worker, "int parent_main()", "#else")
    require(
        checks,
        "for (std::uint64_t cut = 1; cut <= attempts; ++cut)" in parent_segment,
        "parent_walks_every_baseline_allocation_cut",
        "every allocation observed by the no-fault boundary run is cut",
    )
    require(
        checks,
        'std::string_view("oneshot")' in parent_segment
        and 'std::string_view("sticky")' in parent_segment,
        "parent_runs_both_fault_modes_per_cut",
        "every baseline cut is exercised once transiently and once persistently",
    )
    require(
        checks,
        "attempts <= 512" in parent_segment,
        "allocation_frontier_has_reviewed_upper_bound",
        "an accidental runaway worker expansion fails the proof instead of exploding CTest",
    )
    require(
        checks,
        'parse_output_field(result.standard_output, "failures") >= 1'
        in parent_segment,
        "parent_proves_each_requested_cut_fired",
        "a successful child without an injected failure cannot count as a cutpoint pass",
    )

    raw_error_inventory: dict[str, dict[str, object]] = {}
    raw_error_pattern = re.compile(
        r"char\s*\*\s*(?:err|error|errmsg|raw_error|rollback_error)\b"
        r"|sqlite3_exec\([^;]{0,600}&(?:err|error|errmsg|raw_error|rollback_error)\b",
        re.DOTALL,
    )
    for path in RUNTIME_EXEC_HELPERS:
        text = texts[path]
        matches = [match.group(0)[:200] for match in raw_error_pattern.finditer(text)]
        raw_error_inventory[path.as_posix()] = {
            "match_count": len(matches),
            "matches": matches,
            "sqlite3_free_count": text.count("sqlite3_free("),
        }
        require(
            checks,
            not matches,
            "runtime_exec_has_no_owned_errmsg_" + path.stem,
            f"{path.as_posix()} must use connection-owned sqlite3_errmsg evidence",
        )
        require(
            checks,
            "sqlite3_free(" not in text,
            "runtime_exec_has_no_errmsg_free_" + path.stem,
            f"{path.as_posix()} has no sqlite3_exec error-buffer ownership edge",
        )
    require(
        checks,
        "sqlite3_exec() allocates its optional errmsg through sqlite3_malloc()" in texts[Path("src/sync_sqlite_support.cpp")],
        "generic_exec_helper_documents_removed_oom_cut",
        "the allocation/ownership rationale remains adjacent to the shared helper",
    )
    require(
        checks,
        authority.count("sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr)") >= 2,
        "transaction_boundaries_do_not_request_optional_errmsg",
        "post-effect state composition is not preceded by a redundant SQLite allocation",
    )

    require(
        checks,
        "tests/sqlite_transaction_allocator_fault_test.cpp" in package_verifier
        and "tests/self_exec_test_process.hpp" in package_verifier
        and "tests/self_exec_test_process.cpp" in package_verifier
        and "tools/audit_sqlite_transaction_allocator_fault.py" in package_verifier,
        "release_package_requires_allocator_proof_surface",
        "the worker and source audit cannot be omitted while CMake retains stale references",
    )
    require(
        checks,
        "tests/sqlite_transaction_allocator_fault_test.cpp" in stack_audit
        and "tools/audit_sqlite_transaction_allocator_fault.py" in stack_audit,
        "broad_transaction_stack_audit_tracks_allocator_proof",
        "the central stack inventory hashes both the runtime campaign and focused audit",
    )
    require(
        checks,
        "SyncSqliteBoundaryAuthorityStatus" in composition_audit
        and "Indeterminate" in composition_audit,
        "exception_composition_audit_tracks_tri_state_semantics",
        "the earlier cutpoint model cannot silently regress to boolean revocation",
    )
    require(
        checks,
        "schema_rollback_avoids_optional_exec_errmsg_allocation"
        in schema_contract_audit
        and "rollback_without_errmsg" in schema_contract_audit,
        "schema_contract_audit_tracks_no_errmsg_rollback",
        "the existing schema transaction audit must require the allocation-free unwind form",
    )

    violations = [asdict(check) for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-transaction-allocator-fault-audit-v4",
        "root": str(root),
        "passed": not violations,
        "check_count": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "raw_sqlite_exec_error_buffer_inventory": raw_error_inventory,
        "sensitive_file_sha256": {
            path.as_posix(): sha256_file(root / path) for path in SENSITIVE_FILES
        },
        "interpretation": (
            "Current requires a completed exact callback probe. Invalid revokes. "
            "Indeterminate denies the present use but retains the exact generation for retry. "
            "The fresh-image allocator campaign cuts every allocation on each no-fault boundary "
            "frontier in both one-shot and persistent modes. Its bounded concurrent stdout/stderr "
            "owner prevents pipe deadlock, enforces one deadline and two byte caps, and consumes "
            "process and descriptor authority before reporting any failure."
        ),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
