#!/usr/bin/env python3
"""Lexical hygiene audit for post-snapshot outbox dispatch authority.

This inventory deliberately does not prove SQLite isolation, clock behavior,
exception safety, or network semantics. Runtime, compiler, sanitizer, stress,
and crash evidence remain load-bearing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_file_payload_snapshot.hpp"),
    Path("src/sync_replica_file_payload_snapshot.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tools/audit_sync_replica_file_delivery.py"),
    Path("tools/audit_sync_file_effect_path_capability.py"),
    Path("tools/audit_sync_outbox_dispatch_guard.py"),
    Path("tools/verify_release_package.py"),
    Path("OUTBOX_DISPATCH_GUARD_AUDIT_rev0881.md"),
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


def delimited_body(text: str, signature: str, opening: str, closing: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    boundary = text.find(opening, start + len(signature))
    if boundary < 0:
        return ""
    depth = 0
    for index in range(boundary, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def function_body(text: str, signature: str) -> str:
    return delimited_body(text, signature, "{", "}")


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-outbox-dispatch-guard-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
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
    owner_header = text["src/sync_replica_sqlite_owner.hpp"]
    owner = text["src/sync_replica_sqlite_owner.cpp"]
    service_header = text["src/sync_replica_file_delivery_service.hpp"]
    service = text["src/sync_replica_file_delivery_service.cpp"]
    snapshot_header = text["src/sync_replica_file_payload_snapshot.hpp"]
    snapshot_source = text["src/sync_replica_file_payload_snapshot.cpp"]
    store_header = text["src/sync_replica_file_payload_store.hpp"]
    store_source = text["src/sync_replica_file_payload_store.cpp"]
    owner_runtime = text["tests/sync_replica_sqlite_owner_test.cpp"]
    service_runtime = text["tests/sync_replica_file_delivery_service_test.cpp"]
    delivery_audit = text["tools/audit_sync_replica_file_delivery.py"]
    path_audit = text["tools/audit_sync_file_effect_path_capability.py"]
    verifier = text["tools/verify_release_package.py"]
    design = text["OUTBOX_DISPATCH_GUARD_AUDIT_rev0881.md"]
    self_text = text["tools/audit_sync_outbox_dispatch_guard.py"]

    require(
        all(
            token in owner_header
            for token in (
                "enum class SyncReplicaSqliteOutboxDispatchGuardDisposition",
                "Acquired",
                "IntentMissing",
                "StaleClaim",
                "ExpiredClaim",
                "class SyncReplicaSqliteOutboxDispatchGuard final",
                "SyncReplicaSqliteOutboxDispatchGuardResult",
                "guard_outbox_claim_for_dispatch_or_throw",
            )
        ),
        "typed_dispatch_outcomes_and_guard_are_public_owner_surface",
        "missing, stale, expired, and acquired are explicit rather than collapsed into nullable history",
    )
    guard_class = function_body(
        owner_header, "class SyncReplicaSqliteOutboxDispatchGuard final"
    )
    require(
        guard_class.count("= delete") >= 4
        and "std::unique_ptr<SyncSqliteTransaction> transaction_" in guard_class
        and "SyncReplicaSqliteOutboxClaim claim_" in guard_class
        and "observed_epoch_" in guard_class,
        "dispatch_guard_is_scope_bound_nontransferable_transaction_authority",
        "ordinary claim data cannot be confused with the live writer capability",
    )
    require(
        all(
            token in owner_header
            for token in (
                "not a general network-I/O transaction",
                "bounded payload lookup/copy",
                "invoke caller code while it is live",
                "bounded local request",
                "fixed-size first-prefix write",
                "must never cover the",
                "payload body",
            )
        )
        and "The returned frame is not" in service_header
        and "itself a network-send authority" in service_header,
        "header_contract_names_bounded_scope_and_later_send_frontier",
        "the API does not overclaim database-plus-network atomicity",
    )

    staged_attestation = function_body(owner, "void attest_staged_cutpoint_or_throw(")
    staged_commit = function_body(
        owner, "void attest_and_commit_staged_cutpoint_or_throw("
    )
    require(
        ordered(
            staged_attestation,
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
        "staged_cutpoint_attestation_is_refactored_without_weakening_commit_path",
        "dispatch and ordinary publication share one complete independent reload",
    )

    guard = function_body(
        owner,
        "SyncReplicaSqliteOwner::guard_outbox_claim_for_dispatch_or_throw(",
    )
    require(
        "SyncSqliteTransactionMode::Immediate" in guard
        and ordered(
            guard,
            "require_write_authority_or_throw",
            "load_state_or_throw",
            "find_outbox_intent",
        ),
        "dispatch_guard_begins_writer_authority_before_restore",
        "the current row is loaded from a writer-serialized cutpoint",
    )
    require(
        ordered(
            guard,
            "found == loaded.outbox.end()",
            "IntentMissing",
            "found->lease.claim_id != expected_intent.lease.claim_id",
            "StaleClaim",
            "clock_source_->observe_or_throw",
        ),
        "missing_and_stale_identity_precede_clock_observation",
        "obsolete callers cannot ratchet durable liveness time",
    )
    require(
        all(
            token in guard
            for token in (
                "expected_with_current_deadline",
                "lease_expires_at_epoch",
                "*found != expected_with_current_deadline",
                "found->lease.lease_expires_at_epoch <",
                "changed outside bounded renewal",
            )
        ),
        "only_nondecreasing_same_claim_renewal_is_tolerated",
        "receipt identity and every nondeadline row field remain exact",
    )
    require(
        ordered(
            guard,
            "clock_source_->observe_or_throw",
            "accept_outbox_clock_observation_or_commit_quarantine_or_throw",
            "sync_replica_outbox_claim_status_at_or_throw",
            "ExpiredClaim",
        )
        and "attest_and_commit_clock_observation_or_throw" in guard,
        "owned_clock_revalidates_and_durably_revokes_expiry",
        "expiry commits time evidence without fabricating retry release",
    )
    require(
        ordered(
            guard,
            "validate_sync_replica_operation_or_throw",
            "evidence_operation_by_id",
            "*retained != expected_claim.operation",
            "attest_staged_cutpoint_or_throw",
            "SyncReplicaSqliteOutboxClaim current_claim",
            "SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired",
        ),
        "canonical_operation_and_complete_staged_cutpoint_precede_guard_escape",
        "claim identity alone cannot authorize different operation evidence",
    )

    guard_constructor = function_body(
        owner,
        "SyncReplicaSqliteOutboxDispatchGuard::\n    SyncReplicaSqliteOutboxDispatchGuard(",
    )
    guard_commit = function_body(
        owner, "void SyncReplicaSqliteOutboxDispatchGuard::commit_or_throw("
    )
    require(
        "requires a live transaction" in guard_constructor
        and "requires an owned epoch" in guard_constructor
        and "claim is inconsistent" in guard_constructor
        and ordered(guard_commit, "if (!active())", "transaction_->commit()", "transaction_.reset()"),
        "guard_constructor_and_single_commit_validate_capability_state",
        "inactive or internally inconsistent guards cannot authorize construction",
    )

    release_helper = function_body(
        service, "SyncReplicaFileDeliveryService::release_claim_after_pre_dispatch_failure_or_throw("
    )
    require(
        ordered(
            release_helper,
            "release_outbox_for_retry_or_throw",
            "SyncReplicaSqliteOutboxReceiptResult::Applied",
            "IntentMissing",
            "StaleClaim",
            "ExpiredClaim",
            "std::rethrow_exception(original)",
        )
        and "exact retry release failed" in release_helper,
        "pre_dispatch_release_refactor_preserves_exact_contradiction_matrix",
        "all failure sites share one implementation and never misreport a failed release",
    )

    claim = function_body(
        service,
        "SyncReplicaFileDeliveryService::\n    "
        "claim_next_request_from_payload_source_or_throw(",
    )
    require(
        ordered(
            claim,
            "payload_source.require_folder_or_throw",
            "payload_source.preflight_or_throw",
            "claim_next_outbox_for_delivery_or_throw",
            "payload_source.content_inventory()",
            "payload = payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
        )
        and "std::shared_ptr<const State> state_" in snapshot_header
        and "std::sort" in snapshot_source
        and "std::adjacent_find" in snapshot_source
        and "std::unique_ptr<State> state_" in store_header
        and "SyncReplicaFilePayloadStoreSnapshot(\n        const SyncReplicaFilePayloadStoreSnapshot&) = delete" in store_header
        and "std::sort" in store_source
        and "std::adjacent_find" in store_source,
        "immutable_payload_lookup_finishes_before_dispatch_guard",
        "bounded immutable in-memory or durable indexed lookup and copy finish before the SQLite writer capability is held",
    )
    require(
        "throw_dispatch_attestation_failure_or_throw" in claim
        and all(
            token in service
            for token in (
                "dispatch attestation lost its outbox intent",
                "dispatch attestation lost exact claim identity",
                "dispatch attestation found its exact claim expired",
            )
        ),
        "post_snapshot_contradictions_are_typed_and_no_frame_is_returned",
        "missing, superseded, and expired claims are not converted into a generic payload lookup failure",
    )
    require(
        ordered(
            claim,
            "dispatch_guard->claim()",
            "make_sync_replica_delivery_request_from_claim_or_throw",
            "validate_sync_replica_file_delivery_request_or_throw",
            "encode_sync_replica_file_delivery_request_or_throw",
            "sync_replica_file_delivery_request_digest_or_throw",
            "SyncReplicaOutboundFileDelivery outbound",
            "std::is_nothrow_move_constructible_v",
            "std::is_nothrow_constructible_v",
            "dispatch_guard->commit_or_throw()",
            "return outbound",
        ),
        "bounded_request_construction_and_nothrow_escape_precede_guard_commit",
        "no post-commit allocation or throwing frame construction frontier is intended",
    )
    require(
        ordered(
            claim,
            "const std::exception_ptr original = std::current_exception()",
            "dispatch_guard.reset()",
            "release_claim_after_pre_dispatch_failure_or_throw",
        ),
        "construction_failure_rolls_back_guard_before_exact_release",
        "the release transition never competes with the service's own live writer transaction",
    )
    require(
        all(token not in claim for token in ("send(", "sendmsg(", "write(")),
        "network_io_is_absent_from_dispatch_guard_scope",
        "SQLite writer serialization is not held across a socket operation",
    )

    require(
        all(
            token in service_runtime
            for token in (
                "test_payload_snapshot_validation_selection_and_exact_mismatch_release",
                "unavailable head-of-line payload consumed attempt or retry authority",
                "post-selection size mismatch did not exact-release its bounded live attempt",
                "test_post_snapshot_dispatch_guard_closes_clock_expiry",
                "claim expiring after payload lookup escaped as an outbound frame",
                "dispatch guard did not durably retain exact expired authority",
            )
        ),
        "service_runtime_executes_release_settle_expiry_renewal_and_validation_matrix",
        "no-attempt availability selection, post-selection contradiction release, and post-lookup expiry are behaviorally exercised",
    )
    require(
        all(
            token in owner_runtime
            for token in (
                "test_outbox_dispatch_guard_reattests_and_serializes_claim",
                "competing writer crossed live dispatch claim authority",
                "stale dispatch identity sampled time or changed durable authority",
                "expired dispatch claim was not revoked by one durable clock-only cutpoint",
                "missing dispatch intent sampled time or recreated durable state",
                "TEMP-trigger mutation escaped dispatch staged re-attestation",
            )
        ),
        "owner_runtime_executes_serialization_clock_and_trigger_matrix",
        "writer exclusion and full staged rollback are tested independently of the service",
    )

    require(
        "post_snapshot_dispatch_guard_revalidates_exact_claim" in delivery_audit
        and "post_snapshot_dispatch_guard_revalidates_exact_claim" in path_audit,
        "existing_authority_audits_track_dispatch_guard",
        "older inventories cannot silently regress to copied payload plus copied-claim semantics",
    )
    require(
        "anonsync_sync_outbox_dispatch_guard_source_audit" in cmake
        and "tools/audit_sync_outbox_dispatch_guard.py" in verifier
        and "OUTBOX_DISPATCH_GUARD_AUDIT_rev0881.md" in verifier,
        "build_and_package_graph_require_guard_audit_surface",
        "the source audit and design record cannot be omitted from rev0881 packaging",
    )
    require(
        all(
            token in design
            for token in (
                "The failed authority sequence",
                "Corrected ownership sequence",
                "BEGIN IMMEDIATE",
                "https://sqlite.org/lang_transaction.html",
                "https://sqlite.org/isolation.html",
                "https://man7.org/linux/man-pages/man2/send.2.html",
                "Durable frame ownership",
                "returned outbound frame remains current indefinitely",
                "historical evidence is not",
                "live authority",
            )
        ),
        "design_record_contains_primary_sources_failure_matrix_and_nonclaims",
        "the handoff explains both the corrected local frontier and the unresolved network frontier",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "does not prove SQLite isolation" in self_text,
        "audit_disclaims_semantic_proof",
        "runtime, compiler, sanitizer, stress, and crash evidence remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
