#!/usr/bin/env python3
"""Lexical hygiene audit for rev1012 compact source-manifest caching.

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
    Path("COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md"),
    Path("REVISION_NOTES_rev1012.md"),
    Path("src/sync_replica_content_defined_chunker.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_compact_manifest.hpp"),
    Path("src/sync_replica_reconciliation_compact_manifest.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_reconciliation_compact_manifest_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tools/audit_sync_replica_compact_source_manifest_cache.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def block(text: str, start_token: str, end_token: str) -> str:
    start = text.find(start_token)
    if start < 0:
        return ""
    end = text.find(end_token, start + len(start_token))
    if end < 0:
        return ""
    return text[start:end]


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


def normalized(text: str) -> str:
    return " ".join(text.split())


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-source-manifest-cache-compaction-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove allocation counts, ABI layout, "
            "wire compatibility, rooted source authority, whole-process RSS, "
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
    bootstrap_path = next(
        (path for path in bootstrap_candidates if path.is_file()), None
    )
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
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    header = text["src/sync_replica_reconciliation_compact_manifest.hpp"]
    implementation = text["src/sync_replica_reconciliation_compact_manifest.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service = text["src/sync_replica_reconciliation_service.cpp"]
    chunker = text["src/sync_replica_content_defined_chunker.cpp"]
    runtime = text["tests/sync_replica_reconciliation_compact_manifest_test.cpp"]
    service_runtime = text["tests/sync_replica_reconciliation_service_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    docs = (
        text["README.md"] + "\n"
        + text["COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md"]
        + "\n" + text["REVISION_NOTES_rev1012.md"] + "\n" + bootstrap
    )

    compact_chunk = block(
        header,
        "struct SyncReplicaReconciliationCompactManifestChunk final",
        "// Process-local exact source-manifest cache",
    )
    compact_aliases_cumulative = (
        "using SyncReplicaReconciliationCompactManifestChunk =" in header
        and "SyncReplicaReconciliationCumulativeDeltaChunk" in header
    )
    cumulative_chunk = block(
        protocol_h,
        "struct SyncReplicaReconciliationCumulativeDeltaChunk final",
        "// Borrowed complete manifest used only while one response frame is assembled.",
    )
    retained_chunk = cumulative_chunk if compact_aliases_cumulative else compact_chunk
    require(
        "std::uint64_t end_offset_bytes" in retained_chunk
        and "Sha256DigestValue sha256" in retained_chunk
        and "std::string" not in retained_chunk,
        "compact_chunk_is_fixed_width_cumulative_binary",
        "the retained chunk carries one cumulative extent and no heap digest",
    )
    require(
        "sizeof(SyncReplicaReconciliationCompactManifestChunk) == 40U" in header
        and '#include "sync_replica_reconciliation_protocol.hpp"' in header,
        "compact_chunk_layout_has_compile_time_frontiers",
        "record and digest width cannot drift silently",
    )
    compact_class = block(
        header,
        "class SyncReplicaReconciliationCompactManifest final",
        "}  // namespace anonsync",
    )
    require(
        "std::vector<SyncReplicaReconciliationCompactManifestChunk> chunks_" in compact_class
        and "std::vector<std::uint64_t>" not in compact_class
        and "SyncReplicaReconciliationDeltaManifest manifest_" not in compact_class,
        "compact_cache_owns_one_chunk_vector_only",
        "the completed source cache does not retain a second offset or wire container",
    )
    conversion = body(implementation, "from_manifest_or_throw(")
    require(
        "compact.chunks_.reserve(manifest.chunks.size())" in conversion
        and "covered += chunk.size_bytes" in conversion
        and "compact.chunks_.push_back({covered, chunk.sha256})" in conversion
        and "covered != total_size_bytes" in conversion,
        "conversion_validates_and_builds_one_exact_cumulative_sequence",
        "only canonical bounded exact-coverage manifests become cache state",
    )
    require(
        "std::upper_bound(" in implementation
        and "offset < chunk.end_offset_bytes" in implementation,
        "lookup_uses_exclusive_cumulative_end_offsets",
        "exact chunk boundaries select the following record without another index",
    )
    require(
        "manifest.chunks.reserve(chunks_.size())" in implementation
        and "chunk.sha256" in implementation
        and "digest_hex(" not in implementation
        and "preceding != total_size_bytes_" in implementation,
        "wire_materialization_rebuilds_exact_protocol_manifest_on_demand",
        "wire strings are constructed only at an explicit publication boundary",
    )

    cached_struct = block(
        service_h,
        "struct CachedSourceContentDefinedManifest final",
        "struct SourceContentDefinedProjection final",
    )
    require(
        "SyncReplicaReconciliationCompactManifest manifest" in cached_struct
        and "chunk_offsets" not in cached_struct
        and "SyncReplicaReconciliationDeltaManifest" not in cached_struct,
        "service_cache_retains_compact_manifest_without_offset_vector",
        "the shipping owner does not preserve rev1011's duplicate cache shape",
    )
    require(
        service.count(
            "SyncReplicaReconciliationCompactManifest::from_manifest_or_throw("
        ) >= 2
        and "restored compact manifest" in service
        and 'operation_label + " compact manifest"' in service,
        "restart_and_fresh_completion_share_compact_cache_boundary",
        "both completed-manifest entry paths shed protocol strings after validation",
    )
    require(
        "source_manifest.manifest.chunk_index_for_offset_or_throw" in service
        and ".chunk_offset_bytes_or_throw(" in service
        and ".chunk_end_offset_bytes_or_throw(" in service,
        "shipping_range_selection_uses_compact_cumulative_index",
        "ranged transfer no longer consults a separately retained offset vector",
    )
    require(
        service.count("chunk_index, label_") >= 3
        and "offset, label_" in service
        and 'label_ + " source compact manifest' not in service
        and "lookup.count == 0U" in runtime,
        "shipping_numeric_lookup_is_allocation_cold",
        "valid range selection reuses the retained owner label and allocates no diagnostics",
    )
    publication = block(
        service,
        "SyncReplicaReconciliationPayload metadata(",
        'label_ + " ranged payload window ranges");',
    )
    require(
        "source_manifest.manifest.borrow_for_direct_frame()" in publication
        and "source_manifest.manifest_digest" in publication
        and "std::move(borrowed_delta_manifest)" in publication
        and "source_manifest.manifest.materialize_or_throw(" not in service,
        "cache_cold_publication_lends_while_references_stay_constant_size",
        "generation-9 wire compatibility is preserved without permanent or transient wire storage",
    )
    require(
        "source_content_defined_manifest_->manifest.parameters()" in service,
        "cache_identity_reproof_uses_compact_parameters",
        "digest, extent, parameters, and inode observation still gate reuse",
    )

    parameter_validator = body(
        chunker,
        "validate_sync_replica_content_defined_chunking_parameters_or_throw(",
    )
    require(
        "const auto invalid = [label_view]" in parameter_validator
        and "const std::string label(label_view);" not in parameter_validator,
        "valid_parameter_validation_builds_diagnostics_only_on_error",
        "successful compact construction is not charged one unrelated label allocation",
    )

    require(
        all(token in runtime for token in (
            "wire_cache.count == 2U",
            "expected_wire_vector_bytes",
            "expected_offset_bytes",
            "fixed-width wire manifest plus separate offsets",
        )),
        "runtime_measures_current_wire_plus_offset_baseline",
        "the retained-memory comparison is executable rather than prose-only",
    )
    require(
        all(token in runtime for token in (
            "construction.count == 1U",
            "expected_compact_bytes",
            "retained_chunk_capacity_bytes() == expected_compact_bytes",
            "one exact vector allocation",
        )),
        "runtime_proves_one_327680_byte_compact_allocation",
        "maximum cache construction has no per-digest or offset allocation",
    )
    require(
        "copy.count == 1U" in runtime
        and "maximum compact manifest copy was not one exact vector allocation" in runtime,
        "runtime_proves_one_allocation_compact_copy",
        "copy cost remains one bounded contiguous request",
    )
    require(
        all(token in runtime for token in (
            "materialization.count == 1U",
            "materialization.requested_bytes == expected_wire_vector_bytes",
            "materialized == wire",
        )),
        "runtime_binds_transient_wire_cost_and_exact_round_trip",
        "the memory reduction cannot change released generation-9 manifest semantics",
    )
    require(
        all(token in runtime for token in (
            "chunk_index_for_offset_or_throw(kChunkBytes)",
            "chunk_offset_bytes_or_throw(1U)",
            "terminal compact offset was accepted",
            "malformed fixed-width digest assignment was accepted",
            "incomplete compact manifest was accepted",
        )),
        "runtime_covers_boundaries_and_fail_closed_inputs",
        "the cumulative representation is tested beyond the happy path",
    )
    require(
        "content_defined_manifest_publications() == 3U" in service_runtime
        and "cached_delta_manifest_digest" in service_runtime
        and "delta_manifest.has_value()" in service_runtime,
        "retained_service_runtime_still_covers_publication_and_digest_reuse",
        "the compact cache remains integrated with ordinary end-to-end protocol behavior",
    )

    require(
        all(token in cmake for token in (
            "anonsync_sync_replica_reconciliation_compact_manifest STATIC",
            "anonsync_sync_replica_reconciliation_compact_manifest_test",
            "anonsync_product_lane",
            "ANONSYNC_SANITIZER_COMPILE_TARGETS",
        )),
        "compact_library_and_runtime_join_product_and_sanitizer_graphs",
        "the new boundary cannot compile only in an isolated developer target",
    )
    require(
        "anonsync_sync_replica_compact_source_manifest_cache_source_audit" in cmake,
        "focused_rev1012_audit_is_registered",
        "the representation boundary participates in CTest",
    )
    require(
        "COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md" in verifier
        and "REVISION_NOTES_rev1012.md" in verifier
        and "audit_sync_replica_compact_source_manifest_cache.py" in verifier,
        "release_verifier_requires_complete_rev1012_slice",
        "the package cannot omit implementation rationale or focused audit",
    )
    require(
        "rev1012_compact_source_manifest" in structural,
        "structural_audit_binds_rev1012_cache_boundary",
        "the cumulative authority inventory evolves with the memory refactor",
    )

    prose = normalized(docs)
    require(
        all(token in prose for token in (
            "8,194", "925,704", "327,680", "598,024",
            "8,193", "860,160", "40-byte", "generation 9",
        )),
        "documentation_records_exact_retained_and_transient_allocator_shapes",
        "the release states a measured bounded benefit rather than merely optimized",
    )
    require(
        all(token in prose for token in (
            "131,072", "32 MiB", "1 GiB", "4 TiB", "O(chunk count)",
            "RSS", "page-cache", "global", "Android", "ENOSPC",
            "rename/move", "Tor", "I2P",
        )),
        "documentation_keeps_scale_and_product_nonclaims_explicit",
        "one cache compaction is not overstated as solved multi-terabyte product memory",
    )
    require(
        all(token not in docs for token in (
            "VALIDATION_PENDING_REV1012",
            "ARCHIVE_PENDING_REV1012",
            "CODENAME_PENDING_REV1012",
        )),
        "final_release_placeholders_are_sealed",
        "the focused audit cannot pass before exact validation and archive identity exist",
    )
    source_self = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in source_self
        and "not semantic proof" in source_self,
        "lexical_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
