#!/usr/bin/env python3
"""Lexical audit for rev1001 bounded resumable cross-file projection.

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
    Path("BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md"),
    Path("REVISION_NOTES_rev1001.md"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
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
        "format": "anonsync-bounded-resumable-cross-file-projection-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove descriptor identity, bounded runtime "
            "latency, chunk reuse, complete digest authority, sanitizer cleanliness, "
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
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md"]
    notes = text["REVISION_NOTES_rev1001.md"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    store_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_bounded_cross_file_projection_source_audit" in cmake
        and "tools/audit_sync_replica_bounded_cross_file_projection.py" in cmake,
        "focused_audit_is_registered",
        "the rev1001 source audit is an ordinary CTest",
    )
    require(
        "class SyncReplicaFilePayloadStoreContentDefinedProjection final" in store_h
        and "const SyncReplicaFilePayloadStoreContentDefinedProjection&) = delete" in store_h
        and "SyncReplicaFilePayloadStoreContentDefinedProjection&&) noexcept" in store_h
        and "std::unique_ptr<State> state_" in store_h,
        "projection_is_move_only_and_opaque",
        "unfinished hashing has one owner and does not expose mutable implementation state",
    )
    require(
        "content_sha256() const" in store_h
        and "total_size_bytes() const" in store_h
        and "next_offset_bytes() const" in store_h
        and "completed_chunk_bytes() const" in store_h
        and "parameters() const" in store_h
        and "metadata() const" in store_h
        and "completed_chunks() const" in store_h,
        "projection_exposes_exact_read_only_identity_and_progress",
        "callers can inspect only the bound identity, observation, parameters, and completed frontier",
    )
    require(
        "advance_content_defined_projection_or_throw" in store_h
        and "maximum_step_bytes" in store_h
        and "Any read or reproof failure discards" in store_h,
        "bounded_projection_api_declares_failure_and_budget_contract",
        "the public owner boundary names the exact resumable semantics",
    )
    require(
        "class ContentDefinedDigestAccumulator final" in store_c
        and store_c.count("ContentDefinedDigestAccumulator") >= 4
        and "hash_regular_file_content_defined_chunks_or_throw" in store_c,
        "complete_and_bounded_hashing_share_one_accumulator",
        "boundary selection and digest segmentation cannot drift into parallel implementations",
    )
    accumulator = function_body(store_c, "class ContentDefinedDigestAccumulator final")
    require(
        "whole_digest_.update(completed_span)" in accumulator
        and "whole_digest_.update(pending_span)" in accumulator
        and "chunk_digest_.update" in accumulator
        and "chunker_.consume_byte" in accumulator
        and "whole_digest_.checkpoint()" in accumulator
        and "chunk_digest_.checkpoint()" in accumulator
        and "maximum_chunk_count" in accumulator
        and "completed_chunk_bytes_ != total_size_bytes_" in accumulator,
        "accumulator_binds_whole_chunk_and_extent_invariants",
        "whole and chunk resumable SHA-256 progress share the canonical rolling boundary, arbitrary-byte checkpoint, and exact final extent",
    )
    advance = function_body(
        store_c,
        "advance_content_defined_projection_or_throw(",
    )
    require(
        "maximum_step_bytes == 0U" in advance
        and "std::min<std::uint64_t>(" in advance
        and "maximum_step_bytes, source.metadata.size_bytes - before_bytes" in advance,
        "step_budget_is_positive_and_exactly_bounded",
        "a nonterminal call cannot hash beyond its caller-owned byte frontier",
    )
    require(
        "source.content_sha256" in advance
        and "source.metadata" in advance
        and "projection.state_->parameters != parameters" in advance
        and "projection.state_.reset()" in advance
        and "PayloadStoreObservationStaleError" in advance,
        "resume_requires_exact_identity_observation_and_parameters",
        "stale state is discarded before it can extend another payload",
    )
    require(
        ordered(
            advance,
            "::pread(",
            "::fstat(source.descriptor, &after)",
            "same_regular_file_observation(source.status, after)",
            "out.hashed_bytes",
        ),
        "each_step_reads_then_reproves_descriptor_observation",
        "post-read metadata drift fails before step authority is returned",
    )
    require(
        "try {" in advance
        and "catch (...)" in advance
        and advance.count("projection.state_.reset();") >= 4,
        "projection_progress_is_fail_closed",
        "read, allocation, arithmetic, integrity, and reproof failures cannot retain ambiguous continuation state",
    )
    require(
        "completed.whole_sha256 != source.content_sha256" in advance
        and "SyncReplicaFilePayloadStoreIntegrityError" in advance
        and "out.completed_manifest" in advance
        and "projection.state_.reset();" in advance,
        "complete_manifest_requires_source_whole_digest",
        "only exact whole-source verification converts progress into a reusable complete manifest",
    )
    require(
        "kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply" in service_h
        and "32ULL * 1024ULL * 1024ULL" in service_h,
        "service_owns_a_hard_32_mib_projection_frontier",
        "local candidate hashing has a fixed product ceiling",
    )
    require(
        "struct CrossFileContentDefinedProjection final" in service_h
        and "source_metadata" in service_h
        and "SyncReplicaFilePayloadStoreContentDefinedProjection projection" in service_h
        and "digest_order" in service_h
        and "chunk_offsets{0U}" in service_h
        and "indexed_chunk_count" in service_h,
        "service_retains_one_bounded_partial_candidate_index",
        "one current candidate can continue across apply turns without a complete source image",
    )
    apply = function_body(service_c, "SyncReplicaReconciliationService::apply_response_or_throw")
    require(
        "cross_file_manifest_step_attempted" in apply
        and "if (cross_file_manifest_step_attempted) return;" in apply
        and "advance_content_defined_projection_or_throw" in apply,
        "at_most_one_projection_step_runs_per_apply",
        "candidate projection cannot monopolize one reconciliation invocation",
    )
    require(
        "kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply" in apply
        and "protocol_limits_.max_payload_bytes_per_page" not in apply[apply.find("advance_content_defined_projection_or_throw") - 500 : apply.find("advance_content_defined_projection_or_throw") + 1000],
        "local_projection_frontier_is_not_wire_page_coupled",
        "receiver-local disk scheduling remains independent of negotiated response framing",
    )
    require(
        "projected.projection.completed_chunks()" in apply
        and "extend_content_defined_projection_index_or_throw" in apply
        and "delta cross-file partial candidate" in apply
        and "if (!completed)" in apply,
        "completed_partial_chunks_are_reused_before_source_completion",
        "useful local delta progress does not wait for a full candidate manifest",
    )
    require(
        "reuse_local_candidate_chunks_or_throw" in apply
        and "copy_range_or_throw" in apply
        and "stage_payload_prefix_or_throw" in apply
        and "matching_candidate_chunk" in apply,
        "partial_reuse_preserves_exact_copy_and_staging_authority",
        "candidate chunk evidence remains acceleration rather than publication authority",
    )
    require(
        "step.completed_manifest->chunks.size()" in apply
        and "projected.chunk_offsets.back() != candidate.size_bytes" in apply
        and "delta_cross_file_manifest_scans" in apply
        and "delta_cross_file_index_builds" in apply,
        "complete_projection_reproves_exact_index_extent",
        "manifest and index completion cannot lose or invent source extent",
    )
    require(
        "payload_availability_generation_at_sweep_start" in service_h
        and "payload_availability_generation_or_throw" in service_c
        and "delta_cross_file_availability_generation_restarts" in service_c
        and "delta_cross_file_unavailable_candidates" in service_c,
        "late_payload_availability_restarts_exhausted_search",
        "a newly durable source can be discovered without a causal visible-state change",
    )
    for counter in (
        "delta_cross_file_unavailable_candidates",
        "delta_cross_file_availability_generation_restarts",
        "delta_cross_file_manifest_scan_steps",
    ):
        require(
            counter in service_h
            and counter in tls_h
            and counter in tls_c
            and counter in sync_cli
            and counter in replica_cli,
            f"{counter}_crosses_service_tls_and_cli_boundaries",
            "bounded local discovery work is visible in both shipping JSON surfaces",
        )
    require(
        "descriptor-streaming bounded projection reopen" in store_test
        and "5U" in store_test
        and "step.hashed_bytes <= 5U" in store_test
        and "bounded_projection.metadata() ==" in store_test
        and "*bounded_manifest == content_defined" in store_test
        and "stale_parameter_projection" in store_test
        and "retained ambiguous progress after a parameter mismatch" in store_test,
        "payload_store_runtime_reopens_and_reproduces_canonical_manifest",
        "five-byte steps bind exact progress, observation, and complete-manifest equivalence",
    )
    require(
        "test_payload_availability_generation_tracks_durable_insertions" in store_test
        and "durable payload insertion did not advance availability generation" in store_test
        and "already-present payload unexpectedly advanced availability generation" in store_test
        and "batched duplicate unexpectedly advanced availability generation" in store_test,
        "payload_availability_generation_runtime_binds_new_identity_only",
        "late-source rediscovery cannot be triggered by idempotent replay alone",
    )
    require(
        "test_cross_file_content_defined_delta_reuses_renamed_media_chunks" in service_test
        and "48U * mebibyte" in service_test
        and "00-original-media.bin" in service_test
        and "01-unrelated-media.bin" in service_test
        and "candidate_pages == 2U" in service_test
        and "cross_manifest_scan_steps == 4U" in service_test
        and "availability_generation_restarts == 1U" in service_test
        and "partial_candidate_reuse_before_complete_manifest" in service_test,
        "service_runtime_binds_two_sweeps_four_steps_and_partial_reuse",
        "absent useful source, decoy, late publication, bounded restart, and exact reuse are one regression",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_is_unchanged",
        "resumable projection is receiver-local acceleration",
    )
    require(
        "anonsync-bounded-resumable-cross-file-projection-audit-v1" in structural
        and "BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md" in verifier
        and "REVISION_NOTES_rev1001.md" in verifier
        and "tools/audit_sync_replica_bounded_cross_file_projection.py" in verifier,
        "release_policy_binds_rev1001_slice",
        "the archive cannot omit the implementation, runtime oracles, design, notes, or audit",
    )
    normalized = " ".join(
        (design + "\n" + notes + "\n" + readme + "\n" + bootstrap)
        .replace("**", "")
        .split()
    )
    require(
        "32 mib" in normalized.lower()
        and "total cold" in normalized.lower()
        and "process-local" in normalized.lower()
        and "not yet resumable" in normalized.lower()
        and "durable or global chunk index" in normalized.lower()
        and "multi-terabyte" in normalized.lower(),
        "latency_memory_and_product_nonclaims_are_explicit",
        "the release does not overstate one bounded hashing step as bounded total I/O or a global index",
    )
    require(
        all(
            token not in normalized
            for token in (
                "VALIDATION_PENDING_REV1001",
                "ARCHIVE_PENDING_REV1001",
                "CODENAME_PENDING_REV1001",
            )
        ),
        "final_validation_and_archive_identity_are_sealed",
        "rev1001 cannot pass release audit while placeholders remain",
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
