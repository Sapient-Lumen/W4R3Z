#!/usr/bin/env python3
"""Lexical hygiene audit for the incremental TLS write continuation.

This audit inventories review-critical source shape only. It does not prove
OpenSSL retry semantics, pointer stability, kernel socket identity, scheduling,
peer receipt, or end-to-end delivery. Compiled negative tests, sanitizers,
stress runs, and manual review remain authoritative.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_replica_file_tls_dispatch.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_tls_write_continuation.py"),
    Path("tools/audit_sync_file_tls_dispatch.py"),
    Path("tools/verify_release_package.py"),
    Path("TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md"),
    Path("TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md"),
    Path("REVISION_NOTES_rev0886.md"),
    Path("TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md"),
    Path("REVISION_NOTES_rev0888.md"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def ordered(text: str, *tokens: str) -> bool:
    cursor = 0
    for token in tokens:
        cursor = text.find(token, cursor)
        if cursor < 0:
            return False
        cursor += len(token)
    return True


def delimited_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
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
        "format": "anonsync-sync-tls-write-continuation-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove OpenSSL retry semantics, "
            "buffer identity, socket identity, peer receipt, or delivery"
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
    readme = text["README.md"]
    header = text["src/sync_replica_tls_transport.hpp"]
    source = text["src/sync_replica_tls_transport.cpp"]
    dispatch = text["src/sync_replica_file_tls_dispatch.cpp"]
    dispatch_begin = delimited_body(
        dispatch,
        "begin_sync_replica_outbound_file_delivery_over_tls_or_throw(",
    )
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    legacy_design = text["TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md"]
    design = text["TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md"]
    anchor_design = text["TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md"]
    notes = text["REVISION_NOTES_rev0888.md"]
    self_text = text["tools/audit_sync_tls_write_continuation.py"]

    continuation = delimited_body(
        header, "class SyncReplicaTlsRecordWriteContinuation final"
    )
    require(
        continuation.count("= delete") >= 2
        and continuation.count("&& other) noexcept") >= 1
        and "~SyncReplicaTlsRecordWriteContinuation() noexcept" in continuation
        and "std::unique_ptr<detail::SyncReplicaTlsRecordWriteState> state_"
        in continuation,
        "public_writer_is_move_only_noexcept_and_pimpl_owned",
        "moving the public value transfers one heap identity instead of relocating a pending write buffer",
    )
    require(
        all(
            token in header
            for token in (
                "enum class SyncReplicaTlsRecordWriteProgress",
                "Progress",
                "WantRead",
                "WantWrite",
                "Complete",
                "kSyncReplicaTlsRecordWriteStepBytes",
                "io_started() const noexcept",
                "prefix_bytes_written() const noexcept",
                "prefix_complete() const noexcept",
                "body_bytes_written() const noexcept",
                "pending_readiness_or_throw() const",
                "prepare_sync_replica_tls_record_write_or_throw",
            )
        ),
        "public_api_exposes_bounded_typed_write_progress",
        "event loops can distinguish ordinary progress, exact WANT direction, and completion",
    )
    normalized_header = " ".join(header.split())
    require(
        all(
            phrase in normalized_header
            for phrase in (
                "exact prefix and frame bytes are copied into heap-stable private state",
                "cannot substitute a different length or same-length body",
                "Each advance performs at",
                "most one bounded prefix or body write request",
                "Destroying an untouched prepared owner releases its reservation",
                "after any write attempt permanently poisons the",
            )
        ),
        "public_contract_names_owned_bytes_retry_and_abandonment",
        "callers are warned that first attempt, not merely accepted bytes, transfers pending OpenSSL authority",
    )

    state = delimited_body(source, "class detail::SyncReplicaTlsRecordWriteState final")
    require(
        all(
            token in state
            for token in (
                "std::shared_ptr<SyncReplicaTlsAuthenticatedState> authenticated_state",
                "std::string frame",
                "std::array<unsigned char, kSyncReplicaTlsRecordPrefixBytes> prefix",
                "std::size_t prefix_offset",
                "std::size_t body_offset",
                "std::size_t pending_offset",
                "std::size_t pending_bytes",
                "bool pending_prefix",
                "bool reservation_active",
                "bool io_started",
                "bool retry_pending",
                "SyncReplicaTlsPendingReadiness pending_readiness",
                "~SyncReplicaTlsRecordWriteState() noexcept",
                "abandon_noexcept();",
            )
        ),
        "private_state_owns_exact_prefix_body_and_retry_cutpoint",
        "one heap object retains both byte domains, offsets, attempt state, reservation, and pending readiness",
    )
    require(
        ordered(
            state,
            "void abandon_noexcept() noexcept",
            "abandon_record_write_noexcept(io_started)",
            "reservation_active = false",
            "authenticated_state.reset()",
        ),
        "state_destruction_distinguishes_untouched_from_attempted_write",
        "idle preparation releases cleanly while any attempted OpenSSL operation fails closed",
    )

    abandon_write = delimited_body(
        source, "void abandon_record_write_noexcept(bool io_started) const noexcept"
    )
    require(
        ordered(
            abandon_write,
            "require_owner_or_fail_stop_noexcept()",
            "record_reservation_ != SyncReplicaTlsRecordReservation::Write",
            "poisoned_ = true",
            "return",
            "if (io_started) poisoned_ = true",
            "record_reservation_ = SyncReplicaTlsRecordReservation::Idle",
        ),
        "authenticated_owner_releases_only_untouched_preparation_cleanly",
        "reservation mismatch and every attempted write poison, while a truthful zero-attempt preparation returns to idle",
    )

    prepare = delimited_body(
        source,
        "prepare_sync_replica_tls_record_write_or_throw(\n    const SyncReplicaTlsAuthenticatedChannel& channel,\n    std::string_view frame,\n    std::uint64_t max_frame_bytes,\n    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy",
    )
    require(
        ordered(
            prepare,
            "validate_record_limit_or_throw(max_frame_bytes, label)",
            "checked_size_to_u64_or_throw",
            "frame_bytes == 0U",
            "frame_bytes > max_frame_bytes",
            "std::string owned_frame(frame)",
            "std::make_unique<detail::SyncReplicaTlsRecordWriteState>",
            "begin_record_write_or_throw",
            "reservation_active = true",
            "SyncReplicaTlsRecordWriteContinuation(std::move(write_state))",
        ),
        "bounds_copy_state_and_reservation_are_correctly_ordered",
        "oversize input cannot force a duplicate allocation and all local setup precedes the first prefix operation",
    )
    require(
        "SSL_write_ex(" not in prepare
        and "advance_or_throw()" not in prepare
        and "reservation_active = true" in prepare,
        "prepare_returns_before_first_openssl_write",
        "event-loop ownership can exist without inventing prefix progress or hidden blocking work",
    )

    begin = delimited_body(
        source,
        "begin_sync_replica_tls_record_write_or_throw(\n    const SyncReplicaTlsAuthenticatedChannel& channel,\n    std::string_view frame,\n    std::uint64_t max_frame_bytes,\n    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy",
    )
    require(
        ordered(
            begin,
            "prepare_sync_replica_tls_record_write_or_throw(",
            "continuation.advance_or_throw()",
            "continuation.prefix_complete()",
            "return continuation",
            "SyncReplicaTlsRecordWriteProgress::WantRead",
            "SyncReplicaTlsRecordWriteProgress::WantWrite",
            "length prefix reached nonblocking TLS readiness loss",
        ),
        "legacy_begin_drives_only_to_complete_prefix",
        "guarded dispatch keeps its accepted-prefix API while the shared state owns pre-prefix WANT",
    )

    advance = delimited_body(
        source, "SyncReplicaTlsRecordWriteContinuation::advance_or_throw()"
    )
    require(
        ordered(
            advance,
            "const bool writing_prefix",
            "const std::size_t current_offset",
            "const std::size_t current_bytes",
            "if (!state_->retry_pending)",
            "state_->pending_prefix = writing_prefix",
            "state_->pending_offset = current_offset",
            "state_->pending_bytes = std::min(",
            "kSyncReplicaTlsRecordWriteStepBytes",
        ),
        "fresh_prefix_or_body_step_is_bounded_and_records_exact_arguments",
        "one event-loop advance requests no more than the public 64 KiB budget in either byte domain",
    )
    require(
        all(
            token in advance
            for token in (
                "state_->pending_bytes == 0U",
                "state_->pending_prefix != writing_prefix",
                "state_->pending_offset != current_offset",
                "state_->pending_offset > current_bytes",
                "current_bytes - state_->pending_offset",
            )
        ),
        "retry_state_is_phase_and_range_checked_before_openssl",
        "corrupt phase or offsets cannot be converted into an out-of-bounds prefix/body retry pointer",
    )
    require(
        ordered(
            advance,
            "active_record_io_or_throw(",
            "SyncReplicaTlsRecordReservation::Write",
            "state_->retry_pending",
            "const void* const input",
            "state_->prefix.data() + state_->pending_offset",
            "state_->frame.data() + state_->pending_offset",
            "state_->io_started = true",
            "ERR_clear_error()",
            "SSL_write_ex(",
            "SSL_get_error(ssl, result)",
        ),
        "write_retry_uses_owned_phase_pointer_and_immediate_error_classification",
        "the exact pending prefix/body pointer and length reach OpenSSL and no OpenSSL call interposes before SSL_get_error",
    )
    require(
        ordered(
            advance,
            "ssl_error == SSL_ERROR_WANT_READ",
            "state_->retry_pending = true",
            "SyncReplicaTlsPendingReadiness::Readable",
            "SyncReplicaTlsRecordWriteProgress::WantRead",
            "ssl_error == SSL_ERROR_WANT_WRITE",
            "SyncReplicaTlsPendingReadiness::Writable",
            "SyncReplicaTlsRecordWriteProgress::WantWrite",
        ),
        "want_read_and_want_write_preserve_exact_retry_state",
        "both OpenSSL readiness directions retain the exact prefix/body operation without advancing its cutpoint",
    )
    require(
        ordered(
            advance,
            "state_->retry_pending = false",
            "state_->pending_readiness =",
            "SyncReplicaTlsPendingReadiness::None",
            "bytes_written == 0U || bytes_written > state_->pending_bytes",
            "if (state_->pending_prefix)",
            "state_->prefix_offset += bytes_written",
            "else",
            "state_->body_offset += bytes_written",
            "state_->pending_offset = 0U",
            "state_->pending_bytes = 0U",
        ),
        "successful_partial_write_advances_only_its_owned_phase",
        "SSL_MODE_ENABLE_PARTIAL_WRITE is compatible without confusing prefix, body, success, or WANT",
    )
    require(
        ordered(
            advance,
            "if (state_->pending_prefix)",
            "SyncReplicaTlsRecordWriteProgress::Progress",
            "state_->body_offset != state_->frame.size()",
            "SyncReplicaTlsRecordWriteProgress::Progress",
            "complete_record_write_noexcept()",
            "reservation_active = false",
            "state_.reset()",
            "SyncReplicaTlsRecordWriteProgress::Complete",
        ),
        "prefix_frontier_is_observable_before_body_and_completion_releases_once",
        "guarded callers can commit at exact prefix completion and no hidden body operation occurs in that advance",
    )
    require(
        ordered(advance, "catch (...)", "state_->abandon_noexcept()", "throw;"),
        "write_exception_poison_closes_continuation",
        "fatal transport, authority, or internal errors cannot leave the stream reusable",
    )

    pending = delimited_body(
        source,
        "SyncReplicaTlsRecordWriteContinuation::pending_readiness_or_throw() const",
    )
    require(
        ordered(
            pending,
            "if (!state_->require_nonblocking_socket)",
            "caller-managed TLS write has no library-owned poll target",
            "SyncReplicaTlsPendingReadiness::None",
            "TLS record write has no pending readiness request",
            "try",
            "pending_readiness_target_or_throw",
        ),
        "optional_target_queries_reject_without_poison_before_system_reproof",
        "a harmless no-WANT or caller-managed query cannot destroy a valid continuation",
    )
    require(
        ordered(
            pending,
            "pending_readiness_target_or_throw",
            "SyncReplicaTlsRecordReservation::Write",
            "catch (...)",
            "state_->abandon_noexcept()",
        ),
        "stale_pending_target_abandons_ambiguous_stream",
        "descriptor or policy contradiction after WANT cannot expose reusable authority",
    )

    finish = delimited_body(
        source, "void SyncReplicaTlsRecordWriteContinuation::finish_or_throw()"
    )
    require(
        ordered(
            finish,
            "for (;;)",
            "advance_or_throw()",
            "SyncReplicaTlsRecordWriteProgress::Progress",
            "continue",
            "SyncReplicaTlsRecordWriteProgress::Complete",
            "return",
            "SyncReplicaTlsRecordWriteProgress::WantRead",
            "SyncReplicaTlsRecordWriteProgress::WantWrite",
            "reached nonblocking TLS readiness loss",
        ),
        "blocking_adapter_delegates_but_does_not_spin_on_want",
        "legacy synchronous callers preserve fail-closed semantics while event loops use advance_or_throw",
    )
    require(
        ordered(finish, "catch (...)", "if (state_)", "abandon_noexcept()", "throw;"),
        "blocking_adapter_poison_is_idempotent",
        "WANT or fatal failure cannot leak an accepted-prefix continuation",
    )

    wrapper = delimited_body(source, "void write_sync_replica_tls_record_or_throw(")
    require(
        ordered(
            wrapper,
            "begin_sync_replica_tls_record_write_or_throw",
            "continuation.finish_or_throw()",
        ),
        "one_shot_writer_delegates_to_incremental_owner",
        "there is no second body-write implementation with divergent retry semantics",
    )

    require(
        ordered(
            dispatch_begin,
            "guard_outbox_claim_for_dispatch_or_throw",
            "begin_sync_replica_tls_record_write_or_throw(",
            "dispatch_state->outbound.request_frame",
            "prefix_accepted = true",
            "dispatch_guard->commit_or_throw()",
            "dispatch_guard.reset()",
            "return SyncReplicaFileTlsDispatchContinuation(",
        ),
        "file_dispatch_keeps_claim_guard_through_prefix_then_releases_before_body",
        "durable attempt authority crosses the exact prefix frontier before large I/O",
    )
    require(
        ordered(
            dispatch_begin,
            "catch (...)",
            "dispatch_guard.reset()",
            "if (!prefix_accepted)",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "std::rethrow_exception(original)",
        ),
        "file_dispatch_preserves_pre_prefix_release_and_post_prefix_ambiguity",
        "retry authority is exact only before the encrypted length prefix succeeds",
    )

    runtime_tokens = (
        "TLS prepared prefix ownership",
        "untouched TLS preparation emitted ciphertext",
        "TLS first-prefix WANT",
        "first-prefix backpressure was not retained as an exact WANT_WRITE",
        "TLS continuation exact byte ownership",
        "caller mutation substituted bytes after TLS prefix acceptance",
        "TLS incremental write resume",
        "fresh TLS writer invented an event-loop target before WANT",
        "moving TLS writer duplicated, lost, or retargeted the pending operation",
        "one TLS write step exceeded the public body budget",
        "TLS caller-managed write target",
        "TLS pending write descriptor ABA",
        "TLS pending write nonblocking reproof",
        "TLS write BIO replacement frontier",
        "TLS continuation abandonment",
        "file TLS receiver receipt-prefix WANT",
    )
    require(
        all(token in runtime for token in runtime_tokens)
        and "make_socket_nonblocking_with_small_send_buffer" in runtime,
        "compiled_runtime_covers_ownership_backpressure_move_and_stale_authority",
        "real TLS 1.3 sockets exercise failures that lexical shape cannot prove",
    )
    require(
        "max_body_step <= anonsync::kSyncReplicaTlsRecordWriteStepBytes" in runtime
        and "received.has_value() && *received == frame" in runtime,
        "runtime_checks_bounded_progress_and_exact_peer_bytes",
        "the resumable path is observed end-to-end across actual backpressure",
    )

    require(
        cmake.count("anonsync_sync_tls_write_continuation_source_audit") >= 2
        and "tools/audit_sync_tls_write_continuation.py" in cmake,
        "audit_is_registered_in_ctest",
        "ordinary registered and audit-only gates include this writer inventory",
    )
    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 888",
                "tools/audit_sync_tls_write_continuation.py",
                "TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md",
                "REVISION_NOTES_rev0888.md",
            )
        ),
        "release_verifier_requires_prefix_writer_audit_surface",
        "a rev0888 handoff cannot omit the shared prefix/body writer rationale, audit, or notes",
    )
    require(
        all(
            token in design
            for token in (
                "SSL_write_ex",
                "same arguments",
                "64 KiB",
                "Authority invariant",
                "Failure matrix",
                "Rejected alternatives",
                "does not claim",
            )
        )
        and "prefix" in readme.lower()
        and "resumable" in notes.lower()
        and "SSL_write_ex" in legacy_design
        and "TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md" in anchor_design,
        "design_revision_and_readme_name_prefix_writer_rationale_and_nonclaims",
        "authority reasoning and compatibility lineage travel with the implementation rather than living only in code",
    )
    require(
        "does not prove" in self_text
        and "Compiled negative tests" in self_text,
        "audit_disclaims_semantic_authority",
        "substring presence is not represented as transport correctness",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    sys.exit(main())
