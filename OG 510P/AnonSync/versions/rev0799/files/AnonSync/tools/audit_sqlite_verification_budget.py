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


def function_body(text: str, signature: str, next_signature: str) -> str:
    start = text.find(signature)
    end = text.find(next_signature, start + 1) if start >= 0 else -1
    if start < 0 or end < 0:
        return ""
    return text[start:end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    required = [
        Path("CMakeLists.txt"),
        Path("src/persistence/sqlite_verification_budget.hpp"),
        Path("src/persistence/sqlite_verification_budget.cpp"),
        Path("src/persistence/sqlite_snapshot_seal.cpp"),
        Path("src/sqlite_replay_ledger.cpp"),
        Path("tests/persistence/sqlite_verification_budget_tests.cpp"),
        Path("tests/persistence/sqlite_snapshot_geometry_binding_test.cpp"),
    ]
    missing = [str(path) for path in required if not (root / path).is_file()]
    if missing:
        payload = {
            "format": "anonsync-sqlite-verification-budget-audit-v1",
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
    header = texts[Path("src/persistence/sqlite_verification_budget.hpp")]
    owner = texts[Path("src/persistence/sqlite_verification_budget.cpp")]
    seal = texts[Path("src/persistence/sqlite_snapshot_seal.cpp")]
    ledger = texts[Path("src/sqlite_replay_ledger.cpp")]
    focused = texts[Path("tests/persistence/sqlite_verification_budget_tests.cpp")]
    geometry_test = texts[
        Path("tests/persistence/sqlite_snapshot_geometry_binding_test.cpp")
    ]
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
        owner.count("sqlite3_progress_handler(") == 2
        and "&SqliteVerificationBudget::progress_callback" in owner,
        "sole_progress_handler_is_lifetime_owned",
        "installation and detachment must live in one owner",
    )
    require(
        checks,
        "sqlite3_progress_handler(database_, 0, nullptr, nullptr);" in owner,
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
        and "pending report snapshot fence writer commit failed" in ledger,
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
        "maximum_rows = 1U" in ledger
        and "tight row budget" in ledger
        and "SqliteVerificationBudgetException" in ledger,
        "production_verifier_has_tight_budget_reproducer",
        "integration must prove the budget is active and typed",
    )
    require(
        checks,
        "std::to_string(static_cast<long long>(::getpid()))" in seal
        and "process_prefix" in geometry_test,
        "staging_leak_oracle_is_process_scoped",
        "parallel processes must not contaminate one another's staging inventory",
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
        "explicit detach removes progress handler" in focused
        and "destructor removes progress handler" in focused,
        "focused_proof_covers_callback_lifetime",
        "both explicit and RAII detachment are executable",
    )

    payload = {
        "format": "anonsync-sqlite-verification-budget-audit-v1",
        "passed": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "check_count": len(checks),
            "boundary_lines": len((header + owner).splitlines()),
            "focused_test_lines": len(focused.splitlines()),
            "verifier_lines": len(verifier.splitlines()),
            "report_lines": len(report.splitlines()),
            "progress_handler_sites": owner.count("sqlite3_progress_handler("),
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
