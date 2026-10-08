#!/usr/bin/env python3
"""Lexical audit for rev0987 bounded selective synchronization.

This audit checks reviewed source shape and product claims. It is not semantic
proof. Compiler, sanitizer, runtime, stress, reconstruction, and package
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
    Path("BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md"),
    Path("REVISION_NOTES_rev0987.md"),
    Path("src/anonsync_folder.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("src/sync_replica_selective_sync_policy.hpp"),
    Path("src/sync_replica_selective_sync_policy.cpp"),
    Path("src/sync_replica_folder_observer.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("tests/sync_replica_selective_sync_policy_test.cpp"),
    Path("tests/sync_atomic_file_publication_unlink_authority_test.cpp"),
    Path("tests/sync_replica_folder_scan_owner_test.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/test_anonsync_folder_cli.py"),
    Path("tools/audit_sync_replica_selective_sync.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-selective-sync-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove POSIX identity, race freedom, "
            "allocation behavior, durability, crash recovery, performance, "
            "privacy, target-scale memory, or Android"
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
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md"]
    notes = text["REVISION_NOTES_rev0987.md"]
    policy_h = text["src/sync_replica_selective_sync_policy.hpp"]
    policy_c = text["src/sync_replica_selective_sync_policy.cpp"]
    observer = text["src/sync_replica_folder_observer.cpp"]
    folder_h = text["src/sync_replica_folder_scan_owner.hpp"]
    folder_c = text["src/sync_replica_folder_scan_owner.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    folder_cli = text["src/anonsync_folder.cpp"]
    atomic_h = text["src/sync_atomic_file_publication.hpp"]
    atomic_c = text["src/sync_atomic_file_publication.cpp"]
    policy_test = text["tests/sync_replica_selective_sync_policy_test.cpp"]
    unlink_test = text["tests/sync_atomic_file_publication_unlink_authority_test.cpp"]
    folder_test = text["tests/sync_replica_folder_scan_owner_test.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    process_test = text["tools/test_anonsync_folder_cli.py"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_replica_selective_sync.py"]
    sanitizer_compile_start = cmake.find(
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS"
    )
    sanitizer_compile_end = cmake.find(
        "foreach(tgt IN LISTS ANONSYNC_SANITIZER_COMPILE_TARGETS)",
        sanitizer_compile_start,
    )
    sanitizer_link_start = cmake.find(
        "foreach(tgt\n      anonsync_core", sanitizer_compile_end
    )
    sanitizer_link_end = cmake.find(
        "target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)",
        sanitizer_link_start,
    )
    sanitizer_compile_inventory = (
        cmake[sanitizer_compile_start:sanitizer_compile_end]
        if sanitizer_compile_start >= 0 and sanitizer_compile_end >= 0
        else ""
    )
    sanitizer_link_inventory = (
        cmake[sanitizer_link_start:sanitizer_link_end]
        if sanitizer_link_start >= 0 and sanitizer_link_end >= 0
        else ""
    )

    require(
        "anonsync_sync_replica_selective_sync_source_audit" in cmake
        and "tools/audit_sync_replica_selective_sync.py" in cmake,
        "focused_source_audit_is_registered",
        "the rev0987 source-shape audit is in the ordinary CTest registry",
    )
    require(
        "kSyncReplicaSelectiveSyncMaximumRules = 1024U" in policy_h
        and "48ULL * 1024ULL" in policy_h,
        "policy_has_1024_rule_and_48_kib_path_frontiers",
        "selection authority is bounded independently of tree size",
    )
    require(
        "longest-component-prefix" in policy_h
        or "Longest matching canonical component prefix" in policy_h,
        "policy_names_longest_component_prefix_semantics",
        "selection does not use raw byte-prefix ambiguity",
    )
    require(
        "anonsync:sync-replica-selective-sync-policy:v1" in policy_c
        and "append_u64(canonical, generation)" in policy_c
        and "append_framed(canonical, rule.canonical_path)" in policy_c,
        "policy_digest_binds_generation_default_and_rules",
        "durable replay and wire selection use one canonical identity",
    )
    require(
        "sync_replica_selective_sync_policy_materializes_new_paths" in policy_h
        and "finite union" in policy_c
        and "before.default_mode" in policy_c,
        "expansion_decision_uses_finite_policy_boundaries",
        "policy mutation does not walk the synchronized namespace",
    )
    require(
        "path_is_less_than_descendant_prefix" in policy_c
        and "virtual key `directory/`" in policy_c
        and "path[canonical_directory.size()]" in policy_c,
        "allocation_free_directory_prefix_lower_bound_is_lexically_exact",
        "unrelated siblings cannot hide a deeper selected descendant",
    )
    require(
        "const std::string prefix = canonical_directory" not in policy_c,
        "directory_pruning_does_not_allocate_prefix_string",
        "ordinary traversal selection avoids one allocation per directory",
    )
    require(
        "lexically earlier sibling hid a deeper materialized descendant" in policy_test
        and '"a-archive"' in policy_test
        and '"a/keep"' in policy_test,
        "adversarial_virtual_slash_ordering_has_runtime_regression",
        "the adjacent lexical bug is bound by an executable oracle",
    )
    require(
        "prove_materialization_expansion_classifier_exhaustively" in policy_test
        and "policies.reserve(486U)" in policy_test
        and "compared_pairs == 486U * 486U" in policy_test,
        "bounded_policy_expansion_classifier_has_exhaustive_runtime_oracle",
        "all policies over the focused nested-boundary basis are compared pairwise",
    )
    require(
        "kSelectiveSyncSchemaVersion = 6U" in folder_c
        and "kSchemaVersion = 7U" in folder_c
        and "CHECK(schema_version=6)" in folder_c
        and "CHECK(schema_version=7)" in folder_c
        and "sync_replica_folder_catalog_selection_rules" in folder_c,
        "folder_catalog_schema_v7_preserves_selection_policy",
        "the exact v6 selection schema migrates into v7 without losing durable policy",
    )
    require(
        "expected_rule_count > kSyncReplicaSelectiveSyncMaximumRules" in folder_c
        and "kSyncReplicaSelectiveSyncMaximumRulePathBytes" in folder_c,
        "catalog_loader_enforces_policy_count_and_path_byte_bounds",
        "damaged or oversized durable policy state fails closed",
    )
    require(
        "sync_replica_selective_sync_policy_materializes_new_paths" in folder_c
        and "successor_absence_fence_generation" in folder_c,
        "absence_fence_opens_only_for_genuine_expansion",
        "pure exclusion does not globally stall unrelated deletion repair",
    )
    require(
        "current.absence_inference_fence_generation != 0U" in folder_c,
        "active_expansion_fence_survives_later_policy_edits",
        "a follow-on edit cannot erase unfinished absence uncertainty",
    )
    require(
        "pure selective-sync exclusion opened a global absence fence" in folder_test
        and "pure exclusion delayed an unrelated selected-path deletion" in folder_test,
        "narrowing_and_unrelated_deletion_have_regressions",
        "the multi-tree liveness correction is executable",
    )
    require(
        "sync_replica_selective_sync_directory_may_contain_materialized_path" in observer
        and "continue;" in observer,
        "observer_prunes_fully_metadata_only_directories",
        "excluded subtrees are skipped before recursive enumeration",
    )
    require(
        "sync_replica_selective_sync_path_is_materialized" in observer
        and "regular_files" in observer,
        "observer_filters_metadata_only_regular_files",
        "excluded local absence cannot become a local file observation",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "reconciliation-request-frame-v9" in protocol_c
        and "reconciliation-response-frame-v9" in protocol_c,
        "protocol_generation_and_digest_domains_advance_together",
        "older frames cannot be accepted under selective-sync and manifest-reference semantics",
    )
    require(
        "SyncReplicaSelectiveSyncPolicy selective_sync_policy" in protocol_h
        and "request.selective_sync_policy.generation" in protocol_c
        and "request.selective_sync_policy.policy_digest" in protocol_c,
        "request_frame_binds_complete_requester_policy",
        "serving omission is determined by authenticated canonical request state",
    )
    require(
        "metadata_only_file_operation_ids" in protocol_h
        and "expected_metadata_only_operation_ids" in protocol_c
        and "metadata_only_operation_ids.contains" in protocol_c,
        "response_explicitly_and_exactly_marks_omitted_file_payloads",
        "metadata-only operations cannot be inferred from missing bytes alone",
    )
    require(
        "metadata-only operation unexpectedly carries payload bytes" in protocol_c
        or "metadata-only" in protocol_c,
        "protocol_rejects_payload_for_metadata_only_operation",
        "wire omission and metadata admission cannot disagree silently",
    )
    require(
        "metadata_only_file_operations" in service_h
        and "response.metadata_only_file_operation_ids" in service_c
        and "result.metadata_only_file_operations" in service_c,
        "service_admits_and_accounts_metadata_only_operations",
        "shipping reconciliation does not need a second metadata engine",
    )
    require(
        "metadata_only_file_operations" in tls_c
        and "metadata_only_file_operations" in sync_cli,
        "tls_and_shipping_json_expose_metadata_only_work",
        "operators can distinguish causal progress from payload transfer",
    )
    require(
        "selective-sync-status" in sync_cli
        and "selective-sync-set" in sync_cli
        and "service_must_be_stopped" in sync_cli,
        "owner_cli_exposes_offline_policy_inspection_and_replacement",
        "policy mutation has one explicit service-stop boundary",
    )
    require(
        "deployment_singleton_acquired" in sync_cli
        and "payload_store_observed" in sync_cli
        and "rooted_files_observed" in sync_cli
        and "replica_database_observed" in sync_cli,
        "policy_cli_reports_its_narrow_authority_surface",
        "offline policy control does not pretend to observe unrelated stores",
    )
    require(
        "RemoteApplyCandidateKind::DematerializeMetadataOnlyFile" in folder_c
        and "remove_sync_file_atomically_if_expected_content_under_directory_or_throw" in folder_c,
        "metadata_only_policy_has_rooted_dematerialization_effect",
        "already materialized selected bytes do not remain forever by accident",
    )
    require(
        "remove_sync_file_atomically_if_expected_content_under_directory_or_throw" in atomic_h
        and "hash_exact_regular_file_descriptor_or_throw" in atomic_c
        and "displaced content proof" in atomic_c
        and "same_regular_file_stat_observation" in atomic_c,
        "dematerialization_rehashes_exact_private_displaced_inode",
        "the last destructive cutpoint depends on complete bytes, not metadata alone",
    )
    require(
        "preserve_displaced_and_throw" in atomic_c
        and "displaced_name_present" in atomic_c
        and "restored and not removed" in atomic_c,
        "failed_private_content_proof_preserves_displaced_object",
        "pre-unlink observation and digest failures do not become deletion authority",
    )
    require(
        "private recovery residue" in design
        and "no automatic residue recovery" in design
        and "second complete read" in design,
        "dematerialization_crash_and_io_nonclaims_are_explicit",
        "the first destructive slice does not hide its residue or duplicate-read cost",
    )
    require(
        "observation_matches_catalog_entry" in folder_c
        and "require_catalog_operation_or_throw" in folder_c
        and "require_sole_visible_file_operation_or_throw" in folder_c,
        "dematerialization_requires_catalog_and_causal_evidence",
        "untracked, changed, and conflict paths cannot be removed as policy effects",
    )
    require(
        "retained_private_payload" in folder_c
        and "open_optional_payload_for_operation_or_throw" in folder_c
        and "BlockedPayloadUnavailable" in folder_c,
        "dematerialization_retains_verified_private_predecessor_copy",
        "the synchronized root's only proved copy is never intentionally removed",
    )
    require(
        "metadata-only private payload selection changed identity" in folder_c
        and "metadata-only post-removal rooted inspection" in folder_c
        and "post-unlink reproof" in folder_c,
        "dematerialization_reproves_private_payload_root_and_authority",
        "unlink is bracketed by exact current observations",
    )
    require(
        "remote_metadata_only_dematerialization_blocked_file_count" in folder_h
        and "remote_metadata_only_dematerialization_payload_unavailable_count" in folder_h
        and "remote_metadata_only_dematerialized_bytes" in folder_h,
        "dematerialization_outcomes_are_bounded_and_observable",
        "blocked safety cases are not reported as settled policy",
    )
    require(
        "prepared file selective-sync authority changed" in folder_c
        and "selective_sync_policy_generation" in folder_c,
        "prepared_local_file_is_bound_to_selection_cutpoint",
        "a stale scan cannot publish after narrowing",
    )
    require(
        "apply target is metadata-only under the current " in folder_c
        and "selective-sync materialization authority changed before " in folder_c
        and "remote apply publication" in folder_c,
        "direct_remote_apply_rejects_and_reproves_selection",
        "payload and rooted publication do not outlive policy authority",
    )
    require(
        "historical-version restore path is metadata-only under the " in folder_c
        and "historical-version restore catalog or selective-sync " in folder_c
        and "authority changed before publication" in folder_c,
        "historical_restore_obeys_current_selection",
        "restore is not a backdoor that rematerializes excluded paths",
    )
    require(
        "selection_rehydration_fence_active" in folder_c
        and "causal successor without requiring" in folder_c
        and "selective-sync successor fixture" in folder_test,
        "expansion_fence_allows_exact_causal_successor_rehydration",
        "an excluded path can advance remotely before later acquisition",
    )
    require(
        "remote_metadata_only_dematerialization_attempt_count" in folder_test
        and "private predecessor payload" in folder_test
        and "did not dematerialize its predecessor" in folder_test,
        "dematerialization_and_only_copy_safety_have_runtime_regressions",
        "the physical policy effect is tested through real owners",
    )
    require(
        "test_selective_sync_dematerialization_preserves_changed_and_untracked_files" in folder_test
        and "operator-owned untracked bytes" in folder_test
        and "locally changed media bytes" in folder_test,
        "changed_and_untracked_rooted_bytes_have_preservation_regressions",
        "metadata-only policy cannot silently delete operator-owned divergence",
    )
    require(
        "test_selective_sync_dematerialization_obeys_remote_effect_frontier" in folder_test
        and "maximum_remote_apply_operations = 1U" in folder_test
        and "metadata-only dematerialization escaped its bounded remote-effect frontier" in folder_test,
        "dematerialization_uses_existing_bounded_remote_effect_frontier",
        "large narrowing operations resume instead of becoming one unbounded deletion turn",
    )
    require(
        "content-bound conditional-removal mismatch" in unlink_test
        and "SHA-256 did not match" in unlink_test
        and "restores the exact displaced object without unlink" in unlink_test,
        "private_inode_digest_mismatch_has_direct_restoration_regression",
        "the atomic removal primitive itself is tested independently of folder policy",
    )
    require(
        "metadata_only_file_operations == 1U" in service_test
        and "metadata_only_file_operations" in tls_test,
        "service_and_tls_regressions_prove_payload_omission",
        "metadata convergence without bytes is exercised across the wire seam",
    )
    require(
        "selective-sync-status" in process_test
        and "selective-sync-set" in process_test
        and "pure exclusion opened a durable selective-sync absence fence" in process_test,
        "configured_folder_process_oracle_covers_durable_policy_control",
        "the shipping commands, SQLite state, and expansion semantics are composed",
    )
    require(
        "remote_metadata_only_dematerialization_attempt_count" in sync_cli
        and "remote_metadata_only_dematerialization_attempt_count" in folder_cli,
        "both_shipping_convergence_json_surfaces_expose_dematerialization",
        "low-level and configured operation diagnostics remain aligned",
    )
    require(
        "reclaims synchronized-root space" in design
        and "not total AnonSync storage" in design
        and "no filesystem placeholders" in notes,
        "documentation_does_not_overclaim_eviction_or_placeholders",
        "private payload retention and missing UI remain explicit",
    )
    require(
        "multi-terabyte" in design.lower()
        and "target-scale" in design.lower()
        and "Android" in design,
        "documentation_preserves_scale_and_android_nonclaims",
        "bounded source shape is not mislabeled as workload qualification",
    )
    require(
        "rev0987" in readme.lower()
        and "selective" in bootstrap.lower(),
        "visible_product_pages_name_the_current_slice",
        "restart context does not continue to describe selective sync as absent",
    )
    require(
        "anonsync_sync_replica_selective_sync_policy_test"
        in sanitizer_compile_inventory
        and "anonsync_sync_replica_selective_sync_policy_test"
        in sanitizer_link_inventory,
        "selective_policy_test_has_compile_and_final_link_sanitizers",
        "the new product test cannot compile instrumented dependencies and then fail at an uninstrumented final-link frontier",
    )
    require(
        "BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md" in verifier
        and "REVISION_NOTES_rev0987.md" in verifier
        and "audit_sync_replica_selective_sync.py" in verifier,
        "release_verifier_requires_rev0987_owners_tests_audit_and_records",
        "a package cannot omit the selective-sync authority chain",
    )
    require(
        "VALIDATION_PENDING_REV0987" not in notes
        and "ARCHIVE_PENDING_REV0987" not in notes
        and "VALIDATION_PENDING_REV0987" not in readme
        and "ARCHIVE_PENDING_REV0987" not in readme
        and "VALIDATION_PENDING_REV0987" not in bootstrap
        and "ARCHIVE_PENDING_REV0987" not in bootstrap,
        "final_validation_and_archive_identity_are_sealed",
        "the audit remains deliberately gated until exact validation and package identity are final",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not semantic" in self_text
        and "Compiler, sanitizer, runtime, stress, reconstruction, and package" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "a passing spelling scan cannot replace runtime or release proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
