#!/usr/bin/env python3
"""Lexical release audit for rev1020 bounded rename planning.

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
    Path("BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md"),
    Path("REVISION_NOTES_rev1020.md"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_folder_scan_owner_test.cpp"),
    Path("tools/audit_sync_replica_bounded_rename_planning.py"),
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
            "format": "anonsync-bounded-rename-planning-audit-v1",
            "root": str(root),
            "checks": [asdict(check) for check in checks],
            "passed": passed,
            "total": len(checks),
        }, sort_keys=True))
    else:
        for check in checks:
            print(f"[{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.detail}")
        print(f"bounded rename planning audit: {passed}/{len(checks)} checks passed")
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
    sqlite_h = text["src/sync_replica_sqlite_owner.hpp"]
    sqlite_c = text["src/sync_replica_sqlite_owner.cpp"]
    folder_c = text["src/sync_replica_folder_scan_owner.cpp"]
    sqlite_test = text["tests/sync_replica_sqlite_owner_test.cpp"]
    folder_test = text["tests/sync_replica_folder_scan_owner_test.cpp"]
    cmake = text["CMakeLists.txt"]
    design = text["BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md"]
    notes = text["REVISION_NOTES_rev1020.md"]
    readme = text["README.md"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_replica_bounded_rename_planning.py"]

    require(
        "constexpr std::uint64_t kVisiblePathSchemaVersion = 8U" in sqlite_c
        and "constexpr std::uint64_t kSchemaVersion = 9U" in sqlite_c
        and "sync_replica_visible_file_content" in sqlite_c,
        "replica_schema_has_exact_v8_source_and_v9_content_projection",
        "the current-visible content index is an explicit schema migration",
    )
    require(
        "INDEXED BY sync_replica_visible_file_content" in sqlite_c
        and "ORDER BY canonical_path,visible_ordinal LIMIT 2" in sqlite_c,
        "replica_content_lookup_forces_named_index_and_two_row_bound",
        "absent, sole, and ambiguous results cannot materialize an unbounded match set",
    )
    require(
        "struct SyncReplicaSqliteVisibleFileContentCutpoint final" in sqlite_h
        and "sole_visible_file_operation" in sqlite_h
        and "bool ambiguous = false" in sqlite_h,
        "replica_content_lookup_has_typed_bounded_result",
        "one exact operation is distinguished from two-or-more ambiguity",
    )
    require(
        "visible content projection disagrees with active evidence" in sqlite_c
        and "read_exact_operation_row_or_none_or_throw" in sqlite_c,
        "replica_content_projection_is_rebound_to_immutable_operation",
        "normalized values are acceleration rather than independent authority",
    )
    require(
        "test_exact_v8_migration_builds_visible_content_index" in sqlite_test
        and "test_visible_file_content_cutpoint_is_bounded_and_exact" in sqlite_test
        and "visible content lookup trusted a forged normalized projection" in sqlite_test,
        "replica_runtime_covers_migration_restart_ambiguity_and_forgery",
        "the exact prior schema and direct public content cutpoint are executable",
    )
    require(
        "bounded_conflict_visible_operations" in sqlite_h
        and "requested_retained_operation_bounded_conflict_index" in sqlite_h
        and "conflict.bounded_conflict_visible_operations.size() == 2U" in sqlite_test,
        "targeted_path_cutpoint_preserves_two_head_displayed_candidate",
        "bounded conflict adoption does not restore unrelated retained history",
    )
    require(
        "read_visible_file_content_cutpoint_or_throw" in sqlite_c
        and "verify_streamed_visible_projection_witness_or_throw" in sqlite_c
        and "load_state_or_throw" not in sqlite_c.split(
            "publish_local_identity_preserving_rename_from_observed_heads_or_throw", 2
        )[-1].split("SyncReplicaSqliteOwner::", 1)[0],
        "rename_publication_is_targeted_and_history_cold",
        "targeted paths and indexed content replace complete retained-model restore",
    )
    require(
        "verify_streamed_visible_projection_witness_or_throw" in sqlite_c
        and "visible projection witness" in sqlite_test
        and "complete_operation_projection_read_count == 0U" in sqlite_test,
        "rename_publication_retains_streamed_global_corruption_fence",
        "current-visible integrity is O(N-visible) I/O without retained-history decode",
    )
    require(
        "constexpr std::uint64_t kSelectiveSyncSchemaVersion = 6U" in folder_c
        and "constexpr std::uint64_t kSchemaVersion = 7U" in folder_c
        and "sync_replica_folder_catalog_file_content" in folder_c,
        "catalog_schema_has_exact_v6_source_and_v7_content_projection",
        "catalog content lookup survives restart through an exact migration",
    )
    require(
        "INDEXED BY " in folder_c
        and "sync_replica_folder_catalog_file_content " in folder_c
        and "ORDER BY canonical_path,operation_id LIMIT 2" in folder_c,
        "catalog_content_lookup_forces_named_index_and_two_row_bound",
        "duplicate absent source candidates fail closed without whole-catalog materialization",
    )
    require(
        "kSelectiveSyncMetaSchemaSql" in folder_c
        and "kMetaSchemaSql" in folder_c
        and "rev0951 migration did not preserve the v4 cursor at v7 indexed sweep genesis" in folder_test
        and "migrated folder catalog did not attest schema version 7" in folder_test,
        "catalog_migration_preserves_exact_intermediate_v6_schema",
        "v5-to-v6 cannot claim one schema while creating another",
    )
    require(
        "struct StreamedCatalogContentProof final" in folder_c
        and "stream_catalog_content_proof_or_throw" in folder_c
        and "record_catalog_identity_preserving_rename_or_throw" in folder_c,
        "catalog_publication_uses_streamed_canonical_proof",
        "single-path and pair commits retain one row at a time instead of whole vectors",
    )
    require(
        "visible_file_content_cutpoint_or_throw" in folder_c
        and "targeted_path_cutpoint_or_throw" in folder_c
        and "find_unique_absent_identity_preserving_rename_source_or_none" in folder_c,
        "folder_one_file_planning_uses_path_and_content_cutpoints",
        "ordinary planning avoids complete catalog/model restoration",
    )
    require(
        "indexed_visible_content_lookup_count == 1U" in sqlite_test
        and "complete_visible_projection_read_count == 1U" in sqlite_test
        and "complete_operation_projection_read_count == 0U" in sqlite_test,
        "sqlite_trace_distinguishes_indexed_planning_from_publication_witness",
        "the remaining global read is explicit and no retained-operation projection is hidden",
    )
    require(
        "562 checks" not in design or "VALIDATION_PENDING_REV1020" in design,
        "design_does_not_preclaim_final_runtime_counts",
        "preseal prose cannot invent final validation evidence",
    )
    require(
        "anonsync_sync_replica_bounded_rename_planning_source_audit" in cmake
        and "audit_sync_replica_bounded_rename_planning.py" in cmake,
        "cmake_registers_focused_source_audit",
        "the complete test registry cannot omit the rev1020 boundary",
    )
    require(
        "BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md" in verifier
        and "audit_sync_replica_bounded_rename_planning.py" in verifier
        and "rev1020_bounded_rename" in structural,
        "release_policy_binds_design_runtime_audit_and_package",
        "the sealed archive must retain all reviewed rev1020 surfaces",
    )
    prose = normalized("\n".join((design, notes, readme, bootstrap)))
    require(
        all(token in prose for token in (
            "large media trees", "million-path", "path/content-indexed",
            "O(N-visible)", "O(N) I/O", "O(1) row memory", "regular-file",
            "directory", "conflict", "ENOSPC", "Android", "Tor", "I2P",
        )),
        "benefit_complexity_and_product_nonclaims_are_explicit",
        "bounded planning is not overstated as complete namespace or platform support",
    )
    require(
        "not a dense million-file throughput measurement" in normalized(design).lower()
        and "does not change the wire protocol" in normalized(design).lower(),
        "scale_and_wire_nonclaims_are_named",
        "the slice preserves protocol behavior and does not substitute inference for measurement",
    )
    require(
        all(token not in (design + notes + readme + bootstrap) for token in (
            "VALIDATION_PENDING_REV1020",
            "ARCHIVE_PENDING_REV1020",
            "CODENAME_PENDING_REV1020",
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
