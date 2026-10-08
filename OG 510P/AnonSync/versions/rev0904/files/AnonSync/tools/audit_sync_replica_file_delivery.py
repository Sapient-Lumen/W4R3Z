#!/usr/bin/env python3
"""Lexical hygiene audit for the effect-terminal file-delivery composition.

This audit deliberately does not claim semantic proof. It inventories the
load-bearing authority flow so compiler/runtime/crash tests cannot be replaced
by nearby vocabulary or a weaker public overload during refactoring.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_delivery_channel.hpp"),
    Path("src/sync_replica_file_content_inventory.hpp"),
    Path("src/sync_replica_file_content_inventory.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_file_delivery_protocol.hpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_file_payload_snapshot.hpp"),
    Path("src/sync_replica_file_payload_snapshot.cpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tests/sync_replica_delivery_test_channel.hpp"),
    Path("tools/audit_sync_replica_file_delivery.py"),
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


def cmake_call(text: str, command_prefix: str) -> str:
    return delimited_body(text, command_prefix, "(", ")")


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-replica-file-delivery-audit-v5",
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
    channel = text["src/sync_replica_delivery_channel.hpp"]
    inventory_header = text["src/sync_replica_file_content_inventory.hpp"]
    inventory_source = text["src/sync_replica_file_content_inventory.cpp"]
    owner_header = text["src/sync_replica_sqlite_owner.hpp"]
    owner = text["src/sync_replica_sqlite_owner.cpp"]
    protocol = text["src/sync_replica_file_delivery_protocol.hpp"]
    service_header = text["src/sync_replica_file_delivery_service.hpp"]
    service = text["src/sync_replica_file_delivery_service.cpp"]
    snapshot_header = text["src/sync_replica_file_payload_snapshot.hpp"]
    snapshot_source = text["src/sync_replica_file_payload_snapshot.cpp"]
    effect_header = text["src/sync_replica_file_effect_sqlite_owner.hpp"]
    owner_runtime = text["tests/sync_replica_sqlite_owner_test.cpp"]
    service_runtime = text["tests/sync_replica_file_delivery_service_test.cpp"]
    test_channel = text["tests/sync_replica_delivery_test_channel.hpp"]
    verifier = text["tools/verify_release_package.py"]

    public_service = service_header[
        service_header.find("class SyncReplicaFileDeliveryService final") :
        service_header.find("private:", service_header.find("class SyncReplicaFileDeliveryService final"))
    ]
    require(
        public_service.count("const SyncReplicaDeliveryChannelAuthority&") == 5
        and "const SyncReplicaDeliveryChannelContext&" not in public_service,
        "public_file_service_requires_opaque_channel_authority",
        "preflight, claim, receive, and settlement cannot be invoked with caller-fabricable context bytes",
    )
    require(
        "SyncReplicaDeliveryChannelAuthority() = delete" in channel
        and "explicit SyncReplicaDeliveryChannelAuthority(" in channel
        and "friend class SyncReplicaFileDeliveryService" in channel
        and "friend class testing::SyncReplicaDeliveryTestChannelFactory" in channel,
        "channel_authority_minting_remains_private_and_reviewed",
        "the file coordinator may revalidate an authority but ordinary application code cannot mint one",
    )
    require(
        "Separately linked deterministic authority mint" in test_channel
        and "Production libraries do not expose or link this constructor path" in test_channel,
        "synthetic_channel_mint_is_test_only_by_contract",
        "runtime tests receive deterministic authority without adding a production forge path",
    )

    validate_channel = function_body(
        service, "SyncReplicaFileDeliveryService::validate_channel_or_throw("
    )
    require(
        ordered(validate_channel, "require_current_or_throw", ".context()"),
        "file_service_revalidates_before_context_observation",
        "actor and binding bytes are read only after process/thread/transport liveness succeeds",
    )

    claim = function_body(
        service,
        "SyncReplicaFileDeliveryService::\n    "
        "claim_next_request_from_payload_source_or_throw(",
    )
    require(
        ordered(
            claim,
            "validate_channel_or_throw",
            "payload_source.require_folder_or_throw",
            "payload_source.preflight_or_throw",
            "claim_next_outbox_for_delivery_or_throw",
            "SyncReplicaValueKind::File",
            "protocol_limits_.max_payload_bytes",
            "payload_source.content_inventory()",
            "payload = payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
            "validate_sync_replica_file_delivery_request_or_throw",
        ),
        "outbound_claim_has_live_authority_scoped_snapshot_and_dual_preflight",
        "channel and snapshot scope precede mutation; wire size and immutable content availability select the claim; exact bounded bytes are copied and re-proved afterward",
    )
    require(
        "std::shared_ptr<const State> state_" in snapshot_header
        and "SyncReplicaFileContentInventory content_inventory() const" in snapshot_header
        and "std::shared_ptr<const State> state_" in inventory_header
        and "std::vector<std::string> content_sha256s" in inventory_source
        and "std::sort" in snapshot_source
        and "std::adjacent_find" in snapshot_source
        and "std::sort(content_sha256s.begin(), content_sha256s.end())" in inventory_source
        and "contains duplicate content authority" in inventory_source
        and "max_retained_bytes" in snapshot_header
        and "SyncReplicaFilePayloadSource" not in service_header + service,
        "outbound_payload_authority_is_immutable_bounded_and_callback_free",
        "file delivery consumes content-addressed const state and never borrows mutable caller digest storage",
    )

    claim_core = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw("
    )
    require(
        ordered(
            claim_core,
            "load_state_or_throw",
            "evidence_operation_by_id",
            "validate_sync_replica_operation_or_throw",
            "operation->size_bytes > *max_file_payload_bytes",
            "std::binary_search",
            "continue",
            "claim_sync_replica_outbox_lease_or_throw",
            "publish_outbox_lease_update_or_throw",
        ),
        "delivery_policy_is_checked_before_attempt_authority",
        "an unsendable canonical operation cannot consume a claim; an unavailable policy-compatible payload is skipped without attempt authority",
    )

    receive = function_body(
        service, "SyncReplicaFileDeliveryService::receive_request_or_throw("
    )
    require(
        ordered(
            receive,
            "preflight_inbound_channel_or_throw",
            "decode_sync_replica_file_delivery_request_or_throw",
            "stage_with_diagnostics_or_throw",
            "EffectCapacityBlocked",
            "evidence_service_.receive_request_or_throw",
        ),
        "receiver_stages_bounded_payload_before_evidence_admission",
        "effect capacity cannot admit evidence that the receiver cannot retain exact bytes for",
    )
    require(
        "evidence_service_.receive_request_or_throw(\n            channel_authority" in receive,
        "inner_evidence_service_receives_the_same_live_capability",
        "file composition does not downgrade authenticated authority to descriptive context",
    )

    guard_header_tokens = (
        "class SyncReplicaSqliteProjectionGuard final",
        "SyncReplicaSqliteProjectionGuard&&) = delete",
        "std::unique_ptr<SyncSqliteTransaction> transaction_",
        "SyncReplicaSqliteSnapshot snapshot_",
        "It does not make SQLite and the filesystem one transaction",
    )
    require(
        all(token in owner_header for token in guard_header_tokens),
        "projection_guard_is_scope_bound_and_boundary_honest",
        "the bridge retains exact causal authority without relabeling two durable systems as one transaction",
    )
    guard = function_body(
        owner,
        "SyncReplicaSqliteOwner::guard_unambiguous_file_primary_at_cutpoint_or_throw(",
    )
    require(
        ordered(
            guard,
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
        ),
        "projection_guard_matches_exact_receipt_cutpoint_and_primary",
        "changed history, missing evidence, tombstones, conflicts, and preserved alternates cannot authorize publication",
    )
    require(
        ordered(
            receive,
            "guard_unambiguous_file_primary_at_cutpoint_or_throw",
            "evidence_receipt->receiver_state_generation",
            "evidence_receipt->receiver_cutpoint_digest",
            "materialize_or_throw",
            "effect_snapshot_or_throw",
            "encode_sync_replica_file_delivery_receipt_or_throw",
            "sync_replica_file_delivery_receipt_digest_or_throw",
            "projection_guard->commit_or_throw",
        ),
        "projection_guard_spans_materialization_and_receipt_construction",
        "a competing causal writer cannot invalidate the active primary between evidence receipt and visible effect",
    )
    require(
        "A changed cutpoint is conservatively retried" in receive
        and "immutable publication is reconciled by the next retry" in receive,
        "ambiguous_cross_store_frontiers_are_named_not_hidden",
        "stale cutpoints withhold publication while post-publication failures rely on immutable restart reconciliation",
    )
    require(
        "std::optional<SyncReplicaFileDeliveryReceiptDisposition> disposition" in receive
        and "if (!disposition.has_value())" in receive
        and "produced no classified disposition" in receive,
        "receipt_disposition_state_machine_is_total_and_fail_closed",
        "future or invalid materialization outcomes cannot use an uninitialized terminal classification",
    )

    apply_receipt = function_body(
        service, "SyncReplicaFileDeliveryService::apply_receipt_or_throw("
    )
    require(
        ordered(
            apply_receipt,
            "validate_channel_or_throw",
            "validate_sync_replica_file_delivery_receipt_for_request_or_throw",
            "sync_replica_file_delivery_receipt_is_effect_terminal",
            "retry_delay_for_nonterminal_or_throw",
            "release_outbox_for_retry_or_throw",
            "settle_outbox_or_throw",
        ),
        "sender_settles_only_effect_terminal_exact_attempts",
        "validated nonterminal receipts release the exact attempt onto local retry timing; only terminal effect receipts settle",
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
        "pre_dispatch_failure_releases_exact_claim_before_rethrow",
        "one shared helper preserves the original error only after exact bounded retry release succeeds",
    )
    require(
        ordered(
            claim,
            "payload = payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
            "dispatch_guard->claim()",
            "validate_sync_replica_file_delivery_request_or_throw",
            "encode_sync_replica_file_delivery_request_or_throw",
            "sync_replica_file_delivery_request_digest_or_throw",
            "dispatch_guard->commit_or_throw()",
            "return outbound",
        )
        and ordered(
            claim,
            "const std::exception_ptr original = std::current_exception()",
            "dispatch_guard.reset()",
            "release_claim_after_pre_dispatch_failure_or_throw",
        ),
        "post_snapshot_dispatch_guard_revalidates_exact_claim",
        "bounded immutable lookup/copy cannot turn an expired or independently superseded claim into a frame",
    )
    retry_validation = function_body(service, "validate_retry_policy_or_throw(")
    require(
        "delay == 0U" in retry_validation
        and "kSyncReplicaOutboxMaxRetryDelaySeconds" in retry_validation
        and "must be positive and within the fixed outbox retry-delay budget" in retry_validation
        and "zero retry delay reached service authority" in service_runtime,
        "retry_policy_rejects_zero_and_over_budget_delays",
        "caller policy cannot create an immediate retry spin or exceed the fixed owner budget",
    )
    require(
        all(
            token in protocol
            for token in (
                "Published = 1U",
                "AlreadyPublished = 2U",
                "EffectCapacityBlocked",
                "EffectPathBlocked",
                "sync_replica_file_delivery_receipt_precedes_effect_authority",
                "EvidencePending",
                "ProjectionBlocked",
                "DestinationConflict",
                "Every other disposition leaves the sender outbox intent live",
            )
        ),
        "protocol_names_terminal_and_nonterminal_effect_outcomes",
        "receiver retention is not silently equated with visible durable publication",
    )
    require(
        "separate database owner" in effect_header
        and "O(history)" in effect_header
        and "production index" in effect_header,
        "effect_owner_complexity_and_ownership_are_explicit",
        "the correctness oracle is not marketed as a production-scale payload store",
    )

    require(
        all(
            token in service_runtime
            for token in (
                "test_live_authority_and_payload_snapshot_preflight_precede_claim_mutation",
                "payload preflight rejection changed attempt or cutpoint authority",
                "moved-from authority rejection changed claim authority",
                "cross-folder payload snapshot rejection changed authority",
                "test_payload_snapshot_validation_selection_and_exact_mismatch_release",
                "immutable payload inventory did not select the first available canonical intent",
                "unavailable head-of-line payload consumed attempt or retry authority",
                "post-selection size mismatch did not exact-release its bounded live attempt",
                "test_post_snapshot_dispatch_guard_closes_clock_expiry",
                "claim expiring after payload lookup escaped as an outbound frame",
                "test_effect_path_policy_precedes_effect_and_evidence",
                "path-policy receipt did not retain intent under exact local backoff",
                "test_ambiguous_publication_survives_three_owner_restart",
                "old receipt replay changed a settled sender cutpoint",
                "file-only claimant leased an unsupported tombstone",
            )
        ),
        "file_service_runtime_covers_authority_preflight_restart_and_kind_fencing",
        "the integration suite exercises negative authority and ambiguous-response paths, not only the happy path",
    )
    require(
        all(
            token in owner_runtime
            for token in (
                "test_projection_guard_serializes_external_effect_cutpoint",
                "projection guard zero busy timeout",
                "independent causal writer crossed a live projection guard",
                "stale projection cutpoint minted authority or changed durable state",
                "test_outbox_dispatch_guard_reattests_and_serializes_claim",
                "competing writer crossed live dispatch claim authority",
                "stale dispatch identity sampled time or changed durable authority",
                "TEMP-trigger mutation escaped dispatch staged re-attestation",
            )
        ),
        "projection_guard_runtime_uses_an_independent_sqlite_writer",
        "BEGIN IMMEDIATE exclusion and stale-cutpoint no-op are executable evidence rather than source vocabulary alone",
    )

    production_link = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_replica_file_delivery_service "
    )
    test_link = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_replica_file_delivery_service_test "
    )
    require(
        "anonsync_sync_replica_delivery_test_channel" not in production_link
        and "anonsync_sync_replica_delivery_test_channel" in test_link,
        "test_authority_factory_is_absent_from_production_linkage",
        "CMake keeps deterministic minting on the test edge only",
    )
    require(
        "audit_sync_replica_file_delivery.py" in cmake
        and "anonsync_sync_replica_file_delivery_source_audit" in cmake,
        "file_delivery_audit_is_registered_in_ctest",
        "authority-flow inventory runs in the ordinary registered gate",
    )
    verifier_required = (
        "revision_number >= 878",
        "src/sync_replica_file_effect_identity.hpp",
        "src/sync_replica_file_delivery_protocol.cpp",
        "src/sync_replica_file_effect_sqlite_owner.cpp",
        "src/sync_replica_file_delivery_service.cpp",
        "tests/sync_atomic_file_reconciliation_test.cpp",
        "tests/sync_replica_file_effect_sqlite_owner_test.cpp",
        "tests/sync_replica_file_delivery_protocol_test.cpp",
        "tests/sync_replica_file_delivery_service_test.cpp",
        "tools/audit_sync_replica_file_delivery.py",
        "EFFECT_TERMINAL_CUTPOINT_GUARD_AUDIT_rev0878.md",
    )
    require(
        all(token in verifier for token in verifier_required),
        "release_verifier_requires_complete_file_effect_surface",
        "rev0878 packages cannot omit the effect owner, protocol, service, restart tests, audit, or design record",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(encoding="utf-8")
        and "does not claim semantic proof" in Path(__file__).read_text(encoding="utf-8"),
        "audit_does_not_overclaim_lexical_checks",
        "runtime, sanitizer, crash, and compiler evidence remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
