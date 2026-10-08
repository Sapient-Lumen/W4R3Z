#!/usr/bin/env python3
"""Lexical hygiene audit for immutable file-payload snapshot authority.

The checks below inventory reviewed source shape, CMake/package retention, and
runtime-test vocabulary. They do not prove SHA-256 collision resistance,
allocation success, C++ object-model behavior, SQLite transaction semantics,
thread safety, network delivery, or crash recovery. Compiler, sanitizer,
runtime, stress, and package evidence remain load-bearing.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_file_content_inventory.hpp"),
    Path("src/sync_replica_file_content_inventory.cpp"),
    Path("src/sync_replica_file_payload_snapshot.hpp"),
    Path("src/sync_replica_file_payload_snapshot.cpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_file_tls_dispatch.hpp"),
    Path("src/sync_replica_file_tls_dispatch.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_authority_callback_boundaries.py"),
    Path("tools/audit_sync_replica_file_delivery.py"),
    Path("tools/audit_sync_file_payload_snapshot.py"),
    Path("tools/verify_release_package.py"),
    Path("FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


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


def cmake_call(text: str, command_prefix: str) -> str:
    return delimited_body(text, command_prefix, "(", ")")


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
        "format": "anonsync-sync-file-payload-snapshot-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "source vocabulary and source order do not prove collision "
            "resistance, allocation success, transaction semantics, or runtime behavior"
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
    inventory_header = text["src/sync_replica_file_content_inventory.hpp"]
    inventory_source = text["src/sync_replica_file_content_inventory.cpp"]
    header = text["src/sync_replica_file_payload_snapshot.hpp"]
    source = text["src/sync_replica_file_payload_snapshot.cpp"]
    service_header = text["src/sync_replica_file_delivery_service.hpp"]
    service = text["src/sync_replica_file_delivery_service.cpp"]
    dispatch_header = text["src/sync_replica_file_tls_dispatch.hpp"]
    dispatch = text["src/sync_replica_file_tls_dispatch.cpp"]
    owner_header = text["src/sync_replica_sqlite_owner.hpp"]
    owner = text["src/sync_replica_sqlite_owner.cpp"]
    owner_runtime = text["tests/sync_replica_sqlite_owner_test.cpp"]
    runtime = text["tests/sync_replica_file_delivery_service_test.cpp"]
    tls_runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    callback_audit = text["tools/audit_authority_callback_boundaries.py"]
    delivery_audit = text["tools/audit_sync_replica_file_delivery.py"]
    verifier = text["tools/verify_release_package.py"]
    design = text["FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md"]
    self_text = text["tools/audit_sync_file_payload_snapshot.py"]

    service_sources = cmake_call(
        cmake, "set(ANONSYNC_SYNC_REPLICA_FILE_DELIVERY_SERVICE_SOURCE"
    )
    model_sources = cmake_call(
        cmake, "set(ANONSYNC_SYNC_REPLICA_MODEL_SOURCE"
    )
    service_link = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_replica_file_delivery_service"
    )
    require(
        "src/sync_replica_file_delivery_service.cpp" in service_sources
        and "src/sync_replica_file_payload_snapshot.cpp" in service_sources
        and "src/sync_replica_file_content_inventory.cpp" in model_sources
        and cmake.count("add_library(anonsync_sync_replica_file_payload_snapshot") == 0
        and "PRIVATE anonsync_sha256_digest" in service_link,
        "snapshot_is_coowned_by_existing_narrow_service_target",
        "the refactor adds no link-granularity façade and keeps hashing implementation-private",
    )

    require(
        all(
            token in header
            for token in (
                "class SyncReplicaFilePayloadSnapshot final",
                "std::vector<std::string> payloads",
                "std::shared_ptr<const State> state_",
                "SyncReplicaFileContentInventory content_inventory() const",
                "const SyncReplicaFilePayloadSnapshot&) noexcept = default",
                "SyncReplicaFilePayloadSnapshot&&) noexcept = default",
            )
        ),
        "snapshot_is_value_owned_copyable_const_state",
        "construction owns bytes and later copies share only inaccessible immutable state",
    )
    require(
        all(
            token in inventory_header + inventory_source
            for token in (
                "class SyncReplicaFileContentInventory final",
                "kSyncReplicaFileContentInventoryMaxEntries",
                "std::shared_ptr<const State> state_",
                "std::vector<std::string> content_sha256s",
                "content_sha256s.size() >",
                "contains an invalid content digest",
                "std::sort(content_sha256s.begin(), content_sha256s.end())",
                "std::adjacent_find",
                "contains duplicate content authority",
                "file content inventory does not match owner folder identity",
            )
        )
        and "std::string_view" not in function_body(
            inventory_source,
            "SyncReplicaFileContentInventory::SyncReplicaFileContentInventory(",
        ),
        "content_inventory_owns_canonical_bounded_digest_state",
        "durable claim selection never borrows caller-controlled digest storage",
    )
    require(
        "std::function" not in header + source + service_header + service + dispatch_header + dispatch
        and "<functional>" not in header + source + service_header + service + dispatch_header + dispatch
        and "SyncReplicaFilePayloadSource" not in header + source + service_header + service + dispatch_header + dispatch
        and "template <typename PayloadSource>" in service + dispatch,
        "production_payload_path_has_no_executable_callback_surface",
        "ordinary callers cannot inject code between claim mutation and dispatch attestation",
    )

    limits = function_body(
        source, "validate_sync_replica_file_payload_snapshot_limits_or_throw("
    )
    require(
        all(
            token in header + limits
            for token in (
                "kSyncReplicaFilePayloadSnapshotMaxEntries",
                "max_entries",
                "max_payload_bytes",
                "max_retained_bytes",
                "limits.max_entries == 0U",
                "limits.max_entries > kSyncReplicaFilePayloadSnapshotMaxEntries",
                "limits.max_payload_bytes > limits.max_retained_bytes",
                "std::numeric_limits<std::size_t>::max()",
            )
        ),
        "snapshot_limits_are_positive_hard_capped_and_addressable",
        "cardinality, per-object, aggregate, and platform-addressability limits are explicit",
    )

    constructor = function_body(
        source, "SyncReplicaFilePayloadSnapshot::SyncReplicaFilePayloadSnapshot("
    )
    require(
        ordered(
            constructor,
            "label.empty()",
            "sync_id_is_valid(folder_id)",
            "validate_sync_replica_file_payload_snapshot_limits_or_throw",
            "payloads.size() > limits.max_entries",
            "entries.reserve(payloads.size())",
            "payload_bytes > limits.max_payload_bytes",
            "payload_bytes > limits.max_retained_bytes - retained_bytes",
            "sha256_hex(payload)",
            "std::move(payload)",
            "std::sort",
            "std::adjacent_find",
            "duplicate content authority",
            "std::make_shared<State>()",
            "content_sha256s.reserve",
            "content_sha256s.push_back",
            "SyncReplicaFileContentInventory(",
            "snapshot_digest_or_throw",
        ),
        "constructor_owns_hashes_bounds_canonicalizes_and_rejects_duplicates",
        "all caller bytes become finite private state before the snapshot can authorize a service call",
    )
    require(
        "SyncReplicaFileContentInventory content_inventory" in source
        and ordered(
            function_body(
                source,
                "SyncReplicaFilePayloadSnapshot::content_inventory() const",
            ),
            "require_state_or_throw",
            "return state.content_inventory",
        ),
        "snapshot_exposes_owned_inventory_without_digest_borrowing",
        "claim selection receives cheap shared const ownership rather than caller-backed views",
    )
    require(
        "anonsync:sync-replica-file-payload-snapshot:v1" in source
        and ordered(
            function_body(source, "std::string snapshot_digest_or_throw("),
            "kSnapshotDigestDomain",
            "folder_id",
            "limits.max_entries",
            "limits.max_payload_bytes",
            "limits.max_retained_bytes",
            "entries.size()",
            "retained_bytes",
            "entry.content_sha256",
            "entry.bytes.size()",
        )
        and "structural local evidence" in header
        and "not a signature" in header,
        "snapshot_digest_is_domain_separated_canonical_and_non_authenticating",
        "diagnostic identity binds scope, budgets, cardinality, digests, and sizes without overclaiming signature authority",
    )

    lookup = function_body(
        source, "SyncReplicaFilePayloadSnapshot::copy_payload_for_operation_or_throw("
    )
    require(
        "[[nodiscard]] std::string copy_payload_for_operation_or_throw(" in header
        and "std::string_view copy_payload_for_operation_or_throw(" not in header + source,
        "lookup_returns_owned_bytes_not_a_dangling_view",
        "payload authority cannot escape the snapshot through a lifetime-sensitive borrowed view",
    )
    require(
        ordered(
            lookup,
            "require_state_or_throw",
            "operation.kind != SyncReplicaValueKind::File",
            "is_lowercase_sha256_hex(operation.content_sha256)",
            "operation.size_bytes > state.limits.max_payload_bytes",
            "std::lower_bound",
            "has no payload for the claimed operation",
            "found->bytes.size() != operation.size_bytes",
            "return found->bytes",
        ),
        "lookup_requires_exact_kind_digest_presence_and_size",
        "content identity alone cannot bypass operation kind, configured size budget, or declared byte count",
    )
    scope = function_body(
        source, "SyncReplicaFilePayloadSnapshot::require_folder_or_throw("
    )
    require(
        ordered(
            scope,
            "require_state_or_throw",
            "sync_id_is_valid(folder_id)",
            "state.folder_id != folder_id",
            "does not match service folder identity",
        ),
        "snapshot_scope_is_explicit_and_fail_closed",
        "a snapshot from another folder cannot spend this service's durable outbox authority",
    )

    claim = function_body(
        service,
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
            "payload_source.content_inventory()",
        ),
        "channel_and_snapshot_scope_precede_claim_mutation",
        "moved or cross-folder authority fails before attempt, worker, lease, clock, or generation mutation",
    )
    owner_claim = function_body(
        owner, "SyncReplicaSqliteOwner::claim_next_outbox_impl_or_throw("
    )
    require(
        ordered(
            owner_claim,
            "available_file_content.has_value()",
            "payload inventory requires File operation kind",
            "available_file_content->require_folder_or_throw",
            "random_claim_entropy_or_throw",
            "SyncSqliteTransaction transaction",
        ),
        "payload_inventory_ownership_and_scope_precede_entropy_and_writer_authority",
        "inactive or cross-folder immutable inventory cannot consume claim entropy, clock evidence, or a SQLite writer slot",
    )
    require(
        ordered(
            owner_claim,
            "validate_sync_replica_operation_or_throw",
            "operation->size_bytes > *max_file_payload_bytes",
            "std::binary_search",
            "continue",
            "claim_sync_replica_outbox_lease_or_throw",
        ),
        "claim_transaction_selects_only_policy_compatible_available_content",
        "permanent wire policy remains fail-closed while ordinary absent payloads consume no attempt authority",
    )
    require(
        ordered(
            claim,
            "claim_next_outbox_for_delivery_or_throw",
            "payload = payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
            "dispatch_guard->claim()",
        ),
        "lookup_copy_failure_exact_releases_then_guard_reproves",
        "post-selection size contradiction or local allocation failure cannot strand a live lease or authorize from copied history",
    )
    guard_suffix = claim[claim.find("guard_outbox_claim_for_dispatch_or_throw"):]
    require(
        "copy_payload_for_operation_or_throw" not in guard_suffix
        and "No caller code or network" in guard_suffix
        and all(token not in guard_suffix for token in ("send(", "sendmsg(", "write(")),
        "sqlite_writer_scope_contains_no_lookup_callback_or_network_io",
        "the writer guard covers reviewed bounded frame construction only",
    )
    require(
        "finish every bounded payload lookup/copy before acquiring it" in owner_header
        and "invoke caller code while it is live" in owner_header
        and "Re-attests one previously minted claim after bounded immutable payload" in owner_header,
        "sqlite_owner_contract_names_the_new_boundary",
        "public authority documentation no longer teaches callback-era sequencing",
    )

    require(
        service_header.count("SyncReplicaFilePayloadSnapshot payload_snapshot") >= 2
        and dispatch_header.count("SyncReplicaFilePayloadSnapshot payload_snapshot") >= 2
        and dispatch.count("std::move(payload_snapshot)") >= 2,
        "service_and_tls_composition_transfer_snapshot_by_value",
        "cheap shared const-state ownership survives nested dispatch without borrowed caller storage",
    )

    runtime_tokens = (
        "payload snapshot did not retain bounded immutable identity",
        "payload snapshot did not expose one canonical immutable digest inventory",
        "cross-folder payload snapshot reached durable owner work",
        "moved-from payload snapshot reached durable owner work",
        "payload snapshot digest depends on caller insertion order",
        "payload snapshot authorized a non-file operation",
        "payload snapshot ignored declared-size disagreement",
        "payload snapshot accepted an entry limit above its hard ceiling",
        "payload snapshot crossed its configured entry budget",
        "immutable payload inventory did not select the first available canonical intent",
        "unavailable head-of-line payload consumed attempt or retry authority",
        "post-selection size mismatch did not exact-release its bounded live attempt",
        "claim expiring after payload lookup escaped as an outbound frame",
        "zero retry delay reached service authority",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "compiled_file_service_matrix_covers_scope_limits_selection_release_and_expiry",
        "the replacement proves no-attempt availability selection and post-selection contradiction handling at runtime",
    )
    require(
        all(
            token in owner_runtime
            for token in (
                "test_delivery_payload_inventory_validation_precedes_claim_authority",
                "malformed payload inventory sampled time or changed durable authority",
                "duplicate payload inventory sampled time or changed durable authority",
                "oversized payload inventory sampled time or changed durable authority",
                "payload inventory borrowed or failed to canonicalize caller storage",
                "cross-folder payload inventory sampled time or changed durable authority",
                "inactive payload inventory sampled time or changed durable authority",
                "mis-scoped payload inventory sampled time or changed durable authority",
                "immutable payload inventory did not authorize its exact operation",
            )
        ),
        "compiled_owner_matrix_covers_inventory_validation_before_authority",
        "malformed, duplicate, oversized, inactive, cross-folder, and mis-scoped inventories cannot mutate owner authority",
    )
    require(
        tls_runtime.count("payload_snapshot(") >= 8
        and "SyncReplicaFilePayloadSnapshot" in tls_runtime,
        "real_tls_composition_uses_the_same_snapshot_authority",
        "network integration does not retain a hidden callback-only overload",
    )
    require(
        "file_payload_callback_surface_is_retired" in callback_audit
        and "removed_payload_callback_has_compiled_replacement_matrix" in callback_audit
        and "outbound_payload_authority_is_immutable_bounded_and_callback_free" in delivery_audit,
        "existing_authority_audits_track_callback_retirement",
        "older audits were refactored instead of left to bless obsolete source shapes",
    )

    require(
        cmake.count("anonsync_sync_file_payload_snapshot_source_audit") >= 2
        and "tools/audit_sync_file_payload_snapshot.py" in cmake,
        "snapshot_audit_is_registered_with_ctest",
        "ordinary validation detects drift in the new authority boundary",
    )
    require(
        "revision_number >= 892" in verifier
        and "src/sync_replica_file_content_inventory.hpp" in verifier
        and "src/sync_replica_file_content_inventory.cpp" in verifier
        and "src/sync_replica_file_payload_snapshot.hpp" in verifier
        and "src/sync_replica_file_payload_snapshot.cpp" in verifier
        and "tools/audit_sync_file_payload_snapshot.py" in verifier
        and "FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md" in verifier,
        "release_verifier_requires_complete_rev0892_surface",
        "a sealed package cannot omit implementation, audit, or design record",
    )
    require(
        all(
            token in design
            for token in (
                "Failed authority sequence",
                "Corrected authority sequence",
                "Availability selection and exact failure ownership",
                "Unknown code is no longer accepted",
                "Content identity is not authenticity",
                "Aggregate memory remains caller-visible pressure",
                "unavailable head-of-line object",
                "C++ Core Guidelines CP.22",
                "RFC 6920",
                "FIPS 180-4",
                "Lexical audit nonclaim",
            )
        ),
        "design_record_names_research_nonclaims_and_remaining_debt",
        "the handoff distinguishes content addressing, authentication, resource pressure, and executable proof",
    )
    require(
        "lexical hygiene" in self_text.lower()
        and "do not prove SHA-256 collision resistance" in self_text,
        "audit_disclaims_semantic_and_cryptographic_proof",
        "substring checks cannot become release authority by rhetoric",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
