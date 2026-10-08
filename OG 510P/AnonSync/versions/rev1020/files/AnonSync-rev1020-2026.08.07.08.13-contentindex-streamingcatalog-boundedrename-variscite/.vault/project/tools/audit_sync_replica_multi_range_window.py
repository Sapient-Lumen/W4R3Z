#!/usr/bin/env python3
"""Lexical audit for rev0996 bounded multi-range payload windows.

This is source-shape hygiene, not semantic proof. Compiler, sanitizer, runtime,
reconstruction, performance, memory, and package evidence remain load-bearing.
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
    Path("MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md"),
    Path("REVISION_NOTES_rev0996.md"),
    Path("src/anonsync_replica.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_replica_multi_range_window.py"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
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
        "format": "anonsync-multi-range-payload-window-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove transfer throughput, peak RSS, "
            "crash safety, protocol correctness, privacy, or package identity"
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
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(
        bootstrap_path.is_file(),
        "release_root_bootstrap_exists",
        str(bootstrap_path),
    )
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md"]
    notes = text["REVISION_NOTES_rev0996.md"]
    replica_cli = text["src/anonsync_replica.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    process_test = text["tools/test_anonsync_replica_reconciliation_process.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_multi_range_window_source_audit" in cmake
        and "tools/audit_sync_replica_multi_range_window.py" in cmake,
        "focused_audit_registered",
        "the multi-range source audit is in the ordinary CTest registry",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "reconciliation-request-frame-v9" in protocol_c
        and "reconciliation-response-frame-v9" in protocol_c
        and "reconciliation-request-v9" in protocol_c
        and "reconciliation-response-v9" in protocol_c,
        "protocol_and_all_digest_domains_follow_current_generation",
        "older one-range semantics cannot decode under the current frame or body domains",
    )
    require(
        "several" in protocol_h
        and "contiguous chunk-confined ranges" in protocol_h
        and "manifest appears on the first range" in protocol_h,
        "public_protocol_contract_names_one_grouped_manifest_window",
        "the header records the bounded multi-record semantics",
    )
    require(
        "struct PayloadGroup final" in protocol_c
        and "std::uint64_t range_count = 0U" in protocol_c
        and "std::vector<const SyncReplicaReconciliationPayload*> ranges" not in protocol_c,
        "validator_group_state_is_scalar_not_pointer_vector",
        "validation does not allocate one copied pointer per range",
    )
    require(
        "payload ranges are not strictly sorted and unique by digest and offset" in protocol_c
        and "payload ranges disagree about total size" in protocol_c
        and "payload ranges are not exactly contiguous" in protocol_c,
        "range_groups_are_canonical_size_bound_and_contiguous",
        "overlap, gap, duplicate, and extent drift fail before application",
    )
    require(
        "complete content-defined manifest is not confined to the first range" in protocol_c
        and "ranged payloads disagree about their content-defined manifest" in protocol_c
        and "validate_payload_range_against_delta_manifest_or_throw" in protocol_c,
        "one_manifest_authority_binds_every_range_in_the_group",
        "only the first record may carry the manifest and every record retains exact chunk geometry",
    )
    require(
        "payload continuation does not follow its exact contiguous range group" in protocol_c
        and "first_payload.offset_bytes != continuation.next_offset_bytes" in protocol_c
        and "last_payload.offset_bytes" in protocol_c,
        "continuation_binds_first_offset_and_final_group_end",
        "a grouped response cannot skip or replay cursor authority silently",
    )
    require(
        "selected_payloads.size() <" in service_c
        and "protocol_limits_.max_payloads_per_page" in service_c
        and "payload_bytes <" in service_c
        and "protocol_limits_.max_payload_bytes_per_page" in service_c
        and "next_offset < operation.size_bytes" in service_c,
        "source_window_has_record_byte_and_extent_frontiers",
        "one response remains bounded independently of payload size",
    )
    require(
        "protocol_limits_.max_single_payload_bytes" in service_c
        and "available_page_bytes" in service_c
        and "maximum_range" in service_c
        and "chunk_end - next_offset" in service_c
        and "ranged payload plan made no progress" in service_c
        and "const std::uint64_t range_offset = next_offset" in service_c
        and "selected.range_bytes" in service_c,
        "each_emitted_range_is_page_bounded_and_chunk_confined",
        "the bounded plan retains exact range geometry until its descriptor fills the final frame",
    )
    lookup = service_c.find("content-defined chunk-index lookup")
    window = service_c.find("while (", lookup)
    plan = service_c.find("selected_payloads.push_back", window)
    fill = service_c.find("copy_exact_range_into_or_throw", plan)
    require(
        lookup >= 0 and window > lookup and plan > window and fill > plan
        and service_c.count("content-defined chunk-index lookup") == 1,
        "one_source_index_lookup_seeds_each_bounded_window",
        "later records advance linearly through the retained cumulative index before exact descriptor-to-frame fill",
    )
    require(
        "if (first_range &&" in service_c
        and "content-defined manifest publication" in service_c
        and "content-defined manifest reference" in service_c
        and "first_range = false" in service_c,
        "source_publishes_manifest_once_then_exact_references",
        "multi-range framing does not duplicate an 8,192-record manifest per range",
    )
    require(
        all(
            token in service_h
            for token in (
                "ranged_payload_windows()",
                "ranged_payload_ranges()",
                "ranged_payload_bytes()",
            )
        )
        and all(
            token in service_c
            for token in (
                "ranged payload windows",
                "ranged payload ranges",
                "ranged payload bytes",
            )
        ),
        "source_session_counts_windows_ranges_and_bytes",
        "operator evidence distinguishes turn collapse from record and byte work",
    )
    require(
        all(
            token in tls_h + tls_c
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
        ),
        "window_accounting_reaches_tls_and_shipping_json",
        "the authenticated source and operator surface expose exact grouped transfer work",
    )
    require(
        "struct PayloadRangeSpan final" in service_c
        and "std::map<std::string, PayloadRangeSpan>" in service_c
        and "validated payload range group lost contiguity" in service_c
        and "std::vector<const SyncReplicaReconciliationPayload*>" not in service_c,
        "receiver_indexes_validated_groups_as_contiguous_spans",
        "receiver grouping avoids a heap vector and pointer copy for every digest",
    )
    require(
        "if (wire_end <= durable_prefix)" in service_c
        and "delta_wire_already_durable_ranges" in service_c
        and "delta_wire_already_durable_bytes" in service_c
        and "if (wire.offset_bytes > durable_prefix)" in service_c
        and "payload range group skipped the receiver's exact durable prefix" in service_c
        and "if (wire.offset_bytes < durable_prefix)" in service_c
        and "effective_bytes.remove_prefix" in service_c
        and "effective_offset = durable_prefix" in service_c
        and "Sha256DigestBuilder suffix_digest" in service_c
        and "delta_wire_overlap_trimmed_ranges" in service_c
        and "payload range group overlaps the receiver's exact durable prefix" not in service_c,
        "receiver_consumes_ranges_in_order_and_skips_exactly_covered_work",
        "durable replay skips complete ranges, preserves only an advancing overlap suffix, and rejects gaps",
    )
    require(
        "Stop before admitting operation metadata" in service_c
        and "PayloadProgress" in service_c
        and "payload_continuation" in service_c,
        "operation_admission_remains_after_whole_payload_authority",
        "a grouped partial window creates only resumable bytes, never operation-ahead metadata",
    )
    require(
        all(token in protocol_test for token in (
            "multi-range response accepted a gap between adjacent records",
            "multi-range response accepted an overlap between adjacent records",
            "multi-range response repeated its complete manifest",
            "maximum-extent scale proof did not collapse sixteen canonical ranges",
            "65'536U",
            "983'040U",
        )),
        "protocol_regression_covers_group_failures_and_4tib_turn_arithmetic",
        "the exact maximum shape is proved without allocating a multi-terabyte payload",
    )
    require(
        all(token in service_test for token in (
            "initial large-payload page was not one bounded two-range window",
            "two ranges in one response were not one durable prefix",
            "recover and skip the durable two-range prefix",
            "bounded multi-range window",
        )),
        "service_regression_covers_restart_and_shifted_reuse_windows",
        "batched bytes retain crash restart and predecessor-reuse behavior",
    )
    require(
        "test_exhausted_byte_budget_stops_before_next_ranged_payload_open" in service_test
        and "zero-byte frontier opened, hashed, indexed, or published" in service_test
        and "ranged_payload_windows() == 0U" in service_test,
        "zero_byte_frontier_stops_before_large_payload_authority",
        "an exhausted page cannot pay descriptor, manifest, index, or ranged-publication work for its successor",
    )
    require(
        "max_payload_bytes_per_page = 8U" in tls_test
        and "first_options.max_round_trips = 1U" in tls_test
        and "ranged_payload_ranges == 2U" in tls_test
        and "ranged_payload_bytes == 8U" in tls_test
        and "two contiguous ranges in one authenticated round trip" in tls_test,
        "tls_restart_oracle_proves_one_round_trip_multi_range_window",
        "encode, TLS, decode, staging, restart replay, and final completion preserve the grouped window",
    )
    require(
        '"reconciliation_requests_received": 1' in process_test
        and '"reconciliation_ranged_payload_windows": 1' in process_test
        and '"reconciliation_ranged_payload_ranges": 16' in process_test
        and '"reconciliation_ranged_payload_bytes": first_session_bytes'
        in process_test,
        "shipping_process_oracle_proves_default_sixteen_range_window",
        "the real CLI source collapses one 64 MiB window into one authenticated request and response",
    )
    require(
        "65,536" in design
        and "983,040" in design
        and "64 MiB" in design
        and "not a measured 4 TiB transfer" in design,
        "design_quantifies_turn_collapse_without_performance_overclaim",
        "the record distinguishes exact framing arithmetic from measured throughput and RSS",
    )
    require(
        "MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md" in verifier
        and "REVISION_NOTES_rev0996.md" in verifier
        and "tools/audit_sync_replica_multi_range_window.py" in verifier,
        "release_verifier_binds_rev0996_slice",
        "the archive cannot omit implementation, tests, design, notes, or focused audit",
    )
    require(
        "rev0996" in readme.casefold()
        and "rev0996" in bootstrap.casefold()
        and "rev0996" in design.casefold()
        and "rev0996" in notes.casefold(),
        "visible_release_surfaces_name_rev0996",
        "README, runbook, design, and revision notes agree on the current revision",
    )
    require(
        all(
            token not in readme + bootstrap + design + notes
            for token in (
                "VALIDATION_PENDING_REV0996",
                "ARCHIVE_PENDING_REV0996",
                "CODENAME_PENDING_REV0996",
            )
        ),
        "final_validation_and_archive_are_sealed",
        "rev0996 cannot pass its focused audit until validation and archive identity are final",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
