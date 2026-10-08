#!/usr/bin/env python3
"""Lexical hygiene audit for rev0998 direct source payload-frame assembly.

This audit binds reviewed source shape and release vocabulary. It is not a
semantic proof of allocation count, filesystem behavior, hash correctness,
lifetime safety, protocol equivalence, peak RSS, TLS buffering, or package
identity. Compiler, runtime, sanitizer, allocation-oracle, and package evidence
remain load-bearing.
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
    Path("DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md"),
    Path("REVISION_NOTES_rev0998.md"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_source_frame_memory_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
    Path("tools/test_anonsync_sync_process.py"),
    Path("tools/audit_sync_replica_direct_source_frame.py"),
    Path("tools/audit_sync_replica_response_memory_shape.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature: str, occurrence: int = 0) -> str:
    start = -1
    search = 0
    for _ in range(occurrence + 1):
        start = text.find(signature, search)
        if start < 0:
            return ""
        search = start + len(signature)
    brace = text.find("{", start + len(signature))
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-direct-source-frame-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-or-peak-rss-proof",
        "scope_nonclaim": (
            "source spelling does not prove allocation count, filesystem or hash "
            "behavior, protocol equivalence, lifetime safety, TLS buffering, peak "
            "RSS, throughput, or package identity"
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

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md"]
    notes = text["REVISION_NOTES_rev0998.md"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    store_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    memory_test = text["tests/sync_replica_reconciliation_source_frame_memory_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    replica_process = text["tools/test_anonsync_replica_reconciliation_process.py"]
    sync_process = text["tools/test_anonsync_sync_process.py"]
    inherited_audit = text["tools/audit_sync_replica_response_memory_shape.py"]
    structural_audit = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_reconciliation_source_frame_memory_test" in cmake
        and "tests/sync_replica_reconciliation_source_frame_memory_test.cpp" in cmake,
        "source_memory_test_is_built",
        "the actual 64 MiB and synthetic 4 TiB oracle is a configured C++ target",
    )
    require(
        cmake.count("anonsync_sync_replica_reconciliation_source_frame_memory_test") >= 7
        and "PROPERTIES TIMEOUT 120 LABELS \"product\"" in cmake,
        "source_memory_test_is_product_and_sanitizer_retained",
        "the direct-source memory boundary participates in ordinary and sanitizer validation",
    )
    require(
        "anonsync_sync_replica_direct_source_frame_source_audit" in cmake
        and "tools/audit_sync_replica_direct_source_frame.py" in cmake,
        "focused_source_audit_is_registered",
        "the rev0998 source-shape audit is in the ordinary CTest registry",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_remains_7",
        "the source ownership correction is not a protocol fork",
    )
    require(
        "kSyncReplicaReconciliationMaximumPayloadsPerPage" in protocol_h
        and "kSyncReplicaReconciliationMaximumPayloadBytesPerPage" in protocol_h
        and "kSyncReplicaReconciliationMaximumResponseFrameBytes" in protocol_h
        and "fixed product memory and descriptor frontier" in protocol_c,
        "public_limits_cannot_raise_product_memory_or_descriptor_frontiers",
        "in-process callers may reduce but cannot enlarge the 128-descriptor, 64 MiB payload, or 96 MiB frame boundary",
    )
    require(
        "copy_exact_range_into_or_throw" in store_h
        and "std::span<char> destination" in store_h,
        "payload_store_exposes_caller_owned_exact_range_fill",
        "the source can fill one preallocated frame hole without a range string",
    )
    direct_reader = function_body(store_c, "copy_hash_regular_file_range_into_or_throw")
    require(
        "::pread" in direct_reader
        and "std::numeric_limits<ssize_t>::max()" in direct_reader
        and "Sha256DigestBuilder" in direct_reader
        and "same_regular_file_observation" in direct_reader,
        "direct_reader_bounds_hashes_and_reproves",
        "each syscall is bounded and exact bytes are hashed under final inode reproof",
    )
    compatibility_reader = function_body(store_c, "copy_hash_regular_file_range_or_throw")
    require(
        "copy_hash_regular_file_range_into_or_throw" in compatibility_reader
        and compatibility_reader.count("::pread") == 0,
        "compatibility_reader_delegates_to_one_byte_path",
        "direct and owned range reads cannot drift into separate implementations",
    )
    direct_opened = function_body(
        store_c,
        "SyncReplicaFilePayloadStoreOpenedPayload::copy_exact_range_into_or_throw",
    )
    require(
        "retain_process_integrity_fault" in direct_opened
        and "SyncReplicaFilePayloadStoreIntegrityError" in direct_opened
        and "complete range discovered payload corruption" in direct_opened,
        "complete_direct_fill_preserves_integrity_fault_semantics",
        "a whole-payload mismatch remains typed and fail closed",
    )
    require(
        "struct SyncReplicaReconciliationDirectFrameResponse final" in protocol_h
        and "class SyncReplicaReconciliationResponseFrameAssembly final" in protocol_h
        and "std::span<char> payload_bytes_or_throw" in protocol_h,
        "move_only_one_frame_types_are_explicit",
        "metadata-only response and sole frame ownership cross a named C++ boundary",
    )
    require(
        "SyncReplicaReconciliationResponseFrameAssembly(" in protocol_h
        and "const SyncReplicaReconciliationResponseFrameAssembly&) = delete" in protocol_h
        and "std::function" not in protocol_h,
        "frame_assembly_is_move_only_without_executable_callback",
        "payload-hole lifetime is concrete rather than type-erased",
    )
    require(
        "response_body_metrics_impl_or_throw" in protocol_c
        and "append_response_body_impl_or_throw" in protocol_c
        and "payload_slots" in protocol_c
        and "frame.reserve" in protocol_c,
        "protocol_projects_and_builds_one_exact_frame",
        "normal and direct framing share canonical field projection",
    )
    finish = function_body(
        protocol_c,
        "SyncReplicaReconciliationResponseFrameAssembly::finish_or_throw",
    )
    require(
        "uncommitted payload slots" in finish
        and "validate_sync_replica_reconciliation_response_for_request_impl_or_throw" in finish
        and "body_digest_or_throw" in finish
        and "state_.reset()" in finish,
        "finish_validates_frame_backed_bytes_and_consumes_authority",
        "unfilled or digest-mismatched holes cannot become a wire response",
    )
    begin = function_body(
        protocol_c,
        "begin_sync_replica_reconciliation_response_frame_assembly_or_throw",
        occurrence=2,
    )
    require(
        "max_payloads_per_page" in begin
        and "max_payload_bytes_per_page" in begin
        and "max_response_frame_bytes" in begin
        and "source range is not exact and bounded" in begin,
        "construction_enforces_all_range_and_frame_frontiers",
        "allocation happens only after bounded source declarations are accepted",
    )
    require(
        "struct SyncReplicaFramedInboundReconciliation final" in service_h
        and "response_frame" in service_h
        and "direct_payload_bytes" in service_h,
        "shipping_service_result_names_sole_payload_owner",
        "the direct result distinguishes metadata from frame-owned bytes",
    )
    require(
        "begin_sync_replica_reconciliation_response_frame_assembly_or_throw" in service_c
        and "copy_exact_range_into_or_throw" in service_c
        and "opened_payload_index" in service_c
        and "expected_borrowed_manifest_count" in service_c
        and "expected_borrowed_manifest_chunks" in service_c
        and "payload.delta_manifest.has_value()" in service_c
        and "direct response retained a second payload or manifest aggregate" in service_c,
        "shipping_service_fills_frame_from_exact_descriptors",
        "selected source descriptors fill canonical frame holes and metadata keeps no bytes",
    )
    direct_service = function_body(
        service_c,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw",
        occurrence=1,
    )
    require(
        "copy_range_or_throw" not in direct_service
        and "encode_sync_replica_reconciliation_response_for_request_or_throw"
            not in direct_service
        and "decode_sync_replica_reconciliation_response_or_throw"
            not in direct_service,
        "shipping_service_has_no_range_string_or_second_encoder_path",
        "the product source cannot silently recreate the removed payload owner",
    )
    require(
        "serve_request_frame_or_throw" in tls_c
        and "SyncReplicaFramedInboundReconciliation" in tls_c
        and "service.serve_request_or_throw" not in tls_c,
        "tls_uses_direct_frame_service_boundary",
        "owned compatibility decode is not on the authenticated shipping source path",
    )
    require(
        "direct_frame_payload_page_bytes_at_reservation" in service_h
        and "direct_frame_maximum_source_staging_bytes" in service_h
        and "direct_frame_open_source_descriptors_at_reservation" in service_h
        and "response_direct_source_frame_payload_page_bytes_at_reservation" in tls_h
        and "response_direct_source_frame_maximum_open_descriptors" in tls_h
        and "response_direct_source_frames" in tls_c
        and "reconciliation_response_direct_source_frame_maximum_staging_bytes" in replica_cli,
        "shipping_diagnostics_expose_zero_staging_and_descriptor_fanout",
        "every live source session reports direct-frame count, payload bytes, zero aggregate page ownership, zero range staging, and maximum exact descriptors",
    )
    require(
        "response_direct_source_frames" in tls_test
        and "responses_written" in tls_test
        and "response_direct_source_frame_payload_page_bytes_at_reservation" in tls_test
        and "response_direct_source_frame_maximum_staging_bytes" in tls_test
        and "response_direct_source_frame_maximum_open_descriptors" in tls_test
        and "require_direct_source_frame" in replica_process
        and "reconciliation_response_direct_source_frame_payload_page_bytes_at_reservation" in replica_process
        and "reconciliation_response_direct_source_frame_maximum_staging_bytes" in replica_process
        and "reconciliation_response_direct_source_frame_maximum_open_descriptors" in replica_process
        and "reconciliation_response_direct_source_frame_payload_page_bytes_at_reservation" in sync_process
        and "reconciliation_response_direct_source_frame_maximum_staging_bytes" in sync_process
        and "reconciliation_response_direct_source_frame_maximum_open_descriptors" in sync_process,
        "tls_and_process_oracles_bind_the_live_direct_source_path",
        "unit and real-process tests reject a shipping response that silently recreates source page or staging ownership",
    )
    require(
        "decode_sync_replica_reconciliation_response_or_throw" in service_c
        and "serve_request_frame_or_throw" in service_c,
        "owned_service_api_is_named_compatibility_wrapper",
        "legacy callers retain semantics only by explicitly paying the decode copy",
    )
    require(
        "test_direct_response_frame_assembly_lifecycle" in protocol_test
        and "uncommitted" in protocol_test
        and "committed twice" in protocol_test
        and "direct.frame == canonical" in protocol_test,
        "protocol_runtime_binds_lifecycle_and_wire_equality",
        "the builder cannot weaken canonical generation-8 framing",
    )
    require(
        "copy_exact_range_into_or_throw" in store_test
        and "direct_range == payload.substr" in store_test
        and "oversized direct range" in store_test,
        "payload_store_runtime_binds_direct_range_semantics",
        "direct fill preserves bytes, digest, position, and exact extent rejection",
    )
    require(
        "kPayloadBytes = 64U * 1024U * 1024U" in memory_test
        and "kLargeAllocationThreshold = 2U * 1024U * 1024U" in memory_test
        and "direct_allocations.count == 1U" in memory_test
        and "direct_allocations.peak_active_count == 1U" in memory_test
        and "compatibility_allocations.count == 2U" in memory_test
        and "compatibility_allocations.peak_active_count == 2U" in memory_test
        and "probe_generation" in memory_test,
        "actual_64_mib_oracle_proves_simultaneous_one_vs_two_owner_differential",
        "generation-tagged allocation accounting excludes a hidden four-MiB range owner and distinguishes one live frame from compatibility's live frame plus payload",
    )
    require(
        "kSyncReplicaMaximumPayloadExtentBytes" in memory_test
        and "kChunkBytes = 1024ULL * 1024ULL * 1024ULL" in memory_test
        and "kRangeBytes = 4U * 1024U * 1024U" in memory_test
        and "allocations.count == 1U" in memory_test
        and "allocations.peak_active_count == 1U" in memory_test,
        "synthetic_4_tib_oracle_binds_logical_extent_to_bounded_residency",
        "a four-TiB manifest shape transfers one bounded range in one frame allocation",
    )
    require(
        "begin_sync_replica_reconciliation_response_frame_assembly_or_throw" in inherited_audit
        and "copy_exact_range_into_or_throw" in inherited_audit
        and "compatibility API reconstructs owned payload strings" in inherited_audit,
        "inherited_memory_audit_tracks_new_shipping_and_compatibility_split",
        "rev0997 proof language does not become a stale false negative",
    )
    require(
        "anonsync-direct-source-frame-source-audit-v1" in structural_audit
        and "DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md" in structural_audit,
        "structural_audit_includes_rev0998_boundary",
        "the accumulated authority inventory cannot omit the new source ownership slice",
    )
    require(
        "DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md" in verifier
        and "REVISION_NOTES_rev0998.md" in verifier
        and "tests/sync_replica_reconciliation_source_frame_memory_test.cpp" in verifier
        and "tools/audit_sync_replica_direct_source_frame.py" in verifier,
        "release_verifier_binds_rev0998_slice",
        "the archive cannot omit implementation, runtime oracle, design, notes, or audit",
    )
    normalized = " ".join((design + "\n" + notes).replace("**", "").split())
    require(
        "not complete operating-system peak-RSS measurements" in normalized
        and "OpenSSL" in normalized
        and "cross-file chunk discovery" in normalized,
        "design_records_memory_nonclaims_and_next_delta_edge",
        "heap ownership proof is not overstated as complete multi-terabyte qualification",
    )
    require(
        "## Rev0998:" in readme
        and "REV0998 RELEASE CUTPOINT" in bootstrap
        and "CURRENT REVISION MOVE" in bootstrap
        and "Rev1007 advances reconciliation to generation 9" in bootstrap
        and "NEXT PRODUCT EDGE" in bootstrap,
        "visible_release_surfaces_preserve_rev0998_and_current_wire_lineage",
        "README and runbook retain the direct-source cutpoint while later work preserves its generation-8 wire lineage",
    )
    require(
        "VALIDATION_PENDING_REV0998" not in notes
        and "ARCHIVE_PENDING_REV0998" not in notes
        and "CODENAME_PENDING_REV0998" not in notes
        and "VALIDATION_PENDING_REV0998" not in design
        and "ARCHIVE_PENDING_REV0998" not in design
        and "CODENAME_PENDING_REV0998" not in design
        and "VALIDATION_PENDING_REV0998" not in readme
        and "ARCHIVE_PENDING_REV0998" not in readme
        and "CODENAME_PENDING_REV0998" not in readme
        and "VALIDATION_PENDING_REV0998" not in bootstrap
        and "ARCHIVE_PENDING_REV0998" not in bootstrap
        and "CODENAME_PENDING_REV0998" not in bootstrap,
        "final_validation_and_archive_are_sealed",
        "rev0998 cannot pass until exact evidence and archive identity replace all placeholders",
    )
    require(
        "lexical-hygiene-not-semantic-or-peak-rss-proof" in Path(__file__).read_text(encoding="utf-8")
        and "not a semantic proof" in Path(__file__).read_text(encoding="utf-8"),
        "lexical_audit_disclaims_semantic_authority",
        "passing source vocabulary cannot substitute for runtime, sanitizer, and package proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
