#!/usr/bin/env python3
"""Fail-closed audit for the reset/receipt combined crash-frontier proof."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_atomic_file_publication_internal.hpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp"),
    Path("tests/self_exec_test_process.hpp"),
    Path("tests/self_exec_test_process.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_fixture.hpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp"),
    Path("tools/audit_self_exec_test_process.py"),
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


def block_between(text: str, begin: str, end: str) -> str:
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
            "format": "anonsync-reset-publication-crash-frontier-audit-v3",
            "root": str(root),
            "passed": False,
            "passed_checks": 0,
            "total_checks": 0,
            "checks": [],
            "violations": [f"missing required file: {path}" for path in missing],
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
    public_header = text[Path("src/sync_atomic_file_publication.hpp")]
    internal_header = text[Path("src/sync_atomic_file_publication_internal.hpp")]
    publication = text[Path("src/sync_atomic_file_publication.cpp")]
    reset_header = text[Path("src/persistence/sqlite_replay_ledger_reset.hpp")]
    reset_source = text[Path("src/persistence/sqlite_replay_ledger_reset.cpp")]
    protocol_header = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp")]
    protocol_internal = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp")]
    protocol_source = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp")]
    self_exec_header = text[Path("tests/self_exec_test_process.hpp")]
    self_exec_source = text[Path("tests/self_exec_test_process.cpp")]
    fixture = text[Path("tests/persistence/sqlite_replay_ledger_reset_fixture.hpp")]
    reset_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp")]
    frontier_test = text[
        Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp")
    ]
    audit_source = text[
        Path("tools/audit_sqlite_replay_ledger_reset_crash_frontier.py")
    ]
    verifier = text[Path("tools/verify_release_package.py")]
    checks: list[Check] = []

    require(
        checks,
        "AtomicFilePublicationObserver" not in public_header
        and "namespace atomic_file_publication_detail" in public_header
        and "class PreparedImmutableJsonPublicationObserverAccess;"
        in public_header
        and "friend class atomic_file_publication_detail::" in public_header
        and "PreparedImmutableJsonPublicationObserverAccess" in public_header,
        "deterministic_observer_is_internal_friend_only",
        "failure injection is not public runtime API, while one named internal access class can consume the exact capability",
    )
    require(
        checks,
        all(token in internal_header for token in (
            "class PreparedImmutableJsonPublicationObserverAccess final",
            "SyncPreparedImmutableJsonPublication& publication",
            "AtomicFilePublicationObserver observer",
            "void* observer_context",
        )),
        "internal_access_accepts_exact_prepared_capability",
        "the deterministic seam receives the same move-only object prepared before the irreversible SQLite transition",
    )
    require(
        checks,
        ordered(
            publication,
            "void SyncPreparedImmutableJsonPublication::publish_or_throw()",
            "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(",
            "*this, nullptr, nullptr",
        )
        and publication.count(
            "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw("
        ) == 2,
        "public_method_delegates_to_observed_implementation",
        "production and deterministic simulation share one implementation; the production call supplies no observer",
    )
    observed_owner = block_between(
        publication,
        "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(",
        "SyncPreparedImmutableJsonPublication\nprepare_sync_json_file_atomically_create_new_no_symlink_or_throw(",
    )
    require(
        checks,
        bool(observed_owner)
        and ordered(
            observed_owner,
            "if (publication.implementation_ == nullptr)",
            "std::move(publication.implementation_)",
            "require_sync_process_incarnation_or_fail_stop(",
            "implementation->owner_process_incarnation",
            "prepared immutable JSON publication destination authority",
        )
        and "implementation->label +" not in observed_owner
        and "belongs to a different process incarnation" not in observed_owner
        and observed_owner.count("observer_context, implementation->progress") == 2,
        "observed_path_consumes_once_and_forwards_every_platform",
        "authority is consumed before validation and both Windows/POSIX owners receive the same observer and progress state",
    )

    require(
        checks,
        "DurableOutcomeObservedBeforePostcommitVerification" in reset_header
        and ordered(
            reset_source,
            "transaction.commit();",
            "DurableOutcomeObservedBeforePostcommitVerification",
        ),
        "reset_observer_is_strictly_postcommit",
        "the reset frontier cannot be mistaken for precommit authority or a rollback-capable point",
    )

    enum_match = re.search(
        r"enum class AtomicFilePublicationCutpoint\s*\{(?P<body>.*?)\};",
        internal_header,
        re.DOTALL,
    )
    enum_names = []
    if enum_match:
        enum_names = [
            item.strip().rstrip(",")
            for item in enum_match.group("body").splitlines()
            if item.strip()
        ]
    array_match = re.search(
        r"kPreparedPosixPublicationCutpoints\{\{(?P<body>.*?)\}\};",
        frontier_test,
        re.DOTALL,
    )
    array_body = array_match.group("body") if array_match else ""
    normalized_array_body = re.sub(r"\s+", "", array_body)
    missing_cutpoints = [
        name
        for name in enum_names
        if f"AtomicFilePublicationCutpoint::{name}" not in normalized_array_body
    ]
    require(
        checks,
        len(enum_names) == 11 and not missing_cutpoints
        and "std::array<AtomicFilePublicationCutpoint, 11>" in frontier_test,
        "frontier_table_covers_every_publication_effect",
        "the combined oracle names all 11 publication observations exactly once rather than sampling convenient points",
    )

    require(
        checks,
        "class SelfExecTestProcess final" in self_exec_header
        and "::posix_spawn(" in self_exec_source
        and "posix_spawn_file_actions_addclosefrom_np" in self_exec_source
        and "POSIX_SPAWN_SETPGROUP" in self_exec_source
        and "timed out and was killed and reaped" in self_exec_source,
        "frontier_process_owner_is_selfexec_fd_clean_and_bounded",
        "the combined oracle depends on one move-only self-exec owner with race-free descriptor closure, isolated process group, and kill/reap timeout",
    )

    crash_protocol = block_between(
        frontier_test,
        "void test_publication_process_crash_frontiers(",
        "void test_protocol_caught_failure_frontiers(",
    )
    helper_protocol = block_between(
        frontier_test,
        "int run_crash_helper(int argc, char** argv)",
        "void recover_receipt_to_fresh_path(",
    )
    require(
        checks,
        bool(crash_protocol)
        and ordered(
            crash_protocol,
            "spawn_frontier_self_exec_helper(",
            "CrashHelperAction::PublicationCutpoint",
            "wait_for_exact_exit(",
            "!child.active()",
            "inspect_sqlite_replay_ledger_reset_state(fixture.ledger)",
        )
        and bool(helper_protocol)
        and ordered(
            helper_protocol,
            "verify_self_exec_child_boundary_or_throw();",
            "parse_crash_helper_instruction_or_throw(argc, argv)",
            "bind_crash_helper_fixture_or_throw(instruction)",
            "SqliteReplayLedgerResetReceiptProtocolObserverAccess::",
            "execute_or_throw(",
            "crash_at_publication_frontier",
        )
        and "::fork(" not in frontier_test
        and "::waitpid(" not in frontier_test
        and ordered(
            protocol_source,
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(",
            "reset_sqlite_replay_ledger(",
            "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(",
        ),
        "self_exec_oracle_spans_prepare_commit_publish_reopen",
        "each bounded self-exec helper rebinds exact parent evidence, executes the production protocol owner, crashes after SQLite reset, and leaves reopening to the parent",
    )
    reset_crash = block_between(
        frontier_test,
        "void test_reset_crash_frontier(",
        "void test_publication_process_crash_frontiers(",
    )
    require(
        checks,
        all(token in reset_crash for token in (
            "CrashHelperAction::ResetAfterDurableCommit",
            "wait_for_exact_exit(kResetCrashExit, 10s",
            "!child.active()",
            "!fs::exists(fixture.receipt)",
            "publication_temps(fixture.receipt_directory).empty()",
            "recover_receipt_to_fresh_path(",
        ))
        and "crash_at_durable_reset_frontier" in helper_protocol,
        "postcommit_prepublication_crash_is_explicit",
        "the first cross-resource gap uses a bounded self-exec helper and proves committed empty state with no falsely started filesystem publication",
    )

    recovery = block_between(
        frontier_test,
        "void recover_receipt_to_fresh_path(",
        "void test_reset_crash_frontier(",
    )
    require(
        checks,
        all(token in recovery for token in (
            "execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(",
            "SqliteReplayLedgerResetOutcome::AlreadyCommitted",
            "replay.reset.reset_receipt_sha256 == fixture.receipt_sha256",
            "PublishedAndDirectorySynced",
            "fixture.recovery_receipt",
            "verify_empty_reset_state(",
        ))
        and not any(token in recovery for token in (
            "remove(", "unlink(", "rename(", "publication_temps(",
        )),
        "recovery_is_exact_replay_to_fresh_name",
        "recovery invokes the same protocol owner, proves AlreadyCommitted identity, and publishes canonical bytes without guessing cleanup authority",
    )
    require(
        checks,
        all(token in crash_protocol for token in (
            "residue_after.device == residue_before.device",
            "residue_after.inode == residue_before.inode",
            "residue_after.size == residue_before.size",
            "residue_after.bytes == residue_before.bytes",
            "published_after.inode == published_before.inode",
            "first and recovery receipts were not byte-identical",
        )),
        "recovery_preserves_unknown_residue_and_first_publication",
        "the parent proves byte/inode identity instead of deleting crash residue or replacing an already published receipt",
    )

    caught_protocol = block_between(
        frontier_test,
        "void test_protocol_caught_failure_frontiers(",
        "void test_protocol_public_success(",
    )
    require(
        checks,
        all(token in caught_protocol for token in (
            "kPreparedPosixPublicationCutpoints",
            "execute_protocol_and_capture(",
            "ReceiptPublicationAfterExactDurableOutcome",
            "ReplayExactRequestToFreshReceiptPath",
            "expected_outcome_at(cutpoint)",
            "expected_residue_at(cutpoint)",
            "lost the nested publication cause",
            "recover_receipt_to_fresh_path(fixture, label, checks)",
        ))
        and "catch (const SqliteReplayLedgerResetReceiptProtocolError& error)"
        in frontier_test,
        "caught_failure_oracle_checks_typed_effects_and_consumption",
        "every observed failure verifies phase, replay authority, durable outcome, publication effect/residue, nested cause, ledger state, and recovery",
    )
    require(
        checks,
        all(token in frontier_test for token in (
            "rebind_receipt_parent_after_reset",
            "fs::rename(context.live_parent, context.parked_parent)",
            "replacement-sentinel.txt",
            "create_competing_receipt_after_reset",
            "competitor_after.inode == competitor_before.inode",
            "fresh-path recovery replaced the competing final",
        )),
        "postcommit_namespace_adversaries_preserve_unowned_objects",
        "parent rebinding and final-name competition after commit fail closed without mutating replacement or competing objects",
    )

    require(
        checks,
        all(token in frontier_test for token in (
            "test_protocol_public_success",
            "test_protocol_preparation_denial",
            "test_protocol_reset_precondition_denial",
            "test_protocol_postcommit_failure",
            "test_result_binding_contradiction_promotes_only_after_reopen",
            "test_result_binding_indeterminate_blocks_replay_authority",
            "test_durable_identity_indeterminate_blocks_replay_authority",
            "SqliteReplayLedgerResetReceiptProtocolFailure::Preparation",
            "ResetBeforeDurableOutcome",
            "ResetAfterExactDurableOutcome",
            "ReceiptPublicationAfterExactDurableOutcome",
            "ResetDurableIdentityIndeterminate",
            "DurableIdentityIndeterminate",
            "ResolveDurableIdentityBeforeRecovery",
            "preparation denial changed durable ledger state",
            "pre-durable reset denial changed the mismatched ledger",
        )),
        "protocol_state_machine_has_complete_noncrash_oracle",
        "success, exact-durable recovery, indeterminate durability, and all publication phases prove both positive evidence and absence of unauthorized side effects",
    )

    require(
        checks,
        '#include "sqlite_replay_ledger_reset_fixture.hpp"' in reset_test
        and '#include "sqlite_replay_ledger_reset_fixture.hpp"' in frontier_test
        and "seed_nonempty_ledger" in fixture
        and "request_for" in fixture
        and "sqlite_replay_ledger_reset_fixture" not in reset_source,
        "shared_fixture_replaces_duplicate_test_database_owner",
        "one test-only schema/seed owner feeds both reset and cross-frontier proofs without entering production",
    )

    target = "anonsync_sqlite_replay_ledger_reset_crash_frontier_test"
    require(
        checks,
        f"add_executable({target}" in cmake
        and "if(CMAKE_SYSTEM_NAME STREQUAL \"Linux\")" in cmake
        and f"add_test(NAME {target}" in cmake
        and "PROPERTIES TIMEOUT 120" in cmake,
        "linux_frontier_executable_is_release_obligation",
        "self-exec/_exit semantics are platform-scoped and CTest-enforced with an explicit timeout",
    )
    require(
        checks,
        "ANONSYNC_RESET_CRASH_FRONTIER_LINK_LIBRARIES" in cmake
        and "combined reset/publication crash-frontier proof must not link anonsync_core_lib" in cmake
        and target in cmake[cmake.find("ANONSYNC_SANITIZER_COMPILE_TARGETS"):]
        and f"target_link_options(\n      {target} PRIVATE" in cmake,
        "frontier_target_is_focused_and_sanitizer_guarded",
        "the proof cannot silently absorb the core monolith and participates in ASan/UBSan lanes",
    )
    require(
        checks,
        all(path in verifier for path in (
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp",
            "tests/self_exec_test_process.hpp",
            "tests/self_exec_test_process.cpp",
            "tests/self_exec_test_process_test.cpp",
            "tests/persistence/sqlite_replay_ledger_reset_fixture.hpp",
            "tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp",
            "tools/audit_self_exec_test_process.py",
            "tools/audit_sqlite_replay_ledger_reset_crash_frontier.py",
        )),
        "release_verifier_requires_combined_proof_surface",
        "a sealed archive cannot omit the shared fixture, executable oracle, or structural audit",
    )
    require(
        checks,
        "anonsync_self_exec_test_process_source_audit" in cmake
        and "audit_self_exec_test_process.py" in cmake
        and "anonsync_sqlite_replay_ledger_reset_crash_frontier_source_audit" in cmake
        and "audit_sqlite_replay_ledger_reset_crash_frontier.py" in cmake,
        "structural_audit_is_a_ctest_gate",
        "the exact source topology and proof obligations are checked by the same release suite",
    )
    require(
        checks,
        len(audit_source.splitlines()) >= 300
        and all(token in audit_source for token in (
            "self_exec_oracle_spans_prepare_commit_publish_reopen",
            "recovery_preserves_unknown_residue_and_first_publication",
            "postcommit_namespace_adversaries_preserve_unowned_objects",
            "frontier_target_is_focused_and_sanitizer_guarded",
        )),
        "audit_is_substantive_and_self_describing",
        "the audit cannot pass merely because the combined proof disappeared",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-reset-publication-crash-frontier-audit-v3",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "publication_cutpoints": len(enum_names),
            "frontier_test_lines": len(frontier_test.splitlines()),
            "shared_fixture_lines": len(fixture.splitlines()),
            "protocol_owner_lines": len(protocol_source.splitlines()),
            "self_exec_owner_lines": len(self_exec_source.splitlines()),
            "audit_lines": len(audit_source.splitlines()),
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
