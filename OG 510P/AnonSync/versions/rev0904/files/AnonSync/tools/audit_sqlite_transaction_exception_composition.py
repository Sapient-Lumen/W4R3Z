#!/usr/bin/env python3
"""Audit the typed SQLite boundary exception-composition contract.

The runtime model deliberately cuts policy authorization at each transaction-
stack boundary. This source audit complements it by proving that C++ allocation
work for the compound ROLLBACK TO + RELEASE path is completed before the first
SQLite effect and that the model remains a CTest/sanitizer obligation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SENSITIVE_FILES = (
    Path("CMakeLists.txt"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_connection_authority_internal.hpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("tests/sqlite_transaction_exception_composition_test.cpp"),
    Path("tools/audit_sqlite_transaction_stack_authority.py"),
    Path("tools/verify_release_package.py"),
)


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
    checks.append(Check(check_id, condition, detail))


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def segment(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    end_index = text.find(end, start_index + len(start)) if start_index >= 0 else -1
    if start_index < 0 or end_index < 0:
        return ""
    return text[start_index:end_index]


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
            "format": "anonsync-sqlite-transaction-exception-composition-audit-v1",
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
    runtime_test = texts[Path("tests/sqlite_transaction_exception_composition_test.cpp")]
    stack_audit = texts[Path("tools/audit_sqlite_transaction_stack_authority.py")]
    package_verifier = texts[Path("tools/verify_release_package.py")]

    checks: list[Check] = []

    for needle, check_id in (
        ("add_executable(anonsync_sqlite_transaction_exception_composition_test", "model_target_exists"),
        ("tests/sqlite_transaction_exception_composition_test.cpp", "model_source_is_compiled"),
        ("target_link_libraries(\n  anonsync_sqlite_transaction_exception_composition_test PRIVATE\n  anonsync_sqlite_support)", "model_links_reviewed_owner"),
        ("add_test(NAME anonsync_sqlite_transaction_exception_composition_test", "model_is_registered_in_ctest"),
        ("anonsync_sqlite_transaction_exception_composition_source_audit", "composition_audit_is_registered_in_ctest"),
    ):
        require(checks, needle in cmake, check_id, f"required CMake marker: {needle}")

    require(
        checks,
        cmake.count("anonsync_sqlite_transaction_exception_composition_test") >= 7,
        "model_participates_in_build_and_sanitizer_lists",
        "the model target must be defined, linked, tested, and included in sanitizer compile/link lists",
    )

    for needle, check_id in (
        ("std::string_view savepoint_permit_name", "permit_name_is_borrowed_view"),
        ("SavepointPermitScope(ConnectionAuthorityState& state,", "typed_permit_scope_exists"),
        ("std::string_view name", "permit_scope_accepts_nonallocating_name"),
        ("state_.savepoint_permit_name = name;", "permit_scope_borrows_stable_name"),
        ("state_.savepoint_permit_name = {};", "permit_scope_revokes_borrow"),
        ("struct FencedSavepointClosePlan final", "close_plan_has_owned_preallocation"),
        ("make_fenced_savepoint_close_plan_or_throw", "close_plan_builder_exists"),
        ("std::string rollback_sql;", "close_plan_prebuilds_rollback_sql"),
        ("std::string release_sql;", "close_plan_prebuilds_release_sql"),
        ("std::string rollback_label;", "close_plan_prebuilds_rollback_label"),
        ("std::string release_label;", "close_plan_prebuilds_release_label"),
        ("An unrelated std::bad_alloc between those two effects", "allocation_failure_threat_is_documented"),
    ):
        require(checks, needle in authority, check_id, f"required authority marker: {needle}")

    require(
        checks,
        "std::string savepoint_permit_name;" not in authority,
        "connection_state_has_no_allocating_permit_name",
        "the live callback permit must not own a copied savepoint name",
    )

    close_segment = segment(
        authority,
        "void end_sync_sqlite_savepoint_boundary_or_throw(",
        "void end_sync_sqlite_transaction_boundary_or_throw(",
    )
    fenced_segment = close_segment[close_segment.find("ConnectionAuthorityState& state =") :]
    require(
        checks,
        ordered(
            fenced_segment,
            "run_authorizer_ownership_probe_or_throw",
            "const FencedSavepointClosePlan close_plan",
            "SavepointPermitOperation::Rollback",
            "SavepointPermitOperation::Release",
            "state.active_savepoints.pop_back()",
        ),
        "compound_close_preallocates_before_first_effect",
        "all close-plan allocations must precede ROLLBACK TO, RELEASE, and modeled-frame revocation",
    )
    require(
        checks,
        '"ROLLBACK TO SAVEPOINT " + proof.savepoint_name' not in fenced_segment
        and '"RELEASE SAVEPOINT " + proof.savepoint_name' not in fenced_segment,
        "fenced_close_has_no_inline_sql_allocation",
        "the fenced close path must consume only prebuilt SQL strings",
    )
    require(
        checks,
        "label + \" rollback to savepoint\"" not in fenced_segment
        and "label + \" release savepoint\"" not in fenced_segment,
        "fenced_close_has_no_inline_label_allocation",
        "the fenced close path must consume only prebuilt diagnostic labels",
    )
    require(
        checks,
        authority.count("make_fenced_savepoint_close_plan_or_throw(") == 2,
        "close_plan_has_one_definition_and_one_use",
        "the preallocation boundary should remain singular and reviewable",
    )

    for needle, check_id in (
        ("class TransactionStackModel final", "independent_transaction_stack_model_exists"),
        ("void rollback_to_keep_mark()", "model_splits_rewind_from_release"),
        ("void rollback_to_and_release()", "model_composes_retry_completion"),
        ("struct OneShotBoundaryCutpoint final", "one_shot_policy_cutpoint_exists"),
        ("int one_shot_cutpoint_policy", "cutpoint_runs_at_authorizer_boundary"),
        ("test_denied_savepoint_begin_is_retryable", "model_cuts_savepoint_begin"),
        ("test_denied_release_preserves_exact_mark", "model_cuts_release"),
        ("test_denied_rollback_to_preserves_unrewound_state", "model_cuts_rollback_to"),
        ("test_release_cut_after_rewind_models_partial_effect", "model_cuts_release_after_rewind"),
        ("test_nested_partial_rollback_preserves_lifo", "model_covers_nested_lifo_recovery"),
        ("test_denied_commit_is_retryable", "model_cuts_outer_commit"),
        ("test_denied_rollback_is_retryable", "model_cuts_outer_rollback"),
        ("Critical composition cut: ROLLBACK TO succeeds, then RELEASE is denied.", "critical_partial_effect_is_explicit"),
        ("outer COMMIT crossed a rewound but unreleased mark", "model_checks_outer_commit_fence"),
        ("require_matches_model", "sqlite_state_is_differentially_checked"),
    ):
        require(checks, needle in runtime_test, check_id, f"required model marker: {needle}")

    require(
        checks,
        runtime_test.count("fixture.cutpoint.arm(") == 7,
        "all_seven_boundary_cut_traces_are_armed",
        "the suite must cut begin, release, rollback-to, two post-rewind releases, commit, and rollback",
    )
    require(
        checks,
        "catch (...)" not in runtime_test,
        "model_does_not_mask_unknown_failures",
        "the independent test may catch only std::exception through its assertion helper and main boundary",
    )
    require(
        checks,
        "catch (...)" in transaction,
        "production_guard_rechecks_authority_after_failure",
        "typed commit/rollback owners must retain authority only after a use-time boundary recheck",
    )
    for needle, check_id in (
        ("enum class SyncSqliteBoundaryAuthorityStatus", "tri_state_boundary_status_exists"),
        ("Current", "tri_state_current_exists"),
        ("Invalid", "tri_state_invalid_exists"),
        ("Indeterminate", "tri_state_indeterminate_exists"),
        ("sync_sqlite_savepoint_boundary_authority_status_noexcept", "savepoint_status_query_exists"),
        ("sync_sqlite_transaction_boundary_authority_status_noexcept", "transaction_status_query_exists"),
    ):
        require(
            checks,
            needle in authority_internal,
            check_id,
            f"required tri-state marker: {needle}",
        )
    require(
        checks,
        "if (status == SyncSqliteBoundaryAuthorityStatus::Invalid)" in transaction
        and "return status == SyncSqliteBoundaryAuthorityStatus::Current;" in transaction,
        "authority_query_denies_indeterminate_without_revocation",
        "only observed Invalidity revokes; Indeterminate remains fail-closed and retryable",
    )
    require(
        checks,
        transaction.count("boundary ownership could not be revalidated; retry is required") == 4,
        "all_mutating_preflights_preserve_indeterminate_retry",
        "transaction/savepoint commit, rollback, and release expose the same retry contract",
    )
    require(
        checks,
        "if (!sync_sqlite_transaction_boundary_authorizes_noexcept" not in transaction
        and "if (!sync_sqlite_savepoint_boundary_authorizes_noexcept" not in transaction,
        "catch_paths_do_not_conflate_false_with_revocation",
        "a transient ownership-probe failure must not permanently consume a live guard",
    )

    require(
        checks,
        "tests/sqlite_transaction_exception_composition_test.cpp" in stack_audit,
        "stack_authority_audit_tracks_model_source",
        "the broad transaction-stack source audit must hash the composition model",
    )
    require(
        checks,
        "tests/sqlite_transaction_exception_composition_test.cpp" in package_verifier
        and "tools/audit_sqlite_transaction_exception_composition.py" in package_verifier
        and "src/sync_sqlite_connection_authority.cpp" in package_verifier,
        "release_package_requires_composition_proof_surface",
        "the sealed cube must contain the owner, model, and source audit rather than relying on CMake references alone",
    )

    violations = [asdict(check) for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-transaction-exception-composition-audit-v1",
        "root": str(root),
        "passed": not violations,
        "check_count": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "sensitive_file_sha256": {
            path.as_posix(): sha256_file(root / path) for path in SENSITIVE_FILES
        },
        "interpretation": (
            "The source shape excludes application-level C++ allocation between the successful "
            "ROLLBACK TO effect and the RELEASE attempt. SQLite errors at either boundary remain "
            "runtime outcomes, and the exact typed guard retains retry authority while its mark lives."
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
