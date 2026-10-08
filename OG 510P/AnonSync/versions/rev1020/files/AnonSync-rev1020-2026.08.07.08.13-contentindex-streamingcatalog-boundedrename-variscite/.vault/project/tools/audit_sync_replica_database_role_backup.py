#!/usr/bin/env python3
"""Lexical audit for role-bound offline SQLite backup.

This source-shape audit is not semantic proof. Runtime, sanitizer,
reconstruction, and package evidence remain load-bearing.
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
    Path("ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md"),
    Path("REVISION_NOTES_rev0985.md"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_database_backup.hpp"),
    Path("src/sync_replica_database_backup.cpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("src/sync_replica_tls_policy_sqlite_profile.hpp"),
    Path("src/sync_replica_tls_policy_sqlite_profile.cpp"),
    Path("src/sync_replica_tls_membership_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_membership_sqlite_owner.cpp"),
    Path("src/sync_replica_tls_membership_anchor_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_membership_anchor_sqlite_owner.cpp"),
    Path("tools/test_anonsync_database_role_backup.py"),
    Path("tools/audit_sync_replica_database_role_backup.py"),
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
        "format": "anonsync-role-bound-database-backup-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SQLite consistency, filesystem "
            "identity, durability, allocation success, crash recovery, or SHA-256"
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
    if missing:
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    cmake = text["CMakeLists.txt"]
    cli = text["src/anonsync_sync.cpp"]
    header = text["src/sync_replica_database_backup.hpp"]
    source = text["src/sync_replica_database_backup.cpp"]
    effect_h = text["src/sync_replica_file_effect_sqlite_owner.hpp"]
    effect_c = text["src/sync_replica_file_effect_sqlite_owner.cpp"]
    catalog_h = text["src/sync_replica_folder_scan_owner.hpp"]
    catalog_c = text["src/sync_replica_folder_scan_owner.cpp"]
    profile_h = text["src/sync_replica_tls_policy_sqlite_profile.hpp"]
    profile_c = text["src/sync_replica_tls_policy_sqlite_profile.cpp"]
    membership_h = text["src/sync_replica_tls_membership_sqlite_owner.hpp"]
    membership_c = text["src/sync_replica_tls_membership_sqlite_owner.cpp"]
    anchor_h = text["src/sync_replica_tls_membership_anchor_sqlite_owner.hpp"]
    anchor_c = text["src/sync_replica_tls_membership_anchor_sqlite_owner.cpp"]
    runtime = text["tools/test_anonsync_database_role_backup.py"]
    readme = text["README.md"]
    design = text["ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md"]
    notes = text["REVISION_NOTES_rev0985.md"]
    verifier = text["tools/verify_release_package.py"]

    roles = (
        "replica", "file-effect", "tls-membership",
        "tls-membership-anchor", "folder-catalog",
    )
    enum_roles = (
        "SyncReplicaSqliteDeploymentRole::Replica",
        "SyncReplicaSqliteDeploymentRole::FileEffect",
        "SyncReplicaSqliteDeploymentRole::TlsMembership",
        "SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor",
        "SyncReplicaSqliteDeploymentRole::FolderCatalog",
    )

    require(
        "anonsync_sync_database_role_backup_process_test" in cmake and
        "tools/test_anonsync_database_role_backup.py" in cmake and
        "LABELS \"product\"" in cmake,
        "role_backup_process_oracle_is_in_product_registry",
        "the shipping binaries exercise every explicit role through CTest",
    )
    require(
        "anonsync_sync_replica_database_role_backup_source_audit" in cmake and
        "tools/audit_sync_replica_database_role_backup.py" in cmake,
        "role_backup_source_audit_is_registered",
        "the focused authority audit is part of the ordinary registry",
    )
    require(
        all(token in cmake for token in (
            "anonsync_sync_replica_file_effect_sqlite_owner",
            "anonsync_sync_replica_folder_scan_owner",
            "anonsync_sync_replica_tls_membership",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp",
        )),
        "backup_library_links_role_specific_schema_owners",
        "role inspection does not duplicate private schemas in the CLI",
    )
    require(
        "SyncReplicaRoleDatabaseBackupCutpoint" in header and
        "SyncReplicaRoleDatabaseBackupArtifactObservation" in header and
        "create_role_artifact_or_throw" in header and
        "inspect_role_artifact_or_throw" in header,
        "public_owner_exposes_one_typed_role_bound_artifact_surface",
        "the legacy replica surface remains layered over one typed extension",
    )
    require(
        "std::optional<SyncReplicaDatabaseBackupCutpoint> replica_cutpoint" in header and
        "accepted by database-recovery-replace" in header,
        "explicit_replica_artifact_retains_released_replacement_cutpoint",
        "role selection does not fork the primary recovery artifact format",
    )
    require(
        all(token in source for token in enum_roles) and
        source.count("case SyncReplicaSqliteDeploymentRole::") >= 10,
        "all_five_manifest_selected_database_roles_are_switched_explicitly",
        "unknown enum values fail closed rather than selecting a default owner",
    )
    require(
        "SyncReplicaPeerServiceSingletonOwner singleton;" in source and
        "ExistingForensicReadOnly" in source and
        "source snapshot before capture" in source and
        "source snapshot after capture" in source and
        "source final rooted reproof" in source,
        "creation_is_singleton_owned_forensic_and_cutpoint_bracketed",
        "one selected database is copied only while its exact source remains stable",
    )
    require(
        "SealedSqliteSnapshot::capture_database" in source and
        "publish_exact_copy_atomically_create_new_or_throw" in source and
        "published != captured" in source,
        "all_roles_reuse_bounded_immutable_artifact_publication",
        "there is no role-specific copy or publication engine",
    )
    require(
        "create_artifact_or_throw" in source and
        "create_role_artifact_or_throw" in source and
        "SyncReplicaSqliteDeploymentRole::Replica" in source and
        "legacy replica artifact creation" in source,
        "released_no_role_v1_surface_delegates_to_explicit_replica_role",
        "backward compatibility is implementation composition rather than duplication",
    )
    require(
        'options.require_only({"manifest", "snapshot", "role"});' in cli and
        all(f'role == "{role}"' in cli for role in roles) and
        "--role must be replica, file-effect" in cli,
        "cli_accepts_only_the_canonical_five_role_names",
        "misspelling or an unknown authority fails as invalid arguments",
    )
    require(
        "anonsync.local-database-backup-create.response.v1" in cli and
        "anonsync.local-database-backup-inspection.response.v1" in cli and
        "anonsync.local-database-backup-create.response.v2" in cli and
        "anonsync.local-database-backup-inspection.response.v2" in cli,
        "no_role_v1_and_explicit_role_v2_responses_coexist",
        "existing automation keeps its exact response schema until --role is supplied",
    )
    require(
        '"complete_share_backup\\":false"' in cli and
        '"cross_database_atomicity\\":false"' in cli and
        '"payload_bytes_included\\":false"' in cli and
        '"configuration_included\\":false"' in cli and
        '"credentials_included\\":false"' in cli,
        "operator_response_denies_complete_share_and_cross_database_authority",
        "five independent SQLite artifacts are not presented as one restorable share",
    )
    require(
        '"restore_supported\\":" << json_bool(replica)' in cli and
        '"inspection_only\\":" << json_bool(!replica)' in cli and
        '"database_incarnation_sha256\\":null"' in cli,
        "only_replica_role_claims_existing_replacement_compatibility",
        "the other four roles remain explicit inspection-only artifacts",
    )
    require(
        "inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_or_throw" in effect_h and
        "inspect_sync_replica_file_effect_sqlite_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw" in effect_h,
        "file_effect_owner_exports_named_and_detached_root_cold_observers",
        "backup validation can inspect persisted root identity without opening files_root",
    )
    require(
        "32768U" in effect_c and "find('\\0')" in effect_c and
        "expected_root_path" in effect_c and "stored_root_authority_digest" in effect_c,
        "file_effect_observer_bounds_and_canonicalizes_persisted_root_text",
        "malformed root text cannot enter the complete logical snapshot",
    )
    require(
        "inspect_sync_replica_folder_catalog_snapshot_read_only_without_root_access_or_throw" in catalog_h and
        "inspect_sync_replica_folder_catalog_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw" in catalog_h,
        "folder_catalog_owner_exports_named_and_detached_root_cold_observers",
        "offline backup does not turn catalog validation into a filesystem scan",
    )
    require(
        "16384U" in catalog_c and "find('\\0')" in catalog_c and
        "deployment_binding_already_attested" in catalog_c and
        "root_attestation_digest" in catalog_c,
        "folder_catalog_observer_bounds_root_text_and_avoids_duplicate_binding_authority",
        "the detached path validates one binding and one exact current schema",
    )
    require(
        "ForensicReadOnlyDetached = 4U" in profile_h and
        "unnamed read-only MEMORY-journal image" in profile_h and
        "forensic_read_only" in profile_c and "detached_image" in profile_c,
        "shared_tls_profile_models_filename_free_forensic_images_explicitly",
        "the role extension does not smuggle detached images through a mutable owner disposition",
    )
    require(
        "sqlite3_db_readonly" in profile_c and
        "detached image unexpectedly names a file" in profile_c and
        "Detached write denial is therefore proved" in profile_c and
        "observed_read_only != 1" in profile_c,
        "detached_read_only_authority_does_not_depend_on_sqlite_db_readonly_equal_one",
        "SQLite deserialize semantics are handled at the shared profile boundary",
    )
    require(
        "inspect_sync_replica_tls_membership_sqlite_snapshot_in_detached_read_only_image_or_throw" in membership_h and
        "ForensicReadOnlyDetached" in membership_c,
        "membership_owner_has_an_explicit_detached_forensic_observer",
        "current membership state is validated through its retained schema owner",
    )
    require(
        "inspect_sync_replica_tls_membership_anchor_sqlite_snapshot_in_detached_read_only_image_or_throw" in anchor_h and
        "ForensicReadOnlyDetached" in anchor_c,
        "membership_anchor_owner_has_an_explicit_detached_forensic_observer",
        "anchor history is validated independently from membership state",
    )
    require(
        all(f'"{role}"' in runtime for role in roles) and
        "anonsync role-bound database backup" in runtime,
        "process_oracle_exercises_all_five_roles",
        "the role set is tested through shipping commands rather than private calls",
    )
    require(
        "hide_path(payload_root" in runtime and
        "hide_path(files_root" in runtime and
        "hide_family(source" in runtime and
        "detached inspection recreated" in runtime,
        "process_oracle_proves_root_cold_creation_and_source_absent_inspection",
        "detached inspection neither needs nor recreates live authorities",
    )
    require(
        "wrong role artifact inspection" in runtime and
        "explicit replica artifact legacy inspection" in runtime and
        "invalid database role" in runtime,
        "process_oracle_covers_role_confusion_v1_compatibility_and_parser_denial",
        "artifact role binding is fail-closed and replica compatibility is visible",
    )
    require(
        "mode 0600" in runtime and "single-linked" in runtime and
        "artifact left sidecar" in runtime and
        "backup changed its source SQLite family" in runtime,
        "process_oracle_covers_private_sidecar_free_immutable_artifact_properties",
        "role extension retains the released artifact publication contract",
    )
    require(
        "## Rev0985" in readme and
        "role-bound" in readme.lower() and
        "not a complete-share backup" in readme.lower(),
        "readme_names_the_role_extension_and_its_product_nonclaim",
        "operator documentation does not mistake component artifacts for recovery completion",
    )
    require(
        all(token in design for token in (
            "Five role-bound SQLite artifacts", "Consistency boundary",
            "Detached read-only correction", "What remains missing",
            "Complete-share backup",
        )),
        "design_audit_records_authority_consistency_and_missing_edges",
        "the retained rationale explains why this is a prerequisite rather than the destination",
    )
    require(
        all(token in notes for token in (
            "Role-bound database backup", "Backward compatibility",
            "Audit/refactor", "Boundary", "Validation",
        )),
        "revision_notes_separate_feature_refactor_boundary_and_evidence",
        "future readers can distinguish implementation facts from release proof",
    )
    require(
        "REVISION_NOTES_rev0985.md" in verifier and
        "ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md" in verifier and
        "test_anonsync_database_role_backup.py" in verifier,
        "release_verifier_requires_role_backup_sources_and_records",
        "the feature cannot disappear from the packaged active projection",
    )
    own = Path(__file__).read_text(encoding="utf-8")
    require(
        "not semantic proof" in own and
        "Runtime, sanitizer" in own and
        "package evidence" in own,
        "lexical_audit_disclaims_load_bearing_semantic_authority",
        "a passing source scan cannot replace execution and release reconstruction",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
