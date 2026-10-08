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
    Path("README.md"),
    Path("src/sha256_digest.hpp"),
    Path("src/sha256_digest.cpp"),
    Path("src/sync_directory_authority.hpp"),
    Path("src/sync_directory_authority_internal.hpp"),
    Path("src/sync_directory_authority.cpp"),
    Path("src/sync_posix_directory_resolution.hpp"),
    Path("src/sync_posix_directory_resolution.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("src/sync_posix_descriptor_snapshot.hpp"),
    Path("src/sync_posix_descriptor_snapshot.cpp"),
    Path("src/sync_posix_regular_file_snapshot_codec.hpp"),
    Path("src/sync_posix_regular_file_snapshot_codec.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/resumable_sha256.hpp"),
    Path("src/resumable_sha256.cpp"),
    Path("src/sync_replica_file_payload_scrub_state.hpp"),
    Path("src/sync_replica_file_payload_scrub_state.cpp"),
    Path("src/sync_replica_file_payload_retention_mark.hpp"),
    Path("src/sync_replica_file_payload_retention_mark.cpp"),
    Path("src/sync_replica_file_payload_verification_index.hpp"),
    Path("src/sync_replica_file_payload_verification_index.cpp"),
    Path("src/sync_replica_file_delivery_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_peer_server_owner.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_folder.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_local_status_socket.hpp"),
    Path("src/sync_local_status_socket.cpp"),
    Path("src/sync_replica_historical_version_query.hpp"),
    Path("src/sync_replica_historical_version_inventory_json.hpp"),
    Path("src/sync_replica_historical_version_inventory_json.cpp"),
    Path("src/sync_replica_folder_observer.hpp"),
    Path("src/sync_replica_folder_observer.cpp"),
    Path("src/sync_replica_model.hpp"),
    Path("src/sync_replica_model.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("src/sync_replica_folder_process.hpp"),
    Path("src/sync_replica_folder_process.cpp"),
    Path("src/sync_replica_operational_database.hpp"),
    Path("src/sync_replica_operational_database.cpp"),
    Path("src/sync_replica_peer_service_singleton.hpp"),
    Path("src/sync_replica_peer_service_singleton.cpp"),
    Path("src/sync_replica_peer_service.hpp"),
    Path("src/sync_replica_peer_service.cpp"),
    Path("src/sync_replica_peer_service_status.hpp"),
    Path("src/sync_replica_peer_service_status.cpp"),
    Path("src/sync_replica_peer_service_integrity_evidence.hpp"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_replica_sync_once.hpp"),
    Path("src/sync_replica_sync_once.cpp"),
    Path("src/sync_replica_deployment_manifest.hpp"),
    Path("src/sync_replica_payload_extent.hpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_file_payload_snapshot.hpp"),
    Path("src/sync_replica_file_delivery_service.hpp"),
    Path("src/sync_replica_file_delivery_service.cpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_file_tls_dispatch.hpp"),
    Path("src/sync_replica_file_tls_dispatch.cpp"),
    Path("tests/sync_atomic_file_publication_test.cpp"),
    Path("tests/sync_bounded_regular_file_test.cpp"),
    Path("tests/sync_local_status_socket_test.cpp"),
    Path("tests/sync_replica_stream_connector_test.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/resumable_sha256_test.cpp"),
    Path("tests/sync_replica_file_payload_scrub_state_test.cpp"),
    Path("tests/sync_replica_file_payload_retention_mark_test.cpp"),
    Path("tests/sync_replica_file_payload_verification_index_test.cpp"),
    Path("tests/sync_replica_file_delivery_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_folder_observer_test.cpp"),
    Path("tests/sync_replica_network_model_test.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_folder_scan_owner_test.cpp"),
    Path("tests/sync_replica_peer_service_integrity_evidence_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tests/sync_replica_sync_once_test.cpp"),
    Path("tests/sync_replica_file_delivery_service_test.cpp"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/test_anonsync_sync_process.py"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
    Path("tools/test_anonsync_service_process.py"),
    Path("tools/test_anonsync_service_i2p_ingress.py"),
    Path("tools/test_anonsync_service_configuration_status.py"),
    Path("tools/test_anonsync_database_recovery.py"),
    Path("tools/audit_anonsync_replica_database_open_policy.py"),
    Path("tools/test_anonsync_service_folder_wake.py"),
    Path("tools/test_anonsync_provisioning.py"),
    Path("tools/verify_release_package.py"),
    Path("DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md"),
    Path("PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md"),
    Path("REVISION_NOTES_rev0894.md"),
    Path("DURABLE_PAYLOAD_VERIFICATION_CHECKPOINT_AUDIT_rev0954.md"),
    Path("REVISION_NOTES_rev0954.md"),
    Path("DURABLE_BYTE_BOUNDED_PAYLOAD_SCRUB_AUDIT_rev0955.md"),
    Path("REVISION_NOTES_rev0955.md"),
    Path("PAYLOAD_INTEGRITY_SERVICE_RECOVERY_AUDIT_rev0956.md"),
    Path("REVISION_NOTES_rev0956.md"),
    Path("PAYLOAD_REPROOF_HANDOFF_AND_EXACT_OWNER_AUDIT_rev0957.md"),
    Path("REVISION_NOTES_rev0957.md"),
    Path("SCRUB_WRITE_AHEAD_RESTART_FENCE_AUDIT_rev0958.md"),
    Path("REVISION_NOTES_rev0958.md"),
    Path("MINIMUM_READER_IDENTITY_MIGRATION_AUDIT_rev0959.md"),
    Path("REVISION_NOTES_rev0959.md"),
    Path("OWNER_TRIGGERED_PAYLOAD_RECHECK_AUDIT_rev0960.md"),
    Path("REVISION_NOTES_rev0960.md"),
    Path("EXACT_CORRUPT_PAYLOAD_QUARANTINE_AND_LINEARIZED_LOCAL_ACTION_AUDIT_rev0961.md"),
    Path("REVISION_NOTES_rev0961.md"),
    Path("EXACT_QUARANTINE_RELEASE_AND_PROOF_REUSE_AUDIT_rev0962.md"),
    Path("REVISION_NOTES_rev0962.md"),
    Path("RESTART_DISCOVERABLE_QUARANTINE_INVENTORY_AUDIT_rev0963.md"),
    Path("REVISION_NOTES_rev0963.md"),
    Path("BOUNDED_RESUMABLE_DIRECTORY_COMPONENT_BATCH_AUDIT_rev0964.md"),
    Path("REVISION_NOTES_rev0964.md"),
    Path("GLOBAL_RESUMABLE_DIRECTORY_BATCH_LIFETIME_AUDIT_rev0965.md"),
    Path("REVISION_NOTES_rev0965.md"),
    Path("EXPLICIT_CAUSAL_VERSION_INSPECTION_AND_ROOTED_RESTORE_AUDIT_rev0966.md"),
    Path("REVISION_NOTES_rev0966.md"),
    Path("PAGED_CAUSAL_VERSION_QUERY_AND_GROUPED_PROJECTION_AUDIT_rev0967.md"),
    Path("REVISION_NOTES_rev0967.md"),
    Path("EXACT_CAUSAL_HISTORY_SOURCE_CUTPOINT_AUDIT_rev0968.md"),
    Path("REVISION_NOTES_rev0968.md"),
    Path("EXACT_CURRENT_BOUND_HISTORICAL_RESTORE_AUDIT_rev0969.md"),
    Path("REVISION_NOTES_rev0969.md"),
    Path("CAUSAL_METADATA_HISTORY_INSPECTION_AUDIT_rev0970.md"),
    Path("REVISION_NOTES_rev0970.md"),
    Path("BOUNDED_HISTORICAL_STATUS_PAGE_AND_SINGLE_RESULT_AUDIT_rev0971.md"),
    Path("REVISION_NOTES_rev0971.md"),
    Path("RETAINED_PAYLOAD_REACHABILITY_AND_CANONICAL_STATUS_FRONTIER_AUDIT_rev0972.md"),
    Path("REVISION_NOTES_rev0972.md"),
    Path("HISTORICAL_VERSION_RETENTION_PIN_AUTHORITY_AUDIT_rev0973.md"),
    Path("REVISION_NOTES_rev0973.md"),
    Path("DELETION_FREE_EXACT_RETENTION_PLAN_AUDIT_rev0974.md"),
    Path("REVISION_NOTES_rev0974.md"),
    Path("PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md"),
    Path("REVISION_NOTES_rev0975.md"),
    Path("EXACT_TRANSIENT_NAMESPACE_RETENTION_CUTPOINT_AUDIT_rev0976.md"),
    Path("REVISION_NOTES_rev0976.md"),
    Path("EXACT_LIVE_PAYLOAD_CAPABILITY_CUTPOINT_AUDIT_rev0977.md"),
    Path("PAYLOAD_USE_LEASE_AND_SNAPSHOT_READER_FENCE_AUDIT_rev0977.md"),
    Path("REVISION_NOTES_rev0977.md"),
    Path("PROCESS_STORE_LIVE_CAPABILITY_AND_WRITER_FENCED_RETENTION_AUDIT_rev0978.md"),
    Path("REVISION_NOTES_rev0978.md"),
    Path("DURABLE_PAYLOAD_RETENTION_MARK_AND_POLICY_AUDIT_rev0979.md"),
    Path("REVISION_NOTES_rev0979.md"),
    Path("REPLICA_DATABASE_LINEAGE_AND_RETENTION_WITNESS_AUDIT_rev0980.md"),
    Path("REVISION_NOTES_rev0980.md"),
    Path("OFFLINE_DATABASE_RECOVERY_AND_DEPLOYMENT_SINGLETON_AUDIT_rev0981.md"),
    Path("REVISION_NOTES_rev0981.md"),
    Path("OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md"),
    Path("REVISION_NOTES_rev0982.md"),
    Path("src/sync_replica_database_backup.hpp"),
    Path("src/sync_replica_database_backup.cpp"),
    Path("src/sync_replica_deployment_binding.hpp"),
    Path("src/sync_replica_deployment_binding.cpp"),
    Path("tests/persistence/sqlite_snapshot_seal_tests.cpp"),
    Path("tools/audit_sync_replica_database_backup.py"),
    Path("OFFLINE_REPLICA_DATABASE_REPLACEMENT_AUDIT_rev0983.md"),
    Path("REVISION_NOTES_rev0983.md"),
    Path("src/persistence/sqlite_live_backup.hpp"),
    Path("src/persistence/sqlite_live_backup.cpp"),
    Path("src/sync_replica_database_artifact_internal.hpp"),
    Path("src/sync_replica_database_replacement.hpp"),
    Path("src/sync_replica_database_replacement.cpp"),
    Path("tests/persistence/sqlite_live_backup_tests.cpp"),
    Path("tools/audit_sqlite_live_backup.py"),
    Path("tools/audit_sync_replica_database_replacement.py"),
    Path("IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md"),
    Path("REVISION_NOTES_rev0984.md"),
    Path("src/sync_replica_database_replacement_receipt_internal.hpp"),
    Path("src/sync_replica_database_replacement_receipt.cpp"),
    Path("ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md"),
    Path("REVISION_NOTES_rev0985.md"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.cpp"),
    Path("src/sync_replica_tls_policy_sqlite_profile.hpp"),
    Path("src/sync_replica_tls_policy_sqlite_profile.cpp"),
    Path("src/sync_replica_tls_membership_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_membership_sqlite_owner.cpp"),
    Path("src/sync_replica_tls_membership_anchor_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_membership_anchor_sqlite_owner.cpp"),
    Path("tools/test_anonsync_database_role_backup.py"),
    Path("tools/audit_sync_replica_database_role_backup.py"),
    Path("BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md"),
    Path("REVISION_NOTES_rev0987.md"),
    Path("src/sync_replica_selective_sync_policy.hpp"),
    Path("src/sync_replica_selective_sync_policy.cpp"),
    Path("tests/sync_replica_selective_sync_policy_test.cpp"),
    Path("tools/test_anonsync_folder_cli.py"),
    Path("tools/audit_sync_replica_selective_sync.py"),
    Path("TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md"),
    Path("REVISION_NOTES_rev0988.md"),
    Path("tools/audit_sync_replica_targeted_catalog_cutpoint.py"),
    Path("TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md"),
    Path("REVISION_NOTES_rev0989.md"),
    Path("tools/audit_sync_replica_targeted_path_cutpoint.py"),
    Path("TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md"),
    Path("REVISION_NOTES_rev0991.md"),
    Path("src/sync_replica_digest_accumulator.hpp"),
    Path("src/sync_replica_digest_accumulator.cpp"),
    Path("tests/sync_replica_hash_graph_projection_test.cpp"),
    Path("tests/sync_replica_prepared_publication_test.cpp"),
    Path("tools/audit_sync_replica_targeted_local_publication.py"),
    Path("MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md"),
    Path("REVISION_NOTES_rev0992.md"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tools/audit_sync_replica_content_defined_delta.py"),
    Path("tools/audit_sync_replica_manifest_reference.py"),
    Path("REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md"),
    Path("REVISION_NOTES_rev0993.md"),
    Path("tools/audit_sync_replica_targeted_source_access.py"),
    Path("CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"),
    Path("REVISION_NOTES_rev0994.md"),
    Path("src/sync_replica_content_defined_chunker.hpp"),
    Path("src/sync_replica_content_defined_chunker.cpp"),
    Path("tests/sync_replica_content_defined_chunker_test.cpp"),
    Path("SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md"),
    Path("REVISION_NOTES_rev0995.md"),
    Path("tools/audit_sync_replica_source_chunk_index.py"),
    Path("MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md"),
    Path("REVISION_NOTES_rev0996.md"),
    Path("tools/audit_sync_replica_multi_range_window.py"),
    Path("DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md"),
    Path("REVISION_NOTES_rev0997.md"),
    Path("src/sync_replica_tls_record_exchange.hpp"),
    Path("src/sync_replica_tls_record_exchange.cpp"),
    Path("tests/sync_replica_reconciliation_frame_memory_test.cpp"),
    Path("tools/audit_sync_replica_response_frame_memory.py"),
    Path("SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md"),
    Path("tests/sync_replica_reconciliation_memory_shape_test.cpp"),
    Path("tools/audit_sync_replica_response_memory_shape.py"),
    Path("DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md"),
    Path("REVISION_NOTES_rev0998.md"),
    Path("tests/sync_replica_reconciliation_source_frame_memory_test.cpp"),
    Path("tools/audit_sync_replica_direct_source_frame.py"),
    Path("BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md"),
    Path("REVISION_NOTES_rev0999.md"),
    Path("tools/audit_sync_replica_bounded_history_access.py"),
    Path("CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md"),
    Path("REVISION_NOTES_rev1000.md"),
    Path("tools/audit_sync_replica_cross_file_delta.py"),
    Path("BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md"),
    Path("REVISION_NOTES_rev1001.md"),
    Path("tools/audit_sync_replica_bounded_cross_file_projection.py"),
    Path("BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md"),
    Path("REVISION_NOTES_rev1002.md"),
    Path("tools/audit_sync_replica_bounded_local_reuse.py"),
    Path("BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md"),
    Path("REVISION_NOTES_rev1003.md"),
    Path("tools/audit_sync_replica_bounded_predecessor_projection.py"),
    Path("BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md"),
    Path("REVISION_NOTES_rev1004.md"),
    Path("src/sync_replica_file_payload_terminal_verification_state.hpp"),
    Path("src/sync_replica_file_payload_terminal_verification_state.cpp"),
    Path("tests/sync_replica_file_payload_terminal_verification_state_test.cpp"),
    Path("tools/audit_sync_replica_terminal_verification_continuation.py"),
    Path("TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md"),
    Path("REVISION_NOTES_rev1005.md"),
    Path("tools/audit_sync_replica_targeted_terminal_local_pulse.py"),
    Path("RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md"),
    Path("REVISION_NOTES_rev1006.md"),
    Path("tests/sync_replica_terminal_verification_fixture.cpp"),
    Path("tools/test_anonsync_service_terminal_verification_scheduler.py"),
    Path("tools/audit_sync_replica_receiver_local_terminal_scheduler.py"),
    Path("BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md"),
    Path("REVISION_NOTES_rev1007.md"),
    Path("tools/audit_sync_replica_bounded_source_manifest_projection.py"),
    Path("SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md"),
    Path("REVISION_NOTES_rev1008.md"),
    Path("DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md"),
    Path("REVISION_NOTES_rev1010.md"),
    Path("src/sync_replica_source_manifest_checkpoint.hpp"),
    Path("src/sync_replica_source_manifest_checkpoint.cpp"),
    Path("tests/sync_replica_source_manifest_checkpoint_test.cpp"),
    Path("tests/sync_replica_source_manifest_restart_test.cpp"),
    Path("tools/audit_sync_replica_durable_source_manifest_checkpoint.py"),
    Path("SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md"),
    Path("REVISION_NOTES_rev1011.md"),
    Path("tools/audit_sync_replica_source_manifest_checkpoint_memory.py"),
    Path("COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md"),
    Path("REVISION_NOTES_rev1012.md"),
    Path("src/sync_replica_reconciliation_compact_manifest.hpp"),
    Path("src/sync_replica_reconciliation_compact_manifest.cpp"),
    Path("tests/sync_replica_reconciliation_compact_manifest_test.cpp"),
    Path("tools/audit_sync_replica_compact_source_manifest_cache.py"),
    Path("FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md"),
    Path("REVISION_NOTES_rev1013.md"),
    Path("tools/audit_sync_replica_fixed_binary_manifest.py"),
    Path("BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md"),
    Path("REVISION_NOTES_rev1014.md"),
    Path("tools/audit_sync_replica_borrowed_manifest_frame.py"),
    Path("ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md"),
    Path("REVISION_NOTES_rev1015.md"),
    Path("tools/audit_sync_replica_active_source_manifest_memory.py"),
    Path("TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md"),
    Path("tools/audit_sync_replica_terminal_manifest_cache.py"),
    Path("LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md"),
    Path("REVISION_NOTES_rev1016.md"),
    Path("LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md"),
    Path("REVISION_NOTES_rev1017.md"),
    Path("HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md"),
    Path("SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md"),
    Path("REVISION_NOTES_rev1018.md"),
    Path("IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md"),
    Path("REVISION_NOTES_rev1019.md"),
    Path("tools/audit_sync_replica_identity_preserving_rename.py"),
    Path("BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md"),
    Path("REVISION_NOTES_rev1020.md"),
    Path("tools/audit_sync_replica_bounded_rename_planning.py"),
    Path("src/sync_replica_delivery_service.cpp"),
    Path("tools/audit_sync_replica_service_startup.py"),
    Path("tools/test_anonsync_sparse_multiterabyte_selective_resources.py"),
    Path("tools/audit_sync_sparse_multiterabyte_selective_resources.py"),
    Path("src/sync_linux_process_resources.hpp"),
    Path("src/sync_linux_process_resources.cpp"),
    Path("tests/sync_linux_process_resources_test.cpp"),
    Path("tests/sync_linux_process_resources_fixture.cpp"),
    Path("tools/test_anonsync_process_resources.py"),
    Path("tools/audit_sync_linux_process_resources.py"),
    Path("tools/test_anonsync_service_source_manifest_scheduler.py"),
    Path("tools/audit_sync_replica_source_local_manifest_scheduler.py"),
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


def source_window(text: str, start_signature: str, end_signature: str) -> str:
    start = text.find(start_signature)
    if start < 0:
        return ""
    end = text.find(end_signature, start + len(start_signature))
    return text[start:] if end < 0 else text[start:end]


def last_function_body(text: str, signature: str) -> str:
    start = text.rfind(signature)
    if start < 0:
        return ""
    return function_body(text[start:], signature)


def cmake_call(text: str, command_prefix: str) -> str:
    return delimited_body(text, command_prefix, "(", ")")


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def normalized_prose(text: str) -> str:
    """Collapse Markdown wrapping before testing prose-only audit claims."""
    return " ".join(text.split())


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

    active_projection_roots = (
        Path("cmake"),
        Path("fuzz"),
        Path("include"),
        Path("src"),
        Path("tests"),
        Path("third_party"),
        Path("tools"),
    )
    executable_active_sources = sorted(
        path.relative_to(root).as_posix()
        for projection_root in active_projection_roots
        for path in (root / projection_root).rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and (path.stat().st_mode & 0o111) != 0
    )
    require(
        not executable_active_sources,
        "active_source_projection_contains_no_accidental_executable_modes",
        f"executable_active_sources={executable_active_sources}",
    )

    required_bytes = {
        path.as_posix(): (root / path).read_bytes()
        for path in REQUIRED
    }
    embedded_nul_paths = sorted(
        path for path, data in required_bytes.items() if b"\0" in data
    )
    require(
        not embedded_nul_paths,
        "required_release_sources_and_records_are_nul_free",
        f"embedded_nul_paths={embedded_nul_paths}",
    )
    utf8_failures: list[str] = []
    text: dict[str, str] = {}
    for path, data in required_bytes.items():
        try:
            text[path] = data.decode("utf-8")
        except UnicodeDecodeError as error:
            utf8_failures.append(f"{path}: {error}")
    require(
        not utf8_failures,
        "required_release_sources_and_records_are_utf8",
        f"utf8_failures={utf8_failures}",
    )
    if embedded_nul_paths or utf8_failures:
        return emit(root, args.json, checks)
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    sha256_digest_h = text["src/sha256_digest.hpp"]
    sha256_digest = text["src/sha256_digest.cpp"]
    directory_authority_h = text["src/sync_directory_authority.hpp"]
    directory_authority_internal = text[
        "src/sync_directory_authority_internal.hpp"
    ]
    directory_authority = text["src/sync_directory_authority.cpp"]
    resolver_h = text["src/sync_posix_directory_resolution.hpp"]
    resolver = text["src/sync_posix_directory_resolution.cpp"]
    atomic_publication_h = text["src/sync_atomic_file_publication.hpp"]
    atomic_publication = text["src/sync_atomic_file_publication.cpp"]
    descriptor_snapshot_h = text["src/sync_posix_descriptor_snapshot.hpp"]
    descriptor_snapshot = text["src/sync_posix_descriptor_snapshot.cpp"]
    metadata_codec_h = text[
        "src/sync_posix_regular_file_snapshot_codec.hpp"
    ]
    metadata_codec = text[
        "src/sync_posix_regular_file_snapshot_codec.cpp"
    ]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store = text["src/sync_replica_file_payload_store.cpp"]
    resumable_h = text["src/resumable_sha256.hpp"]
    resumable = text["src/resumable_sha256.cpp"]
    scrub_state_h = text["src/sync_replica_file_payload_scrub_state.hpp"]
    scrub_state = text["src/sync_replica_file_payload_scrub_state.cpp"]
    retention_mark_h = text[
        "src/sync_replica_file_payload_retention_mark.hpp"
    ]
    retention_mark = text[
        "src/sync_replica_file_payload_retention_mark.cpp"
    ]
    verification_index_h = text[
        "src/sync_replica_file_payload_verification_index.hpp"
    ]
    verification_index = text[
        "src/sync_replica_file_payload_verification_index.cpp"
    ]
    file_delivery_protocol_h = text["src/sync_replica_file_delivery_protocol.hpp"]
    reconciliation_service = text["src/sync_replica_reconciliation_service.cpp"]
    peer_server = text["src/sync_replica_peer_server_owner.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    folder_cli = text["src/anonsync_folder.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    local_status_h = text["src/sync_local_status_socket.hpp"]
    local_status = text["src/sync_local_status_socket.cpp"]
    historical_query_h = text[
        "src/sync_replica_historical_version_query.hpp"
    ]
    historical_inventory_json_h = text[
        "src/sync_replica_historical_version_inventory_json.hpp"
    ]
    historical_inventory_json = text[
        "src/sync_replica_historical_version_inventory_json.cpp"
    ]
    folder_observer_h = text["src/sync_replica_folder_observer.hpp"]
    folder_observer = text["src/sync_replica_folder_observer.cpp"]
    model_h = text["src/sync_replica_model.hpp"]
    model = text["src/sync_replica_model.cpp"]
    sqlite_owner_h = text["src/sync_replica_sqlite_owner.hpp"]
    sqlite_owner = text["src/sync_replica_sqlite_owner.cpp"]
    folder_scan_h = text["src/sync_replica_folder_scan_owner.hpp"]
    folder_scan = text["src/sync_replica_folder_scan_owner.cpp"]
    folder_process_h = text["src/sync_replica_folder_process.hpp"]
    folder_process = text["src/sync_replica_folder_process.cpp"]
    operational_database_h = text[
        "src/sync_replica_operational_database.hpp"
    ]
    operational_database = text[
        "src/sync_replica_operational_database.cpp"
    ]
    peer_singleton_h = text[
        "src/sync_replica_peer_service_singleton.hpp"
    ]
    peer_singleton = text[
        "src/sync_replica_peer_service_singleton.cpp"
    ]
    peer_service_h = text["src/sync_replica_peer_service.hpp"]
    peer_service = text["src/sync_replica_peer_service.cpp"]
    peer_status_h = text["src/sync_replica_peer_service_status.hpp"]
    peer_status = text["src/sync_replica_peer_service_status.cpp"]
    peer_evidence_h = text[
        "src/sync_replica_peer_service_integrity_evidence.hpp"
    ]
    tls_transport_h = text["src/sync_replica_tls_transport.hpp"]
    tls_transport = text["src/sync_replica_tls_transport.cpp"]
    sync_once_h = text["src/sync_replica_sync_once.hpp"]
    sync_once = text["src/sync_replica_sync_once.cpp"]
    deployment_manifest_h = text["src/sync_replica_deployment_manifest.hpp"]
    payload_extent_h = text["src/sync_replica_payload_extent.hpp"]
    reconciliation_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    reconciliation_protocol_cpp = text[
        "src/sync_replica_reconciliation_protocol.cpp"
    ]
    reconciliation_service_h = text[
        "src/sync_replica_reconciliation_service.hpp"
    ]
    service_h = text["src/sync_replica_file_delivery_service.hpp"]
    service = text["src/sync_replica_file_delivery_service.cpp"]
    reconciliation_service = text["src/sync_replica_reconciliation_service.cpp"]
    dispatch_h = text["src/sync_replica_file_tls_dispatch.hpp"]
    dispatch = text["src/sync_replica_file_tls_dispatch.cpp"]
    atomic_runtime = text["tests/sync_atomic_file_publication_test.cpp"]
    bounded_runtime = text["tests/sync_bounded_regular_file_test.cpp"]
    local_status_runtime = text["tests/sync_local_status_socket_test.cpp"]
    stream_connector_runtime = text[
        "tests/sync_replica_stream_connector_test.cpp"
    ]
    runtime = text["tests/sync_replica_file_payload_store_test.cpp"]
    resumable_runtime = text["tests/resumable_sha256_test.cpp"]
    scrub_state_runtime = text[
        "tests/sync_replica_file_payload_scrub_state_test.cpp"
    ]
    retention_mark_runtime = text[
        "tests/sync_replica_file_payload_retention_mark_test.cpp"
    ]
    verification_index_runtime = text[
        "tests/sync_replica_file_payload_verification_index_test.cpp"
    ]
    file_delivery_runtime = text["tests/sync_replica_file_delivery_protocol_test.cpp"]
    reconciliation_runtime = text["tests/sync_replica_reconciliation_service_test.cpp"]
    folder_observer_runtime = text[
        "tests/sync_replica_folder_observer_test.cpp"
    ]
    network_model_runtime = text["tests/sync_replica_network_model_test.cpp"]
    sqlite_owner_runtime = text["tests/sync_replica_sqlite_owner_test.cpp"]
    folder_scan_runtime = text["tests/sync_replica_folder_scan_owner_test.cpp"]
    peer_evidence_runtime = text[
        "tests/sync_replica_peer_service_integrity_evidence_test.cpp"
    ]
    tls_transport_runtime = text["tests/sync_replica_tls_transport_test.cpp"]
    sync_once_runtime = text["tests/sync_replica_sync_once_test.cpp"]
    service_runtime = text["tests/sync_replica_file_delivery_service_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    sync_process_runtime = text["tools/test_anonsync_sync_process.py"]
    reconciliation_process_runtime = text[
        "tools/test_anonsync_replica_reconciliation_process.py"
    ]
    service_process_runtime = text["tools/test_anonsync_service_process.py"]
    service_i2p_ingress_runtime = text[
        "tools/test_anonsync_service_i2p_ingress.py"
    ]
    i2p_negative_control_start = service_i2p_ingress_runtime.find(
        "def expect_direct_pull_blocked("
    )
    i2p_negative_control = service_i2p_ingress_runtime[
        i2p_negative_control_start:
        service_i2p_ingress_runtime.find("\ndef main()", i2p_negative_control_start)
    ]
    service_configuration_runtime = text[
        "tools/test_anonsync_service_configuration_status.py"
    ]
    database_recovery_runtime = text[
        "tools/test_anonsync_database_recovery.py"
    ]
    database_open_policy_audit = text[
        "tools/audit_anonsync_replica_database_open_policy.py"
    ]
    service_folder_wake_runtime = text[
        "tools/test_anonsync_service_folder_wake.py"
    ]
    provisioning_runtime = text["tools/test_anonsync_provisioning.py"]
    design = text["DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md"]
    lease_design = text[
        "PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md"
    ]
    revision_notes = text["REVISION_NOTES_rev0894.md"]
    checkpoint_design = text[
        "DURABLE_PAYLOAD_VERIFICATION_CHECKPOINT_AUDIT_rev0954.md"
    ]
    rev0954_notes = text["REVISION_NOTES_rev0954.md"]
    scrub_design = text[
        "DURABLE_BYTE_BOUNDED_PAYLOAD_SCRUB_AUDIT_rev0955.md"
    ]
    rev0955_notes = text["REVISION_NOTES_rev0955.md"]
    service_recovery_design = text[
        "PAYLOAD_INTEGRITY_SERVICE_RECOVERY_AUDIT_rev0956.md"
    ]
    rev0956_notes = text["REVISION_NOTES_rev0956.md"]
    reproof_handoff_design = text[
        "PAYLOAD_REPROOF_HANDOFF_AND_EXACT_OWNER_AUDIT_rev0957.md"
    ]
    rev0957_notes = text["REVISION_NOTES_rev0957.md"]
    scrub_restart_fence_design = text[
        "SCRUB_WRITE_AHEAD_RESTART_FENCE_AUDIT_rev0958.md"
    ]
    rev0958_notes = text["REVISION_NOTES_rev0958.md"]
    minimum_reader_design = text[
        "MINIMUM_READER_IDENTITY_MIGRATION_AUDIT_rev0959.md"
    ]
    rev0959_notes = text["REVISION_NOTES_rev0959.md"]
    owner_recheck_design = text[
        "OWNER_TRIGGERED_PAYLOAD_RECHECK_AUDIT_rev0960.md"
    ]
    rev0960_notes = text["REVISION_NOTES_rev0960.md"]
    quarantine_design = text[
        "EXACT_CORRUPT_PAYLOAD_QUARANTINE_AND_LINEARIZED_LOCAL_ACTION_AUDIT_rev0961.md"
    ]
    rev0961_notes = text["REVISION_NOTES_rev0961.md"]
    quarantine_release_design = text[
        "EXACT_QUARANTINE_RELEASE_AND_PROOF_REUSE_AUDIT_rev0962.md"
    ]
    rev0962_notes = text["REVISION_NOTES_rev0962.md"]
    quarantine_inventory_design = text[
        "RESTART_DISCOVERABLE_QUARANTINE_INVENTORY_AUDIT_rev0963.md"
    ]
    rev0963_notes = text["REVISION_NOTES_rev0963.md"]
    bounded_directory_batch_design = text[
        "BOUNDED_RESUMABLE_DIRECTORY_COMPONENT_BATCH_AUDIT_rev0964.md"
    ]
    rev0964_notes = text["REVISION_NOTES_rev0964.md"]
    global_directory_batch_design = text[
        "GLOBAL_RESUMABLE_DIRECTORY_BATCH_LIFETIME_AUDIT_rev0965.md"
    ]
    rev0965_notes = text["REVISION_NOTES_rev0965.md"]
    causal_version_design = text[
        "EXPLICIT_CAUSAL_VERSION_INSPECTION_AND_ROOTED_RESTORE_AUDIT_rev0966.md"
    ]
    rev0966_notes = text["REVISION_NOTES_rev0966.md"]
    paged_history_design = text[
        "PAGED_CAUSAL_VERSION_QUERY_AND_GROUPED_PROJECTION_AUDIT_rev0967.md"
    ]
    rev0967_notes = text["REVISION_NOTES_rev0967.md"]
    source_cutpoint_design = text[
        "EXACT_CAUSAL_HISTORY_SOURCE_CUTPOINT_AUDIT_rev0968.md"
    ]
    rev0968_notes = text["REVISION_NOTES_rev0968.md"]
    exact_current_restore_design = text[
        "EXACT_CURRENT_BOUND_HISTORICAL_RESTORE_AUDIT_rev0969.md"
    ]
    rev0969_notes = text["REVISION_NOTES_rev0969.md"]
    metadata_history_design = text[
        "CAUSAL_METADATA_HISTORY_INSPECTION_AUDIT_rev0970.md"
    ]
    rev0970_notes = text["REVISION_NOTES_rev0970.md"]
    bounded_historical_status_design = text[
        "BOUNDED_HISTORICAL_STATUS_PAGE_AND_SINGLE_RESULT_AUDIT_rev0971.md"
    ]
    rev0971_notes = text["REVISION_NOTES_rev0971.md"]
    retained_reachability_frontier_design = text[
        "RETAINED_PAYLOAD_REACHABILITY_AND_CANONICAL_STATUS_FRONTIER_AUDIT_rev0972.md"
    ]
    rev0972_notes = text["REVISION_NOTES_rev0972.md"]
    retention_pin_design = text[
        "HISTORICAL_VERSION_RETENTION_PIN_AUTHORITY_AUDIT_rev0973.md"
    ]
    rev0973_notes = text["REVISION_NOTES_rev0973.md"]
    retention_plan_design = text[
        "DELETION_FREE_EXACT_RETENTION_PLAN_AUDIT_rev0974.md"
    ]
    rev0974_notes = text["REVISION_NOTES_rev0974.md"]
    retention_mark_witness_design = text[
        "PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md"
    ]
    rev0975_notes = text["REVISION_NOTES_rev0975.md"]
    transient_cutpoint_design = text[
        "EXACT_TRANSIENT_NAMESPACE_RETENTION_CUTPOINT_AUDIT_rev0976.md"
    ]
    rev0976_notes = text["REVISION_NOTES_rev0976.md"]
    live_capability_design = text[
        "EXACT_LIVE_PAYLOAD_CAPABILITY_CUTPOINT_AUDIT_rev0977.md"
    ]
    payload_use_lease_design = text[
        "PAYLOAD_USE_LEASE_AND_SNAPSHOT_READER_FENCE_AUDIT_rev0977.md"
    ]
    rev0977_notes = text["REVISION_NOTES_rev0977.md"]
    process_store_writer_fence_design = text[
        "PROCESS_STORE_LIVE_CAPABILITY_AND_WRITER_FENCED_RETENTION_AUDIT_rev0978.md"
    ]
    rev0978_notes = text["REVISION_NOTES_rev0978.md"]
    durable_retention_mark_design = text[
        "DURABLE_PAYLOAD_RETENTION_MARK_AND_POLICY_AUDIT_rev0979.md"
    ]
    rev0979_notes = text["REVISION_NOTES_rev0979.md"]
    database_lineage_design = text[
        "REPLICA_DATABASE_LINEAGE_AND_RETENTION_WITNESS_AUDIT_rev0980.md"
    ]
    rev0980_notes = text["REVISION_NOTES_rev0980.md"]
    offline_database_recovery_design = text[
        "OFFLINE_DATABASE_RECOVERY_AND_DEPLOYMENT_SINGLETON_AUDIT_rev0981.md"
    ]
    rev0981_notes = text["REVISION_NOTES_rev0981.md"]
    offline_database_backup_design = text[
        "OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md"
    ]
    rev0982_notes = text["REVISION_NOTES_rev0982.md"]
    database_backup_header = text["src/sync_replica_database_backup.hpp"]
    database_backup_source = text["src/sync_replica_database_backup.cpp"]
    deployment_binding_header = text["src/sync_replica_deployment_binding.hpp"]
    deployment_binding_source = text["src/sync_replica_deployment_binding.cpp"]
    sqlite_snapshot_seal_test = text[
        "tests/persistence/sqlite_snapshot_seal_tests.cpp"
    ]
    database_backup_audit = text[
        "tools/audit_sync_replica_database_backup.py"
    ]
    offline_database_replacement_design = text[
        "OFFLINE_REPLICA_DATABASE_REPLACEMENT_AUDIT_rev0983.md"
    ]
    rev0983_notes = text["REVISION_NOTES_rev0983.md"]
    sqlite_live_backup_header = text[
        "src/persistence/sqlite_live_backup.hpp"
    ]
    sqlite_live_backup_source = text[
        "src/persistence/sqlite_live_backup.cpp"
    ]
    sqlite_live_backup_runtime = text[
        "tests/persistence/sqlite_live_backup_tests.cpp"
    ]
    database_artifact_internal = text[
        "src/sync_replica_database_artifact_internal.hpp"
    ]
    database_replacement_header = text[
        "src/sync_replica_database_replacement.hpp"
    ]
    database_replacement_source = text[
        "src/sync_replica_database_replacement.cpp"
    ]
    database_replacement_audit = text[
        "tools/audit_sync_replica_database_replacement.py"
    ]
    immutable_database_replacement_receipt_design = text[
        "IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md"
    ]
    rev0984_notes = text["REVISION_NOTES_rev0984.md"]
    database_replacement_receipt_header = text[
        "src/sync_replica_database_replacement_receipt_internal.hpp"
    ]
    database_replacement_receipt_source = text[
        "src/sync_replica_database_replacement_receipt.cpp"
    ]
    sqlite_live_backup_audit = text[
        "tools/audit_sqlite_live_backup.py"
    ]
    role_bound_database_backup_design = text[
        "ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md"
    ]
    rev0985_notes = text["REVISION_NOTES_rev0985.md"]
    file_effect_owner_header = text[
        "src/sync_replica_file_effect_sqlite_owner.hpp"
    ]
    file_effect_owner_source = text[
        "src/sync_replica_file_effect_sqlite_owner.cpp"
    ]
    tls_policy_profile_header = text[
        "src/sync_replica_tls_policy_sqlite_profile.hpp"
    ]
    tls_policy_profile_source = text[
        "src/sync_replica_tls_policy_sqlite_profile.cpp"
    ]
    tls_membership_owner_header = text[
        "src/sync_replica_tls_membership_sqlite_owner.hpp"
    ]
    tls_membership_owner_source = text[
        "src/sync_replica_tls_membership_sqlite_owner.cpp"
    ]
    tls_anchor_owner_header = text[
        "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp"
    ]
    tls_anchor_owner_source = text[
        "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp"
    ]
    role_backup_runtime = text["tools/test_anonsync_database_role_backup.py"]
    role_backup_audit = text[
        "tools/audit_sync_replica_database_role_backup.py"
    ]
    selective_sync_design = text[
        "BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md"
    ]
    rev0987_notes = text["REVISION_NOTES_rev0987.md"]
    selective_policy_header = text[
        "src/sync_replica_selective_sync_policy.hpp"
    ]
    selective_policy_source = text[
        "src/sync_replica_selective_sync_policy.cpp"
    ]
    selective_policy_runtime = text[
        "tests/sync_replica_selective_sync_policy_test.cpp"
    ]
    folder_cli_process_runtime = text["tools/test_anonsync_folder_cli.py"]
    selective_sync_audit = text[
        "tools/audit_sync_replica_selective_sync.py"
    ]
    targeted_catalog_design = text[
        "TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md"
    ]
    rev0988_notes = text["REVISION_NOTES_rev0988.md"]
    targeted_catalog_audit = text[
        "tools/audit_sync_replica_targeted_catalog_cutpoint.py"
    ]
    targeted_replica_design = text[
        "TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md"
    ]
    rev0989_notes = text["REVISION_NOTES_rev0989.md"]
    targeted_replica_audit = text[
        "tools/audit_sync_replica_targeted_path_cutpoint.py"
    ]
    targeted_local_design = text[
        "TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md"
    ]
    rev0991_notes = text["REVISION_NOTES_rev0991.md"]
    accumulator_h = text["src/sync_replica_digest_accumulator.hpp"]
    accumulator = text["src/sync_replica_digest_accumulator.cpp"]
    hash_graph_runtime = text[
        "tests/sync_replica_hash_graph_projection_test.cpp"
    ]
    prepared_publication_runtime = text[
        "tests/sync_replica_prepared_publication_test.cpp"
    ]
    targeted_local_audit = text[
        "tools/audit_sync_replica_targeted_local_publication.py"
    ]
    manifest_reference_design = text[
        "MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md"
    ]
    rev0992_notes = text["REVISION_NOTES_rev0992.md"]
    reconciliation_protocol_header = text[
        "src/sync_replica_reconciliation_protocol.hpp"
    ]
    reconciliation_protocol_source = text[
        "src/sync_replica_reconciliation_protocol.cpp"
    ]
    reconciliation_service_header = text[
        "src/sync_replica_reconciliation_service.hpp"
    ]
    reconciliation_tls_header = text[
        "src/sync_replica_reconciliation_tls_exchange.hpp"
    ]
    reconciliation_tls_source = text[
        "src/sync_replica_reconciliation_tls_exchange.cpp"
    ]
    reconciliation_protocol_runtime = text[
        "tests/sync_replica_reconciliation_protocol_test.cpp"
    ]
    manifest_reference_audit = text[
        "tools/audit_sync_replica_manifest_reference.py"
    ]
    targeted_source_access_design = text[
        "REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md"
    ]
    rev0993_notes = text["REVISION_NOTES_rev0993.md"]
    targeted_source_access_audit = text[
        "tools/audit_sync_replica_targeted_source_access.py"
    ]
    content_defined_delta_design = text[
        "CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"
    ]
    rev0994_notes = text["REVISION_NOTES_rev0994.md"]
    content_defined_delta_audit = text[
        "tools/audit_sync_replica_content_defined_delta.py"
    ]
    content_defined_chunker_header = text[
        "src/sync_replica_content_defined_chunker.hpp"
    ]
    content_defined_chunker_source = text[
        "src/sync_replica_content_defined_chunker.cpp"
    ]
    content_defined_chunker_runtime = text[
        "tests/sync_replica_content_defined_chunker_test.cpp"
    ]
    source_chunk_index_design = text[
        "SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md"
    ]
    rev0995_notes = text["REVISION_NOTES_rev0995.md"]
    source_chunk_index_audit = text[
        "tools/audit_sync_replica_source_chunk_index.py"
    ]
    multi_range_window_design = text[
        "MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md"
    ]
    rev0996_notes = text["REVISION_NOTES_rev0996.md"]
    multi_range_window_audit = text[
        "tools/audit_sync_replica_multi_range_window.py"
    ]
    response_frame_memory_design = text[
        "DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md"
    ]
    rev0997_notes = text["REVISION_NOTES_rev0997.md"]
    response_frame_memory_audit = text[
        "tools/audit_sync_replica_response_frame_memory.py"
    ]
    tls_record_exchange_h = text[
        "src/sync_replica_tls_record_exchange.hpp"
    ]
    tls_record_exchange = text[
        "src/sync_replica_tls_record_exchange.cpp"
    ]
    response_frame_memory_runtime = text[
        "tests/sync_replica_reconciliation_frame_memory_test.cpp"
    ]
    response_memory_shape_design = text[
        "SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md"
    ]
    reconciliation_memory_shape_runtime = text[
        "tests/sync_replica_reconciliation_memory_shape_test.cpp"
    ]
    response_memory_shape_audit = text[
        "tools/audit_sync_replica_response_memory_shape.py"
    ]
    direct_source_frame_design = text[
        "DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md"
    ]
    rev0998_notes = text["REVISION_NOTES_rev0998.md"]
    direct_source_frame_runtime = text[
        "tests/sync_replica_reconciliation_source_frame_memory_test.cpp"
    ]
    direct_source_frame_audit = text[
        "tools/audit_sync_replica_direct_source_frame.py"
    ]
    bounded_history_design = text[
        "BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md"
    ]
    rev0999_notes = text["REVISION_NOTES_rev0999.md"]
    bounded_history_audit = text[
        "tools/audit_sync_replica_bounded_history_access.py"
    ]
    cross_file_delta_design = text[
        "CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md"
    ]
    rev1000_notes = text["REVISION_NOTES_rev1000.md"]
    cross_file_delta_audit = text[
        "tools/audit_sync_replica_cross_file_delta.py"
    ]
    bounded_cross_file_projection_design = text[
        "BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md"
    ]
    rev1001_notes = text["REVISION_NOTES_rev1001.md"]
    bounded_cross_file_projection_audit = text[
        "tools/audit_sync_replica_bounded_cross_file_projection.py"
    ]
    bounded_local_reuse_design = text[
        "BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md"
    ]
    rev1002_notes = text["REVISION_NOTES_rev1002.md"]
    bounded_local_reuse_audit = text[
        "tools/audit_sync_replica_bounded_local_reuse.py"
    ]
    bounded_predecessor_projection_design = text[
        "BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md"
    ]
    rev1003_notes = text["REVISION_NOTES_rev1003.md"]
    bounded_predecessor_projection_audit = text[
        "tools/audit_sync_replica_bounded_predecessor_projection.py"
    ]
    terminal_verification_design = text[
        "BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md"
    ]
    rev1004_notes = text["REVISION_NOTES_rev1004.md"]
    terminal_verification_state_h = text[
        "src/sync_replica_file_payload_terminal_verification_state.hpp"
    ]
    terminal_verification_state = text[
        "src/sync_replica_file_payload_terminal_verification_state.cpp"
    ]
    terminal_verification_state_runtime = text[
        "tests/sync_replica_file_payload_terminal_verification_state_test.cpp"
    ]
    terminal_verification_audit = text[
        "tools/audit_sync_replica_terminal_verification_continuation.py"
    ]
    targeted_terminal_design = text[
        "TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md"
    ]
    rev1005_notes = text["REVISION_NOTES_rev1005.md"]
    targeted_terminal_audit = text[
        "tools/audit_sync_replica_targeted_terminal_local_pulse.py"
    ]
    receiver_local_terminal_design = text[
        "RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md"
    ]
    rev1006_notes = text["REVISION_NOTES_rev1006.md"]
    receiver_local_terminal_fixture = text[
        "tests/sync_replica_terminal_verification_fixture.cpp"
    ]
    receiver_local_terminal_runtime = text[
        "tools/test_anonsync_service_terminal_verification_scheduler.py"
    ]
    receiver_local_terminal_audit = text[
        "tools/audit_sync_replica_receiver_local_terminal_scheduler.py"
    ]
    bounded_source_manifest_design = text[
        "BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md"
    ]
    rev1007_notes = text["REVISION_NOTES_rev1007.md"]
    bounded_source_manifest_audit = text[
        "tools/audit_sync_replica_bounded_source_manifest_projection.py"
    ]
    source_local_manifest_design = text[
        "SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md"
    ]
    rev1008_notes = text["REVISION_NOTES_rev1008.md"]
    source_local_manifest_runtime = text[
        "tools/test_anonsync_service_source_manifest_scheduler.py"
    ]
    source_local_manifest_audit = text[
        "tools/audit_sync_replica_source_local_manifest_scheduler.py"
    ]
    durable_source_manifest_design = text[
        "DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md"
    ]
    rev1010_notes = text["REVISION_NOTES_rev1010.md"]
    source_manifest_checkpoint_memory_design = text[
        "SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md"
    ]
    rev1011_notes = text["REVISION_NOTES_rev1011.md"]
    source_manifest_checkpoint_memory_audit = text[
        "tools/audit_sync_replica_source_manifest_checkpoint_memory.py"
    ]
    compact_source_manifest_design = text[
        "COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md"
    ]
    rev1012_notes = text["REVISION_NOTES_rev1012.md"]
    compact_source_manifest_h = text[
        "src/sync_replica_reconciliation_compact_manifest.hpp"
    ]
    compact_source_manifest = text[
        "src/sync_replica_reconciliation_compact_manifest.cpp"
    ]
    compact_source_manifest_runtime = text[
        "tests/sync_replica_reconciliation_compact_manifest_test.cpp"
    ]
    compact_source_manifest_audit = text[
        "tools/audit_sync_replica_compact_source_manifest_cache.py"
    ]
    fixed_binary_manifest_design = text[
        "FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md"
    ]
    rev1013_notes = text["REVISION_NOTES_rev1013.md"]
    fixed_binary_manifest_audit = text[
        "tools/audit_sync_replica_fixed_binary_manifest.py"
    ]
    borrowed_manifest_frame_design = text[
        "BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md"
    ]
    rev1014_notes = text["REVISION_NOTES_rev1014.md"]
    borrowed_manifest_frame_audit = text[
        "tools/audit_sync_replica_borrowed_manifest_frame.py"
    ]
    active_source_manifest_memory_design = text[
        "ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md"
    ]
    rev1015_notes = text["REVISION_NOTES_rev1015.md"]
    active_source_manifest_memory_audit = text[
        "tools/audit_sync_replica_active_source_manifest_memory.py"
    ]
    terminal_manifest_cache_design = text[
        "TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md"
    ]
    terminal_manifest_cache_audit = text[
        "tools/audit_sync_replica_terminal_manifest_cache.py"
    ]
    linux_process_resources_design = text[
        "LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md"
    ]
    rev1016_notes = text["REVISION_NOTES_rev1016.md"]
    linux_process_resource_series_design = text[
        "LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md"
    ]
    rev1017_notes = text["REVISION_NOTES_rev1017.md"]
    history_cold_startup_design = text[
        "HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md"
    ]
    rev1018_notes = text["REVISION_NOTES_rev1018.md"]
    replica_delivery_service = text[
        "src/sync_replica_delivery_service.cpp"
    ]
    history_cold_startup_audit = text[
        "tools/audit_sync_replica_service_startup.py"
    ]
    sparse_selective_memory_design = text[
        "SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md"
    ]
    sparse_selective_process_runtime = text[
        "tools/test_anonsync_sparse_multiterabyte_selective_resources.py"
    ]
    sparse_selective_memory_audit = text[
        "tools/audit_sync_sparse_multiterabyte_selective_resources.py"
    ]
    identity_preserving_rename_design = text[
        "IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md"
    ]
    rev1019_notes = text["REVISION_NOTES_rev1019.md"]
    identity_preserving_rename_audit = text[
        "tools/audit_sync_replica_identity_preserving_rename.py"
    ]
    bounded_rename_planning_design = text[
        "BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md"
    ]
    rev1020_notes = text["REVISION_NOTES_rev1020.md"]
    bounded_rename_planning_audit = text[
        "tools/audit_sync_replica_bounded_rename_planning.py"
    ]
    linux_process_resources_h = text["src/sync_linux_process_resources.hpp"]
    linux_process_resources = text["src/sync_linux_process_resources.cpp"]
    linux_process_resources_runtime = text[
        "tests/sync_linux_process_resources_test.cpp"
    ]
    linux_process_resources_fixture = text[
        "tests/sync_linux_process_resources_fixture.cpp"
    ]
    linux_process_resources_process_runtime = text[
        "tools/test_anonsync_process_resources.py"
    ]
    linux_process_resources_audit = text[
        "tools/audit_sync_linux_process_resources.py"
    ]
    source_manifest_checkpoint_h = text[
        "src/sync_replica_source_manifest_checkpoint.hpp"
    ]
    source_manifest_checkpoint = text[
        "src/sync_replica_source_manifest_checkpoint.cpp"
    ]
    source_manifest_checkpoint_runtime = text[
        "tests/sync_replica_source_manifest_checkpoint_test.cpp"
    ]
    source_manifest_restart_runtime = text[
        "tests/sync_replica_source_manifest_restart_test.cpp"
    ]
    durable_source_manifest_audit = text[
        "tools/audit_sync_replica_durable_source_manifest_checkpoint.py"
    ]
    rev0959_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 959:"
    )
    rev0959_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0959_verifier_start
    )
    rev0959_verifier_block = (
        verifier[rev0959_verifier_start:rev0959_verifier_end]
        if rev0959_verifier_start >= 0 and rev0959_verifier_end >= 0
        else ""
    )
    rev0960_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 960:"
    )
    rev0960_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0960_verifier_start
    )
    rev0960_verifier_block = (
        verifier[rev0960_verifier_start:rev0960_verifier_end]
        if rev0960_verifier_start >= 0 and rev0960_verifier_end >= 0
        else ""
    )
    rev0961_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 961:"
    )
    rev0961_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0961_verifier_start
    )
    rev0961_verifier_block = (
        verifier[rev0961_verifier_start:rev0961_verifier_end]
        if rev0961_verifier_start >= 0 and rev0961_verifier_end >= 0
        else ""
    )
    rev0962_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 962:"
    )
    rev0962_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0962_verifier_start
    )
    rev0962_verifier_block = (
        verifier[rev0962_verifier_start:rev0962_verifier_end]
        if rev0962_verifier_start >= 0 and rev0962_verifier_end >= 0
        else ""
    )
    rev0963_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 963:"
    )
    rev0963_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0963_verifier_start
    )
    rev0963_verifier_block = (
        verifier[rev0963_verifier_start:rev0963_verifier_end]
        if rev0963_verifier_start >= 0 and rev0963_verifier_end >= 0
        else ""
    )
    rev0964_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 964:"
    )
    rev0964_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0964_verifier_start
    )
    rev0964_verifier_block = (
        verifier[rev0964_verifier_start:rev0964_verifier_end]
        if rev0964_verifier_start >= 0 and rev0964_verifier_end >= 0
        else ""
    )
    rev0965_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 965:"
    )
    rev0965_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0965_verifier_start
    )
    rev0965_verifier_block = (
        verifier[rev0965_verifier_start:rev0965_verifier_end]
        if rev0965_verifier_start >= 0 and rev0965_verifier_end >= 0
        else ""
    )
    rev0966_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 966:"
    )
    rev0966_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0966_verifier_start
    )
    rev0966_verifier_block = (
        verifier[rev0966_verifier_start:rev0966_verifier_end]
        if rev0966_verifier_start >= 0 and rev0966_verifier_end >= 0
        else ""
    )
    rev0967_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 967:"
    )
    rev0967_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0967_verifier_start
    )
    rev0967_verifier_block = (
        verifier[rev0967_verifier_start:rev0967_verifier_end]
        if rev0967_verifier_start >= 0 and rev0967_verifier_end >= 0
        else ""
    )
    rev0968_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 968:"
    )
    rev0968_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0968_verifier_start
    )
    rev0968_verifier_block = (
        verifier[rev0968_verifier_start:rev0968_verifier_end]
        if rev0968_verifier_start >= 0 and rev0968_verifier_end >= 0
        else ""
    )
    rev0969_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 969:"
    )
    rev0969_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0969_verifier_start
    )
    rev0969_verifier_block = (
        verifier[rev0969_verifier_start:rev0969_verifier_end]
        if rev0969_verifier_start >= 0 and rev0969_verifier_end >= 0
        else ""
    )
    rev0970_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 970:"
    )
    rev0970_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0970_verifier_start
    )
    rev0970_verifier_block = (
        verifier[rev0970_verifier_start:rev0970_verifier_end]
        if rev0970_verifier_start >= 0 and rev0970_verifier_end >= 0
        else ""
    )
    rev0971_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 971:"
    )
    rev0971_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0971_verifier_start
    )
    rev0971_verifier_block = (
        verifier[rev0971_verifier_start:rev0971_verifier_end]
        if rev0971_verifier_start >= 0 and rev0971_verifier_end >= 0
        else ""
    )
    rev0972_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 972:"
    )
    rev0972_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0972_verifier_start
    )
    rev0972_verifier_block = (
        verifier[rev0972_verifier_start:rev0972_verifier_end]
        if rev0972_verifier_start >= 0 and rev0972_verifier_end >= 0
        else ""
    )
    rev0973_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 973:"
    )
    rev0973_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0973_verifier_start
    )
    rev0973_verifier_block = (
        verifier[rev0973_verifier_start:rev0973_verifier_end]
        if rev0973_verifier_start >= 0 and rev0973_verifier_end >= 0
        else ""
    )
    rev0974_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 974:"
    )
    rev0974_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0974_verifier_start
    )
    rev0974_verifier_block = (
        verifier[rev0974_verifier_start:rev0974_verifier_end]
        if rev0974_verifier_start >= 0 and rev0974_verifier_end >= 0
        else ""
    )
    rev0975_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 975:"
    )
    rev0975_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0975_verifier_start
    )
    rev0975_verifier_block = (
        verifier[rev0975_verifier_start:rev0975_verifier_end]
        if rev0975_verifier_start >= 0 and rev0975_verifier_end >= 0
        else ""
    )
    rev0976_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 976:"
    )
    rev0976_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0976_verifier_start
    )
    rev0976_verifier_block = (
        verifier[rev0976_verifier_start:rev0976_verifier_end]
        if rev0976_verifier_start >= 0 and rev0976_verifier_end >= 0
        else ""
    )
    rev0977_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 977:"
    )
    rev0977_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0977_verifier_start
    )
    rev0977_verifier_block = (
        verifier[rev0977_verifier_start:rev0977_verifier_end]
        if rev0977_verifier_start >= 0 and rev0977_verifier_end >= 0
        else ""
    )
    rev0978_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 978:"
    )
    rev0978_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0978_verifier_start
    )
    rev0978_verifier_block = (
        verifier[rev0978_verifier_start:rev0978_verifier_end]
        if rev0978_verifier_start >= 0 and rev0978_verifier_end >= 0
        else ""
    )
    rev0979_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 979:"
    )
    rev0979_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0979_verifier_start
    )
    rev0979_verifier_block = (
        verifier[rev0979_verifier_start:rev0979_verifier_end]
        if rev0979_verifier_start >= 0 and rev0979_verifier_end >= 0
        else ""
    )
    rev0980_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 980:"
    )
    rev0980_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0980_verifier_start
    )
    rev0980_verifier_block = (
        verifier[rev0980_verifier_start:rev0980_verifier_end]
        if rev0980_verifier_start >= 0 and rev0980_verifier_end >= 0
        else ""
    )
    rev0981_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 981:"
    )
    rev0981_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0981_verifier_start
    )
    rev0981_verifier_block = (
        verifier[rev0981_verifier_start:rev0981_verifier_end]
        if rev0981_verifier_start >= 0 and rev0981_verifier_end >= 0
        else ""
    )
    rev0982_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 982:"
    )
    rev0982_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0982_verifier_start
    )
    rev0982_verifier_block = (
        verifier[rev0982_verifier_start:rev0982_verifier_end]
        if rev0982_verifier_start >= 0 and rev0982_verifier_end >= 0
        else ""
    )
    rev0983_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 983:"
    )
    rev0983_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0983_verifier_start
    )
    rev0983_verifier_block = (
        verifier[rev0983_verifier_start:rev0983_verifier_end]
        if rev0983_verifier_start >= 0 and rev0983_verifier_end >= 0
        else ""
    )
    rev0984_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 984:"
    )
    rev0984_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0984_verifier_start
    )
    rev0984_verifier_block = (
        verifier[rev0984_verifier_start:rev0984_verifier_end]
        if rev0984_verifier_start >= 0 and rev0984_verifier_end >= 0
        else ""
    )
    rev0985_verifier_start = verifier.find(
        "if revision_number is not None and revision_number >= 985:"
    )
    rev0985_verifier_end = verifier.find(
        "missing_revision_scoped =", rev0985_verifier_start
    )
    rev0985_verifier_block = (
        verifier[rev0985_verifier_start:rev0985_verifier_end]
        if rev0985_verifier_start >= 0 and rev0985_verifier_end >= 0
        else ""
    )
    self_text = text["tools/audit_sync_file_payload_store.py"]

    historical_version_inspection = last_function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::inspect_historical_versions_or_throw(",
    )
    historical_version_restore = last_function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::restore_historical_version_or_throw(",
    )
    retention_plan_owner = last_function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::plan_payload_retention_impl_or_throw(",
    )
    retention_mark_owner = last_function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::mark_payload_retention_or_throw(",
    )
    retention_plan_impl = last_function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::plan_payload_retention_impl_or_throw(",
    )
    retention_mark_publication = last_function_body(
        store,
        "SyncReplicaFilePayloadStore::publish_retention_mark_or_throw(",
    )
    historical_version_service_step = function_body(
        peer_service, "operator_historical_version_step_or_throw()"
    )
    historical_version_socket_request = function_body(
        local_status, "request_historical_version_response("
    )
    operational_database_open = function_body(
        operational_database,
        "SyncReplicaOperationalDatabase::open_or_throw(",
    )
    primary_database_open = function_body(
        folder_process,
        "open_attested_sync_replica_primary_database_with_disposition_or_throw(",
    )
    database_recovery_inspect = function_body(
        sync_cli, "int command_database_recovery_inspect("
    )
    database_recovery_advance = function_body(
        sync_cli, "int command_database_recovery_advance("
    )
    database_recovery_epoch_advance = function_body(
        sqlite_owner,
        "SyncReplicaSqliteOwner::advance_database_recovery_epoch_or_throw(",
    )
    offline_recovery_ceremony = function_body(
        sync_cli, "class OfflineReplicaDatabaseRecoveryCeremonyOwner final"
    )
    offline_recovery_advance = function_body(
        offline_recovery_ceremony, "advance_or_throw("
    )
    offline_recovery_forensic = function_body(
        offline_recovery_ceremony,
        "forensic_snapshot_or_throw(std::string_view stage)",
    )
    sync_once_command = function_body(sync_cli, "int command_once(")

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

    verification_index_link = cmake_call(
        cmake,
        "target_link_libraries(anonsync_sync_replica_file_payload_verification_index",
    )
    scrub_state_link = cmake_call(
        cmake,
        "target_link_libraries(anonsync_sync_replica_file_payload_scrub_state",
    )
    verification_index_test_link = cmake_call(
        cmake,
        "target_link_libraries(anonsync_sync_replica_file_payload_verification_index_test",
    )
    sanitizer_compile_targets = cmake_call(
        cmake, "set(ANONSYNC_SANITIZER_COMPILE_TARGETS"
    )
    sanitizer_link_targets = cmake_call(
        cmake, "foreach(tgt\n      anonsync_core"
    )
    require(
        "add_library(anonsync_sync_replica_file_payload_verification_index STATIC"
        in cmake
        and "src/sync_replica_file_payload_verification_index.cpp" in cmake
        and "anonsync_sha256_digest" in verification_index_link
        and "add_library(anonsync_sync_posix_regular_file_snapshot_codec STATIC"
        in cmake
        and "src/sync_posix_regular_file_snapshot_codec.cpp" in cmake
        and "anonsync_sync_posix_regular_file_snapshot_codec"
        in verification_index_link
        and "anonsync_sync_posix_regular_file_snapshot_codec"
        in verification_index_test_link
        and "anonsync_sync_replica_file_payload_verification_index" in store_link
        and "anonsync_sync_replica_file_payload_verification_index_test" in cmake
        and cmake.count(
            "anonsync_sync_replica_file_payload_verification_index_test"
        ) >= 5,
        "verification_checkpoint_is_a_focused_product_leaf",
        "binary restart metadata has one narrow checksum/parser target, one focused test, and shares one canonical POSIX observation codec while remaining composed into the existing payload owner",
    )
    require(
        all(
            target in sanitizer_compile_targets
            for target in (
                "anonsync_sync_replica_file_payload_verification_index",
                "anonsync_sync_replica_file_payload_verification_index_test",
                "anonsync_sync_posix_regular_file_snapshot_codec",
            )
        )
        and "anonsync_sync_replica_file_payload_verification_index_test"
        in sanitizer_link_targets,
        "verification_checkpoint_sanitizer_compile_and_link_frontiers_are_complete",
        "the new checkpoint leaf and driver are instrumented, and the executable explicitly links the sanitizer runtimes required by instrumented static dependencies",
    )
    require(
        "add_library(anonsync_resumable_sha256 STATIC" in cmake
        and "src/resumable_sha256.cpp" in cmake
        and "add_library(anonsync_sync_replica_file_payload_scrub_state STATIC"
        in cmake
        and "src/sync_replica_file_payload_scrub_state.cpp" in cmake
        and "anonsync_resumable_sha256" in store_link
        and "anonsync_sync_replica_file_payload_scrub_state" in store_link
        and "anonsync_sync_posix_regular_file_snapshot_codec"
        in scrub_state_link
        and cmake.count("anonsync_resumable_sha256_test") >= 5
        and cmake.count(
            "anonsync_sync_replica_file_payload_scrub_state_test"
        ) >= 5,
        "durable_scrub_is_two_focused_product_leaves",
        "provider-independent hash continuation and the fixed-size state grammar remain independently compiled/tested leaves; both durable metadata records consume one canonical POSIX observation codec",
    )
    require(
        all(
            target in sanitizer_compile_targets
            for target in (
                "anonsync_resumable_sha256",
                "anonsync_resumable_sha256_test",
                "anonsync_sync_replica_file_payload_scrub_state",
                "anonsync_sync_replica_file_payload_scrub_state_test",
                "anonsync_sync_posix_regular_file_snapshot_codec",
            )
        )
        and "anonsync_resumable_sha256_test" in sanitizer_link_targets
        and "anonsync_sync_replica_file_payload_scrub_state_test"
        in sanitizer_link_targets,
        "durable_scrub_sanitizer_compile_and_link_frontiers_are_complete",
        "both new leaves are instrumented and both focused drivers explicitly link the sanitizer runtimes required by their instrumented static dependencies",
    )
    require(
        "set_tests_properties(\n"
        "  anonsync_sync_replica_network_model_test\n"
        "  anonsync_sync_replica_hash_graph_projection_test\n"
        "  PROPERTIES TIMEOUT 60)" in cmake,
        "sanitizer_stress_corpora_have_qualified_timeout_frontiers",
        "the generated network model and graph oracle keep their full corpora while the ASan/UBSan frontier has a measured non-generic timeout",
    )

    digest_observation_shape = function_body(
        descriptor_snapshot_h,
        "struct SyncPosixRegularFileDigestObservation final",
    )
    digest_body = function_body(
        descriptor_snapshot,
        "hash_sync_posix_regular_file_descriptor_or_throw(",
    )
    require(
        all(
            token in descriptor_snapshot_h
            for token in (
                "struct SyncPosixRegularFileDigestObservation final",
                "SyncPosixRegularFileSnapshotMetadata metadata",
                "std::string content_sha256",
                "hash_sync_posix_regular_file_descriptor_or_throw",
            )
        )
        and "std::string bytes" not in digest_observation_shape
        and ordered(
            digest_body,
            "maximum bytes must be positive",
            "initial observation",
            "Sha256DigestBuilder digest",
            "::pread(",
            "final observation",
            "if (after != before)",
            "digest.finish_hex()",
        )
        and "anonsync_sha256_digest" in cmake_call(
            cmake,
            "target_link_libraries(anonsync_sync_bounded_regular_file",
        ),
        "descriptor_digest_streams_one_stable_file_without_freezing_bytes",
        "the shipping observer hashes by positional bounded reads, preserves the caller offset, and re-proves the same object before returning",
    )

    writer_publish = function_body(
        atomic_publication,
        "publish_posix_from_retained_directory_writer_or_throw(",
    )
    exact_descriptor_copy = function_body(
        atomic_publication, "copy_exact_regular_file_to_fd_or_throw("
    )
    require(
        "std::function" not in atomic_publication_h
        and all(
            token in atomic_publication_h
            for token in (
                "copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw",
                "copy_sync_file_atomically_replace_expected_from_borrowed_descriptor_under_directory_or_throw",
                "SyncPosixRegularFileSnapshotMetadata& expected_source",
                "std::string_view expected_source_sha256",
            )
        )
        and ordered(
            exact_descriptor_copy,
            "source preflight",
            "Sha256DigestBuilder digest",
            "::pread(",
            "write_fd_all_or_throw(",
            "source final proof",
            "digest.finish_hex()",
            "source SHA-256 changed before publication",
            "::fstat(destination_descriptor",
            "destination did not receive the exact source extent",
        )
        and ordered(
            writer_publish,
            'write_payload(temp.get(), label + " temp file")',
            "AtomicFilePublicationCutpoint::PayloadWritten",
            "fsync_fd_or_throw",
            "publish_temp_name_or_throw",
        )
        and all(
            token in atomic_runtime
            for token in (
                "descriptor source create-new publishes exact bytes",
                "descriptor source conditional replacement publishes exact bytes",
                "descriptor source publication independently verifies content identity",
                "descriptor source publication rejects a stale source observation",
            )
        ),
        "atomic_descriptor_source_preserves_identity_extent_and_cutpoint_order",
        "the public seam accepts no executable callback; a private synchronous copy re-proves source metadata, digest, and exact destination extent before payload-written authority and namespace publication",
    )

    opened_payload = function_body(
        store,
        "SyncReplicaFilePayloadStoreSnapshot::open_payload_for_operation_or_throw(",
    )
    streamed_put = function_body(
        store,
        "put_payload_from_borrowed_descriptor_or_throw(\n"
        "    int source_descriptor,",
    )
    require(
        all(
            token in store_h
            for token in (
                "class SyncReplicaFilePayloadStoreOpenedPayload final",
                "open_payload_for_operation_or_throw",
                "put_payload_from_borrowed_descriptor_or_throw",
                "const SyncPosixRegularFileSnapshotMetadata& expected_source",
                "borrowed_descriptor() const",
            )
        )
        and ordered(
            opened_payload,
            'state.root_authority.verify_or_throw(label + " root preflight")',
            "duplicate_shared_open_description_or_throw",
            "open_store_file_or_throw",
            "observe_sync_posix_regular_file_descriptor_or_throw",
            "verify_named_regular_file_or_throw",
            'state.root_authority.verify_or_throw(label + " final root proof")',
            "selected->descriptor = file.release()",
        )
        and ordered(
            streamed_put,
            'require_source_metadata("preflight")',
            "find_entry(batch.index.entries, content_sha256)",
            'require_source_identity("existing payload proof")',
            "require_new_payload_publication_capacity_or_throw",
            "descriptor payload pre-publication lease cutpoint",
            "copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw",
            "observe_exact_published_payload_without_rehash_or_throw",
            "insert_payload_index_entry_or_throw",
            "descriptor payload final lease cutpoint",
            "failed descriptor publication reconciliation",
            'require_source_identity("reconciled payload proof")',
        )
        and all(
            token in runtime
            for token in (
                "descriptor publication did not retain exact payload identity",
                "descriptor publication changed the caller file offset",
                "descriptor selection did not return the exact durable payload",
                "selected descriptor did not expose exact durable bytes",
                "descriptor publication accepted a source changed after observation",
            )
        ),
        "payload_store_streams_verified_descriptors_in_both_directions",
        "durable admission and extraction retain exact source identity, descriptor ownership, digest verification, and failure reconciliation without one payload-sized string",
    )

    stable_observation = function_body(
        folder_scan, "struct StableRegularFileObservation final"
    )
    observe_file = function_body(
        folder_scan, "observe_optional_regular_file_beneath_root_or_throw("
    )
    commit_file = function_body(
        folder_scan,
        "commit_prepared_regular_file_with_payload_batch_or_throw(",
    )
    apply_file_entry = function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::apply_visible_regular_file_or_throw(",
    )
    apply_file = function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::\n"
        "    apply_visible_regular_file_with_payload_strategy_or_throw(",
    )
    targeted_payload_open = function_body(
        store,
        "SyncReplicaFilePayloadStoreTargetedAccess::\n"
        "    open_optional_payload_for_operation_or_throw(",
    )
    require(
        "std::string bytes" not in stable_observation
        and "ScopedFd descriptor" in stable_observation
        and "hash_sync_posix_regular_file_descriptor_or_throw" in observe_file
        and "payload_batch == nullptr" in commit_file
        and "put_payload_from_borrowed_descriptor_or_throw" in commit_file
        and "observation.bytes" not in commit_file
        and "apply_visible_regular_file_with_payload_snapshot_or_throw" in apply_file_entry
        and "retained_payload_snapshot" in apply_file
        and "targeted_payload_access" in apply_file
        and "open_optional_payload_for_operation_or_throw" in apply_file
        and "open_payload_for_operation_or_throw" in apply_file
        and "copy_sync_file_atomically_replace_expected_from_borrowed_descriptor_under_directory_or_throw" in apply_file
        and "copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw" in apply_file
        and "copy_payload_for_operation_or_throw" not in apply_file
        and "std::string payload" not in apply_file
        and "stream_hash_regular_file_or_throw" not in targeted_payload_open
        and "observe_sync_posix_regular_file_descriptor_or_throw" in targeted_payload_open
        and "copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw" in apply_file
        and all(
            token in folder_scan_runtime
            for token in (
                "file above the legacy frame ceiling was not streamed into durable history",
                "large durable payload was not streamed into the destination tree",
                "repeated large streamed apply rewrote an exact destination",
            )
        ),
        "shipping_folder_scan_and_apply_do_not_hold_complete_file_bytes",
        "local publication retains a stable source descriptor and remote materialization streams the selected durable descriptor directly into the atomic temp",
    )

    cli_file_limits = function_body(replica_cli, "file_service_limits(")
    cli_effect_limits = function_body(replica_cli, "effect_owner_limits(")
    peer_file_limits = function_body(peer_server, "file_service_limits(")
    cli_reconciliation_limits = function_body(
        replica_cli, "reconciliation_protocol_limits("
    )
    peer_reconciliation_limits = function_body(
        peer_server, "reconciliation_limits("
    )
    require(
        "kSyncReplicaDeploymentManifestDefaultMaxPayloadBytes" in deployment_manifest_h
        and "kSyncReplicaDefaultMaximumPayloadExtentBytes" in deployment_manifest_h
        and "kSyncReplicaDeploymentManifestMaxPayloadBytes" in deployment_manifest_h
        and "kSyncReplicaMaximumPayloadExtentBytes" in deployment_manifest_h
        and "64ULL * 1024ULL * 1024ULL * 1024ULL" in payload_extent_h
        and "4ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL" in payload_extent_h
        and "kSyncReplicaDeploymentManifestMaxPayloadBytes" in folder_scan_h
        and "4ULL * 1024ULL * 1024ULL" in reconciliation_h
        and "64ULL * 1024ULL * 1024ULL" in reconciliation_h
        and "kSyncReplicaDefaultMaximumPayloadExtentBytes" in reconciliation_h
        and "kSyncReplicaMaximumPayloadExtentBytes" in reconciliation_h
        and "kSyncReplicaReconciliationMaximumContentDefinedChunks = 8192U" in reconciliation_h
        and "max_payload_extent_bytes" in reconciliation_h
        and "sync_replica_file_delivery_single_frame_payload_limit" in file_delivery_protocol_h
        and "kSyncReplicaFileDeliveryDefaultMaxPayloadBytes" in file_delivery_protocol_h
        and "sync_replica_file_delivery_single_frame_payload_limit" in cli_file_limits
        and "limits.max_payload_bytes = max_payload_bytes" not in cli_file_limits
        and "sync_replica_file_delivery_single_frame_payload_limit" in cli_effect_limits
        and "sync_replica_file_delivery_single_frame_payload_limit" in peer_file_limits
        and "sync_replica_reconciliation_single_payload_limit" in cli_reconciliation_limits
        and "limits.max_payload_extent_bytes = max_payload_bytes" in cli_reconciliation_limits
        and "sync_replica_reconciliation_single_payload_limit" in peer_reconciliation_limits
        and "limits.max_payload_extent_bytes = max_payload_bytes" in peer_reconciliation_limits
        and "protocol_limits_.max_payload_extent_bytes <" in reconciliation_service
        and "payload_store_.limits().max_payload_bytes" in reconciliation_service
        and "large-file configuration expanded one-frame peer memory authority" in file_delivery_runtime
        and "range-vs-durable reconciliation service" in reconciliation_runtime
        and "complete-file extent below the durable ceiling" in reconciliation_runtime
        and "file above the legacy frame ceiling" in folder_scan_runtime
        and "large durable payload was not streamed into the destination tree" in folder_scan_runtime,
        "multi_terabyte_complete_file_extent_is_separate_from_bounded_wire_ranges",
        "new deployments default to a 64 GiB complete-file ceiling, may select up to the exact 4 TiB content-defined-manifest frontier, and still use repeated bounded ranges and 64 MiB pages while legacy one-frame delivery/effect paths remain capped",
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
                "kSyncReplicaFilePayloadStoreProductionMaxEntries = 100000U",
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
        and store.count("duplicate_shared_open_description_or_throw(") == 20
        and all(
            "duplicate_shared_open_description_or_throw" in function_body(
                store, signature
            )
            for signature in (
                "remove_scanned_publication_residues_or_throw(",
                "acquire_store_lease_or_throw(",
                "scan_store_namespace_or_throw(",
                "observe_staged_prefix_namespace_under_lease_or_throw(",
                "observe_staged_prefix_terminal_target_under_lease_or_throw(",
                "observe_exact_published_payload_without_rehash_or_throw(",
                "observe_quarantine_namespace_under_lease_or_throw(",
                "SyncReplicaFilePayloadStore::begin_targeted_access_or_throw(",
                "load_source_manifest_checkpoint_or_none_or_throw(",
                "SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw(",
                "SyncReplicaFilePayloadStore::quarantine_corrupt_payload_or_throw(",
                "SyncReplicaFilePayloadStore::release_quarantined_payload_or_throw(",
                "writer_fenced_payload_use_exclusive_available_or_throw(",
                "SyncReplicaFilePayloadStoreSnapshot::open_payload_for_operation_or_throw(",
                "SyncReplicaFilePayloadStoreSnapshot::copy_payload_range_for_operation_or_throw(",
                "SyncReplicaFilePayloadStore::stage_payload_range_or_throw(",
                "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw(",
                "advance_payload_scrub_from_snapshot_or_throw(",
                "SyncReplicaFilePayloadStore::publish_retention_mark_or_throw(",
            )
        )
        and "duplicate_shared_open_description_or_throw(" in store[
            store.rfind(
                "publish_rebound_scrub_state_after_identity_rename_or_throw("
            ) :
        ]
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
    production_limits = function_body(
        store,
        "sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(",
    )
    require(
        all(
            token in limits
            for token in (
                "limits.max_entries == 0U",
                "kSyncReplicaFilePayloadStoreMaxEntries",
                "limits.max_payload_bytes == 0U",
                "limits.max_payload_bytes > limits.max_indexed_bytes",
                "limits.max_indexed_bytes > kMaximumPersistentInteger",
                "kSyncReplicaFilePayloadStoreMaxTransientEntries",
                "limits.max_transient_bytes == 0U",
                "limits.max_transient_bytes > kMaximumPersistentInteger",
            )
        )
        and "std::numeric_limits<std::size_t>::max()" not in limits
        and ordered(
            production_limits,
            "max_payload_bytes == 0U",
            "kMaximumPersistentInteger / 2U",
            "limits.max_entries =",
            "kSyncReplicaFilePayloadStoreProductionMaxEntries",
            "limits.max_payload_bytes = max_payload_bytes",
            "max_transient_bytes = std::max<std::uint64_t>",
            "validate_sync_replica_file_payload_store_limits_or_throw(limits)",
        ),
        "all_store_limits_are_validated_before_authority",
        "zero, inverted, persistent-integer, transient, and exact two-payload recovery budgets fail before root authority; production explicitly composes the 100,000-entry folder capacity rather than inheriting the 4,096-entry generic test default",
    )

    regular_open = function_body(
        resolver, "open_regular_file_component_with_missing_policy_or_throw("
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
        )
        and "MissingRegularFileComponentPolicy::ReturnAbsent" in resolver
        and "sync_posix_open_optional_regular_file_component_or_throw" in resolver,
        "regular_components_are_nonblocking_identity_and_mount_reproved",
        "required and optional exact-name opens share one no-follow identity/mount proof; only ENOENT may become an ordinary absence",
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

    metadata_codec_append = function_body(
        metadata_codec,
        "append_sync_posix_regular_file_snapshot_metadata_binary(",
    )
    metadata_codec_parse = function_body(
        metadata_codec,
        "parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(",
    )
    metadata_codec_validate = function_body(
        metadata_codec,
        "validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(",
    )
    index_validate = function_body(
        verification_index, "validate_index("
    )
    index_serialize = function_body(
        verification_index,
        "serialize_sync_replica_file_payload_verification_index_or_throw(",
    )
    index_parse = function_body(
        verification_index,
        "parse_sync_replica_file_payload_verification_index_or_throw(",
    )
    require(
        all(
            token in verification_index_h
            for token in (
                ".anonsync-payload-verification-index-v1",
                "SyncReplicaFilePayloadVerificationIndexEntry",
                "SyncReplicaFilePayloadVerificationIndex",
                "store_identity_sha256",
                "store_identity_metadata",
                "indexed_bytes",
            )
        )
        and all(
            token in verification_index
            for token in (
                "anonsync:sync-replica-file-payload-verification-index:v1",
                "append_u64(",
                "take_u64",
                "kDigestTextBytes = 64U",
                "encoded.append(sha256_hex(encoded))",
                "checksum does not match",
            )
        )
        and ordered(
            index_serialize,
            "validate_index(",
            "append_sync_posix_regular_file_snapshot_metadata_binary",
            "append_u64(encoded, static_cast<std::uint64_t>(index.entries.size())",
            "for (const auto& entry : index.entries)",
            "encoded.append(sha256_hex(encoded))",
        )
        and ordered(
            index_parse,
            "encoded-size ceiling",
            "checksum does not match",
            "incompatible format generation",
            "cursor.take_metadata()",
            "entry_count",
            "length does not match",
            "validate_index(",
        )
        and all(
            token in index_validate
            for token in (
                "strictly sorted",
                "aggregate bytes",
                "aggregate byte total",
            )
        )
        and "validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw"
        in index_validate,
        "verification_checkpoint_format_is_canonical_bounded_and_checksum_sealed",
        "the non-authoritative record has one fixed v1 basename, fixed-width big-endian fields, exact length, sorted unique digests, metadata invariants, and a trailing checksum",
    )
    require(
        "kSyncPosixRegularFileSnapshotMetadataEncodedBytes = 11U * 8U"
        in metadata_codec_h
        and all(
            field in metadata_codec_append
            for field in (
                "metadata.device",
                "metadata.inode",
                "metadata.size_bytes",
                "metadata.link_count",
                "metadata.owner_user_id",
                "metadata.owner_group_id",
                "metadata.mode",
                "metadata.modification_seconds",
                "metadata.modification_nanoseconds",
                "metadata.status_change_seconds",
                "metadata.status_change_nanoseconds",
            )
        )
        and all(
            token in metadata_codec_parse
            for token in (
                "canonical eleven-field width",
                "out-of-range mode",
                "out-of-range modification fraction",
                "out-of-range status-change fraction",
            )
        )
        and all(
            token in metadata_codec_validate
            for token in (
                "non-regular metadata",
                "exact mode 0600",
                "exact single link",
                "configured byte ceiling",
                "invalid timestamp fraction",
            )
        )
        and "sync_posix_regular_file_snapshot_codec.hpp"
        in verification_index
        and "sync_posix_regular_file_snapshot_codec.hpp" in scrub_state
        and verification_index.count(
            "append_sync_posix_regular_file_snapshot_metadata_binary("
        ) >= 2
        and scrub_state.count(
            "append_sync_posix_regular_file_snapshot_metadata_binary("
        ) >= 2
        and "parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw("
        in verification_index
        and "parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw("
        in scrub_state
        and "shared POSIX metadata codec width drifted from eleven fields"
        in verification_index_runtime,
        "durable_payload_records_share_one_canonical_posix_metadata_codec",
        "restart verification and rotating scrub retain their fixed record widths while one compiled leaf owns the eleven-field big-endian projection and private single-link regular-file invariants",
    )
    require(
        all(
            token in verification_index_runtime
            for token in (
                "round trip changed exact fields",
                "checksum-valid incompatible verification-index generation was accepted",
                "checksum-valid false verification-index entry count was accepted",
                "checksum-valid invalid payload digest was accepted",
                "checksum-valid nonprivate payload metadata was accepted",
                "serializer admitted a duplicate payload digest",
                "parser ignored the encoded entry ceiling",
                "maximum-size arithmetic did not reject overflow",
            )
        ),
        "compiled_verification_index_matrix_covers_format_and_ceiling_edges",
        "runtime tests reseal semantically hostile records so checksum validation cannot mask parser-generation, length, digest, mode, or arithmetic defects",
    )

    scan = function_body(store, "scan_store_namespace_or_throw(")
    require(
        "kInitialPayloadIndexReserveEntries = 4096U" in scan
        and "std::min(limits.max_entries, kInitialPayloadIndexReserveEntries)"
        in scan,
        "production_entry_ceiling_does_not_force_eager_capacity_allocation",
        "raising the durable production ceiling to 100,000 entries preserves bounded lazy vector growth for ordinary small stores",
    )
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
    observer_root_open = function_body(
        folder_observer, "open_independent_root_or_throw("
    )
    observer_stream = function_body(
        folder_observer, "explicit ScopedDirectoryStream("
    )
    observer_entry = function_body(
        folder_observer, "observe_sync_replica_folder_or_throw("
    )
    require(
        production_fdopendir_paths
        == [
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_folder_observer.cpp",
        ]
        and "duplicate_shared_open_description_or_throw" in observer_root_open
        and '::openat(shared.descriptor(), ".", flags)' in observer_root_open
        and "::fdopendir(owned_descriptor)" in observer_stream
        and ordered(
            observer_entry,
            "open_independent_root_or_throw",
            "walk_directory_or_throw(context, root.release()",
        ),
        "production_directory_stream_inventory_is_review_complete",
        "every production fdopendir owner is inventoried and opens an independent cursor before traversal; "
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
                "stream_hash_regular_file_or_throw",
                "streamed.sha256 != basename",
                "PayloadIndexEntry{",
                "opened.status",
                "verify_named_regular_file_or_throw",
                "std::sort",
                "std::adjacent_find",
            )
        ),
        "digest_named_payloads_are_hash_verified_and_canonicalized",
        "type, owner, mode, link count, device, cold-or-changed bytes, basename, and stable namespace identity are all represented",
    )
    verification_generation = function_body(
        store, "struct PayloadVerificationGeneration final"
    )
    verification_cache = function_body(
        store, "struct PayloadVerificationCache final"
    )
    verification_cache_lookup = function_body(
        store, "matching_verification_generation_or_none("
    )
    verification_cache_publish = function_body(
        store, "publish_verification_generation("
    )
    require(
        all(
            token in verification_generation
            for token in (
                "std::optional<struct stat> identity_status",
                "std::vector<PayloadIndexEntry> entries",
            )
        )
        and "std::shared_ptr<const PayloadVerificationGeneration> generation"
        in verification_cache
        and "std::mutex" not in verification_cache
        and "std::shared_ptr<PayloadVerificationCache> verification_cache" in store
        and "std::make_shared<PayloadVerificationCache>()" in store
        and "verification_cache" not in function_body(store, "snapshot_digest_or_throw("),
        "verification_cache_is_process_local_acceleration_only",
        "the warm index is an immutable process-owner generation shared only across one store/batch lifetime and never enters durable namespace or canonical snapshot identity",
    )
    require(
        ordered(
            scan,
            "verified_payloads == nullptr",
            "find_entry(*verified_payloads, basename)",
            "find_verification_index_entry",
            "same_regular_file_observation",
            "sync_posix_regular_file_snapshot_metadata_matches_status",
            "if (exact_process_observation)",
            "scan_process_reused_entry_count",
            "else if (exact_durable_observation)",
            "scan_durable_reused_entry_count",
            "} else {",
            "stream_hash_regular_file_or_throw",
            "streamed.sha256 != basename",
            "scan_hashed_entry_count",
            "verify_named_regular_file_or_throw",
        ),
        "warm_reuse_requires_exact_metadata_and_retains_hash_fallback",
        "only an unchanged exact process or durable inode observation skips bytes; every cold, new, or replaced payload still receives complete SHA-256 verification",
    )
    verification_file_observer = function_body(
        store, "observe_verification_index_file_or_throw("
    )
    verification_match = function_body(
        store, "verification_index_matches_scan("
    )
    verification_publish = function_body(
        store, "publish_verification_index_or_throw("
    )
    verification_publication_definition = store.find(
        "enum class VerificationIndexPublicationDisposition"
    )
    verification_capacity = function_body(
        store[verification_publication_definition:],
        "VerificationIndexPublicationCapacity\n"
        "verification_index_publication_capacity_or_throw(",
    )
    verification_due = function_body(
        store, "verification_checkpoint_due("
    )
    snapshot_body = function_body(
        store, "SyncReplicaFilePayloadStore::snapshot_with_reuse_policy_or_throw("
    )
    snapshot_state_gate = function_body(
        store,
        "SyncReplicaFilePayloadStoreSnapshot::require_state_or_throw(",
    )
    targeted_state_gate = function_body(
        store,
        "SyncReplicaFilePayloadStoreTargetedAccess::require_state_or_throw(",
    )
    require(
        ordered(
            scan,
            "read_verification_index =",
            "verified_payloads == nullptr",
            "locked_identity_status != nullptr",
            "synchronizes_store_observation(durability)",
            "observe_verification_index_file_or_throw",
            "find_verification_index_entry",
            "sync_posix_regular_file_snapshot_metadata_matches_status",
            "exact_process_observation",
            "exact_durable_observation",
            "stream_hash_regular_file_or_throw",
            "verification_index_matches_scan",
        )
        and ordered(
            verification_file_observer,
            "AT_SYMLINK_NOFOLLOW",
            "require_private_regular_file_or_throw",
            "encoded-size ceiling",
            "encoded_size_admissible",
            "open_store_file_or_throw",
            "read_contents && encoded_size_admissible",
            "FrozenSyncPosixRegularFileSnapshot",
            "parse_sync_replica_file_payload_verification_index_or_throw",
            "catch (const std::invalid_argument&)",
            "store_identity_sha256",
            "store_identity_metadata",
            "verify_named_regular_file_or_throw",
        )
        and "index.indexed_bytes != scanned.indexed_bytes" in verification_match
        and "sync_posix_regular_file_snapshot_metadata_matches_status" in verification_match,
        "durable_reuse_is_identity_metadata_and_full_scan_bound",
        "a checksum-valid record grants per-payload reuse only under the exact locked marker and exact reopened payload metadata; malformed, stale, absent, or changed observations fall back to complete hashing",
    )
    require(
        all(
            token in verification_due
            for token in (
                "kVerificationCheckpointMinimumAddedEntries",
                "kVerificationCheckpointMaximumAddedEntries",
                "kVerificationCheckpointMinimumAddedBytes",
                "kVerificationCheckpointMaximumAddedBytes",
                "graceful_final_checkpoint",
            )
        )
        and ordered(
            verification_capacity,
            "sync_replica_file_payload_verification_index_maximum_bytes_or_throw",
            "transient_entry_count < limits.max_transient_entries",
            "transient_reserved_bytes <= limits.max_transient_bytes",
            "encoded_bytes <=",
        )
        and ordered(
            verification_publish,
            "verification_index_publication_capacity_or_throw",
            "if (!capacity.available)",
            "SkippedTransientCapacity",
            "make_verification_index_or_throw",
            "serialize_sync_replica_file_payload_verification_index_or_throw",
            "exact-size preflight drifted",
            "write_sync_file_atomically_replace_expected_under_directory_or_throw",
            "write_sync_file_atomically_create_new_under_directory_or_throw",
        )
        and ordered(
            snapshot_body,
            "SharedObservation",
            "scan_store_under_lease_or_throw",
            "observation_lease.verify_or_throw",
            "advance_payload_scrub_from_snapshot_or_throw",
            "refresh_verification_index_best_effort",
            "return SyncReplicaFilePayloadStoreSnapshot",
        )
        and "ExclusiveMutation" in function_body(
            store, "refresh_verification_index_best_effort("
        )
        and all(
            token in runtime
            for token in (
                "oversized durable verification metadata blocked or granted payload reuse",
                "non-authoritative checkpoint consumed unavailable transient capacity",
                "checkpoint omission changed payload truth or claimed warm restart reuse",
                "tight-capacity scan did not retain its exact checkpoint deferral",
                "known-impossible checkpoint publication did not remain deferred on the warm snapshot",
            )
        ),
        "checkpoint_publication_is_geometric_capacity_bounded_and_exclusive",
        "complete scans remain shared and authoritative; only after releasing them may a fail-fast exclusive lease atomically create or expected-replace bounded restart metadata, with oversize fallback and capacity rejection proved at runtime",
    )
    checkpoint_state = function_body(
        store, "struct PayloadVerificationCheckpointState final"
    )
    checkpoint_observation = function_body(
        store, "note_verification_checkpoint_observation("
    )
    checkpoint_addition = function_body(
        store, "note_verification_checkpoint_payload_addition("
    )
    checkpoint_attempt_gate = function_body(
        store, "verification_checkpoint_publication_worth_attempting("
    )
    refresh_body = function_body(
        store, "refresh_verification_index_best_effort("
    )
    require(
        all(
            token in checkpoint_state
            for token in (
                "publication_capacity_observation_known",
                "publication_capacity_available",
            )
        )
        and "publication_capacity_available.has_value()" in checkpoint_observation
        and ordered(
            checkpoint_addition,
            "publication_capacity_observation_known = false",
            "publication_capacity_available = false",
        )
        and "verification_checkpoint_deferred_by_known_capacity" in checkpoint_attempt_gate
        and ordered(
            refresh_body,
            "verification_checkpoint_publication_worth_attempting",
            "scan_store_under_lease_or_throw",
            "verification_checkpoint_publication_worth_attempting",
            "publish_verification_index_or_throw",
        )
        and "verification_checkpoint_deferred_by_transient_capacity" in store_h
        and "verification_checkpoint_deferred_by_transient_capacity" in runtime,
        "known_checkpoint_capacity_deferral_suppresses_duplicate_full_refresh",
        "one complete scan retains exact negative checkpoint-capacity scheduling evidence, ordinary snapshot and graceful teardown skip the known-doomed second scan, and any payload addition invalidates the observation",
    )
    require(
        all(
            token in checkpoint_observation
            for token in (
                "scanned.scan_hashed_entry_count != 0U",
                "state.durable_entry_count !=",
                "state.durable_indexed_bytes != scanned.indexed_bytes",
                "state.force_checkpoint = true",
            )
        )
        and "same-process exact repair was not checkpointed for the next owner"
        in runtime,
        "process_cache_reverification_refreshes_restart_checkpoint",
        "a process-cache miss or exact namespace count/byte drift immediately dirties durable restart evidence, so a successful same-process byte proof is checkpointed instead of being repeated by the next owner",
    )

    batch_state = function_body(
        store, "struct SyncReplicaFilePayloadStoreMutationBatch::State final"
    )
    directory_owner_access = function_body(
        directory_authority_internal,
        "class SyncDirectoryAuthorityAccess final",
    )
    directory_owner_gate = function_body(
        directory_authority,
        "void SyncDirectoryAuthorityAccess::require_current_owner_or_throw(",
    )
    checkpoint_refresh = function_body(
        store, "void refresh_verification_index_best_effort("
    )
    store_teardown = function_body(
        store, "SyncReplicaFilePayloadStore::State::~State() noexcept"
    )
    require(
        "static void require_current_owner_or_throw" in directory_owner_access
        and "authority.require_current_owner_or_throw(label)"
        in directory_owner_gate
        and ordered(
            checkpoint_refresh,
            "require_current_owner_or_throw",
            "verification_checkpoint_publication_worth_attempting",
            "root_authority.verify_or_throw",
        )
        and ordered(
            store_teardown,
            "!verification_cache",
            "refresh_verification_index_best_effort",
        )
        and "verification_checkpoint_publication_worth_attempting"
        not in store_teardown
        and ordered(
            batch_state,
            "if (poisoned || !verification_cache) return",
            "require_current_owner_or_throw",
            "verification_cache.use_count()",
            "verification_checkpoint_publication_worth_attempting",
        ),
        "owner_local_cache_scheduler_never_precedes_thread_proof",
        "the cheap internal process/thread gate precedes every best-effort teardown or refresh scheduler read; clean no-op close avoids a filesystem reproof while foreign-thread misuse cannot race the deliberately unsynchronized cache",
    )
    require(
        "std::shared_ptr<PayloadVerificationCache> verification_cache" in batch_state
        and "store.verification_cache, store.live_capability_registry," in store
        and "std::move(index), full_scan_count" in store
        and all(
            token in batch_state
            for token in (
                "std::shared_ptr<PayloadVerificationCache> verification_cache",
                "ScannedPayloadIndex index",
                "pending_cache_generation",
                "retired_cache_generation",
                "StoreLease mutation_lease",
            )
        )
        and batch_state.rfind("StoreLease mutation_lease") >
            batch_state.rfind("retired_cache_generation")
        and ordered(
            batch_state,
            "~State() noexcept",
            "if (poisoned || !verification_cache) return",
            "publish_verification_index_or_throw(",
            "std::make_shared<PayloadVerificationGeneration>()",
            "mutable_generation->entries.swap(index.entries)",
            "pending_cache_generation = std::move(mutable_generation)",
            "verification-cache publication lease cutpoint",
            "publish_verification_generation(",
            "catch (...) {",
        )
        and ordered(
            verification_cache_publish,
            "std::move(cache.generation)",
            "cache.generation = std::move(generation)",
            "return retired",
        )
        and "std::mutex" not in verification_cache_publish
        and "released payload mutation batch did not publish its exact verified index for immediate warm reuse"
        in runtime
        and "payload mutation batch lost safe ownership after creator destruction"
        in runtime
        and "detached payload mutation batch did not checkpoint exact restart acceleration"
        in runtime,
        "released_batch_promotes_complete_verified_index_without_raw_store_pointer",
        "batch teardown moves its complete exact index into an immutable generation only after a final live lease proof; declaration order releases the flock before old-generation reclamation, and runtime coverage destroys the creator store first to prove safe shared ownership without cache authority over cold restart",
    )
    begin_batch = function_body(
        store, "SyncReplicaFilePayloadStore::begin_mutation_batch_or_throw()"
    )
    require(
        all(
            token in batch_state
            for token in (
                "scan_process_reused_entry_count_value",
                "scan_process_reused_bytes_value",
                "scan_durable_reused_entry_count_value",
                "scan_durable_reused_bytes_value",
            )
        )
        and ordered(
            begin_batch,
            "scan_process_reused_entry_count =",
            "scan_process_reused_bytes =",
            "scan_durable_reused_entry_count =",
            "scan_durable_reused_bytes =",
            "rescanned.scan_process_reused_entry_count",
            "rescanned.scan_process_reused_bytes",
            "rescanned.scan_durable_reused_entry_count",
            "rescanned.scan_durable_reused_bytes",
            "scan_process_reused_entry_count, scan_process_reused_bytes",
            "scan_durable_reused_entry_count, scan_durable_reused_bytes",
        )
        and "restarted payload mutation batch did not attribute reuse to the durable checkpoint" in runtime
        and "post-batch warm snapshot did not attribute reuse to process-local state" in runtime,
        "mutation_batch_reuse_origin_counters_are_source_freshly_composed",
        "the production constructor, cleanup rescan aggregation, and focused runtime partition all retain process-versus-durable reuse provenance; a clean compile is required to prevent stale objects from masking signature drift",
    )
    identity = function_body(store, "ensure_store_identity_or_throw(")
    migration = function_body(
        store, "void migrate_minimum_reader_identity_or_throw("
    )
    identity_rebind = function_body(
        store,
        "void StoreLease::rebind_identity_basename_after_atomic_rename_or_throw(",
    )
    identity_upgrade_pair = function_body(
        store,
        "payload_store_identity_basenames_are_supported_upgrade_pair(",
    )
    staged_prefix_observation = function_body(
        store, "observe_staged_prefix_namespace_under_lease_or_throw("
    )
    require(
        all(
            token in store
            for token in (
                "kStandaloneStoreIdentityBasenameV2ReaderFenceV1",
                "kProductStoreIdentityBasenameV3ReaderFenceV1",
                "kStandaloneStoreIdentityBasenameV2LegacyReader",
                "kProductStoreIdentityBasenameV3LegacyReader",
                "kLegacyStoreIdentityBasenameV1",
                "kStandaloneStoreIdentityDomainV2",
                "kProductStoreIdentityDomainV3",
                "standalone_store_identity_payload",
                "product_store_identity_payload_or_throw",
                "payload_store_identity_basename_is_known",
            )
        )
        and "payload.append(kStoreLeaseProtocol)" in function_body(
            store, "standalone_store_identity_payload("
        )
        and "append_framed_marker_field" in function_body(
            store, "product_store_identity_payload_or_throw("
        )
        and all(
            token in store[
                store.find("kLeaseCapableStoreIdentityBasenames") :
                store.find("kKnownStoreIdentityBasenames")
            ]
            for token in (
                "kStandaloneStoreIdentityBasenameV2ReaderFenceV1",
                "kProductStoreIdentityBasenameV3ReaderFenceV1",
                "kStandaloneStoreIdentityBasenameV2LegacyReader",
                "kProductStoreIdentityBasenameV3LegacyReader",
            )
        )
        and all(
            token in store[
                store.find("kKnownStoreIdentityBasenames") :
                store.find("kStandaloneStoreIdentityDomainV2")
            ]
            for token in (
                "kStandaloneStoreIdentityBasenameV2ReaderFenceV1",
                "kProductStoreIdentityBasenameV3ReaderFenceV1",
                "kStandaloneStoreIdentityBasenameV2LegacyReader",
                "kProductStoreIdentityBasenameV3LegacyReader",
                "kLegacyStoreIdentityBasenameV1",
            )
        )
        and "kLeaseCapableStoreIdentityBasenames" in function_body(
            store, "payload_store_identity_basename_is_lease_capable("
        )
        and "kKnownStoreIdentityBasenames" in function_body(
            store, "payload_store_identity_basename_is_known("
        ),
        "identity_payload_and_minimum_reader_generation_are_separate",
        "v2/v3 identity bytes remain the folder/deployment binding while one centralized basename set raises the minimum cooperative reader generation",
    )
    competing_identity_probe = function_body(
        store, "require_no_competing_store_identity_names_or_throw("
    )
    identity_open_reproof = function_body(
        store, "void verify_open_store_identity_or_throw("
    )
    require(
        all(
            token in competing_identity_probe
            for token in (
                "payload_store_identity_basename_is_lease_capable",
                "kKnownStoreIdentityBasenames",
                "AT_SYMLINK_NOFOLLOW",
                "refuses coexisting incompatible payload-store identity ",
                '"marker: "',
            )
        )
        and "require_no_competing_store_identity_names_or_throw"
        in identity_open_reproof
        and "require_no_competing_store_identity_names_or_throw"
        in identity_rebind
        and "coexisting lock-anchor generations admitted split authority"
        in runtime
        and "cross-family lock anchors admitted split authority before scanning"
        in runtime
        and "targeted remote payload access ignored a legacy v1 lock authority"
        in folder_scan_runtime,
        "every_identity_reproof_rejects_competing_fixed_generation_names",
        "complete and targeted lanes accept only one of four lease-capable v2/v3 anchors and probe all five known names, including unsupported v1, whenever the selected inode is opened or rebound",
    )
    require(
        "test_targeted_remote_payload_rejects_legacy_v1_split_identity"
        in folder_scan_runtime
        and "remote_payload_snapshot_observation_count" not in function_body(
            folder_scan_runtime,
            "void test_targeted_remote_payload_rejects_legacy_v1_split_identity()",
        )
        and "coexisting incompatible payload-store identity marker: "
        in function_body(
            folder_scan_runtime,
            "void test_targeted_remote_payload_rejects_legacy_v1_split_identity()",
        )
        and ".anonsync-payload-store-identity-v1"
        in function_body(
            folder_scan_runtime,
            "void test_targeted_remote_payload_rejects_legacy_v1_split_identity()",
        ),
        "targeted_exact_name_lane_rejects_unsupported_v1_lock_authority",
        "the remote-only exact-digest lane rejects a coexisting v1 lock basename before publishing bytes or catalog state without depending on a complete payload snapshot",
    )
    require(
        "offline migration is required before lease-protected use" in scan
        and "payload_store_identity_basename_is_known" in scan
        and "basename != identity_basename" in scan
        and "payload_store_identity_basename_is_known"
        in staged_prefix_observation
        and "basename != identity_basename" in staged_prefix_observation
        and "incompatible payload-store identity generation" in scan
        and "incompatible payload-store identity generation"
        in staged_prefix_observation,
        "complete_and_lightweight_traversals_share_identity_generation_rejection",
        "both private-root enumerators recognize every supported v2/v3 anchor and reject unsupported v1 or any other known generation beside the exact selected lock anchor",
    )
    require(
        all(
            token in identity_upgrade_pair
            for token in (
                "kStandaloneStoreIdentityBasenameV2LegacyReader",
                "kStandaloneStoreIdentityBasenameV2ReaderFenceV1",
                "kProductStoreIdentityBasenameV3LegacyReader",
                "kProductStoreIdentityBasenameV3ReaderFenceV1",
            )
        )
        and "payload_store_identity_basenames_are_supported_upgrade_pair"
        in identity
        and "payload_store_identity_basenames_are_supported_upgrade_pair"
        in migration
        and "payload_store_identity_basenames_are_supported_upgrade_pair"
        in identity_rebind
        and "payload_store_identity_basename_is_lease_capable"
        not in migration.split("StoreLease migration_lease", 1)[0]
        and "payload_store_identity_basename_is_lease_capable"
        not in identity.split("const std::string expected", 1)[0],
        "identity_migration_accepts_only_two_directed_same_family_pairs",
        "standalone legacy can upgrade only to standalone reader-fenced and product legacy only to product reader-fenced; generic recognized-name distinctness cannot authorize a cross-family inode rename",
    )

    require(
        all(
            token in identity
            for token in (
                "minimum-reader identity reconciliation",
                "legacy-reader identity absence reconciliation",
                "refuses coexisting current and legacy-reader",
                "legacy-reader identity reconciliation",
                "migrate_minimum_reader_identity_or_throw",
                "migrated minimum-reader identity reconciliation",
                "migrated legacy-reader identity absence reconciliation",
                "identity bootstrap preflight",
                "write_sync_file_atomically_create_new_under_directory_or_throw",
                "identity publication did not become durable and exact",
            )
        )
        and ordered(
            identity,
            "minimum-reader identity reconciliation",
            "legacy-reader identity absence reconciliation",
            "legacy-reader identity reconciliation",
            "migrate_minimum_reader_identity_or_throw",
            "identity bootstrap preflight",
            "write_sync_file_atomically_create_new_under_directory_or_throw",
        )
        and "reconcile_sync_immutable_file_create_new_under_directory_or_throw"
        in identity,
        "identity_ensure_is_one_fail_closed_current_legacy_state_machine",
        "exact current proceeds, exact legacy migrates, coexistence/conflict fails, ExistingOnly cannot bootstrap, and CreateIfMissing publishes only the current reader generation after a clean complete preflight",
    )
    require(
        all(
            token in migration
            for token in (
                "ExclusiveMutation",
                "PayloadVerificationReusePolicy::RequireCurrentBytes",
                "minimum-reader migration cold namespace proof",
                "rebind_identity_basename_after_atomic_rename_or_throw",
                "publish_verification_generation",
                "force_checkpoint = true",
                "minimum-reader migration final proof",
            )
        )
        and ordered(
            migration,
            "acquire_store_lease_or_throw",
            "ExclusiveMutation",
            "scan_store_under_lease_or_throw",
            "PayloadVerificationReusePolicy::RequireCurrentBytes",
            "rebind_identity_basename_after_atomic_rename_or_throw",
            "publish_verification_generation",
            "force_checkpoint = true",
            "minimum-reader migration final proof",
        )
        and "verified_payloads = &deliberately_empty_verified_payloads"
        in function_body(store, "scan_store_under_lease_or_throw("),
        "legacy_reader_migration_is_exclusive_and_current_byte_cold_before_rename",
        "no current marker appears until an exclusive legacy-inode lease has completed a full namespace scan with process and durable byte acceleration mechanically disabled",
    )
    require(
        all(
            token in migration
            for token in (
                "rebound_scrub_state",
                "rebound_active_current_bytes_verified",
                "SyncReplicaFilePayloadScrubStateDisposition::Prepared",
                "ResumableSha256{}.checkpoint()",
                "minimum-reader migrated scrub payload metadata",
                "publish_rebound_scrub_state_after_identity_rename_or_throw",
                "minimum-reader migrated scrub identity metadata",
                "note_process_scrub_state_observation",
            )
        )
        and ordered(
            migration,
            "PayloadVerificationReusePolicy::RequireCurrentBytes",
            "rebound_scrub_state = *cold.scrub_state",
            "SyncReplicaFilePayloadScrubStateDisposition::Prepared",
            "ResumableSha256{}.checkpoint()",
            "rebind_identity_basename_after_atomic_rename_or_throw",
            "minimum-reader migrated scrub identity metadata",
            "publish_rebound_scrub_state_after_identity_rename_or_throw",
            "note_process_scrub_state_observation",
            "force_checkpoint = true",
        )
        and store.count(
            "publish_rebound_scrub_state_after_identity_rename_or_throw"
        ) >= 3,
        "migration_rebinds_write_ahead_state_without_reusing_partial_hashes",
        "before rename the migration allocates a rebound scrub record; after the exact inode transition it binds that record to current identity and payload metadata, resets any partial hash to Prepared, durably republishes it, and carries only the cold scan's complete-byte witness",
    )
    require(
        all(
            token in identity_rebind
            for token in (
                "ExclusiveMutation",
                "synchronizes_store_observation(durability_)",
                "pre-rename lease proof",
                "rename_noreplace_at_or_throw",
                "same_regular_file_rename_transition",
                "renamed identity bytes",
                "fsync_or_throw",
                "identity migration directory",
                "legacy identity name survived",
                "migrated identity pathname",
                "identity_status_ = renamed_status",
                "identity_basename_ = std::move(new_identity_basename)",
                "rebound lease proof",
            )
        )
        and ordered(
            identity_rebind,
            "pre-rename lease proof",
            "rename_noreplace_at_or_throw",
            "::fstat(identity_descriptor_",
            "same_regular_file_rename_transition",
            "renamed identity bytes",
            "fsync_or_throw",
            "identity migration directory",
            "legacy identity name survived",
            "migrated identity pathname",
            "identity_status_ = renamed_status",
            "identity_basename_ = std::move(new_identity_basename)",
            "rebound lease proof",
        ),
        "identity_rename_preserves_locked_inode_and_rebinds_only_after_durable_path_proofs",
        "RENAME_NOREPLACE moves the exact flock inode, permits only a rename ctime transition, synchronizes file and directory, proves old absence/new identity, and only then changes the lease basename",
    )
    require(
        "legacy_identity_basename" in function_body(
            store, "struct SyncReplicaFilePayloadStore::State final"
        )
        and store.count("store.legacy_identity_basename") >= 5
        and all(
            token in store
            for token in (
                "kStandaloneStoreIdentityBasenameV2ReaderFenceV1",
                "kStandaloneStoreIdentityBasenameV2LegacyReader",
                "kProductStoreIdentityBasenameV3ReaderFenceV1",
                "kProductStoreIdentityBasenameV3LegacyReader",
            )
        )
        and "if (synchronizes_store_observation(durability))"
        in function_body(
            store,
            "SyncReplicaFilePayloadStore::begin_targeted_access_or_throw(",
        )
        and "ReadOnlyInspect" in function_body(
            store,
            "SyncReplicaFilePayloadStore::begin_targeted_access_or_throw(",
        ),
        "writable_product_entry_points_carry_both_generations_while_readonly_omits_migration",
        "the retained store state supplies current and legacy names to every ensure lane, while observation-only access bypasses ensure and cannot rename operator evidence",
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

    snapshot = function_body(
        store, "SyncReplicaFilePayloadStore::snapshot_with_reuse_policy_or_throw("
    )
    require(
        ordered(
            snapshot,
            "snapshot source preflight",
            "ensure_store_identity_or_throw",
            "store.expected_identity",
            "observation_mode",
            "reopen_matching_root_authority_or_throw",
            "acquire_store_lease_or_throw",
            "scan_store_under_lease_or_throw",
            "SyncReplicaFileContentInventory",
            "snapshot_digest_or_throw",
            'snapshot_label + " final lease cutpoint"',
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
        "SyncReplicaFilePayloadStoreSnapshot::copy_payload_range_for_operation_or_throw(",
    )
    range_copy = function_body(store, "copy_hash_regular_file_range_into_or_throw(")
    require(
        ordered(
            lookup,
            "require_state_or_throw",
            "operation.kind != SyncReplicaValueKind::File",
            "find_entry",
            "root_authority.verify_or_throw",
            "duplicate_shared_open_description_or_throw",
            "open_store_file_or_throw",
            "require_private_regular_file_or_throw",
            "if (same_regular_file_observation(indexed->status, opened.status))",
            "copy_hash_regular_file_range_or_throw",
            "} else {",
            "stream_hash_regular_file_or_throw",
            "revalidated.sha256 != operation.content_sha256",
            "sha256_hex(revalidated.selected_bytes)",
            "verify_named_regular_file_or_throw",
            "final root proof",
        )
        and "reusable durable snapshot did not reconcile exact republished bytes"
            in service_runtime,
        "selected_payload_is_reopened_and_exactly_reproved_after_claim",
        "unchanged indexed payloads take the bounded-read fast path, while inode drift receives complete digest revalidation so changed bytes fail and exact atomic re-publication remains usable",
    )
    require(
        all(
            token in range_copy
            for token in (
                "offset_bytes > total_size",
                "range_bytes > total_size - offset_bytes",
                "::pread(",
                "offset_bytes + copied",
                "Sha256DigestBuilder digest",
                "::fstat(descriptor, &after)",
                "same_regular_file_observation(expected_status, after)",
            )
        )
        and "while (copied < range_bytes)" in range_copy
        and "while (position < total_size)" not in range_copy,
        "selected_range_reads_only_bounded_bytes_after_snapshot",
        "after one verified snapshot, an unchanged payload range reads and hashes only requested bytes; metadata drift is handled by the separate complete-digest fallback",
    )

    prefix_stage = function_body(
        store, "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw("
    )
    prefix_observer = function_body(
        store, "observe_staged_prefix_namespace_under_lease_or_throw("
    )
    require(
        all(
            token in store_h
            for token in (
                "sync_replica_file_payload_store_prefix_basename_is_exact",
                "stage_payload_prefix_or_throw",
                "one private\n    // raw partial file",
                "atomic no-replace rename",
                "truncatable tail",
                "stage_payload_range_or_throw remains",
            )
        )
        and all(
            token in store
            for token in (
                "kStagedPrefixBasenamePrefix",
                "parse_staged_prefix_basename",
                "staged_prefix_basename_or_throw",
                "transient_reserved_bytes",
            )
        )
        and "stage_payload_prefix_or_throw" in reconciliation_service,
        "single_prefix_owner_is_the_shipping_reconciliation_path",
        "new transfers use one basename-committed partial while the rev0941 range owner remains an explicit compatibility oracle",
    )
    require(
        ordered(
            prefix_stage,
            "ensure_store_identity_or_throw",
            "acquire_store_lease_or_throw",
            "observe_staged_prefix_namespace_under_lease_or_throw",
            "legacy_range_or_assembly_present",
            "duplicate_shared_open_description_or_throw",
            "staged_prefix_basename_or_throw",
            "O_RDWR | O_CREAT | O_EXCL",
            "open_staged_prefix_writable_or_throw",
            "staged prefix crash-tail recovery",
            "pwrite_all_or_throw",
            "staged prefix range file",
            "staged prefix commit",
            "staged prefix commit directory",
            "committed staged prefix fstat failed",
            "const std::string completed_sha256 = running.finish_hex()",
            "final publication preflight",
            "staged prefix direct publication",
            "staged prefix publication directory",
        )
        and "stage_payload_range_or_throw(" in prefix_stage,
        "prefix_commit_orders_data_name_and_final_digest_publication",
        "range bytes are fsynced before the basename cutpoint advances, rename ctime is refreshed, whole SHA-256 is re-proved, and only then is the same inode published under its digest",
    )
    require(
        all(
            token in prefix_observer
            for token in (
                "ExclusiveMutation",
                "pre-observation lease proof",
                "contains competing staged prefix owners",
                "legacy_range_or_assembly_present",
                "publication_residue_present",
                "observe_verification_index_file_or_throw",
                "kSyncReplicaFilePayloadVerificationIndexBasename",
                "verification index traversal cutpoint",
                "same_directory_observation",
                "final observation lease proof",
            )
        ),
        "prefix_hot_path_retains_lease_and_complete_namespace_classification",
        "continuation avoids rehashing unrelated immutable payloads without ignoring competing owners, legacy state, residue, or root drift",
    )
    require(
        all(
            token in runtime
            for token in (
                "first prefix range did not commit its exact cutpoint",
                "snapshot did not bound the physical uncommitted crash tail",
                "restart recovery retained bytes beyond the committed basename cutpoint",
                "complete prefix did not publish directly under the whole digest",
                "shipping prefix API did not resume the rev0941 range owner",
                "legacy resume minted a competing staged prefix owner",
                "short physical prefix allowed a second transfer to overcommit completion capacity",
                "staged-prefix hot path rejected or misread the internal verification index",
                "graceful prefix completion did not checkpoint post-rename metadata for restart reuse",
            )
        ),
        "compiled_prefix_matrix_covers_crash_replay_completion_and_upgrade",
        "the runtime matrix distinguishes physical tails from committed prefixes, catches self-rename metadata drift, and proves rev0941 continuation without a second owner",
    )
    one_put = function_body(
        store, "SyncReplicaFilePayloadStore::put_payload_or_throw("
    )
    batch_begin = function_body(
        store, "SyncReplicaFilePayloadStore::begin_mutation_batch_or_throw()"
    )
    batch_put = function_body(
        store,
        "SyncReplicaFilePayloadStoreMutationBatch::put_payload_or_throw(",
    )
    require(
        ordered(
            batch_begin,
            "mutation batch source preflight",
            "ensure_store_identity_or_throw",
            "reopen_matching_root_authority_or_throw",
            "acquire_store_lease_or_throw",
            "SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation",
            "scan_store_under_lease_or_throw",
            "remove_scanned_publication_residues_or_throw",
            "mutation batch ready cutpoint",
        )
        and ordered(
            batch_put,
            "sha256_hex(payload)",
            "batch.source_bytes = checked_add_u64_or_throw",
            "find_entry(batch.index.entries, digest)",
            "existing payload pre-reconciliation lease cutpoint",
            "reconcile_sync_immutable_file_create_new_under_directory_or_throw",
            "require_new_payload_publication_capacity_or_throw",
            "payload pre-publication lease cutpoint",
            "write_sync_file_atomically_create_new_under_directory_or_throw",
            "observe_exact_published_payload_without_rehash_or_throw",
            "insert_payload_index_entry_or_throw",
            "payload publication final lease cutpoint",
            "failed string publication reconciliation",
            "reconciled payload exact-byte proof",
        )
        and "std::rethrow_exception(original)" in batch_put
        and ordered(
            one_put,
            "payload exceeds configured byte budget",
            "begin_mutation_batch_or_throw",
            "batch.put_payload_or_throw",
        ),
        "put_is_preflight_bounded_create_new_and_ambiguity_reconciled",
        "one exclusive batch owns the complete scan and exact sorted index; create-new publication updates that index only after durable exact observation, while the one-put oracle delegates to a one-element batch",
    )

    pass_body = function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw(",
    )
    require(
        all(
            token in store_h
            for token in (
                "class SyncReplicaFilePayloadStoreMutationBatch final",
                "const SyncReplicaFilePayloadStoreMutationBatch&) = delete",
                "begin_mutation_batch_or_throw",
                "full_scan_count() const",
                "source_bytes() const",
                "indexed_entry_count() const",
            )
        )
        and all(
            token in folder_scan_h
            for token in (
                "maximum_payload_batch_puts",
                "maximum_payload_batch_work_bytes",
                "payload_mutation_batch_count",
                "payload_mutation_full_scan_count",
                "payload_mutation_put_count",
                "payload_mutation_source_bytes",
                "payload_mutation_work_bytes",
                "payload_mutation_peak_batch_put_count",
                "payload_mutation_peak_batch_work_bytes",
                "payload_mutation_inserted_count",
                "payload_mutation_already_present_count",
            )
        )
        and ordered(
            pass_body,
            "std::optional<SyncReplicaFilePayloadStoreSnapshot> payload_cutpoint",
            "try_idle_fast_path",
            "observe_payload_snapshot_or_throw()",
            "std::optional<SyncReplicaFilePayloadStoreMutationBatch> payload_batch",
            "payload_batch_prepared_work_bytes",
            "begin_mutation_batch_or_throw",
            "current_payload_batch_work_bytes",
            "payload_mutation_batch_count",
            "payload_mutation_full_scan_count",
            "payload_mutation_put_count",
            "payload_mutation_source_bytes",
            "payload_mutation_work_bytes",
            "payload_mutation_peak_batch_put_count",
            "payload_mutation_peak_batch_work_bytes",
            "payload_mutation_inserted_count",
            "payload_mutation_already_present_count",
            "payload_batch.reset()",
            "batch_would_cross_work",
            "release_saturated_payload_batch",
            "const SyncReplicaFolderTraversalSegment local_segment",
            "visit_sync_replica_folder_regular_file_paths_resumable_or_throw",
            "const std::optional<SyncReplicaFolderCatalogEntry> prior_hint",
            "classified_size_bytes == prior_hint->size_bytes",
            "release_payload_batch();",
            "batch_would_cross_work(classified_size_bytes)",
            "batch_live_during_prepare",
            "payload_batch_prepared_work_bytes = add_or_throw",
            "observed_remote_successor_paths.push_back(",
            "if (handled_without_local_publication)",
            "release_payload_batch();",
            "payload_cutpoint->payload_size_or_none",
            "retained_payload = &*payload_cutpoint",
            "if (retained_payload != nullptr)",
            "batch_would_cross_work(exact_size)",
            "commit_prepared_regular_file_with_payload_batch_or_throw",
            "release_saturated_payload_batch();",
            "segment_seen_paths.push_back(canonical_path)",
            "report.traversal = local_segment.traversal",
            "release_payload_batch();",
            "fallback payload cutpoint reproof",
            "record_scan_seen_paths_or_throw",
            "if (local_segment.completed)",
            "load_complete_scan_seen_paths_or_throw",
            "absence_snapshot",
        )
        and all(
            token in runtime
            for token in (
                "payload mutation batch rescanned or miscounted sequential puts",
                "inactive payload mutation batch exposed source-byte accounting",
                "live payload mutation batch allowed a nested shared snapshot",
                "live payload mutation batch allowed a competing mutation",
                "released payload mutation batch did not publish its exact verified index for immediate warm reuse",
                "payload mutation batch lost safe ownership after creator destruction",
            )
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "one many-file pass did not publish every payload and its immediate warm index through retained mutation authority",
                "changed many-file pass did not release exclusive payload authority before hashing the following likely no-op while preserving immediate warm reuse",
                "payload mutation count frontier did not split one traversal into warm bounded lease segments",
                "payload mutation work frontier did not isolate exact segments and one larger single-file batch",
                "composed pass accepted a zero payload mutation put frontier",
                "composed pass accepted a zero payload mutation work frontier",
                "folder walk did not release local mutation authority for remote apply and reacquire it afterward",
            )
        ),
        "folder_pass_segments_payload_store_lease_by_puts_and_exact_work",
        "one exact append-only payload cutpoint proves unchanged local payloads, while genuinely new digests reuse a warm verified index only inside explicit put and exact-work segments; traversal retains only exact remote-predecessor eligibility and releases exclusive payload authority before the independent cyclic apply phase",
    )
    resumable_walk = function_body(
        folder_observer,
        "visit_sync_replica_folder_regular_file_paths_resumable_impl_or_throw(",
    )
    resumable_regular_file = function_body(
        folder_observer,
        "handle_regular_file_or_throw(",
    )
    require(
        all(
            token in folder_observer_h
            for token in (
                "kSyncReplicaFolderTraversalDefaultMaximumRegularFiles = 4096U",
                "struct SyncReplicaFolderTraversalSegmentLimits final",
                "std::uint64_t maximum_regular_files",
                "const SyncReplicaFolderTraversalSegmentLimits& segment_limits",
                "validate_sync_replica_folder_traversal_segment_limits_or_throw",
            )
        )
        and ordered(
            resumable_walk,
            "validate_sync_replica_folder_observation_limits_or_throw",
            "validate_sync_replica_folder_traversal_segment_limits_or_throw",
            "walk_directory_or_throw",
            "root after traversal",
        )
        and ordered(
            resumable_regular_file,
            "context.summary.regular_file_count >=",
            "context.segment_limits->maximum_regular_files",
            "classified_regular_file_size_or_throw",
            "(*context.visitor)(canonical_path, initial_size)",
            "segment.resume_after_path = canonical_path",
        )
        and ordered(
            folder_observer,
            "segment_limits.maximum_regular_files = limits.maximum_regular_files",
            "return visit_sync_replica_folder_regular_file_paths_resumable_or_throw",
        ),
        "resumable_observer_has_compatible_delivered_file_frontier",
        "the explicit production overload bounds delivered regular paths before the next callback, while the compatibility overload adds no smaller scheduling frontier than the whole-folder regular-file capacity",
    )
    require(
        all(
            token in folder_observer_h
            for token in (
                "enum class SyncReplicaFolderTraversalStopReason",
                "EndOfNamespace = 1",
                "AggregateFileByteFrontier = 2",
                "RegularFileCountFrontier = 3",
                "DirectoryCensusFrontier = 4",
                "sync_replica_folder_traversal_stop_reason_name",
                "SyncReplicaFolderTraversalStopReason stop_reason",
            )
        )
        and all(
            token in folder_observer
            for token in (
                "StoppedAtAggregateFileByteFrontier",
                "StoppedAtRegularFileCountFrontier",
                "StoppedAtDirectoryCensusFrontier",
                "SyncReplicaFolderTraversalStopReason::EndOfNamespace",
                "AggregateFileByteFrontier",
                "RegularFileCountFrontier",
                "DirectoryCensusFrontier",
            )
        )
        and ordered(
            resumable_walk,
            "walk_directory_or_throw",
            "root after traversal",
            "switch (disposition)",
            "segment.traversal = context.summary",
        ),
        "resumable_observer_reports_exact_scheduling_stop_reason",
        "a normally returned segment distinguishes namespace completion from byte and delivered-path scheduling frontiers only after rooted traversal reproof",
    )
    require(
        "maximum_local_scan_segment_regular_files" in folder_scan_h
        and "kSyncReplicaFolderTraversalDefaultMaximumRegularFiles"
        in folder_scan_h
        and ordered(
            folder_scan,
            "limits.maximum_local_scan_segment_regular_files",
            "validate_sync_replica_folder_traversal_segment_limits_or_throw",
            "local_scan_segment_limits.maximum_regular_files =",
            "limits.maximum_local_scan_segment_regular_files",
            "std::min(\n            limits.maximum_regular_files,\n            limits.maximum_local_scan_segment_regular_files)",
            "traversal_limits, local_scan_segment_limits",
        )
        and "catalog_hints.entries.size()" not in folder_scan[
            folder_scan.find("std::vector<std::string> segment_seen_paths;") :
            folder_scan.find("std::optional<SyncReplicaFilePayloadStoreMutationBatch>")
        ]
        and all(
            token in folder_process
            for token in (
                ".maximum_local_scan_segment_regular_files > 0U",
                ".maximum_local_scan_segment_regular_files <=",
                "SyncReplicaFolderConvergencePassLimits{}.maximum_regular_files",
            )
        ),
        "folder_owner_bounds_scan_journal_staging_by_path_count",
        "the production fallback reserves and publishes at most one explicit delivered-file segment instead of inheriting the whole catalog cardinality",
    )
    require(
        all(
            token in folder_observer_h
            for token in (
                "kSyncReplicaFolderObservationDefaultMaximumEntries = 262144U",
                "kSyncReplicaFolderObservationDefaultMaximumRegularFiles = 100000U",
                "std::uint64_t maximum_entries =",
                "std::uint64_t maximum_regular_files =",
            )
        )
        and ordered(
            folder_observer,
            "increment_regular_file_count_or_throw(context, canonical_path)",
            "handle_regular_file_or_throw",
        )
        and "traversal_limits.maximum_regular_files = limits.maximum_regular_files"
        in folder_scan
        and "pass regular-file limit exceeds the retained catalog capacity"
        in folder_scan
        and "pass regular-file limit exceeds the retained payload-store capacity"
        in folder_scan
        and "pass entry limit exceeds the retained catalog capacity"
        not in folder_scan
        and all(
            token in folder_scan_runtime
            for token in (
                "test_namespace_entries_do_not_consume_file_capacity",
                "report.traversal.visited_entry_count == 3U",
                "report.traversal.regular_file_count == 2U",
                "namespace-entry work capacity remained incorrectly coupled to catalog row capacity",
                "regular-file limit exceeds the retained payload-store capacity",
            )
        ),
        "folder_namespace_work_and_durable_file_capacities_are_independent",
        "directories and ignored namespace objects remain bounded by a larger traversal-work ceiling, while only synchronizable regular files are composed against catalog and payload capacities and resumable prefix replay cannot evade that file ceiling",
    )
    idle_fast_path = folder_scan[
        folder_scan.find("const auto try_idle_fast_path") :
        folder_scan.find("// An early idle miss")
    ]
    require(
        ordered(
            idle_fast_path,
            "catalog_hints.entries.size()",
            "local_scan_segment_limits.maximum_regular_files",
            "const std::uint64_t catalog_regular_file_count",
            "const SyncReplicaSqliteSnapshot replica_cutpoint",
            "visit_sync_replica_folder_regular_file_paths_resumable_or_throw",
            "traversal_limits, local_scan_segment_limits",
        )
        and "tombstone-heavy catalog" in idle_fast_path
        and all(
            token in folder_scan_runtime
            for token in (
                "test_idle_proof_obeys_path_effect_frontier",
                "known-large idle folder bypassed the bounded durable scan frontier",
                "first.local_catalog_no_op_count == 2U",
                "second.local_scan_resume_after_path == \"d.txt\"",
                "completed.local_catalog_no_op_count == 1U",
                "tombstone-heavy catalog performed a whole speculative idle proof",
            )
        ),
        "idle_fast_path_obeys_authoritative_path_effect_frontier",
        "a catalog already larger than one scheduling segment, including one dominated by tombstones, bypasses speculative replica projection and whole-catalog filesystem checks; the authoritative scan and completed-epoch absence adjudication remain separate work",
    )
    require(
        "seen_regular_paths" not in idle_fast_path
        and ordered(
            idle_fast_path,
            "std::count_if(",
            "idle_regular_file_count =",
            "idle_regular_file_count != catalog_regular_file_count",
            "idle tombstone inspection",
        )
        and "Every delivered regular path already proved a distinct File catalog"
        in idle_fast_path,
        "idle_fast_path_uses_membership_plus_cardinality_not_path_copy",
        "every observed regular path proves one unique File mapping, cardinality proves no File mapping was omitted, and tombstones remain explicitly inspected without a duplicate whole-tree vector",
    )
    require(
        ordered(
            idle_fast_path,
            "const SyncReplicaFolderCatalogSnapshot fresh_catalog",
            "const FolderScanProgressHead fresh_scan_progress",
            "idle scan-progress reproof",
            "const SyncReplicaSqliteSnapshot fresh_replica",
            "const FolderRemoteWorkProgressHead fresh_remote_work_progress",
            "fresh_catalog != catalog_hints",
            "fresh_scan_progress != scan_progress",
            "fresh_replica != replica_cutpoint",
            "fresh_remote_work_progress != remote_work_progress",
        ),
        "idle_fast_path_reproves_all_mutable_sqlite_cutpoints",
        "the speculative no-effect path rechecks catalog authority, authenticated local scan continuation, replica authority, and the independent remote scheduling cursor before it may report idle; this lexical check does not prove race freedom",
    )

    require(
        "SyncReplicaFolderTraversalStopReason local_scan_stop_reason" in
        folder_scan_h
        and "report.local_scan_stop_reason = local_segment.stop_reason" in
        folder_scan
        and "idle.local_scan_stop_reason = idle_segment.stop_reason" in
        folder_scan
        and folder_cli.count("\\\"local_scan_stop_reason\\\"") == 1
        and sync_cli.count("\\\"local_scan_stop_reason\\\"") == 2
        and all(
            token in folder_scan_runtime
            for token in (
                "RegularFileCountFrontier",
                "AggregateFileByteFrontier",
                "EndOfNamespace",
            )
        ),
        "folder_reports_expose_non_authoritative_scan_stop_reason",
        "both command surfaces render the traversal outcome, and focused tests bind count-frontier and namespace-end reports without treating diagnostics as durable authority",
    )
    require(
        all(
            token in folder_observer_runtime
            for token in (
                "count-bounded continuation reaches every zero-byte path exactly once",
                "maximum_regular_files = 2U",
                "directory path changed while being observed: nested",
                "count frontier refuses success after a visited directory binding is substituted",
            )
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "test_zero_byte_scan_segment_has_bounded_journal_publication",
                "maximum_local_scan_segment_regular_files = 2U",
                "trace.insert_count == 2U",
                "trace.progress_update_count == 1U",
                "completed.local_published_count == 1U",
                "composed pass accepted a zero local scan path frontier",
            )
        ),
        "compiled_tests_cover_zero_byte_progress_restart_and_reproof",
        "focused runtime checks prove 2+2+1 durable progress, one bounded journal transaction, invalid-limit fail-fast behavior, compatibility, and directory-identity rejection at the count cutpoint",
    )

    require(
        all(
            token in folder_scan_h
            for token in (
                "kSyncReplicaFolderDefaultMaximumRemoteApplyOperations = 4096U",
                "enum class SyncReplicaFolderRemoteApplyStopReason",
                "AggregateFileByteFrontier = 2",
                "OperationCountFrontier = 3",
                "std::uint64_t maximum_remote_apply_operations",
                "std::uint64_t remote_apply_operation_count",
                "std::uint64_t deferred_remote_apply_candidate_count",
                "std::string remote_apply_started_after_path",
                "std::string remote_apply_resume_after_path",
                "bool remote_apply_wrapped_projection",
                "SyncReplicaFolderRemoteApplyStopReason remote_apply_stop_reason",
                "This frontier is therefore independent of the local scan segment size.",
            )
        )
        and all(
            token in folder_scan
            for token in (
                "pass remote-apply operation limit is invalid",
                "remote apply plan exceeded its operation frontier",
            )
        )
        and "remote-apply operation limit is smaller than the local scan segment regular-file limit"
        not in folder_scan
        and "local traversal exhausted the remote-apply operation frontier"
        not in folder_scan
        and folder_process.count(".maximum_remote_apply_operations") >= 2,
        "folder_remote_apply_effects_have_an_independent_cyclic_count_frontier",
        "one production pass bounds completed remote file/tombstone apply-owner calls independently of local traversal and bytes; local scanning proves eligibility, while a later cyclic planner owns the scheduling allowance below full remote-path admission",
    )

    convergence_pass = function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw(",
    )
    remote_planner = convergence_pass[
        convergence_pass.find("// Plan current sole-visible remote values") :
    ]
    remote_projection_admission = function_body(
        folder_scan, "validated_remote_projection_or_throw("
    )
    remote_sweep_validation = function_body(
        folder_scan, "validate_continuing_remote_inspection_sweep_or_throw("
    )
    require(
        ordered(
            remote_projection_admission,
            "for (const SyncReplicaPathView& path : remote_paths)",
            "remote path exceeds its relative-path byte limit",
            "remote path exceeds its directory-depth limit",
            "remote_model.active_operation_by_id_or_none(operation_id)",
            "remote file exceeds its per-file byte limit",
            "projection.push_back",
        )
        and ordered(
            remote_planner,
            "remote_paths.size() > limits.maximum_remote_paths",
            "validated_remote_projection_or_throw",
            "load_remote_work_progress_head_or_throw",
            "std::sort(",
            "observed_remote_successor_paths.begin()",
            "First perform hard admission over the complete sole-visible projection.",
            "remote_inspection_sweep_basis_digest_or_throw",
            "validate_continuing_remote_inspection_sweep_or_throw",
            "remaining_remote_apply_operations",
            "remote_candidates.reserve",
            "cyclic_remote_projection_start_after",
            "operation_count_full",
            "aggregate_file_bytes_full",
            "deferred_remote_apply_candidate_count",
            "for (const RemoteApplyCandidate& candidate : remote_candidates)",
            "publish_remote_work_progress_at_terminal_cutpoint_or_none",
        )
        and "pass remote files exceed its aggregate byte limit"
        not in remote_planner
        and "remote_candidates.reserve(remote_paths.size())"
        not in remote_planner,
        "remote_projection_preflights_all_hard_bounds_then_schedules_one_cyclic_segment",
        "path, depth, projection, evidence, and per-file admission inspect the complete sole-visible projection before rooted scheduling; independent inspection, byte, and effect frontiers rotate one segment, and cursor publication follows all selected idempotent effects",
    )

    require(
        all(
            token in folder_scan_h
            for token in (
                "kSyncReplicaFolderDefaultMaximumRemoteInspectionPaths = 4096U",
                "InspectionPathFrontier = 4",
                "std::uint64_t maximum_remote_inspection_paths",
                "std::uint64_t remote_inspected_path_count",
                "std::uint64_t remote_acknowledged_path_count",
                "std::uint64_t deferred_remote_inspection_path_count",
                "std::string remote_inspection_sweep_started_after_path",
                "std::uint64_t remote_inspection_sweep_seen_path_count",
                "bool completed_remote_inspection_sweep",
                "bool remote_inspection_sweep_had_unresolved_paths",
                "AuthorityCutpointChanged = 5",
                "bool remote_inspection_terminal_cutpoint_reproved",
                "std::string remote_inspection_terminal_catalog_digest",
                "std::string remote_inspection_terminal_visible_state_digest",
            )
        )
        and ordered(
            remote_planner,
            "remote_inspection_sweep_remaining_path_count",
            "limits.maximum_remote_inspection_paths",
            "InspectionPathFrontier",
            "acknowledge_remote_path",
            "completed_remote_inspection_sweep",
            "deferred_remote_inspection_path_count",
            "inspection_sweep_started_after_path",
            "publish_remote_work_progress_at_terminal_cutpoint_or_none",
        )
        and ordered(
            remote_sweep_validation,
            "inspection_sweep_seen_path_count",
            "cyclic_remote_projection_start_after",
            "expected_cursor",
            "cursor/count disagrees with its projection origin",
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "test_remote_inspection_frontier_rotates_safe_deferrals_across_restart",
                "test_remote_inspection_sweep_settles_stable_projection_across_restart",
                "remote inspection sweep cursor/count disagrees with its projection origin",
                "folder owner trusted an internally inconsistent cyclic remote sweep",
            )
        ),
        "remote_inspection_sweep_is_bounded_origin_bound_and_restart_safe",
        "rooted inspection has its own path frontier; a stable basis accumulates acknowledged paths across restarts, while the persisted origin makes cursor/count drift detectable before any resumed rooted effect",
    )

    visible_guard = function_body(
        sqlite_owner, "guard_visible_state_at_digest_or_throw("
    )
    catalog_terminal_publication = function_body(
        folder_scan, "publish_remote_work_progress_at_catalog_cutpoint_or_none("
    )
    cross_owner_terminal_publication = function_body(
        folder_scan, "publish_remote_work_progress_at_terminal_cutpoint_or_none("
    )
    require(
        "guard_visible_state_at_digest_or_throw" in sqlite_owner_h
        and ordered(
            visible_guard,
            "is_lowercase_sha256_hex",
            "SyncSqliteTransactionMode::Immediate",
            "require_write_authority_or_throw",
            "load_state_or_throw",
            "snapshot_from_loaded",
            "snapshot.visible_state_digest != expected_visible_state_digest",
            "new SyncReplicaSqliteProjectionGuard",
        )
        and ordered(
            catalog_terminal_publication,
            "SyncSqliteTransactionMode::Immediate",
            "load_folder_catalog_cutpoint_head_or_throw",
            "load_scan_progress_head_or_throw",
            "load_remote_work_progress_head_or_throw",
            "current_catalog_cutpoint != expected_catalog_cutpoint",
            "current_scan_progress != expected_scan_progress",
            "current != expected",
            "UPDATE ",
            "staged != wanted",
            "transaction.commit()",
        )
        and ordered(
            cross_owner_terminal_publication,
            "guard_visible_state_at_digest_or_throw",
            "publish_remote_work_progress_at_catalog_cutpoint_or_none",
            "replica_guard->commit_or_throw",
        )
        and ordered(
            remote_planner,
            "const SyncReplicaFolderCatalogSnapshot terminal_catalog",
            "publish_remote_work_progress_at_terminal_cutpoint_or_none",
            "AuthorityCutpointChanged",
            "remote_inspection_terminal_cutpoint_reproved = true",
            "remote_inspection_terminal_catalog_digest",
            "remote_inspection_terminal_visible_state_digest",
        )
        and "idle terminal cutpoint" in folder_scan
        and all(
            token in sqlite_owner_runtime
            for token in (
                "visible-state guard did not retain the expected projection",
                "independent causal writer crossed a live visible-state guard",
                "stale visible-state digest minted authority or changed durable state",
            )
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "test_terminal_cutpoint_fence_serializes_progress_publication",
                "remote progress publication was not covered by the replica writer guard",
                "terminal-fence pass did not report its exact post-publication cutpoint",
                "test_terminal_cutpoint_movement_withholds_stale_settlement",
                "changed replica projection published stale cursor or settlement authority",
                "test_terminal_catalog_progress_movement_withholds_stale_publication",
                "terminal-progress fixture did not move scheduling authority before the terminal catalog lock",
                "changed catalog progress was overwritten or granted stale settlement authority",
            )
        )
        and folder_cli.count(
            "\\\"remote_inspection_terminal_cutpoint_reproved\\\""
        ) == 1
        and sync_cli.count(
            "\\\"remote_inspection_terminal_cutpoint_reproved\\\""
        ) == 2,
        "terminal_remote_cutpoint_fence_serializes_projection_and_catalog_progress",
        "one replica BEGIN IMMEDIATE guard excludes visible-projection writers while one catalog BEGIN IMMEDIATE transaction compares the exact catalog, authenticated scan, and remote-progress heads; stale authority withholds cursor publication and settlement evidence",
    )

    require(
        "struct RemoteProjectionEntry final" in folder_scan
        and "const SyncReplicaOperation* operation;" in function_body(
            folder_scan, "struct RemoteProjectionEntry final"
        )
        and "SyncReplicaOperation operation;" not in function_body(
            folder_scan, "struct RemoteProjectionEntry final"
        )
        and "std::string canonical_path;" not in function_body(
            folder_scan, "struct RemoteProjectionEntry final"
        )
        and "std::size_t projection_index = 0U;" in function_body(
            folder_scan, "struct RemoteApplyCandidate final"
        )
        and "std::string operation_id;" not in function_body(
            folder_scan, "struct RemoteApplyCandidate final"
        )
        and "active_operation_by_id_or_none(operation_id)" in
            remote_projection_admission
        and "std::optional<SyncReplicaOperation>" not in
            remote_projection_admission
        and ordered(
            remote_planner,
            "const std::vector<SyncReplicaPathView> remote_paths",
            "validated_remote_projection_or_throw",
            "load_remote_work_progress_head_or_throw",
            "RemoteApplyCandidate{",
            "projection_index,",
            "remote_projection[candidate.projection_index].operation",
        ),
        "remote_projection_and_candidate_plan_avoid_duplicate_path_and_operation_ownership",
        "the temporary visible-path graph dies before rooted planning, the admitted projection borrows active operations from one immutable model, and bounded candidates retain only stable projection indexes rather than duplicate paths, IDs, metadata, and causal context",
    )

    require(
        all(
            token in model_h
            for token in (
                "Borrowed active lookup for immutable bulk projections",
                "model remains alive and no non-const model operation is invoked",
                "const SyncReplicaOperation* active_operation_by_id_or_none",
            )
        )
        and ordered(
            function_body(model, "SyncReplicaModel::operation_by_id("),
            "active_operation_by_id_or_none(operation_id)",
            "return *operation;",
        )
        and ordered(
            function_body(
                model,
                "SyncReplicaModel::active_operation_by_id_or_none(",
            ),
            "active_operation_ids_.contains(operation_id)",
            "evidence_by_id_.find(operation_id)",
            "return &found->second;",
        )
        and all(
            token in network_model_runtime
            for token in (
                "borrowed_alpha_first",
                "borrowed_alpha_second ==",
                "unknown-operation",
                "permutation_alpha.operation_id) == nullptr",
                "borrowed active lookup did not return stable model-owned addresses",
                "borrowed active lookup admitted an unknown operation ID",
                "both same-dot envelopes must be retained but inactive",
            )
        ),
        "borrowed_active_operation_lookup_has_explicit_lifetime_and_runtime_coverage",
        "the model exposes an active-only borrowed lookup with a documented lifetime, legacy value lookup delegates to it, and runtime coverage binds stable active addresses plus null quarantined/unknown results",
    )

    visible_path_projection = function_body(
        model, "visible_path_view_or_throw("
    )
    active_path_ordering = function_body(
        model, "SyncReplicaModel::ordered_active_operations_by_path() const"
    )
    active_path_projection = function_body(
        model_h, "void for_each_active_path(const Visitor& visitor) const"
    )
    visible_paths_projection = function_body(
        model, "SyncReplicaModel::visible_paths() const"
    )
    require(
        ordered(
            active_path_ordering,
            "std::vector<const SyncReplicaOperation*> ordered",
            "for (const std::string& operation_id : active_operation_ids_)",
            "std::sort(",
            "left->canonical_path < right->canonical_path",
            "return ordered;",
        )
        and ordered(
            active_path_projection,
            "ordered_active_operations_by_path()",
            "std::span<const SyncReplicaOperation* const> candidates",
            "visible_path_view_from_active_candidates_or_throw(candidates)",
            "visitor(view, candidates)",
        )
        and "std::map<" not in active_path_ordering + active_path_projection
        and "std::vector<SyncReplicaOperation>" not in active_path_ordering + active_path_projection
        and "std::function" not in model_h
        and "for_each_active_path(" in visible_paths_projection
        and "visible_path(path)" not in visible_paths_projection
        and "std::set<std::string> paths" not in visible_paths_projection
        and "visible_path_view_from_active_candidates_or_throw(" in
            function_body(model, "SyncReplicaModel::visible_path(")
        and "visible_path_view_or_throw(" in function_body(
            model,
            "SyncReplicaModel::visible_path_view_from_active_candidates_or_throw(",
        )
        and all(
            token in visible_path_projection
            for token in (
                "std::map<SyncReplicaActor, std::uint64_t>",
                "maximum_covered_counter",
                "candidate->causal_context",
                "covered->second < candidate->dot.counter",
                "visible.reserve(candidates.size())",
                "primary_visible_operation_or_throw(visible)",
                "view.visible_operation_ids.reserve(visible.size())",
                "view.preserved_file_operation_ids.reserve(visible.size() - 1U)",
            )
        )
        and "sync_replica_operation_supersedes" not in visible_path_projection
        and all(
            token in network_model_runtime
            for token in (
                "grouped_projection_path_count = 512U",
                "grouped_projection_model.visible_paths()",
                "one-pass grouped visible projection changed canonical ordering or primary evidence",
                "borrowed active-path visitor changed ordering, grouping, or model-owned operation identity",
                "compile-time active-path visitor copied or omitted a move-only visitor",
                "causal-coverage projection diverged from pairwise supersession",
                "operations.size() == 258U",
            )
        ),
        "visible_path_projection_groups_active_operations_once_by_borrowed_path",
        "bulk projection sorts one borrowed pointer vector, visits each path once, and computes maximal operations from aggregate causal coverage while runtime differential coverage preserves canonical ordering, conflict projection, and model-owned identity",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "remote aggregate frontier did not commit exactly one safe prefix",
                "remote aggregate frontier did not advance its deferred suffix on the next pass",
                "test_remote_apply_count_frontier_bounds_zero_byte_and_tombstone_work",
                "OperationCountFrontier",
                "remote cyclic scheduling weakened complete-projection path preflight",
                "remote suffix preflight applied a selected prefix before rejecting invalid evidence",
                "remote-apply operation limit is invalid",
                "independent local-scan and cyclic remote-apply frontiers were not accepted",
                "test_remote_apply_cursor_survives_restart_and_defeats_prefix_churn",
                "sustained early-path churn starved the later remote path after restart",
                "cyclic cursor did not wrap and settle the continuously changing prefix",
            )
        )
        and "remote-apply operation limit is smaller than the local scan segment regular-file limit"
        not in folder_scan_runtime,
        "compiled_tests_cover_remote_byte_count_cyclic_progress_and_suffix_preflight",
        "focused runtime tests bind two-pass byte progress, mixed zero-byte/tombstone count progress, independent scan/apply frontiers, full-suffix hard preflight, restart persistence, and service of a later path despite sustained early-prefix churn",
    )

    require(
        all(
            token in folder_scan
            for token in (
                "constexpr std::uint64_t kCyclicSchemaVersion = 4U",
                "constexpr std::uint64_t kPreselectionSchemaVersion = 5U",
                "constexpr std::uint64_t kSelectiveSyncSchemaVersion = 6U",
                "constexpr std::uint64_t kSchemaVersion = 7U",
                "inspection_sweep_started_after_path",
                "load_cyclic_catalog_or_throw",
                "migrate_cyclic_catalog_or_throw",
                "retained_scan_progress",
                "retained_remote_work_cursor",
                "migration changed authenticated scan continuation",
                "migration changed the v4 remote-work cursor",
            )
        )
        and ordered(
            function_body(folder_scan, "void migrate_cyclic_catalog_or_throw("),
            "load_cyclic_catalog_or_throw",
            "load_scan_progress_head_or_throw",
            "load_cyclic_remote_work_cursor_or_throw",
            "RENAME TO sync_replica_folder_catalog_meta_v4",
            "RENAME TO sync_replica_folder_catalog_remote_apply_progress_v4",
            "create v5 metadata",
            "create v5 remote-work progress",
            "VALUES(1,?,'','',0,0)",
            "migration changed authenticated scan continuation",
            "migration changed the v4 remote-work cursor",
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "test_rev0951_cyclic_catalog_migrates_cursor_and_resets_sweep",
                "rev0951 migration changed catalog, scan journal, or remote cursor authority",
                "rev0951 migration did not preserve the v4 cursor at v7 indexed sweep genesis",
                "sqlite3_column_int64(schema.stmt, 0) == 7",
                "folder owner accepted a noncanonical remote scheduling cursor",
            )
        ),
        "v5_migration_preserves_v4_cursor_and_authenticated_scan_authority",
        "the exact v4 catalog is proved before the preselection-v5 transition, metadata and scheduling singleton alone are replaced, the authenticated scan journal and cyclic cursor survive, and the later v5-to-v6 selection migration preserves that authority",
    )

    local_traversal = folder_scan[
        folder_scan.find("const SyncReplicaFolderTraversalSegment local_segment") :
        folder_scan.find("report.traversal = local_segment.traversal")
    ]
    require(
        "observed_remote_successor_paths.push_back(" in local_traversal
        and "apply_visible_regular_file_or_throw" not in local_traversal
        and "apply_visible_tombstone_or_throw" not in local_traversal
        and ordered(
            remote_planner,
            "std::sort(",
            "observed_remote_successor_paths.begin()",
            "cyclic_remote_projection_start_after",
            "std::binary_search(",
            "observed_remote_successor_paths.begin()",
            "apply_visible_regular_file_with_payload_snapshot_or_throw",
            "apply_visible_tombstone_or_throw",
            "publish_remote_work_progress_at_terminal_cutpoint_or_none",
        ),
        "local_traversal_proves_predecessors_but_cyclic_planner_owns_all_remote_effects",
        "local namespace order can no longer spend remote-effect capacity: traversal records exact predecessor eligibility or conflict only, and every remote file/tombstone effect is selected through the persisted cyclic scheduler",
    )

    targeted_access_begin = function_body(
        store,
        "SyncReplicaFilePayloadStore::begin_targeted_access_or_throw(",
    )
    targeted_observation = function_body(
        store, "open_targeted_payload_observation_or_throw("
    )
    require(
        all(
            token in folder_scan_h
            for token in (
                "remote_payload_snapshot_observation_count",
                "remote_payload_snapshot_entry_count",
                "remote_targeted_payload_access_count",
                "remote_targeted_payload_probe_count",
                "remote_targeted_payload_selection_count",
                "remote_targeted_payload_selected_bytes",
                "deferred_remote_payload_candidate_count",
                "apply_visible_regular_file_with_payload_snapshot_or_throw",
                "try_apply_visible_regular_file_with_targeted_payload_or_throw",
            )
        )
        and ordered(
            remote_planner,
            "if (report.payload_mutation_put_count != 0U)",
            "payload_cutpoint.reset()",
            "require_retained_remote_payload_snapshot",
            "require_targeted_remote_payload_access",
            "begin_targeted_access_or_throw",
            "remote_targeted_payload_access_count",
            "remote_targeted_payload_probe_count",
            "observe_optional_payload_size_for_operation_or_throw",
            "deferred_remote_payload_candidate_count",
            "operation_count_full",
            "try_apply_visible_regular_file_with_targeted_payload_or_throw",
            "remote_targeted_payload_selection_count",
            "remote_targeted_payload_selected_bytes",
            "publish_remote_work_progress_at_terminal_cutpoint_or_none",
        )
        and all(
            token in store_h
            for token in (
                "class SyncReplicaFilePayloadStoreTargetedAccess final",
                "begin_targeted_access_or_throw",
                "observe_optional_payload_size_for_operation_or_throw",
                "open_optional_payload_for_operation_or_throw",
                "performs the potentially expensive identity bootstrap/reconciliation once",
                "holds no store lease across planning or destination I/O",
                "snapshot_or_throw remains the complete-namespace health",
            )
        )
        and targeted_access_begin.count("ensure_store_identity_or_throw(") == 1
        and targeted_access_begin.count("acquire_store_lease_or_throw(") == 1
        and "label + \" identity cutpoint\",\n"
            "        StoreObservationDurability::ObserveOnly"
            in targeted_access_begin
        and "open_targeted_payload_observation_or_throw" in store
        and "ensure_store_identity_or_throw(" not in targeted_observation
        and "label + \" selection\", StoreObservationDurability::ObserveOnly"
            in targeted_observation
        and "same_regular_file_observation(" in targeted_observation
        and "payload-store identity changed after targeted-access preflight"
            in targeted_observation
        and "selected payload descriptor lease cutpoint" in targeted_payload_open
        and "selected payload descriptor root proof" in targeted_payload_open
        and "payload.payload_durability" in targeted_payload_open
        and "stream_hash_regular_file_or_throw" not in targeted_payload_open
        and all(
            token in sync_cli
            for token in (
                "remote_targeted_payload_accesses",
                "remote_targeted_payload_probes",
                "remote_targeted_payload_selections",
            )
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "catchup.remote_payload_snapshot_observation_count == 1U",
                "catchup.remote_payload_snapshot_entry_count == 3U",
                "catchup.remote_targeted_payload_access_count == 0U",
                "catchup.remote_targeted_payload_probe_count == 0U",
                "catchup.remote_targeted_payload_selection_count == 0U",
                "catchup.remote_targeted_payload_selected_bytes == 0U",
                "missing remote payload was not retained as bounded scheduling remainder",
                "an unavailable remote prefix blocked a ready suffix or forced repeated inventories",
                "test_targeted_remote_payload_path_does_not_claim_complete_namespace_audit",
                "test_remote_only_tombstone_catalog_defers_complete_payload_inventory",
                "test_targeted_remote_payload_hashes_only_at_publication_boundary",
                "targeted selection was incorrectly promoted to a complete payload ",
                "source SHA-256 changed before publication",
                "pass.remote_targeted_payload_access_count == 1U",
            )
        ),
        "remote_apply_uses_one_targeted_access_or_retained_complete_inventory",
        "a retained complete inventory is reused when available; otherwise one pass-scoped identity/root cutpoint amortizes observation-only exact-name probes and selections without claiming unrelated namespace health, while every operation still takes a fresh shared lease and atomic publication performs the sole selected-byte SHA-256 read",
    )

    require(
        all(
            token in folder_scan_h
            for token in (
                "remote_apply_revalidated_catalog_predecessor_count",
                "Catalog metadata only",
                "nominates work",
            )
        )
        and ordered(
            remote_planner,
            "observed_remote_successor_paths.begin()",
            "require_catalog_operation_or_throw",
            "operation.operation_id == prior_operation.operation_id",
            "catalog predecessor metadata reproof",
            "source_snapshot_digest",
            "sync_replica_operation_supersedes",
            "remote_apply_revalidated_catalog_predecessor_count",
            "apply_visible_regular_file_with_payload_snapshot_or_throw",
        )
        and "durable_scan_journal_contains" not in remote_planner
        and "scan_epoch=? AND canonical_path=? AND ordinal<=?" not in folder_scan
        and "observe_optional_regular_file_beneath_root_or_throw" in apply_file
        and "observation_matches_catalog_entry" in apply_file
        and all(
            token in folder_scan_runtime
            for token in (
                "test_catalog_predecessor_reproof_decouples_remote_apply_from_scan_cursor",
                "restart waited for a whole scan-epoch wrap before applying the cataloged predecessor",
                "completed scan-epoch reset stranded a cataloged predecessor behind the new scan cursor",
                "catalog metadata reproof authorized stale remote publication after a local edit",
            )
        ),
        "catalog_predecessor_reproof_decouples_remote_apply_from_scan_journal_lifetime",
        "a present cataloged predecessor can be scheduled independently of the active or reset local scan cursor after fresh rooted metadata reproof, while the exact apply owner still reopens and fully hashes bytes before any effect",
    )

    require(
        all(
            token in folder_scan_h
            for token in (
                "struct SyncReplicaFolderScanProgressSnapshot final",
                "std::uint64_t scan_epoch",
                "std::uint64_t seen_path_count",
                "std::string seen_chain_digest",
                "std::string remote_apply_resume_after_path",
                "std::string remote_inspection_sweep_basis_digest",
                "std::string remote_inspection_sweep_started_after_path",
                "std::uint64_t remote_inspection_sweep_seen_path_count",
                "bool remote_inspection_sweep_had_unresolved_paths",
                "scan_progress_snapshot_or_throw",
            )
        )
        and ordered(
            folder_scan,
            "SyncReplicaFolderScanOwner::scan_progress_snapshot_or_throw",
            "load_scan_progress_head_or_throw",
            "load_remote_work_progress_head_or_throw",
            "SyncReplicaFolderScanProgressSnapshot snapshot",
            "transaction.commit()",
        )
        and all(
            token in sync_once_h
            for token in (
                "local_scan_epoch",
                "local_scan_seen_path_count",
                "local_scan_seen_path_bytes",
                "local_scan_resume_after_path",
                "local_scan_seen_chain_digest",
                "remote_apply_resume_after_path",
                "remote_inspection_sweep_basis_digest",
                "remote_inspection_sweep_started_after_path",
                "remote_inspection_sweep_seen_path_count",
                "remote_inspection_sweep_had_unresolved_paths",
            )
        )
        and ordered(
            sync_once,
            "catalog_snapshot_or_throw",
            "scan_progress_snapshot_or_throw",
            "replica_snapshot_or_throw",
        )
        and "authenticated scan-continuation change did not report durable progress"
        in sync_once_runtime
        and "remote scheduling cursor change did not report durable progress"
        in sync_once_runtime
        and "remote inspection-sweep continuation did not report durable progress"
        in sync_once_runtime
        and "remote inspection-sweep origin change did not report durable progress"
        in sync_once_runtime
        and "sync-once cutpoint did not expose remote cursor advancement"
        in sync_process_runtime
        and sync_cli.count("\\\"remote_apply_started_after_path\\\"") == 2
        and sync_cli.count("\\\"remote_apply_resume_after_path\\\"") == 3
        and sync_cli.count("\\\"remote_apply_wrapped_projection\\\"") == 2
        and sync_cli.count("\\\"remote_payload_snapshot_observations\\\"") == 2
        and sync_cli.count("\\\"remote_payload_snapshot_entries\\\"") == 2
        and sync_cli.count("\\\"deferred_remote_payload_candidates\\\"") == 2
        and sync_cli.count("\\\"remote_apply_revalidated_catalog_predecessors\\\"") == 2
        and sync_cli.count("\\\"remote_inspection_sweep_started_after_path\\\"") == 3
        and sync_cli.count("\\\"remote_inspection_sweep_seen_path_count\\\"") == 3,
        "sync_once_cutpoint_counts_scan_and_remote_scheduler_progress",
        "the process-visible cutpoint includes authenticated local scan continuation plus cursor, sweep basis, origin, count, and unresolved state, so crash-surviving bounded inspection cannot be mislabeled as no durable progress",
    )

    settlement_predicate = function_body(
        sync_once, "bool sync_replica_sync_once_final_pass_settles_cutpoint("
    )
    require(
        all(
            token in settlement_predicate
            for token in (
                "pass.completed_local_scan_epoch",
                "pass.deferred_remote_payload_candidate_count == 0U",
                "pass.deferred_remote_apply_candidate_count == 0U",
                "pass.deferred_unadjudicated_local_absence_remote_file_count == 0U",
                "pass.completed_remote_inspection_sweep",
                "pass.deferred_remote_inspection_path_count == 0U",
                "!pass.remote_inspection_sweep_had_unresolved_paths",
                "SyncReplicaFolderRemoteApplyStopReason::EndOfProjection",
                "pass.remote_inspection_terminal_cutpoint_reproved",
                "pass.remote_inspection_terminal_catalog_digest ==",
                "cutpoint.catalog_digest",
                "pass.remote_inspection_terminal_visible_state_digest ==",
                "cutpoint.replica_visible_state_digest",
                "pass.remote_apply_resume_after_path ==",
                "cutpoint.remote_apply_resume_after_path",
                "cutpoint.local_scan_seen_path_count == 0U",
                "cutpoint.local_scan_seen_path_bytes == 0U",
                "cutpoint.local_scan_resume_after_path.empty()",
                "cutpoint.remote_inspection_sweep_basis_digest.empty()",
                "cutpoint.remote_inspection_sweep_started_after_path.empty()",
                "cutpoint.remote_inspection_sweep_seen_path_count == 0U",
                "!cutpoint.remote_inspection_sweep_had_unresolved_paths",
            )
        )
        and "sync_replica_sync_once_final_pass_settles_cutpoint" in sync_once_h
        and "writer-serialized terminal" in sync_once_h
        and all(
            token in sync_once_runtime
            for token in (
                "matching terminal cutpoint did not settle",
                "missing terminal reproof settled",
                "stale terminal catalog digest settled",
                "stale terminal visible-state digest settled",
                "scheduling-only remote cursor movement settled",
                "incomplete local scan settled",
                "incomplete remote inspection settled",
                "deferred remote inspection settled",
                "changed authority cutpoint settled",
                "active local scan continuation settled",
                "active remote inspection continuation settled",
            )
        )
        and all(
            token in sync_process_runtime
            for token in (
                '"complete_with_unresolved_paths"',
                "settled=False",
                '"deferred_remote_apply_candidates": 1',
                '"completed_remote_inspection_sweep": False',
                '"completed_local_scan_epoch": False',
                '"receiver scan-frontier settlement sync"',
                '"complete_changed"',
                "scan-only settlement did not change its durable scan cutpoint",
            )
        ),
        "sync_once_settlement_proves_exact_terminal_cutpoint_and_empty_schedulers",
        "the final pass must settle the exact post-pass catalog, visible projection, and durable remote fairness cursor named by its writer-serialized terminal fence, while both authenticated local and remote continuations are empty and every bounded scheduling remainder is zero",
    )

    check_config = function_body(sync_cli, "int command_check_config(")
    require(
        "maximum_remote_apply_operations" in check_config
        and "folder_limits.maximum_remote_apply_operations" in check_config
        and 'value.get("maximum_remote_apply_operations") != 4096'
        in service_configuration_runtime,
        "service_check_config_reports_effective_remote_apply_frontier",
        "installed-service preflight exposes the fixed production remote-effect scheduling frontier, and the real process test rejects omission or drift from the reviewed 4096-operation default",
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
    require(
        ordered(
            leased_scan,
            "read-only payload-store scan cannot reuse a verification cache",
            "pre-scan lease proof",
            "matching_verification_generation_or_none(",
            "cached_generation->entries",
            "scan_store_namespace_or_throw",
            "std::make_shared<PayloadVerificationGeneration>()",
            "mutable_generation->entries = out.entries",
            "verified_after = std::move(mutable_generation)",
            "final lease proof",
            "publish_verification_generation(",
        )
        and ordered(
            verification_cache_lookup,
            "cache.generation",
            "same_regular_file_observation",
            "return generation",
        )
        and ordered(
            verification_cache_publish,
            "generation == nullptr",
            "std::move(cache.generation)",
            "cache.generation = std::move(generation)",
        )
        and "std::mutex" not in verification_cache_lookup
        and "std::mutex" not in verification_cache_publish,
        "verification_cache_commits_only_after_complete_leased_scan",
        "failed hashing, allocation, root proof, or final marker proof leaves prior immutable acceleration state intact",
    )
    require(
        "#include <mutex>" in store
        and store.count("mutable std::mutex mutex_;") == 1
        and "class PayloadStoreLiveCapabilityRegistry final" in store
        and "scan_store_namespace_or_throw" not in verification_cache_lookup
        and "scan_store_namespace_or_throw" not in verification_cache_publish
        and "stream_hash_regular_file_or_throw" not in verification_cache_lookup
        and "stream_hash_regular_file_or_throw" not in verification_cache_publish
        and ordered(
            snapshot,
            "snapshot source preflight",
            "scan_store_under_lease_or_throw",
        )
        and ordered(
            batch_begin,
            "mutation batch source preflight",
            "scan_store_under_lease_or_throw",
        )
        and ordered(
            leased_scan,
            "pre-scan lease proof",
            "matching_verification_generation_or_none(",
            "scan_store_namespace_or_throw",
            "publish_verification_generation(",
        )
        and "foreign-thread payload snapshot reached owner-local cache authority"
        in runtime
        and "foreign-thread rejection damaged the originating owner's warm cache"
        in runtime,
        "verification_cache_uses_thread_affinity_instead_of_dead_mutex_bureaucracy",
        "every cache read and replacement follows originating-thread authority proof, compiled foreign-thread use is rejected before cache access, and no redundant mutex remains in the owner-local hot path",
    )
    require(
        "synchronizes_store_observation(durability)" in snapshot
        and "? store.verification_cache.get()" in snapshot
        and ": nullptr" in snapshot
        and all(
            token not in digest_body
            for token in (
                "scan_hashed_entry_count",
                "scan_hashed_bytes",
                "scan_reused_entry_count",
                "scan_reused_bytes",
            )
        )
        and all(
            token in runtime
            for token in (
                "first_inspection.scan_hashed_entry_count() == 2U",
                "first_inspection.scan_hashed_bytes() == total_bytes",
                "second_inspection.scan_hashed_entry_count() == 2U",
                "second_inspection.scan_hashed_bytes() == total_bytes",
                "read-only forensic observation reused process-local verification state",
            )
        ),
        "forensic_scans_bypass_acceleration_byte_verify_and_keep_work_metrics_noncanonical",
        "ReadOnlyInspect receives no warm cache and compiled coverage proves that repeated forensic scans hash every payload byte while diagnostic work cost cannot change durable snapshot identity",
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
        "clean pre-existing content did not receive its marker and restart-verification checkpoint",
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
        "a fresh payload-store owner did not completely hash its cold snapshot",
        "an unchanged warm snapshot reread payload bytes or changed durable identity",
        "an in-place payload mutation escaped complete verification",
        "in-place repair did not isolate hashing to the changed observation",
        "the atomic verification-cache replacement retained the old inode",
        "a replaced payload inode escaped complete verification",
        "replacement repair did not isolate hashing to the changed observation",
        "an identical replacement lease marker retained stale verification acceleration",
        "a restarted owner did not reuse exact marker-bound durable observations",
        "read-only forensic observation reused process-local verification state",
        "verification work accounting leaked into canonical snapshot identity",
        "malformed durable verification metadata granted payload reuse",
        "metadata-change repair was not checkpointed for the next owner",
        "staged-prefix hot path rejected or misread the internal verification index",
        "graceful prefix completion did not checkpoint post-rename metadata for restart reuse",
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
    scrub_advance = function_body(
        store, "advance_payload_scrub_from_snapshot_or_throw("
    )
    scrub_publish = function_body(
        store, "publish_payload_scrub_state_with_reconciliation("
    )
    scrub_state_validate = function_body(scrub_state, "void validate_state(")
    process_scrub_retain = function_body(
        store, "retain_process_scrub_active_observation("
    )
    process_scrub_match = function_body(
        store, "process_scrub_active_observation_matches_state("
    )
    process_scrub_match_wrapper = function_body(
        store, "process_scrub_active_observation_matches("
    )
    snapshot_body = function_body(
        store, "SyncReplicaFilePayloadStore::snapshot_with_reuse_policy_or_throw("
    )
    scrub_limit_validation = function_body(
        store, "validate_sync_replica_file_payload_store_limits_or_throw("
    )
    complete_scan = function_body(store, "scan_store_namespace_or_throw(")
    prefix_scan = function_body(
        store, "observe_staged_prefix_namespace_under_lease_or_throw("
    )
    require(
        all(
            token in resumable_h + resumable
            for token in (
                "kSha256MaximumMessageBytes",
                "ResumableSha256Checkpoint",
                "buffered_block",
                "total_bytes",
                "buffered_bytes",
                "noncanonical unused buffer bytes",
                "process_block",
                "finish_hex_array",
                "finish_hex",
            )
        )
        and all(
            token in resumable_runtime
            for token in (
                "million-a SHA-256 vector",
                "provider_oracle",
                "55U, 56U",
                "63U,",
                "64U, 65U",
                "message-length overflow was accepted",
                "noncanonical unused buffer byte was accepted",
                "fixed-width SHA-256 terminal form changed",
            )
        ),
        "resumable_sha256_has_stable_checked_continuation_and_independent_oracle",
        "the provider-independent continuation validates canonical state and message length while focused NIST, padding-boundary, restart, malformed-state, and OpenSSL-oracle cases guard the implementation",
    )
    require(
        all(
            token in scrub_state_h + scrub_state
            for token in (
                ".anonsync-payload-scrub-state-v1",
                "Idle = 1",
                "Progress = 2",
                "IntegrityFailure = 3",
                "completed_cycles",
                "cursor_after_content_sha256",
                "active_offset_bytes",
                "observed_content_sha256",
                "checksum is invalid",
                "length is not the exact v1 size",
                "active offset does not match hash progress",
                "failure digest does not match its hash state",
                "kSyncPosixRegularFileSnapshotMetadataEncodedBytes",
                "append_sync_posix_regular_file_snapshot_metadata_binary",
                "parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw",
                "validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw",
            )
        )
        and all(
            token in scrub_state_runtime
            for token in (
                "corrupted scrub state",
                "truncated scrub state",
                "extended scrub state",
                "incompatible scrub state",
                "idle scrub state retained active progress",
                "scrub state exceeded configured payload ceiling",
            )
        ),
        "scrub_state_is_fixed_checksum_framed_identity_bound_and_canonical",
        "the exact-size v1 grammar binds identity, cycles, cursor, active metadata/hash progress, and terminal mismatch while malformed or noncanonical forms fail closed",
    )
    require(
        all(
            token in scrub_limit_validation
            for token in (
                "max_scrub_bytes_per_attempt",
                "max_scrub_entries_per_attempt",
                "kSha256MaximumMessageBytes",
            )
        )
        and all(
            token in scrub_advance
            for token in (
                "std::min<std::uint64_t>",
                "snapshot.entries.size()",
                "limits.max_scrub_entries_per_attempt",
                "limits.max_scrub_bytes_per_attempt",
                "report.hashed_bytes",
                "report.touched_entry_count",
                "::pread",
                "received > remaining_file",
                "received > remaining_budget",
                "active_offset_bytes += received",
            )
        )
        and "max_scrub_bytes_per_attempt ==" in runtime
        and "4U * 1024U * 1024U" in runtime
        and "max_scrub_entries_per_attempt == 4U" in runtime,
        "scrub_attempts_are_strictly_byte_and_distinct_entry_bounded",
        "configuration rejects asymmetric or impossible bounds, the per-attempt entry limit is clamped to frozen namespace cardinality so wraparound cannot revisit an entry, and every read is fenced by both the remaining payload extent and remaining attempt budget",
    )
    require(
        ordered(
            snapshot_body,
            "SharedObservation",
            "scan_store_under_lease_or_throw",
            "observation_lease.verify_or_throw",
            "advance_payload_scrub_from_snapshot_or_throw",
            "refresh_verification_index_best_effort",
            "return SyncReplicaFilePayloadStoreSnapshot",
        )
        and "ReadOnlyInspect" in snapshot_body
        and "next_scrub_not_before" in snapshot_body
        and "kPayloadScrubMinimumInterval" in snapshot_body
        and "DeferredLeaseBusy" in snapshot_body
        and "DeferredAttemptFailure" in snapshot_body
        and "snapshot_digest_or_throw" not in scrub_advance,
        "scrub_runs_after_complete_authority_is_released_and_is_noncanonical",
        "one process-throttled exclusive optional attempt follows the complete shared snapshot; forensic mode, contention, and ordinary optional failures cannot change canonical payload truth",
    )
    require(
        all(
            token in complete_scan
            for token in (
                "kSyncReplicaFilePayloadScrubStateBasename",
                "scrub_state_present",
                "scrub_state_metadata",
            )
        )
        and all(
            token in prefix_scan
            for token in (
                "observe_scrub_state_file_or_throw",
                "kSyncReplicaFilePayloadScrubStateBasename",
                "scrub_state_seen",
                "scrub state traversal cutpoint",
            )
        )
        and "product bootstrap treated unbound scrub state as disposable empty space"
        in runtime
        and "scrub state publication crossed the exact transient capacity fence"
        in runtime,
        "scrub_state_namespace_is_reserved_reproved_and_prebootstrap_rejected",
        "both production namespace observers recognize and re-prove the internal record, its writer residue remains capacity-bounded, and product bootstrap cannot adopt attacker-selected scheduling state",
    )
    require(
        ordered(
            scrub_advance,
            "++working.completed_cycles",
            "working.cursor_after_content_sha256.clear()",
            "selected = snapshot.entries.begin()",
        )
        and all(
            token in runtime
            for token in (
                "first rotating scrub progress was not durably resumable",
                "same-owner active-scrub witness did not preserve exact process-cache reuse",
                "rotating scrub restart settlement",
                "rotating scrub next cycle",
                "rotating scrub second restart settlement",
                "rotating scrub third cycle",
                "did not settle exact active progress from the stronger complete scan",
                "did not preserve the fair cursor after zero-read settlement",
                "read-only inspection misreported or advanced scrub scheduling evidence",
            )
        ),
        "scrub_progress_is_restart_safe_cyclic_and_one_entry_rollover_live",
        "durable offsets survive owner replacement, a complete restart scan settles stale progress without duplicate byte work, the process throttle prevents hot-loop repetition, and clearing the old cursor before a new cycle prevents active-equals-cursor publication failure",
    )
    require(
        "active_current_bytes_verified" in store
        and all(
            token in process_scrub_retain
            for token in (
                "active_current_bytes_verified",
                "process_scrub_active_observation_matches_state",
                "cache.scrub_active->active_current_bytes_verified",
            )
        )
        and all(
            token in complete_scan
            for token in (
                "exact_process_observation",
                "exact_same_process_scrub_active",
                "active_current_bytes_verified",
                "out.scrub_active_reverified_good = true",
            )
        )
        and all(
            token in runtime
            for token in (
                "max_scrub_bytes_per_attempt = 7U",
                "migrated.scrub_report().hashed_bytes == 0U",
                "migrated.scrub_report().touched_entry_count == 0U",
                "migrated.scrub_report().completed_entry_count == 1U",
                "migrated.scrub_report().reverified_active_completed",
            )
        ),
        "exact_full_byte_active_witness_survives_migration_and_metadata_reuse",
        "the fixed-width process witness distinguishes full current-byte proof from mere Prepared/Progress observation, carries that proof only across exact state and process-generation reuse, and the migration regression proves zero scrub reads after repairing changed payload metadata",
    )
    require(
        all(
            token in store_h + store
            for token in (
                "scrub_active_reverified_good",
                "ReverifiedScrubSettlement::ActiveCompleted",
                "reverified_active_completed",
                "reverified-state publication",
            )
        )
        and "sync_posix_regular_file_snapshot_metadata_matches_status"
        in scrub_advance
        and ordered(
            scrub_advance,
            "snapshot.scrub_active_reverified_good",
            "working.cursor_after_content_sha256 =",
            "clear_payload_scrub_active(working)",
            "ReverifiedScrubSettlement::ActiveCompleted",
        )
        and all(
            token in runtime
            for token in (
                "test_complete_scan_supersedes_stale_active_scrub_checkpoint",
                "stale-active-checkpoint serialization",
                "complete scan did not supersede stale active scrub progress exactly",
                "complete-scan handoff did not durably settle stale active progress",
            )
        ),
        "complete_scan_supersedes_exact_stale_active_checkpoint_without_reread",
        "a fresh authoritative scan hashes the exact active target, the exclusive cutpoint re-proves state-file and payload metadata, and the fair cursor advances without resuming a potentially stale partial SHA checkpoint",
    )
    require(
        all(
            token in store_h + store
            for token in (
                "SyncReplicaFilePayloadStoreIntegrityError",
                "failure_persisted",
                "scrub_failure_reverified_good",
                "persisted the failure witness",
                "matching scrub failure lacked a current full-byte reproof",
                "reverified_active_completed",
                "reverified_failure_cleared",
            )
        )
        and all(
            token in runtime
            for token in (
                "bounded scrub failure witness did not retain exact current evidence",
                "expected_failure_persisted",
                "persisted failure witness granted warm-cache payload authority",
                "current full-byte repair proof was not reused to clear failure without a duplicate read",
            )
        ),
        "failure_witness_forces_current_reproof_and_repair_avoids_duplicate_hashing",
        "checksum-framed failure evidence never grants corruption authority; a current mismatch fails closed, exact persistence is typed, and the complete scanner's repair proof advances state without a second payload read",
    )
    provisioning_main = provisioning_runtime[provisioning_runtime.find("def main()") :]
    convergence_index = provisioning_main.find("wait_for_tree_convergence(")
    provisioning_after_convergence = (
        provisioning_main[convergence_index:] if convergence_index >= 0 else ""
    )
    provision_command_start = provisioning_runtime.find(
        "def direct_provision_command("
    )
    provision_command_end = provisioning_runtime.find(
        "\ndef require_provision_summary(", provision_command_start
    )
    provisioning_command = (
        provisioning_runtime[provision_command_start:provision_command_end]
        if provision_command_start >= 0 and provision_command_end >= 0
        else ""
    )
    require(
        all(
            token in service_process_runtime
            for token in (
                "def wait_for_service_status_socket",
                "process.poll()",
                "socket_path.lstat()",
                "stat.S_ISLNK",
                "stat.S_ISSOCK",
                "mode != 0o600",
                "listener readiness is not a control-plane readiness witness",
            )
        )
        and ordered(
            provisioning_main,
            "wait_for_service_listener(",
            "wait_for_service_status_socket(",
            "wait_for_tree_convergence(",
        )
        and ordered(
            provisioning_after_convergence,
            "wait_for_tree_convergence(",
            "wait_for_service_status_socket(",
            "provisioned source service before owner-only drain",
            '[str(sync), "stop", "--socket", str(source_status)]',
        )
        and all(
            token in provisioning_command
            for token in (
                '"--max-service-runtime-seconds"',
                '"60"',
            )
        )
        and '"30"' not in provisioning_command,
        "provisioning_waits_for_owner_control_plane_not_only_public_listener",
        "the process proof separately establishes startup readiness, retains a bounded 60-second service horizon, and re-proves the non-symbolic 0600 Unix control socket immediately after convergence and before owner-only drain",
    )

    require(
        all(
            token in service_i2p_ingress_runtime
            for token in (
                "maximum_runtime_seconds=8",
                "timeout=15.0",
                "command_deadline_before_pull",
                "blocked direct pull omitted reconciliation result",
                "handshake_complete",
            )
        )
        and ordered(
            i2p_negative_control,
            "maximum_runtime_seconds=8",
            '"--transport", "direct"',
            "timeout=15.0",
            "completed.returncode == 0",
            'value.get("reconciliation")',
            'reconciliation.get("handshake_complete") is True',
        ),
        "i2p_negative_control_requires_connector_evidence_with_qualified_horizon",
        "the bounded native-I2P negative control has measured scheduling margin but still requires an attempted failed reconciliation and rejects any completed direct TLS handshake",
    )

    require(
        "revision_number >= 954" in verifier
        and "src/sync_directory_authority_internal.hpp" in verifier
        and "src/sync_directory_authority.cpp" in verifier
        and "src/sync_atomic_file_publication.cpp" in verifier
        and "src/sync_replica_file_payload_store.hpp" in verifier
        and "src/sync_replica_file_payload_store.cpp" in verifier
        and "src/sync_replica_file_payload_verification_index.hpp" in verifier
        and "src/sync_replica_file_payload_verification_index.cpp" in verifier
        and "tests/sync_replica_file_payload_store_test.cpp" in verifier
        and "tests/sync_replica_file_payload_verification_index_test.cpp" in verifier
        and "tools/audit_sync_file_payload_store.py" in verifier
        and "DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md" in verifier
        and "PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md" in verifier
        and "REVISION_NOTES_rev0894.md" in verifier
        and "DURABLE_PAYLOAD_VERIFICATION_CHECKPOINT_AUDIT_rev0954.md" in verifier
        and "REVISION_NOTES_rev0954.md" in verifier,
        "release_verifier_requires_complete_rev0954_surface",
        "a sealed handoff cannot omit the binary checkpoint leaf, payload integration, focused runtime matrices, or exact nonclaim audit",
    )
    require(
        "revision_number >= 955" in verifier
        and "DURABLE_BYTE_BOUNDED_PAYLOAD_SCRUB_AUDIT_rev0955.md" in verifier
        and "REVISION_NOTES_rev0955.md" in verifier
        and "src/resumable_sha256.hpp" in verifier
        and "src/resumable_sha256.cpp" in verifier
        and "src/sync_replica_file_payload_scrub_state.hpp" in verifier
        and "src/sync_replica_file_payload_scrub_state.cpp" in verifier
        and "src/sync_posix_regular_file_snapshot_codec.hpp" in verifier
        and "src/sync_posix_regular_file_snapshot_codec.cpp" in verifier
        and "tests/resumable_sha256_test.cpp" in verifier
        and "tests/sync_replica_file_payload_scrub_state_test.cpp" in verifier
        and "tools/test_anonsync_service_process.py" in verifier
        and "tools/test_anonsync_service_i2p_ingress.py" in verifier
        and "tools/test_anonsync_provisioning.py" in verifier,
        "release_verifier_requires_complete_rev0955_scrub_surface",
        "a sealed rev0955 handoff cannot omit resumable hashing, the durable state grammar, the shared POSIX metadata codec, focused tests, or the exact authority/nonclaim audit",
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
        all(
            token in checkpoint_design
            for token in (
                "Heart of the mission",
                "Acceleration, not authority",
                "Crash ordering",
                "geometric",
                "ReadOnlyInspect",
                "same-UID",
                "silent corruption",
                "rotating scrub",
                "fs-verity",
                "staged-prefix",
                "Same-process re-verification",
                "Sanitizer graph closure",
            )
        )
        and all(
            token in rev0954_notes
            for token in (
                "durable payload verification checkpoint",
                "restart",
                "staged-prefix",
                "not permanent corruption detection",
                "checkpoint process-cache re-verification immediately",
                "sanitizer final-link closure",
                "36/36",
            )
        ),
        "rev0954_records_authority_costs_integration_bug_and_nonclaims",
        "the handoff names the cold-restart benefit, partial-observer correction, crash sequence, same-UID boundary, and need for periodic content revalidation",
    )

    process_fault_observation = delimited_body(
        store, "struct ProcessIntegrityFaultObservation final", "{", "}"
    )
    process_fault_retain = function_body(
        store, "[[nodiscard]] bool retain_process_integrity_fault("
    )
    require(
        process_fault_observation.count(
            "std::array<char, kSha256HexCharacters>"
        ) == 2
        and "std::string expected_content_sha256"
        not in process_fault_observation
        and "std::string observed_content_sha256"
        not in process_fault_observation
        and all(
            token in process_fault_observation
            for token in (
                "expected_digest() const noexcept",
                "observed_digest() const noexcept",
            )
        )
        and all(
            token in store
            for token in (
                "std::is_trivially_copyable_v<ProcessIntegrityFaultObservation>",
                "std::declval<std::optional<ProcessIntegrityFaultObservation>&>()",
                "copy_exact_lowercase_sha256_hex",
            )
        )
        and "noexcept" in process_fault_retain.split("{", 1)[0]
        and "copy_exact_lowercase_sha256_hex" in process_fault_retain
        and "std::string(" not in process_fault_retain
        and "make_shared" not in process_fault_retain
        and "make_unique" not in process_fault_retain
        and "new " not in process_fault_retain,
        "process_integrity_fault_retention_is_fixed_inline_and_nonthrowing",
        "the fail-closed mismatch witness owns two fixed 64-character digest arrays, optional publication is compile-time nonthrowing, and retention performs no heap-owning construction before or after advancing revocation state",
    )

    scrub_optional_catches = snapshot_body[
        snapshot_body.find(
            "} catch (const SyncReplicaFilePayloadStoreIntegrityError& error)"
        ) :
    ]
    require(
        ordered(
            scrub_advance,
            "finish_hex_array",
            "retain_process_integrity_fault(",
            "verification_cache.scrub_active.reset()",
            "working.observed_content_sha256 = observed",
            "const bool persisted = publish_working(",
            "throw SyncReplicaFilePayloadStoreIntegrityError(",
        )
        and ordered(
            scrub_optional_catches,
            "} catch (...) {",
            "integrity_fault.has_value()",
            "throw;",
            "DeferredAttemptFailure",
        )
        and all(
            token in runtime
            for token in (
                "test_allocation_failure_after_scrub_mismatch_remains_fail_closed",
                "AllocationArm arm(fail_at)",
                "durable_scrub_failure_present",
                "returned_authority_revoked",
                "post_detection_bad_allocations",
                "a post-detection allocation failure was downgraded",
                "persisted mismatch cutpoint",
            )
        )
        and all(
            token in rev0955_notes + scrub_design
            for token in (
                "allocation-free mismatch cutpoint",
                "typed integrity exception",
                "optional scrub deferral",
            )
        ),
        "scrub_mismatch_revocation_precedes_allocation_and_post_alarm_failures_escape",
        "fixed-width finalization and process revocation occur at the exact digest mismatch before durable serialization or typed-error allocation; allocation-fault coverage proves later failures cannot be returned as optional scrub success",
    )

    require(
        all(
            token in store
            for token in (
                "struct ProcessIntegrityFaultObservation final",
                "std::optional<ProcessIntegrityFaultObservation> integrity_fault",
                "integrity_fault_epoch",
                "integrity_fault_epoch_exhausted",
                "most_recent_integrity_fault",
                "issued_integrity_fault_epoch",
                "retain_process_integrity_fault",
                "reject_revoked_snapshot_authority_or_throw",
                "const bool current_bytes_required",
                "process_integrity_fault_reverified_good",
                "process-observed corrupt payload",
                "payload snapshot revoked by process-observed",
                "!cache.integrity_fault.has_value()",
                "Only this complete scan may release the process-local",
                "must not displace an older unresolved",
            )
        )
        and all(
            token in runtime
            for token in (
                "test_process_fault_survives_scrub_record_loss_until_reproof",
                "durable scrub-record loss restored unchanged-metadata authority",
                "a mutation preflight bypassed the process-local integrity fault",
                "cleared process-local integrity evidence continued to force duplicate payload hashing",
                "test_process_fault_permanently_revokes_live_snapshot_authority",
                "a live pre-fault snapshot retained digest authority after corruption",
                "repair resurrected a snapshot that was live when corruption was found",
                "test_process_fault_preserves_original_target_across_second_mismatch",
                "repairing the first-reported mismatch displaced the original unresolved process fault",
                "descriptor-owned readdir order",
            )
        )
        and all(
            token in scrub_design
            for token in (
                "Process-local witness closes the publication-loss gap",
                "record disappeared after the typed error",
                "mutation preflight scans",
                "verification-checkpoint publication is suppressed",
                "current good bytes or proves the digest name absent",
                "Integrity epoch revokes already-issued snapshots",
                "cannot resurrect one that was live",
                "values or references already",
            )
        )
        and all(
            token in rev0955_notes
            for token in (
                "process-local fail-closed mismatch witness",
                "scrub-record loss or failed publication",
                "mutation preflights",
                "suppressed while the witness is live",
                "non-wrapping owner-local integrity epoch",
                "future method call",
                "already-opened payload descriptors",
            )
        ),
        "process_integrity_fault_revokes_old_snapshots_and_survives_durable_record_loss_until_complete_reproof",
        "a same-owner mismatch cannot be forgotten merely because the best-effort durable scrub record is absent; future calls on old snapshots remain permanently rejected while mutation preflights, targeted access, and checkpoint publication stay fail closed until current-byte or absence proof",
    )

    require(
        all(
            token in snapshot_state_gate
            for token in (
                "SyncDirectoryAuthorityAccess",
                "require_current_owner_or_throw",
                "reject_revoked_snapshot_authority_or_throw",
                "durable payload snapshot owner",
            )
        )
        and snapshot_state_gate.find("require_current_owner_or_throw")
        < snapshot_state_gate.find("reject_revoked_snapshot_authority_or_throw")
        and all(
            token in targeted_state_gate
            for token in (
                "SyncDirectoryAuthorityAccess",
                "require_current_owner_or_throw",
                "targeted payload access owner",
            )
        )
        and all(
            token in runtime
            for token in (
                "foreign-thread metadata-only snapshot method read the mutex-free",
                "foreign-thread payload snapshot reached owner-local cache authority",
            )
        )
        and all(
            token in scrub_design
            for token in (
                "intentionally mutex-free owner cache",
                "cheap process/thread-owner proof before",
                "affinity fence, not a mutex",
            )
        )
        and all(
            token in rev0955_notes
            for token in (
                "metadata-only snapshot methods now read the intentionally mutex-free revocation",
                "cheap owner-only proof before any",
                "foreign-thread canonical-digest regression",
            )
        ),
        "mutex_free_revocation_cache_is_thread_gated_before_snapshot_and_targeted_reads",
        "metadata-only snapshots and pass-scoped targeted access must reject foreign-thread use before consulting owner-local revocation state",
    )

    require(
        all(
            token in scrub_design
            for token in (
                "Heart of the mission",
                "Acceleration versus authority",
                "Authority sequence",
                "Byte and entry bounds",
                "Resumable SHA-256 continuation",
                "Temporal scope of a resumed digest",
                "Cyclic fairness and the one-entry rollover defect",
                "Failure witness is not proof",
                "shared fixed",
                "not a point-in-time",
                "ReadOnlyInspect",
                "same-UID",
                "fs-verity",
                "Btrfs scrub",
                "What this proves",
                "What this does not prove",
                "O(total indexed namespace)",
                "garbage collection",
            )
        )
        and all(
            token in rev0955_notes
            for token in (
                "durable byte-bounded rotating payload scrub",
                "4 MiB and four entries",
                "shared POSIX metadata codec",
                "not a point-in-time byte snapshot",
                "one-entry wraparound",
                "failure_persisted=true",
                "without a duplicate scrub read",
                "not hostile same-UID writer defense",
                "coverage-age SLO",
            )
        ),
        "rev0955_records_authority_rollover_bug_research_and_nonclaims",
        "the handoff distinguishes partial scheduling evidence from byte authority, records the corrected one-entry starvation defect, and keeps hostile-writer, latency, retention, and product gaps explicit",
    )

    require(
        "max_integrity_scrub_entries_per_scan" not in store_h
        and "integrity_scrub_cursor" not in store_h
        and "integrity_scrub_cursor" not in store
        and all(
            token in checkpoint_design
            for token in (
                "Rejected entry-count-only scrub experiment",
                "byte-bounded as well as entry-bounded",
                "many gigabytes",
                "persist its exact continuation",
            )
        )
        and "A late entry-count-only scrub experiment was rejected"
        in rev0954_notes,
        "entry_count_only_scrub_experiment_is_excluded_and_nonclaim_bound",
        "the release cannot silently reintroduce the rejected one-entry-per-pass experiment; rev0955 instead requires byte plus entry bounds and durable continuation",
    )

    peer_owner_run = function_body(
        peer_service, "SyncReplicaPeerServiceOwner::run_next_or_throw()"
    )
    integrity_reproof = function_body(
        peer_service, "payload_integrity_reproof_step_or_throw()"
    )
    payload_snapshot_convergence = function_body(
        peer_service, "complete_payload_snapshot_convergence_or_throw("
    )
    operator_recheck = function_body(
        peer_service, "operator_payload_recheck_step_or_throw()"
    )
    peer_ready = function_body(
        peer_service, "SyncReplicaPeerServiceOwner::ready() const"
    )
    initial_repair = function_body(
        peer_service, "repair_step_or_throw("
    )
    scrub_status_body = function_body(
        store, "SyncReplicaFilePayloadStore::scrub_status() const"
    )

    require(
        all(
            token in peer_service_h
            for token in (
                "PayloadIntegrityFaultObserved",
                "PayloadIntegrityReproofBackoffPending",
                "PayloadIntegrityReproofCompleted",
                "SyncReplicaPeerServicePayloadIntegrityFault",
                "SyncReplicaPeerServicePayloadIntegrityRecovery",
                "most_recent_payload_integrity_recovery",
            )
        )
        and peer_owner_run.count(
            "catch (const SyncReplicaFilePayloadStoreIntegrityError& error)"
        ) == 8
        and peer_owner_run.count(
            "catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error)"
        ) == 8
        and all(
            token in peer_owner_run
            for token in (
                "PayloadAuthorityFailureContext::IntegrityReproof",
                "PayloadAuthorityFailureContext::InitialRepair",
                "PayloadAuthorityFailureContext::HealthyRepair",
                "PayloadAuthorityFailureContext::OutboundNetworkStep",
                "PayloadAuthorityFailureContext::InboundNetworkStep",
                "PayloadAuthorityFailureContext::TerminalVerification",
                "PayloadAuthorityFailureContext::SourceManifestProjection",
            )
        )
        and ordered(
            peer_owner_run,
            "if (state_->payload_integrity_fault.has_value())",
            "if (!state_->initial_repair_done)",
            "state_->observe_folder_wake_or_throw()",
        )
        and "catch (...)" not in peer_owner_run,
        "peer_owner_catches_only_typed_integrity_and_short_circuits_ordinary_work",
        "an active payload alarm is a reusable peer-owner state; before filesystem wake, repair, or network scheduling, calls may only back off or reprove, while arbitrary exceptions stay terminal",
    )

    require(
        all(
            token in integrity_reproof
            for token in (
                "payload_integrity_reproof_attempts",
                "snapshot_or_throw()",
                "complete_payload_snapshot_convergence_or_throw",
            )
        )
        and all(
            token in payload_snapshot_convergence
            for token in (
                "run_convergence_pass_with_payload_snapshot_or_throw",
                "most_recent_payload_integrity_recovery",
                "payload_integrity_fault.reset()",
                "payload_integrity_reproof_recoveries",
            )
        )
        and ordered(
            integrity_reproof,
            "snapshot_or_throw()",
            "complete_payload_snapshot_convergence_or_throw",
        )
        and ordered(
            payload_snapshot_convergence,
            "run_convergence_pass_with_payload_snapshot_or_throw",
            "most_recent_payload_integrity_recovery",
            "payload_integrity_fault.reset()",
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "payload after quarantine",
                "most_recent_recovery",
                "integrity recovery erased exact operator evidence",
                "payload-integrity recovery replaced the service process",
            )
        ),
        "integrity_recovery_requires_current_bytes_convergence_and_retains_exact_history",
        "the active alarm survives until a complete payload snapshot and ordinary convergence both succeed; recovery then preserves exact expected/observed evidence under the same process",
    )

    require(
        "!state_->payload_integrity_fault.has_value()" in peer_ready
        and 'if (owner.payload_integrity_fault_active()) return "faulted";'
        in sync_cli
        and "kSyncReplicaPeerServiceMaximumIntegrityBackoffWaitMilliseconds"
        in sync_cli
        and "payload_integrity_retry_wait" in sync_cli
        and "Faulted: payload integrity mismatch" in sync_cli,
        "service_readiness_and_cli_control_plane_fail_closed_during_integrity_alarm",
        "readiness is false while authority is blocked, but the retained CLI loop keeps publishing status and slices retry waits so local drain remains responsive",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_status
            for token in (
                "append_payload_scrub_status",
                "append_payload_integrity_status",
                "active_fault",
                "most_recent_recovery",
                "expected_content_sha256",
                "observed_content_sha256",
                "fault_duration_milliseconds",
                "recovery_age_milliseconds",
                "reverified_active_completed",
                "reverified_failure_cleared",
            )
        )
        and "render_sync_replica_peer_service_status_json" in sync_cli,
        "status_v10_preserves_scan_settlement_scrub_fault_recheck_release_and_recovery_history",
        "one canonical live/terminal renderer distinguishes zero-read active-checkpoint settlement from failure repair while separating scrub scheduling observations, exact-pair active authority failure, and one process-local recovered event",
    )

    require(
        all(
            token in scrub_status_body
            for token in (
                "require_current_owner_or_throw",
                "last_scrub_report",
                "last_completed_cycle_age_milliseconds",
            )
        )
        and all(
            token not in scrub_status_body
            for token in (
                "snapshot_or_throw",
                "openat",
                "acquire_store_lease",
                "verify_or_throw",
                "sha256",
            )
        )
        and "Cheap exact-owner status projection" in store_h,
        "payload_scrub_status_projection_is_owner_gated_and_filesystem_cold",
        "status serialization copies only process-local completed observations after exact-thread proof and cannot become a scan, hash, lease, or scheduling authority",
    )

    require(
        "SyncReplicaTlsSessionIoError" in tls_transport_h + tls_transport
        and "require_session_io_error" in tls_transport_runtime
        and all(
            token in peer_service_h + peer_service
            for token in (
                "OutboundSessionIoFailed",
                "InboundSessionIoFailed",
                "outbound_session_io_failure_step",
                "inbound_session_io_failure_step",
            )
        ),
        "session_io_churn_is_distinct_from_integrity_and_arbitrary_failure",
        "bounded authenticated-session I/O failure becomes an accounted peer-service step while payload mismatch and unrelated exceptions retain separate semantics",
    )

    require(
        all(
            token in service_configuration_runtime
            for token in (
                'wait_for_payload_integrity_state(',
                '"faulted"',
                '"healthy"',
                'faulted_status.get("pid") != source.pid',
                'recovered_status.get("pid") != source.pid',
                '"expected_content_sha256": source_payload_digest',
                '"observed_content_sha256": corrupted_payload_digest',
                'payload_integrity_recovery_expected=True',
            )
        )
        and "mode-0600" in service_recovery_design
        and "same PID" in service_recovery_design,
        "shipping_process_regresses_exact_fault_same_pid_repair_history_and_drain",
        "the configured product service corrupts a real digest object, remains inspectable, re-proves repaired bytes, retains exact recovery evidence, and drains through the same owner-only socket",
    )

    require(
        all(
            token in service_recovery_design
            for token in (
                "Heart of the mission",
                "Owner-level state machine",
                "Current-byte reproof",
                "Operator projection",
                "Research-informed comparison",
                "What this proves",
                "What this does not prove",
                "duplicate",
                "systemd",
                "sole-copy",
            )
        )
        and all(
            token in rev0956_notes
            for token in (
                "same-process recovery state",
                "most_recent_recovery",
                "process-local",
                "systemd `READY=1`",
                "namespace",
                "No quarantine",
            )
        )
        and all(
            token in verifier
            for token in (
                "PAYLOAD_INTEGRITY_SERVICE_RECOVERY_AUDIT_rev0956.md",
                "REVISION_NOTES_rev0956.md",
                "src/sync_replica_peer_service.cpp",
                "tools/test_anonsync_service_configuration_status.py",
            )
        ),
        "rev0956_records_recovery_authority_waste_nonclaims_and_release_binding",
        "the handoff documents typed-only owner recovery, exact evidence retention, systemd readiness limits, duplicate recovery I/O, sole-copy constraints, and verifier inclusion",
    )

    exact_origin = function_body(
        store,
        "SyncReplicaFilePayloadStore::require_exact_snapshot_origin_or_throw(",
    )
    normal_convergence_entry = function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::run_convergence_pass_or_throw(",
    )
    handoff_convergence_entry = function_body(
        folder_scan,
        "run_convergence_pass_with_payload_snapshot_or_throw(",
    )
    convergence_impl = function_body(
        folder_scan,
        "SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw(",
    )
    evidence_merge = function_body(
        peer_evidence_h,
        "merge_sync_replica_peer_service_payload_integrity_evidence(",
    )
    fault_record = function_body(
        peer_service, "record_payload_integrity_evidence_or_throw("
    )

    require(
        all(
            token in exact_origin
            for token in (
                "snapshot.require_state_or_throw",
                "state_->root_authority.verify_or_throw",
                "candidate.root_authority.verify_or_throw",
                "candidate.verification_cache.get() !=",
                "state_->verification_cache.get()",
                "candidate.folder_id != state_->folder_id",
                "candidate.root_path != state_->root_path",
                "candidate.root_attestation_digest !=",
                "candidate.limits != state_->limits",
                "exact retained store owner",
            )
        )
        and "friend class SyncReplicaFolderScanOwner" in store_h,
        "payload_snapshot_handoff_requires_exact_live_store_origin",
        "same durable identity is insufficient; the candidate must remain valid under its issuing epoch and share the retained process verification cache plus exact structural fields",
    )

    require(
        "run_convergence_pass_impl_or_throw(limits, std::nullopt)"
        in normal_convergence_entry
        and "run_convergence_pass_impl_or_throw(" in handoff_convergence_entry
        and "std::move(retained)" in handoff_convergence_entry
        and folder_scan.count(
            "SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw("
        ) == 1
        and "run_convergence_pass_with_payload_snapshot_or_throw" in folder_process_h
        and "std::move(payload_snapshot)" in folder_process,
        "ordinary_and_handoff_entries_share_one_convergence_implementation",
        "recovery supplies one complete cutpoint to the ordinary algorithm instead of forking catalog, filesystem, replica, or settlement semantics",
    )

    require(
        ordered(
            convergence_impl,
            "require_exact_snapshot_origin_or_throw",
            "report.payload_snapshot_handoff_count = 1U",
            "observe_payload_snapshot_or_throw",
            "SyncReplicaFolderCatalogSnapshot catalog_hints = snapshot_or_throw()",
        )
        and convergence_impl.count(
            "state_->payload_store->snapshot_or_throw()"
        ) == 1
        and convergence_impl.count("observe_payload_snapshot_or_throw()") >= 2
        and all(
            token in folder_scan_h
            for token in (
                "payload_snapshot_handoff_count",
                "payload_snapshot_handoff_entry_count",
                "payload_snapshot_observation_count",
                "payload_snapshot_observed_entry_count",
            )
        ),
        "handoff_is_validated_before_effects_and_all_complete_observations_are_counted",
        "foreign or revoked evidence fails before catalog/replica work, while every convergence-owned complete payload snapshot flows through one accounting wrapper",
    )

    require(
        all(
            token in integrity_reproof + payload_snapshot_convergence
            for token in (
                "SyncReplicaFilePayloadStoreSnapshot payload_reproof",
                "run_convergence_pass_with_payload_snapshot_or_throw",
                "payload_integrity_reproof_snapshot_handoffs",
                "payload_integrity_reproof_convergence_snapshot_observations",
                "payload_integrity_reproof_convergence_mutation_full_scans",
            )
        )
        and ordered(
            integrity_reproof,
            "snapshot_or_throw()",
            "complete_payload_snapshot_convergence_or_throw",
        )
        and ordered(
            payload_snapshot_convergence,
            "run_convergence_pass_with_payload_snapshot_or_throw",
            "refresh_ingress_worker(false)",
            "most_recent_payload_integrity_recovery",
            "payload_integrity_fault.reset()",
        )
        and "(void)folder_process.payload_store_or_throw().snapshot_or_throw();"
        not in integrity_reproof + payload_snapshot_convergence,
        "service_recovery_moves_current_byte_proof_and_accounts_both_rescan_routes",
        "the required complete reproof is consumed once, and both a convergence-owned snapshot and a fallback mutation full scan remain independently visible",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "test_complete_payload_reproof_handoff_requires_exact_store_owner",
                "begin_mutation_batch_or_throw",
                '"lease is busy"',
                "run_convergence_pass_with_payload_snapshot_or_throw",
                "payload_snapshot_observation_count == 0U",
                "payload_mutation_full_scan_count == 0U",
                "foreign_handle",
                '"exact retained store owner"',
                "catalog_before_rejection",
                "replica_before_rejection",
            )
        ),
        "exclusive_lease_and_foreign_owner_regressions_are_hard_handoff_oracles",
        "successful convergence while a second snapshot is mechanically excluded proves actual handoff consumption; a same-root foreign handle is rejected without durable effects",
    )

    require(
        'if (report.payload_mutation_put_count != 0U)' in convergence_impl
        and 'if (report.payload_mutation_inserted_count != 0U)'
        not in convergence_impl
        and 'AlreadyPresent' in convergence_impl
        and ordered(
            convergence_impl,
            'release_payload_batch();',
            'if (report.payload_mutation_put_count != 0U)',
            'payload_cutpoint.reset();',
            'require_targeted_remote_payload_access',
        ),
        'payload_cutpoint_freshness_follows_any_mutation_put',
        'a frozen complete inventory is discarded after Inserted or AlreadyPresent mutation work before remote presence planning',
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                'test_payload_handoff_cutpoint_invalidates_after_already_present_put',
                'stale_handoff.entry_count() == 0U',
                'payload_mutation_put_count == 1U',
                'payload_mutation_inserted_count == 0U',
                'payload_mutation_already_present_count == 1U',
                'remote_targeted_payload_access_count == 1U',
                'remote_targeted_payload_selection_count == 1U',
                'deferred_remote_payload_candidate_count == 0U',
                'remote planning trusted a historical payload inventory',
            )
        ),
        'already_present_append_regression_proves_same_pass_targeted_fallback',
        'the runtime fixture freezes a pre-append handoff and requires exact targeted remote publication after the mutation owner discovers the digest as AlreadyPresent',
    )

    require(
        all(
            token in sync_cli + folder_cli + peer_status
            for token in (
                "payload_snapshot_handoffs",
                "payload_snapshot_handoff_entries",
                "payload_snapshot_observations",
                "payload_snapshot_observed_entries",
            )
        )
        and all(
            token in peer_service_h + peer_status + sync_cli
            for token in (
                "payload_integrity_reproof_snapshot_handoffs",
                "payload_integrity_reproof_convergence_snapshot_observations",
                "payload_integrity_reproof_convergence_mutation_full_scans",
            )
        )
        and all(
            token in peer_service_h + peer_status + sync_cli
            for token in (
                "payload_recheck_snapshot_handoffs",
                "payload_recheck_convergence_snapshot_observations",
                "payload_recheck_convergence_mutation_full_scans",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                '"payload_recheck_snapshot_handoffs"',
                '"payload_recheck_convergence_snapshot_observations"',
                '"payload_recheck_convergence_mutation_full_scans"',
            )
        )
        and "render_sync_replica_peer_service_payload_recheck_status_json"
        in peer_status_h
        and "render_sync_replica_peer_service_payload_recheck_status_json"
        in peer_status
        and "render_sync_replica_peer_service_payload_recheck_status_json"
        in sync_cli,
        "shipping_status_distinguishes_handoff_observation_and_mutation_full_scan",
        "live, terminal, and one-shot surfaces expose enough accounting to detect either form of duplicate complete recovery scan",
    )

    require(
        all(
            token in evidence_merge
            for token in (
                "NewExpectedContent",
                "RepeatedExactObservation",
                "ChangedObservedContent",
                "active.failure_persisted || failure_persisted",
                "active.failure_persisted = failure_persisted",
                "observed_content_change_count",
            )
        )
        and all(
            token in fault_record
            for token in (
                "merge_sync_replica_peer_service_payload_integrity_evidence",
                "active.evidence",
                "evidence.detection_count",
            )
        )
        and all(
            token in peer_evidence_runtime
            for token in (
                "test_exact_pair_persistence_and_change_accounting",
                "returning to an earlier byte image",
                "different expected payload",
                "test_counters_saturate",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "payload integrity second corruption injection",
                "minimum_observed_content_change_count=1",
                "changed corrupt bytes inherited a durable witness",
                'active_fault.get("failure_persisted") is not False',
            )
        ),
        "durable_failure_presentation_is_scoped_to_exact_observed_byte_image",
        "persistence may accumulate only for an identical expected/observed pair; changed corrupt bytes reset that claim and increment a saturating transition counter",
    )

    require(
        all(
            token in evidence_merge
            for token in (
                "std::string_view expected_content_sha256",
                "std::string_view observed_content_sha256",
                "std::string replacement_observed_content",
                "active.observed_content_sha256 == observed_content_sha256",
            )
        )
        and ordered(
            evidence_merge,
            "if (active.observed_content_sha256 == observed_content_sha256)",
            "RepeatedExactObservation",
            "std::string replacement_observed_content",
            "active.observed_content_sha256 =",
            "active.failure_persisted = failure_persisted",
            "active.observed_content_change_count",
        )
        and "std::optional<SyncReplicaPeerServicePayloadIntegrityEvidence>\n"
            "            evidence" not in fault_record
        and "evidence.emplace(payload_integrity_fault->evidence)"
            not in fault_record
        and all(
            token in peer_evidence_runtime
            for token in (
                "test_repeated_exact_merge_retains_digest_storage",
                "active.expected_content_sha256.data() == expected_storage",
                "active.observed_content_sha256.data() == observed_storage",
                "repeated exact evidence rebuilt digest storage",
            )
        )
        and "std::string_view" in reproof_handoff_design
        and "Repeated reports of the exact same digest pair" in rev0957_notes,
        "exact_pair_evidence_merge_avoids_repeated_digest_cloning",
        "exact repeated alarms retain both digest allocations; transition strings are constructed before pair-scoped counters or persistence evidence change",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "observed_content_change_count" in peer_service_h
        and peer_status.count("observed_content_change_count") >= 2
        and '"anonsync.peer-service.status.v26"'
        in service_configuration_runtime
        and '"anonsync.peer-service.status.v26"'
        in service_i2p_ingress_runtime,
        "status_v10_binds_checkpoint_recheck_quarantine_inventory_and_all_process_oracles",
        "the schema change prevents older clients or tests from silently missing zero-read active-checkpoint settlement or interpreting pair-scoped persistence as rev0956 target-scoped evidence",
    )

    require(
        peer_owner_run.count("refresh_ingress_worker(false)") >= 1
        and payload_snapshot_convergence.count(
            "refresh_ingress_worker(false)"
        ) >= 1
        and ordered(
            payload_snapshot_convergence,
            "run_convergence_pass_with_payload_snapshot_or_throw",
            "refresh_ingress_worker(false)",
            "payload_integrity_fault.reset()",
        )
        and "capability-free worker" in peer_service,
        "native_i2p_readiness_is_refreshed_while_faulted_and_at_recovery_cutpoint",
        "asynchronous ingress publication cannot leave readiness restored from a stale pre-fault worker snapshot, and no ingress event preempts fail-closed recovery",
    )

    require(
        all(
            token in reproof_handoff_design
            for token in (
                "Heart of the mission",
                "One convergence algorithm",
                "durable identity equality is insufficient",
                "Mechanical no-second-scan oracle",
                "Adjacent cutpoint-freshness audit",
                "AlreadyPresent",
                "Adjacent evidence audit",
                "Research-informed comparison",
                "What this proves",
                "What this does not prove",
            )
        )
        and all(
            token in rev0957_notes
            for token in (
                "move-only complete payload-snapshot handoff",
                "exact-origin composition fence",
                "false-absence defect",
                "failure_persisted",
                "status.v4",
                "native-I2P",
                "Nonclaims",
            )
        )
        and all(
            token in verifier
            for token in (
                "PAYLOAD_REPROOF_HANDOFF_AND_EXACT_OWNER_AUDIT_rev0957.md",
                "REVISION_NOTES_rev0957.md",
                "src/sync_replica_peer_service_integrity_evidence.hpp",
                "tests/sync_replica_peer_service_integrity_evidence_test.cpp",
            )
        ),
        "rev0957_records_authority_waste_evidence_correction_nonclaims_and_release_binding",
        "the release documents exact-owner cutpoint reuse, hard mechanical proof, pair-scoped evidence, asynchronous readiness, research precedents, and explicit product gaps",
    )


    require(
        all(
            token in scrub_state_h
            for token in (
                "Idle = 1",
                "Progress = 2",
                "IntegrityFailure = 3",
                "Prepared = 4",
                "Durable write-ahead intent",
                "Prepared/Progress/IntegrityFailure only",
            )
        )
        and all(
            token in scrub_state_validate
            for token in (
                "SyncReplicaFilePayloadScrubStateDisposition::Prepared",
                "state.active_offset_bytes != 0U",
                "state.active_hash != initial_hash_checkpoint()",
                "prepared form is not at the initial cutpoint",
                "prepared form contains a terminal digest",
            )
        )
        and all(
            token in scrub_state_runtime
            for token in (
                "test_prepared_round_trip",
                "prepared scrub-state round trip changed fields",
                "prepared state with consumed bytes was accepted",
                "prepared state retained a terminal digest",
            )
        ),
        "prepared_scrub_state_is_canonical_zero_offset_write_ahead_intent",
        "the fixed-width state format retains prior encodings and admits exactly one zero-byte-progress active form before a newly selected payload read",
    )

    require(
        "std::optional<SyncPosixRegularFileSnapshotMetadata>" in scrub_publish
        and all(
            token in scrub_publish
            for token in (
                "observe_exact_committed",
                "observe_scrub_state_file_or_throw",
                "committed-state lease cutpoint",
                "*observed.state != desired",
                "return observed.metadata",
                "return observe_exact_committed()",
                "return std::nullopt",
                "equal to desired authorizes the caller to read payload bytes",
            )
        )
        and ordered(
            scrub_publish,
            "serialize_sync_replica_file_payload_scrub_state_or_throw",
            "prepublication lease cutpoint",
            "write_sync_file_atomically_",
            "postpublication lease cutpoint",
            "return observe_exact_committed()",
        ),
        "scrub_publication_returns_exact_reobserved_committed_metadata",
        "normal publication and rename-cutpoint reconciliation authorize later byte reads only after exact parsed state and state-file metadata are observed under the live lease",
    )

    require(
        all(
            token in scrub_advance
            for token in (
                "const auto publish_working",
                "next_scrub_generation_or_throw",
                "publish_payload_scrub_state_with_reconciliation",
                "note_process_scrub_state_observation",
                "write-ahead intent publication",
                "DeferredPublicationFailure",
                "open_store_file_or_throw",
                "::pread(",
            )
        )
        and ordered(
            scrub_advance,
            "SyncReplicaFilePayloadScrubStateDisposition::Prepared",
            "working.active_offset_bytes = 0U",
            "working.active_hash = ResumableSha256{}.checkpoint()",
            "write-ahead intent publication",
            "active = &*selected",
            "open_store_file_or_throw",
            "::pread(",
        ),
        "new_scrub_target_commits_prepared_before_open_or_read",
        "a selected digest cannot cross its first open or pread unless its exact Prepared record was committed and re-observed; uncertain publication returns a bounded deferral",
    )

    require(
        all(
            token in store
            for token in (
                "struct ProcessScrubActiveObservation final",
                "std::is_trivially_copyable_v<ProcessScrubActiveObservation>",
                "std::optional<ProcessScrubActiveObservation> scrub_active",
                "state_generation",
                "scrub_state_metadata",
                "retain_process_scrub_active_observation",
                "process_scrub_active_observation_matches",
            )
        )
        and "std::string " not in function_body(
            store, "struct ProcessScrubActiveObservation final"
        )
        and all(
            token in process_scrub_retain
            for token in (
                "copy_exact_lowercase_sha256_hex",
                "observation.state_generation = state.generation",
                "observation.scrub_state_metadata = state_metadata",
                "cache.scrub_active = observation",
            )
        )
        and all(
            token in process_scrub_match
            for token in (
                "observation.active_digest() == state.active_content_sha256",
                "observation.state_generation == state.generation",
                "observation.disposition == state.disposition",
                "observation.active_metadata == state.active_metadata",
                "observation.active_offset_bytes == state.active_offset_bytes",
                "observation.active_hash == state.active_hash",
                "observation.scrub_state_metadata == state_metadata",
            )
        )
        and "process_scrub_active_observation_matches_state"
        in process_scrub_match_wrapper,
        "same_process_active_scrub_reuse_is_fixed_width_and_exact_state_file_bound",
        "only an owner with an exact active-state observation plus its own commit or a complete current-byte scan may retain process-cache acceleration",
    )

    active_scan_fragment = complete_scan[
        complete_scan.find("const bool scrub_active_targets_payload") :
        complete_scan.find("const bool process_integrity_fault_targets_payload")
    ]
    require(
        all(
            token in active_scan_fragment
            for token in (
                "scrub_active_targets_payload",
                "exact_same_process_scrub_active",
                "process_scrub_active_observation_matches",
            )
        )
        and all(
            token in complete_scan
            for token in (
                "Prepared/Progress is a write-ahead crash witness",
                "(!scrub_active_targets_payload ||",
                "exact_same_process_scrub_active",
                "!scrub_active_targets_payload &&",
            )
        )
        and ordered(
            complete_scan,
            "const bool scrub_active_targets_payload",
            "const bool exact_same_process_scrub_active",
            "const bool exact_process_observation",
            "const bool exact_durable_observation",
        ),
        "active_scrub_state_forbids_durable_reuse_and_fresh_process_cache_reuse",
        "Prepared/Progress forces current-byte hashing after restart; only a process that has since proved the exact active observation may reuse its process generation",
    )

    damaged_scrub_runtime = function_body(
        runtime,
        "void test_present_unusable_scrub_state_revokes_restart_acceleration()",
    )
    require(
        all(
            token in complete_scan
            for token in (
                "const bool unusable_scrub_state_requires_current_bytes",
                "scrub_state.present && !scrub_state.usable",
                "unusable_scrub_state_requires_current_bytes ||",
                "const bool current_bytes_required",
                "!current_bytes_required &&",
                "damaged active intent whose target can no longer be recovered",
            )
        )
        and ordered(
            complete_scan,
            "const bool unusable_scrub_state_requires_current_bytes",
            "const bool current_bytes_required",
            "const bool exact_process_observation",
            "const bool exact_durable_observation",
            "stream_hash_regular_file_or_throw",
        )
        and all(
            token in damaged_scrub_runtime
            for token in (
                "checksum-invalid scrub intent trusted forged restart metadata",
                "limits.max_scrub_bytes_per_attempt = 1U",
                "forged_index.entries.front().metadata = private_file_metadata",
                "sync_replica_file_payload_scrub_state_exact_bytes",
                "require_integrity_error",
                "expected_digest",
                "observed_digest",
                "snapshot.scan_hashed_entry_count() == 1U",
                "snapshot.scan_reused_entry_count() == 0U",
                "snapshot.scan_durable_reused_entry_count() == 0U",
                "snapshot.scrub_report().state_rebuilt",
                "snapshot.scrub_report().hashed_bytes == 1U",
            )
        )
        and all(
            token in minimum_reader_design
            for token in (
                "damaged intent is not absence",
                "present && !usable",
                "namespace-wide current-byte requirement",
                "one byte",
            )
        )
        and all(
            token in rev0959_notes
            for token in (
                "Damaged write-ahead intent remains a restart fence",
                "checksum-invalid scrub-state file",
                "every digest-named payload",
                "same-size corrupt bytes",
            )
        ),
        "present_unusable_scrub_state_revokes_complete_scan_acceleration",
        "a checksum-invalid fixed-size scrub record is not clean absence: because damaged Prepared/Progress cannot identify one target, every payload in the complete authority-producing scan hashes current bytes before process or durable restart metadata may be trusted; the focused regression makes the optional scrub budget too small to explain detection",
    )

    disabled_settlement_runtime = function_body(
        runtime,
        "void test_disabled_scrub_settles_damaged_restart_fence_once()",
    )
    snapshot_owner = function_body(
        store,
        "SyncReplicaFilePayloadStore::snapshot_with_reuse_policy_or_throw(",
    )
    require(
        all(
            token in scrub_advance
            for token in (
                "const bool scrub_enabled = payload_scrub_enabled(limits)",
                "Disabling bounded scrub reads does not authorize",
                "disabled restart-fence settlement publication",
                "if (!scrub_enabled)",
                "SyncReplicaFilePayloadStoreScrubDisposition::Disabled",
            )
        )
        and all(
            token in snapshot_owner
            for token in (
                "disabled_restart_fence_requires_settlement",
                "prior_state->disposition !=",
                "SyncReplicaFilePayloadScrubStateDisposition::Idle",
                "Disabling bounded scrub reads must not",
                "(!scrub_enabled &&",
            )
        )
        and all(
            token in disabled_settlement_runtime
            for token in (
                "test_disabled_scrub_settles_damaged_restart_fence_once",
                "disabled.max_scrub_bytes_per_attempt = 0U",
                "disabled.max_scrub_entries_per_attempt = 0U",
                "snapshot.scan_hashed_entry_count() == 1U",
                "snapshot.scrub_report().state_rebuilt",
                "snapshot.scrub_report().hashed_bytes == 0U",
                "snapshot.scan_hashed_entry_count() == 0U",
                "snapshot.scan_durable_reused_entry_count() == 1U",
                "disabled scrub repeated the complete restart-fence reproof",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "Setting both scrub work limits to zero",
                "metadata-only canonical settlement",
                "does not advance the process-local",
                "leave the restart fence intact",
            )
        )
        and all(
            token in rev0959_notes
            for token in (
                "Configuring both bounded scrub limits to zero",
                "canonical metadata-only state",
                "does not consume the",
                "preserves the conservative restart fence",
            )
        )
        and all(
            token in minimum_reader_design
            for token in (
                "mandatory metadata-only restart-fence settlement",
                "process-local scrub throttle is not advanced",
                "exact durable-index reuse",
                "immediately retryable",
            )
        ),
        "disabled_scrub_settles_restart_fence_without_repeated_payload_reads",
        "max_scrub_* equal to zero disables bounded byte work but not metadata-only repair of damaged or non-idle write-ahead state; one complete scan settles the fence and the next fresh owner reuses the durable verification checkpoint",
    )

    require(
        ordered(
            snapshot_owner,
            "const bool scrub_enabled = payload_scrub_enabled(store.limits)",
            "disabled_restart_fence_requires_settlement",
            "if (scrub_enabled && now < store.next_scrub_not_before)",
            "if (scrub_enabled)",
            "store.next_scrub_not_before =",
            "advance_payload_scrub_from_snapshot_or_throw(",
        )
        and "store.next_scrub_not_before =" not in scrub_advance,
        "disabled_restart_fence_settlement_does_not_consume_scrub_throttle",
        "metadata-only repair remains immediately retryable after contention or publication failure because zero-budget settlement never advances the bounded byte-scrub deadline",
    )

    require(
        ordered(
            scrub_advance,
            "finish_hex_array",
            "retain_process_integrity_fault(",
            "verification_cache.scrub_active.reset()",
            "working.disposition =",
            "IntegrityFailure",
            "working.observed_content_sha256 = observed",
            "const bool persisted = publish_working(",
            "throw SyncReplicaFilePayloadStoreIntegrityError(",
        )
        and "already committed Prepared/Progress state remains a durable" in scrub_advance,
        "scrub_mismatch_clears_active_acceleration_after_fixed_width_revocation",
        "once current bytes contradict their digest, no active-state acceleration survives and terminal allocation/publication cannot erase the durable restart fence",
    )

    require(
        all(
            token in runtime
            for token in (
                "test_prepared_scrub_state_forces_restart_reproof_before_blocked_optional_attempt",
                "prepared-restart-fence",
                "durable Prepared intent did not force restart current-byte reproof",
                "restart reproof mutated the write-ahead intent before optional scrub authority was available",
                "LOCK_SH",
            )
        )
        and all(
            token in runtime
            for token in (
                "scan_hashed_entry_count() == 0U",
                "scan_process_reused_entry_count() == 1U",
                "scan_durable_reused_entry_count() == 0U",
                "require_integrity_error",
            )
        ),
        "compiled_regressions_mechanically_separate_shared_scan_from_blocked_optional_scrub",
        "a child shared lease permits the complete scanner but blocks the exclusive scrub, proving fresh-process detection is caused by the restart fence rather than by an immediate retry",
    )

    require(
        all(
            token in runtime
            for token in (
                "test_minimum_reader_identity_migration_is_cold_atomic_and_inode_preserving",
                "minimum-reader-migration-contention",
                "read-only inspection silently migrated the legacy reader marker",
                "minimum-reader migration trusted stale restart metadata",
                "minimum-reader migration did not preserve the exact lock inode",
                "post-migration snapshot or scrub repeated or weakened the cold byte proof",
                "migrated.scrub_report().reverified_active_completed",
                "post-migration durable checkpoint was not rebound to the new identity",
                "product-bound minimum-reader migration changed identity or authority",
                "coexisting current and legacy-reader",
                "LOCK_SH",
            )
        )
        and all(
            token in runtime
            for token in (
                "scan_hashed_entry_count() == 0U",
                "scan_process_reused_entry_count() == 1U",
                "scan_durable_reused_entry_count() == 1U",
                "private_file_identity(current_identity) == legacy_identity_inode",
            )
        ),
        "compiled_migration_regressions_cover_cold_corruption_lock_inode_handoff_and_conflict",
        "the focused executable builds the stale-index plus Prepared downgrade hazard, blocks migration with a child flock, preserves the inode, rebinds repaired active metadata and settles scrub with zero reads, proves restart reuse, and rejects same-family and cross-family coexisting generations",
    )

    payload_fault_injection_start = service_configuration_runtime.find(
        "def overwrite_payload_under_exclusive_store_lease("
    )
    payload_fault_injection_end = service_configuration_runtime.find(
        "\ndef ", payload_fault_injection_start + 1
    )
    payload_fault_injection = (
        service_configuration_runtime[
            payload_fault_injection_start:payload_fault_injection_end
        ]
        if payload_fault_injection_start >= 0 and payload_fault_injection_end >= 0
        else ""
    )
    require(
        all(
            token in payload_fault_injection
            for token in (
                "PRODUCT_PAYLOAD_STORE_IDENTITY_BASENAME",
                "O_NOFOLLOW",
                "opened.st_dev != named.st_dev",
                "opened.st_ino != named.st_ino",
                "opened.st_nlink != 1",
                "fcntl.LOCK_EX | fcntl.LOCK_NB",
                "overwrite_regular_file(path, value, label)",
                "identity anchor changed while exclusively leased",
            )
        )
        and service_configuration_runtime.count(
            "overwrite_payload_under_exclusive_store_lease("
        ) == 3
        and service_configuration_runtime.count("overwrite_regular_file(") == 3,
        "configured_service_fault_injection_holds_exact_store_exclusive_lease",
        "the process regression serializes both deliberate corrupt-payload mutations against shared authority scans through the exact reader-fenced identity inode rather than depending on compiler speed",
    )

    require(
        all(
            token in cmake
            for token in (
                "set(ANONSYNC_FOLDER_SCAN_OWNER_TEST_TIMEOUT_SECONDS 60)",
                "if(ANONSYNC_ENABLE_SANITIZERS)",
                "set(ANONSYNC_FOLDER_SCAN_OWNER_TEST_TIMEOUT_SECONDS 120)",
                "TIMEOUT ${ANONSYNC_FOLDER_SCAN_OWNER_TEST_TIMEOUT_SECONDS}",
            )
        ),
        "folder_owner_timeout_distinguishes_ordinary_and_sanitizer_cost",
        "ordinary CTest supervision retains its sixty-second stall detector while the explicitly instrumented build receives a bounded 120-second horizon",
    )

    complete_scan_owner = function_body(
        store,
        "[[nodiscard]] ScannedPayloadIndex scan_store_under_lease_or_throw(",
    )
    require(
        all(
            token in store
            for token in (
                "kMaximumCompleteScanObservationAttempts = 2U",
                "class PayloadStoreObservationStaleError final",
                "became truncated while read",
                "changed between namespace inspection and open",
                "verification index changed during namespace traversal",
                "scrub state changed during namespace traversal",
                "payload root changed while its index was scanned",
            )
        )
        and store.count("throw PayloadStoreObservationStaleError") >= 12
        and ordered(
            complete_scan_owner,
            "ScannedPayloadIndex out;",
            "for (std::uint32_t attempt = 0U;; ++attempt)",
            "scan_store_namespace_or_throw(",
            "catch (const PayloadStoreObservationStaleError&)",
            "stale-observation lease proof",
            "kMaximumCompleteScanObservationAttempts",
            "Allocate the replacement before the final authority cutpoint",
            "publish_verification_generation(",
        ),
        "complete_scan_retries_one_typed_stale_observation_before_authority",
        "only exact observation drift is restartable; one fresh cursor retry occurs under an exact re-proved lease before verification, checkpoint, scrub, or snapshot authority can publish",
    )

    stale_observation_runtime = function_body(
        runtime,
        "void test_complete_scan_restarts_one_stale_payload_observation()",
    )
    require(
        all(
            token in stale_observation_runtime
            for token in (
                "inotify_init1(IN_CLOEXEC | IN_NONBLOCK)",
                "IN_ACCESS",
                "32U * 1024U * 1024U",
                "write_byte_without_sync(changed)",
                "write_byte_without_sync(original)",
                "snapshot.scan_hashed_entry_count() == 1U",
                "snapshot.scan_reused_entry_count() == 0U",
                "read_file_bytes(payload_path) == payload",
            )
        )
        and "#if defined(__linux__)" in runtime
        and all(
            token in readme
            for token in (
                "restart once from a fresh",
                "observation remains terminal",
                "discarded attempt grants no authority",
            )
        )
        and all(
            token in rev0959_notes
            for token in (
                "Bounded stale-observation recovery",
                "retry count is fixed at one",
                "verification generation, checkpoint observation",
            )
        )
        and all(
            token in minimum_reader_design
            for token in (
                "One stale complete observation is restartable",
                "exactly two total attempts",
                "cannot grant content authority",
            )
        ),
        "compiled_stale_observation_regression_crosses_read_cutpoint_and_rehashes",
        "the Linux fixture mutates and restores one byte after the first payload read, proving a stale complete attempt is discarded and the fresh exact snapshot performs one full hash with no reuse",
    )

    lease_busy_step = function_body(
        peer_service,
        "payload_store_lease_busy_step(",
    )
    lease_backoff_step = function_body(
        peer_service,
        "payload_store_lease_backoff_step()",
    )
    unknown_network_outcome_fence = function_body(
        peer_service,
        "apply_unknown_network_outcome_fence_or_throw(",
    )
    require(
        all(
            token in peer_service_h
            for token in (
                "kSyncReplicaPeerServiceMaximumPayloadStoreLeaseBackoffWaitMilliseconds",
                "PayloadStoreLeaseBusyDeferred = 16U",
                "payload_store_lease_retry_delay_milliseconds",
                "payload_store_lease_busy_deferrals",
                "payload_store_lease_backoff_deferrals",
                "payload_store_lease_conflict_observed",
            )
        )
        and all(
            token in lease_busy_step
            for token in (
                "next_payload_store_lease_retry_at = add_milliseconds_or_throw",
                "limits.retry_initial_milliseconds",
                "next_repair_at = next_payload_store_lease_retry_at",
                "state_preserving_deferral_step(",
                "PayloadStoreLeaseBusyDeferred",
                "payload_store_lease_conflict_observed = true",
                "apply_unknown_network_outcome_fence_or_throw",
                "increment_saturating(counters.steps)",
                "increment_saturating(counters.payload_store_lease_busy_deferrals)",
                "separately committed catalog/replica",
                "bounded convergence",
            )
        )
        and peer_owner_run.count(
            "catch (const SyncReplicaFilePayloadStoreLeaseBusyError& error)"
        ) == 8
        and peer_owner_run.count(
            "return state_->payload_store_lease_busy_step("
        ) == 8,
        "peer_service_retains_typed_cooperative_store_lease_contention",
        "each explicit owner phase maps only the typed nonblocking payload-store refusal to a retained step, installs one real retry cutpoint, and schedules bounded convergence without claiming cross-owner rollback",
    )

    require(
        all(
            token in peer_service
            for token in (
                "next_payload_store_lease_retry_at",
                "payload_store_lease_backoff_step()",
                "local_payload_retry_pending",
                "!local_payload_retry_pending && state_->filesystem_wake_pending",
                "!local_payload_retry_pending && now >= state_->next_repair_at",
            )
        )
        and all(
            token in lease_backoff_step
            for token in (
                "PayloadStoreLeaseBusyDeferred",
                "remaining_milliseconds(",
                "next_payload_store_lease_retry_at",
                "payload_store_lease_backoff_deferrals",
            )
        )
        and ordered(
            peer_owner_run,
            "if (state_->payload_integrity_fault.has_value())",
            "now < state_->next_payload_store_lease_retry_at",
            "if (!state_->initial_repair_done)",
            "state_->observe_folder_wake_or_throw()",
            "const bool local_payload_retry_pending",
        ),
        "lease_retry_gate_prevents_hot_flock_loop_and_local_repair_starvation",
        "initial/faulted owners return clock-only deferrals, while an established healthy owner gates local repair until the exact retry cutpoint and remains available for bounded inbound work",
    )

    require(
        all(
            token in peer_service_h
            for token in (
                "network_outcome_known",
                "payload_store_lease_conflict_observed",
                "payload_authority_network_outcome_uncertain_steps",
            )
        )
        and all(
            token in unknown_network_outcome_fence
            for token in (
                "network_outcome_is_unknown(context)",
                "result.network_outcome_known = false",
                "payload_authority_network_outcome_uncertain_steps",
                "successful_handoff_lease_milliseconds(limits)",
                "unknown outbound outcome turn fence",
                "role = SyncReplicaPeerServiceRole::InboundServe",
                "result.role_after = role",
            )
        )
        and all(
            token in peer_status + sync_cli
            for token in (
                '\\"network_outcome_known\\"',
                '\\"payload_store_lease_conflict_observed\\"',
                '\\"payload_authority_network_outcome_uncertain_steps\\"',
                '\\"payload_store_lease_backoff_deferrals\\"',
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                'last_step.get("network_outcome_known")',
                'role_before == "outbound_pull"',
                'role_before == "inbound_serve"',
                'role_after != "inbound_serve"',
                '"apply the conservative inbound turn "',
                '"unknown inbound outcome changed the "',
                '"inbound service role: "',
            )
        ),
        "payload_authority_failure_preserves_truth_and_fences_ambiguous_network_turns",
        "a network-path payload failure never reports a fabricated handoff result: outbound ambiguity yields inbound for the full successful-handoff horizon, while inbound ambiguity remains inbound and both directions schedule bounded convergence",
    )


    require(
        all(
            token in peer_service + peer_status
            for token in (
                "payload_store_lease_busy_deferred",
                '\\"payload_store_lease_busy_deferrals\\"',
                '\\"payload_store_lease_retry_delay_milliseconds\\"',
            )
        )
        and all(
            token in sync_cli
            for token in (
                "payload_store_lease_backoff_pending",
                "payload_store_lease_retry_wait",
                "step.payload_store_lease_retry_delay_milliseconds",
                "kSyncReplicaPeerServiceMaximumPayloadStoreLeaseBackoffWaitMilliseconds",
            )
        )
        and ordered(
            sync_cli,
            "payload_store_lease_backoff_pending",
            "publish_status(",
            "payload_store_lease_retry_wait",
            "bounded_wait = std::min(",
            "kSyncReplicaPeerServiceMaximumPayloadStoreLeaseBackoffWaitMilliseconds",
            "wait_for_action_request_or_timeout(",
        ),
        "lease_deferral_is_operator_visible_and_daemon_wait_is_bounded",
        "live and terminal status expose the typed disposition, delay and monotonic counter while the run loop caps the cooperative retry wait and remains drain-responsive",
    )

    require(
        all(
            token in service_configuration_runtime
            for token in (
                "def require_live_lease_deferral()",
                "while_lease_held=require_live_lease_deferral",
                "service exited during a cooperative payload-store ",
                "lease conflict with",
                "payload_store_lease_busy_deferrals",
                "lease deferral replaced the service process",
                "cooperative lease contention revoked healthy ",
                "service readiness",
                "payload fault status lost cooperative lease accounting",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "The now-correct corruption oracle exposed a separate production availability",
                "pass-wide rollback",
                "same PID remains ready",
            )
        )
        and all(
            token in normalized_prose(rev0959_notes)
            for token in (
                "Retained cooperative lease deferral",
                "separately idempotent progress",
                "does not claim pass-wide",
            )
        )
        and all(
            token in normalized_prose(minimum_reader_design)
            for token in (
                "Cooperative lease contention must not destroy the service owner",
                "failed nonblocking acquisition",
                "consumes no payload-store authority",
                "does not invent cross-owner rollback",
                "requires the same",
                "PID, healthy readiness",
                "network-filesystem equivalence",
            )
        ),
        "real_process_holds_exact_exclusive_lease_while_proving_same_pid_deferral",
        "the product process regression observes the live retained daemon before releasing the exact cooperative writer lease, then continues into stable typed corruption recovery with the accounting claim bound in documentation",
    )

    damaged_migration_runtime = function_body(
        runtime,
        "void test_minimum_reader_migration_rebuilds_damaged_scrub_state_once()",
    )
    require(
        all(
            token in migration
            for token in (
                "cold.scrub_state_present &&",
                "!cold.scrub_state_metadata.has_value()",
                "else if (cold.scrub_state_present)",
                "minimum-reader damaged-state rebuild",
                "prior_scrub_state_metadata = *cold.scrub_state_metadata",
                "cannot force an immediate duplicate scan",
            )
        )
        and ordered(
            migration,
            "PayloadVerificationReusePolicy::RequireCurrentBytes",
            "else if (cold.scrub_state_present)",
            "initial_sync_replica_file_payload_scrub_state_or_throw",
            "rebind_identity_basename_after_atomic_rename_or_throw",
            "publish_rebound_scrub_state_after_identity_rename_or_throw",
        )
        and all(
            token in damaged_migration_runtime
            for token in (
                "test_minimum_reader_migration_rebuilds_damaged_scrub_state_once",
                "limits.max_scrub_bytes_per_attempt = 0U",
                "sync_replica_file_payload_scrub_state_exact_bytes",
                "migrated.scan_hashed_entry_count() == 0U",
                "migrated.scan_process_reused_entry_count() == 1U",
                "!migrated.scrub_report().state_rebuilt",
                "minimum-reader migration repeated the cold proof",
                "minimum-reader migration did not bind canonical state",
            )
        ),
        "migration_rebuilds_unusable_scrub_state_from_cold_proof_before_handoff",
        "a present malformed scrub record globally revokes acceleration during the mandatory pre-rename scan, then is replaced with identity-rebound canonical Idle state so the immediately following ordinary snapshot consumes the exact process generation instead of hashing the namespace a second time",
    )

    require(
        all(
            token in minimum_reader_design
            for token in (
                "Heart of the mission",
                "The concrete downgrade hazard",
                "Chosen fence: rename the exact lock inode",
                "Namespace state machine",
                "Restart and failure matrix",
                "Cooperative old process already active",
                "Mechanical regressions",
                "Adjacent audit and refactor findings",
                "What this proves",
                "What this does not prove",
                "rename(2)",
                "flock(2)",
                "directory-entry rename durable",
                "two directed edges",
                "NFS rename may report failure",
                "Deliberate corruption must obey the cooperative lease boundary",
                "LOCK_EX|LOCK_NB",
                "mixed-version rolling upgrade",
            )
        )
        and all(
            token in rev0959_notes
            for token in (
                "minimum payload-store reader generation",
                "RENAME_NOREPLACE",
                "RequireCurrentBytes",
                "ReadOnlyInspect",
                "Coexisting current and legacy markers",
                "zero duplicate hashes",
                "same-family upgrade",
                "stale rev0958 Ninja build",
                "cooperative exclusive `flock`",
                "120 seconds",
                "Nonclaims",
                "RELEASE_GATE.json",
            )
        )
        and all(
            token in rev0959_verifier_block
            for token in (
                "MINIMUM_READER_IDENTITY_MIGRATION_AUDIT_rev0959.md",
                "REVISION_NOTES_rev0959.md",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_peer_service_status.hpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tools/test_anonsync_replica_cli.py",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0959_records_migration_crash_research_nonclaims_and_release_binding",
        "the release binds the cold-before-rename ordering, exact inode transition, read-only boundary, mixed-version nonclaim, runtime oracle, and package surface",
    )

    require(
        all(
            token in scrub_restart_fence_design
            for token in (
                "Heart of the mission",
                "The concrete restart gap",
                "Intent before read",
                "Fresh-process reproof",
                "Exact publication and re-observation refactor",
                "Reuse matrix",
                "Mechanical restart regression",
                "Adjacent audit findings",
                "Research-informed",
                "What this proves",
                "What this does not prove",
                "downgrade compatibility",
                "power-loss",
            )
        )
        and all(
            token in rev0958_notes
            for token in (
                "Prepared = 4",
                "write-ahead",
                "shared store lease",
                "process-cache",
                "durable verification-index",
                "downgrade safety is not claimed",
                "Nonclaims",
                "RELEASE_GATE.json",
            )
        )
        and all(
            token in verifier
            for token in (
                "SCRUB_WRITE_AHEAD_RESTART_FENCE_AUDIT_rev0958.md",
                "REVISION_NOTES_rev0958.md",
                "src/sync_replica_file_payload_scrub_state.hpp",
                "tests/sync_replica_file_payload_scrub_state_test.cpp",
            )
        ),
        "rev0958_records_restart_authority_refactor_research_nonclaims_and_release_binding",
        "the release binds the mandatory intent ordering, exact same-process exception, hard lease oracle, downgrade boundary, and remaining power-loss/product work",
    )

    local_action_snapshot = function_body(
        local_status,
        "SyncLocalStatusSocketServer::action_snapshot() const",
    )
    local_action_wait = function_body(
        local_status,
        "SyncLocalStatusSocketServer::wait_for_action_request_or_timeout(",
    )
    local_action_seal = function_body(
        local_status,
        "SyncLocalStatusSocketServer::seal_actions_for_owner_shutdown()",
    )
    require(
        all(
            token in local_status_h
            for token in (
                "SyncLocalStatusSocketActionSnapshot action_snapshot() const",
                "seal_actions_for_owner_shutdown()",
                "wait_for_action_request_or_timeout(",
                "sole owner-thread action observation",
                "split-read shutdown race",
            )
        )
        and all(
            token not in local_status_h + local_status
            for token in (
                "SyncLocalStatusSocketServer::stop_requested()",
                "SyncLocalStatusSocketServer::recheck_request_generation()",
                "wait_for_stop_request_or_timeout(",
                "std::atomic<",
                "std::memory_order_",
            )
        )
        and all(
            token in local_action_snapshot
            for token in (
                "std::lock_guard lock(state_->mutex)",
                "state_->drain_requested",
                "state_->recheck_generation",
                "state_->quarantine_pending",
            )
        )
        and all(
            token in local_action_wait
            for token in (
                "std::unique_lock lock(state_->mutex)",
                "state_->drain_requested",
                "state_->recheck_generation >",
                "state_->quarantine_pending->request_generation >",
                "state_->action_condition.wait_for(",
            )
        ),
        "local_control_actions_have_one_mutex_linearization_model",
        "drain, recheck generation, and one exact quarantine pair are observed and waited on only as one mutex-protected action state; obsolete split getters and redundant atomic shadow state are absent",
    )

    command_run = function_body(sync_cli, "int command_run(")
    require(
        all(
            token in local_action_seal
            for token in (
                "std::lock_guard lock(state_->mutex)",
                "state_->drain_requested = true",
                "state_->recheck_generation",
                "state_->action_condition.notify_all()",
            )
        )
        and ordered(
            command_run,
            "status_server->seal_actions_for_owner_shutdown()",
            "owner.observe_payload_recheck_request_generation_or_throw(",
            "service_manager.announce_stopping(",
            'publish_status("stopping", "stopped", stop_reason)',
            "const auto payload_recheck = owner.payload_recheck_status()",
        )
        and all(
            token in local_status_runtime
            for token in (
                "owner shutdown seal must bind all pre-seal actions",
                "owner shutdown seal must be idempotent",
                "post-seal recheck must be rejected without generation advance",
                "owner shutdown seal must preserve read-only status service",
            )
        ),
        "owner_shutdown_seal_closes_the_recheck_acceptance_race",
        "before terminal status is frozen the owner atomically latches drain and observes the final accepted generation, so a racing request is either represented as pending/completed terminal work or rejected after the cutpoint",
    )

    local_drain_request = function_body(
        local_status, "request_drain_response()"
    )
    local_recheck_request = function_body(
        local_status, "request_recheck_response()"
    )
    require(
        ordered(
            local_drain_request,
            "std::lock_guard lock(mutex)",
            "first_request = !drain_requested",
            "drain_requested = true",
            "action_condition.notify_all()",
            "std::ostringstream response",
        )
        and ordered(
            local_recheck_request,
            "std::lock_guard lock(mutex)",
            "if (!drain_requested)",
            "++generation",
            "recheck_generation = generation",
            "if (accepted) action_condition.notify_all()",
            "std::ostringstream response",
        )
        and all(
            token in local_status_runtime
            for token in (
                "wait_for_action_request_or_timeout(",
                "post-drain rejection must not advance generation",
                "accepted recheck must not wait for the fallback timeout",
            )
        ),
        "local_recheck_acceptance_precedes_response_allocation_and_drain_is_terminal",
        "the worker publishes and wakes accepted owner work before response construction, while the same mutex makes a recheck serialized after drain reject without generation advance",
    )

    require(
        "unique_json_object_pairs" in sync_process_runtime
        and "duplicate JSON object key" in sync_process_runtime
        and "object_pairs_hook=unique_json_object_pairs" in sync_process_runtime
        and "unique_json_object_pairs" in service_process_runtime
        and "object_pairs_hook=unique_json_object_pairs"
            in service_process_runtime,
        "live_and_terminal_process_oracles_reject_duplicate_json_keys",
        "the real-process status and terminal-output parsers reject duplicate object members instead of accepting parser-dependent operator evidence",
    )

    require(
        all(
            token in owner_recheck_design
            for token in (
                "Heart of the mission",
                "Product boundary",
                "Local control authority",
                "One linearized action observation",
                "Generation and coalescing semantics",
                "Current-byte authority path",
                "Exact handoff into ordinary convergence",
                "Contention, mismatch, and recovery",
                "Mechanical process oracle",
                "Research-informed product comparison",
                "What this proves",
                "What this does not prove",
                "seal_actions_for_owner_shutdown()",
                "duplicate object keys",
                "process-local scheduling evidence",
            )
        )
        and all(
            token in rev0960_notes
            for token in (
                "owner-operated current-byte payload recheck",
                "anonsync_sync recheck --socket ABSOLUTE_SOCKET",
                "anonsync.local-recheck.response.v1",
                "anonsync.peer-service.status.v7",
                "seal_actions_for_owner_shutdown()",
                "duplicate JSON object keys",
                "ReadOnlyInspect",
                "Nonclaims",
                "GCC 14.2",
                "Clang 17 ASan/UBSan",
                "structural audit",
            )
        )
        and "VALIDATION_PENDING_REV0960" not in rev0960_notes
        and verifier.count(
            "if revision_number is not None and revision_number >= 960:"
        ) == 1
        and all(
            token in rev0960_verifier_block
            for token in (
                "OWNER_TRIGGERED_PAYLOAD_RECHECK_AUDIT_rev0960.md",
                "REVISION_NOTES_rev0960.md",
                "src/sync_local_status_socket.hpp",
                "src/sync_local_status_socket.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_process.py",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/audit_sync_file_payload_store.py",
            )
        ),
        "rev0960_records_owner_recheck_shutdown_cutpoint_nonclaims_and_release_binding",
        "the revision record binds forced current-byte proof, exact snapshot handoff, generation coalescing, terminal action sealing, strict JSON evidence, operator nonclaims, and the mandatory package surface",
    )

    quarantine_store = function_body(
        store,
        "SyncReplicaFilePayloadStore::quarantine_corrupt_payload_or_throw(",
    )
    quarantine_observer = function_body(
        store, "observe_quarantine_namespace_under_lease_or_throw("
    )
    full_store_scan = function_body(
        store, "scan_store_namespace_or_throw("
    )
    staged_prefix_observer = function_body(
        store, "observe_staged_prefix_namespace_under_lease_or_throw("
    )
    local_quarantine_request = function_body(
        local_status, "request_payload_quarantine_response("
    )
    local_quarantine_completion = function_body(
        local_status,
        "complete_payload_quarantine_request_or_throw(",
    )
    operator_quarantine = function_body(
        peer_service, "operator_payload_quarantine_step_or_throw()"
    )
    quarantine_status_renderer = function_body(
        peer_status,
        "render_sync_replica_peer_service_payload_quarantine_status_json(",
    )
    quarantine_result_renderer = function_body(
        peer_status,
        "render_sync_replica_file_payload_store_quarantine_result_json(",
    )
    command_quarantine = function_body(sync_cli, "int command_quarantine(")
    command_quarantine_release = function_body(
        sync_cli, "int command_quarantine_release("
    )
    quarantine_release_store = function_body(
        store,
        "SyncReplicaFilePayloadStore::release_quarantined_payload_or_throw(",
    )
    quarantine_acceleration_refresh = function_body(
        quarantine_store,
        "refresh_acceleration_after_authoritative_namespace_mutation",
    )

    leased_complete_scan = function_body(
        store, "ScannedPayloadIndex scan_store_under_lease_or_throw("
    )
    quarantine_inventory_known_body = function_body(
        store,
        "quarantine_inventory_observation_known() const",
    )
    quarantine_inventory_status_body = function_body(
        store,
        "SyncReplicaFilePayloadStore::quarantine_inventory_status() const",
    )
    public_quarantine_inventory_entry = delimited_body(
        store_h,
        "struct SyncReplicaFilePayloadStoreQuarantineInventoryEntry final",
        "{",
        "}",
    )
    process_quarantine_inventory_entry = delimited_body(
        store, "struct ProcessQuarantineInventoryEntry final", "{", "}"
    )

    require(
        "kSyncReplicaFilePayloadStoreMaxQuarantineEntries = 16U" in store_h
        and all(
            token in store
            for token in (
                "kQuarantineBasenamePrefix",
                ".anonsync-payload-quarantine-v1-",
                "parse_quarantine_basename",
                "basename.size() != 64U + 1U + 64U",
                "expected == observed",
                "maximum_quarantine_bytes",
                "kMaximumPersistentInteger /",
                "std::min(limits.max_indexed_bytes, entry_derived_limit)",
            )
        ),
        "quarantine_name_and_capacity_are_canonical_fixed_and_overflow_checked",
        "one exact expected/observed grammar and a sixteen-entry frontier capped by the active indexed-byte budget prevent diagnostic preservation from becoming an unbounded or disproportionately large hidden archive",
    )

    require(
        all(
            token in full_store_scan
            for token in (
                "parse_quarantine_basename(basename)",
                "require_private_regular_file_or_throw",
                "out.quarantines.push_back",
                "out.quarantine_bytes",
                "payload quarantine count exceeds fixed budget",
                "payload quarantine bytes exceed fixed budget",
            )
        )
        and "parse_quarantine_basename(basename).has_value()" in staged_prefix_observer
        and ordered(
            identity,
            "const ScannedPayloadIndex bootstrap = scan_store_namespace_or_throw(",
            "if (!bootstrap.quarantines.empty())",
            "fresh bootstrap refuses pre-existing payload quarantine",
            "if (!allow_existing_payload_adoption &&",
            "product-bound bootstrap refuses adoption of pre-existing",
        )
        and "!bootstrap.quarantines.empty() ||" not in identity
        and "standalone adoption silently assigned unbound quarantine evidence" in runtime,
        "complete_scans_validate_quarantine_while_targeted_work_excludes_it_and_bootstrap_rejects_it",
        "retained evidence remains visible to namespace health and capacity proof but cannot satisfy payload inventory, targeted access, or unexplained fresh-store adoption, including the standalone adoption path",
    )

    require(
        all(
            token in quarantine_store
            for token in (
                "read-only inspection store cannot quarantine payload bytes",
                "store.verification_cache->integrity_fault",
                "ActiveFaultMismatch",
                "reopen_matching_root_authority_or_throw",
                "SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation",
                "observe_quarantine_namespace_under_lease_or_throw",
                "stream_hash_regular_file_or_throw",
                "verify_named_regular_file_or_throw",
            )
        )
        and ordered(
            quarantine_store,
            "store.verification_cache->integrity_fault",
            "ActiveFaultMismatch",
            "acquire_store_lease_or_throw",
            "stream_hash_regular_file_or_throw",
            "rename_noreplace_at_or_throw",
        ),
        "quarantine_requires_the_exact_active_process_fault_and_current_bytes_under_exclusive_authority",
        "operator-supplied names are insufficient: the active pair, identity/root, cooperative mutation lease, current bytes, metadata, and pathname all precede the move",
    )

    require(
        all(
            token in quarantine_store
            for token in (
                "PayloadAlreadyRepaired",
                "ObservedDigestChanged",
                "PayloadAbsent",
                "ExactQuarantineAlreadyPresent",
                "verify_nonmutating_cutpoint_or_throw",
                "target_quarantine_basename",
                "result.quarantine_basename = target_quarantine_basename",
            )
        )
        and quarantine_store.count(
            "result.quarantine_basename = target_quarantine_basename"
        ) == 2
        and all(
            token in runtime
            for token in (
                "wrong.quarantine_basename.empty()",
                "changed.quarantine_basename.empty()",
                "now_stale.quarantine_basename.empty()",
            )
        ),
        "nonmutating_quarantine_results_do_not_invent_a_retained_destination",
        "the result basename is populated only after an exact existing destination is byte-reproved or after the successful no-replace rename",
    )

    require(
        all(
            token in store_h + store
            for token in (
                "EntryCapacityExceeded",
                "ByteCapacityExceeded",
                "entry_capacity_exceeded",
                "byte_capacity_exceeded",
            )
        )
        and ordered(
            quarantine_store,
            "if (retained.inventory.entry_count >=",
            "EntryCapacityExceeded",
            'verify_nonmutating_cutpoint_or_throw("entry-capacity")',
            "return result;",
            "const std::uint64_t quarantine_byte_limit",
            "ByteCapacityExceeded",
            'verify_nonmutating_cutpoint_or_throw("byte-capacity")',
            "return result;",
        )
        and all(
            token in runtime
            for token in (
                "a full quarantine frontier threw or mutated instead of returning a typed entry-capacity result",
                "a full quarantine byte budget threw or mutated instead of returning a typed capacity result",
                "entry-capacity completion accidentally cleared the active fault",
                "byte-capacity completion accidentally cleared the active fault",
            )
        ),
        "ordinary_quarantine_capacity_is_a_typed_nonfatal_operator_result",
        "an exact full entry or byte frontier completes the accepted request without mutating authority or terminating the retained daemon; structurally invalid over-budget namespaces remain fail-closed scan errors",
    )

    require(
        ordered(
            quarantine_store,
            "if (!retained.exact_destination_status.has_value()) return false",
            "open_store_file_or_throw",
            "stream_hash_regular_file_or_throw",
            "exact quarantine name does not bind its observed bytes",
            "fsync_or_throw",
            "verify_named_regular_file_or_throw",
            "ExactQuarantineAlreadyPresent",
        )
        and all(
            token in runtime
            for token in (
                "an exact retained quarantine was not byte-reproved idempotently",
                "read_file_bytes(quarantine_path) == second_corrupt",
            )
        ),
        "idempotent_quarantine_success_rehashes_the_retained_byte_image",
        "a canonical destination filename is not recovery evidence; exact retained bytes and pathname identity are re-proved before idempotent success",
    )

    require(
        ordered(
            quarantine_store,
            "if (verify_exact_quarantine_or_throw())",
            "duplicate payload quarantine pre-unlink cutpoint",
            "unlink_scanned_private_file_or_throw",
            "duplicate corrupt payload quarantine directory",
            "duplicate quarantined payload source",
            "duplicate quarantined payload destination",
            "refresh_acceleration_after_authoritative_namespace_mutation",
            "ExactQuarantineAlreadyPresent",
        )
        and all(
            token in runtime
            for token in (
                "repeated exact corruption did not reinstall quarantine authority",
                "an exact retained quarantine left repeated corrupt authority stuck",
                "repeated exact quarantine did not permit complete absence reproof",
                "repeated exact quarantine did not permit ordinary byte re-admission",
            )
        ),
        "repeated_identical_corruption_cannot_become_idempotent_but_unrecoverable",
        "after byte-reproving the exact retained image and the reappeared corrupt source, the explicit action removes only the duplicate authoritative name, revokes acceleration, and permits ordinary re-admission",
    )

    require(
        ordered(
            quarantine_store,
            "pre-rename lease cutpoint",
            "pre-rename root proof",
            "corrupt payload quarantine source bytes",
            "corrupt payload quarantine durable source",
            "rename_noreplace_at_or_throw",
            "fsync_or_throw",
            "same_regular_file_rename_transition",
            "verify_named_entry_absent_or_throw",
            "verify_named_regular_file_or_throw",
            "final lease cutpoint",
            "refresh_acceleration_after_authoritative_namespace_mutation();",
            "Quarantined",
        )
        and "generation.reset()" not in quarantine_store
        and "scrub_active.reset()" in quarantine_store
        and "scrub_active->active_digest() ==" in quarantine_store
        and all(
            token in runtime
            for token in (
                "source_before.st_dev == destination_after.st_dev",
                "source_before.st_ino == destination_after.st_ino",
                "same corrupt inode outside authority",
            )
        ),
        "successful_quarantine_is_no_replace_same_inode_durable_and_refreshes_only_stale_acceleration",
        "the exact open source bytes are synchronized before the same inode is moved outside authority, then the directory and both pathname transitions are re-proved while only stale checkpoint, capacity, and matching scrub scheduling are refreshed and the integrity alarm remains",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                "SyncLocalStatusSocketPayloadQuarantineRequest",
                "payload_quarantine_request",
                "quarantine EXPECTED OBSERVED\\n",
                "anonsync.local-quarantine.response.v1",
                "kMaximumRequestBytes = 16U * 1024U",
                "different_quarantine_pending",
                "complete_payload_quarantine_request_or_throw",
            )
        )
        and all(
            token in local_quarantine_request
            for token in (
                "std::lock_guard lock(mutex)",
                "drain_requested",
                "quarantine_pending.has_value()",
                "++generation",
                "action_condition.notify_all()",
                "std::ostringstream response",
            )
        ),
        "local_quarantine_protocol_is_exact_pid_bound_and_uses_the_existing_action_mutex",
        "one strict bounded request grammar advances only one mutex-owned exact-pair generation and wakes the capability-free socket owner before response allocation",
    )

    require(
        all(
            token in local_quarantine_completion
            for token in (
                "std::lock_guard lock(state_->mutex)",
                "completed_generation < state_->quarantine_completed_generation",
                "completed_generation > state_->quarantine_generation",
                "state_->quarantine_pending->request_generation <=",
                "state_->quarantine_pending.reset()",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "different-pair quarantine must not overwrite pending authority",
                "same-pair quarantine must coalesce through a new generation",
                "completion through an older generation cleared coalesced work",
                "payload quarantine serialized after drain must be rejected",
                "drain snapshot must retain every pre-drain generation",
            )
        ),
        "quarantine_generation_coalescing_completion_and_shutdown_order_are_executable",
        "different pairs cannot overwrite one obligation, same-pair generations coalesce without lost completion, and the combined shutdown seal represents every accepted pre-drain request",
    )

    require(
        all(
            token in operator_quarantine
            for token in (
                "payload_quarantine_started_generation",
                "payload_quarantine_attempts",
                "quarantine_corrupt_payload_or_throw",
                "ObservedDigestChanged",
                "record_payload_integrity_evidence_or_throw",
                "payload_quarantine_completed_generation",
                "payload_quarantine_last_result",
                "payload_quarantine_completions",
                "payload_quarantine_images_preserved",
            )
        )
        and ordered(
            peer_owner_run,
            "operator_quarantine_pending",
            "PayloadAuthorityFailureContext::OperatorQuarantine",
            "operator_payload_quarantine_step_or_throw",
            "operator_payload_recheck_step_or_throw",
            "payload_integrity_reproof_step_or_throw",
        ),
        "service_prioritizes_exact_quarantine_without_clearing_integrity_authority",
        "the owner serializes the namespace mutation before recheck/reproof, retains typed lease deferral, updates changed exact-pair evidence, and completes only a typed store result",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_status
            for token in (
                "requested_generation",
                "started_generation",
                "completed_generation",
                "retry_delay_milliseconds",
                "expected_content_sha256",
                "observed_content_sha256",
                "quarantine_basename",
                "last_result",
            )
        )
        and all(
            token in peer_status + sync_cli + service_configuration_runtime
            for token in (
                "payload_quarantine_requests_observed",
                "payload_quarantine_requests_coalesced",
                "payload_quarantine_attempts",
                "payload_quarantine_completions",
                "payload_quarantine_images_preserved",
                "payload_quarantine_observed_content_changes",
            )
        ),
        "status_v10_canonically_exposes_quarantine_obligation_result_inventory_and_accounting",
        "live, terminal, and process-oracle surfaces share versioned generation, pair, retry, typed-result, preservation, and observed-content transition truth",
    )

    require(
        all(
            token in command_quarantine
            for token in (
                '"socket", "expected", "observed", "timeout-milliseconds"',
                "is_lowercase_sha256_hex",
                "request_sync_local_status_payload_quarantine_or_throw",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                '"anonsync.local-quarantine.response.v1"',
                "payload quarantine acceptance was not exact",
                "quarantine did not preserve the exact corrupt byte image",
                "payload quarantine did not preserve the exact private ",
                "source inode",
                "re-admitted authoritative payload still aliases the ",
                "quarantined inode",
                "quarantine recovery did not expose the one full scan",
                "payload-integrity recovery replaced the service process",
            )
        ),
        "shipping_cli_process_oracle_proves_quarantine_preservation_readmission_and_same_pid_recovery",
        "the configured service exercises the exact CLI response, held-lease fault path, same-inode evidence move, distinct-inode correct re-admission, truthful scan cost, retained history, and clean lifecycle",
    )

    require(
        all(
            token in quarantine_design
            for token in (
                "Heart of the mission",
                "Product boundary",
                "Exact active-fault authority",
                "Rooted exclusive mutation path",
                "Current-byte pair reproof",
                "Same-inode no-replace preservation",
                "Authority revocation and re-admission",
                "One linearized local-action observation",
                "Status contract",
                "Mechanical process oracle",
                "Audit/refactor findings",
                "Research-informed product comparison",
                "What this proves",
                "What this does not prove",
                "hostile same-UID",
                "one mutation-authority full scan",
            )
        )
        and all(
            token in rev0961_notes
            for token in (
                "bounded operator recovery action",
                "anonsync_sync quarantine --socket ABSOLUTE_SOCKET",
                "anonsync.local-quarantine.response.v1",
                "anonsync.peer-service.status.v8",
                "same-inode no-replace rename",
                "Nonclaims",
                "GCC 14.2",
                "Clang 17 ASan/UBSan",
                "structural audit",
            )
        )
        and "VALIDATION_PENDING_REV0961" not in rev0961_notes
        and verifier.count(
            "if revision_number is not None and revision_number >= 961:"
        ) == 1
        and all(
            token in rev0961_verifier_block
            for token in (
                "EXACT_CORRUPT_PAYLOAD_QUARANTINE_AND_LINEARIZED_LOCAL_ACTION_AUDIT_rev0961.md",
                "REVISION_NOTES_rev0961.md",
                "src/sync_local_status_socket.hpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/audit_sync_file_payload_store.py",
            )
        ),
        "rev0961_records_exact_quarantine_action_linearization_nonclaims_and_release_binding",
        "the revision record binds exact-pair admission, same-inode bounded preservation, truthful result/status shape, ordinary re-admission cost, action ordering, explicit nonclaims, validation, and the mandatory package surface",
    )

    require(
        all(
            token in quarantine_release_store
            for token in (
                "SyncReplicaFilePayloadStoreQuarantineAction::Release",
                "ActiveFaultPresent",
                "acquire_store_lease_or_throw",
                "observe_quarantine_namespace_under_lease_or_throw",
                "duplicate_shared_open_description_or_throw",
                "open_store_file_or_throw",
                "same_regular_file_observation",
                "verify_named_regular_file_or_throw",
                "unlink_scanned_private_file_or_throw",
                "fsync_or_throw",
                "verify_named_entry_absent_or_throw",
                "ExactQuarantineAbsent",
                "SyncReplicaFilePayloadStoreQuarantineDisposition::Released",
            )
        )
        and ordered(
            quarantine_release_store,
            "ensure_store_identity_or_throw",
            "integrity_fault",
            "acquire_store_lease_or_throw",
            "observe_quarantine_namespace_under_lease_or_throw",
            "open_store_file_or_throw",
            "verify_named_regular_file_or_throw",
            "unlink_scanned_private_file_or_throw",
            "fsync_or_throw",
            "verify_named_entry_absent_or_throw",
            'verify_cutpoint_or_throw("final")',
        )
        and "stream_hash_regular_file_or_throw" not in quarantine_release_store
        and "ResumableSha256" not in quarantine_release_store
        and "read(" not in quarantine_release_store,
        "exact_quarantine_release_is_rooted_reader_fenced_and_does_not_hash_only_to_delete",
        "the owner validates the whole bounded diagnostic namespace, removes only the exact re-proved private inode under the identity lease, synchronizes and proves absence, while making no authenticity claim about explicitly discarded bytes",
    )

    require(
        all(
            token in quarantine_store
            for token in (
                "refresh_acceleration_after_authoritative_namespace_mutation",
                "checkpoint.force_checkpoint = true",
                "publication_capacity_observation_known = false",
                "scrub_active->active_digest() ==",
                "next_scrub_not_before =",
                "std::chrono::steady_clock::time_point::min()",
            )
        )
        and "verification_cache->generation.reset()" not in quarantine_acceleration_refresh
        and all(
            token in runtime
            for token in (
                "quarantine forced a whole-store rehash instead of retaining unrelated exact process proof",
                "non-authoritative quarantine release revoked authoritative byte reuse",
            )
        ),
        "quarantine_preserve_refreshes_namespace_state_without_revoking_unrelated_byte_proof",
        "removing one corrupt digest forces durable membership and relevant scrub refresh but leaves exact unrelated process observations reusable; releasing only diagnostic evidence leaves all payload acceleration intact",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                "SyncLocalStatusSocketPayloadQuarantineOperation",
                "Preserve",
                "Release",
                "quarantine-release ",
                "anonsync.local-quarantine-release.response.v1",
                "request_sync_local_status_payload_quarantine_release_or_throw",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "exact quarantine release must return exact acceptance",
                "combined action snapshot lost the release operation",
                "preserve must not overwrite a pending release action",
                "quarantine release serialized after drain must be rejected",
                "quarantine-release client must reject an identical digest pair",
            )
        ),
        "preserve_and_release_share_one_operation_aware_linearized_local_action_slot",
        "the operation kind is part of request identity across exact framing, generations, pending exclusion, combined waits, drain sealing, PID binding, and client validation",
    )

    require(
        all(
            token in operator_quarantine
            for token in (
                "payload_quarantine_action",
                "SyncReplicaFilePayloadStoreQuarantineAction::Preserve",
                "release_quarantined_payload_or_throw",
                "payload_quarantine_images_released",
            )
        )
        and '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_status + sync_cli + service_configuration_runtime
            for token in (
                '"action"',
                "payload_quarantine_images_preserved",
                "payload_quarantine_images_released",
                "anonsync.local-quarantine-release.response.v1",
                "quarantine-release",
            )
        ),
        "status_v10_and_service_owner_distinguish_preserve_from_release_end_to_end",
        "one owner step dispatches the typed action, retains preserve-only integrity transitions, counts actual releases, and projects the exact action through canonical live and terminal JSON",
    )

    require(
        all(
            token in command_quarantine_release
            for token in (
                '"socket", "expected", "observed", "timeout-milliseconds"',
                "is_lowercase_sha256_hex",
                "request_sync_local_status_payload_quarantine_release_or_throw",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "owner-only exact quarantine release",
                "anonsync.local-quarantine-release.response.v1",
                "wait_for_payload_quarantine_completion",
                "quarantine release changed authoritative payload bytes",
                "quarantine release replaced the authoritative payload inode",
                "quarantine release perturbed completed recheck field",
                "payload_quarantine_images_released",
            )
        ),
        "shipping_process_oracle_proves_exact_release_without_payload_or_recheck_perturbation",
        "the configured daemon preserves, re-admits, rechecks, and then releases diagnostic evidence in one healthy PID while retaining authoritative bytes, inode, readiness, and completed recovery proof",
    )

    require(
        all(
            token in quarantine_release_design
            for token in (
                "Heart of the mission",
                "Exact-pair product boundary",
                "Active-fault release fence",
                "Rooted exclusive release path",
                "Why release does not hash the diagnostic bytes",
                "Adjacent waste audit",
                "One linearized local action lane",
                "Status contract",
                "Mechanical runtime oracles",
                "Audit/refactor findings",
                "What this proves",
                "What this does not prove",
                "hostile same-UID",
            )
        )
        and all(
            token in rev0962_notes
            for token in (
                "anonsync_sync quarantine-release --socket ABSOLUTE_SOCKET",
                "anonsync.local-quarantine-release.response.v1",
                "anonsync.peer-service.status.v9",
                "whole-generation invalidation",
                "Nonclaims",
                "structural audit",
            )
        )
        and "VALIDATION_PENDING_REV0962" not in rev0962_notes
        and verifier.count(
            "if revision_number is not None and revision_number >= 962:"
        ) == 1
        and all(
            token in rev0962_verifier_block
            for token in (
                "EXACT_QUARANTINE_RELEASE_AND_PROOF_REUSE_AUDIT_rev0962.md",
                "REVISION_NOTES_rev0962.md",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/audit_sync_file_payload_store.py",
            )
        ),
        "rev0962_records_exact_release_proof_reuse_nonclaims_validation_and_package_binding",
        "the current revision binds the explicit irreversible evidence-release boundary, narrow acceleration refresh, action identity, status v9, mechanical process proof, nonclaims, final validation, and mandatory package surface",
    )

    require(
        all(
            token in store_h + store
            for token in (
                "SyncReplicaFilePayloadStoreQuarantineInventoryEntry",
                "SyncReplicaFilePayloadStoreQuarantineInventoryStatus",
                "ProcessQuarantineInventoryEntry",
                "ProcessQuarantineInventoryObservation",
                "kSyncReplicaFilePayloadStoreMaxQuarantineEntries> entries",
                "static_assert(std::is_trivially_copyable_v<",
                "append_process_quarantine_inventory_entry_or_throw",
                "sort_process_quarantine_inventory",
            )
        )
        and "expected_content_sha256" in public_quarantine_inventory_entry
        and "observed_content_sha256" in public_quarantine_inventory_entry
        and "size_bytes" in public_quarantine_inventory_entry
        and "quarantine_basename" not in public_quarantine_inventory_entry
        and "std::array<char, kSha256HexCharacters>" in process_quarantine_inventory_entry,
        "quarantine_inventory_is_fixed_width_canonical_and_retains_no_derived_paths",
        "the process owner keeps at most sixteen exact digest pairs and sizes in allocation-free storage; private basenames remain derived rather than duplicated long-lived state",
    )

    require(
        ordered(
            leased_complete_scan,
            "make_process_quarantine_inventory_or_throw",
            "final lease proof",
            "publish_verification_generation",
            "integrity_fault.reset()",
            "note_process_scrub_state_observation",
            "publish_process_quarantine_inventory",
        )
        and "out.quarantines" in leased_complete_scan
        and "out.quarantine_bytes" in leased_complete_scan,
        "complete_scan_publishes_inventory_only_after_existing_authority_and_fault_cutpoints",
        "ordinary writable scans prepare the bounded projection before the terminal lease proof and expose it only after verification, checkpoint, scrub, and fail-closed fault state settle",
    )

    require(
        all(
            token in quarantine_observer
            for token in (
                "QuarantineNamespaceObservation out",
                "append_process_quarantine_inventory_entry_or_throw",
                "sort_process_quarantine_inventory",
                "final scan root authority",
                "final retained root authority",
                "final lease proof",
            )
        )
        and "stream_hash_regular_file_or_throw" not in quarantine_observer,
        "exact_action_observer_returns_complete_bounded_inventory_without_hashing_for_status",
        "preserve and release reuse their complete reader-fenced namespace observation and do not spend diagnostic byte hashing merely to render retained-set metadata",
    )

    require(
        ordered(
            quarantine_store,
            "ProcessQuarantineInventoryObservation inventory_after",
            "forget_process_quarantine_inventory",
            "rename_noreplace_at_or_throw",
            "final lease cutpoint",
            "publish_process_quarantine_inventory",
            "Quarantined",
        )
        and ordered(
            quarantine_release_store,
            "ProcessQuarantineInventoryObservation inventory_after",
            "forget_process_quarantine_inventory",
            "unlink_scanned_private_file_or_throw",
            'verify_cutpoint_or_throw("final")',
            "publish_process_quarantine_inventory",
            "Released",
        )
        and "publish_process_quarantine_inventory" in quarantine_release_store,
        "quarantine_mutations_forget_stale_status_before_change_and_publish_exact_successors_after_reproof",
        "allocation-free successors are prepared before mutation; a late failure can make status unknown but cannot knowingly retain a stale pre-rename or pre-unlink set",
    )

    require(
        all(
            token in quarantine_inventory_status_body
            for token in (
                "require_current_owner_or_throw",
                "maximum_quarantine_bytes",
                "verification_cache->quarantine_inventory",
                "monotonic_age_milliseconds",
                "status.entries.reserve",
            )
        )
        and all(
            token in quarantine_inventory_known_body
            for token in (
                "require_current_owner_or_throw",
                "verification_cache->quarantine_inventory.has_value()",
            )
        )
        and all(
            token not in quarantine_inventory_status_body
            + quarantine_inventory_known_body
            for token in (
                "snapshot_or_throw",
                "scan_store",
                "observe_quarantine_namespace",
                "acquire_store_lease",
                "open_store_file",
                "stream_hash_regular_file",
                "fsync_or_throw",
            )
        )
        and peer_service.count("quarantine_inventory_status()") == 1
        and peer_service.count(
            "quarantine_inventory_observation_known()"
        ) == 2,
        "owner_quarantine_inventory_status_and_readiness_predicate_are_filesystem_cold",
        "status materializes only the most recent complete owner observation while readiness uses an allocation-free exact-thread predicate; neither path acquires a lease, traverses a namespace, opens an inode, hashes a byte, or advances work",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "SyncReplicaFilePayloadStoreQuarantineInventoryStatus inventory" in peer_service_h
        and all(
            token in peer_status
            for token in (
                "append_payload_quarantine_inventory_status",
                r'\"observation_known\"',
                r'\"last_observation_age_milliseconds\"',
                r'\"entry_limit\"',
                r'\"byte_limit\"',
                r'\"entry_count\"',
                r'\"total_bytes\"',
                r'\"entries\"',
            )
        )
        and "require_payload_quarantine_inventory" in service_configuration_runtime
        and '"anonsync.peer-service.status.v26"' in service_configuration_runtime
        and '"anonsync.peer-service.status.v26"' in service_i2p_ingress_runtime,
        "status_v10_exposes_complete_quarantine_inventory_separately_from_last_action_history",
        "canonical live, terminal, direct, and I2P process surfaces carry bounded observation truth while preserving the existing typed preserve/release result domain",
    )

    require(
        "quarantine-list" not in store_h + store + local_status_h + local_status + sync_cli
        and "SyncReplicaFilePayloadStoreQuarantineAction::List" not in store
        and "inspect_quarantined_payloads_or_throw" not in store_h + store,
        "draft_list_command_and_query_time_traversal_were_removed",
        "the adjacent refactor avoids a second control operation and repeated namespace I/O by reusing observations already paid for by ordinary store ownership",
    )

    require(
        all(
            token in runtime
            for token in (
                "test_quarantine_inventory_is_restart_discoverable_and_exactly_updated",
                "fresh payload-store owner invented a quarantine observation",
                "restart borrowed a prior process's quarantine observation",
                "quarantine_inventory_observation_known",
                "diagnostic quarantine leaked into authoritative payload inventory",
                "exact release did not publish its exact successor inventory without another scan",
                "ordinary restart scan did not rediscover retained diagnostic evidence",
            )
        )
        and all(
            token in normalized_prose(service_configuration_runtime)
            for token in (
                "reported ready without its complete empty",
                "ready service did not retain exactly one",
                "initial service unexpectedly retained",
                "recovered quarantine inventory field",
                "exact quarantine release did not publish an exact empty",
                "successor inventory",
                "terminal lost the exact empty quarantine inventory",
            )
        ),
        "unit_and_real_process_oracles_prove_restart_rediscovery_exact_successors_and_payload_separation",
        "focused storage and shipping daemon tests cover raw process-cold state, canonical restart discovery, readiness binding, preserve, release, terminal retention, and exclusion from authoritative payload inventory",
    )

    require(
        "expected_quarantine_observation_known" not in
            service_configuration_runtime + service_folder_wake_runtime
        and all(
            token in service_folder_wake_runtime
            for token in (
                "initial_repair_payload_snapshot_handoffs",
                "initial_repair_payload_snapshot_handoff_entries",
                "initial_repair_convergence_snapshot_observations",
                "initial_repair_convergence_mutation_full_scans",
                "status polling lost the initial payload-store observation",
                "first eligible convergence did not preserve the initial",
                "exact empty quarantine observation",
                "restarted service payload cutpoint",
            )
        )
        and all(
            token in initial_repair
            for token in (
                "snapshot_or_throw",
                "run_convergence_pass_with_payload_snapshot_or_throw",
                "payload_snapshot_handoff_count != 1U",
                "payload_snapshot_observation_count != 0U",
                "quarantine_inventory_observation_known",
                "initial_repair_payload_snapshot_handoffs",
                "initial_repair_convergence_snapshot_observations",
            )
        )
        and all(
            token in peer_ready
            for token in (
                "initial_repair_done",
                "ingress_is_ready",
                "payload_integrity_fault",
                "quarantine_inventory_observation_known",
            )
        )
        and 'return owner.ready() ? "running" : "degraded"' in sync_cli
        and "required readiness evidence is unavailable" in sync_cli
        and "reported ready without a complete" in normalized_prose(
            service_i2p_ingress_runtime
        )
        and "quarantine observation" in normalized_prose(
            service_i2p_ingress_runtime
        ),
        "ready_state_requires_one_complete_initial_inventory_observation_without_duplicate_scan",
        "initial repair moves one exact complete payload snapshot into ordinary convergence, runtime counters expose the no-duplicate cutpoint, all ready route surfaces require known inventory truth, and live readiness cannot hide a later revoked observation behind the historical repair bit",
    )

    stale_control_runtime = function_body(
        stream_connector_runtime,
        "void test_i2p_stale_control_is_recovered_between_sessions()",
    )
    fin_ack_helper = function_body(
        stream_connector_runtime,
        "void shutdown_write_and_wait_for_fin_ack_or_throw(",
    )
    require(
        "#include <netinet/tcp.h>" in stream_connector_runtime
        and ordered(
            fin_ack_helper,
            "::shutdown(descriptor, SHUT_WR)",
            "TCP_INFO",
            "TCP_FIN_WAIT2",
            "std::this_thread::sleep_for(1ms)",
        )
        and ordered(
            stale_control_runtime,
            "shutdown_write_and_wait_for_fin_ack_or_throw",
            "stale SAM first response",
            "connector.connect_until_or_throw",
            "control_session_stale_detected",
            "control_session_recovered",
        )
        and "control.close_noexcept();" not in stale_control_runtime
        and "TCP_FIN_WAIT2" in quarantine_inventory_design
        and "TCP_FIN_WAIT2" in rev0963_notes,
        "stale_sam_control_oracle_proves_cross_socket_fin_observation_order",
        "the I2P recovery regression no longer assumes close on one TCP stream precedes a marker on another; it waits for the peer kernel to acknowledge the control FIN before allowing reuse inspection",
    )

    require(
        all(
            token in quarantine_inventory_design
            for token in (
                "Heart of the mission",
                "Product boundary",
                "The operability defect",
                "One bounded projection, not a second traversal",
                "Complete-scan publication cutpoint",
                "Preserve and release mutation cutpoints",
                "Restart semantics and age semantics",
                "Status contract",
                "Mechanical runtime oracles",
                "Audit/refactor findings",
                "Readiness must not outrun diagnostic discoverability",
                "Research-informed product comparison",
                "What this proves",
                "What this does not prove",
                "hostile same-UID",
            )
        )
        and all(
            token in rev0963_notes
            for token in (
                "restart-discoverable",
                "anonsync.peer-service.status.v10",
                "filesystem-cold",
                "quarantine-list",
                "readiness prerequisite",
                "user-restorable version history",
                "Nonclaims",
                "structural audit",
            )
        )
        and "VALIDATION_PENDING_REV0963" not in rev0963_notes
        and verifier.count(
            "if revision_number is not None and revision_number >= 963:"
        ) == 1
        and all(
            token in rev0963_verifier_block
            for token in (
                "RESTART_DISCOVERABLE_QUARANTINE_INVENTORY_AUDIT_rev0963.md",
                "REVISION_NOTES_rev0963.md",
                "src/anonsync_sync.cpp",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_folder_wake.py",
                "tools/audit_sync_file_payload_store.py",
            )
        ),
        "rev0963_records_discoverability_no_second_scan_nonclaims_validation_and_package_binding",
        "the revision record binds the exact cached-observation boundary, status v10, rejected duplicate list path, runtime proof, research distinction from user versions, final validation, and mandatory package surface",
    )

    bounded_batch_reader = function_body(
        folder_observer,
        "read_next_sorted_component_batch_or_throw(",
    )
    resumable_directory_walk = last_function_body(
        folder_observer,
        "[[nodiscard]] WalkDisposition walk_directory_or_throw(\n"
        "    WalkContext& context,\n"
        "    int owned_descriptor,",
    )
    component_classifier = function_body(
        folder_observer,
        "walk_component_batch_until_directory_or_throw(",
    )
    complete_component_walk = function_body(
        folder_observer,
        "walk_complete_component_batch_or_throw(",
    )
    pending_directory_walk = function_body(
        folder_observer,
        "walk_pending_directory_or_throw(",
    )
    buffered_batch_owner = function_body(
        folder_observer,
        "class ScopedBufferedDirectoryComponentBatch final",
    )
    require(
        "kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch = 4096U"
        in folder_observer_h
        and all(
            token in bounded_batch_reader
            for token in (
                "::rewinddir(directory.get())",
                "std::vector<std::string> selected",
                "selected.reserve(maximum_components)",
                "const std::string_view component(entry->d_name)",
                "maximum_components == 0U",
                "selected.size() < maximum_components",
                "selected.emplace_back(component)",
                "std::push_heap(selected.begin(), selected.end())",
                "std::pop_heap(selected.begin(), selected.end())",
                "selected.back().assign(component.data(), component.size())",
                "std::sort_heap(selected.begin(), selected.end())",
                "batch.components = std::move(selected)",
                "batch.has_more = eligible_count >",
            )
        )
        and "read_sorted_components_or_throw" not in bounded_batch_reader,
        "resumable_directory_selection_retains_one_fixed_lexicographic_batch",
        "the shipping restartable observer scans every candidate but allocates basename strings only for the exact smallest 4096-name component prefix after its current in-directory boundary",
    )

    require(
        "#include <queue>" not in folder_observer
        and "std::priority_queue" not in folder_observer
        and bounded_batch_reader.count("std::vector<std::string> selected") == 1
        and bounded_batch_reader.count("selected.reserve(maximum_components)") == 1
        and bounded_batch_reader.count("batch.components = std::move(selected)") == 1
        and "batch.components.reserve(selected.size())" not in bounded_batch_reader
        and "batch.components.push_back(selected" not in bounded_batch_reader,
        "bounded_component_selection_uses_one_heap_vector_without_copy_out_buffer",
        "one reserved vector is the max-heap, in-place sorted output, and move-only batch payload; no priority-queue container or second O(K) copy-out vector coexists",
    )

    require(
        folder_observer.count(
            "read_sorted_components_or_throw(context, directory, parent_path)"
        ) == 1
        and all(
            token in component_classifier
            for token in (
                "lstat_child_or_throw",
                "increment_regular_file_count_or_throw",
                "handle_regular_file_or_throw",
                "result.directory.component = component",
                "result.directory.canonical_path = canonical_path",
                "sync_posix_open_directory_component_or_throw",
                "result.directory.descriptor = ScopedFd(opened.descriptor)",
            )
        )
        and all(
            token in pending_directory_walk
            for token in (
                "pending.descriptor.release()",
                "walk_directory_or_throw",
                "post-walk directory binding",
                "same_directory_identity",
            )
        )
        and "walk_component_batch_until_directory_or_throw" in complete_component_walk
        and "walk_pending_directory_or_throw" in complete_component_walk
        and "walk_complete_component_batch_or_throw" in resumable_directory_walk
        and "walk_component_batch_until_directory_or_throw" in resumable_directory_walk,
        "full_and_batched_walks_share_rooted_classification_and_rebinding",
        "the complete and resumable paths share one no-follow classifier and one descriptor-rooted recursive/rebinding boundary even though only the resumable path releases selected parent storage",
    )

    require(
        all(
            token in folder_observer
            for token in (
                "struct PendingDirectoryDescent final",
                "ScopedFd descriptor",
                "struct stat opened_status",
                "#include <exception>",
            )
        )
        and ordered(
            component_classifier,
            "result.directory.component = component",
            "result.directory.canonical_path = canonical_path",
            "sync_posix_open_directory_component_or_throw",
            "result.directory.descriptor = ScopedFd(opened.descriptor)",
            "result.directory.present = true",
        )
        and ordered(
            pending_directory_walk,
            "const struct stat opened_status = pending.opened_status",
            "pending.descriptor.release()",
            "post-walk directory binding",
            "same_directory_identity",
        ),
        "pending_directory_descent_owns_descriptor_across_all_throwing_boundaries",
        "component/path allocation precedes child acquisition and ScopedFd owns the opened child until recursive transfer, so allocation, recursion, or rebinding failure cannot leak a descriptor",
    )

    require(
        all(
            token in buffered_batch_owner
            for token in (
                "currently_buffered_directory_component_count",
                "peak_buffered_directory_component_batch_count",
                "peak_simultaneously_buffered_directory_component_count",
                "~ScopedBufferedDirectoryComponentBatch() noexcept",
                "std::terminate()",
            )
        )
        and ordered(
            resumable_directory_walk,
            "retained a resumable directory component batch before selection",
            "read_next_sorted_component_batch_or_throw",
            "ScopedBufferedDirectoryComponentBatch buffered_batch",
            "walk_component_batch_until_directory_or_throw",
            "std::vector<std::string>().swap(batch.components)",
            "buffered_batch.release()",
            "walk_pending_directory_or_throw",
            "after_component = std::move(result.directory.component)",
        )
        and "attempted to overlap resumable directory component batches"
            in buffered_batch_owner
        and ordered(
            folder_observer,
            "walk_directory_or_throw(context, root.release(), {}, 0U)",
            "context.currently_buffered_directory_component_count != 0U",
            "retained buffered directory components after traversal",
        )
        and "peak_simultaneously_buffered_directory_component_count" in folder_observer_h,
        "resumable_recursion_releases_parent_batch_before_child_selection",
        "the selected parent vector and its capacity are destroyed and retired from exact live accounting before recursion; the public boundary rejects any leaked accounting state",
    )

    require(
        ordered(
            bounded_batch_reader,
            "if (charge_entries) increment_entry_count_or_throw(context)",
            "if (!after_component.empty() && component <= after_component) continue",
        )
        and ordered(
            resumable_directory_walk,
            "std::uint64_t remaining_first_census_components = 0U",
            "bool first_census = true",
            "batch.eligible_component_count",
            "first_census = false",
            "batch.eligible_component_count !=",
            "remaining_first_census_components",
            "StoppedAtDirectoryCensusFrontier",
            "consumed_components > remaining_first_census_components",
            "remaining_first_census_components -= consumed_components",
            "context.summary.regular_file_count >=",
            "StoppedAtRegularFileCountFrontier",
        )
        and ordered(
            component_classifier,
            "increment_regular_file_count_or_throw(context, canonical_path)",
            "handle_regular_file_or_throw",
        ),
        "batch_rescans_preserve_capacity_and_exact_suffix_census_fence",
        "each directory charges its first complete non-dot census once, later rescans must match the exact remaining suffix cardinality before processing, and skipped regular files still count against whole-folder capacity",
    )

    require(
        all(
            token in normalized_prose(folder_observer_h)
            for token in (
                "directory_enumeration_pass_count",
                "peak_buffered_directory_component_batch_count",
                "peak_simultaneously_buffered_directory_component_count",
                "Parent batch storage is released before recursive descent",
                "aggregate remains bounded by one batch",
                "O(depth) path state",
                "These diagnostics",
                "authorize no deletion",
            )
        )
        and all(
            token in folder_observer_runtime
            for token in (
                "test_resumable_flat_directory_component_buffer",
                "test_resumable_recursive_walk_releases_ancestor_component_batches",
                "regular_file_count = sibling_file_count * 2U + 1U",
                "segment.directory_enumeration_pass_count == 5U",
                "peak_simultaneously_buffered_directory_component_count",
                "batch_limit",
                "test_resumable_parent_census_rejects_cross_boundary_rename",
                "fs::rename(root / \"z-later.dat\", root / \"a-moved.dat\")",
                "DirectoryCensusFrontier",
                "fresh_delivered == std::vector<std::string>",
                "test_resumable_directory_does_not_chase_post_census_insertions",
                "first.resume_after_path == boundary_name",
                "second_delivered.size() == inserted_file_count + 1U",
                "second.skipped_regular_file_count == batch_limit",
            )
        ),
        "compiled_regressions_bind_global_batch_peak_preorder_and_census_drift",
        "the 8191-file recursive fixture proves one simultaneous 4096-name peak and exact preorder, while cross-boundary rename and 4097+17 growth fixtures deny completion and resume from the last coherent cursor",
    )

    require(
        all(
            token in normalized_prose(bounded_directory_batch_design)
            for token in (
                "Heart of the mission",
                "The defect",
                "Corrected C++ shape",
                "Preserved traversal order",
                "Entry and file capacity accounting",
                "Root and directory authority",
                "Diagnostics without authority",
                "Mechanical regression",
                "Adjacent refactor findings",
                "Complexity and remaining waste",
                "What this proves",
                "What this does not prove",
                "O(N log K)",
                "one bounded batch for each active directory depth",
                "non-resumable complete observer",
                "point-in-time namespace snapshot",
                "non-growing processing budget",
                "unbounded rescan chase",
            )
        )
        and all(
            token in rev0964_notes
            for token in (
                "bounded max-heap selector",
                "std::string_view",
                "walk_component_batch_or_throw",
                "cursor-skipped regular files",
                "process-wide simultaneous-basename ceiling",
                "huge-tree qualification",
                "Nonclaims",
            )
        ),
        "rev0964_record_remains_an_honest_parent_boundary",
        "the sealed parent record preserves the per-batch claim and explicitly names the recursive-depth limitation corrected by rev0965",
    )

    require(
        "VALIDATION_PENDING_REV0964" not in rev0964_notes
        and "VALIDATION_PENDING_REV0964" not in readme
        and verifier.count(
            "if revision_number is not None and revision_number >= 964:"
        ) == 1
        and all(
            token in rev0964_verifier_block
            for token in (
                "BOUNDED_RESUMABLE_DIRECTORY_COMPONENT_BATCH_AUDIT_rev0964.md",
                "REVISION_NOTES_rev0964.md",
                "src/sync_replica_folder_observer.hpp",
                "src/sync_replica_folder_observer.cpp",
                "tests/sync_replica_folder_observer_test.cpp",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0964_final_validation_and_package_surface_remain_mandatory",
        "the parent source audit and package policy remain sealed while the child revision extends the same mandatory implementation surface",
    )

    require(
        all(
            token in normalized_prose(global_directory_batch_design)
            for token in (
                "Heart of the mission",
                "The defect",
                "Corrected C++ ownership shape",
                "Traversal-wide selected-name bound",
                "Exact parent resumption and preorder",
                "Census drift correction",
                "Mechanical regressions",
                "Adjacent audit and contamination correction",
                "Complexity and remaining waste",
                "What this proves",
                "What this does not prove",
                "one 4,096-name batch",
                "O(depth)",
                "O(N log K)",
                "directory_census_frontier",
                "point-in-time filesystem snapshot",
            )
        )
        and all(
            token in rev0965_notes
            for token in (
                "traversal-wide selected-basename limit",
                "descriptor-owning pending descent state",
                "peak_simultaneously_buffered_directory_component_count",
                "exact suffix-cardinality fence",
                "8,191 regular files",
                "4,096 rather than 8,192",
                "Adjacent contamination audit",
                "Nonclaims",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0965: one traversal-wide selected-name batch",
                "destroys the selected parent vector",
                "unconsumed first-census suffix count",
                "asynchronous filesystem sweep, not snapshot isolation",
            )
        ),
        "rev0965_records_global_name_bound_census_fence_cost_and_nonclaims",
        "the audit, revision record, and README bind the exact ownership change, moving-namespace fence, additional enumeration cost, contamination correction, and remaining product boundaries",
    )

    require(
        all(
            token not in replica_cli
            for token in (
                "int command_history(const Options& options)",
                "anonsync_replica history --manifest",
                "\"restorable\"",
            )
        )
        and "restore_retained_regular_file_or_throw" not in folder_scan
        and "restore_retained_regular_file_or_throw" not in folder_scan_h
        and "test_retained_version_restore_reuses_payload_and_resurrects_delete"
            not in folder_scan_runtime,
        "discarded_retained_version_prototype_is_absent_from_rev0965",
        "the unrelated folder-owner and replica-CLI prototype is excluded so this revision cannot silently ship an unreviewed history/restore surface",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 965:"
        ) == 1
        and all(
            token in rev0965_verifier_block
            for token in (
                "GLOBAL_RESUMABLE_DIRECTORY_BATCH_LIFETIME_AUDIT_rev0965.md",
                "REVISION_NOTES_rev0965.md",
                "src/sync_replica_folder_observer.hpp",
                "src/sync_replica_folder_observer.cpp",
                "tests/sync_replica_folder_observer_test.cpp",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0965_package_policy_binds_every_changed_product_surface",
        "the release verifier makes the implementation, regression, audit, revision record, structural audit, and package-policy change mandatory from rev0965 onward",
    )

    require(
        all(
            token in historical_query_h + folder_scan_h
            for token in (
                "kSyncReplicaHistoricalVersionDefaultMaximumEntries = 64U",
                "kSyncReplicaHistoricalVersionMaximumEntries = 1024U",
                "struct SyncReplicaHistoricalVersionEntry final",
                "struct SyncReplicaHistoricalVersionInventory final",
                "struct SyncReplicaHistoricalVersionRestoreResult final",
                "inspect_historical_versions_or_throw(",
                "restore_historical_version_or_throw(std::string operation_id)",
                "retention promise",
                "never reactivates",
            )
        ),
        "rev0966_history_api_is_explicit_bounded_and_nonretentive",
        "the evolved folder-owner API preserves rev0966's bounded causal-predecessor projection and exact restore operation without claiming chronology, retention, or a second synchronization engine",
    )

    require(
        all(
            token in historical_version_inspection
            for token in (
                "snapshot_or_throw()",
                "payload_snapshot->require_folder_or_throw",
                "SyncReplicaModel::restore_or_throw",
                "model.for_each_active_operation",
                "model.for_each_active_path",
                "std::binary_search",
                "inventory.entries.reserve",
                "std::push_heap",
                "std::pop_heap",
                "std::sort_heap",
                "inventory.truncated",
            )
        )
        and "model.all_operations()" not in historical_version_inspection
        and "model.visible_paths()" not in historical_version_inspection
        and all(
            token in model_h
            for token in (
                "template <typename Visitor>",
                "void for_each_active_operation",
                "void for_each_active_path",
                "visitor(found->second)",
                "must not mutate this model",
                "O(active operations) copy",
            )
        ),
        "rev0966_inspection_pays_explicit_authority_and_retains_only_bounded_projection",
        "inspection still performs complete payload and replica observation while bounded heaps and borrowed operation/path visitors avoid whole-response clones and repeated whole-model path scans",
    )

    require(
        all(
            token in historical_version_restore
            for token in (
                "validate_sync_replica_historical_version_restore_request_or_throw",
                "operation_by_id(operation_id)",
                "operation is already visible",
                "refuses an unresolved path conflict",
                "would not change current file bytes",
                "operation_matches_catalog_entry(current, *prior)",
                "begin_targeted_access_or_throw",
                "open_optional_payload_for_operation_or_throw",
                "guard_visible_state_at_digest_or_throw",
                "copy_sync_file_atomically_replace_expected_from_borrowed_descriptor_under_directory_or_throw",
                "copy_sync_file_atomically_create_new_from_borrowed_descriptor_under_directory_or_throw",
                "prepare_regular_file_bounded_for_policy_or_throw",
                "commit_prepared_regular_file_or_throw",
                "sync_replica_operation_supersedes(restored, current)",
                "did not publish the required new causal successor",
            )
        )
        and ordered(
            historical_version_restore,
            "snapshot_or_throw()",
            "begin_targeted_access_or_throw",
            "guard_visible_state_at_digest_or_throw",
            "publish_historical_bytes_or_throw()",
            "replica_guard->commit_or_throw()",
            "prepare_regular_file_bounded_for_policy_or_throw",
            "commit_prepared_regular_file_or_throw",
        ),
        "rev0966_restore_reproves_every_owner_and_mints_a_new_causal_successor",
        "the selected predecessor cannot bypass active-evidence, conflict, catalog, rooted-path, targeted-payload, replica-projection, atomic-publication, or ordinary local-mint cutpoints",
    )

    require(
        all(
            token in local_status_h
            for token in (
                '"versions\\n"',
                "rev0966 unbound compatibility frame",
                "historical_version_request",
                "complete_historical_version_request_or_throw",
                "history operations—including",
            )
        )
        and all(
            token in local_status
            for token in (
                'kHistoricalVersionsRequest = "versions\\n"',
                'kHistoricalVersionRestoreRequestPrefix =',
                '"restore "',
                "different_historical_version_pending",
                "historical-version completion is a future generation",
                'rejection_reason = "drain_requested"',
                "action_condition.notify_all()",
            )
        )
        and all(
            token in historical_version_socket_request
            for token in (
                "historical_version_generation",
                "historical_version_generation = generation",
                "historical_version_pending",
                "request_generation",
                "action_condition.notify_all()",
            )
        ),
        "rev0966_owner_socket_linearizes_history_generations_with_drain",
        "strict inspection and restore frames share the existing mutex-linearized action snapshot, coalesce exact work, reject changed pending work, and close admission at the drain seal",
    )

    require(
        all(
            token in historical_version_service_step
            for token in (
                "historical_version_pending()",
                "historical_version_started_generation = target_generation",
                "inspect_historical_versions_or_throw(",
                "historical_version_query",
                "restore_historical_version_or_throw",
                "SyncReplicaFilePayloadStoreIntegrityError",
                "SyncReplicaFilePayloadStoreLeaseBusyError",
                "historical_version_last_failure = error.what()",
                "historical_version_completed_generation = target_generation",
            )
        )
        and '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_status
            for token in (
                "historical_versions",
                "append_historical_version_status",
                "historical_version_requests_observed",
                "historical_version_inspections",
                "historical_version_restores",
                "historical_version_failures",
            )
        )
        and all(
            token in sync_cli
            for token in (
                "int command_versions(const Options& options)",
                "int command_restore(const Options& options)",
                "validate_sync_replica_historical_version_restore_request_or_throw",
                "render_sync_replica_peer_service_historical_version_status_json",
            )
        ),
        "rev0966_service_status_and_cli_form_one_surviving_operator_path",
        "the retained daemon still schedules inspection and restore through one typed failure/retry path, now exposed through the backward-evolved v12 live/terminal status contract",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "test_historical_version_inspection_and_causal_restore",
                "test_historical_version_restore_from_tombstone",
                "deleted-version restore did not create exact bytes under one new causal successor",
                "historical-version inspection did not report one bounded retained predecessor",
                "historical-version restore reactivated old evidence instead of minting one causal successor",
                "historical-version inspection did not bound, order, or cursor superseded causal values deterministically",
                "historical-version restore accepted the current visible operation",
                "historical-version restore minted a duplicate value over identical current bytes",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "same historical inspection must coalesce by generation",
                "different_historical_version_pending",
                "historical completion accepted a future generation",
                "historical inspection serialized after drain must be rejected",
                "historical restore must reject a socket without exact mode 0600",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "owner-only historical-version inspection",
                "historical-version predecessor was not exactly",
                "owner-only exact historical-version restore",
                "historical-version restore did not converge exact v1 bytes",
                '"historical_version_inspections": 6',
                '"historical_version_restores": 1',
                '"historical_version_failures": 2',
            )
        ),
        "rev0966_compiled_and_process_regressions_bind_exact_discovery_restore_and_peer_convergence",
        "the evolved focused and two-peer process regressions retain exact predecessor discovery, distinct successor minting, authenticated reconvergence, and explicit action accounting",
    )

    require(
        all(
            token in normalized_prose(causal_version_design)
            for token in (
                "Heart of the mission",
                "The operability gap",
                "Product boundary",
                "What an inventory entry means",
                "Explicit inspection, not status-time traversal",
                "Adjacent projection refactor",
                "Exact restore authority path",
                "Failure and crash semantics",
                "Service scheduling and status v11",
                "Mechanical regressions",
                "Audit/refactor findings",
                "Complexity and remaining waste",
                "What this proves",
                "What this does not prove",
                "not a wall-clock date",
                "O(requested entries)",
                "ordinary scanner",
                "garbage collection",
            )
        )
        and all(
            token in normalized_prose(rev0966_notes)
            for token in (
                "owner-only linked-peer service",
                "default 64-entry and hard 1,024-entry",
                "borrowed immutable active-operation visitor",
                "new causal successor",
                "anonsync.peer-service.status.v11",
                "Nonclaims",
                "all 258/258 registered tests",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0966: bounded causal versions and rooted restore",
                "anonsync_sync versions",
                "anonsync_sync restore",
                "ordinary status polling remains filesystem-cold",
                "new causal successor",
                "not yet Resilio-style Archive UX",
            )
        ),
        "rev0966_records_the_operable_slice_cost_crash_boundary_and_nonclaims",
        "the audit, revision record, and README distinguish causal predecessor recovery from chronology, retention, collection, conflict resolution, and cross-owner atomicity",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 966:"
        ) == 1
        and all(
            token in rev0966_verifier_block
            for token in (
                "EXPLICIT_CAUSAL_VERSION_INSPECTION_AND_ROOTED_RESTORE_AUDIT_rev0966.md",
                "REVISION_NOTES_rev0966.md",
                "src/anonsync_sync.cpp",
                "src/sync_local_status_socket.hpp",
                "src/sync_replica_model.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0966_package_policy_binds_every_history_surface",
        "the release verifier makes the CLI, action lane, model refactor, folder authority, service/status, C++ regressions, process oracle, audit, and revision records mandatory from rev0966 onward",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "struct SyncReplicaHistoricalVersionQuery final",
                "maximum_entries",
                "canonical_path",
                "start_after_operation_id",
                "kSyncReplicaHistoricalVersionMaximumEntries = 1024U",
                "kSyncReplicaHistoricalVersionMaximumCanonicalPathBytes = 4096U",
                "validate_sync_relative_path",
                "is_lowercase_sha256_hex",
            )
        ),
        "rev0967_query_contract_is_explicit_canonical_and_independently_bounded",
        "path, cursor, and page size are one reusable validated owner query rather than ad hoc CLI or socket parsing state",
    )

    require(
        all(
            token in historical_version_inspection
            for token in (
                "cursor is not one active file operation",
                "cursor is outside the selected path",
                "cursor is no longer superseded",
                "historical_file_operation_count_after_cursor",
                "next_start_after_operation_id",
                "model.for_each_active_path",
                "std::push_heap",
                "std::pop_heap",
                "std::sort_heap",
            )
        )
        and "model.visible_path(operation.canonical_path)" not in historical_version_inspection
        and all(
            token in folder_scan_runtime
            for token in (
                "historical-version cursor did not expose the exact deterministic second page",
                "path-scoped historical inspection did not expose the complete selected history",
                "historical-version inspection accepted a cursor from another path scope",
                "historical-version inspection accepted a now-visible cursor",
                "historical-version inspection accepted a malformed cursor",
            )
        ),
        "rev0967_pagination_is_exact_bounded_and_stale_cursor_fail_closed",
        "the folder owner returns a canonical bounded suffix, exposes its exact next tail, and refuses cursor semantics that no longer match current causal evidence",
    )

    require(
        all(
            token in model_h + model
            for token in (
                "template <typename Visitor>",
                "for_each_active_path",
                "ordered_active_operations_by_path",
                "std::vector<const SyncReplicaOperation*> ordered",
                "maximum_covered_counter",
                "candidate->causal_context",
            )
        )
        and "sync_replica_operation_supersedes(" in network_model_runtime
        and "*other, *candidate" in network_model_runtime
        and "operations.size() == 258U" in network_model_runtime
        and "causal-coverage projection diverged from pairwise supersession" in network_model_runtime,
        "rev0967_grouped_projection_removes_repeated_whole_model_and_pairwise_work",
        "one sorted borrowed-pointer traversal and one actor-coverage aggregate replace the quadratic projection while a 258-operation differential oracle retains the old semantic definition",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                "MODE LIMIT PATH_HEX CURSOR SOURCE_CUTPOINT_OR_DASH",
                "kHistoricalVersionsQueryRequestPrefix",
                "anonsync.local-historical-versions.response.v5",
                "kMaximumRequestBytes = 16U * 1024U",
                "field_count != 3U && field_count != 4U && field_count != 5U",
                "historical_version_pending->query != query",
                "request_sync_local_status_historical_versions_query_or_throw",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "path-scoped cursor page must return exact acceptance",
                "same historical inspection must coalesce by generation",
                "a different history page must not overwrite pending work",
                "historical query client accepted a zero entry limit",
                "historical query client accepted a non-canonical path",
                "historical query client accepted a malformed cursor",
                "query must reject a socket without exact mode 0600",
            )
        ),
        "rev0967_owner_socket_binds_exact_query_identity_and_pid_bound_echo",
        "the strict lowercase-hex frame, bounded request, exact response echo, request equality, completion, mode checks, and peer PID remain in one existing action lane",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_status + historical_inventory_json
            for token in (
                "append_historical_version_query",
                "historical_file_operation_count_after_cursor",
                "next_start_after_operation_id",
                "status.query",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "owner-only historical-version first page",
                "owner-only historical-version second page",
                "historical-version first page omitted its exact tail cursor",
                "historical-version second page did not settle the exact",
                '"historical_version_inspections": 6',
                '"historical_version_restores": 1',
            )
        ),
        "rev0967_service_status_and_real_process_make_every_bounded_page_reachable",
        "v12 carries the exact retained query and page continuation through live and terminal status while one real two-peer service proves inspection, restore, first-page truncation, and second-page completion",
    )

    require(
        all(
            token in normalized_prose(paged_history_design)
            for token in (
                "bounded output, quadratic work",
                "Owner query contract",
                "Pagination semantics",
                "Service and status integration",
                "Contamination correction",
                "retains reconciliation protocol generation 2",
                "What this does not prove",
            )
        )
        and all(
            token in normalized_prose(rev0967_notes)
            for token in (
                "quadratic",
                "versions-query",
                "anonsync.peer-service.status.v12",
                "unsealed protocol-generation-3 branch",
                "operation-before-bytes invariant",
                "Nonclaims",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0967: paged causal history and grouped projection",
                "--path CANONICAL_RELATIVE_PATH",
                "--after LOWERCASE_SHA256",
                "next_start_after_operation_id",
                "not chronology",
            )
        )
        and "anonsync-sync-replica-reconciliation-request-frame-v9" in reconciliation_protocol_cpp
        and "delta_manifest" in reconciliation_protocol_cpp
        and "metadata-only history pages" not in reconciliation_service_h
        and "test_superseded_missing_payload_transfers_as_metadata_without_store_scan" not in reconciliation_runtime,
        "rev0967_records_scaling_fix_nonclaims_and_excludes_discarded_metadata_only_protocol",
        "the visible records bind the actual paging/projection slice and mechanically exclude the discarded metadata-only history-page transfer prototype while permitting the later content-defined delta and selective-sync protocol generation",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 967:"
        ) == 1
        and all(
            token in rev0967_verifier_block
            for token in (
                "PAGED_CAUSAL_VERSION_QUERY_AND_GROUPED_PROJECTION_AUDIT_rev0967.md",
                "REVISION_NOTES_rev0967.md",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_model.cpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_replica_network_model_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/audit_sync_replica_sqlite_owner.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0967_package_policy_binds_every_paging_and_projection_surface",
        "the release verifier requires the query, model, folder owner, socket, service/status, tests, process oracle, audit, records, and package policy from rev0967 onward",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "struct SyncReplicaHistoricalVersionSourceCutpoint final",
                "operation_set_digest",
                "payload_snapshot_digest",
                'return "v1:" + cutpoint.operation_set_digest',
                "constexpr std::size_t encoded_size",
                "token.starts_with(exact_v1_prefix)",
                "enum class SyncReplicaHistoricalVersionSourceChangeStage",
                "OperationSetBeforePayloadObservation",
                "OperationSetDuringPayloadObservation",
                "PayloadSnapshot",
                "class SyncReplicaHistoricalVersionSourceChangedError final",
                "expected_source_cutpoint",
            )
        )
        and historical_query_h.count(
            "validate_sync_replica_historical_version_source_cutpoint_or_throw"
        ) >= 3,
        "rev0968_source_cutpoint_is_one_strict_versioned_causal_and_payload_token",
        "one canonical 132-byte v1 token binds exact operation-set and payload-snapshot digests, validates at the shared query boundary, and carries typed drift stages",
    )

    require(
        ordered(
            historical_version_inspection,
            "state_->replica_owner->snapshot_or_throw()",
            "expected_source_cutpoint->operation_set_digest",
            "SyncReplicaModel::restore_or_throw",
            "cursor is no longer superseded",
            "state_->payload_store->snapshot_or_throw()",
            "state_->replica_owner->snapshot_or_throw()",
            "OperationSetDuringPayloadObservation",
            "expected_source_cutpoint->payload_snapshot_digest",
            "PayloadSnapshot",
            "inventory.source_operation_set_digest",
        )
        and "replica_snapshot.state_generation !=" not in historical_version_inspection
        and "replica_snapshot.state_generation ==" not in historical_version_inspection,
        "rev0968_bound_pagination_rejects_known_stale_sources_before_payload_work_and_brackets_the_scan",
        "the exact operation-set pin and semantic cursor are checked before the complete payload observation, a second operation-set digest fences intervening causal change, and unrelated state-generation writes cannot manufacture drift",
    )

    require(
        all(
            token in folder_scan_h + peer_status + historical_inventory_json
            for token in (
                "source_operation_set_digest",
                "source_cutpoint()",
                "source_payload_snapshot_digest",
                r'\"source_cutpoint\"',
                r'\"expected_source_cutpoint\"',
            )
        )
        and '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_status
            for token in (
                "last_failure_class",
                "last_source_change_stage",
                "sync_replica_peer_service_historical_version_failure_class_name",
                "sync_replica_historical_version_source_change_stage_name",
                "historical_version_failure_class",
                "historical_version_source_change_stage",
            )
        ),
        "rev0968_source_identity_and_typed_drift_survive_the_evolved_status_schema",
        "live and terminal status render the bound query, canonical source token, exact causal digest, failure class, and source-change stage from cached owner state",
    )

    require(
        ordered(
            historical_version_service_step,
            "historical_version_last_failure_class.reset()",
            "inspect_historical_versions_or_throw(",
            "catch (const SyncReplicaHistoricalVersionSourceChangedError& error)",
            "SourceChanged",
            "historical_version_last_source_change_stage = error.stage()",
            "catch (const std::runtime_error& error)",
            "OperationFailed",
        )
        and all(
            token in peer_service_h
            for token in (
                "SyncReplicaPeerServiceHistoricalVersionFailureClass",
                "OperationFailed",
                "SourceChanged",
                "last_failure_class",
                "last_source_change_stage",
            )
        ),
        "rev0968_service_classifies_source_drift_without_parsing_prose_or_terminating",
        "typed source change clears stale results, records its exact stage, and remains distinct from ordinary operator failure in the existing serialized action lane",
    )

    require(
        all(
            token in local_status
            for token in (
                "anonsync.local-historical-versions.response.v5",
                "std::array<std::string_view, 5U> fields",
                "field_count != 3U && field_count != 4U && field_count != 5U",
                "decode_sync_replica_historical_version_source_cutpoint_or_throw",
                'response << ",\\\"expected_source_cutpoint\\\":"',
                "source_cutpoint.size()",
            )
        )
        and all(
            token in sync_cli
            for token in (
                '"source-cutpoint"',
                "decode_sync_replica_historical_version_source_cutpoint_or_throw",
                "v1:OPERATION_SET_SHA256:PAYLOAD_SHA256|",
            )
        ),
        "rev0968_owner_socket_and_cli_carry_the_exact_token_with_rev0967_request_compatibility",
        "the strict frame accepts either the old three-field form or one canonical fourth source token, echoes it in v3, and exposes it through the shipping versions command",
    )

    stale_scan_oracle = function_body(
        runtime,
        "void test_complete_scan_restarts_one_stale_payload_observation()",
    )
    require(
        ordered(
            stale_scan_oracle,
            "write_byte_without_sync(changed)",
            "write_byte_without_sync(original)",
            "::fsync(payload_descriptor)",
        )
        and stale_scan_oracle.count("::fsync(payload_descriptor)") == 1,
        "rev0968_stale_scan_oracle_does_not_publish_a_transient_corrupt_retry_input",
        "the deterministic race restores byte zero before its sole local durability cutpoint, retaining metadata drift without asking production to ignore a current digest mismatch",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "historical-version source cutpoint did not round-trip canonically",
                "changed historical payload namespace did not fail a bound continuation",
                "stale historical-version source pin did not fail closed before payload observation",
                "OperationSetBeforePayloadObservation",
                "PayloadSnapshot",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "historical_source_token",
                "expected_source_cutpoint",
                "historical query client accepted a malformed source cutpoint",
                "path-scoped cursor page must return exact acceptance",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "is_canonical_historical_source_cutpoint",
                "source_operation_set_digest",
                "historical-version first page omitted its exact source cutpoint",
                '"--source-cutpoint", page_source_cutpoint',
                "owner-only stale historical source cutpoint",
                "operation_set_before_payload_observation",
                '"historical_version_failures": 2',
                "typed historical source drift terminated the service",
                "matching historical step omitted exact ",
                "source drift:",
                "historical_version_generation",
                "historical_version_failure_class",
                "historical_version_source_change_stage",
                '"schema": "anonsync.peer-service.status.v26"',
                '"schema": "anonsync.local-historical-versions.response.v5"',
            )
        )
        and '"anonsync.peer-service.status.v26"' in service_i2p_ingress_runtime,
        "rev0968_regressions_bind_token_codec_payload_drift_causal_drift_and_real_service_continuation",
        "focused C++ tests and real process oracles cover canonical framing, both externally inducible drift classes, exact page-token reuse, stable retained failure evidence, transient matching-step coherence, current schemas, and route status compatibility",
    )

    require(
        all(
            token in normalized_prose(source_cutpoint_design)
            for token in (
                "Defect found",
                "Source-cutpoint contract",
                "Why these two digests",
                "Observation order and wasted-work correction",
                "Typed source drift",
                "Research context",
                "What this does not prove",
            )
        )
        and all(
            token in normalized_prose(rev0968_notes)
            for token in (
                "--source-cutpoint",
                "anonsync.peer-service.status.v13",
                "anonsync.local-historical-versions.response.v3",
                "state_generation",
                "Nonclaims",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0968: exact causal-history page source",
                "source_cutpoint",
                "operation_set_digest",
                "source_changed",
                "exact browse consistency",
            )
        ),
        "rev0968_records_the_consistency_hole_cost_correction_and_product_nonclaims",
        "the design audit, revision notes, and README explain why the token binds operation and payload inputs, why stale causal sources fail before the payload scan, and why this is not retention or a cross-owner transaction",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 968:"
        ) == 1
        and all(
            token in rev0968_verifier_block
            for token in (
                "EXACT_CAUSAL_HISTORY_SOURCE_CUTPOINT_AUDIT_rev0968.md",
                "REVISION_NOTES_rev0968.md",
                "src/anonsync_sync.cpp",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_peer_service.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0968_package_policy_binds_every_source_cutpoint_surface",
        "the release verifier requires the token contract, owner implementation, service/status, CLI/socket, regressions, process oracles, audit, records, and package policy from rev0968 onward",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "struct SyncReplicaHistoricalVersionRestoreRequest final",
                "std::string operation_id",
                "std::optional<std::string> expected_current_operation_id",
                "validate_sync_replica_historical_version_restore_request_or_throw",
                "expected current operation ID is invalid",
                "historical and expected current operation IDs are equal",
                "RestoreCurrentOperation = 4U",
                'return "restore_current_operation"',
            )
        )
        and "bool operator==(const SyncReplicaHistoricalVersionRestoreRequest&) const" in historical_query_h,
        "rev0969_restore_intent_is_one_strict_shared_value_object",
        "one canonical historical/current operation pair validates once and carries typed stale-current classification across every product layer",
    )

    require(
        ordered(
            historical_version_restore,
            "validate_sync_replica_historical_version_restore_request_or_throw",
            "state_->replica_owner->snapshot_or_throw()",
            "model_before.operation_by_id(operation_id)",
            "model_before.visible_path(historical.canonical_path)",
            "if (request.expected_current_operation_id.has_value())",
            "RestoreCurrentOperation",
            "validate_canonical_path_for_root_or_throw",
            "const SyncReplicaFolderCatalogSnapshot catalog_before",
            "observe_current_or_throw()",
            "begin_targeted_access_or_throw",
            "guard_visible_state_at_digest_or_throw",
            "publish_historical_bytes_or_throw()",
            "replica_guard->commit_or_throw()",
            "commit_prepared_regular_file_or_throw",
        )
        and "visible_operation_ids.size() == 1U" in historical_version_restore
        and "primary_operation_id ==" in historical_version_restore
        and historical_version_restore.count("RestoreCurrentOperation") >= 2,
        "rev0969_stale_current_fails_before_later_mutable_authority_and_restore_keeps_late_fences",
        "the path-local precondition is proved from the immutable causal snapshot before catalog, rooted-path, or payload access while the existing projection guard and ordinary mint remain publication authority",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                '"restore-exact OPERATION_ID EXPECTED_CURRENT_OPERATION_ID\\n"',
                'kHistoricalVersionRestoreExactRequestPrefix =',
                '"restore-exact "',
                "anonsync.local-historical-version-restore.response.v2",
                "request_sync_local_status_historical_version_restore_exact_or_throw",
                "historical_version_pending->restore_request !=",
                "different_historical_version_pending",
            )
        )
        and all(
            token in sync_cli
            for token in (
                '"expected-current"',
                "options.one(\"expected-current\")",
                "request_sync_local_status_historical_version_restore_exact_or_throw",
                "--expected-current LOWERCASE_SHA256",
            )
        )
        and 'kHistoricalVersionRestoreRequestPrefix =\n    "restore "' in local_status,
        "rev0969_shipping_cli_uses_exact_frame_while_legacy_owner_frame_remains_explicit",
        "the product command always emits the v2 two-ID frame, strict parsing and PID-bound echo cover both fields, and only the documented owner-only compatibility frame remains unbound",
    )

    require(
        all(
            token in peer_service_h + peer_service
            for token in (
                "SyncReplicaHistoricalVersionRestoreRequest restore_request",
                "historical_version_restore_request",
                "historical_version_restore_request != restore_request",
                "restore_historical_version_or_throw(\n                            historical_version_restore_request)",
                "SyncReplicaHistoricalVersionSourceChangedError",
                "historical_version_last_source_change_stage = error.stage()",
            )
        )
        and all(
            token in peer_status
            for token in (
                "append_historical_version_restore_request",
                r'\"expected_current_operation_id\"',
                r'\"historical_version_restore_request\"',
                "status.restore_request.operation_id",
            )
        )
        and '"anonsync.peer-service.status.v26"' in peer_status_h,
        "rev0969_full_restore_identity_controls_coalescing_execution_and_status",
        "a different expected head cannot coalesce with pending work, and stable plus matching transient status retain the exact request and typed source-change stage",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "stale exact-current restore reported the wrong source-change stage",
                "stale exact-current restore reached payload authority or changed durable/file state",
                "begin_mutation_batch_or_throw",
                "expected current operation ID is invalid",
                "historical and expected current operation IDs are equal",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "request_sync_local_status_historical_version_restore_exact_or_throw",
                "anonsync.local-historical-version-restore.response.v2",
                "a different exact restore must not replace pending authority",
                "exact historical restore client accepted equal historical and current IDs",
                "rev0966 unbound restore frame was not retained as a distinct request",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                '"--expected-current"',
                "restore_current_operation",
                "stale exact-current historical restore",
                "stale exact-current restore terminated the service",
                '"schema": "anonsync.peer-service.status.v26"',
                '"expected_current_operation_id"',
                '"historical_version_restore_request"',
            )
        )
        and '"anonsync.peer-service.status.v26"' in service_i2p_ingress_runtime,
        "rev0969_regressions_prove_no_payload_work_full_request_coalescing_and_same_pid_stale_failure",
        "focused C++ and real-process oracles mechanically distinguish the early stale fence from lease access, cover strict framing, and prove the daemon survives a replayed stale operator intent",
    )

    require(
        all(
            token in normalized_prose(exact_current_restore_design)
            for token in (
                "Product defect",
                "Exact-current contract",
                "Why operation identity, not file bytes",
                "Authority order",
                "Typed failure and operator evidence",
                "Adjacent refactor",
                "Regression strategy",
                "Nonclaims and next edge",
                "RFC 9110",
                "Syncthing",
            )
        )
        and all(
            token in normalized_prose(rev0969_notes)
            for token in (
                "--expected-current",
                "restore-exact",
                "restore_current_operation",
                "anonsync.peer-service.status.v14",
                "compatibility",
                "Nonclaims",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0969: exact-current-bound historical restore",
                "current_primary_operation_id",
                "compare-and-restore",
                "restore_current_operation",
                "unbound local frame",
            )
        ),
        "rev0969_records_lost_update_correction_scope_compatibility_and_nonclaims",
        "the design audit, revision notes, and README explain the exact path-local validator, retained publication cutpoints, explicit compatibility exception, research context, and version-lifecycle work still missing",
    )

    exact_publication_temp_tokens = (
        '_PUBLICATION_TEMP_PREFIX = ".anonsync-publish-v1-"',
        '_PUBLICATION_TEMP_SUFFIX = ".tmp"',
        'len(body) != 50 or body[16] != "-" or body[33] != "-"',
        'byte in "0123456789abcdef"',
        'publication_temp_basename_is_exact(path.name)',
        'stream.read(1024 * 1024)',
    )
    require(
        all(token in sync_process_runtime for token in exact_publication_temp_tokens)
        and all(
            token in reconciliation_process_runtime
            for token in exact_publication_temp_tokens
        )
        and "path.read_bytes()" not in sync_process_runtime
        and all(
            token in normalized_prose(exact_current_restore_design)
            for token in (
                "process registry",
                "atomic-publication temporary",
                "bounded 1 MiB streaming SHA-256",
                "Broad dotfile suppression",
            )
        ),
        "rev0969_process_tree_oracles_exclude_only_exact_internal_publication_temporaries",
        "both live-process tree comparators mirror the product's exact internal temporary-name grammar, and the sync-once oracle hashes large files without whole-file allocation",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 969:"
        ) == 1
        and all(
            token in rev0969_verifier_block
            for token in (
                "EXACT_CURRENT_BOUND_HISTORICAL_RESTORE_AUDIT_rev0969.md",
                "REVISION_NOTES_rev0969.md",
                "src/anonsync_sync.cpp",
                "src/sync_local_status_socket.hpp",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_peer_service.hpp",
                "src/sync_replica_peer_service.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
                "tools/test_anonsync_sync_process.py",
                "tools/test_anonsync_replica_reconciliation_process.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0969_package_policy_binds_every_exact_current_restore_surface",
        "the release verifier requires the shared request, owner, CLI/socket, service/status, focused and process regressions, audit, records, and package policy from rev0969 onward",
    )

    require(
        "second unsealed rev0969 tree" in normalized_prose(exact_current_restore_design)
        and "divergent unsealed rev0969 worktree/build" in normalized_prose(rev0969_notes)
        and "SyncReplicaHistoricalVersionTargetChangedError" not in historical_query_h
        and "restore_target_operation" not in historical_query_h,
        "rev0969_divergent_unsealed_design_is_recorded_and_excluded",
        "the surviving source uses the shared source-changed taxonomy and explicitly excludes the discarded parallel target-changed branch from release authority",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "enum class SyncReplicaHistoricalVersionInspectionMode",
                "ExactPayloadAvailability = 1U",
                "CausalMetadataOnly = 2U",
                'return "exact_payload_availability"',
                'return "causal_metadata_only"',
                "sync_replica_historical_version_inspection_mode_from_name_or_throw",
                "inspection mode is invalid",
            )
        )
        and historical_query_h.count(
            "SyncReplicaHistoricalVersionInspectionMode inspection_mode"
        ) >= 2,
        "rev0970_one_shared_mode_type_defines_exact_and_causal_metadata_authority",
        "the query and source cutpoint consume one canonical two-value authority type and one name/parser vocabulary instead of duplicating CLI, socket, service, and JSON mode strings",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                'constexpr std::string_view exact_v1_prefix = "v1:"',
                'constexpr std::string_view metadata_prefix = "v2:metadata:"',
                "std::optional<std::string> payload_snapshot_digest",
                "metadata-only cutpoint carries an exact-mode digest",
                "expected source cutpoint mode does not match the query",
                "token.starts_with(exact_v1_prefix)",
                "token.starts_with(metadata_prefix)",
            )
        )
        and 'return "v1:" + cutpoint.operation_set_digest' in historical_query_h
        and 'return "v2:metadata:" + cutpoint.operation_set_digest'
        in historical_query_h,
        "rev0970_source_cutpoints_preserve_exact_v1_and_mode_bind_metadata_v2",
        "exact callers keep the rev0968 operation-plus-payload token byte-for-byte while metadata callers receive a payload-free tagged token that cannot cross inspection modes",
    )

    require(
        historical_version_inspection.count(
            "state_->payload_store->snapshot_or_throw()"
        ) == 1
        and ordered(
            historical_version_inspection,
            "state_->replica_owner->snapshot_or_throw()",
            "SyncReplicaModel::restore_or_throw",
            "if (query.inspection_mode ==",
            "ExactPayloadAvailability",
            "state_->payload_store->snapshot_or_throw()",
            "payload_snapshot->require_folder_or_throw",
            "inventory.source_payload_snapshot_digest",
        )
        and all(
            token in historical_version_inspection
            for token in (
                "std::optional<SyncReplicaFilePayloadStoreSnapshot> payload_snapshot",
                "if (payload_snapshot.has_value())",
                "std::optional<bool> payload_present",
                "std::optional<bool> restore_ready",
            )
        ),
        "rev0970_metadata_projection_stops_before_the_only_payload_owner_call",
        "the immutable replica snapshot and causal projection are shared, but the sole complete payload observation and every availability derivation remain inside the explicit exact-mode branch",
    )

    require(
        folder_scan_h.count("std::optional<bool>") >= 2
        and "std::optional<std::string> source_payload_snapshot_digest"
        in folder_scan_h
        and folder_scan_h.count("std::optional<std::uint64_t>") >= 6
        and all(
            token in historical_inventory_json
            for token in (
                "void append_optional_bool(",
                "append_optional_uint64(output, inventory.payload_present_count)",
                "append_optional_uint64(output, inventory.restore_ready_count)",
                "append_optional_bool(output, entry.payload_present)",
                "append_optional_bool(output, entry.restore_ready)",
            )
        ),
        "rev0970_unknown_payload_evidence_is_optional_at_the_cpp_boundary",
        "metadata browsing cannot collapse unobserved byte availability into false or zero because payload digests, scan counters, aggregate counts, and per-entry booleans are optional before JSON rendering",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                "MODE LIMIT PATH_HEX CURSOR SOURCE_CUTPOINT_OR_DASH",
                "exact_payload_availability or causal_metadata_only",
                "field_count != 3U && field_count != 4U && field_count != 5U",
                "sync_replica_historical_version_inspection_mode_from_name_or_throw",
                "anonsync.local-historical-versions.response.v5",
                'response << ",\\\"inspection_mode\\\":"',
            )
        )
        and all(
            token in sync_cli
            for token in (
                '"inspection-mode"',
                'options.one_or("inspection-mode", "exact")',
                'inspection_mode == "metadata"',
                "--inspection-mode must be exact or metadata",
                "[--inspection-mode exact|metadata]",
            )
        )
        and '"anonsync.peer-service.status.v26"' in peer_status_h,
        "rev0970_cli_socket_and_status_share_one_mode_bearing_contract",
        "the shipping default remains exact, new clients send one canonical five-field request, legacy three/four-field requests remain exact, and live plus terminal status advance together",
    )

    require(
        "bool operator==(const SyncReplicaHistoricalVersionQuery&) const = default"
        in historical_query_h
        and "historical_version_pending->query != query" in local_status
        and all(
            token in peer_status + historical_inventory_json
            for token in (
                "append_historical_version_query",
                "sync_replica_historical_version_inspection_mode_name(",
                'output << "{\\\"inspection_mode\\\":"',
            )
        ),
        "rev0970_mode_participates_in_action_identity_and_canonical_status",
        "an exact request cannot coalesce with a metadata request sharing path, limit, cursor, and token because mode is a first-class member of the defaulted query equality and retained status",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "test_historical_version_metadata_only_is_payload_cold",
                "unexpected-history-inspection-entry",
                "metadata-only history inspection fabricated payload authority",
                "metadata-only source cutpoint was not mode-bound and canonical",
                "metadata-only source cutpoint did not reproduce the causal page",
                "unexpected payload-root entry",
                "metadata-only inspection accepted an exact-payload source cutpoint",
            )
        ),
        "rev0970_folder_owner_regression_mechanically_separates_metadata_from_payload_authority",
        "an unexpected private payload-root entry makes exact inspection fail while metadata inspection returns the same causal page with disengaged payload evidence and a round-tripped v2 cutpoint",
    )

    require(
        "candidate->payload_present == std::optional<bool>(true)" in folder_scan_runtime
        and "candidate->restore_ready == std::optional<bool>(true)" in folder_scan_runtime
        and "boolean context on `std::optional<bool>` tests engagement" in metadata_history_design,
        "rev0970_optional_boolean_test_oracle_checks_the_observed_value",
        "the adjacent restore regression compares engaged exact booleans with true rather than accepting any engaged optional value",
    )

    require(
        all(
            token in local_status_runtime
            for token in (
                "metadata history status socket",
                '\\"inspection_mode\\":\\"causal_metadata_only\\"',
                "metadata-only history query did not preserve its exact mode",
                "metadata-only history query was not retained as one action identity",
                "legacy exact query frame accepted a metadata-only cutpoint",
            )
        ),
        "rev0970_local_socket_regression_binds_mode_pid_token_and_legacy_rejection",
        "the owner-only test exercises canonical metadata framing and response echo, retains the complete query as pending identity, and proves an implicit exact legacy frame cannot accept a v2 token",
    )

    require(
        all(
            token in service_configuration_runtime
            for token in (
                '"--inspection-mode", "metadata"',
                "owner-only causal-metadata historical inspection",
                '"inspection_mode": "causal_metadata_only"',
                '"v4:metadata:"',
                "causal-metadata historical inspection fabricated",
                '"historical_version_inspections": 6',
                '"schema": "anonsync.peer-service.status.v26"',
                '"schema": "anonsync.local-historical-versions.response.v5"',
            )
        )
        and '"anonsync.peer-service.status.v26"'
        in service_i2p_ingress_runtime,
        "rev0970_shipping_process_oracles_require_null_payload_evidence_and_schema_coherence",
        "one real retained two-peer service executes the metadata CLI, publishes a v2 token and null payload facts, accounts the completed action, and keeps direct plus I2P status readers on v15",
    )

    require(
        all(
            token in normalized_prose(metadata_history_design)
            for token in (
                "Defect found",
                "Two explicit inspection authorities",
                "Unknown is not false",
                "Mode-bound source cutpoints",
                "Adjacent audit and refactor",
                "Research context",
                "What this does not prove",
            )
        )
        and all(
            token in normalized_prose(rev0970_notes)
            for token in (
                "--inspection-mode metadata",
                "anonsync.peer-service.status.v15",
                "anonsync.local-historical-versions.response.v4",
                "std::optional",
                "Compatibility",
                "Nonclaims",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0970: payload-cold causal-metadata history browsing",
                "v2:metadata:OPERATION_SET_SHA256",
                "Unknown is",
                "payload-cold",
                "not selective sync",
            )
        ),
        "rev0970_records_cost_authority_compatibility_research_and_nonclaims",
        "the design audit, revision notes, and README explain the avoided namespace scan, the null-evidence boundary, exact-mode compatibility, external product precedent, and the unfinished retention/selective-sync edges",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 970:"
        ) == 1
        and all(
            token in rev0970_verifier_block
            for token in (
                "CAUSAL_METADATA_HISTORY_INSPECTION_AUDIT_rev0970.md",
                "REVISION_NOTES_rev0970.md",
                "src/anonsync_sync.cpp",
                "src/sync_local_status_socket.hpp",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0970_package_policy_binds_every_metadata_history_surface",
        "the release verifier makes the shared types, owner branch, CLI/socket/status surfaces, focused and process regressions, records, structural audit, and package policy mandatory from rev0970 onward",
    )

    require(
        all(
            token in historical_inventory_json_h
            for token in (
                "kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes",
                "256U * 1024U",
                "append_sync_replica_historical_version_query_json",
                "append_sync_replica_historical_version_inventory_json",
                "render_sync_replica_historical_version_inventory_json",
                "bound_sync_replica_historical_version_inventory_for_status_or_throw",
            )
        )
        and all(
            token in historical_inventory_json
            for token in (
                "class CountingStreamBuffer final",
                "append_inventory(output, inventory, projection)",
                "inventory.entries.resize(accepted)",
                "inventory.next_start_after_operation_id =",
                "A byte frontier is truthful only when it actually omits",
            )
        )
        and "src/sync_replica_historical_version_inventory_json.cpp" in cmake,
        "rev0971_canonical_history_json_counts_and_emits_one_exact_bounded_contract",
        "one canonical streaming encoder performs both allocation-free exact counting and emission, with a 256-KiB status-page budget and no approximate size oracle",
    )

    require(
        all(
            token in folder_scan_h
            for token in (
                "entry_limit_frontier_reached",
                "status_byte_limit",
                "status_byte_frontier_reached",
            )
        )
        and "inventory.entry_limit_frontier_reached =" in folder_scan
        and "bound_sync_replica_historical_version_inventory_for_status_or_throw" in peer_service
        and peer_service.find(
            "bound_sync_replica_historical_version_inventory_for_status_or_throw"
        ) < peer_service.find("historical_version_last_inventory = inventory;")
        and "next_start_after_operation_id" in historical_inventory_json,
        "rev0971_entry_and_transport_frontiers_are_distinct_and_resume_with_the_existing_cursor",
        "the owner reports semantic entry truncation separately from the status byte frontier, and the bounded prefix retains the existing exact causal cursor rather than adding a second pagination authority",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "append_sync_replica_historical_version_inventory_json" in peer_status
        and "summary.last_step->historical_version_inventory.reset();" in peer_status,
        "rev0971_status_uses_the_canonical_encoder_and_retains_one_completed_inventory",
        "status v16 delegates history JSON to the shared canonical renderer and strips the generic per-step copy after stable historical accounting, while retaining action and failure diagnostics",
    )

    require(
        all(
            token in local_status_runtime
            for token in (
                "test_historical_inventory_status_byte_frontier",
                "maximum exact history page must compose evidence-bound reachability with the status overflow boundary",
                "generic last_step retained a duplicate completed history page",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "historical inventory omitted its status byte limit",
                "duplicated the stable history result",
                '"schema": "anonsync.peer-service.status.v26"',
            )
        )
        and '"anonsync.peer-service.status.v26"' in service_i2p_ingress_runtime,
        "rev0971_regressions_prove_the_large_page_frontier_and_single_copy_shipping_status",
        "the focused C++ oracle constructs the accepted 1,024-entry worst-shape page, while real configured-service and I2P readers require v16, coherent stop reasons, and no duplicate stable inventory in last_step",
    )

    require(
        all(
            token in normalized_prose(bounded_historical_status_design)
            for token in (
                "Defect found",
                "One exact byte frontier",
                "Canonical encoder refactor",
                "Single stable result",
                "Research and design context",
                "What this proves",
            )
        )
        and all(
            token in normalized_prose(rev0971_notes)
            for token in (
                "256 KiB",
                "entry-limit",
                "byte-limit",
                "status.v16",
                "Compatibility",
                "Nonclaims",
            )
        )
        and all(
            token in normalized_prose(readme)
            for token in (
                "## Rev0971:",
                "256 KiB",
                "entry-limit frontier",
                "byte frontier",
                "single stable",
            )
        ),
        "rev0971_records_the_capacity_composition_refactor_compatibility_and_nonclaims",
        "the design audit, revision notes, and README name the 1-MiB composition failure, exact canonical accounting, independent stop reasons, eliminated duplicate retention, compatibility boundary, and unfinished lifecycle work",
    )

    require(
        verifier.count(
            "if revision_number is not None and revision_number >= 971:"
        ) == 1
        and all(
            token in rev0971_verifier_block
            for token in (
                "BOUNDED_HISTORICAL_STATUS_PAGE_AND_SINGLE_RESULT_AUDIT_rev0971.md",
                "REVISION_NOTES_rev0971.md",
                "CMakeLists.txt",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.hpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0971_package_policy_binds_every_bounded_history_status_surface",
        "the release verifier makes the canonical encoder, owner/service/status integration, focused and process regressions, records, structural audit, and package policy mandatory from rev0971 onward",
    )

    require(
        all(
            token in folder_scan_h
            for token in (
                "SyncReplicaHistoricalVersionPayloadReachabilityClass",
                "current_visible",
                "superseded_active",
                "inactive_evidence",
                "retained_union",
                "unreferenced_payload_count",
                "It is not reclaimable authority",
            )
        ),
        "rev0972_header_models_all_retained_file_evidence_without_collection_authority",
        "the public exact-history result separates current, superseded, inactive, union, missing, and unreferenced facts while disclaiming unlink authority",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "v3:exact:",
                "evidence_set_digest",
                "EvidenceSetBeforePayloadObservation",
                "EvidenceSetDuringPayloadObservation",
                "v1:",
                "v2:metadata:",
            )
        )
        and ordered(
            historical_version_inspection,
            "EvidenceSetBeforePayloadObservation",
            "state_->payload_store->snapshot_or_throw()",
            "EvidenceSetDuringPayloadObservation",
        ),
        "rev0972_exact_cutpoint_binds_operations_evidence_and_payload_before_and_across_scan",
        "new exact pages bind the complete retained evidence set, reject known drift before payload work, and bracket evidence across the complete payload observation while preserving v1/v2 decoding",
    )

    evidence_visitor = function_body(model_h, "void for_each_evidence_operation(")
    require(
        "template <typename Visitor>" in model_h
        and "const Visitor& visitor" in evidence_visitor
        and "std::function" not in evidence_visitor
        and "visitor(operation, state->second)" in evidence_visitor
        and "maps diverged" in evidence_visitor,
        "rev0972_retained_evidence_traversal_is_linear_borrowed_and_fail_closed",
        "inactive evidence is visited in map lockstep without callback copying, type erasure, or per-operation lookup",
    )

    require(
        all(
            token in historical_version_inspection
            for token in (
                "kHistoricalPayloadCurrentVisibleMask",
                "kHistoricalPayloadSupersededActiveMask",
                "kHistoricalPayloadInactiveEvidenceMask",
                "for_each_active_path",
                "for_each_evidence_operation",
                "content_inventory()",
                "physical payload entry partition",
                "physical payload byte partition",
                "retained file-operation partition",
            )
        )
        and "inventory.retained_payload_reachability.emplace()" in historical_version_inspection
        and "!metadata.retained_payload_reachability.has_value()" in folder_scan_runtime,
        "rev0972_one_grouped_active_walk_one_inactive_walk_and_one_payload_pass_partition_reachability",
        "exact history avoids an operation-by-payload cross product, checks entry/byte/reference equations before publication, and leaves metadata mode authority-null",
    )

    require(
        all(
            token in historical_inventory_json
            for token in (
                "source_evidence_set_digest",
                "retained_payload_reachability",
                "share_retained_file_operations",
                "reclaimable_authority",
                "class_totals_overlap",
                "append_payload_reachability",
                "append_inventory(output, inventory, projection)",
                "class CountingStreamBuffer final",
            )
        )
        and "append_sync_replica_historical_version_inventory_json" in peer_status
        and "share_retained_file_operations" not in peer_status
        and "reclaimable_authority" not in peer_status,
        "rev0972_reachability_is_inside_the_same_counted_canonical_status_stream",
        "source evidence and reachability are counted and emitted by rev0971's one canonical encoder; service status delegates instead of carrying a second serializer that could bypass the byte frontier",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and '"anonsync.local-historical-versions.response.v5"' in local_status
        and "anonsync.peer-service.status.v26" in service_configuration_runtime
        and "anonsync.peer-service.status.v26" in service_i2p_ingress_runtime
        and "anonsync.peer-service.status.v16" not in peer_status_h
        and "anonsync.peer-service.status.v16" not in service_configuration_runtime
        and "anonsync.peer-service.status.v16" not in service_i2p_ingress_runtime,
        "rev0972_resolves_the_incompatible_sibling_v16_contract_with_one_v17_shape",
        "live, terminal, direct-process, and I2P-process readers require the merged v17 schema while the owner-only acceptance response remains v5",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "test_historical_version_payload_reachability_and_evidence_cutpoint",
                "PendingMissingDependency",
                "noncopyable_visitor",
                "unreferenced_payload_count == 1U",
                "EvidenceSetBeforePayloadObservation",
                "metadata history browsing fabricated",
            )
        ),
        "rev0972_owner_regression_covers_overlap_missing_orphan_metadata_and_prescan_drift",
        "the focused owner oracle exercises current/inactive sharing, missing history, an orphan object, non-copyable visitation, metadata coldness, and exact evidence fencing",
    )

    require(
        all(
            token in local_status_runtime
            for token in (
                "test_historical_inventory_status_byte_frontier",
                "maximum exact history page must compose evidence-bound reachability with the status overflow boundary",
                "canonical exact-history renderer exceeded, concealed, or dropped its composed reachability frontier",
                "generic last_step retained a duplicate completed history page",
                "v4:exact:",
                "retained_payload_reachability",
            )
        ),
        "rev0972_maximum_page_regression_binds_v3_reachability_frontier_and_single_copy",
        "the focused local-status oracle proves the combined exact inventory exceeds the unbounded transport budget, is reduced to the exact 256-KiB frontier, retains its v3 cutpoint and reachability object, and is stored once",
    )

    require(
        "len(value) == 268" in service_configuration_runtime
        and "v4:exact:" in service_configuration_runtime
        and "require_historical_payload_reachability" in service_configuration_runtime
        and "reclaimable_authority" in service_configuration_runtime
        and "anonsync.local-historical-versions.response.v5" in service_configuration_runtime,
        "rev0972_shipping_process_oracle_validates_v3_v17_v5_and_partition_equations",
        "the retained two-peer service rejects malformed source tokens, fabricated metadata authority, inconsistent object/byte partitions, and schema drift",
    )

    require(
        all(
            token in normalized_prose(retained_reachability_frontier_design)
            for token in (
                "Inactive evidence is load-bearing",
                "reclaimable_authority:false",
                "Canonical frontier integration and schema collision",
                "Git makes object reclamation reachability-driven",
                "Syncthing",
                "Why this is not collection authority",
                "v3:exact",
            )
        )
        and all(
            token in normalized_prose(rev0972_notes)
            for token in (
                "share-level retained-payload reachability",
                "incompatible sibling-schema collision",
                "compatible v1",
                "unchanged v2",
                "Rev0972 does not add garbage collection",
                "retention expiry",
            )
        )
        and "## Rev0972: retained-payload reachability inside the canonical frontier" in readme,
        "rev0972_records_authority_cost_schema_collision_research_compatibility_and_nonclaims",
        "the design record, revision notes, and README explain inactive evidence, v3, canonical byte accounting, the v16 collision, and why unreferenced is not safe-to-delete",
    )

    require(
        rev0972_verifier_block.count(
            "if revision_number is not None and revision_number >= 972:"
        ) == 1
        and all(
            token in rev0972_verifier_block
            for token in (
                "RETAINED_PAYLOAD_REACHABILITY_AND_CANONICAL_STATUS_FRONTIER_AUDIT_rev0972.md",
                "REVISION_NOTES_rev0972.md",
                "src/sync_replica_model.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0972_package_policy_binds_every_reachability_cutpoint_and_frontier_surface",
        "the release verifier requires the model, owner, token, canonical serializer, schemas, focused/process tests, records, structural audit, and package policy from rev0972 onward",
    )


    require(
        all(
            token in sqlite_owner
            for token in (
                "constexpr std::uint64_t kHistoricalPinSchemaVersion = 6U;",
                "sync_replica_history_pins",
                "historical_version_pin_count_be",
                "historical_version_pin_set_digest",
                "anonsync-sync-replica-sqlite-cutpoint-v6",
                "FOREIGN KEY(operation_id) REFERENCES sync_replica_operations(operation_id)",
                "ORDER BY operation_id;",
                "historical-version pin-set attestation mismatch",
            )
        ),
        "rev0973_sqlite_v6_owns_one_canonical_attested_retention_pin_set",
        "the durable replica owner—not the byte namespace—stores a sorted foreign-keyed File-operation pin set whose count and folder-bound digest participate in every v6 cutpoint",
    )

    require(
        all(
            token in sqlite_owner
            for token in (
                "constexpr std::uint64_t kRetentionRootSchemaVersion = 5U;",
                "migration source is not schema v1 through v8",
                "definition.name == \"sync_replica_history_pins\"",
                "!source_has_historical_version_pins",
                "meta_from_state_or_throw(",
                "prior.outbox, prior.historical_version_pins",
                "label + \" migration publication\"",
                "schema_matches(observed, kRetentionRootSchema)",
            )
        )
        and ordered(
            sqlite_owner,
            "LoadedState prior",
            "const std::uint64_t generation = increment_or_throw(",
            "definition.name == \"sync_replica_history_pins\"",
            "verify_schema_or_throw(db, label + \" migrated schema\")",
            "attest_and_commit_staged_cutpoint_or_throw(",
        ),
        "rev0973_v5_migration_restores_prior_authority_then_seeds_one_empty_pin_root",
        "migration accepts the exact v5 schema, preserves evidence/outbox authority, creates only the new policy surface, advances generation once, and publishes an attested empty pin set in the same transaction",
    )

    require(
        all(
            token in sqlite_owner
            for token in (
                "SyncReplicaSqliteOwner::pin_historical_version_or_throw(",
                "SyncReplicaSqliteOwner::unpin_historical_version_or_throw(",
                "evidence_operation_by_id(operation_id)",
                "operation->kind != SyncReplicaValueKind::File",
                "SyncReplicaSqliteHistoricalVersionPinDisposition::AlreadyPinned",
                "SyncReplicaSqliteHistoricalVersionPinDisposition::AlreadyUnpinned",
                "historical-version pin state generation",
                "historical-version unpin state generation",
                "SyncSqliteTransactionMode::Immediate",
            )
        )
        and all(
            token in sqlite_owner_h
            for token in (
                "SyncReplicaSqliteHistoricalVersionPinResult",
                "pin_historical_version_or_throw",
                "unpin_historical_version_or_throw",
                "historical_version_pin_set_digest",
            )
        ),
        "rev0973_pin_transitions_are_exact_file_evidence_policy_and_retry_idempotent",
        "pin rejects malformed, missing, or tombstone evidence; repeated pin/unpin is a no-op; only a real set transition increments state generation and commits a new attested cutpoint",
    )

    require(
        all(
            token in sqlite_owner_runtime
            for token in (
                "test_historical_version_pins_are_durable_exact_policy_roots",
                "fresh replica owner invented historical-version pins",
                "idempotent historical-version pin advanced durable authority",
                "historical-version pin accepted tombstone evidence",
                "restart lost the exact historical-version pin set",
                "tampered historical-version pin owner",
                "historical-version pin dispositions are not stable operator words",
            )
        ),
        "rev0973_sqlite_regression_proves_restart_idempotence_rejection_and_tamper_failure",
        "the focused durable-owner test covers initial emptiness, real and repeated transitions, tombstone/malformed rejection without mutation, restart persistence, stable dispositions, and fail-closed row tampering",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "v4:exact:",
                "v4:metadata:",
                "historical_version_pin_set_digest",
                "v3:exact:",
                "v2:metadata:",
                "New v4 tokens bind the local pin set",
            )
        )
        and all(
            token in historical_version_inspection
            for token in (
                "HistoricalVersionPinSetBeforePayloadObservation",
                "HistoricalVersionPinSetDuringPayloadObservation",
                "replica_snapshot.historical_version_pin_count != 0U",
                "source_historical_version_pin_set_digest",
                "historical_version_pin_count",
                "state_->payload_store->snapshot_or_throw()",
            )
        )
        and ordered(
            historical_version_inspection,
            "HistoricalVersionPinSetBeforePayloadObservation",
            "state_->payload_store->snapshot_or_throw()",
            "HistoricalVersionPinSetDuringPayloadObservation",
        ),
        "rev0973_v4_cutpoints_bind_pin_policy_and_legacy_tokens_are_not_wildcards",
        "new exact and metadata tokens bind the pin-set digest; legacy tokens decode only while the current pin set is empty, and exact mode brackets pin policy across its complete payload observation",
    )

    require(
        all(
            token in folder_scan_h + historical_inventory_json
            for token in (
                "explicit_pins",
                "bool pinned = false",
                "historical_version_pin_count",
                "source_historical_version_pin_set_digest",
            )
        )
        and all(
            token in historical_version_inspection
            for token in (
                "mark_explicit_pin",
                "kHistoricalPayloadExplicitPinMask",
                "explicit-pin missing content",
                "validate_class(reachability.explicit_pins, \"explicit-pins\")",
                "observed_pinned_file_operations",
                "historical-version retained payload reachability is inconsistent",
            )
        )
        and "!metadata.retained_payload_reachability.has_value()" in folder_scan_runtime,
        "rev0973_history_projects_pins_without_inventing_payload_availability",
        "every entry carries one pinned bit; exact reachability includes overlapping present or missing explicit roots and validates count equations, while metadata browsing remains payload-cold and authority-null",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "pre-pin source token treated a nonempty retention set as a wildcard",
                "reachability.explicit_pins.file_operation_count == 1U",
                "reachability.explicit_pins.present_content_count == 0U",
                "reachability.explicit_pins.missing_content_count == 1U",
                "metadata.entries.front().pinned",
                "pin_historical_version_or_throw",
                "unpin_historical_version_or_throw",
            )
        ),
        "rev0973_folder_owner_regression_proves_missing_pinned_root_metadata_coldness_and_legacy_fence",
        "the focused owner test pins a retained predecessor whose content is absent, observes exact missing-root accounting and metadata projection, rejects a pre-pin continuation, and proves unpin/repin transitions",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                "version-pin",
                "version-unpin",
                "kHistoricalVersionPinRequestPrefix",
                "kHistoricalVersionUnpinRequestPrefix",
                "different_historical_version_pending",
                "drain_requested",
                "anonsync.local-historical-version-pin.response.v1",
                "anonsync.local-historical-version-unpin.response.v1",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "same historical pin did not coalesce by generation",
                "different_historical_version_pending",
                "unpin overwrote a pending pin in the shared history lane",
                "historical pin client accepted a malformed operation ID",
                "historical unpin client accepted a malformed operation ID",
                "version-pin",
                "version-unpin",
            )
        ),
        "rev0973_owner_socket_linearizes_exact_pin_identity_in_the_existing_history_lane",
        "strict lowercase-hex pin/unpin frames remain PID-bound and mode-0600, coalesce only identical work, reject conflicting pending actions, and close admission at the existing drain seal",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_service
            for token in (
                "else if (restoring)",
                "SyncReplicaPeerServiceHistoricalVersionAction::Pin",
                "SyncReplicaPeerServiceHistoricalVersionAction::Unpin",
                "pin_historical_version_or_throw(",
                "unpin_historical_version_or_throw(",
                "historical_version_last_pin_update",
                "counters.historical_version_pins",
                "counters.historical_version_unpins",
            )
        )
        and all(
            token in peer_status
            for token in (
                "last_pin_update",
                "historical_version_pins",
                "historical_version_unpins",
                "historical_version_retention_operation_id",
            )
        )
        and all(
            token in sync_cli
            for token in (
                "command_version_retention_update",
                'command == "version-pin"',
                'command == "version-unpin"',
                "version-pin and version-unpin mutate only the durable local set",
            )
        ),
        "rev0973_service_cli_and_status_use_one_action_specific_sqlite_authority_path",
        "the CLI maps pin/unpin into the existing owner action lane, peer validation no longer falls through to restore semantics, and v18 publishes one typed update plus separate counters without granting authority to the socket worker or payload store",
    )

    require(
        all(
            token in service_configuration_runtime
            for token in (
                "owner-only historical version pin",
                "pinned causal-metadata historical inspection",
                "owner-only historical version unpin",
                "unpinned causal-metadata historical inspection",
                '"historical_version_pins": 1',
                '"historical_version_unpins": 1',
                '"historical_version_inspections": 6',
                '"schema": "anonsync.peer-service.status.v26"',
            )
        )
        and "anonsync.peer-service.status.v26" in service_i2p_ingress_runtime,
        "rev0973_real_process_proves_pin_reinspect_unpin_reinspect_and_schema_coherence",
        "one retained configured daemon accepts the exact owner commands, survives the corrected validator, exposes durable policy through metadata-only pages, removes it, continues operating, and keeps direct and I2P readers on v18",
    )

    require(
        all(
            token in normalized_prose(retention_pin_design)
            for token in (
                "Authority placement: the replica owner, not the payload store",
                "Schema-v6 cutpoint and restart semantics",
                "Source-cutpoint evolution and legacy safety",
                "Adjacent audit and correction",
                "production wiring defect",
                "Why this is still not garbage collection",
                "reclaimable_authority:false",
            )
        )
        and all(
            token in normalized_prose(rev0973_notes)
            for token in (
                "SQLite schema advances from v5 to v6",
                "unsealed payload-side pin implementation was rejected",
                "legacy-token consistency hole",
                "does not add garbage collection",
            )
        )
        and "## Rev0973: durable causal-version retention pins" in readme,
        "rev0973_records_split_authority_rejection_compatibility_cost_and_nonclaims",
        "the design record, notes, and README explain why pins are causal SQLite policy, how legacy tokens fail safely, what the process oracle corrected, and why no retained fact authorizes unlink",
    )

    require(
        rev0973_verifier_block.count(
            "if revision_number is not None and revision_number >= 973:"
        ) == 1
        and all(
            token in rev0973_verifier_block
            for token in (
                "HISTORICAL_VERSION_RETENTION_PIN_AUTHORITY_AUDIT_rev0973.md",
                "REVISION_NOTES_rev0973.md",
                "src/anonsync_sync.cpp",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_sqlite_owner.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_replica_sqlite_owner_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0973_package_policy_binds_every_retention_authority_and_operator_surface",
        "the release verifier requires the SQLite owner, source tokens, history projection, local/peer actions, status, focused/process regressions, records, structural audit, and package policy from rev0973 onward",
    )

    require(
        all(
            token in historical_query_h
            for token in (
                "kSyncReplicaRetentionPlanDefaultMaximumEntries = 64U",
                "kSyncReplicaRetentionPlanMaximumEntries = 1024U",
                "struct SyncReplicaRetentionPlanQuery final",
                "start_after_content_sha256",
                "expected_source_cutpoint",
                "source cutpoint is not one current exact v4 cutpoint",
            )
        )
        and "SyncReplicaHistoricalVersionInspectionMode::ExactPayloadAvailability"
        in historical_query_h,
        "rev0974_plan_query_binds_digest_pages_to_one_current_exact_v4_cutpoint",
        "the public planner accepts only bounded digest pages and refuses metadata or legacy cutpoints that omit evidence, pin, or payload identity",
    )

    require(
        ordered(
            retention_plan_owner,
            "const SyncReplicaSqliteSnapshot replica_snapshot",
            "OperationSetBeforePayloadObservation",
            "EvidenceSetBeforePayloadObservation",
            "HistoricalVersionPinSetBeforePayloadObservation",
            "const SyncReplicaModel model",
            "SyncReplicaRetentionPlan plan;",
            "snapshot_writer_fenced_for_retention_or_throw()",
            "const SyncReplicaSqliteSnapshot replica_after_payload",
            "OperationSetDuringPayloadObservation",
            "EvidenceSetDuringPayloadObservation",
            "HistoricalVersionPinSetDuringPayloadObservation",
            "SyncReplicaHistoricalVersionSourceChangeStage::PayloadSnapshot",
            "const SyncReplicaSqliteSnapshot replica_final",
            "operation set changed during writer-fenced",
            "verify_writer_fenced_retention_snapshot_or_throw",
        )
        and "begin_mutation_batch_or_throw" not in retention_plan_owner
        and "unlink" not in retention_plan_owner
        and "rename" not in retention_plan_owner,
        "rev0974_owner_brackets_one_complete_payload_observation_without_mutation_authority",
        "known stale roots fail before payload work, SQLite snapshots bracket both the complete physical observation and the writer-fenced candidate probes, and the planner contains no mutation, rename, or unlink path",
    )

    require(
        all(
            token in folder_scan
            for token in (
                "struct HistoricalPayloadReferenceKey final",
                "kHistoricalPayloadCurrentVisibleMask",
                "kHistoricalPayloadSupersededActiveMask",
                "kHistoricalPayloadInactiveEvidenceMask",
                "kHistoricalPayloadExplicitPinMask",
                "retention_plan_disposition_from_root_mask",
            )
        )
        and folder_scan.count(
            "std::map<HistoricalPayloadReferenceKey, std::uint8_t"
        ) >= 1
        and all(
            token in folder_scan
            for token in (
                "struct HistoricalPayloadReferenceProjectionEntry final",
                "std::vector<HistoricalPayloadReferenceProjectionEntry>",
                "historical_payload_reference_key_equal",
            )
        )
        and all(
            token in folder_scan_h
            for token in (
                "CurrentOrExplicitPin",
                "RetainedHistoryOrEvidence",
                "UnreferencedByRetainedFileOperations",
                "current_visible",
                "superseded_active",
                "inactive_evidence",
                "explicit_pin",
            )
        ),
        "rev0974_history_and_plan_share_one_physical_key_root_mask_and_disposition_vocabulary",
        "historical reachability and per-object planning cannot independently redefine current, historical, inactive, pinned, or unreferenced payload identity",
    )

    require(
        all(
            token in retention_plan_owner
            for token in (
                "content_inventory.content_sha256s()",
                "std::lower_bound(",
                "cursor is not one current physical payload",
                "physical_payload_count_after_cursor",
                "current_or_explicit_pin",
                "retained_history_or_evidence",
                "unreferenced_by_retained_file_operations",
                "physical payload entry partition",
                "physical payload byte partition",
                "retained file-operation partition",
                "planned payload partition",
                "planned byte partition",
                "retention-plan projection is inconsistent",
                "next_start_after_content_sha256",
            )
        ),
        "rev0974_digest_order_cursor_and_complete_partition_equations_precede_page_publication",
        "the cursor must name an exact physical object, every physical byte belongs to one disposition, missing references remain in reachability, and all equations are checked before the page returns",
    )

    require(
        all(
            token in historical_inventory_json_h + historical_inventory_json
            for token in (
                "kSyncReplicaRetentionPlanMaximumStatusBytes = 224U * 1024U",
                "append_sync_replica_retention_plan_json",
                "render_sync_replica_retention_plan_json",
                "bound_sync_replica_retention_plan_for_status_or_throw",
                r'\"reclaimable_authority\":false',
                r'\"quota_policy_applied\":false',
                r'\"grace_period_applied\":false',
                r'\"writer_fenced_collection\":false',
                "next_start_after_content_sha256",
                "retention-plan status byte frontier did not converge",
            )
        )
        and "append_payload_reachability_value" in historical_inventory_json,
        "rev0974_canonical_plan_stream_has_a_real_byte_frontier_and_explicit_nonauthority",
        "one counted/emitted serializer carries exact reachability, disposition reasons, deterministic digest continuation, and four deletion-policy nonclaims inside a reachable 224 KiB frontier",
    )

    require(
        all(
            token in local_status_h + local_status
            for token in (
                "RetentionPlan",
                "retention-plan ",
                "anonsync.local-retention-plan.response.v6",
                "SyncReplicaRetentionPlanQuery retention_plan_query",
                "different_historical_version_pending",
                "request_sync_local_status_retention_plan_or_throw",
            )
        )
        and "historical_version_pending->retention_plan_query !=" in local_status
        and "retention_plan_query ||" in local_status
        and all(
            token in local_status_runtime
            for token in (
                "retention-plan request did not return exact acceptance",
                "same retention-plan query did not coalesce by generation",
                "different retention-plan query overwrote pending work",
                "retention-plan accepted a metadata-only source cutpoint",
            )
        ),
        "rev0974_owner_socket_linearizes_the_complete_plan_query_in_the_existing_history_lane",
        "strict framing, PID-bound response validation, equality-based coalescing, conflicting-work rejection, and the drain seal remain one local action authority",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and all(
            token in peer_service
            for token in (
                "SyncReplicaPeerServiceHistoricalVersionAction::RetentionPlan",
                "plan_payload_retention_or_throw(",
                "bound_sync_replica_retention_plan_for_status_or_throw(plan)",
                "historical_version_last_retention_plan = plan",
                "counters.historical_version_retention_plans",
            )
        )
        and peer_service.find(
            "bound_sync_replica_retention_plan_for_status_or_throw(plan)"
        ) < peer_service.find("historical_version_last_retention_plan = plan")
        and all(
            token in peer_status
            for token in (
                "retention_plan_query",
                "last_retention_plan",
                "historical_version_retention_plans",
                "historical_version_retention_plan.reset();",
            )
        ),
        "rev0974_service_status_retains_one_bounded_plan_and_strips_the_generic_duplicate",
        "the peer owner performs and bounds work, v19 keeps one stable completed result, and generic last-step accounting cannot double the largest page",
    )

    require(
        all(
            token in sync_cli
            for token in (
                "command_retention_plan",
                'command == "retention-plan"',
                "anonsync_sync retention-plan --source-cutpoint",
                "deletion-free diagnostic",
                "applies no quota, grace period",
                "quarantine, or unlink authority",
            )
        ),
        "rev0974_shipping_cli_exposes_exact_reasons_without_claiming_collection",
        "the ordinary product binary accepts bounded exact pages and describes the missing policy, transient roots, quarantine, and unlink stages rather than hiding them",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "retention planner did not reuse the exact reachability cutpoint and physical partition",
                "retention planner lost overlapping current and inactive-evidence roots",
                "retention planner promoted an unreferenced physical object into a retained root",
                "retention planner did not resume exactly with one page-invariant mark witness",
                "retention planner accepted a stale operation-set cutpoint",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "maximum retention-plan page did not exercise its status byte frontier",
                "retention-plan byte frontier changed digest order or lost its exact continuation cursor",
                "bounded retention-plan JSON exceeded or concealed its deletion-free mark frontier",
                "generic last_step retained a duplicate retention-plan page",
            )
        ),
        "rev0974_focused_regressions_cover_roots_missing_history_pagination_staleness_and_transport_bounds",
        "owner tests compose exact current, inactive, missing pinned, and orphan facts while status tests exercise the maximum public page and one-copy presentation path",
    )

    require(
        all(
            token in service_configuration_runtime
            for token in (
                "owner-only deletion-free retention plan",
                "anonsync.local-retention-plan.response.v6",
                "retention plan did not bind the exact pinned source",
                "retention plan did not explain the exact pinned payload",
                '"historical_version_retention_plans": 1',
                '"schema": "anonsync.peer-service.status.v26"',
            )
        )
        and "anonsync.peer-service.status.v26" in service_i2p_ingress_runtime
        and all(
            token in service_configuration_runtime
            for token in (
                "reclaimable_authority",
                "quota_policy_applied",
                "grace_period_applied",
                "writer_fenced_collection",
                "explicit_pin",
                "current_or_explicit_pin",
            )
        ),
        "current_real_daemon_proves_pinned_physical_reason_status_v21_and_collection_nonclaims",
        "the retained two-peer service pins a predecessor, obtains its exact physical reason, exposes canonical witnesses, remains alive, and keeps direct plus I2P readers on the current v21 contract",
    )

    require(
        all(
            token in normalized_prose(retention_plan_design)
            for token in (
                "One exact source cutpoint",
                "Canonical physical order and page reachability",
                "Root vocabulary and dispositions",
                "Why unreferenced is not reclaimable",
                "External design precedent",
                "Next safe collection protocol",
                "245,443 bytes",
                "writer_fenced_collection",
            )
        )
        and all(
            token in normalized_prose(rev0974_notes)
            for token in (
                "exact, deletion-free physical payload-retention planner",
                "largest accepted 1,024-entry page encoded to 245,443 bytes",
                "does not add garbage collection",
            )
        )
        and "## Rev0974: exact deletion-free physical retention planning"
        in readme,
        "rev0974_records_the_authority_boundary_dead_frontier_correction_and_future_collector_protocol",
        "the audit, notes, and README explain the exact observation, shared roots, corrected presentation limit, external precedent, and every authority still required before deletion",
    )

    require(
        rev0974_verifier_block.count(
            "if revision_number is not None and revision_number >= 974:"
        ) == 1
        and all(
            token in rev0974_verifier_block
            for token in (
                "DELETION_FREE_EXACT_RETENTION_PLAN_AUDIT_rev0974.md",
                "REVISION_NOTES_rev0974.md",
                "src/anonsync_sync.cpp",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service.cpp",
                "src/sync_replica_peer_service_status.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0974_package_policy_binds_every_planner_authority_operator_test_and_record_surface",
        "release verification requires the source token, owner projection, canonical renderer, local and peer action lanes, real process oracle, design record, revision notes, structural audit, and package policy",
    )

    require(
        all(
            token in retention_plan_owner
            for token in (
                "std::vector<HistoricalPayloadReferenceProjectionEntry>",
                "payload_references.reserve(",
                "std::sort(",
                "compacted_reference_count",
                "historical_payload_reference_key_equal",
                "reference_index",
                "account_missing_reference",
            )
        )
        and "std::map<HistoricalPayloadReferenceKey" not in retention_plan_owner
        and "payload_references.find" not in retention_plan_owner
        and "payload_references.erase" not in retention_plan_owner,
        "rev0975_retention_projection_is_one_bounded_sort_fold_and_linear_merge",
        "the planner borrows immutable operation keys into one contiguous projection, folds duplicate roots in place, and linearly merges the complete physical namespace without per-object tree lookup",
    )

    require(
        all(
            token in folder_scan + folder_scan_h
            for token in (
                "anonsync:sync-replica-retention-plan-unreferenced-candidates:v1",
                "anonsync:sync-replica-retention-plan-deletion-free-mark:v5",
                "unreferenced_candidate_set_digest",
                "exact_deletion_free_mark_digest",
            )
        )
        and all(
            token in retention_plan_owner
            for token in (
                "state_->folder_id",
                "plan.source_operation_set_digest",
                "plan.source_evidence_set_digest",
                "plan.source_historical_version_pin_set_digest",
                "plan.source_visible_state_digest",
                "plan.source_payload_snapshot_digest",
                "reachability.unreferenced_payload_count",
                "reachability.unreferenced_payload_bytes",
            )
        )
        and all(
            token in historical_inventory_json
            for token in (
                "durable_mark_persisted",
                "unreferenced_candidate_set_digest",
                "exact_deletion_free_mark_digest",
            )
        ),
        "rev0975_two_domain_separated_page_invariant_witnesses_bind_candidates_to_the_exact_source",
        "one digest covers the complete canonical unreferenced physical set and one binds it to folder, operation, evidence, pin, visible, and payload cutpoints while JSON explicitly denies durable mark authority",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "retention_unreferenced_candidate_set_digest_for_test",
                "retention_deletion_free_mark_digest_for_test",
                "expected_candidate_set_digest",
                "expected_deletion_free_mark_digest",
                "one page-invariant mark witness",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "durable_mark_persisted",
                "unreferenced_candidate_set_digest",
                "exact_deletion_free_mark_digest",
                "deletion-free mark witness",
                "deletion-free mark frontier",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "durable_mark_persisted",
                "unreferenced_candidate_set_digest",
                "exact_deletion_free_mark_digest",
            )
        ),
        "rev0975_independent_unit_and_process_oracles_prove_exact_witness_values_and_page_invariance",
        "focused C++ tests independently frame both SHA-256 streams across complete and paginated output, while status and real-process tests require canonical fields and explicit nonauthority",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "anonsync.local-retention-plan.response.v6" in local_status
        and "anonsync.peer-service.status.v19" not in peer_status_h
        and "anonsync.local-retention-plan.response.v1" not in local_status
        and "anonsync.peer-service.status.v26" in service_i2p_ingress_runtime,
        "rev0975_local_and_peer_status_contract_has_current_successor_schemas",
        "the current response and service schemas supersede rev0975 while direct plus I2P status oracles remain coherent",
    )

    require(
        all(
            token in normalized_prose(retention_mark_witness_design)
            for token in (
                "Borrowed sorted projection and linear merge",
                "Complete candidate-set digest",
                "Exact deletion-free mark digest",
                "durable_mark_persisted",
                "Contamination and reconstruction audit",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0975_notes)
            for token in (
                "Page-invariant deletion-free mark witness",
                "bounded borrowed vector",
                "durable_mark_persisted:false",
                "contaminated unsealed worktree",
            )
        )
        and "## Rev0975: page-invariant deletion-free mark witness" in readme,
        "rev0975_records_complexity_authority_contamination_and_future_collector_boundaries",
        "the audit, revision notes, and README state the linear projection, exact digest framing, non-durable authority boundary, rejected contamination, and safe durable collector sequence",
    )

    require(
        rev0975_verifier_block.count(
            "if revision_number is not None and revision_number >= 975:"
        ) == 1
        and all(
            token in rev0975_verifier_block
            for token in (
                "PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md",
                "REVISION_NOTES_rev0975.md",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0975_package_policy_binds_every_projection_witness_schema_test_and_record_surface",
        "release verification requires the projection owner, canonical renderer, response schemas, focused and process tests, design record, revision notes, structural audit, and package policy from rev0975 onward",
    )

    require(
        all(
            token in store + store_h + cmake
            for token in (
                "anonsync:sync-replica-file-payload-store-snapshot:v4",
                "anonsync:sync-replica-file-payload-store-transient-namespace:v2",
                "transient_namespace_digest_or_throw",
                "transient_reserved_bytes() const",
                "transient_namespace_digest() const",
                "sync_posix_regular_file_snapshot_metadata_from_status_or_throw",
                "append_sync_posix_regular_file_snapshot_metadata_binary",
                "SyncPosixDescriptorLinkPolicy::exactly_one",
                "anonsync_sync_posix_regular_file_snapshot_codec",
            )
        )
        and ordered(
            store,
            "snapshot->transient_reserved_bytes =",
            "snapshot->transient_namespace_digest =",
            "snapshot->snapshot_digest = snapshot_digest_or_throw(",
            "snapshot->transient_reserved_bytes,",
            "snapshot->transient_namespace_digest,",
        ),
        "rev0976_snapshot_v4_binds_reserved_capacity_exact_inode_observations_and_transient_namespace",
        "the complete payload snapshot binds one canonical POSIX observation per transient inode, exact reservation accounting, and the resulting namespace witness through an explicit build dependency",
    )

    require(
        all(
            store.count(name) >= 3
            for name in (
                "staged_prefix_precedes",
                "staged_range_precedes",
                "assembly_precedes",
                "publication_residue_precedes",
            )
        )
        and all(
            token in store
            for token in (
                'append_string(digest, "staged_prefix")',
                'append_string(digest, "staged_range")',
                'append_string(digest, "assembly_residue")',
                'append_string(digest, "publication_residue")',
                "transient namespace aggregate accounting is inconsistent",
                "transient namespace is not canonically ordered",
            )
        ),
        "rev0976_scanner_and_witness_share_one_ordering_contract_for_all_transient_classes",
        "named comparators drive both canonical scanner sorting and digest-order assertions while aggregate cross-checks cover prefix, range, assembly, and publication obligations",
    )

    require(
        all(
            token in folder_scan + folder_scan_h
            for token in (
                "anonsync:sync-replica-retention-plan-deletion-free-mark:v5",
                "source_payload_transient_namespace_digest",
                "payload_transient_entry_count",
                "payload_transient_bytes",
                "payload_transient_reserved_bytes",
            )
        )
        and ordered(
            retention_plan_owner,
            "plan.source_payload_transient_namespace_digest",
            "plan.payload_transient_entry_count",
            "plan.payload_transient_bytes",
            "plan.payload_transient_reserved_bytes",
            "plan.exact_deletion_free_mark_digest",
        )
        and all(
            token in historical_inventory_json
            for token in (
                r'\"payload_store_transient_namespace_bound\":true',
                r'\"durable_receiver_restart_obligations_bound\":true',
                r'\"active_pass_transient_roots_bound\":false',
                r'\"opened_sender_transient_roots_bound\":false',
                r'\"mutation_batch_transient_roots_bound\":false',
                r'\"external_transient_root_model_complete\":false',
                r'\"reclaimable_authority\":false',
                r'\"writer_fenced_collection\":false',
                r'\"durable_mark_persisted\":false',
            )
        ),
        "rev0976_transient_fields_remain_bound_in_successor_mark_without_inventing_external_roots_or_deletion_authority",
        "the page-invariant mark independently binds exact store transient evidence while the renderer denies active-pass, sender, mutation-batch, durable-mark, writer-fence, and reclaim authority",
    )

    require(
        all(
            token in runtime
            for token in (
                "expected_transient_namespace_digest",
                "same-name same-size transient inode replacement retained stale cutpoint identity",
                "same-count same-byte same-reservation obligations still collide at the snapshot cutpoint",
                "reservation-only transient drift retained the stale snapshot cutpoint",
                "same-name same-size assembly replacement retained stale cutpoint identity",
                "transient namespace witness was not canonical across owner restart",
            )
        )
        and all(
            token in folder_scan_runtime
            for token in (
                "same-size transient identity drift reported the wrong source-change stage",
                "same-count same-byte transient identity drift preserved a stale retention cutpoint",
                "source_payload_transient_namespace_digest",
                "payload_transient_reserved_bytes",
            )
        ),
        "rev0976_independent_oracles_falsify_aggregate_inode_and_semantic_aliases",
        "focused payload and retention tests independently frame v2, replace same-name inodes, separate same-reservation identity drift from reservation-only drift, prove restart stability, and reject stale payload cutpoints",
    )

    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "anonsync.local-retention-plan.response.v6" in local_status
        and "anonsync.local-retention-plan.response.v6" in local_status_runtime
        and "anonsync.local-retention-plan.response.v6" in service_configuration_runtime
        and "anonsync.peer-service.status.v26" in service_configuration_runtime
        and "anonsync.peer-service.status.v26" in service_i2p_ingress_runtime
        and all(
            token in service_configuration_runtime
            for token in (
                "payload_store_transient_namespace_bound",
                "durable_receiver_restart_obligations_bound",
                "active_pass_transient_roots_bound",
                "opened_sender_transient_roots_bound",
                "mutation_batch_transient_roots_bound",
                "external_transient_root_model_complete",
                "source_payload_transient_namespace_digest",
                "payload_transient_reserved_bytes",
            )
        ),
        "rev0976_owner_response_peer_status_and_real_process_oracles_share_v3_v21_transient_contract",
        "local acceptance, live and terminal peer status, configured service, and I2P readers all require the same exact transient witness and explicit partial-root model",
    )

    require(
        all(
            token in normalized_prose(transient_cutpoint_design)
            for token in (
                "Canonical transient namespace witness",
                "same-name, same-size inode replacement",
                "eleven-field POSIX regular-file snapshot codec",
                "Exact deletion-free mark v2",
                "durable_receiver_restart_obligations_bound",
                "external_transient_root_model_complete",
                "Authority still missing",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0976_notes)
            for token in (
                "Exact transient-namespace retention cutpoint",
                "fixed-width canonical POSIX regular-file observation",
                "active-pass",
                "opened-sender",
                "mutation-batch",
                "does not add collection authority",
            )
        )
        and "## Rev0976: exact transient-namespace retention cutpoint" in readme
        and "anonsync.local-retention-plan.response.v3" in readme,
        "rev0976_records_exact_inode_scope_partial_root_model_and_future_collection_boundary",
        "the design audit, revision notes, and README state the old alias, exact metadata framing, bounded store authority, explicit external-root nonclaims, and safe next protocol",
    )

    require(
        rev0976_verifier_block.count(
            "if revision_number is not None and revision_number >= 976:"
        ) == 1
        and all(
            token in rev0976_verifier_block
            for token in (
                "EXACT_TRANSIENT_NAMESPACE_RETENTION_CUTPOINT_AUDIT_rev0976.md",
                "REVISION_NOTES_rev0976.md",
                "CMakeLists.txt",
                "src/sync_local_status_socket.cpp",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0976_package_policy_binds_every_witness_codec_schema_test_and_record_surface",
        "release verification requires the codec dependency, payload witness, retention owner, canonical renderer, local and peer schemas, focused and process tests, design record, notes, audit, and package policy",
    )

    snapshot_payload_open = function_body(
        store,
        "SyncReplicaFilePayloadStoreSnapshot::open_payload_for_operation_or_throw(",
    )
    snapshot_payload_range = function_body(
        store,
        "SyncReplicaFilePayloadStoreSnapshot::copy_payload_range_for_operation_or_throw(",
    )
    targeted_payload_open = function_body(
        store,
        "open_optional_payload_for_operation_or_throw(",
    )

    require(
        all(
            token in store_h + store
            for token in (
                "kSyncReplicaFilePayloadUseLeaseProtocol",
                "anonsync:sync-replica-file-payload-use-flock-lease:v1",
                "try_acquire_payload_use_flock_nonblocking_or_throw",
                "acquire_payload_use_flock_nonblocking_or_throw",
                "acquire_shared_payload_use_lease_or_throw",
                "acquire_exclusive_payload_use_lease_or_throw",
                "LOCK_SH",
                "LOCK_EX",
                "LOCK_NB",
                "SyncReplicaFilePayloadStoreLeaseBusyError",
            )
        )
        and ordered(
            function_body(
                store, "try_acquire_payload_use_flock_nonblocking_or_throw("
            ),
            "::flock(descriptor, operation | LOCK_NB)",
            "flock_conflict_error(error)",
            "return false",
        )
        and ordered(
            function_body(
                store, "void acquire_payload_use_flock_nonblocking_or_throw("
            ),
            "try_acquire_payload_use_flock_nonblocking_or_throw",
            "SyncReplicaFilePayloadStoreLeaseBusyError",
        )
        and "operation != LOCK_SH && operation != LOCK_EX"
        in function_body(
            store, "try_acquire_payload_use_flock_nonblocking_or_throw("
        ),
        "rev0977_stable_payload_use_protocol_is_nonblocking_typed_and_two_sided",
        "one named helper family implements shared reader and exclusive mutator exact-inode leases with typed busy results",
    )

    require(
        all(
            token in store
            for token in (
                "std::string identity_basename;",
                "std::string expected_identity;",
                "StoreObservationDurability durability",
                "snapshot->identity_basename = store.identity_basename",
                "snapshot->expected_identity = expected_identity",
                "snapshot->durability = durability",
            )
        )
        and ordered(
            snapshot_payload_open,
            "root preflight",
            "acquire_store_lease_or_throw",
            "open_store_file_or_throw",
            "acquire_shared_payload_use_lease_or_throw",
            "verify_named_regular_file_or_throw",
            "observation_lease.verify_or_throw",
            "final root proof",
        )
        and ordered(
            snapshot_payload_range,
            "root preflight",
            "acquire_store_lease_or_throw",
            "open_store_file_or_throw",
            "acquire_shared_payload_use_lease_or_throw",
            "copy_hash_regular_file_range_or_throw",
            "verify_named_regular_file_or_throw",
            "observation_lease.verify_or_throw",
            "final root proof",
        ),
        "rev0977_complete_snapshot_byte_reopens_reenter_current_reader_fence",
        "both descriptor and bounded-range access bind the snapshot to the current identity lease before exact-inode use and final pathname/root proof",
    )

    require(
        ordered(
            targeted_payload_open,
            "open_targeted_payload_observation_or_throw",
            "acquire_shared_payload_use_lease_or_throw",
            "verify_named_regular_file_or_throw",
            "payload.observation_lease.verify_or_throw",
            "root proof",
            "payload.payload_descriptor.release()",
        )
        and all(
            token in normalized_prose(store_h)
            for token in (
                "shared per-payload inode",
                "released with the final descriptor",
                "must not retain it across",
                "network waits, sleeps",
                "store-wide lease is retained across a network session",
            )
        )
        and all(
            token in folder_scan
            for token in (
                "shared exact-inode use lease",
                "current shared store reader fence",
                "global store EX",
                "candidate inode EX",
            )
        ),
        "rev0977_targeted_and_product_consumers_transfer_only_bounded_exact_inode_authority",
        "targeted selection transfers the shared inode lease into the move-only descriptor while product comments forbid network-wait retention and name the future collector order",
    )

    require(
        ordered(
            quarantine_store,
            "SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation",
            "open_optional_store_file_or_throw",
            "require_private_regular_file_or_throw",
            "acquire_exclusive_payload_use_lease_or_throw",
            "stream_hash_regular_file_or_throw",
            "rename_noreplace_at_or_throw",
        )
        and ordered(
            quarantine_release_store,
            "SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation",
            "open_store_file_or_throw",
            "require_private_regular_file_or_throw",
            "acquire_exclusive_payload_use_lease_or_throw",
            "unlink_scanned_private_file_or_throw",
            "verify_cutpoint_or_throw(\"final\")",
        )
        and quarantine_store.find("acquire_store_lease_or_throw")
        < quarantine_store.find("acquire_exclusive_payload_use_lease_or_throw")
        and quarantine_release_store.find("acquire_store_lease_or_throw")
        < quarantine_release_store.find(
            "acquire_exclusive_payload_use_lease_or_throw"
        ),
        "rev0977_namespace_removal_obeys_global_then_exact_inode_exclusive_order",
        "both existing rename and unlink owners exclude new readers globally and detect previously issued descriptors on the exact inode before mutation",
    )

    require(
        all(
            token in runtime
            for token in (
                "descriptor-streaming snapshot reader fence",
                "descriptor-streaming range reader fence",
                "shared exact-inode use lease",
                "closing the returned payload descriptor did not release its exact-inode use lease",
                "test_live_payload_descriptor_fences_quarantine_inode_mutation",
                "ChildHeldInheritedDescriptor",
                "quarantine ignored a shared payload-use lease retained only by an inherited descriptor in another process",
                "payload-use lease contention partially mutated the authoritative or quarantine namespace",
                "quarantine did not proceed after the final selected descriptor released its inode lease",
                "anonsync:sync-replica-file-payload-use-flock-lease:v1",
            )
        )
        and "std::string selected_bytes(payload.size(), '\\0');" in runtime
        and "\x00" not in runtime,
        "rev0977_runtime_oracles_cover_reader_fence_same_process_and_fork_inherited_lifetime",
        "the focused suite proves current global contention, exact-inode contention, final-close release, namespace immutability, and cross-process inherited open-file-description lifetime",
    )

    require(
        all(
            token in normalized_prose(payload_use_lease_design)
            for token in (
                "Heart of the mission",
                "Concrete authority defect",
                "Two-tier cooperative protocol",
                "Complete-snapshot reader fence",
                "Bounded descriptor lifetime",
                "Existing mutators now consume the protocol",
                "Runtime proof",
                "source-byte hygiene",
                "What this proves",
                "What this does not prove",
                "opened_sender_transient_roots_bound:false",
                "external_transient_root_model_complete:false",
                "writer_fenced_collection:false",
                "reclaimable_authority:false",
                "noncooperating same-UID",
                "remote filesystems",
                "Next safe edge",
                "man7.org/linux/man-pages/man2/flock.2.html",
                "man7.org/linux/man-pages/man2/unlink.2.html",
                "man7.org/linux/man-pages/man2/rename.2.html",
            )
        )
        and all(
            token in normalized_prose(rev0977_notes)
            for token in (
                "Payload-use lease and current snapshot reader fence",
                "global store identity first",
                "exact payload inode second",
                "fork-inherited cross-process descriptor",
                "literal NUL",
                "remains deletion-free",
                "remote-filesystem behavior",
            )
        )
        and "## Rev0977: payload-use lease and current snapshot reader fence"
        in readme
        and "anonsync.peer-service.status.v26" in readme
        and "anonsync.local-retention-plan.response.v6" in readme,
        "rev0977_records_exact_protocol_nonclaims_research_and_source_hygiene",
        "the design record, revision notes, and README preserve the corrected defect, lock order, executable evidence, advisory and filesystem limits, and deletion-free boundary",
    )

    require(
        rev0977_verifier_block.count(
            "if revision_number is not None and revision_number >= 977:"
        ) == 1
        and all(
            token in rev0977_verifier_block
            for token in (
                "PAYLOAD_USE_LEASE_AND_SNAPSHOT_READER_FENCE_AUDIT_rev0977.md",
                "REVISION_NOTES_rev0977.md",
                "README.md",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0977_package_policy_binds_protocol_consumers_tests_and_records",
        "a sealed rev0977 package cannot omit the payload-use protocol, snapshot and mutator implementations, product-lifetime comments, focused process regression, audit, notes, or verifier",
    )

    require(
        "class PayloadStoreLiveCapabilityRegistry final" in store
        and "anonsync:sync-replica-file-payload-store-live-capability-process-store-scope:v1" in store
        and "anonsync:sync-replica-file-payload-store-live-capability-set:v2" in store
        and "class PayloadStoreLiveCapabilityRegistryBroker final" in store
        and "kLiveCapabilityFixedRecordAllowance = 4096U" in store
        and "kMaximumProcessLiveCapabilityRecordsPerStore" in store
        and store.count(
            "PayloadStoreLiveCapabilityRegistration live_capability_registration;"
        ) == 4
        and all(
            token in store
            for token in (
                "PayloadStoreLiveCapabilityKind::Snapshot",
                "PayloadStoreLiveCapabilityKind::OpenedPayload",
                "PayloadStoreLiveCapabilityKind::TargetedAccess",
                "PayloadStoreLiveCapabilityKind::MutationBatch",
                "live-capability record frontier is exhausted",
                "live-capability registration IDs are exhausted",
                "process_counter.compare_exchange_weak(",
                "payload-store live-capability process counter is exhausted",
                "std::terminate();",
            )
        ),
        "rev0977_bounded_registry_tracks_every_same_owner_payload_capability_fail_closed",
        "one bounded exact same-process store registry tracks all four move-only capability classes without silently losing roots",
    )

    require(
        "std::uint64_t activity_generation = 0U;" in store_h
        and "std::uint64_t activity_generation_ = 0U;" in store
        and "bool activity_generation_exhausted_ = false;" in store
        and store.count("++activity_generation_;") == 2
        and "live-capability activity generation is exhausted" in store
        and "out.activity_generation = activity_generation_;" in store
        and "append_u64(digest, activity_generation_)" not in store
        and "activity_generation" not in historical_inventory_json
        and "friend struct SyncReplicaFilePayloadStoreTestAccess;" in store_h,
        "rev0977_interval_activity_generation_closes_complete_capability_aba",
        "every successful register and unregister advances a fail-closed interval witness while canonical root identity and serialized pages remain activity-generation cold",
    )

    require(
        all(
            token in runtime
            for token in (
                "test_live_capability_cutpoint_detects_complete_interval_aba",
                "SyncReplicaFilePayloadStoreTestAccess",
                "before.capability_set_digest == after.capability_set_digest",
                "before.activity_generation < after.activity_generation",
                "before != after",
                "complete create-and-destroy capability interval aliased equal live cutpoints",
            )
        ),
        "rev0977_runtime_oracle_proves_complete_create_destroy_interval_is_not_equal",
        "the focused C++ regression returns to the same empty canonical set yet requires the non-durable activity witness to distinguish the enclosing cutpoints",
    )

    require(
        "struct SyncReplicaFilePayloadStoreOpenedPayload::State final {\n    PayloadStoreLiveCapabilityRegistration live_capability_registration;" in store
        and "struct SyncReplicaFilePayloadStoreSnapshot::State final {\n    PayloadStoreLiveCapabilityRegistration live_capability_registration;" in store
        and "candidate.live_capability_registration.registry().get() !=\n            state_->live_capability_registry.get()" in store
        and "excluded snapshot registration is not live" in store
        and "append_u64(digest, registration_id);" in store
        and "append_u64(digest, static_cast<std::uint64_t>(record.kind));" in store
        and "out.opened_payload_roots.erase(" in store
        and "distinct opened-payload root bytes overflow" in store,
        "rev0977_raii_order_exact_origin_and_registration_identity_prevent_capability_aliases",
        "descriptor/state teardown precedes root removal, foreign owners cannot subtract capabilities, and same-count replacements change the canonical set",
    )

    require(
        retention_plan_owner.count(
            "live_capability_cutpoint_excluding_snapshot_or_throw("
        ) == 2
        and "live_capabilities_after != live_capabilities_before" in retention_plan_owner
        and "RetentionLiveCapabilitySet" in retention_plan_owner
        and "anonsync:sync-replica-retention-plan-deletion-free-mark:v5" in folder_scan
        and all(
            token in retention_plan_owner
            for token in (
                "live_capability_process_store_scope_digest",
                "live_capability_process_store_scope_incarnation_digest",
                "live_capability_set_digest",
                "live_snapshot_count",
                "live_opened_payload_count",
                "live_targeted_access_count",
                "live_mutation_batch_count",
                "distinct_live_opened_payload_root_count",
                "live_capability_rooted_physical_payload_count",
                "unreferenced_live_capability_rooted_payload_count",
                "same_process_store_live_capability",
            )
        )
        and "RetentionLiveCapabilitySet = 9U" in historical_query_h
        and 'return "retention_live_capability_set";' in historical_query_h,
        "rev0978_retention_projection_is_bracketed_and_mark_v4_binds_process_store_roots",
        "the writer-fenced planner excludes only its own exact snapshot, rejects any process-store live-set drift, and binds all live-root aggregates into mark v4",
    )

    require(
        r'\"same_process_store_live_payload_capabilities_bound\":true' in historical_inventory_json
        and r'\"independently_opened_same_process_store_owner_live_payload_capabilities_bound\":true' in historical_inventory_json
        and r'\"independent_store_owner_live_payload_capabilities_bound\":false' in historical_inventory_json
        and r'\"cross_process_live_payload_capabilities_bound\":false' in historical_inventory_json
        and r'\"already_copied_response_bytes_bound\":false' in historical_inventory_json
        and r'\"live_payload_capabilities\":{\"process_store_scope_digest\":' in historical_inventory_json
        and r'\"same_process_store_live_capability\":' in historical_inventory_json
        and '"anonsync.peer-service.status.v26"' in peer_status_h
        and "anonsync.local-retention-plan.response.v6" in local_status
        and "anonsync.local-retention-plan.response.v6" in local_status_runtime
        and "anonsync.local-retention-plan.response.v6" in service_configuration_runtime
        and "anonsync.peer-service.status.v26" in service_configuration_runtime
        and "anonsync.peer-service.status.v26" in service_i2p_ingress_runtime,
        "rev0978_v23_v5_operator_contract_exposes_same_process_owner_truth_and_external_nonclaims",
        "live, terminal, local, configured-service, and I2P readers share one canonical bounded result while other processes and copied buffers remain explicitly unbound",
    )

    require(
        all(
            token in folder_scan_runtime
            for token in (
                "live same-process-store snapshot was not projected as an all-payload retention root",
                "same-count live snapshot replacement aliased the exact capability-set cutpoint",
                "released same-process-store snapshot remained a retention root",
                "opened payload descriptor was not projected as one exact same-process-store live root",
                "released opened payload descriptor remained a retention root",
            )
        )
        and all(
            token in local_status_runtime
            for token in (
                "same_process_store_live_payload_capabilities_bound",
                "live_payload_capabilities",
                "same_process_store_live_capability",
            )
        )
        and all(
            token in service_configuration_runtime
            for token in (
                "process_store_scope_digest",
                "process_store_scope_incarnation_digest",
                "capability_set_digest",
                "may_reopen_all_current_payloads",
                "unreferenced_rooted_payload_count",
            )
        ),
        "rev0978_runtime_oracles_prove_process_store_exact_descriptor_replacement_and_release_boundaries",
        "focused C++ and real-process readers falsify aggregate-only aliases across same-process owners and require roots to disappear when their move-only capability dies",
    )

    require(
        all(
            token in normalized_prose(live_capability_design)
            for token in (
                "Bounded same-owner registry",
                "Exact capability-set cutpoint",
                "interval ABA hole",
                "Retention-plan bracketing and mark v3",
                "same retained payload-store owner",
                "already copied outbound",
                "does not add policy",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0977_notes)
            for token in (
                "Exact same-owner live payload-capability cutpoint",
                "same-count capability replacement",
                "complete create-and-destroy interval ABA",
                "deletion-free",
                "independently opened store owners",
            )
        )
        and "## Rev0977: exact same-owner live payload-capability cutpoint" in readme
        and "anonsync.peer-service.status.v22" in readme
        and "anonsync.local-retention-plan.response.v4" in readme
        and "## Rev0976: exact transient-namespace retention cutpoint" in readme
        and "anonsync.local-retention-plan.response.v3" in readme,
        "rev0977_records_preserve_exact_owner_history_and_immutable_schema",
        "sealed rev0977 records retain the exact-owner boundary, v22/v4 schema, explicit nonclaims, and safe next protocol",
    )

    require(
        rev0977_verifier_block.count(
            "if revision_number is not None and revision_number >= 977:"
        ) == 1
        and all(
            token in rev0977_verifier_block
            for token in (
                "EXACT_LIVE_PAYLOAD_CAPABILITY_CUTPOINT_AUDIT_rev0977.md",
                "REVISION_NOTES_rev0977.md",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
            )
        ),
        "rev0977_package_policy_binds_registry_mark_schema_regressions_and_authority_record",
        "release verification requires every implementation, renderer, schema, test, design, notes, audit, and package-policy surface changed by the exact live-capability cutpoint",
    )

    writer_fenced_snapshot = function_body(
        store,
        "SyncReplicaFilePayloadStore::snapshot_with_reuse_policy_or_throw(",
    )
    writer_fenced_verify = function_body(
        store,
        "void SyncReplicaFilePayloadStore::\nverify_writer_fenced_retention_snapshot_or_throw(",
    )
    writer_fenced_probe = function_body(
        store,
        "writer_fenced_payload_use_exclusive_available_or_throw(",
    )

    require(
        all(
            token in store
            for token in (
                "PayloadStoreLiveCapabilityRegistryBroker",
                "kLiveCapabilityProcessStoreScopeDomain",
                "kLiveCapabilityProcessStoreScopeIncarnationDomain",
                "kMaximumProcessLiveCapabilityStoreScopes",
                "kMaximumProcessLiveCapabilityRecordsPerStore",
                "std::weak_ptr<PayloadStoreLiveCapabilityRegistry>",
                "process_store_scope_digest",
                "process_store_scope_incarnation_digest",
            )
        )
        and ordered(
            function_body(store, "acquire_or_throw("),
            "std::lock_guard<std::mutex> lock(mutex_)",
            "position->second.expired()",
            "registries_.size() >=",
            "std::make_shared<PayloadStoreLiveCapabilityRegistry>",
            "registries_.emplace",
        )
        and "new_payload_store_live_capability_process_store_scope_incarnation_or_throw"
        in store,
        "rev0978_process_store_broker_is_deterministic_bounded_and_reincarnates_after_release",
        "same-process owners over one attested immutable store share one bounded weakly retained registry and a fresh scope incarnation after final release",
    )

    require(
        "candidate.verification_cache.get() !=\n            state_->verification_cache.get()" in store
        and "payload snapshot was not issued by the exact retained store owner" in store
        and "candidate.live_capability_registration.registry().get() !=\n            state_->live_capability_registry.get()" in store
        and "test_live_capability_scope_spans_independent_store_owners" in runtime
        and "test_live_capability_scope_recreates_after_final_owner_release" in runtime
        and "shared live registry accidentally authorized foreign-owner snapshot handoff" in runtime,
        "rev0978_shared_lifetime_visibility_does_not_lend_exact_owner_integrity_authority",
        "the shared process-store census includes independently opened owners while snapshot handoff still requires the exact owner-local verification cache and integrity epoch",
    )

    require(
        "std::unique_ptr<StoreLease> retained_writer_fence" in store
        and "retain_exclusive_writer_fence" in writer_fenced_snapshot
        and "SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation" in writer_fenced_snapshot
        and "snapshot->retained_writer_fence" in writer_fenced_snapshot
        and "current-byte recheck and writer-fenced retention modes cannot " in writer_fenced_snapshot
        and "read-only inspection cannot retain a writer-fenced retention " in writer_fenced_snapshot
        and ordered(
            writer_fenced_verify,
            "require_exact_snapshot_origin_or_throw",
            "retained_writer_fence->mode()",
            "retained_writer_fence->verify_or_throw",
            "root_authority.verify_or_throw",
        ),
        "rev0978_retention_snapshot_holds_exact_global_writer_fence_and_rejects_unsafe_modes",
        "the complete observation transfers the exact store-global EX lease into a private metadata-only snapshot through final root and identity reproof",
    )

    require(
        ordered(
            writer_fenced_probe,
            "verify_writer_fenced_retention_snapshot_or_throw",
            "find_entry",
            "open_store_file_or_throw",
            "require_private_regular_file_or_throw",
            "same_regular_file_observation",
            "try_acquire_payload_use_flock_nonblocking_or_throw",
            "verify_named_regular_file_or_throw",
            "verify_writer_fenced_retention_snapshot_or_throw",
        )
        and "LOCK_EX" in writer_fenced_probe
        and "candidate changed after the writer-fenced scan" in writer_fenced_probe
        and "test_writer_fenced_retention_snapshot_excludes_namespace_work_and_probes_inode_use" in runtime,
        "rev0978_returned_candidate_probe_is_rooted_exact_inode_nonblocking_and_page_bounded",
        "each returned unreferenced object is re-opened under the global fence, matched to the scanned inode, probed for exact-inode EX availability, and re-proved before release",
    )

    require(
        all(
            token in retention_plan_owner
            for token in (
                "snapshot_writer_fenced_for_retention_or_throw",
                "writer_fenced_observation = true",
                "cooperating_new_namespace_activity_excluded_during_observation = true",
                "writer_fenced_payload_use_exclusive_available_or_throw",
                "writer_fenced_candidate_page_digest",
                "durable_candidate_witness_digest",
                "verify_writer_fenced_retention_snapshot_or_throw",
                "live_capabilities_after != live_capabilities_before",
                "replica_final",
            )
        )
        and retention_plan_owner.find("model.for_each_active_path")
        < retention_plan_owner.find("snapshot_writer_fenced_for_retention_or_throw")
        < retention_plan_owner.find("writer_fenced_payload_use_exclusive_available_or_throw")
        < retention_plan_owner.find("replica_final")
        < retention_plan_owner.find("verify_writer_fenced_retention_snapshot_or_throw"),
        "rev0978_planner_builds_causal_projection_before_writer_fenced_physical_merge_and_final_cutpoints",
        "the immutable causal projection is built before the stall interval; the exact store-global writer fence then spans physical observation and merge, candidate probes, final SQLite snapshots, root proof, and final process-store live-set equality",
    )

    require(
        "anonsync:sync-replica-retention-plan-durable-candidate-witness:v2" in folder_scan
        and "anonsync:sync-replica-retention-plan-writer-fenced-candidate-page:v2" in folder_scan
        and "anonsync:sync-replica-retention-plan-deletion-free-mark:v5" in folder_scan
        and "live_capability_process_store_scope_incarnation_digest" not in function_body(
            folder_scan, "Sha256DigestBuilder durable_candidate_witness"
        )
        and all(
            token in retention_plan_owner
            for token in (
                "source_operation_set_digest",
                "source_evidence_set_digest",
                "source_historical_version_pin_set_digest",
                "source_visible_state_digest",
                "source_payload_snapshot_digest",
                "source_payload_transient_namespace_digest",
                "unreferenced_candidate_set_digest",
            )
        ),
        "rev0978_restart_stable_candidate_witness_is_separate_from_process_interval_mark_and_page_probe_digest",
        "the durable witness binds the complete source and candidate set without process incarnation while mark v4 and the page digest retain their narrower interval identities",
    )

    require(
        r'\"writer_fenced_observation\":' in historical_inventory_json
        and r'\"cooperating_new_namespace_activity_excluded_during_observation\":' in historical_inventory_json
        and r'\"independently_opened_same_process_store_owner_live_payload_capabilities_bound\":true' in historical_inventory_json
        and r'\"cross_process_live_payload_capabilities_bound\":false' in historical_inventory_json
        and r'\"writer_fenced_candidate_page_digest\":' in historical_inventory_json
        and r'\"durable_candidate_witness_digest\":' in historical_inventory_json
        and r'\"payload_use_disposition\":' in historical_inventory_json
        and "anonsync.peer-service.status.v26" in peer_status_h
        and "anonsync.local-retention-plan.response.v6" in local_status
        and all(
            token in service_configuration_runtime
            for token in (
                "writer_fenced_observation",
                "cooperating_new_namespace_activity_excluded_during_observation",
                "writer_fenced_candidate_page_digest",
                "durable_candidate_witness_digest",
                "payload_use_disposition",
                "independently_opened_same_process_store_owner_live_payload_capabilities_bound",
                "cross_process_live_payload_capabilities_bound",
            )
        ),
        "rev0978_v23_v5_runtime_contract_parses_writer_fence_process_scope_probe_and_precise_nonclaims",
        "canonical C++ rendering and the real service oracle agree on every new writer-fence, process-store, candidate-witness, and cross-process boundary field",
    )

    require(
        all(
            token in normalized_prose(process_store_writer_fence_design)
            for token in (
                "Defect 1: independently opened same-process owners were invisible",
                "Defect 2: planning did not hold the global writer fence",
                "Digest separation",
                "Explicit nonclaims",
                "Next safe product edge",
            )
        )
        and all(
            token in normalized_prose(rev0978_notes)
            for token in (
                "Process-store live-capability composition",
                "Writer-fenced retention observation",
                "Restart-stable candidate identity",
                "Deliberately did not persist a mark",
            )
        )
        and "## Rev0978: process-store live roots and writer-fenced retention observation" in readme
        and "anonsync.peer-service.status.v26" in readme
        and "anonsync.local-retention-plan.response.v6" in readme,
        "rev0978_records_bind_the_exact_defects_mechanisms_nonclaims_and_next_safe_collection_edge",
        "the design audit, notes, and README state the same-process composition defect, writer-fence correction, digest separation, deletion-free boundary, and next durable-policy protocol",
    )

    require(
        rev0978_verifier_block.count(
            "if revision_number is not None and revision_number >= 978:"
        ) == 1
        and all(
            token in rev0978_verifier_block
            for token in (
                "PROCESS_STORE_LIVE_CAPABILITY_AND_WRITER_FENCED_RETENTION_AUDIT_rev0978.md",
                "REVISION_NOTES_rev0978.md",
                "CMakeLists.txt",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/test_anonsync_service_i2p_ingress.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0978_package_policy_binds_process_store_writer_fence_candidate_probe_tests_and_records",
        "release verification requires every implementation, renderer, schema, runtime oracle, audit, notes, and package-policy surface changed by rev0978",
    )

    retention_mark_link = cmake_call(
        cmake,
        "target_link_libraries(anonsync_sync_replica_file_payload_retention_mark",
    )
    require(
        "add_library(anonsync_sync_replica_file_payload_retention_mark STATIC"
        in cmake
        and "src/sync_replica_file_payload_retention_mark.cpp" in cmake
        and "anonsync_sha256_digest" in retention_mark_link
        and "anonsync_sync_posix_regular_file_snapshot_codec"
        in retention_mark_link
        and "add_executable(anonsync_sync_replica_file_payload_retention_mark_test"
        in cmake
        and cmake.count(
            "anonsync_sync_replica_file_payload_retention_mark_test"
        ) >= 5,
        "rev0979_retention_mark_codec_and_test_are_product_and_sanitizer_graph_members",
        "the durable mark is one narrow library with an ordinary product test retained by compile, link, dependency, CTest, and product lanes",
    )

    require(
        ".anonsync-payload-retention-mark-v1" in retention_mark_h
        and "kSyncReplicaFilePayloadRetentionMarkMaximumGraceSeconds"
        in retention_mark_h
        and "kMagic" in retention_mark
        and "kEncodedU64Count = 10U" in retention_mark
        and "kSourceDigestCount = 8U" in retention_mark
        and "encoded.append(sha256_hex(encoded))" in retention_mark
        and "Continuity evidence only" in retention_mark_h
        and "external anti-rollback counter" in retention_mark_h
        and "length is not the exact v1 size" in retention_mark
        and "checksum is invalid" in retention_mark,
        "rev0979_mark_format_is_fixed_width_checksum_framed_and_versioned",
        "the record has one fixed internal basename, exact geometry, canonical digest fields, and a checksum over the complete magic/body frame",
    )

    require(
        "policy grace deadline overflows" in retention_mark
        and "policy candidate count exceeds store capacity" in retention_mark
        and "policy candidate bytes exceed store capacity" in retention_mark
        and "observed candidate count exceeds policy" in retention_mark
        and "observed candidate bytes exceed policy" in retention_mark
        and "policy collection count exceeds candidates" in retention_mark
        and "policy collection bytes exceed candidates" in retention_mark
        and "contains no unreferenced payload candidates" in retention_mark,
        "rev0979_mark_policy_and_candidate_frontiers_fail_closed",
        "grace arithmetic, store capacity, policy capacity, collection capacity, and nonempty-candidate requirements are validated before evidence is usable",
    )

    require(
        "retention_mark_present" in store
        and "retention_mark_contents_requested" in store
        and "retention_mark_observation_known" in store_h
        and "retention_mark_observation_known" in store
        and "scanned.retention_mark_contents_requested" in store
        and "ReadOnlyInspect remains byte-cold" in store_h
        and "retention_mark_observation_known()" in runtime,
        "rev0979_mark_observation_distinguishes_synchronized_validity_from_byte_cold_forensics",
        "clean absence, usable or damaged synchronized evidence, and deliberately uninspected forensic presence are separate snapshot states",
    )

    require(
        "kSyncReplicaFilePayloadRetentionMarkBasename" in store
        and "retention mark changed during namespace traversal" in store
        and "bootstrap.retention_mark_present" in store
        and "out.retention_mark_present = retention_mark.present" in store
        and "snapshot->retention_mark_present = scanned.retention_mark_present"
        in store
        and "transient_namespace_digest_or_throw" in store,
        "rev0979_mark_is_recognized_internal_metadata_with_rooted_traversal_reproof",
        "the fixed basename is observed before and during complete scans, fresh bootstrap refuses adoption, and snapshots expose it without classifying it as payload content",
    )

    require(
        "verify_writer_fenced_retention_snapshot_or_throw" in retention_mark_publication
        and "retained_writer_fence" in retention_mark_publication
        and "mark.store_identity_sha256" in retention_mark_publication
        and "mark.store_identity_metadata" in retention_mark_publication
        and "mark.generation = current.mark->generation + 1U"
        in retention_mark_publication
        and "write_sync_file_atomically_replace_expected_under_directory_or_throw"
        in retention_mark_publication
        and "write_sync_file_atomically_create_new_under_directory_or_throw"
        in retention_mark_publication
        and "observe_exact_committed" in retention_mark_publication
        and "const std::exception_ptr original = std::current_exception()"
        in retention_mark_publication
        and "Reconciliation is intentionally best effort"
        in retention_mark_publication
        and retention_mark_publication.rfind("std::rethrow_exception(original)")
        > retention_mark_publication.rfind(
            "Reconciliation is intentionally best effort"
        )
        and "snapshot_with_reuse_policy_or_throw" not in retention_mark_publication,
        "rev0979_mark_publication_reuses_the_exact_writer_fenced_snapshot_without_rescan",
        "identity and generation are store-owned, publication is atomic and conditionally replaced, committed bytes are reopened, secondary reconciliation failure preserves the primary publication exception, and no second complete snapshot is acquired",
    )

    require(
        "SyncReplicaPayloadRetentionMarkRequest" in folder_scan_h
        and "expected_source_replica_state_generation" in folder_scan_h
        and "expected_durable_candidate_witness_digest" in folder_scan_h
        and "marked_at_unix_seconds" in folder_scan_h
        and "SyncReplicaFilePayloadRetentionPolicy policy" in folder_scan_h
        and "ExactPayloadAvailability" in retention_mark_owner
        and "validate_sync_replica_file_payload_retention_policy_for_store_or_throw"
        in retention_mark_owner
        and retention_mark_owner.find(
            "validate_sync_replica_file_payload_retention_policy_for_store_or_throw"
        ) < retention_mark_owner.find("query.maximum_entries = 1U")
        and "payload_store_limits.max_entries" in retention_mark_owner
        and "payload_store_limits.max_indexed_bytes" in retention_mark_owner
        and "query.maximum_entries = 1U" in retention_mark_owner
        and "external exact-image anti-rollback" in folder_scan_h
        and "database_recovery_epoch" in folder_scan_h,
        "rev0979_folder_owner_requires_exact_v4_source_generation_witness_and_policy",
        "marking cannot start from metadata-only history, a cursor page, an unknown generation, a malformed witness, malformed policy, or a store-impossible capacity frontier; all fail before writer-fenced payload observation",
    )

    require(
        "RetentionMarkPublication = 10U" in historical_query_h
        and 'return "retention_mark_publication"' in historical_query_h
        and retention_plan_impl.count(
            "expected_source_replica_state_generation"
        ) >= 2
        and "candidate witness changed before" in retention_plan_impl
        and "publish_retention_mark_or_throw" in retention_plan_impl
        and "const SyncReplicaSqliteSnapshot replica_after_mark"
        in retention_plan_impl
        and "source changed during durable" in retention_plan_impl,
        "rev0979_same_lineage_source_generation_and_final_sqlite_reproof_close_digest_aba",
        "the mark is checked before observation, before publication, and after commit; same-lineage source drift is typed and leaves any committed older-generation record conservative without claiming database anti-rollback authority",
    )

    require(
        "test_round_trip_and_digest" in retention_mark_runtime
        and "test_checksum_and_framing_rejection" in retention_mark_runtime
        and "test_policy_and_candidate_rejection" in retention_mark_runtime
        and "deadline overflow" in retention_mark_runtime
        and "linked identity" in retention_mark_runtime
        and "zero-byte candidate" in retention_mark_runtime,
        "rev0979_codec_runtime_covers_framing_overflow_capacity_identity_and_zero_byte_candidates",
        "the focused codec regression exercises canonical round trip and malformed policy/record boundaries rather than only one happy path",
    )

    require(
        "test_retention_mark_is_durable_identity_bound_and_snapshot_cold"
        in runtime
        and "fresh process owner did not rediscover the exact retention mark"
        in runtime
        and "damaged retention evidence was hidden or treated as authority"
        in runtime
        and "byte-cold forensic inspection claimed retention-mark authority"
        in runtime
        and "writer-fenced retention mark did not preserve exact source, policy, or payload accounting"
        in folder_scan_runtime
        and "caught_retention_mark_generation_aba" in folder_scan_runtime
        and "stale candidate witness replaced the current durable retention mark"
        in folder_scan_runtime
        and "retention policy spent payload-store work before rejecting an impossible count frontier"
        in folder_scan_runtime
        and "retention policy spent payload-store work before rejecting an impossible byte frontier"
        in folder_scan_runtime,
        "rev0979_store_and_folder_runtime_prove_restart_damage_accounting_aba_and_stale_witness_boundaries",
        "focused tests cover durable discovery, conservative damaged replacement, byte-cold forensics, capacity preflight ahead of a held writer lease, witness handoff, monotonic pin ABA, and no stale replacement",
    )

    require(
        all(
            token in normalized_prose(durable_retention_mark_design)
            for token in (
                "Fixed-width record",
                "Exact writer-fenced publication handoff",
                "Same-lineage causal ABA fence and rollback boundary",
                "Metadata cannot invalidate its own witness",
                "Observation-known refactor",
                "Compatibility boundary",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0979_notes)
            for token in (
                "Durable retention mark and policy",
                "Exact publication handoff",
                "Adjacent audit/refactor",
                "deletion-free",
            )
        )
        and all(
            token in normalized_prose(durable_retention_mark_design)
            for token in (
                "does not add a second complete payload scan or hash pass",
                "not an external anti-rollback counter",
                "exact older image can recreate its generation",
                "replacement generation is continuity evidence only",
            )
        )
        and all(
            token in normalized_prose(rev0979_notes)
            for token in (
                "within one retained database lineage",
                "future collection must bind a recovery epoch or reset age",
                "overbroad claim that publication never rehashes",
            )
        )
        and "## Rev0979: durable deletion-free retention mark and ABA fence"
        in readme
        and "not an external anti-rollback counter" in readme
        and "replica-database incarnation or recovery epoch" in readme,
        "rev0979_records_state_the_durable_evidence_authority_nonclaims_and_downgrade_boundary",
        "audit, notes, README, and bootstrap distinguish same-lineage ABA protection from database rollback, mark-generation continuity from freshness, and no-added-scan publication from guaranteed byte-cold observation",
    )

    require(
        rev0979_verifier_block.count(
            "if revision_number is not None and revision_number >= 979:"
        ) == 1
        and all(
            token in rev0979_verifier_block
            for token in (
                "DURABLE_PAYLOAD_RETENTION_MARK_AND_POLICY_AUDIT_rev0979.md",
                "REVISION_NOTES_rev0979.md",
                "CMakeLists.txt",
                "src/sync_replica_file_payload_retention_mark.hpp",
                "src/sync_replica_file_payload_retention_mark.cpp",
                "src/sync_replica_file_payload_store.hpp",
                "src/sync_replica_file_payload_store.cpp",
                "src/sync_replica_historical_version_query.hpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "tests/sync_replica_file_payload_retention_mark_test.cpp",
                "tests/sync_replica_file_payload_store_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0979_package_policy_binds_codec_store_owner_tests_records_and_audit",
        "release verification requires every implementation, runtime, record, structural-audit, and package-policy surface changed by rev0979",
    )

    require(
        all(
            token in sqlite_owner
            for token in (
                "constexpr std::uint64_t kDatabaseLineageSchemaVersion = 7U;",
                "database_incarnation_sha256 TEXT NOT NULL",
                "database_recovery_epoch_be BLOB NOT NULL",
                "mint_database_incarnation_or_throw(",
                "RAND_bytes(",
                "anonsync-sync-replica-sqlite-database-incarnation-v1",
                "meta.database_recovery_epoch = 1U;",
            )
        ),
        "rev0980_schema_v7_mints_one_random_database_incarnation_and_nonzero_epoch",
        "new and migrated databases gain a CSPRNG-derived lineage identity rather than deriving authority from path, time, PID, or logical contents",
    )

    require(
        "constexpr std::uint64_t kHistoricalPinSchemaVersion = 6U;" in sqlite_owner
        and "constexpr std::array<SchemaDefinition, 11> kHistoricalPinSchema" in sqlite_owner
        and "historical_pin_schema_cutpoint_digest_or_throw" in sqlite_owner
        and "anonsync-sync-replica-sqlite-cutpoint-v6" in sqlite_owner
        and "schema_matches(observed, kHistoricalPinSchema)" in sqlite_owner
        and "label_ + \" schema v6 to v9\"" in sqlite_owner
        and "prior.outbox, prior.historical_version_pins" in sqlite_owner
        and "test_exact_v6_migration_preserves_pins_and_mints_database_lineage"
        in sqlite_owner_runtime,
        "rev0980_exact_v6_migration_preserves_pins_before_minting_v7_lineage",
        "the released v6 schema and cutpoint remain exact migration authority; v7 publication retains causal, outbox, clock, policy, limit, and pin state",
    )

    v7_cutpoint_body = function_body(
        sqlite_owner, "std::string database_lineage_cutpoint_digest_or_throw(")
    shared_cutpoint_authority_body = function_body(
        sqlite_owner, "void append_cutpoint_authority(")
    require(
        ordered(
            v7_cutpoint_body,
            "anonsync-sync-replica-sqlite-cutpoint-v7",
            "meta.database_incarnation_sha256",
            "meta.database_recovery_epoch",
            "append_cutpoint_authority(digest, meta)",
            "historical_version_pin_set_digest",
        )
        and ordered(
            shared_cutpoint_authority_body,
            "meta.state_generation",
            "meta.policy_generation",
            "meta.operation_set_digest",
            "meta.evidence_set_digest",
            "meta.visible_state_digest",
            "meta.outbox_digest",
        )
        and "database_incarnation_sha256" in sqlite_owner_h
        and "database_recovery_epoch" in sqlite_owner_h,
        "rev0980_v7_cutpoint_binds_lineage_before_all_mutable_replica_authority",
        "the v7 cutpoint prefixes exact lineage, then composes the shared causal/policy authority and historical-pin root without duplicating the shared digest grammar",
    )

    require(
        "advance_database_recovery_epoch_or_throw(" in sqlite_owner_h
        and all(
            token in function_body(
                sqlite_owner,
                "SyncReplicaSqliteOwner::advance_database_recovery_epoch_or_throw(",
            )
            for token in (
                "SyncSqliteTransactionMode::Immediate",
                "expected_database_incarnation_sha256",
                "expected_database_recovery_epoch",
                "expected_cutpoint_digest",
                "increment_or_throw",
                "database recovery epoch publication",
            )
        )
        and "test_database_incarnation_and_explicit_recovery_epoch"
        in sqlite_owner_runtime,
        "rev0980_explicit_recovery_epoch_is_one_exact_atomic_full_state_transition",
        "stale expectations fail under the writer transaction; an accepted recovery preserves all prior state while advancing epoch and generation exactly once",
    )

    require(
        all(
            token in folder_scan + folder_scan_h
            for token in (
                "source_replica_database_incarnation_sha256",
                "source_replica_database_recovery_epoch",
                "expected_source_replica_database_incarnation_sha256",
                "expected_source_replica_database_recovery_epoch",
                "anonsync:sync-replica-retention-plan-durable-candidate-witness:v2",
                "anonsync:sync-replica-retention-plan-writer-fenced-candidate-page:v2",
                "anonsync:sync-replica-retention-plan-deletion-free-mark:v5",
            )
        )
        and retention_plan_impl.count(
            "source_replica_database_incarnation_sha256"
        ) >= 4
        and retention_plan_impl.count(
            "source_replica_database_recovery_epoch"
        ) >= 4,
        "rev0980_retention_candidate_page_and_mark_domains_bind_exact_database_lineage",
        "planning and mark publication compare incarnation, recovery epoch, and state generation before payload work, before commit, and after commit",
    )

    require(
        "Opaque v2 witness" in retention_mark_h
        and "preserves the fixed v1" in retention_mark_h
        and "source_replica_database_incarnation_sha256" in historical_inventory_json
        and "source_replica_database_recovery_epoch" in historical_inventory_json
        and '"anonsync.peer-service.status.v26"' in peer_status_h
        and '"anonsync.local-retention-plan.response.v6"' in local_status
        and "source_replica_database_incarnation_sha256"
        in service_configuration_runtime
        and "source_replica_database_recovery_epoch"
        in service_configuration_runtime,
        "rev0980_fixed_retention_record_transitively_binds_lineage_and_runtime_exposes_it",
        "the existing checksum-framed record carries the v2 witness without a competing codec, while status and the real process parser expose canonical lineage fields",
    )

    require(
        "test_retention_witness_binds_exact_replica_database_incarnation"
        in folder_scan_runtime
        and "independent identical replica databases aliased retention authority"
        in folder_scan_runtime
        and "caught_foreign_database" in folder_scan_runtime
        and "caught_stale_recovery_epoch" in folder_scan_runtime
        and "explicit replica recovery epoch did not invalidate retention authority"
        in folder_scan_runtime
        and "test_exact_v6_migration_preserves_pins_and_mints_database_lineage"
        in sqlite_owner_runtime
        and "test_database_incarnation_and_explicit_recovery_epoch"
        in sqlite_owner_runtime,
        "rev0980_runtime_proves_cross_database_separation_v6_migration_and_recovery_invalidation",
        "focused tests distinguish identical independent databases, preserve v6 pins, reject stale lineage before payload observation, and invalidate pre-recovery evidence without changing causal facts",
    )

    require(
        all(
            token in normalized_prose(database_lineage_design)
            for token in (
                "Defect: identical databases could alias retention authority",
                "Schema v7 lineage",
                "Exact v6 migration",
                "Explicit recovery epoch",
                "Retention-witness binding",
                "What this does not prove",
                "external anti-rollback authority",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0980_notes)
            for token in (
                "Database-lineage correction",
                "Retention authority correction",
                "Adjacent audit/refactor",
                "deletion-free",
            )
        )
        and "## Rev0980: database incarnation, recovery epoch, and retention witness"
        in readme
        and "not external anti-rollback authority" in readme,
        "rev0980_records_exact_authority_nonclaims_migration_and_rejected_contamination",
        "design, notes, README, and bootstrap distinguish in-database lineage continuity from exact-image anti-rollback and preserve the deletion-free product boundary",
    )

    require(
        rev0980_verifier_block.count(
            "if revision_number is not None and revision_number >= 980:"
        ) == 1
        and all(
            token in rev0980_verifier_block
            for token in (
                "REPLICA_DATABASE_LINEAGE_AND_RETENTION_WITNESS_AUDIT_rev0980.md",
                "REVISION_NOTES_rev0980.md",
                "src/sync_replica_sqlite_owner.hpp",
                "src/sync_replica_sqlite_owner.cpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_folder_scan_owner.cpp",
                "src/sync_replica_historical_version_inventory_json.cpp",
                "src/sync_replica_peer_service_status.hpp",
                "tests/sync_replica_sqlite_owner_test.cpp",
                "tests/sync_replica_folder_scan_owner_test.cpp",
                "tests/sync_local_status_socket_test.cpp",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0980_package_policy_binds_lineage_migration_retention_runtime_and_records",
        "release verification requires every schema, owner, renderer, regression, design, audit, and package-policy surface changed by the database-lineage correction",
    )

    require(
        "ExistingForensicReadOnly = 3U" in operational_database_h
        and "SqliteDescriptorRootedVfsAccess::ReadOnlyExisting"
        in operational_database_open
        and "SQLITE_OPEN_READONLY" in operational_database_open
        and "SQLITE_OPEN_CREATE" not in operational_database_open
        and "sqlite3_db_readonly" in operational_database_open,
        "rev0981_forensic_disposition_is_exact_existing_only_read_only_authority",
        "offline inspection has a first-class descriptor-rooted read-only open and cannot inherit writer or creation authority",
    )

    require(
        ordered(
            operational_database_open,
            "sqlite3_db_readonly",
            "sqlite_set_busy_timeout_or_throw",
            "retain_exclusive_locking_mode_or_throw",
            "configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw",
            "database_has_persistent_schema_or_throw",
            "journal_mode_or_throw",
        )
        and "private heap WAL index" in operational_database,
        "rev0981_read_only_wal_profile_precedes_first_persistent_page_read",
        "the connection selects private WAL indexing and hardened query-only behavior before schema or journal inspection can join shared-memory authority",
    )

    require(
        "open_attested_sync_replica_primary_database_or_throw"
        in folder_process_h
        and "open_attested_sync_replica_primary_database_read_only_or_throw"
        in folder_process_h
        and primary_database_open.count(
            "sync_replica_primary_database_binding_or_throw"
        ) == 1
        and "attest_sync_replica_sqlite_deployment_binding_or_throw"
        in primary_database_open
        and "open_attested_sync_replica_primary_database_or_throw("
        in folder_process,
        "rev0981_folder_owner_and_offline_commands_share_one_attested_primary_database_seam",
        "writer and forensic opens target the same manifest-selected role and deployment binding rather than duplicating pathname authority",
    )

    require(
        ordered(
            offline_recovery_ceremony,
            "SyncReplicaDeploymentManifest deployment_",
            "SyncReplicaPeerServiceSingletonOwner singleton_",
            "std::string label_",
        )
        and "open_attested_sync_replica_primary_database_read_only_or_throw"
            in offline_recovery_forensic
        and "inspect_sync_replica_sqlite_snapshot_read_only_or_throw"
            in offline_recovery_forensic
        and "SyncReplicaSqliteOwner" not in offline_recovery_forensic
        and "SyncReplicaOperationalDatabase database_"
            not in offline_recovery_ceremony
        and "SyncReplicaSqliteOwner replica_owner_"
            not in offline_recovery_ceremony,
        "rev0981_offline_ceremony_locks_deployment_before_short_lived_database_authority",
        "one owner acquires the deployment singleton before any local forensic or writer handle and retains no SQLite authority between stages",
    )

    require(
        ordered(
            offline_recovery_advance,
            'forensic_snapshot_or_throw("advance preflight")',
            "database recovery expectation is stale",
            "open_attested_sync_replica_primary_database_or_throw",
            "SyncReplicaSqliteOwner replica_owner(",
            "advance_database_recovery_epoch_or_throw",
        )
        and "BEGIN IMMEDIATE" in offline_recovery_advance,
        "rev0981_stale_expectations_fail_before_writable_open_then_transactionally_reproof",
        "invalid recovery authority cannot invoke WAL recovery, sidecar creation, checkpointing, migration, or another writer effect before rejection, while accepted authority is independently rechecked under the existing transaction",
    )

    require(
        "#include <type_traits>" in sqlite_owner
        and "std::is_nothrow_move_constructible_v" in sqlite_owner
        and ordered(
            database_recovery_epoch_advance,
            "SyncReplicaSqliteDatabaseRecoveryEpochResult result{",
            "attest_and_commit_staged_cutpoint_or_throw(",
            "return result;",
        )
        and "return {" not in database_recovery_epoch_advance,
        "rev0981_recovery_result_allocation_precedes_the_commit_cutpoint",
        "ordinary owner return construction cannot turn a committed recovery transition into an allocation exception",
    )

    require(
        r'payload_store_observed\":false' in sync_cli
        and r'folder_catalog_observed\":false' in sync_cli
        and r'rooted_files_observed\":false' in sync_cli
        and r'network_started\":false' in sync_cli
        and r'external_anti_rollback_authority\":false' in sync_cli
        and r'operator_asserted_database_recovery\":true'
        in database_recovery_advance
        and r'forensic_preflight_before_writable_open\":true'
        in database_recovery_advance
        and r'exact_transaction_reproof\":true'
        in database_recovery_advance
        and r'whole_image_rollback_reuse_excluded\":false'
        in database_recovery_advance
        and r'retention_age_reset_required_when_continuity_uncertain\":true'
        in database_recovery_advance,
        "rev0981_operator_responses_state_narrow_authority_and_anti_rollback_nonclaims",
        "the CLI reports exactly what it observed and explicitly denies backup validation, unrelated-store authority, and exact-image anti-rollback",
    )

    require(
        ordered(
            sync_once_command,
            "read_sync_replica_deployment_manifest_or_throw",
            "SyncReplicaPeerServiceSingletonOwner singleton_owner",
            "stream_route_from_options_or_throw",
            "folder_limits_from_options_or_throw",
            "load_tls_context_or_throw",
        )
        and "deployment is already owned by another AnonSync process"
        in peer_singleton,
        "rev0981_once_shares_the_deployment_singleton_before_route_tls_or_peer_authority",
        "one-shot synchronization can no longer overlap the retained service merely because lower-level SQLite leases serialize some individual writes",
    )

    require(
        "sqlite_family_fingerprint" in database_recovery_runtime
        and "read-only inspection changed SQLite family bytes"
        in database_recovery_runtime
        and "family_before_noncanonical" in database_recovery_runtime
        and "family_before_stale" in database_recovery_runtime
        and "family_before_reuse" in database_recovery_runtime
        and database_recovery_runtime.count("database recovery expectation is stale")
        >= 2
        and '"payload_store_observed": False' in database_recovery_runtime
        and '"folder_catalog_observed": False' in database_recovery_runtime
        and "recovery changed causal, outbox, policy, payload, effect, or membership state"
        in database_recovery_runtime
        and "expect_deployment_ownership_failure"
        in service_configuration_runtime
        and "database-recovery-inspect" in service_configuration_runtime
        and '"once", "--manifest"' in service_configuration_runtime
        and "must-not-open-i2p-private-destination"
            in service_configuration_runtime
        and "one-shot ownership before I2P private route"
            in service_configuration_runtime
        and "anonsync_sync_database_recovery_process_test" in cmake
        and cmake.count(
            "anonsync_sync_database_recovery_process_test"
        ) >= 3,
        "rev0981_process_oracles_prove_byte_stability_stale_rejection_narrow_scope_and_live_collision",
        "the normal product lane exercises inspection nonmutation, exact transition semantics, hidden unrelated stores, and both offline and one-shot singleton collisions",
    )

    require(
        '"format": "anonsync-replica-database-open-policy-audit-v22"'
        in database_open_policy_audit
        and "offline_recovery_selects_private_wal_index_before_first_page_read"
        in database_open_policy_audit
        and "offline_recovery_rejects_stale_expectation_before_writable_open_then_reproofs"
        in database_open_policy_audit
        and "offline_recovery_and_once_singleton_oracles_run_in_the_product_lane"
        in database_open_policy_audit
        and all(
            token in normalized_prose(offline_database_recovery_design)
            for token in (
                "Operator-visible recovery ceremony",
                "Stale rejection before writable open",
                "Read-only WAL ordering correction",
                "Shared targeting refactor",
                "One deployment, one shipping process owner",
                "What this does not prove",
                "external anti-rollback authority",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0981_notes)
            for token in (
                "Operator recovery surface",
                "Stale-expectation audit/refactor",
                "Lifecycle correction",
                "Read-only database refactor",
                "Boundary",
            )
        )
        and "## Rev0981: offline database recovery and one deployment owner"
        in readme,
        "rev0981_audit_and_records_bind_the_shipping_boundary_and_nonclaims",
        "source audit, design record, notes, and README agree that this is an offline in-database continuity assertion, not backup validation or external rollback protection",
    )

    require(
        rev0981_verifier_block.count(
            "if revision_number is not None and revision_number >= 981:"
        ) == 1
        and all(
            token in rev0981_verifier_block
            for token in (
                "OFFLINE_DATABASE_RECOVERY_AND_DEPLOYMENT_SINGLETON_AUDIT_rev0981.md",
                "REVISION_NOTES_rev0981.md",
                "CMakeLists.txt",
                "src/anonsync_sync.cpp",
                "src/sync_replica_operational_database.hpp",
                "src/sync_replica_operational_database.cpp",
                "src/sync_replica_folder_process.hpp",
                "src/sync_replica_folder_process.cpp",
                "src/sync_replica_peer_service_singleton.hpp",
                "src/sync_replica_peer_service_singleton.cpp",
                "src/sync_replica_sqlite_owner.cpp",
                "tools/test_anonsync_database_recovery.py",
                "tools/test_anonsync_service_configuration_status.py",
                "tools/audit_anonsync_replica_database_open_policy.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0981_package_policy_binds_commands_database_seams_singleton_oracles_and_records",
        "release verification requires every implementation, process oracle, source audit, design record, and package-policy surface changed by rev0981",
    )

    require(
        '"format": "anonsync-replica-database-backup-audit-v1"'
        in database_backup_audit
        and "SyncReplicaDatabaseBackupOwner" in database_backup_header
        and "SyncReplicaDatabaseBackupCutpoint" in database_backup_header
        and "SealedSqliteSnapshot::capture_database" in database_backup_source
        and "publish_exact_copy_atomically_create_new_or_throw"
            in database_backup_source
        and "inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw"
            in database_artifact_internal
        and "state_in_read_only_detached_image_or_throw"
            in deployment_binding_header
        and "SQLITE_READONLY" in deployment_binding_source
        and 'sqlite3_db_readonly(database, "main") == 0'
            in sqlite_snapshot_seal_test,
        "rev0982_backup_owner_uses_bounded_create_new_and_behavioral_detached_reproof",
        "the shipping backup owner composes the retained copy, publication, binding, and complete-schema authorities without trusting the in-memory db_readonly oracle",
    )

    require(
        "database-backup-create" in database_recovery_runtime
        and "database-backup-inspect" in database_recovery_runtime
        and "detached backup inspection without source database"
            in database_recovery_runtime
        and "duplicate immutable backup create" in database_recovery_runtime
        and "backup artifact is not owner-only mode 0600"
            in database_recovery_runtime
        and "source recovery advance changed detached backup bytes"
            in database_recovery_runtime
        and "anonsync_sync_replica_database_backup_source_audit" in cmake,
        "rev0982_product_oracle_covers_detached_artifact_and_source_immutability",
        "the normal registry exercises bad paths, exact creation, source-absent inspection, damage rejection, and old-artifact stability across recovery advance",
    )

    require(
        all(
            token in normalized_prose(offline_database_backup_design)
            for token in (
                "Operator surface",
                "Creation authority order",
                "Boundedness and memory refactor",
                "Detached read-only SQLite correction",
                "What this does not prove",
                "Next safe edge",
            )
        )
        and all(
            token in normalized_prose(rev0982_notes)
            for token in (
                "Offline backup artifact",
                "One canonical artifact",
                "Detached inspector",
                "Audit/refactor: typed rollback authority",
                "Adjacent service-lifecycle correction",
                "Boundary",
            )
        )
        and "## Rev0982: canonical replica-database backup and detached reproof"
            in readme,
        "rev0982_records_keep_replica_database_backup_distinct_from_share_restore",
        "audit, notes, and README agree that this is one bounded database artifact, not payload backup, restore, or external anti-rollback authority",
    )

    require(
        ('options.require_only({"manifest", "snapshot"});' in sync_cli
         or 'options.require_only({"manifest", "snapshot", "role"});' in sync_cli)
        and 'options.one("manifest")' in sync_cli
        and 'options.one("snapshot")' in sync_cli
        and "database-backup-inspect --manifest ... --snapshot ..." in readme
        and "database-backup-inspect --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE"
            in rev0982_notes
        and "[--manifest" not in rev0982_notes
        and "An optional `--manifest`" not in readme,
        "rev0982_detached_inspection_remains_manifest_bound",
        "detached source independence cannot be documented as unauthenticated inspection without the deployment manifest",
    )

    require(
        "enum class LocalSocketCompletionPathPolicy" in local_status
        and "AllowExactAbsenceAfterResponse" in local_status
        and local_status.count(
            "LocalSocketCompletionPathPolicy::AllowExactAbsenceAfterResponse"
        ) == 1
        and "request_sync_local_status_stop_or_throw" in local_status
        and "if (error == ENOENT) return;" in local_status
        and local_status.count(
            "LocalSocketCompletionPathPolicy::RequireSameIdentity"
        ) >= 5,
        "rev0982_stop_completion_allows_only_exact_post_response_absence",
        "a valid completed drain may outlive its socket pathname without weakening the final identity rule for any other local command",
    )

    require(
        "with_raw_server_unlinked_before_response_or_throw"
            in local_status_runtime
        and "completed stop must survive exact post-response socket disappearance"
            in local_status_runtime
        and "socket disappearance must not bypass exact stop-response validation"
            in local_status_runtime
        and "non-stop requests must retain final socket-path identity"
            in local_status_runtime,
        "rev0982_stop_disappearance_regression_has_positive_and_negative_controls",
        "the runtime oracle distinguishes successful drain completion from malformed response and non-stop pathname loss",
    )

    require(
        rev0982_verifier_block.count(
            "if revision_number is not None and revision_number >= 982:"
        ) == 1
        and all(
            token in rev0982_verifier_block
            for token in (
                "OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md",
                "REVISION_NOTES_rev0982.md",
                "src/sync_replica_database_backup.hpp",
                "src/sync_replica_database_backup.cpp",
                "src/sync_replica_deployment_binding.hpp",
                "src/sync_replica_deployment_binding.cpp",
                "src/sync_replica_sqlite_owner.hpp",
                "src/sync_replica_sqlite_owner.cpp",
                "tests/persistence/sqlite_snapshot_seal_tests.cpp",
                "tests/sync_replica_deployment_binding_test.cpp",
                "tools/test_anonsync_database_recovery.py",
                "tools/audit_anonsync_replica_deployment_binding.py",
                "tools/audit_sync_replica_database_backup.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0982_package_policy_binds_backup_owner_detached_gate_oracle_and_records",
        "release verification requires every implementation, test, audit, and documentation surface that defines rev0982",
    )

    require(
        "class SyncReplicaDatabaseReplacementOwner final"
            in database_replacement_header
        and "replace_or_resume_or_throw" in database_replacement_header
        and "replace_or_resume_or_throw" not in database_backup_header
        and "sync_replica_database_replacement_receipt_internal.hpp"
            in database_replacement_source
        and "sync_replica_database_artifact_internal.hpp"
            in database_replacement_receipt_source
        and "sqlite3_backup_init" not in database_replacement_source
        and "sqlite3_backup_step" not in database_replacement_source
        and "replace_sqlite_live_database_bounded_or_throw"
            in database_replacement_source,
        "rev0984_replacement_is_separate_and_reuses_shared_receipt_and_copy_owners",
        "immutable backup creation remains non-destructive while resume composes reviewed hashing, publication, and SQLite-copy protocols",
    )

    require(
        ordered(
            database_replacement_source,
            "read_replacement_receipt_if_present_or_throw",
            "rollback output preflight",
            "bounded candidate capture",
            "candidate validation",
            "require_representable_recovery_successor_or_throw",
            "capture_displaced_database_or_throw",
            "publish_replacement_receipt_create_new_or_throw",
            "immutable rollback artifact publication",
            "pre-database-effect receipt reproof",
            "active replacement classification",
            "replace_sqlite_live_database_bounded_or_throw",
            "advance_database_recovery_epoch_or_throw",
            "final forensic deployment reproof before artifacts",
            "final candidate pathname reproof",
            "final rollback pathname reproof",
            "final immutable receipt reproof",
            "final forensic deployment reproof after artifacts",
        ),
        "rev0984_replacement_orders_receipt_rollback_classifier_effects_and_reopen",
        "the immutable receipt precedes effects while exact active database state alone classifies restart progress",
    )

    require(
        "sqlite_artifact_families_overlap" in database_artifact_internal
        and "require_disjoint_artifact_families_or_throw"
            in database_replacement_source
        and "preflight_artifact_output_family_create_new_or_throw"
            in database_backup_source
        and "preflight_artifact_output_family_create_new_or_throw"
            in database_replacement_source
        and "backup create with preexisting output sidecar"
            in database_recovery_runtime
        and "replacement with overlapping candidate and rollback families"
            in database_recovery_runtime
        and "replacement with preexisting rollback sidecar"
            in database_recovery_runtime
        and "for (const fs::path& artifact_member : artifact_family)"
            in database_artifact_internal
        and "path_is_same_or_descendant(artifact_member, *root)"
            in database_artifact_internal
        and "artifact family sidecar colliding with payload root"
            in database_recovery_runtime,
        "rev0983_complete_artifact_families_are_disjoint_and_preflighted",
        "main names, WAL/SHM/journal names, and deterministic sidecar conflicts are denied before expensive copy or partial rollback publication",
    )

    terminal_branch = sqlite_live_backup_source.find(
        "if (step_rc == SQLITE_DONE)"
    )
    error_branch = sqlite_live_backup_source.find(
        "if (step_rc != SQLITE_OK)", terminal_branch
    )
    observer_branch = sqlite_live_backup_source.find(
        "observer(observation, observer_context)", error_branch
    )
    require(
        min(terminal_branch, error_branch, observer_branch) >= 0
        and terminal_branch < error_branch < observer_branch
        and "throwable observer after that irreversible cutpoint"
            in sqlite_live_backup_source
        and "terminal SQLITE_DONE step became a throwable observer cutpoint"
            in sqlite_live_backup_runtime
        and "nonterminal SQLITE_OK" in sqlite_live_backup_header,
        "rev0983_terminal_sqlite_commit_is_not_a_throwable_observer_cutpoint",
        "deterministic hooks remain between page effects and cannot report failure after the named destination has committed",
    )

    require(
        "database-recovery-replace" in sync_cli
        and "anonsync.local-database-recovery-replacement.response.v3"
            in sync_cli
        and "RECEIPT_ACTION_DOMAIN" in database_recovery_runtime
        and "completed database replacement replay"
            in database_recovery_runtime
        and "candidate-installed replacement resume"
            in database_recovery_runtime
        and "receipt-only database replacement resume"
            in database_recovery_runtime
        and "unknown replacement continuity"
            in database_recovery_runtime
        and "missing rollback after completed replacement"
            in database_recovery_runtime
        and "changed candidate artifact pathname"
            in database_recovery_runtime
        and "changed rollback artifact pathname"
            in database_recovery_runtime
        and "final candidate pathname replacement race"
            in database_recovery_runtime
        and "SIGSTOP" in database_recovery_runtime
        and "candidate artifact changed" in database_recovery_runtime
        and "final candidate pathname reproof resume"
            in database_recovery_runtime
        and "replacement_receipt_effect_authority" in sync_cli
        and "final_candidate_artifact_path_reproved" in sync_cli
        and "final_rollback_artifact_path_reproved" in sync_cli
        and "noncooperating_same_uid_artifact_replacement_excluded" in sync_cli
        and "payload_store_replacement_performed" in sync_cli,
        "rev0984_process_oracle_proves_receipt_integrity_and_exact_crash_resume",
        "the shipping process path independently recomputes receipt digests and exercises every admitted and denied restart state",
    )

    require(
        all(
            token in normalized_prose(immutable_database_replacement_receipt_design)
            for token in (
                "One immutable receipt, not a mutable stage journal",
                "Exact restart classifier",
                "Effect order and reproof",
                "Executable crash-cutpoint proof",
                "not a signature",
            )
        )
        and all(
            token in normalized_prose(rev0984_notes)
            for token in (
                "C++ product move", "Audit/refactor", "Explicit boundaries",
                "536/536", "262/262",
                "AnonSync-rev0984-2026.08.03.12.22-"
                "receiptresume-pathreproof-successorfence-grandidierite.zip",
            )
        )
        and "## Rev0984: immutable receipt and exact database-replacement resume"
            in readme,
        "rev0984_records_immutable_receipt_classifier_and_nonclaim_boundaries",
        "design, notes, and README distinguish restart evidence from effect authority and complete-share restore",
    )

    require(
        "anonsync_sync_replica_database_replacement_source_audit" in cmake
        and '"format": "anonsync-replica-database-replacement-audit-v3"'
            in database_replacement_audit
        and "lexical-hygiene-not-semantic-proof"
            in database_replacement_audit
        and "private_capture_and_named_replacement_share_one_copy_loop"
            in sqlite_live_backup_audit,
        "rev0984_source_audits_are_registered_and_disclaim_semantic_authority",
        "the normal registry binds implementation shape without substituting lexical checks for runtime or package proof",
    )

    require(
        rev0983_verifier_block.count(
            "if revision_number is not None and revision_number >= 983:"
        ) == 1
        and all(
            token in rev0983_verifier_block
            for token in (
                "OFFLINE_REPLICA_DATABASE_REPLACEMENT_AUDIT_rev0983.md",
                "REVISION_NOTES_rev0983.md",
                "src/persistence/sqlite_live_backup.hpp",
                "src/persistence/sqlite_live_backup.cpp",
                "src/sync_replica_database_artifact_internal.hpp",
                "src/sync_replica_database_replacement.hpp",
                "src/sync_replica_database_replacement.cpp",
                "tests/persistence/sqlite_live_backup_tests.cpp",
                "tools/test_anonsync_database_recovery.py",
                "tools/audit_sqlite_live_backup.py",
                "tools/audit_sync_replica_database_replacement.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0983_package_policy_binds_replacement_copy_oracle_audits_and_records",
        "a sealed archive cannot omit any authority, regression, documentation, or package-policy surface defining the replacement ceremony",
    )

    require(
        rev0984_verifier_block.count(
            "if revision_number is not None and revision_number >= 984:"
        ) == 1
        and all(
            token in rev0984_verifier_block
            for token in (
                "IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md",
                "REVISION_NOTES_rev0984.md",
                "src/sync_replica_database_artifact_internal.hpp",
                "src/sync_replica_database_replacement.hpp",
                "src/sync_replica_database_replacement.cpp",
                "src/sync_replica_database_replacement_receipt_internal.hpp",
                "src/sync_replica_database_replacement_receipt.cpp",
                "tools/test_anonsync_database_recovery.py",
                "tools/audit_sync_replica_database_replacement.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0984_package_policy_binds_receipt_resume_oracle_audits_and_records",
        "a sealed archive cannot omit any authority, regression, documentation, or package-policy surface defining crash resume",
    )

    require(
        "SyncReplicaRoleDatabaseBackupCutpoint" in database_backup_header
        and "create_role_artifact_or_throw" in database_backup_header
        and "inspect_role_artifact_or_throw" in database_backup_header
        and all(
            token in database_backup_source
            for token in (
                "SyncReplicaSqliteDeploymentRole::Replica",
                "SyncReplicaSqliteDeploymentRole::FileEffect",
                "SyncReplicaSqliteDeploymentRole::TlsMembership",
                "SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor",
                "SyncReplicaSqliteDeploymentRole::FolderCatalog",
            )
        )
        and "legacy replica artifact creation" in database_backup_source,
        "rev0985_backup_owner_extends_one_immutable_artifact_path_to_five_roles",
        "the role extension composes the released owner and retains v1 replica compatibility",
    )

    require(
        "without_root_access_or_throw" in file_effect_owner_header
        and "32768U" in file_effect_owner_source
        and "without_root_access_or_throw" in folder_scan_h
        and "16384U" in folder_scan
        and "ForensicReadOnlyDetached = 4U" in tls_policy_profile_header
        and "detached_image" in tls_policy_profile_source
        and "snapshot_in_detached_read_only_image_or_throw"
            in tls_membership_owner_header
        and "snapshot_in_detached_read_only_image_or_throw"
            in tls_anchor_owner_header,
        "rev0985_role_observers_are_root_cold_bounded_and_detached_profiled",
        "offline artifact inspection validates durable identity without opening synchronized roots or weakening named SQLite readers",
    )

    require(
        'options.require_only({"manifest", "snapshot", "role"});' in sync_cli
        and "anonsync.local-database-backup-create.response.v1" in sync_cli
        and "anonsync.local-database-backup-create.response.v2" in sync_cli
        and "anonsync.local-database-backup-inspection.response.v1" in sync_cli
        and "anonsync.local-database-backup-inspection.response.v2" in sync_cli
        and "single_role_database_image" in sync_cli
        and "cross_database_atomicity" in sync_cli
        and "complete_share_backup" in sync_cli
        and "restore_supported" in sync_cli
        and "inspection_only" in sync_cli,
        "rev0985_cli_preserves_v1_and_denies_complete_share_authority_in_v2",
        "only an explicit role changes the response schema and only replica claims existing restore compatibility",
    )

    require(
        all(
            token in role_backup_runtime
            for token in (
                "invalid database role",
                "explicit replica artifact legacy inspection",
                "wrong role artifact inspection",
                "hide_path(payload_root",
                "hide_path(files_root",
                "hide_family(source",
                "detached inspection recreated",
                "mode 0600",
                "artifact left sidecar",
                "anonsync role-bound database backup",
            )
        ),
        "rev0985_process_oracle_covers_five_roles_absent_authorities_and_role_confusion",
        "the shipping process proof exercises root-cold creation and source-absent detached inspection",
    )

    require(
        all(
            token in normalized_prose(role_bound_database_backup_design)
            for token in (
                "Five role-bound SQLite artifacts",
                "Consistency boundary",
                "Detached read-only correction",
                "Root-cold file-effect and folder-catalog inspection",
                "What remains missing",
                "Complete-share backup",
            )
        )
        and all(
            token in normalized_prose(rev0985_notes)
            for token in (
                "Role-bound database backup",
                "Backward compatibility",
                "Audit/refactor",
                "Boundary",
                "Validation",
            )
        )
        and "## Rev0985: role-bound offline database artifacts" in readme,
        "rev0985_records_role_consistency_and_complete_share_nonclaim_boundaries",
        "design, notes, and README distinguish component artifacts from a backup set",
    )

    require(
        "anonsync_sync_database_role_backup_process_test" in cmake
        and "anonsync_sync_replica_database_role_backup_source_audit" in cmake
        and "lexical-hygiene-not-semantic-proof" in role_backup_audit
        and "Runtime, sanitizer" in role_backup_audit,
        "rev0985_runtime_and_source_audits_are_registered_and_scoped",
        "lexical checks remain subordinate to shipping execution and release reconstruction",
    )

    require(
        rev0985_verifier_block.count(
            "if revision_number is not None and revision_number >= 985:"
        ) == 1
        and all(
            token in rev0985_verifier_block
            for token in (
                "ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md",
                "REVISION_NOTES_rev0985.md",
                "src/sync_replica_database_backup.hpp",
                "src/sync_replica_database_backup.cpp",
                "src/sync_replica_file_effect_sqlite_owner.hpp",
                "src/sync_replica_folder_scan_owner.hpp",
                "src/sync_replica_tls_policy_sqlite_profile.hpp",
                "src/sync_replica_tls_membership_sqlite_owner.hpp",
                "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp",
                "tools/test_anonsync_database_role_backup.py",
                "tools/audit_sync_replica_database_role_backup.py",
                "tools/audit_sync_file_payload_store.py",
                "tools/verify_release_package.py",
            )
        ),
        "rev0985_package_policy_binds_role_owners_oracle_audit_and_records",
        "a sealed archive cannot omit a role-specific schema owner or the proof that composes it",
    )

    require(
        "kSyncReplicaSelectiveSyncMaximumRules = 1024U"
            in selective_policy_header
        and "48ULL * 1024ULL" in selective_policy_header
        and "sync_replica_selective_sync_policy_materializes_new_paths"
            in selective_policy_header,
        "rev0987_selection_policy_is_bounded_and_expansion_aware",
        "the policy remains prefix-bounded rather than proportional to namespace cardinality",
    )

    require(
        "path_is_less_than_descendant_prefix" in selective_policy_source
        and "virtual key `directory/`" in selective_policy_source
        and "a-archive" in selective_policy_runtime
        and "a/keep" in selective_policy_runtime,
        "rev0987_allocation_free_pruning_preserves_slash_lexical_order",
        "an unrelated sibling cannot hide a deeper materialize rule",
    )

    require(
        "RemoteApplyCandidateKind::DematerializeMetadataOnlyFile"
            in folder_scan
        and "retained_private_payload" in folder_scan
        and "BlockedPayloadUnavailable" in folder_scan
        and "selection_rehydration_fence_active" in folder_scan,
        "rev0987_dematerialization_retains_only_copy_and_rehydrates_successor",
        "metadata-only rooted removal remains catalog, causal, payload, policy, and descriptor bound",
    )

    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_h
        and "metadata_only_file_operation_ids"
            in reconciliation_protocol_cpp
        and "metadata_only_file_operations" in reconciliation_service,
        "rev0987_wire_protocol_explicitly_marks_metadata_only_operations",
        "causal metadata cannot be confused with a failed payload transfer",
    )

    require(
        "selective-sync-status" in sync_cli
        and "selective-sync-set" in sync_cli
        and "pure exclusion opened a durable selective-sync absence fence"
            in folder_cli_process_runtime,
        "rev0987_shipping_policy_control_and_narrowing_oracle_are_present",
        "configured policy ownership and expansion-only fencing are process tested",
    )

    require(
        "lexical-hygiene-not-semantic-proof" in selective_sync_audit
        and "not semantic" in selective_sync_audit
        and "target-scale" in selective_sync_design
        and "not total AnonSync storage" in selective_sync_design,
        "rev0987_audit_and_docs_bound_nonclaims",
        "source shape is not confused with scale qualification, eviction, or semantic proof",
    )

    require(
        all(token in verifier for token in (
            "BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md",
            "REVISION_NOTES_rev0987.md",
            "src/sync_replica_selective_sync_policy.hpp",
            "tests/sync_replica_selective_sync_policy_test.cpp",
            "tools/audit_sync_replica_selective_sync.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        )),
        "rev0987_package_policy_binds_selective_owners_oracles_and_audits",
        "a sealed archive cannot omit the bounded policy or its rooted effect proof",
    )

    require(
        "struct FolderCatalogPathCutpoint final" in folder_scan
        and "load_folder_catalog_path_cutpoint_or_throw(" in folder_scan
        and "WHERE canonical_path=?;" in folder_scan
        and "SyncSqliteTransactionMode::Deferred" in folder_scan
        and "load_modern_catalog_entry_row_or_throw(" in folder_scan,
        "rev0988_catalog_effect_reproof_is_one_path_and_one_snapshot",
        "metadata-only effects re-prove catalog identity, policy metadata, and one exact path without projecting the complete catalog",
    )

    require(
        "remote_targeted_catalog_path_cutpoint_count" in folder_scan_h
        and "remote_targeted_catalog_path_cutpoint_count" in folder_scan
        and "remote_targeted_catalog_path_cutpoints" in folder_cli
        and "remote_targeted_catalog_path_cutpoints" in sync_cli
        and "test_selective_sync_dematerialization_reproof_is_path_local"
            in folder_scan_runtime
        and "3U * kPathCount" in folder_scan_runtime
        and "trace.complete_projection_read_count <= 4U" in folder_scan_runtime,
        "rev0988_runtime_oracle_binds_three_path_cutpoints_and_pass_bounded_projections",
        "an eight-effect batch proves targeted SQL cardinality while preserving pass-level complete observations",
    )

    require(
        "12,288 complete catalog projections" in targeted_catalog_design
        and "1,000,000 paths" in targeted_catalog_design
        and "O(history) reference owner" in targeted_catalog_design
        and "targeted" in targeted_catalog_design
        and "replica path/operation cutpoint" in targeted_catalog_design
        and "lexical-hygiene-not-semantic-proof" in targeted_catalog_audit
        and "not semantic proof" in targeted_catalog_audit,
        "rev0988_audit_quantifies_removed_multiplier_and_remaining_history_seam",
        "the correction is neither mislabeled as global catalog proof nor as completed multi-terabyte qualification",
    )

    require(
        all(token in verifier for token in (
            "TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md",
            "REVISION_NOTES_rev0988.md",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_replica_targeted_catalog_cutpoint.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        )),
        "rev0988_package_policy_binds_targeted_cutpoint_owner_oracle_and_audits",
        "a sealed archive cannot omit the optimized authority boundary or its executable and lexical proofs",
    )

    require(
        "struct SyncReplicaSqliteTargetedPathCutpoint final" in sqlite_owner_h
        and "targeted_path_cutpoint_or_throw(" in sqlite_owner_h
        and "requested_retained_operation_is_sole_visible" in sqlite_owner_h
        and "distinct_retained_operation" in sqlite_owner_h,
        "rev0989_replica_owner_exposes_bounded_path_and_operation_cutpoint",
        "the exact owner result carries at most one sole-visible and one distinct retained operation",
    )

    require(
        "FROM main.sync_replica_visible WHERE canonical_path=?" in sqlite_owner
        and "ORDER BY visible_ordinal LIMIT 2" in sqlite_owner
        and "FROM main.sync_replica_operations WHERE operation_id=?" in sqlite_owner
        and "load_stored_operation_row_or_throw(" in sqlite_owner
        and "SyncSqliteTransactionMode::Deferred" in sqlite_owner,
        "rev0989_targeted_replica_query_is_primary_key_bounded_and_transaction_pinned",
        "metadata, at most two visible rows, and exact operation rows share one deferred snapshot",
    )

    targeted_replica_body = function_body(
        sqlite_owner,
        "SyncReplicaSqliteOwner::targeted_path_cutpoint_or_throw("
    )
    targeted_replica_result = function_body(
        sqlite_owner_h,
        "struct SyncReplicaSqliteTargetedPathCutpoint final"
    )
    current_owner_meta_body = function_body(
        sqlite_owner,
        "read_current_owner_meta_or_throw("
    )
    require(
        targeted_replica_body.count("read_current_owner_meta_or_throw(") == 1
        and current_owner_meta_body.count("verify_schema_or_throw(") == 1
        and current_owner_meta_body.count("require_foreign_keys_or_throw(") == 1
        and "state_generation" not in targeted_replica_result
        and "policy_generation" not in targeted_replica_result
        and "visible_state_digest" not in targeted_replica_result
        and "cutpoint_digest" not in targeted_replica_result,
        "rev0989_targeted_replica_cutpoint_reproves_fixed_authority_without_global_overclaim",
        "each path cutpoint reaches the centralized exact schema and foreign-key reproof but exports only rows it independently proves",
    )

    require(
        "remote_targeted_replica_path_cutpoint_count" in folder_scan_h
        and "remote_targeted_replica_path_cutpoint_count" in folder_scan
        and "remote_targeted_replica_path_cutpoints" in folder_cli
        and "remote_targeted_replica_path_cutpoints" in sync_cli
        and "test_selective_sync_dematerialization_reproof_is_path_local" in folder_scan_runtime
        and "3U * kPathCount" in folder_scan_runtime,
        "rev0989_dematerialization_and_shipping_surfaces_bind_three_targeted_replica_cutpoints",
        "the eight-file runtime oracle and both JSON surfaces expose exact path-local causal reproof",
    )

    require(
        "struct TargetedReplicaReadTrace final" in sqlite_owner_runtime
        and "test_targeted_path_cutpoint_is_exact_and_path_bounded" in sqlite_owner_runtime
        and "test_targeted_path_cutpoint_is_exact_and_history_bounded" in sqlite_owner_runtime
        and "complete_operation_projection_read_count == 0U" in sqlite_owner_runtime
        and "schema_catalog_read_count == 1U" in sqlite_owner_runtime
        and "foreign_key_pragma_count == 1U" in sqlite_owner_runtime,
        "rev0989_direct_sqlite_oracle_proves_exact_history_independent_query_shape",
        "sole, predecessor, conflict, absent, and unrelated-history cases reject full projections while retaining fixed schema proof",
    )

    require(
        "12,288 complete replica snapshots" in targeted_replica_design
        and "122,880,000 retained operation-row decodes" in targeted_replica_design
        and "at most two operation envelopes" in targeted_replica_design
        and "Complete replica snapshots remain" in targeted_replica_design
        and "lexical-hygiene-not-semantic-proof" in targeted_replica_audit
        and "not\nsemantic proof" in targeted_replica_audit,
        "rev0989_audit_quantifies_removed_history_multiplier_and_bounded_nonclaim",
        "the correction names production frontiers, transient envelope bounds, and remaining global authority",
    )

    require(
        all(token in verifier for token in (
            "TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md",
            "REVISION_NOTES_rev0989.md",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_replica_targeted_path_cutpoint.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        )),
        "rev0989_package_policy_binds_targeted_replica_owner_oracles_and_audits",
        "a sealed archive cannot omit the path-local causal boundary or its executable and lexical proof",
    )

    normalized_targeted_local_design = " ".join(targeted_local_design.split())
    normalized_rev0991_notes = " ".join(rev0991_notes.split())

    prepare_local_body = function_body(
        sqlite_owner,
        "SyncReplicaSqliteOwner::prepare_local_file_from_observed_heads_or_throw(",
    )
    commit_local_body = function_body(
        sqlite_owner,
        "SyncReplicaSqliteOwner::commit_prepared_local_file_or_throw(",
    )
    advance_local_meta_body = function_body(
        sqlite_owner,
        "advance_meta_for_targeted_local_publication_or_throw(",
    )

    require(
        "constexpr std::uint64_t kVisiblePathSchemaVersion = 8U" in sqlite_owner
        and "constexpr std::uint64_t kSchemaVersion = 9U" in sqlite_owner
        and "sync_replica_operation_paths" in sqlite_owner
        and "sync_replica_operation_paths_path" in sqlite_owner
        and "visible_path_count_be" in sqlite_owner
        and "operation_set_accumulator_digest()" in sqlite_owner
        and "evidence_set_accumulator_digest()" in sqlite_owner
        and "visible_state_accumulator_digest()" in sqlite_owner,
        "rev0991_schema_v8_binds_path_index_counts_and_incremental_witnesses",
        "targeted local publication has durable path lookup plus complete-rebuild acceptance witnesses",
    )

    require(
        "SyncSqliteTransactionMode::Deferred" in prepare_local_body
        and "read_targeted_path_history_cutpoint_or_throw" in prepare_local_body
        and "read_active_causal_head_operations_or_throw" in prepare_local_body
        and "load_state_or_throw" not in prepare_local_body
        and "SyncSqliteTransactionMode::Immediate" in commit_local_body
        and "read_targeted_path_history_cutpoint_or_throw" in commit_local_body
        and "load_state_or_throw" not in commit_local_body.split(
            "has_retained_child_reference_or_throw", 1
        )[0],
        "rev0991_prepare_and_normal_commit_are_targeted",
        "normal local publication depends on one path history and causal heads rather than complete retained history",
    )

    require(
        "make_sync_replica_local_operation_from_causal_heads_or_throw" in model_h
        and "active causal frontier" in model_h
        and "state_generation" not in function_body(
            sqlite_owner, "local_publication_cutpoint_base_digest_or_throw("
        )
        and "kUnrelatedHistory = 192U" in prepared_publication_runtime
        and "complete_operation_projection_rows == 0U"
            in prepared_publication_runtime
        and "complete_visible_projection_rows == 0U"
            in prepared_publication_runtime
        and "complete_operation_projection_statements == 0U"
            in prepared_publication_runtime,
        "rev0991_path_cutpoint_allows_unrelated_progress_without_global_projection",
        "the shared operation derivation remains causal while unrelated retained rows do not invalidate or expand the query",
    )

    require(
        "has_retained_child_reference_or_throw" in commit_local_body
        and "load_state_or_throw" in commit_local_body
        and "require_no_temporary_triggers_or_throw" in commit_local_body
        and "reverse-dependency" in prepared_publication_runtime
        and "TEMP triggers exist" in prepared_publication_runtime,
        "rev0991_rare_reverse_dependency_falls_back_and_temp_schema_fails_closed",
        "cross-path activation retains complete semantics and executable connection-local schema cannot inject effects",
    )

    require(
        "using Words = std::array<std::uint64_t, 4U>;" in accumulator
        and "sync_replica_digest_accumulator_add_or_throw" in accumulator_h
        and "sync_replica_digest_accumulator_subtract_or_throw" in accumulator_h
        and "unkeyed structural" in accumulator_h
        and "not authentication authority" in accumulator_h
        and "exact modulo-2^256 carry and borrow" in hash_graph_runtime
        and "sync_replica_digest_accumulator_add_or_throw"
            in advance_local_meta_body
        and "sync_replica_digest_accumulator_subtract_or_throw"
            in advance_local_meta_body,
        "rev0991_accumulator_is_fixed_width_tested_and_explicitly_non_authenticating",
        "counted additive witnesses remain structural acceleration accepted by complete reconstruction",
    )

    require(
        "test_quarantined_local_retry_fails_closed"
            in prepared_publication_runtime
        and "retained operation no longer carries active local minting authority"
            in sqlite_owner
        and "evidence_state != SyncReplicaEvidenceState::Active"
            in commit_local_body
        and "local_actor_compromised" in commit_local_body,
        "rev0991_idempotent_retry_rejects_quarantined_or_compromised_authority",
        "a same-dot fork cannot manufacture an AlreadyPublished success",
    )

    require(
        "81,920,000 prior operation-row decodes"
            in normalized_targeted_local_design
        and "O(history-of-that-path + active causal heads)"
            in normalized_targeted_local_design
        and "not constant memory" in normalized_targeted_local_design
        and "not a cryptographic set commitment"
            in normalized_targeted_local_design
        and "No rev0990 archive is part of release lineage."
            in normalized_targeted_local_design
        and "No rev0990 archive is part of release lineage"
            in normalized_rev0991_notes
        and "lexical-hygiene-not-semantic-proof" in targeted_local_audit
        and "not semantic proof" in targeted_local_audit,
        "rev0991_records_scale_boundary_nonclaims_and_exact_lineage_gap",
        "the source record quantifies the removed multiplier without inventing a missing parent or overclaiming the witness",
    )

    require(
        all(token in verifier for token in (
            "TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md",
            "REVISION_NOTES_rev0991.md",
            "src/sync_replica_digest_accumulator.hpp",
            "src/sync_replica_digest_accumulator.cpp",
            "src/sync_replica_model.hpp",
            "src/sync_replica_model.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tests/sync_replica_hash_graph_projection_test.cpp",
            "tests/sync_replica_prepared_publication_test.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tools/audit_sync_replica_targeted_local_publication.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        )),
        "rev0991_package_policy_binds_incremental_owner_oracles_and_audits",
        "a sealed archive cannot omit the schema owner, fixed-width witness, runtime regressions, or release records",
    )

    normalized_manifest_reference_design = " ".join(
        manifest_reference_design.split()
    )
    normalized_rev0992_notes = " ".join(rev0992_notes.split())

    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_protocol_header
        and "anonsync-sync-replica-reconciliation-request-v9"
            in reconciliation_protocol_source
        and "anonsync-sync-replica-reconciliation-response-v9"
            in reconciliation_protocol_source
        and "cached_delta_manifest_digest"
            in reconciliation_protocol_header,
        "rev0992_manifest_reference_authority_survives_generation_7",
        "the rev0992 digest-only continuation remains fail-closed under current generation-9 framing",
    )

    require(
        "CachedTargetContentDefinedManifest" in reconciliation_service_h
        and "CachedPredecessorContentDefinedManifest"
            in reconciliation_service_h
        and "std::vector<std::size_t> digest_order"
            in reconciliation_service_h
        and "ranged payload references a content-defined manifest absent from this receiver process"
            in reconciliation_service
        and "ranged payload bytes do not match the retained content-defined manifest reference"
            in reconciliation_service,
        "rev0992_receiver_cache_is_exact_bounded_and_fail_closed",
        "target and predecessor acceleration remain cohesive process-local records",
    )

    require(
        "content_defined_manifest_publications" in reconciliation_tls_header
        and "content_defined_manifest_references" in reconciliation_tls_header
        and "target_content_defined_manifest_publications"
            in reconciliation_tls_header
        and "target_content_defined_manifest_reuses"
            in reconciliation_tls_header
        and "delta_predecessor_index_builds" in reconciliation_tls_header
        and "delta_predecessor_index_reuses" in reconciliation_tls_header
        and "content_defined_manifest_publications" in reconciliation_tls_source
        and "content_defined_manifest_references" in reconciliation_tls_source,
        "rev0992_shipping_transport_preserves_manifest_and_index_metrics",
        "the optimization remains observable beyond focused service tests",
    )

    require(
        "maximum manifest reference did not remove the complete chunk vector"
            in reconciliation_protocol_runtime
        and "more than 256 GiB of repeated manifest bytes"
            in reconciliation_protocol_runtime
        and "309,237,350,400"
            in normalized_manifest_reference_design
        and "just under 288 GiB"
            in normalized_manifest_reference_design
        and "content-defined chunking" in normalized_rev0992_notes
        and "not a measured peak-RSS result"
            in normalized_manifest_reference_design,
        "rev0992_quantifies_removed_multiplier_without_overclaiming_delta_completion",
        "the release record binds the 4-TiB shape and keeps insertion resilience and RSS measurement open",
    )

    require(
        all(token in verifier for token in (
            "MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md",
            "REVISION_NOTES_rev0992.md",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_file_payload_store.py",
        ))
        and "anonsync-manifest-reference-source-audit-v1"
            in manifest_reference_audit
        and "lexical-hygiene-not-semantic-proof"
            in manifest_reference_audit,
        "rev0992_package_policy_binds_manifest_reference_implementation_and_proof",
        "a sealed archive cannot omit protocol, service, runtime tests, records, or focused audit",
    )

    normalized_targeted_source_access_design = " ".join(
        targeted_source_access_design.split()
    )
    normalized_targeted_source_access_design_lower = (
        normalized_targeted_source_access_design.lower()
    )
    normalized_rev0993_notes = " ".join(rev0993_notes.split())

    serve_session_region = reconciliation_service_header.split(
        "class SyncReplicaReconciliationServeSession final", 1
    )[1].split("enum class SyncReplicaReconciliationApplyDisposition", 1)[0]
    source_serve_region = reconciliation_service.split(
        "SyncReplicaReconciliationService::serve_request_or_throw", 1
    )[1].split(
        "SyncReplicaReconciliationService::apply_response_or_throw", 1
    )[0]

    require(
        "SyncReplicaFilePayloadStoreSnapshot" not in serve_session_region
        and "SyncReplicaFilePayloadStoreTargetedAccess" not in serve_session_region
        and "std::optional<SyncReplicaFilePayloadStoreTargetedAccess>"
            in source_serve_region
        and "request-scoped source payload access" in source_serve_region
        and "payload_store_.snapshot_or_throw" not in source_serve_region,
        "rev0993_source_serve_uses_request_scoped_exact_name_authority",
        "a source request no longer scans the whole payload namespace or retains a namespace-wide capability across network waits",
    )

    require(
        "same live serve session did not observe payload bytes that arrived without an evidence change"
            in reconciliation_runtime
        and "test_targeted_source_serving_does_not_claim_namespace_health"
            in reconciliation_runtime
        and "live.targeted_access_count == 0U"
            in reconciliation_runtime
        and "test_targeted_whole_payload_hashes_before_source_advertisement"
            in reconciliation_runtime
        and "complete range discovered payload corruption"
            in store,
        "rev0993_runtime_proves_late_availability_nonclaim_lifetime_and_integrity",
        "same-session late bytes become visible while targeted serving grants neither namespace-health nor post-response retention authority",
    )

    require(
        "stale negative" in normalized_targeted_source_access_design_lower
        and "retention planning" in normalized_targeted_source_access_design_lower
        and "not a measured target-scale rss claim"
            in normalized_targeted_source_access_design_lower
        and "content-defined or multilevel delta" in normalized_rev0993_notes
        and "Android" in normalized_rev0993_notes,
        "rev0993_records_product_gain_and_remaining_scale_nonclaims",
        "removing a namespace-scaled source multiplier is not presented as measured multi-terabyte or Android completion",
    )

    require(
        all(token in verifier for token in (
            "REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md",
            "REVISION_NOTES_rev0993.md",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_targeted_source_access.py",
            "tools/audit_sync_file_payload_store.py",
        ))
        and "anonsync-targeted-source-access-audit-v1"
            in targeted_source_access_audit
        and "lexical-hygiene-not-semantic-proof"
            in targeted_source_access_audit,
        "rev0993_package_policy_binds_targeted_source_authority_chain",
        "a sealed archive cannot omit the exact byte consumer, request owner, runtime regressions, release records, or focused audit",
    )

    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    if not bootstrap_path.is_file():
        bootstrap_path = root.parent / "BOOTSTRAPROSE.md"
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    require(
        "VALIDATION_PENDING_REV0965" not in rev0965_notes
        and "VALIDATION_PENDING_REV0965" not in readme
        and "ARCHIVE_PENDING_REV0965" not in bootstrap
        and "CODENAME_PENDING_REV0965" not in bootstrap
        and "VALIDATION_PENDING_REV0965" not in bootstrap,
        "rev0965_final_validation_and_visible_release_cutpoint_are_sealed",
        "the structural audit remains deliberately gated until final validation replaces every revision and visible-bootstrap release placeholder",
    )

    require(
        "VALIDATION_PENDING_REV0966" not in rev0966_notes
        and "VALIDATION_PENDING_REV0966" not in readme
        and "ARCHIVE_PENDING_REV0966" not in bootstrap
        and "CODENAME_PENDING_REV0966" not in bootstrap
        and "VALIDATION_PENDING_REV0966" not in bootstrap,
        "rev0966_final_validation_and_visible_release_cutpoint_are_sealed",
        "the new owner recovery surface cannot pass the structural audit until final validation and the visible bootstrap bind the exact release archive",
    )

    require(
        "VALIDATION_PENDING_REV0967" not in rev0967_notes
        and "VALIDATION_PENDING_REV0967" not in readme
        and "ARCHIVE_PENDING_REV0967" not in bootstrap
        and "CODENAME_PENDING_REV0967" not in bootstrap
        and "VALIDATION_PENDING_REV0967" not in bootstrap,
        "rev0967_final_validation_and_visible_release_cutpoint_are_sealed",
        "paging and projection changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0967 archive",
    )

    require(
        "VALIDATION_PENDING_REV0968" not in rev0968_notes
        and "VALIDATION_PENDING_REV0968" not in readme
        and "ARCHIVE_PENDING_REV0968" not in bootstrap
        and "CODENAME_PENDING_REV0968" not in bootstrap
        and "VALIDATION_PENDING_REV0968" not in bootstrap,
        "rev0968_final_validation_and_visible_release_cutpoint_are_sealed",
        "source-cutpoint changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0968 archive",
    )

    require(
        "VALIDATION_PENDING_REV0969" not in rev0969_notes
        and "VALIDATION_PENDING_REV0969" not in exact_current_restore_design
        and "VALIDATION_PENDING_REV0969" not in readme
        and "ARCHIVE_PENDING_REV0969" not in bootstrap
        and "CODENAME_PENDING_REV0969" not in bootstrap
        and "VALIDATION_PENDING_REV0969" not in bootstrap,
        "rev0969_final_validation_and_visible_release_cutpoint_are_sealed",
        "exact-current restore changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0969 archive",
    )

    require(
        "VALIDATION_PENDING_REV0970" not in rev0970_notes
        and "VALIDATION_PENDING_REV0970" not in metadata_history_design
        and "VALIDATION_PENDING_REV0970" not in readme
        and "ARCHIVE_PENDING_REV0970" not in bootstrap
        and "CODENAME_PENDING_REV0970" not in bootstrap
        and "VALIDATION_PENDING_REV0970" not in bootstrap,
        "rev0970_final_validation_and_visible_release_cutpoint_are_sealed",
        "metadata-only history changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0970 archive",
    )

    require(
        "VALIDATION_PENDING_REV0971" not in rev0971_notes
        and "VALIDATION_PENDING_REV0971" not in bounded_historical_status_design
        and "VALIDATION_PENDING_REV0971" not in readme
        and "ARCHIVE_PENDING_REV0971" not in bootstrap
        and "CODENAME_PENDING_REV0971" not in bootstrap
        and "VALIDATION_PENDING_REV0971" not in bootstrap,
        "rev0971_final_validation_and_visible_release_cutpoint_are_sealed",
        "bounded history-status changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0971 archive",
    )

    require(
        "VALIDATION_PENDING_REV0972" not in rev0972_notes
        and "VALIDATION_PENDING_REV0972" not in retained_reachability_frontier_design
        and "VALIDATION_PENDING_REV0972" not in readme
        and "ARCHIVE_PENDING_REV0972" not in bootstrap
        and "CODENAME_PENDING_REV0972" not in bootstrap
        and "VALIDATION_PENDING_REV0972" not in bootstrap,
        "rev0972_final_validation_and_visible_release_cutpoint_are_sealed",
        "retained-reachability and canonical-frontier changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0972 archive",
    )

    require(
        "VALIDATION_PENDING_REV0973" not in rev0973_notes
        and "VALIDATION_PENDING_REV0973" not in retention_pin_design
        and "VALIDATION_PENDING_REV0973" not in readme
        and "ARCHIVE_PENDING_REV0973" not in bootstrap
        and "CODENAME_PENDING_REV0973" not in bootstrap
        and "VALIDATION_PENDING_REV0973" not in bootstrap,
        "rev0973_final_validation_and_visible_release_cutpoint_are_sealed",
        "retention-pin authority and operator-surface changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final rev0973 archive",
    )

    require(
        "VALIDATION_PENDING_REV0974" not in rev0974_notes
        and "VALIDATION_PENDING_REV0974" not in retention_plan_design
        and "VALIDATION_PENDING_REV0974" not in readme
        and "ARCHIVE_PENDING_REV0974" not in bootstrap
        and "CODENAME_PENDING_REV0974" not in bootstrap
        and "VALIDATION_PENDING_REV0974" not in bootstrap,
        "rev0974_final_validation_and_visible_release_cutpoint_are_sealed",
        "the exact retention planner cannot pass the structural audit until final validation and the visible bootstrap bind the sealed rev0974 archive",
    )

    require(
        "VALIDATION_PENDING_REV0975" not in rev0975_notes
        and "VALIDATION_PENDING_REV0975" not in retention_mark_witness_design
        and "VALIDATION_PENDING_REV0975" not in readme
        and "ARCHIVE_PENDING_REV0975" not in bootstrap
        and "CODENAME_PENDING_REV0975" not in bootstrap
        and "VALIDATION_PENDING_REV0975" not in bootstrap,
        "rev0975_final_validation_and_visible_release_cutpoint_are_sealed",
        "the optimized retention projection and mark witness cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0975 archive",
    )

    require(
        "VALIDATION_PENDING_REV0976" not in rev0976_notes
        and "VALIDATION_PENDING_REV0976" not in transient_cutpoint_design
        and "VALIDATION_PENDING_REV0976" not in readme
        and "ARCHIVE_PENDING_REV0976" not in bootstrap
        and "CODENAME_PENDING_REV0976" not in bootstrap
        and "VALIDATION_PENDING_REV0976" not in bootstrap,
        "rev0976_final_validation_and_visible_release_cutpoint_are_sealed",
        "the exact transient-root cutpoint cannot pass the structural audit until final validation and the visible bootstrap bind the sealed rev0976 archive",
    )

    require(
        "VALIDATION_PENDING_REV0977" not in rev0977_notes
        and "VALIDATION_PENDING_REV0977" not in live_capability_design
        and "VALIDATION_PENDING_REV0977" not in payload_use_lease_design
        and "VALIDATION_PENDING_REV0977" not in readme
        and "ARCHIVE_PENDING_REV0977" not in bootstrap
        and "CODENAME_PENDING_REV0977" not in bootstrap
        and "VALIDATION_PENDING_REV0977" not in bootstrap,
        "rev0977_final_validation_and_visible_release_cutpoint_are_sealed",
        "the exact same-owner live-capability cutpoint and payload-use reader fence cannot pass the structural audit until final validation and the visible bootstrap bind the sealed rev0977 archive",
    )

    require(
        "VALIDATION_PENDING_REV0978" not in rev0978_notes
        and "VALIDATION_PENDING_REV0978" not in process_store_writer_fence_design
        and "VALIDATION_PENDING_REV0978" not in readme
        and "ARCHIVE_PENDING_REV0978" not in bootstrap
        and "CODENAME_PENDING_REV0978" not in bootstrap
        and "VALIDATION_PENDING_REV0978" not in bootstrap,
        "rev0978_final_validation_and_visible_release_cutpoint_are_sealed",
        "the process-store live-capability scope and writer-fenced retention observation cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0978 archive",
    )

    require(
        "VALIDATION_PENDING_REV0979" not in rev0979_notes
        and "VALIDATION_PENDING_REV0979" not in durable_retention_mark_design
        and "VALIDATION_PENDING_REV0979" not in readme
        and "ARCHIVE_PENDING_REV0979" not in bootstrap
        and "CODENAME_PENDING_REV0979" not in bootstrap
        and "VALIDATION_PENDING_REV0979" not in bootstrap,
        "rev0979_final_validation_and_visible_release_cutpoint_are_sealed",
        "the durable mark and policy cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0979 archive",
    )

    require(
        "VALIDATION_PENDING_REV0980" not in rev0980_notes
        and "VALIDATION_PENDING_REV0980" not in database_lineage_design
        and "VALIDATION_PENDING_REV0980" not in readme
        and "ARCHIVE_PENDING_REV0980" not in bootstrap
        and "CODENAME_PENDING_REV0980" not in bootstrap
        and "VALIDATION_PENDING_REV0980" not in bootstrap,
        "rev0980_final_validation_and_visible_release_cutpoint_are_sealed",
        "database lineage and retention-witness changes cannot pass the structural audit until final validation and the visible bootstrap bind the sealed rev0980 archive",
    )

    require(
        "VALIDATION_PENDING_REV0981" not in rev0981_notes
        and "VALIDATION_PENDING_REV0981" not in offline_database_recovery_design
        and "VALIDATION_PENDING_REV0981" not in readme
        and "ARCHIVE_PENDING_REV0981" not in bootstrap
        and "CODENAME_PENDING_REV0981" not in bootstrap
        and "VALIDATION_PENDING_REV0981" not in bootstrap,
        "rev0981_final_validation_and_visible_release_cutpoint_are_sealed",
        "offline database recovery and deployment-singleton changes cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0981 archive",
    )

    require(
        "VALIDATION_PENDING_REV0982" not in rev0982_notes
        and "VALIDATION_PENDING_REV0982" not in offline_database_backup_design
        and "VALIDATION_PENDING_REV0982" not in readme
        and "ARCHIVE_PENDING_REV0982" not in bootstrap
        and "CODENAME_PENDING_REV0982" not in bootstrap
        and "VALIDATION_PENDING_REV0982" not in bootstrap,
        "rev0982_final_validation_and_visible_release_cutpoint_are_sealed",
        "offline database backup and detached-image changes cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0982 archive",
    )

    require(
        "VALIDATION_PENDING_REV0983" not in rev0983_notes
        and "VALIDATION_PENDING_REV0983"
            not in offline_database_replacement_design
        and "VALIDATION_PENDING_REV0983" not in readme
        and "ARCHIVE_PENDING_REV0983" not in bootstrap
        and "CODENAME_PENDING_REV0983" not in bootstrap
        and "VALIDATION_PENDING_REV0983" not in bootstrap,
        "rev0983_final_validation_and_visible_release_cutpoint_are_sealed",
        "offline logical replacement cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0983 archive",
    )

    require(
        "VALIDATION_PENDING_REV0984" not in rev0984_notes
        and "ARCHIVE_PENDING_REV0984" not in rev0984_notes
        and "VALIDATION_PENDING_REV0984"
            not in immutable_database_replacement_receipt_design
        and "ARCHIVE_PENDING_REV0984"
            not in immutable_database_replacement_receipt_design
        and "VALIDATION_PENDING_REV0984" not in readme
        and "ARCHIVE_PENDING_REV0984" not in readme
        and "ARCHIVE_PENDING_REV0984" not in bootstrap
        and "CODENAME_PENDING_REV0984" not in bootstrap
        and "VALIDATION_PENDING_REV0984" not in bootstrap,
        "rev0984_final_validation_and_visible_release_cutpoint_are_sealed",
        "immutable receipt resume cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0984 archive",
    )

    require(
        "VALIDATION_PENDING_REV0985" not in rev0985_notes
        and "ARCHIVE_PENDING_REV0985" not in rev0985_notes
        and "VALIDATION_PENDING_REV0985" not in readme
        and "ARCHIVE_PENDING_REV0985" not in readme
        and "ARCHIVE_PENDING_REV0985" not in bootstrap
        and "CODENAME_PENDING_REV0985" not in bootstrap
        and "VALIDATION_PENDING_REV0985" not in bootstrap,
        "rev0985_final_validation_and_visible_release_cutpoint_are_sealed",
        "role-bound artifacts cannot pass the structural audit until exact validation and the visible bootstrap bind the sealed rev0985 archive",
    )

    require(
        "VALIDATION_PENDING_REV0987" not in rev0987_notes
        and "ARCHIVE_PENDING_REV0987" not in rev0987_notes
        and "VALIDATION_PENDING_REV0987" not in selective_sync_design
        and "ARCHIVE_PENDING_REV0987" not in selective_sync_design
        and "VALIDATION_PENDING_REV0987" not in readme
        and "ARCHIVE_PENDING_REV0987" not in readme
        and "ARCHIVE_PENDING_REV0987" not in bootstrap
        and "CODENAME_PENDING_REV0987" not in bootstrap
        and "VALIDATION_PENDING_REV0987" not in bootstrap,
        "rev0987_final_validation_and_visible_release_cutpoint_are_sealed",
        "selective-sync changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "VALIDATION_PENDING_REV0988" not in rev0988_notes
        and "ARCHIVE_PENDING_REV0988" not in rev0988_notes
        and "VALIDATION_PENDING_REV0988" not in targeted_catalog_design
        and "ARCHIVE_PENDING_REV0988" not in targeted_catalog_design
        and "VALIDATION_PENDING_REV0988" not in readme
        and "ARCHIVE_PENDING_REV0988" not in readme
        and "ARCHIVE_PENDING_REV0988" not in bootstrap
        and "CODENAME_PENDING_REV0988" not in bootstrap
        and "VALIDATION_PENDING_REV0988" not in bootstrap,
        "rev0988_final_validation_and_visible_release_cutpoint_are_sealed",
        "targeted catalog reproof cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "VALIDATION_PENDING_REV0989" not in rev0989_notes
        and "ARCHIVE_PENDING_REV0989" not in rev0989_notes
        and "VALIDATION_PENDING_REV0989" not in targeted_replica_design
        and "ARCHIVE_PENDING_REV0989" not in targeted_replica_design
        and "VALIDATION_PENDING_REV0989" not in readme
        and "ARCHIVE_PENDING_REV0989" not in readme
        and "ARCHIVE_PENDING_REV0989" not in bootstrap
        and "CODENAME_PENDING_REV0989" not in bootstrap
        and "VALIDATION_PENDING_REV0989" not in bootstrap,
        "rev0989_final_validation_and_visible_release_cutpoint_are_sealed",
        "targeted replica reproof cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "VALIDATION_PENDING_REV0991" not in rev0991_notes
        and "ARCHIVE_PENDING_REV0991" not in rev0991_notes
        and "VALIDATION_PENDING_REV0991" not in targeted_local_design
        and "ARCHIVE_PENDING_REV0991" not in targeted_local_design
        and "VALIDATION_PENDING_REV0991" not in readme
        and "ARCHIVE_PENDING_REV0991" not in readme
        and "ARCHIVE_PENDING_REV0991" not in bootstrap
        and "CODENAME_PENDING_REV0991" not in bootstrap
        and "VALIDATION_PENDING_REV0991" not in bootstrap,
        "rev0991_final_validation_and_visible_release_cutpoint_are_sealed",
        "targeted local publication cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "VALIDATION_PENDING_REV0992" not in rev0992_notes
        and "ARCHIVE_PENDING_REV0992" not in rev0992_notes
        and "VALIDATION_PENDING_REV0992" not in manifest_reference_design
        and "ARCHIVE_PENDING_REV0992" not in manifest_reference_design
        and "VALIDATION_PENDING_REV0992" not in readme
        and "ARCHIVE_PENDING_REV0992" not in readme
        and "ARCHIVE_PENDING_REV0992" not in bootstrap
        and "CODENAME_PENDING_REV0992" not in bootstrap
        and "VALIDATION_PENDING_REV0992" not in bootstrap,
        "rev0992_final_validation_and_visible_release_cutpoint_are_sealed",
        "manifest-reference and delta-index changes cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_protocol_header
        and "kSyncReplicaReconciliationMaximumContentDefinedChunks = 8192U"
            in reconciliation_protocol_header
        and "CachedTargetContentDefinedManifest"
            in reconciliation_service_h
        and "CachedPredecessorContentDefinedManifest"
            in reconciliation_service_h,
        "rev0994_content_defined_protocol_and_bounded_caches_are_present",
        "the shipping delta path uses generation-6 variable chunks with bounded target and predecessor acceleration",
    )

    require(
        "class SyncReplicaContentDefinedChunker"
            in content_defined_chunker_header
        and "pending_chunk_bytes_ >= parameters_.maximum_chunk_bytes"
            in content_defined_chunker_source
        and "forced maximum" in content_defined_chunker_runtime
        and "inserted fixture" in content_defined_chunker_runtime,
        "rev0994_chunker_has_forced_boundary_and_insertion_regressions",
        "the scalar boundary detector is bounded and its insertion-resynchronization shape is exercised",
    )

    require(
        "test_content_defined_delta_reuses_shifted_predecessor_chunks"
            in reconciliation_runtime
        and "candidate_chunk_begin" in reconciliation_service
        and "reused_payload_chunks" in reconciliation_service_h
        and "target_content_defined_manifest_publications"
            in reconciliation_tls_header,
        "rev0994_shifted_chunk_reuse_reaches_shipping_transport",
        "content-addressed predecessor chunks may be copied from changed offsets while counters survive through TLS",
    )

    require(
        "anonsync-content-defined-delta-source-audit-v1"
            in content_defined_delta_audit
        and "CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"
            in verifier
        and "REVISION_NOTES_rev0994.md" in verifier
        and "tools/audit_sync_replica_content_defined_delta.py" in verifier,
        "rev0994_release_policy_binds_delta_authority_chain",
        "the archive cannot omit the chunker, wire/runtime proof, design record, revision record, or focused audit",
    )

    require(
        "VALIDATION_PENDING_REV0993" not in rev0993_notes
        and "ARCHIVE_PENDING_REV0993" not in rev0993_notes
        and "CODENAME_PENDING_REV0993" not in rev0993_notes
        and "VALIDATION_PENDING_REV0993" not in targeted_source_access_design
        and "ARCHIVE_PENDING_REV0993" not in targeted_source_access_design
        and "CODENAME_PENDING_REV0993" not in targeted_source_access_design
        and "VALIDATION_PENDING_REV0993" not in readme
        and "ARCHIVE_PENDING_REV0993" not in readme
        and "ARCHIVE_PENDING_REV0993" not in bootstrap
        and "CODENAME_PENDING_REV0993" not in bootstrap
        and "VALIDATION_PENDING_REV0993" not in bootstrap,
        "rev0993_final_validation_and_visible_release_cutpoint_are_sealed",
        "request-scoped source authority cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "VALIDATION_PENDING_REV0994" not in rev0994_notes
        and "ARCHIVE_PENDING_REV0994" not in rev0994_notes
        and "CODENAME_PENDING_REV0994" not in rev0994_notes
        and "VALIDATION_PENDING_REV0994" not in content_defined_delta_design
        and "ARCHIVE_PENDING_REV0994" not in content_defined_delta_design
        and "CODENAME_PENDING_REV0994" not in content_defined_delta_design
        and "VALIDATION_PENDING_REV0994" not in readme
        and "ARCHIVE_PENDING_REV0994" not in readme
        and "ARCHIVE_PENDING_REV0994" not in bootstrap
        and "CODENAME_PENDING_REV0994" not in bootstrap
        and "VALIDATION_PENDING_REV0994" not in bootstrap,
        "rev0994_final_validation_and_visible_release_cutpoint_are_sealed",
        "content-defined shifted reuse cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "CachedSourceContentDefinedManifest" in reconciliation_service_h
        and "SyncReplicaReconciliationCompactManifest manifest"
            in reconciliation_service_h
        and "std::vector<std::uint64_t> chunk_offsets"
            not in delimited_body(
                reconciliation_service_h,
                "struct CachedSourceContentDefinedManifest final",
                "{", "}")
        and "source_manifest.manifest.chunk_index_for_offset_or_throw"
            in reconciliation_service
        and "content_defined_manifest_source_metadata_"
            not in reconciliation_service_h + reconciliation_service,
        "rev0995_source_manifest_and_index_have_one_bounded_lifetime",
        "the source retains one cohesive compact manifest/index projection rather than rebuilding or partially resetting parallel state",
    )

    require(
        "content_defined_chunk_index_builds" in reconciliation_service_h
        and "content_defined_chunk_index_reuses" in reconciliation_tls_header
        and "content_defined_chunk_index_lookups" in reconciliation_tls_source
        and "reconciliation_content_defined_chunk_index_builds" in replica_cli
        and "content_defined_chunk_index_builds() == 1U" in reconciliation_runtime
        and "content_defined_chunk_index_lookups == 1U" in tls_transport_runtime,
        "rev0995_source_index_accounting_reaches_shipping_transport",
        "source index builds and exact per-window lookups are visible through the authenticated TLS and CLI surfaces",
    )

    require(
        "8'589'934'592ULL" in reconciliation_protocol_runtime
        and "68'727'865'344ULL" in reconciliation_protocol_runtime
        and "64.0078125 GiB" in source_chunk_index_design
        and "bounded multi-range or byte-window frame" in source_chunk_index_design,
        "rev0995_maximum_shape_exposes_removed_and_remaining_multipliers",
        "the exact 4 TiB arithmetic binds the removed 64-GiB index churn and names one-range-per-turn framing as the next product edge",
    )

    require(
        "anonsync-source-chunk-index-source-audit-v1" in source_chunk_index_audit
        and "SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md" in verifier
        and "REVISION_NOTES_rev0995.md" in verifier
        and "tools/audit_sync_replica_source_chunk_index.py" in verifier,
        "rev0995_release_policy_binds_source_index_slice",
        "the release cannot omit the source cache, scale regression, operator counters, design record, revision notes, or focused audit",
    )

    require(
        "VALIDATION_PENDING_REV0995" not in rev0995_notes
        and "ARCHIVE_PENDING_REV0995" not in rev0995_notes
        and "CODENAME_PENDING_REV0995" not in rev0995_notes
        and "VALIDATION_PENDING_REV0995" not in source_chunk_index_design
        and "ARCHIVE_PENDING_REV0995" not in source_chunk_index_design
        and "CODENAME_PENDING_REV0995" not in source_chunk_index_design
        and "VALIDATION_PENDING_REV0995" not in readme
        and "ARCHIVE_PENDING_REV0995" not in readme
        and "ARCHIVE_PENDING_REV0995" not in bootstrap
        and "CODENAME_PENDING_REV0995" not in bootstrap
        and "VALIDATION_PENDING_REV0995" not in bootstrap,
        "rev0995_final_validation_and_visible_release_cutpoint_are_sealed",
        "source-index retention cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_protocol_header
        and "anonsync-sync-replica-reconciliation-request-frame-v9"
            in reconciliation_protocol_source
        and "anonsync-sync-replica-reconciliation-response-frame-v9"
            in reconciliation_protocol_source
        and "payload ranges are not exactly contiguous"
            in reconciliation_protocol_source
        and "complete content-defined manifest is not confined to the first range"
            in reconciliation_protocol_source,
        "rev0996_generation_7_binds_canonical_contiguous_range_groups",
        "current framing rejects gaps, overlap, manifest drift, and repeated complete manifests under a new digest domain",
    )

    require(
        "std::uint64_t range_count = 0U"
            in reconciliation_protocol_source
        and "std::vector<const SyncReplicaReconciliationPayload*> ranges"
            not in reconciliation_protocol_source
        and "struct PayloadRangeSpan final" in reconciliation_service
        and "std::map<std::string, PayloadRangeSpan>"
            in reconciliation_service
        and "std::vector<const SyncReplicaReconciliationPayload*>"
            not in reconciliation_service,
        "rev0996_group_projection_avoids_per_range_pointer_vectors",
        "protocol validation keeps scalar group state and receiver application indexes contiguous spans into the immutable response",
    )

    require(
        "selected_payloads.size() <" in reconciliation_service
        and "protocol_limits_.max_payloads_per_page"
            in reconciliation_service
        and "payload_bytes <" in reconciliation_service
        and "protocol_limits_.max_payload_bytes_per_page"
            in reconciliation_service
        and "available_page_bytes" in reconciliation_service
        and "chunk_end - next_offset" in reconciliation_service
        and reconciliation_service.count(
            "content-defined chunk-index lookup"
        ) == 1,
        "rev0996_source_window_is_record_byte_chunk_and_index_bounded",
        "one retained-index lookup seeds a linear range loop constrained by the existing page and chunk frontiers",
    )

    exhausted_budget = reconciliation_service.find(
        "payload_bytes >=\n                            protocol_limits_.max_payload_bytes_per_page"
    )
    ranged_open = reconciliation_service.find(
        "reconciliation ranged payload selection", exhausted_budget
    )
    require(
        exhausted_budget >= 0
        and ranged_open > exhausted_budget
        and "test_exhausted_byte_budget_stops_before_next_ranged_payload_open"
            in reconciliation_runtime
        and "zero-byte frontier opened, hashed, indexed, or published"
            in reconciliation_runtime
        and "ranged_payload_windows() == 0U" in reconciliation_runtime,
        "rev0996_exhausted_byte_frontier_precedes_ranged_payload_authority",
        "a page with no remaining bytes stops before the next large descriptor, manifest, index, or grouped-window publication",
    )

    require(
        all(
            token in reconciliation_service_h
            for token in (
                "ranged_payload_windows()",
                "ranged_payload_ranges()",
                "ranged_payload_bytes()",
            )
        )
        and all(
            token in reconciliation_tls_header + reconciliation_tls_source
            for token in (
                "ranged_payload_windows",
                "ranged_payload_ranges",
                "ranged_payload_bytes",
            )
        )
        and all(
            token in replica_cli
            for token in (
                "reconciliation_ranged_payload_windows",
                "reconciliation_ranged_payload_ranges",
                "reconciliation_ranged_payload_bytes",
            )
        )
        and '"reconciliation_ranged_payload_ranges": 16'
            in reconciliation_process_runtime,
        "rev0996_window_range_and_byte_accounting_reaches_shipping_process",
        "session counters propagate through authenticated TLS and shipping JSON to the real 16-range process oracle",
    )

    require(
        "wire_end <=" in reconciliation_service
        and "delta_wire_already_durable_ranges" in reconciliation_service
        and "effective_bytes.remove_prefix" in reconciliation_service
        and "Sha256DigestBuilder suffix_digest" in reconciliation_service
        and "payload range group skipped the receiver's exact durable prefix"
            in reconciliation_service
        and "Stop before admitting operation metadata"
            in reconciliation_service,
        "rev0996_receiver_preserves_prefix_restart_and_operation_after_bytes",
        "fully covered records collapse, partial overlap preserves only the advancing suffix, while gaps and operation-ahead admission remain fail closed",
    )

    require(
        "65'536U" in reconciliation_protocol_runtime
        and "983'040U" in reconciliation_protocol_runtime
        and "initial large-payload page was not one bounded two-range window"
            in reconciliation_runtime
        and "recover and skip the durable two-range prefix"
            in reconciliation_runtime
        and "first_options.max_round_trips = 1U"
            in tls_transport_runtime
        and "ranged_payload_ranges == 2U" in tls_transport_runtime
        and '"reconciliation_requests_received": 1'
            in reconciliation_process_runtime
        and "65,536" in multi_range_window_design
        and "not a measured 4 TiB transfer" in multi_range_window_design,
        "rev0996_runtime_and_design_bind_exact_turn_collapse_without_overclaim",
        "the 4 TiB frontier arithmetic and restartable two-range window are executable while throughput and RSS remain explicit nonclaims",
    )

    require(
        "anonsync-multi-range-payload-window-source-audit-v1"
            in multi_range_window_audit
        and "MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md"
            in verifier
        and "REVISION_NOTES_rev0996.md" in verifier
        and "tools/audit_sync_replica_multi_range_window.py" in verifier,
        "rev0996_release_policy_binds_multi_range_slice",
        "the release cannot omit generation-8 framing, runtime regressions, design record, revision notes, or focused audit",
    )

    require(
        "VALIDATION_PENDING_REV0996" not in rev0996_notes
        and "ARCHIVE_PENDING_REV0996" not in rev0996_notes
        and "CODENAME_PENDING_REV0996" not in rev0996_notes
        and "VALIDATION_PENDING_REV0996" not in multi_range_window_design
        and "ARCHIVE_PENDING_REV0996" not in multi_range_window_design
        and "CODENAME_PENDING_REV0996" not in multi_range_window_design
        and "VALIDATION_PENDING_REV0996" not in readme
        and "ARCHIVE_PENDING_REV0996" not in readme
        and "ARCHIVE_PENDING_REV0996" not in bootstrap
        and "CODENAME_PENDING_REV0996" not in bootstrap
        and "VALIDATION_PENDING_REV0996" not in bootstrap,
        "rev0996_final_validation_and_visible_release_cutpoint_are_sealed",
        "multi-range turn collapse cannot pass the structural audit until exact validation and the visible bootstrap bind the final archive",
    )

    require(
        "struct SyncReplicaReconciliationEncodedResponse final"
            in reconciliation_protocol_header
        and "struct SyncReplicaReconciliationBorrowedResponse final"
            in reconciliation_protocol_header
        and "std::vector<std::string_view> payload_bytes"
            in reconciliation_protocol_header
        and "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_protocol_header,
        "rev0997_wire_compatible_frame_and_borrowed_payload_types_are_explicit",
        "generation 8 remains authoritative while frame ownership and borrowed payload lifetime become named C++ types",
    )

    require(
        "response_body_metrics_or_throw" in reconciliation_protocol_source
        and "append_response_body_or_throw(frame"
            in reconciliation_protocol_source
        and "frame.reserve(u64_to_size_or_throw"
            in reconciliation_protocol_source
        and "derive_semantic_digest" in reconciliation_protocol_source
        and (
            "encode_sync_replica_reconciliation_response_for_request_or_throw"
                in reconciliation_service
            or "begin_sync_replica_reconciliation_response_frame_assembly_or_throw"
                in reconciliation_service
        )
        and "encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw"
            not in reconciliation_service,
        "rev0997_response_encoder_constructs_one_exact_frame_without_unread_digest",
        "shipping validates once, appends directly into one reserved frame, and does not derive the compatibility semantic digest",
    )

    require(
        "std::string response_digest" not in reconciliation_service_h
        and "response direct encoder drifted from its exact body size"
            in reconciliation_protocol_source
        and "response direct encoder drifted from its exact frame size"
            in reconciliation_protocol_source,
        "rev0997_dead_service_digest_is_removed_and_size_drift_fails_closed",
        "the service return no longer retains unread digest text and exact direct-frame projections are re-proved",
    )

    require(
        "prepare_sync_replica_tls_owned_record_write_or_throw" in tls_transport_h
        and "std::move(frame)" in tls_transport
        and "write_sync_replica_tls_owned_record_until_or_throw"
            in tls_record_exchange_h + tls_record_exchange
        and "frame_ownership_transferred" in tls_record_exchange
        and "std::move(inbound.response_frame)"
            in reconciliation_tls_source,
        "rev0997_final_frame_moves_into_bounded_tls_continuation",
        "the final source frame allocation transfers into bounded authenticated write continuation rather than being copied",
    )

    require(
        "std::vector<SyncReplicaOperation>().swap"
            in reconciliation_tls_source
        and "std::vector<SyncReplicaReconciliationPayload>().swap"
            in reconciliation_tls_source
        and reconciliation_tls_source.find(
            "std::vector<SyncReplicaReconciliationPayload>().swap"
        ) < reconciliation_tls_source.find(
            "write_sync_replica_tls_owned_record_until_or_throw"
        )
        and "response_frame_owned_handoffs" in reconciliation_tls_header
        and "reconciliation_response_frame_owned_handoffs" in replica_cli
        and "reconciliation_response_frame_owned_handoffs"
            in reconciliation_process_runtime
        and "reconciliation_response_frame_owned_handoffs"
            in sync_process_runtime,
        "rev0997_page_vectors_release_before_backpressure_and_handoff_is_observable",
        "compact disposition state survives while page-sized response objects release before network waiting",
    )

    require(
        "decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw"
            in reconciliation_service
        and "std::string_view wire_bytes" in reconciliation_service
        and "decoded.payload_bytes[payload_index]" in reconciliation_service
        and "std::string_view bytes" in store_h
        and "SyncReplicaFilePayloadStore::stage_payload_prefix_or_throw"
            in store
        and "pwrite" in function_body(
            store,
            "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw",
        ),
        "rev0997_borrowed_payload_views_reach_normal_durable_prefix_staging",
        "the receiver validates views into the retained frame and writes normal ranges without another record owner",
    )

    require(
        "constexpr std::size_t payload_bytes = 8U * 1024U * 1024U"
            in response_frame_memory_runtime
        and "AllocationScope measurement" in response_frame_memory_runtime
        and "largest_request <= frame.size() + 4096U"
            in response_frame_memory_runtime
        and "requested_bytes <= frame_bytes + auxiliary_budget"
            in response_frame_memory_runtime
        and "decode_sync_replica_reconciliation_response_or_throw"
            in response_frame_memory_runtime,
        "rev0997_allocator_volume_regression_rejects_second_source_page",
        "one 8 MiB response permits one final-frame allocation plus bounded auxiliary work and exact decode",
    )

    require(
        "kPayloadCount = 16U" in reconciliation_memory_shape_runtime
        and "kPayloadBytes = 1024U * 1024U"
            in reconciliation_memory_shape_runtime
        and "encode_allocations.count == 1U"
            in reconciliation_memory_shape_runtime
        and "borrowed_allocations.count == 0U"
            in reconciliation_memory_shape_runtime
        and "owned_allocations.count >= value.response.payloads.size()"
            in reconciliation_memory_shape_runtime,
        "rev0997_borrowed_decode_allocation_oracle_binds_one_zero_and_copy_differential",
        "the 16 MiB fixture proves one source frame, zero borrowed aggregate copies, and the compatibility decoder differential",
    )

    require(
        "anonsync-response-frame-memory-source-audit-v1"
            in response_frame_memory_audit
        and "anonsync-response-memory-shape-source-audit-v1"
            in response_memory_shape_audit
        and "DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md"
            in verifier
        and "SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md"
            in verifier
        and "tests/sync_replica_reconciliation_frame_memory_test.cpp"
            in verifier
        and "tests/sync_replica_reconciliation_memory_shape_test.cpp"
            in verifier
        and "tools/audit_sync_replica_response_frame_memory.py"
            in verifier
        and "tools/audit_sync_replica_response_memory_shape.py"
            in verifier,
        "rev0997_release_policy_binds_both_endpoint_memory_slices",
        "the archive cannot omit source framing, owned TLS handoff, borrowed decode, durable staging, either allocation oracle, or either focused audit",
    )

    require(
        "not an operating-system peak-RSS claim" in response_frame_memory_design
        and "OpenSSL and kernel socket buffers" in response_frame_memory_design
        and "does not claim one total resident page" in response_memory_shape_design
        and "consuming or streaming source encoder" in response_memory_shape_design
        and "VALIDATION_PENDING_REV0997" not in rev0997_notes
        and "ARCHIVE_PENDING_REV0997" not in rev0997_notes
        and "CODENAME_PENDING_REV0997" not in rev0997_notes
        and "VALIDATION_PENDING_REV0997" not in response_frame_memory_design
        and "ARCHIVE_PENDING_REV0997" not in response_frame_memory_design
        and "CODENAME_PENDING_REV0997" not in response_frame_memory_design
        and "VALIDATION_PENDING_REV0997" not in response_memory_shape_design
        and "ARCHIVE_PENDING_REV0997" not in response_memory_shape_design
        and "CODENAME_PENDING_REV0997" not in response_memory_shape_design
        and "VALIDATION_PENDING_REV0997" not in readme
        and "ARCHIVE_PENDING_REV0997" not in readme
        and "CODENAME_PENDING_REV0997" not in readme
        and "VALIDATION_PENDING_REV0997" not in bootstrap
        and "ARCHIVE_PENDING_REV0997" not in bootstrap
        and "CODENAME_PENDING_REV0997" not in bootstrap,
        "rev0997_final_validation_and_visible_release_cutpoint_are_sealed",
        "the combined memory-ownership correction cannot pass until exact validation and archive identity are final without overstating RSS",
    )

    require(
        "copy_exact_range_into_or_throw" in store_h
        and "std::span<char> destination" in store_h
        and "copy_hash_regular_file_range_into_or_throw" in store,
        "rev0998_payload_store_supports_caller_owned_exact_range_fill",
        "one rooted opened payload can hash and fill a caller-owned frame hole without a range string",
    )

    direct_reader = function_body(
        store,
        "copy_hash_regular_file_range_into_or_throw",
    )
    require(
        "::pread" in direct_reader
        and "std::numeric_limits<ssize_t>::max()" in direct_reader
        and "Sha256DigestBuilder" in direct_reader
        and "same_regular_file_observation" in direct_reader,
        "rev0998_direct_reader_is_bounded_hashed_and_reproved",
        "the common byte path bounds each syscall, hashes exact bytes, and re-proves the inode observation",
    )

    require(
        "struct SyncReplicaReconciliationDirectFrameResponse final"
            in reconciliation_protocol_header
        and "class SyncReplicaReconciliationResponseFrameAssembly final"
            in reconciliation_protocol_header
        and "std::span<char> payload_bytes_or_throw"
            in reconciliation_protocol_header
        and "std::function" not in reconciliation_protocol_header,
        "rev0998_one_frame_assembly_is_explicit_and_not_type_erased",
        "one move-only protocol owner exposes bounded writable holes without executable callbacks",
    )

    require(
        "response_body_metrics_impl_or_throw"
            in reconciliation_protocol_source
        and "append_response_body_impl_or_throw"
            in reconciliation_protocol_source
        and "uncommitted payload slots"
            in reconciliation_protocol_source
        and "state_.reset()" in function_body(
            reconciliation_protocol_source,
            "SyncReplicaReconciliationResponseFrameAssembly::finish_or_throw",
        ),
        "rev0998_frame_assembly_shares_canonical_projection_and_consumes_authority",
        "direct and compatibility framing use one field projection and finishing invalidates mutable assembly",
    )

    rev0998_direct_service = last_function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
    )
    require(
        "struct SyncReplicaFramedInboundReconciliation final"
            in reconciliation_service_h
        and "begin_sync_replica_reconciliation_response_frame_assembly_or_throw"
            in rev0998_direct_service
        and "copy_exact_range_into_or_throw" in rev0998_direct_service
        and "copy_range_or_throw" not in rev0998_direct_service
        and "encode_sync_replica_reconciliation_response_for_request_or_throw"
            not in rev0998_direct_service
        and "decode_sync_replica_reconciliation_response_or_throw"
            not in rev0998_direct_service,
        "rev0998_shipping_source_fills_one_frame_without_range_strings",
        "selected exact descriptors fill canonical frame holes and the product source has no range-copy fallback",
    )

    require(
        "SyncReplicaFramedInboundReconciliation" in reconciliation_tls_source
        and "service.serve_request_frame_or_throw" in reconciliation_tls_source
        and "service.serve_request_or_throw" not in reconciliation_tls_source,
        "rev0998_tls_uses_the_direct_source_result",
        "the owned compatibility decoder is not on the authenticated source path",
    )

    require(
        "kSyncReplicaReconciliationMaximumPayloadsPerPage" in reconciliation_protocol_header
        and "kSyncReplicaReconciliationMaximumPayloadBytesPerPage" in reconciliation_protocol_header
        and "kSyncReplicaReconciliationMaximumResponseFrameBytes" in reconciliation_protocol_header
        and "fixed product memory and descriptor frontier" in reconciliation_protocol_source
        and "payload descriptor fanout beyond the fixed product frontier was accepted" in reconciliation_protocol_runtime
        and "payload page bytes beyond the fixed product frontier were accepted" in reconciliation_protocol_runtime
        and "response frame bytes beyond the fixed product frontier were accepted" in reconciliation_protocol_runtime,
        "rev0998_public_limits_cannot_raise_product_memory_or_descriptor_frontiers",
        "in-process callers may narrow but cannot enlarge the 128-descriptor, 64 MiB payload-page, or 96 MiB response-frame boundary",
    )

    require(
        "direct_frame_payload_page_bytes_at_reservation" in reconciliation_service_h
        and "direct_frame_maximum_source_staging_bytes" in reconciliation_service_h
        and "direct_frame_open_source_descriptors_at_reservation" in reconciliation_service_h
        and "response_direct_source_frames" in reconciliation_tls_header
        and "response_direct_source_frame_payload_page_bytes_at_reservation" in reconciliation_tls_header
        and "response_direct_source_frame_maximum_staging_bytes" in reconciliation_tls_header
        and "response_direct_source_frame_maximum_open_descriptors" in reconciliation_tls_header
        and "reconciliation_response_direct_source_frame_payload_page_bytes_at_reservation" in replica_cli,
        "rev0998_shipping_status_exposes_direct_source_ownership_frontiers",
        "live TLS and CLI results expose direct frames, zero aggregate page ownership, zero staging, and maximum exact descriptor fanout",
    )

    require(
        "response_direct_source_frames" in tls_transport_runtime
        and "response_direct_source_frame_maximum_staging_bytes" in tls_transport_runtime
        and "require_direct_source_frame" in reconciliation_process_runtime
        and "reconciliation_response_direct_source_frame_payload_page_bytes_at_reservation" in reconciliation_process_runtime
        and "reconciliation_response_direct_source_frame_maximum_open_descriptors" in sync_process_runtime,
        "rev0998_unit_and_process_oracles_bind_the_live_shipping_path",
        "unit and real-process tests reject a response that recreates aggregate source bytes, range staging, or unbounded descriptor fanout",
    )

    require(
        "test_direct_response_frame_assembly_lifecycle"
            in reconciliation_protocol_runtime
        and "direct.frame == canonical" in reconciliation_protocol_runtime
        and "committed twice" in reconciliation_protocol_runtime
        and "copy_exact_range_into_or_throw" in runtime,
        "rev0998_protocol_and_store_regressions_bind_lifecycle_and_exact_ranges",
        "runtime tests prove canonical equality, single-use assembly, direct bytes, digest, and extent rejection",
    )

    require(
        "kPayloadBytes = 64U * 1024U * 1024U"
            in direct_source_frame_runtime
        and "kLargeAllocationThreshold = 2U * 1024U * 1024U"
            in direct_source_frame_runtime
        and "probe_generation" in direct_source_frame_runtime
        and "direct_allocations.count == 1U"
            in direct_source_frame_runtime
        and "direct_allocations.peak_active_count == 1U"
            in direct_source_frame_runtime
        and "compatibility_allocations.count == 2U"
            in direct_source_frame_runtime
        and "compatibility_allocations.peak_active_count == 2U"
            in direct_source_frame_runtime
        and "kSyncReplicaMaximumPayloadExtentBytes"
            in direct_source_frame_runtime
        and "kRangeBytes = 4U * 1024U * 1024U"
            in direct_source_frame_runtime
        and "allocations.peak_active_count == 1U"
            in direct_source_frame_runtime,
        "rev0998_memory_oracle_binds_actual_64_mib_and_synthetic_4_tib_shapes",
        "generation-tagged simultaneous ownership distinguishes one shipping frame from compatibility's frame-plus-payload while four-TiB logical extent remains bounded",
    )

    require(
        "anonsync-direct-source-frame-source-audit-v1"
            in direct_source_frame_audit
        and "DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md"
            in verifier
        and "REVISION_NOTES_rev0998.md" in verifier
        and "tests/sync_replica_reconciliation_source_frame_memory_test.cpp"
            in verifier
        and "tools/audit_sync_replica_direct_source_frame.py"
            in verifier,
        "rev0998_release_policy_binds_direct_source_slice",
        "the archive cannot omit descriptor fill, one-frame assembly, runtime memory proof, design, notes, or audit",
    )

    normalized_rev0998 = " ".join(
        (direct_source_frame_design + "\n" + rev0998_notes)
        .replace("**", "")
        .split()
    )
    require(
        "not complete operating-system peak-RSS measurements"
            in normalized_rev0998
        and "OpenSSL" in normalized_rev0998
        and "cross-file chunk discovery" in normalized_rev0998,
        "rev0998_design_keeps_peak_rss_and_product_nonclaims_explicit",
        "the one-frame heap proof is not overstated as complete route or multi-terabyte qualification",
    )

    require(
        "VALIDATION_PENDING_REV0998" not in rev0998_notes
        and "ARCHIVE_PENDING_REV0998" not in rev0998_notes
        and "CODENAME_PENDING_REV0998" not in rev0998_notes
        and "VALIDATION_PENDING_REV0998" not in direct_source_frame_design
        and "ARCHIVE_PENDING_REV0998" not in direct_source_frame_design
        and "CODENAME_PENDING_REV0998" not in direct_source_frame_design
        and "VALIDATION_PENDING_REV0998" not in readme
        and "ARCHIVE_PENDING_REV0998" not in readme
        and "CODENAME_PENDING_REV0998" not in readme
        and "VALIDATION_PENDING_REV0998" not in bootstrap
        and "ARCHIVE_PENDING_REV0998" not in bootstrap
        and "CODENAME_PENDING_REV0998" not in bootstrap,
        "rev0998_final_validation_and_visible_release_cutpoint_are_sealed",
        "direct source ownership cannot pass until exact validation and archive identity replace every placeholder",
    )

    require(
        "struct SyncReplicaSqliteIdentityCutpoint final" in sqlite_owner_h
        and "identity_cutpoint_or_throw" in sqlite_owner_h
        and "read_current_owner_meta_or_throw" in sqlite_owner
        and "WHERE operation_id>?" in sqlite_owner
        and "ORDER BY operation_id LIMIT ?" in sqlite_owner,
        "rev0999_sqlite_owner_exposes_fixed_identity_and_bounded_evidence_page",
        "the repeated reconciliation turn uses fixed owner metadata and one primary-key evidence page rather than a complete retained model",
    )

    rev0999_page = function_body(
        sqlite_owner,
        "SyncReplicaSqliteOwner::evidence_page_or_throw",
    )
    require(
        "load_state_or_throw" not in rev0999_page
        and "all_evidence_operations" not in rev0999_page
        and "std::sort" not in rev0999_page
        and "read_exact_operation_row_or_none_or_throw" in rev0999_page
        and "SyncReplicaSqliteEvidencePageDisposition::SourceChanged" in rev0999_page,
        "rev0999_evidence_page_is_history_cold_and_stale_source_fails_early",
        "one page plus lookahead is decoded without whole-history reconstruction or in-memory sorting",
    )

    rev0999_request = function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::make_request_or_throw",
    )
    rev0999_serve = last_function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw",
    )
    rev0999_apply = function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::apply_response_or_throw",
    )
    require(
        "require_current_owner_identity_or_throw" in rev0999_request
        and "snapshot_or_throw" not in rev0999_request
        and "owner_.evidence_page_or_throw" in rev0999_serve
        and "snapshot_or_throw" not in rev0999_serve
        and "targeted_path_cutpoint_or_throw" in rev0999_apply
        and "local_snapshot" not in rev0999_apply
        and "const SyncReplicaOperation* observed" in rev0999_apply
        and "projected.source_operation = *observed" in rev0999_apply,
        "rev0999_request_serve_and_apply_are_bounded_before_terminal_admission",
        "identity, evidence-page, and exact-path owners replace repeated complete history reads while process-local continuation owns its predecessor copy",
    )

    require(
        "test_identity_cutpoint_is_fixed_and_history_cold" in sqlite_owner_runtime
        and "test_evidence_page_is_primary_key_bounded_and_history_cold" in sqlite_owner_runtime
        and "evidence_page_range_read_count" in sqlite_owner_runtime
        and "ReplicaHistoryReadTrace" in reconciliation_runtime
        and "first bounded delta-progress turn reconstructed complete retained history" in reconciliation_runtime,
        "rev0999_sql_trace_regressions_bind_the_live_bounded_turn",
        "runtime SQL traces fail if populated history reintroduces a complete projection into the repeated range path",
    )

    require(
        "anonsync-bounded-reconciliation-history-access-audit-v1" in bounded_history_audit
        and "BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md" in verifier
        and "REVISION_NOTES_rev0999.md" in verifier
        and "tools/audit_sync_replica_bounded_history_access.py" in verifier,
        "rev0999_release_policy_binds_bounded_history_slice",
        "the release cannot omit the owner, service, traces, design, notes, focused audit, or structural integration",
    )

    normalized_rev0999 = " ".join(
        (bounded_history_design + "\n" + rev0999_notes + "\n" + readme + "\n" + bootstrap)
        .replace("**", "")
        .split()
    )
    require(
        "65,536" in normalized_rev0999
        and "262,144" in normalized_rev0999
        and "terminal remote" in normalized_rev0999
        and "same-UID" in normalized_rev0999,
        "rev0999_scale_multiplier_and_nonclaims_are_explicit",
        "the release states the four-terabyte turn multiplier, retained terminal model boundary, and cooperative local-writer assumption",
    )

    require(
        "VALIDATION_PENDING_REV0999" not in rev0999_notes
        and "ARCHIVE_PENDING_REV0999" not in rev0999_notes
        and "CODENAME_PENDING_REV0999" not in rev0999_notes
        and "VALIDATION_PENDING_REV0999" not in bounded_history_design
        and "ARCHIVE_PENDING_REV0999" not in bounded_history_design
        and "CODENAME_PENDING_REV0999" not in bounded_history_design
        and "VALIDATION_PENDING_REV0999" not in readme
        and "ARCHIVE_PENDING_REV0999" not in readme
        and "CODENAME_PENDING_REV0999" not in readme
        and "VALIDATION_PENDING_REV0999" not in bootstrap
        and "ARCHIVE_PENDING_REV0999" not in bootstrap
        and "CODENAME_PENDING_REV0999" not in bootstrap,
        "rev0999_final_validation_and_visible_release_cutpoint_are_sealed",
        "bounded history access cannot pass until exact validation and archive identity replace every placeholder",
    )

    require(
        "kSyncReplicaSqliteVisibleFileCandidateMaximumPaths = 64U"
            in sqlite_owner_h
        and "kSyncReplicaSqliteVisibleFileCandidateMaximumCanonicalBytes"
            in sqlite_owner_h
        and "visible_file_candidate_page_or_throw" in sqlite_owner_h,
        "rev1000_current_visible_candidate_page_has_hard_frontiers",
        "the cross-file accelerator cannot raise its 64-path or four-MiB metadata page",
    )

    rev1000_page = function_body(
        sqlite_owner,
        "SyncReplicaSqliteOwner::visible_file_candidate_page_or_throw",
    )
    require(
        "WHERE v.canonical_path>? AND v.is_primary=1" in rev1000_page
        and "ORDER BY v.canonical_path LIMIT ?" in rev1000_page
        and "SyncReplicaSqliteVisibleFileCandidatePageDisposition::SourceChanged"
            in rev1000_page
        and "load_state_or_throw" not in rev1000_page
        and "all_evidence_operations" not in rev1000_page
        and "std::sort" not in rev1000_page,
        "rev1000_candidate_page_is_primary_key_bounded_and_history_cold",
        "current-visible acceleration uses one exact range instead of retained-history reconstruction",
    )

    require(
        "CrossFileContentDefinedSearch" in reconciliation_service_h
        and "pending_file_operations" in reconciliation_service_h
        and "CachedCrossFileContentDefinedManifest"
            in reconciliation_service_h
        and "cross_file_candidate_page_attempted" in rev0999_apply
        and (
            "cross_file_manifest_scan_attempted" in rev0999_apply
            or "cross_file_manifest_step_attempted" in rev0999_apply
        )
        and "owner_.visible_file_candidate_page_or_throw" in rev0999_apply,
        "rev1000_service_retains_one_bounded_page_and_hashes_one_candidate_per_turn",
        "failed candidates consume one retained metadata page without repeated page-tail SQL reads",
    )

    require(
        "reuse_local_candidate_chunks_or_throw" in rev0999_apply
        and rev0999_apply.count("reuse_local_candidate_chunks_or_throw(") >= 3
        and "delta predecessor" in rev0999_apply
        and "delta cross-file candidate" in rev0999_apply,
        "rev1000_same_path_and_cross_file_copy_authority_is_centralized",
        "both accelerators reopen immutable source ranges and stage through one exact boundary",
    )

    require(
        "test_visible_file_candidate_page_is_path_bounded_and_history_cold"
            in sqlite_owner_runtime
        and "test_cross_file_content_defined_delta_reuses_renamed_media_chunks"
            in reconciliation_runtime
        and (
            "00-unrelated-media.bin" in reconciliation_runtime
            or "01-unrelated-media.bin" in reconciliation_runtime
        )
        and (
            "candidate_pages == 1U" in reconciliation_runtime
            or "candidate_pages == 2U" in reconciliation_runtime
        )
        and "cross_manifest_scans == 2U" in reconciliation_runtime,
        "rev1000_runtime_oracles_bind_page_retention_and_renamed_media_reuse",
        "one decoy and one matching 48-MiB source exercise bounded multi-turn discovery",
    )

    require(
        "anonsync-cross-file-content-defined-discovery-audit-v1"
            in cross_file_delta_audit
        and "CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md"
            in verifier
        and "REVISION_NOTES_rev1000.md" in verifier
        and "tools/audit_sync_replica_cross_file_delta.py" in verifier,
        "rev1000_release_policy_binds_cross_file_delta_slice",
        "the package must carry implementation, tests, design, notes, focused audit, and structural integration",
    )

    normalized_rev1000 = " ".join(
        (
            cross_file_delta_design
            + "\n"
            + rev1000_notes
            + "\n"
            + readme
            + "\n"
            + bootstrap
        )
        .replace("**", "")
        .split()
    )
    require(
        "one complete candidate" in normalized_rev1000
        and "not a global chunk index" in normalized_rev1000
        and "multi-terabyte" in normalized_rev1000
        and "identity-preserving rename" in normalized_rev1000,
        "rev1000_memory_latency_and_product_nonclaims_are_explicit",
        "bounded metadata and manifests are not overstated as bounded candidate-hash latency or rename semantics",
    )

    require(
        "VALIDATION_PENDING_REV1000" not in rev1000_notes
        and "ARCHIVE_PENDING_REV1000" not in rev1000_notes
        and "CODENAME_PENDING_REV1000" not in rev1000_notes
        and "VALIDATION_PENDING_REV1000" not in cross_file_delta_design
        and "ARCHIVE_PENDING_REV1000" not in cross_file_delta_design
        and "CODENAME_PENDING_REV1000" not in cross_file_delta_design
        and "VALIDATION_PENDING_REV1000" not in readme
        and "ARCHIVE_PENDING_REV1000" not in readme
        and "CODENAME_PENDING_REV1000" not in readme
        and "VALIDATION_PENDING_REV1000" not in bootstrap
        and "ARCHIVE_PENDING_REV1000" not in bootstrap
        and "CODENAME_PENDING_REV1000" not in bootstrap,
        "rev1000_final_validation_and_visible_release_cutpoint_are_sealed",
        "cross-file discovery cannot pass until exact validation and archive identity replace every placeholder",
    )

    require(
        "class SyncReplicaFilePayloadStoreContentDefinedProjection final"
            in store_h
        and "std::unique_ptr<State> state_" in store_h
        and "advance_content_defined_projection_or_throw"
            in store_h,
        "rev1001_projection_is_move_only_process_local_payload_state",
        "bounded hashing progress retains exact digest, observation, parameters, and completed chunks without descriptor authority",
    )

    rev1001_advance = function_body(
        store,
        "advance_content_defined_projection_or_throw(",
    )
    require(
        "maximum_step_bytes == 0U" in rev1001_advance
        and "maximum_step_bytes, source.metadata.size_bytes - before_bytes"
            in rev1001_advance
        and "::pread(" in rev1001_advance
        and "::fstat(source.descriptor, &after)" in rev1001_advance
        and "same_regular_file_observation(source.status, after)"
            in rev1001_advance
        and "completed.whole_sha256 != source.content_sha256"
            in rev1001_advance
        and "catch (...)" in rev1001_advance,
        "rev1001_projection_step_is_bounded_reproved_whole_digest_gated_and_fail_closed",
        "each bounded continuation reopens exact bytes, re-proves the inode observation, and discards ambiguous progress",
    )

    require(
        "class ContentDefinedDigestAccumulator final" in store
        and store.count("ContentDefinedDigestAccumulator") >= 4
        and "hash_regular_file_content_defined_chunks_or_throw"
            in store,
        "rev1001_complete_and_resumable_chunking_share_one_accumulator",
        "rolling boundaries and whole/chunk digest segmentation cannot drift between complete and bounded scans",
    )

    require(
        "kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply"
            in reconciliation_service_h
        and "32ULL * 1024ULL * 1024ULL"
            in reconciliation_service_h
        and "struct CrossFileContentDefinedProjection final"
            in reconciliation_service_h
        and "SyncReplicaFilePayloadStoreContentDefinedProjection projection"
            in reconciliation_service_h,
        "rev1001_service_owns_one_hard_32_mib_partial_projection",
        "one current candidate can progress across turns under a fixed receiver-local hashing frontier",
    )

    require(
        "advance_content_defined_projection_or_throw" in rev0999_apply
        and "projected.projection.completed_chunks()" in rev0999_apply
        and "delta cross-file partial candidate" in rev0999_apply
        and "if (!completed)" in rev0999_apply
        and "if (cross_file_manifest_step_attempted) return;"
            in rev0999_apply,
        "rev1001_partial_chunks_are_reused_before_completion_with_one_step_per_apply",
        "bounded projection latency does not discard useful delta acceleration",
    )

    require(
        "payload_availability_generation_at_sweep_start"
            in reconciliation_service_h
        and "payload_availability_generation_or_throw" in rev0999_apply
        and "delta_cross_file_availability_generation_restarts"
            in rev0999_apply
        and "delta_cross_file_unavailable_candidates" in rev0999_apply,
        "rev1001_late_local_payload_availability_restarts_exhausted_search",
        "a useful current-visible source can appear without changing the causal visible-state digest",
    )

    require(
        "descriptor-streaming bounded projection reopen"
            in runtime
        and "step.hashed_bytes <= 5U" in runtime
        and "stale_parameter_projection" in runtime
        and "retained ambiguous progress after a parameter mismatch"
            in runtime
        and "test_payload_availability_generation_tracks_durable_insertions"
            in runtime
        and "candidate_pages == 2U" in reconciliation_runtime
        and "cross_manifest_scan_steps == 4U" in reconciliation_runtime
        and "availability_generation_restarts == 1U"
            in reconciliation_runtime
        and "partial_candidate_reuse_before_complete_manifest"
            in reconciliation_runtime,
        "rev1001_runtime_oracles_bind_reopen_budget_late_availability_and_partial_reuse",
        "five-byte owner steps and two 48-MiB candidate sweeps exercise the exact continuation shape",
    )

    require(
        "anonsync-bounded-resumable-cross-file-projection-audit-v1"
            in bounded_cross_file_projection_audit
        and "BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md"
            in verifier
        and "REVISION_NOTES_rev1001.md" in verifier
        and "tools/audit_sync_replica_bounded_cross_file_projection.py"
            in verifier,
        "rev1001_release_policy_binds_bounded_projection_slice",
        "the package must carry implementation, tests, design, notes, focused audit, and structural integration",
    )

    normalized_rev1001 = " ".join(
        (
            bounded_cross_file_projection_design
            + "\n"
            + rev1001_notes
            + "\n"
            + readme
            + "\n"
            + bootstrap
        )
        .replace("**", "")
        .split()
    )
    require(
        "32 MiB" in normalized_rev1001
        and "total cold" in normalized_rev1001
        and "process-local" in normalized_rev1001
        and "not yet resumable" in normalized_rev1001
        and "durable or global chunk index" in normalized_rev1001
        and "multi-terabyte" in normalized_rev1001,
        "rev1001_latency_and_product_nonclaims_are_explicit",
        "one bounded hash turn is not overstated as fewer total bytes, restart durability, bounded local copy I/O, or a global index",
    )

    require(
        "VALIDATION_PENDING_REV1001" not in rev1001_notes
        and "ARCHIVE_PENDING_REV1001" not in rev1001_notes
        and "CODENAME_PENDING_REV1001" not in rev1001_notes
        and "VALIDATION_PENDING_REV1001"
            not in bounded_cross_file_projection_design
        and "ARCHIVE_PENDING_REV1001"
            not in bounded_cross_file_projection_design
        and "CODENAME_PENDING_REV1001"
            not in bounded_cross_file_projection_design
        and "VALIDATION_PENDING_REV1001" not in readme
        and "ARCHIVE_PENDING_REV1001" not in readme
        and "CODENAME_PENDING_REV1001" not in readme
        and "VALIDATION_PENDING_REV1001" not in bootstrap
        and "ARCHIVE_PENDING_REV1001" not in bootstrap
        and "CODENAME_PENDING_REV1001" not in bootstrap,
        "rev1001_final_validation_and_visible_release_cutpoint_are_sealed",
        "bounded resumable projection cannot pass until exact validation and archive identity replace every placeholder",
    )

    require(
        "kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply"
            in reconciliation_service_h
        and "32ULL * 1024ULL * 1024ULL" in reconciliation_service_h
        and "kSyncReplicaReconciliationMaximumLocalReuseRangeBytes"
            in reconciliation_service_h
        and "4ULL * 1024ULL * 1024ULL" in reconciliation_service_h,
        "rev1002_local_reuse_has_separate_32_mib_apply_and_4_mib_range_frontiers",
        "matched candidate copy has one aggregate scheduling budget and one bounded buffer independent of wire framing",
    )

    require(
        rev0999_apply.count("std::uint64_t remaining_local_reuse_bytes") == 1
        and "max_local_reuse_bytes_per_apply_" in rev0999_apply
        and "LocalCandidateReuseDisposition::BudgetExhausted" in rev0999_apply
        and "mark_local_reuse_budget_exhausted_or_throw" in rev0999_apply,
        "rev1002_same_path_and_cross_file_reuse_share_one_exhaustible_budget",
        "one apply cannot reset local source-read authority for another candidate path",
    )

    require(
        "chunk_index_for_offset_or_throw" in rev0999_apply
        and "chunk_index_at_boundary" not in reconciliation_service
        and "target_offset - target_chunk_begin" in rev0999_apply
        and "candidate_chunk_begin + intra_chunk_offset" in rev0999_apply,
        "rev1002_durable_prefix_resumes_inside_one_adaptive_chunk",
        "a bounded later turn derives the exact matched source displacement rather than requiring a chunk boundary",
    )

    require(
        "kSyncReplicaReconciliationMaximumLocalReuseRangeBytes" in rev0999_apply
        and "remaining_local_reuse_bytes -= supplied" in rev0999_apply
        and "delta_local_reuse_read_bytes" in rev0999_apply
        and "stage_payload_prefix_or_throw" in rev0999_apply,
        "rev1002_actual_local_reads_are_bounded_and_accounted_before_staging",
        "already committed prefix progress cannot make consumed source I/O disappear",
    )

    require(
        "delta_wire_already_durable_ranges" in rev0999_apply
        and "effective_bytes.remove_prefix" in rev0999_apply
        and "Sha256DigestBuilder suffix_digest" in rev0999_apply
        and "delta_wire_overlap_trimmed_ranges" in rev0999_apply
        and "payload range group overlaps the receiver's exact durable prefix"
            not in rev0999_apply,
        "rev1002_authenticated_wire_suffix_survives_local_budget_exhaustion",
        "bounded local acceleration may skip committed prefixes but cannot discard an already framed advancing suffix",
    )

    require(
        "test_local_reuse_frontier_resumes_inside_one_adaptive_chunk"
            in reconciliation_runtime
        and "restarted_after_exhaustion" in reconciliation_runtime
        and "active_receiver = restarted_receiver.get()"
            in reconciliation_runtime
        and "interior_resumptions >= 1U" in reconciliation_runtime
        and "wire_range_bytes = 768U * 1024U" in reconciliation_runtime
        and "maximum_local_read_range_bytes > wire_range_bytes"
            in reconciliation_runtime
        and "overlap_trimmed_wire_ranges != 0U"
            in reconciliation_runtime
        and "staged_bytes + already_durable_wire_bytes == network_bytes"
            in reconciliation_runtime,
        "rev1002_runtime_restarts_service_and_proves_wire_independent_interior_resume",
        "the one-MiB frontier and 768-KiB multi-range fixture exercise durable continuation and partial wire overlap inside a larger chunk",
    )

    for counter in (
        "delta_local_reuse_read_ranges",
        "delta_local_reuse_read_bytes",
        "delta_local_reuse_maximum_read_range_bytes",
        "delta_local_reuse_budget_exhaustions",
        "delta_local_reuse_interior_resumptions",
        "delta_wire_already_durable_ranges",
        "delta_wire_already_durable_bytes",
        "delta_wire_overlap_trimmed_ranges",
    ):
        require(
            counter in reconciliation_service_h
            and counter in reconciliation_tls_header
            and counter in reconciliation_tls_source
            and counter in sync_cli
            and counter in replica_cli,
            f"rev1002_{counter}_is_visible_through_tls_and_both_clis",
            "bounded local-copy scheduling evidence reaches operator JSON without becoming authority",
        )

    require(
        "anonsync-bounded-local-delta-copy-audit-v1"
            in bounded_local_reuse_audit
        and "BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md"
            in verifier
        and "REVISION_NOTES_rev1002.md" in verifier
        and "tools/audit_sync_replica_bounded_local_reuse.py" in verifier,
        "rev1002_release_policy_binds_bounded_local_copy_slice",
        "the package must carry implementation, test, design, notes, focused audit, and structural integration",
    )

    normalized_rev1002 = " ".join(
        (
            bounded_local_reuse_design
            + "\n"
            + rev1002_notes
            + "\n"
            + readme
            + "\n"
            + bootstrap
        )
        .replace("**", "")
        .split()
    )
    require(
        "32 MiB" in normalized_rev1002
        and "four-MiB" in normalized_rev1002
        and "same-path predecessor manifest" in normalized_rev1002
        and "whole-target" in normalized_rev1002
        and "not a global" in normalized_rev1002.lower()
        and "multi-terabyte" in normalized_rev1002,
        "rev1002_copy_scope_and_remaining_complete_file_io_nonclaims_are_explicit",
        "bounded candidate reads are not overstated as a global I/O, durable index, or target-scale result",
    )

    require(
        "VALIDATION_PENDING_REV1002" not in rev1002_notes
        and "ARCHIVE_PENDING_REV1002" not in rev1002_notes
        and "CODENAME_PENDING_REV1002" not in rev1002_notes
        and "VALIDATION_PENDING_REV1002" not in bounded_local_reuse_design
        and "ARCHIVE_PENDING_REV1002" not in bounded_local_reuse_design
        and "CODENAME_PENDING_REV1002" not in bounded_local_reuse_design
        and "VALIDATION_PENDING_REV1002" not in readme
        and "ARCHIVE_PENDING_REV1002" not in readme
        and "CODENAME_PENDING_REV1002" not in readme
        and "VALIDATION_PENDING_REV1002" not in bootstrap
        and "ARCHIVE_PENDING_REV1002" not in bootstrap
        and "CODENAME_PENDING_REV1002" not in bootstrap,
        "rev1002_final_validation_and_visible_release_cutpoint_are_sealed",
        "bounded local-copy resumption cannot pass until exact validation and archive identity replace every placeholder",
    )

    require(
        "kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply"
            in reconciliation_service_h
        and "32ULL * 1024ULL * 1024ULL" in reconciliation_service_h
        and "max_predecessor_projection_bytes_per_apply_" in reconciliation_service,
        "rev1003_same_path_predecessor_projection_has_a_32_mib_apply_frontier",
        "a same-path multi-terabyte source cannot be completely hashed in one apply",
    )

    require(
        "bool predecessor_manifest_step_attempted = false" in rev0999_apply
        and "if (predecessor_manifest_step_attempted) return;" in rev0999_apply
        and "delta predecessor bounded content-defined projection" in rev0999_apply,
        "rev1003_at_most_one_predecessor_projection_step_runs_per_apply",
        "the source-hash scheduler cannot reset for another predecessor in one owner turn",
    )

    require(
        "struct PredecessorContentDefinedProjection final" in reconciliation_service_h
        and "delta_predecessor_projection_" in reconciliation_service_h
        and "projected.projection.completed_chunks()" in rev0999_apply
        and "delta predecessor partial" in rev0999_apply,
        "rev1003_partial_predecessor_chunks_are_process_local_acceleration",
        "completed chunks may be reused before whole-source completion without becoming admission authority",
    )

    require(
        reconciliation_service.count("extend_content_defined_projection_index_or_throw(") >= 3
        and "std::lower_bound" in reconciliation_service
        and "projected.digest_order.insert" in reconciliation_service
        and "projected.chunk_offsets.push_back" in reconciliation_service,
        "rev1003_same_path_and_cross_file_share_one_incremental_index_helper",
        "partial digest ordering and exact source offsets cannot drift into duplicate implementations",
    )

    require(
        "delta_predecessor_projection_.reset();\n                throw;" in rev0999_apply
        and "delta_cross_file_projection_.reset();\n                throw;" in rev0999_apply,
        "rev1003_lower_projection_failure_clears_both_enclosing_indices",
        "a failed lower owner cannot leave stale outer offsets beside inactive projection state",
    )

    require(
        "constexpr std::uint64_t old_size = 48U * mebibyte" in reconciliation_runtime
        and "predecessor_projection_steps" in reconciliation_runtime
        and "predecessor_incomplete_projection_steps" in reconciliation_runtime
        and "reused_before_predecessor_projection_completed" in reconciliation_runtime
        and "predecessor_manifest_hashed_bytes == old_bytes.size()" in reconciliation_runtime,
        "rev1003_runtime_proves_bounded_two_step_projection_and_early_reuse",
        "the 48-MiB semantic oracle exercises an incomplete 32-MiB turn before exact completion",
    )

    require(
        "const std::string completed_sha256 = running.finish_hex()" in store
        and "completed_sha256 != content_sha256" in store
        and "ResumableSha256Checkpoint" in terminal_verification_state_h
        and "update_resumable_hash_regular_file_range_or_throw" not in store
        and ".anonsync-payload-prefix-v2-" not in reconciliation_service,
        "rev1003_terminal_whole_target_hash_remains_and_raw_pathname_checkpoint_is_excluded",
        "bounded predecessor acceleration and rev1004 continuation do not weaken final whole-target SHA-256 publication authority",
    )

    require(
        "anonsync-bounded-predecessor-projection-audit-v1" in bounded_predecessor_projection_audit
        and "BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md" in verifier
        and "REVISION_NOTES_rev1003.md" in verifier
        and "tools/audit_sync_replica_bounded_predecessor_projection.py" in verifier,
        "rev1003_release_policy_binds_the_bounded_predecessor_slice",
        "the package must carry implementation, runtime proof, design, notes, focused audit, and structural integration",
    )

    normalized_rev1003 = " ".join(
        (bounded_predecessor_projection_design + "\n" + rev1003_notes + "\n" + readme + "\n" + bootstrap)
        .replace("**", "").split()
    )
    require(
        "32 MiB" in normalized_rev1003
        and "terminal" in normalized_rev1003.lower()
        and "unbounded" in normalized_rev1003.lower()
        and "process-local" in normalized_rev1003
        and "not restart-durable" in normalized_rev1003
        and "not a durable or global chunk index" in normalized_rev1003.lower()
        and "multi-terabyte" in normalized_rev1003,
        "rev1003_scope_and_remaining_complete_file_io_nonclaims_are_explicit",
        "bounded same-path projection is not overstated as global I/O, durable indexing, or bounded terminal verification",
    )

    require(
        "VALIDATION_PENDING_REV1003" not in rev1003_notes
        and "ARCHIVE_PENDING_REV1003" not in rev1003_notes
        and "CODENAME_PENDING_REV1003" not in rev1003_notes
        and "VALIDATION_PENDING_REV1003" not in bounded_predecessor_projection_design
        and "ARCHIVE_PENDING_REV1003" not in bounded_predecessor_projection_design
        and "CODENAME_PENDING_REV1003" not in bounded_predecessor_projection_design
        and "VALIDATION_PENDING_REV1003" not in readme
        and "ARCHIVE_PENDING_REV1003" not in readme
        and "CODENAME_PENDING_REV1003" not in readme
        and "VALIDATION_PENDING_REV1003" not in bootstrap
        and "ARCHIVE_PENDING_REV1003" not in bootstrap
        and "CODENAME_PENDING_REV1003" not in bootstrap,
        "rev1003_final_validation_and_visible_release_cutpoint_are_sealed",
        "bounded predecessor projection cannot pass until exact validation and archive identity replace every placeholder",
    )

    require(
        ".anonsync-payload-prefix-verification-v1-" in terminal_verification_state_h
        and "32ULL * 1024ULL * 1024ULL" in terminal_verification_state_h
        and "std::array<" in terminal_verification_state_h
        and "std::optional<SyncReplicaFilePayloadTerminalVerificationState>, 2U>" in terminal_verification_state_h
        and "slots;" in terminal_verification_state_h,
        "rev1004_terminal_continuation_has_one_canonical_two_slot_32_mib_boundary",
        "fixed computation progress is separately named and bounded",
    )

    require(
        all(
            token in terminal_verification_state_h
            for token in (
                "store_identity_sha256",
                "store_identity_metadata",
                "generation",
                "content_sha256",
                "total_size_bytes",
                "staged_prefix_metadata",
                "verified_offset_bytes",
                "ResumableSha256Checkpoint",
            )
        )
        and "sha256_hex(encoded)" in terminal_verification_state
        and "journal has conflicting equal generations" in terminal_verification_state,
        "rev1004_slots_bind_identity_target_inode_extent_generation_and_checksum",
        "a torn or conflicting journal cannot float free of the private staged owner",
    )

    require(
        "SyncReplicaFilePayloadTerminalVerificationState prepared{" in prefix_stage
        and "ResumableSha256{}.checkpoint()" in prefix_stage
        and "staged-prefix verification reset" in prefix_stage
        and "while (rebuilt < prefix.committed_prefix_bytes)" not in prefix_stage
        and "update_resumable_hash_regular_file_range_or_throw" not in store,
        "rev1004_missing_or_bad_journal_restarts_at_zero_without_complete_rebuild",
        "compatibility neither rereads the complete prefix nor truncates already received bytes",
    )

    require(
        "std::array<char, kStreamingBufferBytes> verification_buffer" in prefix_stage
        and "::pread(" in prefix_stage
        and "running.update(std::string_view(" in prefix_stage
        and "kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep" in prefix_stage,
        "rev1004_terminal_hash_reads_exact_staged_inode_with_fixed_memory",
        "the bounded whole digest represents persisted bytes rather than the requested write buffer",
    )

    require(
        "range_digest.update(bytes)" in prefix_stage
        and ordered(
            prefix_stage,
            "pwrite_all_or_throw(",
            "staged prefix range file",
            "staged prefix commit",
            "staged prefix commit directory",
            "committed staged prefix fstat failed",
            "const std::string completed_sha256 = running.finish_hex()",
            "final publication preflight",
            "rename_noreplace_at_or_throw(",
        ),
        "rev1004_source_range_durability_precedes_bounded_terminal_publication",
        "range bytes become durable and basename-committed before local whole-target proof can publish",
    )

    require(
        "if (terminal_verification_only)" in prefix_stage
        and "internal terminal verification call carries source range authority" in prefix_stage
        and "range_bytes == 0U || offset_bytes >= total_size_bytes" in prefix_stage
        and "continue_staged_payload_prefix_verification_or_throw" in store_h,
        "rev1004_source_range_and_local_terminal_entry_points_are_distinct",
        "zero-byte local computation cannot be interpreted as authenticated source payload",
    )

    require(
        "const std::string completed_sha256 = running.finish_hex()" in prefix_stage
        and "completed_sha256 != content_sha256" in prefix_stage
        and "completed staged prefix failed whole-file verification" in prefix_stage
        and "verified_offset_bytes >= state.total_size_bytes" in terminal_verification_state,
        "rev1004_exact_whole_digest_remains_final_publication_authority",
        "serialized nonterminal state never substitutes for exact final SHA-256",
    )

    require(
        "same_regular_file_observation(\n                    prefix.status, verified_prefix_status)" in prefix_stage
        and "completed staged-prefix verification final name proof" in prefix_stage
        and "completed staged-prefix verification read lease cutpoint" in prefix_stage
        and "final publication preflight" in prefix_stage,
        "rev1004_each_step_and_final_publication_reprove_inode_path_store_and_lease",
        "computation progress remains bound to the exact complete staged prefix",
    )

    require(
        "terminal verification journal count exceeds configured budget" in store
        and "sync_replica_file_payload_terminal_verification_journal_exact_bytes" in store
        and "bootstrap.terminal_verification_entry_count != 0U" in store,
        "rev1004_hidden_journal_extent_count_and_bootstrap_influence_are_bounded",
        "internal computation metadata is excluded from public roots without becoming an unbounded namespace",
    )

    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in reconciliation_protocol_header
        and "request-frame-v9" in reconciliation_protocol_source
        and "response-frame-v9" in reconciliation_protocol_source
        and "terminal verification continuation cannot carry a cached delta manifest" in reconciliation_protocol_source
        and "terminal verification continuation did not return one exact payload-cold operation" in reconciliation_protocol_source,
        "rev1004_generation_8_carries_exact_payload_cold_terminal_obligation",
        "the source cursor cannot advance when local whole-target verification remains incomplete",
    )

    require(
        "continue_staged_payload_prefix_verification_or_throw(" in reconciliation_service
        and "local terminal payload verification lost exact identity or admitted source authority" in reconciliation_service
        and "response.next_after_operation_id = request.after_operation_id" in reconciliation_service
        and "response.payload_continuation = request.payload_continuation" in reconciliation_service,
        "rev1004_service_integrates_zero_byte_local_continuation_before_admission",
        "terminal turns repeat the exact operation without reopening or retransmitting source payload bytes",
    )

    require(
        "test_terminal_verification_journal_bounds_restart_work" in runtime
        and "nonterminal 32 MiB checkpoint" in runtime
        and "malformed terminal journal did not restart bounded verification" in runtime
        and "journal count frontier admitted hidden unbounded state" in runtime,
        "rev1004_payload_store_runtime_covers_restart_damage_mismatch_and_capacity",
        "focused tests exercise exact reuse, malformed state, digest mismatch, and bounded hidden entries",
    )

    require(
        "test_dual_slot_torn_update_recovery" in terminal_verification_state_runtime
        and "test_framing_and_semantic_rejection" in terminal_verification_state_runtime
        and "terminal verification advance frontier drifted" in terminal_verification_state_runtime,
        "rev1004_codec_runtime_covers_rotation_conflict_and_public_frontier",
        "the fixed small durable owner has a direct product regression",
    )

    require(
        "generation-9 final range did not hand off" in reconciliation_protocol_runtime
        and "terminal payload verification response did not remain exact and payload-cold" in reconciliation_protocol_runtime
        and "terminal_verification_page_count == 0U" in reconciliation_runtime
        and "terminal_verification_local_continuation_steps == 1U" in reconciliation_runtime
        and "test_terminal_verification_step_budget_yields_exact_continuation" in reconciliation_runtime,
        "rev1004_protocol_and_service_runtime_cover_end_to_end_terminal_handoff",
        "a 48-MiB delta transfer requires bounded local proof and one payload-cold continuation turn",
    )

    require(
        "anonsync_sync_replica_file_payload_terminal_verification_state" in cmake
        and "anonsync_sync_replica_file_payload_terminal_verification_state_test" in cmake
        and "anonsync_sync_replica_terminal_verification_continuation_source_audit" in cmake,
        "rev1004_codec_test_product_sanitizer_and_focused_audit_are_registered",
        "the new owner is not an unbuilt side branch",
    )

    require(
        "anonsync-terminal-payload-verification-continuation-audit-v2" in terminal_verification_audit
        and "BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md" in verifier
        and "REVISION_NOTES_rev1004.md" in verifier
        and "tools/audit_sync_replica_terminal_verification_continuation.py" in verifier,
        "rev1004_release_policy_binds_implementation_runtime_design_and_audit",
        "the archive must carry the complete bounded terminal-verification slice",
    )

    normalized_rev1004 = normalized_prose(
        terminal_verification_design
        + "\n"
        + rev1004_notes
        + "\n"
        + readme
        + "\n"
        + bootstrap
    )
    require(
        "32 MiB" in normalized_rev1004
        and "generation 8" in normalized_rev1004
        and "payload-cold" in normalized_rev1004
        and "complete compatibility reread" in normalized_rev1004
        and "source-side target-manifest" in normalized_rev1004
        and "high-latency" in normalized_rev1004
        and "multi-terabyte" in normalized_rev1004,
        "rev1004_scope_and_remaining_scale_nonclaims_are_explicit",
        "bounded local verification is not overstated as an efficient complete multi-terabyte pipeline",
    )

    require(
        "rejected" in terminal_verification_design.lower()
        and "per-range" in terminal_verification_design.lower()
        and "raw resumable hash state" in terminal_verification_design.lower()
        and "update_resumable_hash_regular_file_range_or_throw" not in store,
        "rev1004_discarded_checkpoint_models_are_absent_and_documented",
        "one retained authority model replaces the abandoned per-range and raw-pathname prototypes",
    )

    require(
        "VALIDATION_PENDING_REV1004" not in rev1004_notes
        and "ARCHIVE_PENDING_REV1004" not in rev1004_notes
        and "CODENAME_PENDING_REV1004" not in rev1004_notes
        and "VALIDATION_PENDING_REV1004" not in terminal_verification_design
        and "ARCHIVE_PENDING_REV1004" not in terminal_verification_design
        and "CODENAME_PENDING_REV1004" not in terminal_verification_design
        and "VALIDATION_PENDING_REV1004" not in readme
        and "ARCHIVE_PENDING_REV1004" not in readme
        and "CODENAME_PENDING_REV1004" not in readme
        and "VALIDATION_PENDING_REV1004" not in bootstrap
        and "ARCHIVE_PENDING_REV1004" not in bootstrap
        and "CODENAME_PENDING_REV1004" not in bootstrap,
        "rev1004_final_validation_and_visible_release_cutpoint_are_sealed",
        "bounded terminal verification cannot pass until exact validation and archive identity replace every placeholder",
    )

    targeted_terminal_observer = function_body(
        store, "observe_staged_prefix_terminal_target_under_lease_or_throw(")
    reconciliation_apply = function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::apply_response_or_throw(")
    require(
        bool(targeted_terminal_observer)
        and "reopen_matching_root_authority_or_throw" in targeted_terminal_observer
        and "exact completed prefix" in targeted_terminal_observer
        and "exact durable payload name" in targeted_terminal_observer
        and "readdir" not in targeted_terminal_observer,
        "rev1005_intermediate_terminal_observation_is_exact_name_and_namespace_cold",
        "journal progress no longer traverses unrelated payload entries",
    )
    require(
        "scan_store_under_lease_or_throw" in prefix_stage
        and prefix_stage.find("scan_store_under_lease_or_throw") <
            prefix_stage.find("rename_noreplace_at_or_throw"),
        "rev1005_final_publication_retains_complete_namespace_preflight",
        "targeted computation never becomes publication authority",
    )
    require(
        "stage_payload_prefix_deferring_terminal_verification_or_throw" in store_h
        and "defer_terminal_verification" in prefix_stage
        and "terminal_verification_steps" in store_h,
        "rev1005_deferred_range_path_makes_step_budget_exact",
        "completed ranged files cannot consume hidden terminal steps after exhaustion",
    )
    require(
        "kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply = 32U"
            in reconciliation_service_header
        and "continue_terminal_verification_locally_or_throw" in reconciliation_apply
        and "terminal_verification_step_budget_exhaustions" in reconciliation_apply,
        "rev1005_service_pulses_bounded_receiver_local_terminal_work",
        "one apply advances at most the configured fixed number of hash steps",
    )
    require(
        "test_targeted_terminal_continuation_defers_namespace_reproof" in runtime
        and "test_deferred_terminal_verification_preserves_exact_prefix" in runtime
        and "test_terminal_verification_step_budget_yields_exact_continuation"
            in reconciliation_runtime,
        "rev1005_runtime_covers_targeted_final_fence_defer_and_yield",
        "the new fast path and its mandatory final boundary are both exercised",
    )
    require(
        "anonsync-targeted-terminal-local-pulse-audit-v1" in targeted_terminal_audit
        and "anonsync_sync_replica_targeted_terminal_local_pulse_source_audit" in cmake
        and "TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md" in verifier
        and "REVISION_NOTES_rev1005.md" in verifier,
        "rev1005_release_policy_binds_implementation_runtime_design_and_audit",
        "the archive must carry the complete targeted local-pulse slice",
    )
    normalized_rev1005 = normalized_prose(
        targeted_terminal_design + "\n" + rev1005_notes + "\n" + readme + "\n" + bootstrap)
    require(
        "1 GiB" in normalized_rev1005
        and "4 TiB" in normalized_rev1005
        and "4,096" in normalized_rev1005
        and "complete final scan" in normalized_rev1005
        and "source-side target-manifest" in normalized_rev1005
        and "background receiver-local scheduler" in normalized_rev1005,
        "rev1005_scale_boundary_and_next_scheduler_nonclaim_are_explicit",
        "targeted verification is not overstated as complete multi-terabyte qualification",
    )
    require(
        all(token not in targeted_terminal_design + rev1005_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1005",
                "ARCHIVE_PENDING_REV1005",
                "CODENAME_PENDING_REV1005",
            )),
        "rev1005_final_validation_and_visible_release_cutpoint_are_sealed",
        "targeted terminal verification cannot pass until publication facts replace every placeholder",
    )

    terminal_scheduler_step = function_body(
        store, "continue_one_pending_terminal_verification_or_throw()")
    peer_terminal_scheduler_step = function_body(
        peer_service, "payload_terminal_verification_step_or_throw()")
    peer_owner_step = function_body(
        peer_service, "SyncReplicaPeerServiceOwner::run_next_or_throw()")
    require(
        "terminal_verification_work" in store
        and "terminal_verification_observation_known" in store
        and "committed_prefix_bytes != prefix.total_size_bytes" in store
        and "state.staged_prefix_metadata == prefix_metadata" in store,
        "rev1006_complete_scan_projects_exact_restart_terminal_work",
        "a complete writable store observation derives bounded work only from exact complete prefixes and usable journals",
    )
    require(
        bool(terminal_scheduler_step)
        and "continue_staged_payload_prefix_verification_or_throw" in terminal_scheduler_step
        and "kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep" in terminal_scheduler_step
        and "terminal_verification_steps == 0U" in terminal_scheduler_step,
        "rev1006_one_store_pulse_reuses_bounded_exact_verifier_and_truthful_accounting",
        "the local lane neither invents a second publication engine nor labels stale-cache reconciliation as hash work",
    )
    require(
        "local_payload_work_ordinary_turn_due" in peer_terminal_scheduler_step
        and "LocalPayloadWorkKind::TerminalVerification" in peer_terminal_scheduler_step
        and "local_payload_work_ordinary_turn_due.has_value()" in peer_owner_step
        and "local_payload_scheduler_may_run = false" in peer_owner_step
        and "observe_folder_wake_or_throw" in peer_owner_step
        and "refresh_ingress_worker" in peer_owner_step,
        "rev1006_peer_service_forces_ordinary_turn_between_local_pulses",
        "receiver-local disk work cannot monopolize the single owner loop",
    )
    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "payload_terminal_verification_scheduler_steps" in peer_status
        and "payload_terminal_verification_ordinary_turn_yields" in peer_status
        and "unknown payload terminal-verification status carries work" in peer_status,
        "rev1006_status_v25_exposes_and_rejects_terminal_scheduler_projection",
        "live and terminal diagnostics are exact rather than best-effort serialization",
    )
    require(
        "test_receiver_local_terminal_scheduler_is_restart_fair_and_bounded" in runtime
        and "test_terminal_scheduler_stale_projection_reconciliation_reports_zero_hash" in runtime
        and "test_terminal_scheduler_stale_capacity_invalidates_without_postcommit_failure" in runtime
        and "staged-prefix scheduler cache" in store
        and "stage_payload_prefix_deferring_terminal_verification_or_throw" in receiver_local_terminal_fixture
        and "no peer process" in receiver_local_terminal_runtime
        and '"payload_terminal_verification_scheduler_steps": 3' in receiver_local_terminal_runtime,
        "rev1006_runtime_covers_restart_fairness_stale_cache_and_peer_independence",
        "focused and real-process regressions bind the new local lane",
    )
    require(
        "anonsync-receiver-local-terminal-scheduler-audit-v1" in receiver_local_terminal_audit
        and "anonsync_sync_replica_receiver_local_terminal_scheduler_source_audit" in cmake
        and "RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md" in verifier
        and "REVISION_NOTES_rev1006.md" in verifier,
        "rev1006_release_policy_binds_implementation_runtime_design_and_audit",
        "the archive must carry the complete receiver-local terminal scheduler slice",
    )
    normalized_rev1006 = normalized_prose(
        receiver_local_terminal_design + "\n" + rev1006_notes + "\n" + readme + "\n" + bootstrap)
    require(
        "4 TiB" in normalized_rev1006
        and "131,072" in normalized_rev1006
        and "32 MiB" in normalized_rev1006
        and "complete payload-store scan" in normalized_rev1006
        and "source-side target-manifest" in normalized_rev1006
        and "single owner thread" in normalized_rev1006,
        "rev1006_scale_cost_and_remaining_nonclaims_are_explicit",
        "peer-independent continuation is not overstated as zero disk work or complete multi-terabyte qualification",
    )
    require(
        all(token not in receiver_local_terminal_design + rev1006_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1006",
                "ARCHIVE_PENDING_REV1006",
                "CODENAME_PENDING_REV1006",
            )),
        "rev1006_final_validation_and_visible_release_cutpoint_are_sealed",
        "receiver-local terminal scheduling cannot pass until publication facts replace every placeholder",
    )
    expected_rev1006_archive = (
        "AnonSync-rev1006-2026.08.05.22.03-"
        "receiverlocalscheduler-restartdiscovery-ownerfairness-malachite.zip"
    )
    require(
        all(expected_rev1006_archive in surface and "malachite" in surface
            for surface in (receiver_local_terminal_design, rev1006_notes, readme, bootstrap)),
        "rev1006_final_archive_identity_is_consistent_across_release_surfaces",
        "a stale or divergent sealer cannot leave one mandatory release document bound to another artifact",
    )

    source_serve = last_function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
    )
    source_projection_helper = function_body(
        reconciliation_service,
        "advance_source_content_defined_projection_or_throw(",
    )
    source_local_projection = function_body(
        reconciliation_service,
        "continue_source_manifest_projection_or_throw()",
    )
    require(
        "kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest"
            in reconciliation_service_header
        and "32ULL * 1024ULL * 1024ULL" in reconciliation_service_header
        and "source_content_defined_projection_" in reconciliation_service_header
        and "max_source_manifest_projection_bytes_per_request_" in reconciliation_service,
        "rev1007_source_manifest_projection_is_process_owned_and_32_mib_bounded",
        "the source cannot hash a complete multi-terabyte payload inside one authenticated request",
    )
    require(
        "advance_content_defined_projection_or_throw" in source_projection_helper
        and "opened.content_sha256()" in source_projection_helper
        and "opened.size_bytes()" in source_projection_helper
        and "opened.metadata()" in source_projection_helper
        and "begin_targeted_access_or_throw" in source_local_projection
        and "SourcePayloadPreparing" in source_serve
        and "response.blocked_operation_id" in source_serve,
        "rev1007_each_source_pulse_reproves_exact_payload_and_returns_typed_blocked_state",
        "process-local acceleration does not become source-byte or cursor authority",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_protocol_header
        and "reconciliation-request-frame-v9" in reconciliation_protocol_source
        and "reconciliation-response-frame-v9" in reconciliation_protocol_source
        and "SourcePayloadPreparing = 4U" in reconciliation_protocol_header
        and "ReconciliationSourcePayloadPreparing = 21U" in sync_once_h,
        "rev1007_generation_9_binds_preparing_state_across_protocol_and_owner_result",
        "mixed old framing cannot interpret the new source-work cutpoint",
    )
    require(
        "source_payload_preparing_responses" in reconciliation_tls_header
        and "result.source_payload_preparing_responses =" not in reconciliation_tls_source
        and "observe_served_response" in reconciliation_tls_source
        and reconciliation_tls_source.count(
            "if (index + 1U < options.max_round_trips)") >= 2
        and "result.payload_continuation = payload_continuation;"
            in reconciliation_tls_source
        and "source_digest.reset();" in reconciliation_tls_source
        and "reconciliation_source_payload_preparing_responses" in replica_cli
        and "source_payload_preparing_responses" in replica_cli
        and "source_payload_preparing_responses" in sync_cli
        and "reconciliation_content_defined_manifest_projection_steps" in replica_cli,
        "rev1007_tls_collapses_and_accounts_source_preparing_without_new_authority",
        "the adjacent double-count defect is absent, bounded turns share one stream, and authorized offsets survive",
    )
    require(
        "test_source_manifest_projection_resumes_across_fresh_serve_sessions"
            in reconciliation_runtime
        and "preparing_responses == 3U" in reconciliation_runtime
        and "test_reconciliation_tls_source_manifest_preparing"
            in tls_transport_runtime
        and "projection_budget = 512U * 1024U"
            in tls_transport_runtime
        and "options.max_round_trips = 3U" in tls_transport_runtime
        and "source_payload_preparing_responses == 2U"
            in tls_transport_runtime
        and "serve_result.ranged_payload_bytes == 8U"
            in tls_transport_runtime
        and reconciliation_process_runtime.count("max_round_trips=3") >= 2
        and '"source_payload_preparing_responses": 2'
            in reconciliation_process_runtime
        and '"source_payload_preparing_responses": 0'
            in reconciliation_process_runtime
        and '"reconciliation_content_defined_manifest_reuses": 1'
            in reconciliation_process_runtime
        and "restart-warm final ranged source completion"
            in reconciliation_process_runtime
        and "bounded source-preparing response did not survive canonical generation-9 framing"
            in reconciliation_protocol_runtime,
        "rev1007_runtime_covers_cross_session_resume_same_stream_progress_and_canonical_framing",
        "focused tests bind exact pulses, blocked identity, collapsed preparation turns, wire progress, fresh-session continuation, and the later restart-warm zero-hash handoff",
    )
    require(
        "anonsync-bounded-source-manifest-projection-audit-v1"
            in bounded_source_manifest_audit
        and "anonsync_sync_replica_bounded_source_manifest_projection_source_audit"
            in cmake
        and "BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md"
            in verifier
        and "REVISION_NOTES_rev1007.md" in verifier,
        "rev1007_release_policy_binds_implementation_runtime_design_and_focused_audit",
        "the archive cannot omit the source-scale correction or its proof surfaces",
    )
    normalized_rev1007 = normalized_prose(
        bounded_source_manifest_design + "\n" + rev1007_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1007 for token in (
            "32 MiB", "generation 9", "process-local", "4 TiB",
            "131,072", "authenticated", "restart", "source-local scheduler",
            "same authenticated TLS stream", "2 GiB", "128 GiB",
        )),
        "rev1007_scale_restart_and_next_scheduler_nonclaims_are_explicit",
        "bounded request work is not overstated as efficient or restart-durable multi-terabyte preparation",
    )
    require(
        all(token not in bounded_source_manifest_design + rev1007_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1007",
                "ARCHIVE_PENDING_REV1007",
                "CODENAME_PENDING_REV1007",
            )),
        "rev1007_final_validation_and_visible_release_cutpoint_are_sealed",
        "source projection cannot pass the structural release gate before exact publication facts exist",
    )

    source_manifest_peer_step = function_body(
        peer_service, "source_manifest_projection_step_or_throw()"
    )
    require(
        "SyncReplicaReconciliationSourceManifestProjectionStatus"
            in reconciliation_service_header
        and "SyncReplicaOperation source_operation"
            in reconciliation_service_header
        and "continue_source_manifest_projection_or_throw()"
            in reconciliation_service_header
        and "begin_targeted_access_or_throw" in source_local_projection
        and "open_optional_payload_for_operation_or_throw"
            in source_local_projection,
        "rev1008_source_local_projection_reenters_exact_targeted_authority",
        "peer-independent continuation keeps exact owner, causal operation, digest-name, extent, and inode reproof",
    )
    require(
        reconciliation_service.count(
            "advance_source_content_defined_projection_or_throw(") >= 3
        and "source_content_defined_manifest_ =" in source_projection_helper
        and "sync_replica_reconciliation_delta_manifest_digest_or_throw"
            in source_projection_helper
        and "SyncReplicaReconciliationCompactManifest::from_manifest_or_throw"
            in source_projection_helper,
        "rev1008_network_and_local_paths_share_one_canonical_projection_helper",
        "bounded restart, hashing, manifest construction, digest, and compact cumulative indexing do not diverge",
    )
    require(
        "enum class LocalPayloadWorkKind" in peer_service
        and "SourceManifestProjection" in peer_service
        and "TerminalVerification" in peer_service
        and "local_payload_work_ordinary_turn_due"
            in source_manifest_peer_step
        and "local_payload_work_ordinary_turn_due.has_value()"
            in peer_owner_step
        and "local_payload_scheduler_may_run = false" in peer_owner_step
        and "next_local_payload_work" in peer_owner_step,
        "rev1008_source_and_receiver_hash_work_share_one_fair_owner_gate",
        "every local pulse yields an ordinary owner turn and simultaneous lanes alternate",
    )
    require(
        '"anonsync.peer-service.status.v26"' in peer_status_h
        and "source_manifest_projection_scheduler_steps" in peer_status
        and "source_manifest_projection_progress_steps" in peer_status
        and "source_manifest_projection_completions" in peer_status
        and "source_manifest_projection_payload_unavailable" in peer_status
        and "source_manifest_projection_restarts" in peer_status
        and "source_manifest_projection_hashed_bytes" in peer_status
        and "source_manifest_projection_ordinary_turn_yields" in peer_status
        and "source_manifest_projection" in sync_cli,
        "rev1008_status_v26_exposes_exact_source_frontier_and_all_scheduler_work",
        "live and terminal diagnostics cannot silently omit peer-independent source preparation",
    )
    require(
        "test_source_manifest_projection_advances_without_a_peer_after_discovery"
            in reconciliation_runtime
        and "hashed_bytes == 173U" in reconciliation_runtime
        and "content_defined_manifest_reuses() == 1U"
            in reconciliation_runtime,
        "rev1008_focused_runtime_proves_local_completion_and_fresh_session_reuse",
        "one authenticated discovery is followed by exact bounded local pulses and zero-work reuse",
    )
    require(
        "PAYLOAD_BYTES = 2 * SOURCE_STEP_BYTES + 4097"
            in source_local_manifest_runtime
        and '"source_payload_preparing_responses": 1'
            in source_local_manifest_runtime
        and '"source_manifest_projection_scheduler_steps": 2'
            in source_local_manifest_runtime
        and '"source_payload_preparing_responses": 0'
            in source_local_manifest_runtime
        and "stop_mode" in source_local_manifest_runtime,
        "rev1008_shipping_process_proves_one_discovery_two_local_pulses_and_clean_drain",
        "the same ready PID completes source work and serves a fresh requester without rehashing",
    )
    require(
        "require_source_manifest_projection_status"
            in service_configuration_runtime
        and "require_source_manifest_projection_step"
            in service_configuration_runtime
        and "require_payload_operator_status" in service_i2p_ingress_runtime
        and "anonsync.peer-service.status.v26"
            in service_configuration_runtime
        and "anonsync.peer-service.status.v26"
            in service_i2p_ingress_runtime,
        "rev1008_direct_and_i2p_status_oracles_require_one_v26_contract",
        "route-specific lifecycle coverage cannot ignore the new source scheduler domain",
    )
    require(
        "anonsync-source-local-manifest-scheduler-audit-v1"
            in source_local_manifest_audit
        and "anonsync_sync_replica_source_local_manifest_scheduler_source_audit"
            in cmake
        and "anonsync_sync_service_source_manifest_scheduler_process_test"
            in cmake
        and "SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md"
            in verifier
        and "REVISION_NOTES_rev1008.md" in verifier,
        "rev1008_release_policy_binds_implementation_runtime_design_and_focused_audit",
        "the archive cannot omit the source-local scheduler or its owner-fairness proof surfaces",
    )
    normalized_rev1008 = normalized_prose(
        source_local_manifest_design + "\n" + rev1008_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1008 for token in (
            "32 MiB", "4 TiB", "131,072", "process-local",
            "O(chunk count)", "restart", "peer-independent",
            "ordinary owner turn", "Android", "ENOSPC",
        )),
        "rev1008_scale_restart_memory_and_product_nonclaims_are_explicit",
        "peer independence is not overstated as solved multi-terabyte RSS, restart cost, or product completeness",
    )
    require(
        all(token not in source_local_manifest_design + rev1008_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1008",
                "ARCHIVE_PENDING_REV1008",
                "CODENAME_PENDING_REV1008",
            )),
        "rev1008_final_validation_and_visible_release_cutpoint_are_sealed",
        "source-local scheduling cannot pass the structural release gate before exact publication facts exist",
    )

    require(
        "kSyncReplicaSourceManifestCheckpointMaximumChunks = 8192U"
            in source_manifest_checkpoint_h
        and "anonsync:sync-replica-source-manifest-checkpoint:v2"
            in source_manifest_checkpoint
        and "sha256_hex(output)" in source_manifest_checkpoint,
        "rev1010_durable_source_manifest_record_is_bounded_and_checksum_framed",
        "one exact bounded record carries restart acceleration rather than an unbounded chunk database",
    )
    require(
        "load_source_manifest_checkpoint_or_none_or_throw" in store_h
        and "publish_source_manifest_checkpoint_or_throw" in store_h
        and "ExclusiveMutation" in function_body(
            store, "SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw("
        )
        and "SharedObservation" in function_body(
            store, "load_source_manifest_checkpoint_or_none_or_throw("
        ),
        "rev1010_durable_source_manifest_store_paths_reenter_existing_root_and_lease_authority",
        "checkpoint observation and publication do not add a second payload-store authority model",
    )
    require(
        "discover_source_manifest_projection_or_throw" in reconciliation_service_header
        and "targeted_path_cutpoint_or_throw" in reconciliation_service
        and "requested_retained_operation_or_none" in reconciliation_service
        and "open_optional_payload_for_operation_or_throw" in reconciliation_service
        and "discover_source_manifest_projection_or_throw" in peer_service,
        "rev1010_durable_source_manifest_restart_reproves_causal_path_payload_and_shipping_scheduler",
        "fresh-process recovery cannot trust a record without current targeted operation and inode proof",
    )
    require(
        "kSyncReplicaReconciliationSourceManifestCheckpointPublicationIntervalBytes"
            in reconciliation_service_header
        and "1ULL * 1024ULL * 1024ULL * 1024ULL"
            in reconciliation_service_header
        and "interval_due" in reconciliation_service,
        "rev1010_durable_source_manifest_publication_cadence_avoids_per_pulse_fsync",
        "the first active frontier and completion are sealed while later active progress is coalesced to one GiB",
    )
    require(
        "verify_self_exec_child_boundary_or_throw" in source_manifest_restart_runtime
        and 'phase == "prepare"' in source_manifest_restart_runtime
        and 'phase == "resume"' in source_manifest_restart_runtime
        and 'phase == "serve"' in source_manifest_restart_runtime
        and "anonsync_self_exec_test_process" in cmake,
        "rev1010_durable_source_manifest_runtime_crosses_true_process_boundaries",
        "object recreation inside one process is not mistaken for restart proof",
    )
    require(
        "anonsync-durable-source-manifest-checkpoint-audit-v1"
            in durable_source_manifest_audit
        and "anonsync_sync_replica_durable_source_manifest_checkpoint_source_audit"
            in cmake
        and "DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md"
            in verifier
        and "REVISION_NOTES_rev1010.md" in verifier,
        "rev1010_durable_source_manifest_release_policy_binds_implementation_runtime_design_and_audit",
        "the archive cannot omit the restart record or its proof surfaces",
    )
    normalized_rev1010 = normalized_prose(
        durable_source_manifest_design + "\n" + rev1010_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1010 for token in (
            "32 MiB", "1 GiB", "4 TiB", "131,072", "8,192",
            "384 KiB", "O(chunk count)", "restart", "transfer authority",
            "global chunk", "Android", "ENOSPC",
        )),
        "rev1010_durable_source_manifest_scale_memory_and_product_nonclaims_are_explicit",
        "restart durability is not overstated as solved total disk work, completed-manifest RSS, or product completeness",
    )
    require(
        all(token not in durable_source_manifest_design + rev1010_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1010",
                "ARCHIVE_PENDING_REV1010",
                "CODENAME_PENDING_REV1010",
            )),
        "rev1010_durable_source_manifest_final_validation_and_release_cutpoint_are_sealed",
        "restart durability cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    checkpoint_chunk_struct = delimited_body(
        source_manifest_checkpoint_h,
        "struct SyncReplicaSourceManifestCheckpointChunk final",
        "{",
        "}",
    )
    require(
        "Sha256DigestValue sha256" in checkpoint_chunk_struct
        and "std::string sha256;" not in checkpoint_chunk_struct
        and "sizeof(SyncReplicaSourceManifestCheckpointChunk) == 40U"
            in source_manifest_checkpoint_h,
        "rev1011_source_manifest_checkpoint_uses_fixed_width_digest_records",
        "the restart checkpoint cannot retain one heap-backed digest string per completed chunk",
    )
    require(
        "chunk.sha256.append_binary_to(output);"
            in source_manifest_checkpoint
        and "chunk.sha256 = cursor.take_binary_digest(\"chunk\")"
            in source_manifest_checkpoint
        and "append_digest_binary_or_throw" not in source_manifest_checkpoint,
        "rev1011_source_manifest_checkpoint_codec_stays_binary_in_memory_and_on_disk",
        "parse and serialization do not rebuild hexadecimal strings for every durable chunk",
    )
    require(
        all(token in source_manifest_checkpoint_runtime for token in (
            "construction.count == 0U",
            "copy.count == 1U",
            "expected_vector_bytes = kChunks * sizeof(Chunk)",
            "parsing.count < 128U",
            "7227966f72190f3f30fd2c3b78c5bd6fbc06568b65da3be6b2f34f067317834f",
            "cc5eb04387b25fd6b5cc7f28796d025f67c010a4363a87743cea1ec0cc996ea2",
            "c50edf7819caaf3c51c898d479262473df55c42ff99d8775a43a5f9532261106",
        )),
        "rev1011_source_manifest_checkpoint_runtime_binds_allocations_and_rev1010_wire_images",
        "maximum-shape memory reduction and exact storage compatibility are executable checks",
    )
    require(
        "for (auto& chunk : projected.chunks)" in reconciliation_service
        and "checkpoint.chunks.emplace_back(chunk.size_bytes, chunk.sha256);"
            in reconciliation_service
        and "manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256);"
            in reconciliation_service
        and "chunk.size_bytes, std::move(chunk.sha256)"
            not in reconciliation_service
        and "chunk.sha256_hex()" not in reconciliation_service,
        "rev1011_source_manifest_checkpoint_bridge_preserves_protocol_strings_and_move_ownership",
        "the checkpoint bridge now preserves the released manifest while fixed digests remove the former 8,192-string ownership boundary",
    )
    require(
        "anonsync-source-manifest-checkpoint-memory-audit-v1"
            in source_manifest_checkpoint_memory_audit
        and "anonsync_sync_replica_source_manifest_checkpoint_memory_source_audit"
            in cmake
        and "SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md"
            in verifier
        and "REVISION_NOTES_rev1011.md" in verifier,
        "rev1011_source_manifest_checkpoint_release_policy_binds_code_runtime_design_and_audit",
        "the release cannot omit the compact representation or its measured proof surface",
    )
    normalized_rev1011 = normalized_prose(
        source_manifest_checkpoint_memory_design + "\n" + rev1011_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1011 for token in (
            "8,192", "532,480", "860,160", "327,680",
            "40-byte", "wire", "131,072", "4 TiB",
            "O(chunk count)", "offset index", "RSS", "Android", "ENOSPC",
        )),
        "rev1011_source_manifest_checkpoint_memory_benefit_and_nonclaims_are_explicit",
        "checkpoint allocator reduction is not overstated as solved multi-terabyte RSS or product completeness",
    )
    require(
        all(token not in source_manifest_checkpoint_memory_design + rev1011_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1011",
                "ARCHIVE_PENDING_REV1011",
                "CODENAME_PENDING_REV1011",
            )),
        "rev1011_source_manifest_checkpoint_final_validation_and_release_cutpoint_are_sealed",
        "heap compaction cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    compact_chunk_struct = delimited_body(
        compact_source_manifest_h,
        "struct SyncReplicaReconciliationCompactManifestChunk final",
        "{",
        "}",
    )
    compact_chunk_aliases_cumulative = (
        "using SyncReplicaReconciliationCompactManifestChunk ="
            in compact_source_manifest_h
        and "SyncReplicaReconciliationCumulativeDeltaChunk"
            in compact_source_manifest_h
    )
    cumulative_compact_chunk_struct = delimited_body(
        reconciliation_protocol_header,
        "struct SyncReplicaReconciliationCumulativeDeltaChunk final",
        "{",
        "}",
    )
    compact_chunk_record = (
        cumulative_compact_chunk_struct
        if compact_chunk_aliases_cumulative
        else compact_chunk_struct
    )
    require(
        "std::uint64_t end_offset_bytes" in compact_chunk_record
        and "Sha256DigestValue sha256" in compact_chunk_record
        and "std::string" not in compact_chunk_record
        and "sizeof(SyncReplicaReconciliationCompactManifestChunk) == 40U"
            in compact_source_manifest_h,
        "rev1012_compact_source_manifest_uses_one_fixed_width_cumulative_record",
        "the completed source cache cannot retain heap digests or a second offset record",
    )
    cached_source_manifest_struct = delimited_body(
        reconciliation_service_h,
        "struct CachedSourceContentDefinedManifest final",
        "{",
        "}",
    )
    require(
        "SyncReplicaReconciliationCompactManifest manifest"
            in cached_source_manifest_struct
        and "chunk_offsets" not in cached_source_manifest_struct
        and "SyncReplicaReconciliationDeltaManifest"
            not in cached_source_manifest_struct,
        "rev1012_compact_source_manifest_replaces_wire_and_offset_cache_duplication",
        "the shipping cache owns one bounded cumulative vector",
    )
    require(
        "std::upper_bound(" in compact_source_manifest
        and "offset < chunk.end_offset_bytes" in compact_source_manifest
        and "materialize_or_throw(" in compact_source_manifest
        and "chunk.sha256" in compact_source_manifest
        and "digest_hex(" not in compact_source_manifest,
        "rev1012_compact_source_manifest_supports_exact_lookup_and_wire_materialization",
        "one cumulative sequence answers range lookup and recreates released wire semantics",
    )
    require(
        reconciliation_service.count(
            "SyncReplicaReconciliationCompactManifest::from_manifest_or_throw("
        ) >= 2
        and "source_manifest.manifest.chunk_index_for_offset_or_throw"
            in reconciliation_service
        and "source_manifest.manifest.borrow_for_direct_frame()"
            in reconciliation_service
        and "source_manifest.manifest.materialize_or_throw("
            not in reconciliation_service,
        "rev1012_compact_source_manifest_is_used_by_restart_completion_and_publication",
        "both cache entry paths and the range path cross the compact boundary",
    )
    require(
        all(token in compact_source_manifest_runtime for token in (
            "wire_cache.count == 2U",
            "construction.count == 1U",
            "copy.count == 1U",
            "lookup.count == 0U",
            "materialization.count == 1U",
            "materialized == wire",
        )),
        "rev1012_compact_source_manifest_runtime_binds_allocator_shape_and_wire_equivalence",
        "maximum retained and transient costs are executable checks",
    )
    require(
        "anonsync-source-manifest-cache-compaction-audit-v1"
            in compact_source_manifest_audit
        and "anonsync_sync_replica_compact_source_manifest_cache_source_audit"
            in cmake
        and "COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md"
            in verifier
        and "REVISION_NOTES_rev1012.md" in verifier,
        "rev1012_compact_source_manifest_release_policy_binds_code_runtime_design_and_audit",
        "the archive cannot omit the compact cache or its measured proof surface",
    )
    normalized_rev1012 = normalized_prose(
        compact_source_manifest_design + "\n" + rev1012_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1012 for token in (
            "8,194", "925,704", "327,680", "598,024", "8,193",
            "860,160", "40-byte", "generation 9", "131,072",
            "32 MiB", "1 GiB", "4 TiB", "O(chunk count)",
            "RSS", "global", "Android", "ENOSPC", "rename/move",
        )),
        "rev1012_compact_source_manifest_benefit_and_nonclaims_are_explicit",
        "cache compaction is not overstated as solved multi-terabyte RSS or product completeness",
    )
    require(
        all(token not in compact_source_manifest_design + rev1012_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1012",
                "ARCHIVE_PENDING_REV1012",
                "CODENAME_PENDING_REV1012",
            )),
        "rev1012_compact_source_manifest_final_validation_and_release_cutpoint_are_sealed",
        "cache compaction cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    shared_digest_class = delimited_body(
        sha256_digest_h,
        "class Sha256DigestValue final",
        "{",
        "}",
    )
    require(
        "std::array<std::uint8_t, kSha256DigestBytes> bytes_"
            in shared_digest_class
        and "std::string bytes_" not in shared_digest_class
        and "sizeof(Sha256DigestValue) == kSha256DigestBytes"
            in sha256_digest_h
        and "std::is_trivially_copyable_v<Sha256DigestValue>"
            in sha256_digest_h
        and "std::is_standard_layout_v<Sha256DigestValue>"
            in sha256_digest_h,
        "rev1013_fixed_binary_manifest_uses_one_shared_32_byte_digest_value",
        "wire, cache, and checkpoint chunks cannot hide per-digest heap ownership",
    )
    require(
        "const auto decoded = decode_lowercase_sha256_or_throw"
            in sha256_digest
        and "bytes_ = decoded" in sha256_digest
        and "append_lowercase_hex_to" in sha256_digest
        and "append_binary_to" in sha256_digest
        and "update_lowercase_hex" in sha256_digest
        and "equals_lowercase_hex" in sha256_digest,
        "rev1013_fixed_binary_manifest_centralizes_canonical_text_binary_and_digest_boundaries",
        "failed assignment is strongly ordered and private duplicate codecs are unnecessary",
    )
    delta_chunk_struct = delimited_body(
        reconciliation_protocol_header,
        "struct SyncReplicaReconciliationDeltaChunk final",
        "{",
        "}",
    )
    require(
        "Sha256DigestValue sha256" in delta_chunk_struct
        and "std::string sha256" not in delta_chunk_struct
        and "sizeof(SyncReplicaReconciliationDeltaChunk) == 40U"
            in reconciliation_protocol_header
        and "std::is_trivially_copyable_v<SyncReplicaReconciliationDeltaChunk>"
            in reconciliation_protocol_header
        and "kSyncReplicaReconciliationProtocolVersion = 9U"
            in reconciliation_protocol_header,
        "rev1013_fixed_binary_manifest_keeps_generation9_chunks_as_40_byte_records",
        "the protocol object changes lifetime representation without changing its wire generation",
    )
    require(
        "const Sha256DigestValue& digest" in reconciliation_protocol_source
        and "digest.append_lowercase_hex_to(out)"
            in reconciliation_protocol_source
        and "digest.update_lowercase_hex(destination)"
            in reconciliation_protocol_source
        and "reader.read_view(" in reconciliation_protocol_source
        and "payload_content_defined_chunk_sha256"
            in reconciliation_protocol_source,
        "rev1013_fixed_binary_manifest_serializes_and_parses_without_per_digest_string_owners",
        "wire bytes are emitted and decoded directly at the fixed-value boundary",
    )
    require(
        "Sha256DigestValue sha256" in compact_chunk_record
        and "Sha256DigestValue sha256" in checkpoint_chunk_struct
        and "digest_bytes_or_throw" not in compact_source_manifest
        and "digest_hex(" not in compact_source_manifest
        and "sha256_hex_to_binary_or_throw" not in source_manifest_checkpoint
        and "digest_binary_to_hex" not in source_manifest_checkpoint,
        "rev1013_fixed_binary_manifest_removes_compact_and_checkpoint_codec_duplication",
        "all three bounded source-manifest representations share one canonical converter",
    )
    require(
        all(token in compact_source_manifest_runtime for token in (
            "parser_shape.count == 1U",
            "parser_shape.requested_bytes == expected_wire_vector_bytes",
            "construction.count == 1U",
            "copy.count == 1U",
            "materialization.count == 1U",
            "lookup.count == 0U",
            "failed fixed-width digest assignment changed the prior value",
        )),
        "rev1013_fixed_binary_manifest_runtime_binds_single_allocation_and_strong_assignment",
        "maximum receive, cache, copy, and publication shapes are executable checks",
    )
    require(
        all(token in reconciliation_protocol_runtime for token in (
            "1e6ae4e901d86679e4219ad764dbb290d1fcb4a2f7520490f8a75b6045efab51",
            "29304b77ca55367bbcd259c9119cdc916a2ca918fe0ae5836560a6a673fa8119",
            "sealed rev1012 request frame",
            "sealed rev1012 response frame",
        ))
        and all(token in source_manifest_checkpoint_runtime for token in (
            "7227966f72190f3f30fd2c3b78c5bd6fbc06568b65da3be6b2f34f067317834f",
            "cc5eb04387b25fd6b5cc7f28796d025f67c010a4363a87743cea1ec0cc996ea2",
            "c50edf7819caaf3c51c898d479262473df55c42ff99d8775a43a5f9532261106",
        )),
        "rev1013_fixed_binary_manifest_binds_exact_rev1012_wire_and_rev1010_checkpoint_images",
        "the representation refactor cannot silently change network or durable bytes",
    )
    require(
        "anonsync-fixed-binary-source-manifest-audit-v1"
            in fixed_binary_manifest_audit
        and "anonsync_sync_replica_fixed_binary_manifest_source_audit"
            in cmake
        and "FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md"
            in verifier
        and "REVISION_NOTES_rev1013.md" in verifier
        and "audit_sync_replica_fixed_binary_manifest.py" in verifier,
        "rev1013_fixed_binary_manifest_release_policy_binds_code_runtime_design_and_audit",
        "the archive cannot omit the shared digest correction or its proof surfaces",
    )
    normalized_rev1013 = normalized_prose(
        fixed_binary_manifest_design + "\n" + rev1013_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1013 for token in (
            "8,192", "860,160", "532,480", "327,680",
            "40 bytes", "32-byte", "generation 9", "4 TiB",
            "131,072", "32 MiB", "1 GiB", "O(chunk count)",
            "RSS", "page-cache", "global", "multi-share", "Android",
            "ENOSPC", "rename/move", "Tor", "I2P",
        )),
        "rev1013_fixed_binary_manifest_benefit_compatibility_and_nonclaims_are_explicit",
        "allocator reduction is not overstated as solved multi-terabyte product memory",
    )
    require(
        all(token not in fixed_binary_manifest_design + rev1013_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1013",
                "ARCHIVE_PENDING_REV1013",
                "CODENAME_PENDING_REV1013",
            )),
        "rev1013_fixed_binary_manifest_final_validation_and_release_cutpoint_are_sealed",
        "the shared digest correction cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    cumulative_manifest_chunk = delimited_body(
        reconciliation_protocol_header,
        "struct SyncReplicaReconciliationCumulativeDeltaChunk final",
        "{",
        "}",
    )
    borrowed_manifest_type = delimited_body(
        reconciliation_protocol_header,
        "struct SyncReplicaReconciliationBorrowedDeltaManifest final",
        "{",
        "}",
    )
    direct_frame_serve = last_function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
    )
    require(
        "std::uint64_t end_offset_bytes" in cumulative_manifest_chunk
        and "Sha256DigestValue sha256" in cumulative_manifest_chunk
        and "sizeof(SyncReplicaReconciliationCumulativeDeltaChunk) == 40U"
            in reconciliation_protocol_header
        and "std::span<const SyncReplicaReconciliationCumulativeDeltaChunk> chunks"
            in borrowed_manifest_type,
        "rev1014_borrowed_manifest_uses_one_fixed_nonowning_cumulative_sequence",
        "direct framing cannot hide a second owning complete-manifest vector",
    )
    require(
        "using SyncReplicaReconciliationCompactManifestChunk ="
            in compact_source_manifest_h
        and "SyncReplicaReconciliationCumulativeDeltaChunk"
            in compact_source_manifest_h
        and "borrow_for_direct_frame() const noexcept"
            in compact_source_manifest_h
        and "materialize_or_throw" not in direct_frame_serve
        and "borrow_for_direct_frame" in direct_frame_serve,
        "rev1014_borrowed_manifest_shipping_path_lends_the_retained_cache",
        "cache-cold publication no longer rebuilds a second 327680-byte vector",
    )
    require(
        "borrowed_delta_manifest_at_or_none_or_throw("
            in reconciliation_protocol_source
        and "if (manifests.empty()) return none;"
            in reconciliation_protocol_source
        and "std::move(payload_byte_counts), {}, limits"
            in reconciliation_protocol_source
        and "allocation-cold compatibility path"
            in reconciliation_protocol_header,
        "rev1014_legacy_direct_path_uses_an_allocation_cold_empty_sidecar",
        "ordinary direct framing does not allocate one null optional per payload",
    )
    require(
        "struct DeltaManifestView final" in reconciliation_protocol_source
        and "from_owned" in reconciliation_protocol_source
        and "from_borrowed" in reconciliation_protocol_source
        and "validate_delta_manifest_view_or_throw"
            in reconciliation_protocol_source
        and "delta_manifest_digest_for_view_or_throw"
            in reconciliation_protocol_source
        and "DeltaManifestAt" in reconciliation_protocol_source,
        "rev1014_borrowed_manifest_centralizes_validation_digest_metrics_and_serialization",
        "owned and borrowed manifests cannot drift into separate protocol rules",
    )
    require(
        "carries both owning and borrowed complete manifests"
            in reconciliation_protocol_source
        and "borrowed complete manifest changed payload extent"
            in reconciliation_protocol_source
        and "direct frame validation" in reconciliation_protocol_source
        and "body_digest_or_throw" in reconciliation_protocol_source
        and "kResponseStructuralDigestDomain"
            in reconciliation_protocol_source
        and "std::copy(" in reconciliation_protocol_source,
        "rev1014_borrowed_manifest_fails_closed_and_is_reproved_before_seal",
        "double authority, extent drift, malformed records, and request placement remain terminal",
    )
    require(
        all(token in compact_source_manifest_runtime for token in (
            "kLargeAllocationThreshold = 256U * 1024U",
            "borrowed_allocations.count == 1U",
            "owned_allocations.count == 2U",
            "owned.frame == borrowed.frame",
            "wire.chunks.size() *",
            "sizeof(SyncReplicaReconciliationDeltaChunk)",
            "explicit_allocations.count == legacy_allocations.count + 1U",
            "sizeof(OptionalBorrowedManifest)",
            "legacy.frame == explicit_result.frame",
        )),
        "rev1014_borrowed_manifest_runtime_binds_one_vs_two_allocations_and_wire_equality",
        "the maximum 4TiB 8192-chunk differential is executable rather than prose-only",
    )
    require(
        all(token in compact_source_manifest_runtime for token in (
            "both owning and borrowed complete manifests",
            "changed payload extent",
            "parameters average chunk size",
            "invalid chunk record",
        )),
        "rev1014_borrowed_manifest_runtime_rejects_ambiguous_and_malformed_authority",
        "double authority, extent drift, parameter drift, and cumulative disorder are executable failures",
    )
    require(
        "direct_frame_borrowed_manifest_count == 1U" in reconciliation_runtime
        and "direct_frame_manifest_materialization_bytes == 0U"
            in reconciliation_runtime
        and "!first_direct.response.payloads[0].delta_manifest.has_value()"
            in reconciliation_runtime
        and "decode_sync_replica_reconciliation_response_or_throw"
            in reconciliation_runtime
        and "expected_borrowed_manifest_count"
            in reconciliation_service
        and "expected_borrowed_manifest_chunks"
            in reconciliation_service
        and "payload.delta_manifest.has_value()"
            in reconciliation_service
        and "direct_frame_borrowed_manifest_count == 0U"
            in direct_source_frame_runtime,
        "rev1014_borrowed_manifest_shipping_runtime_binds_direct_and_whole_payload_paths",
        "production service selection and unchanged whole-payload framing are both proved",
    )
    require(
        "anonsync-borrowed-source-manifest-frame-audit-v1"
            in borrowed_manifest_frame_audit
        and "anonsync_sync_replica_borrowed_manifest_frame_source_audit"
            in cmake
        and "BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md"
            in verifier
        and "REVISION_NOTES_rev1014.md" in verifier
        and "audit_sync_replica_borrowed_manifest_frame.py" in verifier,
        "rev1014_borrowed_manifest_release_policy_binds_code_runtime_design_and_audit",
        "the archive cannot omit the removed-copy implementation or its measured proof",
    )
    normalized_rev1014 = normalized_prose(
        borrowed_manifest_frame_design + "\n" + rev1014_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1014 for token in (
            "327,680", "8,192", "4 TiB", "generation 9", "byte-identical",
            "one large allocation", "O(chunk count)", "131,072", "32 MiB",
            "1 GiB", "RSS", "global", "multi-share", "rename/move",
            "directories", "conflict", "selective-sync", "ENOSPC", "Android",
            "Tor", "I2P",
        )),
        "rev1014_borrowed_manifest_benefit_compatibility_and_nonclaims_are_explicit",
        "one publication copy is not overstated as complete multi-terabyte memory work",
    )
    require(
        all(token not in borrowed_manifest_frame_design + rev1014_notes + readme + bootstrap
            for token in (
                "VALIDATION_PENDING_REV1014",
                "ARCHIVE_PENDING_REV1014",
                "CODENAME_PENDING_REV1014",
            )),
        "rev1014_borrowed_manifest_final_validation_and_release_cutpoint_are_sealed",
        "the direct-frame optimization cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    active_source_chunk = delimited_body(
        store_h,
        "struct SyncReplicaFilePayloadStoreContentDefinedChunk final",
        "{",
        "}",
    )
    active_source_accumulator = delimited_body(
        store,
        "class ContentDefinedDigestAccumulator final",
        "{",
        "}",
    )
    require(
        "Sha256DigestValue sha256" in active_source_chunk
        and "std::string sha256;" not in active_source_chunk
        and "sizeof(SyncReplicaFilePayloadStoreContentDefinedChunk) == 40U"
            in store_h
        and "std::is_trivially_copyable_v<" in store_h,
        "rev1015_active_source_manifest_uses_one_fixed_40_byte_record",
        "the in-progress source frontier cannot retain one digest string per chunk",
    )
    require(
        "finish_binary_array()" in resumable_h
        and "std::array<std::uint8_t, 32U> ResumableSha256::finish_binary_array()"
            in resumable
        and "Sha256DigestValue(chunk_digest_.finish_binary_array())"
            in active_source_accumulator
        and "chunk_digest_.finish_hex()" not in active_source_accumulator,
        "rev1015_active_source_manifest_constructs_chunks_without_digest_text",
        "chunk completion stays binary and allocation-cold until an explicit text boundary",
    )
    require(
        "restored.completed_chunks.emplace_back(" in reconciliation_service
        and "manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256)"
            in reconciliation_service
        and "Sha256DigestValue sha256_value" in source_manifest_checkpoint_h
        and "sha256(std::move(sha256_value))" in source_manifest_checkpoint,
        "rev1015_active_source_manifest_copies_fixed_digests_across_owners",
        "active restore, checkpoint publication, protocol, and compact cache avoid text round trips",
    )
    require(
        "test_active_source_projection_uses_one_fixed_vector_per_share"
            in direct_source_frame_runtime
        and "kConcurrentShares = 64U" in direct_source_frame_runtime
        and "direct.count == 0U" in direct_source_frame_runtime
        and "construction.count == 0U" in direct_source_frame_runtime
        and "copies.count == kConcurrentShares" in direct_source_frame_runtime
        and "expected_bytes == 20U * 1024U * 1024U"
            in direct_source_frame_runtime,
        "rev1015_active_source_manifest_runtime_binds_heap_cold_construction_and_linear_64_share_storage",
        "the exact 8192 by 40-byte frontier is executable rather than prose-only",
    )
    require(
        "anonsync-active-source-manifest-memory-audit-v1"
            in active_source_manifest_memory_audit
        and "anonsync_sync_replica_active_source_manifest_memory_source_audit"
            in cmake
        and "ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md"
            in verifier
        and "REVISION_NOTES_rev1015.md" in verifier
        and "audit_sync_replica_active_source_manifest_memory.py" in verifier,
        "rev1015_active_source_manifest_release_policy_binds_code_runtime_design_and_audit",
        "the package cannot omit the active projection correction or its proof surfaces",
    )
    normalized_rev1015 = normalized_prose(
        active_source_manifest_memory_design + "\n" + rev1015_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1015 for token in (
            "8,192", "327,680", "860,160", "532,480", "40-byte",
            "20 MiB", "52.5 MiB", "32.5 MiB", "4 TiB",
            "generation 9", "checkpoint format remains v2", "O(chunk count)",
            "RSS", "page cache", "multi-share", "rename/move", "directories",
            "conflict", "selective-sync", "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1015_active_source_manifest_benefit_compatibility_and_nonclaims_are_explicit",
        "fixed records are not overstated as solved whole-process multi-terabyte memory",
    )
    terminal_cache_release = function_body(
        reconciliation_service,
        "std::uint64_t SyncReplicaReconciliationService::\n"
        "release_terminal_source_manifest_cache_if_possible_or_throw(",
    )
    source_checkpoint_publish = function_body(
        store,
        "SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw(",
    )
    pending_checkpoint_publish = function_body(
        reconciliation_service,
        "void SyncReplicaReconciliationService::\n"
        "publish_pending_source_manifest_checkpoint_if_possible_or_throw(",
    )
    direct_frame_serve = last_function_body(
        reconciliation_service,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
    )
    require(
        "SyncReplicaSourceManifestCheckpoint& checkpoint" in store_h
        and "SyncReplicaSourceManifestCheckpoint checkpoint"
            not in source_checkpoint_publish
        and "SyncReplicaSourceManifestCheckpoint& committed"
            in pending_checkpoint_publish
        and "SyncReplicaSourceManifestCheckpoint candidate"
            not in pending_checkpoint_publish,
        "rev1015_terminal_manifest_cache_checkpoint_publication_is_in_place",
        "the pending <=8192-record acceleration sequence is not copied before publication",
    )
    require(
        "source_durable_checkpoint_manifest_digest_" in reconciliation_service_h
        and all(token in terminal_cache_release for token in (
            "source.operation_id != operation.operation_id",
            "source.canonical_path != operation.canonical_path",
            "source.content_sha256 != operation.content_sha256",
            "source.total_size_bytes != operation.size_bytes",
            "source_durable_checkpoint_manifest_digest_ != source.manifest_digest",
        )),
        "rev1015_terminal_manifest_cache_release_requires_exact_causal_and_manifest_identity",
        "content equality alone cannot authorize destroying the active compact cache",
    )
    require(
        direct_frame_serve.find("assembly.finish_or_throw()")
            < direct_frame_serve.find("opened_payloads.clear()")
            < direct_frame_serve.find(
                "post-frame source manifest checkpoint publication"
            )
            < direct_frame_serve.find(
                "release_terminal_source_manifest_cache_if_possible_or_throw"
            ),
        "rev1015_terminal_manifest_cache_release_follows_frame_descriptor_and_checkpoint_cutpoints",
        "borrowed views and source descriptors are gone before cache destruction",
    )
    require(
        "struct SyncReplicaReconciliationSourceManifestCacheStatus final"
            in reconciliation_service_h
        and "retained_chunk_capacity_bytes" in reconciliation_service_h
        and "exact_complete_checkpoint_durable" in reconciliation_service_h
        and "source_manifest_cache_terminal_releases == 1U"
            in reconciliation_runtime
        and "complete_checkpoint_restorations == 1U"
            in reconciliation_runtime,
        "rev1015_terminal_manifest_cache_status_and_runtime_bind_release_and_rehydration",
        "the lifecycle correction is observable and executable",
    )
    require(
        "anonsync-terminal-source-manifest-cache-audit-v1"
            in terminal_manifest_cache_audit
        and "anonsync_sync_replica_terminal_manifest_cache_source_audit"
            in cmake
        and "TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md"
            in verifier
        and "REVISION_NOTES_rev1015.md" in verifier
        and "audit_sync_replica_terminal_manifest_cache.py" in verifier,
        "rev1015_terminal_manifest_cache_release_policy_binds_code_runtime_design_and_audit",
        "the archive cannot omit the lifetime correction or its proof surfaces",
    )
    normalized_terminal_rev1015 = normalized_prose(
        terminal_manifest_cache_design + "\n" + rev1015_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_terminal_rev1015 for token in (
            "327,680", "8,192", "40-byte", "generation-9", "4 TiB",
            "131,072", "32 MiB", "1 GiB", "O(chunk count)", "RSS",
            "multi-share", "rename/move", "directory", "conflict",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1015_terminal_manifest_cache_benefit_and_nonclaims_are_explicit",
        "bounded copy and lifetime savings are not overstated as solved product memory",
    )
    require(
        all(token not in (
                active_source_manifest_memory_design
                + terminal_manifest_cache_design
                + rev1015_notes + readme + bootstrap
            ) for token in (
                "VALIDATION_PENDING_REV1015",
                "ARCHIVE_PENDING_REV1015",
                "CODENAME_PENDING_REV1015",
            )),
        "rev1015_memory_corrections_final_validation_and_release_cutpoint_are_sealed",
        "the source-memory corrections cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    resources_request_handler = function_body(
        local_status,
        "std::string process_resources_response() const",
    )
    resources_command = function_body(
        sync_cli,
        "int command_resources(const Options& options)",
    )
    resources_status_start = local_status.find(
        "if (request.has_value() && *request == kStatusRequest)"
    )
    resources_status_end = local_status.find(
        "else if (request.has_value() && *request == kResourcesRequest)",
        resources_status_start,
    )
    resources_status_branch = (
        local_status[resources_status_start:resources_status_end]
        if resources_status_start >= 0 and resources_status_end >= 0
        else ""
    )
    require(
        "anonsync.local-process-resources.response.v1"
            in linux_process_resources_h
        and "anonsync.local-process-resources.aggregate.v1"
            in linux_process_resources_h
        and "constexpr std::string_view kResourcesRequest = \"resources\\n\""
            in local_status,
        "rev1016_linux_process_resources_has_explicit_versioned_local_protocol",
        "resource measurement is an explicit owner request rather than implicit status work",
    )
    require(
        "\"/proc/self/smaps_rollup\"" in linux_process_resources
        and "kMaximumProcSnapshotBytes = 64U * 1024U"
            in linux_process_resources
        and "::read(descriptor, bytes.data(), bytes.size())"
            in linux_process_resources
        and all(token in linux_process_resources for token in (
            "\"Pss_Anon\"", "\"Pss_File\"", "\"Pss_Shmem\"",
            "getrusage(RUSAGE_SELF", "\"/proc/self/fd\"",
            "\"/proc/self/task\"",
        )),
        "rev1016_linux_process_resources_uses_bounded_linux_observation",
        "one smaps_rollup read is combined with process-local identity and usage evidence",
    )
    require(
        'resource_socket_paths_or_throw(options, "resources")'
            in resources_command
        and "sample_resource_round_or_throw(" in resources_command
        and "timeout_is_one_aggregate_deadline" in resources_command
        and "selected.empty() || selected.size() > kResourceMaximumProcesses"
            in sync_cli
        and "same live process" in sync_cli
        and "resource_deadline" in sync_cli,
        "rev1016_linux_process_resources_aggregate_is_bounded_deduplicated_and_deadlined",
        "the shared timeout cannot multiply per socket and one live process is counted once",
    )
    require(
        all(token in resources_command for token in (
            "rss_sum_double_counts_shared_pages",
            "pss_values_use_kernel_share_adjustment",
            "samples_are_sequential_not_atomic",
            "measurement_is_diagnostic_only",
            "ordinary_status_remains_procfs_cold",
        ))
        and "observe_sync_linux_process_resources_or_throw"
            not in resources_status_branch
        and "snapshot_copy()" in resources_status_branch,
        "rev1016_linux_process_resources_keeps_interpretation_and_authority_nonclaims_explicit",
        "ordinary status stays procfs-cold and measurement cannot masquerade as sync authority",
    )
    require(
        "test_strict_smaps_parser" in linux_process_resources_runtime
        and "test_live_observation_and_roundtrip"
            in linux_process_resources_runtime
        and "48 * 1024 * 1024" in linux_process_resources_process_runtime
        and "40 * 1024" in linux_process_resources_process_runtime
        and "same live process" in linux_process_resources_process_runtime
        and '"--delay-milliseconds", "250"'
            in linux_process_resources_process_runtime
        and "deadline_elapsed < 0.8"
            in linux_process_resources_process_runtime
        and "MAP_PRIVATE | MAP_ANONYMOUS" in linux_process_resources_fixture,
        "rev1016_linux_process_resources_runtime_binds_parser_live_delta_and_alias_rejection",
        "the shipping socket aggregate is exercised by two independent processes",
    )
    require(
        "anonsync-linux-process-resources-audit-v2"
            in linux_process_resources_audit
        and "anonsync_sync_linux_process_resources_audit" in cmake
        and "LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md"
            in verifier
        and "REVISION_NOTES_rev1016.md" in verifier
        and "audit_sync_linux_process_resources.py" in verifier,
        "rev1016_linux_process_resources_release_policy_binds_code_runtime_design_and_audit",
        "the package cannot omit the measurement seam or its proof surfaces",
    )
    normalized_rev1016 = normalized_prose(
        linux_process_resources_design + "\n" + rev1016_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1016 for token in (
            "Linux", "one total deadline", "256", "smaps_rollup",
            "Pss_Anon", "Pss_File", "Pss_Shmem", "RSS", "PSS",
            "48 MiB", "40 MiB", "diagnostic", "page cache", "allocator",
            "multi-terabyte", "rename/move", "directories", "conflict",
            "selective-sync", "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1016_linux_process_resources_benefit_and_product_nonclaims_are_explicit",
        "measurement is not overstated as solved memory scale or product support",
    )
    require(
        all(token not in (
            linux_process_resources_design + rev1016_notes + readme + bootstrap
        ) for token in (
            "VALIDATION_PENDING_REV1016",
            "ARCHIVE_PENDING_REV1016",
            "CODENAME_PENDING_REV1016",
        )),
        "rev1016_linux_process_resources_final_validation_and_release_cutpoint_are_sealed",
        "the resource observer cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    resource_socket_selection = function_body(
        sync_cli,
        "[[nodiscard]] std::vector<fs::path> resource_socket_paths_or_throw(",
    )
    resource_round_sampler = function_body(
        sync_cli,
        "[[nodiscard]] ResourceRound sample_resource_round_or_throw(",
    )
    resource_series_command = function_body(
        sync_cli,
        "int command_resources_watch(const Options& options)",
    )
    require(
        "anonsync.local-process-resources.series.v1"
            in linux_process_resources_h
        and "resources-watch" in sync_cli
        and "constexpr std::string_view kResourcesRequest = \"resources\\n\""
            in local_status,
        "rev1017_linux_process_resource_series_has_explicit_schema_and_reuses_owner_request",
        "the time series composes the released exact resource request rather than another daemon protocol",
    )
    require(
        "kResourceMaximumProcesses = 256U" in sync_cli
        and "kResourceWatchMaximumSamples = 1024U" in sync_cli
        and "selected.empty() || selected.size() > kResourceMaximumProcesses"
            in resource_socket_selection
        and "expected_identities" in resource_round_sampler
        and "restart or socket identity change" in resource_round_sampler
        and "final scheduled sample must precede the total deadline"
            in resource_series_command
        and "sleep_until(scheduled_at)" in resource_series_command,
        "rev1017_linux_process_resource_series_is_bounded_fixed_schedule_and_identity_stable",
        "one total deadline and one process lifetime govern every bounded round",
    )
    require(
        "std::vector<ResourceSeriesPoint> points"
            in resource_series_command
        and "std::vector<ResourceProcessEnvelope> envelopes"
            in resource_series_command
        and "retained_shape_is_processes_plus_samples"
            in resource_series_command
        and "full_process_by_sample_matrix_is_not_retained"
            in resource_series_command
        and "between_point_peaks_may_be_missed"
            in resource_series_command
        and "measurement_is_diagnostic_only" in resource_series_command,
        "rev1017_linux_process_resource_series_retains_bounded_points_and_truthful_nonclaims",
        "sampled envelopes cannot become an unbounded response matrix or synchronization authority",
    )
    require(
        '"--samples", "16"' in linux_process_resources_process_runtime
        and '"--interval-milliseconds", "75"'
            in linux_process_resources_process_runtime
        and "growth_trigger.write_bytes"
            in linux_process_resources_process_runtime
        and "40 * 1024" in linux_process_resources_process_runtime
        and "changing_identity_server"
            in linux_process_resources_process_runtime
        and "deadline_elapsed < 0.8"
            in linux_process_resources_process_runtime,
        "rev1017_linux_process_resource_series_runtime_binds_growth_identity_and_deadline",
        "the shipping CLI observes triggered growth and rejects alias, restart, and multiplied timeout paths",
    )
    require(
        "const long page_size = ::sysconf(_SC_PAGESIZE);"
            in linux_process_resources_fixture
        and linux_process_resources_fixture.find("::sysconf(_SC_PAGESIZE)")
            < linux_process_resources_fixture.find("::mmap("),
        "rev1017_linux_process_resource_fixture_closes_pre_raii_mapping_window",
        "the only throwable page-size query precedes mapping ownership",
    )
    require(
        "anonsync-linux-process-resources-audit-v2"
            in linux_process_resources_audit
        and "LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md"
            in verifier
        and "REVISION_NOTES_rev1017.md" in verifier
        and "audit_sync_linux_process_resources.py" in verifier,
        "rev1017_linux_process_resource_series_release_policy_binds_code_runtime_design_and_audit",
        "the archive cannot omit the bounded series or its proof surfaces",
    )
    normalized_rev1017_resources = normalized_prose(
        linux_process_resource_series_design + "\n" + rev1017_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1017_resources for token in (
            "O(processes + samples)", "1,024", "one total deadline",
            "48 MiB", "40 MiB", "between", "diagnostic",
            "multi-terabyte", "page cache", "allocator", "cgroup",
            "rename/move", "directories", "conflict", "selective-sync",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1017_linux_process_resource_series_benefit_and_product_nonclaims_are_explicit",
        "bounded sampled peaks are not overstated as solved product memory or breadth",
    )
    require(
        all(token not in (
            linux_process_resource_series_design + rev1017_notes
            + readme + bootstrap
        ) for token in (
            "VALIDATION_PENDING_REV1017",
            "ARCHIVE_PENDING_REV1017",
            "CODENAME_PENDING_REV1017",
        )),
        "rev1017_linux_process_resource_series_final_validation_and_release_cutpoint_are_sealed",
        "the series cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    delivery_ctor_rev1018 = source_window(
        replica_delivery_service,
        "SyncReplicaDeliveryService::SyncReplicaDeliveryService(",
        "SyncReplicaSqliteSnapshot SyncReplicaDeliveryService::snapshot_or_throw(",
    )
    reconciliation_ctor_rev1018 = source_window(
        reconciliation_service,
        "SyncReplicaReconciliationService::SyncReplicaReconciliationService(",
        "void SyncReplicaReconciliationService::\nrequire_current_owner_identity_or_throw(",
    )
    file_delivery_ctor_rev1018 = source_window(
        service,
        "SyncReplicaFileDeliveryService::SyncReplicaFileDeliveryService(",
        "SyncReplicaFileEffectSqliteSnapshot\nSyncReplicaFileDeliveryService::effect_snapshot_or_throw(",
    )
    effect_identity_cutpoint_rev1018 = function_body(
        file_effect_owner_source,
        "load_identity_cutpoint_or_throw(",
    )
    effect_complete_snapshot_rev1018 = function_body(
        file_effect_owner_source,
        "load_state_or_throw(",
    )
    history_cold_runtime_rev1018 = function_body(
        direct_source_frame_runtime,
        "test_peer_service_startup_is_history_cold_for_four_tib_tree()",
    )
    require(
        "SyncReplicaSqliteIdentityCutpoint identity"
            in delivery_ctor_rev1018
        and "owner_.identity_cutpoint_or_throw()"
            in delivery_ctor_rev1018
        and "snapshot_or_throw()" not in delivery_ctor_rev1018
        and "SyncReplicaSqliteIdentityCutpoint identity"
            in reconciliation_ctor_rev1018
        and "identity.limits.model" in reconciliation_ctor_rev1018
        and "snapshot_or_throw()" not in reconciliation_ctor_rev1018,
        "rev1018_history_cold_startup_replica_services_use_bounded_cutpoints",
        "evidence and reconciliation constructors do not reload retained replica history",
    )
    require(
        "SyncReplicaFileEffectSqliteIdentityCutpoint effect"
            in file_delivery_ctor_rev1018
        and "identity_cutpoint_or_throw()" in file_delivery_ctor_rev1018
        and "snapshot_or_throw()" not in file_delivery_ctor_rev1018
        and "struct SyncReplicaFileEffectSqliteIdentityCutpoint final"
            in file_effect_owner_header,
        "rev1018_history_cold_startup_file_delivery_uses_bounded_effect_cutpoint",
        "file delivery obtains exact effect identity and policy without a complete effect snapshot",
    )
    require(
        "struct LoadedEffectMeta final" in file_effect_owner_source
        and "read_effect_meta_or_throw" in effect_identity_cutpoint_rev1018
        and "load_effect_rows_or_throw" not in effect_identity_cutpoint_rev1018
        and "read_effect_meta_or_throw" in effect_complete_snapshot_rev1018
        and "load_effect_rows_or_throw" in effect_complete_snapshot_rev1018
        and "derive_attestation_or_throw" in effect_complete_snapshot_rev1018,
        "rev1018_history_cold_startup_shares_metadata_codec_and_preserves_full_oracle",
        "one exact metadata decoder feeds the bounded cutpoint while complete reconstruction remains intact",
    )
    require(
        "constexpr std::uint64_t kFiles = 64U"
            in history_cold_runtime_rev1018
        and "64ULL * 1024ULL * 1024ULL * 1024ULL"
            in history_cold_runtime_rev1018
        and "4ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL"
            in history_cold_runtime_rev1018
        and "sync_replica_operations" in history_cold_runtime_rev1018
        and "sync_replica_file_effects" in history_cold_runtime_rev1018
        and "arm_large_allocations(64U * 1024U)"
            in history_cold_runtime_rev1018
        and "startup_allocations.count == 0U"
            in history_cold_runtime_rev1018,
        "rev1018_history_cold_startup_runtime_binds_four_tib_history_and_allocation_fences",
        "the product test proves exact logical scale, negative controls, no history reads, and no 64 KiB allocation",
    )
    require(
        "anonsync-peer-service-startup-audit-v1"
            in history_cold_startup_audit
        and "anonsync_sync_replica_service_startup_source_audit" in cmake
        and "HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md"
            in verifier
        and "REVISION_NOTES_rev1018.md" in verifier
        and "audit_sync_replica_service_startup.py" in verifier,
        "rev1018_history_cold_startup_release_policy_binds_code_runtime_design_and_audit",
        "the archive cannot omit the bounded startup correction or its proof surfaces",
    )
    normalized_rev1018_startup = normalized_prose(
        history_cold_startup_design + "\n" + rev1018_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1018_startup for token in (
            "O(history)", "4 TiB", "64 GiB", "64 KiB", "logical",
            "not a measured whole-process RSS", "multi-terabyte",
            "rename/move", "directories", "conflicts", "selective-sync",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1018_history_cold_startup_benefit_and_product_nonclaims_are_explicit",
        "constructor history-coldness is not overstated as solved owner startup or product breadth",
    )
    require(
        all(token not in (
            history_cold_startup_design + rev1018_notes + readme + bootstrap
        ) for token in (
            "VALIDATION_PENDING_REV1018",
            "ARCHIVE_PENDING_REV1018",
            "CODENAME_PENDING_REV1018",
        )),
        "rev1018_history_cold_startup_final_validation_and_release_cutpoint_are_sealed",
        "the startup correction cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    require(
        "metadata_only_regular_file_logical_bytes" in folder_observer_h
        and "not allocated blocks" in folder_observer_h
        and "regular_file_logical_size_or_throw" in folder_observer
        and "metadata-only regular-file logical bytes exceed " in folder_observer,
        "rev1018_sparse_multiterabyte_selective_memory_observer_reports_checked_logical_extent",
        "metadata-only st_size is explicit checked diagnostic evidence rather than payload work",
    )
    require(
        "local_directory_enumeration_pass_count" in folder_scan_h
        and "local_peak_buffered_directory_component_batch_count" in folder_scan_h
        and "local_peak_simultaneously_buffered_directory_component_count" in folder_scan_h
        and folder_scan.count(
            "peak_simultaneously_buffered_directory_component_count"
        ) >= 2,
        "rev1018_sparse_multiterabyte_selective_memory_pass_preserves_bounded_batch_diagnostics",
        "idle and ordinary passes copy the existing traversal evidence without another walk",
    )
    require(
        "test_selective_sparse_logical_bytes_and_bounded_batch" in folder_observer_runtime
        and "metadata-only sparse logical bytes cross four tebibytes exactly" in folder_observer_runtime
        and "metadata-only logical size does not spend selected byte frontiers" in folder_observer_runtime,
        "rev1018_sparse_multiterabyte_selective_memory_cpp_runtime_crosses_four_tib_without_payload_budget",
        "the focused observer test binds sparse extent, pruning, selected bytes, and the component frontier",
    )
    require(
        "FILE_COUNT_PER_SHARE = 4_097" in sparse_selective_process_runtime
        and "4_399_120_252_928" in sparse_selective_process_runtime
        and sparse_selective_process_runtime.count("start_service(sync=sync") == 2
        and '"resources-watch"' in sparse_selective_process_runtime
        and "RESOURCE_SAMPLES = 24" in sparse_selective_process_runtime
        and "RESOURCE_INTERVAL_MILLISECONDS = 75" in sparse_selective_process_runtime,
        "rev1018_sparse_multiterabyte_selective_memory_real_process_gate_binds_two_services_and_four_tib",
        "two configured services expose one fixed-schedule resource series over the exact sparse workload",
    )
    require(
        "MAXIMUM_AGGREGATE_PSS_KIB = 1024 * 1024" in sparse_selective_process_runtime
        and "MAXIMUM_AGGREGATE_PEAK_RSS_KIB = 1536 * 1024" in sparse_selective_process_runtime
        and '"payload_mutation_work_bytes"' in sparse_selective_process_runtime
        and '"local_peak_buffered_directory_component_batch_count"' in sparse_selective_process_runtime
        and "== 4_096" in sparse_selective_process_runtime,
        "rev1018_sparse_multiterabyte_selective_memory_runtime_binds_memory_and_zero_payload_work",
        "release tripwires, selected-byte zeroes, and the 4,096-name batch are executable",
    )
    require(
        "anonsync_sync_sparse_multiterabyte_selective_resources_process_test" in cmake
        and "anonsync_sync_sparse_multiterabyte_selective_resources_audit" in cmake
        and "anonsync-sparse-multiterabyte-selective-audit-v1" in sparse_selective_memory_audit
        and "SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md" in verifier,
        "rev1018_sparse_multiterabyte_selective_memory_release_policy_binds_runtime_design_and_audit",
        "the complete registry, product lane, structural audit, and package verifier retain the sparse gate",
    )
    normalized_rev1018_sparse = normalized_prose(
        sparse_selective_memory_design + "\n" + rev1018_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1018_sparse for token in (
            "4,399,120,252,928", "4,097", "4,096", "sparse", "logical",
            "metadata-only", "PSS", "peak RSS", "sampled", "million-file",
            "dense", "delta", "rename/move", "directories", "conflict",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1018_sparse_multiterabyte_selective_memory_benefit_and_product_nonclaims_are_explicit",
        "sparse namespace memory is not overstated as dense throughput, million-file scale, or product completion",
    )
    require(
        all(token not in (
            sparse_selective_memory_design + rev1018_notes + readme + bootstrap
        ) for token in (
            "VALIDATION_PENDING_REV1018",
            "ARCHIVE_PENDING_REV1018",
            "CODENAME_PENDING_REV1018",
        )),
        "rev1018_sparse_multiterabyte_selective_memory_final_validation_and_release_cutpoint_are_sealed",
        "the sparse proof cannot pass the structural gate before exact publication facts replace every placeholder",
    )

    require(
        "struct SyncReplicaIdentityPreservingRename final" in model_h
        and "identity_preserving_rename_for_source_tombstone" in model_h
        and "sole_matching_file" in model,
        "rev1019_identity_preserving_regular_file_rename_model_infers_one_unambiguous_causal_shape",
        "ordinary retained File/Tombstone evidence is the restart identity oracle",
    )
    require(
        "SyncReplicaSqliteLocalRenamePublicationResult" in sqlite_owner_h
        and "publish_local_identity_preserving_rename_from_observed_heads_or_throw" in sqlite_owner
        and "const SyncReplicaOperation destination_file" in sqlite_owner
        and "const SyncReplicaOperation source_tombstone" in sqlite_owner
        and "SyncSqliteTransactionMode::Immediate" in sqlite_owner,
        "rev1019_identity_preserving_regular_file_rename_replica_pair_is_one_transaction",
        "destination File and source Tombstone are staged together under one state generation",
    )
    require(
        "record_catalog_identity_preserving_rename_or_throw" in folder_scan
        and "visible_file_content_cutpoint_or_throw" in folder_scan
        and "local_identity_preserving_rename_count" in folder_scan_h,
        "rev1019_identity_preserving_regular_file_rename_folder_owner_fences_ambiguity_and_records_one_catalog_pair",
        "current-visible ambiguity is rejected before rooted publication and the pass exposes exact accounting",
    )
    require(
        "test_atomic_identity_preserving_rename_publication" in sqlite_owner_runtime
        and "test_identity_preserving_regular_file_rename_is_atomic_and_restart_stable" in folder_scan_runtime
        and "test_present_same_content_duplicate_falls_back_before_rename_publication" in folder_scan_runtime
        and "test_ambiguous_same_content_absence_does_not_invent_rename_identity" in folder_scan_runtime,
        "rev1019_identity_preserving_regular_file_rename_runtime_binds_atomicity_restart_payload_reuse_and_ambiguity",
        "focused model, SQLite, and folder regressions cover positive and negative authority paths",
    )
    require(
        "sync_replica_digest_accumulator_zero" in sqlite_owner
        and "sync_replica_visible_path_accumulator_element_digest_or_throw" in sqlite_owner
        and "path_count != meta.visible_path_count" in sqlite_owner
        and "accumulator != meta.visible_state_digest" in sqlite_owner
        and "missing duplicate visible row manufactured rename uniqueness" in sqlite_owner_runtime
        and "projection-drift rejection changed replica state" in sqlite_owner_runtime,
        "rev1019_identity_preserving_regular_file_rename_uniqueness_reproves_visible_projection_witness",
        "a damaged current-visible projection cannot hide a duplicate and manufacture identity continuity",
    )
    require(
        "anonsync-identity-preserving-regular-file-rename-audit-v2" in identity_preserving_rename_audit
        and "targeted_payload_reuse" in folder_scan_h
        and "test_identity_preserving_rename_replica_pair_survives_catalog_crash_window" in folder_scan_runtime
        and "anonsync_sync_replica_identity_preserving_rename_source_audit" in cmake
        and "IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md" in verifier,
        "rev1019_identity_preserving_regular_file_rename_release_policy_binds_design_runtime_and_audit",
        "the complete registry and package cannot omit atomic rename, targeted reuse, or crash-window recovery",
    )
    normalized_rev1019_rename = normalized_prose(
        identity_preserving_rename_design + "\n" + rev1019_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1019_rename for token in (
            "causal identity continuity", "copy", "delete", "regular files only",
            "one catalog generation", "one replica generation", "cross-database",
            "O(active evidence", "million-file", "directory", "conflict",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1019_identity_preserving_regular_file_rename_benefit_and_nonclaims_are_explicit",
        "the first file-move slice is not overstated as complete namespace semantics or measured scale",
    )
    require(
        all(token not in (
            identity_preserving_rename_design + rev1019_notes + readme + bootstrap
        ) for token in (
            "VALIDATION_PENDING_REV1019",
            "ARCHIVE_PENDING_REV1019",
            "CODENAME_PENDING_REV1019",
        )),
        "rev1019_identity_preserving_regular_file_rename_final_validation_and_release_cutpoint_are_sealed",
        "the structural gate remains deliberately red until exact publication facts replace every placeholder",
    )

    require(
        "constexpr std::uint64_t kVisiblePathSchemaVersion = 8U" in sqlite_owner
        and "constexpr std::uint64_t kSchemaVersion = 9U" in sqlite_owner
        and "INDEXED BY sync_replica_visible_file_content" in sqlite_owner
        and "ORDER BY canonical_path,visible_ordinal LIMIT 2" in sqlite_owner,
        "rev1020_bounded_rename_replica_content_projection_is_exact_and_bounded",
        "the v9 current-visible index has an exact v8 source and a forced two-row lookup",
    )
    require(
        "test_exact_v8_migration_builds_visible_content_index" in sqlite_owner_runtime
        and "test_visible_file_content_cutpoint_is_bounded_and_exact" in sqlite_owner_runtime
        and "visible content lookup trusted a forged normalized projection" in sqlite_owner_runtime,
        "rev1020_bounded_rename_replica_runtime_binds_migration_restart_and_forgery",
        "the public content cutpoint is executable rather than a lexical-only claim",
    )
    require(
        "constexpr std::uint64_t kSelectiveSyncSchemaVersion = 6U" in folder_scan
        and "constexpr std::uint64_t kSchemaVersion = 7U" in folder_scan
        and "sync_replica_folder_catalog_file_content " in folder_scan
        and "ORDER BY canonical_path,operation_id LIMIT 2" in folder_scan
        and "struct StreamedCatalogContentProof final" in folder_scan,
        "rev1020_bounded_rename_catalog_projection_and_streaming_proof_are_retained",
        "catalog planning is indexed and publication does not retain a whole-catalog vector",
    )
    require(
        "bounded_conflict_visible_operations" in sqlite_owner_h
        and "visible_file_content_cutpoint_or_throw" in folder_scan
        and "targeted_path_cutpoint_or_throw" in folder_scan
        and "complete_operation_projection_read_count == 0U" in sqlite_owner_runtime,
        "rev1020_bounded_rename_one_file_planning_is_path_content_targeted",
        "two-head adoption remains bounded while unrelated retained history stays cold",
    )
    require(
        "anonsync-bounded-rename-planning-audit-v1" in bounded_rename_planning_audit
        and "anonsync_sync_replica_bounded_rename_planning_source_audit" in cmake
        and "BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md" in verifier,
        "rev1020_bounded_rename_release_policy_binds_design_runtime_and_audit",
        "the complete registry and package cannot omit the scale correction",
    )
    normalized_rev1020 = normalized_prose(
        bounded_rename_planning_design + "\n" + rev1020_notes + "\n"
        + readme + "\n" + bootstrap
    )
    require(
        all(token in normalized_rev1020 for token in (
            "path/content-indexed", "O(N-visible)", "O(N) I/O",
            "O(1) row memory", "million-path", "directory", "conflict",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "rev1020_bounded_rename_benefit_complexity_and_nonclaims_are_explicit",
        "the indexed planner is not overstated as complete namespace scale or product support",
    )
    require(
        all(token not in (
            bounded_rename_planning_design + rev1020_notes + readme + bootstrap
        ) for token in (
            "VALIDATION_PENDING_REV1020",
            "ARCHIVE_PENDING_REV1020",
            "CODENAME_PENDING_REV1020",
        )),
        "rev1020_bounded_rename_final_validation_and_release_cutpoint_are_sealed",
        "the structural gate remains deliberately red until exact publication facts replace every placeholder",
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
