#!/usr/bin/env python3
"""Lexical release audit for regular-file identity continuation through rev1020.

Source spelling is not semantic proof. Compiler, sanitizer, runtime,
reconstruction, and package evidence remain load-bearing.
lexical-hygiene-not-semantic-proof
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md"),
    Path("REVISION_NOTES_rev1019.md"),
    Path("src/sync_replica_model.hpp"),
    Path("src/sync_replica_model.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("src/anonsync_folder.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("tests/sync_replica_network_model_test.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_folder_scan_owner_test.cpp"),
    Path("tools/audit_sync_replica_identity_preserving_rename.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def normalized(text: str) -> str:
    return " ".join(text.split())


def emit(root: Path, json_output: bool, checks: list[Check]) -> int:
    passed = sum(check.passed for check in checks)
    if json_output:
        print(json.dumps({
            "format": "anonsync-identity-preserving-regular-file-rename-audit-v2",
            "root": str(root),
            "checks": [asdict(check) for check in checks],
            "passed": passed,
            "total": len(checks),
        }, sort_keys=True))
    else:
        for check in checks:
            print(f"[{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.detail}")
        print(f"identity-preserving rename audit: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    checks: list[Check] = []

    def require(condition: bool, name: str, detail: str) -> None:
        checks.append(Check(name, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in bootstrap_candidates if path.is_file()), None)
    require(bootstrap_path is not None, "bootstrap_exists", "release-root runbook is visible")
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    model_h = text["src/sync_replica_model.hpp"]
    model_c = text["src/sync_replica_model.cpp"]
    sqlite_h = text["src/sync_replica_sqlite_owner.hpp"]
    sqlite_c = text["src/sync_replica_sqlite_owner.cpp"]
    folder_h = text["src/sync_replica_folder_scan_owner.hpp"]
    folder_c = text["src/sync_replica_folder_scan_owner.cpp"]
    network_test = text["tests/sync_replica_network_model_test.cpp"]
    sqlite_test = text["tests/sync_replica_sqlite_owner_test.cpp"]
    folder_test = text["tests/sync_replica_folder_scan_owner_test.cpp"]
    cmake = text["CMakeLists.txt"]
    design = text["IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md"]
    notes = text["REVISION_NOTES_rev1019.md"]
    readme = text["README.md"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_replica_identity_preserving_rename.py"]

    require(
        "struct SyncReplicaIdentityPreservingRename final" in model_h
        and "identity_preserving_rename_for_source_tombstone" in model_h
        and "transport-only rename flag" in model_h,
        "model_exposes_wire_compatible_identity_continuation",
        "the public type is inferred from ordinary immutable evidence",
    )
    require(
        "source_tombstone->predecessor_operation_ids.size() != 1U" in model_c
        and "source_tombstone->dot.counter !=" in model_c
        and "destination_file->dot.counter + 1U" in model_c
        and "sync_replica_context_covers_dot" in model_c,
        "model_requires_exact_consecutive_causal_shape",
        "actor, counter, context, and sole predecessor are all checked",
    )
    require(
        "sole_matching_file" in model_c
        and "visible_operation_ids.size() != 1U" in model_c
        and "sole_matching_file != nullptr" in model_c,
        "model_rejects_historical_duplicate_content_ambiguity",
        "one exact visible source File must be unique in the observed namespace",
    )
    require(
        "copy followed by deletion" in model_h
        and "not proof of a particular filesystem rename syscall" in model_h,
        "model_names_copy_delete_nonclaim",
        "causal continuity is not overstated as rename(2) evidence",
    )
    require(
        "SyncReplicaSqliteLocalRenamePublicationResult" in sqlite_h
        and "publish_local_identity_preserving_rename_from_observed_heads_or_throw" in sqlite_h,
        "sqlite_owner_has_typed_atomic_pair_api",
        "destination File, source Tombstone, identity, generation, and cutpoint are returned together",
    )
    require(
        "publish_local_identity_preserving_rename_from_observed_heads_or_throw" in sqlite_c
        and "SyncSqliteTransactionMode::Immediate" in sqlite_c
        and "const SyncReplicaOperation destination_file" in sqlite_c
        and "const SyncReplicaOperation source_tombstone" in sqlite_c,
        "sqlite_owner_publishes_two_operations_in_one_immediate_transaction",
        "both operations are staged before one durable commit",
    )
    require(
        "final_meta.state_generation = destination_meta.state_generation" in sqlite_c
        and "transaction.commit();" in sqlite_c,
        "sqlite_pair_advances_one_generation",
        "the generalized publication helper commits one exact state transition",
    )
    require(
        "record_catalog_identity_preserving_rename_or_throw" in folder_c
        and "SyncSqliteTransactionMode::Immediate" in folder_c
        and "source_tombstone.last_seen_generation = generation" in folder_c
        and "destination_file.last_seen_generation = generation" in folder_c,
        "catalog_records_pair_in_one_transaction",
        "both exact catalog values share one catalog generation",
    )
    require(
        "find_unique_absent_identity_preserving_rename_source_or_none" in folder_c
        and "catalog_content.ambiguous || replica_content.ambiguous" in folder_c
        and "!catalog_content.sole_file_entry.has_value()" in folder_c
        and "!replica_content.sole_visible_file_operation.has_value()" in folder_c
        and "return std::nullopt;" in folder_c,
        "folder_planning_fences_current_visible_ambiguity",
        "both bounded content indexes must return one exact absent source before effects",
    )
    require(
        "local rename source selective-sync authority changed" in folder_c
        and "rename destination durability reproof" in folder_c
        and "local rename source terminal reproof" in folder_c,
        "folder_reproves_selection_durability_and_rooted_absence",
        "both path authorities remain exact immediately before publication",
    )
    require(
        "published_identity_preserving_rename" in folder_h
        and "local_identity_preserving_rename_count" in folder_h
        and "local_identity_preserving_rename_count" in folder_c,
        "pass_reports_identity_continuation",
        "the shipping pass distinguishes identity-preserving publication from ordinary files",
    )
    require(
        "local_identity_preserving_renames" in text["src/anonsync_folder.cpp"]
        and "local_identity_preserving_renames" in text["src/anonsync_sync.cpp"],
        "shipping_json_exposes_rename_count",
        "folder and once/share JSON use the same exact counter",
    )
    require(
        "identity_preserving_rename_for_source_tombstone" in network_test
        and "duplicate visible content" in network_test
        and "content-changing" in network_test,
        "model_runtime_covers_restart_and_ambiguity",
        "wire-compatible inference has positive and negative controls",
    )
    require(
        "test_atomic_identity_preserving_rename_publication" in sqlite_test
        and "second-operation capacity failure exposed a partial rename" in sqlite_test,
        "sqlite_runtime_proves_atomic_capacity_failure",
        "the destination half cannot escape when the tombstone crosses capacity",
    )
    rename_method = sqlite_c.split(
        "publish_local_identity_preserving_rename_from_observed_heads_or_throw", 2
    )[-1].split("SyncReplicaSqliteOwner::", 1)[0]
    require(
        "read_targeted_path_history_cutpoint_or_throw" in rename_method
        and "read_active_causal_head_operations_or_throw" in rename_method
        and "require_unique_visible_file_content_source_or_throw" in rename_method
        and "load_state_or_throw" not in rename_method,
        "sqlite_pair_publication_is_history_cold",
        "the final transaction uses targeted paths, bounded causal heads, and one streaming uniqueness scan",
    )
    require(
        "streamed_visible_content_scan_count == 0U" in sqlite_test
        and "indexed_visible_content_lookup_count == 1U" in sqlite_test
        and "complete_visible_projection_read_count == 1U" in sqlite_test
        and "complete_operation_projection_read_count == 0U" in sqlite_test,
        "sqlite_runtime_proves_no_complete_history_projection",
        "rename publication uses one indexed content lookup and one streamed current-visible witness without retained-history reconstruction",
    )
    visible_witness_helper = sqlite_c.split(
        "void verify_streamed_visible_projection_witness_or_throw", 1
    )[-1].split(
        "void require_unique_visible_file_content_source_or_throw", 1
    )[0]
    require(
        "sync_replica_digest_accumulator_zero" in visible_witness_helper
        and "sync_replica_visible_path_accumulator_element_digest_or_throw" in visible_witness_helper
        and "path_count != meta.visible_path_count" in visible_witness_helper
        and "accumulator != meta.visible_state_digest" in visible_witness_helper,
        "sqlite_uniqueness_scan_reproves_complete_visible_projection_witness",
        "the streamed current-visible witness cannot infer uniqueness from a missing or malformed visible row",
    )
    require(
        "missing duplicate visible row manufactured rename uniqueness" in sqlite_test
        and "visible projection witness" in sqlite_test
        and "projection-drift rejection changed replica state" in sqlite_test,
        "sqlite_runtime_rejects_missing_duplicate_projection_row",
        "projection damage fails before either rename operation can publish",
    )
    require(
        "test_identity_preserving_regular_file_rename_is_atomic_and_restart_stable" in folder_test
        and "test_convergence_pass_reports_one_identity_preserving_rename" in folder_test
        and "identity-preserving rename duplicated immutable payload storage" in folder_test,
        "folder_runtime_proves_direct_pass_restart_and_single_payload",
        "one exact payload and one rename pair remain stable across owner restart",
    )
    require(
        "targeted_payload_reuse" in folder_h
        and "begin_targeted_access_or_throw" in folder_c
        and "direct retained payload reuse" in folder_c
        and "targeted retained payload proof" in folder_c
        and "targeted_payload_reuse" in folder_test,
        "direct_scan_reuses_exact_retained_payload",
        "direct exact-content rename and no-op scans expose that descriptor admission was skipped",
    )
    require(
        "std::optional<SyncReplicaFilePayloadStoreTargetedAccess>" in folder_c
        and "std::optional<SyncReplicaFilePayloadStoreOpenedPayload>" in folder_c
        and "targeted_payload_access.reset();" in folder_c
        and "targeted_payload_reuse};" in folder_c,
        "targeted_reuse_capability_spans_publication",
        "the exact targeted owner and inode lease outlive both database publication cutpoints",
    )
    require(
        "test_identity_preserving_rename_replica_pair_survives_catalog_crash_window" in folder_test
        and "Deliberately abandon the scanner before the two-path catalog commit" in folder_test
        and "without republishing or duplicating payload bytes" in folder_test,
        "folder_runtime_proves_replica_first_catalog_recovery",
        "restart adopts both durable path effects after the cross-database cutpoint",
    )
    require(
        "test_present_same_content_duplicate_falls_back_before_rename_publication" in folder_test
        and "test_ambiguous_same_content_absence_does_not_invent_rename_identity" in folder_test,
        "folder_runtime_proves_both_ambiguity_fallbacks",
        "same-content current and absent aliases cannot invent identity",
    )
    require(
        "anonsync_sync_replica_identity_preserving_rename_source_audit" in cmake
        and "audit_sync_replica_identity_preserving_rename.py" in cmake,
        "cmake_registers_focused_source_audit",
        "the complete registry cannot omit the rev1019 policy check",
    )
    require(
        "IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md" in verifier
        and "audit_sync_replica_identity_preserving_rename.py" in verifier
        and "rev1019_identity_preserving_regular_file_rename" in structural,
        "release_policy_binds_code_tests_design_and_audit",
        "the package and structural gates require every reviewed surface",
    )
    prose = normalized("\n".join((design, notes, readme, bootstrap)))
    require(
        all(token in prose for token in (
            "regular file", "causal identity continuity", "copy", "delete",
            "one catalog generation", "one replica generation", "payload",
            "cross-database", "O(active evidence", "directory", "conflict",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "benefit_and_nonclaims_are_explicit",
        "the rename slice is not overstated as complete filesystem semantics",
    )
    require(
        "does not add a new transport" in normalized(design).lower()
        and "regular files only" in design
        and "million-file rename throughput proof" in normalized(design),
        "wire_scope_and_scale_limits_are_named",
        "protocol compatibility and unmeasured namespace cost remain explicit",
    )
    require(
        all(token not in (design + notes + readme + bootstrap) for token in (
            "VALIDATION_PENDING_REV1019",
            "ARCHIVE_PENDING_REV1019",
            "CODENAME_PENDING_REV1019",
        )),
        "final_validation_and_release_cutpoint_are_sealed",
        "one deliberate preseal failure remains until exact publication facts are final",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text
        and "Compiler, sanitizer, runtime" in self_text,
        "focused_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
