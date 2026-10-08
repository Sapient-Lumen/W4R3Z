#!/usr/bin/env python3
"""Lexical hygiene audit for rev1014 borrowed source-manifest framing.

Source spelling is not semantic proof. Compiler, sanitizer, runtime allocation,
wire-equivalence, lifetime, reconstruction, and package evidence remain
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
    Path("BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md"),
    Path("REVISION_NOTES_rev1014.md"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_compact_manifest.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_reconciliation_compact_manifest_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_reconciliation_source_frame_memory_test.cpp"),
    Path("tools/audit_sync_replica_borrowed_manifest_frame.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature: str, occurrence: int = 0) -> str:
    search = 0
    start = -1
    for _ in range(occurrence + 1):
        start = text.find(signature, search)
        if start < 0:
            return ""
        search = start + len(signature)
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


def block(text: str, start_token: str, end_token: str) -> str:
    start = text.find(start_token)
    if start < 0:
        return ""
    end = text.find(end_token, start + len(start_token))
    if end < 0:
        return ""
    return text[start:end]


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-borrowed-source-manifest-frame-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove span lifetime, allocation count, "
            "wire equality, runtime authority, sanitizer cleanliness, peak RSS, "
            "throughput, source reconstruction, or package identity"
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
    bootstrap_candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in bootstrap_candidates if path.is_file()), None)
    require(
        bootstrap_path is not None,
        "release_root_bootstrap_exists",
        str(bootstrap_candidates),
    )
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md"]
    notes = text["REVISION_NOTES_rev1014.md"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    compact_h = text["src/sync_replica_reconciliation_compact_manifest.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    compact_test = text["tests/sync_replica_reconciliation_compact_manifest_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    memory_test = text["tests/sync_replica_reconciliation_source_frame_memory_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    cumulative = block(
        protocol_h,
        "struct SyncReplicaReconciliationCumulativeDeltaChunk final",
        "struct SyncReplicaReconciliationBorrowedDeltaManifest final",
    )
    borrowed = block(
        protocol_h,
        "struct SyncReplicaReconciliationBorrowedDeltaManifest final",
        "[[nodiscard]] SyncReplicaContentDefinedChunkingParameters",
    )
    direct_response = block(
        protocol_h,
        "struct SyncReplicaReconciliationDirectFrameResponse final",
        "class SyncReplicaReconciliationResponseFrameAssembly final",
    )
    serve = function_body(
        service_c,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
        occurrence=1,
    )
    assembly = function_body(
        protocol_c,
        "begin_sync_replica_reconciliation_response_frame_assembly_or_throw(",
        occurrence=2,
    )
    finish = function_body(
        protocol_c,
        "SyncReplicaReconciliationResponseFrameAssembly::finish_or_throw()",
    )

    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_remains_9",
        "the ownership correction is not a protocol fork",
    )
    require(
        "std::uint64_t end_offset_bytes" in cumulative
        and "Sha256DigestValue sha256" in cumulative
        and "sizeof(SyncReplicaReconciliationCumulativeDeltaChunk) == 40U"
            in protocol_h
        and "std::is_trivially_copyable_v<"
            in protocol_h,
        "cumulative_record_is_fixed_width_and_nonowning",
        "one compact chunk remains one 40-byte extent-plus-digest record",
    )
    require(
        "std::span<const SyncReplicaReconciliationCumulativeDeltaChunk> chunks"
            in borrowed
        and "std::vector" not in borrowed
        and "std::string" not in borrowed,
        "borrowed_manifest_owns_no_sequence",
        "direct framing receives only parameters, extent, and a borrowed span",
    )
    require(
        "using SyncReplicaReconciliationCompactManifestChunk ="
            in compact_h
        and "SyncReplicaReconciliationCumulativeDeltaChunk" in compact_h
        and "borrow_for_direct_frame() const noexcept" in compact_h
        and "return {parameters_, total_size_bytes_, chunks_};" in compact_h,
        "compact_cache_lends_its_exact_retained_sequence",
        "no translation buffer is required before frame assembly",
    )
    require(
        "borrowed_delta_manifest_count" in direct_response
        and "borrowed_delta_manifest_chunks" in direct_response
        and "frame is the complete canonical authority" in protocol_h,
        "direct_result_reports_borrowed_shape_and_names_frame_authority",
        "process metadata does not pretend to own a manifest it only framed",
    )
    require(
        "materialize_or_throw" not in serve
        and "borrow_for_direct_frame" in serve
        and "first_range" in serve
        and "cached_delta_manifest_digest" in serve,
        "shipping_service_never_materializes_the_cache_cold_manifest",
        "only the first uncached range lends the retained compact sequence",
    )
    require(
        "borrowed_delta_manifests" in serve
        and "begin_sync_replica_reconciliation_response_frame_assembly_or_throw"
            in serve
        and "direct_frame_manifest_materialization_bytes" in service_h
        and "direct.borrowed_delta_manifest_count" in serve
        and "direct.borrowed_delta_manifest_chunks" in serve,
        "shipping_service_threads_borrowed_views_and_zero_copy_telemetry",
        "the production path exposes the removed materialization boundary",
    )
    require(
        "struct DeltaManifestView final" in protocol_c
        and "from_owned" in protocol_c
        and "from_borrowed" in protocol_c
        and "chunk_size_bytes" in protocol_c
        and "chunk_sha256" in protocol_c,
        "owned_and_borrowed_manifests_share_one_private_read_view",
        "the protocol does not grow a second serializer or validator",
    )
    require(
        "carries both owning and borrowed complete manifests" in protocol_c
        and "borrowed complete manifest changed payload extent" in protocol_c,
        "double_authority_and_extent_drift_fail_closed",
        "a borrower cannot silently override an owning manifest or payload size",
    )
    require(
        "validate_delta_manifest_view_or_throw" in protocol_c
        and "does not bind the exact payload extent" in protocol_c
        and "uses noncanonical content-defined parameters" in protocol_c
        and "chunk extents do not cover the payload" in protocol_c,
        "borrowed_sequence_receives_complete_canonical_validation",
        "cumulative records do not bypass the released manifest invariants",
    )
    require(
        "delta_manifest_digest_for_view_or_throw" in protocol_c
        and "manifest.chunk_size_bytes(index)" in protocol_c
        and "manifest.chunk_sha256(index)" in protocol_c,
        "semantic_manifest_digest_reads_the_shared_view",
        "borrowed and owned records bind the same content-defined digest",
    )
    require(
        "response_body_metrics_impl_or_throw" in protocol_c
        and "append_response_body_impl_or_throw" in protocol_c
        and "DeltaManifestAt" in protocol_c
        and "complete_manifest.chunk_count()" in protocol_c,
        "metrics_and_serialization_share_the_manifest_provider",
        "frame reservation and emission cannot disagree about borrowed cardinality",
    )
    require(
        "validate_sync_replica_reconciliation_response_impl_or_throw" in protocol_c
        and "std::optional<DeltaManifestView> complete_manifest" in protocol_c
        and "validate_payload_range_against_delta_manifest_or_throw" in protocol_c,
        "final_response_validation_retains_manifest_group_semantics",
        "later ranges are checked against the exact first-range borrowed manifest",
    )
    require(
        "validate_sync_replica_reconciliation_response_for_request_impl_or_throw"
            in protocol_c
        and "omitted the complete content-defined manifest" in protocol_c
        and "repeated the complete content-defined manifest" in protocol_c,
        "request_bound_first_range_contract_uses_the_shared_view",
        "cache references and first-range publication remain fail closed",
    )
    require(
        "borrowed_delta_manifests.size()" in assembly
        and "borrowed_delta_manifests.empty()" in assembly
        and "payload count does not match its source ranges and borrowed manifests"
            in assembly
        and "state->frame.reserve" in assembly
        and "state->borrowed_delta_manifests" in assembly,
        "assembly_binds_present_view_cardinality_before_one_exact_frame_reservation",
        "an empty sidecar means no borrows; every present sidecar remains exact-cardinality",
    )
    require(
        "direct frame validation" in finish
        and "body_digest_or_throw" in finish
        and "kResponseStructuralDigestDomain" in finish
        and "std::copy(" in finish
        and "borrowed_delta_manifest_count" in finish,
        "finish_revalidates_and_seals_before_borrow_release",
        "the canonical structural digest is written before state and spans die",
    )
    require(
        "borrowed_delta_manifest_at_or_none_or_throw(" in protocol_c
        and "if (manifests.empty()) return none;" in protocol_c
        and "std::move(payload_byte_counts), {}, limits" in protocol_c
        and "allocation-cold compatibility path" in protocol_h,
        "legacy_direct_assembly_uses_an_allocation_cold_empty_sidecar",
        "ordinary owning callers preserve released behavior without one null optional per payload",
    )
    require(
        "kSyncReplicaMaximumPayloadExtentBytes" in compact_test
        and "kSyncReplicaReconciliationMaximumContentDefinedChunks" in compact_test
        and "kLargeAllocationThreshold = 256U * 1024U" in compact_test,
        "runtime_oracle_uses_the_hard_4_tib_8192_chunk_shape",
        "the removed copy is measured at the actual product frontier",
    )
    require(
        "borrowed_allocations.count == 1U" in compact_test
        and "borrowed_allocations.largest_request >= 640U * 1024U" in compact_test
        and "borrowed_delta_manifest_chunks" in compact_test,
        "runtime_oracle_requires_one_large_borrowed_path_allocation",
        "only the final response frame may cross the 256 KiB observation threshold",
    )
    require(
        "owned_allocations.count == 2U" in compact_test
        and "borrowed_allocations.requested_bytes" in compact_test
        and "wire.chunks.size()" in compact_test
        and "sizeof(SyncReplicaReconciliationDeltaChunk)" in compact_test,
        "runtime_oracle_measures_the_exact_327680_byte_baseline_difference",
        "the comparison is allocation arithmetic, not prose-only estimation",
    )
    require(
        "owned.frame == borrowed.frame" in compact_test
        and "decode_sync_replica_reconciliation_response_or_throw" in compact_test
        and "wire.chunks" in compact_test,
        "runtime_oracle_proves_wire_equality_and_decode_completeness",
        "generation-9 bytes remain exact despite different in-process ownership",
    )
    require(
        "explicit_allocations.count == legacy_allocations.count + 1U"
            in compact_test
        and "sizeof(OptionalBorrowedManifest)" in compact_test
        and "legacy.frame == explicit_result.frame" in compact_test,
        "runtime_oracle_proves_the_legacy_sidecar_is_allocation_cold",
        "the empty compatibility sidecar removes exactly one absent-optional vector allocation",
    )
    require(
        all(token in compact_test for token in (
            "both owning and borrowed complete manifests",
            "changed payload extent",
            "parameters average chunk size",
            "invalid chunk record",
        )),
        "runtime_oracle_rejects_malformed_or_ambiguous_borrowed_authority",
        "borrowed framing is fail closed at the executable boundary",
    )
    require(
        "direct_frame_borrowed_manifest_count == 1U" in service_test
        and "direct_frame_manifest_materialization_bytes == 0U" in service_test
        and "!first_direct.response.payloads[0].delta_manifest.has_value()"
            in service_test
        and "decode_sync_replica_reconciliation_response_or_throw" in service_test
        and "expected_borrowed_manifest_count" in service_c
        and "expected_borrowed_manifest_chunks" in service_c
        and "payload.delta_manifest.has_value()" in service_c,
        "shipping_service_runtime_selects_and_reproofs_the_borrowed_path",
        "the production owner avoids materialization and rejects retained secondary authority",
    )
    require(
        "direct_frame_borrowed_manifest_count == 0U" in memory_test
        and "direct_frame_manifest_materialization_bytes == 0U" in memory_test
        and "direct_allocations.count == 1U" in memory_test,
        "whole_payload_direct_frame_retains_its_one_owner_boundary",
        "adding borrowed-manifest telemetry does not recreate payload staging",
    )
    require(
        "anonsync_sync_replica_borrowed_manifest_frame_source_audit" in cmake
        and "tools/audit_sync_replica_borrowed_manifest_frame.py" in cmake,
        "focused_audit_is_registered",
        "the source-shape fence participates in the complete registry",
    )
    require(
        "BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md" in verifier
        and "REVISION_NOTES_rev1014.md" in verifier
        and "audit_sync_replica_borrowed_manifest_frame.py" in verifier
        and "rev1014_borrowed_manifest" in structural,
        "release_and_structural_policy_bind_rev1014_surfaces",
        "the archive cannot omit the implementation, runtime proof, or design boundary",
    )
    prose = "\n".join((design, notes, readme, bootstrap))
    require(
        all(token in prose for token in (
            "327,680", "8,192", "4 TiB", "generation 9", "byte-identical",
            "one large allocation", "O(chunk count)", "131,072", "32 MiB",
            "1 GiB", "RSS", "global", "multi-share", "rename/move",
            "directories", "conflict", "selective-sync", "ENOSPC", "Android",
            "Tor", "I2P",
        )),
        "benefit_compatibility_and_product_nonclaims_are_explicit",
        "one removed copy is not overstated as solved multi-terabyte product memory",
    )
    require(
        all(token not in prose for token in (
            "VALIDATION_PENDING_REV1014",
            "ARCHIVE_PENDING_REV1014",
            "CODENAME_PENDING_REV1014",
        )),
        "final_validation_and_release_cutpoint_are_sealed",
        "the source audit remains deliberately red until exact publication facts replace placeholders",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(encoding="utf-8")
        and "Source spelling is not semantic proof" in Path(__file__).read_text(encoding="utf-8"),
        "lexical_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
