#!/usr/bin/env python3
"""Lexical audit for bounded content-defined manifest references.

This inventories source shape only. Runtime, sanitizer, reconstruction, memory,
cryptographic, crash-safety, and package evidence remain load-bearing.
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
    Path("MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md"),
    Path("REVISION_NOTES_rev0992.md"),
    Path("CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"),
    Path("REVISION_NOTES_rev0994.md"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_replica_content_defined_delta.py"),
    Path("tools/audit_sync_replica_manifest_reference.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)

@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-manifest-reference-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SHA-256 security, boundary quality, "
            "insertion reuse, crash safety, liveness, memory use, or wire behavior"
        ),
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
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls = text["src/sync_replica_reconciliation_tls_exchange.hpp"] + text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    cli = text["src/anonsync_replica.cpp"] + text["src/anonsync_sync.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    focused = text["tools/audit_sync_replica_content_defined_delta.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    rev0994_design = text["CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md"]
    rev0994_notes = text["REVISION_NOTES_rev0994.md"]

    require(
        "anonsync_sync_replica_manifest_reference_source_audit" in cmake
        and "tools/audit_sync_replica_manifest_reference.py" in cmake,
        "audit_registered",
        "the current manifest-reference audit remains in the ordinary CTest registry",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "reconciliation-request-frame-v9" in protocol_c
        and "reconciliation-response-frame-v9" in protocol_c,
        "wire_generation_is_seven",
        "content-defined framing cannot decode as the superseded fixed-boundary protocol",
    )
    require(
        "cached_delta_manifest_digest" in protocol_h
        and "request cached content-defined manifest has no payload continuation" in protocol_c,
        "cache_claim_requires_continuation",
        "a receiver cannot advertise process-local manifest authority outside one payload continuation",
    )
    require(
        "sync_replica_reconciliation_delta_manifest_digest_or_throw" in protocol_h
        and "kDeltaManifestDigestDomain" in protocol_c
        and "content-defined-manifest-v1" in protocol_c,
        "manifest_digest_has_one_domain_separated_definition",
        "the constant-size reference names one canonical complete variable-chunk manifest",
    )
    require(
        all(token in protocol_h for token in (
            "SyncReplicaReconciliationDeltaManifest",
            "delta_manifest_digest",
            "delta_manifest",
            "delta_chunk_offset_bytes",
            "delta_chunk_size_bytes",
        ))
        and "ranged payload lacks a valid content-defined manifest digest" in protocol_c,
        "every_ranged_payload_carries_manifest_identity",
        "reference-only ranges retain exact target chunk geometry authority",
    )
    require(
        "cached_delta_manifest_digest.has_value()" in protocol_c
        and "delta_manifest.has_value()" in protocol_c
        and "omitted the complete content-defined manifest from the first range without receiver cache authority" in protocol_c,
        "publication_and_reference_are_distinct",
        "cache-cold requests require a full manifest while valid continuations may use a digest reference",
    )
    require(
        "CachedTargetContentDefinedManifest" in service_h
        and all(token in service_h for token in (
            "operation_id", "content_sha256", "total_size_bytes",
            "manifest_digest", "SyncReplicaReconciliationDeltaManifest manifest",
            "std::vector<std::uint64_t> chunk_offsets",
        )),
        "target_cache_is_one_exact_identity_record",
        "operation, payload, manifest, and cumulative offsets cannot drift as parallel optional state",
    )
    require(
        "CachedPredecessorContentDefinedManifest" in service_h
        and "std::vector<std::size_t> digest_order" in service_h
        and service_h.count("std::vector<std::uint64_t> chunk_offsets") >= 2,
        "predecessor_cache_keeps_sorted_digest_and_offset_indices",
        "at most 8,192 indices and offsets are built once per selected predecessor",
    )
    require(
        "request.cached_delta_manifest_digest" in service_c
        and "source_manifest.manifest_digest" in service_c
        and "requested content-defined manifest cache does not match current source bytes" in service_c,
        "source_reproves_receiver_cache_claim",
        "receiver-provided digest text never becomes source payload authority",
    )
    require(
        "ranged payload references a content-defined manifest absent from this receiver process" in service_c
        and "delta_target_manifest_.has_value()" in service_c,
        "receiver_reference_requires_actual_process_cache",
        "crafted wire state cannot invent a retained manifest",
    )
    require(
        "ranged payload bytes do not match the retained content-defined manifest reference" in service_c
        and ".equals_lowercase_hex(wire.chunk_sha256)" in service_c
        and "!retained.manifest.chunks[chunk_index].sha256" in service_c,
        "complete_referenced_chunk_is_checked_before_staging",
        "wire bytes plus a matching range digest cannot substitute another target chunk",
    )
    require(
        "extend_content_defined_projection_index_or_throw" in service_c
        and "std::lower_bound" in service_c
        and "projected.digest_order.insert" in service_c
        and "projected.chunk_offsets.push_back" in service_c
        and "delta_predecessor_projection_" in service_c
        and "retained.digest_order = std::move(projected.digest_order)" in service_c
        and "delta_predecessor_manifest_->digest_order" in service_c
        and "result.delta_predecessor_index_builds" in service_c
        and "result.delta_predecessor_index_reuses" in service_c,
        "predecessor_digest_index_is_built_incrementally_then_reused",
        "partial and complete candidate lookup share one canonical sorted index boundary",
    )
    require(
        all(token in service_h for token in (
            "content_defined_manifest_publications",
            "content_defined_manifest_references",
            "target_content_defined_manifest_publications",
            "target_content_defined_manifest_reuses",
            "delta_predecessor_index_builds",
            "delta_predecessor_index_reuses",
        )),
        "source_receiver_and_index_work_are_counted_separately",
        "operator evidence distinguishes bootstrap, reference, target-cache, and local-index work",
    )
    counters = (
        "content_defined_manifest_publications",
        "content_defined_manifest_references",
        "target_content_defined_manifest_publications",
        "target_content_defined_manifest_reuses",
        "delta_predecessor_index_builds",
        "delta_predecessor_index_reuses",
    )
    require(all(token in tls for token in counters), "tls_preserves_manifest_accounting", "framed transport retains focused counters")
    require(all(token in cli for token in counters), "cli_exposes_manifest_accounting", "shipping JSON retains delta bootstrap and cache evidence")
    require(
        "8,192-chunk manifest frontier" in protocol_test
        and "maximum manifest reference" in protocol_test
        and "more than 256 GiB" in protocol_test,
        "maximum_shape_tests_constant_size_reference",
        "the 4 TiB frontier is represented without allocating a 4 TiB payload",
    )
    require(
        "test_content_defined_delta_reuses_shifted_predecessor_chunks" in service_test
        and "target_content_defined_manifest_publications == 1U" in service_test
        and "target_content_defined_manifest_reuses == 1U" in service_test
        and "delta_predecessor_index_builds" in service_test
        and "delta_predecessor_index_reuses" in service_test,
        "service_proves_bootstrap_reference_and_shifted_reuse",
        "the live regression exercises both bounded caches and insertion-resilient lookup",
    )
    require(
        "full chunk digest disagrees" in service_test
        and "receiver cache states" in service_test,
        "restart_or_forgery_path_requires_bootstrap",
        "process-local acceleration is not promoted into durable admission authority",
    )
    require(
        "content_defined_manifest_publications == 1U" in tls_test
        and "content_defined_manifest_references == 1U" in tls_test
        and "content_defined_manifest_scans == 0U" in tls_test
        and "content_defined_manifest_reuses == 1U" in tls_test
        and "content_defined_chunk_index_builds == 0U" in tls_test
        and "content_defined_chunk_index_reuses == 1U" in tls_test
        and "cache-cold TLS replay did not restore the complete source manifest without hashing" in tls_test,
        "tls_observes_full_then_reference_transition",
        "the bounded authenticated exchange preserves full-then-reference framing while restart restores source manifest and index state without hashing",
    )
    require(
        "anonsync-content-defined-delta-source-audit-v1" in focused
        and "kSyncReplicaReconciliationProtocolVersion = 9U" in focused,
        "content_defined_audit_owns_current_generation",
        "the rev0994 focused assurance surface composes with this historical manifest-reference audit",
    )
    require(
        "CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md" in verifier
        and "tools/audit_sync_replica_manifest_reference.py" in verifier
        and "tools/audit_sync_replica_content_defined_delta.py" in verifier,
        "release_verifier_binds_current_authority_chain",
        "the package cannot omit framing, runtime proof, design record, or audits",
    )
    require(
        "MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md" in structural
        and "CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md" in structural,
        "structural_audit_composes_history_and_current_delta",
        "the earlier bounded reference remains part of the current insertion-resilient path",
    )
    require(
        "## Rev0994:" in readme and "REV0994 RELEASE CUTPOINT" in bootstrap,
        "visible_surfaces_name_current_revision",
        "README and restart page bind the same product move",
    )
    visible = "\n".join((readme, rev0994_design, rev0994_notes, bootstrap))
    require(
        "VALIDATION_PENDING_REV0994" not in visible
        and "ARCHIVE_PENDING_REV0994" not in visible,
        "final_placeholders_are_sealed",
        "manifest-reference assurance cannot pass before exact validation and archive identity are recorded",
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
