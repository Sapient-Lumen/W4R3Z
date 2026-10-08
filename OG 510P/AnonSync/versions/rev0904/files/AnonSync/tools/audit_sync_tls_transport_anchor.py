#!/usr/bin/env python3
"""Lexical hygiene audit for authenticated TLS BIO/socket anchoring.

This audit checks review-critical source shape only. It does not prove OpenSSL
semantics, kernel behavior, retry correctness, concurrency safety, or delivery.
Those claims require compiled negative tests and independent build lanes.
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
    required = [
        Path("src/sync_replica_tls_transport.hpp"),
        Path("src/sync_replica_tls_transport.cpp"),
        Path("src/sync_socket_readiness_identity.hpp"),
        Path("tests/sync_replica_tls_transport_test.cpp"),
        Path("tools/audit_sync_tls_transport_anchor.py"),
        Path("CMakeLists.txt"),
        Path("tools/verify_release_package.py"),
        Path("TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md"),
        Path("REVISION_NOTES_rev0886.md"),
    ]
    missing = sorted(str(path) for path in required if not (root / path).is_file())
    text = {
        str(path): (root / path).read_text(encoding="utf-8")
        if (root / path).is_file() else ""
        for path in required
    }
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    require(not missing, "required_files_exist", f"missing={missing}")
    source = text["src/sync_replica_tls_transport.cpp"]
    header = text["src/sync_replica_tls_transport.hpp"]
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]
    design = text["TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md"]
    notes = text["REVISION_NOTES_rev0886.md"]

    anchor = body(source, "struct SyncReplicaTlsTransportAnchor final")
    require(
        "BioReference read_bio" in anchor
        and "BioReference write_bio" in anchor
        and "optional<SyncSocketLifetimeIdentity> read_socket" in anchor
        and "optional<SyncSocketLifetimeIdentity> write_socket" in anchor,
        "anchor_owns_both_bios_and_directional_socket_lifetimes",
        "BIO identity and in-place descriptor identity are independently bound",
    )
    retain = body(source, "BioReference retain_tls_bio_reference_or_throw(")
    require(
        "decltype(&BIO_free_all)" in source
        and ordered(
            retain,
            "BIO_up_ref(bio)",
            "BioReference(bio, BIO_free_all)",
        ),
        "bio_pointer_identity_is_refcount_stabilized",
        "SSL replacement cannot recycle the authenticated BIO pointer and final release traverses a retained filter chain",
    )
    capture = body(source, "capture_tls_transport_anchor_or_throw(")
    require(
        ordered(
            capture,
            "SSL_get_rbio(ssl)",
            "SSL_get_wbio(ssl)",
            "retain_tls_bio_reference_or_throw",
            "observe_direct_tls_stream_socket_lifetime_or_throw",
            "SyncReplicaTlsTransportAnchor anchor",
            "validate_tls_transport_anchor_or_throw",
            "return anchor",
        ),
        "authentication_capture_retains_then_double_checks_transport",
        "the returned anchor cannot silently combine replaced BIO objects",
    )
    direction = body(source, "void validate_tls_transport_anchor_direction_or_throw(")
    require(
        ordered(
            direction,
            "current_bio != expected_bio",
            "BIO changed after authentication",
            "BIO_get_fd(current_bio, nullptr)",
            "descriptor != expected_socket->descriptor()",
            "reprove_sync_stream_socket_lifetime_or_throw",
        ),
        "reproof_checks_pointer_descriptor_and_kernel_lifetime",
        "SSL_set_fd and BIO_set_fd have distinct fail-closed detection paths",
    )
    readiness = body(source, "void require_tls_transport_anchor_nonblocking_or_throw(")
    require(
        "authentication-anchored direct socket TLS read and write BIOs" in readiness
        and readiness.count("require_sync_stream_socket_nonblocking_or_throw") == 2,
        "strict_readiness_requires_both_anchored_directions",
        "custom BIOs and blocking sockets cannot enter bounded readiness mode",
    )

    authenticate = body(source, "authenticate_sync_replica_tls13_channel_or_throw(")
    require(
        ordered(
            authenticate,
            "validate_delivery_tls_or_throw",
            "capture_tls_transport_anchor_or_throw",
            "peer_spki_sha256_after_profile_or_throw",
            "tls_exporter_binding_after_profile_or_throw",
            "validate_tls_transport_anchor_or_throw",
            "make_shared<detail::SyncReplicaTlsAuthenticatedState>",
        ),
        "transport_is_anchored_across_identity_and_exporter_derivation",
        "mutation during authentication is detected before capability publication",
    )
    state = body(source, "class detail::SyncReplicaTlsAuthenticatedState final")
    require(
        "SyncReplicaTlsTransportAnchor transport_anchor_" in state
        and "record_readiness_proof_" not in state,
        "authenticated_anchor_replaces_per_record_identity_cache",
        "one immutable authority source avoids stale duplicated readiness state",
    )
    constructor = body(source, "SyncReplicaTlsAuthenticatedState(")
    require(
        ordered(
            constructor,
            "validate_tls_transport_anchor_or_throw",
            "SSL_up_ref(ssl)",
            "ssl_ = ssl",
        )
        and "No operation below this point may throw" in constructor,
        "ssl_and_bio_retention_is_exception_safe",
        "a failed construction cannot leak references or publish partial state",
    )
    live = body(source, "void validate_authenticated_channel_and_poison_or_throw(")
    require(
        ordered(
            live,
            "validate_tls_transport_anchor_or_throw",
            "validate_authenticated_session_or_throw",
            "poisoned_ = true",
        ),
        "ordinary_authority_reproves_transport_before_session",
        "durable service entry cannot use peer/exporter identity on a replaced transport",
    )
    begin_write = body(source, "SSL* begin_record_write_or_throw(")
    begin_read = body(source, "void begin_record_read_or_throw(")
    require(
        "validate_or_throw(label)" in begin_write
        and "require_nonblocking_transport_policy_or_throw(label, false)" in begin_write
        and "validate_or_throw(label)" in begin_read
        and "require_nonblocking_transport_policy_or_throw(label, false)" in begin_read,
        "pre_io_policy_rejection_does_not_poison_untouched_channel",
        "blocking/custom preflight remains distinguishable from transport contradiction",
    )
    active_io = body(source, "SSL* active_record_io_or_throw(")
    write_advance = body(
        source, "SyncReplicaTlsRecordWriteContinuation::advance_or_throw()"
    )
    require(
        ordered(
            write_advance,
            "active_record_io_or_throw",
            "SyncReplicaTlsRecordReservation::Write",
            "SSL_write_ex",
        )
        and ordered(
            active_io,
            "require_record_owner_or_throw",
            "if (retry_pending)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "return ssl_",
            "validate_authenticated_channel_and_poison_or_throw(label)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
        ),
        "accepted_prefix_body_frontier_reproves_full_anchor",
        "fresh body authority cannot move to a replacement or blocking transport",
    )
    require(
        "SyncReplicaTlsRecordReservation expected" in active_io
        and "if (retry_pending)" in active_io
        and ordered(
            active_io,
            "if (require_nonblocking_socket)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "else",
            "validate_transport_anchor_and_poison_or_throw(label)",
            "return ssl_",
            "validate_authenticated_channel_and_poison_or_throw(label)",
        ),
        "pending_retry_and_fresh_io_have_distinct_reproofs",
        "WANT retry avoids peer/exporter calls while fresh read and write steps re-attest them",
    )
    poll = body(source, "pending_readiness_target_or_throw(")
    require(
        ordered(
            poll,
            "require_record_owner_or_throw",
            "switch (pending)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "transport_anchor_.write_socket",
            "transport_anchor_.read_socket",
            "return {socket->descriptor(), public_readiness}",
        ),
        "poll_target_is_reproved_before_disclosure",
        "an event loop is never intentionally handed a stale transport integer",
    )
    advance = body(source, "SyncReplicaTlsRecordReadContinuation::advance_or_throw()")
    require(
        advance.count("SSL_read_ex(") == 1
        and ordered(advance, "SSL_read_ex(", "SSL_get_error(ssl, result)"),
        "ssl_error_classification_is_immediate",
        "BIO reproof never interposes between SSL_read_ex and SSL_get_error",
    )
    require(
        "retains both exact BIO objects" in header
        and "authentication-time" in header
        and "descriptor number is not authority" in header,
        "public_contract_names_bio_and_socket_anchor",
        "callers are warned that poll integers and session identity are subordinate evidence",
    )

    runtime_tokens = (
        "TLS post-auth BIO replacement",
        "TLS retained filter BIO chain",
        "TLS post-auth BIO fd mutation",
        "TLS write BIO replacement frontier",
        "TLS pending WANT BIO replacement",
        "TLS pending retry BIO fd mutation",
        "TLS write descriptor ABA",
        "TLS pending write descriptor ABA",
        "TLS pending write nonblocking reproof",
        "TLS poll target descriptor ABA",
        "TLS fresh-step descriptor ABA",
        "file TLS blocking generic reuse",
    )
    require(
        all(token in runtime for token in runtime_tokens)
        and "SSL_set_fd(" in runtime
        and "BIO_set_fd(" in runtime
        and "install_counted_filter_bio_chain_or_fail" in runtime
        and "filter_frees == 1U && socket_frees == 1U" in runtime,
        "runtime_matrix_forces_replacement_inplace_retry_and_policy_frontiers",
        "compiled TLS 1.3 tests exercise replacement, in-place mutation, retry, policy, and complete filter-chain release",
    )
    require(
        cmake.count("anonsync_sync_tls_transport_anchor_source_audit") >= 2
        and "tools/audit_sync_tls_transport_anchor.py" in cmake,
        "audit_is_registered_in_ctest",
        "ordinary audit selection includes the authentication anchor inventory",
    )
    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 886",
                "tools/audit_sync_tls_transport_anchor.py",
                "TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md",
                "REVISION_NOTES_rev0886.md",
            )
        ),
        "release_verifier_requires_rev0886_anchor_surface",
        "a sealed handoff cannot omit code rationale runtime or audit",
    )
    require(
        all(
            token in design
            for token in (
                "SSL_set_fd",
                "BIO_set_fd",
                "BIO_free_all",
                "filter chain",
                "OpenSSL",
                "Failure matrix",
                "Rejected",
                "does not claim",
            )
        )
        and all(
            token in notes
            for token in (
                "rev0886",
                "BIO",
                "BIO_free_all",
                "SOCK_STREAM",
                "O_NONBLOCK",
            )
        ),
        "design_and_revision_records_cover_sources_failures_and_nonclaims",
        "the rationale and residual risks travel with the implementation",
    )
    require(
        "does not prove OpenSSL" in __doc__
        and "compiled negative tests" in __doc__,
        "audit_disclaims_semantic_authority",
        "substring presence is not represented as transport correctness",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-sync-tls-transport-anchor-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": "source vocabulary and order do not prove OpenSSL retry semantics, BIO ownership, kernel identity, concurrency, or delivery",
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
