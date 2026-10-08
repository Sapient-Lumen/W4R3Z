#!/usr/bin/env python3
"""Audit AnonSync's live-process SQLite capability boundary.

This is a deterministic source-shape and inventory audit.  It does not claim
that lexical evidence proves runtime behavior; the fork-adversarial executables
and CTest lanes are separate release requirements.  The audit covers both the
shared SQLite handle authority and the independently linked persistence owners
that retain path descriptors, private snapshot cleanup, or progress callbacks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
SKIP_PARTS = {"third_party", ".git", "REVISION_EVIDENCE", "evidence", "audit"}


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    position = -1
    for needle in needles:
        position = text.find(needle, position + 1)
        if position < 0:
            return False
    return True


def source_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for top in ("include", "src", "tests", "fuzz"):
        base = root / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            rel = path.relative_to(root)
            if any(part in SKIP_PARTS or part.startswith("build") for part in rel.parts):
                continue
            result.append(rel)
    return result


def line_inventory(root: Path, files: list[Path], pattern: re.Pattern[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rel in files:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), 1):
            code = line.split("//", 1)[0]
            match = pattern.search(code)
            if match:
                rows.append(
                    {
                        "path": rel.as_posix(),
                        "line": line_number,
                        "name": match.group(1) if match.groups() else "",
                        "text": line.strip()[:360],
                    }
                )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    sensitive = [
        Path("CMakeLists.txt"),
        Path("src/sync_process_incarnation.hpp"),
        Path("src/sync_process_incarnation_internal.hpp"),
        Path("src/sync_process_incarnation.cpp"),
        Path("src/sqlite_path_security.hpp"),
        Path("src/sqlite_path_security.cpp"),
        Path("src/persistence/sqlite_snapshot_seal.hpp"),
        Path("src/persistence/sqlite_snapshot_seal.cpp"),
        Path("src/persistence/sqlite_verification_budget.hpp"),
        Path("src/persistence/sqlite_verification_budget.cpp"),
        Path("src/persistence/sqlite_retained_callback_claim.hpp"),
        Path("src/persistence/sqlite_retained_callback_claim.cpp"),
        Path("src/persistence/sqlite_replay_ledger_write_gate.hpp"),
        Path("src/persistence/sqlite_replay_ledger_write_gate.cpp"),
        Path("src/persistence/sqlite_replay_ledger_restore_lock.hpp"),
        Path("src/persistence/sqlite_replay_ledger_restore_lock.cpp"),
        Path("tests/sqlite_replay_ledger_selftests.cpp"),
        Path("src/sync_sqlite_handle_slot.hpp"),
        Path("src/sync_sqlite_handle_slot.cpp"),
        Path("src/sync_sqlite_support.hpp"),
        Path("src/sync_sqlite_connection_authority.hpp"),
        Path("src/sync_sqlite_connection_authority.cpp"),
        Path("src/sync_sqlite_connection_authority_internal.hpp"),
        Path("src/sync_sqlite_mutex_capability.cpp"),
        Path("src/sync_sqlite_execution_affinity.hpp"),
        Path("src/sync_sqlite_execution_affinity.cpp"),
        Path("src/sync_sqlite_database_mutex_guard.hpp"),
        Path("src/sync_sqlite_database_mutex_guard.cpp"),
        Path("src/sync_sqlite_busy_timeout_mutation_guard.hpp"),
        Path("src/sync_sqlite_busy_timeout_mutation_guard.cpp"),
        Path("src/sync_sqlite_transaction.cpp"),
        Path("src/sync_peer_ingress_payload_store.cpp"),
        Path("src/sync_peer_ingress_payload_store_schema.cpp"),
        Path("src/sqlite_replay_ledger.cpp"),
        Path("tests/process_incarnation_tests.cpp"),
        Path("tests/sqlite_process_authority_fork_test.cpp"),
        Path("tests/persistence/sqlite_persistence_process_authority_fork_test.cpp"),
        Path("tests/sqlite_connection_authority_test.cpp"),
    ]
    missing = [rel.as_posix() for rel in sensitive if not (root / rel).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-process-authority-audit-v8",
            "passed": False,
            "violations": [f"missing sensitive file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 2

    texts = {rel: (root / rel).read_text(encoding="utf-8") for rel in sensitive}
    cmake = texts[Path("CMakeLists.txt")]
    process_hpp = texts[Path("src/sync_process_incarnation.hpp")]
    process_internal = texts[Path("src/sync_process_incarnation_internal.hpp")]
    process_cpp = texts[Path("src/sync_process_incarnation.cpp")]
    path_hpp = texts[Path("src/sqlite_path_security.hpp")]
    path_cpp = texts[Path("src/sqlite_path_security.cpp")]
    seal_hpp = texts[Path("src/persistence/sqlite_snapshot_seal.hpp")]
    seal_cpp = texts[Path("src/persistence/sqlite_snapshot_seal.cpp")]
    budget_hpp = texts[Path("src/persistence/sqlite_verification_budget.hpp")]
    budget_cpp = texts[Path("src/persistence/sqlite_verification_budget.cpp")]
    callback_claim_hpp = texts[
        Path("src/persistence/sqlite_retained_callback_claim.hpp")
    ]
    callback_claim_cpp = texts[
        Path("src/persistence/sqlite_retained_callback_claim.cpp")
    ]
    write_gate_hpp = texts[
        Path("src/persistence/sqlite_replay_ledger_write_gate.hpp")
    ]
    write_gate_cpp = texts[
        Path("src/persistence/sqlite_replay_ledger_write_gate.cpp")
    ]
    restore_lock_hpp = texts[
        Path("src/persistence/sqlite_replay_ledger_restore_lock.hpp")
    ]
    restore_lock_cpp = texts[
        Path("src/persistence/sqlite_replay_ledger_restore_lock.cpp")
    ]
    replay_selftests = texts[Path("tests/sqlite_replay_ledger_selftests.cpp")]
    slot_hpp = texts[Path("src/sync_sqlite_handle_slot.hpp")]
    slot_cpp = texts[Path("src/sync_sqlite_handle_slot.cpp")]
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    authority_hpp = texts[Path("src/sync_sqlite_connection_authority.hpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    authority_internal = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    mutex_cpp = texts[Path("src/sync_sqlite_mutex_capability.cpp")]
    execution_affinity_cpp = texts[
        Path("src/sync_sqlite_execution_affinity.cpp")
    ]
    database_mutex_guard_hpp = texts[
        Path("src/sync_sqlite_database_mutex_guard.hpp")
    ]
    database_mutex_guard_cpp = texts[
        Path("src/sync_sqlite_database_mutex_guard.cpp")
    ]
    busy_timeout_guard_hpp = texts[
        Path("src/sync_sqlite_busy_timeout_mutation_guard.hpp")
    ]
    busy_timeout_guard_cpp = texts[
        Path("src/sync_sqlite_busy_timeout_mutation_guard.cpp")
    ]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    payload_cpp = texts[Path("src/sync_peer_ingress_payload_store.cpp")]
    payload_schema_cpp = texts[
        Path("src/sync_peer_ingress_payload_store_schema.cpp")
    ]
    replay_cpp = texts[Path("src/sqlite_replay_ledger.cpp")]
    incarnation_test = texts[Path("tests/process_incarnation_tests.cpp")]
    fork_test = texts[Path("tests/sqlite_process_authority_fork_test.cpp")]
    persistence_fork_test = texts[
        Path("tests/persistence/sqlite_persistence_process_authority_fork_test.cpp")
    ]
    authority_test = texts[Path("tests/sqlite_connection_authority_test.cpp")]

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    for source in (
        "src/sync_process_incarnation.cpp",
        "src/sync_sqlite_handle_slot.cpp",
        "src/sync_sqlite_mutex_capability.cpp",
        "src/sync_sqlite_execution_affinity.cpp",
        "src/sync_sqlite_database_mutex_guard.cpp",
        "src/sync_sqlite_busy_timeout_mutation_guard.cpp",
        "src/sync_sqlite_transaction.cpp",
        "src/sync_sqlite_connection_authority.cpp",
    ):
        require(source in cmake, f"linked_{Path(source).stem}", f"{source} must remain linked into the shared SQLite boundary")
    require(
        "add_library(anonsync_process_incarnation STATIC" in cmake
        and "${ANONSYNC_PROCESS_INCARNATION_SOURCE}" in cmake,
        "process_incarnation_is_independent_library",
        "fork-lineage identity must remain one separately linked owner",
    )
    support_match = re.search(
        r"add_library\(anonsync_sqlite_support STATIC(?P<body>.*?)\)\s*target_include_directories",
        cmake,
        re.S,
    )
    require(
        support_match is not None
        and "sync_process_incarnation.cpp" not in support_match.group("body")
        and "anonsync_process_incarnation" in cmake,
        "process_source_is_not_privately_reabsorbed",
        "all SQLite boundaries must share one token singleton rather than compiling private copies",
    )
    require("anonsync_sqlite_process_authority_fork_test" in cmake, "fork_test_registered", "the fork-adversarial executable must remain compiled and registered")
    require(
        "anonsync_process_incarnation_test" in cmake
        and "anonsync_sqlite_persistence_process_authority_fork_test" in cmake,
        "lineage_and_persistence_fork_tests_registered",
        "pure lineage and persistence-owner fork proofs must remain CTest targets",
    )
    require(
        "anonsync_sqlite_process_authority_source_audit" in cmake,
        "process_authority_audit_is_registered",
        "process authority architecture must be a CTest gate",
    )

    require(
        "class SyncProcessIncarnation final" in process_hpp
        and "explicit constexpr SyncProcessIncarnation(std::uint64_t value)" in process_hpp
        and "!std::is_constructible_v<SyncProcessIncarnation, std::uint64_t>" in process_hpp
        and "!std::is_convertible_v<std::uint64_t, SyncProcessIncarnation>" in process_hpp,
        "process_identity_has_named_type",
        "live process authority must use one explicit process-local type that rejects arbitrary integer construction",
    )
    require("kSyncProcessCapabilityViolationExitCode = 86" in process_hpp, "fail_stop_exit_is_stable", "adversarial tests and operators need one stable violation status")
    require("::getpid()" in process_cpp or "::_getpid()" in process_cpp, "process_identity_reads_kernel_pid", "process identity must be reacquired at use time")
    require(
        "kSyncProcessKernelPidBits = 32U" in process_internal
        and "sync_lineage_generation_from_process_incarnation" in process_internal
        and "compose_sync_process_incarnation" in process_internal,
        "token_binds_pid_and_fork_lineage",
        "the live token must not collapse back to a recyclable raw PID",
    )
    require(
        "pthread_atfork" in process_cpp
        and "advance_process_incarnation_in_child_after_fork" in process_cpp,
        "ordinary_fork_edges_are_recorded_before_child_code",
        "the child copy must advance before fork() returns to application code",
    )
    require(
        "std::atomic<std::uint64_t>::is_always_lock_free" in process_cpp
        and "live_process_incarnation_raw" in process_cpp
        and "std::memory_order_relaxed" in process_cpp,
        "child_hook_state_is_lock_free",
        "the post-fork child hook must not depend on a copied userspace mutex",
    )
    require(
        "kSyncPoisonedProcessIncarnation" in process_internal
        and "!advanced.valid() ? detail::kSyncPoisonedProcessIncarnation" in process_cpp
        and "observed.valid() && observed_generation == 0U" in process_internal,
        "lineage_exhaustion_is_poisoned",
        "generation wraparound must fail closed instead of looking uninitialized",
    )
    require(
        "refresh_sync_process_incarnation" in process_internal
        and "observed_pid == current_kernel_pid" in process_internal,
        "pid_change_fallback_exists",
        "paths that bypass the ordinary fork hook must still reject a stale PID token",
    )
    process_fail_stop = function_body(process_cpp, "[[noreturn]] void fail_stop_on_sync_process_capability_violation_noexcept()")
    require("std::_Exit(kSyncProcessCapabilityViolationExitCode)" in process_fail_stop, "process_violation_uses_unhookable_exit", "a capability violation must bypass terminate and atexit handlers")
    require("std::terminate" not in process_cpp, "process_boundary_has_no_terminate_path", "replaceable terminate handlers must not own fail-stop policy")

    for header, owner_name in (
        (path_hpp, "path guard"),
        (seal_hpp, "sealed snapshot"),
        (budget_hpp, "verification budget"),
    ):
        require(
            "SyncProcessIncarnation process_id_;" in header,
            f"{owner_name.replace(' ', '_')}_carries_process_token",
            f"the {owner_name} must bind its retained authority to one live process",
        )
    require(
        ordered(
            function_body(path_cpp, "SqlitePathFamilyGuard::~SqlitePathFamilyGuard()"),
            "require_current_process_noexcept",
            "::close",
        )
        and "out.process_id_ = current_sync_process_incarnation_noexcept()" in path_cpp,
        "path_guard_fences_use_move_and_destruction",
        "an inherited directory proof must fail before descriptor close or reuse",
    )
    seal_cleanup = function_body(seal_cpp, "void SealedSqliteSnapshot::cleanup_noexcept()")
    seal_initializer = function_body(
        seal_cpp,
        "void SealedSqliteSnapshot::initialize_process_and_vfs_or_throw(",
    )
    require(
        ordered(
            seal_cleanup,
            "require_current_process_noexcept",
            "serialized_bytes_.reset()",
        )
        and "process_id_ = current_sync_process_incarnation_noexcept()"
            in seal_initializer
        and seal_cpp.count("out.initialize_process_and_vfs_or_throw(label)") == 2
        and all(
            marker not in seal_cpp
            for marker in (
                "::unlink(",
                "::rmdir(",
                "::rename(",
                "staging_directory_",
                "staged_path_",
            )
        ),
        "sealed_snapshot_fences_resident_cleanup_without_namespace_mutation",
        "an inherited seal must fail before freeing resident bytes, and the seal must own no cleanup pathname",
    )
    require(
        "other.require_current_process_noexcept()" in seal_cpp
        and "other.require_current_process_noexcept()" in path_cpp,
        "process_bound_owners_fence_move_sources",
        "child-side movement cannot launder inherited ownership into a new object",
    )
    budget_destructor = function_body(
        budget_cpp, "SqliteVerificationBudget::~SqliteVerificationBudget()"
    )
    budget_detach = function_body(budget_cpp, "void SqliteVerificationBudget::detach()")
    budget_progress = function_body(budget_cpp, "int SqliteVerificationBudget::on_progress()")
    require(
        "process_id_(current_sync_process_incarnation_noexcept())" in budget_cpp
        and "require_current_execution_noexcept" in budget_destructor + budget_detach
        and ordered(
            budget_detach,
            "database_borrow_.get()",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.require_live(database, mutation_guard)",
            "sqlite3_progress_handler(database, 0, nullptr, nullptr)",
            "callback_claim_.detach(database, mutation_guard)",
            "database_borrow_.reset()",
        ),
        "verification_budget_fences_callback_detachment",
        "an inherited destructor must not detach the parent's SQLite callback",
    )
    require(
        ordered(budget_progress, "require_current_execution_noexcept", "failure_ != SqliteVerificationBudgetFailure::none"),
        "progress_callback_checks_process_first",
        "inherited SQLite execution must fail before reading copied callback state",
    )
    require(
        "SyncProcessIncarnation process_id_;" in callback_claim_hpp
        and "sync_process_incarnation_is_current(claim->process_id)" in callback_claim_cpp
        and "fail_stop_on_retained_callback_lifetime_violation_noexcept" in callback_claim_cpp,
        "shared_callback_claim_is_process_incarnation_bound",
        "connection destruction and named-slot replacement cannot launder a retained callback into a fork descendant",
    )
    require(
        "SyncProcessIncarnation process_id_;" in database_mutex_guard_hpp
        and "SyncThreadIncarnation thread_id_;" in database_mutex_guard_hpp
        and ordered(
            execution_affinity_cpp,
            "sync_process_incarnation_is_current",
            "sync_thread_incarnation_is_current",
        )
        and "require_current_sync_sqlite_execution_noexcept"
            in database_mutex_guard_cpp
        and ordered(
            database_mutex_guard_cpp,
            "SyncSqliteDatabaseMutexGuard::~SyncSqliteDatabaseMutexGuard()",
            "require_current_execution_noexcept",
            "sqlite3_mutex_leave",
        )
        and all(marker in busy_timeout_guard_hpp for marker in (
            "SyncProcessIncarnation process_id_",
            "SyncThreadIncarnation thread_id_",
        ))
        and ordered(
            busy_timeout_guard_cpp,
            "SyncSqliteBusyTimeoutMutationGuard::~SyncSqliteBusyTimeoutMutationGuard()",
            "require_current_sync_sqlite_execution_noexcept",
            "sqlite3_mutex_leave",
        )
        and all(marker in fork_test for marker in (
            "foreign-thread NOMUTEX busy-timeout guard destruction fails stopped",
            "inherited NOMUTEX busy-timeout guard destruction fails stopped",
            "released database-mutex guard destruction remains thread affine",
        )),
        "sqlite_scoped_mutation_guards_are_process_then_thread_bound",
        "strict and NOMUTEX-compatible scoped SQLite owners may not cross either a fork boundary or their exact entering thread",
    )
    require(
        all(
            marker in persistence_fork_test
            for marker in (
                "deferred close_v2 destruction cannot outlive a live verification claim",
                "client-data replacement cannot destroy a live child-local verification claim",
                "parent verification generation survives hostile children",
                "parent verification detach releases its exact generation",
            )
        ),
        "verification_claim_close_replacement_and_parent_survival_are_executable",
        "deferred destruction, replacement, parent usability, and exact-generation release remain one fork-adversarial contract",
    )

    require("class ProcessBoundHandleSlot final" in slot_hpp, "typed_owner_slot_exists", "connection and statement ownership share one invariant-owned abstraction")
    require("class ProcessBoundHandleOutGuard final" in slot_hpp, "scoped_output_guard_exists", "SQLite output parameters must be adopted at full-expression completion")
    require("SyncSqliteDbHandlePolicy" in slot_hpp and "SyncSqliteStmtHandlePolicy" in slot_hpp, "connection_and_statement_policies_share_slot", "both SQLite owner kinds must use the same process fence")
    require(
        "sqlite3_get_autocommit(handle) == 0" in slot_cpp
        and "sqlite3_close(handle)" in slot_cpp
        and "sqlite3_close_v2(handle)" not in slot_cpp,
        "connection_disposal_is_strict",
        "connection disposal must reject open transactions and SQLite zombie-close semantics",
    )
    require("sqlite3_finalize(handle)" in slot_cpp, "statement_disposal_uses_finalize", "statement ownership must finalize exactly once")
    require("operator Handle**" in slot_hpp and "adopt_output_noexcept" in slot_hpp, "output_guard_adopts_error_handles", "non-null handles returned on SQLite error must still become owned")
    require("output_pending" in slot_hpp and "output acquisition is already pending" in slot_hpp, "simultaneous_output_guards_are_rejected", "two output parameters cannot race to own one slot")
    require("class ProcessBoundHandleBorrow final" in slot_hpp, "typed_generation_borrow_exists", "dependent work must be able to retain an exact owner generation")
    require(
        "const SyncProcessIncarnation state_process_id" in slot_hpp
        and "state_->state_process_id != process_id_" in slot_hpp,
        "shared_owner_storage_is_process_bound",
        "even closed or null-output shared ownership storage must retain immutable process provenance",
    )
    require(not re.search(r"\b(?:adopt|release|put)\s*\(\s*Handle\s*\*", slot_hpp), "no_public_raw_owner_adoption", "the owner slot exposes no raw-pointer laundering API")
    guarded_slot_functions = (
        ("Handle* get() const noexcept", "get_checks_process"),
        ("void dispose_owned_noexcept() noexcept", "destruction_checks_process"),
        ("void begin_output_or_throw()", "output_acquisition_checks_process"),
    )
    for signature, check_id in guarded_slot_functions:
        body = function_body(slot_hpp, signature)
        require(
            "ProcessBoundHandleStateGuard<Policy> guard" in body,
            check_id,
            f"{signature} must enter the process-aware state guard before ownership use",
        )
    move_body = function_body(
        slot_hpp, "void transfer_from_noexcept(ProcessBoundHandleSlot& other)")
    require(
        "other.require_current_if_owned_noexcept()" in move_body,
        "move_checks_process",
        "owner movement must validate the source process before moving shared state",
    )

    require(
        "SyncSqliteDbHandleSlot db;" in support_hpp
        and "SyncSqliteStmtHandleSlot statement_owner_;" in support_hpp
        and "HandleView stmt;" in support_hpp,
        "common_support_uses_typed_slots",
        "common RAII wrappers must keep raw SQLite ownership in private process-bound slots",
    )
    require("SyncSqliteDbHandleSlot db_;" in replay_cpp, "replay_ledger_long_lived_owner_is_fenced", "the long-lived WAL ledger connection must fail-stop if inherited")
    require("SyncSqliteStmtHandleSlot stmt;" in replay_cpp, "replay_ledger_statement_owner_is_fenced", "internal prepared statements must share the same owner policy")

    for text, marker, check_id, detail in (
        (authority_hpp, "SyncProcessIncarnation process_id_", "proof_and_lease_carry_process", "connection proofs and leases must carry their minting process"),
        (authority_internal, "SyncProcessIncarnation process_id", "transaction_boundary_carries_process", "transaction boundary proofs must carry process authority"),
        (transaction_cpp, "process_id_(current_sync_process_incarnation_noexcept())", "transaction_guard_is_process_stamped", "typed transaction and savepoint guards must record their creation process"),
        (mutex_cpp, "SyncProcessIncarnation process_id", "retained_mutex_state_is_process_stamped", "SQLite-owned lifetime sentinels must reject child-side use"),
        (transaction_cpp, "SyncSqliteSavepoint::SyncSqliteSavepoint", "typed_savepoint_owner_is_process_stamped", "schema and compound-transition savepoints must share the process-bound owner"),
        (authority_internal, "struct SyncSqliteSavepointBoundaryProof final", "savepoint_boundary_carries_process", "the exact savepoint generation must carry process authority"),
        (
            cmake + restore_lock_hpp + restore_lock_cpp,
            "SqliteReplayLedgerRestoreLock",
            "restore_lock_is_present",
            "restore serialization remains an explicit separately linked owner",
        ),
        (
            cmake + write_gate_hpp + write_gate_cpp,
            "anonsync_sqlite_replay_ledger_write_gate",
            "write_gate_is_present",
            "writer serialization remains an explicit separately linked owner",
        ),
    ):
        require(marker in text, check_id, detail)

    savepoint_destructor = function_body(
        transaction_cpp, "SyncSqliteSavepoint::~SyncSqliteSavepoint()")
    require(
        ordered(
            savepoint_destructor,
            "sync_process_incarnation_is_current(process_id_)",
            "sync_sqlite_thread_incarnation_is_current",
            "rollback_sync_sqlite_savepoint_boundary_noexcept",
        ),
        "savepoint_destructor_checks_process_before_sqlite_cleanup",
        "an inheriting child must fail-stop before an inherited savepoint can execute rollback SQL",
    )

    restore_destructor = function_body(
        restore_lock_cpp,
        "SqliteReplayLedgerRestoreLock::~SqliteReplayLedgerRestoreLock()",
    )
    write_gate_destructor = function_body(
        write_gate_cpp, "SqliteReplayLedgerWriteGate::~SqliteReplayLedgerWriteGate()"
    )
    restore_state_destructor = function_body(restore_lock_cpp, "~State()")
    require(
        ordered(
            restore_destructor,
            "sync_process_incarnation_is_current",
            "state_.reset()",
        )
        and "release_flocked_descriptor_noexcept" in restore_state_destructor,
        "restore_lock_destructor_checks_before_close",
        "an inherited destructor must fail-stop before resetting the state whose destructor releases the flock descriptor",
    )
    require(
        ordered(
            write_gate_destructor,
            "sync_process_incarnation_is_current",
            "sync_sqlite_thread_incarnation_is_current",
            "release_descriptor_noexcept",
        ),
        "write_gate_destructor_checks_before_close",
        "an inherited or cross-thread write-gate destructor must fail before close or TLS mutation",
    )
    tls_body = function_body(write_gate_cpp, "current_thread_write_gate_state()")
    require(
        ordered(
            tls_body,
            "current_sync_process_incarnation_noexcept",
            "state.process_id != current",
            "state.scope_stacks.clear()",
            "state.process_id = current",
        ),
        "fork_copied_lock_recursion_is_discarded",
        "copied thread-local recursion evidence cannot authorize a child-side nested lock",
    )

    require("fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept" in mutex_cpp, "mutex_violation_has_named_fail_stop", "thread and close-order violations share an explicit direct-exit primitive")
    require("std::terminate" not in mutex_cpp, "mutex_boundary_has_no_terminate_path", "a hostile terminate handler cannot intercept a SQLite mutex violation")
    require("hostile_affinity_terminate_handler" in authority_test and "kHostileTerminateExit" in authority_test, "mutex_tests_install_hostile_terminate_handler", "tests distinguish direct fail-stop from terminate-handler execution")

    required_fork_markers = [
        "child cannot read an inherited connection owner",
        "child cannot finalize an inherited statement owner",
        "child cannot move an inherited connection owner",
        "child destructor cannot close an inherited connection",
        "child can create and destroy a child-local connection",
        "an empty pre-fork slot may mint a child-local connection",
        "child cannot acquire authority from an inherited proof",
        "child cannot destroy an inherited authority lease",
        "child cannot destruct an inherited live transaction",
        "child cannot destruct an inherited live savepoint",
        "child observes inherited savepoint capability as inactive",
        "child cannot inspect inherited materialized owner storage",
        "child cannot move inherited materialized owner storage",
        "child destructor cannot release an inherited empty shared-state owner",
        "hostile_terminate_handler",
        "hostile_atexit_handler",
    ]
    for index, marker in enumerate(required_fork_markers, 1):
        require(marker in fork_test, f"fork_scenario_{index:02d}_is_present", f"fork test must retain scenario: {marker}")
    for index, marker in enumerate(
        (
            "recycled ancestor PID cannot resurrect ancestor authority",
            "every ordinary fork edge advances lineage before child code",
            "inherited parent token takes direct fail-stop path",
        ),
        1,
    ):
        require(
            marker in incarnation_test,
            f"lineage_scenario_{index:02d}_is_present",
            f"lineage test must retain scenario: {marker}",
        )
    for index, marker in enumerate(
        (
            "child destructor cannot close an inherited path guard owner",
            "child move-assignment cannot free parent resident snapshot bytes",
            "child destructor cannot free an inherited sealed snapshot",
            "inherited SQLite execution reaches the process-bound callback",
            "child destructor cannot detach an inherited verification budget",
            "child can mint fresh persistence authority after fork",
            "hostile_atexit_handler",
        ),
        1,
    ):
        require(
            marker in persistence_fork_test,
            f"persistence_fork_scenario_{index:02d}_is_present",
            f"persistence fork test must retain scenario: {marker}",
        )
    require(
        "inherited recursion evidence" in replay_selftests
        and "inherited destructor did not fail stop" in replay_selftests
        and replay_selftests.count("spawn_inherited_test_process_or_throw(") == 3
        and "::fork()" not in replay_selftests
        and "::waitpid(" not in replay_selftests,
        "file_lock_inheritance_scenarios_are_present",
        "file-lock ownership and copied TLS recursion retain exactly three probes behind the shared bounded inherited-process owner",
    )

    files = source_files(root)
    raw_declarations = line_inventory(root, files, re.compile(r"\bsqlite3(?:_stmt)?\s*\*\s*([A-Za-z_]\w*)"))
    raw_open_outputs = line_inventory(root, files, re.compile(r"\bsqlite3_open(?:16|_v2)?\s*\([^;]*&\s*([A-Za-z_]\w*)"))
    raw_prepare_outputs = line_inventory(root, files, re.compile(r"\bsqlite3_prepare(?:16)?_v[23]\s*\([^;]*&\s*([A-Za-z_]\w*)"))
    raw_header_fields = [
        row for row in raw_declarations
        if row["path"].endswith((".h", ".hpp", ".hh", ".hxx"))
        and re.search(r"\b[A-Za-z_]\w*_\s*(?:=\s*nullptr)?\s*;", str(row["text"]))
    ]

    residuals = [
        {
            "severity": "high",
            "id": "raw_borrowed_handle_laundering",
            "detail": "Raw sqlite3* compatibility overloads remain. The exact-generation borrow now protects migrated statements, transactions, and helpers, but a caller that caches a raw pointer beyond the borrow lifetime can still bypass owner revocation. Continue removing raw overloads at invariant-owned module boundaries.",
        },
        {
            "severity": "medium",
            "id": "stack_scoped_raw_sqlite_helpers",
            "detail": "Several replay-ledger and extracted selftest helpers still open/finalize raw local SQLite handles. They are short-lived rather than long-lived members; the selftest helpers now live outside the runtime graph, but no claim is made that every raw C helper is universally fork-safe.",
        },
        {
            "severity": "medium",
            "id": "post_fork_runtime_scope",
            "detail": "Child-local reopen tests assume a controlled single-threaded fork path. After fork from a multithreaded process, POSIX permits only async-signal-safe operations until exec; AnonSync does not claim arbitrary C++ or SQLite work is safe in that interval.",
        },
        {
            "severity": "medium",
            "id": "raw_fork_variants_bypass_atfork",
            "detail": "POSIX _Fork() and raw clone-style process creation do not run pthread_atfork handlers. The PID-change fallback catches ordinary descendants, but an entirely unobserved bypass chain that eventually reuses an ancestor PID is outside this token's proof boundary.",
        },
        {
            "severity": "low",
            "id": "incarnation_is_live_memory_only",
            "detail": "SyncProcessIncarnation is intentionally a live-memory fork-lineage fence, not restart or serialized authority. Durable authority remains evidence-based and must be reconstructed after process restart.",
        },
    ]

    passed = all(check.passed for check in checks)
    report = {
        "format": "anonsync-sqlite-process-authority-audit-v8",
        "passed": passed,
        "check_count": len(checks),
        "passed_check_count": sum(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "violations": [check.detail for check in checks if not check.passed],
        "sensitive_file_sha256": {rel.as_posix(): sha256_file(root / rel) for rel in sensitive},
        "inventory": {
            "source_files": len(files),
            "raw_sqlite_pointer_declarations": raw_declarations,
            "raw_sqlite_pointer_declaration_count": len(raw_declarations),
            "raw_header_field_candidates": raw_header_fields,
            "raw_header_field_candidate_count": len(raw_header_fields),
            "raw_open_output_candidates": raw_open_outputs,
            "raw_open_output_candidate_count": len(raw_open_outputs),
            "raw_prepare_output_candidates": raw_prepare_outputs,
            "raw_prepare_output_candidate_count": len(raw_prepare_outputs),
        },
        "residual_risks": residuals,
        "interpretation": [
            "A lexical pass is not behavioral proof; compilation and fork-adversarial execution remain required.",
            "A raw sqlite3* declaration may be a borrowed API parameter rather than an owner; candidates are retained for manual review.",
            "The audit intentionally reports unresolved raw-borrow boundaries instead of treating the new owner slot as universal coverage.",
            "The ordinary-fork lineage hook is defense against inherited capability reuse, not permission to execute general C++ or SQLite work in a multithreaded post-fork child.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
