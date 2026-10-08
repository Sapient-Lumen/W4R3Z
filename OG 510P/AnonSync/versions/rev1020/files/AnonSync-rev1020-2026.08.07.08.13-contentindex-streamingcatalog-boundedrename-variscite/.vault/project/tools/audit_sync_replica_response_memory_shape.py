#!/usr/bin/env python3
"""Lexical hygiene audit for rev0997 response-memory ownership.

This audit checks reviewed source shape and release vocabulary. It is not a
semantic proof of allocation behavior, protocol equivalence, lifetime safety,
filesystem behavior, TLS buffering, throughput, peak RSS, or package identity.
Compiler, runtime, sanitizer, allocation-oracle, and package evidence remain
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
    Path("SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md"),
    Path("REVISION_NOTES_rev0997.md"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_memory_shape_test.cpp"),
    Path("tools/audit_sync_replica_response_memory_shape.py"),
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
        "format": "anonsync-response-memory-shape-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove allocation count, lifetime safety, "
            "wire equivalence, TLS buffering, peak RSS, throughput, or package identity"
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


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
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
    design = text["SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md"]
    notes = text["REVISION_NOTES_rev0997.md"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    memory_test = text["tests/sync_replica_reconciliation_memory_shape_test.cpp"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_reconciliation_memory_shape_test" in cmake
        and "tests/sync_replica_reconciliation_memory_shape_test.cpp" in cmake,
        "memory_shape_test_is_built",
        "the deterministic allocation oracle is a configured C++ target",
    )
    require(
        "PROPERTIES TIMEOUT 30 LABELS \"product\"" in cmake
        and cmake.count("anonsync_sync_replica_reconciliation_memory_shape_test") >= 6,
        "memory_shape_test_is_product_and_sanitizer_retained",
        "the new boundary participates in ordinary product and sanitizer graphs",
    )
    require(
        "anonsync_sync_replica_response_memory_shape_source_audit" in cmake
        and "tools/audit_sync_replica_response_memory_shape.py" in cmake,
        "focused_source_audit_is_registered",
        "the release vocabulary check is in the ordinary CTest registry",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "anonsync-sync-replica-reconciliation-request-frame-v9" in protocol_c
        and "anonsync-sync-replica-reconciliation-response-frame-v9" in protocol_c
        and "anonsync-sync-replica-reconciliation-request-v9" in protocol_c
        and "anonsync-sync-replica-reconciliation-response-v9" in protocol_c,
        "wire_generation_and_digest_domains_follow_current_generation",
        "the inherited memory boundary follows the current bounded-source wire generation",
    )
    require(
        "struct SyncReplicaReconciliationEncodedResponse final" in protocol_h
        and all(token in protocol_h for token in (
            "std::string frame",
            "std::string response_digest",
            "canonical_body_bytes",
            "payload_bytes",
            "encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw",
        )),
        "combined_encoder_has_one_explicit_result",
        "frame, digest, and exact byte metrics cross one request-bound API",
    )
    require(
        "struct SyncReplicaReconciliationBorrowedResponse final" in protocol_h
        and "std::vector<std::string_view> payload_bytes" in protocol_h
        and "The frame must outlive this object" in protocol_h,
        "borrowed_response_names_its_lifetime_contract",
        "payload views are explicit and caller-frame lifetime is documented",
    )
    require(
        "ResponseBodyMetrics" in protocol_c
        and "response_body_metrics_or_throw" in protocol_c
        and "frame.reserve(" in protocol_c
        and "append_response_body_or_throw(frame" in protocol_c
        and "sha256_view_or_throw" in protocol_c,
        "encoder_projects_exact_size_and_appends_into_final_frame",
        "one exact final string replaces the temporary complete body",
    )
    require(
        "body_digest_or_throw(\n        kResponseDigestDomain, response_body_or_throw" not in
        function_body(protocol_c, "encode_sync_replica_reconciliation_response_after_validation_or_throw"),
        "combined_encoder_does_not_reserialize_for_semantic_digest",
        "semantic digest hashes the canonical body already resident inside frame",
    )
    source_encoder = function_body(
        protocol_c,
        "encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw",
    )
    require(
        source_encoder.count("validate_sync_replica_reconciliation_response_for_request_or_throw") == 1
        and "encode_sync_replica_reconciliation_response_after_validation_or_throw" in source_encoder,
        "request_bound_source_validation_occurs_once",
        "the request-bound cutpoint calls an already-validated encoder",
    )
    require(
        "FrameReader::read_view" not in protocol_c
        and "[[nodiscard]] std::string_view read_view" in protocol_c
        and "borrowed.payload_bytes.push_back(reader.read_view" in protocol_c
        and "borrowed.response.payloads[index].bytes.assign" in protocol_c,
        "borrowed_parser_views_then_compatibility_decoder_copies",
        "shipping can borrow while the old owned API retains canonical semantics",
    )
    borrowed_decoder = function_body(
        protocol_c,
        "decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw",
    )
    require(
        "parse_response_body_borrowing_payloads_without_validation_or_throw" in borrowed_decoder
        and "validate_sync_replica_reconciliation_borrowed_response_for_request_or_throw" in borrowed_decoder
        and borrowed_decoder.count("validate_sync_replica_reconciliation_borrowed_response_for_request_or_throw") == 1,
        "request_bound_borrowed_decode_validates_once",
        "raw views are request-validated without a preceding generic payload hash pass",
    )
    require(
        "begin_sync_replica_reconciliation_response_frame_assembly_or_throw" in service_c
        and "copy_exact_range_into_or_throw" in service_c
        and "encode_sync_replica_reconciliation_response_for_request_or_throw" not in service_c
        and "serve_request_frame_or_throw" in service_c
        and "decode_sync_replica_reconciliation_response_or_throw" in service_c
        and "decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw" in service_c
        and "decode_sync_replica_reconciliation_response_or_throw(" not in
        function_body(service_c, "SyncReplicaReconciliationService::apply_response_or_throw"),
        "shipping_source_and_receiver_use_new_cutpoints",
        "the shipping source fills one frame directly while only the named compatibility API reconstructs owned payload strings",
    )
    require(
        "std::string_view wire_bytes" in service_c
        and "decoded.payload_bytes[payload_index]" in service_c
        and "stage_payload_prefix_or_throw" in service_c,
        "receiver_threads_borrowed_views_into_staging",
        "payload bytes remain borrowed through sequential grouped-range application",
    )
    stage = function_body(
        store_c,
        "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw",
    )
    require(
        "std::string_view bytes" in store_h
        and "SyncReplicaFilePayloadStore::stage_payload_prefix_or_throw" in store_c
        and "Sha256DigestBuilder range_digest" in stage
        and "pwrite_all_or_throw" in stage,
        "normal_prefix_staging_hashes_and_writes_views",
        "the shared modern staging owner hashes and writes borrowed views without a record-sized copy",
    )
    require(
        stage.count("std::string(bytes)") <= 1
        and "if (delegate_to_legacy_range_owner)" in stage
        and "stage_payload_range_or_throw" in stage,
        "only_named_legacy_delegate_copies_staging_bytes",
        "only the explicit rev0941 compatibility delegate reconstructs an owned range string",
    )
    require(
        "encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw" in protocol_test
        and "decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw" in protocol_test
        and "bytes_begin >= frame_begin" in protocol_test
        and "borrowed.response.payloads[index].bytes.empty()" in protocol_test,
        "protocol_regression_proves_wire_equality_and_frame_views",
        "borrowed semantics are checked independently of the allocation oracle",
    )
    require(
        "kPayloadCount = 16U" in memory_test
        and "kPayloadBytes = 1024U * 1024U" in memory_test
        and "kLargeAllocationThreshold = 512U * 1024U" in memory_test,
        "allocation_fixture_is_sixteen_mebibytes",
        "the probe is large enough to expose page copies without counting metadata",
    )
    require(
        "encode_allocations.count == 1U" in memory_test
        and "borrowed_allocations.count == 0U" in memory_test
        and "owned_allocations.count >= value.response.payloads.size()" in memory_test,
        "allocation_oracle_requires_one_zero_and_owned_differential",
        "the regression checks the concrete ownership shape rather than only output equality",
    )
    require(
        "direct response encoding changed canonical generation-9 framing" in memory_test
        and "direct response encoding changed the semantic digest" in memory_test
        and "payload_begin + payload.size() <= frame_end" in memory_test,
        "allocation_oracle_also_binds_wire_digest_and_view_extent",
        "memory reduction cannot silently weaken canonical protocol authority",
    )
    normalized_design = " ".join(design.replace("**", "").split())
    require(
        "does not claim one total resident page" in normalized_design
        and "OpenSSL and kernel socket buffers are outside" in normalized_design
        and "not measured 64 MiB or multi-terabyte peak RSS" in normalized_design
        and "Source response payload objects and the final frame coexist" in normalized_design,
        "design_records_remaining_memory_nonclaims",
        "deterministic heap shape is not overstated as target-scale RSS or TLS zero-copy",
    )
    require(
        "consuming or streaming source encoder" in normalized_design
        and "controlled ENOSPC" in normalized_design
        and "cross-file chunk discovery" in normalized_design,
        "next_product_edge_is_measurement_driven",
        "remaining transfer memory and delta work stay tied to the multi-terabyte workflow",
    )
    require(
        "SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md" in verifier
        and "REVISION_NOTES_rev0997.md" in verifier
        and "tests/sync_replica_reconciliation_memory_shape_test.cpp" in verifier
        and "tools/audit_sync_replica_response_memory_shape.py" in verifier,
        "release_policy_binds_rev0997_slice",
        "the package cannot omit the implementation proof, design, notes, or focused audit",
    )
    normalized_bootstrap = " ".join(bootstrap.split())
    require(
        "Rev0997" in readme
        and "REV0997 RELEASE CUTPOINT" in bootstrap
        and "borrowed receiver payloads" in readme
        and "Rev0998" in readme
        and "REV0998 RELEASE CUTPOINT" in bootstrap
        and "CURRENT REVISION MOVE" in bootstrap
        and "Rev1007 advances reconciliation to generation 9" in normalized_bootstrap,
        "visible_restart_preserves_historical_move_and_current_wire_lineage",
        "the historical borrowed-receiver and direct-source slices remain visible while later work preserves generation-8 wire lineage",
    )
    require(
        "VALIDATION_PENDING_REV0997" not in notes
        and "ARCHIVE_PENDING_REV0997" not in notes
        and "CODENAME_PENDING_REV0997" not in notes
        and "VALIDATION_PENDING_REV0997" not in design
        and "ARCHIVE_PENDING_REV0997" not in design
        and "CODENAME_PENDING_REV0997" not in design
        and "VALIDATION_PENDING_REV0997" not in readme
        and "ARCHIVE_PENDING_REV0997" not in readme
        and "CODENAME_PENDING_REV0997" not in readme
        and "VALIDATION_PENDING_REV0997" not in bootstrap
        and "ARCHIVE_PENDING_REV0997" not in bootstrap
        and "CODENAME_PENDING_REV0997" not in bootstrap,
        "final_validation_and_visible_release_cutpoint_are_sealed",
        "rev0997 remains intentionally gated until exact evidence and archive identity replace placeholders",
    )
    normalized_doc = " ".join((__doc__ or "").split())
    require(
        "not a semantic proof" in normalized_doc
        and "Compiler, runtime, sanitizer" in normalized_doc,
        "lexical_audit_disclaims_semantic_authority",
        "passing source vocabulary cannot substitute for runtime and package evidence",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
