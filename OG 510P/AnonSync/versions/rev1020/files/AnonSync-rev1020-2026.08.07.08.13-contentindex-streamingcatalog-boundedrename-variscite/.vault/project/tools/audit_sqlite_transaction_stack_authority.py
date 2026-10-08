#!/usr/bin/env python3
"""Deterministic source-shape audit for SQLite transaction-stack authority.

Runtime tests prove behavior for compiled paths. This audit proves that every
production SAVEPOINT/RELEASE/ROLLBACK TO literal remains concentrated in the
reviewed invariant owner, that the typed savepoint proof stays generation- and
thread-bound, and that compound reset/schema users cannot quietly regress to
ad hoc transaction-stack SQL.
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
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("src/sync_sqlite_connection_authority.hpp"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_connection_authority_internal.hpp"),
    Path("src/sync_checkpoint_owner_fence.cpp"),
    Path("src/sync_checkpoint_owner_schema.cpp"),
    Path("src/sync_peer_ingress_schema.cpp"),
    Path("src/sync_peer_ingress_lifecycle.cpp"),
    Path("src/sync_peer_ingress_payload_store_schema.cpp"),
    Path("tests/sqlite_connection_authority_test.cpp"),
    Path("tests/sqlite_transaction_exception_composition_test.cpp"),
    Path("tests/sqlite_transaction_allocator_fault_test.cpp"),
    Path("tools/audit_sqlite_transaction_allocator_fault.py"),
    Path("tests/sync_checkpoint_owner_fence_sqlite_test.cpp"),
    Path("tests/sync_checkpoint_owner_schema_test.cpp"),
    Path("tests/sqlite_runtime_payload_store_test.cpp"),
    Path("tests/peer_ingress_schema_attestation_test.cpp"),
    Path("tests/sqlite_support_test.cpp"),
)

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
SKIP_PARTS = {".git", "build", "_build", "third_party", "vendor"}
RAW_BOUNDARY_LITERAL = re.compile(
    r'"\s*(?:BEGIN(?:\s+(?:DEFERRED|IMMEDIATE|EXCLUSIVE|TRANSACTION))*|'
    r'COMMIT(?:\s+TRANSACTION)?|END(?:\s+TRANSACTION)?|'
    r'ROLLBACK(?:\s+TRANSACTION)?(?:\s+TO(?:\s+SAVEPOINT)?)?|'
    r'SAVEPOINT|RELEASE(?:\s+SAVEPOINT)?)\b',
    re.IGNORECASE,
)
RAW_SAVEPOINT_LITERAL = re.compile(
    r'"\s*(?:SAVEPOINT|'
    r'ROLLBACK(?:\s+TRANSACTION)?\s+TO(?:\s+SAVEPOINT)?|'
    r'RELEASE(?:\s+SAVEPOINT)?)\b'
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


def locations(text: str, path: Path, pattern: re.Pattern[str]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            out.append(
                {
                    "path": path.as_posix(),
                    "line": number,
                    "text": line.strip()[:300],
                }
            )
    return out


def source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        files.append(rel)
    return files


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
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
            "format": "anonsync-sqlite-transaction-stack-authority-audit-v3",
            "passed": False,
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
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    support_cpp = texts[Path("src/sync_sqlite_support.cpp")]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    authority_internal = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    checkpoint_fence = texts[Path("src/sync_checkpoint_owner_fence.cpp")]
    checkpoint_schema = texts[Path("src/sync_checkpoint_owner_schema.cpp")]
    ingress_schema = texts[Path("src/sync_peer_ingress_schema.cpp")]
    lifecycle_cpp = texts[Path("src/sync_peer_ingress_lifecycle.cpp")]
    payload_schema = texts[Path("src/sync_peer_ingress_payload_store_schema.cpp")]
    authority_test = texts[Path("tests/sqlite_connection_authority_test.cpp")]
    composition_test = texts[
        Path("tests/sqlite_transaction_exception_composition_test.cpp")
    ]
    allocator_test = texts[Path("tests/sqlite_transaction_allocator_fault_test.cpp")]
    allocator_audit = texts[Path("tools/audit_sqlite_transaction_allocator_fault.py")]
    checkpoint_fence_test = texts[Path("tests/sync_checkpoint_owner_fence_sqlite_test.cpp")]
    checkpoint_schema_test = texts[Path("tests/sync_checkpoint_owner_schema_test.cpp")]
    payload_test = texts[Path("tests/sqlite_runtime_payload_store_test.cpp")]
    ingress_schema_test = texts[Path("tests/peer_ingress_schema_attestation_test.cpp")]
    support_test = texts[Path("tests/sqlite_support_test.cpp")]

    checks: list[Check] = []

    require(
        checks,
        "src/sync_sqlite_transaction.cpp" in cmake,
        "transaction_implementation_is_independent_target_source",
        "the typed transaction/savepoint implementation must remain an invariant-owned translation unit",
    )
    require(
        checks,
        "anonsync_sqlite_transaction_stack_authority_source_audit" in cmake
        and "tools/audit_sqlite_transaction_stack_authority.py" in cmake,
        "audit_is_registered_in_ctest",
        "transaction-stack source ownership must be a release-gate obligation",
    )
    require(
        checks,
        "SyncSqliteTransaction::" not in support_cpp
        and "SyncSqliteSavepoint::" not in support_cpp,
        "generic_sqlite_support_has_no_stack_owner_implementation",
        "generic statement/codec helpers must not reacquire transaction-stack ownership",
    )

    for method in (
        "SyncSqliteTransaction::SyncSqliteTransaction",
        "SyncSqliteTransaction::~SyncSqliteTransaction",
        "SyncSqliteTransaction::commit",
        "SyncSqliteTransaction::rollback",
        "SyncSqliteTransactionAuthority::authorizes",
        "SyncSqliteSavepoint::SyncSqliteSavepoint",
        "SyncSqliteSavepoint::~SyncSqliteSavepoint",
        "SyncSqliteSavepoint::release",
        "SyncSqliteSavepoint::rollback",
    ):
        require(
            checks,
            method in transaction_cpp,
            "typed_owner_method_" + re.sub(r"[^a-z0-9]+", "_", method.lower()).strip("_"),
            f"typed owner method must remain in transaction implementation: {method}",
        )

    for needle, check_id in (
        ("class SyncSqliteSavepoint final", "public_typed_savepoint_exists"),
        ("friend class SyncSqliteSavepoint", "savepoint_consumes_private_outer_authority"),
        ("SyncSqliteSavepointBoundaryProof", "savepoint_proof_is_private_boundary_type"),
        ("savepoint_generation", "savepoint_proof_binds_generation"),
        ("savepoint_name", "savepoint_proof_binds_generated_name"),
        ("process_salt", "proof_binds_process_salt"),
        ("connection_incarnation", "proof_binds_connection_incarnation"),
        ("authorizer_generation", "proof_binds_authorizer_generation"),
        ("transaction_generation", "proof_binds_transaction_generation"),
        ("owner_thread_incarnation", "proof_binds_thread_incarnation"),
        ("retained_connection_mutex", "proof_retains_connection_mutex"),
        ("retained_capability_state", "proof_retains_close_fence_capability"),
        ("begin_sync_sqlite_savepoint_boundary_or_throw", "typed_savepoint_begin_internal_api"),
        ("end_sync_sqlite_savepoint_boundary_or_throw", "typed_savepoint_end_internal_api"),
        ("rollback_sync_sqlite_savepoint_boundary_noexcept", "typed_savepoint_destructor_api"),
        ("release_sync_sqlite_savepoint_mutex_noexcept", "typed_savepoint_mutex_release_api"),
        ("sync_sqlite_savepoint_boundary_authorizes_noexcept", "typed_savepoint_authority_query_api"),
    ):
        haystack = support_hpp + "\n" + authority_internal
        require(checks, needle in haystack, check_id, f"required savepoint boundary marker: {needle}")

    for needle, check_id in (
        ("if (action == SQLITE_SAVEPOINT)", "savepoint_action_is_intercepted"),
        ("savepoint_permit_active", "savepoint_permit_has_active_state"),
        ("savepoint_permit_observed", "savepoint_permit_is_single_use"),
        ("savepoint_permit_name", "savepoint_permit_binds_exact_name"),
        ("savepoint_operation_matches", "savepoint_permit_binds_exact_operation"),
        ("active_savepoints", "connection_tracks_typed_savepoint_stack"),
        ("allocate_savepoint_generation_or_throw", "connection_allocates_monotonic_savepoint_generation"),
        ("savepoint must close in reverse construction order", "fenced_savepoints_are_lifo"),
        ("cannot commit while a typed savepoint remains active", "outer_commit_is_fenced"),
        ("Complete every allocation before SQLite accepts the mark", "savepoint_publish_has_preallocation_rule"),
        ("ROLLBACK TO SAVEPOINT ", "typed_rollback_rewinds_exact_mark"),
        ("RELEASE SAVEPOINT ", "typed_close_erases_exact_mark"),
        ("Never issue an unfenced fallback for a fenced mark", "destructor_has_no_ambiguous_fallback"),
        ("cannot replace authority while a boundary permit is armed", "authority_reinstall_rejects_armed_permit"),
        ("cannot replace connection authority inside an active transaction", "authority_reinstall_rejects_live_stack"),
    ):
        require(checks, needle in authority_cpp, check_id, f"required owner marker: {needle}")

    require(
        checks,
        "state->authorizer_owner.attach(" in authority_cpp
        and "state->authorizer_owner.replace(" in authority_cpp
        and "sqlite3_set_authorizer(" not in authority_cpp,
        "owned_bridge_can_install_and_supersede",
        "connection authority must consume the focused authorizer owner for install and deliberate supersession",
    )
    require(
        checks,
        "sqlite3_set_authorizer(" not in transaction_cpp,
        "typed_stack_owner_cannot_replace_authorizer",
        "typed transaction/savepoint code must consume, not own, callback installation",
    )
    require(
        checks,
        "release_sync_sqlite_savepoint_mutex_noexcept(*boundary_proof_)" in transaction_cpp,
        "savepoint_revocation_releases_retained_mutex",
        "every typed savepoint generation must release its exact recursive mutex entry",
    )
    require(
        checks,
        "thread-affine transaction guard" in support_hpp
        and "Scope-bound nested rollback owner" in support_hpp,
        "thread_affinity_and_nested_ownership_are_documented",
        "the public contract must explain thread and stack ownership",
    )

    begin_segment_start = authority_cpp.find("begin_sync_sqlite_savepoint_boundary_or_throw(")
    begin_segment_end = authority_cpp.find("void end_sync_sqlite_savepoint_boundary_or_throw(")
    begin_segment = (
        authority_cpp[begin_segment_start:begin_segment_end]
        if begin_segment_start >= 0 and begin_segment_end > begin_segment_start
        else ""
    )
    require(
        checks,
        ordered(
            begin_segment,
            "proof.savepoint_name = fenced_savepoint_name",
            "const std::string sql = \"SAVEPOINT \"",
            "state->active_savepoints.push_back",
            "execute_permitted_savepoint_sql_or_throw",
        ),
        "fenced_savepoint_allocations_precede_sql_publication",
        "name, SQL, and stack-frame allocations must complete before SQLite accepts SAVEPOINT",
    )

    end_segment_start = authority_cpp.find("void end_sync_sqlite_savepoint_boundary_or_throw(")
    end_segment_end = authority_cpp.find("void end_sync_sqlite_transaction_boundary_or_throw(")
    end_segment = (
        authority_cpp[end_segment_start:end_segment_end]
        if end_segment_start >= 0 and end_segment_end > end_segment_start
        else ""
    )
    require(
        checks,
        ordered(
            end_segment,
            "validate_fenced_savepoint_proof_or_throw(db, proof, label, true)",
            "const FencedSavepointClosePlan close_plan",
            "SavepointPermitOperation::Rollback",
            "SavepointPermitOperation::Release",
            "state.active_savepoints.pop_back()",
        ),
        "fenced_preallocate_then_rollback_release_revoke",
        "close-plan allocation must precede rewind, release, and modeled-frame removal",
    )
    require(
        checks,
        "std::string_view savepoint_permit_name" in authority_cpp
        and "std::string_view name" in authority_cpp
        and "std::string savepoint_permit_name;" not in authority_cpp,
        "savepoint_permit_name_is_nonallocating_borrow",
        "the exact callback permit must borrow the stable generated name rather than copy it",
    )
    require(
        checks,
        "make_fenced_savepoint_close_plan_or_throw" in authority_cpp
        and "close_plan.rollback_sql" in end_segment
        and "close_plan.release_sql" in end_segment,
        "compound_savepoint_close_uses_prebuilt_plan",
        "ROLLBACK TO and RELEASE must consume SQL and labels allocated before the first effect",
    )

    require(
        checks,
        "sync_sqlite_connection_authority_state_present_or_throw" in ingress_schema
        and "recover prior connection authority" in ingress_schema,
        "schema_recovery_reinstalls_bridge_before_typed_begin",
        "alien callback recovery must occur before a typed schema snapshot begins",
    )
    require(
        checks,
        ingress_schema.find("recover prior connection authority")
        < ingress_schema.find("schema attestation read snapshot"),
        "schema_recovery_precedes_snapshot",
        "the restrictive policy must be current before schema BEGIN is compiled",
    )

    selftest_marker = "void run_sync_peer_ingress_lifecycle_selftests("
    marker_index = lifecycle_cpp.find(selftest_marker)
    production_lifecycle = lifecycle_cpp[:marker_index] if marker_index >= 0 else lifecycle_cpp
    production_raw_lifecycle = locations(
        production_lifecycle,
        Path("src/sync_peer_ingress_lifecycle.cpp"),
        RAW_BOUNDARY_LITERAL,
    )
    require(
        checks,
        marker_index >= 0,
        "peer_lifecycle_selftest_boundary_found",
        "production/selftest split marker must remain reviewable",
    )
    require(
        checks,
        not production_raw_lifecycle,
        "peer_ingress_production_has_no_raw_transaction_sql",
        "peer-ingress production lifecycle must use only typed transaction owners",
    )

    for text, path, check_id in (
        (checkpoint_schema, Path("src/sync_checkpoint_owner_schema.cpp"), "checkpoint_schema_has_no_raw_savepoint_sql"),
        (payload_schema, Path("src/sync_peer_ingress_payload_store_schema.cpp"), "payload_schema_has_no_raw_savepoint_sql"),
        (checkpoint_fence, Path("src/sync_checkpoint_owner_fence.cpp"), "checkpoint_reset_has_no_raw_savepoint_sql"),
    ):
        require(
            checks,
            not locations(text, path, RAW_SAVEPOINT_LITERAL),
            check_id,
            f"{path.as_posix()} must consume the typed savepoint owner",
        )

    require(
        checks,
        "SyncSqliteSavepoint migration(" in checkpoint_schema
        and "migration.release();" in checkpoint_schema,
        "checkpoint_schema_uses_typed_migration_savepoint",
        "checkpoint owner schema migration must publish through the typed owner",
    )
    require(
        checks,
        "SyncSqliteSavepoint savepoint(" in payload_schema
        and "savepoint.release();" in payload_schema
        and "class PayloadSchemaSavepoint" not in payload_schema,
        "payload_schema_uses_shared_typed_savepoint",
        "the ad hoc payload savepoint wrapper must not return",
    )
    require(
        checks,
        ordered(
            checkpoint_fence,
            "SyncSqliteSavepoint reset(",
            "DELETE FROM main.sync_session_checkpoints",
            "reset.release();",
            "permit.consumed_ = true;",
        ),
        "checkpoint_reset_compound_transition_is_atomic",
        "DELETE, sticky evidence proof, release, and permit consumption must remain ordered",
    )
    require(
        checks,
        "permit.transaction_authority_" in checkpoint_fence[checkpoint_fence.find("SyncSqliteSavepoint reset("):],
        "checkpoint_reset_savepoint_binds_exact_outer_transaction",
        "the reset savepoint must consume the permit's exact transaction authority",
    )

    for needle, check_id in (
        ("void test_typed_savepoint_stack_and_atomicity", "test_typed_savepoint_suite"),
        ("reverse construction order", "test_out_of_order_close"),
        ("typed savepoint remains active", "test_outer_commit_fence"),
        ("SQLITE_IGNORE acquired savepoint-boundary authority", "test_savepoint_ignore_fails_closed"),
        ("typed savepoint claimed release after callback replacement", "test_callback_replacement_fails_closed"),
        ("unowned outermost savepoint rollback", "test_unfenced_outermost_rollback"),
        ("unowned nested compatibility savepoint", "test_unfenced_nested_compatibility"),
        ("a stale transaction authority minted a later savepoint", "test_stale_outer_authority"),
        ("foreign-thread typed savepoint RELEASE", "test_savepoint_foreign_release_affinity"),
        ("foreign-thread typed savepoint ROLLBACK", "test_savepoint_foreign_rollback_affinity"),
        ("foreign-thread savepoint destruction did not fail-stop", "test_savepoint_foreign_destructor_fail_stop"),
        ("live unfenced savepoint did not fail-stop", "test_savepoint_close_fence"),
    ):
        require(checks, needle in authority_test, check_id, f"required adversarial marker: {needle}")
    for needle, check_id in (
        ("class TransactionStackModel final", "test_independent_stack_model"),
        ("struct OneShotBoundaryCutpoint final", "test_one_shot_boundary_cutpoint"),
        ("test_release_cut_after_rewind_models_partial_effect", "test_post_rewind_release_cut"),
        ("outer COMMIT crossed a rewound but unreleased mark", "test_partial_close_commit_fence"),
        ("test_denied_commit_is_retryable", "test_denied_commit_retry"),
        ("test_denied_rollback_is_retryable", "test_denied_rollback_retry"),
    ):
        require(
            checks,
            needle in composition_test,
            check_id,
            f"required exception-composition marker: {needle}",
        )
    for needle, check_id in (
        ("SQLITE_CONFIG_GETMALLOC", "test_allocator_overlay_reads_base"),
        ("SQLITE_CONFIG_MALLOC", "test_allocator_overlay_installs_before_init"),
        ("constexpr std::array<std::pair<std::string_view, Scenario>, 6>", "test_allocator_six_boundary_inventory"),
        ("failed savepoint release permanently revoked a live mark", "test_allocator_release_retry"),
        ("failed savepoint rollback permanently revoked a live mark", "test_allocator_rollback_retry"),
        ("failed commit revoked a still-live transaction", "test_allocator_commit_retry"),
        ("failed rollback revoked a still-live transaction", "test_allocator_outer_rollback_retry"),
        ("g_allocator.live_blocks != 0", "test_allocator_live_block_accounting"),
        ("verify_self_exec_child_boundary_or_throw();", "test_allocator_rebinds_fresh_image"),
        ("spawn_self_exec_test_process_with_output_capture_or_throw(", "test_allocator_process_owner"),
        ("wait_for_exact_exit_with_output(", "test_allocator_bounded_output_capture"),
    ):
        require(
            checks,
            needle in allocator_test,
            check_id,
            f"required allocator-fault marker: {needle}",
        )
    require(
        checks,
        "::fork(" not in allocator_test
        and "::pipe(" not in allocator_test
        and "::dup2(" not in allocator_test
        and "::execl(" not in allocator_test
        and "::waitpid(" not in allocator_test,
        "allocator_campaign_has_no_raw_postfork_bridge",
        "the allocator process campaign delegates fresh-image and capture ownership entirely to SelfExecTestProcess",
    )
    require(
        checks,
        "SyncSqliteBoundaryAuthorityStatus" in allocator_audit
        and "Indeterminate" in allocator_audit
        and "allocator_fault_campaign_uses_fresh_image_capture" in allocator_audit
        and "capture_owner_is_bounded_concurrent_and_fail_closed" in allocator_audit,
        "allocator_source_audit_tracks_tri_state_owner",
        "the focused audit must bind the runtime campaign to retry/revocation semantics",
    )
    require(
        checks,
        "tests/sqlite_transaction_allocator_fault_test.cpp" in cmake
        and "anonsync_sqlite_transaction_allocator_fault_source_audit" in cmake,
        "allocator_campaign_and_audit_are_ctest_obligations",
        "both compiled behavior and source shape must participate in the release gate",
    )

    require(
        checks,
        "caught late reset failure cannot commit the destructive DELETE prefix" in checkpoint_fence_test,
        "test_caught_late_failure_cannot_publish_delete_prefix",
        "the root-reset regression must keep the catch-and-commit adversary",
    )
    require(
        checks,
        "deliberate raw commit misuse" in support_test,
        "unowned_compatibility_boundary_is_tested",
        "unowned utility connections retain an explicit compatibility test",
    )
    require(
        checks,
        "ensure_checkpoint_owner_schema_or_throw(" in checkpoint_schema_test,
        "checkpoint_schema_refactor_has_runtime_suite",
        "the migrated checkpoint schema path must remain covered",
    )
    require(
        checks,
        "ensure_peer_transport_ingress_payload_store_schema_or_throw(" in payload_test
        and "ensure_peer_transport_ingress_payload_store_schema_or_throw(" in ingress_schema_test,
        "payload_schema_refactor_has_runtime_suites",
        "both direct and ingress schema suites must exercise the migrated payload path",
    )

    raw_boundary_inventory: list[dict[str, object]] = []
    raw_savepoint_inventory: list[dict[str, object]] = []
    for rel in source_files(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        raw_boundary_inventory.extend(locations(text, rel, RAW_BOUNDARY_LITERAL))
        raw_savepoint_inventory.extend(locations(text, rel, RAW_SAVEPOINT_LITERAL))

    non_owner_savepoint_inventory = [
        item
        for item in raw_savepoint_inventory
        if item["path"] != "src/sync_sqlite_connection_authority.cpp"
    ]
    require(
        checks,
        not non_owner_savepoint_inventory,
        "all_production_savepoint_sql_is_owned_by_authority_boundary",
        "raw SAVEPOINT/ROLLBACK TO/RELEASE literals may exist only in the reviewed invariant owner",
    )

    owner_paths = {
        "src/sync_sqlite_transaction.cpp",
        "src/sync_sqlite_connection_authority.cpp",
    }
    legacy_raw_boundary_inventory = [
        item for item in raw_boundary_inventory if item["path"] not in owner_paths
    ]

    violations = [asdict(check) for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-transaction-stack-authority-audit-v3",
        "root": str(root),
        "passed": not violations,
        "check_count": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "production_peer_ingress_raw_boundary_locations": production_raw_lifecycle,
        "raw_savepoint_boundary_inventory": raw_savepoint_inventory,
        "non_owner_raw_savepoint_boundary_inventory": non_owner_savepoint_inventory,
        "raw_transaction_boundary_inventory": raw_boundary_inventory,
        "legacy_raw_transaction_boundary_inventory": legacy_raw_boundary_inventory,
        "legacy_raw_transaction_boundary_count": len(legacy_raw_boundary_inventory),
        "sensitive_file_sha256": {
            path.as_posix(): sha256_file(root / path) for path in SENSITIVE_FILES
        },
        "interpretation": (
            "Raw savepoint-stack SQL is enforced to one invariant owner. Legacy raw BEGIN/COMMIT/ROLLBACK "
            "outside this boundary remain an inventory and are migration candidates, not a safety claim."
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
