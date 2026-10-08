#!/usr/bin/env python3
"""Lexical hygiene audit for the accepted TLS file-session owner.

This inventory checks that reviewed lifetime, socket, membership, and cutpoint
vocabulary remains present and ordered. It deliberately does not claim to prove
kernel descriptor identity, OpenSSL behavior, race freedom, timeout enforcement,
SQLite durability, membership freshness, or peer authentication. Compiled
adversarial tests and independent compiler/sanitizer lanes carry those semantic
obligations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def body(text: str, marker: str) -> str:
    start = text.find(marker)
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


def ordered(text: str, *tokens: str) -> bool:
    position = 0
    for token in tokens:
        position = text.find(token, position)
        if position < 0:
            return False
        position += len(token)
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = {
        "header": root / "src/sync_replica_file_tls_server.hpp",
        "source": root / "src/sync_replica_file_tls_server.cpp",
        "membership_header": root / "src/sync_replica_tls_membership_sqlite_owner.hpp",
        "poll_header": root / "src/sync_stream_socket_deadline_poll.hpp",
        "poll_source": root / "src/sync_stream_socket_deadline_poll.cpp",
        "socket_header": root / "src/sync_socket_readiness_identity.hpp",
        "socket_source": root / "src/sync_socket_readiness_identity.cpp",
        "runtime": root / "tests/sync_replica_tls_transport_test.cpp",
        "socket_runtime": root / "tests/sync_socket_readiness_identity_test.cpp",
        "cmake": root / "CMakeLists.txt",
        "verifier": root / "tools/verify_release_package.py",
    }
    missing = sorted(str(path.relative_to(root)) for path in paths.values() if not path.is_file())
    text = {name: path.read_text(encoding="utf-8") if path.is_file() else "" for name, path in paths.items()}
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    require(not missing, "required_files_exist", f"missing={missing}")
    header = text["header"]
    source = text["source"]
    membership_header = text["membership_header"]
    poll_header = text["poll_header"]
    poll_source = text["poll_source"]
    socket_header = text["socket_header"]
    socket_source = text["socket_source"]
    runtime = text["runtime"]
    socket_runtime = text["socket_runtime"]
    cmake = text["cmake"]
    verifier = text["verifier"]

    context = body(header, "class SyncReplicaFileTlsServerContext final")
    require(
        bool(context)
        and "const SyncReplicaFileTlsServerContext&) = delete" in context
        and "SyncReplicaFileTlsServerContext&& other) noexcept" in context
        and "SSL_CTX* context_ = nullptr" in context
        and "retain_sync_replica_file_tls_server_context_or_throw" in context,
        "server_context_is_move_only_retained_reference",
        "raw SSL_CTX lifetime cannot be delegated to one untracked call",
    )
    retain = body(source, "retain_sync_replica_file_tls_server_context_or_throw(")
    require(
        ordered(retain, "context == nullptr", "ERR_clear_error()", "SSL_CTX_up_ref(context)", "SyncReplicaFileTlsServerContext(context)"),
        "context_factory_retains_before_publication",
        "the returned capability owns one successful OpenSSL reference increment",
    )
    require(
        "SSL_CTX_free(context_)" in source
        and "std::exchange(other.context_, nullptr)" in source
        and "underlying context must still be treated as immutable" in header
        and "reference retention closes lifetime" in header,
        "context_destruction_and_mutation_nonclaim_are_explicit",
        "reference counting closes lifetime but does not pretend to serialize mutation",
    )
    require(
        "SSL_CTX* server_context" not in header
        and "SyncReplicaFileTlsServerContext server_context" in header
        and "SyncReplicaTlsAnchoredMembershipAuthority membership" in header
        and "SyncReplicaTlsMembershipAuthority membership" not in header,
        "server_api_rejects_raw_context_and_unanchored_membership",
        "accepted-session dependencies are explicit move-only values with independent rollback coverage",
    )

    listener = body(header, "class SyncReplicaFileTlsServerListener final")
    require(
        bool(listener)
        and "const SyncReplicaFileTlsServerListener&) = delete" in listener
        and "SyncReplicaFileTlsServerListener&& other) noexcept" in listener
        and "std::optional<SyncSocketLifetimeIdentity> socket_" in listener,
        "listener_is_move_only_and_invalidatable",
        "one retained exact listener capability cannot be copied",
    )
    require(
        "non-owning authority" in header
        and "caller retains" in header
        and "must serialize close, dup2, fcntl" in header,
        "listener_contract_separates_capability_from_fd_ownership",
        "scope does not silently close the caller-owned listener",
    )
    require(
        "std::function" not in header + source
        and "SyncReplicaTlsPeerActorResolver" not in header + source
        and "friend class SyncReplicaTlsMembershipSqliteOwner" in membership_header,
        "live_session_membership_has_no_arbitrary_callback",
        "authorization is owner-emitted immutable state",
    )
    require(
        all(token in header for token in (
            "AcceptDeadlineExpired", "HandshakeDeadlineExpired", "HandshakeRejected",
            "PeerUnauthorized", "RequestDeadlineExpired", "ReceiptDeadlineExpired", "ReceiptSent",
        )),
        "session_dispositions_preserve_distinct_cutpoints",
        "accept, authentication, request, receipt, and success are not collapsed",
    )
    require(
        all(token in header for token in ("CloseNotifySent", "Complete", "DeadlineExpired", "Failed"))
        and "close_notify is never represented as proof" in header,
        "shutdown_is_subordinate_diagnostic_state",
        "transport close cannot rewrite application settlement",
    )

    observe = body(source, "observe_sync_replica_file_tls_server_listener_or_throw(")
    require(
        ordered(
            observe,
            "observe_sync_stream_socket_lifetime_or_throw",
            "require_sync_stream_socket_nonblocking_or_throw",
            "require_sync_stream_socket_close_on_exec_or_throw",
            "require_listener_accepting_or_throw",
            "current_sync_process_incarnation_noexcept",
            "current_sync_thread_incarnation_noexcept",
        ),
        "listener_minting_binds_kernel_policy_then_affinity",
        "descriptor number alone cannot mint accept authority",
    )
    access = body(source, "struct SyncReplicaFileTlsServerListenerAccess final")
    require(
        ordered(access, "if (!listener.socket_.has_value())", "require_sync_process_incarnation_or_fail_stop", "require_sync_thread_incarnation_or_throw"),
        "inactive_listener_precedes_process_fail_stop_guard",
        "moved-from misuse throws while inherited active authority still fail-stops",
    )
    accepting = body(source, "void require_listener_accepting_or_throw(")
    require(
        ordered(accepting, "reprove_sync_stream_socket_lifetime_or_throw", "SO_ACCEPTCONN", "reprove_sync_stream_socket_lifetime_or_throw", "accepting != 1"),
        "accepting_state_is_sandwiched_by_lifetime_reproof",
        "SO_ACCEPTCONN cannot be borrowed from a replacement descriptor",
    )
    accept = body(source, "AcceptOutcome accept_one_until_or_throw(")
    require(
        "::accept4(" in accept
        and "SOCK_NONBLOCK | SOCK_CLOEXEC" in accept
        and "AcceptedSocketOwner child(accepted)" in accept,
        "accepted_child_flags_and_ownership_are_atomic",
        "no post-accept flag race or leaked child exists on exceptions",
    )
    require(
        ordered(accept, "require_or_throw", "steady_clock::now() >= deadline", "::accept4(", "post-accept listener reproof"),
        "accept_spends_reproved_listener_before_deadline",
        "queued-child creation cannot bypass identity or cutpoint",
    )
    require(
        all(token in source for token in ("ECONNABORTED", "EPROTO", "EHOSTUNREACH"))
        and "poll_sync_stream_socket_until_or_throw" in accept,
        "accept_transients_retain_one_absolute_cutpoint",
        "peer/network transients do not become listener corruption",
    )
    require(
        "attempts rather than by a fabricated syscall" in accept
        and "counters are diagnostic evidence" in header
        and "result.accept_attempts == 0U" in runtime
        and "TLS server preexpired accept fabricated syscall or session authority" in runtime,
        "preexpired_accept_is_zero_progress_not_test_flake",
        "an exhausted absolute cutpoint neither requires nor fabricates an accept syscall",
    )

    handshake = body(source, "HandshakeOutcome drive_server_handshake_until_or_throw(")
    require(
        ordered(handshake, "ERR_clear_error()", "SSL_accept(ssl)", "SSL_get_error(ssl, result)"),
        "handshake_obeys_same_thread_ssl_get_error_contract",
        "no OpenSSL operation interposes between operation and classification",
    )
    require(
        "SSL_ERROR_WANT_READ" in handshake
        and "SSL_ERROR_WANT_WRITE" in handshake
        and "poll_sync_stream_socket_until_or_throw" in handshake
        and "HandshakeOutcome::Terminal::Rejected" in handshake,
        "handshake_retries_only_explicit_nonblocking_wants",
        "other SSL outcomes terminate without speculative replay",
    )

    serve = body(source, "serve_one_sync_replica_file_delivery_tls_session_or_throw(")
    require(
        ordered(
            serve,
            "SyncReplicaFileTlsServerContextAccess::require_or_throw",
            "membership.snapshot()",
            "membership_snapshot.require_service_identity_or_throw",
            "membership.state_generation()",
            "SSL_new(server_context_handle)",
            "SSL_set_accept_state",
            "accept_one_until_or_throw",
        ),
        "dependencies_and_ssl_owner_precede_accept",
        "configuration or local SSL allocation failure cannot consume a queued peer",
    )
    require(
        ordered(
            serve,
            "accept_one_until_or_throw",
            "observe_sync_stream_socket_lifetime_or_throw",
            "require_sync_stream_socket_nonblocking_or_throw",
            "require_sync_stream_socket_close_on_exec_or_throw",
            "SSL_set_fd",
            "drive_server_handshake_until_or_throw",
        ),
        "accepted_socket_is_proved_before_ssl_binding",
        "SSL cannot inherit an unproved blocking or exec-inheritable child",
    )
    require(
        ordered(
            serve,
            "sync_replica_tls_peer_spki_sha256_or_throw",
            "membership_snapshot.resolve_peer_or_throw",
            "PeerUnauthorized",
            "post-membership accepted socket",
            "authenticate_sync_replica_tls13_channel_or_throw",
            "SyncReplicaFileTlsReceiverSession receiver_session",
            "receiver_session.run_or_throw()",
        ),
        "verified_spki_owner_membership_precedes_receiver",
        "certificate validity alone never authorizes an actor or durable request",
    )
    require(
        all(token in serve for token in (
            "membership_state_generation", "membership_policy_epoch", "membership_entry_count",
            "membership_snapshot_digest", "membership_previous_chain_digest", "membership_chain_digest",
        )),
        "session_result_retains_exact_membership_evidence",
        "terminal diagnostics identify snapshot and history cutpoint",
    )
    require(
        "SyncReplicaFileTlsReceiverSession receiver_session" in serve
        and "std::move(channel)" in serve
        and "receiver_session.run_or_throw()" in serve,
        "accepted_owner_transfers_exclusive_receiver_session",
        "outer socket/SSL lifecycle composes one inner application owner",
    )
    require(
        "if (!accepted.socket.has_value())" in serve
        and "AcceptDeadlineExpired" in serve
        and serve.find("SyncReplicaFileTlsReceiverSession receiver_session") > serve.find("PeerUnauthorized"),
        "preauth_terminal_paths_cannot_reach_service_callback",
        "timeout and unmapped peer return before application composition",
    )
    require(
        "catch (const std::runtime_error&)" in serve
        and "std::bad_alloc" in serve
        and "HandshakeRejected" in serve,
        "peer_profile_rejection_does_not_launder_resource_failure",
        "remote evidence failure is typed while local allocation failure propagates",
    )
    require(
        "SyncReplicaFileTlsServerDisposition::ReceiptSent" in serve
        and "drive_fast_shutdown_until_or_throw" in serve
        and "catch (...)" in serve
        and "shutdown_disposition =" in serve,
        "post_receipt_shutdown_cannot_erase_terminal_result",
        "cleanup failure becomes subordinate diagnostic state",
    )

    shutdown = body(source, "ShutdownOutcome drive_fast_shutdown_until_or_throw(")
    zero_branch = body(shutdown, "if (result == 0)")
    require(
        "SSL_shutdown(ssl)" in shutdown
        and bool(zero_branch)
        and "SSL_get_error(" not in zero_branch
        and "CloseNotifySent" in zero_branch,
        "shutdown_zero_is_not_misclassified_as_ssl_error",
        "OpenSSL fast-shutdown zero remains a non-error terminal state",
    )
    require(
        "SSL_ERROR_WANT_READ" in shutdown
        and "SSL_ERROR_WANT_WRITE" in shutdown
        and "poll_sync_stream_socket_until_or_throw" in shutdown,
        "shutdown_wants_are_bounded_and_exact",
        "one-shot close never blocks beyond its absolute cutpoint",
    )
    require(
        "(void)::close(descriptor)" in source
        and "retrying close() after EINTR" in source
        and "~AcceptedSocketOwner() noexcept" in source,
        "accepted_descriptor_has_single_close_owner",
        "terminal and exceptional paths cannot leak or retry-close an ABA descriptor",
    )

    require(
        "FD_CLOEXEC" in socket_header
        and ordered(
            body(socket_source, "void require_sync_stream_socket_close_on_exec_or_throw("),
            "reprove_sync_stream_socket_lifetime_or_throw", "F_GETFD",
            "reprove_sync_stream_socket_lifetime_or_throw", "FD_CLOEXEC",
        ),
        "close_on_exec_policy_lives_in_generic_socket_leaf",
        "server does not duplicate descriptor-flag authority syscalls",
    )
    require(
        "absolute steady-clock cutpoint" in poll_header
        and "require_sync_stream_socket_nonblocking_or_throw" in poll_source
        and "EINTR" in poll_source and "EAGAIN" in poll_source
        and "descriptor_event.revents == 0" in poll_source,
        "generic_poll_owner_retains_socket_and_deadline",
        "interruptions and spurious results cannot fabricate readiness",
    )

    runtime_tokens = (
        "TLS server context move duplicated or lost retained lifetime",
        "TLS server listener accepted blocking accept authority",
        "TLS server listener accepted exec-inheritable authority",
        "TLS server listener accepted a non-listening stream socket",
        "TLS membership preaccept mismatch reached durable authority",
        "TLS server spent a listener after FD_CLOEXEC mutation",
        "TLS server spent a listener after O_NONBLOCK mutation",
        "TLS server moved-from listener reached process fail-stop authority",
        "TLS server accept timeout reached durable receiver authority",
        "TLS server handshake timeout reached durable receiver authority",
        "TLS server rejected plaintext reached durable receiver authority",
        "TLS server unauthorized peer reached durable receiver authority",
        "TLS server did not preserve accepted-session terminal cutpoints and membership evidence",
        "TLS server accepted session did not converge canonical evidence",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "runtime_matrix_covers_lifetime_policy_auth_and_success",
        "compiled tests exercise no-mutation and complete publication paths",
    )
    require(
        all(token in socket_runtime for token in (
            "clearing FD_CLOEXEC does not rewrite socket lifetime",
            "close-on-exec policy rejects an inheritable authenticated lifetime",
            "already-expired exact socket poll does not issue hidden progress",
            "caller operation, not poll, classifies peer close",
        )),
        "socket_runtime_distinguishes_identity_policy_and_readiness",
        "the shared leaf is tested independently from TLS composition",
    )
    require(
        "add_library(anonsync_sync_replica_tls_membership STATIC" in cmake
        and "add_library(anonsync_sync_replica_file_tls_server STATIC" in cmake
        and "anonsync_sync_replica_tls_membership" in cmake
        and cmake.count("anonsync_sync_file_tls_server_source_audit") >= 2,
        "production_authority_leaves_and_audit_are_registered",
        "membership policy and accepted-session ownership are separate targets",
    )
    require(
        all(token in verifier for token in (
            "src/sync_replica_file_tls_server.hpp", "src/sync_replica_file_tls_server.cpp",
            "src/sync_replica_tls_membership_sqlite_owner.hpp",
            "src/sync_stream_socket_deadline_poll.hpp", "src/sync_stream_socket_deadline_poll.cpp",
            "tools/audit_sync_file_tls_server.py",
        )),
        "release_verifier_requires_complete_server_surface",
        "sealed handoff cannot omit implementation, policy authority, poll leaf, or audit",
    )
    require(
        "Lexical hygiene audit" in (__doc__ or "")
        and "does not claim to prove" in (__doc__ or ""),
        "audit_disclaims_semantic_authority",
        "source vocabulary is not represented as runtime proof",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-file-tls-server-source-audit-v6",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove kernel, OpenSSL, "
            "membership freshness, timeout, SQLite, or filesystem semantics"
        ),
        "root": str(root),
        "passed": passed,
        "passed_checks": sum(bool(check["passed"]) for check in checks),
        "total_checks": len(checks),
        "checks": checks,
        "violations": [check["check_id"] for check in checks if not check["passed"]],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
