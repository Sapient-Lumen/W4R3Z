#!/usr/bin/env python3
"""Fail-closed structural audit for the SQLite replica cutpoint owner."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_model.hpp"),
    Path("src/sync_replica_outbox_clock.hpp"),
    Path("src/sync_replica_outbox_lease.hpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tools/audit_sync_replica_outbox_clock.py"),
    Path("tools/audit_sync_replica_sqlite_owner.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
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
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-replica-sqlite-owner-audit-v7",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
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
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
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
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    cmake = text["CMakeLists.txt"]
    model_header = text["src/sync_replica_model.hpp"]
    clock_header = text["src/sync_replica_outbox_clock.hpp"]
    lease_header = text["src/sync_replica_outbox_lease.hpp"]
    header = text["src/sync_replica_sqlite_owner.hpp"]
    owner = text["src/sync_replica_sqlite_owner.cpp"]
    runtime = text["tests/sync_replica_sqlite_owner_test.cpp"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "class SyncReplicaSqliteOwner final" in header
        and "SyncReplicaSqliteOwner(const SyncReplicaSqliteOwner&) = delete" in header
        and "SyncReplicaSqliteOwner(SyncReplicaSqliteOwner&&) = delete" in header,
        "owner_is_single_nontransferable_authority",
        "one object owns one folder/local-actor cutpoint on one exact handle slot",
    )
    require(
        "intentionally an O(history) reference owner" in header
        and "not a production scaling claim" in header
        and "incremental production projector" in header,
        "reference_complexity_is_an_explicit_nonclaim",
        "full restore is correctness scaffolding rather than a hidden performance promise",
    )
    require(
        "not a substitute for an authenticated local store" in header
        and "local_operation_digest" in header
        and "cutpoint_digest" in header,
        "structural_seals_are_not_overclaimed_as_authentication",
        "the API exposes exact map/cutpoint seals while naming their trust boundary",
    )
    require(
        all(
            token in header
            for token in (
                "SyncReplicaModelLimits model",
                "max_outbox_intents",
                "max_outbox_destination_bytes",
                "max_outbox_clock_uncertainty_ns",
                "max_outbox_clock_forward_step_seconds",
                "max_outbox_clock_realtime_lag_seconds",
                "state_generation",
                "policy_generation",
            )
        ),
        "evidence_outbox_and_clock_policies_are_independent_durable_state",
        "sender pressure and liveness quality are never mislabeled as evidence validity",
    )
    require(
        "local_operation_ids()" in model_header
        and "const std::vector<std::string>&" in model_header,
        "local_authority_map_has_noncopying_const_view",
        "cutpoint hashing does not clone all local evidence merely to inspect counter bindings",
    )
    require(
        "SyncReplicaOutboxClockState outbox_clock_state" in header
        and "outbox_time_high_water_epoch" in header
        and "outbox_clock_digest" in header
        and "accepted/rejected host observation" in header,
        "snapshot_exposes_complete_separate_clock_authority",
        "liveness evidence remains visible without becoming canonical replica history",
    )
    require(
        all(
            token in lease_header
            for token in (
                "dispatch_attempts",
                "claim_id",
                "claimed_at_epoch",
                "lease_expires_at_epoch",
                "retry_released_at_epoch",
                "retry_release_provenance",
                "Expiry also revokes settlement",
            )
        ),
        "outbox_attempt_authority_is_complete_restart_state",
        "receipt identity, lifetime, and retry provenance survive crash and restart",
    )
    require(
        all(
            token in header
            for token in (
                "LeaseAlreadyCovered",
                "IntentMissing",
                "StaleClaim",
                "ExpiredClaim",
                "recover_outbox_clock_or_throw",
            )
        ),
        "public_results_name_noop_expiry_and_recovery_outcomes",
        "callers can distinguish missing, stale, expired, covered, and explicit recovery paths",
    )
    require(
        "std::uint64_t now_epoch" not in header
        and "clock_source_" in header
        and "std::unique_ptr<SyncReplicaOutboxClockSource>" in header,
        "caller_time_is_removed_from_the_owner_surface",
        "liveness observations come from one injected owner-controlled source",
    )

    schema = owner[owner.find("constexpr std::array<SchemaDefinition") :]
    require(
        all(
            token in schema
            for token in (
                "kLegacySchema",
                "kPreviousSchema",
                "kClockSchema",
                "kRetryProvenanceSchema",
                "kSchema",
                "schema_version=1",
                "schema_version=2",
                "schema_version=3",
                "schema_version=4",
                "schema_version=5",
            )
        )
        and schema.count(") STRICT") >= 25,
        "owner_declares_exact_v1_through_v5_strict_schemas",
        "every migration source and destination is an exact sqlite_schema protocol",
    )
    require(
        all(
            token in schema
            for token in (
                "max_outbox_clock_uncertainty_ns_be",
                "max_outbox_clock_forward_step_seconds_be",
                "max_outbox_clock_realtime_lag_seconds_be",
                "clock_state_bytes BLOB NOT NULL",
                "clock_digest TEXT NOT NULL",
                "retry_released_at_epoch_be",
                "retry_release_provenance INTEGER NOT NULL",
            )
        ),
        "schema_v5_persists_clock_policy_state_and_retry_provenance",
        "restart retains every field that can authorize, revoke, delay, or recover delivery",
    )

    read_schema = function_body(owner, "read_schema_objects_or_throw(")
    schema_matches = function_body(owner, "schema_matches(")
    require(
        "name GLOB 'sync_replica_*' OR" in read_schema
        and "tbl_name GLOB 'sync_replica_*'" in read_schema
        and "observed.size() != definitions.size()" in schema_matches
        and "sql != definition.stored_sql" in schema_matches,
        "schema_scan_rejects_extra_changed_missing_and_attached_objects",
        "an unrelated trigger name cannot hide executable behavior on a replica table",
    )
    constructor = function_body(owner, "SyncReplicaSqliteOwner::SyncReplicaSqliteOwner(")
    require(
        ordered(
            constructor,
            "PRAGMA foreign_keys=ON;PRAGMA trusted_schema=OFF;",
            "SyncSqliteTransaction transaction",
            "SyncSqliteTransactionMode::Immediate",
            "read_schema_objects_or_throw",
            "schema_matches(observed, kSchema)",
            "load_state_or_throw",
        ),
        "connection_hardening_precedes_schema_authority",
        "foreign keys and untrusted schema mode are set before any durable protocol decision",
    )
    require(
        "PRAGMA main.foreign_key_check;" in owner
        and "requires SQLite foreign key enforcement" in owner
        and "main.sync_replica_" in owner,
        "restore_enforces_foreign_keys_and_main_namespace_binding",
        "TEMP shadows and disabled references cannot redirect durable authority",
    )

    load = function_body(owner, "LoadedState load_state_for_schema_or_throw(")
    require(
        all(
            token in load
            for token in (
                "verify_schema_or_throw",
                "read_meta_or_throw",
                "read_current_outbox_clock_or_throw",
                "read_operations_or_throw",
                "SyncReplicaModel::restore_or_throw",
                "read_outbox_or_throw",
                "validate_sync_replica_outbox_clock_state_against_policy_or_throw",
            )
        ),
        "restore_rederives_schema_clock_evidence_model_and_outbox_together",
        "no redundant projection or liveness row is trusted without independent reconstruction",
    )
    require(
        "local_operation_digest_or_throw" in load
        and "model.operation_set_digest()" in load
        and "model.evidence_set_digest()" in load
        and "model.visible_state_digest()" in load
        and "outbox_digest_or_throw" in owner,
        "restore_recomputes_all_redundant_structural_digests",
        "same-dot forks, projection edits, and sender-state edits cannot preserve the intended cutpoint accidentally",
    )
    require(
        "outbox_clock_digest_or_throw" in owner
        and "anonsync-sync-replica-outbox-clock-v2" in owner
        and "clock_state_bytes=? AND clock_digest=?" in owner
        and "sqlite3_changes" in function_body(
            owner, "void update_outbox_clock_exact_or_throw("
        ),
        "clock_row_is_identity_bound_digest_sealed_and_exactly_updated",
        "lost-row authority, TEMP shadows, and casual direct edits fail closed",
    )

    migrate = function_body(owner, "void migrate_prior_schema_or_throw(")
    require(
        all(
            token in constructor
            for token in (
                "load_legacy_state_or_throw",
                "load_previous_state_or_throw",
                "load_clock_state_or_throw",
                "load_retry_provenance_state_or_throw",
                "schema v1 to v5",
                "schema v2 to v5",
                "schema v3 to v5",
                "schema v4 to v5",
            )
        )
        and "attest_and_commit_staged_cutpoint_or_throw" in migrate,
        "migration_requires_full_prior_attestation_and_atomic_v5_publication",
        "malformed old state cannot be laundered by rebuilding only metadata",
    )
    require(
        "make_legacy_unbound_sync_replica_outbox_clock_state_or_throw" in owner
        and "migrated_clock_state_or_throw" in owner
        and "high_water_epoch == 0U" in function_body(
            owner, "SyncReplicaOutboxClockState migrated_clock_state_or_throw("
        ),
        "legacy_time_is_quarantined_instead_of_relabelled_as_observed",
        "v1-v4 caller-time gaps become explicit LegacyUnbound recovery obligations",
    )

    staged_recheck = function_body(owner, "void attest_staged_cutpoint_or_throw(")
    staged_commit = function_body(owner, "void attest_and_commit_staged_cutpoint_or_throw(")
    require(
        ordered(
            staged_recheck,
            "load_state_or_throw",
            "observed.meta != expected_meta",
            "observed.outbox_clock != expected_outbox_clock",
            "observed.model.durable_state() != expected_model.durable_state()",
            "observed.outbox != expected_outbox",
            "require_write_authority_or_throw",
        )
        and ordered(
            staged_commit,
            "attest_staged_cutpoint_or_throw",
            "transaction.commit()",
        ),
        "every_successful_publication_has_full_independent_precommit_reattestation",
        "connection-local triggers cannot silently mutate a staged cutpoint after its write statement",
    )

    local_file = function_body(owner, "SyncReplicaSqliteOwner::create_local_file_or_throw(")
    require(
        ordered(
            local_file,
            "load_state_or_throw",
            "validate_destinations_or_throw",
            "require_outbox_capacity_or_throw",
            "create_local_file_or_throw",
            "insert_operation_rows_or_throw",
            "insert_outbox_intents_or_throw",
            "attest_and_commit_staged_cutpoint_or_throw",
        ),
        "local_publication_proves_sender_capacity_before_mint",
        "capacity pressure cannot consume a local dot and evidence/outbox publish as one cutpoint",
    )
    require(
        "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)" in schema
        and "canonical_bytes" not in function_body(owner, "void insert_outbox_intents_or_throw("),
        "outbox_fanout_references_one_canonical_operation_owner",
        "destination fanout stores lightweight intent authority rather than cloning operation bytes",
    )

    exact_update = function_body(owner, "void update_outbox_lease_exact_or_throw(")
    require(
        all(
            token in exact_update
            for token in (
                "enqueued_generation_be=?",
                "dispatch_attempts_be=?",
                "claim_id=?",
                "worker_id=?",
                "claimed_at_epoch_be=?",
                "lease_expires_at_epoch_be=?",
                "retry_not_before_epoch_be=?",
                "retry_released_at_epoch_be=?",
                "retry_release_provenance=?",
                "sqlite3_changes",
            )
        ),
        "lease_updates_compare_the_complete_prior_authority_row",
        "a competing writer or trigger cannot silently retarget an attempt transition",
    )
    lookup = function_body(owner, "find_outbox_intent(")
    require(
        "std::lower_bound" in lookup
        and "destination_device_id" in lookup
        and "operation_id" in lookup,
        "outbox_lookup_uses_canonical_logarithmic_search",
        "settlement, renewal, and release share one exact ordered-key lookup",
    )

    claim_wrapper = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_or_throw("
    )
    delivery_claim_wrapper = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_for_delivery_or_throw("
    )
    claim = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw("
    )
    require(
        "claim_next_outbox_impl_or_throw" in claim_wrapper
        and "claim_next_outbox_impl_or_throw" in delivery_claim_wrapper
        and ordered(
            claim,
            "random_claim_entropy_or_throw",
            "SyncSqliteTransaction transaction",
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "clock_source_->observe_or_throw",
            "accept_outbox_clock_observation_or_commit_quarantine_or_throw",
            "claim_sync_replica_outbox_lease_or_throw",
            "publish_outbox_lease_update_or_throw",
        ),
        "claim_keeps_entropy_prelock_but_linearizes_time_under_writer_authority",
        "both public claim surfaces share one core that excludes CSPRNG latency without aging the clock sample across SQLite wait",
    )
    require(
        "PreparedOutboxClockObservation" not in owner
        and "clock precondition remained contended" not in owner
        and "kOutboxClockPreconditionMaxAttempts" not in owner,
        "stale_prelock_clock_retry_mechanism_is_removed",
        "unrelated writer delay cannot preserve an old sample across a real expiry",
    )

    require(
        all(
            token in header
            for token in (
                "class SyncReplicaSqliteProjectionGuard final",
                "const SyncReplicaSqliteProjectionGuard&) = delete",
                "SyncReplicaSqliteProjectionGuard&&) = delete",
                "std::unique_ptr<SyncSqliteTransaction> transaction_",
                "guard_unambiguous_file_primary_at_cutpoint_or_throw",
                "It does not make SQLite and the filesystem one transaction",
            )
        ),
        "projection_guard_is_nontransferable_and_boundary_honest",
        "the external-effect bridge retains one exact typed transaction without claiming cross-store atomicity",
    )
    projection_guard = function_body(
        owner,
        "SyncReplicaSqliteOwner::guard_unambiguous_file_primary_at_cutpoint_or_throw(",
    )
    require(
        ordered(
            projection_guard,
            "SyncSqliteTransactionMode::Immediate",
            "require_write_authority_or_throw",
            "load_state_or_throw",
            "snapshot.state_generation != expected_state_generation",
            "snapshot.cutpoint_digest != expected_cutpoint_digest",
            "evidence_operation_by_id",
            "SyncReplicaEvidenceState::Active",
            "visible_path",
            "visible_operation_ids.size() == 1U",
            "new SyncReplicaSqliteProjectionGuard",
        )
        and "transaction->commit();" in projection_guard,
        "projection_guard_exactly_fences_one_active_primary_cutpoint",
        "a changed cutpoint or ambiguous projection returns without authority while a match retains BEGIN IMMEDIATE",
    )
    require(
        "test_projection_guard_serializes_external_effect_cutpoint" in runtime
        and "projection guard zero busy timeout" in runtime
        and "independent causal writer crossed a live projection guard" in runtime
        and "stale projection cutpoint minted authority or changed durable state" in runtime,
        "runtime_proves_projection_guard_writer_exclusion_and_stale_noop",
        "an independent connection is blocked while live, resumes after commit, and cannot revive an old cutpoint",
    )

    settle = function_body(owner, "SyncReplicaSqliteOwner::settle_outbox_or_throw(")
    renew = function_body(owner, "SyncReplicaSqliteOwner::renew_outbox_lease_or_throw(")
    release = function_body(owner, "SyncReplicaSqliteOwner::release_outbox_for_retry_or_throw(")
    for body, name in ((settle, "settlement"), (renew, "renewal"), (release, "retry_release")):
        require(
            ordered(
                body,
                "SyncSqliteTransactionMode::Immediate",
                "load_state_or_throw",
                "find_outbox_intent",
                "IntentMissing",
                "found->lease.claim_id != claim_id",
                "StaleClaim",
                "clock_source_->observe_or_throw",
                "sync_replica_outbox_claim_status_at_or_throw",
                "ExpiredClaim",
            ),
            f"{name}_checks_identity_before_owned_time",
            "missing or stale receipts cannot sample, ratchet, or recover liveness authority",
        )
    require(
        "delete_outbox_intent_exact_or_throw" in settle
        and "renew_sync_replica_outbox_lease_or_throw" in renew
        and "release_sync_replica_outbox_lease_or_throw" in release
        and "publish_outbox_lease_update_or_throw" in renew
        and "publish_outbox_lease_update_or_throw" in release,
        "terminal_and_nonterminal_receipt_paths_use_exact_shared_publication",
        "settlement deletes one row while renewal/release publish one exact re-attested lease transition",
    )

    recover = function_body(owner, "SyncReplicaSqliteOwner::recover_outbox_clock_or_throw(")
    require(
        ordered(
            recover,
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "clock_source_->observe_or_throw",
            "recover_sync_replica_outbox_clock_or_throw",
            "update_outbox_clock_exact_or_throw",
            "attest_and_commit_clock_observation_or_throw",
        ),
        "clock_recovery_is_serialized_exact_and_re_attested",
        "generation-fenced recovery cannot race another clock transition or publish a partial row",
    )
    replace = function_body(owner, "SyncReplicaSqliteOwner::replace_limits_or_throw(")
    require(
        ordered(
            replace,
            "validate_owner_limits_or_throw",
            "load_state_or_throw",
            "SyncReplicaModel::restore_or_throw",
            "retained outbox does not fit replacement policy",
            "validate_sync_replica_outbox_clock_state_against_policy_or_throw",
            "policy_generation",
            "attest_and_commit_staged_cutpoint_or_throw",
        ),
        "policy_replacement_reproves_evidence_outbox_and_clock_atomically",
        "restart cannot silently reinterpret retained authority under caller defaults",
    )

    require(
        all(
            token in runtime
            for token in (
                "test_exact_v1_migration_preserves_evidence_and_outbox",
                "test_exact_v2_migration_preserves_live_receipt_and_seeds_clock",
                "test_exact_v3_migration_preserves_clock_and_marks_retry_gap",
                "test_exact_v4_migration_preserves_retry_provenance_and_quarantines_clock",
                "test_malformed_v4_provenance_is_not_laundered_into_v5",
                "v2 migration must not relabel a caller epoch as trusted host time",
                "v3 migration must quarantine its caller-supplied legacy epoch",
                "v4 migration discarded exact retry-release provenance",
                "test_clock_sampling_is_inside_writer_transaction",
                "competing_writer_was_blocked",
                "test_outbox_clock_precommit_reattestation_and_tamper",
                "TEMP clock shadow displaced main clock authority",
                "TEMP-trigger clock mutation escaped staged re-attestation",
                "test_concurrent_claimers_mint_one_receipt",
                "test_process_crash_during_clock_only_publication_recovers_old_fence",
                "test_process_crash_during_renewal_recovers_prior_deadline",
                "std::barrier start(2)",
            )
        ),
        "runtime_covers_migration_linearization_tamper_concurrency_restart_and_crash",
        "the C++ suite pins both authority semantics and SQLite failure frontiers",
    )
    require(
        all(
            token in cmake
            for token in (
                "anonsync_sync_replica_outbox_clock",
                "anonsync_sync_replica_outbox_clock_test",
                "anonsync_sync_replica_outbox_lease",
                "anonsync_sync_replica_outbox_lease_test",
                "anonsync_sync_replica_sqlite_owner_test",
                "audit_sync_replica_outbox_clock.py",
                "audit_sync_replica_sqlite_owner.py",
                "TIMEOUT 60",
            )
        ),
        "owner_clock_lease_runtimes_and_audits_are_registered",
        "all authority layers participate in normal, sanitizer, and structural lanes",
    )
    require(
        "revision_number >= 874" in verifier
        and all(
            token in verifier
            for token in (
                "src/sync_replica_sqlite_owner.hpp",
                "src/sync_replica_sqlite_owner.cpp",
                "tests/sync_replica_sqlite_owner_test.cpp",
                "src/sync_replica_outbox_clock.hpp",
                "tools/audit_sync_replica_outbox_clock.py",
                "tools/audit_sync_replica_sqlite_owner.py",
                "OWNED_OUTBOX_CLOCK_AUDIT_rev0874.md",
            )
        ),
        "release_verifier_requires_the_complete_rev0874_owner_slice",
        "a sealed archive cannot omit implementation, clock authority, runtimes, audits, or design record",
    )
    require(
        "INSERT OR" not in owner and "ON CONFLICT" not in owner,
        "writes_do_not_mask_identity_or_projection_conflicts",
        "constraint conflicts abort the typed transaction rather than being normalized away",
    )
    require(
        "SyncReplicaOutboxClockAnchor" in clock_header
        and "cumulative drift anchor" in clock_header,
        "owner_depends_on_cumulative_not_pairwise_only_clock_evidence",
        "small repeated wall-clock steps cannot accumulate outside the durable policy unnoticed",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
