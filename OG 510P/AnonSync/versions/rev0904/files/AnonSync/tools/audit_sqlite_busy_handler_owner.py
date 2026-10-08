#!/usr/bin/env python3
"""Audit retained SQLite busy-handler ownership and peer-ingress publication."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}


@dataclass(frozen=True)
class Check:
    check_id: str
    detail: str
    passed: bool


def add(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, detail, bool(condition)))


def inventory(root: Path, token: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        # Function-call inventories are code-shape checks. Documentation must
        # not create a false production call site merely by naming the API.
        code = "\n".join(line.split("//", 1)[0] for line in text.splitlines())
        count = code.count(token)
        if count:
            result[path.relative_to(root).as_posix()] = count
    return result


def inventory_regex(root: Path, pattern: str) -> dict[str, int]:
    expression = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    result: dict[str, int] = {}
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        count = len(expression.findall(
            path.read_text(encoding="utf-8", errors="strict")
        ))
        if count:
            result[path.relative_to(root).as_posix()] = count
    return result


def ordered(text: str, *tokens: str) -> bool:
    position = -1
    for token in tokens:
        position = text.find(token, position + 1)
        if position < 0:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    required = [
        Path("CMakeLists.txt"),
        Path("include/anonsync_core.hpp"),
        Path("src/persistence/sqlite_retained_callback_claim.hpp"),
        Path("src/persistence/sqlite_retained_callback_claim.cpp"),
        Path("src/persistence/sqlite_retained_callback_slots.hpp"),
        Path("src/persistence/sqlite_busy_handler_owner.hpp"),
        Path("src/persistence/sqlite_busy_handler_owner.cpp"),
        Path("src/sync_sqlite_support.hpp"),
        Path("src/sync_sqlite_support.cpp"),
        Path("src/sync_peer_ingress_lifecycle.cpp"),
        Path("tests/persistence/sqlite_busy_handler_owner_tests.cpp"),
        Path("tests/persistence/sqlite_persistence_process_authority_fork_test.cpp"),
        Path("tests/sync_peer_ingress_lifecycle_selftest_main.cpp"),
        Path("tools/verify_release_package.py"),
        Path("src/persistence/sqlite_verification_budget.cpp"),
        Path("src/persistence/sqlite_authorizer_owner.cpp"),
        Path("src/sync_sqlite_busy_timeout_mutation_guard.hpp"),
        Path("src/sync_sqlite_busy_timeout_mutation_guard.cpp"),
        Path("src/sync_sqlite_execution_affinity.hpp"),
        Path("src/sync_sqlite_execution_affinity.cpp"),
        Path("tests/sqlite_process_authority_fork_test.cpp"),
    ]
    missing = [path.as_posix() for path in required if not (root / path).is_file()]
    if missing:
        payload = {
            "format": "anonsync-sqlite-busy-handler-owner-audit-v7",
            "passed": False,
            "missing": missing,
        }
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    cmake = (root / required[0]).read_text(encoding="utf-8")
    public = (root / required[1]).read_text(encoding="utf-8")
    claim_header = (root / required[2]).read_text(encoding="utf-8")
    claim_owner = (root / required[3]).read_text(encoding="utf-8")
    callback_slots = (root / required[4]).read_text(encoding="utf-8")
    header = (root / required[5]).read_text(encoding="utf-8")
    owner = (root / required[6]).read_text(encoding="utf-8")
    support_header = (root / required[7]).read_text(encoding="utf-8")
    support_owner = (root / required[8]).read_text(encoding="utf-8")
    lifecycle = (root / required[9]).read_text(encoding="utf-8")
    test = (root / required[10]).read_text(encoding="utf-8")
    process_test = (root / required[11]).read_text(encoding="utf-8")
    lifecycle_driver = (root / required[12]).read_text(encoding="utf-8")
    verifier = (root / required[13]).read_text(encoding="utf-8")
    verification_owner = (root / required[14]).read_text(encoding="utf-8")
    authorizer_owner = (root / required[15]).read_text(encoding="utf-8")
    timeout_guard_header = (
        root / "src/sync_sqlite_busy_timeout_mutation_guard.hpp"
    ).read_text(encoding="utf-8")
    timeout_guard_owner = (
        root / "src/sync_sqlite_busy_timeout_mutation_guard.cpp"
    ).read_text(encoding="utf-8")
    execution_affinity = (
        root / "src/sync_sqlite_execution_affinity.cpp"
    ).read_text(encoding="utf-8")
    shared_process_test = (
        root / "tests/sqlite_process_authority_fork_test.cpp"
    ).read_text(encoding="utf-8")

    sanitizer_block = cmake.split(
        'if(ANONSYNC_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")',
        1,
    )[1].split("include(CTest)", 1)[0]
    sanitizer_compile_targets = sanitizer_block.split(
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS", 1
    )[1].split("\n  if(TARGET", 1)[0]
    sanitizer_link_targets = sanitizer_block.split(
        "  foreach(tgt\n      anonsync_core", 1
    )[1].split("\n    target_link_options(${tgt}", 1)[0]

    busy_handler_sites = inventory(root, "sqlite3_busy_handler(")
    busy_timeout_sites = inventory(root, "sqlite3_busy_timeout(")
    busy_timeout_gateway_sites = inventory(
        root, "sqlite_set_busy_timeout_or_throw("
    )
    busy_timeout_pragma_sites = inventory_regex(
        root,
        r"\bpragma\s+(?:[A-Za-z_][A-Za-z0-9_]*\s*\.\s*)?busy_timeout\b",
    )
    sqlite_sleep_sites = inventory(root, "sqlite3_sleep(")

    checks: list[Check] = []
    add(
        checks,
        "add_library(anonsync_sqlite_busy_handler_owner STATIC" in cmake
        and "${ANONSYNC_SQLITE_BUSY_HANDLER_OWNER_SOURCE}" in cmake,
        "owner_is_independent_library",
        "the retained callback owner remains a separately linkable boundary",
    )
    add(
        checks,
        "anonsync_sqlite_busy_handler_owner_test" in cmake
        and "anonsync_sqlite_busy_handler_owner_source_audit" in cmake,
        "focused_test_and_audit_are_registered",
        "runtime and architecture obligations are both in CTest",
    )
    add(
        checks,
        all(
            target in sanitizer_compile_targets
            for target in (
                "anonsync_sqlite_database_mutex_guard",
                "anonsync_sqlite_busy_handler_owner",
                "anonsync_sqlite_busy_handler_owner_test",
                "anonsync_sync_peer_ingress_lifecycle_selftest",
            )
        )
        and all(
            target in sanitizer_link_targets
            for target in (
                "anonsync_sqlite_busy_handler_owner_test",
                "anonsync_sync_peer_ingress_lifecycle_selftest",
            )
        ),
        "owner_and_focused_consumers_are_in_sanitizer_graph",
        "ASan+UBSan instrument the mutex/affinity dependency, retained context, focused test, and peer-ingress consumer",
    )
    add(
        checks,
        lifecycle_driver.strip()
        == '#include "anonsync_selftest_api.hpp"\n\nint main() {\n    return anonsync::run_sync_peer_ingress_lifecycle_selftest();\n}'
        and all(token in cmake for token in (
            "add_executable(anonsync_sync_peer_ingress_lifecycle_selftest",
            "focused peer-ingress lifecycle selftest must depend only on anonsync_core_lib",
            "add_test(NAME anonsync_core_sync_peer_ingress_lifecycle_selftest\n  COMMAND anonsync_core --selftest-sync-peer-ingress-lifecycle)",
        )),
        "lifecycle_runtime_has_a_minimal_focused_driver",
        "compiler/sanitizer lanes avoid unrelated corpora while CTest retains CLI coverage",
    )
    add(
        checks,
        all(token in verifier for token in (
            '"src/persistence/sqlite_busy_handler_owner.hpp"',
            '"src/persistence/sqlite_busy_handler_owner.cpp"',
            '"src/persistence/sqlite_retained_callback_claim.hpp"',
            '"src/persistence/sqlite_retained_callback_claim.cpp"',
            '"src/persistence/sqlite_retained_callback_slots.hpp"',
            '"src/sync_peer_ingress_lifecycle.cpp"',
            '"tests/persistence/sqlite_busy_handler_owner_tests.cpp"',
            '"tests/sync_peer_ingress_lifecycle_selftest_main.cpp"',
            '"tools/audit_sqlite_busy_handler_owner.py"',
        ))
        and "revision_number >= 849" in verifier
        and "revision_number >= 853" in verifier
        and "revision_number >= 855" in verifier
        and all(token in verifier for token in (
            '"src/sync_sqlite_busy_timeout_mutation_guard.hpp"',
            '"src/sync_sqlite_busy_timeout_mutation_guard.cpp"',
            '"src/sync_sqlite_execution_affinity.hpp"',
            '"src/sync_sqlite_execution_affinity.cpp"',
        )),
        "release_verifier_requires_owner_and_proofs",
        "rev0849+ retains the owner proof set and rev0853+ also requires the shared callback-slot protocol while older parents remain verifiable",
    )
    add(
        checks,
        busy_handler_sites
        == {"src/persistence/sqlite_busy_handler_owner.cpp": 2},
        "all_production_busy_handler_calls_are_owner_confined",
        f"inventory={busy_handler_sites}",
    )
    add(
        checks,
        busy_timeout_sites == {"src/sync_sqlite_support.cpp": 1},
        "alternate_busy_setter_is_confined_to_one_gateway",
        f"busy_timeout_inventory={busy_timeout_sites}",
    )
    add(
        checks,
        busy_timeout_gateway_sites == {
            "src/anonsync_replica.cpp": 1,
            "src/persistence/sqlite_replay_ledger_reset.cpp": 1,
            "src/runner.cpp": 1,
            "src/sqlite_replay_ledger.cpp": 6,
            "src/sync_sqlite_support.cpp": 3,
            "src/sync_sqlite_support.hpp": 2,
        },
        "every_production_timeout_configuration_uses_the_gateway",
        f"gateway_inventory={busy_timeout_gateway_sites}",
    )
    add(
        checks,
        not busy_timeout_pragma_sites,
        "production_sql_cannot_replace_handler_via_busy_timeout_pragma",
        f"pragma_inventory={busy_timeout_pragma_sites}",
    )
    add(
        checks,
        sqlite_sleep_sites
        == {"src/persistence/sqlite_busy_handler_owner.cpp": 1},
        "callback_sleep_authority_is_owner_confined",
        f"sqlite_sleep_inventory={sqlite_sleep_sites}",
    )
    add(
        checks,
        "SyncSqliteSerializedDbBorrow database_borrow_" in header
        and "SyncSqliteSerializedDbBorrow database_borrow" in header
        and "sqlite3*" not in header.split("SqliteBusyHandlerOwner(", 1)[1].split(");", 1)[0],
        "constructor_requires_exact_generation_borrow",
        "a raw sqlite3 address cannot mint retained callback authority",
    )
    add(
        checks,
        all(token in header for token in (
            "SqliteBusyHandlerOwner(const SqliteBusyHandlerOwner&) = delete",
            "SqliteBusyHandlerOwner(SqliteBusyHandlerOwner&&) = delete",
            "std::atomic<std::uint64_t> invocations_",
            "std::atomic<std::uint64_t> authorized_sleep_milliseconds_",
            "std::atomic<std::uint64_t> sleep_milliseconds_",
            "std::atomic<std::uint32_t> callbacks_active_",
            "std::atomic<bool> contention_observed_",
            "std::atomic<bool> timeout_exhausted_",
        ))
        and "std::atomic<std::uint64_t>::is_always_lock_free" in owner
        and "std::atomic<std::uint32_t>::is_always_lock_free" in owner
        and "std::atomic<bool>::is_always_lock_free" in owner
        and "std::atomic<State>::is_always_lock_free" in claim_owner
        and "SqliteRetainedCallbackClaim callback_claim_" in header,
        "callback_address_is_stable_and_state_is_lock_free",
        "every mutable callback-reachable and fork-checked field is proven lock-free",
    )
    add(
        checks,
        "kMaximumSqliteBusyHandlerWaitMilliseconds =\n    60'000ULL" in header
        and "kSyncPeerTransportMaxSqliteBusyTimeoutMs = 60000" in public,
        "owner_ceiling_matches_public_peer_ingress_policy",
        "the callback cannot silently widen the public timeout ceiling",
    )
    add(
        checks,
        all(token in header for token in (
            "authorized_sleep_milliseconds",
            "one cumulative budget for the complete owner",
            "not a fresh allowance for each SQLite locking event",
        ))
        and "event_started_elapsed_milliseconds_" not in header
        and "std::chrono" not in header
        and "elapsed_milliseconds_since" not in owner
        and "steady_clock" not in owner
        and "prior_invocations <= 0" not in owner
        and all(token in owner for token in (
            "authorized_sleep_milliseconds_.load(",
            "maximum_wait_milliseconds_ - authorized_sleep",
            "result.authorized_sleep_milliseconds",
        )),
        "wait_authority_is_cumulative_and_scheduler_independent",
        "one owner lifetime has one exact requested-sleep budget rather than per-event or scheduler-derived renewal",
    )
    add(
        checks,
        ordered(
            owner,
            "authorized_sleep_milliseconds_.store(",
            "sqlite3_sleep(static_cast<int>(requested_sleep))",
        )
        and all(token in test for token in (
            "test_owner_lifetime_sleep_authority_does_not_reset",
            "first.authorized_sleep_milliseconds == 3U",
            "second.invocations == first.invocations + 1U",
            "second.sleep_milliseconds == first.sleep_milliseconds",
        )),
        "sleep_authority_is_consumed_before_call_and_proven_across_events",
        "the callback consumes authority before sleeping and a later SQLite locking event cannot reset it",
    )
    add(
        checks,
        "current_sync_process_incarnation_noexcept()" in owner
        and "sync_process_incarnation_is_current(process_id_)" in owner
        and "fail_stop_on_sync_process_capability_violation_noexcept()" in owner,
        "callback_owner_is_process_incarnation_bound",
        "fork descendants reject inherited callback and destructor authority",
    )
    add(
        checks,
        all(token in callback_slots for token in (
            "kSqliteBusyHandlerOwnerClientDataName",
            '"anonsync.sqlite-busy-handler-owner.v1"',
            "kSqliteVerificationBudgetClientDataName",
            '"anonsync.sqlite-verification-budget.v1"',
            "kSqliteAuthorizerOwnerClientDataName",
            '"anonsync.sqlite.authorizer-owner.v1"',
            "retained SQLite callback owners require distinct client-data slots",
        ))
        and "kSqliteBusyHandlerOwnerClientDataName" in owner
        and "kSqliteVerificationBudgetClientDataName" in verification_owner
        and "kSqliteAuthorizerOwnerClientDataName" in authorizer_owner
        and "callback_claim_.attach" in owner
        and all(token in claim_owner for token in (
            "registration_pending = 0",
            "live = 1",
            "detaching = 2",
            "sqlite3_get_clientdata",
            "sqlite3_set_clientdata",
        ))
        and "class SqliteRetainedCallbackClaim final" in claim_header
        and claim_header.count(
            "const SyncSqliteDatabaseMutexGuard& mutex_guard") == 3,
        "callback_slot_names_are_shared_and_claim_states_are_explicit",
        "alternate setters and all three owners use one distinct, compile-time-checked client-data namespace",
    )
    add(
        checks,
        ordered(
            owner,
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.attach(database",
            "mutation_guard",
            "sqlite3_busy_handler(database",
        )
        and ordered(
            owner,
            "void SqliteBusyHandlerOwner::detach() noexcept",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.require_live(database, mutation_guard)",
            "sqlite3_busy_handler(database, nullptr, nullptr)",
            "callback_claim_.detach(database, mutation_guard)",
            "database_borrow_.reset()",
        ),
        "busy_slot_claim_and_setter_are_one_serialized_transition",
        "constructor and teardown consume the exact shared mutex witness across the full claim/setter mutation",
    )
    add(
        checks,
        "test_concurrent_duplicate_owners_reject_without_fail_stop" in test
        and "kIterations = 64" in test
        and "one live owner and one recoverable rejection" in test,
        "concurrent_duplicate_busy_owners_have_runtime_oracle",
        "simultaneous legitimate constructors must yield one owner and one ordinary rejection without fail-stop",
    )
    add(
        checks,
        all(token in support_header for token in (
            "void sqlite_set_busy_timeout_or_throw(sqlite3* db",
            "void sqlite_set_busy_timeout_or_throw(SyncSqliteDbHandleSlot& db",
        ))
        and all(token in support_owner for token in (
            '#include "sync_sqlite_busy_timeout_mutation_guard.hpp"',
            "SyncSqliteBusyTimeoutMutationGuard mutation_guard(",
        ))
        and ordered(
            support_owner,
            "void sqlite_set_busy_timeout_or_throw(sqlite3* db",
            "SyncSqliteBusyTimeoutMutationGuard mutation_guard(",
            "sqlite3_get_clientdata(",
            "persistence::kSqliteBusyHandlerOwnerClientDataName",
            "sqlite3_busy_timeout(db, milliseconds)",
        ),
        "alternate_setter_probe_and_mutation_share_narrow_fence",
        "the ownership probe and timeout replacement share one non-authorizing process/thread-bound mutation fence",
    )
    add(
        checks,
        all(token in timeout_guard_header for token in (
            "class SyncSqliteBusyTimeoutMutationGuard final",
            "SyncSqliteBusyTimeoutMutationGuard&&) = delete",
            "SyncProcessIncarnation process_id_",
            "SyncThreadIncarnation thread_id_",
        ))
        and "bool authorizes" not in timeout_guard_header
        and "sqlite3_mutex* release" not in timeout_guard_header
        and ordered(
            timeout_guard_owner,
            "SyncSqliteBusyTimeoutMutationGuard::~SyncSqliteBusyTimeoutMutationGuard()",
            "require_current_sync_sqlite_execution_noexcept",
            "sqlite3_mutex_leave",
        )
        and ordered(
            execution_affinity,
            "sync_process_incarnation_is_current",
            "sync_thread_incarnation_is_current",
        )
        and all(marker in shared_process_test for marker in (
            "foreign-thread NOMUTEX busy-timeout guard destruction fails stopped",
            "inherited NOMUTEX busy-timeout guard destruction fails stopped",
        )),
        "busy_timeout_compatibility_guard_is_narrow_and_affine",
        "NOMUTEX compatibility carries no callback or transfer authority and cannot cross a process or exact-thread lifetime",
    )
    add(
        checks,
        ordered(
            support_owner,
            "void sqlite_set_busy_timeout_or_throw(SyncSqliteDbHandleSlot& db",
            "borrow_sync_sqlite_serialized_db_or_throw(",
            "sqlite_set_busy_timeout_or_throw(owner.get(), milliseconds, label)",
        )
        and "busy timeout must be nonnegative milliseconds" in support_owner
        and "cannot replace a live AnonSync SQLite busy-handler owner" in support_owner,
        "typed_gateway_pins_generation_and_rejects_live_owner",
        "typed calls retain exact-generation authority and invalid or conflicting configuration fails before mutation",
    )
    add(
        checks,
        "if (state == ClaimState::State::live)" in claim_owner
        and "thread_local void* g_authorized_retained_claim_destruction" in claim_owner
        and "g_authorized_retained_claim_destruction != claim" in claim_owner,
        "client_data_destruction_requires_state_and_exact_thread_witness",
        "transient pending/detaching state is not ambient destruction authority",
    )
    add(
        checks,
        ordered(
            owner,
            "void SqliteBusyHandlerOwner::detach() noexcept",
            "sqlite3_busy_handler(database, nullptr, nullptr)",
            "callbacks_active_.load",
            "callback_claim_.detach(database, mutation_guard)",
            "database_borrow_.reset()",
        ),
        "detach_revokes_callback_before_claim_and_generation",
        "no retained C address survives release of its exact generation pin",
    )
    add(
        checks,
        "SqliteBusyHandlerOwner::~SqliteBusyHandlerOwner() { detach(); }" in owner,
        "destructor_uses_the_reviewed_detach_protocol",
        "implicit destruction and explicit detach share one revocation path",
    )
    add(
        checks,
        "CallbackActivityScope activity(callbacks_active_)" in owner
        and "fetch_add(1U" in owner
        and "fetch_sub(1U" in owner,
        "callback_concurrency_and_reentry_fail_stopped",
        "serialized-use assumptions are executable rather than documentary",
    )
    add(
        checks,
        "saturating_atomic_add(invocations_" in owner
        and "saturating_atomic_add(sleep_milliseconds_" in owner,
        "diagnostic_counters_saturate",
        "hostile or pathological callback counts cannot wrap evidence",
    )
    add(
        checks,
        "SyncPeerTransportSqliteWriteContentionResult*" not in owner
        and "SyncPeerTransportSqliteWriteContentionResult*" not in header,
        "sqlite_callback_cannot_reach_caller_result_documents",
        "raw callback authority terminates at the focused atomic owner",
    )
    add(
        checks,
        "std::unique_ptr<persistence::SqliteBusyHandlerOwner> busy_handler" in lifecycle
        and "SyncPeerTransportSqliteWriteContentionResult* contention_sink" in lifecycle,
        "peer_connection_binds_callback_owner_and_cpp_sink",
        "the ordinary result sink is retained only by the enclosing C++ owner",
    )
    add(
        checks,
        "~PeerTransportIngressWriteConnection() { publish_contention_noexcept(); }" in lifecycle
        and "std::exchange(other.contention_sink, nullptr)" in lifecycle,
        "move_and_destruction_publish_exactly_once",
        "moved-from connections cannot publish or retain the sink",
    )
    add(
        checks,
        ordered(
            lifecycle,
            "struct PeerTransportIngressWriteConnection",
            "SyncSqliteDb owner",
            "SyncSqliteSerializedDbBorrow serialized",
            "std::unique_ptr<persistence::SqliteBusyHandlerOwner> busy_handler",
        ),
        "member_order_revokes_callback_before_connection_close",
        "reverse destruction tears down the retained context before strict close",
    )
    add(
        checks,
        "snapshot.invocations - published_busy_invocations" in lifecycle
        and "snapshot.sleep_milliseconds - published_busy_sleep_ms" in lifecycle
        and "saturating_peer_transport_counter_add" in lifecycle,
        "publication_is_delta_based_and_idempotent",
        "explicit publication plus destructor publication cannot double-count",
    )
    add(
        checks,
        "PeerTransportSqliteBusyHandlerContext" not in lifecycle
        and "peer_transport_sqlite_busy_handler" not in lifecycle
        and "sqlite3_busy_handler(" not in lifecycle,
        "legacy_monolith_callback_context_is_removed",
        "peer ingress no longer owns a private raw callback helper",
    )
    add(
        checks,
        "write_db->publish_contention_noexcept()" in lifecycle
        and "handoff_db.publish_contention_noexcept()" in lifecycle,
        "precopy_and_live_selftest_publication_are_explicit",
        "ordinary result documents are refreshed before in-scope inspection/copy",
    )
    add(
        checks,
        "handoff_db.busy_handler->contention_observed()" in lifecycle,
        "cross_thread_handoff_observes_atomic_owner",
        "the selftest no longer installs a caller-owned signal pointer",
    )
    add(
        checks,
        all(token in test for token in (
            "test_type_and_constructor_contract",
            "test_singleton_claim_and_explicit_reuse",
            "test_zero_timeout_fail_fast",
            "test_alternate_timeout_setter_is_fenced",
            "test_concurrent_alternate_setter_cannot_supersede_claim",
            "test_cross_thread_handoff_and_atomic_snapshot",
            "test_commit_phase_contention_is_observable",
        )),
        "focused_runtime_covers_lifetime_and_contention_edges",
        "constructor, reuse, alternate-setter rejection, timeout, cross-thread, and COMMIT paths are executable",
    )
    add(
        checks,
        "database.active_borrows() == 1U" in test
        and "database.active_borrows() == 0U" in test,
        "focused_test_proves_generation_pin_release",
        "the callback owner retains and releases exactly one typed generation",
    )
    add(
        checks,
        "third thread may observe intentionally shared callback state" in test
        and "quiescent foreign-thread detach" in test,
        "focused_test_proves_cross_thread_observation_and_detach",
        "shared diagnostics are atomic without pretending the object is thread-affine",
    )
    add(
        checks,
        "anonsync_sqlite_busy_handler_owner" in cmake.split(
            "add_executable(anonsync_sqlite_persistence_process_authority_fork_test", 1
        )[1].split("target_compile_options", 1)[0],
        "process_corpus_links_exact_busy_owner",
        "fork proofs execute the production callback owner rather than a test double",
    )
    add(
        checks,
        all(marker in process_test for marker in (
            "child cannot inspect an inherited busy-handler owner",
            "child cannot detach an inherited busy callback",
            "child destructor cannot detach an inherited busy-handler owner",
            "inherited SQLite contention reaches the process-bound busy callback",
            "child raw close cannot destroy an inherited busy-handler claim",
        )),
        "inherited_busy_owner_surfaces_fail_stopped",
        "access, detach, destruction, raw close, and live callback entry reject copied authority",
    )
    add(
        checks,
        all(marker in process_test for marker in (
            "raw close cannot destroy a live child-local busy-handler claim",
            "client-data replacement cannot destroy a live child-local busy-handler claim",
            "parent busy-handler generation survives hostile children",
            "child can mint and detach fresh busy-handler authority after fork",
        )),
        "client_data_claim_and_parent_survival_have_runtime_proofs",
        "premature same-process claim destruction fails while parent and child-local valid paths remain usable",
    )

    passed = all(check.passed for check in checks)
    payload = {
        "format": "anonsync-sqlite-busy-handler-owner-audit-v7",
        "passed": passed,
        "check_count": len(checks),
        "passed_check_count": sum(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "inventories": {
            "production_busy_handler_calls": busy_handler_sites,
            "production_busy_timeout_calls": busy_timeout_sites,
            "production_busy_timeout_gateway_calls": busy_timeout_gateway_sites,
            "production_busy_timeout_pragma_sites": busy_timeout_pragma_sites,
            "production_sqlite_sleep_calls": sqlite_sleep_sites,
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
