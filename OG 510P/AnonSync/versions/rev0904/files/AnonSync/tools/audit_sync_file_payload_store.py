#!/usr/bin/env python3
"""Lexical hygiene audit for the durable sender file-payload store.

This audit inventories reviewed source shape, ordering, build retention, and
runtime-test vocabulary. It is intentionally not a semantic proof: source
spelling cannot prove POSIX pathname behavior, filesystem durability, SHA-256
security, allocation success, SQLite transaction behavior, race freedom, or
crash recovery. Compiler, sanitizer, runtime, stress, and package evidence are
load-bearing.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_directory_authority.hpp"),
    Path("src/sync_directory_authority_internal.hpp"),
    Path("src/sync_directory_authority.cpp"),
    Path("src/sync_posix_directory_resolution.hpp"),
    Path("src/sync_posix_directory_resolution.cpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_file_payload_snapshot.hpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_file_tls_dispatch.hpp"),
    Path("src/sync_replica_file_tls_dispatch.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
    Path("DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md"),
    Path("PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md"),
    Path("REVISION_NOTES_rev0894.md"),
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
        "format": "anonsync-sync-file-payload-store-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "scope_nonclaim": (
            "source vocabulary and source order do not prove filesystem, "
            "cryptographic, transaction, concurrency, or crash semantics"
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
    directory_authority_h = text["src/sync_directory_authority.hpp"]
    directory_authority_internal = text[
        "src/sync_directory_authority_internal.hpp"
    ]
    directory_authority = text["src/sync_directory_authority.cpp"]
    resolver_h = text["src/sync_posix_directory_resolution.hpp"]
    resolver = text["src/sync_posix_directory_resolution.cpp"]
    atomic_publication = text["src/sync_atomic_file_publication.cpp"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store = text["src/sync_replica_file_payload_store.cpp"]
    service_h = text["src/sync_replica_file_delivery_service.hpp"]
    service = text["src/sync_replica_file_delivery_service.cpp"]
    dispatch_h = text["src/sync_replica_file_tls_dispatch.hpp"]
    dispatch = text["src/sync_replica_file_tls_dispatch.cpp"]
    runtime = text["tests/sync_replica_file_payload_store_test.cpp"]
    service_runtime = text["tests/sync_replica_file_delivery_service_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    design = text["DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md"]
    lease_design = text[
        "PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md"
    ]
    revision_notes = text["REVISION_NOTES_rev0894.md"]
    self_text = text["tools/audit_sync_file_payload_store.py"]

    store_sources = cmake_call(
        cmake, "set(ANONSYNC_SYNC_REPLICA_FILE_PAYLOAD_STORE_SOURCE"
    )
    store_link = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_replica_file_payload_store"
    )
    service_link = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_replica_file_delivery_service"
    )
    require(
        "src/sync_replica_file_payload_store.cpp" in store_sources
        and "anonsync_sync_atomic_file_publication" in store_link
        and "anonsync_sync_directory_authority" in store_link
        and "anonsync_sync_posix_directory_resolution" in store_link
        and "anonsync_sync_bounded_regular_file" in store_link
        and "anonsync_sync_replica_file_payload_store" in service_link,
        "narrow_store_target_is_retained_and_composed",
        "the durable byte owner is a narrow library used by the existing file service",
    )
    require(
        "anonsync_sync_replica_file_payload_store" in cmake
        and "anonsync_sync_replica_file_payload_store_test" in cmake
        and cmake.count("anonsync_sync_replica_file_payload_store_test") >= 5,
        "store_and_runtime_test_are_in_sanitizer_and_ctest_graphs",
        "ordinary and sanitizer builds retain the new owner and its executable matrix",
    )

    require(
        all(
            token in store_h
            for token in (
                "class SyncReplicaFilePayloadStore final",
                "class SyncReplicaFilePayloadStoreSnapshot final",
                "const SyncReplicaFilePayloadStoreSnapshot&) = delete",
                "std::unique_ptr<State> state_",
                "max_entries",
                "max_payload_bytes",
                "max_indexed_bytes",
                "max_transient_entries",
                "max_transient_bytes",
            )
        ),
        "store_and_snapshot_are_move_only_bounded_authorities",
        "descriptor ownership and all durable/transient pressure budgets are explicit",
    )
    require(
        all(
            token in store_h
            for token in (
                "enum class SyncReplicaFilePayloadStoreLeaseMode",
                "SharedObservation",
                "ExclusiveMutation",
                "class SyncReplicaFilePayloadStoreLeaseBusyError final",
                "SyncReplicaFilePayloadStoreLeaseMode mode() const noexcept",
            )
        )
        and "throw SyncReplicaFilePayloadStoreLeaseBusyError" in store
        and "SyncReplicaFilePayloadStoreLeaseBusyError& error" in runtime
        and "error.mode() != expected_mode" in runtime,
        "lease_contention_has_typed_retry_classification",
        "callers and tests distinguish local busy availability from corruption without parsing diagnostic text",
    )
    require(
        all(
            token in directory_authority_internal
            for token in (
                "class SyncDirectorySharedOpenDescriptionLease final",
                "descriptor number but intentionally refers",
                "file description: file offsets",
                "file offsets and status flags are shared",
                "not for an independently",
                "fdopendir/readdir observation",
                "release_descriptor() noexcept",
                "duplicate_shared_open_description_or_throw",
            )
        )
        and "sync_directory_authority_detail::\n        SyncDirectoryAuthorityAccess"
        in directory_authority_h
        and all(
            token in directory_authority
            for token in (
                "SyncDirectorySharedOpenDescriptionLease::reset_noexcept",
                "F_DUPFD_CLOEXEC",
                "root authority before descriptor duplication",
                "root authority after descriptor duplication",
            )
        )
        and store.count("duplicate_shared_open_description_or_throw(") == 3
        and atomic_publication.count(
            "duplicate_shared_open_description_or_throw("
        ) == 1
        and "class SyncDirectoryAuthorityAccess final" not in store
        and "class SyncDirectoryAuthorityAccess final"
        not in atomic_publication,
        "shared_open_description_bridge_is_centralized_and_explicit",
        "descriptor lifetime duplication is one RAII implementation whose type prevents callers from mistaking shared offsets for an independent observation cursor",
    )
    limits = function_body(
        store, "validate_sync_replica_file_payload_store_limits_or_throw("
    )
    require(
        all(
            token in limits
            for token in (
                "limits.max_entries == 0U",
                "kSyncReplicaFilePayloadStoreMaxEntries",
                "limits.max_payload_bytes > limits.max_indexed_bytes",
                "std::numeric_limits<std::size_t>::max()",
                "kSyncReplicaFilePayloadStoreMaxTransientEntries",
                "limits.max_transient_bytes == 0U",
                "kMaximumPersistentInteger",
            )
        ),
        "all_store_limits_are_validated_before_authority",
        "zero, inverted, unaddressable, and over-hard-cap configurations fail before opening the root",
    )

    regular_open = function_body(
        resolver, "sync_posix_open_regular_file_component_or_throw("
    )
    require(
        "SyncPosixOpenedRegularFile" in resolver_h
        and all(
            token in regular_open
            for token in (
                "AT_SYMLINK_NOFOLLOW",
                "S_ISLNK",
                "S_ISREG",
                "open_regular_file_component_with_policy",
                "F_GETFL",
                "O_NONBLOCK",
                "same_identity(before, after)",
                "sync_posix_capture_mount_identity_or_throw",
            )
        ),
        "regular_components_are_nonblocking_identity_and_mount_reproved",
        "special files, symlinks, replacement races, blocking opens, and observed mount crossings fail closed",
    )
    require(
        all(
            token in resolver
            for token in (
                "open_component_with_policy_and_flags",
                "RESOLVE_BENEATH",
                "RESOLVE_NO_MAGICLINKS",
                "RESOLVE_NO_SYMLINKS",
                "RESOLVE_NO_XDEV",
                "regular_file_open_flags()",
                "O_NOFOLLOW",
                "O_NOCTTY",
            )
        ),
        "directory_and_regular_resolution_share_one_policy_core",
        "the refactor reduces drift without weakening file-specific flags",
    )

    scan = function_body(store, "scan_store_namespace_or_throw(")
    require(
        ordered(
            scan,
            "reopen_matching_root_authority_or_throw",
            "duplicate_shared_open_description_or_throw",
            "fstat(root_descriptor.get(), &directory_before)",
            "fdopendir(root_descriptor.get())",
            "root_descriptor.release()",
            "readdir",
            "fsync_or_throw(directory_descriptor",
            "fstat(directory_descriptor, &directory_after)",
            "same_directory_observation",
            "scan_authority.verify_or_throw",
            "root_authority.verify_or_throw",
        ),
        "scan_is_rooted_synchronized_and_cutpoint_reproved",
        "one bounded namespace observation is fenced by retained-root and before/after directory evidence",
    )
    reopen = function_body(
        store, "reopen_matching_root_authority_or_throw("
    )
    require(
        all(
            token in reopen
            for token in (
                "retained.verify_or_throw",
                "SyncDirectoryAuthority::open_or_throw",
                "sync_directory_attestation_digest_or_throw",
                "resolution_capability()",
                "mount_namespace_identity()",
            )
        )
        and "fdopendir(root_descriptor.get())" in scan
        and "independent root" in scan,
        "directory_scans_use_independent_open_file_descriptions",
        "fdopendir/readdir cannot consume the retained authority's shared directory cursor",
    )
    production_fdopendir_paths = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "src").rglob("*")
        if path.is_file()
        and path.suffix in {".cpp", ".hpp"}
        and "fdopendir(" in path.read_text(encoding="utf-8")
    )
    require(
        production_fdopendir_paths
        == ["src/sync_replica_file_payload_store.cpp"],
        "production_directory_stream_inventory_is_review_complete",
        "every production fdopendir owner is forced through the reviewed independent-cursor path; "
        f"inventory={production_fdopendir_paths}",
    )
    require(
        all(
            token in scan
            for token in (
                "basename == identity_basename",
                "identity_required && !out.identity_present",
                "is_lowercase_sha256_hex",
                "require_private_regular_file_or_throw",
                "SyncPosixDescriptorLinkPolicy::exactly_one",
                "sha256_hex(frozen.bytes()) != basename",
                "verify_named_regular_file_or_throw",
                "std::sort",
                "std::adjacent_find",
            )
        ),
        "digest_named_payloads_are_exactly_hashed_and_canonicalized",
        "type, owner, mode, link count, device, bytes, basename, and stable namespace identity are all represented",
    )
    identity = function_body(store, "ensure_store_identity_or_throw(")
    require(
        all(
            token in store
            for token in (
                "kStandaloneStoreIdentityBasenameV2",
                "kProductStoreIdentityBasenameV3",
                "kLegacyStoreIdentityBasenameV1",
                "kStandaloneStoreIdentityDomainV2",
                "kProductStoreIdentityDomainV3",
                "standalone_store_identity_payload",
                "product_store_identity_payload_or_throw",
            )
        )
        and "payload.append(kStoreLeaseProtocol)" in function_body(
            store, "standalone_store_identity_payload("
        )
        and "append_framed_marker_field" in function_body(
            store, "product_store_identity_payload_or_throw("
        )
        and "offline migration is required before lease-protected use" in scan
        and ordered(
            identity,
            "identity reconciliation",
            "identity marker conflicts with the requested folder",
            "identity bootstrap preflight",
            "write_sync_file_atomically_create_new_under_directory_or_throw",
            "identity publication",
            "identity publication did not become durable and exact",
        )
        and "reconcile_sync_immutable_file_create_new_under_directory_or_throw"
        in identity,
        "durable_store_identity_is_cleanly_bootstrapped_and_folder_bound",
        "one lease-generation-bound marker is exact-reconciled, minted only after a clean full scan, rejects folder relabeling, and refuses the lock-ignorant legacy generation",
    )
    require(
        all(
            token in scan
            for token in (
                "sync_atomic_file_publication_temp_basename_is_exact",
                "publication residue count exceeds configured budget",
                "publication residue bytes exceed configured budget",
                "refuses unexpected payload-root entry",
            )
        ),
        "publication_residue_and_unknown_namespace_pressure_are_bounded",
        "only exact writer temp names are classified and both their count and bytes remain finite",
    )

    snapshot = function_body(store, "SyncReplicaFilePayloadStore::snapshot_or_throw()")
    require(
        ordered(
            snapshot,
            "snapshot source preflight",
            "ensure_store_identity_or_throw",
            "store.expected_identity",
            "reopen_matching_root_authority_or_throw",
            "acquire_store_lease_or_throw",
            "SyncReplicaFilePayloadStoreLeaseMode::SharedObservation",
            "scan_store_under_lease_or_throw",
            "SyncReplicaFileContentInventory",
            "snapshot_digest_or_throw",
            "snapshot final lease cutpoint",
        ),
        "snapshot_reopens_and_binds_exact_root_before_index_authority",
        "path rebinding or mount-namespace drift cannot redirect a retained content index",
    )
    digest_body = function_body(store, "snapshot_digest_or_throw(")
    require(
        all(
            token in digest_body
            for token in (
                "kSnapshotDigestDomain",
                "kStoreLeaseProtocol",
                "folder_id",
                "root_path",
                "root_attestation_digest",
                "limits.max_entries",
                "limits.max_transient_bytes",
                "transient_entry_count",
                "transient_bytes",
                "indexed_bytes",
                "entry.content_sha256",
                "entry.size_bytes",
            )
        ),
        "snapshot_digest_binds_scope_limits_pressure_and_exact_index",
        "the summary is deterministic evidence subordinate to the fully checked directory observation",
    )

    lookup = function_body(
        store,
        "SyncReplicaFilePayloadStoreSnapshot::copy_payload_for_operation_or_throw(",
    )
    require(
        ordered(
            lookup,
            "require_state_or_throw",
            "operation.kind != SyncReplicaValueKind::File",
            "find_entry",
            "root_authority.verify_or_throw",
            "duplicate_shared_open_description_or_throw",
            "open_store_file_or_throw",
            "FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw",
            "sha256_hex(frozen.bytes())",
            "verify_named_regular_file_or_throw",
            "final root proof",
        ),
        "selected_payload_is_reopened_and_exactly_reproved_after_claim",
        "the index cannot return stale or replacement bytes after durable claim selection",
    )
    put = function_body(store, "SyncReplicaFilePayloadStore::put_payload_or_throw(")
    require(
        ordered(
            put,
            "sha256_hex(payload)",
            "ensure_store_identity_or_throw",
            "acquire_store_lease_or_throw",
            "SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation",
            "scan_store_under_lease_or_throw",
            "find_entry",
            "max_entries",
            "max_indexed_bytes",
            "max_transient_entries",
            "max_transient_bytes",
            "payload pre-publication lease cutpoint",
            "write_sync_file_atomically_create_new_under_directory_or_throw",
            "payload publication final lease cutpoint",
        )
        and "reconcile_sync_immutable_file_create_new_under_directory_or_throw" in put
        and all(
            token in put
            for token in (
                "existing payload pre-reconciliation lease cutpoint",
                "existing payload final lease cutpoint",
                "failed publication pre-reconciliation lease cutpoint",
                "reconciled publication final lease cutpoint",
                "conflicting publication final lease cutpoint",
                "absent publication final lease cutpoint",
            )
        )
        and "std::rethrow_exception(original)" in put,
        "put_is_preflight_bounded_create_new_and_ambiguity_reconciled",
        "publication cannot replace an existing digest name, exact final bytes close ambiguous local failures, and every terminal result remains bound to the live lock inode",
    )
    lease = function_body(store, "acquire_store_lease_or_throw(")
    require(
        ordered(
            lease,
            "root pre-lease proof",
            "duplicate_shared_open_description_or_throw",
            "open_verified_store_identity_or_throw",
            "acquire_flock_nonblocking_or_throw",
            "independent lease conflict probe",
            "conflicting",
            "flock(",
            "flock_conflict_error",
            "StoreLease lease",
            "lease.verify_or_throw",
            "identity lock anchor after exclusion proof",
        )
        and all(
            token in store
            for token in (
                "LOCK_SH",
                "LOCK_EX",
                "LOCK_NB",
                "EWOULDBLOCK",
                "EAGAIN",
                "kStoreLeaseProtocol",
            )
        ),
        "store_marker_carries_runtime_reproved_shared_exclusive_lease",
        "cooperative scans coexist, mutations exclude every scan/mutation, and unsupported semantics fail closed",
    )
    lease_verify = function_body(store, "StoreLease::verify_or_throw(")
    leased_scan = function_body(store, "scan_store_under_lease_or_throw(")
    require(
        all(
            token in store
            for token in (
                "OwnedFd root_descriptor_",
                "OwnedFd identity_descriptor_",
                "struct stat identity_status_",
                "SyncDirectoryAttestation root_attestation_",
                "std::string expected_identity_",
            )
        )
        and ordered(
            lease_verify,
            "retained root pre-proof",
            "root_authority.attestation() != root_attestation_",
            "verify_open_store_identity_or_throw",
            "retained root post-proof",
        )
        and ordered(
            leased_scan,
            "lease.mode() != required_mode",
            "pre-scan lease proof",
            "scan_store_namespace_or_throw",
            "final lease proof",
        )
        and store.count("scan_store_namespace_or_throw(") == 3,
        "ordinary_scans_require_exact_live_lease_witness",
        "only clean marker bootstrap may call the raw scanner; protected scans re-prove the locked inode before and after traversal",
    )
    identity_open = function_body(
        store, "open_verified_store_identity_or_throw("
    )
    require(
        "verify_open_store_identity_or_throw" in identity_open
        and "open_verified_store_identity_or_throw" in scan
        and "open_verified_store_identity_or_throw" in lease,
        "identity_marker_validation_has_one_implementation",
        "scan and lease paths cannot drift on marker bytes, mode, owner, link, mount, or namespace identity",
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
            "channel_authority.context()",
            "claim_next_outbox_for_delivery_or_throw",
            "payload_source.content_inventory()",
            "payload_source.copy_payload_for_operation_or_throw",
            "release_claim_after_pre_dispatch_failure_or_throw",
            "guard_outbox_claim_for_dispatch_or_throw",
            "dispatch_guard->claim()",
            "dispatch_guard->commit_or_throw()",
        ),
        "shared_claim_path_scopes_indexes_releases_and_reproves",
        "both memory and durable sources use one exact mutation frontier rather than duplicated logic",
    )
    require(
        "std::function" not in service_h + service + dispatch_h + dispatch
        and "SyncReplicaFilePayloadSource" not in service_h + service + dispatch_h + dispatch
        and "<functional>" not in service_h + service + dispatch_h + dispatch,
        "payload_source_polymorphism_is_compile_time_not_caller_code",
        "the shared template adds no executable callback while a claim or writer guard is live",
    )
    require(
        service_h.count("SyncReplicaFilePayloadStoreSnapshot") >= 1
        and dispatch_h.count("SyncReplicaFilePayloadStoreSnapshot") >= 2
        and "claim_and_begin_from_payload_source_or_throw" in dispatch
        and "claim_and_dispatch_from_payload_source_or_throw" in dispatch,
        "durable_source_reaches_both_service_and_tls_composition",
        "the production seam does not stop at an isolated store unit test",
    )

    runtime_tokens = (
        "restart configuration relabeled a durably bound payload root",
        "failed bootstrap minted identity into a hostile namespace",
        "clean pre-existing content did not receive exactly one durable folder marker",
        "exact private publication residue was not bounded separately",
        "publication residue crossed its aggregate byte budget",
        "digest-shaped FIFO blocked a bounded namespace scan",
        "multiply-linked payload retained alias authority",
        "symbolic-link payload entered durable content authority",
        "restart did not reconstruct the same canonical durable index",
        "path rebind redirected a retained durable payload snapshot",
        "post-index deletion returned stale or invented payload bytes",
        "repeated scans inherited a consumed directory-stream cursor",
        "current identity marker did not bind the exact lease generation",
        "a cross-process writer did not exclude a second capacity spend",
        "cooperative shared observations did not coexist",
        "serialized writers crossed the exact aggregate entry budget",
        "legacy identity generation entered lease-protected authority",
        "failed legacy-generation preflight mutated identity authority",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "compiled_store_matrix_covers_restart_namespace_and_pressure_edges",
        "the focused executable exercises ordinary and hostile filesystem observations",
    )
    service_tokens = (
        "unavailable durable head consumed attempt or retry authority",
        "post-index durable read failure did not exact-release its claim",
        "retry_not_before_epoch == 752U",
        "reusable durable snapshot did not reconcile exact republished bytes",
    )
    require(
        all(token in service_runtime for token in service_tokens),
        "compiled_composition_matrix_covers_selection_and_exact_release",
        "a post-index local read failure cannot strand or silently settle sender attempt authority",
    )

    require(
        "anonsync_sync_file_payload_store_source_audit" in cmake
        and "tools/audit_sync_file_payload_store.py" in cmake,
        "store_hygiene_audit_is_registered_with_ctest",
        "ordinary validation detects source/build/package drift at this boundary",
    )
    require(
        "revision_number >= 894" in verifier
        and "src/sync_directory_authority_internal.hpp" in verifier
        and "src/sync_directory_authority.cpp" in verifier
        and "src/sync_atomic_file_publication.cpp" in verifier
        and "src/sync_replica_file_payload_store.hpp" in verifier
        and "src/sync_replica_file_payload_store.cpp" in verifier
        and "tests/sync_replica_file_payload_store_test.cpp" in verifier
        and "tools/audit_sync_file_payload_store.py" in verifier
        and "DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md" in verifier
        and "PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md" in verifier
        and "REVISION_NOTES_rev0894.md" in verifier,
        "release_verifier_requires_complete_rev0894_surface",
        "a sealed handoff cannot omit the centralized descriptor bridge, implementation, runtime matrix, parent design, or lease/cursor audit",
    )
    require(
        all(
            token in design
            for token in (
                "Heart of the mission",
                "Authority sequence",
                "What this proves",
                "What this does not prove",
                "O(total indexed bytes)",
                "same-UID",
                "garbage collection",
                "openat2(2)",
                "fsync(2)",
                "RFC 6920",
                "full-scan oracle",
            )
        ),
        "design_record_names_mission_costs_and_nonclaims",
        "the handoff preserves both the reason for the change and its unresolved risks",
    )
    require(
        all(
            token in lease_design
            for token in (
                "Heart of the mission",
                "Directory-offset defect",
                "Shared observation lease",
                "Exclusive mutation lease",
                "flock(2)",
                "advisory",
                "noncooperating",
                "garbage collection",
                "full-scan oracle",
                "SyncDirectorySharedOpenDescriptionLease",
                "final authority cutpoint",
            )
        ),
        "rev0894_design_record_names_corrected_defect_and_nonclaims",
        "the new authority boundary is documented without promoting advisory locking to hostile-writer security",
    )
    require(
        all(
            token in revision_notes
            for token in (
                "serialized payload capacity",
                "independent scan cursors",
                "typed busy error",
                "SyncDirectoryAuthority",
                "existing open file description",
                "O(total indexed bytes)",
            )
        ),
        "revision_notes_bind_primary_corrections_and_cost_nonclaim",
        "the handoff names capacity serialization, cursor independence, centralized shared-state duplication, and the retained full-scan cost",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not a semantic proof" in self_text
        and "Compiler, sanitizer, runtime, stress, and package evidence" in self_text,
        "lexical_audit_disclaims_load_bearing_semantic_authority",
        "a passing source scan cannot be mistaken for runtime or formal proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
