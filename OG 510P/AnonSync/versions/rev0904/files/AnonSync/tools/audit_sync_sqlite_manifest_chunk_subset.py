#!/usr/bin/env python3
"""Fail-closed structural audit for bounded persisted-manifest subset proof."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_sqlite_manifest_chunk_subset.hpp"),
    Path("src/sync_sqlite_manifest_chunk_subset.cpp"),
    Path("src/sync_domain.cpp"),
    Path("tests/sync_sqlite_manifest_chunk_subset_test.cpp"),
    Path("tools/audit_sync_sqlite_manifest_chunk_subset.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def section(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-manifest-chunk-subset-audit-v1",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
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
        "--root", type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks, {})

    texts = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = texts[Path("CMakeLists.txt")]
    header = texts[Path("src/sync_sqlite_manifest_chunk_subset.hpp")]
    owner = texts[Path("src/sync_sqlite_manifest_chunk_subset.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    focused = texts[Path("tests/sync_sqlite_manifest_chunk_subset_test.cpp")]
    verifier = texts[Path("tools/verify_release_package.py")]

    verify_body = section(
        owner,
        "SyncSqliteManifestChunkSubsetVerifier::verify_source_chunks_or_throw(",
        "\n\nstd::uint64_t\nSyncSqliteManifestChunkSubsetVerifier::owner_generation()",
    )
    preflight = section(
        verify_body,
        "// Complete semantic and arithmetic preflight",
        "SyncSqliteManifestChunkSubsetEvidence evidence;",
    )
    probe_loop = section(
        verify_body,
        "for (const SyncChunkRange& required : required_chunks) {\n        try {",
        "\n\n    return evidence;",
    )
    claim = section(
        domain,
        "SyncValidationResult claim_sync_session_checkpoint_resume_transfer_workorders(",
        "\nSyncValidationResult reset_sync_session_checkpoint_resume_transfer_terminal_workorders(",
    )
    execute = section(
        domain,
        "SyncValidationResult execute_sync_session_checkpoint_resume_transfer_workorders(",
        "\nSyncValidationResult select_sync_session_checkpoint_resume_transfer_workorder_queue(",
    )

    require("class SyncSqliteManifestChunkSubsetVerifier final" in header,
            "owner_is_final", "the extracted verifier cannot be subclassed")
    require(header.count("= delete;") >= 4,
            "owner_is_noncopyable_nonmovable",
            "copy and move construction/assignment are deleted")
    require("SyncSqliteStmt chunk_probe_;" in header and
            header.count("SyncSqliteStmt") == 1,
            "owner_has_one_statement_capability",
            "one exact-generation statement owns the point-probe capability")
    require("std::span<const SyncChunkRange> required_chunks" in header,
            "caller_subset_is_borrowed",
            "the verifier does not copy the selected chunk vector")
    require("kSyncManifestChunkSubsetEvidenceBytesPerRow = 88U" in header,
            "metadata_budget_includes_ordinal",
            "offset, length, digest text, and persisted ordinal total 88 bytes")
    require("max_manifest_rows" in header and "max_required_rows" in header and
            "max_required_metadata_bytes" in header and
            "max_required_chunk_bytes" in header,
            "four_dimensional_limits_are_typed",
            "manifest, selected-row, selected-metadata, and payload ceilings are explicit")
    require("owner_generation() const noexcept" in header,
            "exact_generation_is_observable",
            "tests and callers can compare the retained owner generation")

    require("FROM main.sync_session_manifest_chunks" in owner,
            "durable_query_is_main_qualified",
            "TEMP-first name resolution cannot redirect the point proof")
    require("AND chunk_offset=?" in owner,
            "query_is_exact_offset_probe",
            "each selected chunk is addressed by its planner-frozen offset")
    require("LIMIT 2;" in owner,
            "duplicate_sentinel_is_bounded",
            "uniqueness proof can consume at most two rows")
    require("ORDER BY" not in section(owner, "SELECT chunk_offset", "prepare\"))"),
            "point_probe_has_no_sort",
            "the primary point proof does not build an attacker-sized sort")
    require("borrow_sync_sqlite_serialized_db_or_throw" not in owner and
            "sqlite_prepare_or_throw(\n          db," in owner,
            "statement_uses_typed_prepare",
            "the support layer retains the exact serialized database generation")
    require("all chunk subset limits must be positive" in owner and
            "required-row limit exceeds manifest-row limit" in owner,
            "limit_shape_fails_closed",
            "zero and incoherent policy values are rejected")
    require("sync_id_is_valid(session_id)" in verify_body and
            "validate_sync_relative_path(normalized_path)" in verify_body,
            "identity_and_path_are_prevalidated",
            "portable authority fields are validated before data access")
    require("required_rows > expected_manifest_rows" in verify_body and
            "expected_manifest_rows > limits.max_manifest_rows" in verify_body,
            "frozen_row_count_bounds_subset",
            "selected and persisted cardinalities cannot exceed policy")
    require("required_metadata_bytes > limits.max_required_metadata_bytes" in verify_body,
            "metadata_ceiling_precedes_probe",
            "selected metadata is rejected before any point query")
    require("required.offset > sqlite_i64_max" in preflight,
            "sqlite_key_range_is_preflighted",
            "all point keys are representable before the first bind")
    require("required.length > sqlite_i64_max" in preflight,
            "sqlite_length_range_is_preflighted",
            "persisted lengths are representable before the first data step")
    require("required.length == 0" in preflight and
            "is_lowercase_sha256_hex(required.sha256)" in preflight,
            "chunk_shape_is_preflighted",
            "length and canonical digest checks cover the complete caller subset")
    require("required.length >" in preflight and
            "max() - required.offset" in preflight and
            "max() -\n                required_chunk_bytes" in preflight,
            "uint64_arithmetic_is_checked",
            "chunk end and aggregate payload additions fail before overflow")
    require("required.offset < previous_end" in preflight,
            "caller_order_and_overlap_are_preflighted",
            "selected offsets must be ordered and nonoverlapping")
    require("required_chunk_bytes > limits.max_required_chunk_bytes" in preflight,
            "payload_ceiling_is_incremental_preflight",
            "the aggregate selected payload cannot cross policy")
    require(verify_body.find("SyncSqliteManifestChunkSubsetEvidence evidence;") <
            verify_body.find("sqlite3_step(chunk_probe_.stmt)"),
            "all_preflight_precedes_first_step",
            "evidence initialization occurs only after complete caller preflight")
    require("sqlite_bind_text_or_throw" in probe_loop and
            "sqlite_bind_u64_or_throw" in probe_loop,
            "probe_binds_exact_identity",
            "session, path, and offset are parameterized")
    require(probe_loop.count("sqlite_column_u64_or_throw") >= 3 and
            "kSyncManifestSha256TextBytes" in probe_loop,
            "persisted_scalars_use_exact_bounded_decoders",
            "integer storage classes and the 64-byte digest ceiling are enforced")
    require("stored_sha256 != required.sha256" in probe_loop and
            "stored_length != required.length" in probe_loop,
            "row_must_exactly_match_selected_value",
            "offset-key lookup alone is not treated as authority")
    require("stored_index >= expected_manifest_rows" in probe_loop,
            "ordinal_is_inside_frozen_cardinality",
            "valid persisted ordinals are limited to [0,count)")
    require("stored_index <= previous_stored_index" in probe_loop,
            "persisted_ordinals_are_strictly_monotone",
            "sparse selected offsets preserve manifest order")
    require("trailing_rc == SQLITE_ROW" in probe_loop and
            "point probe is not unique" in probe_loop,
            "second_row_revokes_authority",
            "duplicate durable evidence is detected")
    require("catch (...)" in probe_loop and
            "reset_and_clear_noexcept(chunk_probe_.stmt)" in probe_loop,
            "failure_cleans_reusable_statement",
            "exceptional exits do not strand bindings or row state")

    for name, body in (("claim", claim), ("execute", execute)):
        require(bool(body), f"{name}_section_located",
                f"the {name} integration section was found")
        require("SyncSqliteManifestChunkSubsetVerifier manifest_subset_verifier" in body,
                f"{name}_uses_extracted_owner",
                f"{name} delegates selected-row persistence proof")
        require("e.chunk_count" in body and "source_chunk_count" in body,
                f"{name}_freezes_persisted_chunk_count",
                f"{name} binds point ordinals to the manifest entry cardinality")
        require("FROM main.sync_session_apply_intents" in body and
                "JOIN main.sync_session_manifest_entries" in body,
                f"{name}_evidence_query_is_main_qualified",
                f"{name} cannot read TEMP-shadowed apply or entry evidence")
        require("sync_manifest_default_resource_limits().max_chunks_per_entry" in body,
                f"{name}_inherits_manifest_row_policy",
                f"{name} does not invent a larger persistent cardinality ceiling")
        require("planned.peer_assigned_chunks" in body and
                "planned.peer_assigned_bytes" in body,
                f"{name}_limits_are_exact_plan_summaries",
                f"{name} budgets the already-authorized subset, not the full manifest")
        require("verify_source_chunks_or_throw" in body,
                f"{name}_executes_point_proof",
                f"{name} verifies selected rows before mutation or byte transfer")
        require("std::vector<SyncChunkRange> manifest_chunks" not in body and
                f"resume transfer {name if name == 'claim' else 'executor'} chunk prepare" not in body,
                f"{name}_full_materialization_removed",
                f"{name} no longer copies every persisted chunk")
        require("kSyncCheckpointIdempotencyKeyMaxBytes" in body and
                "kSyncCheckpointAbsolutePathMaxBytes" in body and
                "kSyncManifestSha256TextBytes" in body,
                f"{name}_adjacent_text_evidence_is_bounded",
                f"{name} bounds keys, paths, and digests while decoding")
        require(body.find("verify_source_chunks_or_throw") <
                body.find("chunk_ranges_are_ordered_unique_subset_of(planned.chunks_to_request"),
                f"{name}_durable_proof_precedes_plan_subset_check",
                f"{name} verifies persistence before consuming the planner relation")

    require("CREATE TEMP TABLE sync_session_manifest_chunks" in focused and
            "main binding ignores malicious TEMP shadow" in focused,
            "focused_test_covers_temp_shadow",
            "an executable regression distinguishes main from TEMP")
    require("duplicate point evidence" in focused and "not unique" in focused,
            "focused_test_covers_duplicate_sentinel",
            "a fixture without the production primary key proves bounded duplicate rejection")
    require("wrong_storage_class" in focused,
            "focused_test_covers_exact_storage_class",
            "TEXT masquerading as an integer is rejected")
    require("statement is reusable after missing-row rejection" in focused and
            "owner remains reusable after duplicate-row rejection" in focused,
            "focused_test_covers_failure_reuse",
            "cleanup is exercised after independent failure modes")
    require("offset exceeds SQLite integer range" in owner and
            "unrepresentable point key" in focused,
            "focused_test_covers_complete_key_preflight",
            "a late unbindable key is rejected before probing")
    require("length exceeds SQLite integer range" in owner and
            "unrepresentable stored length" in focused,
            "focused_test_covers_complete_length_preflight",
            "an impossible persisted length is rejected before probing")
    require("owner_generation() == db.db.generation()" in focused,
            "focused_test_covers_generation_pin",
            "the owner reports the exact database incarnation it retains")
    require("metadata accounting rejects uint64 overflow" in focused and
            "selected payload ceiling is enforced" in focused,
            "focused_test_covers_resource_arithmetic",
            "metadata multiplication and payload accumulation are adversarially checked")

    require("add_library(anonsync_sync_sqlite_manifest_chunk_subset STATIC" in cmake and
            "anonsync_sync_sqlite_manifest_chunk_subset_test" in cmake,
            "cmake_builds_owner_and_test",
            "the extracted production owner and corpus are separate targets")
    require("ANONSYNC_SYNC_SQLITE_MANIFEST_CHUNK_SUBSET_SOURCE" in cmake and
            "anonsync_sync_sqlite_manifest_chunk_subset\n    anonsync_sync_manifest_identity" in cmake,
            "core_links_extracted_owner",
            "the monolith consumes the separately linked invariant owner")
    require("anonsync_sync_sqlite_manifest_chunk_subset_source_audit" in cmake and
            "${Python3_EXECUTABLE} -B -S" in section(
                cmake,
                "add_test(NAME anonsync_sync_sqlite_manifest_chunk_subset_source_audit",
                "add_test(NAME anonsync_sync_manifest_identity_source_audit"),
            "audit_is_registered_without_site_initialization",
            "CTest runs this audit with reduced ambient Python state")
    require("revision_number >= 860" in verifier and
            all(path in verifier for path in (
                "src/sync_sqlite_manifest_chunk_subset.hpp",
                "src/sync_sqlite_manifest_chunk_subset.cpp",
                "tests/sync_sqlite_manifest_chunk_subset_test.cpp",
                "tools/audit_sync_sqlite_manifest_chunk_subset.py",
            )),
            "release_verifier_requires_rev0860_boundary",
            "future packages cannot silently omit the extracted owner or its proofs")

    metrics = {
        "owner_lines": len(owner.splitlines()),
        "focused_test_lines": len(focused.splitlines()),
        "claim_full_manifest_vector_occurrences": claim.count(
            "std::vector<SyncChunkRange> manifest_chunks"),
        "execute_full_manifest_vector_occurrences": execute.count(
            "std::vector<SyncChunkRange> manifest_chunks"),
        "point_probe_step_occurrences": owner.count("sqlite3_step(chunk_probe_.stmt)"),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
