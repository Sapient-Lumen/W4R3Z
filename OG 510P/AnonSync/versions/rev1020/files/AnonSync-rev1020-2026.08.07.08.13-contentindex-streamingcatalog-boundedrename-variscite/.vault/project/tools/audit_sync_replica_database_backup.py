#!/usr/bin/env python3
"""Lexical audit for the offline replica-database backup boundary.

This pins reviewed source shape, ownership order, nonclaims, and process-oracle
vocabulary. It is not semantic proof of SQLite, filesystem, crash, allocation,
or cryptographic behavior; runtime, sanitizer, reconstruction, and package
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
    Path("OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md"),
    Path("REVISION_NOTES_rev0982.md"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_database_backup.hpp"),
    Path("src/sync_replica_database_backup.cpp"),
    Path("src/sync_replica_database_artifact_internal.hpp"),
    Path("src/sync_replica_deployment_binding.hpp"),
    Path("src/sync_replica_deployment_binding.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/persistence/sqlite_snapshot_seal.hpp"),
    Path("src/persistence/sqlite_snapshot_seal.cpp"),
    Path("tests/persistence/sqlite_snapshot_seal_tests.cpp"),
    Path("tools/test_anonsync_database_recovery.py"),
    Path("tools/audit_sync_replica_database_backup.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def delimited_body(text: str, signature: str, opening: str, closing: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    boundary = text.find(opening, start + len(signature))
    if boundary < 0:
        return ""
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = boundary
    while index < len(text):
        byte = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if byte == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if byte == "*" and following == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif byte == "\\":
                escaped = True
            elif byte == quote:
                quote = ""
            index += 1
            continue
        if byte == "/" and following == "/":
            line_comment = True
            index += 2
            continue
        if byte == "/" and following == "*":
            block_comment = True
            index += 2
            continue
        if byte in ('"', "'"):
            quote = byte
            index += 1
            continue
        if byte == opening:
            depth += 1
        elif byte == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
        index += 1
    return ""


def function_body(text: str, signature: str) -> str:
    return delimited_body(text, signature, "{", "}")


def cmake_call(text: str, prefix: str) -> str:
    return delimited_body(text, prefix, "(", ")")


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-replica-database-backup-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SQLite snapshot consistency, POSIX "
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
    artifact_internal = text["src/sync_replica_database_artifact_internal.hpp"]
    binding_header = text["src/sync_replica_deployment_binding.hpp"]
    binding_source = text["src/sync_replica_deployment_binding.cpp"]
    owner_header = text["src/sync_replica_sqlite_owner.hpp"]
    owner_source = text["src/sync_replica_sqlite_owner.cpp"]
    seal_header = text["src/persistence/sqlite_snapshot_seal.hpp"]
    seal_source = text["src/persistence/sqlite_snapshot_seal.cpp"]
    seal_test = text["tests/persistence/sqlite_snapshot_seal_tests.cpp"]
    runtime = text["tools/test_anonsync_database_recovery.py"]
    design = text["OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md"]
    notes = text["REVISION_NOTES_rev0982.md"]
    readme = text["README.md"]
    verifier = text["tools/verify_release_package.py"]

    backup_target = cmake_call(
        cmake, "add_library(anonsync_sync_replica_database_backup STATIC"
    )
    backup_links = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_replica_database_backup"
    )
    sync_links = cmake_call(cmake, "target_link_libraries(anonsync_sync PRIVATE")
    create = function_body(
        source, "SyncReplicaDatabaseBackupOwner::create_role_artifact_or_throw("
    )
    inspect = function_body(
        source, "SyncReplicaDatabaseBackupOwner::inspect_role_artifact_or_throw("
    )
    validate_path = function_body(
        artifact_internal, "validate_artifact_path_or_throw(")
    preflight_output_family = function_body(
        artifact_internal,
        "preflight_artifact_output_family_create_new_or_throw(",
    )
    inspect_sealed = function_body(
        artifact_internal, "inspect_sealed_artifact_or_throw(")
    compact = function_body(artifact_internal, "compact_backup_cutpoint(")
    detached_profile = function_body(
        binding_source, "require_detached_read_only_image_or_throw("
    )
    combined_inspector = function_body(
        owner_source,
        "inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw(",
    )
    named_inspector = function_body(
        owner_source, "inspect_sync_replica_sqlite_snapshot_read_only_or_throw("
    )
    cli_create = function_body(cli, "int command_database_backup_create(")
    cli_inspect = function_body(cli, "int command_database_backup_inspect(")
    cli_render = function_body(cli, "void append_database_backup_scope_json(")

    require(
        "src/sync_replica_database_backup.cpp" in backup_target,
        "dedicated_backup_owner_is_a_retained_library",
        "the shipping command composes one reviewed owner instead of embedding a second copy engine",
    )
    require(
        all(
            token in backup_links
            for token in (
                "anonsync_sqlite_snapshot_seal",
                "anonsync_sync_atomic_file_publication",
                "anonsync_sync_replica_deployment_binding",
                "anonsync_sync_replica_operational_database",
                "anonsync_sync_replica_peer_service_singleton",
                "anonsync_sync_replica_tls_membership",
                "anonsync_sync_replica_sqlite_owner",
            )
        )
        and "anonsync_sync_replica_tls_policy_sqlite_profile" not in backup_links,
        "backup_owner_links_only_real_retained_targets",
        "the initial raw -l profile-target integration defect cannot recur",
    )
    require(
        "anonsync_sync_replica_database_backup" in sync_links
        and cmake.count("anonsync_sync_replica_database_backup") >= 4,
        "shipping_and_sanitizer_graphs_retain_the_backup_owner",
        "the owner is linked into anonsync_sync and inventoried in the product dependency graph",
    )
    require(
        "SyncReplicaPeerServiceSingletonOwner singleton" in source
        and ordered(
            source,
            "SyncReplicaDeploymentManifest deployment;",
            "std::string label;",
            "SyncReplicaPeerServiceSingletonOwner singleton;",
        ),
        "deployment_singleton_precedes_database_and_artifact_authority",
        "the owner retains no open database or artifact member before the deployment claim",
    )
    require(
        "kSyncReplicaDatabaseBackupMaximumArtifactBytes" in header
        and "512ULL * 1024ULL * 1024ULL" in header
        and "kSyncReplicaDatabaseBackupMaximumArtifactPages = 262144ULL" in header
        and "kMaximumUntrustedSqliteSnapshotBytes" in artifact_internal
        and "kMaximumUntrustedSqliteSnapshotPages" in artifact_internal,
        "resident_backup_limits_tighten_the_generic_untrusted_ceiling",
        "product backup authority is bounded by bytes and pages",
    )
    require(
        all(
            token in validate_path
            for token in (
                "canonical absolute path without NUL",
                "deployment.manifest_path",
                "deployment.replica_db",
                "deployment.effect_db",
                "deployment.membership_db",
                "deployment.anchor_db",
                "sync_replica_folder_catalog_path_or_throw",
                "deployment.payload_root",
                "deployment.files_root",
                "sqlite_artifact_families_overlap",
            )
        )
        and all(
            token in artifact_internal
            for token in ('"-journal"', '"-wal"', '"-shm"')
        )
        and "for (const fs::path& artifact_member : artifact_family)"
            in validate_path
        and "path_is_same_or_descendant(artifact_member, *root)"
            in validate_path
        and "artifact family sidecar colliding with payload root"
            in runtime,
        "artifact_path_excludes_manifest_all_active_sqlite_families_and_file_roots",
        "backup publication cannot be directed into selected durable stores or synchronized data",
    )
    require(
        create.count("preflight_artifact_output_family_create_new_or_throw") == 2
        and ordered(
            create,
            "validate_artifact_path_or_throw",
            "artifact output preflight",
            "SyncReplicaOperationalDatabase::open_or_throw",
            "source changed across the exact role-bound backup capture bracket",
            "artifact output final prepublication reproof",
            "publish_exact_copy_atomically_create_new_or_throw",
        ),
        "output_family_is_proved_early_and_immediately_before_publication",
        "occupied families fail before the resident copy and drift during capture is denied before main-name publication",
    )
    require(
        ordered(
            preflight_output_family,
            "guard_sqlite_path_family_or_throw",
            "sidecar preflight",
            "preflight_sync_file_create_new_no_symlink_or_throw",
            "final sidecar preflight",
        )
        and "backup create with preexisting output sidecar" in runtime
        and "preexisting backup sidecar allowed the main artifact to publish"
            in runtime,
        "complete_output_family_is_rejected_before_main_publication",
        "a deterministic WAL/SHM/journal conflict cannot leave a newly visible main artifact",
    )
    require(
        ordered(
            create,
            "source snapshot before capture",
            "SealedSqliteSnapshot::capture_database",
            "inspect_role_sealed_artifact_or_throw",
            "source snapshot after capture",
            "source.verify_open_database_or_throw",
            "source changed across the exact role-bound backup capture bracket",
            "publish_exact_copy_atomically_create_new_or_throw",
        ),
        "source_copy_is_pinned_bracketed_rooted_and_create_new_published",
        "one exact logical image is compared with complete source observations before namespace publication",
    )
    require(
        ordered(
            create,
            "publish_exact_copy_atomically_create_new_or_throw",
            "inspect_role_artifact_or_throw(",
            "published artifact differs from the captured role-bound source snapshot",
        ),
        "durable_artifact_is_independently_reopened_and_reproved",
        "success is not reported from resident bytes alone",
    )
    require(
        "SealedSqliteSnapshot::capture(" in inspect
        and "open_attested_sync_replica_primary_database" not in inspect,
        "inspection_has_no_live_primary_database_authority",
        "a detached artifact remains inspectable after the active database family is absent",
    )
    require(
        "SyncReplicaDatabaseBackupCutpoint" in header
        and "SyncReplicaSqliteSnapshot replica_snapshot" not in header
        and all(
            token in compact
            for token in (
                "database_incarnation_sha256",
                "database_recovery_epoch",
                "state_generation",
                "policy_generation",
                "operation_set_digest",
                "evidence_set_digest",
                "visible_state_digest",
                "outbox_digest",
                "outbox_clock_digest",
                "historical_version_pin_set_digest",
                "cutpoint_digest",
            )
        ),
        "backup_bracket_retains_compact_exact_witnesses_not_complete_graphs",
        "complete schema restore is released before the next observation instead of multiplying causal-model memory",
    )
    require(
        "before != captured.source_cutpoint" in create
        and "after != captured.source_cutpoint" in create
        and "published != captured" in create,
        "compact_witness_is_used_at_every_backup_consistency_cutpoint",
        "the memory refactor did not remove source bracketing or durable reproof",
    )
    require(
        "SQLITE_DESERIALIZE_READONLY" in seal_header
        and "open_database_owner_or_throw" in inspect_sealed
        and "configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw"
        in inspect_sealed
        and "PRAGMA temp_store=MEMORY;PRAGMA foreign_keys=ON;" in inspect_sealed,
        "artifact_bytes_enter_one_hardened_filename_free_read_only_sqlite_profile",
        "detached schema inspection has no named journal family or mutable profile",
    )
    require(
        "sqlite3_db_readonly(database.get()" not in detached_profile
        and "PRAGMA query_only" in detached_profile
        and "SyncSqliteSavepoint rollback_guard" in detached_profile
        and "outer_transaction_authority" in detached_profile
        and "PRAGMA query_only=OFF" in detached_profile
        and "CREATE TABLE main.anonsync_detached_read_only_probe_rev0982" in detached_profile
        and "SQLITE_READONLY" in detached_profile
        and "rollback_guard.rollback()" in detached_profile
        and "SAVEPOINT anonsync_detached_read_only_probe" not in binding_source
        and "ROLLBACK TO anonsync_detached_read_only_probe" not in binding_source,
        "detached_read_only_authority_is_behavioral_and_typed_cleanup_fenced",
        "the verifier proves immutable main bytes through the centralized typed savepoint owner",
    )
    require(
        "sqlite3_db_readonly(database.get(), \"main\") != 1" in named_inspector,
        "named_forensic_reader_retains_the_native_read_only_gate",
        "the detached SQLite exception did not weaken ordinary named-file inspection",
    )
    require(
        ordered(
            combined_inspector,
            "SyncSqliteTransaction transaction",
            "attest_sync_replica_sqlite_deployment_binding_state_in_read_only_detached_image_or_throw",
            "load_state_or_throw",
            "require_snapshot_authority_or_throw",
            "snapshot_from_loaded",
            "transaction.commit",
        ),
        "deployment_binding_and_complete_replica_state_share_one_transaction",
        "a detached artifact cannot change between a separate binding transaction and schema observation",
    )
    require(
        "inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw"
        in binding_header + owner_header + source + artifact_internal
        and "attest_sync_replica_sqlite_deployment_binding_in_read_only_detached_image_or_throw"
        not in inspect_sealed,
        "backup_owner_uses_the_single_transaction_composition",
        "the earlier two-transaction attestation path is not retained in the shipping backup flow",
    )
    require(
        'sqlite3_db_readonly(database, "main") == 0' in seal_test
        and '"readonly", checks' in seal_test,
        "focused_test_pins_sqlite_in_memory_introspection_and_actual_denial",
        "future cleanup must preserve the counterintuitive SQLite behavior that triggered this correction",
    )
    require(
        'options.require_only({"manifest", "snapshot", "role"})' in cli_create
        and 'options.require_only({"manifest", "snapshot", "role"})' in cli_inspect
        and '!options.has("role")' in cli_create
        and '!options.has("role")' in cli_inspect
        and "SyncReplicaDatabaseBackupOwner owner" in cli_create
        and "SyncReplicaDatabaseBackupOwner owner" in cli_inspect
        and "sqlite3_backup" not in cli_create + cli_inspect,
        "cli_is_a_strict_two_option_adapter_not_a_second_backup_owner",
        "copy, path, SQLite, and publication authority stays in the retained C++ owner",
    )
    require(
        all(
            token in cli_render
            for token in (
                "single_replica_database_image",
                "external_anti_rollback_authority",
                "payload_store_observed",
                "folder_catalog_observed",
                "rooted_files_observed",
                "network_started",
                "payload_bytes_included",
                "folder_catalog_included",
                "membership_database_included",
                "effect_database_included",
                "anchor_database_included",
                "restore_performed",
                "recovery_epoch_advanced",
                "post_replacement_recovery_advance_required",
                "retention_age_reset_required_after_restore",
            )
        )
        and cli_render.count(":false") >= 12
        and cli_render.count(":true") >= 6,
        "operator_response_denies_share_backup_restore_and_anti_rollback_authority",
        "the JSON surface cannot be mistaken for a complete share backup or restore receipt",
    )
    require(
        all(
            token in runtime
            for token in (
                "backup beneath synchronized root",
                "backup colliding with active SQLite family",
                "offline replica database backup create",
                "duplicate immutable backup create",
                "detached backup inspection without source database",
                "damaged detached backup inspection",
                "backup inspection with hostile sidecar",
                "multiply linked backup inspection",
                "backup artifact is not single-linked",
                "backup artifact is not owner-only mode 0600",
                "backup page geometry disagreed",
                "backup publication left a SQLite sidecar",
                "source recovery advance changed detached backup bytes",
            )
        ),
        "real_process_oracle_covers_namespace_geometry_detachment_damage_and_immutability",
        "the product lane exercises the visible backup contract across independent process invocations",
    )
    require(
        "sqlite_family_fingerprint(replica_db)" in runtime
        and runtime.count("sqlite_family_fingerprint(replica_db)") >= 8
        and "payload_root, files_root, catalog" in runtime,
        "process_oracle_proves_source_family_stability_and_narrow_authority",
        "backup and recovery work does not require payload, rooted files, or the folder catalog",
    )
    require(
        'options.require_only({"manifest", "snapshot", "role"});' in cli
        and 'options.one("manifest")' in cli
        and 'options.one("snapshot")' in cli
        and "database-backup-inspect --manifest ... --snapshot ..." in readme
        and "database-backup-inspect --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE"
            in notes
        and "[--manifest" not in notes
        and "An optional `--manifest`" not in readme,
        "detached_inspection_manifest_requirement_matches_shipping_cli",
        "detached inspection remains source-database independent but manifest-bound rather than unauthenticated",
    )

    require(
        all(
            token in design
            for token in (
                "Creation authority order",
                "Boundedness and memory refactor",
                "Detached read-only SQLite correction",
                "Namespace and artifact properties",
                "What this does not prove",
                "Next safe edge",
                "https://sqlite.org/backup.html",
                "https://sqlite.org/forum/info/80e765eb24d26f01",
            )
        )
        and all(
            token in notes
            for token in (
                "Offline backup artifact",
                "One canonical artifact",
                "Detached inspector",
                "Audit/refactor: typed rollback authority",
                "Boundary",
            )
        )
        and "## Rev0982: canonical replica-database backup and detached reproof"
        in readme,
        "design_notes_and_readme_agree_on_the_narrow_backup_boundary",
        "visible records distinguish one replica database from a share backup and restore ceremony",
    )
    require(
        "revision_number is not None and revision_number >= 982" in verifier
        or "REVISION_NOTES_rev0982.md" not in verifier,
        "release_verifier_update_is_pending_or_present",
        "preseal permits the package-policy update to land with the final revision records",
    )
    require(
        "lexical audit" in Path(__file__).read_text(encoding="utf-8").lower()
        and "not semantic proof" in Path(__file__).read_text(encoding="utf-8")
        and "runtime, sanitizer, reconstruction, and package" in Path(__file__).read_text(encoding="utf-8"),
        "lexical_audit_disclaims_load_bearing_semantic_authority",
        "a passing source scan cannot be substituted for runtime and release proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
