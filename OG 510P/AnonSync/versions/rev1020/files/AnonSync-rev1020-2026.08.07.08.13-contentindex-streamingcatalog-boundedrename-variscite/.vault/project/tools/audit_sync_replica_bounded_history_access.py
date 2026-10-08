#!/usr/bin/env python3
"""Lexical hygiene audit for rev0999 bounded reconciliation history access.

This audit binds reviewed source shape and release vocabulary. It is not a
semantic, transaction, performance, query-plan, lifetime, sanitizer, or package
proof. Runtime SQL traces, C++ tests, compiler/sanitizer evidence, and package
verification remain load-bearing.
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
    Path("BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md"),
    Path("REVISION_NOTES_rev0999.md"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tools/audit_sync_replica_bounded_history_access.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start + len(signature))
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


def last_function_body(text: str, signature: str) -> str:
    start = text.rfind(signature)
    if start < 0:
        return ""
    return function_body(text[start:], signature)


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-bounded-reconciliation-history-access-audit-v1",
        "scope": "lexical-hygiene-not-semantic-or-query-plan-proof",
        "scope_nonclaim": (
            "source spelling does not prove transaction isolation, SQLite query "
            "plans, bounded runtime work, causal correctness, lifetime safety, "
            "same-UID hostility resistance, sanitizer cleanliness, or package identity"
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
    design = text["BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md"]
    notes = text["REVISION_NOTES_rev0999.md"]
    owner_h = text["src/sync_replica_sqlite_owner.hpp"]
    owner_c = text["src/sync_replica_sqlite_owner.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    owner_test = text["tests/sync_replica_sqlite_owner_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_bounded_history_access_source_audit" in cmake
        and "tools/audit_sync_replica_bounded_history_access.py" in cmake,
        "focused_audit_is_registered",
        "the rev0999 source-shape audit is in the ordinary CTest registry",
    )
    require(
        "struct SyncReplicaSqliteIdentityCutpoint final" in owner_h
        and "database_incarnation_sha256" in owner_h
        and "database_recovery_epoch" in owner_h
        and "identity_cutpoint_or_throw" in owner_h,
        "fixed_identity_cutpoint_is_public_and_lineage_bound",
        "bounded service turns can re-prove owner identity without a complete snapshot",
    )
    identity = function_body(owner_c, "SyncReplicaSqliteOwner::identity_cutpoint_or_throw")
    require(
        "read_current_owner_meta_or_throw" in identity
        and "SyncSqliteTransactionMode::Deferred" in identity
        and "require_snapshot_authority_or_throw" in identity
        and "load_state_or_throw" not in identity
        and "sync_replica_operations" not in identity
        and "sync_replica_visible" not in identity,
        "identity_cutpoint_is_metadata_only_and_snapshot_pinned",
        "the fixed cutpoint cannot silently reconstruct retained history",
    )
    require(
        "read_current_owner_meta_or_throw" in owner_c
        and owner_c.count("read_current_owner_meta_or_throw(") >= 4,
        "current_owner_metadata_reproof_is_centralized",
        "identity, path, and evidence readers share one exact schema/meta boundary",
    )
    page = function_body(owner_c, "SyncReplicaSqliteOwner::evidence_page_or_throw")
    require(
        "WHERE operation_id>?" in page
        and "ORDER BY operation_id LIMIT ?" in page
        and "evidence page lookahead limit" in page
        and "load_stored_operation_row_or_throw" in page,
        "evidence_page_uses_bounded_primary_key_range",
        "one page plus one lookahead is decoded in canonical operation-ID order",
    )
    require(
        "load_state_or_throw" not in page
        and "all_evidence_operations" not in page
        and "std::sort" not in page
        and "snapshot_or_throw" not in page,
        "evidence_page_does_not_reconstruct_or_sort_history",
        "page cost is independent of retained-history cardinality apart from B-tree lookup",
    )
    require(
        ordered(
            page,
            "expected_source_evidence_set_digest",
            "SyncReplicaSqliteEvidencePageDisposition::SourceChanged",
            "read_exact_operation_row_or_none_or_throw",
            "evidence page range prepare",
        ),
        "source_change_precedes_cursor_and_range_access",
        "a stale source digest fails before operation-row traversal",
    )
    request = function_body(service_c, "SyncReplicaReconciliationService::make_request_or_throw")
    serve = last_function_body(service_c, "SyncReplicaReconciliationService::serve_request_frame_or_throw")
    apply = function_body(service_c, "SyncReplicaReconciliationService::apply_response_or_throw")
    require(
        "require_current_owner_identity_or_throw" in request
        and "snapshot_or_throw" not in request,
        "outbound_request_uses_fixed_identity_cutpoint",
        "one request no longer rebuilds all retained evidence",
    )
    require(
        "owner_.evidence_page_or_throw" in serve
        and "snapshot_or_throw" not in serve,
        "source_serve_uses_one_bounded_evidence_owner",
        "the responder does not perform a redundant complete snapshot before paging",
    )
    require(
        "require_current_owner_identity_or_throw" in apply
        and "targeted_path_cutpoint_or_throw" in apply
        and "local_snapshot" not in apply
        and "find_operation_by_id_or_none" not in service_c,
        "receiver_apply_is_identity_and_path_bounded_before_terminal_admission",
        "predecessor selection no longer scans a complete local operation vector",
    )
    require(
        "const SyncReplicaOperation* observed" in apply
        and "predecessor_cutpoint.requested_retained_operation_or_none()" in apply
        and "projected.source_operation = *observed" in apply,
        "predecessor_operation_outlives_targeted_cutpoint",
        "the cutpoint-owned observation is copied into retained projection state before the cutpoint leaves scope",
    )
    require(
        "evidence_page_range_read_count" in owner_test
        and "test_identity_cutpoint_is_fixed_and_history_cold" in owner_test
        and "test_evidence_page_is_primary_key_bounded_and_history_cold" in owner_test
        and "72U" in owner_test
        and "complete_operation_projection_read_count == 0U" in owner_test,
        "owner_sql_trace_regressions_bind_bounded_statement_shapes",
        "populated history cannot hide a complete operation projection",
    )
    require(
        "ReplicaHistoryReadTrace" in service_test
        and "first bounded delta-progress turn reconstructed complete retained history" in service_test
        and "source_history_trace.evidence_page_range_read_count == page_count" in service_test
        and "receiver_history_trace.exact_visible_path_read_count >=" in service_test
        and "source_payload_page_count" in service_test
        and "terminal_verification_page_count == 0U" in service_test
        and "terminal_verification_local_continuation_steps == 1U" in service_test
        and "source manifest reuse or receiver-local terminal verification did not remain exact and payload-cold" in service_test,
        "service_trace_binds_progress_turn_and_terminal_boundary",
        "multi-range source paging is bounded while terminal admission remains explicit",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_is_not_forked",
        "history-access correction does not require a wire change",
    )
    normalized = " ".join((design + "\n" + notes + "\n" + readme + "\n" + bootstrap).split())
    require(
        "65,536" in normalized and "262,144" in normalized
        and "terminal remote" in normalized
        and "same-UID" in normalized,
        "scale_consequence_and_nonclaims_are_explicit",
        "the release explains both the multiplier removed and the trust boundary retained",
    )
    require(
        "BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md" in verifier
        and "REVISION_NOTES_rev0999.md" in verifier
        and "tools/audit_sync_replica_bounded_history_access.py" in verifier,
        "release_verifier_requires_rev0999_slice",
        "the archive cannot omit the implementation audit, notes, tests, or verifier integration",
    )
    require(
        "BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md" in structural
        and "rev0999_final_validation_and_visible_release_cutpoint_are_sealed" in structural,
        "structural_audit_requires_rev0999_slice",
        "the complete authority audit includes the new hot-path boundary",
    )
    require(
        "VALIDATION_PENDING_REV0999" not in normalized
        and "ARCHIVE_PENDING_REV0999" not in normalized
        and "CODENAME_PENDING_REV0999" not in normalized,
        "rev0999_final_validation_and_archive_are_sealed",
        "final publication requires exact evidence and filename substitution",
    )
    require(
        "lexical-hygiene-not-semantic-or-query-plan-proof" in Path(__file__).read_text(encoding="utf-8")
        and "not a semantic" in Path(__file__).read_text(encoding="utf-8"),
        "lexical_audit_disclaims_semantic_authority",
        "runtime, sanitizer, and package evidence remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
