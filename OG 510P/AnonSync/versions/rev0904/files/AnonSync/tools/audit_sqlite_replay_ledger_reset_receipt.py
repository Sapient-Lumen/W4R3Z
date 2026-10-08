#!/usr/bin/env python3
"""Fail-closed audit for canonical reset receipts and immutable publication."""

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
    Path("src/persistence/sqlite_replay_ledger_reset_documents.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_documents.cpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp"),
    Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_atomic_file_publication_internal.hpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp"),
    Path("tests/sync_atomic_file_publication_test.cpp"),
    Path("tests/sync_atomic_file_publication_prepared_test.cpp"),
    Path("tests/sync_atomic_file_publication_cutpoint_test.cpp"),
    Path("tools/test_sqlite_replay_ledger_reset_cli.py"),
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
            "format": "anonsync-sqlite-replay-ledger-reset-receipt-audit-v2",
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
    runner = text[Path("src/runner.cpp")]
    reset_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset.hpp")]
    docs_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset_documents.hpp")]
    docs = text[Path("src/persistence/sqlite_replay_ledger_reset_documents.cpp")]
    protocol_hpp = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp")]
    protocol_internal = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp")]
    protocol = text[Path("src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp")]
    publication_hpp = text[Path("src/sync_atomic_file_publication.hpp")]
    publication_internal = text[Path("src/sync_atomic_file_publication_internal.hpp")]
    publication = text[Path("src/sync_atomic_file_publication.cpp")]
    docs_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp")]
    frontier_test = text[Path("tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp")]
    publication_test = text[Path("tests/sync_atomic_file_publication_test.cpp")]
    prepared_test = text[Path("tests/sync_atomic_file_publication_prepared_test.cpp")]
    cutpoint_test = text[Path("tests/sync_atomic_file_publication_cutpoint_test.cpp")]
    cli_test = text[Path("tools/test_sqlite_replay_ledger_reset_cli.py")]
    verifier = text[Path("tools/verify_release_package.py")]

    checks: list[Check] = []
    receipt_function = between(
        docs,
        "std::string sqlite_replay_ledger_reset_receipt_json(",
        "\n}\n\n}  // namespace anonsync::persistence",
    )
    reset_command = between(
        runner,
        "int run_sqlite_replay_ledger_reset_command(",
        "\nnamespace {\n\nstruct CliRuntimeState",
    )
    if not reset_command:
        reset_command = runner[runner.find("int run_sqlite_replay_ledger_reset_command(") :]

    require(
        checks,
        'anonsync-sqlite-replay-ledger-reset-receipt-v4' in reset_hpp
        and 'anonsync-sqlite-replay-ledger-reset-receipt-v4' in docs_test
        and 'anonsync-sqlite-replay-ledger-reset-receipt-v4' in cli_test,
        "receipt_protocol_version_is_pinned_end_to_end",
        "the owner, focused unit oracle, and executable oracle agree on v4 semantics",
    )
    require(
        checks,
        "sqlite_replay_ledger_reset_receipt_json(\n    const SqliteReplayLedgerResetRequest& request,\n    std::string_view request_sha256)" in docs_hpp,
        "receipt_api_accepts_only_durable_event_evidence",
        "canonical receipt bytes depend on the validated request and exact request-file digest",
    )
    require(
        checks,
        bool(receipt_function)
        and "SqliteReplayLedgerResetResult" not in receipt_function
        and "SqliteReplayLedgerResetOutcome" not in receipt_function,
        "receipt_serializer_has_no_attempt_result_input",
        "first execution and recovery cannot diverge through an attempt-local result object",
    )
    require(
        checks,
        all(token not in receipt_function for token in (
            "connection_owner_generation",
            "state_advanced_after_commit",
            "already_committed",
            '"outcome"',
        )),
        "receipt_serializer_excludes_attempt_observations",
        "connection incarnation, classification, and later state are not durable-event fields",
    )
    require(
        checks,
        '\\"durable_outcome\\": \\"committed\\"' in docs
        and '\\"request_sha256\\":' in docs
        and '\\"reset_receipt_sha256\\":' in docs,
        "receipt_binds_commit_and_exact_request_bytes",
        "the event document declares the durable outcome and pins both request bytes and identity",
    )
    require(
        checks,
        all(token in receipt_function for token in (
            "request.reset_intent_id",
            "request.operator_id",
            "sha256_hex(request.reason)",
            "request.ledger_path.generic_string()",
            "expectation_json(request.expected",
        )),
        "receipt_binds_complete_administrative_authorization",
        "actor, reason digest, path, and exact prior state are all committed",
    )
    require(
        checks,
        all(token in receipt_function for token in (
            '\\"durable_line_count\\": 0',
            '\\"durable_head_hash\\": \\"GENESIS\\"',
            '\\"effect_transition_line_count\\": 0',
            '\\"effect_transition_head_hash\\": \\"GENESIS\\"',
            '\\"ledger_entry_rows\\": 0',
            '\\"effect_outbox_rows\\": 0',
        )),
        "receipt_commits_deterministic_empty_poststate",
        "the durable event's immediate poststate is explicit rather than inferred from a later observation",
    )
    require(
        checks,
        "replay-exact-digest-pinned-request-to-fresh-immutable-receipt-path" in receipt_function
        and "fresh absent receipt path" in reset_command,
        "recovery_requires_a_distinct_fresh_immutable_name",
        "recovery never rewrites a prior receipt or reuses a hostile retired pathname",
    )
    require(
        checks,
        "receipt rendering is byte-identical for the exact same evidence" in docs_test
        and "first execution and exact recovery emitted different receipt bytes" in cli_test,
        "canonical_bytes_have_unit_and_cli_oracles",
        "pure rendering and process-level recovery both prove exact byte equality",
    )
    require(
        checks,
        "changing the exact request-file digest changes receipt bytes" in docs_test
        and "receipt rejects malformed request-byte evidence" in docs_test,
        "request_byte_pin_is_material_and_validated",
        "the exact file digest changes output and malformed digest evidence is denied",
    )
    require(
        checks,
        "receipt excludes attempt-local and later-state observations" in docs_test
        and "later-state recovery leaked attempt-local observations into receipt bytes" in cli_test,
        "later_state_cannot_change_event_evidence",
        "subsequent legitimate writes do not mutate the historical reset event document",
    )
    require(
        checks,
        "replayed old reset erased legitimate post-reset state" in cli_test
        and "advanced receipt recovery lost durable receipt identity" in cli_test,
        "advanced_state_recovery_is_nondestructive",
        "exact replay recovers evidence while preserving later durable work",
    )
    require(
        checks,
        "class Sha256DigestBuilder" not in docs_hpp
        and "json_escape_document_text" in docs,
        "document_owner_has_small_explicit_surface",
        "the public document API exposes projections, not hashing or parsing machinery",
    )

    require(
        checks,
        "AtomicFilePublicationDisposition" in publication_internal
        and "ReplaceExisting" in publication_internal
        and "CreateNew" in publication_internal,
        "publication_disposition_is_typed",
        "mutable report replacement and immutable evidence creation cannot be selected by a Boolean",
    )
    require(
        checks,
        "class SyncPreparedImmutableJsonPublication final" in publication_hpp
        and "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw" in publication_hpp
        and "prepare_sync_cli_immutable_json_create_new_or_throw" in publication_hpp
        and "write_sync_json_file_atomically_create_new_no_symlink_or_throw" in publication_hpp,
        "create_new_publication_is_a_named_public_capability",
        "cross-resource callers can retain exact immutable publication authority while one-shot compatibility APIs remain explicit",
    )
    require(
        checks,
        "::renameat2(" in publication
        and "RENAME_NOREPLACE" in publication
        and "::syscall(" not in publication,
        "linux_create_new_uses_typed_atomic_noreplace",
        "the final namespace transition cannot replace a concurrent creator and avoids a variadic syscall boundary",
    )
    require(
        checks,
        "::renameat(directory_fd" in publication
        and "AtomicFilePublicationDisposition::ReplaceExisting" in publication,
        "mutable_replace_path_remains_explicit",
        "legacy mutable reports retain their reviewed replace semantics",
    )
    require(
        checks,
        "requires a no-replace rename primitive on this platform" in publication,
        "unsupported_create_new_platforms_fail_closed",
        "the implementation never emulates no-replace publication with a racy check-then-rename sequence",
    )
    require(
        checks,
        "immutable create-new final path already exists" in publication
        and publication.count("inspect_final_entry_at_or_throw") >= 2,
        "occupied_destination_is_revalidated",
        "preflight is advisory and final publication independently checks the pinned parent entry",
    )
    require(
        checks,
        ordered(
            protocol,
            "sqlite_replay_ledger_reset_receipt_json(request, request_sha256)",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(",
            "reset_sqlite_replay_ledger(",
            "verify_reset_result_binding_or_throw(",
            "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw("),
        "reset_orders_document_prepared_authority_effect_and_publication",
        "the protocol owner binds canonical bytes and exact destination-parent authority before mutation, rechecks reset evidence, then consumes one publication capability",
    )
    require(
        checks,
        "execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw("
            in reset_command
        and "write_sync_cli_report_json_or_throw" not in reset_command
        and "preflight_sync_cli_file_create_new_no_symlink_or_throw"
            not in reset_command
        and "write_sync_cli_immutable_json_create_new_or_throw"
            not in reset_command
        and "reset_sqlite_replay_ledger(" not in reset_command
        and "SyncPreparedImmutableJsonPublication" not in reset_command,
        "reset_does_not_reopen_or_replace_the_verified_destination",
        "the CLI delegates to one owner and cannot discard or reconstruct the retained parent capability between reset and publication",
    )
    require(
        checks,
        "receipt_path, std::move(receipt_document)" in protocol
        and "implementation->payload = std::move(payload);" in publication
        and "implementation->directory = open_parent_directory_or_throw("
            in publication,
        "reset_prepares_owned_bytes_and_parent_capability_before_commit",
        "caller storage, current working directory changes, and parent pathname replacement cannot redirect post-commit evidence",
    )
    require(
        checks,
        "SqliteReplayLedgerResetReceiptProtocolError& error" in reset_command
        and "error.durable_evidence()" in reset_command
        and "return exit_status;" in reset_command
        and "exit_status = 3;" in reset_command
        and "exit_status = 4;" in reset_command
        and "ReceiptPublicationAfterExactDurableOutcome" in protocol
        and "ReplayExactRequestToFreshReceiptPath" in protocol
        and "lost the nested publication cause" in frontier_test,
        "postcommit_publication_denial_is_typed_for_recovery",
        "a committed reset carries explicit replay authority, publication effect, and nested root cause rather than being reported as an ordinary precondition failure",
    )
    require(
        checks,
        "occupied immutable receipt bytes or inode were replaced" in cli_test
        and "occupied immutable receipt denial changed exact ledger state" in cli_test,
        "occupied_regular_path_has_preservation_oracle",
        "unrelated evidence bytes, inode, and ledger state survive preflight denial",
    )
    require(
        checks,
        "immutable receipt-name reuse changed published evidence" in cli_test
        and "immutable receipt-name reuse was not denied at preflight" in cli_test,
        "published_receipt_name_is_single_use",
        "the canonical event is recovered only to another fresh destination",
    )
    require(
        checks,
        "receipt preflight followed or changed a symlink victim" in cli_test
        and "symlink receipt preflight denial changed exact ledger state" in cli_test,
        "symlink_destination_denial_precedes_reset",
        "a hostile output name cannot redirect publication or consume destructive authority",
    )
    require(
        checks,
        "fresh-path reset recreated the formerly occupied symlink name" in cli_test
        and "fresh-path recovery changed the former symlink victim" in cli_test,
        "fresh_path_protocol_avoids_retired_hostile_name",
        "successful recovery uses a genuinely distinct name and preserves the former target",
    )
    require(
        checks,
        "create-new publication rejects rather than replacing an existing file" in publication_test
        and "rejected create-new publication preserves existing inode identity" in publication_test,
        "focused_existing_destination_oracle_preserves_identity",
        "the primitive itself proves bytes and inode preservation independent of the CLI",
    )
    require(
        checks,
        "create-new race reaches the exact post-revalidation frontier" in cutpoint_test
        and "create-new race preserves the competing creator's exact bytes" in cutpoint_test,
        "competing_creator_race_has_deterministic_oracle",
        "a creator arriving after revalidation wins without being replaced",
    )
    require(
        checks,
        "SyncAtomicFilePublicationOutcome::NotPublished" in cutpoint_test
        and "TemporaryArtifactMayRemain" in cutpoint_test
        and "one sanitized private writer-owned residue" in cutpoint_test,
        "race_failure_reports_exact_outcome_and_residue",
        "recovery can distinguish no namespace effect from writer-owned temp cleanup",
    )
    require(
        checks,
        all(token in prepared_test for token in (
            "preparation creates neither final entry nor temp residue",
            "capability owns bytes independently of caller storage",
            "parent rebind is denied against retained directory authority",
            "replacement parent receives no receipt",
            "displaced pinned parent receives no receipt after denial",
            "rebind denial occurs before any temp reservation",
            "fork child cannot exercise inherited publication authority",
        )),
        "prepared_parent_capability_has_focused_rebind_and_fork_oracles",
        "the concrete historical re-open gap is denied before temp creation in both replacement and inherited-process cases",
    )
    require(
        checks,
        "retained parent directory before temp reservation" in publication
        and ordered(
            publication,
            "void SyncPreparedImmutableJsonPublication::publish_or_throw()",
            "require_sync_process_incarnation_or_fail_stop(",
            "implementation->owner_process_incarnation",
            "prepared immutable JSON publication destination authority",
            "publish_posix_from_retained_directory_or_throw("),
        "prepared_publication_revalidates_retained_authority_before_effect",
        "the post-commit method rejects stale process or parent-path evidence before reserving a temporary inode",
    )

    require(
        checks,
        "add_library(anonsync_sqlite_replay_ledger_reset_receipt_protocol STATIC"
            in cmake
        and "anonsync_sqlite_replay_ledger_reset" in cmake
        and "anonsync_sqlite_replay_ledger_reset_documents" in cmake
        and "anonsync_sync_atomic_file_publication" in cmake
        and "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_RECEIPT_PROTOCOL_SOURCE}"
            in cmake,
        "receipt_protocol_has_a_separate_production_owner",
        "cross-resource sequencing is one focused linked invariant rather than CLI-local choreography",
    )
    require(
        checks,
        "class SqliteReplayLedgerResetReceiptProtocolError final" in protocol_hpp
        and "public std::nested_exception" in protocol_hpp
        and "class SqliteReplayLedgerResetReceiptProtocolErrorAccess final"
            in protocol_internal
        and "invalid sqlite reset/receipt protocol error evidence" in protocol,
        "typed_protocol_error_is_invariant_preserving",
        "only the protocol can construct phase/recovery evidence, inconsistent combinations fail closed, and nested causes survive",
    )

    require(
        checks,
        "add_library(anonsync_sqlite_replay_ledger_reset_documents STATIC" in cmake
        and "${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_DOCUMENTS_SOURCE}" in cmake,
        "documents_have_a_separate_production_owner",
        "canonical evidence projection is not embedded in runner.cpp",
    )
    require(
        checks,
        '"${ANONSYNC_SQLITE_REPLAY_LEDGER_RESET_DOCUMENTS_SOURCE}"' in cmake
        and "invariant-owned persistence boundary must remain outside anonsync_core_lib" in cmake,
        "documents_source_is_excluded_from_core_glob",
        "the focused owner cannot be silently duplicated into the aggregate runtime target",
    )
    require(
        checks,
        "add_executable(anonsync_sqlite_replay_ledger_reset_documents_test" in cmake
        and "add_test(NAME anonsync_sqlite_replay_ledger_reset_documents_test" in cmake,
        "documents_focused_test_is_a_ctest_gate",
        "the canonical-byte contract is independently executable",
    )
    require(
        checks,
        "anonsync_sqlite_replay_ledger_reset_documents_test" in cmake
        and "focused persistence boundary must not depend on anonsync_core_lib" in cmake,
        "documents_test_is_covered_by_no_core_guard",
        "focused proof cannot regress into compiling or linking the full runtime",
    )
    require(
        checks,
        "anonsync_sqlite_replay_ledger_reset_documents" in cmake
        and "ANONSYNC_SANITIZER_COMPILE_TARGETS" in cmake,
        "documents_owner_is_in_sanitizer_inventory",
        "the new production and focused test surfaces participate in sanitizer builds",
    )
    require(
        checks,
        "add_executable(anonsync_sync_atomic_file_publication_prepared_test" in cmake
        and "add_test(NAME anonsync_sync_atomic_file_publication_prepared_test" in cmake
        and "anonsync_sync_atomic_file_publication_prepared_test" in cmake,
        "prepared_publication_oracle_is_in_build_test_and_sanitizer_inventories",
        "the parent-capability regression is a normal focused CTest and cannot silently fall out of hardened builds",
    )
    require(
        checks,
        "anonsync_sqlite_replay_ledger_reset_receipt_source_audit" in cmake
        and "anonsync_sqlite_replay_ledger_reset_receipt_protocol_source_audit" in cmake,
        "receipt_source_audit_is_a_ctest_gate",
        "the cross-file authority contract is enforced on every normal test run",
    )
    require(
        checks,
        all(path in verifier for path in (
            "src/persistence/sqlite_replay_ledger_reset_documents.hpp",
            "src/persistence/sqlite_replay_ledger_reset_documents.cpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp",
            "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp",
            "tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp",
            "tests/sync_atomic_file_publication_prepared_test.cpp",
            "tools/audit_sqlite_replay_ledger_reset_receipt.py",
            "tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py",
        )),
        "release_verifier_requires_receipt_owner_and_proofs",
        "a sealed cube cannot omit the canonical serializer, focused oracle, or structural audit",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-replay-ledger-reset-receipt-audit-v2",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "document_owner_lines": len(docs.splitlines()),
            "document_header_lines": len(docs_hpp.splitlines()),
            "document_test_lines": len(docs_test.splitlines()),
            "protocol_owner_lines": len(protocol.splitlines()),
            "protocol_header_lines": len(protocol_hpp.splitlines()),
            "protocol_frontier_oracle_lines": len(frontier_test.splitlines()),
            "reset_command_lines": len(reset_command.splitlines()),
            "publication_owner_lines": len(publication.splitlines()),
            "prepared_publication_test_lines": len(prepared_test.splitlines()),
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
