#!/usr/bin/env python3
"""Lexical audit for rev0993 request-scoped targeted source access.

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
    Path("REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md"),
    Path("REVISION_NOTES_rev0993.md"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_replica_manifest_reference.py"),
    Path("tools/audit_sync_replica_targeted_source_access.py"),
    Path("tools/audit_sync_file_payload_store.py"),
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
        "format": "anonsync-targeted-source-access-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove POSIX race freedom, advisory-lock "
            "exclusion, SHA-256 security, byte integrity, liveness, memory use, "
            "retention safety, protocol behavior, or multi-terabyte scale"
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
    design = text["REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md"]
    notes = text["REVISION_NOTES_rev0993.md"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    cli = text["src/anonsync_replica.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    manifest_audit = text["tools/audit_sync_replica_manifest_reference.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_replica_targeted_source_access.py"]
    normalized_design = " ".join(design.split())
    normalized_design_lower = normalized_design.lower()
    normalized_notes = " ".join(notes.split())
    normalized_store_h = " ".join(store_h.split())

    session_region = service_h.split(
        "class SyncReplicaReconciliationServeSession final", 1
    )[1].split("enum class SyncReplicaReconciliationApplyDisposition", 1)[0]
    serve_region = service_c.split(
        "SyncReplicaReconciliationService::serve_request_or_throw", 1
    )[1].split(
        "SyncReplicaReconciliationService::apply_response_or_throw", 1
    )[0]

    require(
        "anonsync_sync_replica_targeted_source_access_audit" in cmake
        and "tools/audit_sync_replica_targeted_source_access.py" in cmake,
        "focused_source_audit_is_registered",
        "the rev0993 source-shape audit is part of the ordinary CTest registry",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_tracks_current_content_defined_delta",
        "request-scoped source ownership remains intact after the deliberate content-defined wire generation",
    )
    require(
        "SyncReplicaFilePayloadStoreSnapshot" not in session_region
        and "SyncReplicaFilePayloadStoreTargetedAccess" not in session_region
        and "CachedSourceContentDefinedManifest" not in session_region
        and "SourceContentDefinedProjection" not in session_region
        and "struct CachedSourceContentDefinedManifest final" in service_h
        and "struct SourceContentDefinedProjection final" in service_h,
        "serve_session_retains_only_channel_identity_and_bounded_telemetry",
        "neither a namespace capability nor source manifest acceleration survives in session state",
    )
    require(
        "std::optional<SyncReplicaFilePayloadStoreTargetedAccess>" in serve_region
        and "request_payload_access" in serve_region
        and "request-scoped source payload access" in serve_region
        and "begin_targeted_access_or_throw" in serve_region,
        "payload_access_is_local_to_one_serve_request",
        "one bounded request owns identity/root setup without a session-lifetime capability",
    )
    require(
        "session.payload_targeted_access_->" not in service_c
        and "session.payload_targeted_access_." not in service_c
        and "payload_targeted_access_reuses" not in service_h + service_c,
        "session_scoped_targeted_access_and_misleading_reuse_metric_are_absent",
        "the reviewed correction did not retain the first draft's whole-session live root",
    )
    require(
        "open_optional_payload_for_operation_or_throw" in serve_region
        and "payload_targeted_open_attempts_" in serve_region
        and "payload_targeted_opens_" in serve_region,
        "every_selected_payload_uses_current_exact_name_open",
        "availability is observed at the current request rather than cached behind evidence identity",
    )
    require(
        "PayloadUnavailable" in serve_region
        and "blocked_operation_id =" in serve_region
        and "open_source_payload_or_none" in serve_region,
        "current_exact_absence_is_one_typed_blocked_operation",
        "targeted absence remains bounded scheduling/wire evidence only",
    )
    require(
        "while live it" in normalized_store_h
        and "conservatively roots every current payload for retention planning" in normalized_store_h
        and "source may use it only to return PayloadUnavailable" in normalized_store_h,
        "targeted_access_comment_names_consumers_nonclaim_and_lifetime_cost",
        "future callers are warned that broad capability lifetime affects retention roots",
    )
    require(
        "same live serve session did not observe payload bytes that arrived without an evidence change" in service_test
        and "payload_targeted_access_births() == 2U" in service_test
        and "payload_targeted_open_attempts() == 2U" in service_test
        and "payload_targeted_opens() == 1U" in service_test,
        "same_session_late_payload_regression_removes_stale_negative_cache",
        "payload arrival is visible without reconnect or evidence churn",
    )
    require(
        "test_targeted_source_serving_does_not_claim_namespace_health" in service_test
        and "unrelated-invalid-payload-root-entry" in service_test
        and "refuses unexpected payload-root entry" in service_test,
        "runtime_nonclaim_separates_targeted_serve_from_complete_health_scan",
        "one selected digest can be served while the complete scanner rejects unrelated corruption",
    )
    require(
        "live.targeted_access_count == 0U" in service_test
        and "!live.all_current_payloads_may_be_reopened()" in service_test
        and "source request returned while retaining a namespace-wide payload capability" in service_test,
        "runtime_proves_no_targeted_live_root_after_service_return",
        "network output cannot inherit an all-current-payload retention root",
    )
    require(
        "opened->content_sha256()" in serve_region
        and "opened->size_bytes()" in serve_region
        and "whole targeted payload selection lost exact content identity" in serve_region
        and "opened_payloads.push_back(std::move(*opened))" in serve_region
        and "copy_exact_range_into_or_throw" in serve_region,
        "whole_inline_source_uses_descriptor_streaming_exact_hash",
        "targeted selection preserves exact metadata and complete descriptor fill rehashes bytes before framing",
    )
    require(
        "complete range discovered payload corruption during direct fill" in store_c
        and "retain_process_integrity_fault" in store_c
        and "SyncReplicaFilePayloadStoreIntegrityError" in store_c,
        "complete_targeted_range_records_and_raises_integrity_fault",
        "corrupt source bytes cannot be serialized as a normal reconciliation payload",
    )
    require(
        "offset_bytes > state.metadata.size_bytes" in store_c
        and "state.metadata.size_bytes != 0U" in store_c,
        "exact_empty_payload_is_a_valid_complete_range",
        "zero-byte files retain whole-payload identity without accepting nonempty end offsets",
    )
    require(
        "test_targeted_whole_payload_hashes_before_source_advertisement" in service_test
        and "complete range discovered payload corruption" in service_test
        and "receiver.payload_store_.snapshot_or_throw().entry_count() == 0U" in service_test,
        "whole_payload_corruption_regression_preserves_receiver_state",
        "the new bounded source path fails before bytes or operation evidence reach the receiver",
    )
    require(
        "source_metadata" in service_h + service_c
        and "source_content_defined_manifest_->source_metadata" in service_c
        and "source_content_defined_projection_->source_metadata" in service_c
        and "opened->metadata()" in serve_region
        and "advance_source_content_defined_projection_or_throw" in serve_region
        and "advance_source_content_defined_projection_or_throw" in service_c,
        "manifest_reuse_requires_current_exact_source_observation",
        "service-owned acceleration is not reused across a changed selected inode observation",
    )
    require(
        "payload_targeted_access_births" in tls_h + tls_c
        and "payload_targeted_open_attempts" in tls_h + tls_c
        and "payload_targeted_opens" in tls_h + tls_c,
        "tls_result_preserves_targeted_source_work_accounting",
        "the real framed exchange reports request preflights and exact opens",
    )
    require(
        "reconciliation_payload_targeted_access_births" in cli
        and "reconciliation_payload_targeted_open_attempts" in cli
        and "reconciliation_payload_targeted_opens" in cli,
        "shipping_diagnostic_json_exposes_targeted_source_work",
        "the namespace-scale correction remains observable outside focused tests",
    )
    require(
        "first.serve.payload_targeted_access_births == 1U" in tls_test
        and "first.serve.payload_targeted_open_attempts == 1U" in tls_test
        and "first.serve.payload_targeted_opens == 1U" in tls_test
        and "first.serve.ranged_payload_ranges == 2U" in tls_test,
        "tls_range_regression_observes_one_access_per_request",
        "one grouped network request owns one exact targeted access while carrying two ranges",
    )
    require(
        "source_session.payload_targeted_access_births() == 0U" in service_test
        and "metadata-only source path observed or transferred payload bytes" in service_test,
        "metadata_only_source_path_remains_payload_cold",
        "selective-sync exclusion does not pay even the bounded exact-name access cost",
    )
    require(
        "SyncReplicaFilePayloadStoreSnapshot" not in serve_region
        and "payload_store_.snapshot_or_throw" not in serve_region,
        "source_serve_region_has_no_complete_payload_namespace_scan",
        "the removed O(retained-payload-count) ownership cannot silently return",
    )
    require(
        "payload_snapshot_scans" not in service_h + service_c + tls_h + tls_c + cli
        and "payload_snapshot_reuses" not in service_h + service_c + tls_h + tls_c + cli,
        "old_snapshot_metrics_are_absent_from_active_source_surfaces",
        "new targeted counters are not mislabeled as complete namespace proof",
    )
    require(
        "stale negative" in normalized_design_lower
        and "retention planning" in normalized_design_lower
        and "whole physical payload namespace" in normalized_design_lower,
        "design_records_both_liveness_and_retention_root_defects",
        "the first draft's second-order cost is preserved as an explicit warning",
    )
    require(
        "does not enumerate the payload namespace" in normalized_design
        and "complete snapshot remains the sole namespace-health" in normalized_design
        and "not a measured target-scale RSS claim" in normalized_design,
        "design_states_bounded_authority_and_memory_nonclaim",
        "a point lookup is not promoted into health, capacity, or measured scale authority",
    )
    require(
        "content-defined or multilevel delta" in normalized_notes
        and "generated target-shape measurement" in normalized_notes
        and "Android" in normalized_notes,
        "revision_notes_keep_scale_delta_and_android_work_open",
        "source-memory correction is not presented as product completion",
    )
    require(
        "cache-cold requests require a full manifest" in manifest_audit
        and "receiver_reference_requires_actual_process_cache" in manifest_audit,
        "rev0992_manifest_audit_tracks_current_runtime_wording",
        "the preceding manifest-reference proof remains active after source ownership refactoring",
    )
    require(
        all(token in verifier for token in (
            "REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md",
            "REVISION_NOTES_rev0993.md",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_targeted_source_access.py",
            "tools/audit_sync_file_payload_store.py",
        )),
        "release_verifier_binds_rev0993_authority_chain",
        "the package cannot omit the byte consumer, source owner, runtime proof, records, or audits",
    )
    require(
        "REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md" in structural
        and "rev0993" in structural
        and "anonsync-targeted-source-access-audit-v1" in structural,
        "complete_structural_audit_composes_rev0993",
        "the focused lexical check is not an isolated assurance island",
    )
    require(
        "## Rev0993:" in readme
        and "REV0993 RELEASE CUTPOINT" in bootstrap,
        "visible_release_surfaces_name_rev0993",
        "README and release-root runbook describe the same C++ slice",
    )
    require(
        "VALIDATION_PENDING_REV0993" not in notes
        and "ARCHIVE_PENDING_REV0993" not in notes
        and "CODENAME_PENDING_REV0993" not in notes
        and "VALIDATION_PENDING_REV0993" not in design
        and "ARCHIVE_PENDING_REV0993" not in design
        and "CODENAME_PENDING_REV0993" not in design
        and "VALIDATION_PENDING_REV0993" not in readme
        and "ARCHIVE_PENDING_REV0993" not in readme
        and "VALIDATION_PENDING_REV0993" not in bootstrap
        and "ARCHIVE_PENDING_REV0993" not in bootstrap
        and "CODENAME_PENDING_REV0993" not in bootstrap,
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
