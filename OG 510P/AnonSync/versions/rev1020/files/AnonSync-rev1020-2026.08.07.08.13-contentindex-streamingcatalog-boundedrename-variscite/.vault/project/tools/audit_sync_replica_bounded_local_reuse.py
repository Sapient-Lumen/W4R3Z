#!/usr/bin/env python3
"""Lexical audit for rev1002 bounded local delta-copy.

This is source-shape hygiene, not semantic proof. Compiler, sanitizer, runtime,
stress, reconstruction, performance, and package evidence remain load-bearing.
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
    Path("BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md"),
    Path("REVISION_NOTES_rev1002.md"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature: str) -> str:
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
                return text[start : index + 1]
    return ""


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-bounded-local-delta-copy-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove bounded runtime I/O, descriptor "
            "identity, crash recovery, delta efficiency, sanitizer cleanliness, "
            "performance, or package identity"
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
    bootstrap_candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in bootstrap_candidates if path.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(bootstrap_candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md"]
    notes = text["REVISION_NOTES_rev1002.md"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    runtime = text["tests/sync_replica_reconciliation_service_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_bounded_local_reuse_source_audit" in cmake
        and "tools/audit_sync_replica_bounded_local_reuse.py" in cmake,
        "focused_audit_is_registered",
        "the rev1002 source audit is an ordinary CTest",
    )
    require(
        "target_link_libraries(anonsync_sync_replica_reconciliation_service PUBLIC"
            in cmake
        and "anonsync_sha256_digest)" in cmake,
        "trimmed_suffix_hashing_has_an_explicit_build_dependency",
        "the reconciliation service does not rely on a transitive payload-store link for SHA-256",
    )
    require(
        "kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply" in service_h
        and "32ULL * 1024ULL * 1024ULL" in service_h,
        "one_shipping_32_mib_local_reuse_frontier_exists",
        "the receiver owns one hard aggregate source-read budget per apply",
    )
    require(
        "kSyncReplicaReconciliationMaximumLocalReuseRangeBytes" in service_h
        and "4ULL * 1024ULL * 1024ULL" in service_h
        and "static_assert" in service_h,
        "local_copy_range_is_four_mib_and_below_apply_frontier",
        "one local range buffer is product-bounded independently of the wire",
    )
    constructor = function_body(service_c, "SyncReplicaReconciliationService::SyncReplicaReconciliationService(")
    require(
        "max_local_reuse_bytes_per_apply" in service_h
        and "kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply);" in service_h
        and "max_local_reuse_bytes_per_apply_" in constructor
        and "max_local_reuse_bytes_per_apply_ == 0U" in constructor
        and "shipping maximum" in constructor,
        "constructor_defaults_to_shipping_frontier_and_cannot_raise_it",
        "tests may reduce the frontier without expanding the product boundary",
    )
    apply_body = function_body(service_c, "SyncReplicaReconciliationService::apply_response_or_throw(")
    require(
        apply_body.count("remaining_local_reuse_bytes") >= 6
        and "max_local_reuse_bytes_per_apply_" in apply_body
        and apply_body.count("std::uint64_t remaining_local_reuse_bytes") == 1,
        "same_path_and_cross_file_reuse_share_one_budget",
        "the per-apply frontier is not reset per candidate or payload range",
    )
    require(
        "enum class LocalCandidateReuseDisposition" in apply_body
        and "SourceAvailable" in apply_body
        and "SourceUnavailable" in apply_body
        and "BudgetExhausted" in apply_body,
        "local_reuse_outcomes_distinguish_unavailable_from_exhausted",
        "candidate disappearance does not masquerade as scheduling progress",
    )
    require(
        "chunk_index_for_offset_or_throw" in apply_body
        and "chunk_index_at_boundary" not in service_c
        and "target_offset - target_chunk_begin" in apply_body
        and "candidate_chunk_begin + intra_chunk_offset" in apply_body,
        "durable_prefix_can_resume_inside_a_matched_chunk",
        "the candidate source offset carries the exact intra-chunk displacement",
    )
    require(
        "kSyncReplicaReconciliationMaximumLocalReuseRangeBytes" in apply_body
        and "protocol_limits_.max_single_payload_bytes" not in function_body(
            apply_body, "reuse_local_candidate_chunks_or_throw"
        ),
        "local_copy_granularity_is_not_wire_negotiated",
        "tiny frames cannot multiply the local durability effect count",
    )
    require(
        ordered(
            apply_body,
            "copy_range_or_throw(",
            "remaining_local_reuse_bytes -= supplied",
            "delta_local_reuse_read_bytes",
            "stage_payload_prefix_or_throw(",
        ),
        "actual_source_reads_are_charged_before_staging",
        "already-durable prefix jumps cannot erase local I/O accounting",
    )
    require(
        "open_optional_payload_for_operation_or_throw" in apply_body
        and "reopened->metadata() != candidate_metadata" in apply_body
        and "delta local-candidate access" in apply_body,
        "every_bounded_range_reopens_and_reproves_the_candidate",
        "process-local matching state never substitutes for payload-store authority",
    )
    require(
        "mark_local_reuse_budget_exhausted_or_throw" in apply_body
        and "LocalCandidateReuseDisposition::BudgetExhausted" in apply_body
        and "received.next_offset_bytes = target_offset" in apply_body,
        "exhaustion_returns_the_exact_durable_prefix",
        "the next authenticated turn can continue from the committed byte cutpoint",
    )
    require(
        "target_manifest != nullptr &&" in apply_body
        and "!local_reuse_budget_exhausted" in apply_body
        and "delta_wire_already_durable_ranges" in apply_body
        and "effective_bytes.remove_prefix" in apply_body
        and "Sha256DigestBuilder suffix_digest" in apply_body
        and "payload range group overlaps the receiver's exact durable prefix"
            not in apply_body,
        "one_apply_stops_local_reuse_but_preserves_preframed_wire_suffixes",
        "the shared frontier cannot be bypassed and exhaustion cannot discard authenticated response bytes",
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
            counter in service_h
            and counter in tls_h
            and counter in tls_c
            and counter in sync_cli
            and counter in replica_cli,
            f"{counter}_crosses_service_tls_and_cli_boundaries",
            "local scheduling work is visible in both shipping JSON surfaces",
        )
    require(
        "test_local_reuse_frontier_resumes_inside_one_adaptive_chunk" in runtime
        and "local_reuse_bytes_per_apply = 1U * mebibyte" in runtime
        and "wire_range_bytes = 768U * 1024U" in runtime
        and "wire.max_payload_bytes_per_page = 3U * wire_range_bytes" in runtime
        and "has_large_matching_chunk" in runtime,
        "runtime_fixture_contains_a_chunk_larger_than_the_copy_frontier",
        "the test exercises interior continuation rather than a boundary-only loop",
    )
    require(
        "restarted_receiver" in runtime
        and "restarted_after_exhaustion" in runtime
        and "active_receiver = restarted_receiver.get()" in runtime
        and "interior_resumptions >= 1U" in runtime,
        "runtime_reconstructs_service_then_resumes_inside_chunk",
        "durable prefix authority survives loss of process-local service caches",
    )
    require(
        "staged_bytes + reused_bytes == new_bytes.size()" in runtime
        and "staged_bytes + already_durable_wire_bytes == network_bytes" in runtime
        and "network_bytes < new_bytes.size()" in runtime
        and "maximum_local_read_range_bytes > wire_range_bytes" in runtime
        and "overlap_trimmed_wire_ranges != 0U" in runtime
        and "local_read_bytes == reused_bytes" in runtime,
        "runtime_binds_exact_accounting_and_wire_independent_copy_ranges",
        "the deterministic oracle proves net savings without assuming an invented reuse ratio",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_is_unchanged",
        "local-copy scheduling is receiver-local acceleration",
    )
    require(
        "anonsync-bounded-local-delta-copy-audit-v1" in structural
        and "BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md" in verifier
        and "REVISION_NOTES_rev1002.md" in verifier
        and "tools/audit_sync_replica_bounded_local_reuse.py" in verifier,
        "release_policy_binds_rev1002_slice",
        "the archive cannot omit implementation, runtime, design, notes, or focused audit",
    )
    normalized = " ".join((design + "\n" + notes + "\n" + readme + "\n" + bootstrap).replace("**", "").split())
    require(
        "32 MiB" in normalized
        and "four-MiB" in normalized
        and "inside" in normalized
        and "same-path predecessor manifest" in normalized
        and "whole-target" in normalized
        and "not a global" in normalized.lower()
        and "multi-terabyte" in normalized,
        "latency_memory_and_product_nonclaims_are_explicit",
        "bounded candidate reads are not overstated as a global I/O or completed scale proof",
    )
    require(
        all(
            token not in normalized
            for token in (
                "VALIDATION_PENDING_REV1002",
                "ARCHIVE_PENDING_REV1002",
                "CODENAME_PENDING_REV1002",
            )
        ),
        "final_validation_and_archive_identity_are_sealed",
        "rev1002 cannot pass release audit while placeholders remain",
    )
    own_source = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in own_source
        and "not semantic proof" in own_source,
        "lexical_audit_disclaims_semantic_authority",
        "a source scan cannot substitute for compiler, runtime, sanitizer, performance, or package evidence",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
