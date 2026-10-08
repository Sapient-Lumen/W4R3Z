#!/usr/bin/env python3
"""Lexical hygiene audit for exact TLS record-I/O policy authority.

This audit checks review-critical source shape and release inventory only. It
does not prove OpenSSL behavior, retry semantics, close/truncation behavior,
race freedom, poisoning, or end-to-end delivery. Those claims require compiled
negative tests, real TLS peers, sanitizers, and independent build lanes.
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
        Path("src/sync_replica_tls_io_policy.hpp"),
        Path("src/sync_replica_tls_io_policy.cpp"),
        Path("src/sync_replica_tls_transport.hpp"),
        Path("src/sync_replica_tls_transport.cpp"),
        Path("tests/sync_replica_tls_io_policy_test.cpp"),
        Path("tests/sync_replica_tls_transport_test.cpp"),
        Path("tools/audit_sync_tls_io_policy.py"),
        Path("tools/verify_release_package.py"),
        Path("TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md"),
        Path("REVISION_NOTES_rev0887.md"),
        Path("CMakeLists.txt"),
    ]
    missing = sorted(str(path) for path in required if not (root / path).is_file())
    text = {
        str(path): (root / path).read_text(encoding="utf-8")
        if (root / path).is_file()
        else ""
        for path in required
    }
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(
            {"check_id": check_id, "passed": bool(condition), "detail": detail}
        )

    require(not missing, "required_files_exist", f"missing={missing}")
    header = text["src/sync_replica_tls_io_policy.hpp"]
    policy = text["src/sync_replica_tls_io_policy.cpp"]
    transport_header = text["src/sync_replica_tls_transport.hpp"]
    transport = text["src/sync_replica_tls_transport.cpp"]
    leaf_runtime = text["tests/sync_replica_tls_io_policy_test.cpp"]
    transport_runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]
    design = text["TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md"]
    notes = text["REVISION_NOTES_rev0887.md"]

    policy_source_list = cmake[
        cmake.find("set(ANONSYNC_SYNC_REPLICA_TLS_IO_POLICY_SOURCE") :
        cmake.find("add_library(anonsync_sync_replica_tls_transport STATIC")
    ]
    transport_source_list = cmake[
        cmake.find("set(ANONSYNC_SYNC_REPLICA_TLS_TRANSPORT_SOURCE") :
        cmake.find("add_library(anonsync_sync_replica_tls_transport STATIC")
    ]
    transport_link = cmake[
        cmake.find("target_link_libraries(anonsync_sync_replica_tls_transport PUBLIC") :
        cmake.find("target_compile_options(anonsync_sync_replica_tls_transport PRIVATE")
    ]
    require(
        "src/sync_replica_tls_io_policy.cpp" in policy_source_list
        and "OpenSSL::SSL" in policy_source_list
        and "anonsync_sync_replica_tls_io_policy" in transport_link
        and "src/sync_replica_tls_io_policy.cpp" not in transport_source_list,
        "policy_is_a_narrow_transport_dependency_leaf",
        "record semantics no longer add a mixed authority cluster to the transport translation unit",
    )

    policy_value = body(header, "struct SyncReplicaTlsIoPolicy final")
    require(
        all(
            token in policy_value
            for token in (
                "std::uint64_t options",
                "long modes",
                "int read_ahead",
                "int quiet_shutdown",
                "int verify_mode",
                "int shutdown_state",
                "operator==",
            )
        ),
        "policy_value_binds_every_mutable_record_semantic",
        "option, mode, read-ahead, quiet shutdown, verification, and shutdown state are one exact value",
    )

    configure = body(
        policy, "void configure_sync_replica_tls_io_policy_or_throw("
    )
    require(
        ordered(
            configure,
            "SSL_CTX_clear_options(context, SSL_OP_IGNORE_UNEXPECTED_EOF)",
            "SSL_CTX_set_mode(context, SSL_MODE_AUTO_RETRY)",
            "SSL_CTX_clear_mode(context, SSL_MODE_ASYNC)",
            "SSL_CTX_set_read_ahead(context, 0)",
            "SSL_CTX_set_quiet_shutdown(context, 0)",
            "SSL_CTX_get_options(context)",
            "SSL_CTX_get_mode(context)",
            "SSL_CTX_get_read_ahead(context)",
            "SSL_CTX_get_quiet_shutdown(context)",
        ),
        "context_profile_normalizes_then_reads_back_strict_semantics",
        "unsafe inherited defaults cannot silently reach SSL_new",
    )

    observe = body(policy, "observe_tls_io_policy_or_throw(")
    require(
        ordered(
            observe,
            "SSL_get_options(ssl)",
            "SSL_get_mode(ssl)",
            "SSL_get_read_ahead(ssl)",
            "SSL_get_quiet_shutdown(ssl)",
            "SSL_get_verify_mode(ssl)",
            "SSL_get_shutdown(ssl)",
        ),
        "live_observation_populates_the_complete_policy_value",
        "capture and reproof consume one consistent field inventory",
    )

    safe = body(policy, "void validate_tls_io_policy_is_safe_or_throw(")
    require(
        all(
            token in safe
            for token in (
                "SSL_OP_IGNORE_UNEXPECTED_EOF",
                "SSL_MODE_AUTO_RETRY",
                "SSL_MODE_ASYNC",
                "policy.read_ahead != 0",
                "policy.quiet_shutdown != 0",
                "SSL_VERIFY_PEER",
                "policy.shutdown_state != 0",
            )
        ),
        "capture_rejects_every_known_unsafe_semantic",
        "clean close, retry, hidden progress, verification, and shutdown evidence remain explicit",
    )

    reproof = body(
        policy, "void reprove_sync_replica_tls_io_policy_or_throw("
    )
    require(
        ordered(
            reproof,
            "current.options != expected.options",
            "current.modes != expected.modes",
            "current.read_ahead != expected.read_ahead",
            "current.quiet_shutdown != expected.quiet_shutdown",
            "current.verify_mode != expected.verify_mode",
            "current.shutdown_state != expected.shutdown_state",
            "validate_tls_io_policy_is_safe_or_throw(current, label)",
        ),
        "live_reproof_requires_exact_equality_before_safety",
        "an apparently benign mutation cannot borrow old authenticated authority",
    )

    authenticate = body(
        transport, "authenticate_sync_replica_tls13_channel_or_throw("
    )
    require(
        ordered(
            authenticate,
            "capture_tls_transport_anchor_or_throw(",
            "capture_sync_replica_tls_io_policy_or_throw(",
            "peer_spki_sha256_after_profile_or_throw(",
            "tls_exporter_binding_after_profile_or_throw(",
            "validate_tls_transport_anchor_or_throw(",
            "reprove_sync_replica_tls_io_policy_or_throw(",
            "make_shared<detail::SyncReplicaTlsAuthenticatedState>",
        ),
        "authentication_double_checks_transport_and_policy_around_identity_derivation",
        "a mixed transport-policy-peer snapshot cannot be published",
    )

    state = body(transport, "class detail::SyncReplicaTlsAuthenticatedState final")
    constructor = body(transport, "SyncReplicaTlsAuthenticatedState(")
    require(
        "detail::SyncReplicaTlsIoPolicy io_policy_" in state
        and ordered(
            constructor,
            "validate_tls_transport_anchor_or_throw(",
            "reprove_sync_replica_tls_io_policy_or_throw(",
            "SSL_up_ref(ssl)",
            "ssl_ = ssl",
        ),
        "authenticated_state_owns_and_reproves_policy_before_ssl_retention",
        "partial state publication cannot outrun policy contradiction",
    )

    ordinary = body(
        transport, "void validate_authenticated_channel_and_poison_or_throw("
    )
    require(
        ordered(
            ordinary,
            "validate_tls_transport_anchor_or_throw(",
            "reprove_sync_replica_tls_io_policy_or_throw(",
            "validate_authenticated_session_or_throw(",
            "poisoned_ = true",
        ),
        "ordinary_authority_orders_transport_policy_then_session_and_poison",
        "durable authority cannot run under a mutated SSL policy",
    )

    active_io = body(transport, "SSL* active_record_io_or_throw(")
    require(
        ordered(
            active_io,
            "if (retry_pending)",
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "validate_io_policy_and_poison_or_throw(label)",
            "return ssl_",
            "validate_authenticated_channel_and_poison_or_throw(label)",
        ),
        "pending_retry_reproves_transport_and_policy_without_session_reentry",
        "the exact OpenSSL retry is preserved while mutable semantics remain bound",
    )

    target = body(transport, "pending_readiness_target_or_throw(")
    require(
        ordered(
            target,
            "require_nonblocking_transport_policy_or_throw(label, true)",
            "validate_io_policy_and_poison_or_throw(label)",
            "return {socket->descriptor(), public_readiness}",
        ),
        "readiness_target_reproves_policy_before_descriptor_disclosure",
        "the event loop cannot receive a target derived under changed retry semantics",
    )

    require(
        "SSL_read_ex(" in transport
        and "SSL_write_ex(" in transport
        and transport.count("SSL_get_error(ssl, result)") >= 2
        and "reprove_sync_replica_tls_io_policy_or_throw" not in body(
            transport, "SyncReplicaTlsRecordReadContinuation::advance_or_throw("
        ).split("SSL_get_error(ssl, result)")[0].split("SSL_read_ex(")[-1],
        "ssl_error_classification_remains_immediate",
        "policy observation does not interpose between OpenSSL I/O and SSL_get_error",
    )

    leaf_tokens = (
        "context profile restores strict unexpected-EOF semantics",
        "capture rejects abrupt-close laundering",
        "capture rejects weakened retry semantics",
        "capture rejects unowned asynchronous-engine readiness",
        "capture rejects read-ahead state expansion",
        "capture rejects synthetic clean closure",
        "capture rejects missing peer verification",
        "capture rejects forged shutdown evidence",
        "exact reproof rejects",
        "configuration rejects null context",
    )
    require(
        all(token in leaf_runtime for token in leaf_tokens),
        "focused_runtime_matrix_covers_profile_capture_reproof_and_nulls",
        "the extracted leaf has direct executable negative evidence",
    )

    integration_tokens = (
        "test_tls_io_policy_profile_and_mutation_fences",
        "TLS authentication unexpected-EOF policy",
        "TLS authentication AUTO_RETRY policy",
        "TLS authentication asynchronous mode policy",
        "TLS pending-target policy mutation",
        "TLS pending-retry policy mutation",
        "shutdown state changed after authentication",
        "TLS abrupt EOF classification",
        "abrupt TLS EOF was laundered into clean peer close",
        "PeerClosed",
    )
    require(
        all(token in transport_runtime for token in integration_tokens),
        "real_tls_matrix_covers_auth_live_want_and_abrupt_close_frontiers",
        "the semantic claims are exercised through completed TLS 1.3 connections",
    )

    require(
        all(
            token in transport_header
            for token in (
                "unexpected EOF kept distinct from close_notify",
                "authentication-time SSL option mask",
                "Later observable mutation",
                "transient mutate-and-restore",
                "Pending WANT target disclosure",
            )
        ),
        "public_contract_names_policy_and_exclusive_ownership_limit",
        "callers are not told that observable reproof detects unobserved mutation",
    )

    require(
        cmake.count("anonsync_sync_replica_tls_io_policy_test") >= 5
        and cmake.count("anonsync_sync_tls_io_policy_source_audit") >= 2
        and "tools/audit_sync_tls_io_policy.py" in cmake,
        "runtime_and_source_audits_are_registered_in_ctest",
        "ordinary release test selection includes both policy evidence layers",
    )

    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 887",
                "src/sync_replica_tls_io_policy.hpp",
                "src/sync_replica_tls_io_policy.cpp",
                "tests/sync_replica_tls_io_policy_test.cpp",
                "tools/audit_sync_tls_io_policy.py",
                "TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md",
                "REVISION_NOTES_rev0887.md",
            )
        ),
        "release_verifier_requires_rev0887_policy_surface",
        "a sealed handoff cannot omit code, runtime, rationale, or audit",
    )

    require(
        all(
            token in design
            for token in (
                "SSL_OP_IGNORE_UNEXPECTED_EOF",
                "SSL_MODE_AUTO_RETRY",
                "SSL_MODE_ASYNC",
                "SSL_set_shutdown",
                "close_notify",
                "Failure matrix",
                "Rejected alternatives",
                "does **not** claim",
            )
        )
        and all(
            token in notes
            for token in (
                "rev0887",
                "record-I/O policy",
                "pending WANT",
                "abrupt socket closure",
                "transient mutate-and-restore",
            )
        ),
        "design_and_revision_records_cover_sources_failures_and_nonclaims",
        "the rationale and residual ownership gap travel with the implementation",
    )

    require(
        "does not prove OpenSSL behavior" in (__doc__ or "")
        and "compiled" in (__doc__ or ""),
        "audit_disclaims_semantic_authority",
        "source vocabulary is not represented as TLS correctness",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-sync-tls-io-policy-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove OpenSSL semantics, "
            "close/truncation behavior, exact retry, race freedom, poisoning, "
            "or delivery"
        ),
        "root": str(root),
        "passed": passed,
        "passed_checks": sum(bool(check["passed"]) for check in checks),
        "total_checks": len(checks),
        "checks": checks,
        "violations": [
            check["check_id"] for check in checks if not check["passed"]
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
