#!/usr/bin/env python3
"""Lexical hygiene audit for the incremental TLS receive continuation.

This audit is intentionally an inventory of reviewed source shape. It does not
prove OpenSSL behavior, kernel readiness, scheduler behavior, heap stability at
runtime, transport security, peer identity, or crash recovery. Compiled tests,
sanitisers, stress runs, and manual review remain authoritative.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_socket_readiness_identity.hpp"),
    Path("src/sync_socket_readiness_identity.cpp"),
    Path("tests/sync_socket_readiness_identity_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_tls_receive_continuation.py"),
    Path("tools/verify_release_package.py"),
    Path("TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md"),
    Path("TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md"),
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


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-tls-receive-continuation-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove OpenSSL retry semantics, "
            "pointer stability, socket identity, peer behavior, or concurrency"
        ),
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
    header = text["src/sync_replica_tls_transport.hpp"]
    source = text["src/sync_replica_tls_transport.cpp"]
    socket_header = text["src/sync_socket_readiness_identity.hpp"]
    socket_source = text["src/sync_socket_readiness_identity.cpp"]
    socket_runtime = text["tests/sync_socket_readiness_identity_test.cpp"]
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    design = text["TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md"]
    lifetime_design = text["TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md"]
    self_text = text["tools/audit_sync_tls_receive_continuation.py"]

    continuation = class_body(
        header, "class SyncReplicaTlsRecordReadContinuation final"
    )
    require(
        continuation.count("= delete") >= 2
        and "&& other) noexcept" in continuation
        and "operator=(" in continuation
        and "~SyncReplicaTlsRecordReadContinuation() noexcept" in continuation
        and "std::unique_ptr<detail::SyncReplicaTlsRecordReadState> state_"
        in continuation,
        "public_reader_is_move_only_noexcept_and_pimpl_owned",
        "moving the public value transfers one heap identity instead of relocating retry buffers",
    )
    normalized_header = " ".join(header.split())
    require(
        all(
            phrase in normalized_header
            for phrase in (
                "heap-stable private state",
                "exact buffer pointer or length",
                "Each advance performs at most one SSL read",
                "Abandonment after any attempted read",
                "PeerClosed terminal state",
                "Foreign-process or foreign-thread cleanup fails stopped",
            )
        ),
        "public_contract_names_retry_cleanup_and_close_frontiers",
        "the event-loop obligations and fail-closed boundaries are explicit API contract",
    )

    read_state = class_body(
        source, "class detail::SyncReplicaTlsRecordReadState final"
    )
    require(
        all(
            token in read_state
            for token in (
                "std::array<unsigned char, kSyncReplicaTlsRecordPrefixBytes> prefix",
                "std::string frame",
                "std::size_t prefix_offset",
                "std::size_t body_offset",
                "bool reservation_active",
                "bool io_started",
                "bool retry_pending",
                "PendingReadiness pending_readiness",
                "Terminal terminal",
                "~SyncReplicaTlsRecordReadState()",
                "abandon_noexcept()",
            )
        ),
        "heap_state_owns_buffers_offsets_and_cleanup",
        "every retry argument and cleanup decision remains attached to one allocation",
    )

    authenticated = class_body(
        source, "class detail::SyncReplicaTlsAuthenticatedState final"
    )
    require(
        all(
            token in source
            for token in (
                "enum class SyncReplicaTlsRecordReservation",
                "Idle",
                "Read",
                "Write",
            )
        )
        and all(
            token in authenticated
            for token in (
                "record_reservation_",
                "begin_record_read_or_throw",
                "active_record_io_or_throw",
                "require_record_owner_or_throw",
                "complete_record_read_noexcept",
                "abandon_record_read_noexcept",
                "close_record_read_noexcept",
                "begin_record_write_or_throw",
                "complete_record_write_noexcept",
                "require_record_idle_or_throw",
            )
        ),
        "authenticated_state_owns_one_duplex_record_reservation",
        "read, write, and delivery verifier entry cannot concurrently operate one SSL object",
    )
    validate = function_body(source, "void validate_or_throw(")
    require(
        ordered(
            validate,
            "require_current_or_throw(label)",
            "require_usable_or_throw(label)",
            "require_record_idle_or_throw(label)",
            "validate_authenticated_channel_and_poison_or_throw(label)",
        ),
        "delivery_verifier_rejects_active_record_before_openssl_reentry",
        "durable service validation cannot interpose certificate/exporter calls during pending I/O",
    )

    begin = function_body(
        source, "begin_sync_replica_tls_record_read_or_throw("
    )
    require(
        ordered(
            begin,
            "validate_record_limit_or_throw",
            "SyncReplicaTlsRecordReadReadinessPolicy::RequireNonblockingSocket",
            "std::make_unique<detail::SyncReplicaTlsRecordReadState>",
            "begin_record_read_or_throw",
            "reservation_active = true",
            "SyncReplicaTlsRecordReadContinuation(std::move(read_state))",
        ),
        "throwing_construction_precedes_read_reservation",
        "allocation and diagnostics cannot fail after the channel has been reserved",
    )

    active = function_body(source, "SSL* active_record_io_or_throw(")
    require(
        ordered(
            active,
            "require_record_owner_or_throw(expected, label)",
            "if (retry_pending)",
            "if (require_nonblocking_socket)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "else",
            "validate_transport_anchor_and_poison_or_throw(label)",
            "return ssl_",
            "validate_authenticated_channel_and_poison_or_throw(label)",
            "if (require_nonblocking_socket)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
        ),
        "first_byte_revalidation_and_each_retry_readiness_are_separate",
        "a fresh operation is fully re-attested while one pending WANT avoids unrelated session operations",
    )
    require(
        "sync_socket_readiness_identity.hpp" in source
        and "::getsockopt" not in source
        and "::fcntl" not in source
        and "SO_COOKIE" not in source
        and "descriptor number alone is not authority" in socket_header
        and "cannot prove an exact stream-socket lifetime on this platform"
        in socket_source
        and "SyncSocketLifetimeIdentity" in source,
        "receive_path_uses_one_opaque_fail_closed_socket_identity_owner",
        "TLS retry does not duplicate or weaken the Linux lifetime proof",
    )

    advance = function_body(
        source, "SyncReplicaTlsRecordReadContinuation::advance_or_throw()"
    )
    require(
        advance.count("SSL_read_ex(") == 1
        and ordered(
            advance,
            "active_record_io_or_throw",
            "SyncReplicaTlsRecordReservation::Read",
            "state_->io_started = true",
            "ERR_clear_error()",
            "SSL_read_ex(",
            "SSL_get_error(ssl, result)",
        ),
        "advance_issues_one_read_and_immediate_error_classification",
        "one event-loop step cannot hide a blocking read loop and SSL_get_error observes the exact call",
    )
    require(
        ordered(
            advance,
            "SSL_ERROR_WANT_READ",
            "SyncReplicaTlsRecordReadProgress::WantRead",
            "SSL_ERROR_WANT_WRITE",
            "SyncReplicaTlsRecordReadProgress::WantWrite",
            "if (reading_prefix)",
            "state_->prefix_offset += bytes_read",
            "state_->body_offset += bytes_read",
        )
        and "state_->retry_pending" in advance
        and "state_->retry_pending = true" in advance
        and "state_->retry_pending = false" in advance,
        "want_returns_without_mutating_offsets_and_retry_skips_full_reproof",
        "retry reconstructs the same pointer and length from unchanged heap offsets",
    )
    require(
        ordered(
            advance,
            "const std::size_t requested",
            "kSyncReplicaTlsRecordReadStepBytes",
            "SSL_read_ex(",
            "bytes_read > requested",
        )
        and "kSyncReplicaTlsRecordReadStepBytes" in header,
        "each_body_operation_has_a_public_finite_step_budget",
        "one event-loop turn cannot ask OpenSSL to fill an unbounded peer-sized body buffer",
    )
    require(
        ordered(
            advance,
            "state_->prefix_offset += bytes_read",
            "decode_u64_be(state_->prefix)",
            "peer advertised an empty frame",
            "above the configured limit",
            "checked_u64_to_size_or_throw",
            "state_->frame.assign",
            "state_->body_offset += bytes_read",
            "complete_record_read_noexcept",
        ),
        "prefix_is_validated_before_exact_body_allocation",
        "empty, over-limit, and unrepresentable lengths cannot reach a body read",
    )
    require(
        ordered(
            advance,
            "SSL_ERROR_ZERO_RETURN",
            "state_->prefix_offset == 0U",
            "state_->frame_bytes == 0U",
            "state_->body_offset == 0U",
            "close_record_read_noexcept",
            "Terminal::PeerClosed",
            "peer closed TLS before the complete record",
        ),
        "clean_preframe_close_is_distinct_from_truncation",
        "close_notify before bytes closes authority; any framed progress is fail-closed truncation",
    )
    require(
        ordered(
            advance,
            "catch (...)",
            "state_->abandon_noexcept()",
            "throw",
        )
        and ordered(
            function_body(source, "void abandon_record_read_noexcept("),
            "require_owner_or_fail_stop_noexcept()",
            "if (io_started) poisoned_ = true",
            "record_reservation_ = SyncReplicaTlsRecordReservation::Idle",
        ),
        "read_failure_and_abandonment_are_owner_fenced_and_progress_sensitive",
        "pre-I/O cleanup releases cleanly while any attempted operation poisons",
    )

    pending = function_body(
        source,
        "SyncReplicaTlsRecordReadContinuation::pending_readiness_or_throw() const",
    )
    target_owner = function_body(
        source, "pending_readiness_target_or_throw("
    )
    require(
        ordered(
            target_owner,
            "require_record_owner_or_throw(expected, label)",
            "switch (pending)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "return {socket->descriptor(), public_readiness}",
        )
        and ordered(
            pending,
            "SyncReplicaTlsPendingReadiness::None",
            "pending_readiness_target_or_throw",
            "catch (...)",
            "state_->abandon_noexcept()",
        ),
        "poll_target_lookup_reproves_and_abandons_stale_retry",
        "an already recycled descriptor is not disclosed to the event loop",
    )

    wrapper = function_body(
        source, "std::string read_sync_replica_tls_record_or_throw("
    )
    require(
        ordered(
            wrapper,
            "begin_sync_replica_tls_record_read_or_throw",
            "continuation.advance_or_throw",
            "SyncReplicaTlsRecordReadProgress::Complete",
            "continuation.take_frame_or_throw",
            "SyncReplicaTlsRecordReadProgress::WantRead",
            "SyncReplicaTlsRecordReadProgress::WantWrite",
            "nonblocking TLS readiness loss",
        ),
        "legacy_reader_delegates_to_incremental_state_machine",
        "blocking compatibility cannot drift from incremental framing and poisoning semantics",
    )

    require(
        all(
            token in runtime
            for token in (
                "TLS incremental read move after WANT",
                "TLS incremental fragmented record",
                "TLS clean read abandonment",
                "TLS pending read abandonment",
                "TLS duplex read reservation",
                "TLS read readiness reproof",
                "TLS poll target descriptor ABA",
                "TLS caller-managed poll target",
                "TLS read descriptor ABA",
                "TLS fresh-step descriptor ABA",
                "TLS bounded read step",
                "TLS clean peer close before frame",
                "TLS truncated body close",
                "TLS incremental over-limit prefix",
                "TLS read non-socket descriptor policy",
                "TLS foreign-thread read abandonment",
                "TLS legacy read WANT delegation",
            )
        )
        and runtime.count(
            "SyncReplicaTlsRecordReadContinuation>"
        ) >= 5,
        "runtime_matrix_covers_retry_move_duplex_close_bounds_and_affinity",
        "compiled tests exercise the high-risk negative and terminal frontiers",
    )
    require(
        "make_socket_nonblocking" in runtime
        and "make_socket_blocking" in runtime
        and "write_tls_fixture_bytes" in runtime
        and "send_tls_close_notify" in runtime
        and "pending_readiness_or_throw" in runtime
        and "replace_descriptor_lifetime_or_fail" in runtime
        and "spawn_inherited_test_process_or_throw" in runtime,
        "runtime_fixtures_force_readiness_fragmentation_close_and_failstop",
        "the matrix observes actual socket/OpenSSL progress rather than only source vocabulary",
    )

    require(
        cmake.count("anonsync_sync_tls_receive_continuation_source_audit") >= 2
        and "tools/audit_sync_tls_receive_continuation.py" in cmake,
        "audit_is_registered_in_ctest",
        "ordinary release test selection includes this source inventory",
    )
    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 884",
                "revision_number >= 885",
                "tools/audit_sync_tls_receive_continuation.py",
                "TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md",
                "src/sync_socket_readiness_identity.hpp",
                "src/sync_socket_readiness_identity.cpp",
                "tests/sync_socket_readiness_identity_test.cpp",
                "tools/audit_sync_socket_readiness_identity.py",
                "TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md",
            )
        ),
        "release_verifier_requires_rev0884_and_rev0885_receive_surface",
        "a sealed revision cannot omit the continuation or its socket-lifetime proof",
    )
    require(
        all(
            token in design
            for token in (
                "OpenSSL SSL_read",
                "same arguments",
                "SSL_get_error",
                "SSL_pending",
                "Failure matrix",
                "Heap-stable state",
                "PeerClosed",
                "does not claim",
            )
        ),
        "design_record_covers_sources_invariants_failures_and_nonclaims",
        "review rationale and remaining production gaps travel with the code",
    )
    require(
        all(
            token in lifetime_design
            for token in (
                "Descriptor-number ABA",
                "SO_COOKIE",
                "OpenSSL exact retry",
                "Advisory event-loop target",
                "64 KiB",
                "Failure matrix",
                "Unsupported platforms fail closed",
                "Raw descriptor mutation must be serialized",
            )
        )
        and "reproof rejects close/dup2 descriptor ABA" in socket_runtime,
        "rev0885_design_and_generic_runtime_bind_receive_socket_lifetime",
        "the new retry proof has rationale, nonclaims, and an independent compiled matrix",
    )
    require(
        "Lexical hygiene audit" in self_text
        and "does not\nprove" in self_text,
        "audit_disclaims_semantic_authority",
        "the audit cannot represent substring presence as runtime proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
