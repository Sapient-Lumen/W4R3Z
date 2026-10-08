#!/usr/bin/env python3
"""Fail-closed audit for the reset + immutable receipt protocol owner."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/runner.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_documents.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_atomic_file_publication_internal.hpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp"),
    Path("tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py"),
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


def between(text: str, begin: str, end: str) -> str:
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
            "format": "anonsync-reset-receipt-protocol-audit-v1",
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
    runner = text[Path("src/runner.cpp")]
    reset_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset.hpp")]
    reset_cpp = text[Path("src/persistence/sqlite_replay_ledger_reset.cpp")]
    protocol_hpp = text[
        Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp")
    ]
    protocol_internal = text[
        Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp")
    ]
    protocol_cpp = text[
        Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp")
    ]
    publication_hpp = text[Path("src/sync_atomic_file_publication.hpp")]
    publication_internal = text[Path("src/sync_atomic_file_publication_internal.hpp")]
    publication_cpp = text[Path("src/sync_atomic_file_publication.cpp")]
    reset_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_tests.cpp")]
    frontier_test = text[
        Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp")
    ]
    audit_source = text[
        Path("tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py")
    ]
    verifier = text[Path("tools/verify_release_package.py")]
    checks: list[Check] = []

    reset_command = runner[runner.find("int run_sqlite_replay_ledger_reset_command(") :]
    protocol_target = between(
        cmake,
        "set(ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_RECEIPT_PROTOCOL_SOURCE",
        "# Sealed SQLite images publish",
    )
    execute_owner = protocol_cpp[
        protocol_cpp.find(
            "SqliteReplayLedgerResetReceiptProtocolObserverAccess::execute_or_throw("
        ) :
    ]
    durable_classifier = between(
        protocol_cpp,
        "[[noreturn]] void rethrow_after_durable_reset_frontier_as_protocol_error(",
        "\n}\n\n}  // namespace",
    )
    protocol_link = between(
        protocol_target,
        "target_link_libraries(",
        "target_compile_options(",
    )

    require(
        checks,
        all(token in protocol_hpp for token in (
            "enum class SqliteReplayLedgerResetReceiptDurableEvidence",
            "NotDurable",
            "ExactRequestDurable",
            "DurableIdentityIndeterminate",
            "enum class SqliteReplayLedgerResetReceiptProtocolFailure",
            "Preparation",
            "ResetBeforeDurableOutcome",
            "ResetAfterExactDurableOutcome",
            "ResetDurableIdentityIndeterminate",
            "ReceiptPublicationAfterExactDurableOutcome",
            "enum class SqliteReplayLedgerResetReceiptRecoveryAction",
            "ResolveDurableIdentityBeforeRecovery",
            "ReplayExactRequestToFreshReceiptPath",
            "durable_evidence() const noexcept",
            "reported_reset_outcome() const noexcept",
            "SqliteReplayLedgerResetReceiptProtocolResult",
            "SqliteReplayLedgerResetReceiptProtocolError",
        )),
        "public_surface_is_a_typed_cross_resource_state_machine",
        "callers receive named phases, recovery authority, reset evidence, and publication effects instead of reconstructing state from catch order",
    )
    require(
        checks,
        "private:" in protocol_hpp
        and "friend class detail::" in protocol_hpp
        and "SqliteReplayLedgerResetReceiptProtocolError(" in protocol_hpp[
            protocol_hpp.find("private:") :
        ]
        and "class SqliteReplayLedgerResetReceiptProtocolErrorAccess final"
        in protocol_internal,
        "error_construction_is_protocol_private",
        "unrelated callers cannot mint internally inconsistent durable-outcome or retry evidence",
    )
    require(
        checks,
        "public std::nested_exception" in protocol_hpp
        and "public std::nested_exception" in reset_hpp
        and "std::throw_with_nested(SqliteReplayLedgerResetDurableOutcomeError("
        in reset_cpp
        and "typed post-commit error lost its nested root cause" in reset_test
        and "lost its nested observer cause" in frontier_test
        and "lost the nested publication cause" in frontier_test,
        "nested_root_causes_are_runtime_proven",
        "final typed errors explicitly own std::nested_exception and focused tests traverse both reset and publication cause chains",
    )
    require(
        checks,
        all(token in protocol_cpp for token in (
            "evidence_matches_phase",
            "recovery_matches_evidence",
            "outcome_matches_evidence",
            "publication_matches_phase",
            "expected_identity_valid",
            "reported_reset_outcome_.has_value() == !before_durable",
            "invalid sqlite reset/receipt protocol error evidence",
        )),
        "error_constructor_rejects_inconsistent_evidence",
        "phase, durable outcome, recovery action, receipt identity, and publication effect cannot disagree",
    )
    require(
        checks,
        "durable_reset_observed" not in protocol_hpp
        and "durable_reset_observed" not in protocol_cpp
        and "durable_reset_observed" not in reset_command
        and "durable_evidence() const noexcept" in protocol_hpp
        and "reported_reset_outcome() const noexcept" in protocol_hpp,
        "tri_state_evidence_replaces_boolean_authority",
        "callers cannot collapse not-durable, exact-request-durable, and indeterminate identity into one Boolean retry decision",
    )
    require(
        checks,
        all(token in protocol_cpp for token in (
            "inspect_exact_request_durable_evidence(",
            "inspect_sqlite_replay_ledger_reset_state(request.ledger_path)",
            "observed.normalized_ledger_path !=",
            "observed.namespace_identity ==",
            "observed.ledger_instance_id != expected_receipt",
            "independent reopen bound the current SQLite namespace",
        )),
        "independent_reopen_binds_path_namespace_and_identity",
        "promotion to exact replay authority requires a fresh reset-state inspection bound to the request path, original SQLite object, and expected receipt identity",
    )
    require(
        checks,
        protocol_cpp.count(
            "rethrow_after_durable_reset_frontier_as_protocol_error(") >= 3
        and "catch (const SqliteReplayLedgerResetDurableOutcomeError& error)" in execute_owner
        and "verify_reset_result_binding_or_throw(request, expected_receipt" in execute_owner
        and execute_owner.count(
            "rethrow_after_durable_reset_frontier_as_protocol_error(") >= 2
        and "ResetDurableIdentityIndeterminate" in protocol_cpp
        and "ResolveDurableIdentityBeforeRecovery" in protocol_cpp,
        "durable_error_and_binding_contradiction_share_reopen_classifier",
        "both postcommit exceptions and contradictory returned evidence pass through the same independent inspection before recovery authority is minted",
    )
    require(
        checks,
        all(token in frontier_test for token in (
            "corrupt_returned_reason_digest",
            "contradict_returned_result_and_replace_durable_identity",
            "test_result_binding_indeterminate_blocks_replay_authority",
            "replace_durable_identity_before_postcommit_verification",
            "different durable identity after reset commit",
            "incorrectly authorized replay after durable identity drift",
            "incorrectly retained automatic replay authority",
            "contradictory returned result was not promoted only after exact independent reopen",
        )),
        "runtime_oracle_executes_exact_and_indeterminate_promotions",
        "behavioral tests mutate returned evidence and the durable ledger identity, proving exact promotion and replay denial rather than only checking enum spellings",
    )
    require(
        checks,
        "do not replay until durable identity is independently resolved" in reset_command
        and "durable_evidence=" in reset_command
        and "exit_status = 4;" in reset_command,
        "cli_separates_indeterminate_from_exact_durable_failure",
        "automation receives a distinct non-replay exit status and explicit durable-evidence classification",
    )

    require(
        checks,
        "expected_reset_receipt_sha256()" in protocol_hpp
        and "expected_receipt_sha256=" in reset_command
        and " receipt_sha256=" not in reset_command,
        "candidate_digest_is_not_mislabeled_as_durable_evidence",
        "preparation failures may carry a deterministic candidate digest, so the CLI labels it as expected rather than committed",
    )

    require(
        checks,
        ordered(
            execute_owner,
            "reject_receipt_inside_ledger_namespace_or_throw(",
            "sqlite_replay_ledger_reset_receipt_sha256(request)",
            "sqlite_replay_ledger_reset_receipt_json(request, request_sha256)",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(",
            "reset_sqlite_replay_ledger(",
            "verify_reset_result_binding_or_throw(",
            "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(",
        ),
        "protocol_orders_authority_evidence_effect_and_publication",
        "the exact document and pinned output parent exist before reset, returned durable evidence is re-bound, and only then is the single-use publication consumed",
    )
    require(
        checks,
        all(token in protocol_cpp for token in (
            '"-wal"', '"-shm"', '"-journal"', '".write.lock"',
            '".restore.lock"', '".reset.lock"',
            "existing_paths_are_equivalent",
            "fs::equivalent",
            "refuses publication inside the SQLite ledger namespace",
        )),
        "receipt_namespace_fence_covers_lexical_and_object_aliases",
        "the protocol itself rejects every live SQLite family name and hard-link alias before deriving or exercising destructive authority",
    )
    require(
        checks,
        all(token in protocol_cpp for token in (
            "expectation_equals(result.prior, request.expected)",
            "result.normalized_ledger_path != request.ledger_path.generic_string()",
            "result.new_ledger_instance_id != expected_receipt",
            "result.reset_receipt_sha256 != expected_receipt",
            "result.reason_sha256 != sha256_hex(request.reason)",
            "result.connection_owner_generation == 0",
            "result.state_advanced_after_commit",
        )),
        "returned_reset_evidence_is_rebound_before_publication",
        "a reset implementation drift cannot cause the protocol to publish a receipt for different prior state, path, identity, reason, owner generation, or impossible first-commit classification",
    )
    require(
        checks,
        all(token in execute_owner for token in (
            "SqliteReplayLedgerResetReceiptProtocolFailure::Preparation",
            "ResetBeforeDurableOutcome",
            "ReceiptPublicationAfterExactDurableOutcome",
            "SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable",
            "ExactRequestDurable",
            "SqliteReplayLedgerResetReceiptRecoveryAction::None",
            "ReplayExactRequestToFreshReceiptPath",
        ))
        and all(token in durable_classifier for token in (
            "ResetAfterExactDurableOutcome",
            "ResetDurableIdentityIndeterminate",
            "ExactRequestDurable",
            "DurableIdentityIndeterminate",
            "ResolveDurableIdentityBeforeRecovery",
            "ReplayExactRequestToFreshReceiptPath",
        )),
        "every_failure_frontier_has_explicit_recovery_authority",
        "pre-durable failures authorize no effect, exact independently rebound outcomes authorize only fresh-path replay, and indeterminate identities authorize resolution rather than replay",
    )
    require(
        checks,
        "catch (const SyncAtomicFilePublicationError& error)" in execute_owner
        and "error.outcome()" in execute_owner
        and "error.residue()" in execute_owner
        and "ReceiptPublicationAfterExactDurableOutcome" in execute_owner,
        "publication_effect_is_preserved_through_protocol_wrapping",
        "the owner does not collapse not-published, durability-indeterminate, synced, or residue classifications into one textual failure",
    )
    require(
        checks,
        ordered(
            protocol_cpp,
            "execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(",
            "SqliteReplayLedgerResetReceiptProtocolObserverAccess::",
            "execute_or_throw(request, request_sha256, receipt_path, nullptr, nullptr,",
        )
        and "SqliteReplayLedgerResetObserver" not in protocol_hpp
        and "AtomicFilePublicationObserver" not in protocol_hpp,
        "public_entry_delegates_to_internal_exact_production_seam",
        "deterministic observers remain internal and the production API invokes the same owner with null observers",
    )

    require(
        checks,
        reset_command.count(
            "execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw("
        ) == 1
        and "reset_sqlite_replay_ledger(" not in reset_command
        and "prepare_sync_cli_immutable_json_create_new_or_throw(" not in reset_command
        and "SyncPreparedImmutableJsonPublication" not in reset_command
        and "durable_transition_observed" not in reset_command,
        "cli_choreography_is_removed",
        "the CLI parses and pins authorization bytes, then invokes one protocol transition rather than owning a cross-resource Boolean state machine",
    )
    require(
        checks,
        "reject_reset_publication_inside_ledger_namespace_or_throw(" not in reset_command
        and "reject_receipt_inside_ledger_namespace_or_throw(" in protocol_cpp,
        "receipt_namespace_invariant_has_one_owner",
        "state-report publication may retain its CLI fence, but reset receipt disjointness is enforced only by the reusable protocol boundary",
    )
    require(
        checks,
        "SqliteReplayLedgerResetReceiptProtocolError& error" in reset_command
        and "error.durable_evidence()" in reset_command
        and "error.reported_reset_outcome()" in reset_command
        and "error.recovery_action()" in reset_command
        and "error.publication_effect().has_value()" in reset_command
        and "exit_status = 3;" in reset_command
        and "exit_status = 4;" in reset_command
        and "return exit_status;" in reset_command,
        "cli_consumes_typed_recovery_evidence",
        "exit status and diagnostics are derived from the protocol error rather than inferred from which local statement completed",
    )

    require(
        checks,
        bool(protocol_target)
        and "add_library(anonsync_sqlite_replay_ledger_reset_receipt_protocol STATIC"
        in protocol_target
        and "anonsync_sqlite_replay_ledger_reset" in protocol_target
        and "anonsync_sqlite_replay_ledger_reset_documents" in protocol_target
        and "anonsync_sync_atomic_file_publication" in protocol_target
        and "anonsync_sha256_digest" in protocol_target,
        "focused_library_declares_every_direct_dependency",
        "the target cannot link accidentally only because another library happens to export the reset owner transitively",
    )
    require(
        checks,
        ordered(
            protocol_link,
            "PUBLIC",
            "anonsync_sqlite_replay_ledger_reset\n",
            "anonsync_sync_atomic_file_publication",
            "PRIVATE",
            "anonsync_sqlite_replay_ledger_reset_documents",
            "anonsync_sha256_digest",
        ),
        "public_interface_exposes_only_public_contract_dependencies",
        "reset and publication types remain transitive API requirements, while receipt rendering and hashing stay link-only implementation details",
    )
    require(
        checks,
        '"${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_RECEIPT_PROTOCOL_SOURCE}"'
        in cmake
        and "invariant-owned persistence boundary must remain outside anonsync_core_lib"
        in cmake
        and "anonsync_sqlite_replay_ledger_reset_receipt_protocol" in cmake[
            cmake.find("target_link_libraries(anonsync_core_lib") :
        ],
        "protocol_owner_is_not_reabsorbed_by_core_glob",
        "one translation unit owns the state machine and the aggregate runtime consumes it by link dependency",
    )
    require(
        checks,
        "anonsync_sqlite_replay_ledger_reset_receipt_protocol" in cmake[
            cmake.find("ANONSYNC_FOCUSED_BOUNDARY_TARGET") :
        ]
        and "anonsync_sqlite_replay_ledger_reset_receipt_protocol" in cmake[
            cmake.find("ANONSYNC_SANITIZER_COMPILE_TARGETS") :
        ],
        "focused_owner_is_no_core_guarded_and_sanitized",
        "the extracted boundary cannot silently absorb the monolith and participates in ASan/UBSan compile lanes",
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
            "test_protocol_caught_failure_frontiers",
            "SqliteReplayLedgerResetReceiptProtocolFailure::Preparation",
            "ResetBeforeDurableOutcome",
            "ResetAfterExactDurableOutcome",
            "ResetDurableIdentityIndeterminate",
            "ReceiptPublicationAfterExactDurableOutcome",
        )),
        "runtime_oracle_covers_success_and_all_five_failure_phases",
        "the protocol proof includes success, pre-durable denials, exact postcommit recovery, indeterminate identity denial, contradictory-result promotion, and every publication cutpoint",
    )
    require(
        checks,
        all(token in frontier_test for token in (
            "preparation denial changed durable ledger state",
            "pre-durable reset denial changed the mismatched ledger",
            "protocol success published noncanonical receipt bytes",
            "postcommit reset failure attempted receipt publication",
            "recover_receipt_to_fresh_path(",
        )),
        "runtime_oracle_checks_negative_space_and_recovery",
        "denials prove absence of ledger or filesystem effects, success proves canonical bytes, and durable failures recover only to a fresh path",
    )
    require(
        checks,
        "SqliteReplayLedgerResetReceiptProtocolObserverAccess::" in frontier_test
        and "execute_or_throw(" in frontier_test
        and "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw("
            not in frontier_test
        and "reset_sqlite_replay_ledger(fixture.request" not in frontier_test,
        "crash_oracle_uses_exact_production_protocol",
        "tests cannot pass by maintaining parallel prepare/reset/publish choreography that production no longer executes",
    )

    require(
        checks,
        "anonsync_sqlite_replay_ledger_reset_receipt_protocol_source_audit" in cmake
        and "audit_sqlite_replay_ledger_reset_receipt_protocol.py" in cmake,
        "protocol_structural_audit_is_a_ctest_gate",
        "the owner topology and typed recovery contract are enforced by the normal release suite",
    )
    require(
        checks,
        all(path in verifier for path in (
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp",
            "tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py",
        )),
        "release_verifier_requires_protocol_owner_and_audit",
        "a sealed archive cannot omit the cross-resource owner, deterministic seam, public contract, or source audit",
    )
    require(
        checks,
        len(audit_source.splitlines()) >= 300
        and all(token in audit_source for token in (
            "protocol_orders_authority_evidence_effect_and_publication",
            "cli_choreography_is_removed",
            "nested_root_causes_are_runtime_proven",
            "runtime_oracle_covers_success_and_all_five_failure_phases",
        )),
        "audit_is_substantive_and_self_describing",
        "the source gate cannot pass merely because the new protocol files disappeared or were bypassed",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-reset-receipt-protocol-audit-v1",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "protocol_header_lines": len(protocol_hpp.splitlines()),
            "protocol_internal_header_lines": len(protocol_internal.splitlines()),
            "protocol_owner_lines": len(protocol_cpp.splitlines()),
            "frontier_oracle_lines": len(frontier_test.splitlines()),
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
