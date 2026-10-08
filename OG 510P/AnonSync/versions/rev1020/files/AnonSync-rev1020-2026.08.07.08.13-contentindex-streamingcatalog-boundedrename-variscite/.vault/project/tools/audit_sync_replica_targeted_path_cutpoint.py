#!/usr/bin/env python3
"""Lexical audit for rev0989 targeted replica path/operation cutpoints.

This checks reviewed source and documentation shape. It is lexical hygiene, not
semantic proof: compiler, runtime, sanitizer, scale, reconstruction, and package
evidence remain load-bearing.
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
    Path("TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md"),
    Path("REVISION_NOTES_rev0989.md"),
    Path("src/anonsync_folder.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_folder_scan_owner_test.cpp"),
    Path("tools/audit_sync_replica_targeted_path_cutpoint.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def delimited_body(text: str, signature: str, opening: str = "{", closing: str = "}") -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    boundary = text.find(opening, start + len(signature))
    if boundary < 0:
        return ""
    depth = 0
    for index in range(boundary, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-targeted-replica-path-operation-cutpoint-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SQLite snapshot isolation, query "
            "complexity, allocator behavior, race freedom, filesystem authority, "
            "target-scale RSS, or crash recovery"
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
    design = text[
        "TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md"
    ]
    notes = text["REVISION_NOTES_rev0989.md"]
    sqlite_h = text["src/sync_replica_sqlite_owner.hpp"]
    sqlite_c = text["src/sync_replica_sqlite_owner.cpp"]
    folder_h = text["src/sync_replica_folder_scan_owner.hpp"]
    folder_c = text["src/sync_replica_folder_scan_owner.cpp"]
    sqlite_test = text["tests/sync_replica_sqlite_owner_test.cpp"]
    folder_test = text["tests/sync_replica_folder_scan_owner_test.cpp"]
    folder_cli = text["src/anonsync_folder.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_replica_targeted_path_cutpoint.py"]

    cutpoint_result = delimited_body(
        sqlite_h, "struct SyncReplicaSqliteTargetedPathCutpoint final"
    )
    targeted = delimited_body(
        sqlite_c, "SyncReplicaSqliteOwner::targeted_path_cutpoint_or_throw("
    )
    current_owner_meta = delimited_body(
        sqlite_c, "read_current_owner_meta_or_throw("
    )
    exact_operation = delimited_body(
        sqlite_c, "read_exact_operation_row_or_none_or_throw("
    )
    shared_decoder = delimited_body(
        sqlite_c, "load_stored_operation_row_or_throw("
    )
    convergence = delimited_body(
        folder_c, "SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw("
    )
    start = convergence.find("const auto dematerialize_metadata_only_file_or_throw")
    end = convergence.find("bool completed_selected_remote_apply", start)
    dematerialization = convergence[start:end] if start >= 0 and end >= 0 else ""

    require(
        "anonsync_sync_replica_targeted_path_cutpoint_source_audit" in cmake
        and "tools/audit_sync_replica_targeted_path_cutpoint.py" in cmake,
        "focused_audit_is_registered",
        "the rev0989 lexical audit is in the ordinary CTest registry",
    )
    require(
        "sole_visible_operation" in cutpoint_result
        and "distinct_retained_operation" in cutpoint_result
        and "state_generation" not in cutpoint_result
        and "policy_generation" not in cutpoint_result
        and "visible_state_digest" not in cutpoint_result
        and "cutpoint_digest" not in cutpoint_result,
        "cutpoint_owns_only_path_local_operations",
        "the public result cannot masquerade stored global metadata as a fresh aggregate proof",
    )
    require(
        "requested_retained_operation_is_sole_visible" in sqlite_h
        and "requested_retained_operation_or_none()" in sqlite_h,
        "same_operation_uses_single_owned_envelope",
        "the usual target-equals-catalog-head case avoids a second envelope copy",
    )
    require(
        "SyncSqliteTransactionMode::Deferred" in targeted
        and "read_current_owner_meta_or_throw(" in targeted
        and "verify_schema_or_throw(" in current_owner_meta
        and "require_foreign_keys_or_throw(" in current_owner_meta
        and "read_meta_or_throw(" in current_owner_meta
        and "require_snapshot_authority_or_throw(" in targeted,
        "targeted_rows_share_one_pinned_read_snapshot",
        "the path reader reaches the centralized schema, foreign-key, and metadata reproof while exact rows remain pinned without a writer lease",
    )
    require(
        'FROM main.sync_replica_visible WHERE canonical_path=? ' in targeted
        and "ORDER BY visible_ordinal LIMIT 2;" in targeted,
        "visible_query_is_exact_and_conflict_bounded",
        "one indexed path and at most two visible rows decide sole visibility",
    )
    require(
        "WHERE operation_id=?;" in exact_operation
        and "ORDER BY operation_id" not in exact_operation,
        "operation_query_is_primary_key_exact",
        "retained evidence lookup does not project total history",
    )
    require(
        "load_stored_operation_row_or_throw(" in exact_operation
        and sqlite_c.count("load_stored_operation_row_or_throw(") >= 3,
        "complete_and_targeted_reads_share_operation_decoder",
        "one canonical operation-row codec serves both query shapes",
    )
    require(
        "decode_sync_replica_operation_canonical_or_throw" in shared_decoder
        and "canonical operation row attestation mismatch" in shared_decoder
        and "evidence_state" in shared_decoder,
        "shared_decoder_attests_bytes_identity_charges_and_state",
        "the exact query does not trust redundant row columns",
    )
    require(
        "stored->evidence_state != SyncReplicaEvidenceState::Active" in targeted
        and "stored->operation.folder_id != folder_id_" in targeted
        and "stored->operation.canonical_path != canonical_path" in targeted,
        "sole_visible_operation_is_active_and_path_bound",
        "a visible row alone cannot manufacture current file authority",
    )
    require(
        "!row.is_primary || row.preserve_file" in targeted
        and "visible_row_count == 1U" in targeted,
        "sole_visible_flags_are_reproved",
        "primary and preservation semantics remain explicit",
    )
    require(
        "visible_rows[0].operation_id" in targeted
        and "visible_row_count >= visible_rows.size()" in targeted,
        "visible_rows_are_canonical_and_sql_limit_is_defended",
        "duplicate identities, bad ordinals, and limit drift fail closed",
    )
    require(
        targeted.count("read_current_owner_meta_or_throw(") == 1
        and current_owner_meta.count("verify_schema_or_throw(") == 1
        and current_owner_meta.count("require_foreign_keys_or_throw(") == 1
        and current_owner_meta.count("read_meta_or_throw(") == 1,
        "per_path_cutpoint_reproves_fixed_schema_authority",
        "the centralized exact schema, foreign-key, and metadata reproof runs once while history work remains bounded",
    )
    require(
        dematerialization.count("require_targeted_replica_path_cutpoint_or_throw(") >= 2
        and '"dematerialization planning reproof"' in dematerialization
        and '"pre-unlink reproof"' in dematerialization
        and '"post-unlink reproof"' in dematerialization,
        "rooted_removal_is_bracketed_by_three_targeted_replica_cutpoints",
        "planning, pre-effect, and post-effect causal authority are path-local",
    )
    require(
        "replica_owner->snapshot_or_throw()" not in dematerialization
        and "SyncReplicaModel::restore_or_throw(" not in dematerialization,
        "dematerialization_no_longer_reconstructs_complete_history",
        "the optimized effect path cannot regress through a thin full-snapshot wrapper",
    )
    require(
        "remote_targeted_replica_path_cutpoint_count" in folder_h
        and "remote_targeted_replica_path_cutpoint_count" in folder_c,
        "targeted_replica_cutpoints_are_counted",
        "operators can distinguish exact causal reproof from complete snapshots",
    )
    require(
        "remote_targeted_replica_path_cutpoints" in folder_cli
        and "remote_targeted_replica_path_cutpoints" in sync_cli,
        "shipping_json_exposes_targeted_replica_work",
        "low-level and configured convergence diagnostics remain aligned",
    )
    require(
        "struct TargetedReplicaReadTrace final" in sqlite_test
        and "exact_visible_path_read_count" in sqlite_test
        and "complete_visible_projection_read_count" in sqlite_test
        and "schema_catalog_read_count" in sqlite_test
        and "foreign_key_pragma_count" in sqlite_test,
        "sqlite_owner_oracle_distinguishes_all_query_shapes",
        "the direct owner test observes exact, complete, and schema reads",
    )
    require(
        "test_targeted_path_cutpoint_is_exact_and_path_bounded" in sqlite_test
        and "test_targeted_path_cutpoint_is_exact_and_history_bounded" in sqlite_test
        and "for (std::size_t index = 0U; index < 32U; ++index)" in sqlite_test,
        "direct_oracle_covers_path_and_history_cases",
        "unrelated retained history cannot hide a complete projection",
    )
    require(
        "trace.exact_operation_read_count == 2U" in sqlite_test
        and "sole_trace.exact_operation_read_count == 1U" in sqlite_test
        and "complete_operation_projection_read_count == 0U" in sqlite_test
        and "schema_catalog_read_count == 1U" in sqlite_test
        and "foreign_key_pragma_count == 1U" in sqlite_test,
        "direct_oracle_proves_bounded_rows_and_one_schema_reproof",
        "same-identity and distinct-predecessor cases retain exact fixed authority checks",
    )
    require(
        "test_selective_sync_dematerialization_reproof_is_path_local" in folder_test
        and "3U * kPathCount" in folder_test
        and "remote_targeted_replica_path_cutpoint_count" in folder_test,
        "folder_oracle_proves_three_exact_cutpoints_per_effect",
        "the correction is tested across an eight-file batch",
    )
    require(
        "replica_trace.complete_visible_projection_read_count <= 4U" in folder_test
        and "replica_trace.complete_operation_projection_read_count <= 4U" in folder_test,
        "folder_oracle_keeps_complete_replica_projections_pass_bounded",
        "global observations no longer scale with effect count",
    )
    require(
        "12,288 complete replica snapshots" in design
        and "122,880,000 retained operation-row decodes" in design
        and "4,096 remote effects" in design
        and "10,000 retained operation envelopes" in design,
        "audit_quantifies_removed_production_multiplier",
        "the correction is tied to exact production scheduling and model frontiers",
    )
    require(
        "at most two operation envelopes" in design
        and "4 MiB" in design
        and "usual target-equals-catalog-head" in design,
        "audit_states_bounded_transient_memory_and_single_copy_case",
        "the new projection claim names its remaining envelope frontier",
    )
    require(
        "does not claim to recompute" in design
        and "Complete replica snapshots remain" in design
        and "not\nsemantic proof" in design,
        "path_local_nonclaim_and_evidence_boundary_are_explicit",
        "targeted reads are not mislabeled as global replica authority",
    )
    require(
        "TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md" in verifier
        and "REVISION_NOTES_rev0989.md" in verifier
        and "audit_sync_replica_targeted_path_cutpoint.py" in verifier,
        "release_verifier_requires_rev0989_chain",
        "a package cannot omit implementation, audit, or revision record",
    )
    require(
        "rev0989" in readme.lower()
        and "targeted replica" in bootstrap.lower(),
        "visible_product_pages_name_current_slice",
        "restart context no longer points at the removed history multiplier",
    )
    require(
        "VALIDATION_PENDING_REV0989" not in notes
        and "ARCHIVE_PENDING_REV0989" not in notes
        and "VALIDATION_PENDING_REV0989" not in design
        and "ARCHIVE_PENDING_REV0989" not in design
        and "VALIDATION_PENDING_REV0989" not in readme
        and "ARCHIVE_PENDING_REV0989" not in readme
        and "VALIDATION_PENDING_REV0989" not in bootstrap
        and "ARCHIVE_PENDING_REV0989" not in bootstrap,
        "final_validation_and_archive_identity_are_sealed",
        "the audit remains release-gated until exact evidence and filename are final",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not\nsemantic proof" in self_text
        and "runtime, sanitizer, scale, reconstruction, and package" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "source spelling cannot substitute for executable or package evidence",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
