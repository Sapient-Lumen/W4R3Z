#!/usr/bin/env python3
"""Lexical audit for rev0991 targeted local publication.

This inventories reviewed source and documentation shape. It is lexical hygiene,
not semantic proof. Compiler, sanitizer, runtime, stress, reconstruction, and
package evidence remain load-bearing.
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
    Path("TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md"),
    Path("REVISION_NOTES_rev0991.md"),
    Path("src/sync_replica_digest_accumulator.hpp"),
    Path("src/sync_replica_digest_accumulator.cpp"),
    Path("src/sync_replica_model.hpp"),
    Path("src/sync_replica_model.cpp"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("tests/sync_replica_hash_graph_projection_test.cpp"),
    Path("tests/sync_replica_prepared_publication_test.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tools/audit_sync_replica_targeted_local_publication.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def delimited_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-targeted-local-publication-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SQLite transaction isolation, "
            "query complexity, collision resistance, allocator behavior, "
            "race freedom, crash recovery, or target-scale memory"
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
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md"]
    notes = text["REVISION_NOTES_rev0991.md"]
    acc_h = text["src/sync_replica_digest_accumulator.hpp"]
    acc_c = text["src/sync_replica_digest_accumulator.cpp"]
    model_h = text["src/sync_replica_model.hpp"]
    model_c = text["src/sync_replica_model.cpp"]
    sqlite_h = text["src/sync_replica_sqlite_owner.hpp"]
    sqlite_c = text["src/sync_replica_sqlite_owner.cpp"]
    hash_test = text["tests/sync_replica_hash_graph_projection_test.cpp"]
    prepared_test = text["tests/sync_replica_prepared_publication_test.cpp"]
    sqlite_test = text["tests/sync_replica_sqlite_owner_test.cpp"]
    verifier = text["tools/verify_release_package.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    self_text = text["tools/audit_sync_replica_targeted_local_publication.py"]

    prepare = delimited_body(sqlite_c, "SyncReplicaSqliteOwner::prepare_local_file_from_observed_heads_or_throw(")
    commit = delimited_body(sqlite_c, "SyncReplicaSqliteOwner::commit_prepared_local_file_or_throw(")
    advance = delimited_body(sqlite_c, "advance_meta_for_targeted_local_publication_or_throw(")
    publication_cutpoint = delimited_body(
        sqlite_c, "local_publication_cutpoint_base_digest_or_throw("
    )
    normalized_design = " ".join(design.split())
    normalized_notes = " ".join(notes.split())

    require(
        "src/sync_replica_digest_accumulator.cpp" in cmake,
        "accumulator_source_is_in_replica_model_build",
        "the fixed-width witness implementation is linked into the retained model",
    )
    require(
        "anonsync_sync_replica_targeted_local_publication_source_audit" in cmake
        and "tools/audit_sync_replica_targeted_local_publication.py" in cmake,
        "focused_audit_is_registered",
        "the rev0991 audit runs through ordinary CTest registration",
    )
    require(
        all(name in acc_h for name in (
            "sync_replica_digest_accumulator_zero",
            "sync_replica_digest_accumulator_add_or_throw",
            "sync_replica_digest_accumulator_subtract_or_throw",
        )),
        "accumulator_api_is_small_and_explicit",
        "only zero, add, and subtract are public",
    )
    require(
        "using Words = std::array<std::uint64_t, 4U>;" in acc_c
        and "parse_words_or_throw" in acc_c
        and "encode_words" in acc_c
        and "carry" in acc_c
        and "borrow" in acc_c,
        "accumulator_uses_fixed_four_limb_canonical_arithmetic",
        "modulo-2^256 updates neither allocate a bigint nor accept noncanonical input",
    )
    require(
        "unkeyed" in acc_h and "structural witness" in acc_h
        and "not authentication authority" in acc_h,
        "accumulator_header_disclaims_authentication_authority",
        "the additive witness cannot be mistaken for an authenticated commitment",
    )
    require(
        "make_sync_replica_local_operation_from_causal_heads_or_throw" in model_h
        and "active causal frontier" in model_h
        and "sync_replica_active_operation_accumulator_element_digest_or_throw" in model_h
        and "sync_replica_visible_path_accumulator_element_digest_or_throw" in model_h,
        "model_exposes_shared_causal_derivation_and_domain_separated_elements",
        "SQLite and the reference model share operation construction and witness encoding",
    )
    require(
        "constexpr std::uint64_t kVisiblePathSchemaVersion = 8U" in sqlite_c
        and "constexpr std::uint64_t kSchemaVersion = 9U" in sqlite_c
        and "sync_replica_operation_paths" in sqlite_c
        and "sync_replica_operation_paths_path" in sqlite_c
        and "visible_path_count_be" in sqlite_c
        and "sync_replica_visible_file_content" in sqlite_c,
        "schema_v9_preserves_path_index_and_adds_content_index",
        "same-path history, counted visibility, and bounded content lookup are durable schema facts",
    )
    require(
        all(token in sqlite_c for token in (
            "kLegacySchemaVersion = 1U",
            "kPreviousSchemaVersion = 2U",
            "kClockSchemaVersion = 3U",
            "kRetryProvenanceSchemaVersion = 4U",
            "kRetentionRootSchemaVersion = 5U",
            "kHistoricalPinSchemaVersion = 6U",
            "kDatabaseLineageSchemaVersion = 7U",
            "kVisiblePathSchemaVersion = 8U",
        )) and sqlite_c.count("migrate_prior_schema_or_throw(") >= 9,
        "every_released_schema_migrates_through_complete_rebuild",
        "v1-v8 remain explicit migration sources for schema v9",
    )
    require(
        "model.operation_set_accumulator_digest()" in sqlite_c
        and "model.evidence_set_accumulator_digest()" in sqlite_c
        and "model.visible_state_accumulator_digest()" in sqlite_c
        and "model.visible_path_count()" in sqlite_c
        and "durable model metadata mismatch" in sqlite_c,
        "complete_snapshot_recomputes_all_counted_witnesses",
        "incremental metadata is checked against complete canonical reconstruction",
    )
    require(
        "read_targeted_path_history_cutpoint_or_throw" in sqlite_c
        and "FROM main.sync_replica_operation_paths AS p" in sqlite_c
        and "canonical_path=?" in sqlite_c,
        "target_history_query_uses_canonical_path_index",
        "the normal publication path does not scan unrelated retained operations",
    )
    require(
        "read_active_causal_head_operations_or_throw" in sqlite_c
        and "active causal frontier" in model_c,
        "operation_derivation_reads_exact_active_causal_heads",
        "the local context remains causally complete rather than path-only",
    )
    require(
        "meta.policy_generation" in publication_cutpoint
        and "meta.local_operation_digest" in publication_cutpoint
        and "path_history.digest" in publication_cutpoint
        and "visible_operation_ids" in publication_cutpoint
        and "state_generation" not in publication_cutpoint
        and "operation_set_digest" not in publication_cutpoint
        and "evidence_set_digest" not in publication_cutpoint
        and "visible_state_digest" not in publication_cutpoint,
        "publication_cutpoint_excludes_unrelated_global_generation",
        "local chain, policy, path history, and heads bind authority while unrelated liveness may advance",
    )
    require(
        "SyncSqliteTransactionMode::Deferred" in prepare
        and "read_targeted_visible_path_or_throw" in prepare
        and "read_targeted_path_history_cutpoint_or_throw" in prepare
        and "read_active_causal_head_operations_or_throw" in prepare
        and "load_state_or_throw" not in prepare,
        "prepare_is_targeted_and_read_only",
        "preparation performs prospective arithmetic without rebuilding or mutating the complete model",
    )
    require(
        "SyncSqliteTransactionMode::Immediate" in commit
        and "require_no_temporary_triggers_or_throw" in commit
        and "read_targeted_visible_path_or_throw" in commit
        and "read_targeted_path_history_cutpoint_or_throw" in commit
        and "load_state_or_throw" not in commit[:commit.find("has_retained_child_reference_or_throw")],
        "commit_reproves_targeted_authority_before_effect",
        "schema, TEMP trigger, same-path, and prepared-operation fences precede incremental publication",
    )
    require(
        "has_retained_child_reference_or_throw" in commit
        and "load_state_or_throw" in commit
        and "fallback" in commit,
        "reverse_dependency_uses_explicit_complete_model_fallback",
        "rare cross-path activation preserves global evidence semantics",
    )
    require(
        "sync_replica_digest_accumulator_add_or_throw" in advance
        and "sync_replica_digest_accumulator_subtract_or_throw" in advance
        and "visible_path_count" in advance
        and "local_operation_chain_advance_or_throw" in advance,
        "incremental_meta_updates_counts_witnesses_and_local_chain",
        "the staged metadata transition accounts for insertions and visible-path replacement",
    )
    require(
        "kUnrelatedHistory = 192U" in prepared_test
        and "complete_operation_projection_rows == 0U" in prepared_test
        and "complete_visible_projection_rows == 0U" in prepared_test
        and "complete_operation_projection_statements == 0U" in prepared_test
        and "FROM main.sync_replica_operation_paths AS p" in prepared_test,
        "runtime_trace_proves_unrelated_history_independent_query_shape",
        "192 unrelated rows do not trigger complete operation or visible projections",
    )
    require(
        "StaleCutpoint" in prepared_test
        and "reverse-dependency" in prepared_test
        and "TEMP triggers exist" in prepared_test,
        "runtime_oracle_covers_staleness_fallback_and_temp_schema",
        "same-path drift fails, rare dependency activates, and executable TEMP schema is rejected",
    )
    require(
        "test_quarantined_local_retry_fails_closed" in prepared_test
        and "retained operation no longer carries active local minting authority" in sqlite_c
        and "evidence_state != SyncReplicaEvidenceState::Active" in commit
        and "local_actor_compromised" in commit,
        "idempotent_retry_requires_active_uncompromised_authority",
        "a same-dot fork cannot turn quarantined evidence into AlreadyPublished success",
    )
    require(
        "exact modulo-2^256 carry and borrow" in hash_test,
        "accumulator_wrap_and_borrow_are_runtime_tested",
        "the four-limb arithmetic crosses the 256-bit boundary exactly",
    )
    require(
        "test_exact_v8_migration_builds_visible_content_index" in sqlite_test
        and "schema-v9" in sqlite_test.lower()
        and "v8 migration did not rebuild the exact visible-content index" in sqlite_test,
        "schema_v9_runtime_migration_coverage_is_present",
        "the SQLite owner regression exercises exact v8-to-v9 content-index migration",
    )
    require(
        "81,920,000 prior operation-row decodes" in normalized_design
        and "O(history-of-that-path + active causal heads)" in normalized_design
        and "not constant memory" in normalized_design
        and "not a cryptographic set commitment" in normalized_design,
        "design_quantifies_scale_gain_and_nonclaims",
        "the release record names both the removed multiplier and remaining bounds",
    )
    require(
        "No rev0990 archive is part of release lineage." in normalized_design
        and "No rev0990 archive is part of release lineage" in normalized_notes,
        "missing_rev0990_is_not_invented_as_lineage",
        "rev0991 descends from the last independently available sealed parent",
    )
    require(
        all(token in verifier for token in (
            "TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md",
            "REVISION_NOTES_rev0991.md",
            "src/sync_replica_digest_accumulator.hpp",
            "src/sync_replica_digest_accumulator.cpp",
            "tests/sync_replica_prepared_publication_test.cpp",
            "tools/audit_sync_replica_targeted_local_publication.py",
            "tools/audit_sync_file_payload_store.py",
        )),
        "release_verifier_binds_rev0991_authority_chain",
        "the package cannot omit implementation, tests, records, or audits",
    )
    require(
        "## Rev0991:" in readme
        and "REV0991 RELEASE CUTPOINT" in bootstrap
        and "spessartine" in bootstrap,
        "visible_release_surfaces_name_rev0991",
        "README and release-root runbook describe the same C++ slice",
    )
    require(
        "TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md" in structural
        and "rev0991" in structural,
        "complete_structural_audit_composes_rev0991",
        "the focused lexical check is not an isolated assurance island",
    )
    require(
        "VALIDATION_PENDING_REV0991" not in notes
        and "ARCHIVE_PENDING_REV0991" not in notes
        and "VALIDATION_PENDING_REV0991" not in design
        and "ARCHIVE_PENDING_REV0991" not in design
        and "VALIDATION_PENDING_REV0991" not in readme
        and "ARCHIVE_PENDING_REV0991" not in readme
        and "VALIDATION_PENDING_REV0991" not in bootstrap
        and "ARCHIVE_PENDING_REV0991" not in bootstrap,
        "final_release_placeholders_are_sealed",
        "validation and archive identity must be concrete before release",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not semantic proof" in self_text
        and "Compiler, sanitizer, runtime, stress, reconstruction, and\npackage evidence" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "source spelling cannot replace executable and package proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
