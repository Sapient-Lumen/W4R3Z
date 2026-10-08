#!/usr/bin/env python3
"""Audit AnonSync's retained SQLite mutex capability boundary.

This is a deterministic source-shape audit, not a proof of runtime behavior.
It protects the rev0778 invariants that one exact C++ thread incarnation owns
an entered SQLite recursive mutex and that SQLite connection destruction cannot
silently invalidate a retained mutex pointer.
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
    Path("src/sync_thread_incarnation.hpp"),
    Path("src/sync_thread_incarnation.cpp"),
    Path("src/sync_sqlite_mutex_capability.hpp"),
    Path("src/sync_sqlite_mutex_capability.cpp"),
    Path("src/sync_sqlite_execution_affinity.hpp"),
    Path("src/sync_sqlite_execution_affinity.cpp"),
    Path("src/sync_sqlite_database_mutex_guard.hpp"),
    Path("src/sync_sqlite_database_mutex_guard.cpp"),
    Path("src/sync_sqlite_busy_timeout_mutation_guard.hpp"),
    Path("src/sync_sqlite_busy_timeout_mutation_guard.cpp"),
    Path("src/persistence/sqlite_retained_callback_claim.hpp"),
    Path("src/persistence/sqlite_retained_callback_claim.cpp"),
    Path("src/persistence/sqlite_retained_callback_slots.hpp"),
    Path("src/persistence/sqlite_busy_handler_owner.hpp"),
    Path("src/persistence/sqlite_busy_handler_owner.cpp"),
    Path("src/persistence/sqlite_verification_budget.hpp"),
    Path("src/persistence/sqlite_verification_budget.cpp"),
    Path("src/persistence/sqlite_authorizer_owner.hpp"),
    Path("src/persistence/sqlite_authorizer_owner.cpp"),
    Path("src/sync_sqlite_connection_authority.hpp"),
    Path("src/sync_sqlite_connection_authority_internal.hpp"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("tests/thread_incarnation_tests.cpp"),
    Path("tests/sqlite_connection_authority_test.cpp"),
    Path("tests/sqlite_process_authority_fork_test.cpp"),
    Path("tests/sqlite_support_test.cpp"),
    Path("tests/persistence/sqlite_busy_handler_owner_tests.cpp"),
    Path("tests/persistence/sqlite_verification_budget_tests.cpp"),
    Path("tests/persistence/sqlite_authorizer_owner_tests.cpp"),
    Path("tools/verify_release_package.py"),
)

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
SKIP_PARTS = {".git", "third_party", "vendor"}
MUTEX_CALL = re.compile(r"\bsqlite3_mutex_(enter|leave)\s*\(")
CLIENT_DATA_CALL = re.compile(r"\bsqlite3_(get|set)_clientdata\s*\(")


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


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def source_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for base in (root / "src", root / "include"):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            rel = path.relative_to(root)
            if any(
                part in SKIP_PARTS
                or part == "build"
                or part == "_build"
                or part.startswith("build-")
                for part in rel.parts
            ):
                continue
            result.append(rel)
    return result


def line_inventory(
    root: Path, paths: list[Path], pattern: re.Pattern[str]
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for rel in paths:
        text = (root / rel).read_text(encoding="utf-8", errors="strict")
        for line_number, line in enumerate(text.splitlines(), 1):
            # This inventory is deliberately lexical, but comment references
            # are documentation rather than direct production calls.
            code = line.split("//", 1)[0]
            match = pattern.search(code)
            if match:
                result.append(
                    {
                        "path": rel.as_posix(),
                        "line": line_number,
                        "operation": match.group(1),
                        "text": line.strip()[:300],
                    }
                )
    return result


def function_body(text: str, signature_fragment: str) -> str:
    start = text.find(signature_fragment)
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


def ordered(body: str, *needles: str) -> bool:
    position = -1
    for needle in needles:
        found = body.find(needle, position + 1)
        if found < 0:
            return False
        position = found
    return True


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
            "format": "anonsync-sqlite-mutex-capability-audit-v5",
            "passed": False,
            "violations": [f"missing sensitive file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        sys.stdout.write(rendered)
        return 2

    texts = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in SENSITIVE_FILES
    }
    cmake = texts[Path("CMakeLists.txt")]
    thread_hpp = texts[Path("src/sync_thread_incarnation.hpp")]
    thread_cpp = texts[Path("src/sync_thread_incarnation.cpp")]
    capability_hpp = texts[Path("src/sync_sqlite_mutex_capability.hpp")]
    capability_cpp = texts[Path("src/sync_sqlite_mutex_capability.cpp")]
    execution_hpp = texts[Path("src/sync_sqlite_execution_affinity.hpp")]
    execution_cpp = texts[Path("src/sync_sqlite_execution_affinity.cpp")]
    guard_hpp = texts[Path("src/sync_sqlite_database_mutex_guard.hpp")]
    guard_cpp = texts[Path("src/sync_sqlite_database_mutex_guard.cpp")]
    timeout_guard_hpp = texts[
        Path("src/sync_sqlite_busy_timeout_mutation_guard.hpp")
    ]
    timeout_guard_cpp = texts[
        Path("src/sync_sqlite_busy_timeout_mutation_guard.cpp")
    ]
    claim_hpp = texts[Path("src/persistence/sqlite_retained_callback_claim.hpp")]
    claim_cpp = texts[Path("src/persistence/sqlite_retained_callback_claim.cpp")]
    busy_cpp = texts[Path("src/persistence/sqlite_busy_handler_owner.cpp")]
    verification_cpp = texts[Path("src/persistence/sqlite_verification_budget.cpp")]
    authorizer_hpp = texts[Path("src/persistence/sqlite_authorizer_owner.hpp")]
    authorizer_cpp = texts[Path("src/persistence/sqlite_authorizer_owner.cpp")]
    lease_hpp = texts[Path("src/sync_sqlite_connection_authority.hpp")]
    boundary_hpp = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    support_cpp = texts[Path("src/sync_sqlite_support.cpp")]
    callback_slots = texts[
        Path("src/persistence/sqlite_retained_callback_slots.hpp")
    ]
    thread_test = texts[Path("tests/thread_incarnation_tests.cpp")]
    authority_test = texts[Path("tests/sqlite_connection_authority_test.cpp")]
    process_test = texts[Path("tests/sqlite_process_authority_fork_test.cpp")]
    support_test = texts[Path("tests/sqlite_support_test.cpp")]
    busy_test = texts[Path("tests/persistence/sqlite_busy_handler_owner_tests.cpp")]
    verification_test = texts[
        Path("tests/persistence/sqlite_verification_budget_tests.cpp")
    ]
    authorizer_test = texts[
        Path("tests/persistence/sqlite_authorizer_owner_tests.cpp")
    ]
    release_verifier = texts[Path("tools/verify_release_package.py")]

    checks: list[Check] = []

    require(
        checks,
        "src/sync_sqlite_mutex_capability.cpp" in cmake,
        "capability_module_is_linked",
        "the retained-mutex capability implementation must remain in anonsync_sqlite_support",
    )
    require(
        checks,
        "add_library(anonsync_sqlite_database_mutex_guard STATIC" in cmake
        and "${ANONSYNC_SQLITE_EXECUTION_AFFINITY_SOURCE}" in cmake
        and "${ANONSYNC_SQLITE_DATABASE_MUTEX_GUARD_SOURCE}" in cmake
        and "${ANONSYNC_SQLITE_BUSY_TIMEOUT_MUTATION_GUARD_SOURCE}" in cmake
        and "anonsync_sqlite_database_mutex_guard" in cmake.split(
            "target_link_libraries(anonsync_sqlite_retained_callback_claim PUBLIC",
            1,
        )[1].split("target_compile_options", 1)[0]
        and "anonsync_sqlite_database_mutex_guard" in cmake.split(
            "target_link_libraries(anonsync_sqlite_support", 1
        )[1].split("target_compile_options", 1)[0],
        "database_mutex_guard_is_independent_shared_dependency",
        "the scoped connection-mutex owner must be separately linked into both the claim primitive and SQLite support",
    )
    require(
        checks,
        "revision_number >= 854" in release_verifier
        and all(
            f'"{path}"' in release_verifier
            for path in (
                "src/sync_sqlite_database_mutex_guard.hpp",
                "src/sync_sqlite_database_mutex_guard.cpp",
                "tests/sqlite_support_test.cpp",
                "tools/audit_sqlite_mutex_capability.py",
            )
        ),
        "release_verifier_requires_database_mutex_guard_from_rev0854",
        "sealed rev0854+ packages must carry the typed guard, its direct runtime proof, and its structural audit without invalidating older parents",
    )
    require(
        checks,
        "revision_number >= 855" in release_verifier
        and all(
            f'"{path}"' in release_verifier
            for path in (
                "src/sync_sqlite_execution_affinity.hpp",
                "src/sync_sqlite_execution_affinity.cpp",
                "src/sync_sqlite_busy_timeout_mutation_guard.hpp",
                "src/sync_sqlite_busy_timeout_mutation_guard.cpp",
                "tests/sqlite_process_authority_fork_test.cpp",
            )
        ),
        "release_verifier_requires_split_mutation_guards_from_rev0855",
        "sealed rev0855+ packages must carry the shared affinity validator, narrow timeout guard, and fail-stop process proof",
    )

    require(
        checks,
        "sync_sqlite_thread_affinity" not in "\n".join(texts.values()),
        "obsolete_affinity_module_is_absent",
        "the superseded thread-only module name must not remain in sensitive source",
    )
    require(
        checks,
        "using SyncSqliteThreadIncarnation = SyncThreadIncarnation" in capability_hpp
        and '#include "sync_thread_incarnation.hpp"' in capability_hpp,
        "incarnation_has_explicit_type",
        "SQLite must reuse the generic opaque thread-lifetime proof rather than mint a parallel numeric type",
    )
    require(
        checks,
        "class SyncThreadIncarnation final" in thread_hpp
        and "bool valid() const noexcept" in thread_hpp
        and "!std::is_trivially_copyable_v<SyncThreadIncarnation>" in thread_hpp
        and "!std::is_constructible_v<SyncThreadIncarnation, std::uint64_t>"
        in thread_hpp,
        "incarnation_is_opaque_domain_separated_proof",
        "ordinary integers, persisted rows, wire values, and bit-cast bytes must not manufacture live thread authority",
    )
    for needle, check_id, detail in (
        (
            "constinit std::atomic<std::uint64_t> next_thread_incarnation_raw{1U}",
            "incarnation_allocator_is_atomic",
            "thread incarnations must be allocated across threads without collision",
        ),
        (
            "constinit thread_local ThreadLocalIncarnationRaw live_thread_incarnation_raw",
            "incarnation_has_process_aware_thread_local_state",
            "fork-copied raw thread-local bytes must be paired with their minting process",
        ),
        (
            "compare_exchange_weak",
            "incarnation_allocator_is_monotonic",
            "the allocator must consume one process-local generation per thread",
        ),
        (
            "std::numeric_limits<std::uint64_t>::max()",
            "incarnation_exhaustion_is_detected",
            "wraparound must not reauthorize a stale thread generation",
        ),
        (
            "fail_stop_on_sync_thread_capability_violation_noexcept()",
            "incarnation_exhaustion_uses_unhookable_fail_stop",
            "counter exhaustion cannot be routed through a replaceable terminate handler",
        ),
        (
            "std::atomic<std::uint64_t>::is_always_lock_free",
            "incarnation_allocator_is_lock_free_after_fork",
            "the child must not inherit a hidden allocator lock owned by a vanished thread",
        ),
    ):
        require(checks, needle in thread_cpp, check_id, detail)

    require(
        checks,
        "static std::atomic" not in function_body(
            thread_cpp, "allocate_thread_incarnation_noexcept() noexcept"
        )
        and "Namespace storage is constant-initialized" in thread_cpp,
        "incarnation_allocator_avoids_function_local_guard",
        "first use after fork must not wait on a copied function-static initialization guard",
    )
    require(
        checks,
        "struct ThreadLocalIncarnationRaw final" in thread_cpp
        and "std::uint64_t process_raw" in thread_cpp
        and "std::uint64_t incarnation_raw" in thread_cpp
        and "std::is_trivially_copyable_v<ThreadLocalIncarnationRaw>" in thread_cpp
        and "std::is_trivially_destructible_v<ThreadLocalIncarnationRaw>" in thread_cpp,
        "incarnation_thread_local_avoids_destructor_registration",
        "post-fork lookup must not enter a copied TLS guard or __cxa_thread_atexit path",
    )
    require(
        checks,
        ordered(
            function_body(
                thread_cpp,
                "current_sync_thread_incarnation_noexcept() noexcept",
            ),
            "current_sync_process_incarnation_noexcept",
            "SyncProcessIncarnationAccess::raw(current_process)",
            "live_thread_incarnation_raw.process_raw != current_process_raw",
            "allocate_thread_incarnation_noexcept",
            "live_thread_incarnation_raw.process_raw = current_process_raw",
            "SyncThreadIncarnationAccess::raw(replacement)",
            "SyncThreadIncarnationAccess::from_raw",
        ),
        "fork_reseeds_thread_incarnation",
        "a child process must never retain the parent's exact thread generation",
    )
    require(
        checks,
        ordered(
            function_body(
                capability_cpp,
                "current_sync_sqlite_thread_incarnation_noexcept() noexcept",
            ),
            "current_sync_thread_incarnation_noexcept",
        )
        and ordered(
            function_body(
                capability_cpp,
                "sync_sqlite_thread_incarnation_is_current(",
            ),
            "sync_thread_incarnation_is_current",
        )
        and "allocate_thread_incarnation_noexcept" not in capability_cpp,
        "sqlite_adapter_delegates_generic_incarnation_owner",
        "SQLite preserves its API and error vocabulary without duplicating allocation or fork logic",
    )
    require(
        checks,
        all(
            token in thread_test
            for token in (
                "test_live_and_recycled_threads_receive_unique_incarnations",
                "test_fork_refreshes_thread_identity",
                "test_noexcept_foreign_thread_violation_fails_stopped",
                "!std::is_trivially_copyable_v<SyncThreadIncarnation>",
            )
        ),
        "generic_incarnation_has_direct_runtime_and_type_proof",
        "uniqueness, native-ID reuse resistance, fork refresh, fail-stop, and opacity are executable",
    )

    for marker in (
        "std::thread::id",
        "std::this_thread::get_id",
        "hash<std::thread::id>",
        "pthread_self",
    ):
        require(
            checks,
            marker not in thread_cpp and marker not in capability_cpp,
            "incarnation_avoids_" + re.sub(r"[^a-z0-9]+", "_", marker.lower()).strip("_"),
            f"retained authority must not depend on reusable or representation-specific {marker}",
        )

    for needle, check_id, detail in (
        (
            "SQLITE_VERSION_NUMBER >= 3044000",
            "clientdata_version_floor_is_explicit",
            "the lifetime sentinel requires SQLite connection client data",
        ),
        (
            '"anonsync.sqlite.retained-mutex-capabilities.v1"',
            "lifetime_sentinel_has_versioned_namespace",
            "the SQLite-owned sentinel must use a stable, narrow namespace",
        ),
        (
            "SyncSqliteRetainedMutexCapabilityState* self = this",
            "lifetime_sentinel_is_self_authenticating",
            "corrupt or alien client data must fail closed",
        ),
        (
            "std::uint64_t active_capabilities = 0",
            "lifetime_sentinel_counts_retained_entries",
            "connection destruction must know whether any mutex entry remains retained",
        ),
    ):
        require(checks, needle in capability_cpp, check_id, detail)

    destroy_body = function_body(
        capability_cpp, "void destroy_retained_mutex_capability_state(void* raw)"
    )
    require(checks, bool(destroy_body), "lifetime_destructor_is_present", "SQLite must own one sentinel destructor")
    require(
        checks,
        "state->active_capabilities != 0" in destroy_body
        and "fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept" in destroy_body,
        "connection_close_with_live_entry_fails_stopped",
        "close or replacement may not invalidate a still-retained sqlite3_db_mutex pointer",
    )
    require(
        checks,
        ordered(destroy_body, "state->magic = 0", "state->self = nullptr", "delete state"),
        "lifetime_sentinel_is_poisoned_before_delete",
        "normal close must invalidate diagnostic markers before deallocation",
    )

    retain_body = function_body(
        capability_cpp, "retain_sync_sqlite_mutex_capability_or_throw("
    )
    require(
        checks,
        "db == nullptr" in retain_body and "std::invalid_argument" in retain_body,
        "retain_rejects_null_database",
        "client-data lookup must never receive an empty connection handle",
    )
    require(
        checks,
        "sqlite3_set_clientdata" in retain_body
        and "destroy_retained_mutex_capability_state" in retain_body,
        "retain_installs_sqlite_owned_sentinel",
        "SQLite connection lifetime must own and destroy the sentinel",
    )
    require(
        checks,
        "std::numeric_limits<std::uint64_t>::max()" in retain_body
        and "std::overflow_error" in retain_body,
        "retained_entry_count_rejects_overflow",
        "counter wraparound must not make a live close appear safe",
    )
    require(
        checks,
        ordered(retain_body, "active_capabilities ==", "++state->active_capabilities", "return state"),
        "retain_increments_before_return",
        "a capability may escape only after its lifetime pin exists",
    )

    release_body = function_body(
        capability_cpp, "void release_sync_sqlite_mutex_capability_noexcept("
    )
    require(
        checks,
        all(
            needle in release_body
            for needle in ("state == nullptr", "state->magic", "state->self", "active_capabilities == 0")
        ),
        "release_validates_sentinel_and_count",
        "underflow, corruption, or an absent lifetime pin must fail stopped",
    )
    require(
        checks,
        ordered(release_body, "--state->active_capabilities", "state = nullptr"),
        "release_consumes_local_pointer_after_decrement",
        "the exact owner must not retain a usable pointer after releasing its entry",
    )

    require(
        checks,
        "owner_thread_incarnation_" in lease_hpp
        and "retained_capability_state_" in lease_hpp,
        "lease_carries_thread_and_lifetime_proofs",
        "a retained connection lease must carry both exact thread and connection-lifetime state",
    )
    require(
        checks,
        "owner_thread_incarnation" in boundary_hpp
        and "retained_capability_state" in boundary_hpp,
        "transaction_proof_carries_thread_and_lifetime_proofs",
        "both fenced and utility transactions must retain the same dynamic ownership evidence",
    )
    require(
        checks,
        "class RetainedMutexCapabilityReservation" in authority_cpp,
        "retention_is_exception_safe",
        "temporary retention must unwind before the scoped database mutex leaves",
    )
    require(
        checks,
        authority_cpp.count("RetainedMutexCapabilityReservation retained_capability") >= 3,
        "all_retaining_acquisition_branches_reserve_lifetime",
        "connection lease plus fenced and unfenced transaction paths must pin connection lifetime",
    )
    require(
        checks,
        authority_cpp.count("proof.owner_thread_incarnation =") >= 2,
        "both_transaction_branches_capture_thread_incarnation",
        "fenced and unfenced typed transaction generations must bind the entering thread",
    )

    guard_destructor = function_body(
        guard_cpp, "SyncSqliteDatabaseMutexGuard::~SyncSqliteDatabaseMutexGuard()"
    )
    guard_release = function_body(
        guard_cpp, "sqlite3_mutex* SyncSqliteDatabaseMutexGuard::release() noexcept"
    )
    guard_execution = function_body(
        execution_cpp,
        "void require_current_sync_sqlite_execution_noexcept(",
    )
    timeout_guard_constructor = function_body(
        timeout_guard_cpp,
        "SyncSqliteBusyTimeoutMutationGuard::SyncSqliteBusyTimeoutMutationGuard(",
    )
    timeout_guard_destructor = function_body(
        timeout_guard_cpp,
        "SyncSqliteBusyTimeoutMutationGuard::~SyncSqliteBusyTimeoutMutationGuard()",
    )
    guard_authorizes = function_body(
        guard_cpp,
        "bool SyncSqliteDatabaseMutexGuard::authorizes(sqlite3* database) const noexcept",
    )
    require(
        checks,
        ordered(
            guard_execution,
            "sync_process_incarnation_is_current",
            "sync_thread_incarnation_is_current",
        )
        and ordered(
            guard_destructor,
            "require_current_execution_noexcept",
            "sqlite3_mutex_leave",
        )
        and "require_current_sync_sqlite_execution_noexcept" in guard_cpp
        and ordered(
            timeout_guard_destructor,
            "require_current_sync_sqlite_execution_noexcept",
            "sqlite3_mutex_leave",
        ),
        "scoped_sqlite_guards_share_process_then_thread_teardown",
        "strict and NOMUTEX-compatible scoped owners reject fork/thread transfer before leaving SQLite-owned state",
    )
    require(
        checks,
        ordered(
            guard_release,
            "require_current_execution_noexcept",
            "mutex_ == nullptr",
            "mutex_ = nullptr",
            "database_ = nullptr",
        ),
        "shared_mutex_guard_transfer_checks_and_consumes_identity",
        "an entered mutex may transfer only on its originating execution and must consume both mutex and database identity",
    )
    require(
        checks,
        all(
            marker in guard_hpp
            for marker in (
                "class SyncSqliteDatabaseMutexGuard final",
                "SyncSqliteDatabaseMutexGuard(SyncSqliteDatabaseMutexGuard&&) = delete",
                "bool authorizes(sqlite3* database) const noexcept",
                "sqlite3* database_ = nullptr",
                "SyncProcessIncarnation process_id_",
                "SyncThreadIncarnation thread_id_",
            )
        )
        and "SyncSqliteDatabaseMutexRequirement" not in guard_hpp
        and "PermitUnserialized" not in guard_hpp
        and ordered(
            guard_cpp,
            "mutex_ = sqlite3_db_mutex(database)",
            "requires a serialized/FULLMUTEX SQLite connection",
            "sqlite3_mutex_enter(mutex_)",
        )
        and all(
            marker in guard_authorizes
            for marker in (
                "database_ == database",
                "mutex_ != nullptr",
            )
        ),
        "strict_mutex_guard_binds_exact_database_and_serialized_entry",
        "retained callback mutation consumes only a nonmovable exact-database FULLMUTEX witness",
    )
    require(
        checks,
        all(
            marker in timeout_guard_hpp
            for marker in (
                "class SyncSqliteBusyTimeoutMutationGuard final",
                "SyncSqliteBusyTimeoutMutationGuard&&) = delete",
                "SyncProcessIncarnation process_id_",
                "SyncThreadIncarnation thread_id_",
            )
        )
        and "bool authorizes" not in timeout_guard_hpp
        and "sqlite3_mutex* release" not in timeout_guard_hpp
        and ordered(
            timeout_guard_constructor,
            "mutex_ = sqlite3_db_mutex(database)",
            "if (mutex_ != nullptr)",
            "sqlite3_mutex_enter(mutex_)",
        )
        and all(marker in support_test for marker in (
            "!RetainedCallbackMutexWitness<",
            "!TransferableSqliteMutexEntry<",
            "narrow NOMUTEX busy-timeout mutation guard remains usable",
        ))
        and all(marker in process_test for marker in (
            "foreign-thread NOMUTEX busy-timeout guard destruction fails stopped",
            "inherited NOMUTEX busy-timeout guard destruction fails stopped",
            "released database-mutex guard destruction remains thread affine",
        )),
        "timeout_mutation_guard_is_narrow_non_authorizing_and_affine",
        "the raw NOMUTEX compatibility lane has no callback or transfer surface and carries executable fork/thread teardown proofs",
    )
    require(
        checks,
        "const SyncSqliteDatabaseMutexGuard& mutex_guard" in claim_hpp
        and claim_hpp.count("const SyncSqliteDatabaseMutexGuard& mutex_guard") == 3
        and claim_cpp.count("mutex_guard.authorizes(database)") == 2
        and "require_live(database, mutex_guard)" in claim_cpp,
        "retained_callback_claim_requires_typed_mutex_witness",
        "attach, liveness proof, and detach cannot touch SQLite client data without the exact live connection-mutex guard in their signatures",
    )

    lease_owner_helper = function_body(
        authority_cpp, "void require_retained_mutex_lease_owner_noexcept("
    )
    require(
        checks,
        ordered(
            lease_owner_helper,
            "retained_mutex_lease_shape_is_valid",
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_mutex_capability_is_live_noexcept",
        ),
        "lease_owner_helper_checks_shape_thread_lifetime",
        "shared lease validation must reject foreign callers before dereferencing SQLite-owned state",
    )

    lease_destructor = function_body(
        authority_cpp,
        "SyncSqliteConnectionAuthorityLease::~SyncSqliteConnectionAuthorityLease()",
    )
    require(
        checks,
        ordered(
            lease_destructor,
            "require_retained_mutex_lease_owner_noexcept",
            "release_sync_sqlite_mutex_capability_noexcept",
            "sqlite3_mutex_leave",
        ),
        "lease_destructor_orders_thread_lifetime_release",
        "foreign destruction must stop before dereferencing SQLite-owned state or leaving the mutex",
    )

    lease_move = function_body(
        authority_cpp,
        "SyncSqliteConnectionAuthorityLease::SyncSqliteConnectionAuthorityLease(\n    SyncSqliteConnectionAuthorityLease&& other)",
    )
    require(
        checks,
        "require_retained_mutex_lease_owner_noexcept" in lease_move,
        "lease_move_constructor_checks_thread_before_lifetime",
        "foreign transfer must not inspect potentially invalid SQLite-owned memory",
    )
    lease_move_assign = function_body(
        authority_cpp,
        "SyncSqliteConnectionAuthorityLease::operator=(\n    SyncSqliteConnectionAuthorityLease&& other)",
    )
    require(
        checks,
        lease_move_assign.count("require_retained_mutex_lease_owner_noexcept") >= 2,
        "lease_move_assignment_fences_both_entries",
        "destination release and source acquisition must each prove exact ownership",
    )
    require(
        checks,
        ordered(
            lease_move_assign,
            "release_sync_sqlite_mutex_capability_noexcept",
            "sqlite3_mutex_leave",
        ),
        "lease_move_assignment_unpins_before_leave",
        "the connection-lifetime count must be decremented while the mutex pointer is still valid",
    )

    lease_active = function_body(
        authority_cpp, "bool SyncSqliteConnectionAuthorityLease::active() const noexcept"
    )
    require(
        checks,
        ordered(
            lease_active,
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_mutex_capability_is_live_noexcept",
        ),
        "lease_observation_checks_thread_before_lifetime",
        "foreign active() must fail closed without touching SQLite-owned sentinel memory",
    )

    transaction_release = function_body(
        authority_cpp, "void release_sync_sqlite_transaction_mutex_noexcept("
    )
    require(
        checks,
        ordered(
            transaction_release,
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_mutex_capability_is_live_noexcept",
            "release_sync_sqlite_mutex_capability_noexcept",
            "sqlite3_mutex_leave",
        ),
        "transaction_release_orders_thread_lifetime_release",
        "transaction revocation must prove owner, unpin lifetime, then leave the exact entry",
    )

    boundary_validate = function_body(
        authority_cpp, "ConnectionAuthorityState& validate_boundary_proof_or_throw("
    )
    require(
        checks,
        ordered(
            boundary_validate,
            "require_sync_sqlite_thread_incarnation_or_throw",
            "sync_sqlite_mutex_capability_is_live_noexcept",
        ),
        "transaction_validator_checks_thread_before_lifetime",
        "proof validation must reject a foreign caller before dereferencing SQLite-owned sentinel memory",
    )

    boundary_status = function_body(
        authority_cpp,
        "sync_sqlite_transaction_boundary_authority_status_noexcept(",
    )
    require(
        checks,
        ordered(
            boundary_status,
            "sync_process_incarnation_is_current",
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_mutex_capability_is_live_noexcept",
            "sqlite3_db_mutex",
        ),
        "transaction_observation_checks_authority_before_sqlite_state",
        "foreign copied authority must reject process, thread, and lifetime before SQLite mutex acquisition",
    )

    transaction_authorizes = function_body(
        transaction_cpp, "bool SyncSqliteTransactionAuthority::authorizes(sqlite3* db) const noexcept"
    )
    require(
        checks,
        ordered(
            transaction_authorizes,
            "sync_process_incarnation_is_current",
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_transaction_boundary_authority_status_noexcept",
        ),
        "copied_authority_rejects_foreign_process_and_thread_early",
        "foreign observation must reject live-owner mismatch before the recursive mutex probe",
    )
    require(
        checks,
        transaction_authorizes.find("return false")
        < transaction_authorizes.find("state->active.store(false"),
        "foreign_observation_does_not_revoke_owner",
        "a non-owner observation is unusable but must preserve the exact owner generation",
    )

    transaction_destructor = function_body(
        transaction_cpp, "SyncSqliteTransaction::~SyncSqliteTransaction()"
    )
    require(
        checks,
        ordered(
            transaction_destructor,
            "sync_sqlite_thread_incarnation_is_current",
            "rollback_sync_sqlite_transaction_boundary_noexcept",
        ),
        "transaction_destructor_fails_before_foreign_rollback",
        "a foreign destructor must not touch SQLite or attempt unsafe cleanup",
    )
    for method in ("commit", "rollback"):
        body = function_body(transaction_cpp, f"void SyncSqliteTransaction::{method}()")
        require(
            checks,
            ordered(
                body,
                "require_sync_process_incarnation_or_fail_stop",
                "require_sync_sqlite_thread_incarnation_or_throw",
                "sync_sqlite_transaction_boundary_authority_status_noexcept",
            ),
            f"transaction_{method}_rejects_foreign_owner_before_authority",
            f"foreign {method.upper()} must throw before any SQLite authority probe",
        )

    retirement_probe_body = function_body(
        authority_test, "void run() noexcept"
    )
    require(
        checks,
        "std::uint64_t completed = 0U" in retirement_probe_body
        and "observed = request_.load" not in retirement_probe_body
        and ordered(
            retirement_probe_body,
            "request_.load(std::memory_order_acquire)",
            "stop_.load(std::memory_order_acquire)",
            "if (requested == completed)",
            "request_.wait(requested, std::memory_order_acquire)",
            "completed_.store(requested, std::memory_order_release)",
            "completed = requested",
        ),
        "policy_retirement_probe_waits_from_completed_ticket",
        "a request published before worker startup must be processed rather than copied into a lost-notification wait predicate",
    )
    require(
        checks,
        "test_policy_retirement_probe_cannot_lose_prestart_request" in authority_test
        and "PolicyRetirementMutexProbe probe(db.get(), 1U)" in authority_test
        and "probe.completed_requests() < 1U" in authority_test
        and ordered(
            authority_test,
            "test_install_probe_and_policy(checks)",
            "test_policy_retirement_probe_cannot_lose_prestart_request(checks)",
            "test_owned_policy_context_lifetime_and_retirement(checks)",
        ),
        "policy_retirement_prestart_request_has_deterministic_regression",
        "the exact former lost-first-request schedule must execute before ordinary owned-context retirement coverage",
    )

    require(
        checks,
        "PROPERTIES TIMEOUT 15" in cmake,
        "authority_ctest_has_finite_timeout",
        "a future self-deadlock regression must remain a bounded validation failure",
    )
    for needle, check_id, detail in (
        (
            "test_thread_incarnation_affinity",
            "foreign_observation_and_finalization_tests_exist",
            "foreign active/authority/commit/rollback paths need executable coverage",
        ),
        (
            "test_owner_thread_lease_moves",
            "owner_move_semantics_are_tested",
            "normal move, self-move, and move assignment must preserve exact retained entries",
        ),
        (
            "child_foreign_lease_destruction",
            "foreign_lease_destruction_death_test_exists",
            "noexcept destruction must prove the intended fail-stop",
        ),
        (
            "child_foreign_transaction_destruction",
            "foreign_transaction_destruction_death_test_exists",
            "foreign destructor rollback/release must never run",
        ),
        (
            "child_foreign_lease_move",
            "foreign_lease_move_death_test_exists",
            "moving a live retained mutex entry to another thread must fail stopped",
        ),
        (
            "child_close_with_live_lease",
            "same_thread_close_death_test_exists",
            "recursive same-thread close must not free a retained connection mutex",
        ),
        (
            "child_close_with_live_unfenced_transaction",
            "unfenced_transaction_close_death_test_exists",
            "the close fence must not depend on authorizer installation",
        ),
        (
            "child_close_with_live_fenced_transaction",
            "fenced_transaction_close_death_test_exists",
            "the close fence must protect authorizer-fenced transaction ownership too",
        ),
        (
            "child_replace_live_capability_sentinel",
            "live_sentinel_replacement_death_test_exists",
            "replacement of SQLite-owned lifetime state must not invalidate a retained mutex pointer",
        ),
        (
            "child_zombie_close_with_live_lease",
            "zombie_close_death_test_exists",
            "deferred sqlite3_close_v2 destruction must remain fail stopped",
        ),
        (
            "test_close_waits_for_retained_mutex_capability",
            "foreign_close_serialization_test_exists",
            "a foreign close must wait and then succeed after normal release",
        ),
        (
            "SQLITE_OPEN_NOMUTEX",
            "nomutex_rejection_remains_tested",
            "the capability requires a real serialized connection mutex",
        ),
    ):
        require(checks, needle in authority_test, check_id, detail)

    require(
        checks,
        "thread incarnation" in support_hpp.lower()
        and "fails stopped" in support_hpp.lower(),
        "public_transaction_contract_documents_fail_stop",
        "callers must know that thread handoff is not recoverable in a destructor",
    )

    production_sources = source_files(root)
    mutex_inventory = line_inventory(root, production_sources, MUTEX_CALL)
    mutex_owners = {item["path"] for item in mutex_inventory}
    require(
        checks,
        mutex_owners == {
            "src/sync_sqlite_connection_authority.cpp",
            "src/sync_sqlite_database_mutex_guard.cpp",
            "src/sync_sqlite_busy_timeout_mutation_guard.cpp",
        }
        and "class DbMutexGuard" not in authority_cpp
        and "class SqliteDatabaseMutexScope" not in support_cpp
        and "SyncSqliteBusyTimeoutMutationGuard mutation_guard" in support_cpp,
        "direct_sqlite_mutex_calls_have_three_reviewed_owners",
        "manual retained leases, strict callback witnesses, and the non-authorizing timeout fence are the only SQLite mutex owners",
    )
    require(
        checks,
        any(item["operation"] == "enter" for item in mutex_inventory)
        and any(item["operation"] == "leave" for item in mutex_inventory),
        "mutex_inventory_contains_enter_and_leave",
        "the source audit must observe both sides of the retained mutex protocol",
    )
    require(
        checks,
        all(
            ordered(text, "SyncSqliteDatabaseMutexGuard mutation_guard",
                    "callback_claim_.attach(database", "mutation_guard")
            for text in (busy_cpp, verification_cpp, authorizer_cpp)
        )
        and all(
            "callback_claim_.detach(database, mutation_guard)" in text
            for text in (busy_cpp, verification_cpp, authorizer_cpp)
        )
        and "callback_claim_.require_live(database, mutation_guard)" in authorizer_cpp,
        "all_retained_callback_slot_transitions_consume_shared_guard",
        "busy, progress, and authorizer claim/setter transitions share one exact-database recursive mutex protocol",
    )
    require(
        checks,
        "test_concurrent_duplicate_owners_reject_without_fail_stop" in busy_test
        and "test_concurrent_duplicate_budgets_reject_without_fail_stop"
        in verification_test
        and "test_concurrent_duplicate_owners_reject_without_fail_stop"
        in authorizer_test
        and all(
            "kIterations = 64" in text
            for text in (busy_test, verification_test, authorizer_test)
        )
        and all(
            "one live owner and one recoverable rejection" in text
            for text in (busy_test, verification_test, authorizer_test)
        ),
        "concurrent_duplicate_slot_races_have_runtime_oracles",
        "each singleton callback slot executes repeated simultaneous construction with exactly one winner and one nonfatal loser",
    )
    require(
        checks,
        all(
            marker in support_test
            for marker in (
                "database mutex guard owns the exact connection mutex",
                "database mutex guard composes through recursive entry",
                "database mutex guard excludes a competing thread",
                "strict database mutex guard rejects a NOMUTEX connection",
                "database mutex guard transfers the exact entered mutex once",
            )
        ),
        "shared_mutex_guard_has_direct_runtime_proof",
        "focused support tests cover exact identity, recursion, exclusion, NOMUTEX rejection, and one-way transfer",
    )

    clientdata_inventory = line_inventory(root, production_sources, CLIENT_DATA_CALL)
    clientdata_owners = {item["path"] for item in clientdata_inventory}
    require(
        checks,
        clientdata_owners
        == {
            "src/persistence/sqlite_retained_callback_claim.cpp",
            "src/sync_sqlite_connection_authority.cpp",
            "src/sync_sqlite_mutex_capability.cpp",
            "src/sync_sqlite_support.cpp",
        }
        and '"anonsync.sqlite-busy-handler-owner.v1"' in callback_slots
        and '"anonsync.sqlite-verification-budget.v1"' in callback_slots
        and '"anonsync.sqlite.authorizer-owner.v1"' in callback_slots
        and "kSqliteBusyHandlerOwnerClientDataName" in support_cpp
        and "SqliteRetainedCallbackClaim callback_claim_" in texts[
            Path("src/persistence/sqlite_busy_handler_owner.hpp")
        ]
        and "SqliteRetainedCallbackClaim callback_claim_" in texts[
            Path("src/persistence/sqlite_verification_budget.hpp")
        ],
        "clientdata_calls_have_four_primitive_owners_and_five_namespaces",
        "connection authority, retained mutex, authorizer, busy, and verification client-data lifetimes remain composition-owned",
    )

    checks_data = [asdict(check) for check in checks]
    violations = [check.detail for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-mutex-capability-audit-v5",
        "passed": not violations,
        "check_count": len(checks),
        "passed_check_count": sum(1 for check in checks if check.passed),
        "violations": violations,
        "checks": checks_data,
        "mutex_call_inventory": mutex_inventory,
        "clientdata_call_inventory": clientdata_inventory,
        "sensitive_file_sha256": {
            path.as_posix(): sha256_file(root / path) for path in SENSITIVE_FILES
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
