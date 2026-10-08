#!/usr/bin/env python3
"""Fail-closed audit for exact-state SQLite replay-ledger reset authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_core.hpp"),
    Path("include/anonsync_core_internal.hpp"),
    Path("src/anonsync_core.cpp"),
    Path("src/runner.cpp"),
    Path("src/replay_ledger.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("src/sqlite_path_security.cpp"),
    Path("src/sha256_digest.hpp"),
    Path("src/sha256_digest.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_documents.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_documents.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp"),
    Path("src/persistence/sqlite_replay_ledger_write_gate.hpp"),
    Path("src/persistence/sqlite_replay_ledger_write_gate.cpp"),
    Path("tests/self_exec_test_process.hpp"),
    Path("tests/self_exec_test_process.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_fixture.hpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("tests/sync_atomic_file_publication_prepared_test.cpp"),
    Path("tools/audit_self_exec_test_process.py"),
    Path("tools/test_sqlite_replay_ledger_reset_cli.py"),
    Path("tools/audit_sqlite_replay_ledger_reset_crash_frontier.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def slice_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-replay-ledger-reset-audit-v3",
            "root": str(root),
            "passed": False,
            "passed_checks": 0,
            "total_checks": 0,
            "checks": [],
            "violations": [f"missing required file: {item}" for item in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    text = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = text[Path("CMakeLists.txt")]
    public = text[Path("include/anonsync_core.hpp")]
    internal = text[Path("include/anonsync_core_internal.hpp")]
    cli = text[Path("src/anonsync_core.cpp")]
    runner = text[Path("src/runner.cpp")]
    jsonl = text[Path("src/replay_ledger.cpp")]
    ledger = text[Path("src/sqlite_replay_ledger.cpp")]
    path_source = text[Path("src/sqlite_path_security.cpp")]
    digest_hpp = text[Path("src/sha256_digest.hpp")]
    digest_cpp = text[Path("src/sha256_digest.cpp")]
    reset_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset.hpp")]
    reset = text[Path("src/persistence/sqlite_replay_ledger_reset.cpp")]
    documents_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset_documents.hpp")]
    documents = text[Path("src/persistence/sqlite_replay_ledger_reset_documents.cpp")]
    protocol_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp")]
    protocol_internal = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp")]
    protocol = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp")]
    gate_hpp = text[Path("src/persistence/sqlite_replay_ledger_write_gate.hpp")]
    gate = text[Path("src/persistence/sqlite_replay_ledger_write_gate.cpp")]
    self_exec_header = text[Path("tests/self_exec_test_process.hpp")]
    self_exec_source = text[Path("tests/self_exec_test_process.cpp")]
    focused = text[Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp")]
    focused_fixture = text[Path("tests/persistence/sqlite_replay_ledger_reset_fixture.hpp")]
    crash_frontier_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp")]
    documents_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp")]
    publication_hpp = text[Path("src/sync_atomic_file_publication.hpp")]
    prepared_publication_test = text[Path("tests/sync_atomic_file_publication_prepared_test.cpp")]
    cli_test = text[Path("tools/test_sqlite_replay_ledger_reset_cli.py")]
    verifier = text[Path("tools/verify_release_package.py")]
    checks: list[Check] = []

    active_source_files = sorted(
        list((root / "src").rglob("*.cpp"))
        + list((root / "src").rglob("*.hpp"))
        + list((root / "include").rglob("*.hpp"))
    )
    unlink_hits = [
        path.relative_to(root).as_posix()
        for path in active_source_files
        if "unlink_sqlite_family(" in path.read_text(encoding="utf-8")
    ]
    require(
        checks,
        not unlink_hits,
        "sqlite_family_deletion_primitive_is_absent",
        "ordinary production source must contain no whole-family deletion helper or caller",
    )
    require(
        checks,
        all(token not in reset for token in (
            "std::remove", "::unlink(", "std::filesystem::remove",
            "std::filesystem::rename", "unlink_sqlite_family",
        )),
        "reset_has_no_namespace_delete_or_rename",
        "administrative reset must mutate the verified database in place",
    )

    require(
        checks,
        "virtual void load(const std::string& ledger_path, const std::string& mode" in internal
        and "load(const std::string& ledger_path, bool reset" not in internal,
        "backend_load_interface_is_nondestructive",
        "ordinary backend opening cannot carry a reset Boolean",
    )
    sqlite_load = slice_between(
        ledger,
        "void SqliteWalReplayLedger::load(",
        "ReplayLedgerStats SqliteWalReplayLedger::stats(",
    )
    jsonl_load = slice_between(
        jsonl,
        "void ReplayLedger::load(",
        "bool ReplayLedger::contains_jti(",
    )
    require(
        checks,
        bool(sqlite_load) and "bool reset" not in sqlite_load
        and "unlink" not in sqlite_load and "remove(" not in sqlite_load,
        "sqlite_load_is_nondestructive",
        "opening a SQLite ledger must acquire and verify, never erase",
    )
    require(
        checks,
        bool(jsonl_load) and "bool reset" not in jsonl_load
        and "std::remove" not in jsonl_load and "unlink" not in jsonl_load,
        "jsonl_load_is_nondestructive",
        "the sibling backend must not retain a hidden destructive load path",
    )
    require(
        checks,
        "--ledger-reset was removed because ordinary open must not mint destructive authority" in cli
        and "return 64;" in cli[cli.find("--ledger-reset was removed"):cli.find("--ledger-reset was removed") + 400],
        "legacy_reset_flag_fails_closed",
        "the removed convenience flag must explain and enforce the new authority boundary",
    )

    core_sources = re.search(
        r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S
    )
    reset_link = re.search(
        r"target_link_libraries\(anonsync_sqlite_replay_ledger_reset(?P<body>.*?)\)",
        cmake,
        re.S,
    )
    gate_link = re.search(
        r"target_link_libraries\(anonsync_sqlite_replay_ledger_write_gate(?P<body>.*?)\)",
        cmake,
        re.S,
    )
    require(
        checks,
        "add_library(anonsync_sqlite_replay_ledger_reset STATIC" in cmake
        and reset_link is not None
        and all(name in reset_link.group("body") for name in (
            "anonsync_sha256_digest",
            "anonsync_sqlite_replay_ledger_schema_contract",
            "anonsync_sqlite_replay_ledger_write_gate",
            "anonsync_sqlite_verification_budget",
            "anonsync_sqlite_support",
        )),
        "reset_is_separately_linked_production_owner",
        "the destructive transition and every evidence dependency remain reviewable",
    )
    require(
        checks,
        "add_library(anonsync_sqlite_replay_ledger_write_gate STATIC" in cmake
        and gate_link is not None
        and "anonsync_sqlite_path_security" in gate_link.group("body")
        and "anonsync_sqlite_support" in gate_link.group("body"),
        "write_gate_is_separately_linked_path_hardened_owner",
        "reset and ordinary writers must consume one extracted exclusive capability",
    )
    require(
        checks,
        core_sources is not None
        and "sqlite_replay_ledger_reset.cpp" not in core_sources.group("body")
        and "sqlite_replay_ledger_write_gate.cpp" not in core_sources.group("body"),
        "owners_are_not_reabsorbed_by_core_glob",
        "focused owners must not silently become duplicate core translation units",
    )
    require(
        checks,
        '"${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_SOURCE}"' in cmake
        and '"${ANONSYNC_SQLITE_REPLAY_LEDGER_WRITE_GATE_SOURCE}"' in cmake
        and "list(FIND ANONSYNC_CORE_SOURCES" in cmake
        and "invariant-owned persistence boundary must remain outside anonsync_core_lib" in cmake,
        "reset_source_is_explicitly_excluded_from_core",
        "source glob exclusion must be visible and fail closed",
    )

    require(
        checks,
        "class Sha256DigestBuilder" in digest_hpp
        and "Sha256DigestBuilder(const Sha256DigestBuilder&) = delete" in digest_hpp
        and "void update(std::string_view bytes);" in digest_hpp
        and "std::string finish_hex();" in digest_hpp,
        "streaming_digest_is_move_only_and_single_owner",
        "canonical state hashing must not build an unbounded aggregate string",
    )
    require(
        checks,
        "EVP_DigestUpdate" in digest_cpp and "EVP_DigestFinal_ex" in digest_cpp
        and "SHA-256 digest builder is not finishable" in digest_cpp
        and "SHA-256 digest builder is not updateable" in digest_cpp,
        "streaming_digest_uses_checked_single_finish_evp",
        "incremental hashing must reject reuse after finalization",
    )

    for token, check_id, detail in (
        ("kSqliteReplayLedgerResetRequestFormat", "versioned_request_format", "request bytes need an explicit protocol version"),
        ("kSqliteReplayLedgerResetStateFormat", "versioned_state_format", "operator inspection needs an explicit protocol version"),
        ("kSqliteReplayLedgerResetReceiptFormat", "versioned_receipt_format", "recovery evidence needs an explicit protocol version"),
        ("SqliteReplayLedgerResetExpectation", "typed_exact_expectation", "destructive authority must be represented as typed evidence"),
        ("SqliteReplayLedgerResetOutcome", "typed_reset_outcome", "commit and idempotent recovery must remain distinguishable"),
    ):
        require(checks, token in reset_hpp, check_id, detail)

    require(
        checks,
        "SqliteReplayLedgerWriteGateNesting::RejectSameThread" in reset
        and reset.count("SqliteReplayLedgerWriteGateNesting::RejectSameThread") == 2,
        "inspection_and_reset_require_fresh_exclusive_gate",
        "neither authority-minting operation may borrow an already-open same-thread writer",
    )
    require(
        checks,
        "LOCK_EX | LOCK_NB" in gate and "open_private_lock_file_or_throw" in gate
        and "::fsync(fd)" in gate,
        "write_gate_is_nonblocking_private_and_marker_durable",
        "the adjacent lock capability must be hardened and observable before use",
    )
    require(
        checks,
        "current_sync_process_incarnation_noexcept" in gate
        and "sync_process_incarnation_is_current" in gate
        and "fail_stop_on_sync_process_capability_violation_noexcept" in gate
        and "fork() copies thread-local bytes" in gate,
        "write_gate_is_process_incarnation_bound",
        "forked children cannot inherit recursive ownership or release parent authority",
    )
    require(
        checks,
        "RejectSameThread" in gate_hpp and "AllowSameThread" in gate_hpp
        and "rejects same-thread nested ownership" in gate,
        "write_gate_nesting_policy_is_explicit",
        "administrative callers may reject recursion while reviewed restore paths opt in",
    )
    require(
        checks,
        "SqliteReplayLedgerWriteGateParentPolicy" in gate_hpp
        and "RequireExistingParent" in gate_hpp
        and reset.count(
            "SqliteReplayLedgerWriteGateParentPolicy::RequireExistingParent"
        ) >= 2,
        "administrative_gate_requires_an_existing_parent",
        "inspection and reset cannot create a directory merely by being asked to inspect an absent ledger",
    )

    require(
        checks,
        "SyncSqliteThreadIncarnation thread_incarnation" in gate
        and "current_sync_sqlite_thread_incarnation_noexcept" in gate
        and "sync_sqlite_thread_incarnation_is_current" in gate
        and "fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept" in gate,
        "write_gate_is_exact_thread_incarnation_bound",
        "a capability moved to another thread cannot report ownership or release the lock",
    )
    require(
        checks,
        "scope_stacks" in gate
        and "position->second.back() != state_->scope_token" in gate
        and "lifetime inversion" in gate
        and "fail_stop_on_sync_process_capability_violation_noexcept" in gate,
        "nested_gate_scopes_are_strict_lifo",
        "an outer scope cannot release the kernel lock while inner authority survives",
    )

    require(
        checks,
        "SqliteVerificationBudget budget" in reset
        and "budget.consume_row()" in reset
        and "budget.consume_decoded_text_bytes" in reset
        and "budget.checkpoint()" in reset
        and "kMaximumUnboundedLedgerTextBytes" in reset,
        "exact_state_digest_has_row_byte_opcode_and_time_ceiling",
        "authorization must not turn a large or hostile ledger into unbounded work",
    )
    require(
        checks,
        "SyncSqliteTransactionMode::Deferred" in reset
        and "authorizes_snapshot" in reset,
        "inspection_digest_is_pinned_to_one_read_transaction",
        "operator evidence cannot mix rows from different logical images",
    )
    require(
        checks,
        "SyncSqliteTransactionMode::Immediate" in reset
        and "authorizes_write" in reset,
        "reset_uses_typed_immediate_write_transaction",
        "comparison and destructive effects must share one exclusive transaction",
    )
    require(
        checks,
        ordered(
            reset,
            "verify_exact_schema_or_throw(owner, budget, label);",
            "verify_backend_profile_or_throw(owner, label);",
            "verify_integrity_or_throw(owner, budget, label);",
            "query_canonical_state(owner, budget, normalized_path, label)",
            "expectation_matches_state(request.expected, observed)",
            "execute_expected_delete(",
            "rotate_identity(",
            "transaction.commit();",
        ),
        "proof_precedes_effects_and_receipt_precedes_commit",
        "schema, integrity, exact-state comparison, deletion, identity rotation, and commit must remain ordered",
    )
    require(
        checks,
        "verify_sqlite_replay_ledger_schema(observed)" in reset
        and "singleton table cardinality mismatch" in reset
        and "durable metadata/table cardinality mismatch" in reset,
        "schema_and_cardinality_are_exact",
        "the digest cannot silently omit extra schema objects or singleton rows",
    )
    require(
        checks,
        all(f'digest, "{table}"' in reset for table in (
            "backend_profile",
            "ledger_identity",
            "metadata",
            "effect_transition_metadata",
            "ledger_entries",
            "effect_transitions",
            "effect_outbox",
            "ingress_sender_replay_cache",
        )),
        "canonical_digest_covers_every_durable_table",
        "a stale request must fail after any durable-table mutation",
    )
    require(
        checks,
        all(column in reset for column in (
            '"dispatch_attempts"',
            '"worker_claim_id"',
            '"lease_expires_at_epoch"',
            '"transition_intent_sha256"',
            '"sender_replay_cache_instance_id"',
            '"material_sha256"',
        )),
        "canonical_digest_covers_non_summary_mutable_fields",
        "retry, lease, intent, and ingress changes must invalidate old reset authority",
    )
    require(
        checks,
        "ORDER BY sequence" in reset
        and "ORDER BY effect_idempotency_key COLLATE BINARY" in reset
        and "ORDER BY replay_key_sha256 COLLATE BINARY" in reset
        and "digest_token(digest, \"column\", column.name)" in reset
        and "digest_token(digest, \"storage\"" in reset,
        "canonical_digest_has_total_order_column_and_storage_framing",
        "row ordering and SQLite storage classes must be unambiguous evidence",
    )
    require(
        checks,
        "state_sha256" in reset_hpp and "expectation_matches_state" in reset
        and "exact prior logical-state precondition mismatch" in reset,
        "exact_digest_is_mandatory_precondition",
        "identity and summary counters alone cannot authorize destruction",
    )
    require(
        checks,
        "SqlitePathIdentity namespace_identity" in reset_hpp
        and "bound_path_identity_or_throw" in reset
        and "exact SQLite namespace precondition mismatch" in reset
        and "observed.namespace_identity" in reset,
        "request_binds_parent_and_database_objects",
        "a logically equivalent replacement database at the same pathname must not inherit reset authority",
    )
    bound_identity_start = path_source.find(
        "SqlitePathIdentity SqlitePathFamilyGuard::bound_path_identity_or_throw"
    )
    bound_identity_end = path_source.find(
        "void SqlitePathFamilyGuard::verify_family_or_throw", bound_identity_start
    )
    bound_identity_body = (
        path_source[bound_identity_start:bound_identity_end]
        if min(bound_identity_start, bound_identity_end) >= 0
        else ""
    )
    require(
        checks,
        "inspect_family_member_or_throw" in bound_identity_body
        and "database_device_" in bound_identity_body
        and "database_inode_" in bound_identity_body
        and "SQLite main database identity changed" in bound_identity_body,
        "path_identity_getter_rechecks_current_main_object",
        "the getter must not return stale retained identity after pathname replacement",
    )
    namespace_check = reset.find(
        "if (!(namespace_identity == request.expected.namespace_identity))"
    )
    open_check = reset.find("open_existing_ledger_or_throw", namespace_check)
    begin_check = reset.find("SyncSqliteTransaction transaction", open_check)
    require(
        checks,
        min(namespace_check, open_check, begin_check) >= 0
        and namespace_check < open_check < begin_check,
        "namespace_precondition_precedes_database_open_and_transaction",
        "a replacement object is rejected before SQLite interprets or mutates it",
    )

    require(
        checks,
        reset.count("sqlite3_changes64(db)") >= 3
        and "changed an unexpected row count" in reset
        and "lost exact metadata precondition" in reset
        and "lost exact identity precondition" in reset,
        "every_mutation_has_exact_changed_row_evidence",
        "a concurrent or anomalous row effect must roll back the transaction",
    )
    require(
        checks,
        all(f'owner, "{table}"' in reset for table in (
            "effect_transitions",
            "effect_outbox",
            "ingress_sender_replay_cache",
            "ledger_entries",
        )),
        "all_operational_tables_are_explicitly_cleared",
        "reset must neither depend on cascades nor leave hidden replay state",
    )
    require(
        checks,
        "UPDATE ledger_identity SET ledger_instance_id=?1" in reset
        and "reset_receipt_sha256 = receipt" in reset
        and "new_ledger_instance_id = receipt" in reset,
        "durable_identity_is_the_deterministic_receipt",
        "commit-before-report recovery must be derivable from ledger state",
    )
    require(
        checks,
        all(label in reset for label in (
            '"ledger_path"',
            '"reset_intent_id"',
            '"operator_id"',
            '"reason_sha256"',
            '"expected_parent_device"',
            '"expected_parent_inode"',
            '"expected_database_device"',
            '"expected_database_inode"',
            '"expected_ledger_instance_id"',
            '"expected_state_sha256"',
            '"expected_effect_outbox_rows"',
            '"expected_ingress_sender_replay_rows"',
        )),
        "receipt_digest_binds_actor_reason_path_and_exact_prior",
        "the new identity must commit the complete administrative authorization",
    )
    require(
        checks,
        "anonsync-sqlite-replay-ledger-logical-reset-receipt-v3" in reset
        and "logical-reset-receipt-v2" not in reset,
        "receipt_digest_domain_version_matches_namespace_bound_protocol",
        "adding filesystem-object identity changes the receipt algebra and must advance its internal domain separator",
    )
    require(
        checks,
        reset.count("is_complete_empty_postcondition(") >= 3
        and "transaction postcondition" in reset
        and "committed postcondition" in reset
        and "state_advanced_after_commit" in reset,
        "fresh_commit_proves_empty_while_recovery_classifies_later_state",
        "the committing call proves the empty result, while an exact retry recovers history without erasing subsequent work",
    )
    recovery_start = reset.find("if (observed.ledger_instance_id == receipt)")
    mutation_start = reset.find("} else {", recovery_start)
    mutation_end = reset.find("transaction.commit();", mutation_start)
    recovery_branch = (
        reset[recovery_start:mutation_start]
        if min(recovery_start, mutation_start) >= 0
        else ""
    )
    require(
        checks,
        bool(recovery_branch)
        and "state_advanced_after_commit" in recovery_branch
        and "AlreadyCommitted" in recovery_branch
        and "execute_expected_delete" not in recovery_branch
        and "rotate_identity" not in recovery_branch,
        "receipt_recovery_has_no_destructive_effect_authority",
        "once the deterministic receipt identity is durable, replay may classify current state but cannot clear or rotate it again",
    )
    require(
        checks,
        mutation_start >= 0
        and mutation_end > mutation_start
        and "expectation_matches_state(request.expected, observed)"
        in reset[mutation_start:mutation_end]
        and "execute_expected_delete" in reset[mutation_start:mutation_end]
        and "rotate_identity" in reset[mutation_start:mutation_end],
        "only_exact_prior_state_reaches_the_mutation_branch",
        "the destructive branch remains guarded by the complete logical-state expectation",
    )
    require(
        checks,
        "budget.detach();" in reset
        and "SqliteVerificationBudget postcommit_budget" in reset,
        "progress_handler_ownership_is_explicit_across_postcommit_check",
        "one verification budget must detach before another installs its callback",
    )
    require(
        checks,
        all(token in reset_hpp for token in (
            "SqliteReplayLedgerResetCutpoint",
            "DurableOutcomeObservedBeforePostcommitVerification",
            "SqliteReplayLedgerResetDurableOutcomeError",
            "reset_receipt_sha256() const noexcept",
        )),
        "typed_durable_outcome_surface_is_public",
        "callers must distinguish a denied precondition from a committed transition whose verification could not complete",
    )
    reset_function_start = reset.find(
        "SqliteReplayLedgerResetResult reset_sqlite_replay_ledger("
    )
    reset_function = reset[reset_function_start:] if reset_function_start >= 0 else ""
    detach = reset_function.find("budget.detach();")
    final_commit_before_detach = reset_function.rfind("transaction.commit();", 0, detach)
    observer_cutpoint = reset_function.find(
        "DurableOutcomeObservedBeforePostcommitVerification", detach
    )
    postcommit_namespace = reset_function.find(
        'label + " post-commit namespace gate"', observer_cutpoint
    )
    durable_wrap = reset_function.find(
        "std::throw_with_nested(SqliteReplayLedgerResetDurableOutcomeError(",
        postcommit_namespace,
    )
    require(
        checks,
        min(detach, final_commit_before_detach, observer_cutpoint,
            postcommit_namespace, durable_wrap) >= 0
        and final_commit_before_detach < detach < observer_cutpoint
        < postcommit_namespace < durable_wrap,
        "durable_cutpoint_precedes_postcommit_checks_and_typed_wrap",
        "after COMMIT, every observer or verification failure must carry durable-outcome evidence rather than masquerading as an uncommitted denial",
    )
    require(
        checks,
        "result.outcome" in reset_function[durable_wrap:]
        and "receipt" in reset_function[durable_wrap:]
        and "std::throw_with_nested" in reset_function[durable_wrap:]
        and "public std::nested_exception" in reset_hpp
        and "typed post-commit error lost its nested root cause" in focused,
        "typed_postcommit_error_preserves_outcome_receipt_and_cause",
        "recovery needs the exact deterministic receipt and the original nested diagnostic",
    )
    require(
        checks,
        all(token in reset for token in (
            "SQLITE_OPEN_FULLMUTEX",
            "SQLITE_OPEN_NOFOLLOW",
            "SQLITE_DBCONFIG_TRUSTED_SCHEMA",
            "SQLITE_DBCONFIG_DEFENSIVE",
            "PRAGMA foreign_keys=ON",
            "PRAGMA trusted_schema=OFF",
            "PRAGMA ignore_check_constraints=OFF",
            "PRAGMA cell_size_check=ON",
            "PRAGMA mmap_size=0",
            "PRAGMA synchronous=FULL",
        )),
        "reset_connection_profile_is_hardened_and_verified",
        "the administrative connection must fail closed on profile drift",
    )
    require(
        checks,
        reset.count("verify_family_or_throw") >= 3
        and reset.count("verify_open_database_or_throw") >= 4
        and "requires an existing ledger database" in reset,
        "namespace_and_open_identity_are_reasserted",
        "reset must neither create a new database nor switch pathname identity",
    )

    digest_pin = runner.find("if (sha256_hex(request_text) != request_sha256)")
    parse = runner.find("const Json root = parse_json_text(request_text)", digest_pin)
    reset_call = runner.find(
        "execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(", parse
    )
    require(
        checks,
        min(digest_pin, parse, reset_call) >= 0 and digest_pin < parse < reset_call,
        "request_digest_pin_precedes_parse_and_effect",
        "untrusted request bytes cannot be interpreted or used before exact pin verification",
    )
    require(
        checks,
        "kMaximumResetRequestBytes = 64U * 1024U" in runner
        and "request_text.size() != request_size" in runner,
        "request_read_has_size_and_change_ceiling",
        "the CLI must reject oversized or changing request files",
    )
    require(
        checks,
        "reject_reset_publication_inside_ledger_namespace_or_throw" in runner
        and "std::filesystem::equivalent" in runner
        and all(suffix in runner for suffix in (
            '"-wal"', '"-shm"', '"-journal"', '".write.lock"',
            '".restore.lock"', '".reset.lock"',
        ))
        and "refuses publication inside the SQLite ledger namespace" in runner,
        "reset_publication_fence_covers_lexical_and_object_aliases",
        "a report pathname may not name or hard-link any live ledger-family object",
    )
    state_command_start = runner.find(
        "int run_sqlite_replay_ledger_reset_state_command("
    )
    state_command_end = runner.find(
        "int run_sqlite_replay_ledger_reset_command(", state_command_start
    )
    state_command = (
        runner[state_command_start:state_command_end]
        if min(state_command_start, state_command_end) >= 0
        else ""
    )
    state_output_fence = state_command.find(
        "reject_reset_publication_inside_ledger_namespace_or_throw("
    )
    state_inspection = state_command.find(
        "inspect_sqlite_replay_ledger_reset_state("
    )
    state_publication = state_command.find(
        "write_sync_cli_report_json_or_throw("
    )
    require(
        checks,
        min(state_output_fence, state_inspection, state_publication) >= 0
        and state_output_fence < state_inspection < state_publication,
        "reset_state_output_fence_precedes_inspection_and_publication",
        "an aliased inspection report must be denied before opening or interpreting the ledger",
    )
    reset_command_start = runner.find(
        "int run_sqlite_replay_ledger_reset_command("
    )
    reset_command = runner[reset_command_start:] if reset_command_start >= 0 else ""
    request_receipt_fence = reset_command.find(
        "reject_reset_receipt_request_alias_or_throw("
    )
    request_read = reset_command.find("const std::string request_text = read_file(")
    ledger_receipt_fence = protocol.find(
        "reject_receipt_inside_ledger_namespace_or_throw("
    )
    reset_effect = protocol.find("reset_sqlite_replay_ledger(")
    require(
        checks,
        min(request_receipt_fence, request_read) >= 0
        and request_receipt_fence < request_read,
        "receipt_request_alias_fence_precedes_request_read",
        "receipt publication cannot overwrite or hard-link the digest-pinned authorization bytes",
    )
    require(
        checks,
        min(ledger_receipt_fence, reset_effect) >= 0
        and ledger_receipt_fence < reset_effect,
        "receipt_ledger_namespace_fence_precedes_reset_effect",
        "the output destination must be proved disjoint from the request-owned ledger before mutation",
    )
    require(
        checks,
        runner.count("require_exact_json_object_fields(") >= 2
        and "contains duplicate ASCII-case-insensitive field" in runner,
        "request_json_has_exact_casefolded_unique_fields",
        "duplicate or unknown fields cannot smuggle alternate authority",
    )
    require(
        checks,
        all(format_name in reset_hpp for format_name in (
            "anonsync-sqlite-replay-ledger-reset-request-v3",
            "anonsync-sqlite-replay-ledger-reset-state-v2",
            "anonsync-sqlite-replay-ledger-reset-receipt-v4",
        ))
        and all(format_name in cli_test for format_name in (
            "anonsync-sqlite-replay-ledger-reset-request-v3",
            "anonsync-sqlite-replay-ledger-reset-state-v2",
            "anonsync-sqlite-replay-ledger-reset-receipt-v4",
        ))
        and "\\\"durable_outcome\\\": \\\"committed\\\"" in documents
        and "fresh-immutable-receipt-path" in documents,
        "protocol_versions_pin_namespace_and_recovery_semantics",
        "request, inspection, receipt, and executable oracle must advance together when authority semantics change",
    )
    require(
        checks,
        "namespace_identity" in runner
        and all(field in runner for field in (
            "parent_device", "parent_inode", "database_device", "database_inode"
        ))
        and "require_json_u64_decimal_string" in runner,
        "cli_roundtrips_exact_uint64_namespace_identity",
        "device and inode values cannot be truncated through signed JSON-number conversion",
    )
    require(
        checks,
        ordered(
            protocol,
            "sqlite_replay_ledger_reset_receipt_json(request, request_sha256)",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(",
            "reset_sqlite_replay_ledger(",
            "verify_reset_result_binding_or_throw(",
            "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(")
        and "execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw("
            in reset_command
        and "reset_sqlite_replay_ledger(" not in reset_command
        and "durable_transition_observed" not in reset_command
        and "SqliteReplayLedgerResetReceiptProtocolError" in reset_command
        and "error.durable_evidence()" in reset_command
        and "error.reported_reset_outcome()" in reset_command
        and "class SyncPreparedImmutableJsonPublication final" in publication_hpp
        and "parent rebind is denied against retained directory authority"
            in prepared_publication_test
        and "rebind denial occurs before any temp reservation"
            in prepared_publication_test,
        "receipt_publication_is_atomic_and_commit_loss_is_classified",
        "one focused owner binds bytes and parent authority before reset, verifies returned durable evidence, publishes once, and gives the CLI typed recovery evidence",
    )
    protocol_catch = runner.find(
        "SqliteReplayLedgerResetReceiptProtocolError& error"
    )
    require(
        checks,
        protocol_catch >= 0
        and "rerun the exact digest-pinned request with a fresh absent receipt path"
            in runner[protocol_catch:]
        and "do not replay until durable identity is independently resolved"
            in runner[protocol_catch:]
        and "exit_status = 3;" in runner[protocol_catch:]
        and "exit_status = 4;" in runner[protocol_catch:]
        and "return exit_status;" in runner[protocol_catch:]
        and "error.recovery_action()" in runner[protocol_catch:]
        and "error.publication_effect().has_value()" in runner[protocol_catch:],
        "cli_classifies_postcommit_verification_failure_as_recoverable",
        "the CLI consumes one invariant-preserving protocol error instead of reconstructing commit and publication state from catch ordering",
    )
    require(
        checks,
        "argc != 5" in cli and "argc != 7" in cli
        and "separate commands" in cli
        and "no unrelated arguments" in cli,
        "administrative_commands_are_cli_isolated",
        "ordinary command state cannot broaden the request-owned path or transition",
    )
    require(
        checks,
        all(flag in cli for flag in (
            "--ledger-reset-state",
            "--ledger-reset-state-report",
            "--ledger-reset-request",
            "--ledger-reset-request-sha256",
            "--ledger-reset-receipt",
        )),
        "standalone_state_and_reset_flags_are_public",
        "operators need a two-step inspect-authorize-execute surface",
    )
    require(
        checks,
        "run_sqlite_replay_ledger_reset_state_command" in public
        and "run_sqlite_replay_ledger_reset_command" in public,
        "standalone_commands_have_explicit_core_api",
        "the CLI facade must delegate to named reviewed functions",
    )

    require(
        checks,
        "class SelfExecTestProcess final" in self_exec_header
        and "::posix_spawn(" in self_exec_source
        and "posix_spawn_file_actions_addclosefrom_np" in self_exec_source
        and "POSIX_SPAWN_SETPGROUP" in self_exec_source
        and "timed out and was killed and reaped" in self_exec_source,
        "failstop_process_owner_is_selfexec_fd_clean_and_bounded",
        "focused fail-stop/crash probes use one move-only self-exec owner with race-free descriptor closure, isolated process group, and kill/reap timeout",
    )
    focused_helper = slice_between(
        focused,
        "int run_focused_reset_helper(int argc, char** argv)",
        "void test_streaming_digest(",
    )
    require(
        checks,
        '#include "self_exec_test_process.hpp"' in focused
        and "--anonsync-reset-focused-helper-v1" in focused
        and "argc != 7" in focused
        and "::fork(" not in focused
        and "::waitpid(" not in focused
        and bool(focused_helper)
        and ordered(
            focused_helper,
            "verify_self_exec_child_boundary_or_throw();",
            "parse_focused_helper_instruction_or_throw(argc, argv)",
            "inspect_sqlite_replay_ledger_reset_state(instruction.ledger_path)",
            "state.state_sha256 != instruction.expected_state_sha256",
            "sqlite_replay_ledger_reset_receipt_sha256(request) !=",
            "reset_sqlite_replay_ledger(request)",
        ),
        "focused_helpers_rebind_durable_evidence_after_exec",
        "no C++ or SQLite executes in a raw post-fork child; the fresh image verifies its boundary and reconstructs exact state/receipt authority before mutation",
    )
    require(
        checks,
        focused.count("wait_for_exact_exit(") >= 3
        and focused.count("10s") >= 3
        and "!child.active()" in focused,
        "focused_helper_waits_are_bounded_and_consuming",
        "all migrated write-gate and commit/report-loss subprocesses have explicit deadlines and surrender process authority after reap",
    )

    for marker, check_id, detail in (
        ("digest-only mutation did not isolate stale-intent hazard", "focused_stale_outbox_oracle", "non-summary mutable state must invalidate stale authority"),
        ("same-thread nested reset mutated durable state", "focused_same_thread_gate_oracle", "administrative reset cannot borrow ordinary writer ownership"),
        ("nested write-gate lifetime inversion did not fail stopped", "focused_lifo_lifetime_oracle", "nested capability lifetime inversion must fail before kernel unlock"),
        ("cross-thread write-gate destruction did not fail stopped", "focused_thread_affinity_oracle", "another thread cannot destroy originating lock authority"),
        ("reset replaced or deleted the main database inode", "focused_in_place_inode_oracle", "reset must preserve namespace identity"),
        ("namespace-mismatched reset mutated replacement database", "focused_replacement_inode_oracle", "a byte-equivalent object at the same path must not inherit an old intent"),
        ("bound path identity accepted a replaced database object", "focused_bound_identity_recheck_oracle", "retained identity must be compared with the current directory entry at use time"),
        ("reset-state inspection created an unauthorized parent directory", "focused_missing_parent_side_effect_oracle", "inspection cannot manufacture namespace prerequisites"),
        ("replayed old reset wiped post-reset append", "focused_advanced_state_recovery_oracle", "receipt recovery cannot reactivate destructive authority"),
        ("lost-report retry did not recover committed outcome", "focused_commit_report_loss_oracle", "the durable receipt must recover a commit/report crash window"),
        ("post-commit failure was reported as an ordinary pre-commit error", "focused_typed_postcommit_oracle", "postcommit uncertainty must retain its committed outcome and deterministic receipt"),
        ("typed post-commit failure was not recoverable by exact replay", "focused_typed_postcommit_recovery_oracle", "the exact request must recover a typed durable-outcome failure without another destructive effect"),
        ("exact schema rejected", "focused_exact_schema_oracle", "unreviewed schema objects must deny reset"),
        ("--seed-ledger", "focused_cli_fixture_mode", "the integration oracle needs an exact schema fixture"),
        ("--append-after-reset", "focused_cli_advanced_fixture_mode", "the integration oracle needs a legitimate post-reset advance"),
    ):
        require(checks, marker in focused, check_id, detail)
    for marker, check_id, detail in (
        ("wrong request pin did not fail at the digest boundary", "cli_wrong_pin_oracle", "CLI must prove digest-before-effect ordering"),
        ("reset replaced the SQLite namespace", "cli_inode_oracle", "CLI execution must remain in-place"),
        ("first execution and exact recovery emitted different receipt bytes", "cli_idempotent_recovery_oracle", "exact retry must recover byte-identical durable-event evidence at a fresh path"),
        ("receipt preflight followed or changed a symlink victim", "cli_symlink_publication_oracle", "receipt output cannot follow hostile names"),
        ("immutable receipt-name reuse was not denied at preflight", "cli_immutable_name_reuse_oracle", "an occupied evidence name must deny before destructive authority is exercised"),
        ("ordinary open must not mint destructive authority", "cli_legacy_flag_oracle", "removed convenience authority must stay removed"),
        ("did not bind the inspected database object", "cli_database_identity_oracle", "inspection JSON must expose exact object identity"),
        ("did not bind the inspected parent directory", "cli_parent_identity_oracle", "inspection JSON must expose exact namespace-owner identity"),
        ("replayed old reset erased legitimate post-reset state", "cli_advanced_state_recovery_oracle", "exact retry recovers a receipt without deleting later state"),
        ("later-state recovery leaked attempt-local observations into receipt bytes", "cli_advanced_state_receipt_oracle", "receipt recovery must remain byte-identical and exclude later-state observations"),
        ("occupied immutable receipt bytes or inode were replaced", "cli_occupied_regular_receipt_oracle", "create-new publication must preserve unrelated existing bytes and inode"),
        ("state report main-file alias replaced the ledger", "cli_state_main_alias_oracle", "inspection output cannot overwrite the database main file"),
        ("state report sidecar alias created a WAL-named output", "cli_state_sidecar_alias_oracle", "inspection output cannot occupy a SQLite sidecar name"),
        ("state report hardlink alias replaced the aliased object", "cli_state_hardlink_alias_oracle", "inspection output cannot target a hard link to the database object"),
        ("reset receipt hardlink alias replaced the aliased ledger object", "cli_receipt_hardlink_alias_oracle", "reset receipt output cannot target a hard link to the live database"),
        ("reset receipt/request lexical alias changed pinned request bytes", "cli_request_lexical_alias_oracle", "receipt output cannot overwrite its exact request pathname"),
        ("reset receipt/request hardlink alias changed pinned request bytes", "cli_request_hardlink_alias_oracle", "receipt output cannot target an equivalent request object"),
        ("publication alias rejection mutated exact ledger state", "cli_output_alias_no_effect_oracle", "all output alias denials must occur before the reset transition"),
    ):
        require(checks, marker in cli_test, check_id, detail)

    require(
        checks,
        "add_library(anonsync_self_exec_test_process STATIC" in cmake
        and "add_executable(anonsync_self_exec_test_process_test" in cmake
        and "add_executable(anonsync_sqlite_replay_ledger_reset_test" in cmake
        and "add_executable(anonsync_sqlite_replay_ledger_reset_crash_frontier_test" in cmake
        and "add_executable(anonsync_sqlite_replay_ledger_reset_documents_test" in cmake
        and "add_test(NAME anonsync_sqlite_replay_ledger_reset_test" in cmake
        and "add_test(NAME anonsync_sqlite_replay_ledger_reset_crash_frontier_test" in cmake
        and "add_test(NAME anonsync_sqlite_replay_ledger_reset_documents_test" in cmake
        and "anonsync_sqlite_replay_ledger_reset_cli_test" in cmake
        and "anonsync_self_exec_test_process_test" in cmake
        and "anonsync_self_exec_test_process_source_audit" in cmake
        and "anonsync_sqlite_replay_ledger_reset_source_audit" in cmake
        and "anonsync_sqlite_replay_ledger_reset_crash_frontier_source_audit" in cmake
        and "anonsync_sqlite_replay_ledger_reset_receipt_source_audit" in cmake
        and "anonsync_sqlite_replay_ledger_reset_receipt_protocol_source_audit" in cmake
        and "add_executable(anonsync_sync_atomic_file_publication_prepared_test" in cmake
        and "add_test(NAME anonsync_sync_atomic_file_publication_prepared_test" in cmake,
        "focused_cpp_cli_and_source_oracles_are_ctest_gates",
        "runtime, integration, and structural proofs must all be release obligations",
    )
    require(
        checks,
        all(path in verifier for path in (
            "src/persistence/sqlite_replay_ledger_reset.cpp",
            "src/persistence/sqlite_replay_ledger_reset.hpp",
            "src/persistence/sqlite_replay_ledger_reset_documents.cpp",
            "src/persistence/sqlite_replay_ledger_reset_documents.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp",
            "src/persistence/sqlite_replay_ledger_write_gate.cpp",
            "src/persistence/sqlite_replay_ledger_write_gate.hpp",
            "tests/self_exec_test_process.hpp",
            "tests/self_exec_test_process.cpp",
            "tests/self_exec_test_process_test.cpp",
            "tests/persistence/sqlite_replay_ledger_reset_tests.cpp",
            "tests/persistence/sqlite_replay_ledger_reset_fixture.hpp",
            "tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp",
            "tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp",
            "tests/sync_atomic_file_publication_prepared_test.cpp",
            "tools/audit_self_exec_test_process.py",
            "tools/test_sqlite_replay_ledger_reset_cli.py",
            "tools/audit_sqlite_replay_ledger_reset.py",
            "tools/audit_sqlite_replay_ledger_reset_crash_frontier.py",
            "tools/audit_sqlite_replay_ledger_reset_receipt.py",
            "tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py",
        )),
        "release_verifier_requires_reset_boundary_and_proofs",
        "a sealed archive cannot omit the owner, capability, runtime oracle, or audits",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-replay-ledger-reset-audit-v3",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "active_source_files_scanned": len(active_source_files),
            "active_unlink_sqlite_family_hits": unlink_hits,
            "reset_owner_lines": len(reset.splitlines()),
            "write_gate_owner_lines": len(gate.splitlines()),
            "self_exec_owner_lines": len(self_exec_source.splitlines()),
            "focused_cpp_lines": len(focused.splitlines()),
            "focused_fixture_lines": len(focused_fixture.splitlines()),
            "crash_frontier_test_lines": len(crash_frontier_test.splitlines()),
            "reset_documents_lines": len(documents.splitlines()),
            "reset_receipt_protocol_lines": len(protocol.splitlines()),
            "reset_documents_test_lines": len(documents_test.splitlines()),
            "cli_oracle_lines": len(cli_test.splitlines()),
        },
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
