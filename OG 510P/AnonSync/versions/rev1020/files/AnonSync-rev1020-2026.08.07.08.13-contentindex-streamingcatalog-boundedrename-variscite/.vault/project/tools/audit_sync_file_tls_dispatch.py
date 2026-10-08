#!/usr/bin/env python3
"""Lexical hygiene audit for the file/TLS first-prefix dispatch frontier.

This inventory does not prove TLS delivery, SQLite isolation, crash safety,
peer receipt, or exactly-once effects. Compiled runtime, sanitizer, stress, and
end-to-end crash evidence remain load-bearing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_delivery_service.hpp"),
    Path("src/sync_replica_delivery_service.cpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_socket_readiness_identity.hpp"),
    Path("src/sync_socket_readiness_identity.cpp"),
    Path("tests/sync_socket_readiness_identity_test.cpp"),
    Path("src/sync_replica_file_tls_dispatch.hpp"),
    Path("src/sync_replica_file_tls_dispatch.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_file_tls_dispatch.py"),
    Path("tools/verify_release_package.py"),
    Path("TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md"),
    Path("TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md"),
    Path("TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md"),
    Path("TLS_FILE_DISPATCH_CONTINUATION_AUDIT_rev0887.md"),
    Path("TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md"),
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


def class_body(text: str, signature: str) -> str:
    return delimited_body(text, signature, "{", "}")


def target_block(cmake: str, target: str) -> str:
    start = cmake.find(f"add_library({target}")
    if start < 0:
        start = cmake.find(f"add_executable({target}")
    if start < 0:
        return ""
    next_target = cmake.find("\nadd_", start + 1)
    return cmake[start:] if next_target < 0 else cmake[start:next_target]


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-file-tls-dispatch-audit-v6",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "substring and source-order checks do not prove socket progress, "
            "SQLite transaction semantics, crash recovery, peer admission, "
            "terminal effects, or exactly-once delivery"
        ),
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
    evidence_h = text["src/sync_replica_delivery_service.hpp"]
    evidence_cpp = text["src/sync_replica_delivery_service.cpp"]
    file_h = text["src/sync_replica_file_delivery_service.hpp"]
    file_cpp = text["src/sync_replica_file_delivery_service.cpp"]
    owner_h = text["src/sync_replica_sqlite_owner.hpp"]
    tls_h = text["src/sync_replica_tls_transport.hpp"]
    tls_cpp = text["src/sync_replica_tls_transport.cpp"]
    socket_h = text["src/sync_socket_readiness_identity.hpp"]
    socket_cpp = text["src/sync_socket_readiness_identity.cpp"]
    socket_runtime = text["tests/sync_socket_readiness_identity_test.cpp"]
    dispatch_h = text["src/sync_replica_file_tls_dispatch.hpp"]
    dispatch_cpp = text["src/sync_replica_file_tls_dispatch.cpp"]
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    design = text["TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md"]
    affinity_design = text["TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md"]
    lifetime_design = text["TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md"]
    dispatch_design = text["TLS_FILE_DISPATCH_CONTINUATION_AUDIT_rev0887.md"]
    self_text = text["tools/audit_sync_file_tls_dispatch.py"]

    dispatch_target = target_block(cmake, "anonsync_sync_replica_file_tls_dispatch")
    require(
        "ANONSYNC_SYNC_REPLICA_FILE_TLS_DISPATCH_SOURCE" in dispatch_target
        and "src/sync_replica_file_tls_dispatch.cpp" in cmake
        and all(
            token in dispatch_target
            for token in (
                "anonsync_sync_replica_file_delivery_service",
                "anonsync_sync_replica_tls_poll",
                "-Wall -Wextra -Wpedantic",
            )
        ),
        "composition_is_a_narrow_separately_linked_library",
        "the file service remains transport-neutral and the TLS seam is reviewable",
    )
    require(
        "sync_replica_tls_transport" not in file_cpp
        and "<openssl/" not in file_cpp
        and "<openssl/" not in file_h,
        "file_delivery_service_remains_transport_neutral",
        "OpenSSL and stream lifetime do not leak into effect/evidence ownership",
    )
    require(
        cmake.count("anonsync_sync_file_tls_dispatch_source_audit") >= 2
        and "tools/audit_sync_file_tls_dispatch.py" in cmake,
        "audit_is_registered_with_ctest",
        "the structural inventory participates in the ordinary source-audit gate",
    )

    builder = "make_sync_replica_delivery_request_from_claim_or_throw"
    require(
        evidence_cpp.count(builder + "(") == 2
        and file_cpp.count(builder + "(") == 1
        and dispatch_cpp.count(builder + "(") == 2,
        "one_canonical_claim_to_request_builder_serves_all_delivery_paths",
        "generic, file, and immediate TLS dispatch cannot drift through duplicate identity logic",
    )
    builder_body = function_body(evidence_cpp, builder + "(")
    require(
        all(
            token in builder_body
            for token in (
                "claim.intent.destination_device_id != channel.peer_actor.device_id",
                "claim.intent.operation_id != claim.operation.operation_id",
                "claim.operation.dot.actor != local_actor",
                "required_kind.has_value()",
                "claim.intent.lease.claim_id.empty()",
                "claim.intent.lease.dispatch_attempts == 0U",
            )
        ),
        "shared_builder_checks_destination_evidence_kind_and_attempt_identity",
        "descriptive rows cannot silently mint a request for another actor or attempt",
    )

    continuation = class_body(tls_h, "class SyncReplicaTlsRecordWriteContinuation final")
    require(
        continuation.count("= delete") >= 2
        and "&& other) noexcept" in continuation
        and "operator=(" in continuation
        and "~SyncReplicaTlsRecordWriteContinuation() noexcept" in continuation,
        "record_continuation_is_move_only_and_noexcept_transferable",
        "one scope owns the unfinished stream record and handoff after prefix cannot allocate",
    )
    require(
        "private:" in continuation
        and "SyncReplicaTlsRecordWriteContinuation(" in continuation.split("private:", 1)[1]
        and "std::unique_ptr<detail::SyncReplicaTlsRecordWriteState> state_"
        in continuation.split("private:", 1)[1],
        "continuation_mint_is_private",
        "ordinary callers cannot fabricate an accepted-prefix capability",
    )
    file_continuation = class_body(
        dispatch_h, "class SyncReplicaFileTlsDispatchContinuation final"
    )
    require(
        file_continuation.count("= delete") >= 2
        and "&& other) noexcept" in file_continuation
        and "~SyncReplicaFileTlsDispatchContinuation() noexcept"
            in file_continuation
        and all(
            token in file_continuation
            for token in (
                "outbound_or_throw()",
                "advance_or_throw()",
                "pending_readiness_or_throw() const",
                "poll_and_advance_or_throw(",
                "std::unique_ptr<detail::SyncReplicaFileTlsDispatchState> state_",
                "SyncReplicaTlsRecordWriteContinuation transport_",
            )
        ),
        "file_dispatch_continuation_is_exclusive_exact_and_pollable",
        "the durable attempt and exact TLS retry travel in one move-only owner",
    )
    file_move_assignment = function_body(
        dispatch_cpp,
        "SyncReplicaFileTlsDispatchContinuation::operator=(",
    )
    file_pending = function_body(
        dispatch_cpp,
        "SyncReplicaFileTlsDispatchContinuation::pending_readiness_or_throw() const",
    )
    require(
        ordered(
            file_move_assignment,
            "transport_ = std::move(other.transport_)",
            "state_ = std::move(other.state_)",
        )
        and ordered(
            file_pending,
            "transport_.pending_readiness_or_throw()",
            "if (!transport_.active())",
            "Terminal::Failed",
        ),
        "outer_owner_poison_order_and_precondition_classification_are_explicit",
        "old stream authority is surrendered before metadata and pre-WANT misuse stays nonterminal",
    )
    state = class_body(tls_cpp, "class detail::SyncReplicaTlsAuthenticatedState final")
    require(
        all(
            token in state
            for token in (
                "SyncReplicaTlsRecordReservation::Idle",
                "SyncReplicaTlsRecordReservation::Read",
                "SyncReplicaTlsRecordReservation::Write",
                "record_reservation_",
                "begin_record_write_or_throw",
                "active_record_io_or_throw",
                "require_record_owner_or_throw",
                "complete_record_write_noexcept",
                "begin_record_read_or_throw",
                "complete_record_read_noexcept",
                "record_reservation_ = SyncReplicaTlsRecordReservation::Write",
                "record_reservation_ = SyncReplicaTlsRecordReservation::Read",
                "record_reservation_ = SyncReplicaTlsRecordReservation::Idle",
            )
        ),
        "tls_state_owns_one_exclusive_duplex_record_reservation",
        "read and write continuations are serialized by the live SSL owner rather than caller convention",
    )
    owner_fence = function_body(
        tls_cpp, "void require_owner_or_fail_stop_noexcept() const noexcept"
    )
    require(
        ordered(
            owner_fence,
            "sync_process_incarnation_is_current(owner_process_)",
            "fail_stop_on_sync_process_capability_violation_noexcept()",
            "sync_thread_incarnation_is_current(owner_thread_)",
            "fail_stop_on_sync_thread_capability_violation_noexcept()",
        ),
        "one_noexcept_owner_fence_covers_process_then_thread",
        "cleanup paths share the same fail-stop affinity proof before touching SSL-owned state",
    )
    require(
        all(
            ordered(
                function_body(tls_cpp, signature),
                "require_owner_or_fail_stop_noexcept()",
                mutation,
            )
            for signature, mutation in (
                (
                    "void complete_record_write_noexcept() const noexcept",
                    "record_reservation_",
                ),
                ("void poison_noexcept() const noexcept", "poisoned_ = true"),
                ("void release_ssl_noexcept() noexcept", "SSL_free"),
            )
        ),
        "noexcept_completion_poison_and_ssl_release_fence_before_mutation",
        "destructors and failure cleanup cannot silently mutate or free a foreign-thread SSL owner",
    )
    require(
        all(
            phrase in tls_h
            for phrase in (
                "Abandoning,",
                "after any write attempt permanently poisons",
                "Foreign-owner cleanup fails stopped",
                "shared TLS state",
            )
        ),
        "public_contract_names_foreign_owner_cleanup_fail_stop",
        "the no-throw destructor boundary and attempted-write poison rule are explicit rather than implementation accidents",
    )
    require(
        ordered(
            function_body(tls_cpp, "void validate_or_throw("),
            "require_current_or_throw(label)",
            "require_usable_or_throw(label)",
            "require_record_idle_or_throw(label)",
            "validate_authenticated_channel_and_poison_or_throw(label)",
        )
        and "validate_or_throw(label)" in function_body(
            tls_cpp, "SSL* begin_record_write_or_throw("
        )
        and "validate_or_throw(label)" in function_body(
            tls_cpp, "void begin_record_read_or_throw("
        ),
        "ordinary_authority_and_record_begin_reject_active_duplex_io",
        "service validation, a second read, or a write cannot enter OpenSSL through an unfinished record operation",
    )
    prepare = function_body(
        tls_cpp, "prepare_sync_replica_tls_record_write_or_throw("
    )
    begin = function_body(
        tls_cpp, "begin_sync_replica_tls_record_write_or_throw("
    )
    write_state = class_body(
        tls_cpp, "class detail::SyncReplicaTlsRecordWriteState final"
    )
    require(
        ordered(
            prepare,
            "validate_record_limit_or_throw",
            "if (frame_bytes == 0U)",
            "if (frame_bytes > max_frame_bytes)",
            "std::string owned_frame(frame)",
            "SyncReplicaTlsRecordWriteReadinessPolicy::RequireNonblockingSocket",
            "std::make_unique<detail::SyncReplicaTlsRecordWriteState>",
            "begin_record_write_or_throw(",
            "reservation_active = true",
            "SyncReplicaTlsRecordWriteContinuation(std::move(write_state))",
        )
        and "SSL_write_ex(" not in prepare
        and ordered(
            begin,
            "prepare_sync_replica_tls_record_write_or_throw",
            "continuation.advance_or_throw",
            "continuation.prefix_complete()",
        ),
        "prefix_begin_validates_and_constructs_before_stream_progress",
        "prepare freezes all throwing local state and reserves the stream before begin advances the prefix",
    )
    require(
        ordered(
            write_state,
            "~SyncReplicaTlsRecordWriteState() noexcept",
            "abandon_noexcept()",
            "abandon_record_write_noexcept(io_started)",
        )
        and "length prefix reached nonblocking TLS readiness loss" in begin
        and "zero-byte WANT owns one exact pending" in tls_h,
        "failed_prefix_poison_is_fail_closed",
        "after any attempted prefix operation, failure or readiness loss cannot leave a reusable framing stream",
    )
    transport_anchor = function_body(
        tls_cpp, "capture_tls_transport_anchor_or_throw("
    )
    nonblocking = function_body(
        tls_cpp, "void require_tls_transport_anchor_nonblocking_or_throw("
    )
    socket_observer = function_body(
        socket_cpp, "SyncSocketLifetimeIdentity observe_sync_stream_socket_lifetime_or_throw("
    )
    require(
        ordered(
            transport_anchor,
            "SSL_get_rbio(ssl)",
            "SSL_get_wbio(ssl)",
            "retain_tls_bio_reference_or_throw",
            "observe_direct_tls_stream_socket_lifetime_or_throw",
            "validate_tls_transport_anchor_or_throw",
        )
        and nonblocking.count(
            "require_sync_stream_socket_nonblocking_or_throw"
        ) == 2
        and ordered(
            socket_observer,
            "fstat(descriptor, &before)",
            "S_ISSOCK(before.st_mode)",
            "observe_socket_type_or_throw",
            "observe_socket_cookie_or_throw",
            "fstat(descriptor, &after)",
        )
        and "SOCK_STREAM" in socket_cpp
        and "SO_COOKIE" in socket_cpp
        and "anonsync_sync_socket_readiness_identity" in
            target_block(cmake, "anonsync_sync_replica_tls_transport")
        and "descriptor number alone is not authority" in socket_h
        and "identity fields deliberately remain opaque" in socket_h
        and "cannot prove an exact stream-socket lifetime on this platform"
            in socket_cpp
        and all(
            token not in tls_cpp
            for token in ("::getsockopt", "::fcntl", "::fstat", "SO_COOKIE")
        ),
        "bounded_policy_reproves_socket_backing_and_both_nonblocking_directions",
        "a database writer cannot enter an unobservable or blocking TLS BIO",
    )
    advance_write = function_body(
        tls_cpp, "SyncReplicaTlsRecordWriteContinuation::advance_or_throw()"
    )
    finish = function_body(
        tls_cpp, "SyncReplicaTlsRecordWriteContinuation::finish_or_throw("
    )
    pending_write = function_body(
        tls_cpp,
        "SyncReplicaTlsRecordWriteContinuation::pending_readiness_or_throw() const",
    )
    require(
        "std::string frame" in class_body(
            tls_cpp, "class detail::SyncReplicaTlsRecordWriteState final"
        )
        and ordered(
            advance_write,
            "kSyncReplicaTlsRecordWriteStepBytes",
            "active_record_io_or_throw",
            "SyncReplicaTlsRecordReservation::Write",
            "SSL_write_ex",
            "SSL_get_error",
            "SSL_ERROR_WANT_READ",
            "SSL_ERROR_WANT_WRITE",
            "complete_record_write_noexcept",
            "catch (...)",
            "state_->abandon_noexcept()",
        )
        and ordered(
            pending_write,
            "SyncReplicaTlsPendingReadiness::None",
            "pending_readiness_target_or_throw",
            "catch (...)",
            "state_->abandon_noexcept()",
        )
        and ordered(
            finish,
            "advance_or_throw",
            "SyncReplicaTlsRecordWriteProgress::WantRead",
            "reached nonblocking TLS readiness loss",
            "state_->abandon_noexcept()",
        ),
        "continuation_binds_exact_body_and_poison_on_failure",
        "private stable bytes, retry progress, lost authority, and body failure cannot desynchronize reuse",
    )
    wrapper = function_body(tls_cpp, "write_sync_replica_tls_record_or_throw(")
    require(
        ordered(
            wrapper,
            "begin_sync_replica_tls_record_write_or_throw",
            "continuation.finish_or_throw()",
        ),
        "legacy_record_writer_delegates_to_one_state_machine",
        "the ordinary and composed send paths share framing and poisoning semantics",
    )

    validate_frozen = function_body(
        dispatch_cpp, "validate_frozen_outbound_or_throw("
    )
    require(
        ordered(
            validate_frozen,
            builder,
            "validate_sync_replica_file_delivery_request_or_throw",
            "encode_sync_replica_file_delivery_request_or_throw",
            "canonical_frame != outbound.request_frame",
            "sync_replica_file_delivery_request_digest_or_throw",
            "canonical_digest != outbound.request_digest",
        ),
        "preflight_rebuilds_request_frame_and_digest",
        "caller-owned outbound bytes are not trusted as canonical dispatch authority",
    )
    dispatch_begin = function_body(
        dispatch_cpp,
        "begin_sync_replica_outbound_file_delivery_over_tls_or_throw(",
    )
    dispatch_wrapper = function_body(
        dispatch_cpp,
        "dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(",
    )
    claim_begin = function_body(
        dispatch_cpp,
        "claim_and_begin_from_payload_source_or_throw(",
    )
    require(
        ordered(
            dispatch_begin,
            "std::make_unique<detail::SyncReplicaFileTlsDispatchState>",
            "channel_context.emplace(channel.delivery_context())",
            "validate_channel_or_throw",
            "validate_frozen_outbound_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
        ),
        "bounded_freeze_and_canonical_preflight_precede_sqlite_writer",
        "allocation and caller-data validation do not extend the database critical section",
    )
    require(
        ordered(
            dispatch_begin,
            "guard_outbox_claim_for_dispatch_or_throw",
            "validate_channel_or_throw",
            "dispatch_guard->claim()",
            "current_evidence_request !=",
            "dispatch_state->outbound.request.evidence_request",
            "begin_sync_replica_tls_record_write_or_throw",
        ),
        "guarded_frontier_reattests_exact_claim_and_live_channel",
        "the prefix cannot be emitted from a stale attempt or stale TLS capability",
    )
    require(
        ordered(
            dispatch_begin,
            "begin_sync_replica_tls_record_write_or_throw",
            "RequireNonblockingSocket",
            "prefix_accepted = true",
            "dispatch_guard->commit_or_throw()",
            "dispatch_guard.reset()",
            "return SyncReplicaFileTlsDispatchContinuation(",
        )
        and "continuation.finish_or_throw()" not in dispatch_begin,
        "sqlite_writer_covers_only_complete_prefix_not_frame_body",
        "the potentially large immutable body is returned to the event-loop owner after SQLite release",
    )
    require(
        ordered(
            dispatch_begin,
            "catch (...) ",
            "dispatch_guard.reset()",
            "if (!prefix_accepted)",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "std::rethrow_exception(original)",
        )
        or ordered(
            dispatch_begin,
            "catch (...)",
            "dispatch_guard.reset()",
            "if (!prefix_accepted)",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "std::rethrow_exception(original)",
        ),
        "catch_rolls_back_before_exact_pre_prefix_release",
        "an old transaction cannot overlap the separate retry-release transaction",
    )
    require(
        ordered(
            dispatch_wrapper,
            "begin_sync_replica_outbound_file_delivery_over_tls_or_throw",
            "continuation.finish_or_throw()",
        )
        and ordered(
            claim_begin,
            "service.claim_next_request_or_throw",
            "begin_sync_replica_outbound_file_delivery_over_tls_or_throw",
            "std::optional<SyncReplicaFileTlsDispatchContinuation>",
        ),
        "blocking_and_nonblocking_convenience_paths_share_one_guarded_prefix_owner",
        "the compatibility adapter and event-loop claim path cannot drift in SQLite/TLS composition",
    )
    require(
        all(
            token not in (dispatch_begin + dispatch_wrapper + claim_begin).lower()
            for token in ("settle_outbox", "apply_receipt", "receive_request")
        ),
        "dispatch_does_not_overclaim_receipt_admission_or_effect",
        "TLS write progress cannot retire durable sender intent",
    )
    require(
        all(
            phrase in dispatch_h
            for phrase in (
                "Deadline expiry therefore preserves both durable attempt identity",
                "it never releases or settles the outbox claim",
                "Failure after prefix acceptance is ambiguous",
                "ordinary nonblocking WANT is retained",
                "New bounded event-loop code should retain",
                "authenticated terminal",
            )
        ),
        "public_contract_names_transport_progress_and_bounded_readiness",
        "the API does not disguise local TLS progress as remote authority",
    )
    require(
        all(
            phrase in owner_h
            for phrase in (
                "not a general network-I/O transaction",
                "fixed-size first-prefix write",
                "nonblocking TLS read/write readiness",
                "must never cover the",
                "payload body",
                "without pretending the peer",
            )
        ),
        "sqlite_guard_contract_limits_network_scope",
        "future callers are warned against holding the sole writer across payload transfer",
    )

    require(
        all(
            token in runtime
            for token in (
                "SyncReplicaTlsRecordWriteContinuation",
                "TLS overlapping continuation",
                "TLS generic write during continuation",
                "TLS read during continuation",
                "TLS abandoned continuation reuse",
                "TLS foreign-thread continuation abandonment",
                "spawn_inherited_test_process_or_throw",
                "std::thread foreign_thread",
                "kSyncProcessCapabilityViolationExitCode",
                "file TLS stale attempt dispatch",
                "file TLS blocking policy dispatch",
                "TLS non-socket descriptor policy",
                "BIO changed after authentication",
                "TLS write descriptor ABA",
                "TLS write BIO replacement frontier",
                "TLS poll target descriptor ABA",
                "TLS caller-managed poll target",
                "TLS read descriptor ABA",
                "file TLS tampered preflight",
                "file TLS prefix failure dispatch",
                "file TLS post-prefix abandonment",
                "file TLS renewed attempt dispatch",
                "SyncReplicaFileTlsDispatchContinuation",
                "claim_and_begin_next_file_delivery_over_tls_or_throw",
                "file TLS pre-WANT composite poll",
                "file TLS expired composite poll",
                "file TLS resumable cooperative transfer",
            )
        ),
        "runtime_matrix_names_affinity_exclusivity_preflight_and_failure_frontiers",
        "compiled tests exercise ordinary and no-throw owner violations that lexical checks cannot prove",
    )
    require(
        "make_socket_nonblocking_with_small_send_buffer" in runtime
        and "2U * 1024U * 1024U" in runtime
        and "SyncReplicaOutboxRetryReleaseProvenance::None" in runtime,
        "runtime_forces_body_backpressure_and_checks_claim_provenance",
        "post-prefix ambiguity is observed rather than inferred from a closed peer alone",
    )
    require(
        all(
            token in runtime
            for token in (
                "TempFileDeliveryWorkspace",
                "SyncReplicaFileEffectSqliteOwner effect",
                "SyncReplicaFileEffectMaterializeResult::Published",
                "receiver_effect_cutpoint_digest",
                "file TLS resumable terminal receipt write",
                "SyncReplicaFileDeliveryReceiptApplyResult::",
                "EffectSettled",
                "settled_sender.outbox.empty()",
            )
        ),
        "runtime_composes_backpressure_publication_receipt_and_settlement",
        "the focused matrix crosses two replica owners, one effect owner, real TLS, and a terminal receipt",
    )
    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 882",
                "revision_number >= 883",
                "revision_number >= 885",
                "src/sync_replica_file_tls_dispatch.hpp",
                "src/sync_replica_file_tls_dispatch.cpp",
                "tools/audit_sync_file_tls_dispatch.py",
                "TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md",
                "TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md",
                "src/sync_socket_readiness_identity.hpp",
                "src/sync_socket_readiness_identity.cpp",
                "tests/sync_socket_readiness_identity_test.cpp",
                "tools/audit_sync_socket_readiness_identity.py",
                "TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md",
                "revision_number >= 887",
                "TLS_FILE_DISPATCH_CONTINUATION_AUDIT_rev0887.md",
            )
        ),
        "release_verifier_requires_dispatch_affinity_and_lifetime_surface",
        "a handoff cannot omit the first-prefix owner or its socket-lifetime proof",
    )
    require(
        all(
            token in design
            for token in (
                "OpenSSL SSL_write",
                "BEGIN IMMEDIATE",
                "Failure matrix",
                "Peer receipt is not claimed",
                "same-thread overlap",
                "nonblocking readiness",
                "body can cross lease expiry",
            )
        ),
        "design_record_covers_sources_failure_matrix_and_nonclaims",
        "the revision explains both the correction and its remaining hazards",
    )
    require(
        all(
            token in affinity_design
            for token in (
                "OpenSSL thread safety",
                "SSL_free",
                "Failure matrix",
                "foreign-thread destructor",
                "Rejected receive prototype",
                "578-line",
                "ThreadSanitizer is not claimed",
                "receiver loop remains missing",
            )
        ),
        "affinity_design_records_sources_failure_matrix_scope_rejection_and_nonclaims",
        "the correction, rejected speculative branch, and remaining production gap stay reviewable",
    )
    require(
        all(
            token in lifetime_design
            for token in (
                "Descriptor-number ABA",
                "SO_COOKIE",
                "Strict write frontier",
                "Failure matrix",
                "Unsupported platforms fail closed",
                "does not claim",
            )
        )
        and "reproof rejects close/dup2 descriptor ABA" in socket_runtime,
        "lifetime_design_and_generic_runtime_bind_first_prefix_body_socket",
        "the dispatch cutpoint retains exact kernel-object rationale and executable evidence",
    )
    require(
        all(
            token in dispatch_design
            for token in (
                "Severe composition defect",
                "SyncReplicaFileTlsDispatchContinuation",
                "claim_and_begin_next_file_delivery_over_tls_or_throw",
                "Failure matrix",
                "Frame memory amplification",
                "No production session owner yet",
                "Receipt path still uses the synchronous adapter",
                "does not claim",
            )
        )
        and all(
            source in dispatch_design
            for source in (
                "https://docs.openssl.org/3.5/man3/SSL_write/",
                "https://docs.openssl.org/3.5/man3/SSL_get_error/",
                "https://man7.org/linux/man-pages/man2/poll.2.html",
                "https://docs.openssl.org/3.5/man3/SSL_shutdown/",
            )
        ),
        "rev0887_design_records_primary_sources_failure_matrix_waste_and_nonclaims",
        "the correction and its remaining production/memory hazards stay reviewable",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "does not prove" in self_text,
        "audit_disclaims_semantic_authority",
        "source vocabulary cannot substitute for compiled and crash evidence",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
