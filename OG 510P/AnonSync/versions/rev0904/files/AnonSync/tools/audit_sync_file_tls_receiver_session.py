#!/usr/bin/env python3
"""Lexical hygiene audit for the receiver TLS session ownership boundary.

This inventory checks declared C++ ownership shape, ordering vocabulary, runtime
fixture presence, build wiring, and release retention. It cannot prove lifetime
safety, OpenSSL behavior, scheduler deadlines, byte non-consumption, SQLite or
filesystem durability, peer receipt, clean TLS shutdown, exactly-once effects,
package integrity, or anonymity.
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
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_file_tls_exchange.py"),
    Path("tools/audit_sync_file_tls_receiver_session.py"),
    Path("tools/verify_release_package.py"),
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


def class_body(text: str, declaration: str) -> str:
    return function_body(text, declaration)


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-file-tls-receiver-session-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "source vocabulary and order cannot prove C++ lifetime safety, "
            "OpenSSL behavior, elapsed deadlines, byte non-consumption, "
            "SQLite/file durability, peer receipt, close_notify, exactly-once "
            "effects, package integrity, or anonymity"
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
    runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    design = text["TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md"]
    notes = text["REVISION_NOTES_rev0889.md"]
    self_text = text["tools/audit_sync_file_tls_receiver_session.py"]

    require(
        cmake.count("anonsync_sync_file_tls_receiver_session_source_audit") >= 2
        and "tools/audit_sync_file_tls_receiver_session.py" in cmake,
        "session_audit_is_registered",
        "ordinary CTest retains the dedicated ownership inventory",
    )
    require(
        "preflights" in cmake
        and "move-only session" in cmake
        and "terminalizes" in cmake,
        "build_comment_names_receiver_authority_and_terminal_ownership",
        "the composition leaf is not still documented as a reusable borrowed stream",
    )

    require(
        all(
            token in service_h
            for token in (
                "void preflight_inbound_channel_or_throw(",
                "before a receiver transport consumes any application record bytes",
                "receive_request_or_throw()",
                "re-attests the same live authority immediately before durable work",
            )
        ),
        "service_exports_narrow_early_receiver_preflight",
        "transport can reject configuration before bytes without treating preflight as durable authority",
    )
    preflight = function_body(
        service_cpp,
        "SyncReplicaFileDeliveryService::preflight_inbound_channel_or_throw(",
    )
    require(
        ordered(
            preflight,
            "operation_label.empty()",
            "validate_channel_or_throw(channel_authority, operation_label)",
            "receiver_effect_owner_ == nullptr",
            "requires a receiver file-effect owner",
        ),
        "preflight_validates_live_channel_before_receiver_role",
        "fabricated or stale channel state cannot use role diagnostics as a side door",
    )
    receive = function_body(
        service_cpp, "SyncReplicaFileDeliveryService::receive_request_or_throw("
    )
    require(
        ordered(
            receive,
            "preflight_inbound_channel_or_throw(",
            "channel_authority.context()",
            "decode_sync_replica_file_delivery_request_or_throw(",
            "receiver_effect_owner_->stage_with_diagnostics_or_throw(",
        )
        and receive.count("receiver_effect_owner_ == nullptr") == 0,
        "durable_receive_reuses_one_preflight_invariant",
        "role/channel validation is not duplicated and drifting around request decode",
    )

    exchange = function_body(
        source, "receive_one_sync_replica_file_delivery_over_tls_or_throw("
    )
    require(
        ordered(
            exchange,
            'const std::string preflight_label = label + " inbound preflight"',
            'const std::string receipt_poll_label = label + " receipt poll"',
            "service.preflight_inbound_channel_or_throw(",
            "read_request_until_or_throw(",
            "service.receive_request_or_throw(",
            "write_receipt_until_or_throw(",
        ),
        "receiver_preflight_precedes_first_application_read",
        "all diagnostic allocations and receiver-role proof occur before TLS stream reservation",
    )
    require(
        exchange.count(
            "discard_sync_replica_tls_authenticated_channel_noexcept(channel)"
        ) >= 6
        and ordered(
            exchange,
            "result.disposition = sent",
            "discard_sync_replica_tls_authenticated_channel_noexcept(channel)",
            "return result",
        ),
        "every_terminal_path_including_success_discards_local_capability",
        "local receipt completion cannot authorize a second application record",
    )
    require(
        "Borrowed low-level primitive" in header
        and "unconditional local capability discard" in header
        and "including a" in header
        and "successful receipt write" in header,
        "borrowed_primitive_states_its_terminal_policy",
        "the legacy reference-taking API no longer implies reusable success",
    )

    session = class_body(
        header, "class SyncReplicaFileTlsReceiverSession final"
    )
    require(
        all(
            token in session
            for token in (
                "SyncReplicaTlsAuthenticatedChannel&& channel",
                "const SyncReplicaFileTlsReceiverSession&) = delete",
                "= delete",
                "SyncReplicaFileTlsReceiverSession&& other) noexcept",
                "SyncReplicaFileTlsReceiverSession& operator=(",
                "~SyncReplicaFileTlsReceiverSession() noexcept",
                "bool active() const noexcept",
                "SyncReplicaFileTlsReceiveResult run_or_throw()",
                "void discard_noexcept() noexcept",
                "std::optional<SyncReplicaTlsAuthenticatedChannel> channel_",
                "request_deadline_",
                "receipt_deadline_",
            )
        ),
        "session_is_move_only_and_freezes_exact_channel_and_deadlines",
        "the public type cannot be copied, default-created, or renewed per call",
    )
    constructor = function_body(
        source,
        "SyncReplicaFileTlsReceiverSession::SyncReplicaFileTlsReceiverSession(\n    SyncReplicaFileDeliveryService& service",
    )
    require(
        ordered(
            constructor,
            "label_.empty()",
            'const std::string preflight_label = label_ + " construction preflight"',
            "service.preflight_inbound_channel_or_throw(",
            "channel_.emplace(std::move(channel))",
        ),
        "session_preflights_before_channel_transfer",
        "configuration failure leaves the caller's sole capability unconsumed",
    )
    move_constructor = function_body(
        source,
        "SyncReplicaFileTlsReceiverSession::SyncReplicaFileTlsReceiverSession(\n    SyncReplicaFileTlsReceiverSession&& other) noexcept",
    )
    move_assignment = function_body(
        source,
        "SyncReplicaFileTlsReceiverSession::operator=(\n    SyncReplicaFileTlsReceiverSession&& other) noexcept",
    )
    require(
        "std::exchange(other.service_, nullptr)" in move_constructor
        and "channel_(std::move(other.channel_))" in move_constructor
        and "other.channel_.reset()" in move_constructor
        and ordered(
            move_assignment,
            "discard_noexcept()",
            "std::exchange(other.service_, nullptr)",
            "channel_ = std::move(other.channel_)",
            "other.channel_.reset()",
        ),
        "moves_leave_exactly_one_truthful_active_owner",
        "optional move engagement is explicitly cleared and displaced authority is discarded",
    )
    run = function_body(
        source, "SyncReplicaFileTlsReceiverSession::run_or_throw()"
    )
    discard = function_body(
        source, "SyncReplicaFileTlsReceiverSession::discard_noexcept() noexcept"
    )
    require(
        ordered(
            run,
            "if (!active())",
            "receive_one_sync_replica_file_delivery_over_tls_or_throw(",
            "discard_noexcept()",
            "return result",
            "catch (...)",
            "discard_noexcept()",
        )
        and ordered(
            discard,
            "channel_.has_value()",
            "discard_sync_replica_tls_authenticated_channel_noexcept(*channel_)",
            "channel_.reset()",
            "service_ = nullptr",
        ),
        "session_run_and_cleanup_are_terminal_on_all_paths",
        "one result or exception consumes the exact local application capability",
    )
    require(
        "SSL*" not in session
        and "int descriptor" not in session
        and "close_notify" in header
        and "accept-loop" in header,
        "session_does_not_fake_transport_or_listener_ownership",
        "socket closure, TLS shutdown, enrollment, quotas, and accept policy remain explicit higher-layer gaps",
    )
    require(
        "discard_sync_replica_tls_authenticated_channel_noexcept" in transport_h
        and "channel.state_->poison_noexcept()" in transport_cpp,
        "session_uses_existing_destructive_capability_primitive",
        "the wrapper does not invent a second poison bit or raw SSL mutation path",
    )

    runtime_tokens = (
        "FIONREAD",
        "request-must-remain-buffered",
        "requires a receiver file-effect owner",
        "session-construction preflight consumed buffered application bytes",
        "receiver preflight consumed ciphertext or changed durable evidence",
        "SyncReplicaFileTlsReceiverSession receiver_session",
        "receiver session move left two apparent channel owners",
        "completed receiver session retained application authority",
        "receiver session accepted a second application request",
        "completed borrowed receiver exchange permitted a second record",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "real_tls_runtime_covers_prebyte_rejection_and_one_shot_success",
        "compiled evidence observes queued ciphertext, unchanged durable state, move truthfulness, and terminal success",
    )
    require(
        all(
            token in runtime
            for token in (
                "!std::is_default_constructible_v<",
                "!std::is_copy_constructible_v<",
                "std::is_nothrow_move_constructible_v<",
                "std::is_nothrow_move_assignable_v<",
                "std::is_nothrow_destructible_v<",
                "SyncReplicaFileTlsReceiverSession",
            )
        ),
        "runtime_translation_unit_compiles_session_type_contract",
        "copy/default construction and throwing cleanup cannot silently return",
    )

    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 889",
                "tools/audit_sync_file_tls_receiver_session.py",
                "TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md",
                "REVISION_NOTES_rev0889.md",
            )
        ),
        "release_verifier_retains_rev0889_boundary",
        "a sealed revision cannot omit implementation rationale, notes, or the dedicated audit",
    )
    require(
        all(
            token in design
            for token in (
                "Authority invariant",
                "Pre-byte receiver preflight",
                "Exclusive one-conversation session",
                "Close versus discard",
                "Failure matrix",
                "Online protocol review",
                "Rejected alternatives",
                "Nonclaims and remaining gaps",
                "does not claim",
            )
        )
        and "receiver session" in readme.lower()
        and "preflight" in notes.lower(),
        "design_record_states_invariants_shutdown_boundary_and_nonclaims",
        "mission, close/discard distinction, alternatives, and limitations remain reviewable",
    )
    require(
        "cannot prove" in self_text
        and "close_notify" in self_text
        and "exactly-once" in self_text
        and "anonymity" in self_text,
        "audit_self_limits_its_authority",
        "lexical inventory is not promoted into runtime or protocol proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
