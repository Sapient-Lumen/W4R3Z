#!/usr/bin/env python3
"""Lexical audit for the offline primary-replica replacement boundary.

This source-shape audit is deliberately non-semantic. Runtime, sanitizer,
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
    Path("IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md"),
    Path("REVISION_NOTES_rev0984.md"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_database_backup.hpp"),
    Path("src/sync_replica_database_artifact_internal.hpp"),
    Path("src/sync_replica_database_replacement.hpp"),
    Path("src/sync_replica_database_replacement.cpp"),
    Path("src/sync_replica_database_replacement_receipt_internal.hpp"),
    Path("src/sync_replica_database_replacement_receipt.cpp"),
    Path("src/persistence/sqlite_live_backup.hpp"),
    Path("src/persistence/sqlite_live_backup.cpp"),
    Path("tools/test_anonsync_database_recovery.py"),
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
                return text[start:index + 1]
        index += 1
    return ""


def function_body(text: str, signature: str) -> str:
    return delimited_body(text, signature, "{", "}")


def cmake_call(text: str, prefix: str) -> str:
    return delimited_body(text, prefix, "(", ")")


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-replica-database-replacement-audit-v3",
        "scope": "lexical-hygiene-not-semantic-proof",
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
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1])
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

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8")
            for path in REQUIRED}
    cmake = text["CMakeLists.txt"]
    cli = text["src/anonsync_sync.cpp"]
    backup_header = text["src/sync_replica_database_backup.hpp"]
    helper = text["src/sync_replica_database_artifact_internal.hpp"]
    header = text["src/sync_replica_database_replacement.hpp"]
    source = text["src/sync_replica_database_replacement.cpp"]
    receipt_header = text["src/sync_replica_database_replacement_receipt_internal.hpp"]
    receipt = text["src/sync_replica_database_replacement_receipt.cpp"]
    live_header = text["src/persistence/sqlite_live_backup.hpp"]
    live_source = text["src/persistence/sqlite_live_backup.cpp"]
    process_test = text["tools/test_anonsync_database_recovery.py"]
    readme = text["README.md"]
    design = text["IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md"]
    notes = text["REVISION_NOTES_rev0984.md"]
    verifier = text["tools/verify_release_package.py"]
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    bootstrap = bootstrap_path.read_text(encoding="utf-8") if bootstrap_path.is_file() else ""

    target = cmake_call(cmake, "add_library(anonsync_sync_replica_database_backup STATIC")
    links = cmake_call(cmake, "target_link_libraries(anonsync_sync_replica_database_backup")
    replace = function_body(source, "SyncReplicaDatabaseReplacementOwner::replace_or_resume_or_throw(")
    command = function_body(cli, "int command_database_recovery_replace(")
    optional_artifact = function_body(source, "inspect_existing_artifact_if_present_or_throw(")
    optional_receipt = function_body(receipt, "read_replacement_receipt_if_present_or_throw(")
    absence = function_body(helper, "require_exact_path_absence_or_rethrow(")
    serialize = function_body(receipt, "serialize_receipt(")
    parse = function_body(receipt, "parse_receipt(")
    classifier = function_body(source, "classify_entry_stage_or_throw(")
    required_artifact = function_body(source, "inspect_required_artifact_or_throw(")
    successor_preflight = function_body(
        source, "require_representable_recovery_successor_or_throw(")

    require(
        "class SyncReplicaDatabaseReplacementOwner final" in header
        and "replace_or_resume_or_throw" in header
        and "replace_or_resume_or_throw" not in backup_header,
        "replacement_remains_a_separate_offline_owner",
        "immutable backup creation does not acquire destructive resume authority",
    )
    require(
        all(token in target for token in (
            "sync_replica_database_backup.cpp",
            "sync_replica_database_replacement.cpp",
            "sync_replica_database_replacement_receipt.cpp",
        )) and all(token in links for token in (
            "anonsync_sqlite_live_backup", "anonsync_sha256_digest",
            "anonsync_sync_atomic_file_publication",
            "anonsync_sync_bounded_regular_file",
        )),
        "shipping_graph_retains_receipt_and_shared_owners",
        "the receipt adds no private hashing, file-publication, or SQLite-copy engine",
    )
    require(
        ordered(source, "SyncReplicaDeploymentManifest deployment;",
                "std::string label;", "SyncReplicaPeerServiceSingletonOwner singleton;"),
        "deployment_singleton_precedes_selected_authority",
        "the singleton is acquired during owner construction before artifact opens",
    )
    require(
        'options.require_only(\n        {"manifest", "snapshot", "rollback", "receipt", "expected-current"})'
            in command
        and "replace_or_resume_or_throw" in command
        and "sqlite3_backup" not in command,
        "cli_is_a_strict_receipt_bound_adapter",
        "the executable requires all exact selections and delegates effects to one owner",
    )
    require(
        "anonsync.local-database-recovery-replacement.response.v3" in command
        and all(token in command for token in (
            "replacement_entry_stage", "replacement_receipt_preexisting",
            "replacement_receipt_created_this_invocation",
            "rollback_artifact_published_this_invocation",
            "logical_database_replacement_performed_this_invocation",
            "recovery_epoch_advanced_this_invocation", "idempotent_reproof_only",
            "final_candidate_artifact_path_reproved",
            "final_rollback_artifact_path_reproved",
            "final_artifact_reproof_bracketed_by_database_cutpoint",
            "artifact_pathnames_continuously_reserved\\\":false",
            "noncooperating_same_uid_artifact_replacement_excluded\\\":false",
        )),
        "response_v3_reports_effects_final_path_reproof_and_nonclaims",
        "operators can distinguish effects, durable final observation, and the hostile-local-writer nonclaim",
    )
    require(
        replace.count("validate_artifact_path_or_throw") == 2
        and "require_disjoint_artifact_families_or_throw" in replace
        and "validate_external_receipt_path_or_throw" in replace,
        "candidate_rollback_and_receipt_share_exact_path_admission",
        "all selected external state is validated before capture or publication",
    )
    require(
        "sqlite_artifact_family_paths" in receipt
        and "receipt_path_collides_with_family" in receipt
        and "collides with a selected SQLite artifact family" in receipt,
        "receipt_cannot_occupy_candidate_or_rollback_family_name",
        "the external record is outside deterministic main/journal/WAL/SHM namespaces",
    )
    require(
        "kMaximumReceiptBytes = 8U * 1024U" in receipt
        and "read_sync_bounded_private_regular_file_no_symlink_or_throw" in receipt
        and "write_sync_file_atomically_create_new_no_symlink_or_throw" in receipt,
        "receipt_is_bounded_private_and_create_new",
        "receipt bytes are no-follow, mode-0600, single-link state",
    )
    require(
        all(token in receipt for token in (
            'path:v1\\0"sv', 'action:v1\\0"sv', 'record:v1\\0"sv',
            "static_assert(kReceiptPathDigestDomain.back() == '\\0')",
            "static_assert(kReceiptActionDigestDomain.back() == '\\0')",
            "static_assert(kReceiptRecordDigestDomain.back() == '\\0')",
        )),
        "receipt_digest_domains_bind_explicit_nul_bytes",
        "C++ literal construction cannot silently drop the intended separator",
    )
    require(
        all(token in receipt for token in (
            "deployment_id", "manifest_digest", "manifest_path_sha256",
            "replica_database_path_sha256", "candidate_path_sha256",
            "rollback_path_sha256", "receipt_path_sha256",
            "expected_database_incarnation_sha256",
            "expected_database_recovery_epoch", "expected_cutpoint_digest",
            "append_artifact_fields(output, \"candidate\"",
            "append_artifact_fields(output, \"rollback\"",
        )),
        "action_digest_binds_deployment_selection_and_complete_artifacts",
        "the immutable admission cannot be replayed for another path or cutpoint",
    )
    require(
        ordered(serialize, "kReceiptMagic", "immutable_receipt_fields(receipt)",
                "action_sha256", "kReceiptRecordDigestDomain", "record_sha256")
        and ordered(parse, "record_line_bytes", "kReceiptRecordDigestDomain",
                    "checksum is invalid", "validate_receipt", "encoding is noncanonical"),
        "receipt_has_canonical_action_and_record_integrity",
        "parsing rejects reorder, truncation, trailing fields, checksum drift, and noncanonical encoding",
    )
    require(
        "stage" not in receipt_header.lower()
        and "rewrite" not in receipt_header.lower()
        and "progress_classified_from_active_database" in command
        and "replacement_receipt_effect_authority\\\":false" in command,
        "receipt_is_not_a_mutable_progress_journal",
        "database state, not a receipt stage, classifies restart progress",
    )
    require(
        "require_exact_path_absence_or_rethrow" in optional_artifact
        and "require_exact_path_absence_or_rethrow" in optional_receipt
        and all(token in absence for token in (
            "symlink_status", "no_such_file_or_directory", "file_type::not_found",
            "rethrow_exception",
        )),
        "optional_receipt_and_rollback_share_exact_absence_classifier",
        "only fresh exact absence becomes nullopt; all other failures remain terminal",
    )
    require(
        ordered(replace, "read_replacement_receipt_if_present_or_throw",
                "rollback output preflight", "bounded candidate capture",
                "candidate validation")
        and "receipt_preexisting" in replace,
        "cheap_output_conflicts_precede_large_candidate_capture",
        "deterministic namespace denial does not retain a large database image",
    )
    require(
        ordered(replace, "bounded candidate capture", "candidate validation",
                "capture_displaced_database_or_throw", "publish_replacement_receipt_create_new_or_throw"),
        "candidate_and_displaced_state_are_proved_before_first_effect",
        "no receipt, rollback, or database effect precedes complete source proof",
    )
    require(
        ordered(source, "snapshot before capture", "require_expected_current_or_throw",
                "bounded database capture", "snapshot after capture",
                "database changed across rollback capture"),
        "displaced_capture_is_expected_and_bracketed",
        "the receipt's rollback denotes one exact operator-approved database",
    )
    require(
        all(token in source for token in (
            "candidate and displaced database cutpoints are identical",
            "displaced database is already the candidate's exact recovery",
        )) and "require_unambiguous_restart_states_or_throw" in replace,
        "ambiguous_restart_shapes_are_rejected_before_admission",
        "pre-copy, post-copy, and completed states remain distinguishable",
    )
    require(
        all(token in successor_preflight for token in (
            "database_recovery_epoch", "state_generation",
            "numeric_limits<std::uint64_t>::max()",
            "no representable recovery successor",
        ))
        and ordered(
            replace, "candidate validation",
            "require_representable_recovery_successor_or_throw",
            "bool receipt_created_this_invocation",
            "publish_replacement_receipt_create_new_or_throw",
        ),
        "recovery_successor_overflow_is_rejected_before_durable_admission",
        "an immutable receipt or rollback cannot be created for an action whose mandatory epoch successor is unrepresentable",
    )
    require(
        ordered(replace, "publish_replacement_receipt_create_new_or_throw",
                "rollback output final prepublication reproof",
                "immutable rollback artifact publication")
        and ordered(replace, "pre-database-effect receipt reproof",
                    "active replacement classification"),
        "immutable_receipt_precedes_and_is_reproved_around_effects",
        "admission survives restart without becoming effect authority",
    )
    require(
        ordered(replace, "Receipt-only restart", "capture_displaced_database_or_throw",
                "require_replacement_receipt_artifact_matches_or_throw",
                "resumed rollback artifact publication")
        and "require_expected_current_or_throw" in source,
        "receipt_only_resume_recreates_rollback_only_from_exact_displaced_state",
        "a later database cannot be misrepresented as the original rollback",
    )
    require(
        "Release the resident displaced snapshot" in replace
        and ordered(replace, "immutable rollback artifact publication",
                    "if (!receipt.has_value())", "if (!rollback.has_value())",
                    "durable rollback artifact"),
        "durable_rollback_reopen_does_not_retain_third_complete_image",
        "peak resident complete images remain candidate+displaced or candidate+rollback",
    )
    require(
        all(token in classifier for token in (
            "active == displaced", "active == candidate",
            "recovery_successor_matches(candidate, active)", "continuity is unknown",
        )),
        "active_database_is_the_exact_three_state_restart_classifier",
        "every state outside displaced/candidate/successor fails closed",
    )
    require(
        "replace_sqlite_live_database_bounded_or_throw" in replace
        and "sqlite3_backup_init" not in source
        and "sqlite3_backup_step" not in source
        and "replace_sqlite_live_database_bounded_or_throw" in live_header
        and "ExistingNamedWritable" in live_source,
        "resume_adds_no_second_sqlite_copy_loop",
        "logical replacement remains one profile of the retained bounded owner",
    )
    require(
        ordered(replace, "DisplacedDatabaseCurrent", "replacement source database",
                "replace_sqlite_live_database_bounded_or_throw")
        and "CandidateInstalledEpochPending" in classifier
        and ordered(replace, "expected_writable_entry",
                    "replace_sqlite_live_database_bounded_or_throw",
                    "restored database rooted reproof"),
        "candidate_pending_resume_skips_database_copy",
        "the installed candidate advances lineage without duplicate page transfer",
    )
    require(
        ordered(replace, "restored database differs from the validated candidate",
                "pre-recovery-epoch receipt reproof",
                "advance_database_recovery_epoch_or_throw",
                "post-replacement recovery epoch proof is inconsistent"),
        "epoch_advance_requires_exact_candidate_and_receipt_reproof",
        "lineage cannot advance for a different active database or changed receipt",
    )
    require(
        all(token in required_artifact for token in (
            "SealedSqliteSnapshot::capture",
            "inspect_sealed_artifact_or_throw",
        ))
        and ordered(
            replace,
            "final forensic deployment reproof before artifacts",
            "pre-final-artifact receipt reproof",
            "candidate_seal = {}",
            "rollback->seal = {}",
            "final candidate pathname reproof",
            "final rollback pathname reproof",
            "final immutable receipt reproof",
            "final forensic deployment reproof after artifacts",
        )
        and "final database changed across artifact pathname reproof" in replace
        and "noncooperating same-UID" in replace
        and "idempotent_reproof_only" in replace,
        "success_reopens_named_artifacts_inside_database_cutpoint_bracket",
        "retained resident buffers no longer stand in for candidate and rollback pathnames, while hostile-local-writer exclusion remains explicitly unclaimed",
    )
    require(
        "::rename" not in source and "::unlink" not in source
        and "remove(" not in source
        and "publish_exact_copy_atomically_create_new_or_throw" in source,
        "replacement_does_not_invent_raw_family_swap_or_cleanup",
        "rollback publication is create-new and active replacement remains inside SQLite",
    )
    require(
        all(token in process_test for token in (
            "RECEIPT_ACTION_DOMAIN", "RECEIPT_RECORD_DOMAIN",
            "action digest disagreed with canonical bytes",
            "record digest disagreed with canonical bytes",
        )),
        "process_oracle_independently_recomputes_receipt_digests",
        "production serialization is not its own only oracle",
    )
    require(
        all(token in process_test for token in (
            "damaged replacement receipt", "nonprivate replacement receipt",
            "hardlinked replacement receipt", "changed the active database",
        )),
        "process_oracle_rejects_damaged_nonprivate_and_hardlinked_receipts",
        "invalid external evidence cannot authorize database effects",
    )
    require(
        "completed database replacement replay" in process_test
        and '"idempotent_reproof_only": True' in process_test
        and '"mutation_performed": False' in process_test,
        "process_oracle_proves_mutation_free_completed_replay",
        "repeated operator invocation is safe after exact completion",
    )
    require(
        all(token in process_test for token in (
            "changed candidate artifact pathname",
            "changed rollback artifact pathname",
            "changed candidate artifact altered the active database",
            "changed rollback artifact altered the active database",
            "final candidate pathname replacement race",
            "SIGSTOP",
            "candidate artifact changed",
            "final candidate pathname reproof resume",
        )),
        "process_oracle_rejects_stable_candidate_and_rollback_path_drift",
        "each invocation reopens both selected artifacts instead of trusting an earlier resident seal",
    )
    require(
        "candidate-installed replacement resume" in process_test
        and '"candidate_installed_epoch_pending"' in process_test
        and '"backup_step_calls": 0' in process_test,
        "process_oracle_proves_candidate_pending_resume",
        "the crash cutpoint advances exactly once without another logical copy",
    )
    require(
        "receipt-only database replacement resume" in process_test
        and '"rollback_artifact_published_this_invocation": True' in process_test
        and "receipt-only resume did not restore exact rollback and successor" in process_test,
        "process_oracle_proves_receipt_only_rollback_reconstruction",
        "earliest durable crash resumes from exact displaced bytes",
    )
    require(
        "missing rollback after completed replacement" in process_test
        and "current database expectation is stale" in process_test,
        "receipt_cannot_reconstruct_rollback_from_completed_database",
        "external evidence remains nonauthoritative after active state changes",
    )
    require(
        "unknown replacement continuity" in process_test
        and "continuity is unknown" in process_test
        and "replacement recovery after unknown-state rejection" in process_test,
        "process_oracle_proves_unknown_state_denial_and_later_recovery",
        "fail-closed classification does not poison an admitted future resume",
    )
    require(
        all(token in command for token in (
            'payload_store_replacement_performed\\\":false',
            'other_database_replacement_performed\\\":false',
            'replacement_receipt_effect_authority\\\":false',
            'artifact_pathnames_continuously_reserved\\\":false',
            'noncooperating_same_uid_artifact_replacement_excluded\\\":false',
        )),
        "response_preserves_scope_and_namespace_race_nonclaims",
        "the command cannot be mistaken for complete-share recovery or continuous same-UID pathname reservation",
    )
    final_archive = (
        "AnonSync-rev0984-2026.08.03.12.22-"
        "receiptresume-pathreproof-successorfence-grandidierite.zip"
    )
    require(
        all(token in " ".join(design.split()) for token in (
            "One immutable receipt, not a mutable stage journal",
            "Exact restart classifier", "Executable crash-cutpoint proof",
            "not a signature", "external monotonic counter",
            "noncooperating same-UID", "representable recovery successor",
            "598 checks", final_archive,
        )) and all(token in notes for token in (
            "exact restart classifier", "representable-successor fence",
            "pathname reproof", "536/536", "262/262", final_archive,
        )),
        "design_and_revision_notes_state_the_real_authority_boundary",
        "sealed prose records exact validation, positive guarantees, and explicit nonclaims",
    )
    require(
        "Rev0984: immutable receipt" in readme
        and "REV0984 RELEASE CUTPOINT" in bootstrap
        and "262/262" in readme
        and "262/262" in bootstrap
        and "247/247" in bootstrap
        and final_archive in readme
        and final_archive in bootstrap
        and "VALIDATION_PENDING_REV0984" not in readme
        and "VALIDATION_PENDING_REV0984" not in bootstrap
        and "ARCHIVE_PENDING_REV0984" not in readme
        and "ARCHIVE_PENDING_REV0984" not in bootstrap,
        "operator_and_restart_pages_are_reconciled_for_seal",
        "operator and restart pages bind the exact archive and terminal validation",
    )
    require(
        "revision_number is not None and revision_number >= 983" in verifier
        or "REVISION_NOTES_rev0983.md" not in verifier,
        "release_verifier_can_be_advanced_at_final_seal",
        "package-policy binding remains visible rather than implied",
    )
    require(
        "non-semantic" in __doc__.lower() and "runtime" in __doc__.lower()
        and "package" in __doc__.lower(),
        "lexical_audit_disclaims_semantic_authority",
        "source spelling cannot substitute for executable or package proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
