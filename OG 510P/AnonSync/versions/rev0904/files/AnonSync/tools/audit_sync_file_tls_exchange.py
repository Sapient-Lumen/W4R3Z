#!/usr/bin/env python3
"""Lexical hygiene audit for the receiver file/TLS exchange cutpoints.

This inventory checks source shape, ordering vocabulary, and build wiring. It
cannot prove OpenSSL retry semantics, deadlines, SQLite durability, filesystem
publication, crash safety, peer receipt, exactly-once effects, or anonymity.
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
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_file_tls_exchange.hpp"),
    Path("src/sync_replica_file_tls_exchange.cpp"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_replica_tls_poll.hpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_file_tls_exchange.py"),
    Path("tools/audit_sync_file_tls_receiver_session.py"),
    Path("tools/verify_release_package.py"),
    Path("TLS_RECEIVER_EXCHANGE_CUTPOINT_AUDIT_rev0887.md"),
    Path("TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md"),
    Path("REVISION_NOTES_rev0888.md"),
    Path("TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md"),
    Path("REVISION_NOTES_rev0889.md"),
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


def target_block(cmake: str, target: str) -> str:
    starts = (
        cmake.find(f"add_library({target}"),
        cmake.find(f"add_executable({target}"),
    )
    start = next((value for value in starts if value >= 0), -1)
    if start < 0:
        return ""
    end = cmake.find("\nadd_", start + 1)
    return cmake[start:] if end < 0 else cmake[start:end]


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-file-tls-receiver-exchange-audit-v3",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "source vocabulary and order cannot prove OpenSSL retry identity, "
            "scheduler deadlines, SQLite/file durability, crash recovery, "
            "peer receipt, exactly-once effects, package integrity, or anonymity"
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
    readme = text["README.md"]
    service_h = text["src/sync_replica_file_delivery_service.hpp"]
    service_cpp = text["src/sync_replica_file_delivery_service.cpp"]
    header = text["src/sync_replica_file_tls_exchange.hpp"]
    source = text["src/sync_replica_file_tls_exchange.cpp"]
    transport_h = text["src/sync_replica_tls_transport.hpp"]
    transport_cpp = text["src/sync_replica_tls_transport.cpp"]
    poll_h = text["src/sync_replica_tls_poll.hpp"]
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    legacy_design = text["TLS_RECEIVER_EXCHANGE_CUTPOINT_AUDIT_rev0887.md"]
    parent_design = text["TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md"]
    parent_notes = text["REVISION_NOTES_rev0888.md"]
    design = text["TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md"]
    notes = text["REVISION_NOTES_rev0889.md"]
    self_text = text["tools/audit_sync_file_tls_exchange.py"]

    leaf = target_block(cmake, "anonsync_sync_replica_file_tls_exchange")
    test_leaf = target_block(cmake, "anonsync_sync_replica_tls_transport_test")
    require(
        "STATIC" in leaf
        and "src/sync_replica_file_tls_exchange.cpp" in cmake
        and "anonsync_sync_replica_file_delivery_service" in leaf
        and "anonsync_sync_replica_tls_poll" in leaf
        and "-Wall -Wextra -Wpedantic" in leaf,
        "exchange_is_one_strict_composition_leaf",
        "receiver orchestration composes rather than duplicating durable/TLS owners",
    )
    require(
        "anonsync_sync_replica_file_tls_exchange" in test_leaf,
        "real_tls_runtime_links_exchange_leaf",
        "the production seam is exercised through actual TLS and SQLite owners",
    )
    sanitizer_tail = cmake[cmake.find("ANONSYNC_SANITIZER_COMPILE_TARGETS") :]
    require(
        "anonsync_sync_replica_file_tls_exchange" in sanitizer_tail,
        "exchange_is_in_sanitizer_compile_inventory",
        "the new C++ leaf receives sanitizer instrumentation",
    )
    require(
        cmake.count("anonsync_sync_file_tls_exchange_source_audit") >= 2,
        "exchange_source_audit_is_registered",
        "ordinary CTest includes the limited lexical inventory",
    )

    require(
        all(
            token in header
            for token in (
                "enum class SyncReplicaFileTlsReceiveDisposition",
                "PeerClosed",
                "RequestDeadlineExpired",
                "ReceiptDeadlineExpired",
                "ReceiptSent",
                "std::optional<SyncReplicaInboundFileDelivery> inbound",
                "receipt_write_started",
                "receipt_prefix_bytes_written",
                "receipt_prefix_accepted",
                "receipt_body_bytes_written",
                "receive_one_sync_replica_file_delivery_over_tls_or_throw",
            )
        ),
        "public_result_keeps_transport_policy_and_durable_state_distinct",
        "timeouts and local receipt completion do not erase the inbound decision",
    )
    require(
        header.count("std::chrono::steady_clock::time_point") >= 6
        and "independent absolute steady-clock" in header
        and "64 KiB" in header
        and "request_deadline_" in header
        and "receipt_deadline_" in header,
        "public_contract_owns_two_absolute_bounded_cutpoints",
        "the borrowed exchange and exclusive session freeze request and receipt cutpoints rather than renewing one relative budget",
    )
    require(
        "max_request_frame_bytes() const noexcept" in service_h
        and "max_receipt_frame_bytes() const noexcept" in service_h
        and "protocol_limits_.max_request_frame_bytes" in service_h
        and "protocol_limits_.max_receipt_frame_bytes" in service_h,
        "exchange_consumes_service_owned_wire_ceilings",
        "callers cannot silently select looser request or receipt bounds",
    )
    preflight = function_body(
        service_cpp,
        "SyncReplicaFileDeliveryService::preflight_inbound_channel_or_throw(",
    )
    durable_receive = function_body(
        service_cpp, "SyncReplicaFileDeliveryService::receive_request_or_throw("
    )
    require(
        ordered(
            preflight,
            "validate_channel_or_throw(channel_authority, operation_label)",
            "receiver_effect_owner_ == nullptr",
            "requires a receiver file-effect owner",
        )
        and ordered(
            durable_receive,
            "preflight_inbound_channel_or_throw(",
            "decode_sync_replica_file_delivery_request_or_throw(",
            "receiver_effect_owner_->stage_with_diagnostics_or_throw(",
        ),
        "receiver_role_preflight_is_shared_and_re_attested",
        "known local incapacity is rejected before bytes while live authority is re-proved at the durable frontier",
    )

    read = function_body(source, "read_request_until_or_throw(")
    require(
        ordered(
            read,
            "std::chrono::steady_clock::now() >= deadline",
            "begin_sync_replica_tls_record_read_or_throw(",
            "RequireNonblockingSocket",
            "bool retry_pending = false",
        ),
        "request_deadline_precedes_strict_stream_reservation",
        "an already-expired request cannot enter OpenSSL or durable authority",
    )
    require(
        read.count("reader.advance_or_throw()") == 1
        and read.count(
            "poll_and_advance_sync_replica_tls_record_read_or_throw("
        ) == 1
        and "DeadlineExpired" in read
        and "take_frame_or_throw()" in read,
        "request_driver_uses_one_fresh_and_one_exact_retry_site",
        "WANT is polled before retry and no second hidden TLS driver exists",
    )
    require(
        "service.receive_request_or_throw" not in read,
        "partial_request_cannot_reach_durable_service",
        "the transport reader owns bytes only, not evidence or file authority",
    )

    write = function_body(source, "write_receipt_until_or_throw(")
    require(
        ordered(
            write,
            "result.receipt_frame_bytes",
            "std::chrono::steady_clock::now() >= deadline",
            "prepare_sync_replica_tls_record_write_or_throw(",
            "RequireNonblockingSocket",
            "const auto observe_progress",
            "writer.io_started()",
            "writer.prefix_bytes_written()",
            "writer.prefix_complete()",
            "writer.body_bytes_written()",
        ),
        "receipt_deadline_and_bounds_precede_prepared_prefix_owner",
        "an unexpired bounded response owns exact diagnostics before any prefix/body operation is attempted",
    )
    require(
        ordered(
            write,
            "const auto expire_and_discard",
            "observe_progress()",
            "discard_sync_replica_tls_authenticated_channel_noexcept(channel)",
            "bool retry_pending = false",
            "std::chrono::steady_clock::now() >= deadline",
            "return expire_and_discard()",
        ),
        "every_receipt_deadline_snapshots_then_discards",
        "timeout preserves the exact local frontier but never leaves an abandoned application conversation reusable",
    )
    require(
        write.count("writer.advance_or_throw()") == 1
        and write.count(
            "poll_and_advance_sync_replica_tls_record_write_or_throw("
        ) == 1
        and "DeadlineExpired" in write
        and write.count("observe_progress();") >= 4,
        "receipt_driver_uses_one_fresh_and_one_exact_retry_site",
        "one shared prefix/body WANT owner retains the exact pending write operation and exports each observed cutpoint",
    )
    require(
        ordered(
            write,
            "SyncReplicaTlsRecordWritePollProgress::Complete",
            "result.receipt_write_started = true",
            "result.receipt_prefix_bytes_written =",
            "kSyncReplicaTlsRecordPrefixBytes",
            "result.receipt_prefix_accepted = true",
            "result.receipt_body_bytes_written =",
            "result.receipt_frame_bytes",
            "return true",
        )
        and ordered(
            write,
            "SyncReplicaTlsRecordWriteProgress::Complete",
            "result.receipt_write_started = true",
            "result.receipt_prefix_bytes_written =",
            "kSyncReplicaTlsRecordPrefixBytes",
            "result.receipt_prefix_accepted = true",
            "result.receipt_body_bytes_written =",
            "result.receipt_frame_bytes",
            "return true",
        ),
        "only_complete_writer_reports_terminal_receipt_progress",
        "a zero-byte WANT, partial prefix, or partial body cannot be mislabeled as a completed local receipt write",
    )

    exchange = function_body(
        source, "receive_one_sync_replica_file_delivery_over_tls_or_throw("
    )
    require(
        ordered(
            exchange,
            'const std::string preflight_label = label + " inbound preflight"',
            'const std::string request_label = label + " request"',
            'const std::string receipt_poll_label = label + " receipt poll"',
            "service.preflight_inbound_channel_or_throw(",
            "read_request_until_or_throw(",
            "switch (request.terminal)",
            "service.receive_request_or_throw(",
            "write_receipt_until_or_throw(",
        ),
        "preflight_then_complete_request_then_effect_then_receipt",
        "the load-bearing production order rejects known local incapacity before bytes and re-attests at the durable frontier",
    )
    require(
        exchange.count(
            "discard_sync_replica_tls_authenticated_channel_noexcept(channel)"
        ) >= 6
        and "result.inbound.emplace" in exchange
        and ordered(
            exchange,
            "result.disposition = sent",
            "discard_sync_replica_tls_authenticated_channel_noexcept(channel)",
            "return result",
        ),
        "all_terminal_paths_discard_without_erasing_durable_result",
        "peer close, timeout, malformed frames, response failure, and successful one-shot completion cannot reuse conversation framing",
    )
    require(
        "std::is_nothrow_move_constructible_v<" in source
        and "SyncReplicaInboundFileDelivery" in source
        and "SyncReplicaFileTlsReceiveResult" in source,
        "post_effect_result_handoff_is_statically_nothrow",
        "returning a timeout decision adds no new move allocation frontier",
    )

    require(
        "discard_sync_replica_tls_authenticated_channel_noexcept" in transport_h
        and "friend void discard_sync_replica_tls_authenticated_channel_noexcept"
        in transport_h
        and "channel.state_->poison_noexcept()" in transport_cpp,
        "transport_exposes_one_destructive_application_discard",
        "conversation abandonment invalidates capability without fake shutdown evidence",
    )
    require(
        "absolute steady-clock deadline" in poll_h
        and "at most one" in poll_h,
        "exchange_reuses_existing_bounded_poll_contract",
        "the orchestration leaf does not invent a second readiness model",
    )

    required_runtime_tokens = (
        "test_file_tls_receiver_exchange",
        "ReceiptSent",
        "ReceiptDeadlineExpired",
        "RequestDeadlineExpired",
        "AlreadyPublished",
        "expired receiver exchange emitted receipt ciphertext",
        "file TLS partial-timeout exchange",
        "partial request timeout lost its exact local framing cutpoint",
        "malformed complete request left the application stream reusable",
        "sender.snapshot_or_throw().outbox.empty()",
        "file TLS receiver receipt-prefix WANT",
        "receipt-prefix WANT was not retained as an exact post-effect timeout",
        "receipt-prefix WANT lost or repeated the durable visible effect",
        "receipt-prefix WANT locally settled the sender without a receipt",
        "FIONREAD",
        "request-must-remain-buffered",
        "session-construction preflight consumed buffered application bytes",
        "receiver preflight consumed ciphertext or changed durable evidence",
        "SyncReplicaFileTlsReceiverSession receiver_session",
        "receiver session accepted a second application request",
        "completed borrowed receiver exchange permitted a second record",
    )
    require(
        all(token in runtime for token in required_runtime_tokens),
        "real_tls_runtime_covers_success_timeout_retry_and_malformed",
        "compiled evidence exercises both durable and stream cutpoints",
    )
    require(
        "template <typename WriteContinuation>" in runtime
        and "advance_tls_write_until_want(" in runtime,
        "shared_test_driver_accepts_raw_and_file_continuations",
        "the recovered rev0887 fixture no longer duplicates or mis-types progress loops",
    )
    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 888",
                "TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md",
                "REVISION_NOTES_rev0888.md",
                "revision_number >= 889",
                "src/sync_replica_file_tls_exchange.hpp",
                "src/sync_replica_file_tls_exchange.cpp",
                "tools/audit_sync_file_tls_exchange.py",
                "tools/audit_sync_file_tls_receiver_session.py",
                "TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md",
                "REVISION_NOTES_rev0889.md",
            )
        ),
        "release_verifier_requires_prefix_resume_and_session_surface",
        "a sealed rev0889 cannot omit the inherited first-prefix frontier or the pre-byte and one-shot ownership boundary",
    )
    require(
        all(
            token in design
            for token in (
                "Authority invariant",
                "Pre-byte receiver preflight",
                "Exclusive one-conversation session",
                "Successful receipt is terminal too",
                "Failure matrix",
                "Online protocol review",
                "Rejected alternatives",
                "Nonclaims and remaining gaps",
                "does not claim",
            )
        )
        and "receiver session" in readme.lower()
        and "preflight" in notes.lower()
        and "resumable" in parent_notes.lower()
        and "Receiver post-effect behavior" in parent_design
        and "Why two deadlines matter" in legacy_design,
        "design_record_states_invariants_lineage_and_nonclaims",
        "source changes retain mission, inherited prefix/deadline rationale, current ownership reasoning, and explicit limitations",
    )
    require(
        "cannot prove" in self_text
        and "exactly-once" in self_text
        and "anonymity" in self_text,
        "audit_self_limits_its_authority",
        "lexical inventory is not promoted into semantic evidence",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
