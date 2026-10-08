#!/usr/bin/env python3
"""Lexical hygiene audit for the socket-lifetime/readiness capability leaf.

This inventory deliberately does not claim to prove Linux kernel behavior,
serialization against descriptor mutation, or TLS correctness. Runtime tests
and sanitizer/compiler lanes carry those semantic obligations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def delimited_body(text: str, marker: str) -> str:
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
        "header": root / "src/sync_socket_readiness_identity.hpp",
        "source": root / "src/sync_socket_readiness_identity.cpp",
        "runtime": root / "tests/sync_socket_readiness_identity_test.cpp",
        "poll_header": root / "src/sync_stream_socket_deadline_poll.hpp",
        "poll_source": root / "src/sync_stream_socket_deadline_poll.cpp",
        "tls": root / "src/sync_replica_tls_transport.cpp",
        "server": root / "src/sync_replica_file_tls_server.cpp",
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
    runtime = text["runtime"]
    poll_header = text["poll_header"]
    poll_source = text["poll_source"]
    tls = text["tls"]
    server = text["server"]
    cmake = text["cmake"]
    verifier = text["verifier"]

    identity = delimited_body(header, "class SyncSocketLifetimeIdentity final")
    private = identity.split("private:", 1)[1] if "private:" in identity else ""
    require(
        bool(identity)
        and "SyncSocketLifetimeIdentity()" not in identity
        and "friend SyncSocketLifetimeIdentity" in private
        and "observe_sync_stream_socket_lifetime_or_throw" in private,
        "lifetime_identity_is_observer_minted",
        "callers cannot default-construct or forge the kernel tuple",
    )
    require(
        "descriptor() const noexcept" in identity
        and "device_" in private
        and "inode_" in private
        and "linux_socket_cookie_" in private
        and "socket_type_" in private,
        "lifetime_identity_is_opaque_except_poll_descriptor",
        "partial tuple comparison and serialization are not public API",
    )
    require(
        "operator==(const SyncSocketLifetimeIdentity&) const noexcept = default" in identity,
        "exact_comparison_covers_whole_private_tuple",
        "descriptor, type, stat identity, and cookie move as one value",
    )
    require(
        "O_NONBLOCK is deliberately not part of lifetime identity" in header
        and "process-local evidence" in header
        and "serialize descriptor and file-status mutation" in header,
        "public_contract_separates_lifetime_policy_and_ownership",
        "the value is neither readiness state nor descriptor ownership",
    )

    observe = delimited_body(source, "SyncSocketLifetimeIdentity observe_sync_stream_socket_lifetime_or_throw(")
    require(
        ordered(
            observe,
            "fstat(descriptor, &before)",
            "S_ISSOCK(before.st_mode)",
            "observe_socket_type_or_throw",
            "observe_socket_cookie_or_throw",
            "fstat(descriptor, &after)",
            "same_file_identity(before, after)",
            "socket_type_after",
            "cookie_after",
            "return SyncSocketLifetimeIdentity(",
        ),
        "linux_lifetime_capture_is_double_observed",
        "one returned tuple cannot intentionally combine sequential fd occupants",
    )
    require(
        "socket_type != SOCK_STREAM" in source
        and "is not a SOCK_STREAM socket" in source,
        "byte_stream_semantics_are_explicit",
        "datagram sockets cannot back TLS stream framing authority",
    )
    require(
        "#ifndef SO_COOKIE" in source
        and "#error \"Linux socket lifetime reproof requires SO_COOKIE\"" in source
        and "cookie == 0U" in source
        and "cookie_after != cookie" in source,
        "linux_cookie_is_required_nonzero_and_stable",
        "kernel generation or descriptor class is not substituted for lifetime evidence",
    )
    require(
        "unsigned_stat_component_or_throw" in observe
        and "does not fit uint64_t" in source
        and "negative" in source,
        "stat_identity_conversion_is_checked",
        "platform stat fields cannot silently truncate into the retained tuple",
    )
    require(
        "cannot prove an exact stream-socket lifetime on this platform" in observe,
        "unsupported_lifetime_platform_fails_closed",
        "no weaker tuple is mislabeled as exact Linux lifetime evidence",
    )

    reprove = delimited_body(source, "void reprove_sync_stream_socket_lifetime_or_throw(")
    require(
        ordered(
            reprove,
            "observe_sync_stream_socket_lifetime_or_throw",
            "observed != expected",
            "no longer names the exact observed socket lifetime",
        ),
        "lifetime_reproof_reobserves_and_exactly_compares",
        "same-number class checks cannot replace captured identity",
    )
    readiness = delimited_body(source, "void require_sync_stream_socket_nonblocking_or_throw(")
    require(
        ordered(
            readiness,
            "reprove_sync_stream_socket_lifetime_or_throw(expected, label)",
            "F_GETFL",
            "reprove_sync_stream_socket_lifetime_or_throw(expected, label)",
            "O_NONBLOCK",
        ),
        "readiness_policy_is_sandwiched_by_lifetime_reproof",
        "an ABA descriptor cannot lend unrelated file-status flags",
    )
    close_on_exec = delimited_body(
        source, "void require_sync_stream_socket_close_on_exec_or_throw(")
    require(
        ordered(
            close_on_exec,
            "reprove_sync_stream_socket_lifetime_or_throw(expected, label)",
            "F_GETFD",
            "reprove_sync_stream_socket_lifetime_or_throw(expected, label)",
            "FD_CLOEXEC",
        )
        and "is inheritable across exec" in close_on_exec,
        "close_on_exec_policy_is_sandwiched_by_lifetime_reproof",
        "descriptor inheritance policy cannot be borrowed across fd ABA",
    )
    require(
        "close-on-exec" in header
        and "separate" in header
        and "mutable policy check" in header,
        "close_on_exec_is_not_mislabeled_as_socket_identity",
        "process inheritance hygiene remains distinct from kernel lifetime",
    )
    require(
        "F_GETFL" not in observe
        and "O_NONBLOCK" not in observe
        and "F_GETFD" not in observe
        and "FD_CLOEXEC" not in observe,
        "mutable_policies_are_absent_from_lifetime_capture",
        "blocking and inheritable views of one socket retain one identity",
    )
    require(
        all(token not in source for token in ("SSL_", "BIO_", "openssl/")),
        "kernel_capability_leaf_is_transport_independent",
        "OpenSSL policy cannot leak into the socket observer",
    )

    poll = delimited_body(
        poll_source, "poll_sync_stream_socket_until_or_throw(")
    require(
        "std::chrono::steady_clock::is_steady" in poll_source
        and "absolute steady-clock cutpoint" in poll_header
        and "DeadlineExpired" in poll_header,
        "poll_owns_one_monotonic_absolute_cutpoint",
        "relative retry waits cannot silently extend network authority",
    )
    require(
        ordered(
            poll,
            "require_sync_stream_socket_nonblocking_or_throw(socket, label)",
            "before_poll >= deadline",
            "::poll(&descriptor_event, 1U, timeout)",
            "descriptor_event.revents == 0",
            "std::chrono::steady_clock::now() >= deadline",
            "require_sync_stream_socket_nonblocking_or_throw(socket, label)",
            "SyncStreamSocketDeadlinePollResult::Ready",
        ),
        "poll_reproves_exact_lifetime_policy_before_and_after_wait",
        "readiness cannot outlive the socket identity or absolute cutpoint",
    )
    require(
        "poll_errno == EINTR || poll_errno == EAGAIN" in poll
        and "continue;" in poll
        and "INT_MAX" in poll_source
        and "whole_milliseconds" in poll_source,
        "poll_retries_interruptions_without_resetting_deadline",
        "timeouts are ceiling-rounded and clamped without relative-budget drift",
    )
    require(
        all(token in poll_header for token in ("POLLERR", "POLLHUP", "POLLNVAL", "advisory wakeups"))
        and "cannot own a bounded stream-socket poll on this platform" in poll,
        "poll_reports_advisory_wakeup_and_fails_closed_elsewhere",
        "the leaf does not invent protocol progress or weak fallback authority",
    )
    require(
        all(token not in poll_source for token in ("SSL_", "BIO_", "openssl/")),
        "poll_leaf_is_protocol_independent",
        "TLS and accept state machines share one kernel readiness owner",
    )

    require(
        all(
            token in runtime
            for token in (
                "unchanged blocking socket lifetime reproves",
                "readiness policy rejects a blocking authenticated lifetime",
                "deadline poll rejects a blocking authenticated lifetime",
                "same lifetime gains nonblocking readiness authority",
                "same lifetime carries close-on-exec process hygiene",
                "clearing FD_CLOEXEC does not rewrite socket lifetime",
                "close-on-exec policy rejects an inheritable authenticated lifetime",
                "already-expired exact socket poll does not issue hidden progress",
                "exact socket poll exposes advisory readability",
                "exact socket poll exposes advisory writability",
                "peer close is an advisory readiness wakeup",
                "caller operation, not poll, classifies peer close",
                "clearing O_NONBLOCK does not rewrite socket lifetime",
                "datagram socket cannot mint byte-stream transport authority",
                "lifetime reproof rejects close/dup2 descriptor ABA",
                "closed descriptor cannot reprove socket lifetime",
            )
        ),
        "runtime_matrix_covers_identity_policies_poll_type_aba_and_close",
        "compiled tests distinguish identity, policy, advisory readiness, and protocol outcome",
    )
    require(
        "SyncSocketLifetimeIdentity" in tls
        and "observe_sync_stream_socket_lifetime_or_throw" in tls
        and "require_sync_stream_socket_nonblocking_or_throw" in tls
        and all(token not in tls for token in ("::getsockopt", "::fcntl", "::fstat", "SO_COOKIE")),
        "tls_consumes_one_generic_lifetime_owner",
        "transport code does not duplicate kernel identity syscalls",
    )
    require(
        "poll_sync_stream_socket_until_or_throw" in server
        and "require_sync_stream_socket_close_on_exec_or_throw" in server
        and all(token not in server for token in ("::fcntl", "::fstat", "SO_COOKIE")),
        "accepted_session_composes_shared_policy_and_poll_leaves",
        "listener/session code adds only accept policy instead of another fd identity stack",
    )
    require(
        cmake.count("anonsync_sync_socket_readiness_identity_source_audit") >= 2
        and "tools/audit_sync_socket_readiness_identity.py" in cmake
        and "add_library(anonsync_sync_stream_socket_deadline_poll STATIC" in cmake
        and "src/sync_stream_socket_deadline_poll.cpp" in cmake,
        "poll_leaf_and_audit_are_registered_in_build_graph",
        "ordinary builds and source-audit selection include the shared owner",
    )
    require(
        all(
            token in verifier
            for token in (
                "src/sync_socket_readiness_identity.hpp",
                "src/sync_socket_readiness_identity.cpp",
                "tests/sync_socket_readiness_identity_test.cpp",
                "src/sync_stream_socket_deadline_poll.hpp",
                "src/sync_stream_socket_deadline_poll.cpp",
                "tools/audit_sync_socket_readiness_identity.py",
            )
        ),
        "release_verifier_requires_socket_capability_surface",
        "a sealed handoff cannot omit implementation, runtime, or audit",
    )
    require(
        "Lexical hygiene audit" in __doc__
        and "does not claim to prove" in __doc__,
        "audit_disclaims_semantic_authority",
        "source vocabulary is not represented as runtime or kernel proof",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-sync-socket-lifetime-readiness-audit-v4",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": "source vocabulary and order do not prove Linux socket identity, descriptor-mutation serialization, timeout behavior, race freedom, or TLS correctness",
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
