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
    Path("src/sync_sqlite_mutex_capability.hpp"),
    Path("src/sync_sqlite_mutex_capability.cpp"),
    Path("src/sync_sqlite_connection_authority.hpp"),
    Path("src/sync_sqlite_connection_authority_internal.hpp"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("src/sync_sqlite_support.hpp"),
    Path("tests/sqlite_connection_authority_test.cpp"),
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
            "format": "anonsync-sqlite-mutex-capability-audit-v1",
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
    capability_hpp = texts[Path("src/sync_sqlite_mutex_capability.hpp")]
    capability_cpp = texts[Path("src/sync_sqlite_mutex_capability.cpp")]
    lease_hpp = texts[Path("src/sync_sqlite_connection_authority.hpp")]
    boundary_hpp = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    authority_test = texts[Path("tests/sqlite_connection_authority_test.cpp")]

    checks: list[Check] = []

    require(
        checks,
        "src/sync_sqlite_mutex_capability.cpp" in cmake,
        "capability_module_is_linked",
        "the retained-mutex capability implementation must remain in anonsync_sqlite_support",
    )
    require(
        checks,
        "sync_sqlite_thread_affinity" not in "\n".join(texts.values()),
        "obsolete_affinity_module_is_absent",
        "the superseded thread-only module name must not remain in sensitive source",
    )
    require(
        checks,
        "using SyncSqliteThreadIncarnation = std::uint64_t" in capability_hpp,
        "incarnation_has_explicit_type",
        "process-local thread lifetime identity must use one named nonserializable type",
    )
    for needle, check_id, detail in (
        (
            "std::atomic<SyncSqliteThreadIncarnation>",
            "incarnation_allocator_is_atomic",
            "thread incarnations must be allocated across threads without collision",
        ),
        (
            "thread_local ThreadLocalIncarnation local",
            "incarnation_has_process_aware_thread_local_state",
            "fork-copied thread-local bytes must be paired with their minting process",
        ),
        (
            "compare_exchange_weak",
            "incarnation_allocator_is_monotonic",
            "the allocator must consume one process-local generation per thread",
        ),
        (
            "std::numeric_limits<SyncSqliteThreadIncarnation>::max()",
            "incarnation_exhaustion_is_detected",
            "wraparound must not reauthorize a stale thread generation",
        ),
        (
            "fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept()",
            "incarnation_exhaustion_uses_unhookable_fail_stop",
            "counter exhaustion cannot be routed through a replaceable terminate handler",
        ),
    ):
        require(checks, needle in capability_cpp, check_id, detail)

    require(
        checks,
        ordered(
            function_body(
                capability_cpp,
                "current_sync_sqlite_thread_incarnation_noexcept() noexcept",
            ),
            "current_sync_sqlite_process_id_noexcept",
            "local.process_id != current_process",
            "allocate_thread_incarnation_noexcept",
        ),
        "fork_reseeds_thread_incarnation",
        "a child process must never retain the parent's exact thread generation",
    )

    for marker in (
        "std::thread::id",
        "std::this_thread::get_id",
        "hash<std::thread::id>",
        "pthread_self",
    ):
        require(
            checks,
            marker not in capability_cpp,
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

    db_guard_destructor = function_body(authority_cpp, "~DbMutexGuard()")
    db_guard_release = function_body(authority_cpp, "sqlite3_mutex* release() noexcept")
    require(
        checks,
        ordered(db_guard_destructor, "sync_sqlite_thread_incarnation_is_current", "sqlite3_mutex_leave"),
        "scoped_mutex_guard_destructor_checks_thread_first",
        "even private scoped mutex ownership must not rely on convention",
    )
    require(
        checks,
        ordered(db_guard_release, "sync_sqlite_thread_incarnation_is_current", "mutex_ = nullptr"),
        "scoped_mutex_transfer_checks_thread_first",
        "an entered mutex may transfer only on its originating thread",
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

    boundary_authorizes = function_body(
        authority_cpp, "bool sync_sqlite_transaction_boundary_authorizes_noexcept("
    )
    require(
        checks,
        ordered(
            boundary_authorizes,
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_mutex_capability_is_live_noexcept",
            "sqlite3_db_mutex",
        ),
        "transaction_observation_checks_thread_before_sqlite_state",
        "foreign copied authority must return before sentinel dereference or SQLite mutex acquisition",
    )

    transaction_authorizes = function_body(
        transaction_cpp, "bool SyncSqliteTransactionAuthority::authorizes(sqlite3* db) const noexcept"
    )
    require(
        checks,
        ordered(
            transaction_authorizes,
            "sync_sqlite_thread_incarnation_is_current",
            "sync_sqlite_transaction_boundary_authorizes_noexcept",
        ),
        "copied_authority_rejects_foreign_thread_early",
        "foreign observation must not block behind its owner's recursive mutex",
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
                "require_sync_sqlite_thread_incarnation_or_throw",
                "authority().authorizes",
            ),
            f"transaction_{method}_rejects_foreign_thread_before_authority",
            f"foreign {method.upper()} must throw before any SQLite authority probe",
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
        mutex_owners == {"src/sync_sqlite_connection_authority.cpp"},
        "direct_sqlite_mutex_calls_have_one_owner",
        "all direct production enter/leave operations must remain in the connection-authority owner",
    )
    require(
        checks,
        any(item["operation"] == "enter" for item in mutex_inventory)
        and any(item["operation"] == "leave" for item in mutex_inventory),
        "mutex_inventory_contains_enter_and_leave",
        "the source audit must observe both sides of the retained mutex protocol",
    )

    clientdata_inventory = line_inventory(root, production_sources, CLIENT_DATA_CALL)
    clientdata_owners = {item["path"] for item in clientdata_inventory}
    require(
        checks,
        clientdata_owners
        == {
            "src/sync_sqlite_connection_authority.cpp",
            "src/sync_sqlite_mutex_capability.cpp",
        },
        "clientdata_calls_have_two_invariant_owners",
        "authorizer generation and retained-mutex lifetime must be the only client-data namespaces",
    )

    checks_data = [asdict(check) for check in checks]
    violations = [check.detail for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-mutex-capability-audit-v1",
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
