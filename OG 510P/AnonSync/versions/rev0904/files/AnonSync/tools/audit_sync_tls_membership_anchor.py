#!/usr/bin/env python3
"""Lexical hygiene audit for independently anchored TLS membership.

This inventory checks reviewed ownership, ordering, schema, type-boundary, and
runtime-test vocabulary. It does not prove SQLite or filesystem durability,
independent failure domains, SHA-256 security, C++ semantics, race freedom,
rollback resistance against joint replacement, or successful crash recovery.
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
        "profile_header": root / "src/sync_replica_tls_policy_sqlite_profile.hpp",
        "profile_source": root / "src/sync_replica_tls_policy_sqlite_profile.cpp",
        "membership_header": root / "src/sync_replica_tls_membership_sqlite_owner.hpp",
        "membership_source": root / "src/sync_replica_tls_membership_sqlite_owner.cpp",
        "anchor_header": root / "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp",
        "anchor_source": root / "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp",
        "coordinator_header": root / "src/sync_replica_tls_membership_anchored_owner.hpp",
        "coordinator_source": root / "src/sync_replica_tls_membership_anchored_owner.cpp",
        "server_header": root / "src/sync_replica_file_tls_server.hpp",
        "server_source": root / "src/sync_replica_file_tls_server.cpp",
        "runtime_header": root / "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.hpp",
        "runtime": root / "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp",
        "transport": root / "tests/sync_replica_tls_transport_test.cpp",
        "design": root / "TLS_DURABLE_MEMBERSHIP_ANCHOR_AUDIT_rev0892.md",
        "cmake": root / "CMakeLists.txt",
        "verifier": root / "tools/verify_release_package.py",
    }
    missing = sorted(
        str(path.relative_to(root))
        for path in paths.values()
        if not path.is_file()
    )
    text = {
        name: path.read_text(encoding="utf-8") if path.is_file() else ""
        for name, path in paths.items()
    }
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(
            {"check_id": check_id, "passed": bool(condition), "detail": detail}
        )

    require(not missing, "required_files_exist", f"missing={missing}")
    profile_header = text["profile_header"]
    profile_source = text["profile_source"]
    membership_header = text["membership_header"]
    membership_source = text["membership_source"]
    anchor_header = text["anchor_header"]
    anchor_source = text["anchor_source"]
    coordinator_header = text["coordinator_header"]
    coordinator_source = text["coordinator_source"]
    server_header = text["server_header"]
    server_source = text["server_source"]
    runtime = text["runtime"]
    transport = text["transport"]
    design = text["design"]
    cmake = text["cmake"]
    verifier = text["verifier"]

    require(
        "sync_replica_tls_policy_sqlite_profile.cpp" in cmake
        and "sync_replica_tls_policy_sqlite_profile.hpp" in membership_header
        and "sync_replica_tls_policy_sqlite_profile.hpp" in anchor_header
        and "SyncReplicaTlsPolicySqliteConnectionBinding database_" in membership_header
        and "SyncReplicaTlsPolicySqliteConnectionBinding database_" in anchor_header,
        "membership_and_anchor_share_one_sqlite_policy_owner",
        "connection and backend rules cannot silently drift between the two stores",
    )
    profile_config = body(
        profile_source,
        "void configure_sync_replica_tls_policy_sqlite_connection_or_throw(",
    )
    profile_attest = body(
        profile_source,
        "void attest_sync_replica_tls_policy_sqlite_backend_or_throw(",
    )
    require(
        all(
            token in profile_config
            for token in (
                "SQLITE_DBCONFIG_DEFENSIVE",
                "SQLITE_DBCONFIG_TRUSTED_SCHEMA",
                "SQLITE_DBCONFIG_ENABLE_TRIGGER",
                "SQLITE_DBCONFIG_ENABLE_VIEW",
                "SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION",
                "SQLITE_LIMIT_ATTACHED",
                "PRAGMA read_uncommitted=OFF",
                "PRAGMA ignore_check_constraints=OFF",
            )
        )
        and all(
            token in profile_attest
            for token in (
                "sqlite3_db_readonly",
                "PRAGMA main.journal_mode",
                "PRAGMA main.synchronous",
                'journal_mode == "wal" ? 2U : 3U',
            )
        ),
        "shared_profile_is_defensive_named_writable_and_durable",
        "both policy stores re-attest the same narrow SQLite capability profile",
    )

    binding = body(
        profile_source,
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
        and "database_.require_current_or_throw" in membership_source
        and "database_.require_current_or_throw" in anchor_source
        and "renamed-membership.displaced.sqlite3" in runtime
        and "continued after its live main database path moved" in runtime,
        "policy_owners_pin_and_reprove_exact_sqlite_generation",
        "slot retargeting and live main-path displacement cannot silently redirect durable policy authority",
    )

    distinct = body(
        profile_source,
        "void require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw(",
    )
    require(
        ordered(
            distinct,
            "first_filename == second_filename",
            "std::filesystem::equivalent",
            "if (error)",
            "if (equivalent)",
        )
        and "does not prove separate media" in profile_header
        and "coordinated replacement" in profile_header
        and "std::filesystem::create_hard_link" in runtime
        and "membership and rollback anchor accepted different names for one filesystem object" in runtime,
        "distinct_file_preflight_rejects_exact_and_aliasing_paths",
        "same-file composition fails closed without becoming a storage-domain claim",
    )

    anchor_value = body(
        membership_header, "struct SyncReplicaTlsMembershipAnchor final"
    )
    require(
        "state_generation" in anchor_value
        and "chain_digest" in anchor_value
        and "validate_sync_replica_tls_membership_anchor_or_throw" in membership_header
        and "sync_replica_tls_membership_genesis_anchor_or_throw" in membership_header,
        "anchor_format_is_shared_generation_plus_digest",
        "membership history, anchor store, and coordinator use one exact cutpoint format",
    )

    anchor_owner = body(
        anchor_header, "class SyncReplicaTlsMembershipAnchorSqliteOwner final"
    )
    require(
        bool(anchor_owner)
        and "const SyncReplicaTlsMembershipAnchorSqliteOwner&) = delete" in anchor_owner
        and "SyncReplicaTlsMembershipAnchorSqliteOwner&&) = delete" in anchor_owner
        and "SyncReplicaTlsPolicySqliteConnectionBinding database_" in anchor_owner
        and "database_.database_filename()" in anchor_owner,
        "anchor_owner_is_stationary_on_one_named_database",
        "checkpoint authority cannot copy or migrate between SQLite slots",
    )
    require(
        "hardware monotonic counter" in anchor_header
        and "does not sign anchors" in anchor_header
        and "rolls back or replaces both stores together" in anchor_header,
        "anchor_owner_threat_nonclaims_are_explicit",
        "ordinary SQLite persistence is not mislabeled as hardware or cryptographic provenance",
    )

    require(
        all(
            token in anchor_source
            for token in (
                "CREATE TABLE sync_replica_tls_membership_anchor_meta(",
                "CREATE TABLE sync_replica_tls_membership_anchor_updates(",
                ")) STRICT",
                "kSyncReplicaTlsMembershipAnchorMaxTransitions",
            )
        ),
        "anchor_schema_is_two_strict_bounded_tables",
        "one singleton cutpoint and one append-only transition chain have explicit closure",
    )
    require(
        "name GLOB 'sync_replica_tls_membership_anchor_*'" in anchor_source
        and "FROM temp.sqlite_schema" in anchor_source
        and "schema object count mismatch" in anchor_source
        and "unowned temp schema attachments" in anchor_source,
        "anchor_schema_closes_main_and_temp_attachments",
        "unreviewed indexes, triggers, views, or temp attachments fail restoration",
    )

    genesis = body(anchor_source, "std::string genesis_transition_digest(")
    transition = body(anchor_source, "std::string transition_digest(")
    require(
        "anonsync:sync-replica-tls-membership-anchor:genesis:v1" in anchor_source
        and ordered(genesis, "kGenesisTransitionDigestDomain", "kSchemaVersion", "folder_id", "local_actor", "genesis_anchor"),
        "anchor_genesis_is_domain_version_and_identity_bound",
        "an empty checkpoint store has one canonical service-scoped state",
    )
    require(
        "anonsync:sync-replica-tls-membership-anchor:transition:v1" in anchor_source
        and ordered(
            transition,
            "kTransitionDigestDomain",
            "kSchemaVersion",
            "folder_id",
            "local_actor",
            "transition_sequence",
            "previous_anchor",
            "current_anchor",
            "previous_transition_digest",
        ),
        "anchor_transition_digest_commits_complete_link",
        "sequence, membership endpoints, identity, and prior transition are structurally bound",
    )

    load = body(anchor_source, "SyncReplicaTlsMembershipAnchorSqliteSnapshot load_state_or_throw(")
    require(
        ordered(
            load,
            "attest_sync_replica_tls_policy_sqlite_backend_or_throw",
            "attest_schema_or_throw",
            "metadata prepare",
            "history_rows_or_throw",
            "ORDER BY transition_sequence",
        ),
        "every_anchor_load_reattests_backend_schema_metadata_and_history",
        "checkpoint authority is reconstructed from one exact durable snapshot",
    )
    require(
        all(
            token in load
            for token in (
                "transition sequence is not contiguous",
                "transition is not monotonic",
                "history link is invalid",
                "transition digest mismatch",
                "metadata sequence does not match history",
                "current membership anchor metadata is inconsistent",
            )
        ),
        "anchor_restoration_rejects_sequence_link_digest_and_metadata_drift",
        "partial, reordered, rewritten, or detached transitions cannot become coverage",
    )

    advance = body(
        anchor_source,
        "SyncReplicaTlsMembershipAnchorSqliteOwner::advance_or_throw(",
    )
    require(
        ordered(
            advance,
            "next.state_generation <= expected_current.state_generation",
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "observed == next",
            "observed != expected_current",
            "INSERT INTO main.sync_replica_tls_membership_anchor_updates",
            "UPDATE main.sync_replica_tls_membership_anchor_meta SET",
            "transaction.commit()",
        ),
        "anchor_advance_is_monotonic_exact_cas_with_idempotent_retry",
        "ambiguous same-target retry is safe and a stale expected anchor never mutates",
    )
    require(
        "next.state_generation <= expected_current.state_generation" in advance
        and "next.state_generation == expected_current.state_generation + 1U" not in advance
        and "may jump across multiple membership" in anchor_header,
        "anchor_advance_allows_proved_crash_recovery_jumps",
        "several committed membership generations can be covered in one retained transition",
    )

    coordinator = body(
        coordinator_header, "class SyncReplicaTlsMembershipAnchoredOwner final"
    )
    constructor = body(
        coordinator_source,
        "SyncReplicaTlsMembershipAnchoredOwner::\n    SyncReplicaTlsMembershipAnchoredOwner(",
    )
    require(
        "membership_owner_.folder_id() != anchor_owner_.folder_id()" in constructor
        and "require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw" in constructor
        and ordered(
            constructor,
            "anchor_owner_.snapshot_or_throw()",
            "membership_owner_.snapshot_or_throw",
        ),
        "coordinator_constructor_proves_identity_file_separation_and_anchor_prefix",
        "mismatched, same-file, rolled-back, or forked stores fail before use",
    )
    require(
        bool(coordinator)
        and "const SyncReplicaTlsMembershipAnchoredOwner&) = delete" in coordinator
        and "SyncReplicaTlsMembershipAnchoredOwner&&) = delete" in coordinator
        and "membership_owner_" in coordinator
        and "anchor_owner_" in coordinator,
        "coordinator_is_stationary_over_two_exact_owners",
        "reconciliation authority cannot copy or silently retarget either database",
    )

    ensure = body(
        coordinator_source,
        "SyncReplicaTlsMembershipAnchoredOwner::ensure_anchor_covers_or_throw(",
    )
    require(
        "kSyncReplicaTlsMembershipAnchorReconciliationMaxAttempts" in ensure
        and ordered(
            ensure,
            "anchor_owner_.snapshot_or_throw()",
            "membership_owner_.snapshot_or_throw",
            "snapshot_contains_anchor(membership_snapshot, target)",
            "anchor_snapshot.current_anchor.state_generation >=",
            "anchor_owner_.advance_or_throw",
        ),
        "reconciliation_reproves_both_stores_on_every_bounded_attempt",
        "coverage is never inferred from generation numbers or cached belief alone",
    )
    require(
        "StaleExpected" in ensure
        and "Another exact owner advanced" in ensure
        and "Re-read" in ensure,
        "reconciliation_retries_stale_cas_only_after_full_reproof",
        "a concurrent winner cannot be relabeled as equivalent without chain validation",
    )

    publish = body(
        coordinator_source,
        "SyncReplicaTlsMembershipAnchoredOwner::publish_or_throw(",
    )
    require(
        ordered(
            publish,
            "anchor_owner_.snapshot_or_throw()",
            "membership_owner_.snapshot_or_throw",
            "ensure_anchor_covers_or_throw(membership_snapshot.anchor())",
            "membership_snapshot.anchor() != expected_current",
            "membership_owner_.publish_or_throw",
            "seal_authority_or_throw",
        ),
        "publication_closes_prior_gap_then_commits_membership_before_sealing",
        "no new append roots itself in an unretained predecessor and no raw authority escapes",
    )
    seal = body(
        coordinator_source,
        "SyncReplicaTlsMembershipAnchoredOwner::seal_authority_or_throw(",
    )
    require(
        ordered(
            seal,
            "membership.anchor()",
            "ensure_anchor_covers_or_throw(target)",
            "anchor_owner_.snapshot_or_throw()",
            "membership_owner_.snapshot_or_throw(anchor_snapshot.current_anchor)",
            "snapshot_contains_anchor(membership_snapshot, target)",
            "anchor_snapshot.current_anchor != target",
            "membership_snapshot.anchor() != target",
            "MembershipAuthoritySuperseded",
            "SyncReplicaTlsAnchoredMembershipAuthority(",
        )
        and "durable_anchor_ != membership_.anchor()" in coordinator_source
        and "catch (const MembershipAuthoritySuperseded&)" in coordinator_source,
        "capability_sealing_requires_exact_current_membership_and_anchor_cutpoint",
        "covered-by-newer reconciliation cannot mint a capability already known to be superseded",
    )

    anchored_authority = body(
        coordinator_header,
        "class SyncReplicaTlsAnchoredMembershipAuthority final",
    )
    require(
        bool(anchored_authority)
        and "const SyncReplicaTlsAnchoredMembershipAuthority&) = delete" in anchored_authority
        and "SyncReplicaTlsAnchoredMembershipAuthority&&) noexcept = default" in anchored_authority
        and "friend class SyncReplicaTlsMembershipAnchoredOwner" in anchored_authority
        and "SyncReplicaTlsMembershipAuthority membership_" in anchored_authority
        and "durable_transition_digest_" in anchored_authority,
        "anchored_capability_is_move_only_coordinator_constructible_and_evidence_bearing",
        "raw membership authority cannot impersonate independently retained coverage",
    )

    serve = body(
        server_source,
        "serve_one_sync_replica_file_delivery_tls_session_or_throw(",
    )
    require(
        "SyncReplicaTlsAnchoredMembershipAuthority membership" in server_header
        and "SyncReplicaTlsMembershipAuthority membership" not in server_header
        and "SyncReplicaTlsMembershipSnapshot membership" not in server_header
        and ordered(
            serve,
            "membership.snapshot()",
            "membership.durable_anchor()",
            "membership.durable_transition_sequence()",
            "membership.durable_transition_digest()",
            "accept_one_until_or_throw",
        ),
        "accepted_server_requires_and_reports_anchored_capability_before_accept",
        "the production session boundary cannot bypass the external rollback cutpoint",
    )
    require(
        all(
            token in server_header
            for token in (
                "membership_durable_anchor_state_generation",
                "membership_durable_anchor_chain_digest",
                "membership_durable_anchor_transition_sequence",
                "membership_durable_anchor_transition_digest",
            )
        )
        and all(token in transport for token in (
            "durable_anchor_state_generation",
            "durable_anchor_transition_digest",
            "result_binds_membership",
            "anchored_membership_owner.current_authority_or_throw()",
        )),
        "terminal_server_evidence_binds_membership_and_anchor_store",
        "every result identifies both the authorization snapshot and retained rollback checkpoint",
    )

    runtime_tokens = (
        "membership and rollback anchor silently shared one failure domain",
        "two-store failure fixture did not leave membership ahead of anchor",
        "restart-style reconciliation did not close membership/anchor gap before authority emission",
        "concurrent anchor reconciliation did not converge on exact current authority",
        "anchor reconciliation did not retain one exact crash recovery jump",
        "anchored membership accepted whole-file rollback below retained anchor",
        "anchored membership accepted a divergent retained checkpoint",
        "membership anchor trusted a rewritten transition digest",
        "membership anchor did not re-attest its SQLite connection profile",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "compiled_runtime_matrix_covers_file_separation_gap_race_rollback_fork_and_tamper",
        "failure ownership and recovery are executable rather than audit vocabulary",
    )
    require(
        "BEGIN IMMEDIATE;" in runtime
        and "publish_or_throw" in runtime
        and "locked" in runtime
        and ordered(
            runtime,
            "BEGIN IMMEDIATE;",
            "coordinator.publish_or_throw",
            "committed_membership",
            "retained_anchor",
            "ROLLBACK;",
            "coordinator.current_authority_or_throw",
        ),
        "runtime_deterministically_exercises_post_membership_pre_anchor_failure",
        "the two-database crash gap is observed directly rather than simulated by comments",
    )

    require(
        "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp" in cmake
        and "src/sync_replica_tls_membership_anchored_owner.cpp" in cmake
        and "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp" in cmake
        and cmake.count("anonsync_sync_tls_membership_anchor_source_audit") >= 2,
        "anchor_sources_runtime_and_audit_are_registered",
        "ordinary CMake and CTest retain the complete anchor authority surface",
    )
    required_verifier_tokens = (
        "src/sync_replica_tls_policy_sqlite_profile.hpp",
        "src/sync_replica_tls_policy_sqlite_profile.cpp",
        "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp",
        "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp",
        "src/sync_replica_tls_membership_anchored_owner.hpp",
        "src/sync_replica_tls_membership_anchored_owner.cpp",
        "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.hpp",
        "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp",
        "tools/audit_sync_tls_membership_anchor.py",
        "TLS_DURABLE_MEMBERSHIP_ANCHOR_AUDIT_rev0892.md",
    )
    require(
        all(token in verifier for token in required_verifier_tokens),
        "release_verifier_requires_complete_anchor_surface",
        "a sealed handoff cannot omit implementation, runtime, audit, or design record",
    )
    require(
        all(
            token in design
            for token in (
                "Exact crash ordering",
                "Crash and concurrency matrix",
                "Independent-file preflight",
                "Type-level bypass closure",
                "Shared SQLite profile refactor",
                "Update Framework",
                "SQLite",
                "TPM",
                "Both databases are rolled back/replaced together",
                "Lexical audit nonclaim",
            )
        ),
        "design_record_names_research_ordering_nonclaims_and_remaining_risk",
        "rollback accounting is documented without overstating SQLite or hash authority",
    )
    require(
        "Lexical hygiene audit" in (__doc__ or "")
        and "does not prove" in (__doc__ or ""),
        "audit_disclaims_semantic_authority",
        "substring checks cannot become durability or security proof",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-tls-membership-anchor-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove SQLite/filesystem durability, "
            "independent failure domains, hash security, C++ semantics, or rollback resistance"
        ),
        "root": str(root),
        "passed": passed,
        "passed_checks": sum(bool(check["passed"]) for check in checks),
        "total_checks": len(checks),
        "checks": checks,
        "violations": [
            check["check_id"] for check in checks if not check["passed"]
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
