#!/usr/bin/env python3
"""Lexical audit for rev0994 bounded content-defined delta.

This is source-shape hygiene, not semantic proof. Compiler, sanitizer, runtime,
reconstruction, performance, and package evidence remain load-bearing.
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
    Path("CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"),
    Path("REVISION_NOTES_rev0994.md"),
    Path("src/sync_replica_content_defined_chunker.hpp"),
    Path("src/sync_replica_content_defined_chunker.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("tests/sync_replica_content_defined_chunker_test.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_replica_content_defined_delta.py"),
    Path("tools/verify_release_package.py"),
)

@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [c.check_id for c in checks if not c.passed]
    report = {
        "format": "anonsync-content-defined-delta-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove cryptography, crash safety, insertion "
            "reuse, memory bounds, performance, privacy, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(c) for c in checks],
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
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {p.as_posix(): (root / p).read_text(encoding="utf-8") for p in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"]
    notes = text["REVISION_NOTES_rev0994.md"]
    chunk_h = text["src/sync_replica_content_defined_chunker.hpp"]
    chunk_c = text["src/sync_replica_content_defined_chunker.cpp"]
    payload_h = text["src/sync_replica_file_payload_store.hpp"]
    payload_c = text["src/sync_replica_file_payload_store.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    chunk_test = text["tests/sync_replica_content_defined_chunker_test.cpp"]
    payload_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_content_defined_delta_source_audit" in cmake
        and "tools/audit_sync_replica_content_defined_delta.py" in cmake,
        "focused_audit_registered",
        "the content-defined delta audit is in the ordinary test registry",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "reconciliation-request-frame-v9" in protocol_c
        and "reconciliation-response-frame-v9" in protocol_c,
        "protocol_and_domains_are_generation_7",
        "older fixed-boundary frames cannot decode as current",
    )
    require(
        all(token in chunk_h for token in (
            "minimum_chunk_bytes", "average_chunk_bytes",
            "maximum_chunk_bytes", "maximum_chunk_count",
            "class SyncReplicaContentDefinedChunker",
        ))
        and "std::vector" not in chunk_h,
        "chunker_state_is_scalar_and_allocation_free",
        "the boundary detector owns no payload-sized or chunk-count-sized storage",
    )
    require(
        "kGearTable" in chunk_c and "gear_hash_" in chunk_c
        and "boundary_mask_" in chunk_c
        and "pending_chunk_bytes_ >= parameters_.maximum_chunk_bytes" in chunk_c,
        "gear_boundaries_have_a_forced_maximum",
        "random boundary scheduling cannot produce an unbounded chunk",
    )
    require(
        "kSyncReplicaReconciliationMinimumAverageChunkBytes" in protocol_h
        and "4ULL * 1024ULL * 1024ULL" in protocol_h
        and "kSyncReplicaReconciliationMaximumAverageChunkBytes" in protocol_h
        and "1024ULL * 1024ULL * 1024ULL" in protocol_h
        and "kSyncReplicaReconciliationMaximumContentDefinedChunks = 8192U" in protocol_h,
        "manifest_has_explicit_4mib_to_1gib_8192_frontier",
        "one active manifest remains bounded independently of tree size",
    )
    require(
        "kSyncReplicaReconciliationMaximumAverageChunkBytes / 2U" in protocol_h
        and "kSyncReplicaMaximumPayloadExtentBytes" in protocol_h,
        "worst_case_manifest_frontier_covers_exact_4tib_extent",
        "minimum-sized chunks still fit at the maximum supported payload extent",
    )
    require(
        "average *= 2U" in protocol_c
        and "worst_case_count" in protocol_c
        and "parameters.maximum_chunk_count" in protocol_c,
        "canonical_parameters_scale_without_peer_selected_geometry",
        "large files increase average chunk size under one canonical policy",
    )
    require(
        "SyncReplicaFilePayloadStoreContentDefinedManifest" in payload_h
        and "content_defined_manifest_or_throw" in payload_h
        and "SyncReplicaFilePayloadStoreFixedBlockManifest" not in payload_h
        and "fixed_block_manifest_or_throw" not in payload_h,
        "payload_store_has_one_delta_projection_engine",
        "the superseded fixed-block projection was removed instead of retained beside shipping code",
    )
    require(
        "hash_regular_file_content_defined_chunks_or_throw" in payload_c
        and "::pread" in payload_c
        and "same_regular_file_observation" in payload_c
        and "whole_sha256" in payload_c,
        "payload_projection_is_descriptor_rooted_and_whole_file_reproved",
        "chunk hints never replace complete SHA-256 identity",
    )
    require(
        "SyncReplicaReconciliationDeltaChunk" in protocol_h
        and "SyncReplicaReconciliationDeltaManifest" in protocol_h
        and "delta_chunk_offset_bytes" in protocol_h
        and "delta_chunk_size_bytes" in protocol_h,
        "wire_manifest_binds_variable_chunk_sizes_and_exact_extent",
        "range offsets are interpreted through cumulative chunk sizes",
    )
    require(
        "ranged payload crosses its content-defined chunk boundary" in protocol_c
        and "full chunk digest disagrees with its content-defined manifest" in protocol_c,
        "wire_ranges_are_confined_and_complete_chunks_are_sha_bound",
        "a full chunk cannot be substituted under a matching range hash alone",
    )
    require(
        "cached_delta_manifest_digest" in protocol_h
        and "delta_manifest_digest" in protocol_h
        and "delta_manifest" in protocol_h,
        "bounded_manifest_reference_survives_generation_7",
        "continuations carry a constant-size exact reference after bootstrap",
    )
    require(
        "CachedTargetContentDefinedManifest" in service_h
        and "CachedPredecessorContentDefinedManifest" in service_h
        and service_h.count("std::vector<std::uint64_t> chunk_offsets") >= 2,
        "receiver_caches_cumulative_offsets_for_target_and_predecessor",
        "bounded continuations do not rebuild variable-offset geometry every range",
    )
    require(
        "auto reuse_local_candidate_chunks_or_throw" in service_c
        and "chunk_index_for_offset_or_throw(" in service_c
        and "target_offset - target_chunk_begin" in service_c
        and "candidate_offsets[*candidate_chunk]" in service_c
        and "candidate_chunk_begin + intra_chunk_offset" in service_c
        and "first_read_resumes_inside_chunk" in service_c
        and "delta_local_reuse_interior_resumptions" in service_c
        and "auto reuse_predecessor_chunks_or_throw" in service_c
        and "auto reuse_cross_file_chunks_or_throw" in service_c
        and service_c.count("reuse_local_candidate_chunks_or_throw(") >= 3,
        "predecessor_reuse_allows_shifted_offsets",
        "same-path and cross-file candidates share one shifted-offset, interior-resumable copy boundary",
    )
    require(
        "auto matching_candidate_chunk" in service_c
        and "candidate_chunks[*found].sha256 == target_chunk.sha256" in service_c
        and "candidate_chunks[*found].size_bytes ==" in service_c
        and "target_chunk.size_bytes" in service_c
        and "std::lower_bound" in service_c,
        "reuse_matches_sha256_and_exact_chunk_size",
        "gear boundaries schedule lookup but do not grant byte authority",
    )
    require(
        "stage_payload_prefix_or_throw" in service_c
        and "owner_.accept_remote_or_throw(operation)" in service_c
        and service_c.index("stage_payload_prefix_or_throw") < service_c.rindex("owner_.accept_remote_or_throw(operation)"),
        "crash_safe_prefix_staging_precedes_operation_admission",
        "reused and network bytes converge through the existing durable prefix owner",
    )
    require(
        all(token in service_h for token in (
            "reused_payload_chunks", "reused_payload_ranges", "reused_payload_bytes",
            "content_defined_manifest_scans", "content_defined_manifest_reuses",
            "target_content_defined_manifest_publications",
        )),
        "service_exposes_content_defined_work_accounting",
        "network, source hashing, target cache, and local reuse remain distinguishable",
    )
    require(
        all(token in tls_h + tls_c for token in (
            "reused_payload_chunks", "content_defined_manifest_scans",
            "content_defined_manifest_publications",
            "target_content_defined_manifest_publications",
        )),
        "tls_exchange_preserves_delta_accounting",
        "the shipping framed transport does not discard focused counters",
    )
    require(
        all(token in replica_cli + sync_cli for token in (
            "reused_payload_chunks", "content_defined_manifest_scans",
            "target_content_defined_manifest_publications",
        )),
        "shipping_json_surfaces_content_defined_work",
        "delta efficiency can be observed from retained CLI surfaces",
    )
    require(
        "forced maximum" in chunk_test
        and "inserted fixture" in chunk_test
        and "chunk-count frontier" in chunk_test,
        "chunker_regression_covers_forced_boundary_insertion_and_frontier",
        "the scalar boundary engine has deterministic negative controls",
    )
    require(
        "content-defined projection" in payload_test
        and "undersized content-defined frontier" in payload_test,
        "payload_store_regression_covers_projection_and_count_failure",
        "descriptor streaming and bounded manifest storage are exercised",
    )
    require(
        "8,192-chunk manifest frontier" in protocol_test
        and "maximum manifest reference" in protocol_test
        and "more than 256 GiB" in protocol_test,
        "protocol_regression_covers_4tib_shape_and_reference",
        "the maximum representation is tested without allocating a 4 TiB file",
    )
    require(
        "test_content_defined_delta_reuses_shifted_predecessor_chunks" in service_test
        and "shifted_matching_chunks" in service_test
        and "candidate_chunk_begin" in service_c,
        "service_regression_proves_shifted_insertion_reuse",
        "the end-to-end fixture contains insertion, a distant edit, bounded pages, and exact final bytes",
    )
    require(
        "content_defined_manifest_scans" in tls_test
        and "target_content_defined_manifest_reuses" in tls_test,
        "tls_regression_uses_generation_6_accounting",
        "the actual transport exercises manifest publication and reference reuse",
    )
    shipping = "\n".join((payload_h, payload_c, protocol_h, protocol_c, service_h, service_c, tls_h, tls_c, replica_cli, sync_cli))
    require(
        all(token not in shipping for token in (
            "FixedBlock", "fixed_block_manifest", "reused_payload_blocks",
            "target_fixed_block_manifest", "kSyncReplicaReconciliationMaximumFixedBlocks",
        )),
        "shipping_fixed_block_engine_is_absent",
        "one content-defined implementation owns the current delta path",
    )
    require(
        "CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md" in verifier
        and "REVISION_NOTES_rev0994.md" in verifier
        and "tools/audit_sync_replica_content_defined_delta.py" in verifier,
        "release_verifier_binds_rev0994_slice",
        "the archive cannot omit the design record, revision record, or focused audit",
    )
    require(
        "## Rev0994:" in readme and "REV0994 RELEASE CUTPOINT" in bootstrap,
        "visible_release_surfaces_name_rev0994",
        "README and release-root runbook describe the same product move",
    )
    visible = "\n".join((readme, design, notes, bootstrap))
    require(
        "VALIDATION_PENDING_REV0994" not in visible
        and "ARCHIVE_PENDING_REV0994" not in visible,
        "final_release_placeholders_are_sealed",
        "validation and archive identity must be concrete before publication",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(encoding="utf-8")
        and "not semantic proof" in Path(__file__).read_text(encoding="utf-8"),
        "audit_disclaims_semantic_authority",
        "source spelling cannot replace runtime and package proof",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
