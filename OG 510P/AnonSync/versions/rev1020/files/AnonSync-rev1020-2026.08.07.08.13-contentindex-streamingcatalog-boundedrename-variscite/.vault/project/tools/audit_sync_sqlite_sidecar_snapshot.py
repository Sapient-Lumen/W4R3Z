#!/usr/bin/env python3
"""Fail-closed structural audit for single-snapshot sidecar hydration."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_core.hpp"),
    Path("src/persistence/sqlite_busy_handler_owner.hpp"),
    Path("src/persistence/sqlite_busy_handler_owner.cpp"),
    Path("src/persistence/sqlite_verification_budget.hpp"),
    Path("src/persistence/sqlite_verification_budget.cpp"),
    Path("src/sync_peer_ingestion.cpp"),
    Path("src/sync_sqlite_sidecar_claimed_path_snapshot.hpp"),
    Path("src/sync_sqlite_sidecar_claimed_path_snapshot.cpp"),
    Path("src/sync_domain_selftests.cpp"),
    Path("tests/sync_sqlite_sidecar_claimed_path_snapshot_test.cpp"),
    Path("tools/audit_sync_sqlite_sidecar_snapshot.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def section(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def ordered(text: str, *tokens: str) -> bool:
    position = -1
    for token in tokens:
        position = text.find(token, position + 1)
        if position < 0:
            return False
    return True


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
                return text[start:index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-sidecar-snapshot-audit-v2",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks, {})

    texts = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = texts[Path("CMakeLists.txt")]
    public = texts[Path("include/anonsync_core.hpp")]
    generic_busy_header = texts[Path("src/persistence/sqlite_busy_handler_owner.hpp")]
    generic_busy_owner = texts[Path("src/persistence/sqlite_busy_handler_owner.cpp")]
    generic_budget_header = texts[Path("src/persistence/sqlite_verification_budget.hpp")]
    generic_budget_owner = texts[Path("src/persistence/sqlite_verification_budget.cpp")]
    ingestion = texts[Path("src/sync_peer_ingestion.cpp")]
    header = texts[Path("src/sync_sqlite_sidecar_claimed_path_snapshot.hpp")]
    owner = texts[Path("src/sync_sqlite_sidecar_claimed_path_snapshot.cpp")]
    domain_tests = texts[Path("src/sync_domain_selftests.cpp")]
    focused = texts[Path("tests/sync_sqlite_sidecar_claimed_path_snapshot_test.cpp")]
    verifier = texts[Path("tools/verify_release_package.py")]

    owner_load = function_body(
        owner, "SyncSqliteSidecarClaimedPathSnapshotReader::load_or_throw(")
    budget_authorize = function_body(
        owner,
        "void SyncSqliteSidecarSnapshotExecutionBudget::require_authorizes_or_throw(")
    budget_checkpoint = function_body(
        owner, "void SyncSqliteSidecarSnapshotExecutionBudget::checkpoint()")
    budget_detach = function_body(
        owner, "void SyncSqliteSidecarSnapshotExecutionBudget::detach()")
    budget_policy = function_body(
        owner, "persistence::SqliteVerificationBudgetPolicy execution_policy_or_throw(")
    lock_authorize = function_body(
        owner,
        "void SyncSqliteSidecarLockWaitBudget::require_authorizes_or_throw(")
    lock_throw = function_body(
        owner, "void SyncSqliteSidecarLockWaitBudget::throw_if_exhausted() const")
    lock_detach = function_body(
        owner, "void SyncSqliteSidecarLockWaitBudget::detach() noexcept")
    generic_budget_progress = function_body(
        generic_budget_owner, "int SqliteVerificationBudget::on_progress()")
    options_validation = function_body(
        ingestion, "SyncValidationResult validate_peer_sidecar_recovery_sweep_options(")
    execution_limit_mapper = function_body(
        ingestion, "peer_sidecar_snapshot_execution_limits(")
    lock_wait_limit_mapper = function_body(
        ingestion, "peer_sidecar_lock_wait_limits(")
    session_wrapper = function_body(
        ingestion,
        "peer_sidecar_claimed_workorder_path_snapshot_for_session_or_throw(")
    classify = function_body(
        ingestion,
        "classify_archived_checkpoint_sidecar_hydration_backfill_or_throw(")
    apply_loader = function_body(
        ingestion, "bool load_peer_sidecar_apply_entry_for_path_or_throw(")
    remote_loader = function_body(
        ingestion, "bool load_peer_sidecar_remote_file_entry_for_path_or_throw(")
    checkpoint_loader = function_body(
        ingestion,
        "SyncValidationResult load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(")

    require("class SyncSqliteSidecarClaimedPathSnapshotReader final" in header,
            "owner_is_final", "the exact-generation query owner cannot be subclassed")
    require(header.count("= delete;") >= 4,
            "owner_is_noncopyable_nonmovable", "copy and move are all deleted")
    require(header.count("SyncSqliteStmt") == 1 and
            "SyncSqliteStmt claimed_path_query_;" in header,
            "owner_has_one_statement_capability", "one retained statement owns the frontier query")
    require("database_owner_generation" in header and
            "owner_generation() const noexcept" in header,
            "generation_is_published", "the exact connection incarnation remains observable")
    require("max_paths" in header and "max_total_path_bytes" in header,
            "row_and_byte_limits_are_typed", "frontier cardinality and aggregate bytes are independent")

    require("struct SyncSqliteSidecarSnapshotExecutionLimits final" in header and
            all(token in header for token in (
                "maximum_progress_callbacks", "progress_opcode_interval",
                "maximum_elapsed_milliseconds")),
            "execution_limits_are_typed", "SQLite VM callbacks and monotonic elapsed time are independent dimensions")
    require("class SyncSqliteSidecarSnapshotExecutionBudget final" in header and
            header.count("SyncSqliteSidecarSnapshotExecutionBudget") >= 13,
            "purpose_specific_budget_owner_is_final", "sidecar hydration cannot expose the generic verifier's unrelated row or text mutation surface")
    require(all(token in header for token in (
                "SyncSqliteSerializedDbBorrow database_borrow",
                "persistence::SqliteVerificationBudget budget_",
                "bool attached_ = true",
                "void detach() noexcept")),
            "budget_freezes_generation_and_revocation_state", "one exact generation and one-way attachment state are owned together")
    require(header.count("SyncSqliteSidecarSnapshotExecutionBudget&") >= 2 and
            "execution budget is detached" in owner,
            "reader_requires_live_execution_authority", "bounded rows alone cannot authorize unmetered SQLite work")
    require(all(token in budget_policy for token in (
                "policy.maximum_progress_callbacks = limits.maximum_progress_callbacks",
                "policy.progress_opcode_interval = limits.progress_opcode_interval",
                "policy.maximum_elapsed_milliseconds")) and
            "maximum_rows" not in budget_policy and
            "maximum_decoded_text_bytes" not in budget_policy and
            "maximum_retained_text_bytes" not in budget_policy,
            "execution_policy_maps_only_execution_dimensions", "the narrow adapter cannot rewrite unrelated generic projection ceilings")
    require("borrow_sync_sqlite_serialized_db_or_throw" in owner and
            "budget_(std::move(database_borrow)" in owner,
            "budget_consumes_serialized_generation_borrow", "callback lifetime pins typed close and replacement on one FULLMUTEX generation")
    require(ordered(
                budget_authorize,
                "budget_.progress_callbacks();",
                "if (!attached_)",
                "budget_.checkpoint();",
                "database != database_") and
            "database_owner_generation != database_owner_generation_" in budget_authorize,
            "budget_authorization_is_fenced_and_exact", "process/thread authority and revocation precede pointer-plus-generation comparison")
    require(ordered(
                budget_checkpoint,
                "budget_.progress_callbacks();",
                "if (!attached_)",
                "budget_.checkpoint();") and
            ordered(budget_detach, "budget_.detach();", "attached_ = false;"),
            "detachment_is_one_way_revocation", "the retained identity remains diagnostic only and cannot authorize callback-free work")

    require(all(token in generic_busy_header for token in (
                "authorized_sleep_milliseconds",
                "one cumulative budget for the complete owner",
                "not a fresh allowance for each SQLite locking event")) and
            "event_started_elapsed_milliseconds_" not in generic_busy_header and
            "steady_clock" not in generic_busy_owner and
            ordered(generic_busy_owner,
                    "authorized_sleep_milliseconds_.store(",
                    "sqlite3_sleep(static_cast<int>(requested_sleep))"),
            "generic_busy_authority_is_cumulative", "lock waits consume one exact requested-sleep allowance across the complete owner lifetime")
    require("struct SyncSqliteSidecarLockWaitLimits final" in header and
            "class SyncSqliteSidecarLockWaitBudgetException final" in header and
            "class SyncSqliteSidecarLockWaitBudget final" in header and
            header.count("SyncSqliteSidecarLockWaitBudget") >= 14 and
            "persistence::SqliteBusyHandlerOwner budget_;" in header,
            "lock_wait_is_a_distinct_typed_dimension", "blocked-lock authority is not conflated with cooperative VM execution authority")
    require(all(token in header for token in (
                "SyncSqliteSerializedDbBorrow database_borrow",
                "sqlite3* database_ = nullptr",
                "database_owner_generation_",
                "bool attached_ = true")) and
            "borrow_sync_sqlite_serialized_db_or_throw" in owner and
            "exact lock-wait database generation" in owner and
            ordered(lock_authorize,
                    "budget_.snapshot();",
                    "if (!attached_)",
                    "database != database_",
                    "database_owner_generation != database_owner_generation_"),
            "lock_wait_owner_freezes_exact_generation", "process fencing and one-way revocation precede exact pointer-plus-generation authorization")
    require("sqlite_sidecar_lock_wait_budget[lock_wait_limit]" in owner and
            "observed.timeout_exhausted" in lock_throw and
            "throw SyncSqliteSidecarLockWaitBudgetException" in lock_throw and
            ordered(lock_detach, "budget_.detach();", "attached_ = false;"),
            "lock_wait_exhaustion_is_sticky_and_typed", "native SQLITE_BUSY is translated only when the retained callback recorded exact exhaustion evidence")
    require("max_sqlite_lock_wait_milliseconds = 60000" in public and
            "Zero is valid" in public and
            "fail fast on the first lock conflict" in public and
            "limits.max_sqlite_lock_wait_milliseconds == 0" not in options_validation and
            "kMaximumSqliteBusyHandlerWaitMilliseconds" in options_validation and
            "lock-wait limit cannot widen the reviewed ceiling" in options_validation,
            "public_lock_policy_admits_zero_and_cannot_widen", "callers may fail fast or tighten the generic 60-second ceiling but cannot renew or enlarge it")
    require(".maximum_lock_wait_milliseconds" in lock_wait_limit_mapper and
            "max_sqlite_lock_wait_milliseconds" in lock_wait_limit_mapper and
            "maximum_progress_callbacks" not in lock_wait_limit_mapper and
            "maximum_elapsed_milliseconds" not in lock_wait_limit_mapper,
            "lock_wait_mapper_is_dimension_exact", "public lock policy cannot rewrite progress or elapsed execution dimensions")
    require(ordered(session_wrapper,
                    "SyncSqliteSidecarLockWaitBudget lock_wait_budget",
                    "SyncSqliteTransaction snapshot_transaction",
                    "SyncSqliteSidecarSnapshotExecutionBudget execution_budget",
                    "execution_budget.detach();",
                    "snapshot_transaction.commit();",
                    "lock_wait_budget.snapshot();",
                    "lock_wait_budget.detach();",
                    "lock_wait_budget.throw_if_exhausted();"),
            "session_snapshot_has_complementary_callback_lifetimes", "the progress callback revokes before cleanup while one older busy callback spans begin, statements, commit, and rollback")
    require(ordered(checkpoint_loader,
                    "SyncSqliteSidecarLockWaitBudget lock_wait_budget",
                    "SyncSqliteTransaction snapshot_transaction",
                    "SyncSqliteSidecarSnapshotExecutionBudget execution_budget",
                    "execution_budget.detach();",
                    "snapshot_transaction.commit();",
                    "lock_wait_budget.snapshot();",
                    "lock_wait_budget.detach();",
                    "lock_wait_budget.throw_if_exhausted();"),
            "checkpoint_hydration_has_complementary_callback_lifetimes", "one cumulative busy owner covers the complete multi-query snapshot without surviving publication")
    require(public.count("sqlite_lock_contention_observed") == 2 and
            public.count("sqlite_lock_wait_invocations") == 2 and
            public.count("sqlite_lock_wait_authorized_sleep_milliseconds") == 2 and
            public.count("sqlite_lock_wait_observed_sleep_milliseconds") == 2 and
            all(token in ingestion for token in (
                "pending.sqlite_lock_wait_authorized_sleep_milliseconds",
                "pending.sqlite_lock_wait_observed_sleep_milliseconds",
                "out.sqlite_lock_wait_authorized_sleep_milliseconds",
                "out.sqlite_lock_wait_observed_sleep_milliseconds")),
            "success_publication_exposes_bounded_lock_evidence", "authorized sleep remains distinct from scheduler-sensitive observed sleep in both public result paths")
    require(all(token in focused for token in (
                "SyncSqliteSidecarLockWaitBudgetException",
                "sidecar lock-wait authority cannot widen the generic ceiling",
                "zero lock wait converts SQLITE_BUSY into stable typed evidence",
                "sticky lock-wait evidence survives transaction cleanup",
                "fresh lock, transaction, and execution owners succeed after exhaustion cleanup")) and
            all(token in domain_tests for token in (
                "admits a zero lock-wait policy and succeeds when uncontended",
                "cannot widen the reviewed SQLite lock-wait ceiling",
                "sqlite_lock_wait_authorized_sleep_milliseconds == 0")),
            "focused_and_integrated_lock_wait_proofs_exist", "exact generation, zero-wait contention, cleanup, reuse, public monotonicity, and sticky-output behavior are executable")
    require("anonsync_sqlite_busy_handler_owner\n  anonsync_sqlite_verification_budget" in cmake and
            "revision_number >= 863" in verifier and
            all(path in verifier for path in (
                "src/persistence/sqlite_busy_handler_owner.hpp",
                "src/persistence/sqlite_busy_handler_owner.cpp",
                "tests/persistence/sqlite_busy_handler_owner_tests.cpp",
                "tools/audit_sqlite_busy_handler_owner.py")),
            "build_and_release_gate_bind_the_lock_owner", "the extracted sidecar target links the generic busy owner and rev0863+ packages must retain both proof sets")
    require(all(token in generic_budget_header for token in (
                "kMaximumSqliteVerificationProgressCallbacks",
                "kMaximumSqliteVerificationProgressOpcodeInterval",
                "kMaximumSqliteVerificationElapsedMilliseconds")) and
            generic_budget_owner.count("sqlite3_progress_handler(") == 2,
            "generic_progress_owner_remains_inventory_complete", "one reviewed owner installs and revokes SQLite's singleton progress slot")
    require(ordered(generic_budget_progress,
                    "require_current_execution_noexcept();",
                    "failure_ != SqliteVerificationBudgetFailure::none",
                    "progress_callbacks_") and
            "exhausted()" not in generic_budget_progress,
            "hot_callback_avoids_duplicate_affinity_checks", "the fail-stop fence runs once before the sticky state read on every callback")

    require("FROM main.sync_session_resume_transfer_workorders" in owner,
            "frontier_is_main_qualified", "TEMP-first resolution cannot redirect the durable frontier")
    require(owner.count("COLLATE BINARY") == 6 and
            all(token in owner for token in (
                "session_id COLLATE BINARY=?",
                "worker_id COLLATE BINARY=?",
                "worker_lease_id COLLATE BINARY=?",
                "work_state COLLATE BINARY='claimed'",
                "path COLLATE BINARY")),
            "frontier_identity_is_binary", "schema-declared NOCASE cannot widen lookup authority or collapse path identities")
    require("LIMIT ?;" in owner,
            "frontier_has_sql_sentinel", "the query materializes at most max_paths plus one rows")
    require("limits.max_paths + 1U" in owner_load and
            "limits.max_paths >= sqlite_i64_max" in owner,
            "sentinel_arithmetic_is_guarded", "the +1 SQL sentinel cannot wrap or exceed SQLite integer range")
    require("sync_id_is_valid(session_id)" in owner_load,
            "session_identity_is_prevalidated", "the durable lookup uses a canonical session identifier")
    require(owner_load.count("require_bounded_lookup_key") == 2,
            "worker_keys_are_bounded", "worker and lease lookup keys cannot drive unbounded binds")
    require("transaction_authority.authorizes(database)" in owner_load and
            "transaction_authority.authorizes_snapshot(database)" in owner_load,
            "transaction_then_snapshot_authority", "the exact transaction is required before and after first SELECT")
    require(owner_load.find("transaction_authority.authorizes(database)") <
            owner_load.find("execution_budget.require_authorizes_or_throw") <
            owner_load.find("sqlite3_step(statement)"),
            "execution_authority_precedes_sqlite_work", "the exact live transaction and callback owner are both proven before the first opcode")
    require("execution_budget.throw_if_exhausted();" in owner_load and
            owner_load.find("execution_budget.throw_if_exhausted();") <
            owner_load.find("throw_sqlite_exception("),
            "sqlite_interrupt_recovers_typed_budget_reason", "generic SQLITE_INTERRUPT cannot erase the sticky resource failure")
    require(owner_load.count("execution_budget.checkpoint();") >= 1 and
            owner_load.count("execution_budget.require_authorizes_or_throw(") == 2,
            "reader_checks_deadline_and_generation_through_publication", "every step boundary and final result retain the same live execution owner")
    require("kSyncManifestRelativePathMaxBytes" in owner_load and
            "normalize_sync_relative_path" in owner_load,
            "persisted_paths_are_exact_and_normalized", "storage class, byte ceiling, and portable path semantics are enforced")
    require("snapshot.paths.back().value" in owner_load and
            "previous_path" not in owner_load,
            "ordering_reuses_published_storage", "strict ordering does not retain a second full-path copy")
    require(owner_load.find("snapshot.total_path_bytes >") <
            owner_load.find("snapshot.paths.push_back"),
            "aggregate_bytes_precede_vector_growth", "the byte budget is consumed before each vector append")
    require("reset_and_clear_or_throw" in owner_load and
            "reset_and_clear_noexcept" in owner_load and
            "catch (...)" in owner_load,
            "statement_is_reusable_after_failure", "success and exceptions both clear retained state")

    require(all(token in options_validation for token in (
                "max_claimed_paths", "max_claimed_path_bytes",
                "max_manifest_chunks", "max_manifest_lineage_rows",
                "max_metadata_bytes", "max_sqlite_progress_callbacks",
                "sqlite_progress_opcode_interval",
                "max_sqlite_elapsed_milliseconds")),
            "all_public_limits_are_validated", "zero-valued projection and execution dimensions fail before database access")
    require(all(token in options_validation for token in (
                "kMaximumSqliteVerificationProgressCallbacks",
                "kMaximumSqliteVerificationProgressOpcodeInterval",
                "kMaximumSqliteVerificationElapsedMilliseconds",
                "cannot widen reviewed ceilings")),
            "public_execution_limits_cannot_widen", "callers may tighten but cannot enlarge the reviewed callback or deadline authority")
    require(all(token in execution_limit_mapper for token in (
                ".maximum_progress_callbacks =",
                "limits.max_sqlite_progress_callbacks",
                ".progress_opcode_interval =",
                "limits.sqlite_progress_opcode_interval",
                ".maximum_elapsed_milliseconds =",
                "limits.max_sqlite_elapsed_milliseconds")),
            "public_execution_limits_map_exactly", "all three dimensions reach the purpose-specific owner without ambient defaults")
    require("checkpoint claimed-path limit cannot form a SQLite sentinel" in options_validation,
            "public_row_limit_is_sql_representable", "invalid policy cannot reach the owner")
    require("SyncSqliteTransactionMode::Deferred" in session_wrapper and
            "snapshot_transaction.authorizes_snapshot" in session_wrapper and
            "snapshot_transaction.commit();" in session_wrapper,
            "session_sweep_uses_bounded_snapshot_owner", "the secondary sweep path also loses the legacy autocommit scan")
    require(session_wrapper.find("SyncSqliteTransaction snapshot_transaction(") <
            session_wrapper.find("SyncSqliteSidecarSnapshotExecutionBudget execution_budget(") <
            session_wrapper.find("peer_sidecar_claimed_workorder_path_snapshot_or_throw") and
            session_wrapper.find("execution_budget.detach();") <
            session_wrapper.find("snapshot_transaction.commit();") and
            "execution_budget.throw_if_exhausted();" in session_wrapper,
            "session_budget_detaches_before_transaction_end", "success revokes before commit and failure converts interruption before rollback destruction")
    require("peer_sidecar_claimed_workorder_paths_for_session_or_throw" not in ingestion,
            "legacy_unbounded_helper_is_removed", "no caller can silently reopen the frontier on another connection")

    require(checkpoint_loader.count("sqlite3_open_v2(") == 1,
            "checkpoint_loader_opens_once", "one result is bound to one exact connection generation")
    require("SyncSqliteTransactionMode::Deferred" in checkpoint_loader and
            "const SyncSqliteTransactionAuthority snapshot_authority" in checkpoint_loader,
            "checkpoint_loader_owns_typed_snapshot", "a scope-bound deferred transaction carries the read generation")
    require(checkpoint_loader.find("peer_sidecar_claimed_workorder_path_snapshot_or_throw") <
            checkpoint_loader.find("classify_archived_checkpoint_sidecar_hydration_backfill_or_throw") <
            checkpoint_loader.find("for (const auto& path : claimed_snapshot.paths)"),
            "claimed_frontier_is_first_select", "schema and row hydration cannot precede snapshot establishment")
    require(checkpoint_loader.count(
                "SyncSqliteSidecarSnapshotExecutionBudget execution_budget(") == 1 and
            checkpoint_loader.find("SyncSqliteTransaction snapshot_transaction(") <
            checkpoint_loader.find("SyncSqliteSidecarSnapshotExecutionBudget execution_budget(") <
            checkpoint_loader.find("peer_sidecar_claimed_workorder_path_snapshot_or_throw") and
            checkpoint_loader.find("execution_budget.checkpoint();") >
            checkpoint_loader.find("for (const auto& path : claimed_snapshot.paths)"),
            "one_budget_spans_complete_hydration", "frontier, schema, apply, manifest, chunks, and lineage share one callback owner and deadline")
    require(checkpoint_loader.find("execution_budget.detach();") <
            checkpoint_loader.find("snapshot_transaction.commit();") and
            "execution_budget.throw_if_exhausted();" in checkpoint_loader,
            "checkpoint_budget_detaches_before_transaction_end", "an exhausted callback cannot interrupt commit or failure-path rollback cleanup")
    require(checkpoint_loader.count("snapshot_authority") >= 6,
            "one_authority_threads_all_reads", "classification and per-path loaders share the same typed lease")
    require(checkpoint_loader.find("snapshot_transaction.commit();") >
            checkpoint_loader.find("for (const auto& path : claimed_snapshot.paths)"),
            "commit_follows_complete_hydration", "the snapshot cannot end while evidence is still being interpreted")
    require("pending = out;" in checkpoint_loader and
            checkpoint_loader.find("snapshot_transaction.commit();") <
            checkpoint_loader.find("out = std::move(pending);") and
            checkpoint_loader.count("out = std::move(pending);") == 1 and
            "std::is_nothrow_move_assignable_v" in ingestion and
            "post-commit checkpoint evidence publication must not throw" in ingestion,
            "result_publishes_after_commit", "exceptions discard local evidence and the final post-commit move is statically nonthrowing")
    require("evidence_budget.admit_entry_count(claimed_snapshot.path_count)" in checkpoint_loader,
            "entry_count_is_admitted_once", "the path frontier sets the aggregate nested-value budget")
    require("evidence_budget.usage().metadata_bytes" in checkpoint_loader,
            "metadata_usage_is_published", "the result reports the scalar budget actually consumed")

    require("FROM main.sqlite_schema" in ingestion and
            "FROM main.sync_session_schema_meta" in ingestion,
            "schema_reads_are_main_bound", "TEMP cannot rewrite checkpoint version classification")
    require("type COLLATE BINARY='table'" in ingestion and
            "name COLLATE BINARY=?" in ingestion and
            "key COLLATE BINARY=?" in ingestion,
            "schema_identity_is_binary", "hostile schema collations cannot widen table or metadata-key identity")
    require("LIMIT 2;" in function_body(
                ingestion, "std::string peer_ingestion_schema_meta_value_or_empty_or_throw("),
            "schema_meta_has_duplicate_sentinel", "duplicate version rows fail after at most two values")
    require("PeerSidecarCheckpointTableInventory" in classify and
            classify.count("peer_ingestion_table_exists_or_throw") == 2,
            "table_inventory_is_frozen_once", "chunk and lineage table presence is read once per snapshot")
    require("peer_ingestion_table_exists_or_throw" not in remote_loader and
            "manifest_lineage_table_exists" in remote_loader,
            "lineage_probe_is_not_per_path", "hydrating N paths does not repeat the same schema query N times")
    require("admit_peer_sidecar_metadata_bytes_or_throw" in classify,
            "schema_value_consumes_shared_budget", "version text is included in the aggregate scalar ceiling")

    require("FROM main.sync_session_apply_intents" in apply_loader,
            "apply_query_is_main_qualified", "apply intent evidence cannot resolve through TEMP")
    require("session_id COLLATE BINARY=?" in apply_loader and
            "path COLLATE BINARY=?" in apply_loader,
            "apply_identity_is_binary", "apply lookup authority remains byte-exact under hostile schema collation")
    require("LIMIT 2;" in apply_loader,
            "apply_query_has_duplicate_sentinel", "uniqueness proof consumes at most two rows")
    require(apply_loader.count("peer_ingestion_column_text_or_throw") == 11 and
            all(token in apply_loader for token in (
                "kPeerSidecarActionTextMaxBytes",
                "kPeerSidecarIdempotencyKeyMaxBytes",
                "kPeerSidecarAbsolutePathMaxBytes",
                "kSyncManifestSha256TextBytes")),
            "apply_scalars_are_individually_bounded", "no persisted apply string is materialized without a ceiling")
    require(apply_loader.count("admit_peer_sidecar_metadata_bytes_or_throw") >= 1 and
            "kPeerSidecarApplyFixedMetadataBytes" in apply_loader,
            "apply_scalars_consume_shared_budget", "text and fixed-width fields count against one aggregate")
    require("require_peer_sidecar_snapshot_authority_or_throw" in apply_loader,
            "apply_loader_requires_snapshot", "a raw handle alone is not enough to hydrate apply evidence")

    for durable_name in (
        "main.sync_session_manifest_entries",
        "main.sync_session_manifests",
        "main.sync_session_manifest_chunks",
        "main.sync_session_manifest_lineage",
    ):
        require(durable_name in remote_loader,
                "remote_" + durable_name.split(".")[-1] + "_is_main_qualified",
                f"{durable_name} cannot resolve to TEMP")
    require(all(token in remote_loader for token in (
                "m.session_id COLLATE BINARY=e.session_id COLLATE BINARY",
                "m.role COLLATE BINARY=e.role COLLATE BINARY",
                "e.session_id COLLATE BINARY=?",
                "e.role COLLATE BINARY='source'",
                "e.path COLLATE BINARY=?",
                "session_id COLLATE BINARY=?",
                "role COLLATE BINARY='source'",
                "path COLLATE BINARY=?")),
            "manifest_identity_is_binary", "header joins and nested row lookups cannot inherit permissive schema collations")
    require("LIMIT 2;" in remote_loader,
            "manifest_header_has_duplicate_sentinel", "entry uniqueness consumes at most two rows")
    require("peer_sidecar_sql_row_sentinel_or_throw" in remote_loader and
            "chunk_row_sentinel" in remote_loader and
            "lineage_row_sentinel" in remote_loader,
            "nested_sentinels_are_overflow_checked", "recorded counts cannot wrap SQL LIMIT values")
    require("chunk_index != local_chunks_loaded" in remote_loader and
            "lineage_index != local_lineage_rows_loaded" in remote_loader,
            "nested_ordinals_are_exact", "row count cannot hide gaps or duplicate persisted ordinals")
    require(remote_loader.find("admit_peer_sidecar_entry_shape_or_throw") <
            remote_loader.find("FROM main.sync_session_manifest_chunks"),
            "shape_budget_precedes_nested_query", "attacker-sized declared vectors fail before nested reads")
    require(remote_loader.count("admit_peer_sidecar_metadata_bytes_or_throw") >= 5,
            "nested_rows_consume_shared_metadata", "headers, chunks, and lineage all share one byte ceiling")
    require("require_peer_sidecar_snapshot_authority_or_throw" in remote_loader,
            "remote_loader_requires_snapshot", "manifest reconstruction cannot outlive the read generation")

    require("CheckpointEvidenceLimits" in public and
            all(token in public for token in (
                "max_claimed_paths", "max_manifest_chunks",
                "max_manifest_lineage_rows", "max_metadata_bytes",
                "max_sqlite_progress_callbacks",
                "sqlite_progress_opcode_interval",
                "max_sqlite_elapsed_milliseconds")),
            "public_policy_is_multidimensional", "callers explicitly control projection, SQLite VM work, and elapsed-time amplification")
    require(all(token in public for token in (
                "main_read_snapshot_established", "database_owner_generation",
                "claimed_workorder_path_bytes", "evidence_metadata_bytes")),
            "result_exposes_snapshot_evidence", "observability distinguishes frozen hydration from best-effort reads")

    require("PRAGMA journal_mode=WAL" in focused and
            "original WAL snapshot after writer commit" in focused and
            "later committed generation" in focused,
            "focused_test_proves_snapshot_stability", "a writer commit cannot splice a live hydration snapshot")
    require("CREATE TEMP TABLE sync_session_resume_transfer_workorders" in focused and
            "malicious TEMP shadow" in focused,
            "focused_test_proves_main_namespace", "the executable fixture distinguishes main and TEMP")
    require("path TEXT COLLATE NOCASE" in focused and
            all(token in focused for token in (
                "wrong-session-case", "wrong-worker-case",
                "wrong-lease-case", "wrong-state-case")) and
            "explicit binary collation" in focused,
            "focused_test_proves_binary_identity", "schema collation cannot widen lookup authority or merge case-distinct normalized paths")
    require("row-limit rejection" in focused and
            "aggregate path bytes" in focused,
            "focused_test_proves_row_and_byte_limits", "both frontier amplification dimensions reject and recover")
    require("wrong_storage_class" in focused and
            "stored claimed path is invalid" in focused,
            "focused_test_proves_hostile_storage", "exact SQLite type and path grammar failures are executable")
    require("stale transaction authority" in focused and
            "different database generation" in focused and
            "missing transaction authority" in focused,
            "focused_test_proves_authority_exclusion", "stale, foreign, and absent capabilities all fail closed")
    require("reader remains reusable after hostile storage rejection" in focused,
            "focused_test_proves_failure_reuse", "exception cleanup is exercised after persisted-value rejection")
    require(all(token in focused for token in (
                "SqliteVerificationBudgetFailure::progress_callback_limit",
                "error.observed() == 2", "error.limit() == 1",
                "statement and transaction are reusable after typed interruption")),
            "focused_test_proves_vm_step_interruption", "an expensive DISTINCT/ORDER BY is interrupted with exact typed accounting and reusable SQLite state")
    require(all(token in focused for token in (
                "SqliteVerificationBudgetFailure::elapsed_time_limit",
                "sleep_for(std::chrono::milliseconds(4))",
                "fresh execution authority succeeds after elapsed rejection")),
            "focused_test_proves_elapsed_deadline", "ordinary C++ boundaries detect expiry even before SQLite reaches its callback interval")
    require("execution budget from a different database generation is rejected" in focused and
            "detached execution authority cannot authorize callback-free work" in focused,
            "focused_test_proves_budget_authority_exclusion", "foreign and one-way-revoked callback owners both fail closed")
    require("checkpoint evidence hydration rejects claimed-path bytes" in domain_tests and
            "rejects aggregate manifest cardinality" in domain_tests and
            "aggregate scalar metadata budget" in domain_tests,
            "domain_selftest_proves_integrated_limits", "the public API rejects each aggregate dimension before publication")
    require("main_read_snapshot_established" in domain_tests and
            "database_owner_generation != 0" in domain_tests,
            "domain_selftest_checks_snapshot_evidence", "integrated success asserts exact-generation observability")
    require("caller-visible evidence at its initialized baseline" in domain_tests and
            "!metadata_limited_evidence_result.main_read_snapshot_established" in domain_tests and
            "metadata_limited_evidence_result.apply_entries.empty()" in domain_tests,
            "domain_selftest_proves_sticky_failure_output", "integrated rejection cannot leak a partially hydrated result")
    require("SQLite VM-step exhaustion keeps caller-visible evidence at its initialized baseline" in domain_tests and
            "sqlite_verification_budget[progress_callback_limit]" in domain_tests,
            "domain_selftest_proves_integrated_execution_budget", "the complete hydration path converts SQLITE_INTERRUPT without publishing a prefix")
    require("callers may tighten but cannot widen reviewed SQLite execution ceilings" in domain_tests and
            "max_sqlite_progress_callbacks = 1000001U" in domain_tests,
            "domain_selftest_proves_monotone_public_policy", "untrusted callers cannot enlarge the reviewed generic ceiling")

    require("add_library(anonsync_sync_sqlite_sidecar_claimed_path_snapshot STATIC" in cmake and
            "anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test" in cmake and
            "anonsync_sqlite_verification_budget\n  anonsync_sync_manifest_validation" in cmake,
            "cmake_builds_owner_test_and_budget_dependency", "the narrow owner is separately linked to the reviewed retained-callback implementation")
    require("ANONSYNC_SYNC_SQLITE_SIDECAR_CLAIMED_PATH_SNAPSHOT_SOURCE" in cmake and
            "anonsync_sync_manifest_identity\n    anonsync_sync_sqlite_sidecar_claimed_path_snapshot" in cmake,
            "core_links_extracted_owner", "the monolith consumes the focused capability without breaking prior link-order audit")
    audit_registration = section(
        cmake,
        "add_test(NAME anonsync_sync_sqlite_sidecar_snapshot_source_audit",
        "add_test(NAME anonsync_sync_manifest_identity_source_audit")
    require("${Python3_EXECUTABLE} -B -S" in audit_registration,
            "audit_disables_python_site", "CTest minimizes ambient interpreter startup state")
    python_command_count = cmake.count("COMMAND ${Python3_EXECUTABLE}")
    require(python_command_count >= 50 and
            cmake.count("COMMAND ${Python3_EXECUTABLE} -B -S") ==
                python_command_count and
            "COMMAND ${Python3_EXECUTABLE}\n" not in cmake and
            "COMMAND ${Python3_EXECUTABLE} -S\n" not in cmake,
            "all_python_audits_are_hermetic", "every registered Python audit disables bytecode writes and ambient site initialization")
    require("revision_number >= 861" in verifier and
            all(path in verifier for path in (
                "src/sync_sqlite_sidecar_claimed_path_snapshot.hpp",
                "src/sync_sqlite_sidecar_claimed_path_snapshot.cpp",
                "tests/sync_sqlite_sidecar_claimed_path_snapshot_test.cpp",
                "tools/audit_sync_sqlite_sidecar_snapshot.py",
            )),
            "release_verifier_requires_rev0861_boundary", "future packages cannot omit this owner or its proofs")
    require("revision_number >= 862" in verifier and
            all(path in verifier for path in (
                "src/persistence/sqlite_verification_budget.hpp",
                "src/persistence/sqlite_verification_budget.cpp",
                "tools/audit_sqlite_verification_budget.py",
            )),
            "release_verifier_requires_rev0862_execution_boundary", "future packages cannot retain the sidecar adapter while omitting its generic callback owner or audit")

    unqualified_durable_froms = [
        token for token in (
            "FROM sync_session_apply_intents",
            "FROM sync_session_manifest_entries",
            "FROM sync_session_manifests",
            "FROM sync_session_manifest_chunks",
            "FROM sync_session_manifest_lineage",
            "FROM sync_session_resume_transfer_workorders",
        ) if token in checkpoint_loader + apply_loader + remote_loader + session_wrapper
    ]
    require(not unqualified_durable_froms,
            "hydration_has_no_unqualified_durable_froms",
            f"unqualified={unqualified_durable_froms}")

    metrics = {
        "owner_lines": len(owner.splitlines()),
        "python_audit_commands_hermetic": cmake.count("COMMAND ${Python3_EXECUTABLE} -B -S"),
        "focused_progress_limit_markers": focused.count("progress_callback_limit"),
        "focused_test_lines": len(focused.splitlines()),
        "checkpoint_loader_open_calls": checkpoint_loader.count("sqlite3_open_v2("),
        "checkpoint_loader_commit_calls": checkpoint_loader.count("snapshot_transaction.commit();"),
        "remote_main_qualified_table_occurrences": remote_loader.count("main.sync_session_"),
        "remote_table_inventory_probes": remote_loader.count("peer_ingestion_table_exists_or_throw"),
        "unqualified_durable_froms": unqualified_durable_froms,
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
