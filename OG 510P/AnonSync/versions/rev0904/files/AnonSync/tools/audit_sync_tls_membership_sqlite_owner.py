#!/usr/bin/env python3
"""Lexical hygiene audit for durable TLS membership SQLite authority.

This inventory checks reviewed schema, digest-chain, compare-and-swap, rollback,
and composition vocabulary. It deliberately does not claim to prove SQLite or
filesystem durability, SHA-256 collision resistance, malicious-writer defense,
external-anchor persistence, authorization freshness, race freedom, or C++
object semantics. Compiled adversarial tests, independent toolchains, and an
external trusted-anchor store must carry those obligations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def body(text: str, marker: str) -> str:
    start = text.find(marker)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def ordered(text: str, *tokens: str) -> bool:
    position = 0
    for token in tokens:
        position = text.find(token, position)
        if position < 0:
            return False
        position += len(token)
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = {
        "header": root / "src/sync_replica_tls_membership_sqlite_owner.hpp",
        "source": root / "src/sync_replica_tls_membership_sqlite_owner.cpp",
        "profile_header": root / "src/sync_replica_tls_policy_sqlite_profile.hpp",
        "profile": root / "src/sync_replica_tls_policy_sqlite_profile.cpp",
        "anchored_header": root / "src/sync_replica_tls_membership_anchored_owner.hpp",
        "anchored_source": root / "src/sync_replica_tls_membership_anchored_owner.cpp",
        "anchor_runtime": root / "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp",
        "snapshot_header": root / "src/sync_replica_tls_membership_snapshot.hpp",
        "server_header": root / "src/sync_replica_file_tls_server.hpp",
        "server_source": root / "src/sync_replica_file_tls_server.cpp",
        "runtime_header": root / "tests/sync_replica_tls_membership_sqlite_owner_test.hpp",
        "runtime": root / "tests/sync_replica_tls_membership_sqlite_owner_test.cpp",
        "transport_runtime": root / "tests/sync_replica_tls_transport_test.cpp",
        "cmake": root / "CMakeLists.txt",
        "verifier": root / "tools/verify_release_package.py",
    }
    missing = sorted(str(path.relative_to(root)) for path in paths.values() if not path.is_file())
    text = {name: path.read_text(encoding="utf-8") if path.is_file() else "" for name, path in paths.items()}
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    require(not missing, "required_files_exist", f"missing={missing}")
    header = text["header"]
    source = text["source"]
    profile_header = text["profile_header"]
    profile = text["profile"]
    anchored_header = text["anchored_header"]
    anchored_source = text["anchored_source"]
    anchor_runtime = text["anchor_runtime"]
    server_header = text["server_header"]
    server_source = text["server_source"]
    runtime = text["runtime"]
    transport_runtime = text["transport_runtime"]
    cmake = text["cmake"]
    verifier = text["verifier"]

    require(
        "kSyncReplicaTlsMembershipMaxHistoryRecords = 65536U" in header
        and "kSyncReplicaTlsMembershipMaxRetainedEntryRows = 4194304U" in header
        and "sync_replica_tls_membership_append_fits_hard_limits" in header
        and "candidate_entry_rows <=" in header,
        "persistent_history_has_explicit_hard_ceilings",
        "complete restoration and the crossing append are both bounded",
    )
    anchor = body(header, "struct SyncReplicaTlsMembershipAnchor final")
    require(
        "state_generation" in anchor and "chain_digest" in anchor
        and "external durable-store implementation" in header,
        "anchor_binds_generation_and_digest_with_store_nonclaim",
        "digest is never treated as meaningful without its exact cutpoint",
    )
    authority = body(header, "class SyncReplicaTlsMembershipAuthority final")
    require(
        bool(authority)
        and "const SyncReplicaTlsMembershipAuthority&) = delete" in authority
        and "SyncReplicaTlsMembershipAuthority&&) noexcept = default" in authority
        and "friend class SyncReplicaTlsMembershipSqliteOwner" in authority
        and "explicit SyncReplicaTlsMembershipAuthority(" in authority,
        "authority_is_move_only_and_owner_constructible",
        "raw snapshots cannot impersonate a committed accepted-session capability",
    )
    owner = body(header, "class SyncReplicaTlsMembershipSqliteOwner final")
    require(
        bool(owner)
        and "const SyncReplicaTlsMembershipSqliteOwner&) = delete" in owner
        and "SyncReplicaTlsMembershipSqliteOwner&&) = delete" in owner
        and "SyncReplicaTlsPolicySqliteConnectionBinding database_" in owner
        and "database_.database_filename()" in owner,
        "owner_is_stationary_on_one_exact_database_slot",
        "publication ownership cannot silently migrate or copy",
    )
    binding = body(
        profile,
        "SyncReplicaTlsPolicySqliteConnectionBinding::require_current_or_throw(",
    )
    require(
        "SyncSqliteSerializedDbBorrow retained_lifetime_" in profile_header
        and "SqlitePathFamilyGuard database_path_guard_" in profile_header
        and "database_generation_" in profile_header
        and ordered(
            binding,
            "retained_lifetime_.get()",
            "database_.get()",
            "database_.generation() != database_generation_",
            "sqlite3_db_filename",
            "database_filename_ != observed_filename",
            "database_path_guard_.verify_open_database_or_throw",
        )
        and source.count("database_.require_current_or_throw") >= 3
        and "renamed-membership.displaced.sqlite3" in anchor_runtime,
        "owner_pins_and_reproves_exact_connection_generation",
        "handle-slot move/refill and live path displacement cannot silently redirect membership history authority",
    )

    require(
        "Correctness-oracle owner" in header
        and "O(history + retained entries)" in header
        and "not a scalable" in header
        and "production index" in header,
        "full_history_oracle_scope_is_explicit",
        "correctness validation is not misrepresented as scalable serving architecture",
    )
    require(
        "not signed provenance" in header
        and "malicious local writer" in header
        and "every external" in header
        and "anchor available to the process" in header,
        "chain_and_anchor_threat_nonclaims_are_explicit",
        "unkeyed hashes do not become signatures or host-compromise defense",
    )

    require(
        "may emit multiple capabilities" in header
        and "one-session-per-generation nonce" in header
        and "later policy rotation" in header
        and "retroactively revoke" in header,
        "authority_issuance_and_revocation_cutpoint_nonclaim_is_explicit",
        "move-only use is not misrepresented as a unique generation lease or live revocation",
    )

    require(
        all(token in source for token in (
            "CREATE TABLE sync_replica_tls_membership_meta(",
            "CREATE TABLE sync_replica_tls_membership_updates(",
            "CREATE TABLE sync_replica_tls_membership_entries(",
            ")) STRICT",
        )),
        "schema_uses_three_exact_strict_tables",
        "metadata, history, and canonical entries have a closed reviewed shape",
    )
    require(
        "schema_object_count_or_throw" in source
        and "name GLOB 'sync_replica_tls_membership_*'" in source
        and "tbl_name IN ('sync_replica_tls_membership_meta'" in source
        and "count != kSchema.size()" in source,
        "main_schema_closure_catches_named_and_attached_objects",
        "arbitrary-named indexes or triggers on authority tables are rejected",
    )
    require(
        "temp_schema_attachment_count_or_throw" in source
        and "FROM temp.sqlite_schema" in source
        and "unowned temp schema attachments" in source,
        "connection_local_temp_schema_is_closed",
        "TEMP triggers cannot silently rewrite owner statements on one connection",
    )
    schema_init = body(source, "void initialize_or_attest_schema_or_throw(")
    require(
        ordered(
            schema_init,
            "SyncSqliteTransactionMode::Immediate",
            "attest_sync_replica_tls_policy_sqlite_backend_or_throw",
            "schema_object_count_or_throw",
            "if (existing == 0U)",
            "for (const auto& definition : kSchema)",
            "sqlite_exec_or_throw",
            "attest_schema_or_throw",
            "transaction.commit()",
        ),
        "first_open_decision_is_serialized_with_creation",
        "two owners cannot both act on an authority-free pretransaction observation",
    )

    connection_config = body(
        profile,
        "void configure_sync_replica_tls_policy_sqlite_connection_or_throw(",
    )
    connection_attest = body(profile, "void require_connection_profile_or_throw(")
    require(
        all(token in connection_config for token in (
            "SQLITE_DBCONFIG_DEFENSIVE", "SQLITE_DBCONFIG_TRUSTED_SCHEMA",
            "SQLITE_DBCONFIG_ENABLE_TRIGGER", "SQLITE_DBCONFIG_ENABLE_VIEW",
            "SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION", "SQLITE_LIMIT_ATTACHED",
            "PRAGMA read_uncommitted=OFF", "PRAGMA ignore_check_constraints=OFF",
        ))
        and all(token in connection_attest for token in (
            "require_db_config_or_throw", "SQLITE_LIMIT_ATTACHED",
            "PRAGMA database_list", "attached database outside owner authority",
            "mutable connection pragma escaped the owner profile",
        )),
        "dedicated_connection_profile_is_configured_and_reattested",
        "unsafe schema execution, dirty reads, ignored CHECKs, extensions, and attached schemas fail closed",
    )

    backend = body(
        profile,
        "void attest_sync_replica_tls_policy_sqlite_backend_or_throw(",
    )
    filename = body(
        profile,
        "std::string sync_replica_tls_policy_sqlite_main_filename_or_throw(",
    )
    require(
        ordered(filename, "sqlite3_db_filename", "has no durable main filename")
        and ordered(
            backend,
            "sync_replica_tls_policy_sqlite_main_filename_or_throw",
            "sqlite3_db_readonly",
            "PRAGMA main.journal_mode",
            "PRAGMA main.synchronous",
        ),
        "backend_profile_requires_named_writable_database",
        "in-memory and read-only handles cannot mint durable write authority",
    )
    require(
        all(token in backend for token in ('"wal"', '"delete"', '"truncate"', '"persist"'))
        and "journal mode is not durable" in backend,
        "journal_mode_allowlist_excludes_memory_and_off",
        "authority publication requires a rollback-capable persistent journal family",
    )
    require(
        "journal_mode == \"wal\" ? 2U : 3U" in backend
        and "WAL synchronous mode is below FULL" in backend
        and "rollback-journal synchronous mode is below EXTRA" in backend
        and "necessary" in backend
        and "not a proof of the storage stack" in backend,
        "synchronous_policy_distinguishes_wal_and_rollback",
        "WAL requires FULL; rollback journals require EXTRA without overclaiming hardware durability",
    )

    genesis = body(source, "std::string genesis_chain_digest(")
    update = body(source, "std::string update_chain_digest(")
    require(
        "anonsync:sync-replica-tls-membership-chain:genesis:v1" in source
        and ordered(genesis, "kGenesisDigestDomain", "kSchemaVersion", "folder_id", "local_actor"),
        "genesis_is_domain_separated_and_identity_bound",
        "an empty policy database has one deterministic service-scoped anchor",
    )
    require(
        "anonsync:sync-replica-tls-membership-chain:update:v1" in source
        and ordered(
            update,
            "kUpdateDigestDomain", "kSchemaVersion", "folder_id", "local_actor",
            "state_generation", "policy_epoch", "entry_count",
            "previous_chain_digest", "snapshot_digest",
        ),
        "update_chain_commits_complete_policy_cutpoint",
        "identity, sequence, version, count, prior chain, and snapshot are all bound",
    )
    require(
        "std::array<char, 8U> encoded" in source
        and "append_u64(digest, static_cast<std::uint64_t>(value.size()))" in source,
        "chain_fields_use_canonical_binary_framing",
        "architecture and concatenation ambiguity do not alter digest material",
    )

    load = body(source, "LoadedMembershipState load_state_or_throw(")
    require(
        ordered(load, "attest_sync_replica_tls_policy_sqlite_backend_or_throw", "attest_schema_or_throw", "metadata prepare", "history_rows_or_throw", "total_entry_rows_or_throw", "ORDER BY state_generation"),
        "every_load_attests_backend_schema_metadata_and_complete_history",
        "authority is reconstructed from the exact durable cutpoint, not cached belief",
    )
    require(
        all(token in load for token in (
            "membership generations are not contiguous",
            "membership policy epochs are not strictly increasing",
            "membership history previous-chain link is invalid",
            "membership snapshot digest mismatch",
            "membership chain digest mismatch",
            "membership entry table contains orphan rows",
            "current membership metadata is inconsistent",
        )),
        "restoration_rejects_sequence_digest_orphan_and_metadata_drift",
        "partial, reordered, rewritten, or detached history cannot mint authority",
    )
    require(
        "sqlite_column_text_or_throw" in load
        and "128U" in load and "64U" in load
        and "kSyncReplicaTlsMembershipMaxHistoryRecords" in load
        and "kSyncReplicaTlsMembershipMaxRetainedEntryRows" in load,
        "restoration_bounds_rows_and_text",
        "hostile durable data cannot request unbounded text or row retention",
    )
    trusted = body(source, "void require_trusted_anchor_or_throw(")
    require(
        ordered(trusted, "validate_anchor_or_throw", "trusted.state_generation > snapshot.state_generation", "trusted.state_generation == 0U", "snapshot.history.at", "*observed != trusted.chain_digest"),
        "trusted_anchor_detects_rollback_and_divergence",
        "newer retained generation rejects rollback and exact digest rejects a fork through that point",
    )

    publish = body(source, "SyncReplicaTlsMembershipSqliteOwner::publish_or_throw(")
    require(
        ordered(
            publish,
            "validate_sync_replica_tls_membership_anchor_or_throw",
            "SyncReplicaTlsMembershipSnapshot candidate",
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "observed != expected_current",
            "policy_epoch <=",
            "update_chain_digest",
        ),
        "publication_prepares_candidate_then_exact_cas_under_writer_lock",
        "caller allocation precedes writer authority and stale writers cannot overwrite",
    )
    require(
        "sync_replica_tls_membership_append_fits_hard_limits" in publish
        and "loaded.retained_entry_rows" in publish
        and "membership append exceeds retained-history hard ceilings" in publish,
        "crossing_append_is_rejected_before_it_can_brick_restoration",
        "history and retained-entry ceilings govern the candidate under the exact writer cutpoint",
    )
    require(
        ordered(
            publish,
            "INSERT INTO main.sync_replica_tls_membership_updates",
            "INSERT INTO main.sync_replica_tls_membership_entries",
            "UPDATE main.sync_replica_tls_membership_meta SET",
            "make_shared<SyncReplicaTlsMembershipAuthority::State>",
            "transaction.commit()",
            "return SyncReplicaTlsMembershipAuthority",
        ),
        "return_allocation_precedes_commit_and_authority_follows_commit",
        "allocation failure rolls back; complete history, entries, and metadata commit before capability emission",
    )
    require(
        ordered(
            publish,
            "SyncReplicaTlsMembershipSnapshot candidate",
            "entry.actor.epoch > kMaxPersistentInteger",
            "SyncSqliteTransactionMode::Immediate",
        ),
        "sqlite_integer_range_is_validated_before_writer_cutpoint",
        "caller actor epochs cannot fail first while durable write authority is held",
    )
    require(
        "No callback or external lookup runs while the" in publish
        and "append transaction is live" in publish,
        "writer_cutpoint_excludes_caller_callbacks",
        "arbitrary code cannot run while append authority is held",
    )
    snapshot = body(source, "SyncReplicaTlsMembershipSqliteOwner::snapshot_or_throw(")
    require(
        ordered(snapshot, "SyncSqliteTransactionMode::Deferred", "load_state_or_throw", "require_trusted_anchor_or_throw", "current_authority", "transaction.commit()"),
        "snapshot_uses_one_validated_read_transaction",
        "metadata and complete history are observed at one SQLite snapshot cutpoint",
    )

    serve = body(server_source, "serve_one_sync_replica_file_delivery_tls_session_or_throw(")
    require(
        "SyncReplicaTlsAnchoredMembershipAuthority membership" in server_header
        and "SyncReplicaTlsMembershipAuthority membership" not in server_header
        and ordered(
            serve,
            "membership.snapshot()",
            "membership.state_generation()",
            "membership.previous_chain_digest()",
            "membership.chain_digest()",
            "membership.durable_anchor()",
            "membership.durable_transition_sequence()",
            "membership.durable_transition_digest()",
            "accept_one_until_or_throw",
        ),
        "accepted_server_consumes_and_reports_anchored_authority",
        "one server result names the exact committed policy and independent anchor cutpoint before accept",
    )
    anchored_authority = body(
        anchored_header,
        "class SyncReplicaTlsAnchoredMembershipAuthority final",
    )
    require(
        bool(anchored_authority)
        and "const SyncReplicaTlsAnchoredMembershipAuthority&) = delete" in anchored_authority
        and "friend class SyncReplicaTlsMembershipAnchoredOwner" in anchored_authority
        and "SyncReplicaTlsMembershipAuthority membership_" in anchored_authority
        and "durable_transition_digest_" in anchored_authority
        and "seal_authority_or_throw" in anchored_source,
        "anchored_authority_is_type_distinct_and_coordinator_only",
        "raw history authority cannot accidentally cross the accepted-session anchor frontier",
    )

    runtime_tokens = (
        "concurrent membership schema initialization left partial authority",
        "membership history admitted one record beyond its hard ceiling",
        "membership retention admitted one entry beyond its hard ceiling",
        "membership owner did not install its exact safe pragma profile",
        "membership owner reused authority after connection-profile mutation",
        "membership owner admitted an attached schema on its authority connection",
        "membership owner minted durable authority with synchronous OFF",
        "membership owner overstated rollback-journal FULL durability",
        "membership owner overstated WAL NORMAL durability",
        "membership owner minted durable authority in memory journal mode",
        "empty membership history minted accepted-session authority",
        "membership owner entered its write cutpoint with an unpersistable actor epoch",
        "rejected unpersistable actor epoch mutated membership authority",
        "membership publication accepted a stale compare-and-swap anchor",
        "second SQLite connection overwrote a newer membership generation",
        "membership restart lost append-only chain continuity",
        "membership owner accepted a fork through a retained generation",
        "external membership anchor did not detect whole-database rollback",
        "membership owner trusted rows that no longer match snapshot digest",
        "membership owner trusted a rewritten append-only chain digest",
        "membership owner ignored unowned retained entry rows",
        "membership owner admitted an unowned schema object",
        "membership owner admitted a connection-local trigger on its tables",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "compiled_runtime_matrix_covers_durability_cas_rollback_and_tamper",
        "negative and restart semantics are executable rather than lexical claims",
    )
    require(
        all(token in transport_runtime for token in (
            "result_binds_membership",
            "anchored_membership_owner.current_authority_or_throw()",
            "membership_previous_chain_digest",
            "membership_chain_digest",
        )),
        "transport_runtime_binds_owner_evidence_end_to_end",
        "accepted-session tests consume fresh owner-emitted capabilities and compare exact chain evidence",
    )
    require(
        all(token in anchor_runtime for token in (
            "two-store failure fixture did not leave membership ahead of anchor",
            "restart-style reconciliation did not close membership/anchor gap",
            "concurrent anchor reconciliation did not converge",
            "whole-file rollback below retained anchor",
            "divergent retained checkpoint",
        )),
        "compiled_anchor_runtime_covers_gap_recovery_race_rollback_and_fork",
        "the independent anchor is exercised as executable authority rather than a documentation convention",
    )

    require(
        "add_library(anonsync_sync_replica_tls_membership STATIC" in cmake
        and "src/sync_replica_tls_membership_sqlite_owner.cpp" in cmake
        and "tests/sync_replica_tls_membership_sqlite_owner_test.cpp" in cmake
        and cmake.count("anonsync_sync_tls_membership_sqlite_owner_source_audit") >= 2,
        "owner_library_runtime_and_audit_are_registered",
        "ordinary build and CTest retain the complete authority surface",
    )
    require(
        all(token in verifier for token in (
            "src/sync_replica_tls_membership_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_sqlite_owner.cpp",
            "tests/sync_replica_tls_membership_sqlite_owner_test.hpp",
            "tests/sync_replica_tls_membership_sqlite_owner_test.cpp",
            "tools/audit_sync_tls_membership_sqlite_owner.py",
        )),
        "release_verifier_requires_owner_surface",
        "sealed handoff cannot omit implementation, runtime matrix, or audit",
    )
    require(
        "Lexical hygiene audit" in (__doc__ or "")
        and "does not claim to prove" in (__doc__ or ""),
        "audit_disclaims_semantic_authority",
        "source vocabulary is not represented as durability or security proof",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-tls-membership-sqlite-owner-source-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove SQLite/filesystem durability, "
            "hash security, external anchor persistence, freshness, or C++ semantics"
        ),
        "root": str(root),
        "passed": passed,
        "passed_checks": sum(bool(check["passed"]) for check in checks),
        "total_checks": len(checks),
        "checks": checks,
        "violations": [check["check_id"] for check in checks if not check["passed"]],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
