#!/usr/bin/env python3
"""Lexical audit for rev1003 bounded same-path predecessor projection.

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
    Path("BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md"),
    Path("REVISION_NOTES_rev1003.md"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_file_payload_terminal_verification_state.hpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tools/audit_sync_replica_bounded_cross_file_projection.py"),
    Path("tools/audit_sync_replica_manifest_reference.py"),
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
        "format": "anonsync-bounded-predecessor-projection-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove bounded runtime I/O, descriptor "
            "identity, partial-chunk reuse, final digest authority, sanitizer "
            "cleanliness, performance, or package identity"
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
    candidates = (root.parent.parent / "BOOTSTRAPROSE.md", root.parent / "BOOTSTRAPROSE.md")
    bootstrap_path = next((path for path in candidates if path.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md"]
    notes = text["REVISION_NOTES_rev1003.md"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    terminal_state_h = text["src/sync_replica_file_payload_terminal_verification_state.hpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    runtime = text["tests/sync_replica_reconciliation_service_test.cpp"]
    bounded_cross = text["tools/audit_sync_replica_bounded_cross_file_projection.py"]
    manifest_reference = text["tools/audit_sync_replica_manifest_reference.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    apply = function_body(service_c, "SyncReplicaReconciliationService::apply_response_or_throw(")
    constructor = function_body(service_c, "SyncReplicaReconciliationService::SyncReplicaReconciliationService(")
    terminal = function_body(store_c, "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw(")

    require(
        "anonsync_sync_replica_bounded_predecessor_projection_source_audit" in cmake
        and "tools/audit_sync_replica_bounded_predecessor_projection.py" in cmake,
        "focused_audit_is_registered", "the rev1003 source-shape audit is an ordinary CTest")
    require(
        "kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply" in service_h
        and "32ULL * 1024ULL * 1024ULL" in service_h,
        "one_shipping_32_mib_predecessor_frontier_exists", "one apply has a hard local predecessor hashing ceiling")
    require(
        "max_predecessor_projection_bytes_per_apply" in service_h
        and "max_predecessor_projection_bytes_per_apply_" in constructor
        and "max_predecessor_projection_bytes_per_apply_ == 0U" in constructor
        and "shipping maximum" in constructor,
        "constructor_defaults_to_shipping_frontier_and_cannot_raise_it", "tests may reduce but production callers cannot expand the frontier")
    require(
        "struct PredecessorContentDefinedProjection final" in service_h
        and "SyncReplicaFilePayloadStoreContentDefinedProjection projection" in service_h
        and "digest_order" in service_h and "chunk_offsets{0U}" in service_h
        and "indexed_chunk_count" in service_h and "delta_predecessor_projection_" in service_h,
        "one_process_local_predecessor_projection_is_retained", "bounded source progress and its exact partial index survive later applies")
    require(
        "bool predecessor_manifest_step_attempted = false" in apply
        and "if (predecessor_manifest_step_attempted) return;" in apply
        and "predecessor_manifest_step_attempted = true" in apply,
        "at_most_one_predecessor_projection_step_runs_per_apply", "same-path hashing cannot reset its budget for another predecessor")
    require(
        "open_optional_payload_for_operation_or_throw" in apply
        and "delta predecessor selection" in apply and "opened->metadata()" in apply,
        "each_step_reopens_and_reproves_exact_predecessor_observation", "retained process state does not substitute for targeted payload authority")
    require(
        ordered(apply, "delta predecessor bounded content-defined projection", "result.delta_predecessor_manifest_hashed_bytes", "step.hashed_bytes == 0U", "max_predecessor_projection_bytes_per_apply_"),
        "actual_hashed_bytes_are_charged_and_frontier_checked", "a lower projection cannot silently exceed or return zero progress")
    require(
        "projected.projection.completed_chunks()" in apply
        and "delta predecessor partial" in apply
        and apply.find("delta predecessor partial") < apply.find("advance_content_defined_projection_or_throw"),
        "completed_partial_chunks_are_reused_before_another_hash_step", "already discovered chunks can accelerate the target before source completion")
    require(
        apply.count("extend_content_defined_projection_index_or_throw(") >= 2
        and "std::lower_bound" in service_c and "projected.digest_order.insert" in service_c
        and "projected.chunk_offsets.push_back" in service_c,
        "same_path_and_cross_file_share_one_incremental_index_helper", "digest ordering and exact offsets cannot drift into duplicate implementations")
    require(
        "step.completed_manifest->chunks.size()" in apply
        and "projected.chunk_offsets.back() != observed->size_bytes" in apply
        and ordered(apply, "completed delta predecessor projection lost its exact index extent", "retained.manifest = std::move(*step.completed_manifest)", "delta_predecessor_manifest_ = std::move(retained)", "delta_predecessor_manifest_scans"),
        "only_complete_exact_source_projection_becomes_retained_manifest", "partial chunk evidence remains acceleration rather than complete-manifest authority")
    require(
        "delta_predecessor_projection_.reset();\n                throw;" in apply
        and "delta_cross_file_projection_.reset();\n                throw;" in apply,
        "lower_projection_failure_clears_the_enclosing_partial_index", "inactive lower state cannot coexist with stale outer offsets on a later apply")
    require(
        "constexpr std::uint64_t old_size = 48U * mebibyte" in runtime
        and "predecessor_projection_steps" in runtime
        and "predecessor_incomplete_projection_steps" in runtime
        and "reused_before_predecessor_projection_completed" in runtime
        and "predecessor_manifest_hashed_bytes == old_bytes.size()" in runtime,
        "runtime_proves_two_step_48_mib_projection_and_early_reuse", "the focused semantic oracle exercises a nonterminal step before exact completion")
    require(
        "const std::string completed_sha256 = running.finish_hex()" in terminal
        and "completed_sha256 != content_sha256" in terminal
        and "ResumableSha256Checkpoint" in terminal_state_h,
        "terminal_whole_target_hash_remains_publication_authority", "rev1004 bounds final local SHA-256 without replacing exact whole-target authority with partial acceleration state")
    normalized = " ".join((design + "\n" + notes + "\n" + readme + "\n" + bootstrap).replace("**", "").split())
    require(
        "terminal" in normalized.lower() and "unbounded" in normalized.lower()
        and "process-local" in normalized and "not restart-durable" in normalized
        and "multi-terabyte" in normalized and "not a durable or global chunk index" in normalized.lower(),
        "scope_and_remaining_complete_file_io_nonclaims_are_explicit", "bounded predecessor latency is not overstated as global I/O or durable indexing")
    require(
        ".anonsync-payload-prefix-v2-" not in service_c
        and "update_resumable_hash_regular_file_range_or_throw" not in store_c
        and "rejected" in design.lower() and "pathname" in design.lower() and "integrity-framed" in design.lower(),
        "rejected_raw_pathname_sha_checkpoint_is_not_shipping_authority", "generation-8 terminal continuation uses separately framed identity-bound computation metadata")
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_advances_to_eight_for_terminal_handoff", "bounded predecessor projection remains compatible with the explicit generation-8 receiver terminal obligation")
    require(
        "anonsync-bounded-resumable-cross-file-projection-audit-v1" in bounded_cross
        and "extend_content_defined_projection_index_or_throw" in bounded_cross
        and "extend_content_defined_projection_index_or_throw" in manifest_reference,
        "inherited_projection_audits_follow_the_shared_index_refactor", "source-shape checks follow the canonical incremental helper")
    require(
        "BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md" in verifier
        and "REVISION_NOTES_rev1003.md" in verifier
        and "tools/audit_sync_replica_bounded_predecessor_projection.py" in verifier
        and "rev1003" in structural,
        "release_and_structural_policy_bind_the_rev1003_slice", "the archive must carry code, runtime proof, design, notes, focused audit, and integration")
    require(
        all(token not in design + notes + readme + bootstrap for token in (
            "VALIDATION_PENDING_REV1003", "ARCHIVE_PENDING_REV1003", "CODENAME_PENDING_REV1003")),
        "final_validation_and_visible_release_cutpoint_are_sealed", "rev1003 cannot pass final release audit until every placeholder is replaced")
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not semantic proof" in self_text and "Compiler, sanitizer, runtime" in self_text,
        "lexical_audit_disclaims_load_bearing_semantic_authority", "source spelling cannot replace runtime and package evidence")
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
