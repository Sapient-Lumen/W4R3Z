#!/usr/bin/env python3
"""Lexical hygiene audit for rev1010 durable source-manifest restart state.

Source spelling is not semantic proof. Compiler, sanitizer, runtime,
reconstruction, and package evidence remain load-bearing.
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
    Path("DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md"),
    Path("REVISION_NOTES_rev1010.md"),
    Path("src/resumable_sha256.hpp"),
    Path("src/sync_replica_content_defined_chunker.hpp"),
    Path("src/sync_replica_content_defined_chunker.cpp"),
    Path("src/sync_replica_source_manifest_checkpoint.hpp"),
    Path("src/sync_replica_source_manifest_checkpoint.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_peer_server_owner.hpp"),
    Path("src/sync_replica_peer_server_owner.cpp"),
    Path("src/sync_replica_peer_service.cpp"),
    Path("tests/self_exec_test_process.hpp"),
    Path("tests/sync_replica_content_defined_chunker_test.cpp"),
    Path("tests/sync_replica_source_manifest_checkpoint_test.cpp"),
    Path("tests/sync_replica_source_manifest_restart_test.cpp"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/audit_sync_replica_durable_source_manifest_checkpoint.py"),
    Path("tools/verify_release_package.py"),
)

@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str

def body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""

def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-durable-source-manifest-checkpoint-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove crash durability, exact inode "
            "identity, bounded I/O, hash continuation, scheduler fairness, "
            "sanitizer cleanliness, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(item) for item in checks],
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
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []
    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [p.as_posix() for p in REQUIRED if not (root / p).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_candidates = (root.parent.parent / "BOOTSTRAPROSE.md", root.parent / "BOOTSTRAPROSE.md")
    bootstrap_path = next((p for p in bootstrap_candidates if p.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(bootstrap_candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {p.as_posix(): (root / p).read_text(encoding="utf-8") for p in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    checkpoint_h = text["src/sync_replica_source_manifest_checkpoint.hpp"]
    checkpoint_c = text["src/sync_replica_source_manifest_checkpoint.cpp"]
    chunker_h = text["src/sync_replica_content_defined_chunker.hpp"]
    chunker_c = text["src/sync_replica_content_defined_chunker.cpp"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    server_h = text["src/sync_replica_peer_server_owner.hpp"]
    server_c = text["src/sync_replica_peer_server_owner.cpp"]
    peer_c = text["src/sync_replica_peer_service.cpp"]
    codec_test = text["tests/sync_replica_source_manifest_checkpoint_test.cpp"]
    restart_test = text["tests/sync_replica_source_manifest_restart_test.cpp"]
    chunker_test = text["tests/sync_replica_content_defined_chunker_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    docs = "\n".join((
        text["README.md"],
        text["DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md"],
        text["REVISION_NOTES_rev1010.md"],
        bootstrap,
    ))

    parse = body(checkpoint_c, "parse_sync_replica_source_manifest_checkpoint_or_throw(")
    serialize = body(checkpoint_c, "serialize_sync_replica_source_manifest_checkpoint_or_throw(")
    load = body(store_c, "load_source_manifest_checkpoint_or_none_or_throw(")
    publish = body(store_c, "SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw(")
    discover = body(service_c, "discover_source_manifest_projection_or_throw()")
    restore = body(service_c, "restore_source_content_defined_checkpoint_without_peer_or_throw()")
    install = body(service_c, "install_source_content_defined_checkpoint_for_operation_or_throw(")
    advance = body(service_c, "advance_source_content_defined_projection_or_throw(")
    scheduler = body(peer_c, "SyncReplicaPeerServiceOwner::run_next_or_throw()")

    require(
        "kSyncReplicaSourceManifestCheckpointMaximumChunks = 8192U" in checkpoint_h
        and "kSyncReplicaSourceManifestCheckpointMaximumCanonicalPathBytes = 4096U" in checkpoint_h
        and "sync_replica_source_manifest_checkpoint_maximum_bytes" in checkpoint_h,
        "record_has_explicit_chunk_path_and_byte_frontiers",
        "the restart record cannot grow with payload extent or unbounded path input",
    )
    require(
        'anonsync:sync-replica-source-manifest-checkpoint:v2' in checkpoint_c
        and "sha256_hex(output)" in serialize
        and "checksum is invalid" in parse,
        "record_is_magic_versioned_and_checksum_framed",
        "torn or altered bytes are not accepted as acceleration",
    )
    require(
        all(token in checkpoint_h for token in (
            "store_identity_sha256", "store_identity_metadata", "generation",
            "operation_id", "canonical_path", "content_sha256",
            "payload_metadata", "parameters", "manifest_digest")),
        "record_binds_store_operation_path_payload_and_manifest_identity",
        "durable state cannot float across stores or causal file values",
    )
    require(
        all(token in checkpoint_h for token in (
            "next_offset_bytes", "completed_chunk_bytes", "whole_hash",
            "current_chunk_hash", "SyncReplicaContentDefinedChunkerCheckpoint",
            "chunks")),
        "active_record_retains_exact_arbitrary_byte_continuation",
        "restart need not discard the current partial chunk",
    )
    require(
        "ActiveProjection" in checkpoint_h and "CompleteManifest" in checkpoint_h
        and "active record is not a nonterminal byte frontier" in checkpoint_c
        and "complete record does not cover the payload" in checkpoint_c,
        "active_and_complete_dispositions_are_strictly_separate",
        "partial state cannot masquerade as a reusable complete manifest",
    )
    require(
        "active record exhausted its chunk-count frontier" in checkpoint_c
        and "chunk count exceeds its durable frontier" in checkpoint_c
        and "encoded extent exceeded its maximum" in checkpoint_c,
        "codec_rejects_chunk_and_encoded_extent_overflow",
        "a malformed record cannot allocate beyond the reviewed frontier",
    )
    require(
        "checkpoint()" in chunker_h
        and "validate_sync_replica_content_defined_chunker_checkpoint_or_throw" in chunker_h
        and "SyncReplicaContentDefinedChunkerCheckpoint checkpoint" in chunker_h
        and "gear_hash" in chunker_h
        and "pending_chunk_bytes" in chunker_h
        and "completed_chunk_count" in chunker_h,
        "chunker_exports_and_validates_provider_independent_state",
        "rolling boundary selection resumes at the exact byte frontier",
    )
    require(
        "resumed chunker changed a later boundary" in chunker_test
        and "resumed chunker ended with different scalar state" in chunker_test,
        "chunker_runtime_proves_roundtrip_and_suffix_equivalence",
        "the resumed boundary stream matches uninterrupted hashing",
    )
    require(
        "SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint" in store_h
        and "restore_checkpoint_or_throw" in store_h
        and "ResumableSha256Checkpoint" in store_h,
        "payload_projection_exposes_one_copyable_bounded_checkpoint",
        "durability does not retain descriptors or store leases",
    )
    require(
        bool(load) and "SharedObservation" in load
        and "observe_source_manifest_checkpoint_file_or_throw" in load
        and "final lease cutpoint" in load and "retained-root proof" in load,
        "checkpoint_load_reenters_rooted_shared_store_authority",
        "pathname bytes alone are never trusted",
    )
    require(
        bool(publish) and "ExclusiveMutation" in publish
        and "write_sync_file_atomically" in publish
        and "post-publication" in publish
        and "lease.verify_or_throw" in publish,
        "checkpoint_publication_is_writer_fenced_atomic_and_reopened",
        "the returned generation names the exact durable record",
    )
    require(
        "kSyncReplicaSourceManifestCheckpointBasename" in store_c
        and "basename == kSyncReplicaSourceManifestCheckpointBasename" in store_c
        and "transient_reserved_bytes" in store_c,
        "checkpoint_basename_is_reserved_from_payload_inventory",
        "internal acceleration cannot become a digest-named payload",
    )
    require(
        bool(restore) and "targeted_path_cutpoint_or_throw" in restore
        and "requested_retained_operation_or_none" in restore
        and "checkpoint->canonical_path" in restore
        and "open_optional_payload_for_operation_or_throw" in service_c,
        "restart_restore_uses_targeted_causal_and_payload_reproof",
        "no full history or payload-tree scan is required",
    )
    require(
        bool(install) and "content_sha256" in install
        and "total_size_bytes" in install
        and "payload_metadata" in install
        and "restore_checkpoint_or_throw" in install
        and "source_content_defined_manifest_->source_metadata" in service_c
        and "opened->metadata()" in service_c,
        "checkpoint_install_requires_exact_current_payload_observation",
        "same bytes on a replacement inode do not inherit stale progress",
    )
    require(
        bool(discover) and "require_current_owner_identity_or_throw" in discover
        and "restore_source_content_defined_checkpoint_without_peer_or_throw" in discover
        and "source_manifest_projection_status" in discover,
        "explicit_discovery_is_owner_bound_and_status_remains_cold",
        "restart effects are separate from diagnostic inspection",
    )
    require(
        "discover_source_manifest_projection_or_throw" in server_h
        and "->discover_source_manifest_projection_or_throw()" in server_c
        and "discover_source_manifest_projection_or_throw" in scheduler,
        "shipping_single_owner_scheduler_invokes_restart_discovery",
        "peer-free restart progress does not wait for another requester",
    )
    retry_at = discover.find(
        "publish_pending_source_manifest_checkpoint_if_possible_or_throw(")
    restore_at = discover.find(
        "restore_source_content_defined_checkpoint_without_peer_or_throw();")
    require(
        retry_at >= 0 and restore_at > retry_at
        and "Completion clears the process-local projection before the optional"
        in discover,
        "peer_free_discovery_retries_retained_complete_publication",
        "a typed final publication failure cannot leave completed work restart-cold until another peer request",
    )
    require(
        "kSyncReplicaReconciliationSourceManifestCheckpointPublicationIntervalBytes" in service_h
        and "1ULL * 1024ULL * 1024ULL * 1024ULL" in service_h
        and "interval_due" in advance,
        "active_checkpoint_cadence_is_one_gib_not_every_fairness_pulse",
        "4 TiB preparation avoids 131,072 atomic metadata publications",
    )
    require(
        "!retained_checkpoint_matches" in advance
        and "source_durable_checkpoint_complete_" in advance
        and "CompleteManifest" in service_c,
        "first_progress_and_completion_are_always_sealed",
        "a first useful frontier and the terminal manifest survive restart",
    )
    require(
        "catch (const SyncReplicaFilePayloadStoreLeaseBusyError&)" in service_c
        and "catch (const SyncAtomicFilePublicationError&)" in service_c
        and "pending_source_manifest_checkpoint_" in service_c,
        "optional_publication_failure_retains_bounded_acceleration_only",
        "checkpoint availability cannot make re-proved payload bytes unavailable",
    )
    require(
        "void test_round_trip()" in codec_test
        and "void test_bounded_maximum_shape()" in codec_test
        and "void test_rejection()" in codec_test,
        "codec_runtime_covers_active_complete_and_malformed_records",
        "format acceptance is not inferred from one happy path",
    )
    require(
        "verify_self_exec_child_boundary_or_throw" in restart_test
        and 'phase == "prepare"' in restart_test
        and 'phase == "resume"' in restart_test
        and 'phase == "serve"' in restart_test
        and "spawn_self_exec_test_process_or_throw" in restart_test,
        "restart_runtime_crosses_three_fresh_process_images",
        "new C++ objects inside one process are not mistaken for restart proof",
    )
    require(
        "hash exactly the remaining source bytes" in restart_test
        and "rehashed a completed durable manifest" in restart_test
        and "self-exec complete checkpoint" in restart_test,
        "self_exec_runtime_proves_suffix_resume_and_zero_hash_reuse",
        "the active frontier is consumed once and the complete manifest is reusable",
    )
    require(
        "same bytes" in restart_test
        and "stale durable frontier" in restart_test
        and "physical payload inventory" in restart_test,
        "restart_runtime_covers_inode_drift_lower_frontier_and_inventory_exclusion",
        "stale cache state cannot suppress current exact hashing",
    )
    require(
        all(token in restart_test for token in (
            "class FileSizePublicationFault final",
            "RLIMIT_FSIZE",
            "SIGXFSZ",
            "test_completed_publication_retries_from_peer_free_discovery",
            "failed completion publication replaced the last durable frontier",
            "fresh service rehashed after peer-free complete-checkpoint retry",
        )),
        "runtime_proves_failed_completion_publication_retry",
        "a deterministic write fault preserves the prior frontier before peer-free completion sealing",
    )
    require(
        "anonsync_sync_replica_source_manifest_checkpoint" in cmake
        and "anonsync_sync_replica_source_manifest_checkpoint_test" in cmake
        and "anonsync_sync_replica_source_manifest_restart_test" in cmake
        and "anonsync_self_exec_test_process" in cmake,
        "codec_and_true_restart_tests_are_in_the_build_graph",
        "the new durability surface is not a manual-only test",
    )
    require(
        "anonsync_product_lane" in cmake
        and "anonsync_sync_replica_source_manifest_restart_test" in cmake,
        "restart_runtime_is_in_the_product_lane",
        "ordinary focused validation executes the process-boundary proof",
    )
    require(
        "anonsync_sync_replica_durable_source_manifest_checkpoint_source_audit" in cmake,
        "focused_rev1010_audit_is_registered",
        "the lexical release boundary participates in CTest",
    )
    require(
        "DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md" in verifier
        and "REVISION_NOTES_rev1010.md" in verifier
        and "sync_replica_source_manifest_checkpoint.cpp" in verifier
        and "sync_replica_source_manifest_restart_test.cpp" in verifier,
        "release_verifier_requires_the_complete_rev1010_slice",
        "implementation cannot be packaged without runtime and authority records",
    )
    require(
        "rev1010_durable_source_manifest" in structural
        and "source_manifest_checkpoint" in structural,
        "structural_audit_binds_checkpoint_store_scheduler_and_release_surfaces",
        "the complete authority inventory evolves with the new record",
    )
    normalized = " ".join(docs.split())
    require(
        all(token in normalized for token in (
            "32 MiB", "1 GiB", "4 TiB", "131,072", "8,192",
            "384 KiB", "O(chunk count)", "restart", "publication",
            "transfer authority",
            "global chunk", "Android", "ENOSPC")),
        "documentation_states_scale_cost_and_product_nonclaims",
        "restart durability is not overstated as solved RSS or product completeness",
    )
    require(
        "unmaterialized" in normalized and "rev1008" in normalized and "rev1009" in normalized,
        "documentation_records_the_exact_available_parent_lineage",
        "the missing rev1009 archive is not fabricated as source authority",
    )
    require(
        all(token not in docs for token in (
            "VALIDATION_PENDING_REV1010", "ARCHIVE_PENDING_REV1010",
            "CODENAME_PENDING_REV1010")),
        "final_release_placeholders_are_sealed",
        "the focused audit cannot pass before exact validation and archive identity are published",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(encoding="utf-8")
        and "not semantic proof" in Path(__file__).read_text(encoding="utf-8"),
        "lexical_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)

if __name__ == "__main__":
    raise SystemExit(main())
