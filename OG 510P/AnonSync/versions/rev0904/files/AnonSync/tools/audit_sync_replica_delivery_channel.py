#!/usr/bin/env python3
"""Fail-closed structural hygiene audit for authenticated replica delivery.

This audit deliberately proves only source-shape invariants. Runtime authority
comes from the compiled tests, not from substring presence.
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
    Path("src/sync_replica_delivery_channel.cpp"),
    Path("src/sync_replica_delivery_service.hpp"),
    Path("src/sync_replica_delivery_service.cpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_replica_file_tls_dispatch.hpp"),
    Path("src/sync_replica_file_tls_dispatch.cpp"),
    Path("tests/sync_replica_delivery_test_channel.hpp"),
    Path("tests/sync_replica_delivery_test_channel.cpp"),
    Path("tests/sync_replica_delivery_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
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
        "format": "anonsync-sync-replica-delivery-channel-audit-v3",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "lexical source hygiene only; compiled runtime and crash tests remain "
            "the authority for behavior"
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
    channel_h = text["src/sync_replica_delivery_channel.hpp"]
    channel_cpp = text["src/sync_replica_delivery_channel.cpp"]
    service_h = text["src/sync_replica_delivery_service.hpp"]
    service_cpp = text["src/sync_replica_delivery_service.cpp"]
    owner_cpp = text["src/sync_replica_sqlite_owner.cpp"]
    tls_h = text["src/sync_replica_tls_transport.hpp"]
    tls_cpp = text["src/sync_replica_tls_transport.cpp"]
    test_factory_h = text["tests/sync_replica_delivery_test_channel.hpp"]
    service_test = text["tests/sync_replica_delivery_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    service_class_start = service_h.find("class SyncReplicaDeliveryService final")
    service_class_end = service_h.find("\n};", service_class_start)
    service_class = (
        service_h[service_class_start : service_class_end + 3]
        if service_class_start >= 0 and service_class_end >= 0
        else ""
    )

    require(
        all(
            token in channel_h
            for token in (
                "SyncReplicaDeliveryChannelAuthority() = delete",
                "const SyncReplicaDeliveryChannelAuthority&) = delete",
                "SyncReplicaDeliveryChannelAuthority&& other) noexcept",
                "std::shared_ptr<const detail::SyncReplicaDeliveryChannelVerifier>",
            )
        ),
        "authority_is_move_only_and_verifier_backed",
        "descriptive peer/binding bytes are not directly accepted as service authority",
    )
    require(
        "explicit SyncReplicaDeliveryChannelAuthority(" in channel_h
        and channel_h.find("explicit SyncReplicaDeliveryChannelAuthority(")
        > channel_h.find("private:"),
        "authority_mint_is_private",
        "ordinary callers cannot construct authority from public context bytes",
    )
    require(
        all(
            token in channel_h
            for token in (
                "SyncProcessIncarnation owner_process_",
                "SyncThreadIncarnation owner_thread_",
                "bool valid_ = false",
            )
        )
        and ordered(
            function_body(
                channel_cpp,
                "SyncReplicaDeliveryChannelAuthority::require_current_or_throw("),
            "if (!valid_)",
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
            "verifier_->validate_or_throw",
        ),
        "authority_checks_move_process_thread_and_live_transport",
        "service entry validates every local and lower-layer capability dimension",
    )
    require(
        service_class.count("const SyncReplicaDeliveryChannelAuthority&") >= 4
        and "SyncReplicaDeliveryChannelContext" not in service_class,
        "service_surface_requires_authority_not_context",
        "public service methods require opaque authority; the separate canonical builder may consume already-attested context",
    )
    claim = function_body(
        service_cpp, "SyncReplicaDeliveryService::claim_next_request_or_throw(")
    require(
        ordered(
            claim,
            "validate_channel_or_throw",
            "channel_authority.context()",
            "claim_next_outbox_for_delivery_or_throw",
        ),
        "live_channel_validation_precedes_durable_claim",
        "a stale or poisoned transport cannot reach outbox lease mutation",
    )
    owner_claim = function_body(
        owner_cpp, "SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw(")
    require(
        ordered(
            owner_claim,
            "evidence_operation_by_id",
            "validate_sync_replica_operation_or_throw",
            "exceeds delivery wire policy before claim",
            "claim_sync_replica_outbox_lease_or_throw",
            "publish_outbox_lease_update_or_throw",
        ),
        "wire_preflight_precedes_lease_mutation",
        "a locally unsendable first-ready operation cannot enter claim/expiry churn",
    )
    require(
        "class detail::SyncReplicaTlsAuthenticatedState final" in tls_cpp
        and ": public detail::SyncReplicaDeliveryChannelVerifier" in tls_cpp
        and "std::shared_ptr<detail::SyncReplicaTlsAuthenticatedState> state_" in tls_h,
        "tls_state_is_shared_with_service_verifier",
        "record I/O and durable service authority observe one exact session state",
    )
    require(
        ordered(
            function_body(tls_cpp, "SyncReplicaTlsAuthenticatedState("),
            "SSL_up_ref(ssl)",
            "ssl_ = ssl",
        )
        and "SSL_free(std::exchange(ssl_, nullptr))" in tls_cpp,
        "tls_channel_retains_and_releases_ssl_reference",
        "the authenticated capability no longer borrows an externally fragile SSL lifetime",
    )
    validate_tls = function_body(tls_cpp, "void validate_or_throw(")
    validate_live_tls = function_body(
        tls_cpp, "void validate_authenticated_channel_and_poison_or_throw("
    )
    require(
        ordered(
            validate_tls,
            "require_current_or_throw(label)",
            "require_usable_or_throw(label)",
            "require_record_idle_or_throw(label)",
            "validate_authenticated_channel_and_poison_or_throw(label)",
        )
        and ordered(
            validate_live_tls,
            "validate_authenticated_session_or_throw",
            "poisoned_ = true",
        ),
        "tls_verifier_rechecks_live_session_and_poison_state",
        "SPKI/exporter changes invalidate service authority before durable work",
    )
    tls_owner = function_body(tls_cpp, "void require_current_or_throw(")
    require(
        ordered(
            tls_owner,
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        ),
        "tls_state_is_process_and_thread_affine",
        "fork and foreign-thread use are rejected before OpenSSL access",
    )
    prepare_record = function_body(
        tls_cpp, "prepare_sync_replica_tls_record_write_or_throw(")
    begin_record = function_body(
        tls_cpp, "begin_sync_replica_tls_record_write_or_throw(")
    finish_record = function_body(
        tls_cpp, "void SyncReplicaTlsRecordWriteContinuation::finish_or_throw(")
    write_record = function_body(
        tls_cpp, "void write_sync_replica_tls_record_or_throw(")
    advance_write = function_body(
        tls_cpp, "SyncReplicaTlsRecordWriteContinuation::advance_or_throw()"
    )
    write_state = function_body(
        tls_cpp, "class detail::SyncReplicaTlsRecordWriteState final")
    require(
        ordered(
            prepare_record,
            "validate_record_limit_or_throw",
            "frame must not be empty",
            "frame exceeds configured limit",
            "std::string owned_frame(frame)",
            "std::make_unique<detail::SyncReplicaTlsRecordWriteState>",
            "begin_record_write_or_throw",
            "reservation_active = true",
            "SyncReplicaTlsRecordWriteContinuation(std::move(write_state))",
        )
        and "SSL_write_ex(" not in prepare_record
        and ordered(
            advance_write,
            "kSyncReplicaTlsRecordWriteStepBytes",
            "pending_prefix",
            "active_record_io_or_throw",
            "state_->io_started = true",
            "SSL_write_ex",
            "SSL_get_error",
            "SSL_ERROR_WANT_READ",
            "SSL_ERROR_WANT_WRITE",
            "state_->prefix_offset += bytes_written",
            "complete_record_write_noexcept",
            "catch (...)",
            "state_->abandon_noexcept",
        )
        and ordered(
            begin_record,
            "prepare_sync_replica_tls_record_write_or_throw",
            "continuation.advance_or_throw",
            "continuation.prefix_complete()",
            "length prefix reached nonblocking TLS readiness loss",
        )
        and ordered(
            write_state,
            "~SyncReplicaTlsRecordWriteState() noexcept",
            "abandon_noexcept()",
            "abandon_record_write_noexcept(io_started)",
        )
        and ordered(
            finish_record,
            "advance_or_throw",
            "SyncReplicaTlsRecordWriteProgress::WantRead",
            "reached nonblocking TLS readiness loss",
            "state_->abandon_noexcept",
        )
        and ordered(
            write_record,
            "begin_sync_replica_tls_record_write_or_throw",
            "continuation.finish_or_throw()",
        ),
        "write_validates_local_shape_before_io_and_poisons_uncertain_cutpoint",
        "bounded frozen prefix/body state precedes I/O; one continuation owns every exact WANT and progress cutpoint",
    )
    begin_read = function_body(
        tls_cpp, "begin_sync_replica_tls_record_read_or_throw(")
    advance_read = function_body(
        tls_cpp, "SyncReplicaTlsRecordReadContinuation::advance_or_throw(")
    read_record = function_body(
        tls_cpp, "std::string read_sync_replica_tls_record_or_throw(")
    require(
        ordered(
            begin_read,
            "validate_record_limit_or_throw",
            "std::make_unique<detail::SyncReplicaTlsRecordReadState>",
            "begin_record_read_or_throw",
            "reservation_active = true",
        )
        and ordered(
            advance_read,
            "active_record_io_or_throw",
            "SyncReplicaTlsRecordReservation::Read",
            "ERR_clear_error()",
            "SSL_read_ex",
            "SSL_get_error",
            "SSL_ERROR_WANT_READ",
            "SSL_ERROR_WANT_WRITE",
            "peer advertised an empty frame",
            "above the configured limit",
            "complete_record_read_noexcept",
            "catch (...)",
            "abandon_noexcept",
        )
        and ordered(
            read_record,
            "begin_sync_replica_tls_record_read_or_throw",
            "continuation.advance_or_throw",
            "continuation.take_frame_or_throw",
        ),
        "read_uses_one_resumable_fail_closed_state_machine",
        "incremental and blocking adapters share exact framing, WANT, bounds, completion, and abandonment semantics",
    )
    require(
        "SyncReplicaDeliveryTestChannelFactory" in test_factory_h
        and "Separately linked deterministic authority mint" in test_factory_h,
        "test_authority_mint_is_explicitly_separate",
        "unit tests can model authenticated channels without weakening production constructors",
    )
    service_block = target_block(cmake, "anonsync_sync_replica_delivery_service")
    tls_block = target_block(cmake, "anonsync_sync_replica_tls_transport")
    test_block = target_block(cmake, "anonsync_sync_replica_delivery_service_test")
    require(
        "anonsync_sync_replica_delivery_test_channel" not in service_block
        and "anonsync_sync_replica_delivery_test_channel" not in tls_block
        and "anonsync_sync_replica_delivery_test_channel" in test_block,
        "test_mint_is_not_linked_into_production_libraries",
        "the deterministic bypass is confined to the service-test target",
    )
    require(
        all(
            token in service_test
            for token in (
                "!std::is_default_constructible_v<DeliveryAuthority>",
                "!std::is_copy_constructible_v<DeliveryAuthority>",
                "test_wire_policy_preflight_preserves_unclaimed_intent",
                "after_rejection == before",
                "dispatch_attempts == 0U",
            )
        ),
        "runtime_covers_opaque_authority_and_preclaim_rollback",
        "compiled tests prove type shape and exact no-mutation rejection",
    )
    require(
        all(
            token in tls_test
            for token in (
                "TLS foreign-thread capability use",
                "kSyncProcessCapabilityViolationExitCode",
                "retained.client.reset()",
                "TLS channel borrowed a caller-owned SSL lifetime",
                "stale TLS authority changed the sender cutpoint or lease",
                "over-limit peer frame left the TLS byte stream reusable",
            )
        ),
        "runtime_covers_lifetime_affinity_liveness_and_poisoning",
        "compiled integration tests exercise the high-risk negative matrix",
    )
    require(
        "anonsync_sync_replica_delivery_channel_source_audit" in cmake,
        "audit_is_registered_in_ctest",
        "future package validation runs this hygiene check through the normal registry",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
