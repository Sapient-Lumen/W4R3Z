#!/usr/bin/env python3
"""Lexical hygiene audit for rev0881 local file-effect path capability.

This inventory checks reviewed source ownership and ordering around canonical
path identity, receiver-local filename ceilings, pre-effect receipts, exact
retry release, live mount-namespace authority, and reboot-ephemeral boot
observations. It deliberately does not prove syscall behavior, race freedom,
filesystem semantics, retry liveness, or crash safety; compiler and runtime
lanes remain load-bearing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_manifest_validation.hpp"),
    Path("src/sync_manifest_validation.cpp"),
    Path("src/sync_directory_authority.hpp"),
    Path("src/sync_directory_authority.cpp"),
    Path("src/sync_posix_mount_namespace_authority.hpp"),
    Path("src/sync_posix_mount_namespace_authority.cpp"),
    Path("src/sync_system_epoch_identity.hpp"),
    Path("src/sync_system_epoch_identity.cpp"),
    Path("src/sync_process_identity_observation.cpp"),
    Path("src/sync_replica_outbox_clock_linux.cpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.cpp"),
    Path("src/sync_replica_file_delivery_protocol.hpp"),
    Path("src/sync_replica_file_delivery_protocol.cpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("tests/sync_manifest_validation_test.cpp"),
    Path("tests/sync_posix_directory_resolution_test.cpp"),
    Path("tests/sync_system_epoch_identity_test.cpp"),
    Path("tests/sync_replica_file_effect_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_file_delivery_protocol_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tools/audit_sync_replica_file_delivery.py"),
    Path("tools/audit_sync_file_effect_path_capability.py"),
    Path("tools/verify_release_package.py"),
    Path("FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md"),
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


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-file-effect-path-capability-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
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
    manifest_header = text["src/sync_manifest_validation.hpp"]
    manifest = text["src/sync_manifest_validation.cpp"]
    directory_header = text["src/sync_directory_authority.hpp"]
    directory = text["src/sync_directory_authority.cpp"]
    namespace_header = text["src/sync_posix_mount_namespace_authority.hpp"]
    namespace_source = text["src/sync_posix_mount_namespace_authority.cpp"]
    epoch_header = text["src/sync_system_epoch_identity.hpp"]
    epoch = text["src/sync_system_epoch_identity.cpp"]
    process_identity = text["src/sync_process_identity_observation.cpp"]
    outbox_clock = text["src/sync_replica_outbox_clock_linux.cpp"]
    effect_header = text["src/sync_replica_file_effect_sqlite_owner.hpp"]
    effect = text["src/sync_replica_file_effect_sqlite_owner.cpp"]
    protocol_header = text["src/sync_replica_file_delivery_protocol.hpp"]
    protocol = text["src/sync_replica_file_delivery_protocol.cpp"]
    service_header = text["src/sync_replica_file_delivery_service.hpp"]
    service = text["src/sync_replica_file_delivery_service.cpp"]
    manifest_test = text["tests/sync_manifest_validation_test.cpp"]
    directory_test = text["tests/sync_posix_directory_resolution_test.cpp"]
    epoch_test = text["tests/sync_system_epoch_identity_test.cpp"]
    effect_test = text["tests/sync_replica_file_effect_sqlite_owner_test.cpp"]
    protocol_test = text["tests/sync_replica_file_delivery_protocol_test.cpp"]
    service_test = text["tests/sync_replica_file_delivery_service_test.cpp"]
    delivery_audit = text["tools/audit_sync_replica_file_delivery.py"]
    verifier = text["tools/verify_release_package.py"]
    design = text["FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md"]

    require(
        "validate_sync_relative_path_component_byte_limit" in manifest_header
        and "receiver-local filename-component byte ceiling" in manifest_header
        and "This is deliberately separate from the" in manifest_header
        and "canonical 4096-byte wire/model limit" in manifest_header,
        "local_component_limit_is_not_canonical_identity",
        "portable path identity and receiver-local effect capacity remain separate APIs",
    )

    component_validator = function_body(
        manifest, "validate_sync_relative_path_component_byte_limit("
    )
    require(
        ordered(
            component_validator,
            "validate_relative_path_value(raw_path)",
            "maximum_component_bytes == 0U",
            "index <= raw_path.size()",
            "index - component_begin",
            "converted > maximum_component_bytes",
        ),
        "component_limit_reuses_canonical_validation_then_counts_bytes",
        "invalid canonical spelling fails first and each slash-delimited component is measured as encoded bytes",
    )
    require(
        "local component policy counts encoded bytes rather than displayed characters" in manifest_test
        and "local component-byte preflight accepts the exact inclusive boundary" in manifest_test
        and "a zero local filename ceiling cannot silently authorize a path" in manifest_test,
        "component_limit_runtime_matrix_covers_bytes_boundary_and_zero",
        "the focused validator distinguishes UTF-8 byte length and exact-boundary acceptance",
    )

    require(
        "DestinationPathBlocked" in effect_header
        and "No effect row or payload authority is created" in effect_header,
        "effect_owner_has_typed_pre_authority_path_denial",
        "local unnameability is not collapsed into capacity, conflict, or an exception-only side channel",
    )
    stage = function_body(
        effect,
        "SyncReplicaFileEffectSqliteOwner::stage_with_diagnostics_or_throw(",
    )
    require(
        ordered(
            stage,
            "validate_sync_replica_operation_or_throw",
            "payload size does not match operation",
            "payload digest does not match operation",
            "destination_path_is_blocked",
            "find_effect",
            "SyncReplicaResourceBudget effect_budget",
            "SyncReplicaFileEffectCapacityConstraint constraint",
            "checked_increment_or_throw",
            "encode_sync_replica_operation_canonical_or_throw",
            "insert_effect_or_throw",
        ),
        "path_capability_preflight_precedes_duplicate_capacity_and_mutation",
        "only exact canonical operation and payload bytes reach a no-mutation local path decision",
    )
    require(
        ordered(
            stage,
            "destination_path_is_blocked",
            "path-blocked stage pre-commit root authority",
            "transaction.commit()",
            "DestinationPathBlocked",
        ),
        "path_denial_commits_an_unchanged_attested_transaction",
        "the receiver re-proves the retained root and returns without minting generation or payload authority",
    )
    local_limit = function_body(effect, "destination_component_byte_limit(")
    require(
        "filesystem_name_maximum" in local_limit
        and "path_name_maximum" in local_limit
        and "std::min" in local_limit
        and "std::optional<std::uint64_t>" in local_limit,
        "local_limit_is_conservative_and_explicitly_optional",
        "available statvfs and fpathconf ceilings are intersected; an indeterminate host does not invent a number",
    )
    require(
        "constexpr std::uint64_t kSchemaVersion = 3U" in effect
        and "constexpr std::uint64_t kLegacySchemaVersion = 2U" in effect
        and "CHECK(schema_version=3)" in effect
        and "CHECK(schema_version=2)" in effect
        and all(
            token not in effect
            for token in (
                "root_boot_source",
                "root_epoch_binding",
                "root_mount_identity_kind",
                "SyncDirectoryEpochBinding",
            )
        ),
        "reboot_ephemeral_identity_is_not_persisted_as_root_authority",
        "the correction does not strand a valid effect database merely because the host rebooted",
    )
    require(
        "test_destination_component_limit_precedes_durable_stage" in effect_test
        and "path-policy denial must not consume payload bytes, effect rows, or generation authority" in effect_test
        and "path-policy denial must not attempt filesystem publication" in effect_test
        and "only the locally representable boundary operation may acquire durable effect authority" in effect_test,
        "effect_runtime_proves_no_mutation_and_exact_boundary_acceptance",
        "an impossible component leaves both SQLite and the destination namespace unchanged",
    )

    require(
        "kSyncReplicaFileDeliveryProtocolVersion = 2U" in protocol_header
        and ordered(
            protocol_header,
            "Published = 1U",
            "DestinationConflict = 8U",
            "EffectPathBlocked = 9U",
        )
        and "file-delivery-request-v2" in protocol
        and "file-delivery-receipt-v2" in protocol,
        "protocol_extension_is_an_explicit_v2_break",
        "prior disposition numbers remain stable while old peers reject the new frame version cleanly",
    )
    pre_effect = function_body(
        protocol, "sync_replica_file_delivery_receipt_precedes_effect_authority("
    )
    require(
        "EffectCapacityBlocked" in pre_effect
        and "EffectPathBlocked" in pre_effect,
        "pre_effect_classifier_is_total_for_authority_free_denials",
        "capacity and local path policy share the same no-effect/no-evidence receipt contract",
    )
    receipt_validation = function_body(
        protocol, "void validate_sync_replica_file_delivery_receipt_or_throw("
    )
    require(
        ordered(
            receipt_validation,
            "sync_replica_file_delivery_receipt_precedes_effect_authority",
            "receipt.evidence_receipt.has_value()",
            "!receipt.effect_id.empty()",
            "pre-effect receipt must not claim staged evidence or effect identity",
            "return;",
            "lacks staged effect authority",
        ),
        "pre_effect_receipt_cannot_smuggle_effect_or_causal_authority",
        "typed denial validation exits before the branch that requires staged effect evidence",
    )
    require(
        "pre-effect classifier did not isolate authority-free denials" in protocol_test
        and "path-policy receipt claimed effect or evidence authority" in protocol_test
        and "file request did not advertise explicit protocol v2" in protocol_test
        and "file-delivery v1 frame was accepted" in protocol_test
        and "EffectPathBlocked" in protocol_test,
        "protocol_runtime_covers_path_denial_roundtrip_and_residue_rejection",
        "the wire codec and validator exercise the new disposition rather than only naming it",
    )

    receive = function_body(
        service, "SyncReplicaFileDeliveryService::receive_request_or_throw("
    )
    require(
        ordered(
            receive,
            "stage_with_diagnostics_or_throw",
            "DestinationPathBlocked",
            "EffectPathBlocked",
            "if (!disposition.has_value())",
            "evidence_service_.receive_request_or_throw",
        ),
        "receiver_path_policy_precedes_causal_evidence_admission",
        "an unnameable local effect cannot consume receiver causal authority",
    )
    make_receipt = function_body(service, "make_receipt_or_throw(")
    require(
        "sync_replica_file_delivery_receipt_precedes_effect_authority" in make_receipt
        and "find_effect_record_or_throw" in make_receipt,
        "receipt_construction_omits_effect_id_for_pre_effect_denial",
        "effect identity is looked up only after the shared pre-effect classifier says authority exists",
    )
    retry_validation = function_body(service, "validate_retry_policy_or_throw(")
    require(
        "effect_path_blocked_delay_seconds" in service_header
        and "Local policy owns retry timing" in service_header
        and "delay == 0U" in retry_validation
        and "kSyncReplicaOutboxMaxRetryDelaySeconds" in retry_validation
        and "must be positive and within the fixed outbox retry-delay budget" in retry_validation
        and "zero retry delay reached service authority" in service_test,
        "path_retry_timing_is_local_positive_and_bounded",
        "receiver classification cannot dictate sender time, an immediate spin, or an unbounded delay",
    )
    apply_receipt = function_body(
        service, "SyncReplicaFileDeliveryService::apply_receipt_or_throw("
    )
    require(
        ordered(
            apply_receipt,
            "validate_sync_replica_file_delivery_receipt_for_request_or_throw",
            "sync_replica_file_delivery_receipt_is_effect_terminal",
            "retry_delay_for_nonterminal_or_throw",
            "release_outbox_for_retry_or_throw",
            "settle_outbox_or_throw",
        ),
        "nonterminal_receipts_release_exact_claim_terminal_receipts_settle",
        "current nonterminal attempts move to owner-clock retry authority instead of idling until lease expiry",
    )
    claim = function_body(
        service,
        "SyncReplicaFileDeliveryService::\n    "
        "claim_next_request_from_payload_source_or_throw(",
    )
    release_helper = function_body(
        service,
        "SyncReplicaFileDeliveryService::"
        "release_claim_after_pre_dispatch_failure_or_throw(",
    )
    require(
        ordered(
            release_helper,
            "release_outbox_for_retry_or_throw",
            "SyncReplicaSqliteOutboxReceiptResult::Applied",
            "IntentMissing",
            "StaleClaim",
            "ExpiredClaim",
            "std::rethrow_exception(original)",
        )
        and "exact retry release failed" in release_helper,
        "pre_dispatch_failures_release_exact_attempt_before_rethrow",
        "one helper exact-releases payload lookup/copy, guard, validation, encoding, and digest failures",
    )
    require(
        ordered(
            claim,
            "payload_source.require_folder_or_throw",
            "payload_source.preflight_or_throw",
            "claim_next_outbox_for_delivery_or_throw",
            "payload_source.content_inventory()",
            "payload = payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
            "dispatch_guard->claim()",
            "validate_sync_replica_file_delivery_request_or_throw",
            "encode_sync_replica_file_delivery_request_or_throw",
            "dispatch_guard->commit_or_throw()",
            "return outbound",
        )
        and ordered(
            claim,
            "const std::exception_ptr original = std::current_exception()",
            "dispatch_guard.reset()",
            "release_claim_after_pre_dispatch_failure_or_throw",
        ),
        "post_snapshot_dispatch_guard_revalidates_exact_claim",
        "bounded immutable lookup cannot authorize a frame from expired or independently superseded history",
    )
    require(
        "test_payload_snapshot_validation_selection_and_exact_mismatch_release" in service_test
        and "unavailable head-of-line payload consumed attempt or retry authority" in service_test
        and "post-selection size mismatch did not exact-release its bounded live attempt" in service_test
        and "test_post_snapshot_dispatch_guard_closes_clock_expiry" in service_test
        and "claim expiring after payload lookup escaped as an outbound frame" in service_test
        and "test_retry_policy_validation_precedes_durable_authority" in service_test
        and "test_effect_path_policy_precedes_effect_and_evidence" in service_test
        and "an exact retry did not reproduce the same no-mutation path-policy receipt" in service_test
        and "path-policy receipt did not retain intent under exact local backoff" in service_test,
        "service_runtime_covers_exact_release_replay_and_no_mutation",
        "sender and receiver proofs include fresh claim timing and stable repeated denial",
    )

    require(
        "class SyncPosixMountNamespaceAuthority final" in namespace_header
        and "/proc/thread-self/ns/mnt" in namespace_source
        and "status.st_dev" in namespace_source
        and "status.st_ino" in namespace_source,
        "mount_namespace_is_a_retained_live_capability",
        "Linux retains a namespace handle and compares documented device/inode identity with a fresh observation",
    )
    capture = function_body(directory, "SyncDirectoryAuthority::open_or_throw(")
    require(
        ordered(
            capture,
            "SyncPosixMountNamespaceAuthority::capture_or_throw",
            "traverse_directory_or_throw",
            "capture_attestation_or_throw",
        ),
        "mount_namespace_is_captured_before_path_traversal",
        "the descriptor cannot be minted in an unbound namespace context",
    )
    directory_verify = function_body(directory, "SyncDirectoryAuthority::verify_or_throw(")
    require(
        ordered(
            directory_verify,
            "mount_namespace_authority_.verify_or_throw",
            "retained directory fstat",
            "traverse_directory_or_throw",
        ),
        "namespace_reproof_precedes_retained_and_visible_path_proofs",
        "setns or unshare is detected before a descriptor from the old namespace can authorize new traversal",
    )
    namespace_verify = function_body(
        namespace_source, "SyncPosixMountNamespaceAuthority::verify_or_throw("
    )
    require(
        "revoked_.load(std::memory_order_acquire)" in namespace_verify
        and "catch (...)" in namespace_verify
        and "revoked_.store(true, std::memory_order_release)" in namespace_verify
        and "mount namespace changed" in namespace_verify,
        "mount_namespace_failure_is_sticky",
        "returning to an earlier namespace cannot resurrect an authority after an observed mismatch",
    )
    require(
        "CLONE_NEWUSER | CLONE_NEWNS" in directory_test
        and "mount namespace authority is revoked" in directory_test
        and "directory authority is revoked" in directory_test
        and "host denies user+mount namespace unshare witness" in directory_test,
        "runtime_mount_namespace_witness_is_executable_or_explicitly_skipped",
        "the focused test attempts a same-process namespace transition and checks both primitive and composed revocation",
    )

    require(
        "sync_system_parse_boot_id_text_or_throw" in epoch_header
        and "O_NOFOLLOW" in epoch
        and "kMaximumBootIdentityBytes" in epoch
        and "is not exactly one UUID line" in epoch,
        "shared_boot_observation_is_strict_and_bounded",
        "one leaf owner reads procfs without symlink following or whitespace normalization",
    )
    require(
        '#include "sync_system_epoch_identity.hpp"' in process_identity
        and "observe_sync_system_boot_identity_or_throw" in process_identity
        and '#include "sync_system_epoch_identity.hpp"' in outbox_clock
        and outbox_clock.count("observe_sync_system_boot_identity_or_throw") >= 1,
        "process_and_clock_reuse_one_boot_parser",
        "independent identity authorities no longer carry divergent procfs boot-ID readers",
    )
    require(
        "repeated newline is not normalized into evidence" in epoch_test
        and "leading whitespace is not trimmed into evidence" in epoch_test
        and "unexpected boot source failure is fatal" in epoch_test,
        "boot_observation_runtime_covers_strict_framing_and_failure_classification",
        "missing/permission-hidden evidence is typed while malformed or unexpected failures stay fatal",
    )
    require(
        all(
            token not in effect + directory
            for token in (
                "SyncSystemBootIdentityObservation",
                "observe_sync_system_boot_identity_or_throw",
                "system-boot-identity",
            )
        )
        and "reboot-ephemeral evidence, never persistent filesystem-root identity" in cmake,
        "boot_uuid_is_not_effect_root_storage_identity",
        "boot observation remains useful to clocks/processes without creating a reboot lockout for durable effects",
    )

    namespace_link = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_directory_authority"
    )
    require(
        "anonsync_sync_posix_mount_namespace_authority" in namespace_link
        and "anonsync_system_epoch_identity" not in namespace_link
        and "anonsync_system_epoch_identity_test" in cmake
        and "anonsync_sync_file_effect_path_capability_source_audit" in cmake,
        "build_graph_preserves_narrow_dependency_direction",
        "directory authority owns live namespace proof but does not acquire a boot-ID storage dependency",
    )
    sanitizer_compile_inventory = cmake_call(
        cmake, "set(ANONSYNC_SANITIZER_COMPILE_TARGETS"
    )
    sanitizer_link_inventory = cmake_call(
        cmake, "foreach(tgt\n      anonsync_core"
    )
    require(
        "anonsync_system_epoch_identity_test" in sanitizer_compile_inventory
        and "anonsync_system_epoch_identity_test" in sanitizer_link_inventory,
        "standalone_epoch_test_links_the_sanitizer_runtime",
        "instrumented leaf tests cannot compile successfully but fail at link because manual CMake policy inventories diverge",
    )
    require(
        "pre_dispatch_failure_releases_exact_claim_before_rethrow" in delivery_audit
        and "post_snapshot_dispatch_guard_revalidates_exact_claim" in delivery_audit
        and "EffectPathBlocked" in delivery_audit
        and "release_outbox_for_retry_or_throw" in delivery_audit,
        "existing_delivery_audit_tracks_new_retry_semantics",
        "the older source inventory no longer expects the removed snapshot-only nonterminal classifier",
    )
    verifier_required = (
        "revision_number >= 881",
        "src/sync_posix_mount_namespace_authority.hpp",
        "src/sync_system_epoch_identity.cpp",
        "tests/sync_system_epoch_identity_test.cpp",
        "tools/audit_sync_file_effect_path_capability.py",
        "tools/audit_sync_outbox_dispatch_guard.py",
        "FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md",
        "OUTBOX_DISPATCH_GUARD_AUDIT_rev0881.md",
    )
    require(
        all(token in verifier for token in verifier_required),
        "release_verifier_requires_complete_rev0881_surface",
        "the package cannot omit the path policy, namespace owner, shared epoch reader, tests, audit, or design record",
    )
    require(
        all(
            token in design
            for token in (
                "Canonical identity versus local effect capability",
                "Legacy staged poison remains a repair concern",
                "Reboot-ephemeral evidence is not durable root identity",
                "Boot-ID unavailability still escapes durable clock evidence",
                "Post-callback claim authority is re-attested locally",
                "Network first-byte dispatch remains a separate authority frontier",
                "strictly positive",
                "Lexical audits are not semantic proof",
                "pubs.opengroup.org",
                "man7.org/linux/man-pages/man7/namespaces.7.html",
                "docs.kernel.org/admin-guide/sysctl/kernel.html",
            )
        ),
        "design_record_contains_research_nonclaims_and_remaining_gap",
        "the handoff names standards grounding, the rejected reboot-lockout design, and unresolved legacy repair",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(encoding="utf-8")
        and "does not prove syscall behavior" in Path(__file__).read_text(encoding="utf-8"),
        "audit_does_not_overclaim_lexical_checks",
        "runtime, compiler, sanitizer, and crash evidence remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
