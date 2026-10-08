#!/usr/bin/env python3
"""Lexical hygiene inventory for callbacks near authority-bearing operations.

This audit classifies the remaining reviewed callback surfaces and verifies that
file payload delivery now uses immutable value-owned snapshot authority instead
of caller code after a durable outbox claim exists. It deliberately does not
claim to prove callback purity, reentrancy safety, transaction isolation,
cryptographic collision resistance, memory exhaustion behavior, transport
liveness, or absence of indirect calls. Compiled adversarial tests and
architectural ownership rules carry those semantic obligations.
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
        "file_header": root / "src/sync_replica_file_delivery_service.hpp",
        "file_source": root / "src/sync_replica_file_delivery_service.cpp",
        "snapshot_header": root / "src/sync_replica_file_payload_snapshot.hpp",
        "snapshot_source": root / "src/sync_replica_file_payload_snapshot.cpp",
        "inventory_header": root / "src/sync_replica_file_content_inventory.hpp",
        "inventory_source": root / "src/sync_replica_file_content_inventory.cpp",
        "file_runtime": root / "tests/sync_replica_file_delivery_service_test.cpp",
        "tls_header": root / "src/sync_replica_file_tls_server.hpp",
        "tls_source": root / "src/sync_replica_file_tls_server.cpp",
        "membership_header": root / "src/sync_replica_tls_membership_snapshot.hpp",
        "membership_source": root / "src/sync_replica_tls_membership_snapshot.cpp",
        "membership_owner_header": root / "src/sync_replica_tls_membership_sqlite_owner.hpp",
        "membership_anchored_header": root / "src/sync_replica_tls_membership_anchored_owner.hpp",
        "ledger": root / "src/sqlite_replay_ledger.cpp",
        "ledger_bridge": root / "src/sqlite_replay_ledger_selftest_bridge.hpp",
        "peer_claim_header": root / "src/sync_peer_ingress_claim.hpp",
        "peer_claim_source": root / "src/sync_peer_ingress_claim.cpp",
        "peer_wire_header": root / "src/sync_peer_ingress_wire.hpp",
        "peer_wire_source": root / "src/sync_peer_ingress_wire.cpp",
        "peer_lifecycle": root / "src/sync_peer_ingress_lifecycle.cpp",
        "authorizer": root / "src/persistence/sqlite_authorizer_owner.hpp",
        "tls_runtime": root / "tests/sync_replica_tls_transport_test.cpp",
        "cmake": root / "CMakeLists.txt",
        "verifier": root / "tools/verify_release_package.py",
    }
    missing = sorted(
        str(path.relative_to(root)) for path in paths.values() if not path.is_file()
    )
    text = {
        name: path.read_text(encoding="utf-8") if path.is_file() else ""
        for name, path in paths.items()
    }
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({
            "check_id": check_id,
            "passed": bool(condition),
            "detail": detail,
        })

    require(not missing, "required_files_exist", f"missing={missing}")

    function_occurrences: dict[str, int] = {}
    for path in sorted((root / "src").rglob("*")):
        if path.suffix not in {".cpp", ".hpp"}:
            continue
        count = path.read_text(encoding="utf-8").count("std::function")
        if count:
            function_occurrences[str(path.relative_to(root))] = count
    expected_occurrences = {
        "src/sqlite_replay_ledger.cpp": 2,
        "src/sqlite_replay_ledger_selftest_bridge.hpp": 1,
        "src/sync_peer_ingress_claim.cpp": 1,
        "src/sync_peer_ingress_claim.hpp": 1,
        "src/sync_peer_ingress_lifecycle.cpp": 1,
        "src/sync_peer_ingress_wire.cpp": 1,
        "src/sync_peer_ingress_wire.hpp": 1,
    }
    require(
        function_occurrences == expected_occurrences,
        "std_function_inventory_is_exact_and_reviewed",
        f"actual={function_occurrences}",
    )

    tls_text = (
        text["tls_header"] + text["tls_source"] +
        text["membership_header"] + text["membership_source"] +
        text["membership_owner_header"] + text["membership_anchored_header"]
    )
    require(
        "std::function" not in tls_text
        and "SyncReplicaTlsPeerActorResolver" not in tls_text
        and "resolve_peer_actor" not in tls_text,
        "live_authenticated_server_has_no_membership_callback",
        "certificate-to-actor lookup cannot re-enter arbitrary membership code",
    )
    require(
        "std::shared_ptr<const State> state_" in text["membership_owner_header"]
        and "friend class SyncReplicaTlsMembershipSqliteOwner"
            in text["membership_owner_header"]
        and "SyncReplicaTlsMembershipAuthority membership_"
            in text["membership_anchored_header"]
        and "SyncReplicaTlsAnchoredMembershipAuthority membership"
            in text["tls_header"]
        and "SyncReplicaTlsMembershipAuthority membership" not in text["tls_header"]
        and "SyncReplicaTlsMembershipSnapshot membership" not in text["tls_header"],
        "tls_membership_is_owner_emitted_value_owned_const_state",
        "the accepted-session owner consumes only independently anchored immutable committed authority by value",
    )

    inventory_text = text["inventory_header"] + text["inventory_source"]
    snapshot_text = text["snapshot_header"] + text["snapshot_source"]
    file_surface = (
        text["file_header"] + text["file_source"] + snapshot_text + inventory_text
    )
    require(
        "std::function" not in file_surface
        and "SyncReplicaFilePayloadSource" not in file_surface
        and "<functional>" not in file_surface
        and "template <typename PayloadSource>" in text["file_source"],
        "file_payload_callback_surface_is_retired",
        "the production file-delivery path accepts no caller executable for payload lookup",
    )
    require(
        "std::shared_ptr<const State> state_" in text["snapshot_header"]
        and "std::vector<std::string> payloads" in text["snapshot_header"]
        and "SyncReplicaFilePayloadSnapshot payload_snapshot" in text["file_header"],
        "file_payload_authority_is_value_owned_const_state",
        "payload bytes are copied and hashed before any service call can mint a lease",
    )
    require(
        "class SyncReplicaFileContentInventory final" in text["inventory_header"]
        and "std::shared_ptr<const State> state_" in text["inventory_header"]
        and "std::vector<std::string> content_sha256s" in text["inventory_source"]
        and "std::sort(content_sha256s.begin(), content_sha256s.end())"
            in text["inventory_source"]
        and "std::span<const std::string_view>" not in file_surface
        and "payload_source.content_inventory()" in text["file_source"],
        "payload_digest_inventory_is_owned_not_borrowed",
        "claim selection receives bounded shared-const digest ownership rather than caller-managed views",
    )

    claim = body(
        text["file_source"],
        "SyncReplicaFileDeliveryService::\n    "
        "claim_next_request_from_payload_source_or_throw(",
    )
    require(
        ordered(
            claim,
            "validate_channel_or_throw",
            "payload_source.require_folder_or_throw",
            "payload_source.preflight_or_throw",
            "const SyncReplicaDeliveryChannelContext channel =",
            "claim_next_outbox_for_delivery_or_throw",
            "payload = payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
        ),
        "immutable_payload_lookup_is_scoped_then_exactly_released_and_reproved",
        "scope checks precede mutation; lookup/copy failure releases the exact claim before dispatch attestation",
    )
    guard_suffix = claim[claim.find("guard_outbox_claim_for_dispatch_or_throw"):]
    require(
        "No caller code or network" in guard_suffix
        and "I/O is permitted while the SQLite writer capability is held" in guard_suffix
        and "copy_payload_for_operation_or_throw" not in guard_suffix,
        "payload_lookup_does_not_run_under_sqlite_writer_guard",
        "the durable serialization window contains only reviewed local construction",
    )
    require(
        "kSyncReplicaFilePayloadSnapshotMaxEntries" in snapshot_text
        and "max_payload_bytes" in snapshot_text
        and "max_retained_bytes" in snapshot_text
        and "std::sort" in text["snapshot_source"]
        and "std::adjacent_find" in text["snapshot_source"]
        and "anonsync:sync-replica-file-payload-snapshot:v1" in snapshot_text,
        "payload_snapshot_has_explicit_cardinality_byte_and_identity_bounds",
        "immutable replacement authority is finite, canonicalized, and structurally attestable",
    )

    ledger = text["ledger"]
    pending_impl = body(ledger, "std::string sqlite_effect_pending_report_json_impl(")
    production_pending = body(ledger, "std::string sqlite_effect_pending_report_json(")
    selftest_pending = body(
        ledger,
        "std::string sqlite_effect_pending_report_json_for_selftest(",
    )
    require(
        "PendingReportAfterVerificationHook" in pending_impl
        and "if (after_verification) after_verification();" in pending_impl
        and "return sqlite_effect_pending_report_json_impl(ledger_path, {});" in production_pending,
        "sqlite_interposition_hook_is_empty_on_production_entry",
        "normal report generation cannot inject caller code into its read transaction",
    )
    require(
        "after_verification" in selftest_pending
        and "for_selftest" in text["ledger_bridge"]
        and "sqlite_effect_pending_report_json_for_selftest" in text["ledger_bridge"],
        "sqlite_interposition_hook_is_named_and_declared_selftest_only",
        "the deliberate race-test seam is not presented as a production API",
    )

    peer_text = (
        text["peer_claim_header"] + text["peer_claim_source"] +
        text["peer_wire_header"] + text["peer_wire_source"] +
        text["peer_lifecycle"]
    )
    function_lines = [
        line.strip() for line in peer_text.splitlines() if "std::function" in line
    ]
    require(
        len(function_lines) == 5
        and "run_sync_peer_ingress_lifecycle_selftests" in text["peer_lifecycle"]
        and "run_peer_transport_ingress_claim_generation_selftests" in text["peer_claim_header"]
        and "run_peer_transport_ingress_wire_codec_selftests" in text["peer_wire_header"],
        "peer_ingress_std_functions_are_selftest_assertion_sinks",
        "production peer-ingress state transitions do not accept caller callbacks",
    )
    require(
        "using SqliteAuthorizerCallback = int (*)" in text["authorizer"]
        and "sqlite3_set_authorizer" in text["authorizer"],
        "sqlite_authorizer_callback_is_typed_as_c_abi_policy_hook",
        "the database authorizer is distinguished from application std::function seams",
    )

    tls_runtime_tokens = (
        "immutable TLS membership digest depended on caller entry order",
        "TLS membership preaccept mismatch reached durable authority",
        "TLS server authorized or misattributed a certificate-valid unmapped peer",
    )
    require(
        all(token in text["tls_runtime"] for token in tls_runtime_tokens),
        "removed_tls_callback_has_compiled_replacement_matrix",
        "value lookup and no-mutation outcomes are exercised by real TLS tests",
    )
    file_runtime_tokens = (
        "payload snapshot digest depends on caller insertion order",
        "cross-folder payload snapshot reached durable owner work",
        "immutable payload inventory did not select the first available canonical intent",
        "unavailable head-of-line payload consumed attempt or retry authority",
        "post-selection size mismatch did not exact-release its bounded live attempt",
        "claim expiring after payload lookup escaped as an outbound frame",
    )
    require(
        all(token in text["file_runtime"] for token in file_runtime_tokens),
        "removed_payload_callback_has_compiled_replacement_matrix",
        "immutability, scope, no-attempt availability selection, contradiction release, and post-lookup expiry are executable evidence",
    )
    require(
        text["cmake"].count("anonsync_authority_callback_boundaries_source_audit") >= 2,
        "callback_inventory_is_registered_with_ctest",
        "the reviewed callback set cannot drift silently in ordinary validation",
    )
    require(
        "tools/audit_authority_callback_boundaries.py" in text["verifier"],
        "release_verifier_requires_callback_inventory",
        "a sealed revision cannot omit the audit after changing callback authority",
    )
    require(
        "Lexical hygiene inventory" in (__doc__ or "")
        and "does not" in (__doc__ or "")
        and "cryptographic collision resistance" in (__doc__ or ""),
        "audit_disclaims_semantic_authority",
        "source vocabulary is not represented as behavioral or cryptographic proof",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-authority-callback-boundaries-source-audit-v2",
        "scope": "lexical-inventory-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and inventory do not prove callback purity, "
            "cryptographic collision resistance, memory exhaustion behavior, "
            "reentrancy safety, bounded execution, or transaction semantics"
        ),
        "root": str(root),
        "passed": passed,
        "passed_checks": sum(bool(check["passed"]) for check in checks),
        "total_checks": len(checks),
        "checks": checks,
        "violations": [
            str(check["check_id"]) for check in checks if not check["passed"]
        ],
    }
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
