#!/usr/bin/env python3
"""Lexical hygiene audit for the duplex bounded TLS poll owner.

This inventory checks source shape and wiring. It does not prove scheduler
behavior, signal timing, syscall counts, OpenSSL semantics, race freedom,
deadline bounds, delivery, or package correctness.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_tls_poll.hpp"),
    Path("src/sync_replica_tls_poll.cpp"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_tls_poll_owner.py"),
    Path("tools/test_verify_release_package_policy.py"),
    Path("tools/verify_release_package.py"),
    Path("TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def target_block(cmake: str, target: str) -> str:
    starts = [
        cmake.find(f"add_library({target}"),
        cmake.find(f"add_executable({target}"),
    ]
    start = next((value for value in starts if value >= 0), -1)
    if start < 0:
        return ""
    end = cmake.find("\nadd_", start + 1)
    return cmake[start:] if end < 0 else cmake[start:end]


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start + len(signature))
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
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-tls-duplex-poll-owner-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "source vocabulary and order cannot prove scheduler timing, signal "
            "interleavings, exact syscall count, OpenSSL retry semantics, race "
            "freedom, package correctness, or end-to-end delivery"
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
    header = text["src/sync_replica_tls_poll.hpp"]
    source = text["src/sync_replica_tls_poll.cpp"]
    transport = text["src/sync_replica_tls_transport.hpp"]
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    policy_test = text["tools/test_verify_release_package_policy.py"]
    verifier = text["tools/verify_release_package.py"]
    design = text["TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md"]
    self_text = text["tools/audit_sync_tls_poll_owner.py"]

    leaf = target_block(cmake, "anonsync_sync_replica_tls_poll")
    test_leaf = target_block(cmake, "anonsync_sync_replica_tls_transport_test")
    require(
        "ANONSYNC_SYNC_REPLICA_TLS_POLL_SOURCE" in leaf
        and "src/sync_replica_tls_poll.cpp" in cmake
        and "STATIC" in leaf
        and "anonsync_sync_replica_tls_transport" in leaf
        and "-Wall -Wextra -Wpedantic" in leaf,
        "poll_owner_is_one_strict_transport_leaf",
        "readiness scheduling composes rather than duplicates TLS state",
    )
    require(
        "anonsync_sync_replica_tls_poll" in test_leaf,
        "real_tls_runtime_links_poll_owner",
        "the owner is exercised through actual TLS continuations",
    )
    sanitizer_tail = cmake[cmake.find("ANONSYNC_SANITIZER_COMPILE_TARGETS") :]
    require(
        "anonsync_sync_replica_tls_poll" in sanitizer_tail,
        "poll_owner_is_in_sanitizer_compile_inventory",
        "the new C++ leaf receives sanitizer instrumentation",
    )
    require(
        cmake.count("anonsync_sync_tls_poll_owner_source_audit") >= 2
        and "anonsync_release_path_policy_test" in cmake,
        "poll_and_release_policy_tests_are_registered",
        "ordinary CTest includes both authority surfaces",
    )

    require(
        all(
            token in header
            for token in (
                "enum class SyncReplicaTlsRecordReadPollProgress",
                "enum class SyncReplicaTlsRecordWritePollProgress",
                "DeadlineExpired",
                "PeerClosed",
                "poll_and_advance_sync_replica_tls_record_read_or_throw",
                "poll_and_advance_sync_replica_tls_record_write_or_throw",
            )
        ),
        "public_api_preserves_read_and_write_result_classes",
        "deadline, WANT, progress, completion, and clean close remain distinct",
    )
    require(
        header.count("std::chrono::steady_clock::time_point deadline") == 2
        and "absolute steady-clock deadline" in header
        and "at most one" in header,
        "public_contract_uses_absolute_deadline_and_one_step",
        "relative budget renewal and hidden progress loops are excluded",
    )
    require(
        "kSyncReplicaTlsRecordWriteStepBytes" in transport
        and "64U * 1024U" in transport,
        "transport_retains_public_bounded_write_step",
        "poll composition does not erase the per-operation work ceiling",
    )

    generic = function_body(source, "poll_and_advance_or_throw(")
    require(
        generic.count("continuation.advance_or_throw()") == 1,
        "one_wakeup_can_issue_at_most_one_tls_operation",
        "the shared poll leaf contains no TLS progress loop",
    )
    require(
        ordered(
            generic,
            "continuation.pending_readiness_or_throw()",
            "before_poll",
            "if (before_poll >= deadline)",
            "::poll",
            "if (result < 0)",
            "poll_errno == EINTR || poll_errno == EAGAIN",
            "continue",
            "if (result == 0)",
            "descriptor_event.revents == 0",
            "std::chrono::steady_clock::now() >= deadline",
            "continuation.advance_or_throw()",
        ),
        "poll_loop_reproves_interrupts_and_rechecks_cutpoint",
        "a cached target and renewed relative timeout cannot cross interruption",
    )
    timeout = function_body(source, "poll_timeout_milliseconds(")
    require(
        all(
            token in timeout
            for token in (
                "if (deadline <= now) return 0",
                "std::chrono::milliseconds(INT_MAX)",
                "++timeout",
                "return timeout > 0 ? timeout : 1",
            )
        ),
        "timeout_rounds_up_clamps_and_avoids_early_zero",
        "syscall granularity remains subordinate to the absolute cutpoint",
    )
    require(
        "std::chrono::steady_clock::is_steady" in source
        and "static_assert" in source,
        "monotonic_clock_requirement_is_compile_time_checked",
        "wall-clock adjustment cannot become poll deadline authority",
    )
    require(
        "POLLIN" in source
        and "POLLOUT" in source
        and "Error, hangup, and invalid bits are advisory wakeups" in source,
        "typed_readiness_and_advisory_error_semantics_are_documented",
        "raw poll flags are not promoted into protocol truth",
    )
    require(
        "map_read_progress_or_throw" in source
        and "map_write_progress_or_throw" in source
        and "unknown TLS read progress value" in source
        and "unknown TLS write progress value" in source,
        "read_and_write_mappings_are_exhaustive_and_fail_closed",
        "future transport states cannot silently collapse",
    )
    require(
        source.count("cannot own a bounded TLS readiness poll on this platform") == 2,
        "unsupported_platforms_fail_closed_for_both_directions",
        "no implicit blocking or weak fallback is invented",
    )

    require(
        all(
            phrase in runtime
            for phrase in (
                "TLS poll before read WANT",
                "TLS already-expired read poll",
                "TLS bounded idle read poll",
                "one read poll step crossed the prefix/body cutpoint",
                "TLS duplex poll clean close",
                "TLS duplex poll EINTR",
            )
        ),
        "runtime_covers_read_preconditions_deadline_framing_close_and_signal",
        "real TLS exercises the read-side policy boundaries",
    )
    require(
        all(
            phrase in runtime
            for phrase in (
                "TLS poll before write WANT",
                "TLS already-expired write poll",
                "TLS bounded idle write poll",
                "TLS duplex cooperative transfer",
                'label + " write poll"',
                "write_poll_operations > 0U",
                "kSyncReplicaTlsRecordWriteStepBytes",
                "received.has_value() && *received == frame",
            )
        ),
        "runtime_covers_write_retention_bounded_progress_and_exact_bytes",
        "the shared owner is exercised under genuine backpressure",
    )
    require(
        runtime.count("poll_and_advance_sync_replica_tls_record_read_or_throw") >= 7
        and runtime.count("poll_and_advance_sync_replica_tls_record_write_or_throw") >= 4,
        "runtime_uses_both_public_overloads_at_multiple_frontiers",
        "coverage is not one superficial construction test",
    )

    require(
        "directory_parts = path.parts[:-1]" in verifier
        and "FORBIDDEN_BUILD_DIRECTORY_BASENAMES = {\"build\"}" in verifier
        and "FORBIDDEN_BUILD_DIRECTORY_PREFIXES" in verifier,
        "release_verifier_separates_directories_from_basename",
        "evidence names and generated trees are classified at the right boundary",
    )
    require(
        all(
            token in policy_test
            for token in (
                '"build/CMakeCache.txt"',
                '"build-debug/src/object.o"',
                '"cmake-build-release/bin/anonsync_core"',
                "build-shape-observation.json",
                '"build-report.json"',
            )
        ),
        "release_path_policy_has_positive_and_negative_runtime_matrix",
        "the former false positive and actual build directory are both covered",
    )
    require(
        all(
            token in verifier
            for token in (
                '"src/sync_replica_tls_poll.hpp"',
                '"src/sync_replica_tls_poll.cpp"',
                '"tools/audit_sync_tls_poll_owner.py"',
                '"tools/test_verify_release_package_policy.py"',
                '"TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md"',
            )
        ),
        "revision_package_inventory_requires_new_authority_surface",
        "a sealed rev0886 cannot silently omit the poll owner or policy regression",
    )

    require(
        all(
            token in design
            for token in (
                "https://man7.org/linux/man-pages/man2/poll.2.html",
                "https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html",
                "https://docs.openssl.org/3.5/man3/SSL_get_error/",
                "https://docs.openssl.org/3.5/man3/SSL_write/",
                "not a production event loop",
                "peer receipt",
                "lexical hygiene",
            )
        ),
        "design_records_primary_sources_residual_gap_and_nonclaims",
        "the audit does not promote this leaf into completed product delivery",
    )
    require(
        "does not prove" in self_text
        and "lexical-hygiene-not-semantic-proof" in self_text,
        "audit_self_identifies_as_nonsemantic_hygiene",
        "source inventory cannot masquerade as runtime proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
