#!/usr/bin/env python3
"""Lexical audit for rev0995 retained source chunk index and range-scale proof.

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
    Path("SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md"),
    Path("REVISION_NOTES_rev0995.md"),
    Path("src/anonsync_replica.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_replica_source_chunk_index.py"),
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
        "format": "anonsync-source-chunk-index-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove multi-terabyte throughput, memory "
            "use, correctness, crash safety, privacy, or package identity"
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
    design = text["SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md"]
    notes = text["REVISION_NOTES_rev0995.md"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_source_chunk_index_source_audit" in cmake
        and "tools/audit_sync_replica_source_chunk_index.py" in cmake,
        "focused_audit_registered",
        "the source chunk-index audit is in the ordinary test registry",
    )
    source_cache_start = service_h.find(
        "struct CachedSourceContentDefinedManifest final")
    source_cache_end = service_h.find(
        "struct SourceContentDefinedProjection final", source_cache_start)
    source_cache = (
        service_h[source_cache_start:source_cache_end]
        if source_cache_start >= 0 and source_cache_end > source_cache_start
        else ""
    )
    require(
        bool(source_cache)
        and "SyncPosixRegularFileSnapshotMetadata source_metadata" in source_cache
        and "SyncReplicaReconciliationCompactManifest manifest" in source_cache
        and "SyncReplicaReconciliationDeltaManifest manifest" not in source_cache
        and "std::vector<std::uint64_t> chunk_offsets" not in source_cache,
        "source_manifest_and_index_are_one_cohesive_cache",
        "source identity, inode observation, digest, cumulative extents, and fixed digests share one bounded lifetime",
    )
    require(
        "content_defined_manifest_source_metadata_" not in service_h + service_c
        and "content_defined_manifest_digest_" not in service_h + service_c
        and "content_defined_manifest_chunk_offsets_" not in service_h + service_c,
        "parallel_source_cache_members_removed",
        "source cache reset cannot leave parallel optional/scalar state behind",
    )
    require(
        "source_content_defined_manifest_.reset();" in service_c
        and "const bool projection_matches =" in service_c
        and "if (!projection_matches)" in service_c
        and "source_content_defined_projection_ =" in service_c,
        "source_identity_change_resets_cache_and_projection",
        "exact payload or inode drift discards the completed cache and starts one cohesive projection",
    )
    require(
        service_c.count(
            "SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(") >= 2
        and "std::move(compact_manifest)" in service_c
        and "source_manifest.manifest.chunk_index_for_offset_or_throw(" in service_c
        and ".chunk_offset_bytes_or_throw(" in service_c
        and ".chunk_end_offset_bytes_or_throw(" in service_c
        and "source_manifest.chunk_offsets" not in service_c,
        "source_compact_manifest_is_built_then_retained",
        "ranged lookup reads one retained cumulative fixed-digest vector rather than rebuilding a second offset vector",
    )
    stale_check = service_c.find("*request.cached_delta_manifest_digest !=")
    lookup = service_c.find("content-defined chunk-index lookup", stale_check)
    copy_range = service_c.find("copy_range_or_throw", stale_check)
    require(
        stale_check >= 0 and lookup > stale_check and copy_range > stale_check,
        "stale_manifest_reference_fails_before_range_copy",
        "an unusable continuation cannot force an avoidable payload range read after current cache reproof",
    )
    require(
        all(token in service_h for token in (
            "content_defined_chunk_index_builds",
            "content_defined_chunk_index_reuses",
            "content_defined_chunk_index_lookups",
        )),
        "source_index_counters_exist",
        "build, reuse, and lookup are independently observable",
    )
    require(
        all(token in tls_h + tls_c for token in (
            "content_defined_chunk_index_builds",
            "content_defined_chunk_index_reuses",
            "content_defined_chunk_index_lookups",
        )),
        "source_index_counters_cross_tls_boundary",
        "transport results preserve the source-session scale evidence",
    )
    require(
        all(token in replica_cli for token in (
            "reconciliation_content_defined_chunk_index_builds",
            "reconciliation_content_defined_chunk_index_reuses",
            "reconciliation_content_defined_chunk_index_lookups",
        )),
        "source_index_counters_reach_operator_json",
        "the shipping diagnostic surface exposes the removed multiplier",
    )
    require(
        "content_defined_chunk_index_builds() == 1U" in service_test
        and "content_defined_chunk_index_reuses() == 3U" in service_test
        and "content_defined_chunk_index_lookups() == 4U" in service_test
        and "stale receiver manifest reference consumed source index reuse or lookup work" in service_test,
        "service_regressions_bind_one_build_many_lookups",
        "cold publication and grouped continuation windows exercise the retained source index",
    )
    require(
        "content_defined_chunk_index_builds == 1U" in tls_test
        and "content_defined_chunk_index_reuses == 0U" in tls_test
        and "content_defined_chunk_index_lookups == 1U" in tls_test
        and "ranged_payload_windows == 1U" in tls_test
        and "ranged_payload_ranges == 2U" in tls_test
        and "ranged_payload_bytes == 8U" in tls_test,
        "tls_regression_binds_index_accounting",
        "one authenticated grouped window proves one source-index lookup covers two contiguous ranges",
    )
    require(
        "8'589'934'592ULL" in protocol_test
        and "68'727'865'344ULL" in protocol_test
        and "1'048'576U" in protocol_test,
        "maximum_extent_shape_quantifies_removed_multiplier",
        "the 4 TiB shape records exact range, addition, and vector-byte counts",
    )
    require(
        "64.0078125 GiB" in design
        and "one-range-per-request/response" in design
        and "bounded multi-range or byte-window frame" in design,
        "design_records_scale_result_and_next_bottleneck",
        "the release does not hide the remaining one-range-per-turn frontier",
    )
    require(
        "SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md" in verifier
        and "REVISION_NOTES_rev0995.md" in verifier
        and "tools/audit_sync_replica_source_chunk_index.py" in verifier,
        "release_verifier_binds_rev0995_slice",
        "the archive cannot omit implementation, tests, design, notes, or focused audit",
    )
    require(
        "rev0995" in readme.casefold() and "rev0995" in bootstrap.casefold()
        and "rev0995" in design.casefold() and "rev0995" in notes.casefold(),
        "visible_release_surfaces_name_rev0995",
        "README, runbook, design, and revision notes agree on the current revision",
    )
    require(
        all(token not in readme + bootstrap + design + notes for token in (
            "VALIDATION_PENDING_REV0995",
            "ARCHIVE_PENDING_REV0995",
            "CODENAME_PENDING_REV0995",
        )),
        "final_validation_and_archive_are_sealed",
        "rev0995 cannot pass its focused audit until validation and archive identity are final",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
