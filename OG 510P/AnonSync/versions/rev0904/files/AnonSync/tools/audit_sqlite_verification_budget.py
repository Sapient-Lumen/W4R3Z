#!/usr/bin/env python3
"""Enforce the finite-work SQLite snapshot verification architecture."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    check_id: str
    detail: str
    passed: bool


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id=check_id, detail=detail, passed=bool(condition)))


RAW_STRING_START = re.compile(
    r'(?:u8|u|U|L)?R"(?P<delimiter>[^ ()\\\t\r\n]{0,16})\\\('
)
SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}


def function_body(
    text: str, signature: str, next_signature: str | None = None
) -> str:
    """Return one complete braced definition, ignoring C++ non-code.

    The previous audit sliced until the spelling of the next function. A rename,
    overload insertion, or reordered helper could therefore make an unrelated
    body satisfy an obligation. `next_signature` remains accepted as a guard
    against matching a declaration. The definition brace is selected only
    after the outer parameter list closes, so a default argument such as `{}`
    cannot be mistaken for the function body.
    """

    start = text.find(signature)
    if start < 0:
        return ""
    next_start = text.find(next_signature, start + 1) if next_signature else -1

    parameter_depth = 0
    saw_parameter_list = False
    brace = -1
    index = start
    while index < len(text):
        if next_start >= 0 and index >= next_start:
            return ""
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = len(text) if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            close = text.find("*/", index + 2)
            index = len(text) if close < 0 else close + 2
            continue
        raw = RAW_STRING_START.match(text, index)
        if raw:
            terminator = ")" + raw.group("delimiter") + '"'
            close = text.find(terminator, raw.end())
            index = len(text) if close < 0 else close + len(terminator)
            continue
        character = text[index]
        if character in {'"', "'"}:
            quote = character
            index += 1
            escaped = False
            while index < len(text):
                character = text[index]
                index += 1
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    break
            continue
        if character == "(":
            parameter_depth += 1
            saw_parameter_list = True
        elif character == ")" and parameter_depth > 0:
            parameter_depth -= 1
        elif character == "{" and saw_parameter_list and parameter_depth == 0:
            brace = index
            break
        index += 1
    if brace < 0:
        return ""

    depth = 0
    index = brace
    while index < len(text):
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = len(text) if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            close = text.find("*/", index + 2)
            index = len(text) if close < 0 else close + 2
            continue
        raw = RAW_STRING_START.match(text, index)
        if raw:
            terminator = ")" + raw.group("delimiter") + '"'
            close = text.find(terminator, raw.end())
            index = len(text) if close < 0 else close + len(terminator)
            continue
        character = text[index]
        if character in {'"', "'"}:
            quote = character
            index += 1
            escaped = False
            while index < len(text):
                character = text[index]
                index += 1
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    break
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
        index += 1
    return ""


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def progress_handler_inventory(root: Path) -> dict[str, int]:
    inventory: dict[str, int] = {}
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        count = path.read_text(encoding="utf-8", errors="strict").count(
            "sqlite3_progress_handler("
        )
        if count:
            inventory[path.relative_to(root).as_posix()] = count
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    required = [
        Path("CMakeLists.txt"),
        Path("src/persistence/sqlite_retained_callback_claim.hpp"),
        Path("src/persistence/sqlite_retained_callback_claim.cpp"),
        Path("src/persistence/sqlite_verification_budget.hpp"),
        Path("src/persistence/sqlite_verification_budget.cpp"),
        Path("src/persistence/sqlite_snapshot_seal.cpp"),
        Path("src/sqlite_replay_ledger.cpp"),
        Path("tests/sqlite_replay_ledger_selftests.cpp"),
        Path("tests/persistence/sqlite_verification_budget_tests.cpp"),
        Path("tests/persistence/sqlite_snapshot_geometry_binding_test.cpp"),
        Path("tools/verify_release_package.py"),
    ]
    missing = [str(path) for path in required if not (root / path).is_file()]
    if missing:
        payload = {
            "format": "anonsync-sqlite-verification-budget-audit-v5",
            "passed": False,
            "missing": missing,
        }
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    texts = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in required
    }
    cmake = texts[Path("CMakeLists.txt")]
    claim_header = texts[Path("src/persistence/sqlite_retained_callback_claim.hpp")]
    claim_owner = texts[Path("src/persistence/sqlite_retained_callback_claim.cpp")]
    header = texts[Path("src/persistence/sqlite_verification_budget.hpp")]
    owner = texts[Path("src/persistence/sqlite_verification_budget.cpp")]
    seal = texts[Path("src/persistence/sqlite_snapshot_seal.cpp")]
    ledger = texts[Path("src/sqlite_replay_ledger.cpp")]
    ledger_selftests = texts[Path("tests/sqlite_replay_ledger_selftests.cpp")]
    focused = texts[Path("tests/persistence/sqlite_verification_budget_tests.cpp")]
    geometry_test = texts[
        Path("tests/persistence/sqlite_snapshot_geometry_binding_test.cpp")
    ]
    release_verifier = texts[Path("tools/verify_release_package.py")]
    verifier = function_body(
        ledger,
        "ReplayLedgerStats verify_profiled_open_sqlite_ledger_snapshot_readonly(",
        "ReplayLedgerStats verify_open_sqlite_ledger_snapshot_readonly(",
    )
    wrapper = function_body(
        ledger,
        "ReplayLedgerStats verify_open_sqlite_ledger_snapshot_readonly(",
        "ReplayLedgerStats verify_sealed_sqlite_ledger_snapshot_readonly(",
    )
    sealed = function_body(
        ledger,
        "ReplayLedgerStats verify_sealed_sqlite_ledger_snapshot_readonly(",
        "ReplayLedgerStats verify_sqlite_ledger_snapshot_readonly(",
    )
    report = function_body(
        ledger,
        "std::string sqlite_effect_pending_report_json_impl(",
        "std::string sqlite_effect_pending_report_json(",
    )
    budget_constructor = function_body(
        owner, "SqliteVerificationBudget::SqliteVerificationBudget("
    )
    budget_destructor = function_body(
        owner, "SqliteVerificationBudget::~SqliteVerificationBudget()"
    )
    budget_detach = function_body(owner, "void SqliteVerificationBudget::detach()")
    budget_progress = function_body(owner, "int SqliteVerificationBudget::on_progress()")
    execution_noexcept = function_body(
        owner, "void SqliteVerificationBudget::require_current_execution_noexcept()"
    )
    execution_throwing = function_body(
        owner, "void SqliteVerificationBudget::require_current_execution_or_throw()"
    )
    progress_sites = progress_handler_inventory(root)

    checks: list[Check] = []
    require(
        checks,
        "add_library(anonsync_sqlite_verification_budget STATIC" in cmake
        and "${ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE}" in cmake,
        "budget_is_independent_library",
        "finite-work authority must remain a separately linkable production owner",
    )
    core_match = re.search(
        r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S
    )
    require(
        checks,
        core_match is not None
        and "sqlite_verification_budget.cpp" not in core_match.group("body"),
        "budget_source_is_not_reabsorbed_by_core",
        "the resource owner must not become a private helper in the core monolith",
    )
    require(
        checks,
        "target_link_libraries(anonsync_sqlite_verification_budget PUBLIC" in cmake
        and "anonsync_thread_incarnation" in cmake,
        "budget_links_exact_thread_authority",
        "the callback owner must consume the generic process-reseeded exact-thread capability",
    )
    require(
        checks,
        "anonsync_sqlite_verification_budget" in cmake
        and "target_link_libraries(anonsync_core_lib" in cmake,
        "core_consumes_budget_library",
        "production verification must link the invariant owner",
    )
    require(
        checks,
        "target_link_libraries(anonsync_sqlite_verification_budget_test PRIVATE"
        in cmake
        and "anonsync_sqlite_verification_budget)" in cmake,
        "focused_test_links_only_owner",
        "the focused executable must consume the small resource boundary",
    )
    require(
        checks,
        "anonsync_sqlite_verification_budget_test" in cmake
        and "focused persistence boundary must not depend on anonsync_core_lib" in cmake,
        "focused_dependency_fence_exists",
        "CMake must enforce the no-core focused-test dependency boundary",
    )
    require(
        checks,
        "anonsync_sqlite_verification_budget_source_audit" in cmake,
        "source_audit_is_registered",
        "the architecture must be a CTest gate, not prose",
    )
    require(
        checks,
        "add_library(anonsync_sqlite_retained_callback_claim STATIC" in cmake
        and "anonsync_sqlite_retained_callback_claim" in cmake.split(
            "target_link_libraries(anonsync_sqlite_verification_budget PUBLIC", 1
        )[1].split("target_compile_options", 1)[0],
        "shared_callback_claim_is_independent_and_composed",
        "verification lifetime proof must reuse the separately linked SQLite client-data sentinel",
    )
    require(
        checks,
        "revision_number >= 849" in release_verifier
        and all(
            marker in release_verifier
            for marker in (
                '"src/persistence/sqlite_retained_callback_claim.hpp"',
                '"src/persistence/sqlite_retained_callback_claim.cpp"',
                '"tests/persistence/sqlite_verification_budget_tests.cpp"',
                '"tests/persistence/sqlite_snapshot_seal_tests.cpp"',
                '"tests/persistence/sqlite_persistence_process_authority_fork_test.cpp"',
                '"tools/audit_sqlite_snapshot_seal.py"',
                '"tools/audit_sqlite_verification_budget.py"',
                '"revision_scoped_required_files_present"',
            )
        ),
        "release_verifier_requires_shared_claim_from_rev0849",
        "a self-consistent package cannot omit the extracted callback lifetime boundary while older sealed parents remain verifiable",
    )
    require(
        checks,
        all(
            marker in claim_header
            for marker in (
                "class SqliteRetainedCallbackClaim final",
                "SqliteRetainedCallbackClaim(const SqliteRetainedCallbackClaim&) = delete",
                "SqliteRetainedCallbackClaim(SqliteRetainedCallbackClaim&&) = delete",
                "SyncProcessIncarnation process_id_;",
            )
        ),
        "shared_callback_claim_has_stable_process_bound_identity",
        "SQLite must retain a nontransferable sentinel whose authority dies across fork",
    )
    require(
        checks,
        claim_header.count(
            "const SyncSqliteDatabaseMutexGuard& mutex_guard") == 3
        and claim_owner.count("mutex_guard.authorizes(database)") == 2
        and "requires the exact serialized database-mutex guard" in claim_owner,
        "shared_claim_requires_exact_database_mutex_witness",
        "client-data attachment, liveness proof, and detach cannot compile or proceed without the exact serialized guard",
    )
    require(
        checks,
        ordered(
            claim_owner,
            "std::string frozen_client_data_name(client_data_name)",
            "std::make_unique<ClaimState>(process_id_)",
            "client_data_name_.swap(frozen_client_data_name)",
            "sqlite3_set_clientdata(",
        )
        and "client_data_name.find('\\0')" in claim_owner,
        "shared_claim_freezes_allocations_before_publication",
        "allocation failure and NUL aliases cannot leave a half-attached or ambiguous named claim",
    )
    require(
        checks,
        all(
            marker in claim_owner
            for marker in (
                "registration_pending = 0",
                "live = 1",
                "detaching = 2",
                "std::atomic<State>::is_always_lock_free",
                "ClaimState* const self = this",
                "const SyncProcessIncarnation process_id",
            )
        ),
        "shared_claim_state_is_explicit_lock_free_and_self_authenticating",
        "fork-safe state, process generation, and exact allocation identity guard the retained sentinel",
    )
    require(
        checks,
        "thread_local void* g_authorized_retained_claim_destruction" in claim_owner
        and "ScopedAuthorizedRetainedClaimDestruction authorized(claim)" in claim_owner
        and "g_authorized_retained_claim_destruction != claim" in claim_owner,
        "shared_claim_destruction_requires_exact_thread_witness",
        "pending or detaching state alone is never ambient authority for close or replacement",
    )
    require(
        checks,
        ordered(
            claim_owner,
            "void SqliteRetainedCallbackClaim::detach(",
            "const SyncSqliteDatabaseMutexGuard& mutex_guard",
            "require_live(database, mutex_guard)",
            "ClaimState::State::detaching",
            "sqlite3_set_clientdata(",
            "claim_state_ = nullptr",
            "client_data_name_.clear()",
        )
        and "Auto-detach would touch an address" in claim_owner,
        "shared_claim_has_explicit_ordered_detach_only",
        "the enclosing callback owner must revoke its callback before synchronously clearing the sentinel",
    )
    require(
        checks,
        all(
            marker in focused
            for marker in (
                "live verification claim rejects immediate raw close_v2 destruction",
                "live verification claim rejects deferred close_v2 zombie destruction",
                "live verification claim rejects named-slot replacement",
                "typed database owner rejects close while verification borrow is live",
            )
        ),
        "focused_proof_covers_close_replacement_and_zombie_frontier",
        "immediate destruction, deferred close_v2 destruction, replacement, and typed-close denial are executable",
    )
    require(
        checks,
        "test_concurrent_duplicate_budgets_reject_without_fail_stop" in focused
        and "kIterations = 64" in focused
        and "one live owner and one recoverable rejection" in focused
        and "shared claim rejects a guard for another database" in focused,
        "focused_proof_covers_serialized_claim_race_and_exact_guard",
        "the runtime corpus proves one-winner duplicate attachment and rejects a mutex witness for another database",
    )
    require(
        checks,
        cmake.count("anonsync_sqlite_verification_budget") >= 10,
        "sanitizer_and_validation_lists_include_owner",
        "normal and sanitizer lanes must retain the owner and proof",
    )

    for marker, check_id, detail in (
        ("kMaximumSqliteVerificationProgressCallbacks", "hard_callback_ceiling", "VM callback count has a reviewed hard ceiling"),
        ("kMaximumSqliteVerificationProgressOpcodeInterval", "hard_opcode_interval", "callback responsiveness has a reviewed ceiling"),
        ("kMaximumSqliteVerificationRows", "hard_row_ceiling", "decoded row cardinality has a reviewed hard ceiling"),
        ("kMaximumSqliteVerificationDecodedTextBytes", "hard_decoded_text_ceiling", "cumulative decoded text has a reviewed hard ceiling"),
        ("kMaximumSqliteVerificationRetainedTextBytes", "hard_retained_text_ceiling", "container-retained text has a reviewed hard ceiling"),
        ("kMaximumSqliteVerificationElapsedMilliseconds", "hard_elapsed_ceiling", "wall-clock authority has a reviewed hard ceiling"),
    ):
        require(checks, marker in header, check_id, detail)
    require(
        checks,
        "policy has a zero ceiling" in owner,
        "zero_policy_is_rejected",
        "zero must not ambiguously mean unlimited",
    )
    require(
        checks,
        "may tighten but not widen reviewed ceilings" in owner,
        "caller_cannot_widen_authority",
        "caller input may revoke but never mint resource authority",
    )
    require(
        checks,
        "requires nonzero verified geometry" in owner,
        "geometry_derivation_rejects_zero_evidence",
        "resource authority requires promoted byte/page evidence",
    )
    require(
        checks,
        "saturating_multiply" in owner
        and "std::numeric_limits<std::uint64_t>::max() / right" in owner,
        "geometry_budget_arithmetic_is_overflow_safe",
        "hostile geometry cannot wrap a derived ceiling",
    )
    require(
        checks,
        "saturating_multiply(page_count, 64U)" in owner
        and "saturating_multiply(page_count, 32U)" in owner,
        "page_geometry_tightens_work_and_rows",
        "page count constrains VM callbacks and decoded rows",
    )
    require(
        checks,
        "saturating_multiply(exact_file_bytes, 4U)" in owner
        and "policy.maximum_retained_text_bytes" in owner,
        "byte_geometry_tightens_text_authority",
        "exact bytes constrain decoded and retained text",
    )
    require(
        checks,
        "SqliteVerificationBudget(const SqliteVerificationBudget&) = delete" in header
        and "operator=(const SqliteVerificationBudget&) = delete" in header,
        "callback_owner_is_noncopyable",
        "SQLite must not retain an address that can be copied away",
    )
    require(
        checks,
        "SqliteVerificationBudget(SqliteVerificationBudget&&) = delete" in header
        and "operator=(SqliteVerificationBudget&&) = delete" in header,
        "callback_owner_is_nonmovable",
        "SQLite callback context must retain stable object identity",
    )
    require(
        checks,
        '#include "sync_thread_incarnation.hpp"' in header
        and ordered(
            header,
            "SyncProcessIncarnation process_id_;",
            "SyncThreadIncarnation thread_id_;",
            "SyncSqliteSerializedDbBorrow database_borrow_;",
            "SqliteRetainedCallbackClaim callback_claim_;",
        ),
        "callback_owner_binds_process_then_exact_thread",
        "immutable execution authority must precede the SQLite handle and every mutable counter",
    )
    require(
        checks,
        ordered(
            budget_constructor,
            "process_id_(current_sync_process_incarnation_noexcept())",
            "thread_id_(current_sync_thread_incarnation_noexcept())",
            "database_borrow_(std::move(database_borrow))",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.attach(database",
            "mutation_guard",
            "sqlite3_progress_handler(",
        ),
        "callback_context_is_frozen_before_installation",
        "SQLite must never retain this address before both process and exact-thread authority exist",
    )
    require(
        checks,
        ordered(
            execution_noexcept,
            "sync_process_incarnation_is_current",
            "fail_stop_on_sync_process_capability_violation_noexcept",
            "sync_thread_incarnation_is_current",
            "fail_stop_on_sync_thread_capability_violation_noexcept",
        )
        and "process_id_.valid()" not in execution_noexcept
        and "thread_id_.valid()" not in execution_noexcept
        and ordered(
            execution_throwing,
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and "label_" not in execution_throwing,
        "execution_checks_are_process_first_and_thread_second",
        "empty or inherited process authority fails closed; diagnostics remain unread until exact-thread authority exists",
    )
    require(
        checks,
        owner.count("require_current_execution_or_throw();") == 7
        and owner.count("require_current_execution_noexcept();") == 8,
        "entire_public_and_callback_surface_is_affinity_fenced",
        "all throwing calls reject before state while accessors, callback, detach, and destruction use the fail-stop path",
    )
    require(
        checks,
        ordered(budget_progress, "require_current_execution_noexcept();", "failure_ != SqliteVerificationBudgetFailure::none", "progress_callbacks_")
        and ordered(
            budget_detach,
            "require_current_execution_noexcept();",
            "database_borrow_.get()",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.require_live(database, mutation_guard)",
            "sqlite3_progress_handler(",
        )
        and "detach();" in budget_destructor,
        "callback_detach_and_destruction_check_before_state",
        "serialized SQLite use cannot authorize a foreign thread to read counters or replace the retained callback",
    )
    require(
        checks,
        progress_sites == {"src/persistence/sqlite_verification_budget.cpp": 2},
        "all_production_progress_handlers_are_inventory_owned",
        f"observed={progress_sites}",
    )
    require(
        checks,
        owner.count("sqlite3_progress_handler(") == 2
        and "&SqliteVerificationBudget::progress_callback" in owner,
        "sole_progress_handler_is_lifetime_owned",
        "installation and detachment must live in one owner",
    )
    require(
        checks,
        ordered(
            budget_detach,
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.require_live(database, mutation_guard)",
            "sqlite3_progress_handler(database, 0, nullptr, nullptr);",
            "callback_claim_.detach(database, mutation_guard)",
            "database_borrow_.reset()",
        ),
        "progress_handler_is_detached_before_close",
        "the callback must not outlive its C++ owner",
    )
    require(
        checks,
        "if (failure_ != SqliteVerificationBudgetFailure::none) return;" in owner,
        "first_failure_is_sticky",
        "later observations cannot overwrite the original denial reason",
    )
    require(
        checks,
        "return 1;" in owner and "SQLITE_INTERRUPT" in focused,
        "callback_denial_interrupts_sqlite",
        "exhausted VM authority must stop SQLite execution",
    )
    require(
        checks,
        "sqlite_verification_budget[" in owner
        and "failure_observed_" in owner
        and "failure_limit_" in owner,
        "diagnostics_are_typed_and_value_free",
        "resource diagnostics expose dimensions and counters, not hostile field bytes",
    )
    require(
        checks,
        '#include "sqlite_verification_budget.hpp"' in ledger,
        "ledger_uses_single_budget_owner",
        "the hostile snapshot path must delegate to the invariant owner",
    )
    require(
        checks,
        "sqlite_verification_budget_for_snapshot" in sealed
        and "snapshot.byte_count()" in sealed
        and "snapshot.page_count()" in sealed,
        "sealed_geometry_derives_verification_authority",
        "the exact seal must tighten default resource authority",
    )
    require(
        checks,
        wrapper.find("SqliteVerificationBudget budget")
        < wrapper.find("apply_untrusted_snapshot_readonly_profile"),
        "budget_precedes_untrusted_sql",
        "finite VM authority must exist before profile PRAGMAs and schema parsing",
    )
    require(
        checks,
        "verify_readonly_snapshot_schema(db, label, budget);" in verifier
        and "consume_retained_text" in function_body(
            ledger,
            "void verify_sqlite_replay_ledger_schema_or_throw(",
            "void verify_readonly_snapshot_schema(",
        ),
        "schema_scan_is_budgeted",
        "schema rows and retained SQL text must consume shared authority",
    )
    require(
        checks,
        verifier.count("sqlite3_step(stmt.stmt)") >= 4
        and "integrity_check returned more than one verdict" in verifier,
        "integrity_verdict_is_exact_and_budgeted",
        "one exact ok row followed by DONE is required",
    )
    require(
        checks,
        "verify_foreign_key_integrity(db, label, &budget);" in verifier,
        "foreign_key_scan_shares_budget",
        "referential integrity traversal must consume the same VM authority",
    )
    require(
        checks,
        verifier.count("budget.consume_text_row") >= 5,
        "all_major_row_families_account_decoded_text",
        "profile, entries, transitions, metadata, and outbox rows are counted",
    )
    require(
        checks,
        verifier.count("budget.consume_retained_text") >= 3,
        "container_retention_is_accounted",
        "long-lived map state must spend retained-text authority",
    )
    require(
        checks,
        verifier.count("std::map<std::string, SnapshotPreparedEffectState>") == 1
        and "std::unordered_set" not in verifier
        and "std::unordered_map" not in verifier,
        "cross_table_state_is_fused_deterministically",
        "one ordered map replaces several attacker-sized hash containers",
    )
    require(
        checks,
        "prepared.sender_replay_seen" in ledger
        and "verify_ingress_sender_replay_rows(" in verifier
        and "&budget" in verifier,
        "sender_replay_scan_shares_fused_state_and_budget",
        "replay evidence must not allocate independent alias sets",
    )
    require(
        checks,
        "BEGIN DEFERRED;" in report and "COMMIT;" in report,
        "report_verification_and_projection_share_read_transaction",
        "verified heads/counts and projected rows must come from one snapshot",
    )
    require(
        checks,
        "verify_profiled_open_sqlite_ledger_snapshot_readonly" in report
        and "SqliteVerificationBudget budget" in report,
        "report_reuses_one_resource_budget",
        "verification and report projection must share finite authority",
    )
    require(
        checks,
        "after_verification" in report
        and "pending report snapshot fence writer commit failed" in ledger_selftests,
        "concurrent_writer_snapshot_fence_is_executable",
        "a permanent hook proof must commit between verification and projection",
    )
    require(
        checks,
        report.count("budget.consume_text_row") >= 1
        and report.count("budget.consume_retained_text") >= 3,
        "report_projection_accounts_rows_and_retention",
        "report vectors cannot bypass verifier resource accounting",
    )
    require(
        checks,
        "verify_sqlite_ledger_snapshot_readonly_with_row_limit_for_selftest(" in ledger_selftests
        and "tight row budget" in ledger_selftests
        and "SqliteVerificationBudgetException" in ledger_selftests
        and "e.limit() == 1U" in ledger_selftests,
        "production_verifier_has_tight_budget_reproducer",
        "integration must prove the budget is active and typed",
    )
    require(
        checks,
        "process_prefix" in geometry_test
        and "std::to_string(static_cast<long long>(::getpid()))" in geometry_test
        and "staging_directory_" not in seal
        and "mkdtemp" not in seal,
        "legacy_namespace_regression_oracle_is_process_scoped",
        "the no-staging regression oracle must ignore parallel processes while production owns no staging namespace",
    )
    require(
        checks,
        "maximum_progress_callbacks = 1U" in focused
        and "progress_opcode_interval = 1U" in focused
        and "SQLITE_INTERRUPT" in focused,
        "focused_proof_interrupts_exact_progress_edge",
        "the callback ceiling has an executable off-by-one proof",
    )
    require(
        checks,
        all(
            marker in focused
            for marker in (
                "row_limit",
                "decoded_text_byte_limit",
                "retained_text_byte_limit",
                "elapsed_time_limit",
            )
        ),
        "focused_proof_covers_every_manual_dimension",
        "row, decoded, retained, and elapsed denials all have typed proofs",
    )
    require(
        checks,
        all(
            marker in focused
            for marker in (
                "test_exact_thread_authority",
                "foreign throwing rejection preserves mutable counters",
                "foreign rejection does not disclose owner diagnostics",
                "originating thread retains authority after rejection",
                "foreign SQLite callback fails stopped before budget state",
                "foreign detach fails stopped before callback replacement",
                "foreign destructor fails stopped before callback replacement",
                "wait_for_exact_exit(kSyncProcessCapabilityViolationExitCode",
            )
        )
        and focused.count("spawn_inherited_test_process_or_throw(") == 2,
        "focused_proof_covers_exact_thread_authority",
        "throwing rejection is non-consuming and every noexcept callback-lifetime surface takes the exact direct-exit path",
    )
    require(
        checks,
        "explicit detach removes progress handler" in focused
        and "destructor removes progress handler" in focused,
        "focused_proof_covers_callback_lifetime",
        "both explicit and RAII detachment are executable",
    )

    payload = {
        "format": "anonsync-sqlite-verification-budget-audit-v5",
        "passed": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "check_count": len(checks),
            "boundary_lines": len((claim_header + claim_owner + header + owner).splitlines()),
            "shared_claim_lines": len((claim_header + claim_owner).splitlines()),
            "focused_test_lines": len(focused.splitlines()),
            "verifier_lines": len(verifier.splitlines()),
            "report_lines": len(report.splitlines()),
            "progress_handler_sites": sum(progress_sites.values()),
            "progress_handler_translation_units": len(progress_sites),
            "thread_authority_fields": header.count("SyncThreadIncarnation thread_id_"),
            "prepared_effect_state_maps": verifier.count(
                "std::map<std::string, SnapshotPreparedEffectState>"
            ),
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
