#!/usr/bin/env python3
"""Audit database-minted checkpoint owner generations and recipient-side fences."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def source_list_block(cmake: str, variable: str) -> str:
    match = re.search(rf"set\({re.escape(variable)}\s+(.*?)\)", cmake, re.DOTALL)
    return match.group(1) if match else ""


def target_block(cmake: str, command: str, target: str) -> str:
    match = re.search(
        rf"{re.escape(command)}\({re.escape(target)}\b(.*?)\)",
        cmake,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def include_users(root: Path, header: str) -> list[str]:
    include = f'#include "{header}"'
    users: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".cpp", ".cc", ".h", ".hpp"}:
            continue
        relative = path.relative_to(root)
        if any(part.startswith("build") for part in relative.parts):
            continue
        if include in path.read_text(errors="replace"):
            users.append(relative.as_posix())
    return users


def function_slice(text: str, name: str, next_name: str | None = None) -> str:
    start = text.find(name)
    if start < 0:
        return ""
    if next_name is not None:
        end = text.find(next_name, start + len(name))
        if end >= 0:
            return text[start:end]
    # Audit only needs a conservative bounded window; these functions are large.
    return text[start : start + 36000]


def struct_slice(text: str, name: str) -> str:
    match = re.search(
        rf"struct\s+{re.escape(name)}(?:\s+final)?\s*\{{(.*?)\n\}};",
        text,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def foreach_block(cmake: str, variable: str) -> str:
    match = re.search(
        rf"foreach\({re.escape(variable)}\s+(.*?)\)\s*",
        cmake,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    cmake = (root / "CMakeLists.txt").read_text()
    core_header = (root / "include/anonsync_core.hpp").read_text()
    core_internal_header = (root / "include/anonsync_core_internal.hpp").read_text()
    capability_header = (
        root / "include/anonsync_sync_checkpoint_owner_fence.hpp"
    ).read_text()
    policy_header = (root / "src/sync_checkpoint_owner_fence_policy.hpp").read_text()
    policy = (root / "src/sync_checkpoint_owner_fence_policy.cpp").read_text()
    runtime_header = (root / "src/sync_checkpoint_owner_fence.hpp").read_text()
    runtime = (root / "src/sync_checkpoint_owner_fence.cpp").read_text()
    schema_header = (root / "src/sync_checkpoint_owner_schema.hpp").read_text()
    schema = (root / "src/sync_checkpoint_owner_schema.cpp").read_text()
    schema_identity = (root / "src/sync_sqlite_schema_identity.cpp").read_text()
    domain = (root / "src/sync_domain.cpp").read_text()
    peer = (root / "src/sync_peer_ingestion.cpp").read_text()
    scheduler = (root / "src/sync_checkpoint_scheduler.cpp").read_text()
    operator_cli = (root / "src/sync_operator_cli.cpp").read_text()
    selftests = (root / "src/sync_domain_selftests.cpp").read_text()
    policy_test = (root / "tests/sync_checkpoint_owner_fence_policy_test.cpp").read_text()
    sqlite_test = (root / "tests/sync_checkpoint_owner_fence_sqlite_test.cpp").read_text()
    schema_test = (root / "tests/sync_checkpoint_owner_schema_test.cpp").read_text()

    checks: list[dict[str, object]] = []

    def check(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(passed), "detail": detail})

    capability_fields = [
        "std::string session_id;",
        "std::string daemon_id;",
        "std::string worker_id;",
        "std::string owner_lock_id;",
        "std::uint64_t owner_lock_epoch = 0;",
    ]
    check(
        "public_capability_is_exact_generation_evidence",
        all(field in capability_header for field in capability_fields)
        and "expires_at_epoch" not in capability_header
        and "acquired_at_epoch" not in capability_header
        and '#include "anonsync_sync_checkpoint_owner_fence.hpp"' in core_header,
        "capability binds session, daemon, worker, canonical lock id, and generation only",
    )

    mutating_option_structs = [
        "SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions",
        "SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions",
        "SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineOptions",
        "SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions",
        "SyncSessionCheckpointStagingRepairOptions",
        "SyncSessionCheckpointMaterializeResumeOptions",
        "SyncSessionCheckpointCleanupResumeOptions",
        "SyncSessionCheckpointResumeTransferClaimOptions",
        "SyncSessionCheckpointResumeTransferExecutionOptions",
        "SyncSessionCheckpointResumeTransferTerminalResetOptions",
        "SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions",
        "SyncSessionCheckpointResumeCycleOptions",
    ]
    missing_caps = [
        name
        for name in mutating_option_structs
        if "SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;"
        not in struct_slice(core_header, name)
    ]
    check(
        "public_mutators_carry_recipient_capability",
        not missing_caps,
        f"missing capability fields={missing_caps}",
    )

    external_file_mutators = [
        "SyncSessionCheckpointStagingRepairOptions",
        "SyncSessionCheckpointMaterializeResumeOptions",
        "SyncSessionCheckpointCleanupResumeOptions",
        "SyncSessionCheckpointResumeCycleOptions",
    ]
    missing_times = [
        name
        for name in external_file_mutators
        if "std::uint64_t owner_fence_now_epoch = 1;"
        not in struct_slice(core_header, name)
    ]
    check(
        "filesystem_mutators_carry_explicit_fence_observation_time",
        not missing_times,
        f"missing observation time fields={missing_times}",
    )

    core_sources = source_list_block(cmake, "ANONSYNC_CORE_SOURCES")
    invariant_sources = foreach_block(cmake, "ANONSYNC_INVARIANT_OWNED_SOURCE")
    check(
        "policy_schema_and_recipient_runtime_are_outside_core_monolith",
        "src/sync_checkpoint_owner_fence_policy.cpp" not in core_sources
        and "src/sync_checkpoint_owner_schema.cpp" not in core_sources
        and "src/sync_checkpoint_owner_fence.cpp" not in core_sources
        and "src/sync_sqlite_schema_identity.cpp" not in core_sources
        and "${ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_POLICY_SOURCE}" in invariant_sources
        and "${ANONSYNC_SYNC_CHECKPOINT_OWNER_SCHEMA_SOURCE}" in invariant_sources
        and "${ANONSYNC_SYNC_CHECKPOINT_OWNER_FENCE_SOURCE}" in invariant_sources
        and "${ANONSYNC_SQLITE_SCHEMA_IDENTITY_SOURCE}" in invariant_sources,
        "policy, exact schema owner, recipient runtime, and shared canonicalizer are protected by the CMake source-ownership guard",
    )

    policy_links = target_block(
        cmake, "target_link_libraries", "anonsync_sync_checkpoint_owner_fence_policy"
    )
    schema_links = target_block(
        cmake, "target_link_libraries", "anonsync_sync_checkpoint_owner_schema"
    )
    runtime_links = target_block(
        cmake, "target_link_libraries", "anonsync_sync_checkpoint_owner_fence"
    )
    core_links = target_block(cmake, "target_link_libraries", "anonsync_core_lib")
    check(
        "dependency_direction_is_core_to_recipient_to_schema_and_pure_policy",
        "add_library(anonsync_sync_checkpoint_owner_fence_policy STATIC" in cmake
        and "add_library(anonsync_sync_checkpoint_owner_schema STATIC" in cmake
        and "add_library(anonsync_sync_checkpoint_owner_fence STATIC" in cmake
        and "anonsync_core_lib" not in policy_links
        and "anonsync_core_lib" not in schema_links
        and "anonsync_core_lib" not in runtime_links
        and "anonsync_sync_checkpoint_owner_fence_policy" in runtime_links
        and "anonsync_sync_checkpoint_owner_schema" in runtime_links
        and "anonsync_sqlite_schema_identity" in schema_links
        and "anonsync_sync_checkpoint_owner_fence" in core_links,
        "core -> recipient boundary -> exact schema and pure transition owners; no reverse core dependency",
    )

    forbidden_policy_tokens = [
        "sqlite3",
        "filesystem",
        "fstream",
        "openssl",
        "sha256_digest.hpp",
        "sha256_hex(",
        "std::chrono",
        "sync_domain",
        "SyncSqlite",
    ]
    present_forbidden = [
        token for token in forbidden_policy_tokens if token.lower() in policy.lower()
    ]
    check(
        "transition_policy_is_pure",
        not present_forbidden,
        f"forbidden dependencies present={present_forbidden}",
    )

    policy_required = [
        "latest_generation + 1",
        "mode.latest_owner_lock_epoch",
        "owner generation is exhausted",
        "stored owner row exceeds SQLite signed integer range",
        "stored owner mode row exceeds SQLite signed integer range",
        "owner lease expiration exceeds SQLite signed integer range",
        "owner lock is still live",
        "acquisition clock regressed behind durable owner mode evidence",
        "presented owner capability is only partially populated",
        "live durable owner row requires its exact capability",
        "presented owner capability does not match the live durable generation",
        "sticky owner mode remains required after release",
        "sticky owner mode has no live durable generation",
        "durable owner generation is expired",
        "stored owner lock id does not bind its row identities and generation",
        "administratively-disabled mode lacks canonical disable evidence",
    ]
    check(
        "pure_policy_fail_closes_generation_and_capability_geometry",
        all(token in policy for token in policy_required),
        "mint, takeover, live-owner, expiry, release, malformed-row, and exact-match branches are explicit",
    )

    runtime_required = [
        'sqlite3_txn_state(db, "main") != SQLITE_TXN_WRITE',
        "inside the recipient write transaction",
        "load_stored_owner_lock_evidence_or_throw",
        "load_or_backfill_owner_mode_in_write_transaction_or_throw",
        "owner_lock_id_or_throw(",
        "stored.owner_lock_id_is_canonical",
        "authorize_recipient(",
        "mode, stored, request",
        "recipient owner fence rejected",
    ]
    check(
        "recipient_runtime_rechecks_exact_durable_state_in_write_transaction",
        all(token in runtime for token in runtime_required),
        "recipient reads the row, recomputes the canonical id, and invokes policy on the write snapshot",
    )

    checkpoint_options = struct_slice(core_header, "SyncSessionCheckpointOptions")
    check(
        "checkpoint_root_reset_api_carries_exact_owner_and_observation_evidence",
        "SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;"
        in checkpoint_options
        and "std::uint64_t owner_fence_now_epoch = 1;" in checkpoint_options
        and checkpoint_options.find("daemon_owner_capability")
        < checkpoint_options.find("reset_existing_session_rows"),
        "destructive checkpoint replacement carries recipient capability and explicit fence time",
    )

    mode_schema = function_slice(
        runtime,
        "void ensure_checkpoint_owner_mode_schema_or_throw(",
        "std::string owner_lock_id_or_throw(",
    )
    check(
        "sticky_owner_mode_schema_is_outside_checkpoint_cascade",
        "kOwnerModeStoredDdl" in schema
        and "session_id TEXT NOT NULL PRIMARY KEY" in schema
        and "REFERENCES" not in schema[
            schema.find("kOwnerModeStoredDdl") : schema.find("kOwnerModeCreateDdl")
        ]
        and "ON DELETE" not in schema[
            schema.find("kOwnerModeStoredDdl") : schema.find("kOwnerModeCreateDdl")
        ],
        "mode memory has no foreign key or cascade edge to the replaceable checkpoint root",
    )

    check(
        "owner_schema_bootstrap_is_exact_not_if_not_exists",
        "CREATE TABLE main.sync_session_checkpoint_owner_modes" in schema
        and "CREATE TABLE IF NOT EXISTS sync_session_checkpoint_owner_modes" not in schema
        and "canonicalize_sqlite_schema_sql_or_throw" in schema
        and "main.sqlite_schema" in schema,
        "bootstrap distinguishes true absence from lookalike objects, creates one main object, then compares canonical stored SQL",
    )

    schema_attest = function_slice(
        schema,
        "void attest_checkpoint_owner_schema_or_throw(",
        "void ensure_checkpoint_owner_schema_or_throw(",
    )
    schema_ensure = function_slice(
        schema,
        "void ensure_checkpoint_owner_schema_or_throw(",
    )
    lock_attest_pos = schema_ensure.find("attest_optional_owner_lock_table_or_throw")
    mode_create_pos = schema_ensure.find("kOwnerModeCreateDdl")
    check(
        "hostile_legacy_owner_schema_is_rejected_before_migration_mutation",
        0 <= lock_attest_pos < mode_create_pos
        and "verify_no_relevant_temp_objects_or_throw" in schema_ensure
        and "verify_no_checkpoint_root_triggers_or_throw" in schema_ensure,
        f"positions owner_lock_attest={lock_attest_pos} mode_create={mode_create_pos}",
    )

    check(
        "owner_schema_attestation_requires_live_constraint_enforcement",
        "PRAGMA foreign_keys;" in schema
        and "PRAGMA ignore_check_constraints;" in schema
        and "requires foreign-key enforcement" in schema
        and "requires CHECK-constraint enforcement" in schema
        and schema_attest.find("verify_constraint_enforcement_profile_or_throw")
        < schema_attest.find("attest_mode_table_or_throw"),
        "the exact schema is interpreted only while its foreign-key and CHECK constraints are enabled on the live connection",
    )

    check(
        "schema_attestation_pins_sql_columns_foreign_keys_and_program_surface",
        all(
            token in schema
            for token in [
                "PRAGMA main.table_list;",
                "pragma_table_xinfo(?, 'main')",
                "pragma_foreign_key_list(?, 'main')",
                "sqlite_temp_schema",
                "unexpected SQL-bearing index, trigger, or alias objects",
                "checkpoint root has an unreviewed trigger",
                "owner lock foreign-key geometry does not match",
            ]
        ),
        "the verifier independently checks stored SQL, table geometry, exact columns, FK cascade, TEMP objects, indexes, and triggers",
    )

    savepoint_pos = schema_ensure.find("SyncSqliteSavepoint migration(")
    backfill_pos = schema_ensure.find(
        "INSERT INTO main.sync_session_checkpoint_owner_modes"
    )
    post_attest_pos = schema_ensure.find("post-migration attestation")
    release_pos = schema_ensure.find("migration.release();")
    check(
        "owner_schema_migration_is_savepoint_atomic_and_attested_before_publish",
        0 <= savepoint_pos < lock_attest_pos < mode_create_pos < backfill_pos
        < post_attest_pos < release_pos
        and "FROM main.sync_session_resume_transfer_daemon_owner_locks"
        in schema_ensure
        and "SAVEPOINT anonsync_checkpoint_owner_schema_migration" not in schema_ensure
        and "ROLLBACK TO anonsync_checkpoint_owner_schema_migration" not in schema_ensure,
        "positions "
        f"typed_savepoint={savepoint_pos} owner_lock_attest={lock_attest_pos} "
        f"mode_create={mode_create_pos} backfill={backfill_pos} "
        f"post_attest={post_attest_pos} release={release_pos}; "
        "destructor rollback is owned by SyncSqliteSavepoint",
    )

    check(
        "schema_bootstrap_and_backfill_have_one_invariant_owner",
        "ensure_checkpoint_owner_schema_or_throw(" in mode_schema
        and "INSERT INTO main.sync_session_checkpoint_owner_modes" not in mode_schema
        and "sync_session_resume_transfer_daemon_owner_locks" not in mode_schema
        and "INSERT INTO main.sync_session_checkpoint_owner_modes" in schema_ensure,
        "runtime delegates bootstrap while the exact-schema boundary owns creation, legacy migration, re-attestation, and rollback",
    )

    check(
        "sqlite_case_insensitive_names_are_folded_in_cpp_not_programmable_sql",
        "bool ascii_case_equal(" in schema
        and "is_checkpoint_owner_authority_name" in schema
        and "WHERE sql IS NOT NULL ORDER BY type,name,tbl_name;" in schema
        and "SELECT name,tbl_name FROM sqlite_temp_schema" in schema
        and "lower(name)" not in schema
        and "COLLATE NOCASE" not in schema,
        "main and TEMP catalogs are scanned and ASCII-folded in C++, avoiding BINARY false absence and overridable SQL functions/collations",
    )

    check(
        "checkpoint_schema_delegates_sticky_mode_ownership",
        "ensure_checkpoint_owner_mode_schema_or_throw(" in domain
        and domain.find("ensure_checkpoint_owner_mode_schema_or_throw(")
        > domain.find("sync_session_resume_transfer_daemon_owner_locks"),
        "the domain creates its owner child row then delegates independent mode migration to the focused boundary",
    )

    release_slice = function_slice(
        runtime,
        "void release_owner_generation_in_write_transaction_or_throw(",
        "void require_recipient_write_authority_or_throw(",
    )
    check(
        "release_retires_generation_without_disabling_sticky_ownership",
        "lock_state='released'" in release_slice
        and "UPDATE main.sync_session_checkpoint_owner_modes" in release_slice
        and "ownership_mode='owner-required'" in release_slice
        and "administratively-disabled" not in release_slice,
        "release advances owner-required mode but exposes no capability-free transition",
    )

    permit_class = runtime_header[
        runtime_header.find("class CheckpointRootResetPermit final") :
        runtime_header.find(
            "authorize_checkpoint_root_reset_in_write_transaction_or_throw(",
            runtime_header.find("class CheckpointRootResetPermit final"),
        )
    ]
    check(
        "checkpoint_root_reset_permit_is_private_nontransferable_and_single_use",
        "private:" in permit_class
        and "CheckpointRootResetPermit(const CheckpointRootResetPermit&) = delete;"
        in permit_class
        and "CheckpointRootResetPermit(CheckpointRootResetPermit&&) = delete;"
        in permit_class
        and "bool consumed_ = false;" in permit_class,
        "only the focused authorizer can mint a noncopyable, nonmovable one-shot reset capability",
    )

    reset_authorize = function_slice(
        runtime,
        "authorize_checkpoint_root_reset_in_write_transaction_or_throw(",
        "void delete_checkpoint_root_with_permit_in_write_transaction_or_throw(",
    )
    reset_delete = function_slice(
        runtime,
        "void delete_checkpoint_root_with_permit_in_write_transaction_or_throw(",
    )
    reset_savepoint_pos = reset_delete.find("SyncSqliteSavepoint reset(")
    reset_sql_pos = reset_delete.find(
        "DELETE FROM main.sync_session_checkpoints WHERE session_id=?;"
    )
    reset_release_pos = reset_delete.find("reset.release();")
    reset_consume_pos = reset_delete.find("permit.consumed_ = true;")
    check(
        "root_reset_compound_transition_has_nested_rollback_owner",
        0 <= reset_savepoint_pos < reset_sql_pos < reset_release_pos < reset_consume_pos
        and "permit.transaction_authority_" in reset_delete
        and "caught late reset failure cannot commit the destructive DELETE prefix"
        in sqlite_test,
        "positions "
        f"savepoint={reset_savepoint_pos} delete={reset_sql_pos} "
        f"release={reset_release_pos} consume={reset_consume_pos}",
    )

    check(
        "root_reset_binds_recipient_evidence_to_exact_typed_transaction_generation",
        "transaction_authority.authorizes_write(db)" in reset_authorize
        and "require_recipient_write_authority_or_throw(" in reset_authorize
        and "permit.transaction_authority_.authorizes_write(db)" in reset_delete
        and "permit.consumed_" in reset_delete,
        "authorization and consumption both verify the same live typed write-transaction generation",
    )

    active_cpp = [
        path
        for path in root.rglob("*.cpp")
        if "REVISION_EVIDENCE" not in path.parts
        and not any(part.startswith("build") for part in path.relative_to(root).parts)
    ]
    root_delete_users = [
        path.relative_to(root).as_posix()
        for path in active_cpp
        if "DELETE FROM main.sync_session_checkpoints" in path.read_text(errors="replace")
    ]
    check(
        "checkpoint_root_delete_has_one_focused_invariant_owner",
        root_delete_users == ["src/sync_checkpoint_owner_fence.cpp"]
        and "DELETE FROM main.sync_session_checkpoints" in reset_delete,
        f"active root-delete SQL owners={root_delete_users}",
    )

    unqualified_authority_sql = re.findall(
        r"(?:FROM|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+"
        r"(sync_session_(?:checkpoint_owner_modes|"
        r"resume_transfer_daemon_owner_locks|checkpoints))",
        runtime,
    )
    check(
        "authority_bearing_sql_is_explicitly_main_qualified",
        not unqualified_authority_sql
        and "FROM main.sync_session_checkpoint_owner_modes" in runtime
        and "FROM main.sync_session_resume_transfer_daemon_owner_locks" in runtime
        and "DELETE FROM main.sync_session_checkpoints" in runtime,
        f"unqualified authority SQL={unqualified_authority_sql}",
    )

    persist_slice = function_slice(
        domain,
        "SyncValidationResult persist_sync_fake_peer_session_checkpoint(",
        "SyncValidationResult load_sync_session_checkpoint_resume_view(",
    )
    persist_tx = persist_slice.find("SyncSqliteTransaction transaction(")
    permit_issue = persist_slice.find(
        "authorize_checkpoint_root_reset_in_write_transaction_or_throw("
    )
    root_delete = persist_slice.find(
        "delete_checkpoint_root_with_permit_in_write_transaction_or_throw("
    )
    root_insert = persist_slice.find("INSERT INTO sync_session_checkpoints")
    persist_commit = persist_slice.find("transaction.commit()")
    check(
        "checkpoint_replacement_uses_typed_raii_transaction_and_ordered_reset_permit",
        0 <= persist_tx < permit_issue < root_delete < root_insert < persist_commit
        and "BEGIN IMMEDIATE;" not in persist_slice
        and '"COMMIT;"' not in persist_slice
        and '"ROLLBACK;"' not in persist_slice
        and "transaction.authority()" in persist_slice,
        f"positions transaction={persist_tx} authorize={permit_issue} delete={root_delete} insert={root_insert} commit={persist_commit}",
    )

    check(
        "administrative_disable_is_modeled_but_not_forgeable_by_production_api",
        "administratively-disabled" in policy
        and "sync-checkpoint-owner-admin-disable:v1:" in policy
        and "SET ownership_mode='administratively-disabled'" not in runtime
        and "disable_owner" not in runtime_header.lower()
        and "administrative_disable" not in capability_header,
        "policy can interpret separately evidenced disable state, but this revision exposes no transition that fabricates it",
    )

    public_users = include_users(root, "anonsync_sync_checkpoint_owner_fence.hpp")
    policy_users = include_users(root, "sync_checkpoint_owner_fence_policy.hpp")
    runtime_users = include_users(root, "sync_checkpoint_owner_fence.hpp")
    check(
        "owner_fence_headers_have_narrow_include_surfaces",
        public_users
        == [
            "include/anonsync_core.hpp",
            "src/sync_checkpoint_owner_fence.hpp",
            "src/sync_checkpoint_owner_fence_policy.hpp",
        ]
        and policy_users
        == [
            "src/sync_checkpoint_owner_fence.cpp",
            "src/sync_checkpoint_owner_fence_policy.cpp",
            "tests/sync_checkpoint_owner_fence_policy_test.cpp",
        ]
        and runtime_users
        == [
            "src/sync_checkpoint_owner_fence.cpp",
            "src/sync_domain.cpp",
            "src/sync_peer_ingestion.cpp",
            "tests/sync_checkpoint_owner_fence_sqlite_test.cpp",
        ],
        f"public={public_users} policy={policy_users} runtime={runtime_users}",
    )

    schema_users = include_users(root, "sync_checkpoint_owner_schema.hpp")
    schema_identity_users = include_users(root, "sync_sqlite_schema_identity.hpp")
    check(
        "owner_schema_and_shared_identity_headers_have_narrow_surfaces",
        schema_users
        == [
            "src/sync_checkpoint_owner_fence.cpp",
            "src/sync_checkpoint_owner_schema.cpp",
            "tests/sync_checkpoint_owner_schema_test.cpp",
        ]
        and schema_identity_users
        == [
            "src/sync_checkpoint_owner_schema.cpp",
            "src/sync_peer_ingress_payload_store_schema.cpp",
            "src/sync_peer_ingress_schema.cpp",
            "src/sync_sqlite_schema_identity.cpp",
            "tests/peer_ingress_schema_attestation_test.cpp",
        ],
        f"owner_schema={schema_users} schema_identity={schema_identity_users}",
    )

    acquire = function_slice(
        runtime,
        "acquire_owner_generation_in_write_transaction_or_throw(",
        "void release_owner_generation_in_write_transaction_or_throw(",
    )
    signature = acquire[: acquire.find(") {") + 3] if ") {" in acquire else acquire[:1000]
    write_tx_pos = acquire.find("require_write_transaction_or_throw")
    load_pos = acquire.find("load_stored_owner_lock_evidence_or_throw")
    plan_pos = acquire.find("sync_checkpoint_owner_fence_policy::plan_acquisition")
    mutate_pos = min(
        pos
        for pos in [
            acquire.find("UPDATE main.sync_session_resume_transfer_daemon_owner_locks"),
            acquire.find("INSERT INTO main.sync_session_resume_transfer_daemon_owner_locks"),
        ]
        if pos >= 0
    ) if ("UPDATE main.sync_session_resume_transfer_daemon_owner_locks" in acquire and "INSERT INTO main.sync_session_resume_transfer_daemon_owner_locks" in acquire) else -1
    check(
        "acquisition_mints_generation_from_durable_row_inside_caller_write_transaction",
        "owner_lock_epoch" not in signature
        and 0 <= write_tx_pos < load_pos < plan_pos < mutate_pos
        and "out.owner_lock_epoch = decision.owner_lock_epoch;" in acquire
        and "existing.owner_lock_epoch" in acquire,
        f"positions write_tx={write_tx_pos} load={load_pos} plan={plan_pos} mutate={mutate_pos}",
    )

    acquire_attest_pos = acquire.find("attest_checkpoint_owner_schema_or_throw(")
    recipient = function_slice(
        runtime,
        "void require_recipient_write_authority_or_throw(",
        "CheckpointRootResetPermit::CheckpointRootResetPermit(",
    )
    recipient_attest_pos = recipient.find("attest_checkpoint_owner_schema_or_throw(")
    recipient_load_pos = recipient.find("load_stored_owner_lock_evidence_or_throw")
    check(
        "every_owner_transition_attests_schema_before_interpreting_rows",
        0 <= write_tx_pos < acquire_attest_pos < load_pos
        and 0 <= recipient_attest_pos < recipient_load_pos
        and reset_delete.find("attest_checkpoint_owner_schema_or_throw(")
        < reset_delete.find("DELETE FROM main.sync_session_checkpoints"),
        f"acquire attest={acquire_attest_pos} load={load_pos}; recipient attest={recipient_attest_pos} load={recipient_load_pos}",
    )
    check(
        "takeover_uses_compare_and_replace_on_prior_generation",
        '"WHERE session_id=? AND owner_lock_epoch=?;"' in acquire
        and "existing.owner_lock_epoch" in acquire
        and "compare-and-replace did not affect exactly one row" in acquire
        and "sqlite3_changes(db) != 1" in acquire,
        "stored generation is both the increment source and the update precondition",
    )
    check(
        "acquisition_reloads_and_verifies_committed_generation_evidence",
        "proof prepare" in acquire
        and "proof did not reload exact minted evidence" in acquire
        and "sqlite3_step(proof_stmt.stmt) != SQLITE_DONE" in acquire,
        "returned capability is checked against the exact row written in the caller transaction",
    )

    release = function_slice(
        runtime,
        "void release_owner_generation_in_write_transaction_or_throw(",
        "void require_recipient_write_authority_or_throw(",
    )
    release_write_tx = release.find("require_write_transaction_or_throw")
    release_fence = release.find("require_recipient_write_authority_or_throw")
    release_update = release.find("UPDATE main.sync_session_resume_transfer_daemon_owner_locks")
    check(
        "release_is_an_exact_recipient_fenced_transition",
        0 <= release_write_tx < release_fence < release_update
        and "const SyncSessionCheckpointDaemonOwnerCapability& capability" in release
        and "AND owner_lock_epoch=? AND lock_state='held' AND released_at_epoch=0" in release
        and "did not affect exactly one live generation" in release
        and "sqlite3_changes(db) != 1" in release,
        f"positions write_tx={release_write_tx} fence={release_fence} update={release_update}",
    )

    acquire_wrapper = function_slice(
        domain,
        "ResumeTransferDaemonOwnerLockRecord acquire_resume_transfer_daemon_owner_lock_or_throw(",
        "void release_resume_transfer_daemon_owner_lock_or_throw(",
    )
    release_wrapper = function_slice(
        domain,
        "void release_resume_transfer_daemon_owner_lock_or_throw(",
        "std::string checkpoint_resume_transfer_execution_idempotency_key_or_throw(",
    )
    check(
        "domain_wrappers_own_immediate_transaction_and_commit_after_focused_boundary",
        "SyncSqliteTransactionMode::Immediate" in acquire_wrapper
        and "acquire_owner_generation_in_write_transaction_or_throw" in acquire_wrapper
        and acquire_wrapper.find("acquire_owner_generation_in_write_transaction_or_throw")
        < acquire_wrapper.find("transaction.commit()")
        and "SyncSqliteTransactionMode::Immediate" in release_wrapper
        and "release_owner_generation_in_write_transaction_or_throw" in release_wrapper
        and release_wrapper.find("release_owner_generation_in_write_transaction_or_throw")
        < release_wrapper.find("transaction.commit()"),
        "domain owns database open/schema/commit while the focused boundary owns row interpretation and mutation",
    )

    internal_lease_struct = struct_slice(
        core_internal_header, "SyncInternalCheckpointMutationOwnerLease"
    )
    internal_acquire = function_slice(
        domain,
        "SyncValidationResult sync_internal_acquire_checkpoint_mutation_owner_lease(",
        "SyncValidationResult sync_internal_release_checkpoint_mutation_owner_lease(",
    )
    internal_release = function_slice(
        domain,
        "SyncValidationResult sync_internal_release_checkpoint_mutation_owner_lease(",
        "bool sync_checkpoint_apply_intent_routes_remote_file_bytes_to_staging(",
    )
    check(
        "internal_mutation_lease_is_database_minted_and_exactly_retired",
        "SyncSessionCheckpointDaemonOwnerCapability capability;"
        in internal_lease_struct
        and "std::uint64_t acquired_at_epoch = 0;" in internal_lease_struct
        and "std::uint64_t expires_at_epoch = 0;" in internal_lease_struct
        and "acquire_resume_transfer_daemon_owner_lock_or_throw(" in internal_acquire
        and "out.capability.owner_lock_id = record.owner_lock_id;" in internal_acquire
        and "out.capability.owner_lock_epoch = record.owner_lock_epoch;"
        in internal_acquire
        and "release_resume_transfer_daemon_owner_lock_or_throw(" in internal_release
        and "sqlite_path, session_id, capability, released_at_epoch" in internal_release,
        "cross-translation-unit orchestration can only receive database-minted evidence and retire that exact capability",
    )

    repair_guard = function_slice(
        operator_cli,
        "class SyncOperatorRepairOwnerLeaseGuard final",
        "std::string sync_cli_json_bool",
    )
    check(
        "operator_repair_owner_guard_is_scoped_and_nontransferable",
        "const SyncOperatorRepairOwnerLeaseGuard&) = delete;" in repair_guard
        and "SyncOperatorRepairOwnerLeaseGuard&&) = delete;" in repair_guard
        and "~SyncOperatorRepairOwnerLeaseGuard()" in repair_guard
        and "sync_internal_release_checkpoint_mutation_owner_lease(" in repair_guard
        and "if (released.ok) armed_ = false;" in repair_guard,
        "the repair owner lease cannot be copied or moved and has a no-throw cleanup fallback",
    )

    standalone_repair = function_slice(
        operator_cli,
        "int run_sync_checkpoint_sidecar_repair_reset_command(",
        "int run_sync_checkpoint_daemon_run_command(",
    )
    workflow_repair = function_slice(
        operator_cli,
        "int run_sync_checkpoint_operator_recovery_workflow_command(",
    )
    standalone_acquire = standalone_repair.find(
        "sync_internal_acquire_checkpoint_mutation_owner_lease("
    )
    standalone_propagate = standalone_repair.find(
        "options.daemon_owner_capability = owner_lease.capability;"
    )
    standalone_mutate = standalone_repair.find(
        "repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event("
    )
    standalone_release = standalone_repair.find("owner_guard.release_now()")
    workflow_acquire = workflow_repair.find(
        "sync_internal_acquire_checkpoint_mutation_owner_lease("
    )
    workflow_propagate = workflow_repair.find(
        "config.repair_options.daemon_owner_capability ="
    )
    workflow_mutate = workflow_repair.find(
        "repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event("
    )
    workflow_release = workflow_repair.find("repair_owner_guard.release_now()")
    check(
        "operator_repair_paths_acquire_propagate_and_release_exact_authority",
        0
        <= standalone_acquire
        < standalone_propagate
        < standalone_mutate
        < standalone_release
        and 0
        <= workflow_acquire
        < workflow_propagate
        < workflow_mutate
        < workflow_release
        and "repair_owner_lock" in workflow_repair
        and "repair_owner_release_run" in workflow_repair,
        "both standalone and workflow repair paths mint before mutation, pass the exact capability, retire afterward, and report release evidence",
    )

    recipient_source = domain + "\n" + peer
    fence_contexts = [
        "bound peer chunk acceptance db advance",
        "bound peer chunk response batch acceptance sidecar publication",
        "staging repair filesystem mutation",
        "resume materialization",
        "resume cleanup",
        "resume transfer claim",
        "resume transfer terminal reset",
        "resume transfer executor",
        "terminal tombstone apply",
        "terminal conflict tombstone apply",
        "terminal conflict file apply",
        "daemon lease event",
        "sidecar review repair reset",
        "bound peer sidecar review event",
        "sidecar review quarantine",
    ]
    missing_contexts = [token for token in fence_contexts if token not in recipient_source]
    fence_call_count = recipient_source.count(
        "require_recipient_write_authority_or_throw("
    )
    check(
        "mutation_families_recheck_owner_at_recipient",
        not missing_contexts and fence_call_count >= len(fence_contexts),
        f"fence calls={fence_call_count} missing contexts={missing_contexts}",
    )

    sidecar_accept = function_slice(
        domain,
        "SyncValidationResult accept_sync_session_checkpoint_bound_peer_chunk_response_batch_envelope(",
        "SyncValidationResult load_sync_session_checkpoint_resume_view(",
    )
    reservation_pos = sidecar_accept.find("SyncSqliteTransaction owner_reservation")
    sidecar_fence_pos = sidecar_accept.find("require_recipient_write_authority_or_throw")
    write_pos = sidecar_accept.find("write_sync_staged_chunk")
    reservation_commit_pos = sidecar_accept.find("owner_reservation.commit()")
    check(
        "sidecar_publication_holds_write_reservation_across_filesystem_effects",
        0 <= reservation_pos < sidecar_fence_pos < write_pos < reservation_commit_pos
        and "SyncSqliteTransactionMode::Immediate" in sidecar_accept,
        f"positions reservation={reservation_pos} fence={sidecar_fence_pos} write={write_pos} commit={reservation_commit_pos}",
    )

    staging = function_slice(
        domain,
        "SyncValidationResult repair_sync_session_checkpoint_staging_artifacts(",
        "SyncValidationResult plan_sync_session_checkpoint_resume_actions(",
    )
    staging_tx = staging.find("SyncSqliteTransaction owner_reservation")
    staging_fence = staging.find("require_recipient_write_authority_or_throw")
    remove_positions = [
        pos
        for pos in [staging.find("fs::remove"), staging.find("remove_file")]
        if pos >= 0
    ]
    staging_remove = min(remove_positions) if remove_positions else -1
    staging_commit = staging.find("owner_reservation.commit()")
    check(
        "stale_artifact_repair_holds_write_reservation_across_removals",
        0 <= staging_tx < staging_fence < staging_remove < staging_commit
        and "SyncSqliteTransactionMode::Immediate" in staging,
        f"positions transaction={staging_tx} fence={staging_fence} remove={staging_remove} commit={staging_commit}",
    )

    propagation_tokens = [
        "claim_options.daemon_owner_capability = options.daemon_owner_capability;",
        "execution_options.daemon_owner_capability = options.daemon_owner_capability;",
        "binding.daemon_owner_capability = options.daemon_owner_capability;",
        "transfer_options.daemon_owner_capability = options.daemon_owner_capability;",
        "materialize_options.daemon_owner_capability = options.daemon_owner_capability;",
        "cleanup_options.daemon_owner_capability = options.daemon_owner_capability;",
        "startup_recovery_options.daemon_owner_capability = daemon_owner_capability;",
        "pass_options.daemon_owner_capability = daemon_owner_capability;",
    ]
    propagation_text = scheduler + "\n" + peer + "\n" + domain
    check(
        "orchestration_propagates_exact_capability_without_reconstruction",
        all(token in propagation_text for token in propagation_tokens),
        "scheduler, recovery sweep, cycle, and daemon branches forward the durable capability",
    )

    daemon_tokens = [
        "daemon_owner_capability.session_id = options.session_id;",
        "daemon_owner_capability.daemon_id = daemon_id;",
        "daemon_owner_capability.worker_id = worker_id;",
        "daemon_owner_capability.owner_lock_id = daemon_owner_lock.owner_lock_id;",
        "daemon_owner_capability.owner_lock_epoch = daemon_owner_lock.owner_lock_epoch;",
    ]
    check(
        "daemon_constructs_capability_only_from_acquired_record",
        all(token in domain for token in daemon_tokens)
        and "initial_worker_lease_epoch," not in signature,
        "caller lease epoch is no longer accepted as owner generation authority",
    )

    positive_time_messages = [
        "staging repair owner_fence_now_epoch must be positive",
        "resume materialization owner_fence_now_epoch must be positive",
        "resume cleanup owner_fence_now_epoch must be positive",
        "resume cycle owner_fence_now_epoch must be positive",
    ]
    check(
        "external_effect_fence_times_fail_closed_at_api_boundary",
        all(message in domain for message in positive_time_messages),
        "zero observation time is rejected before planning or filesystem work",
    )

    policy_test_tokens = [
        "first owner acquisition did not mint generation one",
        "released owner takeover did not increment sticky generation",
        "owner-row absence after reset reused or lost sticky generation",
        "administratively disabled mode did not reactivate with a new generation",
        "expired owner takeover did not increment generation",
        "live owner was overwritten",
        "acquisition clock regression was accepted",
        "mode/owner generation disagreement was accepted",
        "owner generation overflow was accepted",
        "owner lease exceeded SQLite durable integer range",
        "out-of-range durable owner integer was accepted",
        "partial owner capability was accepted",
        "expired owner capability authorized a mutation",
        "release erased sticky ownership",
        "root-reset owner gap admitted an empty capability",
        "noncanonical owner id was accepted",
    ]
    check(
        "focused_pure_policy_corpus_is_adversarial",
        all(token in policy_test for token in policy_test_tokens)
        and "owner fence policy checks" in policy_test,
        "first mint, takeover, malformed state, time, overflow, partial and stale capability cases are independent",
    )

    sqlite_test_tokens = [
        "database acquisition mints generation one from absent evidence",
        "database acquisition cannot overwrite a live generation",
        "release cannot reopen capability-free mutation",
        "release and reacquisition mint the next sticky generation",
        "stale generation cannot release its successor",
        "newly minted durable generation authorizes its exact recipient",
        "inside the recipient write transaction",
        "generation one is fenced after generation two takeover",
        "stale generation produces no recipient effect",
        "new durable generation can mutate after takeover",
        "forged durable owner id fails canonical recomputation",
        "malformed durable evidence produces no effect",
        "root reset executes the real foreign-key owner cascade",
        "sticky mode survives and advances across root cascade",
        "checkpoint reset cannot launder ownership into unowned mode",
        "reset permit cannot cross typed transaction generations",
        "hostile sticky-mode lookalike is rejected before legacy backfill",
        "hostile schema refusal produces no legacy owner-mode row",
        "recipient refuses TEMP schema shadow before interpreting owner evidence",
    ]
    check(
        "focused_sqlite_recipient_proof_demonstrates_no_stale_effect",
        all(token in sqlite_test for token in sqlite_test_tokens)
        and "effect_count(db) == 2" in sqlite_test
        and "effect_count(db) == 3" in sqlite_test,
        "database mint/release plus A->B takeover reject stale authority in immediate transactions without recipient effects",
    )

    check(
        "domain_corpus_locks_in_minted_generation_sequence",
        "held_owner.owner_lock_epoch == 1" in selftests
        and "takeover_loop_result.daemon_owner_lock_epoch == held_owner.owner_lock_epoch + 1"
        in selftests
        and "mints the first durable generation" in selftests
        and "mints the next durable generation" in selftests,
        "full-domain fixture proves first mint and expired-owner successor generation",
    )

    check(
        "domain_corpus_proves_operator_repair_owner_lifecycle",
        "repair_owner_lock" in selftests
        and 'at("acquire_attempted").boolean(false)' in selftests
        and 'at("release_attempted").boolean(false)' in selftests
        and 'at("released").boolean(false)' in selftests
        and "sidecar operator fixture acquires an exact successor owner generation before mutation"
        in selftests
        and "sidecar operator fixture retires its exact generation before the CLI acquires a successor"
        in selftests
        and "sidecar_review_quarantine_options.daemon_owner_capability ="
        in selftests
        and "sidecar_review_repair_options.daemon_owner_capability ="
        in selftests,
        "the full-domain corpus proves workflow, direct operator, and standalone CLI capability lifecycles",
    )

    schema_test_tokens = [
        "a view cannot occupy the sticky owner-mode authority name",
        "constraint-free owner-mode table is rejected",
        "explicit owner-mode index is treated as unreviewed schema code",
        "TEMP trigger cannot program a main owner table",
        "checkpoint-root deletion cannot be redirected by a trigger program",
        "hostile owner-lock evidence is rejected before mode-table creation",
        "owner-lock foreign-key cascade drift is rejected",
        "non-key checkpoint root",
        "genuinely pre-owner database",
        "case-insensitive owner-lock aliases",
        "case-insensitive TEMP aliases",
        "failed legacy backfill rolls mode-table creation back",
        "failed owner-schema migration releases its nested savepoint cleanly",
        "refuses a connection that cannot enforce the reviewed cascade",
        "refuses a connection that has disabled reviewed CHECK constraints",
        "savepoint publication never commits the caller transaction",
        "caller rollback removes schema created through the nested migration savepoint",
    ]
    check(
        "focused_owner_schema_corpus_covers_hostile_objects_and_atomic_ordering",
        all(token in schema_test for token in schema_test_tokens)
        and "sync checkpoint owner schema checks" in schema_test,
        "focused corpus covers views, permissive tables, indexes, case-folded aliases, live constraint profile, nested savepoints, main/TEMP triggers, FK drift, root-anchor drift, atomic rollback, and legacy absence",
    )

    peer_schema_sources = source_list_block(cmake, "ANONSYNC_PEER_INGRESS_SCHEMA_SOURCES")
    identity_links = target_block(
        cmake, "target_link_libraries", "anonsync_peer_ingress_schema"
    )
    check(
        "schema_identity_parser_is_shared_without_duplicate_compilation",
        "src/sync_sqlite_schema_identity.cpp" not in peer_schema_sources
        and "add_library(anonsync_sqlite_schema_identity STATIC" in cmake
        and "anonsync_sqlite_schema_identity" in identity_links
        and "anonsync_sqlite_schema_identity" in schema_links,
        "peer-ingress and owner-schema boundaries share one independently compiled canonicalizer target",
    )

    focused_targets = foreach_block(cmake, "ANONSYNC_FOCUSED_BOUNDARY_TARGET")
    sanitizer_targets = source_list_block(cmake, "ANONSYNC_SANITIZER_COMPILE_TARGETS")
    check(
        "focused_build_graph_covers_owner_policy_schema_and_recipient_boundaries",
        all(
            target in focused_targets
            for target in [
                "anonsync_sync_checkpoint_owner_fence_policy",
                "anonsync_sync_checkpoint_owner_fence_policy_test",
                "anonsync_sync_checkpoint_owner_schema",
                "anonsync_sync_checkpoint_owner_schema_test",
                "anonsync_sync_checkpoint_owner_fence",
                "anonsync_sync_checkpoint_owner_fence_sqlite_test",
                "anonsync_sqlite_schema_identity",
            ]
        )
        and all(
            target in sanitizer_targets
            for target in [
                "anonsync_sync_checkpoint_owner_fence_policy",
                "anonsync_sync_checkpoint_owner_fence_policy_test",
                "anonsync_sync_checkpoint_owner_schema",
                "anonsync_sync_checkpoint_owner_schema_test",
                "anonsync_sync_checkpoint_owner_fence",
                "anonsync_sync_checkpoint_owner_fence_sqlite_test",
                "anonsync_sqlite_schema_identity",
            ]
        ),
        "independent policy, schema, canonicalizer, recipient boundaries and proofs participate in no-core and sanitizer graphs",
    )

    check(
        "focused_proofs_are_registered_release_obligations",
        "add_test(NAME anonsync_sync_checkpoint_owner_fence_policy_test" in cmake
        and "add_test(NAME anonsync_sync_checkpoint_owner_schema_test" in cmake
        and "add_test(NAME anonsync_sync_checkpoint_owner_fence_sqlite_test" in cmake
        and "COMMAND anonsync_sync_checkpoint_owner_fence_policy_test" in cmake
        and "COMMAND anonsync_sync_checkpoint_owner_schema_test" in cmake
        and "COMMAND anonsync_sync_checkpoint_owner_fence_sqlite_test" in cmake,
        "pure policy, hostile schema, and SQLite recipient proofs are visible to CTest",
    )

    passed = sum(1 for item in checks if item["passed"])
    total = len(checks)
    report = {
        "format": "anonsync-sync-checkpoint-owner-fence-source-audit-v2",
        "root": str(root),
        "passed": passed,
        "failed": total - passed,
        "checks": checks,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n")

    for item in checks:
        marker = "PASS" if item["passed"] else "FAIL"
        print(f"[{marker}] {item['check_id']}: {item['detail']}")
    print(f"sync checkpoint owner fence source audit: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
